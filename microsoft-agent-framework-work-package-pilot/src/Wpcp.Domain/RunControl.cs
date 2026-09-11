using System.Text.Json.Serialization;

namespace Wpcp.Domain;

public sealed record RunControlState(
    long RunVersion, string TargetAttemptId, string? HeadSha,
    long LeaseEpoch, ActorIdentity? Holder, DateTimeOffset? ClaimedAt);

public sealed record ControlMutation(
    [property: JsonRequired] string TargetAttemptId,
    [property: JsonRequired] long ExpectedRunVersion,
    [property: JsonRequired] string? ExpectedHeadSha,
    [property: JsonRequired] long LeaseEpoch);

public sealed record ControlDecision(string Code, RepositoryAccess Access, RunControlState? Current)
{
    public bool Accepted => Code is "control-lease-claimed" or "control-lease-released" or "observed";
    public bool CanClaim => Access.IsHuman && Access.CanContribute && Current is { Holder: null };
    public bool CanRelease => Access.IsHuman && Access.CanContribute && Current?.Holder == Access.Actor;
}

public sealed record SecurityAuditEntry(
    long Position, DateTimeOffset OccurredAt, string Action, string Code, ActorIdentity? Actor);
