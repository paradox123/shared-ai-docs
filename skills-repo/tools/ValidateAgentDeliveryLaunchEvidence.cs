using System.Text.Json;
using System.Text.Json.Serialization.Metadata;
using System.Text.RegularExpressions;

#pragma warning disable IL2026, IL3050

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
    Handoff = options.HandoffPath!,
    LaunchRequest = options.LaunchRequestPath,
    Evidence = options.EvidencePath,
    AutomaticClaim = options.RequireAutomatic,
    Expected = options.RequireAutomatic ? "pass" : "manual"
}, Directory.GetCurrentDirectory());

PrintCase(single);
return single.MatchesExpected ? 0 : 1;

static int RunFixture(string fixturePath)
{
    fixturePath = Path.GetFullPath(fixturePath);
    var manifestPath = Path.Combine(fixturePath, "fixture-manifest.json");
    if (!File.Exists(manifestPath))
    {
        Console.Error.WriteLine($"Fixture manifest not found: {manifestPath}");
        return 2;
    }

    var manifest = JsonSerializer.Deserialize<FixtureManifest>(
        File.ReadAllText(manifestPath),
        new JsonSerializerOptions { PropertyNameCaseInsensitive = true, TypeInfoResolver = new DefaultJsonTypeInfoResolver() }) ?? new FixtureManifest();
    if (manifest.Cases.Count == 0)
    {
        Console.Error.WriteLine("Fixture manifest contains no cases.");
        return 2;
    }

    var failures = 0;
    foreach (var testCase in manifest.Cases)
    {
        var result = ValidateCase(testCase, fixturePath);
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

    Console.WriteLine($"RESULT: PASS ({manifest.Cases.Count} cases)");
    return 0;
}

static CaseResult ValidateCase(CaseDefinition testCase, string baseDir)
{
    var errors = new List<string>();
    var warnings = new List<string>();
    var handoffPath = Resolve(baseDir, testCase.Handoff);
    var handoffText = File.Exists(handoffPath) ? File.ReadAllText(handoffPath) : "";
    if (!File.Exists(handoffPath))
    {
        errors.Add($"handoff not found: {handoffPath}");
    }

    var targetId = ExtractField(handoffText, "Target ID")
        ?? ExtractField(handoffText, "Stable Child ID")
        ?? ExtractField(handoffText, "Child")
        ?? "";

    var launchRequestPath = ResolveOptional(baseDir, testCase.LaunchRequest);
    var evidencePath = ResolveOptional(baseDir, testCase.Evidence);
    JsonDocument? launchRequest = ReadJsonIfPresent(launchRequestPath, errors, "launch-request.json");
    JsonDocument? evidence = ReadJsonIfPresent(evidencePath, errors, "evidence.json");

    if (testCase.AutomaticClaim)
    {
        if (launchRequest is null)
        {
            errors.Add("automatic transition claim requires launch-request.json");
        }
        if (evidence is null)
        {
            errors.Add("automatic transition claim requires evidence.json");
        }
    }

    var status = GetString(evidence, "status") ?? GetString(launchRequest, "status") ?? "";
    var outcome = "fail";

    if (evidence is not null || launchRequest is not null)
    {
        ValidateEvidenceJson(launchRequest, evidence, targetId, handoffPath, baseDir, errors, warnings);

        outcome = status switch
        {
            "queued" or "launched" when errors.Count == 0 => "pass",
            "manual_start_required" => "manual",
            "blocked" or "failed" => "fail",
            _ => "fail"
        };
    }

    var sessionOutcome = ValidateSessionReference(handoffText, evidence, launchRequest);
    if (outcome == "pass")
    {
        // Matching launcher evidence is the forensic session reference.
    }
    else if (sessionOutcome.Kind == "legacy")
    {
        outcome = "legacy";
    }
    else if (sessionOutcome.Kind == "manual" && outcome == "manual")
    {
        outcome = "manual";
    }
    else if (sessionOutcome.Kind == "real" && !testCase.AutomaticClaim)
    {
        outcome = "pass";
    }
    else if (sessionOutcome.Kind == "semantic-only")
    {
        errors.Add("handoff has only semantic SessionId without real log path, launcher evidence, manual marker, or legacy_reconstructed marker");
        outcome = "fail";
    }

    if (testCase.AutomaticClaim && outcome is "manual" or "legacy")
    {
        warnings.Add($"{outcome} evidence is visible but does not satisfy an automatic transition claim");
    }

    var matches = string.Equals(outcome, testCase.Expected, StringComparison.OrdinalIgnoreCase);
    return new CaseResult(testCase.Id, testCase.Expected, outcome, matches, errors, warnings);
}

static void ValidateEvidenceJson(JsonDocument? launchRequest, JsonDocument? evidence, string targetId, string handoffPath, string baseDir, List<string> errors, List<string> warnings)
{
    var status = GetString(evidence, "status") ?? GetString(launchRequest, "status");
    if (string.IsNullOrWhiteSpace(status))
    {
        errors.Add("launch evidence is missing status");
    }

    var evidenceTarget = GetString(evidence, "target_id") ?? GetString(launchRequest, "target_id");
    if (!string.Equals(evidenceTarget, targetId, StringComparison.OrdinalIgnoreCase))
    {
        errors.Add($"target_id mismatch: handoff `{targetId}`, evidence `{evidenceTarget}`");
    }

    var evidenceHandoff = GetString(evidence, "handoff_path") ?? GetString(launchRequest, "handoff_path");
    if (string.IsNullOrWhiteSpace(evidenceHandoff))
    {
        errors.Add("launch evidence is missing handoff_path");
    }
    else if (!SamePath(Resolve(baseDir, evidenceHandoff), handoffPath))
    {
        errors.Add($"handoff_path mismatch: evidence `{evidenceHandoff}`, handoff `{handoffPath}`");
    }

    var provider = GetString(evidence, "agent", "requested_provider") ?? GetString(launchRequest, "agent", "requested_provider");
    var adapterStatus = GetString(evidence, "agent", "adapter_status") ?? GetString(launchRequest, "agent", "adapter_status");
    if (string.IsNullOrWhiteSpace(provider))
    {
        errors.Add("launch evidence is missing agent.requested_provider");
    }
    if (string.IsNullOrWhiteSpace(adapterStatus))
    {
        errors.Add("launch evidence is missing agent.adapter_status");
    }

    if (status is "queued" or "launched")
    {
        var promptPath = GetString(evidence, "evidence_paths", "prompt") ?? GetString(launchRequest, "evidence_paths", "prompt");
        if (string.IsNullOrWhiteSpace(promptPath))
        {
            errors.Add("queued/launched evidence is missing evidence_paths.prompt");
        }
        else if (!File.Exists(Resolve(baseDir, promptPath)))
        {
            errors.Add($"prompt path not found: {promptPath}");
        }
    }
    else if (status == "manual_start_required")
    {
        warnings.Add("manual_start_required is visible but not automatic transition proof");
    }
    else if (status is "blocked" or "failed")
    {
        errors.Add($"{status} launch evidence blocks downstream delivery");
    }
}

static SessionReference ValidateSessionReference(string handoffText, JsonDocument? evidence, JsonDocument? launchRequest)
{
    var status = GetString(evidence, "status") ?? GetString(launchRequest, "status") ?? "";
    if (status == "manual_start_required")
    {
        return new SessionReference("manual");
    }

    var hasLegacy = handoffText.Contains("legacy_reconstructed", StringComparison.OrdinalIgnoreCase);
    var hasReconstructionSource = Regex.IsMatch(handoffText, @"(?i)Reconstruction (Source|Date)|Rekonstruktions(source|datum)");
    if (hasLegacy && hasReconstructionSource)
    {
        return new SessionReference("legacy");
    }

    var hasJsonl = handoffText.Contains(".jsonl", StringComparison.OrdinalIgnoreCase);
    var hasCodexSessionId = Regex.IsMatch(handoffText, @"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", RegexOptions.IgnoreCase);
    if (hasJsonl && hasCodexSessionId)
    {
        return new SessionReference("real");
    }

    var hasSessionId = Regex.IsMatch(handoffText, @"(?im)^SessionId:\s*.+$") ||
                       Regex.IsMatch(handoffText, @"(?im)^\s*[-*]\s*(Codex Session / Log|Session ID|SessionId):\s*.+$");
    if (hasSessionId)
    {
        return new SessionReference("semantic-only");
    }

    return new SessionReference("none");
}

static JsonDocument? ReadJsonIfPresent(string? path, List<string> errors, string label)
{
    if (string.IsNullOrWhiteSpace(path))
    {
        return null;
    }

    if (!File.Exists(path))
    {
        errors.Add($"{label} not found: {path}");
        return null;
    }

    try
    {
        return JsonDocument.Parse(File.ReadAllText(path));
    }
    catch (JsonException ex)
    {
        errors.Add($"{label} is not valid JSON: {ex.Message}");
        return null;
    }
}

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

static string? ExtractField(string text, string label)
{
    var match = Regex.Match(text, @"^\s*[-*]\s*" + Regex.Escape(label) + @"\s*:\s*(.+?)\s*$", RegexOptions.Multiline | RegexOptions.IgnoreCase);
    if (!match.Success) return null;
    return match.Groups[1].Value.Trim().Trim('`');
}

static string Resolve(string baseDir, string path)
{
    path = path.Trim().Trim('`');
    return Path.IsPathRooted(path) ? Path.GetFullPath(path) : Path.GetFullPath(Path.Combine(baseDir, path));
}

static string? ResolveOptional(string baseDir, string? path) =>
    string.IsNullOrWhiteSpace(path) ? null : Resolve(baseDir, path);

static bool SamePath(string left, string right) =>
    string.Equals(Path.GetFullPath(left).TrimEnd(Path.DirectorySeparatorChar), Path.GetFullPath(right).TrimEnd(Path.DirectorySeparatorChar), StringComparison.Ordinal);

static void PrintCase(CaseResult result)
{
    var status = result.MatchesExpected ? "PASS" : "FAIL";
    Console.WriteLine($"{status}: {result.Id} expected={result.Expected} actual={result.Actual}");
    foreach (var warning in result.Warnings)
    {
        Console.WriteLine($"  warning: {warning}");
    }
    foreach (var error in result.Errors)
    {
        Console.WriteLine($"  error: {error}");
    }
}

sealed class FixtureManifest
{
    public List<CaseDefinition> Cases { get; set; } = [];
}

sealed class CaseDefinition
{
    public string Id { get; set; } = "";
    public string Handoff { get; set; } = "";
    public string? LaunchRequest { get; set; }
    public string? Evidence { get; set; }
    public bool AutomaticClaim { get; set; }
    public string Expected { get; set; } = "fail";
}

sealed record CaseResult(string Id, string Expected, string Actual, bool MatchesExpected, List<string> Errors, List<string> Warnings);
sealed record SessionReference(string Kind);

sealed class Options
{
    public string? FixturePath { get; private init; }
    public string? HandoffPath { get; private init; }
    public string? LaunchRequestPath { get; private init; }
    public string? EvidencePath { get; private init; }
    public bool RequireAutomatic { get; private init; }
    public bool ShowHelp { get; private init; }

    public bool IsValid =>
        !string.IsNullOrWhiteSpace(FixturePath) ||
        (!string.IsNullOrWhiteSpace(HandoffPath) && (!RequireAutomatic || !string.IsNullOrWhiteSpace(EvidencePath)));

    public static Options Parse(string[] args)
    {
        string? fixture = null;
        string? handoff = null;
        string? launchRequest = null;
        string? evidence = null;
        var requireAutomatic = false;
        var help = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--fixture" when i + 1 < args.Length:
                    fixture = args[++i];
                    break;
                case "--handoff" when i + 1 < args.Length:
                    handoff = args[++i];
                    break;
                case "--launch-request" when i + 1 < args.Length:
                    launchRequest = args[++i];
                    break;
                case "--evidence" when i + 1 < args.Length:
                    evidence = args[++i];
                    break;
                case "--require-automatic":
                    requireAutomatic = true;
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
            HandoffPath = handoff,
            LaunchRequestPath = launchRequest,
            EvidencePath = evidence,
            RequireAutomatic = requireAutomatic,
            ShowHelp = help
        };
    }

    public static void PrintUsage()
    {
        Console.WriteLine("""
        Usage:
          dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture <fixture-dir>
          dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --handoff <handoff.md> --evidence <evidence.json> [--launch-request <launch-request.json>] [--require-automatic]

        Validates Agent Delivery Session Launch/Queue Evidence:
        - automatic claims require matching target id, handoff path, prompt path and status queued/launched
        - manual_start_required is visible manual residue, not automatic success
        - blocked/failed stop downstream delivery
        - semantic-only SessionId is rejected unless legacy_reconstructed or real Codex log evidence exists
        """);
    }
}
