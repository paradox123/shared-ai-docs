using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;

#pragma warning disable IL2026, IL3050

var options = Options.Parse(args);
if (options.ShowHelp)
{
    Options.PrintUsage();
    return 0;
}

if (!options.IsValid)
{
    Options.PrintUsage();
    return 2;
}

var doctor = new WorkflowDoctor(GetSourcePath());
var report = await doctor.Run(options);
Print(report, options.Format);
return report.FinalExitCode;

static string GetSourcePath([CallerFilePath] string path = "") => path;

static void Print(DoctorReport report, string format)
{
    if (format is "json" or "both")
    {
        Console.WriteLine(JsonSerializer.Serialize(report, JsonSupport.Options));
    }

    if (format is "both")
    {
        Console.WriteLine();
    }

    if (format is "markdown" or "both")
    {
        Console.WriteLine(MarkdownSummary.Render(report));
    }
}

sealed class WorkflowDoctor(string sourcePath)
{
    public async Task<DoctorReport> Run(Options options)
    {
        var findings = new List<string>();
        var toolRuns = new List<ToolRun>();
        var finalExitCode = 0;

        if (options.Phase != "post-orchestration")
        {
            findings.Add($"Unsupported phase outside Slice A: {options.Phase}");
            finalExitCode = 2;
            return BuildReport(options, toolRuns, findings, finalExitCode, RecommendedNextAction.FromFindings(findings));
        }

        if (string.IsNullOrWhiteSpace(options.PackPath))
        {
            findings.Add("--phase post-orchestration requires --pack <path>.");
            finalExitCode = 2;
            return BuildReport(options, toolRuns, findings, finalExitCode, RecommendedNextAction.FromFindings(findings));
        }

        var toolsDir = Path.GetDirectoryName(Path.GetFullPath(sourcePath)) ?? Directory.GetCurrentDirectory();
        var evaluatorPath = Path.Combine(toolsDir, "EvaluateOrchestrationNextStep.cs");
        if (!File.Exists(evaluatorPath))
        {
            findings.Add($"missing-underlying-tool: EvaluateOrchestrationNextStep.cs was not found beside WorkflowDoctor.cs at {evaluatorPath}");
            finalExitCode = 2;
            return BuildReport(options, toolRuns, findings, finalExitCode, RecommendedNextAction.FromFindings(findings));
        }

        var evaluatorArgs = BuildEvaluatorArgs(evaluatorPath, options);
        var toolRun = await RunTool("EvaluateOrchestrationNextStep.cs", evaluatorArgs, Directory.GetCurrentDirectory());
        toolRuns.Add(toolRun);

        var recommended = RecommendedNextAction.FromToolRun(toolRun);
        finalExitCode = toolRun.ExitCode switch
        {
            0 => 0,
            1 => 1,
            _ => 2
        };

        if (toolRun.ExitCode == 1)
        {
            findings.Add("required-next-step: underlying evaluator reported a required next workflow step under --fail-on-required-next-step.");
        }
        else if (toolRun.ExitCode != 0)
        {
            findings.Add("underlying-tool-error: EvaluateOrchestrationNextStep.cs exited non-zero before producing a passing evaluation.");
        }

        if (toolRun.ParsedJson is null && toolRun.ExitCode is 0 or 1)
        {
            findings.Add("malformed-tool-output: EvaluateOrchestrationNextStep.cs did not emit parseable JSON.");
            finalExitCode = 2;
        }

        return BuildReport(options, toolRuns, findings, finalExitCode, recommended);
    }

    static List<string> BuildEvaluatorArgs(string evaluatorPath, Options options)
    {
        var args = new List<string>
        {
            "run",
            evaluatorPath,
            "--",
            "--pack",
            options.PackPath!
        };

        if (!string.IsNullOrWhiteSpace(options.RepoPath))
        {
            args.Add("--repo");
            args.Add(options.RepoPath!);
        }

        if (!string.IsNullOrWhiteSpace(options.ChildIndexSection))
        {
            args.Add("--child-index-section");
            args.Add(options.ChildIndexSection!);
        }

        if (!string.IsNullOrWhiteSpace(options.Intent))
        {
            args.Add("--intent");
            args.Add(options.Intent!);
        }

        if (options.NoImplementation)
        {
            args.Add("--no-implementation");
        }

        args.Add("--format");
        args.Add("json");

        if (options.FailOnRequiredNextStep)
        {
            args.Add("--fail-on-required-next-step");
        }

        return args;
    }

