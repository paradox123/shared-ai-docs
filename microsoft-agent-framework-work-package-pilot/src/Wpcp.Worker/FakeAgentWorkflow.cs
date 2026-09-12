using System.Text.Json;
using Microsoft.Agents.AI.Workflows;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

namespace Wpcp.Worker;

internal sealed class FakeAgentSessionAdapter(HttpClient client, bool readOnly = false) : IAgentSessionAdapter
{
    public async Task<AgentAdapterResponse> StartOrReadAsync(string operationKey, string note, CancellationToken token)
    {
        using var body = new StringContent(JsonSerializer.Serialize(new { note }), System.Text.Encoding.UTF8, "application/json");
        using var response = readOnly ? await client.GetAsync($"sessions/{operationKey}", token) :
            await client.PutAsync($"sessions/{operationKey}", body, token);
        return new((int)response.StatusCode, await response.Content.ReadAsStringAsync(token));
    }
}

internal static class FakeAgentWorkflow
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    public static async Task ExecuteAsync(PostgresImplementationRunStore store, string runId,
        string origin, string note, string? pauseAt, bool rejectBlocked, int timeoutMs, bool repositoryDelivery = false, bool readOnly = false)
    {
        var uri = ControlledHttp.Origin(origin);
        await using var delivery = repositoryDelivery ? null : await store.AcquireAgentDeliveryAsync(runId);
        await using var standalone = repositoryDelivery ? null : await store.AcquireStandaloneAgentAsync(runId);
        using var client = ControlledHttp.Client(origin, timeoutMs);
        var prepare = new PrepareExecutor(store, uri.AbsoluteUri, rejectBlocked);
        var execute = new FakeExecutor(store, new FakeAgentSessionAdapter(client, readOnly), note, pauseAt);
        var workflow = new WorkflowBuilder(prepare).WithName("FakeCodexAttemptV1")
            .AddEdge(prepare, execute).Build();
        await using var run = await InProcessExecution.RunAsync(workflow, runId);
        // Framework errors are events, not necessarily thrown by RunAsync.
        foreach (var error in run.OutgoingEvents.OfType<WorkflowErrorEvent>())
            throw Unwrap(error.Exception ?? new InvalidOperationException("Workflow error event has no exception."));
        foreach (var error in run.OutgoingEvents.OfType<ExecutorFailedEvent>())
            throw Unwrap(error.Data ?? new InvalidOperationException("Executor failure event has no exception."));
    }

    private static Exception Unwrap(Exception error)
    {
        while (error is System.Reflection.TargetInvocationException && error.InnerException is { } inner)
            error = inner;
        return error;
    }

    private static async Task PauseAsync(string boundary, string? requested, CancellationToken token)
    {
        if (requested != boundary) return;
        Console.Out.WriteLine(JsonSerializer.Serialize(new { faultHook = boundary }));
        await Task.Delay(Timeout.InfiniteTimeSpan, token);
    }

    private sealed class PrepareExecutor(PostgresImplementationRunStore store, string origin, bool rejectBlocked)
        : Executor<string, AgentAttemptReceipt>("PrepareFakeAttempt")
    {
        public override async ValueTask<AgentAttemptReceipt> HandleAsync(string runId, IWorkflowContext context,
            CancellationToken cancellationToken = default) =>
            await store.PrepareAgentAsync(runId, origin, rejectBlocked, cancellationToken);
    }

    private sealed class FakeExecutor(PostgresImplementationRunStore store, IAgentSessionAdapter adapter, string note, string? pauseAt)
        : Executor<AgentAttemptReceipt, string>("ExecuteExternalFakeSession")
    {
        public override async ValueTask<string> HandleAsync(AgentAttemptReceipt receipt, IWorkflowContext context,
            CancellationToken cancellationToken = default)
        {
            if (receipt.State != "running") return receipt.State;
            string category;
            try
            {
                AgentAdapterResponse response;
                if (receipt.Session.ObservedResponse is { } saved)
                    response = new(receipt.Session.ResponseStatus!.Value, saved.GetRawText());
                else
                {
                    response = await adapter.StartOrReadAsync(receipt.Session.OperationKey, note, cancellationToken);
                    await PauseAsync("after-session-start", pauseAt, cancellationToken);
                    receipt = await store.CaptureAgentResponseAsync(receipt.RunId, response, cancellationToken);
                }
                if (response.StatusCode >= 500) throw new AgentContractFailure("infrastructure-failure");
                if (response.StatusCode != 200) throw new AgentContractFailure("transport-failure");
                var session = JsonSerializer.Deserialize<AgentSessionRead>(response.Body, JsonOptions)
                    ?? throw new JsonException();
                if (session.ContractVersion != "AgentSessionAdapter/v1")
                    throw new AgentContractFailure("contract-incompatible");
                if (session.OperationKey != receipt.Session.OperationKey || !Guid.TryParse(session.SessionId, out _) ||
                    session.Events is null || session.Events.Count == 0)
                    throw new JsonException();
                receipt = await store.BindAgentSessionAsync(receipt.RunId, session.SessionId,
                    session.OpenInCodex, cancellationToken);
                await PauseAsync("after-session-mapping", pauseAt, cancellationToken);
                var terminal = false;
                foreach (var observation in session.Events)
                {
                    if (terminal || observation is null) throw new JsonException();
                    receipt = await store.ObserveAgentAsync(receipt.RunId, observation, cancellationToken);
                    if (observation.Data.ValueKind != JsonValueKind.Object) throw new JsonException();
                    if (observation.Type == "process-exit")
                    {
                        if (observation.Data.TryGetProperty("exitCode", out var exit) && exit.TryGetInt32(out var code) && code != 0)
                            throw new AgentContractFailure("process-failure");
                        throw new JsonException();
                    }
                    if (observation.Type is not ("message" or "tool-call" or "tool-result" or "artifact" or "result"))
                        throw new JsonException();
                    terminal = observation.Type == "result";
                }
                await PauseAsync("after-result-observed", pauseAt, cancellationToken);
                var result = receipt.Session.OriginalResult;
                if (!terminal || result is null || !TextEquals(result.Value, "schemaVersion", "fake-worker-result/v1") ||
                    !TextEquals(result.Value, "status", "blocked") || !result.Value.TryGetProperty("reason", out var reason) ||
                    reason.ValueKind != JsonValueKind.String || string.IsNullOrWhiteSpace(reason.GetString()))
                    throw new JsonException();
                category = receipt.RejectBlocked ? "semantic-rejection" : "blocked";
            }
            catch (AgentContractFailure error) { category = error.Category; }
            catch (JsonException) { category = "schema-failure"; }
            catch (ArgumentException) { category = "schema-failure"; }
            catch (HttpRequestException) { category = "transport-failure"; }
            catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested) { category = "timeout"; }
            receipt = await store.CompleteAgentAsync(receipt.RunId, category,
                category is "blocked" or "semantic-rejection" ? "blocked" :
                category == "process-failure" ? "failed" : "unknown", cancellationToken);
            return receipt.State;
        }
    }

    private static bool TextEquals(JsonElement value, string property, string expected) =>
        value.ValueKind == JsonValueKind.Object && value.TryGetProperty(property, out var field) &&
        field.ValueKind == JsonValueKind.String && field.GetString() == expected;

    private sealed class AgentContractFailure(string category) : Exception
    {
        public string Category { get; } = category;
    }
}
