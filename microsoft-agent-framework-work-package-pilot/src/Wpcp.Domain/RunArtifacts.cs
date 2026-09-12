namespace Wpcp.Domain;

public sealed record RunArtifact(string ArtifactId, string? Sha256, long SizeBytes,
    string MediaType, string Availability, string? Reason, RedactionMetadata Redaction);

public sealed record ArtifactManifest(string RunId, IReadOnlyList<RunArtifact> Artifacts)
{
    public bool QualificationEligible => Artifacts.All(a => a.Availability == "available");
}
