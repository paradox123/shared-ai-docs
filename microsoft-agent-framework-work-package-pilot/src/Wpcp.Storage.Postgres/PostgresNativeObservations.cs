using System.Text.Json;
using Npgsql;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    // Service evidence only: this never authorizes a tool or qualifies an outcome.
    public async Task AppendNativeQuarantineAsync(string runId, string attemptId, string sessionId,
        string observationId, JsonElement observation, string adapterOrigin, CancellationToken token)
    {
        if (!Guid.TryParse(observationId, out _)) throw new ArgumentException("Invalid observation identity.");
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await LockRunAsync(connection, transaction, runId, token);
        var run = await FindRunAsync(connection, transaction, runId, token) ?? throw new ArgumentException("Unknown run.");
        var attempt = await ReadAgentAttemptAsync(connection, transaction, runId, attemptId, token);
        if (attempt?.Kind != "real-codex" || attempt.AdapterOrigin != adapterOrigin || attempt.Session.SessionId != sessionId)
            throw new ArgumentException("Unassigned native source.");
        var safe = await SanitizeEvidenceAsync(connection, transaction, runId, observation, token);
        var digest = Digest(safe.Value);
        await using var existing = new NpgsqlCommand("""
            SELECT payload->>'digest' FROM wpcp_run_events WHERE run_id=@run
                AND event_type='NativeObservationQuarantined' AND payload->>'observationId'=@observation
            """, connection, transaction);
        existing.Parameters.AddWithValue("run", Guid.Parse(runId));
        existing.Parameters.AddWithValue("observation", observationId);
        if (await existing.ExecuteScalarAsync(token) is string previous)
        {
            if (previous != digest) throw new ArgumentException("Conflicting observation replay.");
            return;
        }
        await AppendAgentEventAsync(connection, transaction, run, "NativeObservationQuarantined",
            new { attemptId, sessionId, observationId, digest, qualifiesResult = false,
                actor = new { kind = "service", provider = "real-codex-adapter" }, data = observation }, token);
        await transaction.CommitAsync(token);
    }
}
