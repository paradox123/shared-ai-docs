using Npgsql;
using NpgsqlTypes;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    /// <summary>The row lock covers provider revalidation and the complete decision across hosts.</summary>
    public async Task<ControlDecision> DecideControlAsync(
        string runId, string? action, ControlMutation? mutation,
        Func<RepositoryBinding, CancellationToken, Task<RepositoryAccess>> authorize,
        CancellationToken cancellationToken = default)
    {
        if (!Guid.TryParse(runId, out var parsed))
            return new("implementation-run-not-found", new(null, false, false), null);
        await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(cancellationToken);
        await using (var rowLock = new NpgsqlCommand(
            "SELECT run_id FROM wpcp_implementation_runs WHERE run_id = @id FOR UPDATE", connection, transaction))
        {
            rowLock.Parameters.AddWithValue("id", parsed);
            await rowLock.ExecuteScalarAsync(cancellationToken);
        }
        var run = await FindRunAsync(connection, transaction, runId, cancellationToken);
        if (run is null) return new("implementation-run-not-found", new(null, false, false), null);
        var current = await ReadControlStateAsync(connection, transaction, run, cancellationToken);
        var access = run.Correlation.Repository is { } binding
            ? await authorize(binding, cancellationToken)
            : new RepositoryAccess(null, false, false, "repository-binding-required");
        // Revocation is a separate security transition, never the requested action.
        if (current.Holder is not null && current.Holder == access.Actor && !access.CanContribute &&
            access.FailureCode is null or "repository-access-denied")
        {
            var revoked = current with { RunVersion = current.RunVersion + 1,
                LeaseEpoch = current.LeaseEpoch + 1, Holder = null, ClaimedAt = null };
            await WriteControlTransitionAsync(connection, transaction, run, current, revoked,
                "ControlLeaseRevoked", access.Actor!, cancellationToken);
            current = revoked;
            await AppendAuditAsync(connection, transaction, runId, "revalidate", "control-lease-revoked",
                access.Actor, cancellationToken);
        }
        string code;
        if (!access.CanRead || !access.IsHuman)
            code = access.FailureCode ?? "repository-access-denied";
        else if (action is null)
            code = "observed";
        else if (!access.CanContribute)
            code = "repository-contribution-required";
        else if (action is not ("claim" or "release"))
            code = "invalid-control-action";
        else if (mutation is null || !Guid.TryParse(mutation.TargetAttemptId, out _) ||
            mutation.ExpectedRunVersion < 1 || mutation.LeaseEpoch < 0)
            code = "invalid-control-mutation";
        else if (action == "claim" && current.Holder is not null)
            code = "control-lease-held";
        else if (action == "release" && current.Holder != access.Actor)
            code = "control-lease-required";
        else if (mutation.TargetAttemptId != current.TargetAttemptId)
            code = "stale-target-attempt";
        else if (mutation.ExpectedRunVersion != current.RunVersion)
            code = "stale-run-version";
        else if (mutation.ExpectedHeadSha != current.HeadSha)
            code = "stale-head-sha";
        else if (mutation.LeaseEpoch != current.LeaseEpoch)
            code = "stale-lease-epoch";
        else
        {
            var next = current with
            {
                RunVersion = current.RunVersion + 1,
                LeaseEpoch = current.LeaseEpoch + 1,
                Holder = action == "claim" ? access.Actor : null,
                ClaimedAt = action == "claim" ? DateTimeOffset.UtcNow : null,
            };
            await WriteControlTransitionAsync(connection, transaction, run, current, next,
                action == "claim" ? "ControlLeaseClaimed" : "ControlLeaseReleased", access.Actor!, cancellationToken);
            current = next;
            code = action == "claim" ? "control-lease-claimed" : "control-lease-released";
        }
        if (action is not null || code != "observed")
            await AppendAuditAsync(connection, transaction, runId,
                action is "claim" or "release" ? action : action is null ? "observe" : "invalid",
                code, access.Actor, cancellationToken);
        await transaction.CommitAsync(cancellationToken);
        return new(code, access, access.CanRead ? current : null);
    }

    private static async Task AppendAuditAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, string runId,
        string action, string code, ActorIdentity? actor, CancellationToken token)
    {
        await using var command = new NpgsqlCommand("""
            INSERT INTO wpcp_security_audit(run_id, occurred_at, action, code, actor)
            VALUES (@id, @at, @action, @code, @actor)
            """, connection, transaction);
        command.Parameters.AddWithValue("id", Guid.Parse(runId));
        command.Parameters.AddWithValue("at", DateTimeOffset.UtcNow);
        command.Parameters.AddWithValue("action", action);
        command.Parameters.AddWithValue("code", code);
        AddNullable(command, "actor", NpgsqlDbType.Jsonb,
            actor is null ? null : System.Text.Json.JsonSerializer.Serialize(actor, JsonOptions));
        await command.ExecuteNonQueryAsync(token);
    }

    public async Task<IReadOnlyList<SecurityAuditEntry>> GetAuditAsync(string runId, CancellationToken token = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var command = new NpgsqlCommand("""
            SELECT position, occurred_at, action, code, actor::text FROM wpcp_security_audit
            WHERE run_id = @id ORDER BY position
            """, connection);
        command.Parameters.AddWithValue("id", Guid.Parse(runId));
        await using var reader = await command.ExecuteReaderAsync(token);
        var entries = new List<SecurityAuditEntry>();
        while (await reader.ReadAsync(token))
            entries.Add(new(reader.GetInt64(0), reader.GetFieldValue<DateTimeOffset>(1),
                reader.GetString(2), reader.GetString(3),
                reader.IsDBNull(4) ? null : Deserialize<ActorIdentity>(reader.GetString(4))));
        return entries;
    }

    private static async Task<RunControlState> ReadControlStateAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, StoredRun run, CancellationToken token)
    {
        const string sql = """
            SELECT lease_epoch, lease_holder::text, lease_claimed_at, head_sha,
                   (SELECT attempt_id::text FROM wpcp_activity_attempts a
                    JOIN wpcp_run_activities activity USING (activity_id)
                    WHERE activity.run_id = r.run_id
                    ORDER BY a.started_at DESC, a.attempt_number DESC, a.attempt_id DESC LIMIT 1)
            FROM wpcp_implementation_runs r WHERE run_id = @id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("id", Guid.Parse(run.Correlation.RunId));
        await using var reader = await command.ExecuteReaderAsync(token);
        await reader.ReadAsync(token);
        return new(run.LastPosition, reader.GetString(4), reader.IsDBNull(3) ? null : reader.GetString(3),
            reader.GetInt64(0), reader.IsDBNull(1) ? null : Deserialize<ActorIdentity>(reader.GetString(1)),
            reader.IsDBNull(2) ? null : reader.GetFieldValue<DateTimeOffset>(2));
    }

    private async Task WriteControlTransitionAsync(
        NpgsqlConnection connection, NpgsqlTransaction transaction, StoredRun run,
        RunControlState previous, RunControlState next, string eventType, ActorIdentity actor,
        CancellationToken token)
    {
        const string sql = """
            UPDATE wpcp_implementation_runs SET last_position = @version, lease_epoch = @epoch,
                lease_holder = @holder, lease_claimed_at = @claimed WHERE run_id = @id;
            INSERT INTO wpcp_run_events
                (run_id, position, event_id, event_type, occurred_at, correlation, payload,
                 provenance, redaction_occurred, redaction_policy_version, redaction_marker)
            VALUES (@id, @version, @event_id, @event_type, @at, @correlation, @payload,
                    @provenance, @redaction_occurred, @redaction_policy_version, @redaction_marker);
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("id", Guid.Parse(run.Correlation.RunId));
        command.Parameters.AddWithValue("version", next.RunVersion);
        command.Parameters.AddWithValue("epoch", next.LeaseEpoch);
        AddNullable(command, "holder", NpgsqlDbType.Jsonb,
            next.Holder is null ? null : System.Text.Json.JsonSerializer.Serialize(next.Holder, JsonOptions));
        AddNullable(command, "claimed", NpgsqlDbType.TimestampTz, next.ClaimedAt);
        command.Parameters.AddWithValue("event_id", Guid.NewGuid());
        command.Parameters.AddWithValue("event_type", eventType);
        command.Parameters.AddWithValue("at", DateTimeOffset.UtcNow);
        AddJson(command, "correlation", run.Correlation);
        AddJson(command, "payload", new { actor, previous, current = next });
        AddJson(command, "provenance", run.Provenance);
        AddRedaction(command, _redactionPolicy.Metadata(false));
        await command.ExecuteNonQueryAsync(token);
    }
}
