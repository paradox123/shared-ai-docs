using System.Text.Json;
using System.Text.Json.Serialization;

namespace Wpcp.Domain;

/// <summary>
/// The immutable product correlation captured when an issue becomes an implementation run.
/// This is deliberately independent of worker, framework, and scheduler identifiers.
/// </summary>
public sealed record RunCorrelation(
    [property: JsonPropertyName("runId")] string RunId,
    [property: JsonPropertyName("repositoryId")] string RepositoryId,
    [property: JsonPropertyName("issueId")] string IssueId,
    [property: JsonPropertyName("issueNumber")] int IssueNumber,
    [property: JsonPropertyName("commandId")] string CommandId,
    RepositoryBinding? Repository = null);

/// <summary>Versions of the product inputs captured at admission time.</summary>
public sealed record RunProvenance(
    [property: JsonPropertyName("sourceRevision")] string SourceRevision,
    [property: JsonPropertyName("packageRevision")] string PackageRevision,
    [property: JsonPropertyName("configurationRevision")] string ConfigurationRevision,
    [property: JsonPropertyName("contractRevision")] string ContractRevision)
{
    public void Validate()
    {
        Require(SourceRevision, nameof(SourceRevision));
        Require(PackageRevision, nameof(PackageRevision));
        Require(ConfigurationRevision, nameof(ConfigurationRevision));
        Require(ContractRevision, nameof(ContractRevision));
    }

    internal static void Require(string? value, string parameterName)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("A required correlation value was empty.", parameterName);
        }
    }
}

/// <summary>Safe, versioned metadata describing controlled-canary redaction.</summary>
public sealed record RedactionMetadata(
    [property: JsonPropertyName("occurred")] bool Occurred,
    [property: JsonPropertyName("policyVersion")] string PolicyVersion,
    [property: JsonPropertyName("marker")] string Marker);

/// <summary>
/// Raw, authorized start input. Its note is an input-only value and must be redacted by
/// the store before it is hashed, persisted, or included in an event.
/// </summary>
public sealed record StartRunCommand(
    [property: JsonPropertyName("commandId")] string CommandId,
    [property: JsonPropertyName("actorId")] string ActorId,
    [property: JsonPropertyName("repositoryId")] string RepositoryId,
    [property: JsonPropertyName("issueId")] string IssueId,
    [property: JsonPropertyName("issueNumber")] int IssueNumber,
    [property: JsonIgnore] string Note,
    [property: JsonPropertyName("provenance")] RunProvenance Provenance,
    ActorIdentity? Actor = null,
    RepositoryBinding? Repository = null)
{
    public void Validate()
    {
        RunProvenance.Require(CommandId, nameof(CommandId));
        RunProvenance.Require(ActorId, nameof(ActorId));
        RunProvenance.Require(RepositoryId, nameof(RepositoryId));
        RunProvenance.Require(IssueId, nameof(IssueId));
        RunProvenance.Require(Note, nameof(Note));
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(IssueNumber);
        ArgumentNullException.ThrowIfNull(Provenance);
        Provenance.Validate();
    }
}

/// <summary>The transactional classification of a start-command delivery.</summary>
public enum StartRunDisposition
{
    Accepted,
    Idempotent,
    CommandIdConflict,
    IssueAlreadyHasRun,
}

