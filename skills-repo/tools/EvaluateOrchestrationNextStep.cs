using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;
using System.Text.RegularExpressions;

#pragma warning disable IL2026, IL3050

var options = Options.Parse(args);
if (options.ShowHelp || !options.IsValid)
{
    Options.PrintUsage();
    return options.ShowHelp ? 0 : 2;
}

var result = Evaluator.Evaluate(options);
if (result.Errors.Count > 0)
{
    Print(result, options.Format);
    return 2;
}

Print(result, options.Format);
return options.FailOnRequiredNextStep && result.RequiredNextSkill != "none" ? 1 : 0;

static void Print(EvaluationResult result, string format)
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

static class Evaluator
{
    public static EvaluationResult Evaluate(Options options)
    {
        var errors = new List<string>();
        var warnings = new List<string>();
        var packPath = Path.GetFullPath(options.PackPath!);
        var repoPath = Path.GetFullPath(options.RepoPath ?? Directory.GetCurrentDirectory());

        if (!File.Exists(packPath))
        {
            errors.Add($"Pack not found: {packPath}");
            return ErrorResult(options, packPath, repoPath, errors, warnings);
        }

        if (!Directory.Exists(repoPath))
        {
            warnings.Add($"Repository path does not exist in this environment: {repoPath}");
        }

        var markdown = File.ReadAllText(packPath);
        var table = MarkdownTable.FindRequiredTable(markdown, options.ChildIndexSection!);
        if (table is null)
        {
            errors.Add("Child Index table with exact operational columns was not found.");
            return ErrorResult(options, packPath, repoPath, errors, warnings);
        }

        var rows = table.Rows.Select((row, index) => ChildRow.From(row, index)).ToList();
        var states = rows.ToDictionary(row => row.Child, DetermineRowState, StringComparer.OrdinalIgnoreCase);
        var lanes = rows.Select(row => Classify(row, rows, states, repoPath)).ToList();

        var firstReady = lanes.FirstOrDefault(l => l.Classification == "ready_for_delivery");
        var firstHardenNow = lanes.FirstOrDefault(l => l.Classification == "harden_now");
        var hardeningExpected = options.Intent is "expects-hardening" or "expects-implementation-ready" or "hardening-queue-only";
        var userDeferredHardening = options.Intent is "orchestration-only" or "stop-before-hardening";

        var requiredNextSkill = "none";
        var triggerResult = "no_action_required";
        var finalStatusToken = "no_action_required";
        string? firstUnblockedChild = null;
        var deliveryAllowed = false;

        if (userDeferredHardening)
        {
            triggerResult = options.Intent == "orchestration-only"
                ? "orchestration_only_by_user_request"
                : "hardening_deferred_by_user";
            finalStatusToken = options.Intent == "orchestration-only"
                ? "orchestration_only_by_user_request"
                : "hardening_deferred_by_user";
        }
        else if (firstReady is not null)
        {
            firstUnblockedChild = firstReady.Child;
            deliveryAllowed = !options.NoImplementation;
            if (deliveryAllowed)
            {
                requiredNextSkill = "spec-change-delivery";
                triggerResult = "ready_for_delivery";
                finalStatusToken = "ready_for_spec_change_delivery";
            }
            else
            {
                triggerResult = "ready_for_delivery";
                finalStatusToken = "no_action_required";
                warnings.Add("A child is implementation-ready, but --no-implementation prevents routing to spec-change-delivery.");
            }
        }
        else if (hardeningExpected && firstHardenNow is not null)
        {
            requiredNextSkill = "child-spec-hardening";
            firstUnblockedChild = firstHardenNow.Child;
            triggerResult = "hardening_required_not_started";
            finalStatusToken = "hardening_started_required";
        }
        else if (hardeningExpected && lanes.Any(l => l.Classification == "blocked_by_dependency"))
        {
            triggerResult = "hardening_blocked";
            finalStatusToken = "hardening_blocked";
        }
        else if (lanes.Any(l => l.Classification == "needs_orchestrator_sync"))
        {
            requiredNextSkill = "spec-orchestrator";
            triggerResult = "hardening_blocked";
            finalStatusToken = "hardening_blocked";
        }

        if (lanes.Any(l => l.Classification == "parallel_draft_only") && requiredNextSkill == "child-spec-hardening")
        {
            warnings.Add("Parallel hardening lanes are available, but parallel agents require explicit user authorization.");
        }

        return new EvaluationResult
        {
            PackPath = packPath,
            RepoPath = repoPath,
            Intent = options.Intent!,
            NoImplementation = options.NoImplementation,
            WorkflowPhase = "post_orchestration",
            RequiredNextSkill = requiredNextSkill,
            FirstUnblockedChild = firstUnblockedChild,
            DeliveryAllowed = deliveryAllowed,
            HardeningExpected = hardeningExpected,
            TriggerResult = triggerResult,
            FinalStatusToken = finalStatusToken,
            LaneClassification = lanes,
            Warnings = warnings,
            Errors = errors
        };
    }

