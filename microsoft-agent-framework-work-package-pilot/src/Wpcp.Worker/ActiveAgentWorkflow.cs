using System.Net.Http.Json;
using System.Text.Json;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

namespace Wpcp.Worker;

internal static class ActiveAgentWorkflow
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    // A controlled fault boundary: stdin newline releases it; closed stdin waits for process termination.
    private sealed class FaultBoundary(string? requested)
    {
        private bool _reached;
        public async Task PauseAsync(string boundary)
        {
            if (_reached || boundary != requested) return;
            _reached = true;
            Console.Out.WriteLine(JsonSerializer.Serialize(new { faultHook = boundary }));
            if (await Console.In.ReadLineAsync() is null) await Task.Delay(Timeout.InfiniteTimeSpan);
        }
    }

    public static async Task ExecuteAsync(PostgresImplementationRunStore store, string runId, string? pauseAt)
    {
        var fault = new FaultBoundary(pauseAt);
        foreach (var delivery in await store.GetActiveAgentDeliveriesAsync(runId))
        {
            using var client = ControlledHttp.Client(delivery.AdapterOrigin, 10000);
            var attempt = delivery.Attempt;
            while ((attempt.State is "running" or "cancelling") && attempt.CurrentOperation is { } operation)
            {
                await fault.PauseAsync("before-active-dispatch");
                if (operation.CommandId is not null) await fault.PauseAsync("before-active-delivery");
                var body = new { attemptId = attempt.AttemptId, sessionId = attempt.SessionId,
                    operation.FenceEpoch, operation.CommandId, operation.Message, effectScope = "none" };
                using var content = new StringContent(JsonSerializer.Serialize(body, JsonOptions),
                    System.Text.Encoding.UTF8, "application/json");
                JsonElement receipt;
                try
                {
                    using var response = operation.StopRequested
                        ? await client.PostAsync($"operations/{operation.OperationKey}/stop", content)
                        : await client.PutAsync($"operations/{operation.OperationKey}", content);
                    response.EnsureSuccessStatusCode();
                    receipt = await response.Content.ReadFromJsonAsync<JsonElement>();
                }
                catch (Exception error) when (error is HttpRequestException or TaskCanceledException or JsonException)
                {
                    await store.RecordActiveDeliveryUnavailableAsync(delivery, operation,
                        error is TaskCanceledException ? "adapter-timeout" : error is JsonException ? "invalid-adapter-json" : "adapter-unavailable");
                    break;
                }
                await fault.PauseAsync("after-active-response");
                if (operation.StopRequested) await fault.PauseAsync("after-active-stop");
                else if (operation.CommandId is not null) await fault.PauseAsync("after-active-delivery");
                attempt = await store.ObserveActiveAgentAsync(delivery, operation, receipt);
                if (attempt.CurrentOperation?.OperationKey == operation.OperationKey &&
                    (!attempt.CurrentOperation.StopRequested || operation.StopRequested)) break;
            }
        }
    }
}
