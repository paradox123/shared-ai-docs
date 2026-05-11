using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
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

var controller = new VisibleSessionController(options);
var result = options.FixtureRoot is not null
    ? await controller.RunFixtureSuiteAsync()
    : await controller.RunLiveAsync();
return result;

sealed class VisibleSessionController
{
    private const string RequestSchema = "agent-delivery.visible-session-controller.request.v1";
    private const string ResponseSchema = "agent-delivery.visible-session-controller.response.v1";
    private const string SummarySchema = "agent-delivery.visible-session-controller.summary.v1";
    private readonly Options options;

    public VisibleSessionController(Options options)
    {
        this.options = options;
    }

    public async Task<int> RunLiveAsync()
    {
        var runDir = Full(options.RunDir!);
        Directory.CreateDirectory(runDir);
        var launcher = new ProcessLauncher(options);
        var result = await RunCoreAsync(runDir, launcher, liveMode: true);
        Console.WriteLine($"{result.SummaryStatus}: {Path.Combine(runDir, "controller", "controller-summary.json")}");
        return result.ExitCode;
    }

    public async Task<int> RunFixtureSuiteAsync()
    {
        var fixtureRoot = Full(options.FixtureRoot!);
        var manifestPath = Path.Combine(fixtureRoot, "fixture-manifest.json");
        if (!File.Exists(manifestPath))
        {
            Console.Error.WriteLine($"Fixture manifest not found: {manifestPath}");
            return 2;
        }

        var manifest = JsonNode.Parse(await File.ReadAllTextAsync(manifestPath))!.AsObject();
        if (manifest["schema_id"]?.GetValue<string>() != "agent-delivery.visible-session-controller.fixture-manifest.v1")
        {
            Console.Error.WriteLine("Fixture manifest schema_id mismatch.");
            return 2;
        }

        var failures = new List<string>();
        foreach (var entry in manifest["cases"]!.AsArray())
        {
            var item = entry!.AsObject();
            var id = item["id"]!.GetValue<string>();
            var expectedExit = item["expected_exit_code"]!.GetValue<int>();
            var expectedSummary = item["expected_summary_status"]!.GetValue<string>();
            var expectedResponse = item["expected_response_status"]?.GetValue<string>();
            var expectedResponseCount = item["expected_response_count"]?.GetValue<int>();
            var caseRoot = Path.Combine(fixtureRoot, id);
            var tempRun = Path.Combine(Path.GetTempPath(), "visible-session-controller-fixture", $"{DateTimeOffset.UtcNow:yyyyMMddTHHmmssfffZ}-{Slug(id)}");

            CopyDirectory(caseRoot, tempRun);
            ReplaceRunDirTokens(tempRun);
            var launcher = new FixtureLauncher(tempRun);
            var result = await RunCoreAsync(tempRun, launcher, liveMode: false);
            var summaryPath = Path.Combine(tempRun, "controller", "controller-summary.json");
            var summary = JsonNode.Parse(await File.ReadAllTextAsync(summaryPath))!.AsObject();
            var actualSummary = summary["status"]!.GetValue<string>();
            var responseStatus = ReadFirstResponseStatus(Path.Combine(tempRun, "controller", "responses"));
            var responseCount = CountResponses(Path.Combine(tempRun, "controller", "responses"));

            if (result.ExitCode != expectedExit)
            {
                failures.Add($"{id}: expected exit {expectedExit}, got {result.ExitCode}");
            }
            if (actualSummary != expectedSummary)
            {
                failures.Add($"{id}: expected summary {expectedSummary}, got {actualSummary}");
            }
            if (expectedResponse is not null && responseStatus != expectedResponse)
            {
                failures.Add($"{id}: expected response {expectedResponse}, got {responseStatus ?? "<none>"}");
            }
            if (expectedResponse is null && responseStatus is not null)
            {
                failures.Add($"{id}: expected no response, got {responseStatus}");
            }
            if (expectedResponseCount is not null && responseCount != expectedResponseCount)
            {
                failures.Add($"{id}: expected {expectedResponseCount} response(s), got {responseCount}");
            }

            Console.WriteLine($"{(failures.Count == 0 ? "PASS" : "CHECK")} {id}: exit={result.ExitCode} summary={actualSummary} response={responseStatus ?? "<none>"}");
        }

        if (failures.Count > 0)
        {
            Console.Error.WriteLine(string.Join(Environment.NewLine, failures));
            return 1;
        }

        Console.WriteLine($"RESULT: PASS ({manifest["cases"]!.AsArray().Count} controller fixture cases)");
        return 0;
    }

