using System.Text.Json;
using Npgsql;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

public sealed partial class PostgresImplementationRunStore
{
    public async Task<Publication> SavePublicationAsync(string runId, Publication next)
    {
        await using var connection = await _dataSource.OpenConnectionAsync();
        await using var transaction = await connection.BeginTransactionAsync();
        await using (var row = new NpgsqlCommand("SELECT run_id FROM wpcp_implementation_runs WHERE run_id=@id FOR UPDATE", connection, transaction))
        {
            row.Parameters.AddWithValue("id", Guid.Parse(runId));
            await row.ExecuteScalarAsync();
        }
        var run = await FindRunAsync(connection, transaction, runId, default)
            ?? throw new InvalidOperationException("Unknown run.");
        var previous = await ReadPublicationAsync(connection, transaction, runId, default);
        if (previous is not null && (previous.AssignmentHash != next.AssignmentHash ||
            (previous.Dispatched && !next.Dispatched) ||
            (previous.CaptureHeadSha is not null && previous.CaptureHeadSha != next.CaptureHeadSha) ||
            (previous.Qualification is { } qualification &&
                (next.Qualification is null || !JsonElement.DeepEquals(qualification, next.Qualification.Value))) ||
            (previous.Intent is { } intent && (next.Intent is null || !JsonElement.DeepEquals(intent, next.Intent.Value)))))
            throw new AgentAssignmentConflictException();
        if (previous is null)
        {
            await using var mode = new NpgsqlCommand("SELECT pg_try_advisory_xact_lock(hashtextextended(@key, 0))", connection, transaction);
            mode.Parameters.AddWithValue("key", "repository-mode:" + run.Correlation.RepositoryId);
            if (await mode.ExecuteScalarAsync() is not true) throw new RepositoryRegistrationBusyException();
            await using var legacy = new NpgsqlCommand("""
                SELECT EXISTS(SELECT 1 FROM wpcp_agent_sessions WHERE run_id=@id
                    UNION ALL SELECT 1 FROM wpcp_live_attempts WHERE run_id=@id
                    UNION ALL SELECT 1 FROM wpcp_repository_owners WHERE repository_id=@repo)
                """, connection, transaction);
            legacy.Parameters.AddWithValue("id", Guid.Parse(runId));
            legacy.Parameters.AddWithValue("repo", run.Correlation.RepositoryId);
            if (await legacy.ExecuteScalarAsync() is true) throw new AgentAssignmentConflictException();
        }
        var safe = RedactAgentValue(JsonSerializer.SerializeToElement(next, JsonOptions));
        next = safe.Value.Deserialize<Publication>(JsonOptions)!;
        await using var save = new NpgsqlCommand("""
            INSERT INTO wpcp_publications VALUES (@id, @value)
                ON CONFLICT (run_id) DO UPDATE SET publication=EXCLUDED.publication;
            UPDATE wpcp_implementation_runs SET state=@state, head_sha=COALESCE(@head, head_sha) WHERE run_id=@id;
            """, connection, transaction);
        save.Parameters.AddWithValue("id", Guid.Parse(runId));
        save.Parameters.AddWithValue("state", next.State);
        AddNullable(save, "head", NpgsqlTypes.NpgsqlDbType.Text,
            next.Intent is { } publishedIntent ? publishedIntent.GetProperty("headSha").GetString() : next.CaptureHeadSha);
        AddJson(save, "value", next);
        await save.ExecuteNonQueryAsync();
        await AppendAgentEventAsync(connection, transaction, run, "PublicationStateObserved", next, default);
        if (previous?.Qualification is null && next.Qualification is not null)
            await AppendAgentEventAsync(connection, transaction, run, "EvidenceQualificationObserved",
                new { next.Qualification, next.CaptureHeadSha }, default);
        if (next.Capture is { } capture && (capture.Number != previous?.Capture?.Number || capture.State != previous?.Capture?.State))
        {
            await using var activity = new NpgsqlCommand(capture.State == "running" ? """
                INSERT INTO wpcp_run_activities VALUES (@activity, @run, @kind, @state, @now, NULL);
                INSERT INTO wpcp_activity_attempts VALUES (@attempt, @activity, @number, @state, @now, NULL);
                """ : """
                UPDATE wpcp_run_activities SET state=@state, completed_at=@now WHERE activity_id=@activity;
                UPDATE wpcp_activity_attempts SET state=@state, completed_at=@now WHERE attempt_id=@attempt;
                """, connection, transaction);
            activity.Parameters.AddWithValue("activity", Guid.Parse(capture.ActivityId));
            activity.Parameters.AddWithValue("attempt", Guid.Parse(capture.AttemptId));
            activity.Parameters.AddWithValue("run", Guid.Parse(runId));
            activity.Parameters.AddWithValue("kind", "evidence-" + capture.Kind);
            activity.Parameters.AddWithValue("number", capture.Number);
            activity.Parameters.AddWithValue("state", capture.State);
            activity.Parameters.AddWithValue("now", DateTimeOffset.UtcNow);
            await activity.ExecuteNonQueryAsync();
            await AppendAgentEventAsync(connection, transaction, run,
                capture.State == "running" ? "EvidenceCaptureStarted" : "EvidenceCaptureObserved",
                new { next.CaptureHeadSha, next.Capture, source = next.Qualification?.GetProperty("source") }, default);
        }
        if (next.State is "publication-blocked" or "draft-published" && next.Qualification is { } qualified)
        {
            var source = qualified.GetProperty("source");
            var attempt = await ReadAgentAttemptAsync(connection, transaction, runId,
                source.GetProperty("attemptId").GetString()!, default);
            if (attempt?.Session.HumanRequest is { State: "open" } request)
            {
                await UpdateAgentReceiptAsync(connection, transaction, attempt with {
                    Session = attempt.Session with { HumanRequest = request with { State = "resolved" } } }, default);
                await AppendAgentEventAsync(connection, transaction, run, "HumanRequestResolved",
                    new { request.RequestId, attempt.AttemptId, attempt.Session.SessionId,
                        reason = "completed-work-reached-publication-disposition", next.State, next.CaptureHeadSha }, default);
            }
        }
        await transaction.CommitAsync();
        return next;
    }

