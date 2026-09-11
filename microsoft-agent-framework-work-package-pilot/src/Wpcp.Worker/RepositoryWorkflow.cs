using System.Diagnostics;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.RegularExpressions;
using Wpcp.Domain;
using Wpcp.Storage.Postgres;

namespace Wpcp.Worker;

internal static class RepositoryWorkflow
{
    internal static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    public static async Task ExecuteAsync(PostgresImplementationRunStore store, string runId, string planPath, string? pauseAt)
    {
        var plan = JsonSerializer.Deserialize<RepositoryPlan>(await File.ReadAllTextAsync(planPath), JsonOptions)
            ?? throw new ArgumentException("Missing repository plan.");
        Validate(plan);
        await using var delivery = await store.AcquireAgentDeliveryAsync(runId);
        var execution = await store.BindRepositoryExecutionAsync(runId, plan);
        if (execution.Terminal) return;
        if (execution.RequestedAction is "reconcile" or "adopt" or "retire")
        {
            await ReconcileAsync(store, runId, execution, pauseAt);
            return;
        }
        var retry = execution.RequestedAction == "retry";
        if (!retry && execution.State is "human-decision" or "adoptable" or "reconciled") return;
        if (retry) execution = await store.RecordRecoveryStateAsync(runId, "ready");
        execution = await PreflightAsync(store, runId, execution, retry && (execution.Effects?.Count ?? 0) == 0);
        if (execution.Blocker is not null) return;
        execution = await store.AcquireRepositoryOwnerAsync(runId);
        if (!execution.Active) return;
        execution = await store.IntentRepositoryEffectAsync(runId, "git", $"refs/heads/wpcp/{runId}");
        var effect = execution.Effects!.Single(e => e.Kind == "git");
        try
        {
            var receipt = await ReadGitReceiptAsync(plan, effect);
            var adopted = receipt is not null;
            if (receipt is null)
            {
                await GitAsync(plan.LocalPath, "update-ref", "--create-reflog", "-m", effect.OperationId,
                    effect.Target, effect.HeadSha, new string('0', 40));
                await PauseAsync("after-git-effect", pauseAt);
                receipt = await ReadGitReceiptAsync(plan, effect) ?? throw new RepositoryGitException();
            }
            if (effect.State is not ("completed" or "adopted"))
                execution = await store.SetRepositoryEffectAsync(runId, effect.OperationId, adopted ? "adopted" : "completed", receipt);
            execution = await PreflightAsync(store, runId, execution);
            if (execution.Blocker is not null) return;
            execution = await store.IntentRepositoryEffectAsync(runId, "provider", $"run-marker:{runId}");
            effect = execution.Effects!.Single(e => e.Kind == "provider");
            using var client = Client(plan.ProviderOrigin);
            receipt = await ReadProviderReceiptAsync(client, plan, effect);
            adopted = receipt is not null;
            if (receipt is null)
            {
                using var body = new StringContent(JsonSerializer.Serialize(
                    new { effect.OperationId, effect.Kind, repository = plan.Repository, effect.HeadSha, effect.Target }, JsonOptions),
                    System.Text.Encoding.UTF8, "application/json");
                using var response = await client.PutAsync($"effects/{effect.OperationId}", body);
                response.EnsureSuccessStatusCode();
                await PauseAsync("after-provider-effect", pauseAt);
                receipt = await ReadProviderReceiptAsync(client, plan, effect) ?? throw new RepositoryEffectConflict("provider-receipt-missing", effect);
            }
            if (effect.State is not ("completed" or "adopted"))
                execution = await store.SetRepositoryEffectAsync(runId, effect.OperationId, adopted ? "adopted" : "completed", receipt);
            execution = await PreflightAsync(store, runId, execution);
            if (execution.Blocker is not null) return;
            var attempt = await store.PrepareAgentAsync(runId, Origin(plan.AgentOrigin).AbsoluteUri, false);
            execution = await store.IntentRepositoryEffectAsync(runId, "session", attempt.AttemptId, attempt.Session.OperationKey);
            effect = execution.Effects!.Single(e => e.Kind == "session");
            using var agentClient = Client(plan.AgentOrigin);
            var existing = await ReadSessionReceiptAsync(agentClient, plan, effect);
            if (existing is null && attempt.Session.SessionId is not null)
                throw new RepositoryEffectConflict("session-receipt-missing", effect);
            await FakeAgentWorkflow.ExecuteAsync(store, runId, plan.AgentOrigin,
                $"Repository base {effect.HeadSha}", pauseAt, false, 10000, repositoryDelivery: true);
            var sessionReceipt = await ReadSessionReceiptAsync(agentClient, plan, effect)
                ?? throw new RepositoryEffectConflict("session-receipt-missing", effect);
            var run = (await store.GetProjectionAsync(runId))!;
            var result = run.Attempts.Single(a => a.AttemptId == attempt.AttemptId);
            if (result.Session?.SessionId != sessionReceipt.ReceiptId)
                throw new RepositoryEffectConflict("session-receipt-conflict", effect);
            if (effect.State is not ("completed" or "adopted"))
                await store.SetRepositoryEffectAsync(runId, effect.OperationId, existing is null ? "completed" : "adopted", sessionReceipt);
            await PauseAsync("after-session-receipt", pauseAt);
            await store.FinishRepositoryAsync(runId, result.State);
        }
        catch (RepositoryEffectConflict error) { await store.BlockRepositoryAsync(runId, error.Code, error.Decision); }
        catch (RepositoryGitException) { await store.BlockRepositoryAsync(runId, "git-evidence-unavailable"); }
        catch (Exception error) when (error is HttpRequestException or TaskCanceledException or JsonException)
        { await store.BlockRepositoryAsync(runId, "provider-evidence-unavailable"); }
    }