    private async Task<ControllerRunResult> RunCoreAsync(string runDir, ILauncher launcher, bool liveMode)
    {
        var startedAt = DateTimeOffset.UtcNow;
        var states = new List<StateRecord>();
        var blockers = new List<string>();
        var warnings = new List<string>();
        var requests = new List<Dictionary<string, object?>>();
        ParentSummary? parentSummary = null;
        var responseStatus = "";
        var summaryStatus = "failed";
        var exitCode = 1;

        Directory.CreateDirectory(Path.Combine(runDir, "controller", "requests"));
        Directory.CreateDirectory(Path.Combine(runDir, "controller", "responses"));
        Directory.CreateDirectory(Path.Combine(runDir, "launches", "parent"));
        Directory.CreateDirectory(Path.Combine(runDir, "launches", "children"));

        using (EnterState(states, "initialized"))
        {
            if (liveMode && !IsBelow(Full(runDir), Full(Path.Combine(Directory.GetCurrentDirectory(), "tests", "docworkflow-agent-delivery", "e2e", "session-workflow-live"))))
            {
                blockers.Add("Live run-dir must resolve below tests/docworkflow-agent-delivery/e2e/session-workflow-live.");
                summaryStatus = "setup_error";
                exitCode = 2;
            }
        }

        if (blockers.Count == 0)
        {
            LauncherResult parent;
            using (EnterState(states, "parent_launching"))
            {
                parent = await launcher.LaunchParentAsync(runDir);
            }
            parentSummary = new ParentSummary(ExpectedParentTargetId(), parent.ExitCode, parent.EvidencePath, parent.Status);
            if (parent.Status != "launched")
            {
                summaryStatus = parent.Status == "blocked" ? "blocked" : "failed";
                exitCode = 1;
                blockers.Add($"Parent launch did not produce launched evidence: {parent.Status}.");
            }
        }

        var processedRequests = new HashSet<string>(StringComparer.Ordinal);
        var expectedChildren = options.ExpectedChildTargetIds.Count > 0
            ? options.ExpectedChildTargetIds
            : [""];
        if (blockers.Count == 0)
        {
            foreach (var expectedChild in expectedChildren)
            {
                RequestValidation? validation = null;
                string? requestPath;
                using (EnterState(states, "waiting_for_request"))
                {
                    requestPath = await WaitForRequestAsync(
                        Path.Combine(runDir, "controller", "requests"),
                        liveMode ? options.RequestTimeoutSeconds : 1,
                        liveMode ? options.PollIntervalMs : 50,
                        processedRequests,
                        expectedChild);
                }

                if (requestPath is null)
                {
                    summaryStatus = "timeout";
                    exitCode = 1;
                    blockers.Add(string.IsNullOrWhiteSpace(expectedChild)
                        ? $"No child request appeared before {options.RequestTimeoutSeconds} seconds."
                        : $"No child request for {expectedChild} appeared before {options.RequestTimeoutSeconds} seconds.");
                    break;
                }

                processedRequests.Add(requestPath);
                using (EnterState(states, "validating_request"))
                {
                    validation = await ValidateRequestAsync(requestPath, runDir, expectedChild);
                }

                if (!validation.Valid)
                {
                    responseStatus = "rejected";
                    summaryStatus = "setup_error";
                    exitCode = 2;
                    blockers.AddRange(validation.Blockers);
                    await WriteResponseAsync(runDir, validation, null, null, "rejected", "not_checked", blockers, warnings);
                    requests.Add(RequestSummary(validation, "rejected", runDir));
                    break;
                }

                LauncherResult child;
                using (EnterState(states, "child_launching"))
                {
                    child = await launcher.LaunchChildAsync(runDir, validation.Request!);
                }

                using (EnterState(states, "validating_child_result"))
                {
                    var assertion = ValidateOutput(validation.Request!, runDir);
                    responseStatus = DetermineResponseStatus(child, assertion.Status);
                    requests.Add(RequestSummary(validation, responseStatus, runDir));
                    await WriteResponseAsync(runDir, validation, child, assertion, responseStatus, assertion.Status, blockers, warnings);

                    if (responseStatus != "launched")
                    {
                        summaryStatus = responseStatus switch
                        {
                            "blocked" => "blocked",
                            "timeout" => "timeout",
                            _ => "failed",
                        };
                        exitCode = 1;
                        blockers.Add($"Child result did not satisfy launched+output contract: target={validation.RequestId}, launcher={child.Status}, output={assertion.Status}.");
                        break;
                    }

                    summaryStatus = "pass";
                    exitCode = 0;
                }
            }
        }

        var writingSummary = new StateRecord("writing_summary", DateTimeOffset.UtcNow);
        states.Add(writingSummary);
        writingSummary.Complete();
        try
        {
            await WriteSummaryAsync(
                runDir,
                summaryStatus,
                startedAt,
                DateTimeOffset.UtcNow,
                states,
                parentSummary,
                requests,
                blockers,
                warnings);
            if (!string.IsNullOrWhiteSpace(options.SummaryOut))
            {
                var summaryOut = Path.GetFullPath(options.SummaryOut);
                Directory.CreateDirectory(Path.GetDirectoryName(summaryOut)!);
                File.Copy(Path.Combine(runDir, "controller", "controller-summary.json"), summaryOut, overwrite: true);
            }
        }
        catch
        {
            writingSummary.MarkFailed();
            throw;
        }

        return new ControllerRunResult(exitCode, summaryStatus);
    }

