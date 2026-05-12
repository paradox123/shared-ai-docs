using System.Text.Json;

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

var root = Path.GetFullPath(options.Root ?? Directory.GetCurrentDirectory());
var manifestPath = Path.GetFullPath(options.Manifest!);
var findings = new List<string>();
var warnings = new List<string>();

if (!File.Exists(manifestPath))
{
    findings.Add($"manifest-missing: {manifestPath}");
    WriteReport("fail", root, manifestPath, findings, warnings);
    return 1;
}

var entries = new List<CleanupEntry>();
try
{
    using var document = JsonDocument.Parse(File.ReadAllText(manifestPath));
    if (document.RootElement.TryGetProperty("entries", out var entriesElement) &&
        entriesElement.ValueKind == JsonValueKind.Array)
    {
        foreach (var element in entriesElement.EnumerateArray())
        {
            entries.Add(new CleanupEntry(
                GetString(element, "path"),
                GetString(element, "action"),
                GetString(element, "reason"),
                GetString(element, "category")));
        }
    }
}
catch (JsonException ex)
{
    findings.Add($"manifest-json-invalid: {ex.Message}");
}

if (entries.Count == 0)
{
    findings.Add("manifest-entries-missing: cleanup-manifest.json must contain entries.");
}

var deleted = new List<string>();
foreach (var entry in entries)
{
    if (string.IsNullOrWhiteSpace(entry.Path))
    {
        findings.Add("entry-path-missing");
        continue;
    }

    if (entry.Action is not ("delete" or "retain" or "archive-reference"))
    {
        findings.Add($"entry-action-invalid: {entry.Path} -> {entry.Action}");
    }

    if (string.IsNullOrWhiteSpace(entry.Reason))
    {
        findings.Add($"entry-reason-missing: {entry.Path}");
    }

    var resolved = Resolve(root, entry.Path);
    if (entry.Action == "delete")
    {
        deleted.Add(entry.Path);
        if (File.Exists(resolved) || Directory.Exists(resolved))
        {
            findings.Add($"deleted-path-still-exists: {entry.Path}");
        }
    }
}

foreach (var reference in FindDeletedReferences(root, deleted))
{
    findings.Add(reference);
}

WriteReport(findings.Count == 0 ? "pass" : "fail", root, manifestPath, findings, warnings);
return findings.Count == 0 ? 0 : 1;

static string GetString(JsonElement element, string property)
{
    return element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
        ? value.GetString() ?? ""
        : "";
}

static IEnumerable<string> FindDeletedReferences(string root, IReadOnlyList<string> deletedPaths)
{
    if (deletedPaths.Count == 0)
    {
        yield break;
    }

    var scanRoots = new[]
    {
        Path.Combine(root, "docs", "doc-workflow.md"),
        Path.Combine(root, "openspec", "changes", "simplify-agent-delivery-active-openspec"),
        Path.Combine(root, "skills-repo", "skills"),
        Path.Combine(root, "tests", "docworkflow-agent-delivery")
    };

    foreach (var file in EnumerateFiles(scanRoots))
    {
        var name = Path.GetFileName(file);
        if (name is "cleanup-manifest.json" or "cleanup-evidence.md")
        {
            continue;
        }

        var text = File.ReadAllText(file);
        foreach (var deletedPath in deletedPaths)
        {
            if (text.Contains(deletedPath, StringComparison.Ordinal))
            {
                yield return $"deleted-path-referenced: {Relative(root, file)} references {deletedPath}";
            }
        }
    }
}

static IEnumerable<string> EnumerateFiles(IEnumerable<string> paths)
{
    foreach (var path in paths)
    {
        if (File.Exists(path))
        {
            yield return path;
        }
        else if (Directory.Exists(path))
        {
            foreach (var file in Directory.GetFiles(path, "*", SearchOption.AllDirectories))
            {
                if (file.EndsWith(".md", StringComparison.OrdinalIgnoreCase) ||
                    file.EndsWith(".json", StringComparison.OrdinalIgnoreCase) ||
                    file.EndsWith(".js", StringComparison.OrdinalIgnoreCase) ||
                    file.EndsWith(".sh", StringComparison.OrdinalIgnoreCase) ||
                    file.EndsWith(".cs", StringComparison.OrdinalIgnoreCase))
                {
                    yield return file;
                }
            }
        }
    }
}

static string Resolve(string root, string path) => Path.IsPathRooted(path) ? path : Path.Combine(root, path);
static string Relative(string root, string path) => Path.GetRelativePath(root, path);

static void WriteReport(string verdict, string root, string manifestPath, List<string> findings, List<string> warnings)
{
    Console.WriteLine("{");
    Console.WriteLine("""  "schema_id": "agent-delivery.cleanup-validation.v1",""");
    Console.WriteLine($"""  "verdict": "{JsonEscape(verdict)}",""");
    Console.WriteLine($"""  "root": "{JsonEscape(root)}",""");
    Console.WriteLine($"""  "manifest": "{JsonEscape(manifestPath)}",""");
    PrintArray("findings", findings, trailingComma: true);
    PrintArray("warnings", warnings, trailingComma: false);
    Console.WriteLine("}");
}

static void PrintArray(string name, IReadOnlyList<string> values, bool trailingComma)
{
    Console.WriteLine($"""  "{name}": [""");
    for (var i = 0; i < values.Count; i++)
    {
        var comma = i == values.Count - 1 ? "" : ",";
        Console.WriteLine($"""    "{JsonEscape(values[i])}"{comma}""");
    }
    Console.WriteLine(trailingComma ? "  ]," : "  ]");
}

static string JsonEscape(string value) =>
    value.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "\\r");

sealed record CleanupEntry(string Path, string Action, string Reason, string? Category = null);

sealed class Options
{
    public string? Manifest { get; private init; }
    public string? Root { get; private init; }
    public bool ShowHelp { get; private init; }
    public bool IsValid => ShowHelp || !string.IsNullOrWhiteSpace(Manifest);

    public static Options Parse(string[] args)
    {
        string? manifest = null;
        string? root = null;
        var showHelp = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--manifest":
                    manifest = Next(args, ref i);
                    break;
                case "--root":
                    root = Next(args, ref i);
                    break;
                case "-h":
                case "--help":
                    showHelp = true;
                    break;
            }
        }

        return new Options { Manifest = manifest, Root = root, ShowHelp = showHelp };
    }

    static string? Next(string[] args, ref int index) => index + 1 < args.Length ? args[++index] : null;

    public static void PrintUsage()
    {
        Console.Error.WriteLine("Usage: dotnet run skills-repo/tools/ValidateAgentDeliveryCleanup.cs -- --manifest <path> [--root <repo-root>]");
    }
}