    static EvaluationResult ErrorResult(Options options, string packPath, string repoPath, List<string> errors, List<string> warnings) => new()
    {
        PackPath = packPath,
        RepoPath = repoPath,
        Intent = options.Intent ?? "unknown",
        NoImplementation = options.NoImplementation,
        WorkflowPhase = "post_orchestration",
        RequiredNextSkill = "spec-orchestrator",
        FirstUnblockedChild = null,
        DeliveryAllowed = false,
        HardeningExpected = options.Intent is "expects-hardening" or "expects-implementation-ready" or "hardening-queue-only",
        TriggerResult = "hardening_blocked",
        FinalStatusToken = "hardening_blocked",
        LaneClassification = [],
        Warnings = warnings,
        Errors = errors
    };

    static string DetermineRowState(ChildRow row)
    {
        var verdict = Normalize(row.Verdict);
        var nextAction = Normalize(row.NextAction);
        if (verdict.Contains("DEFERRED", StringComparison.OrdinalIgnoreCase) ||
            nextAction.StartsWith("DO NOT START", StringComparison.OrdinalIgnoreCase))
        {
            return "deferred";
        }

        if (IsImplementationReady(row.Verdict))
        {
            return "ready_for_delivery";
        }

        if (verdict.Contains("NEEDS HARDENING", StringComparison.OrdinalIgnoreCase))
        {
            return "needs_hardening";
        }

        if (verdict.Contains("BLOCK", StringComparison.OrdinalIgnoreCase))
        {
            return "blocked_by_dependency";
        }

        return "needs_orchestrator_sync";
    }

    static LaneClassification Classify(ChildRow row, List<ChildRow> rows, Dictionary<string, string> states, string repoPath)
    {
        var state = states[row.Child];
        var handoff = ExtractPath(row.SessionHandoff);
        var dependencies = ExtractChildIds(row.Dependencies)
            .Where(id => !id.Equals(row.Child, StringComparison.OrdinalIgnoreCase))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToArray();

        var unresolved = dependencies
            .Where(id => !states.TryGetValue(id, out var dependencyState) || dependencyState is not "ready_for_delivery")
            .ToArray();

        if (state == "deferred")
        {
            return Lane(row, "deferred", "child is explicitly deferred or says not to start", handoff);
        }

        if (state == "ready_for_delivery")
        {
            return Lane(row, "ready_for_delivery", "child has an implementation-allowing verdict", handoff);
        }

        if (state == "needs_orchestrator_sync")
        {
            return Lane(row, "needs_orchestrator_sync", "child verdict is not recognized as ready, needs hardening, blocked, or deferred", handoff);
        }

        if (IsParallelDraftOnly(row))
        {
            return Lane(row, "parallel_draft_only", "row allows partial/draft spec or docs work, but final readiness waits for integration", handoff);
        }

        if (unresolved.Length > 0)
        {
            return Lane(row, "blocked_by_dependency", "depends on unresolved predecessor child ids: " + string.Join(", ", unresolved), handoff);
        }

        var firstUnblockedHardening = rows
            .Where(r => states[r.Child] == "needs_hardening")
            .FirstOrDefault(r =>
            {
                var deps = ExtractChildIds(r.Dependencies).Where(id => !id.Equals(r.Child, StringComparison.OrdinalIgnoreCase));
                return deps.All(id => states.TryGetValue(id, out var dependencyState) && dependencyState == "ready_for_delivery");
            });

        if (firstUnblockedHardening is not null && firstUnblockedHardening.Child.Equals(row.Child, StringComparison.OrdinalIgnoreCase))
        {
            return Lane(row, "harden_now", "needs hardening and has no unresolved predecessor dependency", handoff);
        }

        return Lane(row, "blocked_by_dependency", "later hardening waits for the first unblocked child to harden", handoff);
    }

    static bool IsParallelDraftOnly(ChildRow row)
    {
        var text = Normalize(string.Join(" ", row.Dependencies, row.BacklogReEntry, row.NextAction, row.Verification));
        return text.Contains("PARTIALLY PARALLEL", StringComparison.OrdinalIgnoreCase) ||
               text.Contains("DRAFT", StringComparison.OrdinalIgnoreCase) ||
               text.Contains("PARTIAL DRAFT", StringComparison.OrdinalIgnoreCase);
    }

    static LaneClassification Lane(ChildRow row, string classification, string reason, string? handoff) => new()
    {
        Child = row.Child,
        Classification = classification,
        Reason = reason,
        Handoff = handoff
    };

