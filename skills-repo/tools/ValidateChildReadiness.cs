using System.Text.RegularExpressions;

var options = Options.Parse(args);
if (!options.IsValid)
{
    Options.PrintUsage();
    return 2;
}

var errors = new List<string>();
var warnings = new List<string>();

var indexPath = Path.GetFullPath(options.IndexPath!);
if (!File.Exists(indexPath))
{
    Fail($"Child Index not found: {indexPath}");
}

var indexText = File.ReadAllText(indexPath);
var table = MarkdownTable.FindRequiredTable(indexText);
if (table is null)
{
    Fail("Child Index does not contain the exact required operational header:\n" + MarkdownTable.RequiredHeader);
    return 2;
}

var extraColumns = table.Headers.Where(h => !MarkdownTable.RequiredHeaders.Contains(h)).ToArray();
if (extraColumns.Length > 0 && !options.AllowExtraColumns)
{
    errors.Add("Child Index has extra columns. Keep the operational control surface exact or rerun with --allow-extra-columns if the workflow explicitly permits extras: " + string.Join(", ", extraColumns));
}

var aliasHeaders = table.Headers.Where(MarkdownTable.AliasHeaders.Contains).ToArray();
if (aliasHeaders.Length > 0)
{
    errors.Add("Child Index uses compressed/aliased substitute columns: " + string.Join(", ", aliasHeaders));
}

var row = table.Rows.FirstOrDefault(r => CellEquals(r["Child"], options.ChildId!));
if (row is null)
{
    errors.Add($"Child row not found in exact `Child` column: {options.ChildId}");
}
else
{
    ValidateRequiredCells(row, errors);
    ValidateReadiness(row, options, errors, warnings);
    ValidateHandoff(row, indexPath, options, errors, warnings);
}

if (errors.Count > 0)
{
    Console.Error.WriteLine("Child readiness validation failed:");
    foreach (var error in errors)
    {
        Console.Error.WriteLine("- " + error);
    }
    foreach (var warning in warnings)
    {
        Console.Error.WriteLine("warning: " + warning);
    }
    return 1;
}

Console.WriteLine($"Child readiness validation passed for {options.ChildId}.");
foreach (var warning in warnings)
{
    Console.WriteLine("warning: " + warning);
}
return 0;

static void ValidateRequiredCells(IReadOnlyDictionary<string, string> row, List<string> errors)
{
    foreach (var header in MarkdownTable.RequiredHeaders)
    {
        var value = NormalizeCell(row[header]);
        if (string.IsNullOrWhiteSpace(value) || value is "-" or "—")
        {
            errors.Add($"Required Child Index cell is empty: {header}");
        }
    }
}

static void ValidateReadiness(IReadOnlyDictionary<string, string> row, Options options, List<string> errors, List<string> warnings)
{
    var verdict = NormalizeCell(row["Readiness / Hardening Verdict"]);
    var isReady = ContainsVerdict(verdict, "IMPLEMENTATION READY") || ContainsVerdict(verdict, "READY WITH NON-BLOCKING NOTES");
    if (!isReady && options.RequireReady)
    {
        errors.Add("Readiness / Hardening Verdict is not an implementation-allowing verdict.");
    }

    var writeSet = NormalizeCell(row["Allowed Write-Set"]);
    ValidateWriteSet("Child Index Allowed Write-Set", writeSet, errors);

    var nextAction = NormalizeCell(row["Next Action"]);
    if (isReady && !nextAction.Contains("spec-change-delivery", StringComparison.OrdinalIgnoreCase))
    {
        errors.Add("Next Action for an implementation-ready child must name `spec-change-delivery`.");
    }

    foreach (var header in new[] { "Parent Coverage", "OpenSpec / Ledger", "Dependencies", "Verification", "Evidence / Closeout", "Backlog / Re-entry", "Next Action" })
    {
        var value = NormalizeCell(row[header]);
        if (LooksLikePlaceholder(value))
        {
            errors.Add($"Child Index cell `{header}` still looks like a placeholder: {value}");
        }
    }

    if (!isReady && !options.RequireReady)
    {
        warnings.Add($"Verdict is not implementation-allowing: {verdict}");
    }
}

