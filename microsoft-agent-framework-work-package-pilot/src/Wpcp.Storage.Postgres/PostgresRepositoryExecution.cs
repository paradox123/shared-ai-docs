using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    public async Task EnsureStandaloneAgentAllowedAsync(string runId, CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var check = new NpgsqlCommand("""
            SELECT EXISTS(SELECT 1 FROM wpcp_repository_owners owner
                JOIN wpcp_implementation_runs run USING(repository_id) WHERE run.run_id=@id)
            """, connection);
        check.Parameters.AddWithValue("id", Guid.Parse(runId));
        if (await check.ExecuteScalarAsync(token) is true) throw new RepositoryExecutionRequiredException();
    }

    private async Task<string> QueueRepositoryRecoveryAsync(NpgsqlConnection connection, NpgsqlTransaction transaction,
        StoredRun run, string action, ControlMutation mutation, ActorIdentity actor, CancellationToken token)
    {
        await using var gate = new NpgsqlCommand("SELECT pg_try_advisory_xact_lock(hashtextextended(@key, 0))", connection, transaction);
        gate.Parameters.AddWithValue("key", "agent-delivery:" + run.Correlation.RunId);
        if (await gate.ExecuteScalarAsync(token) is not true) return "worker-delivery-active";
        var execution = await ReadRepositoryExecutionAsync(connection, transaction, run.Correlation.RunId, token);
        if (execution is null) return "repository-execution-required";
        if (execution.Terminal) return "run-terminal";
        if (execution.RequestedAction is not null) return "recovery-already-pending";
        if (action != "adopt" && (mutation.OperationId is not null || mutation.ReceiptId is not null))
            return "invalid-recovery-selection";
        if (action == "adopt" && !(execution.Effects ?? []).Any(e => e.OperationId == mutation.OperationId &&
            e.State == "adoptable" && e.Receipt?.ReceiptId == mutation.ReceiptId && mutation.ReceiptId is not null))
            return "invalid-adopt-selection";
        execution = execution with { RequestedAction = action, SelectedOperationId = mutation.OperationId,
            SelectedReceiptId = mutation.ReceiptId };
        await using var save = new NpgsqlCommand("UPDATE wpcp_repository_executions SET execution=@value WHERE run_id=@id", connection, transaction);
        save.Parameters.AddWithValue("id", Guid.Parse(run.Correlation.RunId));
        AddJson(save, "value", execution);
        await save.ExecuteNonQueryAsync(token);
        await AppendAgentEventAsync(connection, transaction, run, "RepositoryRecoveryRequested",
            new { actor, action, mutation.TargetAttemptId, mutation.OperationId, mutation.ReceiptId }, token);
        return "recovery-requested";
    }

    public Task<RepositoryExecution> RecordRecoveryStateAsync(string runId, string state, CancellationToken token = default) =>
        ChangeRepositoryAsync(runId, (_, current) => current! with { State = state, Blocker = null, RequestedAction = null,
            SelectedOperationId = null, SelectedReceiptId = null, HumanDecision = null }, "RepositoryRecoveryProcessed", token);

    public Task<RepositoryExecution> BindRepositoryExecutionAsync(string runId, RepositoryPlan plan,
        CancellationToken token = default) => ChangeRepositoryAsync(runId, (run, current) =>
        {
            if (run.Correlation.Repository != plan.Repository ||
                _redactionPolicy.ContainsControlledCanary(JsonSerializer.Serialize(plan, JsonOptions)))
                throw new AgentAssignmentConflictException();
            if (current is not null && current.Plan != plan) throw new AgentAssignmentConflictException();
            return current ?? new(plan);
        }, "RepositoryExecutionBound", token);

    public Task<RepositoryExecution> RecordRepositoryBaseAsync(string runId, RepositoryBaseEvidence evidence,
        string? blocker, CancellationToken token = default) =>
        ChangeRepositoryAsync(runId, (_, current) => current! with {
            Base = evidence, Blocker = blocker, State = blocker is null ? "ready" : "preflight-blocked"
        }, "RepositoryBaseChecked", token);

    public Task<RepositoryExecution> IntentRepositoryEffectAsync(string runId, string kind, string target, string? operationId = null,
        CancellationToken token = default) => ChangeRepositoryAsync(runId, (_, current) =>
        {
            var effects = current!.Effects ?? [];
            var operation = new RepositoryEffect(operationId ?? $"{runId}-{kind}-v1", kind, current.Base!.ExpectedSha, target);
            var existing = effects.SingleOrDefault(e => e.Kind == kind);
            if (existing is not null)
            {
                if (existing.OperationId != operation.OperationId || existing.HeadSha != operation.HeadSha || existing.Target != target)
                    throw new AgentAssignmentConflictException();
                return current;
            }
            return current with { Effects = [..effects, operation] };
        }, "RepositoryEffectRequested", token);

    public Task<RepositoryExecution> SetRepositoryEffectAsync(string runId, string operationId,
        string state, EffectReceipt? receipt, CancellationToken token = default) =>
        ChangeRepositoryAsync(runId, (_, current) =>
        {
            var effect = current!.Effects!.Single(e => e.OperationId == operationId);
            if (effect.State == state && effect.Receipt == receipt) return current;
            return current with { Effects = current.Effects.Select(e => e.OperationId == operationId
                ? e with { State = state, Receipt = receipt } : e).ToArray() };
        }, "RepositoryEffectObserved", token);

    public Task<RepositoryExecution> AcquireRepositoryOwnerAsync(string runId, CancellationToken token = default) =>
        ChangeRepositoryAsync(runId, async (connection, transaction, _, current) =>
        {
            await using var read = new NpgsqlCommand(
                "SELECT active_run_id::text FROM wpcp_repository_owners WHERE repository_id=@repo FOR UPDATE", connection, transaction);
            read.Parameters.AddWithValue("repo", current!.Plan.Repository.RepositoryId);
            var owner = await read.ExecuteScalarAsync(token) as string;
            if (owner is not null && owner != runId)
                return current with { State = "waiting", Blocker = "repository-busy", OwnerRunId = owner, Active = false };
            await using var claim = new NpgsqlCommand(
                "UPDATE wpcp_repository_owners SET active_run_id=@id WHERE repository_id=@repo", connection, transaction);
            claim.Parameters.AddWithValue("repo", current.Plan.Repository.RepositoryId);
            claim.Parameters.AddWithValue("id", Guid.Parse(runId));
            await claim.ExecuteNonQueryAsync(token);
            return current with { State = "ready", Blocker = null, OwnerRunId = runId, Active = true };
        }, "RepositoryOwnershipChecked", token);

    public Task<RepositoryExecution> FinishRepositoryAsync(string runId, string state, CancellationToken token = default) =>
        ChangeRepositoryAsync(runId, async (connection, transaction, _, current) =>
        {
            await using var release = new NpgsqlCommand("""
                UPDATE wpcp_repository_owners SET active_run_id=NULL WHERE active_run_id=@id;
                UPDATE wpcp_implementation_runs SET lease_holder=NULL, lease_claimed_at=NULL,
                    lease_epoch=lease_epoch+1 WHERE run_id=@id;
                UPDATE wpcp_run_activities SET state='retired', completed_at=COALESCE(completed_at, now())
                    WHERE run_id=@id AND state='running';
                UPDATE wpcp_activity_attempts SET state='retired', completed_at=COALESCE(completed_at, now())
                    WHERE activity_id IN (SELECT activity_id FROM wpcp_run_activities WHERE run_id=@id) AND state='running';
                UPDATE wpcp_agent_sessions SET receipt=jsonb_set(receipt, '{state}', '"retired"')
                    WHERE run_id=@id AND receipt->>'state'='running';
                """, connection, transaction);
            release.Parameters.AddWithValue("id", Guid.Parse(runId));
            await release.ExecuteNonQueryAsync(token);
            return current! with { State = state, Blocker = null, Terminal = true, Active = false, OwnerRunId = null, RequestedAction = null };
        }, "RepositoryExecutionFinished", token);

    public Task<RepositoryExecution> BlockRepositoryAsync(string runId, string code,
        RepositoryHumanDecision? decision = null, CancellationToken token = default) =>
        ChangeRepositoryAsync(runId, (_, current) => current! with { State = "human-decision", Blocker = code, RequestedAction = null,
            HumanDecision = decision ?? new(current!.Effects?.LastOrDefault()?.OperationId, code, current.Base?.ExpectedSha) },
            "RepositoryHumanDecisionRequired", token);

    private Task<RepositoryExecution> ChangeRepositoryAsync(string runId,
        Func<StoredRun, RepositoryExecution?, RepositoryExecution> change, string eventType, CancellationToken token) =>
        ChangeRepositoryAsync(runId, (_, _, run, current) => Task.FromResult(change(run, current)), eventType, token);

    private async Task<RepositoryExecution> ChangeRepositoryAsync(string runId,
        Func<NpgsqlConnection, NpgsqlTransaction, StoredRun, RepositoryExecution?, Task<RepositoryExecution>> change,
        string eventType, CancellationToken token)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await using (var rowLock = new NpgsqlCommand(
            "SELECT run_id FROM wpcp_implementation_runs WHERE run_id=@id FOR UPDATE", connection, transaction))
        {
            rowLock.Parameters.AddWithValue("id", Guid.Parse(runId));
            await rowLock.ExecuteScalarAsync(token);
        }
        var run = await FindRunAsync(connection, transaction, runId, token)
            ?? throw new InvalidOperationException("Unknown run.");
        var previous = await ReadRepositoryExecutionAsync(connection, transaction, runId, token);
        var next = await change(connection, transaction, run, previous);
        if (previous is null)
        {
            var config = next.Plan with { ExpectedBaseSha = "", PredecessorIssueNumber = null };
            await using var register = new NpgsqlCommand("""
                INSERT INTO wpcp_repository_owners(repository_id, configuration) VALUES (@repo, @config)
                ON CONFLICT (repository_id) DO NOTHING;
                SELECT configuration::text FROM wpcp_repository_owners WHERE repository_id=@repo FOR UPDATE;
                """, connection, transaction);
            register.Parameters.AddWithValue("repo", next.Plan.Repository.RepositoryId);
            AddJson(register, "config", config);
            var stored = await register.ExecuteScalarAsync(token) as string;
            if (stored is null || Deserialize<RepositoryPlan>(stored) != config)
                throw new AgentAssignmentConflictException();
        }
        if (next != previous)
        {
            await using var save = new NpgsqlCommand("""
                INSERT INTO wpcp_repository_executions VALUES (@id, @value)
                ON CONFLICT (run_id) DO UPDATE SET execution=EXCLUDED.execution;
                UPDATE wpcp_implementation_runs SET state=@state, head_sha=COALESCE(@head, head_sha) WHERE run_id=@id;
                """, connection, transaction);
            save.Parameters.AddWithValue("id", Guid.Parse(runId));
            save.Parameters.AddWithValue("state", next.State);
            AddNullable(save, "head", NpgsqlTypes.NpgsqlDbType.Text,
                next.Base is { } evidence && evidence.ExpectedSha == evidence.ProviderSha && evidence.LocalSha == evidence.ProviderSha
                    && evidence.PredecessorCompleted ? evidence.ProviderSha : null);
            AddJson(save, "value", RedactAgentValue(JsonSerializer.SerializeToElement(next, JsonOptions)).Value);
            await save.ExecuteNonQueryAsync(token);
            await AppendAgentEventAsync(connection, transaction, run, eventType, next, token);
        }
        await transaction.CommitAsync(token);
        return next;
    }

    private static async Task<RepositoryExecution?> ReadRepositoryExecutionAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, string runId, CancellationToken token)
    {
        await using var read = new NpgsqlCommand(
            "SELECT execution::text FROM wpcp_repository_executions WHERE run_id=@id", connection, transaction);
        read.Parameters.AddWithValue("id", Guid.Parse(runId));
        return await read.ExecuteScalarAsync(token) is string raw ? Deserialize<RepositoryExecution>(raw) : null;
    }

    private const string RepositorySchema = """
        CREATE TABLE IF NOT EXISTS wpcp_repository_owners (
            repository_id text PRIMARY KEY, configuration jsonb NOT NULL,
            active_run_id uuid REFERENCES wpcp_implementation_runs(run_id)
        );
        CREATE TABLE IF NOT EXISTS wpcp_repository_executions (
            run_id uuid PRIMARY KEY REFERENCES wpcp_implementation_runs(run_id), execution jsonb NOT NULL
        );
        """;
}
