using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;
using System.Text.RegularExpressions;
using static Util;

#pragma warning disable IL2026, IL3050

var options = Options.Parse(args);
if (options.ShowHelp || !options.IsValid)
{
    Options.PrintUsage();
    return options.ShowHelp ? 0 : 2;
}

var result = SyncChildHandoff.Run(options);
Output.Print(result, options);
return result.ExitCode;

static class SyncChildHandoff
{
    public static SyncResult Run(Options options)
    {
        var findings = new List<Finding>();
        var indexPath = Path.GetFullPath(options.IndexPath!);
        var outPath = Path.GetFullPath(options.OutPath!);
        var targetRepo = Path.GetFullPath(options.TargetRepo ?? Directory.GetCurrentDirectory());

        if (!File.Exists(indexPath))
        {
            findings.Add(Error("USAGE_ERROR", null, $"Child Index not found: {indexPath}"));
            return Build("error", options.ChildId!, outPath, null, findings, 2);
        }

        var table = MarkdownTable.FindRequiredTable(File.ReadAllText(indexPath));
        if (table is null)
        {
            findings.Add(Error("COMPRESSED_INDEX", null, "Child Index table with exact operational columns was not found."));
            return Build("error", options.ChildId!, outPath, null, findings, 2);
        }

        if (table.HasAliasHeaders)
        {
            findings.Add(Error("COMPRESSED_INDEX", null, "Child Index uses compressed/aliased substitute columns."));
            return Build("error", options.ChildId!, outPath, null, findings, 2);
        }

        var row = table.Rows.FirstOrDefault(r => CellEquals(r["Child"], options.ChildId!));
        if (row is null)
        {
            findings.Add(Error("CHILD_NOT_FOUND", "Child", $"Child row not found in exact `Child` column: {options.ChildId}."));
            return Build("error", options.ChildId!, outPath, null, findings, 2);
        }

        ValidateIndexPointer(row, indexPath, outPath, findings);
        ValidateWriteSet(row["Allowed Write-Set"], options.AllowApproxWriteSet, findings);

        var existed = File.Exists(outPath);
        var existingText = existed ? File.ReadAllText(outPath) : "";
        var existingFields = existed ? HandoffFields.Parse(existingText) : new Dictionary<string, string>(StringComparer.Ordinal);
        var timestamp = ResolveTimestamp(options, existingFields);
        var expected = HandoffRenderer.Render(row, new RenderInputs(
            Parent: options.ParentPath ?? "unknown",
            IndexPath: indexPath,
            OutPath: outPath,
            TargetRepo: targetRepo,
            Timestamp: timestamp));
        if (!existed)
        {
            findings.Add(new Finding("warning", "HANDOFF_MISSING", null, $"Handoff not found: {outPath}."));
        }
        else
        {
            CompareControlledFields(existingFields, HandoffFields.Parse(expected), findings);
        }

        if (HasBlocking(findings))
        {
            return Build("blocked", row["Child"], outPath, options.Mode == Mode.DryRun ? expected : null, findings, 1);
        }

        if (options.Mode == Mode.Check)
        {
            if (findings.Any(f => f.Code is "HANDOFF_MISSING" or "FIELD_DRIFT"))
            {
                return Build("blocked", row["Child"], outPath, null, PromoteDriftForCheck(findings), 1);
            }

            return Build("current", row["Child"], outPath, null, findings, 0);
        }

        if (options.Mode == Mode.DryRun)
        {
            var status = existed ? "would_update" : "would_create";
            return Build(status, row["Child"], outPath, expected, findings, 0);
        }

        var preserved = PreserveManualSection(existingText);
        var finalText = expected + preserved;
        Directory.CreateDirectory(Path.GetDirectoryName(outPath)!);
        File.WriteAllText(outPath, finalText);
        return Build("written", row["Child"], outPath, null, findings, 0);
    }

    static SyncResult Build(string status, string child, string handoffPath, string? proposedHandoff, List<Finding> findings, int exitCode) =>
        new(status, NormalizeCell(child), handoffPath, findings, proposedHandoff, exitCode);

    static void ValidateIndexPointer(IReadOnlyDictionary<string, string> row, string indexPath, string outPath, List<Finding> findings)
    {
        var cell = NormalizeCell(row["Session Handoff"]);
        var pointer = ExtractPathFromMarkdownCell(cell);
        if (string.IsNullOrWhiteSpace(pointer))
        {
            findings.Add(Error("INDEX_POINTER_MISMATCH", "Session Handoff", "Child Index Session Handoff cell does not contain a usable path."));
            return;
        }

        var resolved = Path.IsPathRooted(pointer)
            ? Path.GetFullPath(pointer)
            : Path.GetFullPath(Path.Combine(Path.GetDirectoryName(indexPath)!, pointer));
        if (!SamePath(resolved, outPath))
        {
            findings.Add(Error("INDEX_POINTER_MISMATCH", "Session Handoff", $"Child Index points to `{resolved}`, but --out is `{outPath}`."));
        }
    }

