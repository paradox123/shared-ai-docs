using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;
using System.Text.RegularExpressions;

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

if (options.Phase == "evidence-resolution")
{
    var resolver = new EvidenceResolution(options);
    var report = resolver.Run();
    Console.WriteLine(JsonSerializer.Serialize(report, JsonSupport.Options));
    return report.ExitCode;
}
else
{
    var doctor = new WorkflowDoctor(GetSourcePath());
    var report = await doctor.Run(options);
    Print(report, options.Format);
    return report.FinalExitCode;
}

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

sealed class EvidenceResolution(Options options)
{
    const string SchemaId = "agent-delivery.evidence-resolution.v1";
    static readonly HashSet<string> Modes = new(StringComparer.Ordinal)
    {
        "launcher_only",
        "controller_visible_multi_session",
        "closeout_archive"
    };

    public EvidenceResolutionReport Run()
    {
        if (!string.IsNullOrWhiteSpace(options.FixturePath))
        {
            return RunFixture(options.FixturePath!, options.SummaryOutPath);
        }

        var mode = options.EvidenceMode;
        if (string.IsNullOrWhiteSpace(mode) || !Modes.Contains(mode))
        {
            return Report("fail", mode ?? "", null, null, new(), new() { "evidence-resolution requires --mode launcher_only|controller_visible_multi_session|closeout_archive" }, new(), "Provide a supported --mode.", 2);
        }

        return mode switch
        {
            "launcher_only" => ResolveLauncherOnly(),
            "controller_visible_multi_session" => ResolveControllerVisibleRun(),
            "closeout_archive" => ResolveCloseoutArchive(),
            _ => Report("fail", mode, null, null, new(), new() { $"unsupported mode: {mode}" }, new(), "Choose a supported mode.", 2)
        };
    }

    EvidenceResolutionReport RunFixture(string fixturePath, string? summaryOutPath)
    {
        fixturePath = Path.GetFullPath(fixturePath);
        var manifestPath = Path.Combine(fixturePath, "fixture-manifest.json");
        if (!File.Exists(manifestPath))
        {
            return Report("fail", "fixture", null, fixturePath, new() { ["manifest"] = manifestPath }, new() { $"fixture manifest not found: {manifestPath}" }, new(), "Create fixture-manifest.json.", 2);
        }

        FixtureManifest manifest;
        try
        {
            manifest = JsonSerializer.Deserialize<FixtureManifest>(
                File.ReadAllText(manifestPath),
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true, TypeInfoResolver = new DefaultJsonTypeInfoResolver() })
                ?? new FixtureManifest();
        }
        catch (JsonException ex)
        {
            return Report("fail", "fixture", null, fixturePath, new() { ["manifest"] = manifestPath }, new() { $"fixture manifest is invalid JSON: {ex.Message}" }, new(), "Fix fixture-manifest.json.", 2);
        }

        if (manifest.Cases.Count == 0)
        {
            return Report("fail", "fixture", null, fixturePath, new() { ["manifest"] = manifestPath }, new() { "fixture manifest contains no cases" }, new(), "Add at least one fixture case.", 2);
        }

        var caseResults = new List<EvidenceFixtureCaseResult>();
        var blockers = new List<string>();
        foreach (var testCase in manifest.Cases)
        {
            var result = RunFixtureCase(fixturePath, testCase);
            caseResults.Add(result);
            if (!result.MatchesExpected)
            {
                blockers.Add($"{testCase.Id}: expected {testCase.Expect}, got {result.Report.Verdict}");
            }
        }

        var verdict = blockers.Count == 0 ? "pass" : "fail";
        var report = Report(
            verdict,
            "fixture",
            manifest.SchemaId,
            fixturePath,
            new() { ["manifest"] = manifestPath },
            blockers,
            new(),
            verdict == "pass" ? "Fixture replay passed." : "Inspect mismatched fixture cases.",
            verdict == "pass" ? 0 : 1);
        report.FixtureResults = caseResults;

        if (!string.IsNullOrWhiteSpace(summaryOutPath))
        {
            var full = Path.GetFullPath(summaryOutPath);
            Directory.CreateDirectory(Path.GetDirectoryName(full)!);
            report.EvidencePaths["summary_out"] = full;
            File.WriteAllText(full, JsonSerializer.Serialize(report, JsonSupport.IndentedOptions));
        }