    static bool IsImplementationReady(string value)
    {
        var normalized = Normalize(value);
        return normalized.Contains("IMPLEMENTATION READY", StringComparison.OrdinalIgnoreCase) ||
               normalized.Contains("READY WITH NON-BLOCKING NOTES", StringComparison.OrdinalIgnoreCase);
    }

    static string[] ExtractChildIds(string value)
    {
        return Regex.Matches(value, @"\b[A-Z]{2,}-[A-Z0-9]+-\d+\b|\b[A-Z]{2,}-\d+\b|\bS\d+\b|\bDWT-S\d+\b", RegexOptions.IgnoreCase)
            .Select(m => m.Value.Trim('`', '.', ',', ';', ':'))
            .Where(v => !string.IsNullOrWhiteSpace(v))
            .ToArray();
    }

    static string? ExtractPath(string value)
    {
        var match = Regex.Match(value, @"`([^`]+\.(?:md|json))`");
        if (match.Success)
        {
            return match.Groups[1].Value;
        }

        match = Regex.Match(value, @"(\S+\.(?:md|json))");
        return match.Success ? match.Groups[1].Value.TrimEnd('.', ',', ';') : null;
    }

    static string Normalize(string value) => Regex.Replace(value.Replace("<br>", " ", StringComparison.OrdinalIgnoreCase), @"\s+", " ").Trim();
}

sealed class Options
{
    static readonly HashSet<string> Intents = new(StringComparer.Ordinal)
    {
        "expects-hardening",
        "expects-implementation-ready",
        "hardening-queue-only",
        "orchestration-only",
        "stop-before-hardening",
        "unknown"
    };

    static readonly HashSet<string> Formats = new(StringComparer.Ordinal)
    {
        "json",
        "markdown",
        "both"
    };

    public string? PackPath { get; private init; }
    public string? RepoPath { get; private init; }
    public string? ChildIndexSection { get; private init; } = "Child Index";
    public string? Intent { get; private init; } = "unknown";
    public bool NoImplementation { get; private init; }
    public string Format { get; private init; } = "json";
    public bool FailOnRequiredNextStep { get; private init; }
    public bool ShowHelp { get; private init; }
    public bool ParseError { get; private init; }

    public bool IsValid =>
        !ParseError &&
        (!string.IsNullOrWhiteSpace(PackPath) &&
         !string.IsNullOrWhiteSpace(ChildIndexSection) &&
         Intent is not null &&
         Intents.Contains(Intent) &&
         Formats.Contains(Format));

    public static Options Parse(string[] args)
    {
        string? pack = null;
        string? repo = null;
        var section = "Child Index";
        var intent = "unknown";
        var noImplementation = false;
        var format = "json";
        var failOnRequiredNextStep = false;
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
                    section = RequireValue(args, ref i, "--child-index-section", ref parseError);
                    break;
                case "--intent":
                    intent = RequireValue(args, ref i, "--intent", ref parseError);
                    break;
                case "--no-implementation":
                    noImplementation = true;
                    break;
                case "--format":
                    format = RequireValue(args, ref i, "--format", ref parseError);
                    break;
                case "--fail-on-required-next-step":
                    failOnRequiredNextStep = true;
                    break;
                default:
                    Console.Error.WriteLine($"Unknown argument: {args[i]}");
                    parseError = true;
                    break;
            }
        }

        return new Options
        {
            PackPath = pack,
            RepoPath = repo,
            ChildIndexSection = section,
            Intent = intent,
            NoImplementation = noImplementation,
            Format = format,
            FailOnRequiredNextStep = failOnRequiredNextStep,
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

    public static void PrintUsage()
    {
        Console.WriteLine("""
        Usage:
          dotnet run <path-to-EvaluateOrchestrationNextStep.cs> -- --pack <orchestration-pack.md> [options]

        Options:
          --pack <path>                   Markdown file containing the Child Index.
          --repo <path>                   Repository root for resolving related paths. Defaults to current directory.
          --child-index-section <name>    Section heading to prefer. Default: Child Index.
          --intent <value>                expects-hardening | expects-implementation-ready | hardening-queue-only | orchestration-only | stop-before-hardening | unknown.
          --no-implementation             Runtime/product implementation is forbidden; spec hardening remains allowed.
          --format <json|markdown|both>   Output format. Default: json.
          --fail-on-required-next-step    Exit 1 when a required next workflow step is present.
          --help                          Print this help and exit 0.

        Exit codes:
          0  Evaluation succeeded.
          1  Evaluation succeeded and --fail-on-required-next-step found a required next step.
          2  Invalid arguments, unreadable files, or malformed required table structure.
        """);
    }
}

sealed record ChildRow
{
    public required int Index { get; init; }
    public required string Child { get; init; }
    public required string ChildSpec { get; init; }
    public required string Verdict { get; init; }
    public required string SessionHandoff { get; init; }
    public required string Dependencies { get; init; }
    public required string Verification { get; init; }
    public required string BacklogReEntry { get; init; }
    public required string NextAction { get; init; }

