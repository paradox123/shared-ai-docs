using System.Text.Json;
using Npgsql;
using NpgsqlTypes;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    private static readonly string[] ContinuationActions =
        ["resume", "fork", "fresh-retry", "handoff", "write"];

    private async Task<(string Code, ContinuationOperation? Operation)> QueueHumanRequestActionAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        StoredRun run,
        string action,
        ControlMutation mutation,
        CancellationToken token)
    {
        if (!ContinuationActions.Contains(action, StringComparer.Ordinal))
            return ("invalid-control-action", null);
        if (mutation.RequestId is null || mutation.CommandId is null ||
            !Guid.TryParse(mutation.RequestId, out _) || !Guid.TryParse(mutation.CommandId, out _))
            return ("invalid-control-mutation", null);

        var safeMessage = _redactionPolicy.Redact(mutation.Message);
        var digest = ContinuationDigest(action, mutation, safeMessage.Value);
        var existing = await ReadContinuationCommandAsync(connection, transaction, mutation.CommandId, token);
        if (existing is not null)
        {
            if (existing.RunId != run.Correlation.RunId || existing.PayloadDigest != digest)
                return ("continuation-command-conflict", null);
            return (existing.State == "applied" ? "continuation-applied" : "continuation-requested",
                existing.ToOperation());
        }

        var source = await ReadAgentAttemptAsync(connection, transaction, run.Correlation.RunId,
            mutation.TargetAttemptId, token);
        var request = source?.Session.HumanRequest;
        if (source is null || request is null || request.RequestId != mutation.RequestId ||
            (action != "write" && request.State != "open"))
            return ("human-request-not-open", null);
        if (source.Session.SessionId is null)
            return ("human-request-session-unavailable", null);
        if (action == "write" && !source.Session.OpenedInCodex)
            return ("session-not-opened", null);
        if (action == "handoff" && source.Session.OpenInCodex?.Mode != "handoff-confirmation-required")
            return ("handoff-not-required", null);

        var commandId = mutation.CommandId;
        var operationKey = Guid.NewGuid().ToString("D");
        var message = action == "write" ? safeMessage.Value : null;
        var resultAttemptId = mutation.TargetAttemptId;
        string? resultSessionId = source.Session.SessionId;
        string? parentSessionId = null;
        string? origin = null;
        var state = "pending";

        if (action is "fork" or "fresh-retry" or "handoff")
        {
            var activityId = Guid.NewGuid().ToString("D");
            resultAttemptId = Guid.NewGuid().ToString("D");
            parentSessionId = action == "fresh-retry" ? null : source.Session.SessionId;
            origin = action == "handoff" ? "handoff" : action == "fork" ? "fork" : null;
            resultSessionId = null;
            var nextSession = new AgentSession(
                operationKey,
                Status: "continuation-pending",
                ContractVersion: source.Session.ContractVersion,
                OpenInCodex: source.Session.OpenInCodex,
                Lineage: new SessionLineage(parentSessionId, origin));
            var nextReceipt = new AgentAttemptReceipt(
                run.Correlation.RunId,
                activityId,
                resultAttemptId,
                "continuation-pending",
                source.AdapterOrigin,
                source.RejectBlocked,
                nextSession);
            await using var insert = new NpgsqlCommand("""
                INSERT INTO wpcp_run_activities (activity_id, run_id, activity_type, state, started_at, completed_at)
                VALUES (@activity, @run, 'codex-continuation', 'continuation-pending', @now, NULL);
                INSERT INTO wpcp_activity_attempts (attempt_id, activity_id, attempt_number, state, started_at, completed_at)
                VALUES (@attempt, @activity, 1, 'continuation-pending', @now, NULL);
                INSERT INTO wpcp_agent_sessions (run_id, attempt_id, receipt) VALUES (@run, @attempt, @receipt);
                """, connection, transaction);
            insert.Parameters.AddWithValue("activity", Guid.Parse(activityId));
            insert.Parameters.AddWithValue("attempt", Guid.Parse(resultAttemptId));
            insert.Parameters.AddWithValue("run", Guid.Parse(run.Correlation.RunId));
            insert.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
            AddJson(insert, "receipt", nextReceipt);
            await insert.ExecuteNonQueryAsync(token);
        }
        else if (action == "resume")
        {
            origin = "resume";
        }
        else if (action == "write")
        {
            origin = "interactive-write";
        }

        var operation = new ContinuationOperation(
            commandId, mutation.RequestId, action, mutation.TargetAttemptId, source.Session.SessionId,
            resultAttemptId, resultSessionId, operationKey, state, parentSessionId, origin,
            source.AdapterOrigin, message, run.Correlation.RunId);

        await InsertContinuationCommandAsync(connection, transaction, run, operation, digest, token);
        if (action != "write")
        {
            await ResolveHumanRequestAsync(connection, transaction, run, source, request, action, operation, token);
        }
        else
        {
            await AppendAgentEventAsync(connection, transaction, run, "AgentInteractiveWriteRequested",
                new { attemptId = operation.SourceAttemptId, operation.CommandId, operation.RequestId, operation.SourceAttemptId,
                    operation.SourceSessionId, operation.OperationKey, message = mutation.Message }, token);
        }
        if (action is "fork" or "fresh-retry" or "handoff" or "resume")
        {
            await AppendAgentEventAsync(connection, transaction, run, "HumanRequestContinuationRequested",
                new { attemptId = operation.SourceAttemptId, operation.CommandId, operation.RequestId, operation.Action, operation.SourceAttemptId,
                    operation.SourceSessionId, operation.ResultAttemptId, operation.ParentSessionId,
                    operation.Origin, operation.OperationKey }, token);
        }
        return (state == "applied" ? "continuation-applied" : "continuation-requested", operation);
    }

    private async Task<ContinuationOperation?> QueueSessionOpenUnderLockAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        StoredRun run,
        string attemptId,
        SessionOpenCommand command,
        CancellationToken token)
    {
        var runId = run.Correlation.RunId;
        var source = await ReadAgentAttemptAsync(connection, transaction, runId, attemptId, token);
        var request = source?.Session.HumanRequest;
        if (source?.Session.SessionId is null || request is null || request.RequestId != command.RequestId)
            return null;
        var digest = Digest(new { action = "open", command.RequestId, attemptId });
        var existing = await ReadContinuationCommandAsync(connection, transaction, command.CommandId, token);
        if (existing is not null)
        {
            if (existing.RunId != runId || existing.PayloadDigest != digest)
                throw new ArgumentException("Conflicting session-open command.");
            return existing.ToOperation();
        }
        var sameSession = source.Session.OpenInCodex is { Mode: "same-session", SameSession: true };
        var state = sameSession ? "pending" : "limitation";
        var operation = new ContinuationOperation(command.CommandId, command.RequestId, "open", attemptId,
            source.Session.SessionId, attemptId, source.Session.SessionId, Guid.NewGuid().ToString("D"), state,
            source.Session.Lineage?.ParentSessionId, source.Session.Lineage?.Origin, source.AdapterOrigin,
            RunId: runId);
        await InsertContinuationCommandAsync(connection, transaction, run, operation, digest, token);
        await AppendAgentEventAsync(connection, transaction, run,
            sameSession ? "CodexSessionOpenRequested" : "CodexSessionOpenCapabilityDisclosed",
            new { attemptId, operation.CommandId, operation.RequestId, operation.SourceAttemptId,
                operation.SourceSessionId, capability = source.Session.OpenInCodex }, token);
        return operation;
    }

    public async Task<ContinuationOperation?> CompleteContinuationAdapterAsync(
        string runId,
        string commandId,
        JsonElement adapterReceipt,
        CancellationToken token = default)
    {
        if (!Guid.TryParse(runId, out _) || !Guid.TryParse(commandId, out _)) return null;
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await LockRunAsync(connection, transaction, runId, token);
        var run = await FindRunAsync(connection, transaction, runId, token);
        var command = await ReadContinuationCommandAsync(connection, transaction, commandId, token);
        if (run is null || command is null || command.RunId != runId) return null;
        if (command.State == "applied")
        {
            await transaction.CommitAsync(token);
            return command.ToOperation();
        }
        var safeReceipt = await SanitizeEvidenceAsync(connection, transaction, runId, adapterReceipt, token);
        var operation = command.ToOperation();
        RequireReceiptString(safeReceipt.Value, "contractVersion", "AgentSessionAdapter/v1");
        RequireReceiptString(safeReceipt.Value, "operationKey", operation.OperationKey);
        if (command.Action is "fork" or "fresh-retry" or "handoff")
        {
            if (!TryReadSessionId(safeReceipt.Value, out var sessionId))
                throw new ArgumentException("Continuation adapter returned no session identity.");
            if (sessionId == operation.SourceSessionId)
                throw new ArgumentException("Continuation adapter reused the source session identity.");
            RequireReceiptString(safeReceipt.Value, "sourceSessionId", operation.SourceSessionId);
            RequireReceiptString(safeReceipt.Value, "action", command.Action);
            RequireReceiptString(safeReceipt.Value, "parentSessionId", operation.ParentSessionId);
            var target = await ReadAgentAttemptAsync(connection, transaction, runId, command.ResultAttemptId, token)
                ?? throw new InvalidOperationException("Continuation target is missing.");
            if (target.Session.SessionId is not null && target.Session.SessionId != sessionId)
                throw new ArgumentException("Conflicting continuation session identity.");
            var source = await ReadAgentAttemptAsync(connection, transaction, runId, operation.SourceAttemptId, token)
                ?? throw new InvalidOperationException("Continuation source is missing.");
            var capability = ReadOpenInCodexCapability(safeReceipt.Value) ?? target.Session.OpenInCodex;
            var control = await ReadHumanRequestControlContextAsync(connection, transaction, run, token);
            var freshRetry = command.Action == "fresh-retry";
            var request = new HumanRequest(
                Guid.NewGuid().ToString("D"), target.AttemptId, sessionId, "awaiting-human", control.HeadSha,
                freshRetry ? "Fresh retry requires human direction." :
                    source.Session.HumanRequest?.Problem ?? "Continuation session requires human direction.",
                freshRetry ? [] : source.Session.HumanRequest?.Evidence ?? [], HumanRequestAllowedActions(capability),
                ExpectedRunVersion: run.LastPosition + 2, LeaseEpoch: control.LeaseEpoch);
            var session = target.Session with { SessionId = sessionId, Status = "waiting-human",
                OpenInCodex = capability, HumanRequest = request };
            await UpdateAgentReceiptAsync(connection, transaction, target with { State = "waiting-human", Session = session }, token);
            await using (var state = new NpgsqlCommand("""
                UPDATE wpcp_run_activities SET state='waiting-human' WHERE activity_id=@activity;
                UPDATE wpcp_activity_attempts SET state='waiting-human' WHERE attempt_id=@attempt;
                """, connection, transaction))
            {
                state.Parameters.AddWithValue("activity", Guid.Parse(target.ActivityId));
                state.Parameters.AddWithValue("attempt", Guid.Parse(target.AttemptId));
                await state.ExecuteNonQueryAsync(token);
            }
            operation = operation with { ResultSessionId = sessionId, ResultRequestId = request.RequestId, State = "applied" };
            await AppendAgentEventAsync(connection, transaction, run, "HumanRequestContinuationApplied",
                new { attemptId = operation.ResultAttemptId, operation.CommandId, operation.RequestId, operation.Action, operation.SourceAttemptId,
                    operation.SourceSessionId, operation.ResultAttemptId, operation.ResultSessionId,
                    operation.ResultRequestId, operation.ParentSessionId, operation.Origin, operation.OperationKey }, token);
            var requestEventId = await AppendAgentEventAsync(connection, transaction, run, "HumanRequestCreated",
                new { request.RequestId, request.AttemptId, request.SessionId, request.Phase,
                    request.ExpectedHeadSha, request.ExpectedRunVersion, request.LeaseEpoch,
                    request.Problem, request.Evidence, request.AllowedActions }, token);
            await UpdateAgentReceiptAsync(connection, transaction, target with { State = "waiting-human",
                Session = session with { HumanRequest = request with { CreatedEventId = requestEventId } } }, token);
        }
        else if (command.Action == "resume")
        {
            if (!TryReadSessionId(safeReceipt.Value, out var sessionId) || sessionId != operation.SourceSessionId)
                throw new ArgumentException("Resume adapter returned a different session identity.");
            operation = operation with { State = "applied" };
            await AppendAgentEventAsync(connection, transaction, run, "HumanRequestContinuationApplied",
                new { attemptId = operation.SourceAttemptId, operation.CommandId, operation.RequestId, operation.Action, operation.SourceAttemptId,
                    operation.SourceSessionId, operation.ResultAttemptId, operation.ResultSessionId,
                    operation.OperationKey }, token);
        }
        else if (command.Action == "write")
        {
            if (!TryReadSessionId(safeReceipt.Value, out var sessionId) || sessionId != operation.SourceSessionId)
                throw new ArgumentException("Interactive adapter returned a different session identity.");
            if (string.IsNullOrEmpty(operation.Message))
                throw new ArgumentException("Interactive operation has no canonical message.");
            RequireReceiptString(safeReceipt.Value, "message", operation.Message);
            await AppendInteractionEventsAsync(connection, transaction, run, operation, safeReceipt.Value, token);
            operation = operation with { State = "applied" };
        }
        else if (command.Action == "open")
        {
            if (!TryReadSessionId(safeReceipt.Value, out var sessionId) || sessionId != operation.SourceSessionId ||
                !ReadReceiptBoolean(safeReceipt.Value, "opened"))
                throw new ArgumentException("Open adapter did not confirm the selected session.");
            var source = await ReadAgentAttemptAsync(connection, transaction, runId, operation.SourceAttemptId, token)
                ?? throw new InvalidOperationException("Open target is missing.");
            await UpdateAgentReceiptAsync(connection, transaction,
                source with { Session = source.Session with { OpenedInCodex = true } }, token);
            await AppendAgentEventAsync(connection, transaction, run, "CodexSessionOpened",
                new { attemptId = operation.SourceAttemptId, operation.CommandId, operation.RequestId, operation.SourceAttemptId,
                    operation.SourceSessionId, operation.OperationKey }, token);
            operation = operation with { State = "applied" };
        }
        else
        {
            throw new ArgumentException("Continuation action has no adapter completion.");
        }
        await UpdateContinuationCommandAsync(connection, transaction, operation,
            await ExternalizeLargeValueAsync(connection, transaction, runId, safeReceipt.Value, safeReceipt.Occurred, token), token);
        await transaction.CommitAsync(token);
        return operation;
    }

    /// <summary>
    /// A host-owned recovery loop reads only intents made durable by a previously
    /// authorized decision.  It never reconstructs an operation from caller input.
    /// </summary>
    public async Task<IReadOnlyList<ContinuationOperation>> GetPendingContinuationsAsync(
        CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var command = new NpgsqlCommand("""
            SELECT command_id::text, run_id::text, request_id::text, action, payload_digest,
                   source_attempt_id::text, source_session_id, result_attempt_id::text, result_session_id,
                   result_request_id::text, operation_key::text, state, parent_session_id, origin, adapter_origin, message
            FROM wpcp_human_request_commands WHERE state='pending' ORDER BY created_at, command_id;
            """, connection);
        await using var reader = await command.ExecuteReaderAsync(token);
        var operations = new List<ContinuationOperation>();
        while (await reader.ReadAsync(token))
        {
            var commandRecord = ReadStoredContinuationCommand(reader);
            operations.Add(commandRecord.ToOperation());
        }
        return operations;
    }

    public async Task<ContinuationReceipt?> GetContinuationReceiptAsync(
        string runId, string commandId, CancellationToken token = default)
    {
        if (!Guid.TryParse(runId, out _) || !Guid.TryParse(commandId, out _)) return null;
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var command = new NpgsqlCommand("""
            SELECT command_id::text, run_id::text, request_id::text, action, payload_digest,
                   source_attempt_id::text, source_session_id, result_attempt_id::text, result_session_id,
                   result_request_id::text, operation_key::text, state, parent_session_id, origin, adapter_origin,
                   message, adapter_receipt::text
            FROM wpcp_human_request_commands WHERE run_id=@run AND command_id=@command;
            """, connection);
        command.Parameters.AddWithValue("run", Guid.Parse(runId));
        command.Parameters.AddWithValue("command", Guid.Parse(commandId));
        await using var reader = await command.ExecuteReaderAsync(token);
        if (!await reader.ReadAsync(token)) return null;
        var operation = ReadStoredContinuationCommand(reader).ToOperation();
        return new ContinuationReceipt(operation,
            reader.IsDBNull(16) ? null : Deserialize<JsonElement>(reader.GetString(16)));
    }

    private async Task<(string Code, ContinuationOperation? Operation)> ReplayHumanRequestActionAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        StoredRun run,
        string action,
        ControlMutation mutation,
        CancellationToken token)
    {
        if (mutation.CommandId is null || !Guid.TryParse(mutation.CommandId, out _)) return ("invalid-control-mutation", null);
        var existing = await ReadContinuationCommandAsync(connection, transaction, mutation.CommandId, token);
        if (existing is null) return ("continuation-command-not-found", null);
        if (existing.RunId != run.Correlation.RunId || existing.PayloadDigest !=
            ContinuationDigest(action, mutation, _redactionPolicy.Redact(mutation.Message).Value))
            return ("continuation-command-conflict", null);
        return (existing.State == "applied" ? "continuation-applied" : "continuation-requested", existing.ToOperation());
    }

    private async Task ResolveHumanRequestAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        StoredRun run,
        AgentAttemptReceipt source,
        HumanRequest request,
        string action,
        ContinuationOperation operation,
        CancellationToken token)
    {
        var resolved = source.Session with { HumanRequest = request with { State = "resolved" } };
        await UpdateAgentReceiptAsync(connection, transaction, source with { Session = resolved }, token);
        await AppendAgentEventAsync(connection, transaction, run, "HumanRequestResolved",
            new { attemptId = operation.SourceAttemptId, operation.CommandId, operation.RequestId, operation.Action, operation.SourceAttemptId,
                operation.SourceSessionId, operation.ResultAttemptId, operation.ResultSessionId,
                operation.ParentSessionId, operation.Origin }, token);
    }

    private async Task AppendInteractionEventsAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        StoredRun run,
        ContinuationOperation operation,
        JsonElement receipt,
        CancellationToken token)
    {
        if (receipt.ValueKind != JsonValueKind.Object || !receipt.TryGetProperty("events", out var events) ||
            events.ValueKind != JsonValueKind.Array)
            throw new ArgumentException("Interactive adapter receipt has no events.");
        foreach (var item in events.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.Object || !item.TryGetProperty("type", out var type) ||
                type.ValueKind != JsonValueKind.String || !item.TryGetProperty("data", out var data))
                throw new ArgumentException("Interactive adapter event is malformed.");
            await AppendAgentEventAsync(connection, transaction, run, "AgentInteractiveObservation",
                new { attemptId = operation.SourceAttemptId, operation.CommandId, operation.RequestId, operation.SourceAttemptId,
                    operation.SourceSessionId, operation.OperationKey, type = type.GetString(), data }, token);
        }
        await AppendAgentEventAsync(connection, transaction, run, "AgentInteractiveWriteApplied",
            new { attemptId = operation.SourceAttemptId, operation.CommandId, operation.RequestId, operation.SourceAttemptId,
                operation.SourceSessionId, operation.OperationKey }, token);
    }

    private static bool TryReadSessionId(JsonElement value, out string sessionId)
    {
        sessionId = string.Empty;
        return value.ValueKind == JsonValueKind.Object && value.TryGetProperty("sessionId", out var property) &&
            property.ValueKind == JsonValueKind.String && Guid.TryParse(property.GetString(), out _) &&
            (sessionId = property.GetString()!) is not null;
    }

    private static bool ReadReceiptBoolean(JsonElement value, string name) =>
        value.ValueKind == JsonValueKind.Object && value.TryGetProperty(name, out var property) &&
        property.ValueKind is JsonValueKind.True;

    private static OpenInCodexCapability? ReadOpenInCodexCapability(JsonElement value)
    {
        if (value.ValueKind != JsonValueKind.Object || !value.TryGetProperty("openInCodex", out var property) ||
            property.ValueKind != JsonValueKind.Object)
            return null;
        try { return property.Deserialize<OpenInCodexCapability>(JsonOptions); }
        catch (JsonException) { throw new ArgumentException("Continuation adapter returned an invalid open capability."); }
    }

    private static void RequireReceiptString(JsonElement value, string name, string? expected)
    {
        var actual = value.ValueKind == JsonValueKind.Object && value.TryGetProperty(name, out var property) &&
            property.ValueKind == JsonValueKind.String ? property.GetString() : null;
        if (!string.Equals(actual, expected, StringComparison.Ordinal))
            throw new ArgumentException($"Continuation adapter returned a conflicting {name}.");
    }

    private async Task<AgentAttemptReceipt?> ReadAgentAttemptAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, string runId, string attemptId,
        CancellationToken token)
    {
        const string sql = """
            SELECT session.receipt::text FROM wpcp_agent_sessions session
            JOIN wpcp_activity_attempts attempt ON attempt.attempt_id=session.attempt_id
            JOIN wpcp_run_activities activity ON activity.activity_id=attempt.activity_id
            WHERE activity.run_id=@run AND attempt.attempt_id=@attempt;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("run", Guid.Parse(runId));
        command.Parameters.AddWithValue("attempt", Guid.Parse(attemptId));
        var raw = await command.ExecuteScalarAsync(token) as string;
        return raw is null ? null : Deserialize<AgentAttemptReceipt>(raw);
    }

    private async Task UpdateAgentReceiptAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, AgentAttemptReceipt receipt, CancellationToken token)
    {
        await using var command = new NpgsqlCommand("UPDATE wpcp_agent_sessions SET receipt=@receipt WHERE attempt_id=@attempt", connection, transaction);
        command.Parameters.AddWithValue("attempt", Guid.Parse(receipt.AttemptId));
        AddJson(command, "receipt", receipt);
        await command.ExecuteNonQueryAsync(token);
    }

    private async Task InsertContinuationCommandAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, StoredRun run, ContinuationOperation operation,
        string digest, CancellationToken token)
    {
        await using var command = new NpgsqlCommand("""
            INSERT INTO wpcp_human_request_commands
                (command_id, run_id, request_id, action, payload_digest, source_attempt_id, source_session_id,
                 result_attempt_id, result_session_id, result_request_id, operation_key, state, parent_session_id, origin, adapter_origin, message, created_at)
            VALUES (@command, @run, @request, @action, @digest, @source_attempt, @source_session,
                    @result_attempt, @result_session, @result_request, @operation, @state, @parent, @origin, @adapter_origin, @message, @now);
            """, connection, transaction);
        command.Parameters.AddWithValue("command", Guid.Parse(operation.CommandId));
        command.Parameters.AddWithValue("run", Guid.Parse(run.Correlation.RunId));
        command.Parameters.AddWithValue("request", Guid.Parse(operation.RequestId));
        command.Parameters.AddWithValue("action", operation.Action);
        command.Parameters.AddWithValue("digest", digest);
        command.Parameters.AddWithValue("source_attempt", Guid.Parse(operation.SourceAttemptId));
        command.Parameters.AddWithValue("source_session", operation.SourceSessionId);
        command.Parameters.AddWithValue("result_attempt", Guid.Parse(operation.ResultAttemptId));
        AddNullable(command, "result_session", NpgsqlDbType.Text, operation.ResultSessionId);
        AddNullable(command, "result_request", NpgsqlDbType.Uuid,
            operation.ResultRequestId is null ? null : Guid.Parse(operation.ResultRequestId));
        command.Parameters.AddWithValue("operation", Guid.Parse(operation.OperationKey));
        command.Parameters.AddWithValue("state", operation.State);
        AddNullable(command, "parent", NpgsqlDbType.Text, operation.ParentSessionId);
        AddNullable(command, "origin", NpgsqlDbType.Text, operation.Origin);
        command.Parameters.AddWithValue("adapter_origin", operation.AdapterOrigin);
        AddNullable(command, "message", NpgsqlDbType.Text, operation.Message);
        command.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
        await command.ExecuteNonQueryAsync(token);
    }

    private async Task UpdateContinuationCommandAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, ContinuationOperation operation,
        JsonElement receipt, CancellationToken token)
    {
        await using var command = new NpgsqlCommand("""
            UPDATE wpcp_human_request_commands SET state=@state, result_session_id=@result_session,
                result_request_id=@result_request, adapter_receipt=@receipt WHERE command_id=@command;
            """, connection, transaction);
        command.Parameters.AddWithValue("state", operation.State);
        AddNullable(command, "result_session", NpgsqlDbType.Text, operation.ResultSessionId);
        AddNullable(command, "result_request", NpgsqlDbType.Uuid,
            operation.ResultRequestId is null ? null : Guid.Parse(operation.ResultRequestId));
        AddJson(command, "receipt", receipt);
        command.Parameters.AddWithValue("command", Guid.Parse(operation.CommandId));
        await command.ExecuteNonQueryAsync(token);
    }

    private async Task<StoredContinuationCommand?> ReadContinuationCommandAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, string commandId, CancellationToken token)
    {
        await using var command = new NpgsqlCommand("""
            SELECT command_id::text, run_id::text, request_id::text, action, payload_digest,
                   source_attempt_id::text, source_session_id, result_attempt_id::text, result_session_id,
                   result_request_id::text, operation_key::text, state, parent_session_id, origin, adapter_origin, message
            FROM wpcp_human_request_commands WHERE command_id=@command;
            """, connection, transaction);
        command.Parameters.AddWithValue("command", Guid.Parse(commandId));
        await using var reader = await command.ExecuteReaderAsync(token);
        if (!await reader.ReadAsync(token)) return null;
        return ReadStoredContinuationCommand(reader);
    }

    private static string ContinuationDigest(string action, ControlMutation mutation, string? redactedMessage) =>
        Digest(new { action, mutation.RequestId, mutation.TargetAttemptId, mutation.ExpectedRunVersion,
            mutation.ExpectedHeadSha, mutation.LeaseEpoch, Message = redactedMessage });

    private static async Task LockRunAsync(NpgsqlConnection connection, NpgsqlTransaction transaction, string runId,
        CancellationToken token)
    {
        await using var lockCommand = new NpgsqlCommand(
            "SELECT run_id FROM wpcp_implementation_runs WHERE run_id=@id FOR UPDATE", connection, transaction);
        lockCommand.Parameters.AddWithValue("id", Guid.Parse(runId));
        await lockCommand.ExecuteScalarAsync(token);
    }

    private sealed record StoredContinuationCommand(
        string CommandId, string RunId, string RequestId, string Action, string PayloadDigest,
        string SourceAttemptId, string SourceSessionId, string ResultAttemptId, string? ResultSessionId,
        string? ResultRequestId, string OperationKey, string State, string? ParentSessionId, string? Origin,
        string AdapterOrigin, string? Message)
    {
        public ContinuationOperation ToOperation() => new(CommandId, RequestId, Action, SourceAttemptId,
            SourceSessionId, ResultAttemptId, ResultSessionId, OperationKey, State, ParentSessionId, Origin,
            AdapterOrigin, Message, RunId, ResultRequestId);
    }

    private static StoredContinuationCommand ReadStoredContinuationCommand(NpgsqlDataReader reader) => new(
        reader.GetString(0), reader.GetString(1), reader.GetString(2), reader.GetString(3), reader.GetString(4),
        reader.GetString(5), reader.GetString(6), reader.GetString(7), reader.IsDBNull(8) ? null : reader.GetString(8),
        reader.IsDBNull(9) ? null : reader.GetString(9), reader.GetString(10), reader.GetString(11),
        reader.IsDBNull(12) ? null : reader.GetString(12), reader.IsDBNull(13) ? null : reader.GetString(13),
        reader.GetString(14), reader.IsDBNull(15) ? null : reader.GetString(15));

    private const string ContinuationSchema = """
        DO $$
        DECLARE primary_key_name text;
        BEGIN
            SELECT constraint_name INTO primary_key_name
              FROM information_schema.table_constraints
             WHERE table_schema=current_schema()
               AND table_name='wpcp_agent_sessions'
               AND constraint_type='PRIMARY KEY';
            IF NOT EXISTS (
                SELECT 1
                  FROM information_schema.table_constraints tc
                  JOIN information_schema.key_column_usage kcu
                    ON kcu.constraint_catalog=tc.constraint_catalog
                   AND kcu.constraint_schema=tc.constraint_schema
                   AND kcu.constraint_name=tc.constraint_name
                 WHERE tc.table_schema=current_schema()
                   AND tc.table_name='wpcp_agent_sessions'
                   AND tc.constraint_type='PRIMARY KEY'
                   AND kcu.column_name='attempt_id') THEN
                IF primary_key_name IS NOT NULL THEN
                    EXECUTE format('ALTER TABLE wpcp_agent_sessions DROP CONSTRAINT %I', primary_key_name);
                END IF;
                ALTER TABLE wpcp_agent_sessions ADD PRIMARY KEY (attempt_id);
            END IF;
        END $$;
        CREATE INDEX IF NOT EXISTS wpcp_agent_sessions_run_idx ON wpcp_agent_sessions(run_id, attempt_id);

        CREATE TABLE IF NOT EXISTS wpcp_human_request_commands (
            command_id uuid PRIMARY KEY,
            run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            request_id uuid NOT NULL,
            action text NOT NULL,
            payload_digest text NOT NULL,
            source_attempt_id uuid NOT NULL REFERENCES wpcp_activity_attempts(attempt_id),
            source_session_id text NOT NULL,
            result_attempt_id uuid NOT NULL REFERENCES wpcp_activity_attempts(attempt_id),
            result_session_id text,
            result_request_id uuid,
            operation_key uuid NOT NULL,
            state text NOT NULL CHECK (state IN ('pending', 'applied')),
            parent_session_id text,
            origin text,
            adapter_origin text NOT NULL,
            message text,
            adapter_receipt jsonb,
            created_at timestamptz NOT NULL
        );
        CREATE INDEX IF NOT EXISTS wpcp_human_request_commands_run_idx
            ON wpcp_human_request_commands(run_id, created_at);
        ALTER TABLE wpcp_human_request_commands ADD COLUMN IF NOT EXISTS adapter_origin text;
        ALTER TABLE wpcp_human_request_commands ADD COLUMN IF NOT EXISTS message text;
        ALTER TABLE wpcp_human_request_commands ADD COLUMN IF NOT EXISTS result_request_id uuid;
        UPDATE wpcp_human_request_commands SET adapter_origin='' WHERE adapter_origin IS NULL;
        ALTER TABLE wpcp_human_request_commands ALTER COLUMN adapter_origin SET NOT NULL;
        ALTER TABLE wpcp_human_request_commands
            DROP CONSTRAINT IF EXISTS wpcp_human_request_commands_state_check;
        ALTER TABLE wpcp_human_request_commands
            ADD CONSTRAINT wpcp_human_request_commands_state_check
            CHECK (state IN ('pending', 'applied', 'limitation'));
        """;
}
