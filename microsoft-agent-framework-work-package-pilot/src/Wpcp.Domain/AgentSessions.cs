using System.Text.Json;

namespace Wpcp.Domain;

public sealed record OpenInCodexCapability(
    string Mode = "unsupported", bool SameSession = false, bool AppTaskVisible = false,
    string Reason = "fake-adapter-has-no-codex-app-session", string? Url = null);

public sealed record AgentSession(
    string OperationKey, string? SessionId = null, string Status = "start-pending",
    string ContractVersion = "AgentSessionAdapter/v1", string? StartedEventId = null,
    int LastSequence = 0, string? LastEventId = null, JsonElement? OriginalResult = null,
    string? OriginalResultEventId = null, string? FailureCategory = null,
    OpenInCodexCapability? OpenInCodex = null,
    JsonElement? ObservedResponse = null, int? ResponseStatus = null, string? ResponseEventId = null);

public sealed record AgentAttemptReceipt(
    string RunId, string ActivityId, string AttemptId, string State,
    string AdapterOrigin, bool RejectBlocked, AgentSession Session);

public sealed record AgentAdapterResponse(int StatusCode, string Body);

public sealed record AgentSourceEvent(int Sequence, string Type, JsonElement Data);
public sealed record AgentSessionRead(string ContractVersion, string OperationKey,
    string SessionId, IReadOnlyList<AgentSourceEvent> Events);

/// <summary>An external harness operation, never a framework model agent.</summary>
public interface IAgentSessionAdapter
{
    Task<AgentAdapterResponse> StartOrReadAsync(string operationKey, string note, CancellationToken token);
}

public sealed class AgentAssignmentConflictException : Exception;
