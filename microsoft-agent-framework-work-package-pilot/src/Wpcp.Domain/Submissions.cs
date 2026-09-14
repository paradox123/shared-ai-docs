namespace Wpcp.Domain;

public sealed record SubmissionSource(
    string Provider, long ProviderIssueId, int IssueNumber, string Url, DateTimeOffset UpdatedAt);

/// <summary>The admitted snapshot; execution is a separate lifecycle decision.</summary>
public sealed record Submission(
    string SubmissionId, string State, string? RunId, string Title, string Body,
    SubmissionSource Source, RepositoryBinding Repository, ActorIdentity SubmittedBy,
    DateTimeOffset AdmittedAt, string ContentSha256, RedactionMetadata Redaction);

public sealed record SubmitGitHubIssueRequest(string? SourceUrl);

public sealed record SubmissionAdmission(Submission Submission, bool Created);