/// <summary>
/// Result of the command-inbox decision. HTTP hosts can serialize this result directly
/// and choose status codes from <see cref="Disposition"/> without re-reading storage.
/// </summary>
public sealed record StartRunResult(
    [property: JsonIgnore] StartRunDisposition Disposition,
    [property: JsonPropertyName("correlation")] RunCorrelation Correlation)
{
    [JsonPropertyName("outcome")]
    public string Outcome => Disposition switch
    {
        StartRunDisposition.Accepted => "accepted",
        StartRunDisposition.Idempotent => "idempotent",
        StartRunDisposition.CommandIdConflict => "conflict",
        StartRunDisposition.IssueAlreadyHasRun => "conflict",
        _ => throw new InvalidOperationException("Unknown command disposition."),
    };

    [JsonPropertyName("idempotent")]
    public bool Idempotent => Disposition == StartRunDisposition.Idempotent;

    [JsonPropertyName("code")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string? Code => Disposition switch
    {
        StartRunDisposition.CommandIdConflict => "command-id-conflict",
        StartRunDisposition.IssueAlreadyHasRun => "issue-already-has-run",
        _ => null,
    };

    [JsonPropertyName("runId")]
    public string RunId => Correlation.RunId;

    [JsonPropertyName("commandId")]
    public string CommandId => Correlation.CommandId;
}

/// <summary>A product-owned, append-only event from the canonical run history.</summary>
public sealed record CanonicalRunEvent(
    [property: JsonPropertyName("runId")] string RunId,
    [property: JsonPropertyName("position")] long Position,
    [property: JsonPropertyName("eventId")] string EventId,
    [property: JsonPropertyName("eventType")] string EventType,
    [property: JsonPropertyName("occurredAt")] DateTimeOffset OccurredAt,
    [property: JsonIgnore] string PayloadJson,
    [property: JsonIgnore] string CorrelationJson,
    [property: JsonIgnore] string ProvenanceJson,
    [property: JsonPropertyName("redaction")] RedactionMetadata Redaction)
{
    /// <summary>Returns the already-redacted event payload as JSON, not a JSON-encoded string.</summary>
    [JsonPropertyName("payload")]
    public JsonElement Payload
    {
        get
        {
            using var document = JsonDocument.Parse(PayloadJson);
            return document.RootElement.Clone();
        }
    }

    [JsonPropertyName("correlation")]
    public JsonElement Correlation
    {
        get
        {
            using var document = JsonDocument.Parse(CorrelationJson);
            return document.RootElement.Clone();
        }
    }

    [JsonPropertyName("provenance")]
    public JsonElement Provenance
    {
        get
        {
            using var document = JsonDocument.Parse(ProvenanceJson);
            return document.RootElement.Clone();
        }
    }
}

/// <summary>One product admission activity associated with a run.</summary>
public sealed record RunActivity(
    [property: JsonPropertyName("activityId")] string ActivityId,
    [property: JsonPropertyName("activityType")] string ActivityType,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("startedAt")] DateTimeOffset StartedAt,
    [property: JsonPropertyName("completedAt")] DateTimeOffset? CompletedAt);

/// <summary>One independently timed attempt within a product activity.</summary>
public sealed record RunAttempt(
    [property: JsonPropertyName("attemptId")] string AttemptId,
    [property: JsonPropertyName("activityId")] string ActivityId,
    [property: JsonPropertyName("attemptNumber")] int AttemptNumber,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("startedAt")] DateTimeOffset StartedAt,
    [property: JsonPropertyName("completedAt")] DateTimeOffset? CompletedAt,
    AgentSession? Session = null);

/// <summary>Supplemental process lifecycle evidence, never a canonical run event.</summary>
public sealed record ProcessObservation(
    [property: JsonPropertyName("processId")] string ProcessId,
    [property: JsonPropertyName("processKind")] string ProcessKind,
    [property: JsonPropertyName("processStartedAt")] DateTimeOffset ProcessStartedAt,
    [property: JsonPropertyName("processStoppedAt")] DateTimeOffset? ProcessStoppedAt)
{
    public ActorIdentity Actor => new("service", $"wpcp-{ProcessKind}", ProcessId);
}

/// <summary>Supplemental heartbeat evidence with its own time axis.</summary>
public sealed record HeartbeatObservation(
    [property: JsonPropertyName("heartbeatId")] string HeartbeatId,
    [property: JsonPropertyName("processId")] string ProcessId,
    [property: JsonPropertyName("heartbeatAt")] DateTimeOffset HeartbeatAt);

/// <summary>
/// Optional Agent Framework and Durable Task correlations. These identify execution
/// evidence only; they cannot replace product run state or canonical event positions.
/// </summary>
public sealed record ExecutionEvidence(
    [property: JsonPropertyName("evidenceId")] string EvidenceId,
    [property: JsonPropertyName("processId")] string ProcessId,
    [property: JsonPropertyName("agentFrameworkWorkflowId")] string? AgentFrameworkWorkflowId,
    [property: JsonPropertyName("agentFrameworkSessionId")] string? AgentFrameworkSessionId,
    [property: JsonPropertyName("durableTaskOrchestrationId")] string? DurableTaskOrchestrationId,
    [property: JsonPropertyName("durableTaskTaskId")] string? DurableTaskTaskId,
    [property: JsonPropertyName("recordedAt")] DateTimeOffset RecordedAt,
    [property: JsonPropertyName("note")] string? Note,
    [property: JsonPropertyName("redaction")] RedactionMetadata Redaction)
{
    public ActorIdentity Actor => new("service", "wpcp-worker", ProcessId);
}