    private async Task<RequestValidation> ValidateRequestAsync(string requestPath, string runDir, string expectedChildTargetId)
    {
        var blockers = new List<string>();
        var bytes = await File.ReadAllBytesAsync(requestPath);
        var sha = Sha256(bytes);
        var requestId = RequestIdFromFile(requestPath);
        JsonObject? request = null;

        try
        {
            request = JsonNode.Parse(bytes)!.AsObject();
            requestId = request["request_id"]?.GetValue<string>() ?? requestId;
        }
        catch
        {
            blockers.Add("Request JSON is malformed.");
            return new RequestValidation(false, requestPath, requestId, sha, null, blockers);
        }

        string? GetString(params string[] path)
        {
            JsonNode? node = request;
            foreach (var segment in path)
            {
                node = node?[segment];
            }
            return node?.GetValue<string>();
        }

        var childId = GetString("child", "target_id");
        if (!string.IsNullOrWhiteSpace(expectedChildTargetId) && requestId != expectedChildTargetId)
        {
            blockers.Add($"request_id must be {expectedChildTargetId}.");
        }
        if (GetString("schema_id") != RequestSchema) blockers.Add("schema_id mismatch.");
        if (string.IsNullOrWhiteSpace(requestId) || requestId != childId) blockers.Add("request_id must equal child.target_id.");
        if (GetString("requested_by", "target_id") != ExpectedParentTargetId()) blockers.Add("requested_by.target_id mismatch.");
        if (GetString("launch", "agent") != "codex") blockers.Add("launch.agent must be codex.");
        if (GetString("launch", "adapter") != "codex-app-server") blockers.Add("launch.adapter must be codex-app-server.");
        if (GetString("launch", "mode") != "launch") blockers.Add("launch.mode must be launch.");
        var expectedCwd = options.InitiatingProjectCwd ?? Directory.GetCurrentDirectory();
        if (!SamePath(GetString("launch", "initiating_project_cwd") ?? "", expectedCwd)) blockers.Add("launch.initiating_project_cwd mismatch.");

        foreach (var (label, raw) in new[]
        {
            ("child.handoff_path", GetString("child", "handoff_path")),
            ("child.expected_output_path", GetString("child", "expected_output_path")),
            ("launch.out", GetString("launch", "out")),
        })
        {
            if (string.IsNullOrWhiteSpace(raw))
            {
                blockers.Add($"{label} is missing.");
                continue;
            }
            if (!IsBelow(ResolvePath(raw!, runDir), Full(runDir)))
            {
                blockers.Add($"{label} must resolve below run-dir.");
            }
        }

        return new RequestValidation(blockers.Count == 0, requestPath, requestId, sha, request, blockers);
    }

    private static OutputAssertion ValidateOutput(JsonObject request, string runDir)
    {
        var rawPath = request["child"]?["expected_output_path"]?.GetValue<string>() ?? "";
        var expected = request["child"]?["expected_output_text"]?.GetValue<string>() ?? "";
        var path = ResolvePath(rawPath, runDir);
        if (!File.Exists(path))
        {
            return new OutputAssertion(RelativeOrFull(path), expected, null, "missing");
        }

        var actual = File.ReadAllText(path, TextEncoding.Utf8NoBom);
        return new OutputAssertion(RelativeOrFull(path), expected, Sha256(Encoding.UTF8.GetBytes(actual)), actual == expected ? "pass" : "fail");
    }

    private string ExpectedParentTargetId()
    {
        if (!string.IsNullOrWhiteSpace(options.ParentTargetId)) return options.ParentTargetId;
        return options.ExpectedChildTargetIds.Any(id => id.StartsWith("RSW-", StringComparison.Ordinal)) ? "RSW-PARENT" : "CTRL-PARENT";
    }

    private static string DetermineResponseStatus(LauncherResult launcher, string outputStatus)
    {
        if (launcher.TimedOut) return "timeout";
        if (launcher.Status == "blocked") return "blocked";
        if (launcher.Status == "launched" && outputStatus == "pass") return "launched";
        return "failed";
    }

