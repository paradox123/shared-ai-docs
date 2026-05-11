using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization.Metadata;
using System.Text.RegularExpressions;

#pragma warning disable IL2026, IL3050

const string SummarySchema = "agent-delivery.visible-session-closeout-archive.v1";
var jsonOptions = new JsonSerializerOptions
{
    WriteIndented = true,
    TypeInfoResolver = new DefaultJsonTypeInfoResolver()
};

var options = Options.Parse(args);
if (options.ShowHelp || !options.IsValid)
{
    Options.PrintUsage();
    return options.ShowHelp ? 0 : 2;
}

if (options.Mode == "live" && string.IsNullOrWhiteSpace(options.AppServer))
{
    Console.Error.WriteLine("--mode live requires --app-server <stdio-or-socket>");
    return 2;
}

if (!string.IsNullOrWhiteSpace(options.FixturePath))
{
    return RunFixture(options);
}

if (!string.IsNullOrWhiteSpace(options.ValidateSummaryPath))
{
    var result = ValidateSummaryFile(options.ValidateSummaryPath!, null, options);
    PrintSummaryResult(result, Path.GetFileName(options.ValidateSummaryPath));
    return result.SetupErrors.Count > 0 ? 2 : result.MatchesExpected ? 0 : 1;
}

if (options.EvidencePaths.Count > 0 && !string.IsNullOrWhiteSpace(options.SummaryOutPath))
{
    return WriteSummaryFromEvidence(options);
}

Console.Error.WriteLine("Provide --fixture, --validate-summary, or --evidence with --summary-out.");
return 2;

int RunFixture(Options options)
{
    var fixturePath = Path.GetFullPath(options.FixturePath!);
    var manifestPath = Path.Combine(fixturePath, "fixture-manifest.json");
    if (!File.Exists(manifestPath))
    {
        Console.Error.WriteLine($"Fixture manifest not found: {manifestPath}");
        return 2;
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
        Console.Error.WriteLine($"Fixture manifest is not valid JSON: {ex.Message}");
        return 2;
    }

    var manifestErrors = ValidateManifest(manifest);
    if (manifestErrors.Count > 0)
    {
        foreach (var error in manifestErrors)
        {
            Console.Error.WriteLine($"Manifest error: {error}");
        }
        return 2;
    }

    var results = manifest.Cases.Select(testCase => ValidateFixtureCase(testCase, fixturePath, options)).ToList();
    var setupErrors = results.SelectMany(result => result.SetupErrors.Select(error => $"{result.Id}: {error}")).ToList();
    if (setupErrors.Count > 0)
    {
        foreach (var error in setupErrors)
        {
            Console.Error.WriteLine($"Setup error: {error}");
        }
        return 2;
    }

    var failures = 0;
    foreach (var result in results)
    {
        PrintSummaryResult(result, result.Id);
        if (!result.MatchesExpected)
        {
            failures++;
        }
    }

    if (failures > 0)
    {
        Console.Error.WriteLine($"RESULT: FAIL ({failures} case(s) mismatched expected outcome)");
        return 1;
    }

    Console.WriteLine($"RESULT: PASS ({results.Count} cases)");
    return 0;
}

List<string> ValidateManifest(FixtureManifest manifest)
{
    var errors = new List<string>();
    if (manifest.Cases.Count == 0)
    {
        errors.Add("fixture manifest contains no cases");
    }

    foreach (var testCase in manifest.Cases)
    {
        if (string.IsNullOrWhiteSpace(testCase.Id))
        {
            errors.Add("case id is required");
        }
        if (testCase.Expect is not "pass" and not "fail")
        {
            errors.Add($"{testCase.Id}: expect must be pass or fail");
        }
        if (testCase.Expect == "fail" && string.IsNullOrWhiteSpace(testCase.ExpectedArchiveFailureClass ?? testCase.ExpectedFailureClass))
        {
            errors.Add($"{testCase.Id}: expectedArchiveFailureClass is required for failing archive cases");
        }
    }

    return errors;
}

SummaryResult ValidateFixtureCase(FixtureCase testCase, string fixturePath, Options options)
{
    var caseDir = Resolve(fixturePath, testCase.Dir ?? CaseIdToDir(testCase.Id));
    var summaryPath = Resolve(caseDir, testCase.Summary ?? "expected-summary.json");
    var transcriptPath = string.IsNullOrWhiteSpace(testCase.Transcript)
        ? ResolveOptional(caseDir, "mock-app-server-transcript.jsonl")
        : Resolve(fixturePath, testCase.Transcript!);
    return ValidateSummaryFile(summaryPath, transcriptPath, options, testCase);
}

