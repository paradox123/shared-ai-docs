using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Npgsql;
using NpgsqlTypes;
using Wpcp.Domain;

namespace Wpcp.Storage.Postgres;

/// <summary>
/// PostgreSQL implementation of the product-owned run record.  Agent Framework and
/// Durable Task identifiers are deliberately stored only as lifecycle evidence.
/// </summary>
public sealed partial class PostgresImplementationRunStore : IImplementationRunStore, IAsyncDisposable
{
    private const string StartCommandKind = "start-implementation-run";
    private const string AdmissionActivity = "admission";
    private const string StartedEvent = "ImplementationRunStarted";

    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    private readonly NpgsqlDataSource _dataSource;
    private readonly ControlledRedactionPolicy _redactionPolicy;

    public PostgresImplementationRunStore(
        string connectionString,
        ControlledRedactionPolicy redactionPolicy)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(connectionString);
        ArgumentNullException.ThrowIfNull(redactionPolicy);

        _dataSource = NpgsqlDataSource.Create(connectionString);
        _redactionPolicy = redactionPolicy;
    }

    public async Task EnsureSchemaAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
        await using var command = new NpgsqlCommand(Schema + AgentSchema, connection);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    public async Task<StartRunResult> StartAsync(
        StartRunCommand command,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(command);
        command.Validate();
        RejectControlledCanaryInCorrelation(command);

        var safe = Redact(command);
        var payloadDigest = Digest(safe.Payload);

        await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(cancellationToken);

        // Cross-process locks make duplicate delivery and issue identity decisions
        // deterministic without relying on a process-local cache.
        await AcquireLockAsync(connection, transaction, $"command:{command.CommandId}", cancellationToken);
        await AcquireLockAsync(
            connection,
            transaction,
            $"issue:{command.RepositoryId}:{command.IssueNumber}",
            cancellationToken);

        var existingCommand = await FindCommandAsync(
            connection, transaction, command.CommandId, cancellationToken);
        if (existingCommand is not null)
        {
            if (existingCommand.Correlation.Repository != command.Repository)
                throw new RepositoryBindingConflictException();
            await transaction.CommitAsync(cancellationToken);
            var disposition = string.Equals(existingCommand.PayloadDigest, payloadDigest, StringComparison.Ordinal)
                ? StartRunDisposition.Idempotent
                : StartRunDisposition.CommandIdConflict;
            return new StartRunResult(disposition, existingCommand.Correlation);
        }

        var existingIssue = await FindRunByIssueAsync(
            connection,
            transaction,
            command.RepositoryId,
            command.IssueNumber,
            cancellationToken);
        if (existingIssue is not null)
        {
            if (existingIssue.Correlation.Repository != command.Repository)
                throw new RepositoryBindingConflictException();
            await transaction.CommitAsync(cancellationToken);
            return new StartRunResult(StartRunDisposition.IssueAlreadyHasRun, existingIssue.Correlation);
        }

        var now = DateTimeOffset.UtcNow;
        var runId = Guid.NewGuid().ToString("D");
        var activityId = Guid.NewGuid().ToString("D");
        var attemptId = Guid.NewGuid().ToString("D");
        var eventId = Guid.NewGuid().ToString("D");
        var correlation = new RunCorrelation(
            runId,
            command.RepositoryId,
            command.IssueId,
            command.IssueNumber,
            command.CommandId,
            command.Repository);

        await InsertRunAsync(connection, transaction, correlation, now, safe, cancellationToken);
        await InsertCommandAsync(
            connection,
            transaction,
            command.CommandId,
            payloadDigest,
            correlation,
            now,
            safe,
            cancellationToken);
        await InsertAdmissionAsync(
            connection,
            transaction,
            activityId,
            attemptId,
            runId,
            now,
            cancellationToken);
        await InsertStartedEventAsync(
            connection,
            transaction,
            eventId,
            correlation,
            now,
            safe,
            cancellationToken);

        await AppendAuditAsync(connection, transaction, runId, "start", "implementation-run-started",
            command.Actor, cancellationToken);
        await transaction.CommitAsync(cancellationToken);
        return new StartRunResult(StartRunDisposition.Accepted, correlation);
    }

    public async Task<ImplementationRunProjection?> GetProjectionAsync(
        string runId,
        CancellationToken cancellationToken = default)
    {
        if (!Guid.TryParse(runId, out _))
        {
            return null;
        }

        await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(
            System.Data.IsolationLevel.RepeatableRead,
            cancellationToken);
        var run = await FindRunAsync(connection, transaction, runId, cancellationToken);
        if (run is null)
        {
            return null;
        }

        var activities = await ReadActivitiesAsync(connection, transaction, runId, cancellationToken);
        var attempts = await ReadAttemptsAsync(connection, transaction, runId, cancellationToken);
        var processes = await ReadProcessesAsync(connection, transaction, runId, cancellationToken);
        var heartbeats = await ReadHeartbeatsAsync(connection, transaction, runId, cancellationToken);
        var evidence = await ReadEvidenceAsync(connection, transaction, runId, cancellationToken);
        var lifecycleRedaction = await ReadLifecycleRedactionAsync(connection, transaction, runId, cancellationToken);
        var projection = new ImplementationRunProjection(
            run.Correlation.RunId,
            run.State,
            run.Correlation,
            run.RunStartedAt,
            activities,
            attempts,
            processes,
            heartbeats,
            evidence,
            run.Provenance,
            MergeRedaction(run.Redaction, lifecycleRedaction),
            run.LastPosition,
            await ReadControlStateAsync(connection, transaction, run, cancellationToken));
        await transaction.CommitAsync(cancellationToken);
        return projection;
    }

    public async Task<RunEventsPage?> GetEventsAfterAsync(
        string runId,
        long afterPosition,
        CancellationToken cancellationToken = default)
    {
        if (!Guid.TryParse(runId, out _) || afterPosition < 0)
        {
            return null;
        }

        await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(
            System.Data.IsolationLevel.RepeatableRead,
            cancellationToken);
        var run = await FindRunAsync(connection, transaction, runId, cancellationToken);
        if (run is null)
        {
            return null;
        }

        const string sql = """
            SELECT run_id::text, position, event_id::text, event_type, occurred_at,
                   payload::text, correlation::text, provenance::text,
                   redaction_occurred, redaction_policy_version, redaction_marker
              FROM wpcp_run_events
             WHERE run_id = @run_id AND position > @after_position
             ORDER BY position ASC;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
        command.Parameters.Add(new NpgsqlParameter("after_position", NpgsqlDbType.Bigint) { Value = afterPosition });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        var events = new List<CanonicalRunEvent>();
        while (await reader.ReadAsync(cancellationToken))
        {
            events.Add(new CanonicalRunEvent(
                reader.GetString(0),
                reader.GetInt64(1),
                reader.GetString(2),
                reader.GetString(3),
                reader.GetFieldValue<DateTimeOffset>(4),
                reader.GetString(5),
                reader.GetString(6),
                reader.GetString(7),
                ReadRedaction(reader, 8)));
        }

        await reader.CloseAsync();
        await transaction.CommitAsync(cancellationToken);
        return new RunEventsPage(runId, afterPosition, events, run.LastPosition);
    }

    public async Task<LifecycleRecordResult> RecordLifecycleAsync(
        LifecycleObservation observation,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(observation);
        observation.Validate();
        if (!Guid.TryParse(observation.RunId, out var runId))
        {
            throw new ArgumentException("A valid run ID is required for a lifecycle observation.", nameof(observation));
        }

        var safe = Redact(observation);
        await using var connection = await _dataSource.OpenConnectionAsync(cancellationToken);
        await using var transaction = await connection.BeginTransactionAsync(cancellationToken);
        var existing = await FindRunAsync(connection, transaction, observation.RunId!, cancellationToken);
        if (existing is null)
        {
            throw new InvalidOperationException("Cannot record lifecycle evidence for an unknown run.");
        }

        // A process ID identifies exactly one incarnation of a reporting process.
        // Serialize its transitions so an observer never receives a heartbeat or
        // stop record that cannot be attached to one visible process lifetime.
        await AcquireLockAsync(
            connection,
            transaction,
            $"lifecycle:{runId:D}:{safe.ProcessId}",
            cancellationToken);
        var lifecycle = await FindProcessLifecycleAsync(
            connection,
            transaction,
            runId,
            safe.ProcessId,
            cancellationToken);
        ValidateLifecycleTransition(observation, lifecycle);

        var observationId = Guid.NewGuid().ToString("D");
        var observationType = observation.Kind switch
        {
            LifecycleObservationKind.ProcessStarted => "process-started",
            LifecycleObservationKind.Heartbeat => "heartbeat",
            LifecycleObservationKind.ProcessStopped => "process-stopped",
            _ => throw new ArgumentOutOfRangeException(nameof(observation)),
        };
        var evidenceId = observation.Kind == LifecycleObservationKind.ProcessStarted && safe.HasEvidence
            ? Guid.NewGuid().ToString("D")
            : null;
        DateTimeOffset? heartbeatAt = observation.Kind == LifecycleObservationKind.Heartbeat
            ? observation.ObservedAt
            : null;
        DateTimeOffset? stoppedAt = observation.Kind == LifecycleObservationKind.ProcessStopped
            ? observation.ObservedAt
            : null;

        await InsertLifecycleAsync(
            connection, transaction, observationId, runId, safe.ProcessId, observationType,
            safe.ProcessKind, observation.ObservedAt, heartbeatAt, stoppedAt, safe, evidenceId, cancellationToken);

        await transaction.CommitAsync(cancellationToken);
        return new LifecycleRecordResult(safe.ProcessId, observationId, evidenceId, safe.Redaction);
    }

    public async ValueTask DisposeAsync() => await _dataSource.DisposeAsync();

    private static async Task AcquireLockAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string key,
        CancellationToken cancellationToken)
    {
        const string sql = "SELECT pg_advisory_xact_lock(hashtext(@key));";
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("key", NpgsqlDbType.Text) { Value = key });
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    private async Task<StoredCommand?> FindCommandAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction? transaction,
        string commandId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT payload_digest, run_id::text
              FROM wpcp_command_inbox
             WHERE command_id = @command_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("command_id", NpgsqlDbType.Text) { Value = commandId });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        if (!await reader.ReadAsync(cancellationToken))
        {
            return null;
        }

        var payloadDigest = reader.GetString(0);
        var runId = reader.GetString(1);
        await reader.CloseAsync();
        var run = await FindRunAsync(connection, transaction, runId, cancellationToken)
            ?? throw new InvalidOperationException("A command inbox row referenced a missing run.");
        return new StoredCommand(payloadDigest, run.Correlation);
    }

    private async Task<StoredRun?> FindRunByIssueAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction? transaction,
        string repositoryId,
        int issueNumber,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT run_id::text, repository_id, issue_id, issue_number, command_id,
                   state, run_started_at, last_position, provenance::text,
                   redaction_occurred, redaction_policy_version, redaction_marker, repository_binding::text
              FROM wpcp_implementation_runs
             WHERE repository_id = @repository_id AND issue_number = @issue_number;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("repository_id", NpgsqlDbType.Text) { Value = repositoryId });
        command.Parameters.Add(new NpgsqlParameter("issue_number", NpgsqlDbType.Integer) { Value = issueNumber });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        return await reader.ReadAsync(cancellationToken) ? ReadRun(reader) : null;
    }

    private async Task<StoredRun?> FindRunAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction? transaction,
        string runId,
        CancellationToken cancellationToken)
    {
        if (!Guid.TryParse(runId, out var parsed))
        {
            return null;
        }

        const string sql = """
            SELECT run_id::text, repository_id, issue_id, issue_number, command_id,
                   state, run_started_at, last_position, provenance::text,
                   redaction_occurred, redaction_policy_version, redaction_marker, repository_binding::text
              FROM wpcp_implementation_runs
             WHERE run_id = @run_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = parsed });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        return await reader.ReadAsync(cancellationToken) ? ReadRun(reader) : null;
    }

    private static StoredRun ReadRun(NpgsqlDataReader reader)
    {
        var correlation = new RunCorrelation(
            reader.GetString(0),
            reader.GetString(1),
            reader.GetString(2),
            reader.GetInt32(3),
            reader.GetString(4),
            reader.IsDBNull(12) ? null : Deserialize<RepositoryBinding>(reader.GetString(12)));
        return new StoredRun(
            correlation,
            reader.GetString(5),
            reader.GetFieldValue<DateTimeOffset>(6),
            reader.GetInt64(7),
            Deserialize<RunProvenance>(reader.GetString(8)),
            ReadRedaction(reader, 9));
    }

    private static RedactionMetadata ReadRedaction(NpgsqlDataReader reader, int occurredOrdinal)
    {
        return new RedactionMetadata(
            reader.GetBoolean(occurredOrdinal),
            reader.IsDBNull(occurredOrdinal + 1) ? string.Empty : reader.GetString(occurredOrdinal + 1),
            reader.IsDBNull(occurredOrdinal + 2) ? string.Empty : reader.GetString(occurredOrdinal + 2));
    }

    private async Task InsertRunAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        RunCorrelation correlation,
        DateTimeOffset now,
        SafeStart safe,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO wpcp_implementation_runs (
                run_id, repository_id, issue_id, issue_number, command_id, state,
                run_started_at, last_position, provenance, redaction_occurred,
                redaction_policy_version, redaction_marker, repository_binding)
            VALUES (
                @run_id, @repository_id, @issue_id, @issue_number, @command_id, 'admitted',
                @run_started_at, 1, @provenance, @redaction_occurred,
                @redaction_policy_version, @redaction_marker, @repository_binding);
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        AddJson(command, "repository_binding", correlation.Repository!);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(correlation.RunId) });
        command.Parameters.Add(new NpgsqlParameter("repository_id", NpgsqlDbType.Text) { Value = correlation.RepositoryId });
        command.Parameters.Add(new NpgsqlParameter("issue_id", NpgsqlDbType.Text) { Value = correlation.IssueId });
        command.Parameters.Add(new NpgsqlParameter("issue_number", NpgsqlDbType.Integer) { Value = correlation.IssueNumber });
        command.Parameters.Add(new NpgsqlParameter("command_id", NpgsqlDbType.Text) { Value = correlation.CommandId });
        command.Parameters.Add(new NpgsqlParameter("run_started_at", NpgsqlDbType.TimestampTz) { Value = now });
        AddJson(command, "provenance", safe.Provenance);
        AddRedaction(command, safe.Redaction);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    private static async Task InsertCommandAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string commandId,
        string payloadDigest,
        RunCorrelation correlation,
        DateTimeOffset now,
        SafeStart safe,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO wpcp_command_inbox (
                command_id, command_kind, payload_digest, run_id, accepted_at, redacted_payload,
                redaction_occurred, redaction_policy_version, redaction_marker)
            VALUES (
                @command_id, @command_kind, @payload_digest, @run_id, @accepted_at, @redacted_payload,
                @redaction_occurred, @redaction_policy_version, @redaction_marker);
            """;
        await using var db = new NpgsqlCommand(sql, connection, transaction);
        db.Parameters.Add(new NpgsqlParameter("command_id", NpgsqlDbType.Text) { Value = commandId });
        db.Parameters.Add(new NpgsqlParameter("command_kind", NpgsqlDbType.Text) { Value = StartCommandKind });
        db.Parameters.Add(new NpgsqlParameter("payload_digest", NpgsqlDbType.Text) { Value = payloadDigest });
        db.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(correlation.RunId) });
        db.Parameters.Add(new NpgsqlParameter("accepted_at", NpgsqlDbType.TimestampTz) { Value = now });
        AddJson(db, "redacted_payload", safe.Payload);
        AddRedaction(db, safe.Redaction);
        await db.ExecuteNonQueryAsync(cancellationToken);
    }

    private static async Task InsertAdmissionAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string activityId,
        string attemptId,
        string runId,
        DateTimeOffset now,
        CancellationToken cancellationToken)
    {
        const string activitySql = """
            INSERT INTO wpcp_run_activities (
                activity_id, run_id, activity_type, state, started_at, completed_at)
            VALUES (@activity_id, @run_id, @activity_type, 'completed', @started_at, @completed_at);
            """;
        await using (var activity = new NpgsqlCommand(activitySql, connection, transaction))
        {
            activity.Parameters.Add(new NpgsqlParameter("activity_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(activityId) });
            activity.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
            activity.Parameters.Add(new NpgsqlParameter("activity_type", NpgsqlDbType.Text) { Value = AdmissionActivity });
            activity.Parameters.Add(new NpgsqlParameter("started_at", NpgsqlDbType.TimestampTz) { Value = now });
            activity.Parameters.Add(new NpgsqlParameter("completed_at", NpgsqlDbType.TimestampTz) { Value = now });
            await activity.ExecuteNonQueryAsync(cancellationToken);
        }

        const string attemptSql = """
            INSERT INTO wpcp_activity_attempts (
                attempt_id, activity_id, attempt_number, state, started_at, completed_at)
            VALUES (@attempt_id, @activity_id, 1, 'completed', @started_at, @completed_at);
            """;
        await using var attempt = new NpgsqlCommand(attemptSql, connection, transaction);
        attempt.Parameters.Add(new NpgsqlParameter("attempt_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(attemptId) });
        attempt.Parameters.Add(new NpgsqlParameter("activity_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(activityId) });
        attempt.Parameters.Add(new NpgsqlParameter("started_at", NpgsqlDbType.TimestampTz) { Value = now });
        attempt.Parameters.Add(new NpgsqlParameter("completed_at", NpgsqlDbType.TimestampTz) { Value = now });
        await attempt.ExecuteNonQueryAsync(cancellationToken);
    }

    private static async Task InsertStartedEventAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string eventId,
        RunCorrelation correlation,
        DateTimeOffset now,
        SafeStart safe,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO wpcp_run_events (
                run_id, position, event_id, event_type, occurred_at, correlation, payload,
                provenance, redaction_occurred, redaction_policy_version, redaction_marker)
            VALUES (
                @run_id, 1, @event_id, @event_type, @occurred_at, @correlation, @payload,
                @provenance, @redaction_occurred, @redaction_policy_version, @redaction_marker);
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(correlation.RunId) });
        command.Parameters.Add(new NpgsqlParameter("event_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(eventId) });
        command.Parameters.Add(new NpgsqlParameter("event_type", NpgsqlDbType.Text) { Value = StartedEvent });
        command.Parameters.Add(new NpgsqlParameter("occurred_at", NpgsqlDbType.TimestampTz) { Value = now });
        AddJson(command, "correlation", correlation);
        AddJson(command, "payload", new
        {
            actor = safe.Actor,
            authorization = new { decision = "authorized", source = safe.Actor?.Provider ?? "synthetic-provider-fixture" },
            note = safe.Note,
        });
        AddJson(command, "provenance", safe.Provenance);
        AddRedaction(command, safe.Redaction);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    private static async Task InsertLifecycleAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string observationId,
        Guid runId,
        string processId,
        string observationType,
        string processKind,
        DateTimeOffset observedAt,
        DateTimeOffset? heartbeatAt,
        DateTimeOffset? processStoppedAt,
        SafeLifecycle safe,
        string? evidenceId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            INSERT INTO wpcp_lifecycle_observations (
                observation_id, run_id, process_id, observation_type, process_kind,
                process_started_at, heartbeat_at, process_stopped_at, evidence_id,
                agent_framework_workflow_id, agent_framework_session_id,
                durable_task_orchestration_id, durable_task_task_id, evidence_note,
                redaction_occurred, redaction_policy_version, redaction_marker)
            VALUES (
                @observation_id, @run_id, @process_id, @observation_type, @process_kind,
                @process_started_at, @heartbeat_at, @process_stopped_at, @evidence_id,
                @agent_framework_workflow_id, @agent_framework_session_id,
                @durable_task_orchestration_id, @durable_task_task_id, @evidence_note,
                @redaction_occurred, @redaction_policy_version, @redaction_marker);
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("observation_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(observationId) });
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = runId });
        command.Parameters.Add(new NpgsqlParameter("process_id", NpgsqlDbType.Text) { Value = processId });
        command.Parameters.Add(new NpgsqlParameter("observation_type", NpgsqlDbType.Text) { Value = observationType });
        command.Parameters.Add(new NpgsqlParameter("process_kind", NpgsqlDbType.Text) { Value = processKind });
        command.Parameters.Add(new NpgsqlParameter("process_started_at", NpgsqlDbType.TimestampTz) { Value = observedAt });
        AddNullable(command, "heartbeat_at", NpgsqlDbType.TimestampTz, heartbeatAt);
        AddNullable(command, "process_stopped_at", NpgsqlDbType.TimestampTz, processStoppedAt);
        AddNullable(command, "evidence_id", NpgsqlDbType.Uuid, evidenceId is null ? null : Guid.Parse(evidenceId));
        AddNullable(command, "agent_framework_workflow_id", NpgsqlDbType.Text, safe.AgentFrameworkWorkflowId);
        AddNullable(command, "agent_framework_session_id", NpgsqlDbType.Text, safe.AgentFrameworkSessionId);
        AddNullable(command, "durable_task_orchestration_id", NpgsqlDbType.Text, safe.DurableTaskOrchestrationId);
        AddNullable(command, "durable_task_task_id", NpgsqlDbType.Text, safe.DurableTaskTaskId);
        AddNullable(command, "evidence_note", NpgsqlDbType.Text, safe.EvidenceNote);
        AddRedaction(command, safe.Redaction);
        await command.ExecuteNonQueryAsync(cancellationToken);
    }

    private static async Task<ProcessLifecycleState> FindProcessLifecycleAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        Guid runId,
        string processId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT COUNT(*) FILTER (WHERE observation_type = 'process-started'),
                   COALESCE(bool_or(observation_type = 'process-stopped'), false),
                   MAX(process_started_at)
              FROM wpcp_lifecycle_observations
             WHERE run_id = @run_id AND process_id = @process_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = runId });
        command.Parameters.Add(new NpgsqlParameter("process_id", NpgsqlDbType.Text) { Value = processId });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        if (!await reader.ReadAsync(cancellationToken))
        {
            throw new InvalidOperationException("The lifecycle aggregate query returned no row.");
        }

        return new ProcessLifecycleState(
            reader.GetInt64(0) > 0,
            reader.GetBoolean(1),
            reader.IsDBNull(2) ? null : reader.GetFieldValue<DateTimeOffset>(2));
    }

    private static void ValidateLifecycleTransition(
        LifecycleObservation observation,
        ProcessLifecycleState lifecycle)
    {
        if (lifecycle.LastObservedAt is { } lastObservedAt && observation.ObservedAt < lastObservedAt)
        {
            throw new ArgumentException("Lifecycle observations cannot move backwards in time.", nameof(observation));
        }

        switch (observation.Kind)
        {
            case LifecycleObservationKind.ProcessStarted when lifecycle.HasStarted:
                throw new ArgumentException("A process ID may identify only one lifecycle incarnation.", nameof(observation));
            case LifecycleObservationKind.Heartbeat when !lifecycle.HasStarted || lifecycle.HasStopped:
                throw new ArgumentException("A heartbeat requires an active process lifecycle.", nameof(observation));
            case LifecycleObservationKind.ProcessStopped when !lifecycle.HasStarted || lifecycle.HasStopped:
                throw new ArgumentException("A stop requires an active process lifecycle.", nameof(observation));
        }
    }

    private static async Task<IReadOnlyList<RunActivity>> ReadActivitiesAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string runId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT activity_id::text, activity_type, state, started_at, completed_at
              FROM wpcp_run_activities
             WHERE run_id = @run_id ORDER BY started_at, activity_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        var results = new List<RunActivity>();
        while (await reader.ReadAsync(cancellationToken))
        {
            results.Add(new RunActivity(
                reader.GetString(0), reader.GetString(1), reader.GetString(2),
                reader.GetFieldValue<DateTimeOffset>(3),
                reader.IsDBNull(4) ? null : reader.GetFieldValue<DateTimeOffset>(4)));
        }
        return results;
    }

    private static async Task<IReadOnlyList<RunAttempt>> ReadAttemptsAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string runId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT attempt.attempt_id::text, attempt.activity_id::text, attempt.attempt_number,
                   attempt.state, attempt.started_at, attempt.completed_at, session.receipt::text
              FROM wpcp_activity_attempts attempt
              JOIN wpcp_run_activities activity ON activity.activity_id = attempt.activity_id
              LEFT JOIN wpcp_agent_sessions session ON session.attempt_id = attempt.attempt_id
             WHERE activity.run_id = @run_id
             ORDER BY attempt.started_at, attempt.attempt_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        var results = new List<RunAttempt>();
        while (await reader.ReadAsync(cancellationToken))
        {
            results.Add(new RunAttempt(
                reader.GetString(0), reader.GetString(1), reader.GetInt32(2), reader.GetString(3),
                reader.GetFieldValue<DateTimeOffset>(4),
                reader.IsDBNull(5) ? null : reader.GetFieldValue<DateTimeOffset>(5),
                reader.IsDBNull(6) ? null : Deserialize<AgentAttemptReceipt>(reader.GetString(6)).Session));
        }
        return results;
    }

    private static async Task<IReadOnlyList<ProcessObservation>> ReadProcessesAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string runId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT started.process_id, started.process_kind, started.process_started_at,
                   (
                       SELECT stopped.process_stopped_at
                         FROM wpcp_lifecycle_observations stopped
                        WHERE stopped.run_id = started.run_id
                          AND stopped.process_id = started.process_id
                          AND stopped.observation_type = 'process-stopped'
                        ORDER BY stopped.process_stopped_at DESC
                        LIMIT 1
                   )
              FROM wpcp_lifecycle_observations started
             WHERE started.run_id = @run_id AND started.observation_type = 'process-started'
             ORDER BY started.process_started_at, started.process_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        var results = new List<ProcessObservation>();
        while (await reader.ReadAsync(cancellationToken))
        {
            results.Add(new ProcessObservation(
                reader.GetString(0), reader.GetString(1), reader.GetFieldValue<DateTimeOffset>(2),
                reader.IsDBNull(3) ? null : reader.GetFieldValue<DateTimeOffset>(3)));
        }
        return results;
    }

    private static async Task<IReadOnlyList<HeartbeatObservation>> ReadHeartbeatsAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string runId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT observation_id::text, process_id, heartbeat_at
              FROM wpcp_lifecycle_observations
             WHERE run_id = @run_id AND observation_type = 'heartbeat'
             ORDER BY heartbeat_at, observation_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        var results = new List<HeartbeatObservation>();
        while (await reader.ReadAsync(cancellationToken))
        {
            results.Add(new HeartbeatObservation(
                reader.GetString(0), reader.GetString(1), reader.GetFieldValue<DateTimeOffset>(2)));
        }
        return results;
    }

    private static async Task<IReadOnlyList<ExecutionEvidence>> ReadEvidenceAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string runId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT evidence_id::text, process_id, agent_framework_workflow_id,
                   agent_framework_session_id, durable_task_orchestration_id,
                   durable_task_task_id, process_started_at, evidence_note,
                   redaction_occurred, redaction_policy_version, redaction_marker
              FROM wpcp_lifecycle_observations
             WHERE run_id = @run_id AND evidence_id IS NOT NULL
             ORDER BY process_started_at, evidence_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        var results = new List<ExecutionEvidence>();
        while (await reader.ReadAsync(cancellationToken))
        {
            results.Add(new ExecutionEvidence(
                reader.GetString(0), reader.GetString(1),
                ReadNullableString(reader, 2), ReadNullableString(reader, 3),
                ReadNullableString(reader, 4), ReadNullableString(reader, 5),
                reader.GetFieldValue<DateTimeOffset>(6), ReadNullableString(reader, 7),
                ReadRedaction(reader, 8)));
        }
        return results;
    }

    private static async Task<RedactionMetadata> ReadLifecycleRedactionAsync(
        NpgsqlConnection connection,
        NpgsqlTransaction transaction,
        string runId,
        CancellationToken cancellationToken)
    {
        const string sql = """
            SELECT COALESCE(bool_or(redaction_occurred), false),
                   COALESCE(max(redaction_policy_version) FILTER (WHERE redaction_occurred), ''),
                   COALESCE(max(redaction_marker) FILTER (WHERE redaction_occurred), '')
              FROM wpcp_lifecycle_observations
             WHERE run_id = @run_id;
            """;
        await using var command = new NpgsqlCommand(sql, connection, transaction);
        command.Parameters.Add(new NpgsqlParameter("run_id", NpgsqlDbType.Uuid) { Value = Guid.Parse(runId) });
        await using var reader = await command.ExecuteReaderAsync(cancellationToken);
        if (!await reader.ReadAsync(cancellationToken))
        {
            return new RedactionMetadata(false, string.Empty, string.Empty);
        }

        return new RedactionMetadata(reader.GetBoolean(0), reader.GetString(1), reader.GetString(2));
    }

    private static RedactionMetadata MergeRedaction(
        RedactionMetadata runRedaction,
        RedactionMetadata lifecycleRedaction) =>
        lifecycleRedaction.Occurred ? lifecycleRedaction : runRedaction;

    private SafeStart Redact(StartRunCommand command)
    {
        var note = _redactionPolicy.Redact(command.Note);
        var source = _redactionPolicy.Redact(command.Provenance.SourceRevision);
        var package = _redactionPolicy.Redact(command.Provenance.PackageRevision);
        var configuration = _redactionPolicy.Redact(command.Provenance.ConfigurationRevision);
        var contract = _redactionPolicy.Redact(command.Provenance.ContractRevision);
        var occurred = note.Occurred || source.Occurred || package.Occurred || configuration.Occurred || contract.Occurred;
        var provenance = new RunProvenance(
            source.Value!, package.Value!, configuration.Value!, contract.Value!);
        var payload = new
        {
            commandId = command.CommandId,
            actorId = command.ActorId,
            repositoryId = command.RepositoryId,
            repository = command.Repository,
            issueId = command.IssueId,
            issueNumber = command.IssueNumber,
            note = note.Value,
            provenance,
        };
        return new SafeStart(note.Value!, provenance, payload, _redactionPolicy.Metadata(occurred), command.Actor);
    }

    private void RejectControlledCanaryInCorrelation(StartRunCommand command)
    {
        if (_redactionPolicy.ContainsControlledCanary(command.CommandId) ||
            _redactionPolicy.ContainsControlledCanary(command.ActorId) ||
            _redactionPolicy.ContainsControlledCanary(command.RepositoryId) ||
            _redactionPolicy.ContainsControlledCanary(command.IssueId))
        {
            // Do not rewrite keys that establish idempotency or authorization: a
            // caller gets a generic rejection and the raw value never reaches a
            // digest, event, projection, inbox row, or response.
            throw new ArgumentException("A controlled canary cannot be used as a correlation identifier.");
        }
    }

    private SafeLifecycle Redact(LifecycleObservation observation)
    {
        var processKind = _redactionPolicy.Redact(observation.ProcessKind);
        var processId = _redactionPolicy.Redact(observation.ProcessId);
        var frameworkWorkflow = _redactionPolicy.Redact(observation.AgentFrameworkWorkflowId);
        var frameworkSession = _redactionPolicy.Redact(observation.AgentFrameworkSessionId);
        var durabilityOrchestration = _redactionPolicy.Redact(observation.DurableTaskOrchestrationId);
        var durabilityTask = _redactionPolicy.Redact(observation.DurableTaskTaskId);
        var note = _redactionPolicy.Redact(observation.EvidenceNote);
        var occurred = processKind.Occurred || processId.Occurred ||
            frameworkWorkflow.Occurred || frameworkSession.Occurred ||
            durabilityOrchestration.Occurred || durabilityTask.Occurred || note.Occurred;
        return new SafeLifecycle(
            processKind.Value!, processId.Value!, frameworkWorkflow.Value, frameworkSession.Value, durabilityOrchestration.Value,
            durabilityTask.Value, note.Value, observation.HasExecutionEvidence,
            _redactionPolicy.Metadata(occurred));
    }

    private static string Digest(object payload)
    {
        var json = JsonSerializer.Serialize(payload, JsonOptions);
        return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(json))).ToLowerInvariant();
    }

    private static T Deserialize<T>(string value) =>
        JsonSerializer.Deserialize<T>(value, JsonOptions)
        ?? throw new InvalidOperationException("A stored JSON value could not be deserialized.");

    private static void AddJson(NpgsqlCommand command, string name, object value) =>
        command.Parameters.Add(new NpgsqlParameter(name, NpgsqlDbType.Jsonb)
        {
            Value = JsonSerializer.Serialize(value, JsonOptions),
        });

    private static void AddRedaction(NpgsqlCommand command, RedactionMetadata redaction)
    {
        command.Parameters.Add(new NpgsqlParameter("redaction_occurred", NpgsqlDbType.Boolean) { Value = redaction.Occurred });
        AddNullable(command, "redaction_policy_version", NpgsqlDbType.Text, redaction.Occurred ? redaction.PolicyVersion : null);
        AddNullable(command, "redaction_marker", NpgsqlDbType.Text, redaction.Occurred ? redaction.Marker : null);
    }

    private static void AddNullable(NpgsqlCommand command, string name, NpgsqlDbType type, object? value) =>
        command.Parameters.Add(new NpgsqlParameter(name, type) { Value = value ?? DBNull.Value });

    private static string? ReadNullableString(NpgsqlDataReader reader, int ordinal) =>
        reader.IsDBNull(ordinal) ? null : reader.GetString(ordinal);

    private sealed record StoredCommand(string PayloadDigest, RunCorrelation Correlation);

    private sealed record StoredRun(
        RunCorrelation Correlation,
        string State,
        DateTimeOffset RunStartedAt,
        long LastPosition,
        RunProvenance Provenance,
        RedactionMetadata Redaction);

    private sealed record ProcessLifecycleState(
        bool HasStarted,
        bool HasStopped,
        DateTimeOffset? LastObservedAt);

    private sealed record SafeStart(
        string Note,
        RunProvenance Provenance,
        object Payload,
        RedactionMetadata Redaction,
        ActorIdentity? Actor);

    private sealed record SafeLifecycle(
        string ProcessKind,
        string ProcessId,
        string? AgentFrameworkWorkflowId,
        string? AgentFrameworkSessionId,
        string? DurableTaskOrchestrationId,
        string? DurableTaskTaskId,
        string? EvidenceNote,
        bool HasEvidence,
        RedactionMetadata Redaction);

    private const string Schema = """
        CREATE TABLE IF NOT EXISTS wpcp_implementation_runs (
            run_id uuid PRIMARY KEY,
            repository_id text NOT NULL,
            issue_id text NOT NULL,
            issue_number integer NOT NULL CHECK (issue_number > 0),
            command_id text NOT NULL UNIQUE,
            state text NOT NULL,
            run_started_at timestamptz NOT NULL,
            last_position bigint NOT NULL CHECK (last_position >= 0),
            provenance jsonb NOT NULL,
            redaction_occurred boolean NOT NULL,
            redaction_policy_version text,
            redaction_marker text,
            UNIQUE (repository_id, issue_number)
        );

        ALTER TABLE wpcp_implementation_runs ADD COLUMN IF NOT EXISTS repository_binding jsonb;
        ALTER TABLE wpcp_implementation_runs ADD COLUMN IF NOT EXISTS lease_epoch bigint NOT NULL DEFAULT 0;
        ALTER TABLE wpcp_implementation_runs ADD COLUMN IF NOT EXISTS lease_holder jsonb;
        ALTER TABLE wpcp_implementation_runs ADD COLUMN IF NOT EXISTS lease_claimed_at timestamptz;
        ALTER TABLE wpcp_implementation_runs ADD COLUMN IF NOT EXISTS head_sha text;

        CREATE TABLE IF NOT EXISTS wpcp_security_audit (
            position bigserial PRIMARY KEY,
            run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            occurred_at timestamptz NOT NULL,
            action text NOT NULL,
            code text NOT NULL,
            actor jsonb
        );
        CREATE INDEX IF NOT EXISTS wpcp_security_audit_run_idx ON wpcp_security_audit(run_id, position);

        CREATE TABLE IF NOT EXISTS wpcp_command_inbox (
            command_id text PRIMARY KEY,
            command_kind text NOT NULL,
            payload_digest text NOT NULL,
            run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            accepted_at timestamptz NOT NULL,
            redacted_payload jsonb NOT NULL,
            redaction_occurred boolean NOT NULL,
            redaction_policy_version text,
            redaction_marker text
        );

        CREATE TABLE IF NOT EXISTS wpcp_run_activities (
            activity_id uuid PRIMARY KEY,
            run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            activity_type text NOT NULL,
            state text NOT NULL,
            started_at timestamptz NOT NULL,
            completed_at timestamptz
        );

        CREATE TABLE IF NOT EXISTS wpcp_activity_attempts (
            attempt_id uuid PRIMARY KEY,
            activity_id uuid NOT NULL REFERENCES wpcp_run_activities(activity_id),
            attempt_number integer NOT NULL,
            state text NOT NULL,
            started_at timestamptz NOT NULL,
            completed_at timestamptz,
            UNIQUE (activity_id, attempt_number)
        );

        CREATE TABLE IF NOT EXISTS wpcp_run_events (
            run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            position bigint NOT NULL CHECK (position > 0),
            event_id uuid NOT NULL UNIQUE,
            event_type text NOT NULL,
            occurred_at timestamptz NOT NULL,
            correlation jsonb NOT NULL,
            payload jsonb NOT NULL,
            provenance jsonb NOT NULL,
            redaction_occurred boolean NOT NULL,
            redaction_policy_version text,
            redaction_marker text,
            PRIMARY KEY (run_id, position)
        );

        CREATE TABLE IF NOT EXISTS wpcp_lifecycle_observations (
            observation_id uuid PRIMARY KEY,
            run_id uuid NOT NULL REFERENCES wpcp_implementation_runs(run_id),
            process_id text NOT NULL,
            observation_type text NOT NULL,
            process_kind text NOT NULL,
            process_started_at timestamptz NOT NULL,
            heartbeat_at timestamptz,
            process_stopped_at timestamptz,
            evidence_id uuid,
            agent_framework_workflow_id text,
            agent_framework_session_id text,
            durable_task_orchestration_id text,
            durable_task_task_id text,
            evidence_note text,
            redaction_occurred boolean NOT NULL,
            redaction_policy_version text,
            redaction_marker text
        );

        CREATE INDEX IF NOT EXISTS wpcp_lifecycle_run_type_idx
            ON wpcp_lifecycle_observations (run_id, observation_type, process_started_at);
        """;
}
