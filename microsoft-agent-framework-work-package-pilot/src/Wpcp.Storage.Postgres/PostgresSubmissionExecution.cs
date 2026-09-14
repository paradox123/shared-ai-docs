using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    public async Task<bool> StartSubmissionAsync(Submission submission, ActorIdentity actor,
        SubmissionExecutionConfiguration configuration, CancellationToken token)
    {
        configuration.Validate();
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await AcquireLockAsync(connection, transaction, "submission:" + submission.SubmissionId, token);
        await using var existing = new NpgsqlCommand(
            "SELECT run_id FROM wpcp_submission_dispatch WHERE submission_id=@id", connection, transaction);
        existing.Parameters.AddWithValue("id", Guid.Parse(submission.SubmissionId));
        if (await existing.ExecuteScalarAsync(token) is not null) return false;
        var result = await StartInTransactionAsync(new StartRunCommand(submission.SubmissionId,
            $"{actor.Provider}:{actor.SubjectId}", submission.Repository.RepositoryId,
            "github:" + submission.Source.ProviderIssueId, submission.Source.IssueNumber,
            JsonSerializer.Serialize(new { step = SubmissionExecutionConfiguration.Step, submission }, JsonOptions),
            new(submission.ContentSha256, SubmissionExecutionConfiguration.Step,
                Digest(JsonSerializer.Serialize(configuration, JsonOptions)), "AgentSessionAdapter/v1"),
            actor, submission.Repository), connection, transaction, token);
        if (result.Disposition != StartRunDisposition.Accepted)
            throw new SubmissionRunConflictException();
        await using var insert = new NpgsqlCommand("""
            INSERT INTO wpcp_submission_dispatch (submission_id, run_id, configuration, queued_at)
            VALUES (@submission, @run, @configuration, @now)
            """, connection, transaction);
        insert.Parameters.AddWithValue("submission", Guid.Parse(submission.SubmissionId));
        insert.Parameters.AddWithValue("run", Guid.Parse(result.RunId));
        insert.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
        AddJson(insert, "configuration", configuration);
        await insert.ExecuteNonQueryAsync(token);
        var run = (await FindRunAsync(connection, transaction, result.RunId, token))!;
        await AppendAgentEventAsync(connection, transaction, run, "SubmissionExecutionQueued",
            new { submission.SubmissionId, submission.ContentSha256, step = SubmissionExecutionConfiguration.Step, actor }, token);
        await transaction.CommitAsync(token);
        return true;
    }

    public async Task<SubmissionExecution?> GetSubmissionExecutionAsync(Guid submissionId, CancellationToken token)
    {
        await using var command = _dataSource.CreateCommand(
            "SELECT run_id::text, state, code FROM wpcp_submission_dispatch WHERE submission_id=@id");
        command.Parameters.AddWithValue("id", submissionId);
        await using var reader = await command.ExecuteReaderAsync(token);
        if (!await reader.ReadAsync(token)) return null;
        return new(submissionId.ToString(), reader.GetString(0), reader.GetString(1),
            reader.IsDBNull(2) ? null : reader.GetString(2));
    }

    public async Task<SubmissionDelivery?> ClaimSubmissionAsync(CancellationToken token)
    {
        // The repository lock belongs to the worker connection, so process death releases it.
        // Running and uncertain dispositions remain eligible for receipt reconciliation by a replacement.
        await using var read = _dataSource.CreateCommand("""
            SELECT s.snapshot::text, d.run_id::text, d.configuration::text
            FROM wpcp_submission_dispatch d JOIN wpcp_submissions s USING(submission_id)
            WHERE d.state IN ('queued', 'running', 'reconciling') ORDER BY d.queued_at, d.submission_id
            """);
        var candidates = new List<(Submission Submission, string RunId, SubmissionExecutionConfiguration Configuration)>();
        await using (var reader = await read.ExecuteReaderAsync(token))
            while (await reader.ReadAsync(token)) candidates.Add((Deserialize<Submission>(reader.GetString(0)),
                reader.GetString(1), Deserialize<SubmissionExecutionConfiguration>(reader.GetString(2))));
        foreach (var candidate in candidates)
        {
            var connection = await _dataSource.OpenConnectionAsync(token);
            var lease = new DeliveryLock(connection);
            try
            {
                await using var gate = new NpgsqlCommand("SELECT pg_try_advisory_lock(hashtextextended(@key, 0))", connection);
                gate.Parameters.AddWithValue("key", "submission-repository:" + candidate.Submission.Repository.RepositoryId);
                if (await gate.ExecuteScalarAsync(token) is true)
                {
                    var current = await GetSubmissionExecutionAsync(Guid.Parse(candidate.Submission.SubmissionId), token);
                    if (current?.State is "queued" or "running" or "reconciling")
                        return new(candidate.Submission, candidate.RunId, candidate.Configuration, lease);
                }
            }
            catch { await lease.DisposeAsync(); throw; }
            await lease.DisposeAsync();
        }
        return null;
    }

    public async Task SetSubmissionExecutionAsync(SubmissionDelivery delivery, string state, string? code,
        CancellationToken token)
    {
        if (state is not ("running" or "reconciling" or "completed" or "failed")) throw new ArgumentException("Unknown execution state.");
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var transaction = await connection.BeginTransactionAsync(token);
        await using var rowLock = new NpgsqlCommand(
            "SELECT run_id FROM wpcp_implementation_runs WHERE run_id=@run FOR UPDATE", connection, transaction);
        rowLock.Parameters.AddWithValue("run", Guid.Parse(delivery.RunId));
        await rowLock.ExecuteScalarAsync(token);
        await using var command = new NpgsqlCommand("""
            UPDATE wpcp_submission_dispatch SET state=@state, code=@code,
                completed_at=CASE WHEN @state IN ('running', 'reconciling') THEN NULL ELSE now() END
            WHERE submission_id=@id AND (state<>@state OR code IS DISTINCT FROM @code);
            """, connection, transaction);
        command.Parameters.AddWithValue("id", Guid.Parse(delivery.Submission.SubmissionId));
        command.Parameters.AddWithValue("state", state);
        command.Parameters.AddWithValue("code", NpgsqlTypes.NpgsqlDbType.Text, (object?)code ?? DBNull.Value);
        if (await command.ExecuteNonQueryAsync(token) > 0)
        {
            var run = (await FindRunAsync(connection, transaction, delivery.RunId, token))!;
            await AppendAgentEventAsync(connection, transaction, run, "SubmissionExecutionStateChanged",
                new { delivery.Submission.SubmissionId, state, code, step = SubmissionExecutionConfiguration.Step }, token);
            await using var update = new NpgsqlCommand(
                "UPDATE wpcp_implementation_runs SET state=@state WHERE run_id=@run", connection, transaction);
            update.Parameters.AddWithValue("run", Guid.Parse(delivery.RunId));
            update.Parameters.AddWithValue("state", state == "completed" ? "analysis-completed" : state);
            await update.ExecuteNonQueryAsync(token);
        }
        await transaction.CommitAsync(token);
    }
}

public sealed record SubmissionExecution(string SubmissionId, string RunId, string State, string? Code);
public sealed class SubmissionRunConflictException : Exception;
public sealed record SubmissionDelivery(Submission Submission, string RunId,
    SubmissionExecutionConfiguration Configuration, IAsyncDisposable Lease) : IAsyncDisposable
{
    public ValueTask DisposeAsync() => Lease.DisposeAsync();
}
