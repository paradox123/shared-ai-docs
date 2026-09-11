using System.Text.Json;

namespace Wpcp.Domain;

/// <summary>
/// Controlled issue catalogue and provider repository bindings for the isolated pilot.
/// It contains no membership list; controlled canaries stay inside the redactor.
/// </summary>
public sealed class SyntheticProviderFixture
{
    private readonly IReadOnlyList<SyntheticRepository> _repositories;
    private readonly IReadOnlyList<RepositoryBinding> _bindings;

    private SyntheticProviderFixture(
        string fixtureVersion,
        IReadOnlyList<SyntheticRepository> repositories,
        IReadOnlyList<RepositoryBinding> bindings,
        ControlledRedactionPolicy redactionPolicy)
    {
        FixtureVersion = fixtureVersion;
        _repositories = repositories;
        _bindings = bindings;
        RedactionPolicy = redactionPolicy;
    }

    public string FixtureVersion { get; }

    public ControlledRedactionPolicy RedactionPolicy { get; }

    public static SyntheticProviderFixture Load(string fixturePath)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(fixturePath);

        var json = File.ReadAllText(fixturePath);
        var document = JsonSerializer.Deserialize<FixtureDocument>(json, SerializerOptions)
            ?? throw new InvalidOperationException("The synthetic provider fixture was empty.");

        var fixtureVersion = Required(document.FixtureVersion, "fixtureVersion");
        ArgumentNullException.ThrowIfNull(document.Provider);
        ArgumentNullException.ThrowIfNull(document.RedactionPolicy);

        var repositories = document.Provider.Repositories?
            .Select(repository => new SyntheticRepository(
                Required(repository.RepositoryId, "repositoryId"),
                (repository.Issues ?? [])
                    .Select(issue => new SyntheticIssue(
                        Required(issue.IssueId, "issueId"),
                        Required(repository.RepositoryId, "repositoryId"),
                        Positive(issue.IssueNumber, "issueNumber"),
                        Required(issue.Title, "title")))
                    .ToArray()))
            .ToArray()
            ?? [];

        var bindings = (document.Provider.Repositories ?? []).Select(repository =>
            new RepositoryBinding(Required(repository.RepositoryId, "repositoryId"),
                Required(repository.FullName, "fullName"), repository.ProviderRepositoryId)).ToArray();
        if (bindings.Any(binding => binding.ProviderRepositoryId <= 0 ||
            binding.FullName.Split('/').Length != 2 || binding.FullName.Split('/').Any(string.IsNullOrWhiteSpace)))
            throw new ArgumentException("Invalid repository provider binding.");

        var policy = new ControlledRedactionPolicy(
            Required(document.RedactionPolicy.Version, "redactionPolicy.version"),
            Required(document.RedactionPolicy.Marker, "redactionPolicy.marker"),
            (document.RedactionPolicy.ControlledCanaries ?? [])
                .Select(canary => Required(canary.Value, "redactionPolicy.controlledCanaries.value"))
                .ToArray());

        return new SyntheticProviderFixture(fixtureVersion, repositories, bindings, policy);
    }

    public SyntheticIssue? FindIssue(string repositoryId, int issueNumber) =>
        _repositories
            .FirstOrDefault(repository => string.Equals(repository.RepositoryId, repositoryId, StringComparison.Ordinal))
            ?.Issues.FirstOrDefault(issue => issue.IssueNumber == issueNumber);

    public RepositoryBinding? FindRepositoryBinding(string repositoryId) =>
        _bindings.FirstOrDefault(binding => binding.RepositoryId == repositoryId);

    private static string Required(string? value, string name)
    {
        RunProvenance.Require(value, name);
        return value!;
    }

    private static int Positive(int value, string name)
    {
        if (value <= 0)
        {
            throw new InvalidOperationException("A required fixture number was not positive: " + name + ".");
        }

        return value;
    }

    private static readonly JsonSerializerOptions SerializerOptions = new()
    {
        PropertyNameCaseInsensitive = true,
    };

    private sealed class FixtureDocument
    {
        public string? FixtureVersion { get; init; }

        public ProviderDocument? Provider { get; init; }

        public RedactionPolicyDocument? RedactionPolicy { get; init; }
    }

    private sealed class ProviderDocument
    {
        public List<RepositoryDocument>? Repositories { get; init; }


    }

    private sealed class RepositoryDocument
    {
        public string? RepositoryId { get; init; }
        public string? FullName { get; init; }
        public long ProviderRepositoryId { get; init; }

        public List<IssueDocument>? Issues { get; init; }
    }

    private sealed class IssueDocument
    {
        public string? IssueId { get; init; }

        public int IssueNumber { get; init; }

        public string? Title { get; init; }
    }

    private sealed class RedactionPolicyDocument
    {
        public string? Version { get; init; }

        public string? Marker { get; init; }

        public List<CanaryDocument>? ControlledCanaries { get; init; }
    }

    private sealed class CanaryDocument
    {
        public string? Value { get; init; }
    }
}

/// <summary>One deterministic repository issue from the controlled fixture.</summary>
public sealed record SyntheticIssue(string IssueId, string RepositoryId, int IssueNumber, string Title);

internal sealed record SyntheticRepository(string RepositoryId, IReadOnlyList<SyntheticIssue> Issues);