    private async Task WriteResponseAsync(
        string runDir,
        RequestValidation validation,
        LauncherResult? launcher,
        OutputAssertion? assertion,
        string status,
        string assertionStatus,
        List<string> blockers,
        List<string> warnings)
    {
        var responsePath = Path.Combine(runDir, "controller", "responses", $"{(string.IsNullOrWhiteSpace(validation.RequestId) ? "unknown" : validation.RequestId)}.response.json");
        var response = new Dictionary<string, object?>
        {
            ["schema_id"] = ResponseSchema,
            ["request_id"] = string.IsNullOrWhiteSpace(validation.RequestId) ? "unknown" : validation.RequestId,
            ["request_sha256"] = validation.RequestSha256,
            ["status"] = status,
            ["created_at"] = DateTimeOffset.UtcNow.ToString("O"),
            ["completed_at"] = DateTimeOffset.UtcNow.ToString("O"),
            ["launcher"] = launcher is null ? null : new Dictionary<string, object?>
            {
                ["command"] = launcher.Command is null ? null : string.Join(" ", launcher.Command.Select(ShellQuote)),
                ["exit_code"] = launcher.ExitCode,
                ["run_dir"] = RelativeOrFull(launcher.RunDir),
                ["evidence_path"] = launcher.EvidencePath is null ? null : RelativeOrFull(launcher.EvidencePath),
                ["transcript_path"] = launcher.TranscriptPath is null ? null : RelativeOrFull(launcher.TranscriptPath),
                ["stderr_path"] = launcher.StderrPath is null ? null : RelativeOrFull(launcher.StderrPath),
            },
            ["output_assertion"] = assertion is null
                ? new Dictionary<string, object?>
                {
                    ["path"] = validation.Request?["child"]?["expected_output_path"]?.GetValue<string>(),
                    ["expected_text"] = validation.Request?["child"]?["expected_output_text"]?.GetValue<string>(),
                    ["actual_text_sha256"] = null,
                    ["status"] = assertionStatus,
                }
                : new Dictionary<string, object?>
                {
                    ["path"] = assertion.Path,
                    ["expected_text"] = assertion.ExpectedText,
                    ["actual_text_sha256"] = assertion.ActualTextSha256,
                    ["status"] = assertion.Status,
                },
            ["blockers"] = blockers,
            ["warnings"] = warnings,
        };

        await WriteJsonAsync(responsePath, response);
    }

    private static async Task WriteSummaryAsync(
        string runDir,
        string status,
        DateTimeOffset startedAt,
        DateTimeOffset completedAt,
        List<StateRecord> states,
        ParentSummary? parent,
        List<Dictionary<string, object?>> requests,
        List<string> blockers,
        List<string> warnings)
    {
        var summary = new Dictionary<string, object?>
        {
            ["schema_id"] = SummarySchema,
            ["run_dir"] = RelativeOrFull(runDir),
            ["status"] = status,
            ["started_at"] = startedAt.ToString("O"),
            ["completed_at"] = completedAt.ToString("O"),
            ["states"] = states.Select(s => new Dictionary<string, object?>
            {
                ["state"] = s.State,
                ["entered_at"] = s.EnteredAt.ToString("O"),
                ["exited_at"] = s.ExitedAt?.ToString("O"),
                ["status"] = s.Status,
            }).ToArray(),
            ["parent"] = parent is null ? null : new Dictionary<string, object?>
            {
                ["target_id"] = parent.TargetId,
                ["launcher_exit_code"] = parent.LauncherExitCode,
                ["evidence_path"] = parent.EvidencePath is null ? null : RelativeOrFull(parent.EvidencePath),
                ["status"] = parent.Status,
            },
            ["requests"] = requests,
            ["blockers"] = blockers,
            ["warnings"] = warnings,
        };

        await WriteJsonAsync(Path.Combine(runDir, "controller", "controller-summary.json"), summary);
    }

    private static Dictionary<string, object?> RequestSummary(RequestValidation validation, string status, string runDir)
    {
        var responsePath = Path.Combine(runDir, "controller", "responses", $"{(string.IsNullOrWhiteSpace(validation.RequestId) ? "unknown" : validation.RequestId)}.response.json");
        return new Dictionary<string, object?>
        {
            ["request_id"] = string.IsNullOrWhiteSpace(validation.RequestId) ? "unknown" : validation.RequestId,
            ["request_path"] = RelativeOrFull(validation.RequestPath),
            ["response_path"] = RelativeOrFull(responsePath),
            ["status"] = status,
        };
    }

    private static IDisposable EnterState(List<StateRecord> states, string state)
    {
        var record = new StateRecord(state, DateTimeOffset.UtcNow);
        states.Add(record);
        return new StateScope(record);
    }

    private static async Task<string?> WaitForRequestAsync(string requestDir, int timeoutSeconds, int pollIntervalMs, HashSet<string> processedRequests, string expectedChildTargetId)
    {
        var deadline = DateTimeOffset.UtcNow.AddSeconds(timeoutSeconds);
        while (DateTimeOffset.UtcNow < deadline)
        {
            var files = Directory.Exists(requestDir)
                ? Directory.GetFiles(requestDir, "*.request.json").OrderBy(f => f, StringComparer.Ordinal).ToArray()
                : [];
            var candidates = files
                .Where(file => !processedRequests.Contains(file))
                .Where(file => string.IsNullOrWhiteSpace(expectedChildTargetId) || RequestIdFromFile(file) == expectedChildTargetId)
                .ToArray();
            if (candidates.Length > 0)
            {
                return candidates[0];
            }
            await Task.Delay(pollIntervalMs);
        }
        return null;
    }