    static void ValidateWriteSet(string value, bool allowApprox, List<Finding> findings)
    {
        var normalized = NormalizeCell(value);
        var forbidden = new[]
        {
            "voraussichtlich", "likely", "probably", "expected", "tbd", "to be decided",
            "as needed", "related files", "and related", "etc.", "etc"
        };

        var messages = new List<string>();
        foreach (var term in forbidden)
        {
            if (normalized.Contains(term, StringComparison.OrdinalIgnoreCase))
            {
                messages.Add($"contains `{term}`");
            }
        }

        var hasPathLikeEntry = Regex.IsMatch(normalized, @"[`']?[\w./*-]+/[\w./*{}-]+[`']?");
        if (!hasPathLikeEntry && !normalized.Contains(';'))
        {
            messages.Add("does not name concrete paths, directories or glob patterns");
        }

        foreach (var message in messages)
        {
            findings.Add(new Finding(allowApprox ? "warning" : "error", "APPROX_WRITE_SET", "Allowed Write-Set", $"Allowed Write-Set is approximate: {message}."));
        }
    }

    static void CompareControlledFields(IReadOnlyDictionary<string, string> actual, IReadOnlyDictionary<string, string> expected, List<Finding> findings)
    {
        foreach (var (field, expectedValue) in expected)
        {
            if (!actual.TryGetValue(field, out var actualValue))
            {
                findings.Add(new Finding("warning", "FIELD_DRIFT", field, $"Handoff is missing controlled field `{field}`."));
                continue;
            }

            if (!NormalizeComparable(actualValue).Equals(NormalizeComparable(expectedValue), StringComparison.Ordinal))
            {
                findings.Add(new Finding("warning", "FIELD_DRIFT", field, $"Handoff field `{field}` is stale. Expected `{expectedValue}`, found `{actualValue}`."));
            }
        }
    }

    static List<Finding> PromoteDriftForCheck(List<Finding> findings) =>
        findings.Select(f => f.Code is "HANDOFF_MISSING" or "FIELD_DRIFT" ? f with { Severity = "error" } : f).ToList();

    static string ResolveTimestamp(Options options, IReadOnlyDictionary<string, string> existingFields)
    {
        if (!string.IsNullOrWhiteSpace(options.Timestamp))
        {
            return options.Timestamp;
        }

        if (options.Mode == Mode.Check && existingFields.TryGetValue("Handoff Timestamp", out var existingTimestamp) && !string.IsNullOrWhiteSpace(existingTimestamp))
        {
            return existingTimestamp;
        }

        return DateTimeOffset.UtcNow.ToString("yyyy-MM-dd");
    }

    static bool HasBlocking(IEnumerable<Finding> findings) =>
        findings.Any(f => f.Severity == "error" && f.Code is not "FIELD_DRIFT" and not "HANDOFF_MISSING");

    static string PreserveManualSection(string text)
    {
        if (string.IsNullOrEmpty(text)) return "";

        var match = Regex.Match(text.Replace("\r\n", "\n"), @"(?m)^## Notes Preserved By Sync\b");
        if (!match.Success) return "";

        var preserved = text.Replace("\r\n", "\n")[match.Index..].TrimEnd();
        return "\n\n" + preserved + "\n";
    }

    static Finding Error(string code, string? field, string message) => new("error", code, field, message);
}

