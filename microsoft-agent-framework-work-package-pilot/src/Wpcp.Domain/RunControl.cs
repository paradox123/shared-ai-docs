using System.Text.Json;
using System.Text.Json.Serialization;

namespace Wpcp.Domain;

public sealed record RunControlState(
    long RunVersion, string TargetAttemptId, string? HeadSha,
    long LeaseEpoch, ActorIdentity? Holder, DateTimeOffset? ClaimedAt, ControlTransferRequest? TransferRequest = null);

public sealed record ControlTransferRequest(string RequestId, ActorIdentity Requester,
    string RequesterLogin, ActorIdentity Holder, long LeaseEpoch, DateTimeOffset RequestedAt,
    string Reason, string State = "pending");

public sealed record ControlMutation(
    [property: JsonRequired] string TargetAttemptId,
    [property: JsonRequired] long ExpectedRunVersion,
    [property: JsonRequired] string? ExpectedHeadSha,
    [property: JsonRequired] long LeaseEpoch, string? OperationId = null, string? ReceiptId = null,
    string? RequestId = null, string? CommandId = null, string? Message = null, string? Reason = null);

public sealed record SessionOpenCommand(string RequestId, string CommandId);

public sealed record ContinuationOperation(
    string CommandId, string RequestId, string Action, string SourceAttemptId,
    string SourceSessionId, string ResultAttemptId, string? ResultSessionId,
    string OperationKey, string State, string? ParentSessionId, string? Origin,
    [property: JsonIgnore] string AdapterOrigin,
    [property: JsonIgnore] string? Message = null,
    [property: JsonIgnore] string? RunId = null,
    string? ResultRequestId = null);

public sealed record ContinuationReceipt(
    ContinuationOperation Operation, JsonElement? AdapterReceipt);

public sealed record ControlDecision(string Code, RepositoryAccess Access, RunControlState? Current,
    ContinuationOperation? Continuation = null, bool Historical = false)
{
    public bool Accepted => Code is "control-lease-claimed" or "control-lease-released" or "observed" or
        "control-lease-forced-taken-over" or "control-lease-transferred" or "control-transfer-requested" or "control-transfer-rejected" or "recovery-requested" or "continuation-requested" or "continuation-applied";
    public bool CanClaim => !Historical && Access.IsHuman && Access.CanContribute && Current is { Holder: null };
    public bool CanRequestTransfer => !Historical && Access.IsHuman && Access.CanContribute && Current?.Holder is not null &&
        Current.Holder != Access.Actor && Current.TransferRequest?.State != "pending";
    public bool CanForceTakeover => !Historical && Access.IsHuman && Access.CanContribute && Current?.Holder is not null &&
        Current.Holder != Access.Actor;
    public bool CanDecideTransfer => CanRelease && Current?.TransferRequest?.State == "pending";
    public bool CanRelease => !Historical && Access.IsHuman && Access.CanContribute && Current?.Holder == Access.Actor;
}

public sealed record SecurityAuditEntry(
    long Position, DateTimeOffset OccurredAt, string Action, string Code, ActorIdentity? Actor);
