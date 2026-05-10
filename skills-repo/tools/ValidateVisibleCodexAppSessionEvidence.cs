using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization.Metadata;
using System.Text.RegularExpressions;

#pragma warning disable IL2026, IL3050

const string SupportedSchema = "agent-delivery.session-launch.v2";
const string DefaultExpectedTitle = "ADV-CAS-1: Implementation - S2 Visible Evidence Validator";
const string DefaultExpectedCwd = "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs";

var options = Options.Parse(args);
if (options.ShowHelp || !options.IsValid)
{
    Options.PrintUsage();
    return options.ShowHelp ? 0 : 2;
}

if (!string.IsNullOrWhiteSpace(options.FixturePath))
{
    return RunFixture(options.FixturePath!);
}

var single = ValidateCase(new CaseDefinition
{
    Id = "single",
    Evidence = options.EvidencePath!,
    Prompt = options.PromptPath,
    Transcript = options.TranscriptPath,
    Closeout = options.CloseoutPath,
    Expect = "pass",
    ExpectTitle = options.ExpectTitle,
    ExpectInitiatingProjectCwd = options.ExpectInitiatingProjectCwd,
    RequireCloseoutArchived = options.RequireCloseoutArchived
}, Directory.GetCurrentDirectory());

PrintCase(single);
return single.SetupErrors.Count > 0 ? 2 : single.MatchesExpected ? 0 : 1;

static int RunFixture(string fixturePath)
{
    fixturePath = Path.GetFullPath(fixturePath);
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

    var results = manifest.Cases.Select(testCase => ValidateCase(testCase, fixturePath)).ToList();
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
        PrintCase(result);
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

static List<string> ValidateManifest(FixtureManifest manifest)
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
        if (string.IsNullOrWhiteSpace(testCase.Evidence))
        {
            errors.Add($"{testCase.Id}: evidence path is required");
        }
        if (testCase.Expect is not "pass" and not "fail")
        {
            errors.Add($"{testCase.Id}: expect must be pass or fail");
        }
        if (testCase.Expect == "fail" && string.IsNullOrWhiteSpace(testCase.ExpectedFailureClass))
        {
            errors.Add($"{testCase.Id}: expectedFailureClass is required for failing cases");
        }
    }

    return errors;
}

static CaseResult ValidateCase(CaseDefinition testCase, string baseDir)
{
    var setupErrors = new List<string>();
    var failures = new List<ValidationFailure>();
    var evidencePath = Resolve(baseDir, testCase.Evidence);
    var evidence = ReadJson(evidencePath, setupErrors, "evidence");
    var promptPath = ResolveOptional(baseDir, testCase.Prompt);
    var prompt = ReadTextIfPresent(promptPath, setupErrors, "prompt");
    var transcriptPath = ResolveOptional(baseDir, testCase.Transcript);
    var transcript = ReadTextIfPresent(transcriptPath, setupErrors, "transcript");
    var closeoutPath = ResolveOptional(baseDir, testCase.Closeout);
    var closeout = ReadJsonIfPresent(closeoutPath, setupErrors, "closeout");

    if (setupErrors.Count == 0 && evidence is not null)
    {
        ValidateVisibleEvidence(testCase, evidence, prompt, transcript, closeout, failures);
    }

    var actual = failures.Count == 0 ? "pass" : "fail";
    var actualFailureClass = failures.FirstOrDefault()?.Class;
    var matches = testCase.Expect == "pass"
        ? actual == "pass"
        : actual == "fail" && string.Equals(actualFailureClass, testCase.ExpectedFailureClass, StringComparison.Ordinal);

    return new CaseResult(testCase.Id, testCase.Expect, testCase.ExpectedFailureClass, actual, actualFailureClass, matches, failures, setupErrors);
}

