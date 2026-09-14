using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Npgsql;
using NpgsqlTypes;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

/// <summary>Immutable, redacted intake records, independent of worker/run admission.</summary>
public sealed class PostgresSubmissionStore(string connectionString, ControlledRedactionPolicy policy) : IAsyncDisposable
{
    private readonly NpgsqlDataSource _dataSource = NpgsqlDataSource.Create(connectionString);
    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    public async Task EnsureSchemaAsync()
    {
        await using var command = _dataSource.CreateCommand("""
            CREATE TABLE IF NOT EXISTS wpcp_submissions (
                submission_id uuid PRIMARY KEY,
                provider_issue_id bigint NOT NULL UNIQUE,
                repository_id text NOT NULL,
                admitted_at timestamptz NOT NULL,
                snapshot jsonb NOT NULL
            );
            CREATE INDEX IF NOT EXISTS wpcp_submissions_repository
                ON wpcp_submissions (repository_id, admitted_at DESC);
            CREATE TABLE IF NOT EXISTS wpcp_submission_dispatch (
                submission_id uuid PRIMARY KEY REFERENCES wpcp_submissions(submission_id),
                run_id uuid NOT NULL UNIQUE REFERENCES wpcp_implementation_runs(run_id),
                configuration jsonb NOT NULL,
                state text NOT NULL DEFAULT 'queued',
                code text,
                queued_at timestamptz NOT NULL,
                completed_at timestamptz
            );
            """);
        await command.ExecuteNonQueryAsync();
    }

    public async Task<SubmissionAdmission> AdmitAsync(string title, string body,
        SubmissionSource source, RepositoryBinding repository, ActorIdentity actor, CancellationToken token)
    {
        // Correlation values must keep their identity; never rewrite them to a redaction marker.
        if (policy.ContainsControlledCanary(JsonSerializer.Serialize(new { source, repository, actor }, JsonOptions)))
            throw new ArgumentException("submission-correlation-rejected");
        var safeTitle = policy.Redact(title);
        var safeBody = policy.Redact(body);
        var digest = Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(
            JsonSerializer.Serialize(new { title = safeTitle.Value, body = safeBody.Value }, JsonOptions))));
        var submission = new Submission(Guid.NewGuid().ToString("D"), "admitted", null,
            safeTitle.Value!, safeBody.Value!, source, repository, actor, DateTimeOffset.UtcNow,
            digest, policy.Metadata(safeTitle.Occurred || safeBody.Occurred));
        await using var connection = await _dataSource.OpenConnectionAsync(token);
        await using var command = new NpgsqlCommand("""
            INSERT INTO wpcp_submissions (submission_id, provider_issue_id, repository_id, admitted_at, snapshot)
            VALUES (@id, @issue, @repository, @time, @snapshot)
            ON CONFLICT (provider_issue_id) DO NOTHING RETURNING snapshot::text;
            """, connection);
        command.Parameters.AddWithValue("id", Guid.Parse(submission.SubmissionId));
        command.Parameters.AddWithValue("issue", source.ProviderIssueId);
        command.Parameters.AddWithValue("repository", repository.RepositoryId);
        command.Parameters.AddWithValue("time", submission.AdmittedAt);
        command.Parameters.AddWithValue("snapshot", NpgsqlDbType.Jsonb, JsonSerializer.Serialize(submission, JsonOptions));
        var inserted = await command.ExecuteScalarAsync(token) as string;
        if (inserted is not null) return new(Read(inserted), true);
        // A concurrent insert has committed before ON CONFLICT returns. Read its first snapshot.
        await using var existing = new NpgsqlCommand(
            "SELECT snapshot::text FROM wpcp_submissions WHERE provider_issue_id = @issue", connection);
        existing.Parameters.AddWithValue("issue", source.ProviderIssueId);
        var original = Read((string)(await existing.ExecuteScalarAsync(token))!);
        if (original.Repository != repository) throw new RepositoryBindingConflictException();
        return new((await GetAsync(Guid.Parse(original.SubmissionId), token))!, false);
    }

    public async Task<Submission?> GetAsync(Guid id, CancellationToken token)
    {
        await using var command = _dataSource.CreateCommand(
            "SELECT " + SnapshotProjection + " FROM wpcp_submissions s LEFT JOIN wpcp_submission_dispatch d USING (submission_id) WHERE submission_id = @id");
        command.Parameters.AddWithValue("id", id);
        return await command.ExecuteScalarAsync(token) is string json ? Read(json) : null;
    }

    public async Task<Submission?> FindBySourceAsync(long providerIssueId, CancellationToken token)
    {
        await using var command = _dataSource.CreateCommand(
            "SELECT submission_id FROM wpcp_submissions WHERE provider_issue_id=@id");
        command.Parameters.AddWithValue("id", providerIssueId);
        return await command.ExecuteScalarAsync(token) is Guid id ? await GetAsync(id, token) : null;
    }

    public async Task<IReadOnlyList<Submission>> ListAsync(CancellationToken token)
    {
        await using var command = _dataSource.CreateCommand(
            "SELECT " + SnapshotProjection + " FROM wpcp_submissions s LEFT JOIN wpcp_submission_dispatch d USING (submission_id) ORDER BY admitted_at DESC, submission_id");
        await using var reader = await command.ExecuteReaderAsync(token);
        var result = new List<Submission>();
        while (await reader.ReadAsync(token)) result.Add(Read(reader.GetString(0)));
        return result;
    }

    private static Submission Read(string json) => JsonSerializer.Deserialize<Submission>(json, JsonOptions)!;
    private const string SnapshotProjection = "(s.snapshot || CASE WHEN d.run_id IS NULL THEN '{}'::jsonb ELSE jsonb_build_object('runId', d.run_id::text, 'state', 'started') END)::text";
    public ValueTask DisposeAsync() => _dataSource.DisposeAsync();
}
