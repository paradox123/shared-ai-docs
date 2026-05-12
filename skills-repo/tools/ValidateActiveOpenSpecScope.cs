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
var changeDir = options.ChangeDir is not null
    ? Path.GetFullPath(options.ChangeDir)
    : Path.Combine(root, "openspec", "changes", options.Change!);

var findings = new List<string>();
var warnings = new List<string>();

if (!Directory.Exists(changeDir))
{
    findings.Add($"active-change-missing: {changeDir}");
    WriteReport("fail", root, changeDir, findings, warnings);
    return 1;
}

var proposalPath = Path.Combine(changeDir, "proposal.md");
var designPath = Path.Combine(changeDir, "design.md");
var tasksPath = Path.Combine(changeDir, "tasks.md");
var specsDir = Path.Combine(changeDir, "specs");

RequireFile(proposalPath, "proposal.md", findings);
RequireFile(tasksPath, "tasks.md", findings);
if (!Directory.Exists(specsDir) || Directory.GetFiles(specsDir, "*.md", SearchOption.AllDirectories).Length == 0)
{
    findings.Add("specs-missing: active OpenSpec change must include at least one specs/**/*.md delta.");
}

var proposal = ReadIfExists(proposalPath);
var design = ReadIfExists(designPath);
var tasks = ReadIfExists(tasksPath);
var specs = Directory.Exists(specsDir)
    ? string.Join("\n", Directory.GetFiles(specsDir, "*.md", SearchOption.AllDirectories).Select(File.ReadAllText))
    : "";
var all = string.Join("\n", proposal, design, tasks, specs);

RequireAny("goal", findings, all, "## Why", "Ziel", "Goal", "What Changes");
RequireAny("in-scope", findings, all, "In Scope", "in-scope", "What Changes", "ADDED Requirements", "MODIFIED Requirements");
RequireAny("out-of-scope", findings, all, "Out of Scope", "Non-Goals", "out-of-scope", "Non-Goals:");
RequireAny("write-set-or-impact", findings, all, "## Impact", "Write-set", "write-set", "Affected", "skills-repo/", "docs/");
RequireAny("verification", findings, all, "Verification", "validation", "validate", "git diff --check", "tests");

if (!tasks.Contains("- [ ]") && !tasks.Contains("- [x]"))
{
    findings.Add("tasks-checkboxes-missing: tasks.md must contain OpenSpec checkbox tasks.");
}

if (options.Parent is not null)
{
    var parent = Path.GetFullPath(options.Parent);
    if (!File.Exists(parent) && !Directory.Exists(parent))
    {
        warnings.Add($"parent-reference-not-found: {parent}");
    }
}

WriteReport(findings.Count == 0 ? "pass" : "fail", root, changeDir, findings, warnings);
return findings.Count == 0 ? 0 : 1;

static void RequireFile(string path, string label, List<string> findings)
{
    if (!File.Exists(path))
    {
        findings.Add($"required-file-missing: {label}");
    }
}

static string ReadIfExists(string path) => File.Exists(path) ? File.ReadAllText(path) : "";

static void RequireAny(string label, List<string> findings, string text, params string[] needles)
{
    if (!needles.Any(n => text.Contains(n, StringComparison.OrdinalIgnoreCase)))
    {
        findings.Add($"active-scope-field-missing: {label}");
    }
}

static void WriteReport(string verdict, string root, string changeDir, List<string> findings, List<string> warnings)
{
    Console.WriteLine("{");
    Console.WriteLine("""  "schema_id": "agent-delivery.active-openspec-scope.v1",""");
    Console.WriteLine($"""  "verdict": "{JsonEscape(verdict)}",""");
    Console.WriteLine($"""  "root": "{JsonEscape(root)}",""");
    Console.WriteLine($"""  "change_dir": "{JsonEscape(changeDir)}",""");
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

sealed class Options
{
    public string? Change { get; private init; }
    public string? ChangeDir { get; private init; }
    public string? Root { get; private init; }
    public string? Parent { get; private init; }
    public bool ShowHelp { get; private init; }
    public bool IsValid => ShowHelp || !string.IsNullOrWhiteSpace(Change) || !string.IsNullOrWhiteSpace(ChangeDir);

    public static Options Parse(string[] args)
    {
        string? change = null;
        string? changeDir = null;
        string? root = null;
        string? parent = null;
        var showHelp = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--change":
                    change = Next(args, ref i);
                    break;
                case "--change-dir":
                    changeDir = Next(args, ref i);
                    break;
                case "--root":
                    root = Next(args, ref i);
                    break;
                case "--parent":
                    parent = Next(args, ref i);
                    break;
                case "-h":
                case "--help":
                    showHelp = true;
                    break;
            }
        }

        return new Options { Change = change, ChangeDir = changeDir, Root = root, Parent = parent, ShowHelp = showHelp };
    }

    static string? Next(string[] args, ref int index) => index + 1 < args.Length ? args[++index] : null;

    public static void PrintUsage()
    {
        Console.Error.WriteLine("Usage: dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change <change-name> [--root <repo-root>] [--parent <path>]");
        Console.Error.WriteLine("   or: dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change-dir <path> [--root <repo-root>]");
    }
}