    private static async Task ReconcileAsync(PostgresImplementationRunStore store, string runId, RepositoryExecution execution, string? pauseAt)
    {
        try
        {
            foreach (var effect in execution.Effects ?? [])
            {
                if (execution.RequestedAction == "adopt" && effect.OperationId != execution.SelectedOperationId) continue;
                var receipt = await ReadEffectAsync(execution.Plan, effect);
                if (receipt is null && effect.Receipt is not null)
                    throw new RepositoryEffectConflict($"{effect.Kind}-receipt-missing");
                if (execution.RequestedAction == "adopt" && receipt?.ReceiptId != execution.SelectedReceiptId)
                    throw new RepositoryEffectConflict($"{effect.Kind}-receipt-conflict");
                var state = receipt is null ? "missing" : execution.RequestedAction is "adopt" or "retire" ? "adopted" :
                    effect.State is "completed" or "adopted" ? effect.State : "adoptable";
                await store.SetRepositoryEffectAsync(runId, effect.OperationId, state, receipt);
                await PauseAsync("after-reconciled-effect", pauseAt);
            }
            var updated = (await store.GetProjectionAsync(runId))!.RepositoryExecution!;
            if (execution.RequestedAction == "retire")
            {
                if ((updated.Effects ?? []).Any(e => e.Kind == "session" && e.Receipt is not null))
                    await FakeAgentWorkflow.ExecuteAsync(store, runId, execution.Plan.AgentOrigin,
                        "Read existing session for retirement", null, false, 10000, repositoryDelivery: true, readOnly: true);
                await store.FinishRepositoryAsync(runId, "retired");
            }
            else
                await store.RecordRecoveryStateAsync(runId,
                    (updated.Effects ?? []).Any(e => e.State == "adoptable") ? "adoptable" : "reconciled");
        }
        catch (RepositoryEffectConflict error) { await store.BlockRepositoryAsync(runId, error.Code, error.Decision); }
        catch (Exception error) when (error is RepositoryGitException or HttpRequestException or TaskCanceledException or JsonException)
        { await store.BlockRepositoryAsync(runId, "effect-evidence-unavailable"); }
    }

    private static async Task<EffectReceipt?> ReadEffectAsync(RepositoryPlan plan, RepositoryEffect effect)
    {
        if (effect.Kind == "git") return await ReadGitReceiptAsync(plan, effect);
        using var client = Client(effect.Kind == "session" ? plan.AgentOrigin : plan.ProviderOrigin);
        return effect.Kind == "session" ? await ReadSessionReceiptAsync(client, plan, effect) :
            await ReadProviderReceiptAsync(client, plan, effect);
    }

