namespace Wpcp.Domain;

public sealed record RepositoryPlan(RepositoryBinding Repository, string LocalPath,
    string RemoteName, string BaseBranch, string ProviderOrigin, string AgentOrigin,
    string ExpectedBaseSha, int? PredecessorIssueNumber = null);

public sealed record RepositoryBaseEvidence(string ExpectedSha, string? ProviderSha,
    string? LocalSha, bool PredecessorCompleted);

public sealed record RepositoryExecution(RepositoryPlan Plan, string State = "preflight",
    string? Blocker = null, RepositoryBaseEvidence? Base = null,
    IReadOnlyList<RepositoryEffect>? Effects = null, bool Terminal = false,
    bool Active = false, string? OwnerRunId = null,
    string? RequestedAction = null, string? SelectedOperationId = null, string? SelectedReceiptId = null, RepositoryHumanDecision? HumanDecision = null);

public sealed record ProviderBaseRead(string ContractVersion, RepositoryBinding Repository,
    string HeadSha, IReadOnlyList<int> CompletedIssues);

public sealed record EffectReceipt(string ContractVersion, string OperationId, string ReceiptId,
    string Kind, RepositoryBinding Repository, string HeadSha, string Target);

public sealed record RepositoryEffect(string OperationId, string Kind, string HeadSha, string Target,
    string State = "pending", EffectReceipt? Receipt = null);

public sealed class RepositoryExecutionRequiredException : Exception;

public sealed record RepositoryHumanDecision(string? OperationId, string Code, string? ExpectedHeadSha,
    string? ObservedHeadSha = null, IReadOnlyList<EffectReceipt>? Candidates = null);

public sealed class RepositoryRegistrationBusyException : Exception;