        return report;
    }

    EvidenceFixtureCaseResult RunFixtureCase(string fixturePath, FixtureCase testCase)
    {
        var caseBase = string.IsNullOrWhiteSpace(testCase.Dir)
            ? fixturePath
            : ResolvePath(fixturePath, testCase.Dir!);

        var nestedOptions = options with
        {
            EvidenceMode = testCase.Mode,
            HandoffPath = ResolveOptional(caseBase, testCase.Handoff),
            LaunchRequestPath = ResolveOptional(caseBase, testCase.LaunchRequest),
            StartPromptPath = ResolveOptional(caseBase, testCase.StartPrompt),
            EvidencePath = ResolveOptional(caseBase, testCase.Evidence),
            ControllerRunPath = ResolveOptional(caseBase, testCase.ControllerRun),
            ControllerSummaryPath = ResolveOptional(caseBase, testCase.ControllerSummary),
            VisibleSessionSummaryPath = ResolveOptional(caseBase, testCase.VisibleSessionSummary),
            ArchiveSummaryPath = ResolveOptional(caseBase, testCase.ArchiveSummary),
            ClaimLevel = testCase.ClaimLevel ?? options.ClaimLevel,
            FixturePath = null,
            SummaryOutPath = null
        };
        var report = new EvidenceResolution(nestedOptions).Run();
        var matches = string.Equals(report.Verdict, testCase.Expect, StringComparison.Ordinal);
        if (!matches && testCase.Expect is "not_pass")
        {
            matches = report.Verdict is "not_ready" or "fail";
        }

        return new EvidenceFixtureCaseResult
        {
            Id = testCase.Id,
            Mode = testCase.Mode,
            Expected = testCase.Expect,
            Actual = report.Verdict,
            MatchesExpected = matches,
            Report = report
        };
    }

    EvidenceResolutionReport ResolveLauncherOnly()
    {
        var blockers = new List<string>();
        var warnings = new List<string>();
        var paths = new Dictionary<string, string?>();
        var mode = "launcher_only";
        var claim = options.ClaimLevel ?? "launched";

        var handoffPath = RequireExisting(options.HandoffPath, "handoff", blockers, paths);
        var evidencePath = RequireExisting(options.EvidencePath, "evidence", blockers, paths);
        var launchRequestPath = ExistingOrInferred(options.LaunchRequestPath, evidencePath, "launch-request.json", "launch_request", blockers, paths);
        var startPromptPath = ExistingOrInferred(options.StartPromptPath, evidencePath, "start-prompt.md", "start_prompt", blockers, paths);

        var handoffText = ReadText(handoffPath, blockers, "handoff");
        var evidence = ReadJson(evidencePath, blockers, "evidence");
        var launchRequest = ReadJson(launchRequestPath, blockers, "launch_request");
        var targetId = ExtractHandoffField(handoffText, "Target ID") ?? GetString(evidence, "target_id") ?? GetString(launchRequest, "target_id");

        if (evidence is not null || launchRequest is not null)
        {
            ValidateLauncherEvidence(handoffPath, handoffText, targetId, evidence, launchRequest, startPromptPath, claim, blockers, warnings);
        }

        var status = GetString(evidence, "status") ?? GetString(launchRequest, "status");
        var verdict = blockers.Count == 0 ? "pass" : IsUnsafeLauncherStatus(status) ? "fail" : "not_ready";
        return Report(verdict, mode, targetId, null, paths, blockers, warnings, verdict == "pass" ? "Evidence satisfies launcher-only claim." : "Resolve launcher evidence blockers before continuing.", verdict == "pass" ? 0 : 1);
    }

    EvidenceResolutionReport ResolveControllerVisibleRun()
    {
        var blockers = new List<string>();
        var warnings = new List<string>();
        var paths = new Dictionary<string, string?>();
        var runDir = RequireExistingDirectory(options.ControllerRunPath, "controller_run", blockers, paths);
        var summaryPath = ExistingOrInferred(options.ControllerSummaryPath, runDir, Path.Combine("controller", "controller-summary.json"), "controller_summary", blockers, paths);
        var visibleSummaryPath = ExistingOrInferred(options.VisibleSessionSummaryPath, runDir, "visible-session-summary.json", "visible_session_summary", blockers, paths, required: false);
        var summary = ReadJson(summaryPath, blockers, "controller_summary");
        var runId = runDir is null ? null : Path.GetFileName(runDir.TrimEnd(Path.DirectorySeparatorChar));

        if (summary is not null)
        {
            if (GetString(summary, "schema_id") != "agent-delivery.visible-session-controller.summary.v1")
            {
                blockers.Add("controller summary schema_id mismatch");
            }
            if (GetString(summary, "status") != "pass")
            {
                blockers.Add($"controller summary status is {GetString(summary, "status") ?? "<missing>"}");
            }

            var requestRecords = GetArray(summary, "requests").ToList();
            if (requestRecords.Count == 0)
            {
                blockers.Add("controller summary contains no requests");
            }

            var parentEvidence = GetString(summary, "parent", "evidence_path");
            if (!string.IsNullOrWhiteSpace(parentEvidence))
            {
                paths["parent_launcher_evidence"] = parentEvidence;
                ValidateLauncherEvidencePath(parentEvidence, expectedStatus: "launched", blockers, warnings);
            }
            else
            {
                blockers.Add("controller summary missing parent evidence path");
            }

            foreach (var request in requestRecords)
            {
                var requestId = GetString(request, "request_id") ?? "<unknown>";
                var requestPath = GetString(request, "request_path");
                var responsePath = GetString(request, "response_path");
                if (string.IsNullOrWhiteSpace(requestPath))
                {
                    blockers.Add($"{requestId}: missing request_path");
                }
                else
                {
                    paths[$"request:{requestId}"] = requestPath;
                }

                if (string.IsNullOrWhiteSpace(responsePath) || !File.Exists(ResolvePath(Directory.GetCurrentDirectory(), responsePath)))
                {
                    blockers.Add($"{requestId}: missing controller response");
                    continue;
                }

                paths[$"response:{requestId}"] = responsePath;
                var response = ReadJson(responsePath, blockers, $"{requestId} response");
                if (response is null) continue;
                if (GetString(response, "status") != "launched")
                {
                    blockers.Add($"{requestId}: response status is {GetString(response, "status") ?? "<missing>"}");
                }
                var launcherEvidence = GetString(response, "launcher", "evidence_path");
                if (string.IsNullOrWhiteSpace(launcherEvidence))
                {
                    blockers.Add($"{requestId}: response missing launcher.evidence_path");
                }
                else
                {
                    paths[$"launcher:{requestId}"] = launcherEvidence;
                    ValidateLauncherEvidencePath(launcherEvidence, expectedStatus: "launched", blockers, warnings);
                }
            }
        }

        if (string.IsNullOrWhiteSpace(visibleSummaryPath))
        {
            blockers.Add("visible-session summary path is required for controller-backed visible workflow evidence");
        }
        else
        {
            paths["visible_session_summary"] = visibleSummaryPath;
            if (!File.Exists(ResolvePath(Directory.GetCurrentDirectory(), visibleSummaryPath)))
            {
                blockers.Add($"visible-session summary not found: {visibleSummaryPath}");
            }
        }

        if (runDir is not null)
        {
            var parentStartedHits = FindParentStartedChildLaunches(runDir).ToList();
            if (parentStartedHits.Count > 0)
            {
                blockers.Add("parent-started child launches do not satisfy controller-backed gate: " + string.Join("; ", parentStartedHits.Take(3)));
            }
        }

        var verdict = blockers.Count == 0 ? "pass" : blockers.Any(b => b.Contains("parent-started", StringComparison.Ordinal)) ? "fail" : "not_ready";
        return Report(verdict, "controller_visible_multi_session", null, runId, paths, blockers, warnings, verdict == "pass" ? "Controller-backed visible evidence satisfies the gate." : "Resolve controller evidence blockers before claiming visible multi-session success.", verdict == "pass" ? 0 : 1);
    }

    EvidenceResolutionReport ResolveCloseoutArchive()
    {
        var blockers = new List<string>();
        var warnings = new List<string>();
        var paths = new Dictionary<string, string?>();
        var archivePath = RequireExisting(options.ArchiveSummaryPath, "archive_summary", blockers, paths);
        var summary = ReadJson(archivePath, blockers, "archive_summary");

        if (summary is not null)
        {
            if (GetString(summary, "schema_id") != "agent-delivery.visible-session-closeout-archive.v1")
            {
                blockers.Add("archive summary schema_id mismatch");
            }
            var overall = GetString(summary, "overall_archive_status");
            if (overall is not "READY" and not "READY_NO_SESSION_EVIDENCE")
            {
                blockers.Add($"archive summary overall_archive_status is {overall ?? "<missing>"}");
            }

            var records = GetArray(summary, "session_records").ToList();
            if (records.Count == 0)
            {
                blockers.Add("archive summary has no session_records");
            }
            for (var index = 0; index < records.Count; index++)
            {
                var record = records[index];
                var status = GetString(record, "archive_status");
                var visibility = GetString(record, "visibility_class");
                var threadId = GetString(record, "thread_id");
                var evidencePath = GetString(record, "evidence_path");
                if (!string.IsNullOrWhiteSpace(evidencePath))
                {
                    paths[$"session:{index}:evidence"] = evidencePath;
                    ValidateLauncherEvidencePath(evidencePath, null, blockers, warnings);
                }
                if (visibility is "visible_codex_app_session" or "manual_visible_start")
                {
                    if (string.IsNullOrWhiteSpace(threadId))
                    {
                        blockers.Add($"session {index}: manual-visible/visible record is missing thread_id");
                    }
                    if (status is not "archived" and not "already_archived" and not "retained_session_accepted")
                    {
                        blockers.Add($"session {index}: visible record archive_status {status ?? "<missing>"} is not accepted for closeout");
                    }
                }
                else if (status is "archive_failed" or "unarchived")
                {
                    blockers.Add($"session {index}: blocking archive_status {status}");
                }
            }
        }

        var verdict = blockers.Count == 0 ? "pass" : blockers.Any(b => b.Contains("archive_status", StringComparison.Ordinal) || b.Contains("missing thread_id", StringComparison.Ordinal)) ? "fail" : "not_ready";
        return Report(verdict, "closeout_archive", null, null, paths, blockers, warnings, verdict == "pass" ? "Closeout archive evidence satisfies the gate." : "Resolve archive closeout blockers before marking closeout ready.", verdict == "pass" ? 0 : 1);
    }

    static void ValidateLauncherEvidence(string? handoffPath, string? handoffText, string? targetId, JsonDocument? evidence, JsonDocument? launchRequest, string? startPromptPath, string claim, List<string> blockers, List<string> warnings)
    {
        var status = GetString(evidence, "status") ?? GetString(launchRequest, "status");
        if (status is null)
        {
            blockers.Add("launcher evidence missing status");
        }
        else if (status is "manual_start_required" or "blocked" or "failed")
        {
            blockers.Add($"launcher status {status} blocks the requested claim");
        }
        else if (claim is "launched" or "visible" or "closeout_archive")
        {
            if (status != "launched")
            {
                blockers.Add($"claim level {claim} requires launched status, got {status}");
            }
        }
        else if (claim == "queued")
        {
            if (status is not "queued" and not "launched")
            {
                blockers.Add($"claim level queued requires queued or launched status, got {status}");
            }
        }

        var evidenceTarget = GetString(evidence, "target_id") ?? GetString(launchRequest, "target_id");
        if (string.IsNullOrWhiteSpace(targetId))
        {
            blockers.Add("target id could not be inferred");
        }
        else if (!string.Equals(targetId, evidenceTarget, StringComparison.OrdinalIgnoreCase))
        {
            blockers.Add($"target_id mismatch: expected {targetId}, evidence {evidenceTarget ?? "<missing>"}");
        }

        var evidenceHandoff = GetString(evidence, "handoff_path") ?? GetString(launchRequest, "handoff_path");
        if (!string.IsNullOrWhiteSpace(handoffPath))
        {
            if (string.IsNullOrWhiteSpace(evidenceHandoff))
            {
                blockers.Add("launcher evidence missing handoff_path");
            }
            else if (!SamePath(handoffPath, evidenceHandoff))
            {
                blockers.Add($"handoff_path mismatch: expected {handoffPath}, evidence {evidenceHandoff}");
            }
        }

        if (string.IsNullOrWhiteSpace(startPromptPath) || !File.Exists(ResolvePath(Directory.GetCurrentDirectory(), startPromptPath)))
        {
            blockers.Add("start-prompt.md is required and must exist");
        }

        if (string.IsNullOrWhiteSpace(GetString(evidence, "agent", "requested_provider") ?? GetString(launchRequest, "agent", "requested_provider")))
        {
            blockers.Add("launcher evidence missing agent.requested_provider");
        }
        if (string.IsNullOrWhiteSpace(GetString(evidence, "agent", "adapter_status") ?? GetString(launchRequest, "agent", "adapter_status")))
        {
            blockers.Add("launcher evidence missing agent.adapter_status");
        }

        if (!string.IsNullOrWhiteSpace(handoffText) && handoffText.Contains("SessionId:", StringComparison.OrdinalIgnoreCase) && evidence is null && launchRequest is null)
        {
            warnings.Add("semantic-only SessionId requires launcher evidence before it proves a fresh session transition");
        }
    }

    void ValidateLauncherEvidencePath(string evidencePath, string? expectedStatus, List<string> blockers, List<string> warnings)
    {
        var full = ResolvePath(Directory.GetCurrentDirectory(), evidencePath);
        if (!File.Exists(full))
        {
            blockers.Add($"launcher evidence not found: {evidencePath}");
            return;
        }
        var evidence = ReadJson(evidencePath, blockers, "launcher evidence");
        if (evidence is null) return;
        var status = GetString(evidence, "status");
        if (expectedStatus is not null && status != expectedStatus)
        {
            blockers.Add($"launcher evidence {evidencePath} status is {status ?? "<missing>"}, expected {expectedStatus}");
        }
        if (status is "manual_start_required" or "blocked" or "failed")
        {
            blockers.Add($"launcher evidence {evidencePath} status {status} blocks success");
        }
        if (GetString(evidence, "schema_version") != "agent-delivery.session-launch.v2")
        {
            warnings.Add($"launcher evidence {evidencePath} has unexpected schema_version {GetString(evidence, "schema_version") ?? "<missing>"}");
        }
    }

    IEnumerable<string> FindParentStartedChildLaunches(string runDir)
    {
        var summaryPath = Path.Combine(runDir, "controller", "controller-summary.json");
        var parentEvidence = ReadJson(summaryPath, new(), "controller_summary") is { } summary
            ? GetString(summary, "parent", "evidence_path")
            : null;
        if (string.IsNullOrWhiteSpace(parentEvidence)) yield break;
        var parentEvidenceDir = Path.GetDirectoryName(ResolvePath(Directory.GetCurrentDirectory(), parentEvidence));
        if (string.IsNullOrWhiteSpace(parentEvidenceDir)) yield break;
        var events = Path.Combine(parentEvidenceDir, "agent-events.jsonl");
        if (!File.Exists(events)) yield break;
        foreach (var line in File.ReadLines(events))
        {
            if (line.Contains("AgentDeliverySessionLauncher.cs", StringComparison.OrdinalIgnoreCase) ||
                line.Contains("codex app-server", StringComparison.OrdinalIgnoreCase))
            {
                yield return events;
                yield break;
            }
        }
    }

    static string? RequireExisting(string? path, string key, List<string> blockers, Dictionary<string, string?> paths)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            blockers.Add($"{key} path is required");
            return null;
        }
        paths[key] = path;
        if (!File.Exists(ResolvePath(Directory.GetCurrentDirectory(), path)))
        {
            blockers.Add($"{key} not found: {path}");
        }
        return path;
    }

    static string? RequireExistingDirectory(string? path, string key, List<string> blockers, Dictionary<string, string?> paths)
    {
        if (string.IsNullOrWhiteSpace(path))
        {
            blockers.Add($"{key} path is required");
            return null;
        }
        paths[key] = path;
        if (!Directory.Exists(ResolvePath(Directory.GetCurrentDirectory(), path)))
        {
            blockers.Add($"{key} directory not found: {path}");
        }
        return path;
    }

    static string? ExistingOrInferred(string? explicitPath, string? basePath, string fileName, string key, List<string> blockers, Dictionary<string, string?> paths, bool required = true)
    {
        var candidate = explicitPath;
        if (string.IsNullOrWhiteSpace(candidate) && !string.IsNullOrWhiteSpace(basePath))
        {
            var fullBase = ResolvePath(Directory.GetCurrentDirectory(), basePath);
            var dir = Directory.Exists(fullBase) ? fullBase : Path.GetDirectoryName(fullBase);
            if (!string.IsNullOrWhiteSpace(dir))
            {
                candidate = Path.Combine(dir, fileName);
            }
        }

        if (string.IsNullOrWhiteSpace(candidate))
        {
            if (required) blockers.Add($"{key} path is required");
            return null;
        }

        paths[key] = candidate;
        if (!File.Exists(ResolvePath(Directory.GetCurrentDirectory(), candidate)))
        {
            if (required) blockers.Add($"{key} not found: {candidate}");
            return candidate;
        }
        return candidate;
    }

    static string? ResolveOptional(string baseDir, string? path) => string.IsNullOrWhiteSpace(path) ? null : ResolvePath(baseDir, path);

    static string? ReadText(string? path, List<string> blockers, string label)
    {
        if (string.IsNullOrWhiteSpace(path)) return null;
        var full = ResolvePath(Directory.GetCurrentDirectory(), path);
        if (!File.Exists(full)) return null;
        try { return File.ReadAllText(full); }
        catch (IOException ex) { blockers.Add($"{label} could not be read: {ex.Message}"); return null; }
    }

    static JsonDocument? ReadJson(string? path, List<string> blockers, string label)
    {
        if (string.IsNullOrWhiteSpace(path)) return null;
        var full = ResolvePath(Directory.GetCurrentDirectory(), path);
        if (!File.Exists(full)) return null;
        try { return JsonDocument.Parse(File.ReadAllText(full)); }
        catch (JsonException ex) { blockers.Add($"{label} is invalid JSON: {ex.Message}"); return null; }
    }

    static string? ExtractHandoffField(string? text, string field)
    {
        if (string.IsNullOrWhiteSpace(text)) return null;
        var match = Regex.Match(text, @"(?im)^\s*[-*]\s*" + Regex.Escape(field) + @"\s*:\s*`?([^`\r\n]+)`?\s*$");
        return match.Success ? match.Groups[1].Value.Trim() : null;
    }

    static IEnumerable<JsonElement> GetArray(JsonDocument document, string property) =>
        document.RootElement.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Array
            ? value.EnumerateArray()
            : Enumerable.Empty<JsonElement>();

    static string? GetString(JsonDocument? document, params string[] path) =>
        document is null ? null : GetString(document.RootElement, path);

    static string? GetString(JsonElement element, params string[] path)
    {
        var current = element;
        foreach (var segment in path)
        {
            if (current.ValueKind != JsonValueKind.Object || !current.TryGetProperty(segment, out current))
            {
                return null;
            }
        }
        return current.ValueKind == JsonValueKind.String ? current.GetString() : current.ToString();
    }

    static bool SamePath(string expected, string actual) =>
        Path.GetFullPath(ResolvePath(Directory.GetCurrentDirectory(), expected))
            .Equals(Path.GetFullPath(ResolvePath(Directory.GetCurrentDirectory(), actual)), StringComparison.OrdinalIgnoreCase);

    static string ResolvePath(string baseDir, string path) =>
        Path.IsPathRooted(path) ? path : Path.GetFullPath(Path.Combine(baseDir, path));

    static bool IsUnsafeLauncherStatus(string? status) => status is "blocked" or "failed";

    static EvidenceResolutionReport Report(
        string verdict,
        string mode,
        string? targetId,
        string? runId,
        Dictionary<string, string?> evidencePaths,
        List<string> blockers,
        List<string> warnings,
        string recommendedNextAction,
        int exitCode) => new()
    {
        SchemaId = SchemaId,
        Verdict = verdict,
        Mode = mode,
        TargetId = targetId,
        RunId = runId,
        EvidencePaths = evidencePaths,
        Blockers = blockers,
        Warnings = warnings,
        RecommendedNextAction = recommendedNextAction,
        ExitCode = exitCode
    };
}