SummaryResult ValidateSummaryFile(string summaryPath, string? transcriptPath, Options options, FixtureCase? testCase = null)
{
    var setupErrors = new List<string>();
    var failures = new List<ValidationFailure>();
    var summary = ReadJson(summaryPath, setupErrors, "summary");
    var transcript = ReadTextIfPresent(transcriptPath, setupErrors, "transcript");

    if (summary is not null)
    {
        ValidateSummary(summary, transcript, options, failures);
    }

    var expected = testCase?.Expect ?? "pass";
    var expectedFailureClass = testCase?.ExpectedArchiveFailureClass ?? testCase?.ExpectedFailureClass;
    var actual = failures.Count == 0 ? "pass" : "fail";
    var actualFailureClass = failures.FirstOrDefault()?.Class;
    var matches = expected == "pass"
        ? actual == "pass"
        : actual == "fail" && string.Equals(actualFailureClass, expectedFailureClass, StringComparison.Ordinal);

    return new SummaryResult(testCase?.Id ?? "summary", expected, expectedFailureClass, actual, actualFailureClass, matches, failures, setupErrors);
}

void ValidateSummary(JsonDocument summary, string? transcript, Options options, List<ValidationFailure> failures)
{
    if (GetString(summary, "schema_id") != SummarySchema)
    {
        Add(failures, "invalid_schema", $"schema_id must be {SummarySchema}");
        return;
    }

    var root = summary.RootElement;
    if (LooksLikeSecret(root.GetRawText()) || LooksLikeSecret(transcript))
    {
        Add(failures, "secret_leak", "summary or transcript contains secret-like material");
        return;
    }

    if (!root.TryGetProperty("session_records", out var records) || records.ValueKind != JsonValueKind.Array)
    {
        Add(failures, "invalid_summary", "session_records array is required");
        return;
    }

    var ready = true;
    foreach (var record in records.EnumerateArray())
    {
        ValidateRecord(record, transcript, failures);
        if (!RecordAllowsReady(record))
        {
            ready = false;
        }
    }

    var overall = GetString(summary, "overall_archive_status");
    if (overall == "READY" && !ready && failures.Count == 0)
    {
        Add(failures, "unarchived_visible_session", "summary claims READY while a visible session is not archived");
    }
    else if (overall == "READY" && failures.Any(failure => IsBlockingFailureClass(failure.Class)))
    {
        return;
    }
    else if (overall is not "READY" and not "NOT_READY" and not "READY_NO_SESSION_EVIDENCE")
    {
        Add(failures, "invalid_summary", "overall_archive_status must be READY, NOT_READY or READY_NO_SESSION_EVIDENCE");
    }

    if (options.Mode == "live")
    {
        // Live mode is opt-in. The tool validates the same summary contract here; the
        // caller must supply an app-server transport for real archive execution.
        _ = options.AppServer;
    }
}

bool IsBlockingFailureClass(string failureClass) =>
    failureClass is "unarchived_visible_session" or "manual_visible_missing_thread" or "archive_failed" or "proof_failed" or "secret_leak";