static void ValidateVisibleEvidence(CaseDefinition testCase, JsonDocument evidence, string? prompt, string? transcript, JsonDocument? closeout, List<ValidationFailure> failures)
{
    var expectedTitle = testCase.ExpectTitle ?? DefaultExpectedTitle;
    var expectedCwd = testCase.ExpectInitiatingProjectCwd ?? DefaultExpectedCwd;
    var schema = GetString(evidence, "schema_version");
    if (schema != SupportedSchema)
    {
        Add(failures, "invalid_schema", $"schema_version must be {SupportedSchema}");
        return;
    }

    var status = GetString(evidence, "status");
    if (status is "queued" or "manual_start_required" or "blocked" or "failed")
    {
        Add(failures, "queued_not_visible", $"status {status} is not visible-session proof");
    }

    var actualCommand = GetString(evidence, "mechanism", "actual_command") ?? "";
    if (actualCommand.Contains("codex exec", StringComparison.OrdinalIgnoreCase) ||
        GetString(evidence, "execution_channel") == "headless_cli")
    {
        Add(failures, "headless_cli_not_visible", "headless codex exec evidence cannot prove app visibility");
    }

    var visibilityClass = GetString(evidence, "session_visibility", "class");
    var visibleInApp = GetBool(evidence, "session_visibility", "visible_in_codex_app");
    if (visibilityClass != "visible_codex_app_session" ||
        visibleInApp != true ||
        GetString(evidence, "session_visibility", "proof_status") != "verified")
    {
        Add(failures, "missing_visible_class", "visible session evidence requires class visible_codex_app_session, visible_in_codex_app true and proof_status verified");
    }

    var observedSource = GetString(evidence, "session_visibility", "thread_source_observed")
        ?? GetString(evidence, "session_visibility", "source_kind_observed")
        ?? GetString(evidence, "codex_app", "thread_source");
    var observedSourceKind = GetString(evidence, "session_visibility", "source_kind_observed");
    if (observedSource == "exec" || observedSourceKind == "exec" || GetString(evidence, "codex_app", "visibility_status") == "verified_same_project")
    {
        Add(failures, "source_exec_not_visible", "exec or verified_same_project source evidence is not app-visible proof");
    }

    var threadId = GetString(evidence, "session_visibility", "thread_id");
    var proofMethod = GetString(evidence, "session_visibility", "proof_method");
    var listObserved = GetBool(evidence, "session_visibility", "sidebar_or_default_list_observed") == true ||
        GetBool(evidence, "app_server", "thread_list_observed") == true;
    var acceptedProofMethod = proofMethod is "app_server_thread_list" or "codex_app_ui_observation" or "manual_human_confirmation";
    if (string.IsNullOrWhiteSpace(threadId) || !acceptedProofMethod || !listObserved)
    {
        Add(failures, "missing_thread", "visible proof requires thread id, accepted proof method and thread-list/sidebar observation");
    }

    var sessionTitle = GetString(evidence, "session_title");
    var titleObserved = GetString(evidence, "session_visibility", "title_observed");
    if (sessionTitle != expectedTitle || titleObserved != expectedTitle)
    {
        Add(failures, "wrong_title", "observed title must equal the parent-prefixed expected title");
    }

    var initiatingCwd = GetString(evidence, "initiating_project_cwd");
    var cwdObserved = GetString(evidence, "session_visibility", "cwd_observed");
    if (initiatingCwd != expectedCwd || cwdObserved != expectedCwd)
    {
        Add(failures, "wrong_cwd", "observed cwd must equal initiating_project_cwd");
    }

    if (GetString(evidence, "execution_channel") != "app_server" || GetString(evidence, "adapter_id") != "codex-app-server")
    {
        Add(failures, "headless_cli_not_visible", "visible machine proof requires the app-server adapter");
    }

    var promptHash = GetString(evidence, "prompt_sha256");
    if (!Regex.IsMatch(promptHash ?? "", "^[a-f0-9]{64}$") || prompt is null || Sha256(prompt) != promptHash)
    {
        Add(failures, "prompt_hash_mismatch", "prompt_sha256 must match the persisted prompt");
    }

    var appServerTurnPresent =
        GetBool(evidence, "app_server", "thread_start_observed") == true &&
        GetBool(evidence, "app_server", "thread_name_set_observed") == true &&
        GetBool(evidence, "app_server", "turn_start_observed") == true &&
        GetString(evidence, "app_server", "turn_completed_status") == "completed" &&
        GetBool(evidence, "app_server", "thread_list_observed") == true;
    if (!appServerTurnPresent || !TranscriptHasOrderedProof(transcript, threadId))
    {
        Add(failures, "missing_turn", "app-server evidence requires materialized turn proof and ordered transcript methods");
    }

    if (testCase.RequireCloseoutArchived)
    {
        var archived = GetBool(closeout, "archived") ?? GetBool(closeout, "visible_session_archived");
        if (archived != true)
        {
            Add(failures, "unarchived_visible_session", "closeout-required visible session remains unarchived");
        }
    }
}

