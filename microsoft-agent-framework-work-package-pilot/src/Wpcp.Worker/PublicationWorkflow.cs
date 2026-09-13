using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

namespace Wpcp.Worker;

internal static class PublicationWorkflow
{
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    public static async Task ExecuteAsync(PostgresImplementationRunStore store, string runId,
        string planPath, string python, string fixture, string? pauseAt)
    {
        await using var delivery = await store.AcquireAgentDeliveryAsync(runId);
        var bytes = await File.ReadAllBytesAsync(planPath);
        var hash = Convert.ToHexStringLower(SHA256.HashData(JsonSerializer.SerializeToUtf8Bytes(new {
            planHash = Convert.ToHexStringLower(SHA256.HashData(bytes)), python = Path.GetFullPath(python) })));
        var run = (await store.GetProjectionAsync(runId))!;
        if (await store.GetRestoredProjectionAsync(runId) is not null)
            throw new AgentAssignmentConflictException();
        await using var repositoryDelivery = await store.AcquireAgentDeliveryAsync("publication-repository:" + run.Correlation.RepositoryId);
        var publication = run.Publication;
        if (publication is not null && publication.AssignmentHash != hash)
            throw new AgentAssignmentConflictException();
        var plan = JsonSerializer.Deserialize<JsonElement>(bytes);
        publication ??= await store.SavePublicationAsync(runId, new Publication(hash, "preflight"));
        if (await store.FindPublicationOwnerAsync(run.Correlation.RepositoryId, runId) is { } owner)
        {
            await store.SavePublicationAsync(runId, publication with { State = "preflight-blocked",
                Blocker = "repository-publication-busy", Report = JsonSerializer.SerializeToElement(new { ownerRunId = owner }) });
            return;
        }
        if (publication?.Intent is null)
        {
            if (publication?.State is not ("ready" or "awaiting-agent" or "evidence-running"))
            {
                var readiness = await InvokeAsync(python, new { stage = "preflight", plan, run.Correlation, fixture });
                publication = await store.SavePublicationAsync(runId, FromReport(hash, readiness));
                if (publication.State != "ready") return;
            }
            // This outer delivery owns serialization; the existing real Agent Framework
            // workflow still owns session capture and full canonical result validation.
            var origin = plan.GetProperty("agentOrigin").GetString()!;
            await FakeAgentWorkflow.ExecuteAsync(store, runId, origin,
                "Implement the admitted issue with this evidence plan: " + plan.GetRawText(),
                null, false, 90000, repositoryDelivery: true, realPython: python);
            run = (await store.GetProjectionAsync(runId))!;
            if (!await HasCompletedResultAsync(store, run, python))
            {
                await store.SavePublicationAsync(runId, publication! with { State = "awaiting-agent", Blocker = "agent-completion-required" });
                return;
            }
            publication = await store.SavePublicationAsync(runId, publication! with { State = "evidence-running" });
            var evidence = await InvokeAsync(python, new { stage = "evidence", plan, run.Correlation, fixture, runId });
            if (evidence.GetProperty("state").GetString() != "evidence-ready")
            {
                await store.SavePublicationAsync(runId, FromReport(hash, evidence));
                return;
            }
            publication = await store.SavePublicationAsync(runId, publication with {
                State = "evidence-ready", Blocker = null, Intent = evidence.GetProperty("intent").Clone() });
        }
        var allowCreate = !publication.Dispatched;
        publication = await store.SavePublicationAsync(runId, publication with { State = "publication-dispatching", Dispatched = true });
        var report = await InvokeAsync(python, new { stage = "publish", plan, run.Correlation, fixture,
            intent = publication.Intent, allowCreate });
        if (pauseAt == "after-provider-effect" && report.GetProperty("state").GetString() == "draft-published")
        {
            Console.Out.WriteLine(JsonSerializer.Serialize(new { faultHook = pauseAt }));
            await Task.Delay(Timeout.InfiniteTimeSpan);
        }
        await store.SavePublicationAsync(runId, publication with { State = report.GetProperty("state").GetString()!,
            Blocker = report.TryGetProperty("blocker", out var blocker) ? blocker.GetString() : null, Report = report });
    }