    private static string? ReadFirstResponseStatus(string responseDir)
    {
        if (!Directory.Exists(responseDir)) return null;
        var file = Directory.GetFiles(responseDir, "*.response.json").OrderBy(f => f, StringComparer.Ordinal).FirstOrDefault();
        if (file is null) return null;
        return JsonNode.Parse(File.ReadAllText(file))?["status"]?.GetValue<string>();
    }

    private static int CountResponses(string responseDir)
    {
        return Directory.Exists(responseDir) ? Directory.GetFiles(responseDir, "*.response.json").Length : 0;
    }

    private static void CopyDirectory(string source, string target)
    {
        Directory.CreateDirectory(target);
        foreach (var dir in Directory.GetDirectories(source, "*", SearchOption.AllDirectories))
        {
            Directory.CreateDirectory(dir.Replace(source, target, StringComparison.Ordinal));
        }
        foreach (var file in Directory.GetFiles(source, "*", SearchOption.AllDirectories))
        {
            File.Copy(file, file.Replace(source, target, StringComparison.Ordinal), overwrite: true);
        }
    }

    private static void ReplaceRunDirTokens(string runDir)
    {
        foreach (var file in Directory.GetFiles(runDir, "*", SearchOption.AllDirectories))
        {
            var text = File.ReadAllText(file, TextEncoding.Utf8NoBom);
            if (!text.Contains("<RUN_DIR>", StringComparison.Ordinal))
            {
                continue;
            }
            File.WriteAllText(file, text.Replace("<RUN_DIR>", runDir, StringComparison.Ordinal), TextEncoding.Utf8NoBom);
        }
    }

    public static string Full(string path) => Path.GetFullPath(path);
    public static string ResolvePath(string path, string runDir) => Path.IsPathRooted(path) ? Full(path) : Full(Path.Combine(Directory.GetCurrentDirectory(), path));
    public static bool SamePath(string left, string right) => !string.IsNullOrWhiteSpace(left) && !string.IsNullOrWhiteSpace(right) && string.Equals(Full(left).TrimEnd(Path.DirectorySeparatorChar), Full(right).TrimEnd(Path.DirectorySeparatorChar), StringComparison.Ordinal);
    public static bool IsBelow(string path, string root)
    {
        var full = Full(path).TrimEnd(Path.DirectorySeparatorChar);
        var fullRoot = Full(root).TrimEnd(Path.DirectorySeparatorChar);
        return string.Equals(full, fullRoot, StringComparison.Ordinal) || full.StartsWith(fullRoot + Path.DirectorySeparatorChar, StringComparison.Ordinal);
    }
    public static string RelativeOrFull(string path)
    {
        var full = Full(path);
        var cwd = Full(Directory.GetCurrentDirectory());
        return full.StartsWith(cwd + Path.DirectorySeparatorChar, StringComparison.Ordinal) ? Path.GetRelativePath(cwd, full) : full;
    }
    public static string Sha256(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    public static string RequestIdFromFile(string path)
    {
        var name = Path.GetFileName(path);
        return name.EndsWith(".request.json", StringComparison.Ordinal) ? name[..^".request.json".Length] : "unknown";
    }
    public static string Slug(string value) => Regex.Replace(value.ToLowerInvariant(), @"[^a-z0-9-]+", "-").Trim('-');
    public static string ShellQuote(string value) => "'" + value.Replace("'", "'\"'\"'") + "'";
    public static Task WriteJsonAsync(string path, object value)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        var json = JsonSerializer.Serialize(value, JsonSupport.Options);
        return File.WriteAllTextAsync(path, json + Environment.NewLine, TextEncoding.Utf8NoBom);
    }
}

interface ILauncher
{
    Task<LauncherResult> LaunchParentAsync(string runDir);
    Task<LauncherResult> LaunchChildAsync(string runDir, JsonObject request);
}

sealed class ProcessLauncher : ILauncher
{
    private readonly Options options;

    public ProcessLauncher(Options options)
    {
        this.options = options;
    }

    public Task<LauncherResult> LaunchParentAsync(string runDir)
    {
        var outDir = Path.Combine(runDir, "launches", "parent");
        var args = new[]
        {
            "run", "skills-repo/tools/AgentDeliverySessionLauncher.cs", "--",
            "--handoff", options.ParentHandoff!,
            "--target-id", options.ParentTargetId!,
            "--mode", "launch",
            "--agent", "codex",
            "--adapter", "codex-app-server",
            "--initiating-project-cwd", options.InitiatingProjectCwd!,
            "--out", outDir,
            "--app-server-timeout-minutes", options.ParentTimeoutMinutes.ToString(),
            "--app-server-request-timeout-seconds", options.AppServerRequestTimeoutSeconds.ToString(),
        };
        return RunLauncherAsync(args, outDir, options.ParentTargetId!, TimeSpan.FromMinutes(options.ParentTimeoutMinutes + 2), Path.Combine(runDir, "controller", "parent-launcher"));
    }