/// <summary>The independently observable read projection returned to an Operator client.</summary>
public sealed record ImplementationRunProjection(
    [property: JsonPropertyName("runId")] string RunId,
    [property: JsonPropertyName("state")] string State,
    [property: JsonPropertyName("correlation")] RunCorrelation Correlation,
    [property: JsonPropertyName("runStartedAt")] DateTimeOffset RunStartedAt,
    [property: JsonPropertyName("activities")] IReadOnlyList<RunActivity> Activities,
    [property: JsonPropertyName("attempts")] IReadOnlyList<RunAttempt> Attempts,
    [property: JsonPropertyName("processes")] IReadOnlyList<ProcessObservation> Processes,
    [property: JsonPropertyName("heartbeats")] IReadOnlyList<HeartbeatObservation> Heartbeats,
    [property: JsonPropertyName("executionEvidence")] IReadOnlyList<ExecutionEvidence> ExecutionEvidence,
    [property: JsonPropertyName("provenance")] RunProvenance Provenance,
    [property: JsonPropertyName("redaction")] RedactionMetadata Redaction,
    [property: JsonPropertyName("lastPosition")] long LastPosition,
    [property: JsonPropertyName("control")] RunControlState Control,
    [property: JsonPropertyName("authorization")] ControlDecision? Authorization = null);

/// <summary>A canonical-history page strictly after an acknowledged event position.</summary>
public sealed record RunEventsPage(
    [property: JsonPropertyName("runId")] string RunId,
    [property: JsonPropertyName("after")] long After,
    [property: JsonPropertyName("events")] IReadOnlyList<CanonicalRunEvent> Events,
    [property: JsonPropertyName("lastPosition")] long LastPosition);

/// <summary>
/// The one real lifecycle transition a reporter is persisting.  A process emits
/// start, then zero or more heartbeats, then a stop; callers never synthesize all
/// three axes from one timestamp.
/// </summary>
public enum LifecycleObservationKind
{
    ProcessStarted,
    Heartbeat,
    ProcessStopped,
}

/// <summary>Raw lifecycle input. The storage seam redacts textual values before persistence.</summary>
public sealed record LifecycleObservation(
    [property: JsonPropertyName("runId")] string? RunId,
    [property: JsonPropertyName("kind")] LifecycleObservationKind Kind,
    [property: JsonPropertyName("processKind")] string ProcessKind,
    [property: JsonPropertyName("processId")] string ProcessId,
    [property: JsonPropertyName("observedAt")] DateTimeOffset ObservedAt,
    [property: JsonIgnore] string? AgentFrameworkWorkflowId = null,
    [property: JsonIgnore] string? AgentFrameworkSessionId = null,
    [property: JsonIgnore] string? DurableTaskOrchestrationId = null,
    [property: JsonIgnore] string? DurableTaskTaskId = null,
    [property: JsonIgnore] string? EvidenceNote = null)
{
    public bool HasExecutionEvidence =>
        !string.IsNullOrWhiteSpace(AgentFrameworkWorkflowId) ||
        !string.IsNullOrWhiteSpace(AgentFrameworkSessionId) ||
        !string.IsNullOrWhiteSpace(DurableTaskOrchestrationId) ||
        !string.IsNullOrWhiteSpace(DurableTaskTaskId) ||
        !string.IsNullOrWhiteSpace(EvidenceNote);

    public void Validate()
    {
        RunProvenance.Require(ProcessKind, nameof(ProcessKind));
        RunProvenance.Require(ProcessId, nameof(ProcessId));
    }
}

/// <summary>Result of persisting one correlated or global lifecycle report.</summary>
public sealed record LifecycleRecordResult(
    [property: JsonPropertyName("processId")] string ProcessId,
    [property: JsonPropertyName("observationId")] string ObservationId,
    [property: JsonPropertyName("evidenceId")] string? EvidenceId,
    [property: JsonPropertyName("redaction")] RedactionMetadata Redaction);

/// <summary>Public persistence seam used by the HTTP API and separately runnable worker.</summary>
public interface IImplementationRunStore
{
    Task EnsureSchemaAsync(CancellationToken cancellationToken = default);

    Task<StartRunResult> StartAsync(
        StartRunCommand command,
        CancellationToken cancellationToken = default);

    Task<ImplementationRunProjection?> GetProjectionAsync(
        string runId,
        CancellationToken cancellationToken = default);

    Task<RunEventsPage?> GetEventsAfterAsync(
        string runId,
        long afterPosition,
        CancellationToken cancellationToken = default);

    Task<LifecycleRecordResult> RecordLifecycleAsync(
        LifecycleObservation observation,
        CancellationToken cancellationToken = default);
}