static void ValidateHandoff(IReadOnlyDictionary<string, string> row, string indexPath, Options options, List<string> errors, List<string> warnings)
{
    var handoffCell = NormalizeCell(row["Session Handoff"]);
    var handoffFromIndex = ExtractPathFromMarkdownCell(handoffCell);
    var expectedHandoff = options.HandoffPath;

    if (string.IsNullOrWhiteSpace(handoffFromIndex) && string.IsNullOrWhiteSpace(expectedHandoff))
    {
        errors.Add("Session Handoff cell does not contain a usable file path.");
        return;
    }

    var indexDir = Path.GetDirectoryName(indexPath)!;
    var resolvedFromIndex = !string.IsNullOrWhiteSpace(handoffFromIndex)
        ? Path.GetFullPath(Path.Combine(indexDir, handoffFromIndex))
        : null;
    var resolvedExpected = !string.IsNullOrWhiteSpace(expectedHandoff)
        ? Path.GetFullPath(expectedHandoff)
        : null;

    var handoffPath = resolvedExpected ?? resolvedFromIndex!;
    if (resolvedFromIndex is not null && resolvedExpected is not null && !SamePath(resolvedFromIndex, resolvedExpected))
    {
        errors.Add($"Session Handoff pointer mismatch. Index points to `{resolvedFromIndex}`, but --handoff is `{resolvedExpected}`.");
    }

    if (!File.Exists(handoffPath))
    {
        errors.Add($"Session Handoff file not found: {handoffPath}");
        return;
    }

    var handoffText = File.ReadAllText(handoffPath);
    if (!handoffText.Contains(options.ChildId!, StringComparison.OrdinalIgnoreCase))
    {
        warnings.Add($"Handoff file does not mention child id `{options.ChildId}`.");
    }

    var indexVerdict = NormalizeCell(row["Readiness / Hardening Verdict"]);
    var handoffVerdict = ExtractBulletValue(handoffText, "Aktueller Verdict")
        ?? ExtractBulletValue(handoffText, "Current verdict");
    if (handoffVerdict is null)
    {
        errors.Add("Handoff is missing `Aktueller Verdict` / `Current verdict`.");
    }
    else if (!VerdictsAgree(indexVerdict, handoffVerdict))
    {
        errors.Add($"Verdict mismatch between Child Index (`{indexVerdict}`) and Handoff (`{handoffVerdict}`).");
    }

    var handoffWriteSet = ExtractBulletValue(handoffText, "Allowed Write-Set")
        ?? ExtractBulletValue(handoffText, "Allowed write-set");
    if (handoffWriteSet is null)
    {
        errors.Add("Handoff is missing `Allowed Write-Set`.");
    }
    else
    {
        ValidateWriteSet("Handoff Allowed Write-Set", handoffWriteSet, errors);
    }
}

static void ValidateWriteSet(string label, string value, List<string> errors)
{
    if (LooksLikePlaceholder(value))
    {
        errors.Add($"{label} still looks like a placeholder: {value}");
    }

    var forbidden = new[]
    {
        "voraussichtlich", "likely", "probably", "expected", "tbd", "to be decided",
        "as needed", "related files", "and related", "etc.", "etc"
    };
    foreach (var term in forbidden)
    {
        if (value.Contains(term, StringComparison.OrdinalIgnoreCase))
        {
            errors.Add($"{label} is approximate/advisory because it contains `{term}`.");
        }
    }

    var hasPathLikeEntry = Regex.IsMatch(value, @"[`']?[\w./*-]+/[\w./*{}-]+[`']?");
    if (!hasPathLikeEntry && !value.Contains(";"))
    {
        errors.Add($"{label} must name concrete paths, directories, or glob patterns.");
    }
}

static bool LooksLikePlaceholder(string value)
{
    var normalized = value.Trim().Trim('`').Trim();
    if (string.IsNullOrWhiteSpace(normalized)) return true;

    var placeholders = new[]
    {
        "tbd", "todo", "unknown", "n/a", "na", "none", "not hardened", "not evaluated",
        "pending", "blocked until own hardening", "to decide", "to be decided", "?", "-"
    };

    return placeholders.Any(p => normalized.Equals(p, StringComparison.OrdinalIgnoreCase));
}

static string? ExtractBulletValue(string text, string label)
{
    var pattern = @"^\s*[-*]\s*" + Regex.Escape(label) + @"\s*:\s*(.+?)\s*$";
    var match = Regex.Match(text, pattern, RegexOptions.Multiline | RegexOptions.IgnoreCase);
    return match.Success ? NormalizeCell(match.Groups[1].Value) : null;
}

static string ExtractPathFromMarkdownCell(string cell)
{
    var markdownLink = Regex.Match(cell, @"\[[^\]]+\]\(([^)]+)\)");
    if (markdownLink.Success) return markdownLink.Groups[1].Value.Trim();

    var codePath = Regex.Match(cell, @"`([^`]+)`");
    if (codePath.Success) return codePath.Groups[1].Value.Trim();

    return cell.Trim();
}

