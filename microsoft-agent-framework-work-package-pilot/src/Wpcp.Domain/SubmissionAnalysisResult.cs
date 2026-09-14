using System.Text.Json;

namespace Wpcp.Domain;

/// <summary>Completion of requirements analysis never claims completed implementation.</summary>
public static class SubmissionAnalysisResult
{
    public static bool IsValid(JsonElement value) => value.ValueKind == JsonValueKind.Object &&
        value.EnumerateObject().Count() == 4 &&
        value.TryGetProperty("schemaVersion", out var schema) && schema.ValueKind == JsonValueKind.String &&
        schema.GetString() == SubmissionExecutionConfiguration.Step &&
        value.TryGetProperty("outcome", out var outcome) && outcome.ValueKind == JsonValueKind.String &&
        outcome.GetString() is "completed" or "failed" &&
        value.TryGetProperty("summary", out var summary) && summary.ValueKind == JsonValueKind.String &&
        !string.IsNullOrWhiteSpace(summary.GetString()) &&
        value.TryGetProperty("findings", out var findings) && findings.ValueKind == JsonValueKind.Array &&
        findings.EnumerateArray().All(f => f.ValueKind == JsonValueKind.String && !string.IsNullOrWhiteSpace(f.GetString()));
}