void ValidateRecord(JsonElement record, string? transcript, List<ValidationFailure> failures)
{
    var status = GetElementString(record, "archive_status");
    var threadId = GetElementString(record, "thread_id");
    var visibilityClass = GetElementString(record, "visibility_class");
    var visible = visibilityClass is "visible_codex_app_session" or "manual_visible_start";

    if (visible && string.IsNullOrWhiteSpace(threadId))
    {
        Add(failures, "manual_visible_missing_thread", "visible/manual-visible archive record is missing thread_id");
        return;
    }

    switch (status)
    {
        case "archived":
            if (!HasArchiveProof(record))
            {
                Add(failures, "proof_failed", $"thread {threadId} lacks post-archive proof");
            }
            if (!TranscriptHasMethod(transcript, "thread/archive", threadId))
            {
                Add(failures, "archive_failed", $"thread {threadId} has no archive call transcript");
            }
            break;
        case "already_archived":
            if (!HasArchiveProof(record))
            {
                Add(failures, "proof_failed", $"thread {threadId} lacks already-archived proof");
            }
            break;
        case "not_app_visible_not_archived":
            if (visible)
            {
                Add(failures, "unarchived_visible_session", $"visible thread {threadId} cannot use not_app_visible_not_archived");
            }
            break;
        case "no_thread_created":
            if (visible)
            {
                Add(failures, "manual_visible_missing_thread", "visible/manual-visible evidence has no thread");
            }
            break;
        case "manual_visible_missing_thread":
            Add(failures, "manual_visible_missing_thread", "manual-visible evidence lacks a thread id");
            break;
        case "archive_failed":
            Add(failures, "archive_failed", $"thread {threadId} archive failed");
            break;
        case "proof_failed":
            Add(failures, "proof_failed", $"thread {threadId} archive proof failed");
            break;
        case "retained_session_accepted":
            if (string.IsNullOrWhiteSpace(GetElementString(record, "retention_accepted_by")) ||
                string.IsNullOrWhiteSpace(GetElementString(record, "retention_reason")))
            {
                Add(failures, "unarchived_visible_session", $"thread {threadId} retention lacks explicit acceptance");
            }
            break;
        default:
            if (visible)
            {
                Add(failures, "unarchived_visible_session", $"visible thread {threadId} has unsupported archive_status {status ?? "<missing>"}");
            }
            else
            {
                Add(failures, "invalid_summary", $"unsupported archive_status {status ?? "<missing>"}");
            }
            break;
    }
}

bool RecordAllowsReady(JsonElement record)
{
    var status = GetElementString(record, "archive_status");
    return status is "archived" or "already_archived" or "not_app_visible_not_archived" or "no_thread_created"
        || (status == "retained_session_accepted" &&
            !string.IsNullOrWhiteSpace(GetElementString(record, "retention_accepted_by")) &&
            !string.IsNullOrWhiteSpace(GetElementString(record, "retention_reason")));
}

bool HasArchiveProof(JsonElement record)
{
    if (!record.TryGetProperty("post_archive_proof", out var proof) || proof.ValueKind != JsonValueKind.Object)
    {
        return false;
    }

    return GetBool(proof, "archived_false_absent") == true || GetBool(proof, "archived_true_present") == true;
}