sealed record Options
{
    static readonly HashSet<string> Formats = new(StringComparer.Ordinal)
    {
        "json",
        "markdown",
        "both"
    };

    public string? Phase { get; init; }
    public string? PackPath { get; init; }
    public string? RepoPath { get; init; }
    public string? ChildIndexSection { get; init; } = "Child Index";
    public string? Intent { get; init; } = "unknown";
    public bool NoImplementation { get; init; }
    public bool FailOnRequiredNextStep { get; init; }
    public string Format { get; init; } = "both";
    public bool ShowHelp { get; init; }
    public bool ParseError { get; init; }
    public string? EvidenceMode { get; init; }
    public string? ClaimLevel { get; init; }
    public string? HandoffPath { get; init; }
    public string? LaunchRequestPath { get; init; }
    public string? StartPromptPath { get; init; }
    public string? EvidencePath { get; init; }
    public string? ControllerRunPath { get; init; }
    public string? ControllerSummaryPath { get; init; }
    public string? VisibleSessionSummaryPath { get; init; }
    public string? ArchiveSummaryPath { get; init; }
    public string? FixturePath { get; init; }
    public string? SummaryOutPath { get; init; }

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
        string? evidenceMode = null;
        string? claimLevel = null;
        string? handoffPath = null;
        string? launchRequestPath = null;
        string? startPromptPath = null;
        string? evidencePath = null;
        string? controllerRunPath = null;
        string? controllerSummaryPath = null;
        string? visibleSessionSummaryPath = null;
        string? archiveSummaryPath = null;
        string? fixturePath = null;
        string? summaryOutPath = null;
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
                case "--mode":
                    evidenceMode = RequireValue(args, ref i, "--mode", ref parseError);
                    break;
                case "--claim-level":
                    claimLevel = RequireValue(args, ref i, "--claim-level", ref parseError);
                    break;
                case "--handoff":
                    handoffPath = RequireValue(args, ref i, "--handoff", ref parseError);
                    break;
                case "--launch-request":
                    launchRequestPath = RequireValue(args, ref i, "--launch-request", ref parseError);
                    break;
                case "--start-prompt":
                    startPromptPath = RequireValue(args, ref i, "--start-prompt", ref parseError);
                    break;
                case "--evidence":
                    evidencePath = RequireValue(args, ref i, "--evidence", ref parseError);
                    break;
                case "--controller-run":
                    controllerRunPath = RequireValue(args, ref i, "--controller-run", ref parseError);
                    break;
                case "--controller-summary":
                    controllerSummaryPath = RequireValue(args, ref i, "--controller-summary", ref parseError);
                    break;
                case "--visible-session-summary":
                    visibleSessionSummaryPath = RequireValue(args, ref i, "--visible-session-summary", ref parseError);
                    break;
                case "--archive-summary":
                    archiveSummaryPath = RequireValue(args, ref i, "--archive-summary", ref parseError);
                    break;
                case "--fixture":
                    fixturePath = RequireValue(args, ref i, "--fixture", ref parseError);
                    break;
                case "--summary-out":
                    summaryOutPath = RequireValue(args, ref i, "--summary-out", ref parseError);
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
            EvidenceMode = evidenceMode,
            ClaimLevel = claimLevel,
            HandoffPath = handoffPath,
            LaunchRequestPath = launchRequestPath,
            StartPromptPath = startPromptPath,
            EvidencePath = evidencePath,
            ControllerRunPath = controllerRunPath,
            ControllerSummaryPath = controllerSummaryPath,
            VisibleSessionSummaryPath = visibleSessionSummaryPath,
            ArchiveSummaryPath = archiveSummaryPath,
            FixturePath = fixturePath,
            SummaryOutPath = summaryOutPath,
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
          dotnet run <path-to-WorkflowDoctor.cs> -- --phase evidence-resolution --mode <mode> [options]
          dotnet run <path-to-WorkflowDoctor.cs> -- --phase evidence-resolution --fixture <dir> [--summary-out <path>]

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

