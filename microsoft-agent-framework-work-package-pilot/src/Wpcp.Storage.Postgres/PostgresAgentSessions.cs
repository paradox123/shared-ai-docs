using System.Text.Json;
using System.Text.Json.Nodes;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    // A session lock is released by PostgreSQL when the worker connection dies.
    // Pooling must not return a locked session; disposal explicitly unlocks it.
    public async Task<IAsyncDisposable> AcquireAgentDeliveryAsync(string runId, CancellationToken token = default)
    {
        var connection = await _dataSource.OpenConnectionAsync(token);
        try
        {
            await using var command = new NpgsqlCommand("SELECT pg_advisory_lock(hashtextextended(@key, 0))", connection);
            command.Parameters.AddWithValue("key", "agent-delivery:" + runId);
            await command.ExecuteNonQueryAsync(token);
            return new DeliveryLock(connection);
        }
        catch { await connection.DisposeAsync(); throw; }
    }

    public Task<AgentAttemptReceipt> PrepareAgentAsync(string runId, string origin, bool rejectBlocked,
        CancellationToken token = default) =>
        ChangeAgentAsync(runId, async (connection, transaction, run, receipt) =>
        {
            if (receipt is not null)
            {
                if (receipt.AdapterOrigin != origin || receipt.RejectBlocked != rejectBlocked)
                    throw new AgentAssignmentConflictException();
                return receipt;
            }
            var activityId = Guid.NewGuid();
            var attemptId = Guid.NewGuid();
            await using var insert = new NpgsqlCommand("""
                INSERT INTO wpcp_run_activities VALUES (@activity, @run, 'fake-codex', 'running', @now, NULL);
                INSERT INTO wpcp_activity_attempts VALUES (@attempt, @activity, 1, 'running', @now, NULL);
                """, connection, transaction);
            insert.Parameters.AddWithValue("activity", activityId);
            insert.Parameters.AddWithValue("attempt", attemptId);
            insert.Parameters.AddWithValue("run", Guid.Parse(runId));
            insert.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
            await insert.ExecuteNonQueryAsync(token);
            receipt = new(runId, activityId.ToString(), attemptId.ToString(), "running", origin,
                rejectBlocked, new(attemptId.ToString(), OpenInCodex: new()));
            await AppendAgentEventAsync(connection, transaction, run, "AgentPreparationCompleted",
                new { receipt.ActivityId, receipt.AttemptId, executor = "deterministic", framework = "Microsoft.Agents.AI.Workflows/1.16.0", runtime = Environment.Version.ToString() }, token);
            await AppendAgentEventAsync(connection, transaction, run, "AgentSessionStartRequested",
                new { receipt.ActivityId, receipt.AttemptId, receipt.Session.OperationKey, receipt.Session.ContractVersion }, token);
            return receipt;
        }, token);

    public Task<AgentAttemptReceipt> CaptureAgentResponseAsync(string runId, AgentAdapterResponse response,
        CancellationToken token = default) =>
        ChangeAgentAsync(runId, async (connection, transaction, run, receipt) =>
        {
            ArgumentNullException.ThrowIfNull(receipt);
            JsonElement body;
            try { body = JsonSerializer.Deserialize<JsonElement>(response.Body); }
            catch (JsonException) { body = JsonSerializer.SerializeToElement(response.Body); }
            var safe = await SanitizeEvidenceAsync(connection, transaction, runId, body, token);
            var storedBody = await ExternalizeLargeValueAsync(connection, transaction, runId, safe.Value, safe.Occurred, token);
            if (receipt.Session.ObservedResponse is { } previous)
            {
                if (!JsonElement.DeepEquals(previous, storedBody) || receipt.Session.ResponseStatus != response.StatusCode)
                    throw new ArgumentException("Conflicting adapter response.");
                return receipt;
            }
            var eventId = await AppendAgentEventAsync(connection, transaction, run, "AgentAdapterResponseObserved",
                new { receipt.ActivityId, receipt.AttemptId, response.StatusCode, body = storedBody }, token);
            return receipt with { Session = receipt.Session with { ObservedResponse = storedBody,
                ResponseStatus = response.StatusCode, ResponseEventId = eventId } };
        }, token);

    public Task<AgentAttemptReceipt> BindAgentSessionAsync(string runId, string sessionId,
        OpenInCodexCapability? openInCodex = null, CancellationToken token = default) =>
        ChangeAgentAsync(runId, async (connection, transaction, run, receipt) =>
        {
            ArgumentNullException.ThrowIfNull(receipt);
            if (!Guid.TryParse(sessionId, out _) || _redactionPolicy.ContainsControlledCanary(sessionId))
                throw new ArgumentException("Invalid session identity.");
            if (receipt.Session.SessionId is not null)
            {
                if (receipt.Session.SessionId != sessionId) throw new ArgumentException("Conflicting session identity.");
                return receipt;
            }
            var capability = openInCodex ?? receipt.Session.OpenInCodex;
            var safeCapability = capability is null ? null :
                RedactAgentValue(JsonSerializer.SerializeToElement(capability, JsonOptions)).Value
                    .Deserialize<OpenInCodexCapability>(JsonOptions)
                ?? throw new ArgumentException("Invalid Codex opening capability.");
            var eventId = await AppendAgentEventAsync(connection, transaction, run, "AgentSessionStarted",
                new { receipt.ActivityId, receipt.AttemptId, sessionId, receipt.Session.OperationKey,
                    receipt.Session.ContractVersion,
                    openInCodex = capability }, token);
            return receipt with { Session = receipt.Session with { SessionId = sessionId, Status = "running",
                StartedEventId = eventId, LastEventId = eventId,
                OpenInCodex = safeCapability } };
        }, token);

    public Task<AgentAttemptReceipt> ObserveAgentAsync(string runId, AgentSourceEvent observation,
        CancellationToken token = default) =>
        ChangeAgentAsync(runId, async (connection, transaction, run, receipt) =>
        {
            ArgumentNullException.ThrowIfNull(receipt);
            var session = receipt.Session;
            if (session.SessionId is null) throw new ArgumentException("No bound session.");
            // Compare canonical redacted JSON, including source type and sequence.
            var safeData = await SanitizeEvidenceAsync(connection, transaction, runId, observation.Data, token);
            observation = observation with { Data = await ExternalizeLargeValueAsync(connection, transaction,
                runId, safeData.Value, safeData.Occurred, token) };
            var safe = RedactAgentValue(JsonSerializer.SerializeToElement(observation, JsonOptions));
            if (observation.Sequence <= session.LastSequence)
            {
                await using var previous = new NpgsqlCommand("""
                    SELECT observation::text FROM wpcp_agent_observations WHERE attempt_id=@id AND sequence=@sequence
                    """, connection, transaction);
                previous.Parameters.AddWithValue("id", Guid.Parse(receipt.AttemptId));
                previous.Parameters.AddWithValue("sequence", observation.Sequence);
                var stored = await previous.ExecuteScalarAsync(token) as string;
                if (stored is null || !JsonElement.DeepEquals(JsonSerializer.Deserialize<JsonElement>(stored), safe.Value))
                    throw new ArgumentException("Conflicting observation replay.");
                return receipt;
            }
            if (observation.Sequence != session.LastSequence + 1 || session.OriginalResult is not null)
                throw new ArgumentException("Non-contiguous or post-terminal observation.");
            var safeObservation = safe.Value.Deserialize<AgentSourceEvent>(JsonOptions)!;
            var eventId = await AppendAgentEventAsync(connection, transaction, run,
                observation.Type == "result" ? "AgentResultObserved" : "AgentObservationReceived",
                new { receipt.ActivityId, receipt.AttemptId, session.SessionId,
                    sourceSequence = observation.Sequence, observation.Type, data = observation.Data,
                    causedByEventId = session.LastEventId }, token);
            await using var insert = new NpgsqlCommand("""
                INSERT INTO wpcp_agent_observations VALUES (@id, @sequence, @observation)
                """, connection, transaction);
            insert.Parameters.AddWithValue("id", Guid.Parse(receipt.AttemptId));
            insert.Parameters.AddWithValue("sequence", observation.Sequence);
            AddJson(insert, "observation", safeObservation);
            await insert.ExecuteNonQueryAsync(token);
            return receipt with { Session = session with { LastSequence = observation.Sequence, LastEventId = eventId,
                OriginalResult = observation.Type == "result" ? safeObservation.Data : session.OriginalResult,
                OriginalResultEventId = observation.Type == "result" ? eventId : session.OriginalResultEventId } };
        }, token);

    public Task<AgentAttemptReceipt> CompleteAgentAsync(string runId, string category, string sessionStatus,
        CancellationToken token = default) =>
        ChangeAgentAsync(runId, async (connection, transaction, run, receipt) =>
        {
            ArgumentNullException.ThrowIfNull(receipt);
            if (receipt.State != "running") return receipt;
            await AppendAgentEventAsync(connection, transaction, run,
                category == "semantic-rejection" ? "AgentResultRejected" : "AgentAttemptCompleted",
                new { receipt.ActivityId, receipt.AttemptId, receipt.Session.SessionId, category,
                    originalResultEventId = receipt.Session.OriginalResultEventId }, token);
            var session = receipt.Session with { Status = sessionStatus, FailureCategory = category };
            if (category is "blocked" or "semantic-rejection" && session.HumanRequest is null &&
                session.SessionId is not null)
            {
                var control = await ReadHumanRequestControlContextAsync(connection, transaction, run, token);
                JsonElement? original = session.OriginalResult;
                try { original = await ReadOriginalAgentResultAsync(receipt, token); }
                catch (IOException) { /* The immutable reference and availability endpoint retain the failure. */ }
                var request = new HumanRequest(
                    Guid.NewGuid().ToString(), receipt.AttemptId, session.SessionId, "awaiting-human", control.HeadSha,
                    HumanRequestProblem(original),
                    session.OriginalResultEventId is null ? [] : [session.OriginalResultEventId],
                    HumanRequestAllowedActions(session.OpenInCodex),
                    ExpectedRunVersion: run.LastPosition + 2, LeaseEpoch: control.LeaseEpoch);
                var eventId = await AppendAgentEventAsync(connection, transaction, run, "HumanRequestCreated",
                    new { request.RequestId, request.AttemptId, request.SessionId, request.Phase,
                        request.ExpectedHeadSha, request.ExpectedRunVersion, request.LeaseEpoch,
                        request.Problem, request.Evidence, request.AllowedActions }, token);
                session = session with { HumanRequest = request with { CreatedEventId = eventId } };
            }
            return receipt with { State = category, Session = session };
        }, token);

    private static string HumanRequestProblem(JsonElement? originalResult)
    {
        if (originalResult is { ValueKind: JsonValueKind.Object } result &&
            result.TryGetProperty("reason", out var reason) && reason.ValueKind == JsonValueKind.String &&
            !string.IsNullOrWhiteSpace(reason.GetString()))
        {
            var text = reason.GetString()!;
            return text.Length <= 1024 ? text : text[..1024] + "… (full original in Run History artifacts)";
        }
        return "Agent attempt requires human direction.";
    }

    private static IReadOnlyList<string> HumanRequestAllowedActions(OpenInCodexCapability? capability)
    {
        var actions = new List<string> { "resume", "fork", "fresh-retry", "open", "write" };
        if (capability?.Mode == "handoff-confirmation-required") actions.Add("handoff");
        return actions;
    }

    private static async Task<(string? HeadSha, long LeaseEpoch)> ReadHumanRequestControlContextAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, StoredRun run, CancellationToken token)
    {
        await using var command = new NpgsqlCommand(
            "SELECT head_sha, lease_epoch FROM wpcp_implementation_runs WHERE run_id=@run", connection, transaction);
        command.Parameters.AddWithValue("run", Guid.Parse(run.Correlation.RunId));
        await using var reader = await command.ExecuteReaderAsync(token);
        if (!await reader.ReadAsync(token)) throw new InvalidOperationException("Unknown run.");
        return (reader.IsDBNull(0) ? null : reader.GetString(0), reader.GetInt64(1));
    }

    private async Task<AgentAttemptReceipt> ChangeAgentAsync(string runId,
        Func<NpgsqlConnection, NpgsqlTransaction, StoredRun, AgentAttemptReceipt?, Task<AgentAttemptReceipt>> change,
        CancellationToken token)
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
        await using var read = new NpgsqlCommand("""
            SELECT session.receipt::text
              FROM wpcp_agent_sessions session
              JOIN wpcp_activity_attempts attempt ON attempt.attempt_id=session.attempt_id
              JOIN wpcp_run_activities activity ON activity.activity_id=attempt.activity_id
             WHERE session.run_id=@id AND activity.activity_type='fake-codex'
             ORDER BY attempt.started_at, attempt.attempt_id
             LIMIT 1
            """, connection, transaction);
        read.Parameters.AddWithValue("id", Guid.Parse(runId));
        var raw = await read.ExecuteScalarAsync(token) as string;
        var receipt = await change(connection, transaction, run,
            raw is null ? null : Deserialize<AgentAttemptReceipt>(raw));
        await using var save = new NpgsqlCommand("""
            INSERT INTO wpcp_agent_sessions (run_id, attempt_id, receipt) VALUES (@run, @attempt, @receipt)
            ON CONFLICT (attempt_id) DO UPDATE SET receipt=EXCLUDED.receipt;
            UPDATE wpcp_implementation_runs SET state=@state WHERE run_id=@run;
            UPDATE wpcp_run_activities SET state=@state, completed_at=CASE WHEN @state='running' THEN NULL ELSE COALESCE(completed_at, @now) END
                WHERE activity_id=@activity;
            UPDATE wpcp_activity_attempts SET state=@state, completed_at=CASE WHEN @state='running' THEN NULL ELSE COALESCE(completed_at, @now) END
                WHERE attempt_id=@attempt;
            """, connection, transaction);
        save.Parameters.AddWithValue("run", Guid.Parse(runId));
        save.Parameters.AddWithValue("activity", Guid.Parse(receipt.ActivityId));
        save.Parameters.AddWithValue("attempt", Guid.Parse(receipt.AttemptId));
        save.Parameters.AddWithValue("state", receipt.State);
        save.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
        AddJson(save, "receipt", receipt);
        await save.ExecuteNonQueryAsync(token);
        await transaction.CommitAsync(token);
        return receipt;
    }

    private async Task<string> AppendAgentEventAsync(NpgsqlConnection connection, NpgsqlTransaction transaction,
        StoredRun run, string type, object payload, CancellationToken token)
    {
        var safe = await SanitizeEvidenceAsync(connection, transaction, run.Correlation.RunId,
            JsonSerializer.SerializeToElement(payload, JsonOptions), token);
        var envelope = JsonNode.Parse(safe.Value.GetRawText())!.AsObject();
        foreach (var field in new[] { "body", "data", "receipt", "response", "diagnostic" })
            if (envelope[field] is { } content)
                envelope[field] = JsonNode.Parse((await ExternalizeLargeValueAsync(connection, transaction,
                    run.Correlation.RunId, JsonSerializer.SerializeToElement(content, JsonOptions), safe.Occurred, token)).GetRawText());
        var eventId = Guid.NewGuid();
        await using var command = new NpgsqlCommand("""
            UPDATE wpcp_implementation_runs SET last_position=last_position+1,
                redaction_occurred=redaction_occurred OR @occurred,
                redaction_policy_version=CASE WHEN @occurred THEN @policy ELSE redaction_policy_version END,
                redaction_marker=CASE WHEN @occurred THEN @marker ELSE redaction_marker END WHERE run_id=@id;
            INSERT INTO wpcp_run_events
                (run_id, position, event_id, event_type, occurred_at, correlation, payload,
                 provenance, redaction_occurred, redaction_policy_version, redaction_marker)
            SELECT @id, last_position, @event, @type, @now, @correlation, @payload,
                @provenance, @occurred, @policy, @marker FROM wpcp_implementation_runs WHERE run_id=@id;
            """, connection, transaction);
        command.Parameters.AddWithValue("id", Guid.Parse(run.Correlation.RunId));
        command.Parameters.AddWithValue("event", eventId);
        command.Parameters.AddWithValue("type", type);
        command.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
        command.Parameters.AddWithValue("occurred", safe.Occurred);
        command.Parameters.AddWithValue("policy", _redactionPolicy.Version);
        command.Parameters.AddWithValue("marker", _redactionPolicy.Marker);
        AddJson(command, "payload", envelope);
        AddJson(command, "correlation", run.Correlation);
        AddJson(command, "provenance", run.Provenance);
        await command.ExecuteNonQueryAsync(token);
        return eventId.ToString();
    }

    private (JsonElement Value, bool Occurred) RedactAgentValue(JsonElement value)
    {
        var occurred = false;
        JsonNode? Visit(JsonNode? node)
        {
            if (node is JsonValue v && v.TryGetValue<string>(out var text))
            {
                var safe = _redactionPolicy.Redact(text);
                occurred |= safe.Occurred || text!.Contains(_redactionPolicy.Marker, StringComparison.Ordinal);
                return JsonValue.Create(safe.Value);
            }
            if (node is JsonObject obj)
            {
                var result = new JsonObject();
                foreach (var pair in obj)
                {
                    var key = _redactionPolicy.Redact(pair.Key);
                    occurred |= key.Occurred;
                    result[key.Value!] = Visit(pair.Value);
                }
                return result;
            }
            if (node is JsonArray array) return new JsonArray(array.Select(Visit).ToArray());
            return node?.DeepClone();
        }
        var result = Visit(JsonNode.Parse(value.GetRawText()));
        return (JsonSerializer.SerializeToElement(result, JsonOptions), occurred);
    }

    private sealed class DeliveryLock(NpgsqlConnection connection) : IAsyncDisposable
    {
        public async ValueTask DisposeAsync()
        {
            try
            {
                await using var unlock = new NpgsqlCommand("SELECT pg_advisory_unlock_all()", connection);
                await unlock.ExecuteNonQueryAsync();
            }
            finally { await connection.DisposeAsync(); }
        }
    }

    private const string AgentSchema = """
        CREATE TABLE IF NOT EXISTS wpcp_agent_sessions (
            run_id uuid PRIMARY KEY REFERENCES wpcp_implementation_runs(run_id),
            attempt_id uuid NOT NULL UNIQUE REFERENCES wpcp_activity_attempts(attempt_id),
            receipt jsonb NOT NULL
        );
        CREATE TABLE IF NOT EXISTS wpcp_agent_observations (
            attempt_id uuid NOT NULL REFERENCES wpcp_activity_attempts(attempt_id),
            sequence integer NOT NULL CHECK (sequence > 0), observation jsonb NOT NULL,
            PRIMARY KEY (attempt_id, sequence)
        );
        """;
}