    static async Task<ToolRun> RunTool(string tool, IReadOnlyList<string> arguments, string workingDirectory)
    {
        using var process = new Process();
        process.StartInfo = new ProcessStartInfo("dotnet")
        {
            WorkingDirectory = workingDirectory,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };

        foreach (var argument in arguments)
        {
            process.StartInfo.ArgumentList.Add(argument);
        }

        var command = "dotnet " + string.Join(" ", arguments.Select(ShellQuote));
        process.Start();
        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        var stdout = await stdoutTask;
        var stderr = await stderrTask;
        var parsed = TryParseJson(stdout);

        return new ToolRun
        {
            Tool = tool,
            Command = command,
            ExitCode = process.ExitCode,
            Stdout = stdout,
            Stderr = stderr,
            ParsedJson = parsed,
            Status = process.ExitCode switch
            {
                0 => "pass",
                1 => "blocker",
                _ => "error"
            }
        };
    }

    static JsonElement? TryParseJson(string stdout)
    {
        if (string.IsNullOrWhiteSpace(stdout))
        {
            return null;
        }

        try
        {
            using var document = JsonDocument.Parse(stdout);
            return document.RootElement.Clone();
        }
        catch (JsonException)
        {
            return null;
        }
    }

    static string ShellQuote(string value)
    {
        if (value.Length == 0)
        {
            return "''";
        }

        return value.Any(char.IsWhiteSpace) ? "'" + value.Replace("'", "'\\''") + "'" : value;
    }

    static DoctorReport BuildReport(
        Options options,
        List<ToolRun> toolRuns,
        List<string> findings,
        int finalExitCode,
        RecommendedNextAction recommended) => new()
    {
        Phase = options.Phase!,
        Format = options.Format,
        PackPath = options.PackPath,
        RepoPath = options.RepoPath,
        FailOnRequiredNextStep = options.FailOnRequiredNextStep,
        ToolRuns = toolRuns,
        Findings = findings,
        RecommendedNextAction = recommended,
        FinalExitCode = finalExitCode
    };
}

sealed class Options
{
    static readonly HashSet<string> Formats = new(StringComparer.Ordinal)
    {
        "json",
        "markdown",
        "both"
    };

    public string? Phase { get; private init; }
    public string? PackPath { get; private init; }
    public string? RepoPath { get; private init; }
    public string? ChildIndexSection { get; private init; } = "Child Index";
    public string? Intent { get; private init; } = "unknown";
    public bool NoImplementation { get; private init; }
    public bool FailOnRequiredNextStep { get; private init; }
    public string Format { get; private init; } = "both";
    public bool ShowHelp { get; private init; }
    public bool ParseError { get; private init; }

    public bool IsValid =>
        !ParseError &&
        !string.IsNullOrWhiteSpace(Phase) &&
        Formats.Contains(Format);

    public static Options Parse(string[] args)
    {
        string? phase = null;
        string? pack = null;
        string? repo = null;
        var childIndexSection = "Child Index";
        var intent = "unknown";
        var noImplementation = false;
        var failOnRequiredNextStep = false;
        var format = "both";
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
                case "--phase":
                    phase = RequireValue(args, ref i, "--phase", ref parseError);
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
                case "--intent":
                    intent = RequireValue(args, ref i, "--intent", ref parseError);
                    break;
                case "--no-implementation":
                    noImplementation = true;
                    break;
                case "--fail-on-required-next-step":
                    failOnRequiredNextStep = true;
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
            Console.Error.WriteLine($"Unsupported --format value: {format}");
            parseError = true;
        }

