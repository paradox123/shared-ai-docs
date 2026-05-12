var options = Options.Parse(args);
if (options.ShowHelp)
{
    Options.PrintUsage();
    return 0;
}

var root = Path.GetFullPath(options.Root ?? Directory.GetCurrentDirectory());
var skillPaths = new[]
{
    "skills-repo/skills/spec-orchestrator/SKILL.md",
    "skills-repo/skills/child-spec-hardening/SKILL.md",
    "skills-repo/skills/spec-change-delivery/SKILL.md",
    "skills-repo/skills/spec-closeout/SKILL.md",
    "skills-repo/skills/agent-delivery-retro-review/SKILL.md"
};

var forbiddenTerms = new[]
{
    "AgentDeliverySessionLauncher",
    "AgentDeliveryVisibleSessionController",
    "ArchiveVisibleCodexAppSession",
    "WorkflowDoctor.cs --phase evidence-resolution",
    "Child Session Handoff",
    "Agent Delivery Session Launch/Queue Evidence",
    "controller_visible_multi_session",
    "visible Codex-App",
    "run-profile",
    "Run Profile"
};

var findings = new List<string>();
var warnings = new List<string>();

foreach (var relative in skillPaths)
{
    var path = Path.Combine(root, relative);
    if (!File.Exists(path))
    {
        warnings.Add($"skill-missing: {relative}");
        continue;
    }

    var text = File.ReadAllText(path);
    var forbiddenHits = forbiddenTerms.Where(term => text.Contains(term, StringComparison.OrdinalIgnoreCase)).ToArray();
    foreach (var hit in forbiddenHits)
    {
        findings.Add($"obsolete-prose-term: {relative} contains `{hit}`");
    }

    if (text.Contains("Agent Delivery", StringComparison.OrdinalIgnoreCase) &&
        !text.Contains("ValidateActiveOpenSpecScope.cs", StringComparison.Ordinal) &&
        !text.Contains("ValidateAgentDeliveryCleanup.cs", StringComparison.Ordinal))
    {
        findings.Add($"validator-command-missing: {relative} mentions Agent Delivery but not the simplified validator commands.");
    }

    var longLines = File.ReadLines(path)
        .Select((line, index) => new { line, number = index + 1 })
        .Where(item => item.line.Length > 700)
        .ToArray();
    foreach (var item in longLines)
    {
        findings.Add($"long-line: {relative}:{item.number} has {item.line.Length} characters.");
    }
}

Console.WriteLine("{");
Console.WriteLine("""  "schema_id": "agent-delivery.skill-prose-budget.v1",""");
Console.WriteLine($"""  "verdict": "{(findings.Count == 0 ? "pass" : "fail")}",""");
Console.WriteLine($"""  "root": "{JsonEscape(root)}",""");
PrintArray("findings", findings, trailingComma: true);
PrintArray("warnings", warnings, trailingComma: false);
Console.WriteLine("}");
return findings.Count == 0 ? 0 : 1;

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
    public string? Root { get; private init; }
    public bool ShowHelp { get; private init; }

    public static Options Parse(string[] args)
    {
        string? root = null;
        var showHelp = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--root":
                    root = i + 1 < args.Length ? args[++i] : null;
                    break;
                case "-h":
                case "--help":
                    showHelp = true;
                    break;
            }
        }

        return new Options { Root = root, ShowHelp = showHelp };
    }

    public static void PrintUsage()
    {
        Console.Error.WriteLine("Usage: dotnet run skills-repo/tools/ValidateSkillProseBudget.cs -- [--root <repo-root>]");
    }
}