    public static ChildRow From(IReadOnlyDictionary<string, string> row, int index) => new()
    {
        Index = index,
        Child = row["Child"],
        ChildSpec = row["Child Spec"],
        Verdict = row["Readiness / Hardening Verdict"],
        SessionHandoff = row["Session Handoff"],
        Dependencies = row["Dependencies"],
        Verification = row["Verification"],
        BacklogReEntry = row["Backlog / Re-entry"],
        NextAction = row["Next Action"]
    };
}

sealed class EvaluationResult
{
    [JsonPropertyName("schema")]
    public string Schema { get; init; } = "agent-delivery.evaluate-orchestration-next-step.v1";

    [JsonPropertyName("pack_path")]
    public required string PackPath { get; init; }

    [JsonPropertyName("repo_path")]
    public required string RepoPath { get; init; }

    [JsonPropertyName("intent")]
    public required string Intent { get; init; }

    [JsonPropertyName("no_implementation")]
    public required bool NoImplementation { get; init; }

    [JsonPropertyName("workflow_phase")]
    public required string WorkflowPhase { get; init; }

    [JsonPropertyName("required_next_skill")]
    public required string RequiredNextSkill { get; init; }

    [JsonPropertyName("first_unblocked_child")]
    public required string? FirstUnblockedChild { get; init; }

    [JsonPropertyName("delivery_allowed")]
    public required bool DeliveryAllowed { get; init; }

    [JsonPropertyName("hardening_expected")]
    public required bool HardeningExpected { get; init; }

    [JsonPropertyName("trigger_result")]
    public required string TriggerResult { get; init; }

    [JsonPropertyName("final_status_token")]
    public required string FinalStatusToken { get; init; }

    [JsonPropertyName("lane_classification")]
    public required List<LaneClassification> LaneClassification { get; init; }

    [JsonPropertyName("warnings")]
    public required List<string> Warnings { get; init; }

    [JsonPropertyName("errors")]
    public required List<string> Errors { get; init; }
}

sealed class LaneClassification
{
    [JsonPropertyName("child")]
    public required string Child { get; init; }

    [JsonPropertyName("classification")]
    public required string Classification { get; init; }

    [JsonPropertyName("reason")]
    public required string Reason { get; init; }

    [JsonPropertyName("handoff")]
    public string? Handoff { get; init; }
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

    public required string[] Headers { get; init; }
    public required List<Dictionary<string, string>> Rows { get; init; }

    public static MarkdownTable? FindRequiredTable(string markdown, string section)
    {
        var scoped = ExtractSection(markdown, section) ?? markdown;
        return FindTable(scoped) ?? (ReferenceEquals(scoped, markdown) ? null : FindTable(markdown));
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

    static MarkdownTable? FindTable(string markdown)
    {
        var lines = markdown.Replace("\r\n", "\n").Split('\n');
        for (var i = 0; i < lines.Length - 1; i++)
        {
            if (!IsTableLine(lines[i]) || !IsSeparatorLine(lines[i + 1]))
            {
                continue;
            }

            var headers = SplitRow(lines[i]);
            if (!RequiredHeaders.All(required => headers.Contains(required, StringComparer.Ordinal)))
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
        if (trimmed.StartsWith('|')) trimmed = trimmed[1..];
        if (trimmed.EndsWith('|')) trimmed = trimmed[..^1];
        return trimmed.Split('|').Select(c => c.Trim()).ToArray();
    }
}

static class MarkdownSummary
{
    public static string Render(EvaluationResult result)
    {
        var lines = new List<string>
        {
            "**Evaluate Orchestration Next Step**",
            "",
            $"- required_next_skill: `{result.RequiredNextSkill}`",
            $"- first_unblocked_child: `{result.FirstUnblockedChild ?? ""}`",
            $"- delivery_allowed: `{result.DeliveryAllowed.ToString().ToLowerInvariant()}`",
            $"- trigger_result: `{result.TriggerResult}`",
            $"- final_status_token: `{result.FinalStatusToken}`",
            "",
            "| Child | Classification | Reason |",
            "|---|---|---|"
        };

        lines.AddRange(result.LaneClassification.Select(lane => $"| `{lane.Child}` | `{lane.Classification}` | {lane.Reason} |"));

        if (result.Warnings.Count > 0)
        {
            lines.Add("");
            lines.Add("Warnings:");
            lines.AddRange(result.Warnings.Select(w => $"- {w}"));
        }

        if (result.Errors.Count > 0)
        {
            lines.Add("");
            lines.Add("Errors:");
            lines.AddRange(result.Errors.Select(e => $"- {e}"));
        }

        return string.Join(Environment.NewLine, lines);
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