        return new Options
        {
            Phase = phase,
            PackPath = pack,
            RepoPath = repo,
            ChildIndexSection = childIndexSection,
            Intent = intent,
            NoImplementation = noImplementation,
            FailOnRequiredNextStep = failOnRequiredNextStep,
            Format = format,
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
          dotnet run <path-to-WorkflowDoctor.cs> -- --phase post-orchestration --pack <orchestration-pack.md> [options]

        Slice A scope:
          Supports only --phase post-orchestration.
          Runs EvaluateOrchestrationNextStep.cs beside WorkflowDoctor.cs.
          Does not run orchestration pack validation, handoff sync, pre-delivery checks, skill integration, or agent launches.

        Options:
          --phase <value>                post-orchestration.
          --pack <path>                  Markdown file containing the Child Index. Required for post-orchestration.
          --repo <path>                  Repository root passed through to EvaluateOrchestrationNextStep.cs.
          --child-index-section <name>   Section heading passed through. Default: Child Index.
          --intent <value>               Intent passed through to EvaluateOrchestrationNextStep.cs. Default: unknown.
          --no-implementation            Passed through to EvaluateOrchestrationNextStep.cs.
          --fail-on-required-next-step   Pass through and exit 1 when a required next step is present.
          --format <json|markdown|both>  Output format. Default: both.
          --help                         Print this help and exit 0.

        Exit codes:
          0  Selected tools ran and no selected tool reported a blocker.
          1  Selected tools ran and reported a workflow blocker or required next action.
          2  Invalid doctor arguments, required files missing, missing underlying tool, unsupported phase, or malformed tool output.
        """);
    }
}

static class MarkdownSummary
{
    public static string Render(DoctorReport report)
    {
        var lines = new List<string>
        {
            "# Workflow Doctor",
            "",
            $"- Phase: {report.Phase}",
            $"- Final exit code: {report.FinalExitCode}",
            $"- Recommended next skill: {report.RecommendedNextAction.RequiredNextSkill ?? "unknown"}",
            $"- Final status token: {report.RecommendedNextAction.FinalStatusToken ?? "unknown"}"
        };

        if (!string.IsNullOrWhiteSpace(report.RecommendedNextAction.FirstUnblockedChild))
        {
            lines.Add($"- First unblocked child: {report.RecommendedNextAction.FirstUnblockedChild}");
        }

        if (report.ToolRuns.Count > 0)
        {
            lines.Add("");
            lines.Add("## Tool Runs");
            foreach (var run in report.ToolRuns)
            {
                lines.Add($"- {run.Tool}: {run.Status} (exit {run.ExitCode})");
            }
        }

        if (report.Findings.Count > 0)
        {
            lines.Add("");
            lines.Add("## Findings");
            foreach (var finding in report.Findings)
            {
                lines.Add($"- {finding}");
            }
        }

        return string.Join(Environment.NewLine, lines);
    }
}

sealed class DoctorReport
{
    [JsonPropertyName("schema")]
    public string Schema { get; init; } = "agent-delivery.workflow-doctor.v1";

    [JsonPropertyName("phase")]
    public required string Phase { get; init; }

    [JsonPropertyName("format")]
    public required string Format { get; init; }

    [JsonPropertyName("pack_path")]
    public required string? PackPath { get; init; }

    [JsonPropertyName("repo_path")]
    public required string? RepoPath { get; init; }

    [JsonPropertyName("fail_on_required_next_step")]
    public required bool FailOnRequiredNextStep { get; init; }

    [JsonPropertyName("tool_runs")]
    public required List<ToolRun> ToolRuns { get; init; }

    [JsonPropertyName("findings")]
    public required List<string> Findings { get; init; }

    [JsonPropertyName("recommended_next_action")]
    public required RecommendedNextAction RecommendedNextAction { get; init; }

    [JsonPropertyName("final_exit_code")]
    public required int FinalExitCode { get; init; }
}

sealed class ToolRun
{
    [JsonPropertyName("tool")]
    public required string Tool { get; init; }

    [JsonPropertyName("command")]
    public required string Command { get; init; }

    [JsonPropertyName("exit_code")]
    public required int ExitCode { get; init; }

    [JsonPropertyName("stdout")]
    public required string Stdout { get; init; }

    [JsonPropertyName("stderr")]
    public required string Stderr { get; init; }

    [JsonPropertyName("parsed_json")]
    public required JsonElement? ParsedJson { get; init; }

    [JsonPropertyName("status")]
    public required string Status { get; init; }
}

sealed class RecommendedNextAction
{
    [JsonPropertyName("required_next_skill")]
    public string? RequiredNextSkill { get; init; }

    [JsonPropertyName("first_unblocked_child")]
    public string? FirstUnblockedChild { get; init; }

    [JsonPropertyName("delivery_allowed")]
    public bool? DeliveryAllowed { get; init; }

    [JsonPropertyName("trigger_result")]
    public string? TriggerResult { get; init; }

    [JsonPropertyName("final_status_token")]
    public string? FinalStatusToken { get; init; }

    [JsonPropertyName("message")]
    public string? Message { get; init; }

    public static RecommendedNextAction FromFindings(IReadOnlyList<string> findings) => new()
    {
        RequiredNextSkill = "none",
        FinalStatusToken = "doctor_blocked",
        Message = string.Join(" ", findings)
    };

    public static RecommendedNextAction FromToolRun(ToolRun run)
    {
        if (run.ParsedJson is not { ValueKind: JsonValueKind.Object } parsed)
        {
            return new RecommendedNextAction
            {
                RequiredNextSkill = "unknown",
                FinalStatusToken = "tool_output_unparsed",
                Message = "Underlying tool output was not parseable JSON."
            };
        }

        return new RecommendedNextAction
        {
            RequiredNextSkill = GetString(parsed, "required_next_skill"),
            FirstUnblockedChild = GetString(parsed, "first_unblocked_child"),
            DeliveryAllowed = GetBool(parsed, "delivery_allowed"),
            TriggerResult = GetString(parsed, "trigger_result"),
            FinalStatusToken = GetString(parsed, "final_status_token")
        };
    }

    static string? GetString(JsonElement element, string propertyName) =>
        element.TryGetProperty(propertyName, out var property) && property.ValueKind != JsonValueKind.Null
            ? property.GetString()
            : null;

    static bool? GetBool(JsonElement element, string propertyName) =>
        element.TryGetProperty(propertyName, out var property) && property.ValueKind is JsonValueKind.True or JsonValueKind.False
            ? property.GetBoolean()
            : null;
}

static class JsonSupport
{
    public static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = false,
        TypeInfoResolver = new DefaultJsonTypeInfoResolver()
    };
}
