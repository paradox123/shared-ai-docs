namespace Wpcp.Domain;

/// <summary>
/// Literal, deterministic redaction for the pilot's configured controlled canaries.
/// It intentionally exposes policy metadata but never exposes the configured values.
/// </summary>
public sealed class ControlledRedactionPolicy
{
    private readonly string[] _canaries;

    public ControlledRedactionPolicy(string version, string marker, IEnumerable<string> controlledCanaries)
    {
        RunProvenance.Require(version, nameof(version));
        RunProvenance.Require(marker, nameof(marker));
        ArgumentNullException.ThrowIfNull(controlledCanaries);

        Version = version;
        Marker = marker;
        _canaries = controlledCanaries
            .Where(canary => !string.IsNullOrEmpty(canary))
            .Distinct(StringComparer.Ordinal)
            .OrderByDescending(canary => canary.Length)
            .ToArray();

        if (_canaries.Length == 0)
        {
            throw new ArgumentException("At least one controlled canary is required.", nameof(controlledCanaries));
        }
    }

    public string Version { get; }

    public string Marker { get; }

    /// <summary>
    /// Returns whether an identifier contains a controlled canary. Identifiers are
    /// rejected rather than rewritten because they participate in stable command,
    /// repository, issue, and authorization correlation.
    /// </summary>
    public bool ContainsControlledCanary(string? value) =>
        value is not null && _canaries.Any(canary => value.Contains(canary, StringComparison.Ordinal));

    public bool ContainsControlledCanaryBytes(ReadOnlySpan<byte> value)
    {
        foreach (var canary in _canaries)
            foreach (var encoding in new[] { System.Text.Encoding.UTF8, System.Text.Encoding.Unicode,
                System.Text.Encoding.BigEndianUnicode })
                if (value.IndexOf(encoding.GetBytes(canary)) >= 0) return true;
        return false;
    }

    public RedactedText Redact(string? value)
    {
        if (value is null)
        {
            return new RedactedText(null, false);
        }

        var redacted = value;
        var occurred = false;
        foreach (var canary in _canaries)
        {
            if (!redacted.Contains(canary, StringComparison.Ordinal))
            {
                continue;
            }

            redacted = redacted.Replace(canary, Marker, StringComparison.Ordinal);
            occurred = true;
        }

        return new RedactedText(redacted, occurred);
    }

    public RedactionMetadata Metadata(bool occurred) => new(occurred, Version, Marker);
}

/// <summary>A textual value after a controlled redaction pass.</summary>
public sealed record RedactedText(string? Value, bool Occurred);