static class HandoffRenderer
{
    public static string Render(IReadOnlyDictionary<string, string> row, RenderInputs inputs)
    {
        var child = NormalizeCell(row["Child"]);
        var childSpec = NormalizeCell(row["Child Spec"]);
        var parentCoverage = NormalizeCell(row["Parent Coverage"]);
        var verdict = NormalizeCell(row["Readiness / Hardening Verdict"]);
        var dependencies = NormalizeCell(row["Dependencies"]);
        var writeSet = NormalizeCell(row["Allowed Write-Set"]);
        var verification = NormalizeCell(row["Verification"]);
        var ledger = NormalizeCell(row["OpenSpec / Ledger"]);
        var evidence = NormalizeCell(row["Evidence / Closeout"]);
        var backlog = NormalizeCell(row["Backlog / Re-entry"]);
        var nextAction = NormalizeCell(row["Next Action"]);
        var freshSession = nextAction.Contains("spec-change-delivery", StringComparison.OrdinalIgnoreCase) ? "Yes" : "Review next action";

        return $"""
        ## Child Session Handoff

        - Parent: {NormalizePathValue(inputs.Parent)}
        - Stable Child ID: {child}
        - Child: {child}
        - Child Spec: {childSpec}
        - Child Index / Queue: {NormalizePathValue(inputs.IndexPath)} section `Child Index`
        - Handoff File: {NormalizePathValue(inputs.OutPath)}
        - Target Repository / Working Directory: {inputs.TargetRepo}
        - Codex Session / Log: not created by SyncChildHandoff
        - Session Evidence: not created by SyncChildHandoff
        - Handoff Timestamp: {inputs.Timestamp}
        - Naechster Modus/Skill: {nextAction}
        - Aktueller Verdict: {verdict}
        - Scope Summary: Parent Coverage: {parentCoverage}. Dependencies: {dependencies}.
        - Non-Goals: No agent session launch; no edits outside the allowed write-set.
        - Allowed Write-Set: {writeSet}
        - Shared / Read-only Files: `docs/doc-workflow.md`; `skills-repo/tools/ValidateChildReadiness.cs`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`
        - Verification Lifecycle:
          - Rehearsal / Preflight: not recorded by SyncChildHandoff
          - Delivery Gate: {verification}
          - Pre-Archive Closeout: not recorded by SyncChildHandoff
          - Post-Archive / Current Replay: not recorded by SyncChildHandoff
        - Evidence / OpenSpec: {ledger}; {evidence}
        - Retained Evidence: {evidence}
        - Offene Blocker oder non-blocking Notes: {backlog}
        - Fresh Session empfohlen: {freshSession}
        """.TrimEnd() + "\n";
    }

    static string NormalizePathValue(string value)
    {
        var normalized = NormalizeCell(value);
        return string.IsNullOrWhiteSpace(normalized) ? "unknown" : normalized;
    }
}

static class HandoffFields
{
    public static Dictionary<string, string> Parse(string text)
    {
        var fields = new Dictionary<string, string>(StringComparer.Ordinal);
        var lines = text.Replace("\r\n", "\n").Split('\n');
        for (var i = 0; i < lines.Length; i++)
        {
            var line = lines[i];
            if (!line.StartsWith("- ", StringComparison.Ordinal))
            {
                continue;
            }

            var colon = line.IndexOf(':');
            if (colon < 0) continue;

            var key = line[2..colon].Trim();
            var value = line[(colon + 1)..].Trim();
            if (key == "Verification Lifecycle")
            {
                var nested = new List<string>();
                for (var j = i + 1; j < lines.Length && lines[j].StartsWith("  - ", StringComparison.Ordinal); j++)
                {
                    nested.Add(lines[j].Trim());
                    i = j;
                }
                value = string.Join("; ", nested);
            }

            fields[key] = NormalizeCell(value);
        }

        return fields;
    }
}

static class Output
{
    public static void Print(SyncResult result, Options options)
    {
        if (options.Format == "json")
        {
            Console.WriteLine(JsonSerializer.Serialize(result, JsonSupport.Options));
            return;
        }

        Console.WriteLine($"{result.Status}: {result.HandoffPath}");
        foreach (var finding in result.Findings)
        {
            Console.WriteLine($"{finding.Severity}: {finding.Code}" + (finding.Field is null ? "" : $" [{finding.Field}]") + $": {finding.Message}");
        }

        if (!string.IsNullOrWhiteSpace(result.ProposedHandoff))
        {
            Console.WriteLine();
            Console.Write(result.ProposedHandoff);
        }
    }
}

sealed class Options
{
    public string? IndexPath { get; private init; }
    public string? ChildId { get; private init; }
    public string? OutPath { get; private init; }
    public string? TargetRepo { get; private init; }
    public string? ParentPath { get; private init; }
    public string? Timestamp { get; private init; }
    public Mode Mode { get; private init; }
    public string Format { get; private init; } = "text";
    public bool AllowApproxWriteSet { get; private init; }
    public bool ShowHelp { get; private init; }

    public bool IsValid =>
        ShowHelp ||
        (!string.IsNullOrWhiteSpace(IndexPath) &&
         !string.IsNullOrWhiteSpace(ChildId) &&
         !string.IsNullOrWhiteSpace(OutPath) &&
         Mode != Mode.None &&
         (Format is "text" or "json") &&
         (string.IsNullOrWhiteSpace(Timestamp) || Regex.IsMatch(Timestamp, @"^\d{4}-\d{2}-\d{2}$")));

