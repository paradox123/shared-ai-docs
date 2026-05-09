using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;
using System.Text.RegularExpressions;

#pragma warning disable IL2026, IL3050

var options = Options.Parse(args);
if (options.ShowHelp || !options.IsValid)
{
    Options.PrintUsage(options.ParseError ? Console.Error : Console.Out);
    return options.ShowHelp ? 0 : 2;
}

var result = Validator.Validate(options);
Print(result, options.Format);
return result.HasFatalInputError ? 2 : result.Valid ? 0 : 1;

static void Print(ValidationResult result, string format)
{
    if (format is "json" or "both")
    {
        Console.WriteLine(JsonSerializer.Serialize(result, JsonSupport.Options));
    }

    if (format is "both")
    {
        Console.WriteLine();
    }

    if (format is "markdown" or "both")
    {
        Console.WriteLine(MarkdownSummary.Render(result));
    }
}

static class Validator
{
    public static ValidationResult Validate(Options options)
    {
        var findings = new List<Finding>();
        var packPath = Path.GetFullPath(options.PackPath!);
        var repoPath = Path.GetFullPath(options.RepoPath ?? Directory.GetCurrentDirectory());

        if (!File.Exists(packPath))
        {
            findings.Add(Error("pack-not-found", null, $"Pack not found: {packPath}"));
            return Build(packPath, repoPath, 0, findings, fatal: true);
        }

        if (!Directory.Exists(repoPath))
        {
            findings.Add(Error("repo-not-found", null, $"Repository path not found: {repoPath}"));
            return Build(packPath, repoPath, 0, findings, fatal: true);
        }

        var markdown = File.ReadAllText(packPath);
        var packDir = Path.GetDirectoryName(packPath)!;
        var childIndex = MarkdownTable.FindChildIndex(markdown, options.ChildIndexSection!);
        if (childIndex.Status == TableFindStatus.CompressedAlias)
        {
            findings.Add(Error("compressed-child-index", null, "Child Index uses compressed/aliased substitute columns: " + string.Join(", ", childIndex.AliasHeaders)));
            return Build(packPath, repoPath, 0, findings, fatal: false);
        }

        if (childIndex.Table is null)
        {
            findings.Add(Error("missing-child-index", null, "Child Index table with exact operational columns was not found."));
            return Build(packPath, repoPath, 0, findings, fatal: true);
        }

        ValidateHeaders(childIndex.Table, options, findings);
        var rows = childIndex.Table.Rows.Select((row, index) => ChildRow.From(row, index)).ToList();
        foreach (var row in rows)
        {
            ValidateRow(row, packDir, repoPath, findings);
        }

        ValidateHardeningQueue(markdown, options, rows, findings);
        ValidateFalseAdvancement(markdown, rows, packDir, repoPath, findings);

        return Build(packPath, repoPath, rows.Count, findings, fatal: false);
    }

    static ValidationResult Build(string packPath, string repoPath, int childCount, List<Finding> findings, bool fatal)
    {
        var errors = findings.Count(f => f.Severity == "error");
        var warnings = findings.Count(f => f.Severity == "warning");
        return new ValidationResult
        {
            PackPath = packPath,
            RepoPath = repoPath,
            Valid = errors == 0 && !fatal,
            HasFatalInputError = fatal,
            ChildCount = childCount,
            FindingCounts = new FindingCounts(errors, warnings),
            Findings = findings
        };
    }

    static void ValidateHeaders(MarkdownTable table, Options options, List<Finding> findings)
    {
        var extraColumns = table.Headers.Where(h => !MarkdownTable.RequiredHeaders.Contains(h)).ToArray();
        if (extraColumns.Length > 0 && !options.AllowExtraColumns)
        {
            findings.Add(Error("extra-child-index-columns", null, "Child Index has extra columns: " + string.Join(", ", extraColumns)));
        }

        var aliasHeaders = table.Headers.Where(MarkdownTable.AliasHeaders.Contains).ToArray();
        if (aliasHeaders.Length > 0)
        {
            findings.Add(Error("compressed-child-index", null, "Child Index uses compressed/aliased substitute columns: " + string.Join(", ", aliasHeaders)));
        }
    }