    public async Task<string?> FindPublicationOwnerAsync(string repositoryId, string runId)
    {
        await using var connection = await _dataSource.OpenConnectionAsync();
        await using var read = new NpgsqlCommand("""
            SELECT p.run_id::text FROM wpcp_publications p
            JOIN wpcp_implementation_runs r USING(run_id)
            WHERE r.repository_id=@repo AND p.run_id<>@run AND
                (p.publication->>'state' NOT IN ('preflight-blocked', 'publication-blocked', 'draft-published')
                 OR (p.publication->>'dispatched'='true' AND p.publication->>'state'<>'draft-published'))
            ORDER BY r.run_started_at LIMIT 1
            """, connection);
        read.Parameters.AddWithValue("repo", repositoryId);
        read.Parameters.AddWithValue("run", Guid.Parse(runId));
        return await read.ExecuteScalarAsync() as string;
    }

    private static async Task<Publication?> ReadPublicationAsync(NpgsqlConnection connection,
        NpgsqlTransaction transaction, string runId, CancellationToken token)
    {
        await using var read = new NpgsqlCommand("SELECT publication::text FROM wpcp_publications WHERE run_id=@id", connection, transaction);
        read.Parameters.AddWithValue("id", Guid.Parse(runId));
        return await read.ExecuteScalarAsync(token) is string raw ? Deserialize<Publication>(raw) : null;
    }

    private const string PublicationSchema = """
        CREATE TABLE IF NOT EXISTS wpcp_publications (
            run_id uuid PRIMARY KEY REFERENCES wpcp_implementation_runs(run_id), publication jsonb NOT NULL
        );
        """;
}