static bool TranscriptHasOrderedProof(string? transcript, string? expectedThreadId)
{
    if (string.IsNullOrWhiteSpace(transcript))
    {
        return false;
    }

    var entries = ParseTranscript(transcript);
    var methods = entries
        .Where(entry => entry.Direction == "client")
        .Select(entry => entry.Method)
        .Where(method => !string.IsNullOrWhiteSpace(method))
        .ToList();

    if (!HasOrderedMethods(methods, ["initialize", "thread/start", "thread/name/set", "turn/start", "thread/list"]))
    {
        return false;
    }

    var observedThreadIds = entries
        .Where(entry => entry.Method is "thread/start" or "thread/name/set" or "turn/start" or "thread/list")
        .Select(entry => entry.ThreadId)
        .Where(id => !string.IsNullOrWhiteSpace(id))
        .Distinct(StringComparer.Ordinal)
        .ToList();

    return observedThreadIds.Count == 0 ||
        (!string.IsNullOrWhiteSpace(expectedThreadId) && observedThreadIds.Count == 1 && observedThreadIds[0] == expectedThreadId);
}

static List<TranscriptEntry> ParseTranscript(string transcript)
{
    var entries = new List<TranscriptEntry>();
    foreach (var line in transcript.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
    {
        using var document = JsonDocument.Parse(line);
        var method = GetString(document, "method") ?? GetString(document, "message", "method");
        var threadId = GetString(document, "thread_id")
            ?? GetString(document, "params", "thread_id")
            ?? GetString(document, "params", "threadId")
            ?? GetString(document, "message", "params", "thread_id")
            ?? GetString(document, "message", "params", "threadId");
        entries.Add(new TranscriptEntry(GetString(document, "direction") ?? "", method ?? "", threadId ?? ""));
    }

    return entries;
}

static bool HasOrderedMethods(List<string> methods, string[] expected)
{
    var cursor = 0;
    foreach (var method in methods)
    {
        if (method == expected[cursor])
        {
            cursor++;
        }
        if (cursor == expected.Length)
        {
            return true;
        }
    }

    return false;
}

static JsonDocument? ReadJson(string path, List<string> setupErrors, string label)
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

static JsonDocument? ReadJsonIfPresent(string? path, List<string> setupErrors, string label) =>
    string.IsNullOrWhiteSpace(path) ? null : ReadJson(path, setupErrors, label);

static string? ReadTextIfPresent(string? path, List<string> setupErrors, string label)
{
    if (string.IsNullOrWhiteSpace(path))
    {
        return null;
    }
    if (!File.Exists(path))
    {
        setupErrors.Add($"{label} not found: {path}");
        return null;
    }

    return File.ReadAllText(path);
}

static string Sha256(string text)
{
    var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(text));
    return Convert.ToHexString(bytes).ToLowerInvariant();
}

static string? ResolveOptional(string baseDir, string? path) =>
    string.IsNullOrWhiteSpace(path) ? null : Resolve(baseDir, path);

static string Resolve(string baseDir, string path)
{
    path = path.Trim().Trim('`');
    return Path.IsPathRooted(path) ? Path.GetFullPath(path) : Path.GetFullPath(Path.Combine(baseDir, path));
}

static void Add(List<ValidationFailure> failures, string failureClass, string message) =>
    failures.Add(new ValidationFailure(failureClass, message));

static string? GetString(JsonDocument? document, params string[] path)
{
    if (document is null) return null;
    JsonElement current = document.RootElement;
    foreach (var segment in path)
    {
        if (current.ValueKind != JsonValueKind.Object || !current.TryGetProperty(segment, out current))
        {
            return null;
        }
    }

    return current.ValueKind == JsonValueKind.String ? current.GetString() : current.ToString();
}

static bool? GetBool(JsonDocument? document, params string[] path)
{
    if (document is null) return null;
    JsonElement current = document.RootElement;
    foreach (var segment in path)
    {
        if (current.ValueKind != JsonValueKind.Object || !current.TryGetProperty(segment, out current))
        {
            return null;
        }
    }

    return current.ValueKind == JsonValueKind.True ? true : current.ValueKind == JsonValueKind.False ? false : null;
}