    static void ValidateRow(ChildRow row, string packDir, string repoPath, List<Finding> findings)
    {
        foreach (var header in MarkdownTable.RequiredHeaders)
        {
            var value = Normalize(row.Cells[header]);
            if (LooksLikePlaceholder(value))
            {
                findings.Add(Error("empty-required-cell", row.ChildOrUnknown, $"Required Child Index cell `{header}` is empty or placeholder."));
            }
        }

        if (!IsStableChildId(row.Child))
        {
            findings.Add(Error("empty-required-cell", row.ChildOrUnknown, $"Child id is not a stable exact id: `{row.Child}`."));
        }

        var childSpec = ExtractPath(row.ChildSpec);
        if (string.IsNullOrWhiteSpace(childSpec))
        {
            findings.Add(Error("missing-child-spec", row.ChildOrUnknown, "Child Spec cell does not contain a usable path."));
        }
        else if (!ResolveExisting(childSpec, packDir, repoPath, out var childSpecPath))
        {
            findings.Add(Error("missing-child-spec", row.ChildOrUnknown, $"Child Spec file not found: {childSpecPath}"));
        }

        var handoff = ExtractPath(row.SessionHandoff);
        if (string.IsNullOrWhiteSpace(handoff))
        {
            findings.Add(Error("missing-handoff", row.ChildOrUnknown, "Session Handoff cell does not contain a usable path."));
        }
        else if (!ResolveExisting(handoff, packDir, repoPath, out var handoffPath))
        {
            findings.Add(Error("missing-handoff", row.ChildOrUnknown, $"Session Handoff file not found: {handoffPath}"));
        }
        else
        {
            ValidateHandoff(row, handoffPath, findings);
        }

        ValidateStatusNextAction(row, findings);
    }

    static void ValidateHandoff(ChildRow row, string handoffPath, List<Finding> findings)
    {
        var text = File.ReadAllText(handoffPath);
        var targetId = ExtractBulletValue(text, "Target ID")
            ?? ExtractBulletValue(text, "Stable Child ID")
            ?? ExtractBulletValue(text, "Child");

        if (targetId is not null && !ContainsExactToken(targetId, row.Child))
        {
            findings.Add(Error("handoff-child-mismatch", row.ChildOrUnknown, $"Handoff child id mismatch. Index child `{row.Child}`, handoff declares `{targetId}`."));
            return;
        }

        if (targetId is null && !ContainsExactToken(text, row.Child))
        {
            findings.Add(Error("handoff-child-mismatch", row.ChildOrUnknown, $"Handoff file does not mention child id `{row.Child}`."));
        }
    }

    static void ValidateStatusNextAction(ChildRow row, List<Finding> findings)
    {
        var verdict = Normalize(row.Verdict);
        var next = Normalize(row.NextAction);

        if (IsImplementationReady(verdict))
        {
            if (!ContainsAny(next, "spec-change-delivery", "implementation may start", "may start", "implement"))
            {
                findings.Add(Error("status-next-action-mismatch", row.ChildOrUnknown, "Implementation-ready child does not route to `spec-change-delivery` or implementation start."));
            }
            return;
        }

        if (verdict.Contains("NEEDS HARDENING", StringComparison.OrdinalIgnoreCase))
        {
            if (next.Contains("spec-change-delivery", StringComparison.OrdinalIgnoreCase) && !ContainsAny(next, "after hardening", "after child-spec-hardening"))
            {
                findings.Add(Error("status-next-action-mismatch", row.ChildOrUnknown, "`NEEDS HARDENING` child routes directly to `spec-change-delivery`."));
            }
            else if (!ContainsAny(next, "child-spec-hardening", "harden", "hardening"))
            {
                findings.Add(Error("status-next-action-mismatch", row.ChildOrUnknown, "`NEEDS HARDENING` child next action does not keep hardening visible."));
            }
            return;
        }

        if (verdict.Contains("DEFERRED", StringComparison.OrdinalIgnoreCase))
        {
            if (!ContainsAny(next, "do not start", "future", "deferred", "follow-up", "later"))
            {
                findings.Add(Error("status-next-action-mismatch", row.ChildOrUnknown, "Deferred child next action does not keep deferral visible."));
            }
            return;
        }

        if (ContainsAny(verdict, "BLOCK", "NEEDS USER DECISION"))
        {
            if (ContainsAny(next, "spec-change-delivery", "implementation may start", "may start"))
            {
                findings.Add(Error("status-next-action-mismatch", row.ChildOrUnknown, "Blocked or decision-needed child claims implementation can start."));
            }
        }
    }