    private static async Task<bool> HasCompletedResultAsync(PostgresImplementationRunStore store,
        ImplementationRunProjection run, string python)
    {
        var attempt = run.Attempts.LastOrDefault(a => a.Session is not null);
        if (attempt?.Session is not { } session) return false;
        if (attempt.State == "completed" && session.OriginalResult is { } original &&
            await ResolveEvidenceValueAsync(store, run.RunId, original) is { } resultValue &&
            resultValue.TryGetProperty("outcome", out var outcome) && outcome.GetString() == "completed") return true;
        string? turn = null;
        JsonElement? candidate = null;
        var completed = false;
        long after = 0;
        do
        {
            var page = (await store.GetEventsAfterAsync(run.RunId, after))!;
            foreach (var item in page.Events)
            {
                if (item.EventType != "AgentInteractiveObservation") continue;
                var payload = item.Payload;
                if (payload.GetProperty("sourceSessionId").GetString() != session.SessionId ||
                    payload.GetProperty("type").GetString() != "observation") continue;
                var data = await ResolveEvidenceValueAsync(store, run.RunId, payload.GetProperty("data"));
                // Missing/corrupt artifact bytes must not preserve an older completion.
                if (data is null) return false;
                var observation = data.Value.GetProperty("event");
                var parameters = observation.GetProperty("params");
                switch (observation.GetProperty("method").GetString())
                {
                    case "turn/started":
                        turn = parameters.GetProperty("turn").GetProperty("id").GetString();
                        candidate = null; completed = false;
                        break;
                    case "item/completed" when parameters.GetProperty("item").GetProperty("type").GetString() == "agentMessage":
                        if (parameters.GetProperty("turnId").GetString() != turn) break;
                        try { candidate = JsonSerializer.Deserialize<JsonElement>(parameters.GetProperty("item").GetProperty("text").GetString()!); }
                        catch (JsonException) { candidate = null; }
                        break;
                    case "turn/completed":
                        completed = parameters.GetProperty("turn").GetProperty("id").GetString() == turn &&
                            parameters.GetProperty("turn").GetProperty("status").GetString() == "completed";
                        break;
                }
            }
            after = page.NextAfter;
            if (!page.HasMore) break;
        } while (true);
        return completed && candidate is { } result &&
            result.TryGetProperty("outcome", out var status) && status.GetString() == "completed" &&
            await CanonicalResult.ValidateAsync(python, result, default);
    }

    private static async Task<JsonElement?> ResolveEvidenceValueAsync(PostgresImplementationRunStore store,
        string runId, JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object || !value.TryGetProperty("artifactId", out var id)) return value;
        var artifact = await store.GetArtifactAsync(runId, id.GetString()!);
        return artifact is { Bytes: { } bytes } ? JsonSerializer.Deserialize<JsonElement>(bytes) : null;
    }

    private static Publication FromReport(string hash, JsonElement report) =>
        new(hash, report.GetProperty("state").GetString()!,
            report.TryGetProperty("blocker", out var blocker) ? blocker.GetString() : null, report);

    private static async Task<JsonElement> InvokeAsync(string python, object input)
    {
        var start = new ProcessStartInfo(python) { RedirectStandardInput = true,
            RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        start.ArgumentList.Add(Path.Combine(AppContext.BaseDirectory, "publication_adapter.py"));
        try
        {
            using var process = Process.Start(start) ?? throw new IOException();
            var output = process.StandardOutput.ReadToEndAsync();
            var errors = process.StandardError.ReadToEndAsync();
            await process.StandardInput.WriteAsync(JsonSerializer.Serialize(input, JsonOptions));
            process.StandardInput.Close();
            using var timeout = new CancellationTokenSource(TimeSpan.FromMinutes(5));
            try { await process.WaitForExitAsync(timeout.Token); }
            catch (OperationCanceledException)
            {
                process.Kill(entireProcessTree: true);
                await process.WaitForExitAsync();
                throw new IOException();
            }
            await errors;
            if (process.ExitCode != 0) throw new IOException();
            return JsonSerializer.Deserialize<JsonElement>(await output);
        }
        catch (Exception error) when (error is IOException or System.ComponentModel.Win32Exception or JsonException)
        {
            return JsonSerializer.SerializeToElement(new { state = "preflight-blocked", blocker = "publication-adapter-unavailable" });
        }
    }
}
