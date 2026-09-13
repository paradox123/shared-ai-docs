using System.Text.Json;

namespace Wpcp.Domain;

public sealed record Publication(string AssignmentHash, string State,
    string? Blocker = null, JsonElement? Report = null, JsonElement? Intent = null,
    bool Dispatched = false, JsonElement? Qualification = null,
    string? CaptureHeadSha = null, EvidenceCapture? Capture = null,
    HeadQualification? HeadQualification = null);

public sealed record HeadQualification(string HeadSha, string State, IReadOnlyList<QualificationRound> Rounds,
    string? QualifiedHeadSha = null, string? Blocker = null, HumanRequest? HumanRequest = null,
    IReadOnlyList<QualificationRepair>? Repairs = null);

public sealed record QualificationRepair(int Number, string OperationKey, string SourceHeadSha,
    JsonElement Assignment, string State = "dispatching", JsonElement? Report = null,
    string? HeadSha = null, JsonElement? Evidence = null, JsonElement? PublicationReport = null,
    JsonElement? LastObservation = null)
{
    public const int MaximumRounds = 3;
}

public sealed record QualificationRound(int Number, string HeadSha, JsonElement Evidence,
    string State = "pending", JsonElement? Verification = null, IReadOnlyList<HeadReview>? Reviews = null);

public sealed record HeadReview(string Axis, string OperationKey, JsonElement? Report = null);

public sealed record EvidenceCapture(int Number, string Kind, string State,
    string ActivityId, string AttemptId, JsonElement? Report = null)
{
    public const int MaximumRounds = 2;
}