    static void ValidateHardeningQueue(string markdown, Options options, List<ChildRow> rows, List<Finding> findings)
    {
        var queue = MarkdownTable.FindAnyTableInSection(markdown, options.HardeningQueueSection!);
        if (queue is null)
        {
            return;
        }

        if (!queue.Headers.Contains("Child", StringComparer.Ordinal))
        {
            findings.Add(Error("queue-missing-child", null, "Hardening Queue table is missing required `Child` column."));
            return;
        }

        var orderColumn = queue.Headers.FirstOrDefault(h => h.Equals("Order", StringComparison.OrdinalIgnoreCase))
            ?? queue.Headers.FirstOrDefault(h => h.Contains("Status", StringComparison.OrdinalIgnoreCase));
        if (orderColumn is null)
        {
            findings.Add(Error("queue-missing-child", null, "Hardening Queue table needs an `Order` or status column."));
            return;
        }

        var rowByChild = rows.ToDictionary(r => r.Child, StringComparer.OrdinalIgnoreCase);
        var queueChildren = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        foreach (var queueRow in queue.Rows)
        {
            var child = Normalize(queueRow["Child"]).Trim('`');
            if (string.IsNullOrWhiteSpace(child))
            {
                findings.Add(Error("queue-missing-child", null, "Hardening Queue contains an empty Child cell."));
                continue;
            }

            queueChildren.Add(child);
            if (!rowByChild.TryGetValue(child, out var childRow))
            {
                findings.Add(Error("queue-child-missing-from-index", child, $"Hardening Queue child `{child}` is not present in the Child Index."));
                continue;
            }

            ValidateQueueStatus(queueRow[orderColumn], childRow, findings);
        }

        foreach (var row in rows.Where(r => r.Verdict.Contains("NEEDS HARDENING", StringComparison.OrdinalIgnoreCase)))
        {
            if (!queueChildren.Contains(row.Child) && !row.Verdict.Contains("DEFERRED", StringComparison.OrdinalIgnoreCase))
            {
                findings.Add(Error("queue-missing-child", row.ChildOrUnknown, "`NEEDS HARDENING` child is missing from Hardening Queue."));
            }
        }

        var queueText = string.Join(" ", queue.Rows.SelectMany(row => row.Values));
        if (Regex.IsMatch(queueText, @"(?i)\ball\s+children\s+(are\s+)?ready\b") &&
            rows.Any(row => !IsImplementationReady(row.Verdict)))
        {
            findings.Add(Error("queue-status-mismatch", null, "Hardening Queue claims all children are ready while Child Index still has non-ready rows."));
        }
    }

