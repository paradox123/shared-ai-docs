namespace Wpcp.Domain;

/// <summary>Immutable identity asserted by an external authority, never a client label.</summary>
public sealed record ActorIdentity(string Kind, string Provider, string SubjectId);

public sealed record RepositoryAccess(
    ActorIdentity? Actor, bool CanRead, bool CanContribute, string? FailureCode = null)
{
    public bool IsHuman => Actor?.Kind == "human";
}

public sealed record RepositoryBinding(string RepositoryId, string FullName, long ProviderRepositoryId);

/// <summary>Fresh provider evaluation; credentials are request-scoped and never persisted.</summary>
public interface IRepositoryAuthorization
{
    Task<RepositoryAccess> EvaluateAsync(
        RepositoryBinding binding, string? credential, CancellationToken cancellationToken = default);
}

/// <summary>A conflicting admission cannot disclose a run from another repository.</summary>
public sealed class RepositoryBindingConflictException : Exception;