static bool VerdictsAgree(string indexVerdict, string handoffVerdict)
{
    foreach (var verdict in new[] { "IMPLEMENTATION READY", "READY WITH NON-BLOCKING NOTES", "NEEDS HARDENING", "NEEDS PARENT/ORCHESTRATOR SYNC", "NEEDS USER DECISION" })
    {
        if (ContainsVerdict(indexVerdict, verdict) && ContainsVerdict(handoffVerdict, verdict))
        {
            return true;
        }
    }
    return false;
}

static bool ContainsVerdict(string value, string verdict) =>
    value.Contains(verdict, StringComparison.OrdinalIgnoreCase);

static bool CellEquals(string left, string right) =>
    NormalizeCell(left).Equals(right.Trim(), StringComparison.OrdinalIgnoreCase);

static string NormalizeCell(string value)
{
    return value
        .Replace("<br>", "; ", StringComparison.OrdinalIgnoreCase)
        .Replace("<br/>", "; ", StringComparison.OrdinalIgnoreCase)
        .Replace("<br />", "; ", StringComparison.OrdinalIgnoreCase)
        .Trim();
}

static bool SamePath(string left, string right) =>
    string.Equals(Path.GetFullPath(left).TrimEnd(Path.DirectorySeparatorChar), Path.GetFullPath(right).TrimEnd(Path.DirectorySeparatorChar), StringComparison.Ordinal);

static void Fail(string message)
{
    Console.Error.WriteLine(message);
    Environment.Exit(2);
}

sealed class Options
{
    public string? IndexPath { get; private init; }
    public string? ChildId { get; private init; }
    public string? HandoffPath { get; private init; }
    public bool RequireReady { get; private init; } = true;
    public bool AllowExtraColumns { get; private init; }

    public bool IsValid => !string.IsNullOrWhiteSpace(IndexPath) && !string.IsNullOrWhiteSpace(ChildId);

    public static Options Parse(string[] args)
    {
        string? index = null;
        string? child = null;
        string? handoff = null;
        var requireReady = true;
        var allowExtra = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--index" when i + 1 < args.Length:
                    index = args[++i];
                    break;
                case "--child" when i + 1 < args.Length:
                    child = args[++i];
                    break;
                case "--handoff" when i + 1 < args.Length:
                    handoff = args[++i];
                    break;
                case "--allow-non-ready":
                    requireReady = false;
                    break;
                case "--allow-extra-columns":
                    allowExtra = true;
                    break;
            }
        }

        return new Options
        {
            IndexPath = index,
            ChildId = child,
            HandoffPath = handoff,
            RequireReady = requireReady,
            AllowExtraColumns = allowExtra
        };
    }

    public static void PrintUsage()
    {
        Console.Error.WriteLine("""
        Usage:
          dotnet run <path-to-ValidateChildReadiness.cs> -- --index <child-index.md> --child <child-id> [--handoff <handoff.md>]

        Options:
          --allow-non-ready       Validate structure without requiring IMPLEMENTATION READY / READY WITH NON-BLOCKING NOTES.
          --allow-extra-columns   Permit extra columns beyond the exact operational minimum.
        """);
    }
}

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

    public static readonly string RequiredHeader = "| " + string.Join(" | ", RequiredHeaders) + " |";

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

    public static MarkdownTable? FindRequiredTable(string markdown)
    {
        var lines = markdown.Replace("\r\n", "\n").Split('\n');
        for (var i = 0; i < lines.Length - 1; i++)
        {
            if (!IsTableLine(lines[i]) || !IsSeparatorLine(lines[i + 1]))
            {
                continue;
            }

            var headers = SplitRow(lines[i]);
            var hasAllRequired = RequiredHeaders.All(required => headers.Contains(required, StringComparer.Ordinal));
            if (!hasAllRequired && headers.Intersect(AliasHeaders, StringComparer.OrdinalIgnoreCase).Any())
            {
                return new MarkdownTable { Headers = headers, Rows = [] };
            }
            if (!hasAllRequired)
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

            return new MarkdownTable { Headers = headers, Rows = rows };
        }

        return null;
    }

    static bool IsTableLine(string line) => line.TrimStart().StartsWith("|", StringComparison.Ordinal) && line.TrimEnd().EndsWith("|", StringComparison.Ordinal);

    static bool IsSeparatorLine(string line)
    {
        var cells = SplitRow(line);
        return cells.Length > 0 && cells.All(c => Regex.IsMatch(c, @"^:?-{3,}:?$"));
    }

    static string[] SplitRow(string line)
    {
        var trimmed = line.Trim();
        if (trimmed.StartsWith("|")) trimmed = trimmed[1..];
        if (trimmed.EndsWith("|")) trimmed = trimmed[..^1];
        return trimmed.Split('|').Select(c => c.Trim()).ToArray();
    }
}