    static void ValidateQueueStatus(string queueStatus, ChildRow childRow, List<Finding> findings)
    {
        var status = Normalize(queueStatus).Trim('`');
        var verdict = Normalize(childRow.Verdict);
        var next = Normalize(childRow.NextAction);

        if (status.Equals("complete", StringComparison.OrdinalIgnoreCase))
        {
            if (!IsImplementationReady(verdict))
            {
                findings.Add(Error("queue-status-mismatch", childRow.ChildOrUnknown, "Hardening Queue marks child complete, but Child Index is not implementation-ready."));
            }
            return;
        }

        if (Regex.IsMatch(status, @"^\d+$"))
        {
            if (!verdict.Contains("NEEDS HARDENING", StringComparison.OrdinalIgnoreCase))
            {
                findings.Add(Error("queue-status-mismatch", childRow.ChildOrUnknown, "Hardening Queue has numeric order, but Child Index verdict is not `NEEDS HARDENING`."));
            }
            return;
        }

        if (status.Contains("deferred", StringComparison.OrdinalIgnoreCase))
        {
            if (!ContainsAny(verdict + " " + next, "DEFERRED", "do not start", "future", "follow-up"))
            {
                findings.Add(Error("queue-status-mismatch", childRow.ChildOrUnknown, "Hardening Queue marks child deferred, but Child Index does not."));
            }
        }
    }

    static void ValidateFalseAdvancement(string markdown, List<ChildRow> rows, string packDir, string repoPath, List<Finding> findings)
    {
        var hasExistingEvidence = ExistingEvidencePaths(markdown, packDir, repoPath).Any();
        var hasReadyRow = rows.Any(row => IsImplementationReady(row.Verdict));

        var claimPatterns = new (string Code, Regex Pattern, Func<bool> HasEvidence)[]
        {
            ("workflow advanced", new Regex(@"(?i)\bworkflow\s+advanced\b|\badvanced\s+to\b|\bmoved\s+to\s+hardening\b"), () => hasExistingEvidence),
            ("hardening started", new Regex(@"(?i)\bhardening\s+started\b"), () => hasExistingEvidence),
            ("hardening completed", new Regex(@"(?i)\bhardening\s+completed\b"), () => hasExistingEvidence || hasReadyRow),
            ("agent queued/launched", new Regex(@"(?i)\bagent\s+(queued|launched)\b|\blaunch\s+evidence\s+exists\b"), () => hasExistingEvidence),
            ("delivery/implementation", new Regex(@"(?i)\bdelivery\s+started\b|\bimplementation\s+(started|complete)\b"), () => hasExistingEvidence),
            ("closeout accepted", new Regex(@"(?i)\bcloseout\s+accepted\b|\baccepted\s+and\s+closed\b"), () => hasExistingEvidence)
        };

        foreach (var (label, pattern, hasEvidence) in claimPatterns)
        {
            if (pattern.IsMatch(markdown) && !hasEvidence())
            {
                findings.Add(Error("false-advancement-claim", null, $"Pack claims `{label}` without matching evidence."));
            }
        }
    }

    static IEnumerable<string> ExistingEvidencePaths(string markdown, string packDir, string repoPath)
    {
        foreach (Match match in Regex.Matches(markdown, @"(?<path>(?:`|\()?(?:[A-Za-z0-9_./ -]+/)?evidence\.json)(?:`|\))?", RegexOptions.IgnoreCase))
        {
            var raw = match.Groups["path"].Value.Trim('`', '(', ')');
            if (ResolveExisting(raw, packDir, repoPath, out var resolved))
            {
                yield return resolved;
            }
        }
    }

    static bool ResolveExisting(string rawPath, string packDir, string repoPath, out string resolved)
    {
        resolved = ResolveCandidate(rawPath, packDir, repoPath).First();
        foreach (var candidate in ResolveCandidate(rawPath, packDir, repoPath))
        {
            if (File.Exists(candidate))
            {
                resolved = candidate;
                return true;
            }
        }

        return false;
    }

    static IEnumerable<string> ResolveCandidate(string rawPath, string packDir, string repoPath)
    {
        var path = rawPath.Trim().Trim('`').Trim();
        if (Path.IsPathRooted(path))
        {
            yield return Path.GetFullPath(path);
            yield break;
        }

        yield return Path.GetFullPath(Path.Combine(packDir, path));
        yield return Path.GetFullPath(Path.Combine(repoPath, path));
    }