bool TranscriptHasMethod(string? transcript, string method, string? threadId)
{
    if (string.IsNullOrWhiteSpace(transcript))
    {
        return false;
    }

    foreach (var line in transcript.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
    {
        try
        {
            using var document = JsonDocument.Parse(line);
            var observedMethod = GetElementString(document.RootElement, "method") ?? GetElementString(document.RootElement, "message", "method");
            var observedThreadId = GetElementString(document.RootElement, "thread_id")
                ?? GetElementString(document.RootElement, "params", "thread_id")
                ?? GetElementString(document.RootElement, "params", "threadId")
                ?? GetElementString(document.RootElement, "message", "params", "thread_id")
                ?? GetElementString(document.RootElement, "message", "params", "threadId");
            if (observedMethod == method && (string.IsNullOrWhiteSpace(threadId) || observedThreadId == threadId))
            {
                return true;
            }
        }
        catch (JsonException)
        {
            return false;
        }
    }

    return false;
}

int WriteSummaryFromEvidence(Options options)
{
    var setupErrors = new List<string>();
    var records = new JsonArray();
    foreach (var evidencePath in options.EvidencePaths)
    {
        var evidence = ReadJson(evidencePath, setupErrors, "evidence");
        if (evidence is null)
        {
            continue;
        }
        records.Add(BuildRecordFromEvidence(evidencePath, evidence, options));
    }

    if (setupErrors.Count > 0)
    {
        foreach (var error in setupErrors)
        {
            Console.Error.WriteLine($"Setup error: {error}");
        }
        return 2;
    }

    var overall = records.All(record => RecordAllowsReady(JsonDocument.Parse(record!.ToJsonString()).RootElement))
        ? "READY"
        : "NOT_READY";
    var summary = new JsonObject
    {
        ["schema_id"] = SummarySchema,
        ["overall_archive_status"] = overall,
        ["created_at"] = DateTimeOffset.UtcNow.ToString("O"),
        ["session_records"] = records
    };

    var outputPath = Path.GetFullPath(options.SummaryOutPath!);
    Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
    File.WriteAllText(outputPath, summary.ToJsonString(jsonOptions));
    Console.WriteLine($"Wrote closeout archive summary: {outputPath}");
    return 0;
}

JsonObject BuildRecordFromEvidence(string evidencePath, JsonDocument evidence, Options options)
{
    var visibilityClass = GetString(evidence, "session_visibility", "class") ?? "";
    var executionChannel = GetString(evidence, "execution_channel") ?? "";
    var threadId = GetString(evidence, "session_visibility", "thread_id") ?? "";
    var status = ClassifyArchiveStatus(visibilityClass, executionChannel, threadId, options);
    var record = new JsonObject
    {
        ["evidence_path"] = evidencePath,
        ["execution_channel"] = executionChannel,
        ["visibility_class"] = visibilityClass,
        ["thread_id"] = threadId,
        ["session_title"] = GetString(evidence, "session_title") ?? GetString(evidence, "session_visibility", "title_observed") ?? "",
        ["archive_status"] = status
    };

    if (status == "retained_session_accepted")
    {
        record["retention_accepted_by"] = options.RetainedSessionAcceptedBy;
        record["retention_reason"] = options.RetentionReason;
    }

    return record;
}

string ClassifyArchiveStatus(string visibilityClass, string executionChannel, string threadId, Options options)
{
    if ((visibilityClass is "visible_codex_app_session" or "manual_visible_start") && string.IsNullOrWhiteSpace(threadId))
    {
        return "manual_visible_missing_thread";
    }
    if (visibilityClass is "visible_codex_app_session" or "manual_visible_start")
    {
        return !string.IsNullOrWhiteSpace(options.RetainedSessionAcceptedBy) && !string.IsNullOrWhiteSpace(options.RetentionReason)
            ? "retained_session_accepted"
            : "proof_failed";
    }
    if (executionChannel == "headless_cli" || visibilityClass is "headless_cli_session" or "traceable_but_not_visible")
    {
        return "not_app_visible_not_archived";
    }
    if (visibilityClass == "queued_manual_start" || executionChannel == "manual_queue")
    {
        return "no_thread_created";
    }

    return "not_app_visible_not_archived";
}

JsonDocument? ReadJson(string path, List<string> setupErrors, string label)
{
    if (!File.Exists(path))
    {
        setupErrors.Add($"{label} not found: {path}");
        return null;
    }

    try
    {
        return JsonDocument.Parse(File.ReadAllText(path));
    }
    catch (JsonException ex)
    {
        setupErrors.Add($"{label} is not valid JSON: {ex.Message}");
        return null;
    }
}

string? ReadTextIfPresent(string? path, List<string> setupErrors, string label)
{
    if (string.IsNullOrWhiteSpace(path))
    {
        return null;
    }
    if (!File.Exists(path))
    {
        return null;
    }

    return File.ReadAllText(path);
}

bool LooksLikeSecret(string? text)
{
    if (string.IsNullOrWhiteSpace(text))
    {
        return false;
    }

    return Regex.IsMatch(text, @"(?i)(bearer\s+[a-z0-9._\-]+|api[_-]?key|secret[_-]?key|BEGIN\s+(RSA|OPENSSH|PRIVATE)\s+KEY|raw_environment|prompt_body)");
}

string? ResolveOptional(string baseDir, string? path) =>
    string.IsNullOrWhiteSpace(path) ? null : Resolve(baseDir, path);

string Resolve(string baseDir, string path)
{
    path = path.Trim().Trim('`');
    return Path.IsPathRooted(path) ? Path.GetFullPath(path) : Path.GetFullPath(Path.Combine(baseDir, path));
}

string CaseIdToDir(string id)
{
    var marker = id.IndexOf('-', StringComparison.Ordinal);
    if (marker >= 0)
    {
        marker = id.IndexOf('-', marker + 1);
    }
    if (marker >= 0)
    {
        return id[(marker + 1)..];
    }
    return id;
}

string? GetString(JsonDocument? document, params string[] path)
{
    if (document is null) return null;
    return GetElementString(document.RootElement, path);
}

string? GetElementString(JsonElement element, params string[] path)
{
    JsonElement current = element;
    foreach (var segment in path)
    {
        if (current.ValueKind != JsonValueKind.Object || !current.TryGetProperty(segment, out current))
        {
            return null;
        }
    }

    return current.ValueKind == JsonValueKind.String ? current.GetString() : current.ToString();
}

bool? GetBool(JsonElement element, params string[] path)
{
    JsonElement current = element;
    foreach (var segment in path)
    {
        if (current.ValueKind != JsonValueKind.Object || !current.TryGetProperty(segment, out current))
        {
            return null;
        }
    }

    return current.ValueKind == JsonValueKind.True ? true : current.ValueKind == JsonValueKind.False ? false : null;
}

void Add(List<ValidationFailure> failures, string failureClass, string message)
{
    if (failures.Count == 0 || failures.All(failure => failure.Class != failureClass || failure.Message != message))
    {
        failures.Add(new ValidationFailure(failureClass, message));
    }
}

void PrintSummaryResult(SummaryResult result, string id)
{
    var status = result.MatchesExpected ? "PASS" : "FAIL";
    var expected = result.Expected == "pass" ? "pass" : $"fail:{result.ExpectedFailureClass}";
    var actual = result.Actual == "pass" ? "pass" : $"fail:{result.ActualFailureClass ?? "unknown"}";
    Console.WriteLine($"{status}: {id} expected={expected} actual={actual}");
    foreach (var failure in result.Failures)
    {
        Console.WriteLine($"  {failure.Class}: {failure.Message}");
    }
}

sealed class FixtureManifest
{
    public List<FixtureCase> Cases { get; set; } = [];
}

sealed class FixtureCase
{
    public string Id { get; set; } = "";
    public string? Dir { get; set; }
    public string? Summary { get; set; }
    public string? Transcript { get; set; }
    public string Expect { get; set; } = "fail";
    public string? ExpectedFailureClass { get; set; }
    public string? ExpectedArchiveFailureClass { get; set; }
}

sealed record ValidationFailure(string Class, string Message);
sealed record SummaryResult(
    string Id,
    string Expected,
    string? ExpectedFailureClass,
    string Actual,
    string? ActualFailureClass,
    bool MatchesExpected,
    List<ValidationFailure> Failures,
    List<string> SetupErrors);

sealed class Options
{
    public string? FixturePath { get; private init; }
    public string? ValidateSummaryPath { get; private init; }
    public List<string> EvidencePaths { get; private init; } = [];
    public string? SummaryOutPath { get; private init; }
    public string Mode { get; private init; } = "validate";
    public string? AppServer { get; private init; }
    public string? RetainedSessionAcceptedBy { get; private init; }
    public string? RetentionReason { get; private init; }
    public bool ShowHelp { get; private init; }

    public bool IsValid =>
        !string.IsNullOrWhiteSpace(FixturePath) ||
        !string.IsNullOrWhiteSpace(ValidateSummaryPath) ||
        (EvidencePaths.Count > 0 && !string.IsNullOrWhiteSpace(SummaryOutPath));

    public static Options Parse(string[] args)
    {
        string? fixture = null;
        string? validateSummary = null;
        var evidence = new List<string>();
        string? summaryOut = null;
        var mode = "validate";
        string? appServer = null;
        string? retainedBy = null;
        string? retentionReason = null;
        var help = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--fixture" when i + 1 < args.Length:
                    fixture = args[++i];
                    break;
                case "--validate-summary" when i + 1 < args.Length:
                    validateSummary = args[++i];
                    break;
                case "--evidence" when i + 1 < args.Length:
                    evidence.Add(args[++i]);
                    break;
                case "--summary-out" when i + 1 < args.Length:
                    summaryOut = args[++i];
                    break;
                case "--mode" when i + 1 < args.Length:
                    mode = args[++i];
                    break;
                case "--app-server" when i + 1 < args.Length:
                    appServer = args[++i];
                    break;
                case "--retained-session-accepted-by" when i + 1 < args.Length:
                    retainedBy = args[++i];
                    break;
                case "--retention-reason" when i + 1 < args.Length:
                    retentionReason = args[++i];
                    break;
                case "--help":
                case "-h":
                    help = true;
                    break;
            }
        }

        return new Options
        {
            FixturePath = fixture,
            ValidateSummaryPath = validateSummary,
            EvidencePaths = evidence,
            SummaryOutPath = summaryOut,
            Mode = mode,
            AppServer = appServer,
            RetainedSessionAcceptedBy = retainedBy,
            RetentionReason = retentionReason,
            ShowHelp = help
        };
    }

    public static void PrintUsage()
    {
        Console.WriteLine("""
        Usage:
          dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture <fixture-dir> [--mode validate]
          dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --validate-summary <summary.json> [--mode validate]
          dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --evidence <evidence.json> [--evidence <evidence.json> ...] --summary-out <summary.json>

        Validates or builds closeout archive summaries for visible Codex-App Agent Delivery sessions.
        Live thread/archive execution remains opt-in via --mode live --app-server <stdio-or-socket>.
        """);
    }
}