        Evidence-resolution options:
          --mode <launcher_only|controller_visible_multi_session|closeout_archive>
          --claim-level <queued|launched|visible|closeout_archive>
          --handoff <path>                Launcher-only handoff path.
          --launch-request <path>         Launcher-only launch-request.json.
          --start-prompt <path>           Launcher-only start-prompt.md.
          --evidence <path>               Launcher-only evidence.json.
          --controller-run <dir>          Controller-backed visible run directory.
          --controller-summary <path>     Controller summary override.
          --visible-session-summary <path>
          --archive-summary <path>        Closeout archive summary path.
          --fixture <dir>                 Replay resolver fixture manifest.
          --summary-out <path>            Persist fixture replay summary JSON.
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

sealed class EvidenceResolutionReport
{
    [JsonPropertyName("schema_id")]
    public required string SchemaId { get; init; }

    [JsonPropertyName("verdict")]
    public required string Verdict { get; init; }

    [JsonPropertyName("mode")]
    public required string Mode { get; init; }

    [JsonPropertyName("target_id")]
    public string? TargetId { get; init; }

    [JsonPropertyName("run_id")]
    public string? RunId { get; init; }

    [JsonPropertyName("evidence_paths")]
    public required Dictionary<string, string?> EvidencePaths { get; init; }