    static string ExtractPath(string value)
    {
        var markdownLink = Regex.Match(value, @"\[[^\]]+\]\(([^)]+)\)");
        if (markdownLink.Success) return markdownLink.Groups[1].Value.Trim();

        var codePath = Regex.Match(value, @"`([^`]+)`");
        if (codePath.Success) return codePath.Groups[1].Value.Trim();

        var plainPath = Regex.Match(value, @"(?<path>\S+\.(?:md|json))", RegexOptions.IgnoreCase);
        return plainPath.Success ? plainPath.Groups["path"].Value.TrimEnd('.', ',', ';') : value.Trim();
    }

    static string? ExtractBulletValue(string text, string label)
    {
        var pattern = @"^\s*[-*]\s*" + Regex.Escape(label) + @"\s*:\s*(.+?)\s*$";
        var match = Regex.Match(text, pattern, RegexOptions.Multiline | RegexOptions.IgnoreCase);
        return match.Success ? Normalize(match.Groups[1].Value) : null;
    }

    static bool ContainsExactToken(string text, string token)
    {
        if (string.IsNullOrWhiteSpace(token)) return false;
        return Regex.IsMatch(text, @"(?<![A-Za-z0-9_-])" + Regex.Escape(token) + @"(?![A-Za-z0-9_-])", RegexOptions.IgnoreCase);
    }

    static bool IsStableChildId(string value)
    {
        var normalized = Normalize(value).Trim('`');
        if (LooksLikePlaceholder(normalized)) return false;
        if (normalized.Contains(' ') && Regex.IsMatch(normalized, @"^[A-Z0-9-]+\s+\w+", RegexOptions.IgnoreCase)) return false;
        return Regex.IsMatch(normalized, @"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+$|^[A-Z]+\d+$|^[A-Z]+-[A-Z0-9]+-\d+$|^S\d+$", RegexOptions.IgnoreCase);
    }

    static bool IsImplementationReady(string value) =>
        ContainsAny(value, "IMPLEMENTATION READY", "READY WITH NON-BLOCKING NOTES");

    static bool ContainsAny(string value, params string[] terms) =>
        terms.Any(term => value.Contains(term, StringComparison.OrdinalIgnoreCase));

    static bool LooksLikePlaceholder(string value)
    {
        var normalized = Normalize(value).Trim('`').Trim();
        if (string.IsNullOrWhiteSpace(normalized)) return true;

        var placeholders = new[]
        {
            "tbd", "todo", "unknown", "n/a", "na", "none", "not hardened", "not evaluated",
            "pending", "blocked until own hardening", "to decide", "to be decided", "?", "-"
        };

        return placeholders.Any(p => normalized.Equals(p, StringComparison.OrdinalIgnoreCase));
    }

    static string Normalize(string value) =>
        Regex.Replace(value.Replace("<br>", " ", StringComparison.OrdinalIgnoreCase)
                .Replace("<br/>", " ", StringComparison.OrdinalIgnoreCase)
                .Replace("<br />", " ", StringComparison.OrdinalIgnoreCase),
            @"\s+", " ").Trim();

    static Finding Error(string code, string? child, string message) => new()
    {
        Severity = "error",
        Code = code,
        Child = child,
        Message = message
    };
}

sealed class Options
{
    static readonly HashSet<string> Formats = new(StringComparer.Ordinal) { "json", "markdown", "both" };

    public string? PackPath { get; private init; }
    public string? RepoPath { get; private init; }
    public string? ChildIndexSection { get; private init; } = "Child Index";
    public string? HardeningQueueSection { get; private init; } = "Hardening Queue";
    public string Format { get; private init; } = "json";
    public bool AllowExtraColumns { get; private init; }
    public bool ShowHelp { get; private init; }
    public bool ParseError { get; private init; }

