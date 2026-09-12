using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    public async Task<ActiveAgentAttempt> PrepareActiveAgentAsync(string runId, string activityKey,
        string origin, CancellationToken token = default)
    {
        if (string.IsNullOrWhiteSpace(activityKey) || _redactionPolicy.ContainsControlledCanary(activityKey))
            throw new ArgumentException("Invalid activity key.");
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await LockRunAsync(connection, transaction, runId, token);
        var run = await FindRunAsync(connection, transaction, runId, token)
            ?? throw new InvalidOperationException("Unknown run.");
        if (await ReadRepositoryExecutionAsync(connection, transaction, runId, token) is not null)
            throw new RepositoryExecutionRequiredException();
        await using var read = new NpgsqlCommand(
            "SELECT state::text, adapter_origin FROM wpcp_live_attempts WHERE run_id=@run AND activity_key=@key", connection, transaction);
        read.Parameters.AddWithValue("run", Guid.Parse(runId));
        read.Parameters.AddWithValue("key", activityKey);
        await using (var reader = await read.ExecuteReaderAsync(token))
        {
            if (await reader.ReadAsync(token))
            {
                if (reader.GetString(1) != origin) throw new AgentAssignmentConflictException();
                return Deserialize<ActiveAgentAttempt>(reader.GetString(0));
            }
        }
        await using var mode = new NpgsqlCommand("""
            SELECT pg_advisory_xact_lock_shared(hashtextextended(@key, 0));
            SELECT EXISTS(SELECT 1 FROM wpcp_repository_owners WHERE repository_id=@repo);
            """, connection, transaction);
        mode.Parameters.AddWithValue("key", "repository-mode:" + run.Correlation.RepositoryId);
        mode.Parameters.AddWithValue("repo", run.Correlation.RepositoryId);
        await using (var reader = await mode.ExecuteReaderAsync(token))
        {
            await reader.NextResultAsync(token);
            await reader.ReadAsync(token);
            if (reader.GetBoolean(0)) throw new RepositoryExecutionRequiredException();
        }
        var attempt = new ActiveAgentAttempt(Guid.NewGuid().ToString(), Guid.NewGuid().ToString(),
            Guid.NewGuid().ToString(), "running", 0,
            new(Guid.NewGuid().ToString(), 0, null, "controlled active operation"), []);
        await using var insert = new NpgsqlCommand("""
            INSERT INTO wpcp_run_activities VALUES (@activity, @run, 'live-codex', 'running', @now, NULL);
            INSERT INTO wpcp_activity_attempts VALUES (@attempt, @activity, 1, 'running', @now, NULL);
            INSERT INTO wpcp_live_attempts (attempt_id, run_id, activity_key, adapter_origin, state) VALUES (@attempt, @run, @key, @origin, @state);
            """, connection, transaction);
        insert.Parameters.AddWithValue("activity", Guid.Parse(attempt.ActivityId));
        insert.Parameters.AddWithValue("attempt", Guid.Parse(attempt.AttemptId));
        insert.Parameters.AddWithValue("run", Guid.Parse(runId));
        insert.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
        insert.Parameters.AddWithValue("key", activityKey);
        insert.Parameters.AddWithValue("origin", origin);
        AddJson(insert, "state", attempt);
        await insert.ExecuteNonQueryAsync(token);
        await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentOperationPrepared", attempt, token);
        await SaveActiveAttemptAsync(connection, transaction, runId, attempt, token);
        await transaction.CommitAsync(token);
        return attempt;
    }

    public async Task<ActiveAgentDecision> DecideActiveAgentAsync(string runId, string mode,
        ActiveAgentCommandRequest request,
        Func<RepositoryBinding, CancellationToken, Task<RepositoryAccess>> authorize,
        CancellationToken token = default)
    {
        if (!Guid.TryParse(runId, out _)) return new("implementation-run-not-found", null);
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await AcquireLockAsync(connection, transaction, "live-command:" + request.CommandId, token);
        await LockRunAsync(connection, transaction, runId, token);
        var run = await FindRunAsync(connection, transaction, runId, token);
        if (run is null) return new("implementation-run-not-found", null);
        var (control, access) = await RevalidateControlAccessAsync(connection, transaction, run, authorize, token);
        ActiveAgentCommand? accepted = null;
        var code = !access.IsHuman || !access.CanRead ? access.FailureCode ?? "repository-access-denied" :
            !access.CanContribute ? "repository-contribution-required" :
            control.Holder != access.Actor ? "control-lease-required" :
            request.TargetAttemptId is null ? "explicit-target-required" :
            !Guid.TryParse(request.TargetAttemptId, out _) || !Guid.TryParse(request.CommandId, out _) ||
                !ValidActiveCommand(mode, request) ? "invalid-agent-command" : "check";
        if (code == "check")
        {
            var digest = Digest(new { runId, mode, request.TargetAttemptId,
                message = _redactionPolicy.Redact(request.Message).Value,
                reason = _redactionPolicy.Redact(request.Reason).Value, request.Scope });
            await using var replay = new NpgsqlCommand(
                "SELECT run_id::text, attempt_id::text, digest FROM wpcp_live_commands WHERE command_id=@command", connection, transaction);
            replay.Parameters.AddWithValue("command", Guid.Parse(request.CommandId));
            string? previousAttempt = null;
            await using (var reader = await replay.ExecuteReaderAsync(token))
            {
                if (await reader.ReadAsync(token))
                {
                    if (reader.GetString(0) != runId || reader.GetString(2) != digest) code = "agent-command-conflict";
                    else previousAttempt = reader.GetString(1);
                }
            }
            if (previousAttempt is not null)
            {
                var saved = await ReadActiveAttemptAsync(connection, transaction, runId, previousAttempt, token);
                accepted = saved!.Commands.Single(c => c.CommandId == request.CommandId);
                code = "agent-command-accepted";
            }
            else if (code == "check")
            {
                code = request.ExpectedRunVersion != control.RunVersion ? "stale-run-version" :
                    request.ExpectedHeadSha != control.HeadSha ? "stale-head-sha" :
                    request.LeaseEpoch != control.LeaseEpoch ? "stale-lease-epoch" : "accept";
                var attempt = await ReadActiveAttemptAsync(connection, transaction, runId, request.TargetAttemptId!, token);
                if (code == "accept" && (attempt is null || attempt.State != "running")) code = "target-attempt-not-active";
                if (code == "accept" && (mode is "interrupt" or "cancel") && attempt!.CurrentOperation?.StopRequested == true)
                    code = "operation-stop-pending";
                if (code == "accept")
                {
                    accepted = new(request.CommandId, attempt!.AttemptId, mode, control.RunVersion + 1,
                        _redactionPolicy.Redact(request.Message).Value, _redactionPolicy.Redact(request.Reason).Value,
                        request.Scope, State: mode == "cancel" ? "stopping" : "queued",
                        QueuePosition: mode == "cancel" ? null : mode == "interrupt" ? 1 : attempt.Commands.Count(c => c.State == "queued") + 1);
                    await using var insert = new NpgsqlCommand(
                        "INSERT INTO wpcp_live_commands (command_id, run_id, attempt_id, digest) VALUES (@command, @run, @attempt, @digest)", connection, transaction);
                    insert.Parameters.AddWithValue("command", Guid.Parse(request.CommandId));
                    insert.Parameters.AddWithValue("run", Guid.Parse(runId));
                    insert.Parameters.AddWithValue("attempt", Guid.Parse(attempt.AttemptId));
                    insert.Parameters.AddWithValue("digest", digest);
                    await insert.ExecuteNonQueryAsync(token);
                    await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentCommandAccepted",
                        new { actor = access.Actor, attemptId = attempt.AttemptId, command = accepted, message = request.Message, reason = request.Reason }, token);
                    attempt = attempt with { Commands = [.. attempt.Commands, accepted] };
                    if (mode is "interrupt" or "cancel")
                    {
                        attempt = attempt with { FenceEpoch = attempt.FenceEpoch + 1,
                            State = mode == "cancel" && request.Scope == "attempt" ? "cancelling" : attempt.State,
                            CurrentOperation = attempt.CurrentOperation! with { StopRequested = true, ProcessStatus = "stop-pending" } };
                        await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentStopRequested",
                            new { actor = access.Actor, attempt.AttemptId, attempt.FenceEpoch, operation = attempt.CurrentOperation, command = accepted,
                                repairRoundConsumed = false }, token);
                    }
                    if (mode == "cancel" && request.Scope == "attempt")
                    {
                        foreach (var queued in attempt.Commands.Where(c => c.State == "queued"))
                            await AppendAgentEventAsync(connection, transaction, run, "ActiveAgentCommandRejected",
                                new { attempt.AttemptId, queued.CommandId, reason = "attempt-cancelled", cancelCommandId = request.CommandId }, token);
                        attempt = attempt with { Commands = attempt.Commands.Select(c => c.State == "queued"
                            ? c with { State = "rejected", RejectionReason = "attempt-cancelled", QueuePosition = null } : c).ToArray() };
                    }
                    attempt = RepositionActiveQueue(attempt);
                    accepted = attempt.Commands.Single(c => c.CommandId == request.CommandId);
                    await SaveActiveAttemptAsync(connection, transaction, runId, attempt, token);
                    control = await ReadControlStateAsync(connection, transaction,
                        (await FindRunAsync(connection, transaction, runId, token))!, token);
                    code = "agent-command-accepted";
                }
            }
        }
        await AppendAuditAsync(connection, transaction, runId, mode is "queue" or "interrupt" or "cancel" ? mode : "invalid", code, access.Actor, token);
        await transaction.CommitAsync(token);
        return new(code, access.CanRead ? control : null, accepted);
    }

    private static bool ValidActiveCommand(string mode, ActiveAgentCommandRequest request) => mode switch
    {
        "queue" => !string.IsNullOrWhiteSpace(request.Message) && request.Scope is null && request.Reason is null,
        "interrupt" => !string.IsNullOrWhiteSpace(request.Message) && !string.IsNullOrWhiteSpace(request.Reason) && request.Scope is null,
        "cancel" => request.Message is null && !string.IsNullOrWhiteSpace(request.Reason) && request.Scope is "operation" or "attempt",
        _ => false,
    };

    private static async Task<ActiveAgentAttempt?> ReadActiveAttemptAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, string runId, string attemptId, CancellationToken token)
    {
        await using var command = new NpgsqlCommand(
            "SELECT state::text FROM wpcp_live_attempts WHERE run_id=@run AND attempt_id=@attempt", connection, transaction);
        command.Parameters.AddWithValue("run", Guid.Parse(runId));
        command.Parameters.AddWithValue("attempt", Guid.Parse(attemptId));
        return await command.ExecuteScalarAsync(token) is string raw ? Deserialize<ActiveAgentAttempt>(raw) : null;
    }

    private static async Task SaveActiveAttemptAsync(NpgsqlConnection connection, NpgsqlTransaction transaction,
        string runId, ActiveAgentAttempt attempt, CancellationToken token)
    {
        await using var save = new NpgsqlCommand("""
            UPDATE wpcp_live_attempts SET state=@state WHERE attempt_id=@attempt;
            UPDATE wpcp_activity_attempts SET state=@status,
                completed_at=CASE WHEN @status IN ('running', 'cancelling') THEN NULL ELSE COALESCE(completed_at, now()) END WHERE attempt_id=@attempt;
            UPDATE wpcp_run_activities SET state=@status,
                completed_at=CASE WHEN @status IN ('running', 'cancelling') THEN NULL ELSE COALESCE(completed_at, now()) END WHERE activity_id=@activity;
            UPDATE wpcp_implementation_runs SET state=CASE WHEN EXISTS
                (SELECT 1 FROM wpcp_live_attempts WHERE run_id=@run AND state->>'state'='running')
                THEN 'running' WHEN EXISTS
                (SELECT 1 FROM wpcp_live_attempts WHERE run_id=@run AND state->>'state'='cancelling')
                THEN 'cancelling' ELSE @status END WHERE run_id=@run;
            """, connection, transaction);
        AddJson(save, "state", attempt);
        save.Parameters.AddWithValue("status", attempt.State);
        save.Parameters.AddWithValue("attempt", Guid.Parse(attempt.AttemptId));
        save.Parameters.AddWithValue("activity", Guid.Parse(attempt.ActivityId));
        save.Parameters.AddWithValue("run", Guid.Parse(runId));
        await save.ExecuteNonQueryAsync(token);
    }

    private const string ActiveAgentSchema = """
        CREATE TABLE IF NOT EXISTS wpcp_live_attempts (
            attempt_id uuid PRIMARY KEY REFERENCES wpcp_activity_attempts(attempt_id),
            run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            activity_key text NOT NULL, adapter_origin text NOT NULL, state jsonb NOT NULL,
            UNIQUE(run_id, activity_key));
        CREATE TABLE IF NOT EXISTS wpcp_live_commands (
            command_id uuid PRIMARY KEY, run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            attempt_id uuid NOT NULL REFERENCES wpcp_live_attempts(attempt_id), digest text NOT NULL);
        CREATE TABLE IF NOT EXISTS wpcp_live_receipts (
            operation_key uuid NOT NULL, digest text NOT NULL, PRIMARY KEY(operation_key, digest));
        """;
}