    [JsonPropertyName("blockers")]
    public required List<string> Blockers { get; init; }

    [JsonPropertyName("warnings")]
    public required List<string> Warnings { get; init; }

    [JsonPropertyName("recommended_next_action")]
    public required string RecommendedNextAction { get; init; }

    [JsonPropertyName("fixture_results")]
    public List<EvidenceFixtureCaseResult>? FixtureResults { get; set; }

    [JsonPropertyName("exit_code")]
    public required int ExitCode { get; init; }
}

sealed class EvidenceFixtureCaseResult
{
    [JsonPropertyName("id")]
    public required string Id { get; init; }

    [JsonPropertyName("mode")]
    public required string Mode { get; init; }

    [JsonPropertyName("expected")]
    public required string Expected { get; init; }

    [JsonPropertyName("actual")]
    public required string Actual { get; init; }

    [JsonPropertyName("matches_expected")]
    public required bool MatchesExpected { get; init; }

    [JsonPropertyName("report")]
    public required EvidenceResolutionReport Report { get; init; }
}

sealed class FixtureManifest
{
    [JsonPropertyName("schema_id")]
    public string SchemaId { get; init; } = "agent-delivery.evidence-resolution-fixtures.v1";

    [JsonPropertyName("cases")]
    public List<FixtureCase> Cases { get; init; } = new();
}

sealed class FixtureCase
{
    [JsonPropertyName("id")]
    public string Id { get; init; } = "";

    [JsonPropertyName("mode")]
    public string Mode { get; init; } = "";

    [JsonPropertyName("expect")]
    public string Expect { get; init; } = "pass";

    [JsonPropertyName("claim_level")]
    public string? ClaimLevel { get; init; }

    [JsonPropertyName("dir")]
    public string? Dir { get; init; }

    [JsonPropertyName("handoff")]
    public string? Handoff { get; init; }

    [JsonPropertyName("launch_request")]
    public string? LaunchRequest { get; init; }

    [JsonPropertyName("start_prompt")]
    public string? StartPrompt { get; init; }

    [JsonPropertyName("evidence")]
    public string? Evidence { get; init; }

    [JsonPropertyName("controller_run")]
    public string? ControllerRun { get; init; }

    [JsonPropertyName("controller_summary")]
    public string? ControllerSummary { get; init; }

    [JsonPropertyName("visible_session_summary")]
    public string? VisibleSessionSummary { get; init; }

    [JsonPropertyName("archive_summary")]
    public string? ArchiveSummary { get; init; }
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

    public static readonly JsonSerializerOptions IndentedOptions = new()
    {
        WriteIndented = true,
        TypeInfoResolver = new DefaultJsonTypeInfoResolver()
    };
}
