using System.Text.Json;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

namespace Wpcp.Worker;

internal sealed class HeadQualificationWorkflow(PostgresImplementationRunStore store,
    ImplementationRunProjection run, Publication publication, JsonElement plan, string python, string fixture, string? pauseAt)
{
    private static readonly string[] Axes = ["requirements", "code-quality", "architecture"];
    private HeadQualification qualification = publication.HeadQualification ?? new HeadQualification(
        publication.Intent!.Value.GetProperty("headSha").GetString()!, "qualification-running",
        [new QualificationRound(0, publication.Intent.Value.GetProperty("headSha").GetString()!, publication.Intent.Value)], Repairs: []);
    private readonly int pullNumber = publication.Report!.Value.GetProperty("pullRequest").GetProperty("number").GetInt32();
    private readonly string writer = publication.Qualification!.Value.GetProperty("source").GetProperty("sessionId").GetString()!;

    public static Task ExecuteAsync(PostgresImplementationRunStore store, ImplementationRunProjection run,
        Publication publication, JsonElement plan, string python, string fixture, string? pauseAt) =>
        new HeadQualificationWorkflow(store, run, publication, plan, python, fixture, pauseAt).RunAsync();

    private async Task RunAsync()
    {
        if (qualification.State is "qualification-blocked" or "awaiting-human") return;
        if (qualification.State == "qualified")
        {
            var current = await InvokeAsync("current-head");
            if (State(current) != "head-current") await BlockAsync(Blocker(current));
            return;
        }
        while (true)
        {
            if (qualification.Repairs?.LastOrDefault() is { State: not "completed" })
            {
                if (!await CompleteRepairAsync()) return;
            }
            if (!await ReviewRoundAsync()) return;
            var round = qualification.Rounds[^1];
            var failed = round.Reviews!.Where(r => r.Report!.Value.GetProperty("result").GetProperty("verdict").GetString() == "fail").ToArray();
            if (failed.Length == 0 && State(round.Verification!.Value) == "check-passed")
            {
                var final = await InvokeAsync("current-head");
                if (State(final) != "head-current") { await BlockAsync(Blocker(final)); return; }
                await SaveRoundAsync(round with { State = "passed" });
                await SaveAsync(qualification with { State = "qualified", QualifiedHeadSha = round.HeadSha, Blocker = null });
                return;
            }
            await SaveRoundAsync(round with { State = "failed" });
            var number = (qualification.Repairs?.Count ?? 0) + 1;
            if (number > QualificationRepair.MaximumRounds)
            { await BlockAsync("repair-limit-exhausted", human: true); return; }
            if (failed.Length == 0)
            { await BlockAsync("deterministic-check-failed-without-actionable-review", human: true); return; }
            var assignment = await PublicationWorkflow.InvokeAsync(python, new { stage = "repair-assignment", plan,
                run.Correlation, fixture, headSha = round.HeadSha, pullNumber, runId = run.RunId,
                number, writerSessionId = writer, reviews = round.Reviews, verification = round.Verification,
                priorAttempts = qualification.Repairs!.Select(r => new { r.Number, r.SourceHeadSha, r.HeadSha, r.State,
                    summary = r.Report?.GetProperty("result").GetProperty("summary").GetString() }), intent = round.Evidence });
            if (State(assignment) != "repair-assigned") { await BlockAsync(Blocker(assignment)); return; }
            var repair = new QualificationRepair(number, Guid.NewGuid().ToString(), round.HeadSha, assignment.GetProperty("assignment").Clone());
            // Invalidate usable qualification before the writer is dispatched.
            await SaveAsync(qualification with { State = "qualification-running", QualifiedHeadSha = null,
                Repairs = [.. qualification.Repairs!, repair] });
        }
    }

    private async Task<bool> ReviewRoundAsync()
    {
        var round = qualification.Rounds[^1];
        if (round.Verification is null)
        {
            if (round.State == "verifying") { await BlockAsync("verification-interrupted"); return false; }
            await SaveRoundAsync(round with { State = "verifying" });
            await PauseAsync("before-qualification-verification");
            var report = await InvokeAsync("verify-head");
            round = qualification.Rounds[^1] with { State = "reviewing", Verification = report };
            await SaveRoundAsync(round);
        }
        if (State(round.Verification!.Value) is not ("check-passed" or "check-failed"))
        { await BlockAsync(Blocker(round.Verification.Value)); return false; }
        if (round.Reviews is null)
        {
            round = round with { Reviews = Axes.Select(axis => new HeadReview(axis, Guid.NewGuid().ToString())).ToArray() };
            await SaveRoundAsync(round);
        }
        foreach (var pending in round.Reviews!.Where(r => r.Report is null).ToArray())
        {
            var report = await PublicationWorkflow.InvokeAsync(python, new { stage = "review-head", plan,
                run.Correlation, fixture, headSha = round.HeadSha, pullNumber, runId = run.RunId,
                axis = pending.Axis, operationKey = pending.OperationKey, intent = round.Evidence });
            await PauseAsync("after-qualification-review-response");
            round = round with { Reviews = round.Reviews.Select(r => r.OperationKey == pending.OperationKey ? r with { Report = report } : r).ToArray() };
            await SaveRoundAsync(round);
        }
        if (round.Reviews.Any(r => State(r.Report!.Value) != "review-completed"))
        { await BlockAsync("invalid-review-batch"); return false; }
        var sessions = qualification.Rounds.SelectMany(r => r.Reviews ?? [])
            .Where(r => r.Report is { } report && State(report) == "review-completed")
            .Select(r => r.Report!.Value.GetProperty("sessionId").GetString()).ToArray();
        if (sessions.Distinct().Count() != sessions.Length || sessions.Contains(writer))
        { await BlockAsync("review-session-not-fresh"); return false; }
        return true;
    }

    private async Task<bool> CompleteRepairAsync()
    {
        var repair = qualification.Repairs![^1];
        if (repair.Report is null)
        {
            var report = await RepairInvokeAsync("repair-head", repair);
            await PauseAsync("after-qualification-repair-response");
            if (State(report) == "repair-uncertain")
            {
                await SaveRepairAsync(repair with { LastObservation = report });
                await BlockAsync(Blocker(report), uncertain: true);
                return false;
            }
            repair = repair with { Report = report, State = "repaired" };
            await SaveRepairAsync(repair);
        }
        if (State(repair.Report.Value) != "repair-completed")
        { await BlockAsync(State(repair.Report.Value) == "repair-intervention" ? "repair-needs-human-decision" : Blocker(repair.Report.Value), human: true); return false; }
        if (repair.HeadSha is null)
        {
            var prepared = await RepairInvokeAsync("prepare-repair", repair);
            if (State(prepared) != "evidence-prepared") { await BlockAsync(Blocker(prepared)); return false; }
            repair = repair with { HeadSha = prepared.GetProperty("headSha").GetString(), State = "prepared" };
            await SaveRepairAsync(repair);
            await SaveAsync(qualification with { HeadSha = repair.HeadSha! });
        }
        if (repair.Evidence is null)
        {
            if (repair.State == "capturing") { await BlockAsync("repair-evidence-interrupted"); return false; }
            await SaveRepairAsync(repair with { State = "capturing" });
            var evidence = await PublicationWorkflow.InvokeAsync(python, new { stage = "capture", plan, run.Correlation,
                fixture, runId = run.RunId, headSha = repair.HeadSha });
            if (State(evidence) != "evidence-ready") { await BlockAsync(Blocker(evidence)); return false; }
            repair = repair with { Evidence = evidence.GetProperty("intent").Clone(), State = "publishing" };
            await SaveRepairAsync(repair);
        }
        if (repair.PublicationReport is null || State(repair.PublicationReport.Value) != "draft-updated")
        {
            var published = await RepairInvokeAsync("publish-repair", repair);
            repair = repair with { PublicationReport = published };
            await SaveRepairAsync(repair);
            if (State(published) != "draft-updated")
            {
                // Preserve ownership while a dispatched push/body update needs reconciliation.
                await SaveAsync(qualification with { State = "qualification-uncertain", Blocker = Blocker(published) });
                return false;
            }
        }
        var newRound = new QualificationRound(repair.Number, repair.HeadSha!, repair.Evidence!.Value);
        // Completing the repair and adding its head round are one durable transition.
        await SaveAsync(qualification with { State = "qualification-running", HeadSha = repair.HeadSha!, Blocker = null,
            HumanRequest = null,
            Repairs = [.. qualification.Repairs.Take(qualification.Repairs.Count - 1), repair with { State = "completed" }],
            Rounds = [.. qualification.Rounds, newRound] });
        return true;
    }

    private Task<JsonElement> RepairInvokeAsync(string stage, QualificationRepair repair) => PublicationWorkflow.InvokeAsync(python,
        new { stage, plan, run.Correlation, fixture, runId = run.RunId, headSha = repair.SourceHeadSha,
            pullNumber, number = repair.Number, operationKey = repair.OperationKey, assignment = repair.Assignment,
            intent = repair.Evidence, previousIntent = qualification.Rounds[^1].Evidence });

    private Task<JsonElement> InvokeAsync(string stage) => PublicationWorkflow.InvokeAsync(python,
        new { stage, plan, run.Correlation, fixture, headSha = qualification.HeadSha, pullNumber });

    private Task SaveRoundAsync(QualificationRound round) => SaveAsync(qualification with {
        Rounds = [.. qualification.Rounds.Take(qualification.Rounds.Count - 1), round] });

    private Task SaveRepairAsync(QualificationRepair repair)
    {
        var repairs = qualification.Repairs!;
        return SaveAsync(qualification with { Repairs = [.. repairs.Take(repairs.Count - 1), repair] });
    }

    private async Task SaveAsync(HeadQualification next)
    {
        publication = await store.SavePublicationAsync(run.RunId, publication with {
            State = next.State, Blocker = next.Blocker, HeadQualification = next });
        qualification = publication.HeadQualification!;
    }

    private Task BlockAsync(string blocker, bool human = false, bool uncertain = false)
    {
        var source = publication.Qualification!.Value.GetProperty("source");
        var findings = qualification.Rounds[^1].Reviews?.Where(r => r.Report is { } report && State(report) == "review-completed")
            .SelectMany(r => r.Report!.Value.GetProperty("result").GetProperty("findings").EnumerateArray()
                .Select(f => r.Axis + " / " + f.GetProperty("location").GetString() + ": " + f.GetProperty("description").GetString())) ?? [];
        var details = string.Join("; ", findings);
        if (qualification.Repairs?.LastOrDefault()?.Report is { } repairReport && State(repairReport) == "repair-intervention")
            details = repairReport.GetProperty("result").GetProperty("summary").GetString();
        var request = new HumanRequest(qualification.HumanRequest?.RequestId ?? Guid.NewGuid().ToString(), source.GetProperty("attemptId").GetString()!, writer,
            "qualification", qualification.HeadSha,
            blocker + ": " + details + " Inspect the retained draft and evidence; resolve this conflict before authorizing further work.",
            [publication.Report!.Value.GetProperty("pullRequest").GetProperty("html_url").GetString()!,
                "/api/v1/runs/" + run.RunId, "head:" + qualification.HeadSha], ["inspect-draft", "inspect-evidence"]);
        return SaveAsync(qualification with { State = uncertain ? "qualification-uncertain" : human ? "awaiting-human" : "qualification-blocked",
            QualifiedHeadSha = null, Blocker = blocker, HumanRequest = request });
    }

    private async Task PauseAsync(string boundary)
    {
        if (pauseAt != boundary) return;
        Console.Out.WriteLine(JsonSerializer.Serialize(new { faultHook = boundary }));
        await Task.Delay(Timeout.InfiniteTimeSpan);
    }

    private static string? State(JsonElement report) => report.TryGetProperty("state", out var state) ? state.GetString() : null;
    private static string Blocker(JsonElement report) => report.TryGetProperty("blocker", out var blocker) ? blocker.GetString()! : "qualification-boundary-unavailable";
}