    public Task<LauncherResult> LaunchChildAsync(string runDir, JsonObject request)
    {
        var child = request["child"]!.AsObject();
        var launch = request["launch"]!.AsObject();
        var targetId = child["target_id"]!.GetValue<string>();
        var outDir = Path.IsPathRooted(launch["out"]!.GetValue<string>())
            ? launch["out"]!.GetValue<string>()
            : Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), launch["out"]!.GetValue<string>()));
        var args = new[]
        {
            "run", "skills-repo/tools/AgentDeliverySessionLauncher.cs", "--",
            "--handoff", child["handoff_path"]!.GetValue<string>(),
            "--target-id", targetId,
            "--mode", "launch",
            "--agent", "codex",
            "--adapter", "codex-app-server",
            "--initiating-project-cwd", launch["initiating_project_cwd"]!.GetValue<string>(),
            "--out", outDir,
            "--app-server-timeout-minutes", options.ChildTimeoutMinutes.ToString(),
            "--app-server-request-timeout-seconds", options.AppServerRequestTimeoutSeconds.ToString(),
        };
        return RunLauncherAsync(args, outDir, targetId, TimeSpan.FromMinutes(options.ChildTimeoutMinutes + 2), Path.Combine(runDir, "controller", "child-launcher"));
    }

    private static async Task<LauncherResult> RunLauncherAsync(string[] args, string outDir, string targetId, TimeSpan timeout, string logPrefix)
    {
        Directory.CreateDirectory(outDir);
        Directory.CreateDirectory(Path.GetDirectoryName(logPrefix)!);
        var stdoutPath = logPrefix + ".stdout.log";
        var stderrPath = logPrefix + ".stderr.log";
        var psi = new ProcessStartInfo
        {
            FileName = "dotnet",
            WorkingDirectory = Directory.GetCurrentDirectory(),
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        foreach (var arg in args) psi.ArgumentList.Add(arg);

        using var process = Process.Start(psi);
        if (process is null)
        {
            return new LauncherResult("failed", 2, outDir, null, null, stderrPath, ["dotnet", .. args], TimedOut: false);
        }

        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        var timedOut = false;
        try
        {
            await process.WaitForExitAsync().WaitAsync(timeout);
        }
        catch (TimeoutException)
        {
            timedOut = true;
            try { process.Kill(entireProcessTree: true); } catch { }
        }

        var stdout = await stdoutTask.WaitAsync(TimeSpan.FromSeconds(5)).ContinueWith(t => t.IsCompletedSuccessfully ? t.Result : "");
        var stderr = await stderrTask.WaitAsync(TimeSpan.FromSeconds(5)).ContinueWith(t => t.IsCompletedSuccessfully ? t.Result : "");
        await File.WriteAllTextAsync(stdoutPath, stdout, TextEncoding.Utf8NoBom);
        await File.WriteAllTextAsync(stderrPath, stderr, TextEncoding.Utf8NoBom);

        var runDirectory = ParseLauncherRunDir(stdout) ?? FindNewestLauncherRunDir(outDir, targetId) ?? outDir;
        var evidencePath = Path.Combine(runDirectory, "evidence.json");
        var status = timedOut ? "timeout" : "failed";
        if (File.Exists(evidencePath))
        {
            status = JsonNode.Parse(await File.ReadAllTextAsync(evidencePath))?["status"]?.GetValue<string>() ?? status;
        }

        return new LauncherResult(
            status,
            timedOut ? 1 : process.ExitCode,
            runDirectory,
            File.Exists(evidencePath) ? evidencePath : null,
            File.Exists(Path.Combine(runDirectory, "app-server-transcript.jsonl")) ? Path.Combine(runDirectory, "app-server-transcript.jsonl") : null,
            File.Exists(Path.Combine(runDirectory, "app-server-stderr.log")) ? Path.Combine(runDirectory, "app-server-stderr.log") : stderrPath,
            ["dotnet", .. args],
            timedOut);
    }

    private static string? ParseLauncherRunDir(string stdout)
    {
        foreach (var line in stdout.Split('\n').Reverse())
        {
            var match = Regex.Match(line.Trim(), @"^(launched|blocked|failed|queued|manual_start_required):\s+(.+)$");
            if (match.Success) return Path.GetFullPath(match.Groups[2].Value.Trim());
        }
        return null;
    }

    private static string? FindNewestLauncherRunDir(string outDir, string targetId)
    {
        if (!Directory.Exists(outDir)) return null;
        var suffix = "-" + VisibleSessionController.Slug(targetId);
        return Directory.GetDirectories(outDir)
            .Where(d => Path.GetFileName(d).EndsWith(suffix, StringComparison.OrdinalIgnoreCase))
            .OrderByDescending(d => Directory.GetCreationTimeUtc(d))
            .FirstOrDefault();
    }
}

