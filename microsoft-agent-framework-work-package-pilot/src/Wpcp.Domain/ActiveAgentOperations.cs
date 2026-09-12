using System.Text.Json;
using System.Text.Json.Serialization;

namespace Wpcp.Domain;

public sealed record ActiveAgentCommandRequest(
    [property: JsonRequired] string? TargetAttemptId,
    [property: JsonRequired] long ExpectedRunVersion,
    [property: JsonRequired] string? ExpectedHeadSha,
    [property: JsonRequired] long LeaseEpoch,
    [property: JsonRequired] string CommandId,
    string? Message = null, string? Reason = null, string? Scope = null);

public sealed record ActiveAgentCommand(
    string CommandId, string AttemptId, string Mode, long AcceptancePosition,
    string? Message, string? Reason, string? Scope, string State = "queued",
    string? OperationKey = null, string? RejectionReason = null, int? QueuePosition = null);

public sealed record ActiveAgentOperation(
    string OperationKey, long FenceEpoch, string? CommandId, string Message,
    string ProcessStatus = "start-pending", string? ProcessId = null,
    bool StopRequested = false, JsonElement? Response = null);

public sealed record ActiveAgentAttempt(
    string AttemptId, string ActivityId, string SessionId, string State,
    long FenceEpoch, ActiveAgentOperation? CurrentOperation,
    IReadOnlyList<ActiveAgentCommand> Commands);

public sealed record ActiveAgentDecision(
    string Code, RunControlState? Current, ActiveAgentCommand? Command = null);

public sealed record ActiveAgentDelivery(string RunId, string AdapterOrigin, ActiveAgentAttempt Attempt);