    public static Options Parse(string[] args)
    {
        string? index = null;
        string? child = null;
        string? outPath = null;
        string? targetRepo = null;
        string? parent = null;
        string? timestamp = null;
        var mode = Mode.None;
        var modeCount = 0;
        var format = "text";
        var allowApprox = false;
        var showHelp = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--help" or "-h":
                    showHelp = true;
                    break;
                case "--index" when i + 1 < args.Length:
                    index = args[++i];
                    break;
                case "--child" when i + 1 < args.Length:
                    child = args[++i];
                    break;
                case "--out" when i + 1 < args.Length:
                    outPath = args[++i];
                    break;
                case "--target-repo" when i + 1 < args.Length:
                    targetRepo = args[++i];
                    break;
                case "--parent" when i + 1 < args.Length:
                    parent = args[++i];
                    break;
                case "--timestamp" when i + 1 < args.Length:
                    timestamp = args[++i];
                    break;
                case "--check":
                    mode = Mode.Check;
                    modeCount++;
                    break;
                case "--dry-run":
                    mode = Mode.DryRun;
                    modeCount++;
                    break;
                case "--write":
                    mode = Mode.Write;
                    modeCount++;
                    break;
                case "--format" when i + 1 < args.Length:
                    format = args[++i];
                    break;
                case "--allow-approx-write-set":
                    allowApprox = true;
                    break;
                case "--allow-non-ready":
                    break;
            }
        }

        if (modeCount != 1 && !showHelp)
        {
            mode = Mode.None;
        }

        return new Options
        {
            IndexPath = index,
            ChildId = child,
            OutPath = outPath,
            TargetRepo = targetRepo,
            ParentPath = parent,
            Timestamp = timestamp,
            Mode = mode,
            Format = format,
            AllowApproxWriteSet = allowApprox,
            ShowHelp = showHelp
        };
    }

    public static void PrintUsage()
    {
        Console.Error.WriteLine("""
        Usage:
          dotnet run <path-to-SyncChildHandoff.cs> -- --index <child-index.md> --child <child-id> --out <handoff.md> (--check|--dry-run|--write) [options]

        Options:
          --target-repo <path>          Target Repository / Working Directory. Defaults to current working directory.
          --parent <path>               Parent field to render. Defaults to unknown.
          --timestamp <yyyy-MM-dd>      Deterministic handoff timestamp. Check mode accepts existing timestamp when omitted.
          --format text|json            Output format. Defaults to text.
          --allow-non-ready             Accepted for workflow compatibility; does not change sync behavior.
          --allow-approx-write-set      Downgrade approximate Allowed Write-Set findings to warnings.
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
    public bool HasAliasHeaders => Headers.Any(AliasHeaders.Contains);

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

static class JsonSupport
{
    public static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        TypeInfoResolver = new DefaultJsonTypeInfoResolver()
    };
}

record RenderInputs(string Parent, string IndexPath, string OutPath, string TargetRepo, string Timestamp);

record SyncResult(
    [property: JsonPropertyName("status")] string Status,
    [property: JsonPropertyName("child")] string Child,
    [property: JsonPropertyName("handoff_path")] string HandoffPath,
    [property: JsonPropertyName("findings")] IReadOnlyList<Finding> Findings,
    [property: JsonPropertyName("proposed_handoff")] string? ProposedHandoff,
    [property: JsonIgnore] int ExitCode);

record Finding(
    [property: JsonPropertyName("severity")] string Severity,
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("field")] string? Field,
    [property: JsonPropertyName("message")] string Message);

enum Mode
{
    None,
    Check,
    DryRun,
    Write
}

static class Util
{
    public static bool CellEquals(string left, string right) =>
        NormalizeCell(left).Equals(right.Trim(), StringComparison.OrdinalIgnoreCase);

    public static string NormalizeCell(string value)
    {
        return value
            .Replace("<br>", "; ", StringComparison.OrdinalIgnoreCase)
            .Replace("<br/>", "; ", StringComparison.OrdinalIgnoreCase)
            .Replace("<br />", "; ", StringComparison.OrdinalIgnoreCase)
            .Trim();
    }

    public static string NormalizeComparable(string value) =>
        Regex.Replace(NormalizeCell(value).Trim('`').Trim(), @"\s+", " ");

    public static string ExtractPathFromMarkdownCell(string cell)
    {
        var markdownLink = Regex.Match(cell, @"\[[^\]]+\]\(([^)]+)\)");
        if (markdownLink.Success) return markdownLink.Groups[1].Value.Trim();

        var codePath = Regex.Match(cell, @"`([^`]+)`");
        if (codePath.Success) return codePath.Groups[1].Value.Trim();

        return cell.Trim();
    }

    public static bool SamePath(string left, string right) =>
        string.Equals(Path.GetFullPath(left).TrimEnd(Path.DirectorySeparatorChar), Path.GetFullPath(right).TrimEnd(Path.DirectorySeparatorChar), StringComparison.Ordinal);
}