sealed class FixtureLauncher : ILauncher
{
    private readonly string runDir;

    public FixtureLauncher(string runDir)
    {
        this.runDir = runDir;
    }

    public Task<LauncherResult> LaunchParentAsync(string ignored)
    {
        return Task.FromResult(ReadFixtureResult("parent", "CTRL-PARENT"));
    }

    public Task<LauncherResult> LaunchChildAsync(string ignored, JsonObject request)
    {
        return Task.FromResult(ReadFixtureResult("child", request["child"]?["target_id"]?.GetValue<string>() ?? "CTRL-C1"));
    }

    private LauncherResult ReadFixtureResult(string role, string targetId)
    {
        var targetSpecificRoot = role == "child"
            ? Path.Combine(runDir, "fixture-launcher", "children", VisibleSessionController.Slug(targetId))
            : Path.Combine(runDir, "fixture-launcher", role);
        var root = Directory.Exists(targetSpecificRoot)
            ? targetSpecificRoot
            : Path.Combine(runDir, "fixture-launcher", role);
        var evidence = Path.Combine(root, "evidence.json");
        var status = File.Exists(evidence)
            ? JsonNode.Parse(File.ReadAllText(evidence))?["status"]?.GetValue<string>() ?? "failed"
            : "failed";
        return new LauncherResult(
            status,
            status is "launched" ? 0 : 1,
            root,
            File.Exists(evidence) ? evidence : null,
            File.Exists(Path.Combine(root, "app-server-transcript.jsonl")) ? Path.Combine(root, "app-server-transcript.jsonl") : null,
            File.Exists(Path.Combine(root, "app-server-stderr.log")) ? Path.Combine(root, "app-server-stderr.log") : null,
            ["fixture-launcher", role, targetId],
            TimedOut: false);
    }
}

sealed record ControllerRunResult(int ExitCode, string SummaryStatus);
sealed record RequestValidation(bool Valid, string RequestPath, string RequestId, string RequestSha256, JsonObject? Request, List<string> Blockers);
sealed record OutputAssertion(string Path, string ExpectedText, string? ActualTextSha256, string Status);
sealed record LauncherResult(string Status, int ExitCode, string RunDir, string? EvidencePath, string? TranscriptPath, string? StderrPath, string[]? Command, bool TimedOut);
sealed record ParentSummary(string TargetId, int LauncherExitCode, string? EvidencePath, string Status);

sealed class StateRecord
{
    public StateRecord(string state, DateTimeOffset enteredAt)
    {
        State = state;
        EnteredAt = enteredAt;
    }

    public string State { get; }
    public DateTimeOffset EnteredAt { get; }
    public DateTimeOffset? ExitedAt { get; private set; }
    public string Status { get; private set; } = "in_progress";

    public void Complete()
    {
        ExitedAt = DateTimeOffset.UtcNow;
        Status = "completed";
    }

    public void MarkFailed()
    {
        ExitedAt = DateTimeOffset.UtcNow;
        Status = "failed";
    }
}

sealed class StateScope : IDisposable
{
    private readonly StateRecord record;
    public StateScope(StateRecord record) => this.record = record;
    public void Dispose() => record.Complete();
}

sealed class Options
{
    public string? RunDir { get; private init; }
    public string? ParentHandoff { get; private init; }
    public string? ParentTargetId { get; private init; }
    public string? InitiatingProjectCwd { get; private init; }
    public string? FixtureRoot { get; private init; }
    public int RequestTimeoutSeconds { get; private init; } = 300;
    public int ParentTimeoutMinutes { get; private init; } = 30;
    public int ChildTimeoutMinutes { get; private init; } = 30;
    public int AppServerRequestTimeoutSeconds { get; private init; } = 60;
    public int PollIntervalMs { get; private init; } = 1000;
    public string? SummaryOut { get; private init; }
    public List<string> ExpectedChildTargetIds { get; private init; } = [];
    public bool ShowHelp { get; private init; }

    public bool IsValid
    {
        get
        {
            if (ShowHelp) return true;
            if (FixtureRoot is not null)
            {
                return RunDir is null && ParentHandoff is null && ParentTargetId is null && InitiatingProjectCwd is null;
            }
            return RunDir is not null &&
                   ParentHandoff is not null &&
                   ParentTargetId is not null &&
                   InitiatingProjectCwd is not null &&
                   RequestTimeoutSeconds > 0 &&
                   ParentTimeoutMinutes > 0 &&
                   ChildTimeoutMinutes > 0 &&
                   AppServerRequestTimeoutSeconds > 0 &&
                   PollIntervalMs > 0;
        }
    }