static void PrintCase(CaseResult result)
{
    var status = result.MatchesExpected ? "PASS" : "FAIL";
    var expected = result.Expected == "pass" ? "pass" : $"fail:{result.ExpectedFailureClass}";
    var actual = result.Actual == "pass" ? "pass" : $"fail:{result.ActualFailureClass ?? "unknown"}";
    Console.WriteLine($"{status}: {result.Id} expected={expected} actual={actual}");
    foreach (var failure in result.Failures)
    {
        Console.WriteLine($"  {failure.Class}: {failure.Message}");
    }
}

sealed class FixtureManifest
{
    public List<CaseDefinition> Cases { get; set; } = [];
}

sealed class CaseDefinition
{
    public string Id { get; set; } = "";
    public string Evidence { get; set; } = "";
    public string? Prompt { get; set; }
    public string? Transcript { get; set; }
    public string? Closeout { get; set; }
    public string Expect { get; set; } = "fail";
    public string? ExpectedFailureClass { get; set; }
    public string? ExpectTitle { get; set; }
    public string? ExpectInitiatingProjectCwd { get; set; }
    public bool RequireCloseoutArchived { get; set; }
}

sealed record ValidationFailure(string Class, string Message);
sealed record TranscriptEntry(string Direction, string Method, string ThreadId);
sealed record CaseResult(
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
    public string? EvidencePath { get; private init; }
    public string? PromptPath { get; private init; }
    public string? TranscriptPath { get; private init; }
    public string? CloseoutPath { get; private init; }
    public string? ExpectTitle { get; private init; }
    public string? ExpectInitiatingProjectCwd { get; private init; }
    public bool RequireCloseoutArchived { get; private init; }
    public bool ShowHelp { get; private init; }

    public bool IsValid =>
        !string.IsNullOrWhiteSpace(FixturePath) ||
        !string.IsNullOrWhiteSpace(EvidencePath);

    public static Options Parse(string[] args)
    {
        string? fixture = null;
        string? evidence = null;
        string? prompt = null;
        string? transcript = null;
        string? closeout = null;
        string? expectTitle = null;
        string? expectCwd = null;
        var requireCloseoutArchived = false;
        var help = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--fixture" when i + 1 < args.Length:
                    fixture = args[++i];
                    break;
                case "--evidence" when i + 1 < args.Length:
                    evidence = args[++i];
                    break;
                case "--prompt" when i + 1 < args.Length:
                    prompt = args[++i];
                    break;
                case "--transcript" when i + 1 < args.Length:
                    transcript = args[++i];
                    break;
                case "--closeout" when i + 1 < args.Length:
                    closeout = args[++i];
                    break;
                case "--expect-title" when i + 1 < args.Length:
                    expectTitle = args[++i];
                    break;
                case "--expect-initiating-project-cwd" when i + 1 < args.Length:
                    expectCwd = args[++i];
                    break;
                case "--require-closeout-archived":
                    requireCloseoutArchived = true;
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
            EvidencePath = evidence,
            PromptPath = prompt,
            TranscriptPath = transcript,
            CloseoutPath = closeout,
            ExpectTitle = expectTitle,
            ExpectInitiatingProjectCwd = expectCwd,
            RequireCloseoutArchived = requireCloseoutArchived,
            ShowHelp = help
        };
    }

    public static void PrintUsage()
    {
        Console.WriteLine("""
        Usage:
          dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture <fixture-dir>
          dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --evidence <evidence.json> [--prompt <start-prompt.md>] [--transcript <app-server-transcript.jsonl>] [--closeout <closeout-summary.json>] [--expect-title <title>] [--expect-initiating-project-cwd <cwd>] [--require-closeout-archived]

        Validates visible Codex-App Agent Delivery session evidence:
        - accepts only agent-delivery.session-launch.v2 app-server visible-session proof
        - rejects headless codex exec, queued/manual-only, exec source, wrong title, wrong cwd, missing thread, prompt hash mismatch, missing turn and unarchived closeout evidence
        - fixture mode requires expected negatives to fail with their declared failure class
        """);
    }
}