    private static async Task<EffectReceipt?> ReadSessionReceiptAsync(HttpClient client, RepositoryPlan plan, RepositoryEffect effect)
    {
        using var response = await client.GetAsync($"sessions/{effect.OperationId}");
        if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            if (effect.Receipt is not null) throw new RepositoryEffectConflict("session-receipt-missing", effect);
            return null;
        }
        response.EnsureSuccessStatusCode();
        var session = await response.Content.ReadFromJsonAsync<AgentSessionRead>(JsonOptions);
        if (session?.ContractVersion != "AgentSessionAdapter/v1" || session.OperationKey != effect.OperationId ||
            !Guid.TryParse(session.SessionId, out _) || session.Events is null)
            throw new RepositoryEffectConflict("session-receipt-conflict", effect);
        var receipt = new EffectReceipt("RepositoryEffects/v1", effect.OperationId, session.SessionId,
            "session", plan.Repository, effect.HeadSha, effect.Target);
        if (effect.Receipt is not null && receipt != effect.Receipt)
            throw new RepositoryEffectConflict("session-receipt-conflict", effect);
        return receipt;
    }

    private sealed record ProviderReceipts(IReadOnlyList<EffectReceipt>? Receipts);

    private static async Task<EffectReceipt?> ReadProviderReceiptAsync(HttpClient client, RepositoryPlan plan, RepositoryEffect effect)
    {
        var found = await client.GetFromJsonAsync<ProviderReceipts>($"effects/{effect.OperationId}", JsonOptions);
        if (found?.Receipts is null) throw new RepositoryEffectConflict("provider-receipt-invalid", effect);
        if (found.Receipts.Count == 0)
        {
            if (effect.Receipt is not null) throw new RepositoryEffectConflict("provider-receipt-missing", effect);
            return null;
        }
        if (found.Receipts.Count != 1) throw new RepositoryEffectConflict("provider-receipt-ambiguous", effect, candidates: found.Receipts);
        var receipt = found.Receipts[0];
        if (receipt is null || receipt.ContractVersion != "RepositoryEffects/v1" ||
            receipt.OperationId != effect.OperationId || receipt.Repository != plan.Repository ||
            receipt.HeadSha != effect.HeadSha || receipt.Target != effect.Target || receipt.Kind != effect.Kind ||
            !Guid.TryParse(receipt.ReceiptId, out _) || (effect.Receipt is not null && effect.Receipt != receipt))
            throw new RepositoryEffectConflict("provider-receipt-conflict", effect);
        return receipt;
    }

    private static async Task<EffectReceipt?> ReadGitReceiptAsync(RepositoryPlan plan, RepositoryEffect effect)
    {
        var refs = await GitAsync(plan.LocalPath, "for-each-ref", "--format=%(refname) %(objectname)", effect.Target);
        if (refs.Length == 0)
        {
            if (effect.Receipt is not null) throw new RepositoryEffectConflict("git-receipt-missing", effect);
            return null;
        }
        if (refs != $"{effect.Target} {effect.HeadSha}") throw new RepositoryEffectConflict("git-target-conflict", effect, refs.Split(' ').LastOrDefault());
        var entries = (await GitAsync(plan.LocalPath, "reflog", "show", "--format=%H %gs", effect.Target)).Split('\n');
        if (entries.Count(e => e == $"{effect.HeadSha} {effect.OperationId}") != 1)
            throw new RepositoryEffectConflict("git-receipt-conflict", effect);
        return new("RepositoryEffects/v1", effect.OperationId, effect.OperationId, effect.Kind,
            plan.Repository, effect.HeadSha, effect.Target);
    }

    private static async Task PauseAsync(string boundary, string? requested)
    {
        if (boundary != requested) return;
        Console.Out.WriteLine(JsonSerializer.Serialize(new { faultHook = boundary }));
        await Task.Delay(Timeout.InfiniteTimeSpan);
    }

    private static void Validate(RepositoryPlan plan)
    {
        ArgumentNullException.ThrowIfNull(plan.Repository);
        if (!Path.IsPathFullyQualified(plan.LocalPath) || !Directory.Exists(plan.LocalPath) ||
            !Regex.IsMatch(plan.RemoteName, "^[a-zA-Z0-9_-]+$") ||
            !Regex.IsMatch(plan.BaseBranch, "^[a-zA-Z0-9_-]+$") || !IsSha(plan.ExpectedBaseSha) ||
            plan.PredecessorIssueNumber is <= 0)
            throw new ArgumentException("Invalid repository plan.");
        _ = Origin(plan.ProviderOrigin);
        _ = Origin(plan.AgentOrigin);
    }

    internal static Uri Origin(string origin)
    {
        if (!Uri.TryCreate(origin, UriKind.Absolute, out var uri) || !uri.IsLoopback || uri.Scheme != "http" ||
            uri.AbsolutePath != "/" || uri.UserInfo.Length != 0 || uri.Query.Length != 0 || uri.Fragment.Length != 0)
            throw new ArgumentException("Controlled providers require loopback HTTP origins.");
        return uri;
    }

    private static bool IsSha(string? value) => value is not null && Regex.IsMatch(value, "^[0-9a-f]{40}$");

    private static async Task<RepositoryExecution> PreflightAsync(PostgresImplementationRunStore store,
        string runId, RepositoryExecution execution, bool refreshExpected = false)
    {
        var plan = execution.Plan;
        var expected = execution.Base?.ExpectedSha ?? plan.ExpectedBaseSha;
        string? providerSha = null, localSha = null, blocker = null;
        var predecessorCompleted = false;
        try
        {
            using var client = Client(plan.ProviderOrigin);
            var provider = await client.GetFromJsonAsync<ProviderBaseRead>("base", JsonOptions);
            if (provider?.ContractVersion != "RepositoryEffects/v1" || provider.Repository != plan.Repository ||
                !IsSha(provider.HeadSha) || provider.CompletedIssues is null)
                blocker = "provider-base-invalid";
            else
            {
                providerSha = provider.HeadSha;
                if (refreshExpected) expected = providerSha;
                predecessorCompleted = plan.PredecessorIssueNumber is null || provider.CompletedIssues.Contains(plan.PredecessorIssueNumber.Value);
                localSha = await GitAsync(plan.LocalPath, "rev-parse", "--verify", $"refs/heads/{plan.BaseBranch}^{{commit}}");
                var remote = await GitAsync(plan.LocalPath, "ls-remote", "--exit-code", plan.RemoteName, $"refs/heads/{plan.BaseBranch}");
                var remoteSha = remote.Split('\t')[0];
                blocker = !predecessorCompleted ? "predecessor-not-completed" :
                    remoteSha != providerSha ? "provider-remote-mismatch" :
                    expected != providerSha ? "expected-base-stale" :
                    localSha != providerSha ? "local-base-stale" : null;
            }
        }
        catch (Exception error) when (error is HttpRequestException or TaskCanceledException or JsonException or RepositoryGitException)
        { blocker = "repository-evidence-unavailable"; }
        return await store.RecordRepositoryBaseAsync(runId,
            new(expected, providerSha, localSha, predecessorCompleted), blocker);
    }

    internal static HttpClient Client(string origin) => new(new HttpClientHandler { AllowAutoRedirect = false })
        { BaseAddress = Origin(origin), Timeout = TimeSpan.FromSeconds(5), MaxResponseContentBufferSize = 1024 * 1024 };

    internal static async Task<string> GitAsync(string path, params string[] args)
    {
        var start = new ProcessStartInfo("git") { RedirectStandardOutput = true, RedirectStandardError = true };
        start.ArgumentList.Add("-C");
        start.ArgumentList.Add(path);
        foreach (var arg in args) start.ArgumentList.Add(arg);
        start.Environment["GIT_TERMINAL_PROMPT"] = "0";
        using var process = Process.Start(start) ?? throw new RepositoryGitException();
        var stdout = process.StandardOutput.ReadToEndAsync();
        var stderr = process.StandardError.ReadToEndAsync();
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(10));
        try { await process.WaitForExitAsync(timeout.Token); }
        catch (OperationCanceledException)
        {
            process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            throw new RepositoryGitException();
        }
        await stderr;
        var result = (await stdout).Trim();
        if (process.ExitCode != 0) throw new RepositoryGitException();
        return result;
    }
}

internal sealed class RepositoryGitException : Exception;

internal sealed class RepositoryEffectConflict(string code, RepositoryEffect? effect = null,
    string? observedHeadSha = null, IReadOnlyList<EffectReceipt>? candidates = null) : Exception
{
    public string Code { get; } = code;
    public RepositoryHumanDecision? Decision { get; } = effect is null ? null :
        new(effect.OperationId, code, effect.HeadSha, observedHeadSha, candidates);
}