    public static Options Parse(string[] args)
    {
        string? runDir = null;
        string? parentHandoff = null;
        string? parentTargetId = null;
        string? initiatingProjectCwd = null;
        string? fixture = null;
        string? summaryOut = null;
        var requestTimeoutSeconds = 300;
        var parentTimeoutMinutes = 30;
        var childTimeoutMinutes = 30;
        var appServerRequestTimeoutSeconds = 60;
        var pollIntervalMs = 1000;
        var expectedChildTargetIds = new List<string>();
        var showHelp = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--help":
                case "-h":
                    showHelp = true;
                    break;
                case "--run-dir" when i + 1 < args.Length:
                    runDir = args[++i];
                    break;
                case "--parent-handoff" when i + 1 < args.Length:
                    parentHandoff = args[++i];
                    break;
                case "--parent-target-id" when i + 1 < args.Length:
                    parentTargetId = args[++i];
                    break;
                case "--initiating-project-cwd" when i + 1 < args.Length:
                    initiatingProjectCwd = args[++i];
                    break;
                case "--fixture" when i + 1 < args.Length:
                    fixture = args[++i];
                    break;
                case "--request-timeout-seconds" when i + 1 < args.Length && int.TryParse(args[i + 1], out var requestTimeout):
                    requestTimeoutSeconds = requestTimeout;
                    i++;
                    break;
                case "--parent-timeout-minutes" when i + 1 < args.Length && int.TryParse(args[i + 1], out var parentTimeout):
                    parentTimeoutMinutes = parentTimeout;
                    i++;
                    break;
                case "--child-timeout-minutes" when i + 1 < args.Length && int.TryParse(args[i + 1], out var childTimeout):
                    childTimeoutMinutes = childTimeout;
                    i++;
                    break;
                case "--app-server-request-timeout-seconds" when i + 1 < args.Length && int.TryParse(args[i + 1], out var requestRpcTimeout):
                    appServerRequestTimeoutSeconds = requestRpcTimeout;
                    i++;
                    break;
                case "--poll-interval-ms" when i + 1 < args.Length && int.TryParse(args[i + 1], out var poll):
                    pollIntervalMs = poll;
                    i++;
                    break;
                case "--summary-out" when i + 1 < args.Length:
                    summaryOut = args[++i];
                    break;
                case "--expected-child-target-ids" when i + 1 < args.Length:
                    expectedChildTargetIds = args[++i]
                        .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                        .ToList();
                    break;
            }
        }

        return new Options
        {
            RunDir = runDir,
            ParentHandoff = parentHandoff,
            ParentTargetId = parentTargetId,
            InitiatingProjectCwd = initiatingProjectCwd is null ? null : Path.GetFullPath(initiatingProjectCwd),
            FixtureRoot = fixture,
            RequestTimeoutSeconds = requestTimeoutSeconds,
            ParentTimeoutMinutes = parentTimeoutMinutes,
            ChildTimeoutMinutes = childTimeoutMinutes,
            AppServerRequestTimeoutSeconds = appServerRequestTimeoutSeconds,
            PollIntervalMs = pollIntervalMs,
            SummaryOut = summaryOut,
            ExpectedChildTargetIds = expectedChildTargetIds,
            ShowHelp = showHelp,
        };
    }

    public static void PrintUsage()
    {
        Console.WriteLine("""
        Usage:
          dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --run-dir <dir> --parent-handoff <path> --parent-target-id <id> --initiating-project-cwd <path> [options]
          dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --fixture <dir> [--summary-out <path>]

        Options:
          --run-dir <dir>                          Live run directory below tests/docworkflow-agent-delivery/e2e/session-workflow-live.
          --parent-handoff <path>                  Handoff used to start the visible parent session.
          --parent-target-id <id>                  Parent target id, for example CTRL-PARENT.
          --initiating-project-cwd <path>          Codex App project cwd passed to launcher.
          --fixture <dir>                          Validate deterministic controller fixtures without live launches.
          --request-timeout-seconds <n>            Max wait for child request after parent launch. Defaults to 300.
          --parent-timeout-minutes <n>             App-server turn timeout for parent launcher. Defaults to 30.
          --child-timeout-minutes <n>              App-server turn timeout for child launcher. Defaults to 30.
          --app-server-request-timeout-seconds <n> JSON-RPC request timeout passed to launcher. Defaults to 60.
          --poll-interval-ms <n>                   Poll interval for request artifacts. Defaults to 1000.
          --summary-out <path>                     Reserved summary output override.
          --expected-child-target-ids <ids>        Optional comma-separated ordered child ids for multi-child workflows.
          --help                                   Show this help.
        """);
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

static class TextEncoding
{
    public static readonly UTF8Encoding Utf8NoBom = new(false);
}