    public bool IsValid =>
        !ParseError &&
        !string.IsNullOrWhiteSpace(PackPath) &&
        !string.IsNullOrWhiteSpace(ChildIndexSection) &&
        !string.IsNullOrWhiteSpace(HardeningQueueSection) &&
        Formats.Contains(Format);

    public static Options Parse(string[] args)
    {
        string? pack = null;
        string? repo = null;
        var childIndexSection = "Child Index";
        var hardeningQueueSection = "Hardening Queue";
        var format = "json";
        var allowExtraColumns = false;
        var showHelp = false;
        var parseError = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--help":
                case "-h":
                    showHelp = true;
                    break;
                case "--pack":
                    pack = RequireValue(args, ref i, "--pack", ref parseError);
                    break;
                case "--repo":
                    repo = RequireValue(args, ref i, "--repo", ref parseError);
                    break;
                case "--child-index-section":
                    childIndexSection = RequireValue(args, ref i, "--child-index-section", ref parseError);
                    break;
                case "--hardening-queue-section":
                    hardeningQueueSection = RequireValue(args, ref i, "--hardening-queue-section", ref parseError);
                    break;
                case "--allow-extra-columns":
                    allowExtraColumns = true;
                    break;
                case "--format":
                    format = RequireValue(args, ref i, "--format", ref parseError);
                    break;
                default:
                    Console.Error.WriteLine($"Unknown argument: {args[i]}");
                    parseError = true;
                    break;
            }
        }

        if (!Formats.Contains(format))
        {
            Console.Error.WriteLine($"Unsupported --format: {format}");
            parseError = true;
        }

        return new Options
        {
            PackPath = pack,
            RepoPath = repo,
            ChildIndexSection = childIndexSection,
            HardeningQueueSection = hardeningQueueSection,
            Format = format,
            AllowExtraColumns = allowExtraColumns,
            ShowHelp = showHelp,
            ParseError = parseError
        };
    }

    static string RequireValue(string[] args, ref int index, string option, ref bool parseError)
    {
        if (index + 1 >= args.Length)
        {
            Console.Error.WriteLine($"{option} requires a value.");
            parseError = true;
            return "";
        }

        index++;
        return args[index];
    }

    public static void PrintUsage(TextWriter writer)
    {
        writer.WriteLine("""
        Usage:
          dotnet run <path-to-ValidateOrchestrationPack.cs> -- --pack <orchestration-pack.md> [options]

        Options:
          --pack <path>                         Markdown orchestration pack to validate.
          --repo <path>                         Repository root for resolving repo-relative paths. Defaults to current directory.
          --child-index-section <name>          Section heading to prefer. Default: Child Index.
          --hardening-queue-section <name>      Section heading to prefer. Default: Hardening Queue.
          --allow-extra-columns                 Permit extra Child Index columns. Compressed/aliased substitutes still fail.
          --format <json|markdown|both>         Output format. Default: json.
          --help                                Print this help and exit 0.

        Exit codes:
          0  Validation passed with no error findings.
          1  Validation completed and found one or more error findings.
          2  Invalid arguments, unreadable inputs, or missing required Child Index.
        """);
    }
}

sealed record ChildRow
{
    public required int Index { get; init; }
    public required Dictionary<string, string> Cells { get; init; }
    public string Child => Cells["Child"].Trim('`').Trim();
    public string ChildOrUnknown => string.IsNullOrWhiteSpace(Child) ? $"row-{Index + 1}" : Child;
    public string ChildSpec => Cells["Child Spec"];
    public string Verdict => Cells["Readiness / Hardening Verdict"];
    public string SessionHandoff => Cells["Session Handoff"];
    public string NextAction => Cells["Next Action"];

    public static ChildRow From(Dictionary<string, string> row, int index) => new()
    {
        Index = index,
        Cells = row
    };
}

sealed class ValidationResult
{
    [JsonPropertyName("schema")]
    public string Schema { get; init; } = "agent-delivery.validate-orchestration-pack.v1";

