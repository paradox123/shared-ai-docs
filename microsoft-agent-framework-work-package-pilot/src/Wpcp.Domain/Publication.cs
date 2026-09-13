using System.Text.Json;

namespace Wpcp.Domain;

public sealed record Publication(string AssignmentHash, string State,
    string? Blocker = null, JsonElement? Report = null, JsonElement? Intent = null,
    bool Dispatched = false, JsonElement? Qualification = null,
    string? CaptureHeadSha = null, EvidenceCapture? Capture = null);

public sealed record EvidenceCapture(int Number, string Kind, string State,
    string ActivityId, string AttemptId, JsonElement? Report = null)
{
    public const int MaximumRounds = 2;
}
