using System.Text.Json;
using System.Text.RegularExpressions;

namespace Wpcp.Domain;

/// <summary>Deployment repository bindings and redaction policy; never an issue catalogue or member list.</summary>
public sealed record SubmissionConfiguration(
    IReadOnlyList<RepositoryBinding> Repositories, ControlledRedactionPolicy RedactionPolicy)
{
    public static SubmissionConfiguration Load(string path)
    {
        using var document = JsonDocument.Parse(File.ReadAllText(path));
        var root = document.RootElement;
        var repositories = root.GetProperty("provider").GetProperty("repositories").EnumerateArray()
            .Select(r => new RepositoryBinding(r.GetProperty("repositoryId").GetString()!,
                r.GetProperty("fullName").GetString()!, r.GetProperty("providerRepositoryId").GetInt64())).ToArray();
        if (repositories.Length == 0 || repositories.Any(r => string.IsNullOrWhiteSpace(r.RepositoryId) ||
            r.ProviderRepositoryId <= 0 || r.FullName is null ||
            !Regex.IsMatch(r.FullName, @"\A[A-Za-z0-9-]+/[A-Za-z0-9_.-]+\z")) ||
            repositories.Select(r => r.RepositoryId).Distinct().Count() != repositories.Length ||
            repositories.Select(r => r.ProviderRepositoryId).Distinct().Count() != repositories.Length ||
            repositories.Select(r => r.FullName).Distinct(StringComparer.OrdinalIgnoreCase).Count() != repositories.Length)
            throw new ArgumentException("Repository bindings must be valid and unique.");
        var redaction = root.GetProperty("redactionPolicy");
        var policy = new ControlledRedactionPolicy(redaction.GetProperty("version").GetString()!,
            redaction.GetProperty("marker").GetString()!, redaction.GetProperty("controlledCanaries").EnumerateArray()
                .Select(c => c.GetProperty("value").GetString()!));
        if (policy.ContainsControlledCanary(JsonSerializer.Serialize(repositories)))
            throw new ArgumentException("Repository bindings contain redacted values.");
        return new(repositories, policy);
    }
}