    [JsonPropertyName("pack_path")]
    public required string PackPath { get; init; }

    [JsonPropertyName("repo_path")]
    public required string RepoPath { get; init; }

    [JsonPropertyName("valid")]
    public required bool Valid { get; init; }

    [JsonIgnore]
    public bool HasFatalInputError { get; init; }

    [JsonPropertyName("child_count")]
    public required int ChildCount { get; init; }

    [JsonPropertyName("finding_counts")]
    public required FindingCounts FindingCounts { get; init; }

    [JsonPropertyName("findings")]
    public required List<Finding> Findings { get; init; }
}

sealed record FindingCounts(
    [property: JsonPropertyName("errors")] int Errors,
    [property: JsonPropertyName("warnings")] int Warnings);

sealed class Finding
{
    [JsonPropertyName("severity")]
    public required string Severity { get; init; }

    [JsonPropertyName("code")]
    public required string Code { get; init; }

    [JsonPropertyName("child")]
    public string? Child { get; init; }

    [JsonPropertyName("message")]
    public required string Message { get; init; }
}

enum TableFindStatus
{
    NotFound,
    Found,
    CompressedAlias
}

sealed record ChildIndexFind(TableFindStatus Status, MarkdownTable? Table, string[] AliasHeaders);

sealed class MarkdownTable
{
    public static readonly string[] RequiredHeaders =
    [
        "Child",
        "Child Spec",
        "Parent Coverage",
        "Readiness / Hardening Verdict",
        "Session Handoff",
        "OpenSpec / Ledger",
        "Dependencies",
        "Allowed Write-Set",
        "Verification",
        "Evidence / Closeout",
        "Backlog / Re-entry",
        "Next Action"
    ];

    public static readonly HashSet<string> AliasHeaders = new(StringComparer.OrdinalIgnoreCase)
    {
        "Slice",
        "Spec",
        "Status",
        "Readiness Status",
        "Hardening Verdict",
        "Evidence / OpenSpec",
        "Dependencies / Evidence",
        "Allowed Next Mode",
        "Implementation Gate",
        "Closeout Sync",
        "Shared / Read-only Files",
        "Open Decisions / Blockers",
        "Notes"
    };

    public required string[] Headers { get; init; }
    public required List<Dictionary<string, string>> Rows { get; init; }

    public static ChildIndexFind FindChildIndex(string markdown, string section)
    {
        var scoped = ExtractSection(markdown, section) ?? markdown;
        return FindChildIndexInText(scoped) is { Status: not TableFindStatus.NotFound } scopedResult
            ? scopedResult
            : ReferenceEquals(scoped, markdown)
                ? new ChildIndexFind(TableFindStatus.NotFound, null, [])
                : FindChildIndexInText(markdown);
    }

    public static MarkdownTable? FindAnyTableInSection(string markdown, string section)
    {
        var scoped = ExtractSection(markdown, section);
        return scoped is null ? null : FindFirstTable(scoped, requireChildIndex: false)?.Table;
    }

    static ChildIndexFind FindChildIndexInText(string markdown)
    {
        var candidate = FindFirstTable(markdown, requireChildIndex: true);
        if (candidate is null)
        {
            return new ChildIndexFind(TableFindStatus.NotFound, null, []);
        }

        var headers = candidate.Table.Headers;
        var aliasHeaders = headers.Where(AliasHeaders.Contains).ToArray();
        if (RequiredHeaders.All(required => headers.Contains(required, StringComparer.Ordinal)))
        {
            return new ChildIndexFind(TableFindStatus.Found, candidate.Table, aliasHeaders);
        }

        if (aliasHeaders.Length > 0)
        {
            return new ChildIndexFind(TableFindStatus.CompressedAlias, null, aliasHeaders);
        }

        return new ChildIndexFind(TableFindStatus.NotFound, null, []);
    }

