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
        if (publication?.HeadQualification is not null)
        {
            await HeadQualificationWorkflow.ExecuteAsync(store, run, publication, plan, python, fixture, pauseAt);
            return;
        }
        publication ??= await store.SavePublicationAsync(runId, new Publication(hash, "preflight"));
        if (publication.CaptureHeadSha is not null && publication.Intent is null && publication.State == "publication-blocked")
            return;
        if (await store.FindPublicationOwnerAsync(run.Correlation.RepositoryId, runId) is { } owner)
        {
            await store.SavePublicationAsync(runId, publication with { State = "preflight-blocked",
                Blocker = "repository-publication-busy", Report = JsonSerializer.SerializeToElement(new { ownerRunId = owner }) });
            return;
        }
        if (publication.Intent is null)
        {
            if (publication.CaptureHeadSha is null)
            {
                if (publication.State is not ("ready" or "awaiting-agent" or "evidence-running"))
                {
                    var readiness = await InvokeAsync(python, new { stage = "preflight", plan, run.Correlation, fixture });
                    publication = await store.SavePublicationAsync(runId, FromReport(hash, readiness));
                    if (publication.State != "ready") return;
                }
                // The existing Agent Framework workflow owns canonical result validation.
                var origin = plan.GetProperty("agentOrigin").GetString()!;
                await AgentSessionWorkflow.ExecuteAsync(store, runId, origin,
                    "Implement the admitted issue with this evidence plan: " + plan.GetRawText(),
                    null, false, 90000, repositoryDelivery: true, realPython: python, mode: AgentSessionMode.Real);
                run = (await store.GetProjectionAsync(runId))!;
                var completed = await GetCompletedResultAsync(store, run, python);
                if (completed is null)
                {
                    await store.SavePublicationAsync(runId, publication with { State = "awaiting-agent", Blocker = "agent-completion-required" });
                    return;
                }
                var prepared = await InvokeAsync(python, new { stage = "prepare", plan, run.Correlation, fixture });
                if (prepared.GetProperty("state").GetString() != "evidence-prepared")
                {
                    await store.SavePublicationAsync(runId, FromReport(hash, prepared));
                    return;
                }
                var attempt = run.Attempts.Last(a => a.Session is not null);
                var qualified = await InvokeAsync(python, new { stage = "qualify", plan, run.Correlation, fixture,
                    result = completed.Result, source = new { attempt.AttemptId, attempt.Session!.SessionId,
                        originalResultEventId = completed.EventId } });
                if (!qualified.TryGetProperty("schemaValid", out var valid) || !valid.GetBoolean())
                {
                    await store.SavePublicationAsync(runId, publication with { State = "publication-blocked",
                        Blocker = "evidence-qualification-unavailable", Report = qualified });
                    return;
                }
                publication = await store.SavePublicationAsync(runId, publication with {
                    Qualification = qualified, CaptureHeadSha = prepared.GetProperty("headSha").GetString(),
                    State = "evidence-running", Blocker = null });
            }
            publication = await CaptureEvidenceAsync(store, run, publication, plan, python, fixture, pauseAt);
            if (publication.Intent is null) return;
        }
        var allowCreate = !publication.Dispatched;
        publication = await store.SavePublicationAsync(runId, publication with { State = "publication-dispatching", Dispatched = true });
        var report = await InvokeAsync(python, new { stage = "publish", plan, run.Correlation, fixture,
            intent = publication.Intent, allowCreate });
        if (report.GetProperty("state").GetString() == "draft-published")
            await PauseAsync(pauseAt, "after-provider-effect");
        publication = await store.SavePublicationAsync(runId, publication with { State = report.GetProperty("state").GetString()!,
            Blocker = report.TryGetProperty("blocker", out var blocker) ? blocker.GetString() : null, Report = report });
        if (publication.State == "draft-published" && plan.TryGetProperty("headQualification", out _))
            await HeadQualificationWorkflow.ExecuteAsync(store, (await store.GetProjectionAsync(runId))!, publication, plan, python, fixture, pauseAt);
    }

    private static async Task<Publication> CaptureEvidenceAsync(PostgresImplementationRunStore store,
        ImplementationRunProjection run, Publication publication, JsonElement plan,
        string python, string fixture, string? pauseAt)
    {
        var runId = run.RunId;
        if (publication.Capture is { State: "running" } interrupted)
            publication = await store.SavePublicationAsync(runId, publication with {
                Capture = interrupted with { State = "interrupted", Report = JsonSerializer.SerializeToElement(new {
                    state = "interrupted", blocker = "evidence-capture-interrupted", headSha = publication.CaptureHeadSha }) },
                Blocker = "evidence-capture-interrupted" });
        while ((publication.Capture?.Number ?? 0) < EvidenceCapture.MaximumRounds)
        {
            var number = (publication.Capture?.Number ?? 0) + 1;
            var kind = number > 1 || !publication.Qualification!.Value.GetProperty("complete").GetBoolean()
                ? "correction" : "capture";
            publication = await store.SavePublicationAsync(runId, publication with {
                State = "evidence-running", Capture = new EvidenceCapture(number, kind, "running", Guid.NewGuid().ToString(), Guid.NewGuid().ToString()) });
            await PauseAsync(pauseAt, "after-evidence-capture-start");
            var evidence = await InvokeAsync(python, new { stage = "capture", plan, run.Correlation, fixture, runId,
                headSha = publication.CaptureHeadSha });
            var success = evidence.GetProperty("state").GetString() == "evidence-ready";
            var captured = publication with {
                Capture = publication.Capture! with { State = success ? "succeeded" : "failed", Report = evidence },
                State = success ? "evidence-ready" : "evidence-running",
                Blocker = evidence.TryGetProperty("blocker", out var captureBlocker) ? captureBlocker.GetString() : null,
                Intent = success ? evidence.GetProperty("intent").Clone() : null };
            if (!success && (number == EvidenceCapture.MaximumRounds || captured.Blocker == "evidence-head-drift"))
                captured = BlockedCapture(captured);
            publication = await store.SavePublicationAsync(runId, captured);
            await PauseAsync(pauseAt, "after-evidence-capture-result");
            if (success || publication.Blocker == "evidence-head-drift") break;
        }
        if (publication.Intent is null)
        {
            if (publication.State != "publication-blocked")
                publication = await store.SavePublicationAsync(runId, BlockedCapture(publication));
        }
        return publication;
    }

    private static async Task PauseAsync(string? requested, string boundary)
    {
        if (requested != boundary) return;
        Console.Out.WriteLine(JsonSerializer.Serialize(new { faultHook = boundary }));
        await Task.Delay(Timeout.InfiniteTimeSpan);
    }

    private static Publication BlockedCapture(Publication publication) => publication with {
        State = "publication-blocked",
        Report = JsonSerializer.SerializeToElement(new { exhausted = publication.Capture?.Number >= EvidenceCapture.MaximumRounds,
            requiredAction = publication.Blocker == "evidence-head-drift"
                ? "Inspect the changed repository and submit a new authorized run; the captured head cannot be reused."
                : "Restore the failed evidence surface and submit a new authorized run; automatic capture is exhausted." }) };

    private sealed record CompletedResult(JsonElement Result, string? EventId);

    private static async Task<CompletedResult?> GetCompletedResultAsync(PostgresImplementationRunStore store,
        ImplementationRunProjection run, string python)
    {
        var attempt = run.Attempts.LastOrDefault(a => a.Session is not null);
        if (attempt?.Session is not { } session) return null;
        if (attempt.State == "completed" && session.OriginalResult is { } original &&
            await ResolveEvidenceValueAsync(store, run.RunId, original) is { } resultValue &&
            resultValue.TryGetProperty("outcome", out var outcome) && outcome.GetString() == "completed")
            return new(resultValue, session.OriginalResultEventId);
        string? turn = null;
        JsonElement? candidate = null;
        string? candidateEventId = null;
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
                if (data is null) return null;
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
                        try { candidate = JsonSerializer.Deserialize<JsonElement>(parameters.GetProperty("item").GetProperty("text").GetString()!); candidateEventId = item.EventId; }
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
            await CanonicalResult.ValidateAsync(python, result, default) ? new(result, candidateEventId) : null;
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

    internal static async Task<JsonElement> InvokeAsync(string python, object input)
    {
        var start = new ProcessStartInfo(python) { RedirectStandardInput = true,
            RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        start.ArgumentList.Add(Path.Combine(AppContext.BaseDirectory, "publication_adapter.py"));
        start.Environment["WPCP_PUBLICATION_OWNER_PID"] = Environment.ProcessId.ToString();
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