    static TableCandidate? FindFirstTable(string markdown, bool requireChildIndex)
    {
        var lines = markdown.Replace("\r\n", "\n").Split('\n');
        for (var i = 0; i < lines.Length - 1; i++)
        {
            if (!IsTableLine(lines[i]) || !IsSeparatorLine(lines[i + 1]))
            {
                continue;
            }

            var headers = SplitRow(lines[i]);
            if (requireChildIndex &&
                !RequiredHeaders.All(required => headers.Contains(required, StringComparer.Ordinal)) &&
                !headers.Any(AliasHeaders.Contains))
            {
                continue;
            }

            var rows = new List<Dictionary<string, string>>();
            for (var r = i + 2; r < lines.Length && IsTableLine(lines[r]); r++)
            {
                var cells = SplitRow(lines[r]);
                var row = new Dictionary<string, string>(StringComparer.Ordinal);
                for (var c = 0; c < headers.Length; c++)
                {
                    row[headers[c]] = c < cells.Length ? cells[c] : "";
                }

                rows.Add(row);
            }

            return new TableCandidate(new MarkdownTable { Headers = headers, Rows = rows });
        }

        return null;
    }

    static string? ExtractSection(string markdown, string section)
    {
        var lines = markdown.Replace("\r\n", "\n").Split('\n');
        var start = -1;
        var level = 0;
        for (var i = 0; i < lines.Length; i++)
        {
            var match = Regex.Match(lines[i], @"^(#{1,6})\s+(.+?)\s*$");
            if (!match.Success || !match.Groups[2].Value.Trim().Equals(section, StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            start = i + 1;
            level = match.Groups[1].Value.Length;
            break;
        }

        if (start < 0)
        {
            return null;
        }

        var end = lines.Length;
        for (var i = start; i < lines.Length; i++)
        {
            var match = Regex.Match(lines[i], @"^(#{1,6})\s+");
            if (match.Success && match.Groups[1].Value.Length <= level)
            {
                end = i;
                break;
            }
        }

        return string.Join('\n', lines.Skip(start).Take(end - start));
    }

    static bool IsTableLine(string line) => line.TrimStart().StartsWith('|') && line.TrimEnd().EndsWith('|');

    static bool IsSeparatorLine(string line)
    {
        var cells = SplitRow(line);
        return cells.Length > 0 && cells.All(c => Regex.IsMatch(c, @"^:?-{3,}:?$"));
    }

    static string[] SplitRow(string line)
    {
        var trimmed = line.Trim();
        if (trimmed.StartsWith('|')) trimmed = trimmed[1..];
        if (trimmed.EndsWith('|')) trimmed = trimmed[..^1];
        return trimmed.Split('|').Select(c => c.Trim()).ToArray();
    }
}

sealed record TableCandidate(MarkdownTable Table);

static class MarkdownSummary
{
    public static string Render(ValidationResult result)
    {
        var lines = new List<string>
        {
            "**Validate Orchestration Pack**",
            "",
            $"- valid: `{result.Valid.ToString().ToLowerInvariant()}`",
            $"- child_count: `{result.ChildCount}`",
            $"- errors: `{result.FindingCounts.Errors}`",
            $"- warnings: `{result.FindingCounts.Warnings}`"
        };

        if (result.Findings.Count > 0)
        {
            lines.Add("");
            lines.Add("| Severity | Code | Child | Message |");
            lines.Add("|---|---|---|---|");
            lines.AddRange(result.Findings.Select(f => $"| `{f.Severity}` | `{f.Code}` | `{f.Child ?? ""}` | {EscapeMarkdownCell(f.Message)} |"));
        }

        return string.Join(Environment.NewLine, lines);
    }

    static string EscapeMarkdownCell(string value) => value.Replace("|", "\\|", StringComparison.Ordinal);
}

static class JsonSupport
{
    public static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        TypeInfoResolver = new DefaultJsonTypeInfoResolver()
    };
}
