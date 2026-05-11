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

var launcher = new Launcher(options);
var result = await launcher.RunAsync();
return result.ExitCode;

sealed class Launcher
{
    private const string SchemaVersion = "agent-delivery.session-launch.v2";
    private readonly Options options;
    private readonly List<string> blockers = [];
    private readonly List<string> warnings = [];

    public Launcher(Options options)
    {
        this.options = options;
    }

    public async Task<RunResult> RunAsync()
    {
        var createdAt = DateTimeOffset.UtcNow;
        var handoffPath = Path.GetFullPath(options.HandoffPath!);
        var outRoot = Path.GetFullPath(options.OutPath ?? "_specs/agent-delivery-session-launches");
        var runDir = Path.Combine(outRoot, $"{createdAt:yyyyMMddTHHmmssZ}-{Slug(options.TargetId!)}");
        Directory.CreateDirectory(runDir);

        if (!File.Exists(handoffPath))
        {
            blockers.Add($"Handoff not found: {handoffPath}");
            await WriteBlockedEvidenceAsync(runDir, createdAt, handoffPath, null, null, secretBlocked: false);
            return new RunResult(1);
        }

        var handoffText = await File.ReadAllTextAsync(handoffPath);
        if (ContainsSecret(handoffText, out var secretFinding))
        {
            blockers.Add($"Secret-like content detected before prompt persistence: {secretFinding}");
            await WriteBlockedEvidenceAsync(runDir, createdAt, handoffPath, null, null, secretBlocked: true);
            return new RunResult(1);
        }

        var handoff = Handoff.Parse(handoffText, handoffPath);
        ValidateRequiredHandoff(handoff);
        ValidateTargetId(handoff, options.TargetId!);

        var controlIndexPath = ResolveControlIndexPath(handoff, handoffPath);
        MarkdownTable? controlTable = null;
        Dictionary<string, string>? controlRow = null;
        if (controlIndexPath is not null)
        {
            ValidateControlIndex(controlIndexPath, handoff, options.TargetId!, handoffPath, out controlTable, out controlRow);
            await RunChildReadinessValidatorAsync(controlIndexPath, handoff, options.TargetId!, handoffPath);
        }
        else if (handoff.TargetRole.Equals("child", StringComparison.OrdinalIgnoreCase))
        {
            blockers.Add("Child handoff is missing a usable Control Index / Queue path.");
        }

        ValidateVerdict(handoff);
        ValidateWriteSet("Handoff Allowed Write-Set", handoff.AllowedWriteSet);
        ValidateWorkspace(handoff.TargetWorkspace);

        var adapter = AdapterContract.For(options.Adapter!);
        var agent = AgentContract.For(options.Agent!, adapter);
        var command = BuildCodexCommand(handoff.TargetWorkspace, Path.Combine(runDir, "last-message.md"));
        var parentSpecAbbrevAndNumber = BuildParentSpecAbbrevAndNumber(options.TargetId!);
        var sessionStage = BuildSessionStage(handoff.NextSkill);
        var childSpecDesignation = BuildChildSpecDesignation(options.TargetId!, handoff.TargetSpec, handoff.ScopeSummary);
        var sessionTitle = BuildSessionTitle(parentSpecAbbrevAndNumber, sessionStage, childSpecDesignation);
        ValidateSessionTitle(sessionTitle);
        var initiatingProjectCwd = ResolveInitiatingProjectCwd(handoff);
        var projectCwdSource = ResolveProjectCwdSource();
        ValidateInitiatingProjectCwd(initiatingProjectCwd);

        var request = BuildLaunchRequest(
            createdAt,
            runDir,
            handoff,
            handoffPath,
            controlIndexPath,
            sessionTitle,
            parentSpecAbbrevAndNumber,
            sessionStage,
            childSpecDesignation,
            initiatingProjectCwd,
            projectCwdSource,
            agent,
            adapter,
            command);
        if (controlRow is not null)
        {
            ApplyControlRow(request, controlRow);
        }

        if (blockers.Count > 0)
        {
            request["status"] = "blocked";
            request["blockers"] = blockers;
            request["warnings"] = warnings;
            await WriteJsonAsync(Path.Combine(runDir, "evidence.json"), request);
            return new RunResult(1);
        }

        var prompt = BuildPrompt(handoff, request, sessionTitle, agent);
        var requestHasSecret = ContainsSecret(JsonSerializer.Serialize(request, JsonSupport.Options), out var requestSecret);
        var promptHasSecret = ContainsSecret(prompt, out var promptSecret);
        if (requestHasSecret || promptHasSecret)
        {
            blockers.Add($"Secret-like content detected before prompt persistence: {requestSecret ?? promptSecret}");
            request["status"] = "blocked";
            request["blockers"] = blockers;
            request["warnings"] = warnings;
            await WriteJsonAsync(Path.Combine(runDir, "evidence.json"), RedactedEvidence(request));
            return new RunResult(1);
        }

        var promptPath = Path.Combine(runDir, "start-prompt.md");
        await File.WriteAllTextAsync(promptPath, prompt, TextEncoding.Utf8NoBom);
        var promptHash = Sha256(prompt);
        ((Dictionary<string, object?>)request["evidence_paths"]!)["prompt"] = RelativeOrFull(promptPath);
        request["prompt_sha256"] = promptHash;

        var status = DetermineInitialStatus(agent, adapter);
        request["status"] = status;
        ((Dictionary<string, object?>)request["mechanism"]!)["type"] = status == "queued" ? "queue" : "manual";
        ((Dictionary<string, object?>)request["mechanism"]!)["recommended_command"] = agent.IsCodex
            ? adapter.Kind == AdapterKind.CodexAppServer
                ? $"dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff {ShellQuote(handoffPath)} --target-id {ShellQuote(options.TargetId!)} --agent codex --mode launch --adapter codex-app-server --initiating-project-cwd {ShellQuote(initiatingProjectCwd)}"
                : $"codex exec --json -C {ShellQuote(handoff.TargetWorkspace)} --output-last-message {ShellQuote(Path.Combine(runDir, "last-message.md"))} - < {ShellQuote(promptPath)}"
            : "Open a fresh session in the requested provider and paste start-prompt.md.";

        if (agent.IsCodex && (options.Mode is "launch" or "auto"))
        {
            if (!CommandExists("codex"))
            {
                warnings.Add("codex executable not found; falling back to queued start request.");
                status = options.Mode == "launch" ? "blocked" : "queued";
                request["status"] = status;
            }
            else if (options.DryRun)
            {
                status = "queued";
                request["status"] = status;
                request["dry_run"] = true;
                warnings.Add("Dry-run requested; codex exec command was not executed.");
            }
            else
            {
                if (adapter.Kind == AdapterKind.CodexAppServer)
                {
                    await LaunchCodexAppServerAsync(request, prompt, runDir, initiatingProjectCwd, sessionTitle);
                }
                else
                {
                    await LaunchCodexAsync(request, prompt, runDir, handoff.TargetWorkspace, command);
                }
            }
        }
        else if (!agent.IsCodex)
        {
            request["status"] = "manual_start_required";
            request["dry_run"] = options.DryRun;
        }

        request["blockers"] = blockers;
        request["warnings"] = warnings;
        await WriteJsonAsync(Path.Combine(runDir, "launch-request.json"), request);
        await WriteJsonAsync(Path.Combine(runDir, "evidence.json"), request);

        var finalStatus = Convert.ToString(request["status"]) ?? "failed";
        Console.WriteLine($"{finalStatus}: {runDir}");
        return new RunResult(finalStatus is "blocked" or "failed" ? 1 : 0);
    }

    private string? ResolveControlIndexPath(Handoff handoff, string handoffPath)
    {
        if (!string.IsNullOrWhiteSpace(options.ControlIndexPath))
        {
            return Path.GetFullPath(options.ControlIndexPath);
        }

        var raw = handoff.ControlIndex;
        if (string.IsNullOrWhiteSpace(raw))
        {
            return null;
        }

        raw = StripMarkdownPath(raw);
        if (string.IsNullOrWhiteSpace(raw))
        {
            return null;
        }

        if (Path.IsPathRooted(raw))
        {
            return raw;
        }

        var handoffDir = Path.GetDirectoryName(handoffPath)!;
        var candidate = Path.GetFullPath(Path.Combine(handoffDir, raw));
        if (File.Exists(candidate))
        {
            return candidate;
        }

        return Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), raw));
    }

    private static void ApplyControlRow(Dictionary<string, object?> request, Dictionary<string, string> row)
    {
        request["target_spec"] = NormalizeCell(row["Child Spec"]);
        request["current_verdict"] = NormalizeCell(row["Readiness / Hardening Verdict"]);
        request["allowed_write_set"] = SplitListCell(row["Allowed Write-Set"]);
        request["verification"] = SplitListCell(row["Verification"]);
        request["evidence_openspec"] = SplitListCell(row["OpenSpec / Ledger"] + "; " + row["Evidence / Closeout"]);
    }

    private void ValidateControlIndex(string controlIndexPath, Handoff handoff, string targetId, string handoffPath, out MarkdownTable? table, out Dictionary<string, string>? row)
    {
        table = null;
        row = null;
        if (!File.Exists(controlIndexPath))
        {
            blockers.Add($"Control Index not found: {controlIndexPath}");
            return;
        }

        table = MarkdownTable.FindRequiredTable(File.ReadAllText(controlIndexPath));
        if (table is null)
        {
            blockers.Add("Control Index does not contain the exact operational Child Index header.");
            return;
        }

        row = table.Rows.FirstOrDefault(r => CellEquals(r["Child"], targetId));
        if (row is null)
        {
            blockers.Add($"Control Index row not found for target id `{targetId}`.");
            return;
        }

        var indexHandoff = StripMarkdownPath(row["Session Handoff"]);
        if (string.IsNullOrWhiteSpace(indexHandoff))
        {
            blockers.Add("Control Index Session Handoff cell does not contain a usable path.");
        }
        else
        {
            var resolved = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(controlIndexPath)!, indexHandoff));
            if (!SamePath(resolved, handoffPath))
            {
                blockers.Add($"Control Index handoff pointer mismatch. Index points to `{resolved}`, but --handoff is `{handoffPath}`.");
            }
        }

        if (!VerdictsAgree(row["Readiness / Hardening Verdict"], handoff.CurrentVerdict))
        {
            blockers.Add($"Verdict mismatch between Control Index (`{NormalizeCell(row["Readiness / Hardening Verdict"])}`) and Handoff (`{handoff.CurrentVerdict}`).");
        }

        ValidateWriteSet("Control Index Allowed Write-Set", row["Allowed Write-Set"]);
    }

    private async Task RunChildReadinessValidatorAsync(string controlIndexPath, Handoff handoff, string targetId, string handoffPath)
    {
        if (!handoff.TargetRole.Equals("child", StringComparison.OrdinalIgnoreCase))
        {
            return;
        }

        var validator = Path.Combine(Directory.GetCurrentDirectory(), "skills-repo", "tools", "ValidateChildReadiness.cs");
        if (!File.Exists(validator))
        {
            blockers.Add($"ValidateChildReadiness.cs not found at `{validator}`.");
            return;
        }

        var psi = new ProcessStartInfo
        {
            FileName = "dotnet",
            WorkingDirectory = "/tmp",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        psi.ArgumentList.Add("run");
        psi.ArgumentList.Add(validator);
        psi.ArgumentList.Add("--");
        psi.ArgumentList.Add("--index");
        psi.ArgumentList.Add(controlIndexPath);
        psi.ArgumentList.Add("--child");
        psi.ArgumentList.Add(targetId);
        psi.ArgumentList.Add("--handoff");
        psi.ArgumentList.Add(handoffPath);
        if (!handoff.NextSkill.Contains("spec-change-delivery", StringComparison.OrdinalIgnoreCase))
        {
            psi.ArgumentList.Add("--allow-non-ready");
        }

        using var process = Process.Start(psi);
        if (process is null)
        {
            blockers.Add("Could not start ValidateChildReadiness.cs.");
            return;
        }

        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        var stdout = await stdoutTask;
        var stderr = await stderrTask;

        if (process.ExitCode != 0)
        {
            blockers.Add("ValidateChildReadiness.cs failed: " + Redact((stderr + " " + stdout).Trim(), 1200));
        }
        else if (!string.IsNullOrWhiteSpace(stdout))
        {
            warnings.Add("ValidateChildReadiness.cs passed: " + stdout.Trim());
        }
    }

    private void ValidateRequiredHandoff(Handoff handoff)
    {
        foreach (var (label, value) in new[]
        {
            ("Parent", handoff.Parent),
            ("Target ID / Child", handoff.TargetId),
            ("Target Spec / Child Spec", handoff.TargetSpec),
            ("Handoff File", handoff.HandoffFile),
            ("Target Repository / Working Directory", handoff.TargetWorkspace),
            ("Next Mode / Skill", handoff.NextSkill),
            ("Current Verdict", handoff.CurrentVerdict),
            ("Scope Summary", handoff.ScopeSummary),
            ("Non-Goals", handoff.NonGoals),
            ("Allowed Write-Set", handoff.AllowedWriteSet),
            ("Shared / Read-only Files", handoff.ReadOnlyFiles),
            ("Verification", handoff.Verification),
            ("Evidence / OpenSpec", handoff.EvidenceOpenSpec),
        })
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                blockers.Add($"Handoff is missing `{label}`.");
            }
        }
    }

    private void ValidateTargetId(Handoff handoff, string requested)
    {
        if (!handoff.TargetId.Equals(requested, StringComparison.OrdinalIgnoreCase))
        {
            blockers.Add($"Target-ID mismatch. CLI requested `{requested}`, handoff says `{handoff.TargetId}`.");
        }

        var fileText = Path.GetFileNameWithoutExtension(handoff.SourcePath).ToLowerInvariant();
        var idsInName = Regex.Matches(fileText, @"[a-z]+-[a-z0-9]+(?:-[a-z0-9]+)*")
            .Select(m => m.Value.ToUpperInvariant())
            .Where(v => v.StartsWith("DWT-", StringComparison.Ordinal))
            .ToArray();
        if (idsInName.Length > 0 && !idsInName.Contains(requested.ToUpperInvariant()))
        {
            blockers.Add($"Target-ID mismatch. Handoff filename suggests `{string.Join(", ", idsInName)}`, CLI requested `{requested}`.");
        }
    }

    private void ValidateVerdict(Handoff handoff)
    {
        var nextSkill = handoff.NextSkill;
        var verdict = handoff.CurrentVerdict;
        if (nextSkill.Contains("spec-change-delivery", StringComparison.OrdinalIgnoreCase) &&
            !ContainsVerdict(verdict, "IMPLEMENTATION READY") &&
            !ContainsVerdict(verdict, "READY WITH NON-BLOCKING NOTES"))
        {
            blockers.Add("`spec-change-delivery` requires `IMPLEMENTATION READY` or accepted `READY WITH NON-BLOCKING NOTES`.");
        }

        if (nextSkill.Contains("child-spec-hardening", StringComparison.OrdinalIgnoreCase) &&
            !(verdict.Contains("needs_hardening", StringComparison.OrdinalIgnoreCase) ||
              verdict.Contains("ready_candidate", StringComparison.OrdinalIgnoreCase) ||
              verdict.Contains("NEEDS HARDENING", StringComparison.OrdinalIgnoreCase) ||
              verdict.Contains("blocker", StringComparison.OrdinalIgnoreCase)))
        {
            blockers.Add("`child-spec-hardening` requires a hardening-capable verdict such as `needs_hardening`, `ready_candidate`, `NEEDS HARDENING`, or an explicit blocker.");
        }
    }

    private void ValidateWriteSet(string label, string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            blockers.Add($"{label} is missing.");
            return;
        }

        var forbidden = new[] { "voraussichtlich", "likely", "probably", "expected", "tbd", "to be decided", "as needed", "related files", "and related", "etc.", "etc" };
        foreach (var term in forbidden)
        {
            if (value.Contains(term, StringComparison.OrdinalIgnoreCase))
            {
                blockers.Add($"{label} is approximate/advisory because it contains `{term}`.");
            }
        }

        if (!Regex.IsMatch(value, @"[\w.-]+/[\w./*{} -]+"))
        {
            blockers.Add($"{label} must name concrete paths, directories, or glob patterns.");
        }
    }

    private void ValidateWorkspace(string workspace)
    {
        var path = StripBackticks(workspace);
        if (!Path.IsPathRooted(path))
        {
            blockers.Add($"Target workspace must be an absolute path: {workspace}");
            return;
        }

        if (!Directory.Exists(path))
        {
            blockers.Add($"Target workspace does not exist: {path}");
        }
    }

    private void ValidateSessionTitle(string title)
    {
        if (string.IsNullOrWhiteSpace(title) || title.Length > 80 || title.Contains('\n') || title.Contains('\r'))
        {
            blockers.Add($"Invalid session_title `{title}`; it must be non-empty, one line and at most 80 chars.");
        }
    }

    private Dictionary<string, object?> BuildLaunchRequest(
        DateTimeOffset createdAt,
        string runDir,
        Handoff handoff,
        string handoffPath,
        string? controlIndexPath,
        string sessionTitle,
        string parentSpecAbbrevAndNumber,
        string sessionStage,
        string childSpecDesignation,
        string initiatingProjectCwd,
        string projectCwdSource,
        AgentContract agent,
        AdapterContract adapter,
        string[] command)
    {
        var promptPath = Path.Combine(runDir, "start-prompt.md");
        var eventsPath = Path.Combine(runDir, "agent-events.jsonl");
        var lastMessagePath = Path.Combine(runDir, "last-message.md");
        var transcriptPath = Path.Combine(runDir, "app-server-transcript.jsonl");
        var executionChannel = adapter.ExecutionChannel;
        return new Dictionary<string, object?>
        {
            ["schema_version"] = SchemaVersion,
            ["status"] = "queued",
            ["execution_channel"] = executionChannel,
            ["adapter_id"] = adapter.AdapterId,
            ["created_at"] = createdAt.ToString("O"),
            ["started_at"] = null,
            ["completed_at"] = null,
            ["parent"] = handoff.Parent,
            ["target_id"] = options.TargetId!,
            ["target_role"] = handoff.TargetRole,
            ["target_spec"] = handoff.TargetSpec,
            ["control_index"] = controlIndexPath is null ? handoff.ControlIndex : RelativeOrFull(controlIndexPath),
            ["handoff_path"] = RelativeOrFull(handoffPath),
            ["initiating_project_cwd"] = initiatingProjectCwd,
            ["target_workspace"] = StripBackticks(handoff.TargetWorkspace),
            ["project_cwd_source"] = projectCwdSource,
            ["project_cwd"] = StripBackticks(handoff.TargetWorkspace),
            ["parent_spec_abbrev_and_number"] = parentSpecAbbrevAndNumber,
            ["session_stage"] = sessionStage,
            ["child_spec_designation"] = childSpecDesignation,
            ["session_title"] = sessionTitle,
            ["next_skill"] = handoff.NextSkill,
            ["next_mode"] = handoff.NextMode,
            ["current_verdict"] = handoff.CurrentVerdict,
            ["scope_summary"] = handoff.ScopeSummary,
            ["non_goals"] = SplitListCell(handoff.NonGoals),
            ["allowed_write_set"] = SplitListCell(handoff.AllowedWriteSet),
            ["read_only_files"] = SplitListCell(handoff.ReadOnlyFiles),
            ["verification"] = SplitListCell(handoff.Verification),
            ["evidence_openspec"] = SplitListCell(handoff.EvidenceOpenSpec),
            ["open_notes"] = SplitListCell(handoff.OpenNotes),
            ["fresh_session_required"] = true,
            ["agent"] = new Dictionary<string, object?>
            {
                ["requested_provider"] = options.Agent,
                ["adapter_id"] = agent.AdapterId,
                ["adapter_status"] = agent.AdapterStatus,
                ["launch_capability"] = agent.LaunchCapability,
                ["command_contract"] = agent.CommandContract,
            },
            ["mechanism"] = new Dictionary<string, object?>
            {
                ["type"] = "queue",
                ["recommended_command"] = null,
                ["actual_command"] = null,
                ["adapter_available"] = agent.IsCodex && CommandExists("codex"),
            },
            ["evidence_paths"] = new Dictionary<string, object?>
            {
                ["prompt"] = RelativeOrFull(promptPath),
                ["events"] = options.Mode == "launch" && agent.IsCodex && adapter.Kind == AdapterKind.CodexExec ? RelativeOrFull(eventsPath) : null,
                ["last_message"] = options.Mode == "launch" && agent.IsCodex && adapter.Kind == AdapterKind.CodexExec ? RelativeOrFull(lastMessagePath) : null,
                ["app_server_transcript"] = adapter.Kind == AdapterKind.CodexAppServer ? RelativeOrFull(transcriptPath) : null,
            },
            ["session_visibility"] = NewSessionVisibility(adapter),
            ["app_server"] = NewAppServerEvidence(adapter, transcriptPath),
            ["codex_app"] = new Dictionary<string, object?>
            {
                ["visibility_status"] = "not_applicable",
                ["thread_id"] = null,
                ["rollout_path"] = null,
                ["thread_source"] = null,
                ["thread_cwd_observed"] = null,
                ["thread_title_observed"] = null,
                ["title_status"] = "not_applicable",
            },
            ["blockers"] = blockers,
            ["warnings"] = warnings,
        };
    }

    private string BuildPrompt(Handoff handoff, Dictionary<string, object?> request, string sessionTitle, AgentContract agent)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"Session Title: {sessionTitle}");
        sb.AppendLine();
        sb.AppendLine($"Wir arbeiten in {StripBackticks(handoff.TargetWorkspace)}.");
        sb.AppendLine();
        sb.AppendLine("Starte eine frische Agent-Delivery-Session aus folgendem persistierten Handoff.");
        sb.AppendLine();
        sb.AppendLine("Pflicht: Lies zuerst das Handoff, den Control Index / die Queue und das Target-Artefakt. Validiere, dass Target-ID, Target-Rolle, Handoff-Pfad, Control Index, aktueller Verdict, Target Workspace und Allowed Write-Set konsistent sind. Arbeite nur im erlaubten Write-Set. Wenn ein Gate stale, widerspruechlich oder unvollstaendig ist, stoppe mit NOT READY und persistiere Evidence statt zu implementieren.");
        sb.AppendLine();
        sb.AppendLine($"- Parent: {handoff.Parent}");
        sb.AppendLine($"- Target ID: {request["target_id"]}");
        sb.AppendLine($"- Target Role: {request["target_role"]}");
        sb.AppendLine($"- Target Spec: {request["target_spec"]}");
        sb.AppendLine($"- Control Index / Queue: {request["control_index"]}");
        sb.AppendLine($"- Handoff File: {request["handoff_path"]}");
        sb.AppendLine($"- Target Repository / Working Directory: {request["target_workspace"]}");
        sb.AppendLine($"- Initiating Project CWD / App-Kontext: {request["initiating_project_cwd"]}");
        sb.AppendLine($"- Target Workspace: {request["target_workspace"]}");
        sb.AppendLine($"- Session Title: {sessionTitle}");
        sb.AppendLine($"- Next Mode / Skill: {handoff.NextSkill}");
        sb.AppendLine($"- Requested Agent Provider: {options.Agent}");
        sb.AppendLine($"- Agent Adapter Status: {agent.AdapterStatus}; {agent.AdapterId}");
        sb.AppendLine($"- Current Verdict: {request["current_verdict"]}");
        sb.AppendLine($"- Scope Summary: {handoff.ScopeSummary}");
        sb.AppendLine($"- Non-Goals: {handoff.NonGoals}");
        sb.AppendLine($"- Allowed Write-Set: {handoff.AllowedWriteSet}");
        sb.AppendLine($"- Shared / Read-only Files: {handoff.ReadOnlyFiles}");
        sb.AppendLine($"- Verification Commands: {handoff.Verification}");
        sb.AppendLine($"- Evidence / OpenSpec: {handoff.EvidenceOpenSpec}");
        sb.AppendLine($"- Open Notes: {handoff.OpenNotes}");
        sb.AppendLine();
        sb.AppendLine("## Persisted Handoff");
        sb.AppendLine();
        sb.AppendLine(handoff.RawText.TrimEnd());
        sb.AppendLine();
        return sb.ToString();
    }

    private string DetermineInitialStatus(AgentContract agent, AdapterContract adapter)
    {
        if (!agent.IsCodex)
        {
            return "manual_start_required";
        }

        if (options.Mode is "queue")
        {
            return "queued";
        }

        if (options.DryRun)
        {
            return "queued";
        }

        return "queued";
    }

    private async Task LaunchCodexAsync(Dictionary<string, object?> request, string prompt, string runDir, string workspace, string[] command)
    {
        var startedAt = DateTimeOffset.UtcNow;
        request["started_at"] = startedAt.ToString("O");
        ((Dictionary<string, object?>)request["mechanism"]!)["type"] = "launch";
        ((Dictionary<string, object?>)request["mechanism"]!)["actual_command"] = string.Join(" ", command.Select(ShellQuote));

        var eventsPath = Path.Combine(runDir, "agent-events.jsonl");
        var psi = new ProcessStartInfo
        {
            FileName = command[0],
            WorkingDirectory = workspace,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        foreach (var arg in command.Skip(1))
        {
            psi.ArgumentList.Add(arg);
        }

        using var process = Process.Start(psi);
        if (process is null)
        {
            request["status"] = "failed";
            blockers.Add("Failed to start codex process.");
            return;
        }

        await process.StandardInput.WriteAsync(prompt);
        process.StandardInput.Close();
        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        var stdout = await stdoutTask;
        var stderr = await stderrTask;
        await File.WriteAllTextAsync(eventsPath, stdout, TextEncoding.Utf8NoBom);
        request["completed_at"] = DateTimeOffset.UtcNow.ToString("O");
        request["exit_code"] = process.ExitCode;
        request["stderr_excerpt"] = Redact(stderr, 2000);
        request["status"] = process.ExitCode == 0 ? "launched" : "failed";
        request["execution_channel"] = "headless_cli";
        request["adapter_id"] = "codex-cli";
        request["session_visibility"] = new Dictionary<string, object?>
        {
            ["class"] = "headless_cli_session",
            ["visible_in_codex_app"] = false,
            ["proof_status"] = "not_visible",
            ["proof_method"] = "codex_exec_downgrade",
            ["thread_id"] = null,
            ["thread_source_observed"] = null,
            ["source_kind_observed"] = null,
            ["cwd_observed"] = null,
            ["title_observed"] = null,
            ["rollout_path"] = null,
            ["sidebar_or_default_list_observed"] = false,
        };
        ((Dictionary<string, object?>)request["evidence_paths"]!)["events"] = RelativeOrFull(eventsPath);
        ((Dictionary<string, object?>)request["evidence_paths"]!)["last_message"] = RelativeOrFull(Path.Combine(runDir, "last-message.md"));

        var codexApp = await CodexAppInspector.TryInspectAsync(workspace, startedAt, Convert.ToString(request["session_title"]) ?? "");
        request["codex_app"] = codexApp;
        if (Convert.ToString(codexApp["visibility_status"]) == "wrong_project")
        {
            warnings.Add("Codex thread metadata was found, but it points at a different project cwd.");
        }
    }

    private async Task LaunchCodexAppServerAsync(Dictionary<string, object?> request, string prompt, string runDir, string initiatingProjectCwd, string sessionTitle)
    {
        var startedAt = DateTimeOffset.UtcNow;
        request["started_at"] = startedAt.ToString("O");
        request["status"] = "launched";
        ((Dictionary<string, object?>)request["mechanism"]!)["type"] = "launch";
        ((Dictionary<string, object?>)request["mechanism"]!)["actual_command"] = "codex app-server --listen stdio://";

        var transcriptPath = Path.Combine(runDir, "app-server-transcript.jsonl");
        var stderrPath = Path.Combine(runDir, "app-server-stderr.log");
        try
        {
            var result = await CodexAppServerJsonRpcClient.LaunchVisibleSessionAsync(new AppServerLaunchRequest
            {
                Cwd = initiatingProjectCwd,
                Prompt = prompt,
                SessionTitle = sessionTitle,
                TranscriptPath = transcriptPath,
                StderrPath = stderrPath,
                Timeout = TimeSpan.FromMinutes(options.AppServerTimeoutMinutes),
                RequestTimeout = TimeSpan.FromSeconds(options.AppServerRequestTimeoutSeconds),
            });

            request["completed_at"] = DateTimeOffset.UtcNow.ToString("O");
            request["app_server"] = new Dictionary<string, object?>
            {
                ["listen"] = "stdio://",
                ["request_timeout_seconds"] = options.AppServerRequestTimeoutSeconds,
                ["thread_start_observed"] = result.ThreadStartObserved,
                ["thread_name_set_observed"] = result.ThreadNameSetObserved,
                ["turn_start_observed"] = result.TurnStartObserved,
                ["turn_completed_status"] = result.TurnCompletedStatus,
                ["thread_list_observed"] = result.ThreadListObserved,
                ["transcript_path"] = RelativeOrFull(transcriptPath),
                ["stderr_path"] = File.Exists(stderrPath) ? RelativeOrFull(stderrPath) : null,
            };
            ((Dictionary<string, object?>)request["evidence_paths"]!)["app_server_transcript"] = RelativeOrFull(transcriptPath);

            var verified = result.Visible &&
                           SamePath(result.CwdObserved ?? "", initiatingProjectCwd) &&
                           string.Equals(result.TitleObserved, sessionTitle, StringComparison.Ordinal) &&
                           result.TurnCompletedStatus == "completed";
            request["status"] = verified ? "launched" : "failed";
            if (!verified)
            {
                blockers.Add("App-server launch completed, but visibility proof did not satisfy thread/list cwd/title/turn requirements.");
            }

            request["session_visibility"] = new Dictionary<string, object?>
            {
                ["class"] = verified ? "visible_codex_app_session" : "visibility_proof_failed",
                ["visible_in_codex_app"] = verified,
                ["proof_status"] = verified ? "verified" : "failed",
                ["proof_method"] = "app_server_thread_list",
                ["thread_id"] = result.ThreadId,
                ["thread_source_observed"] = result.ThreadSourceObserved,
                ["source_kind_observed"] = result.SourceKindObserved,
                ["cwd_observed"] = result.CwdObserved,
                ["title_observed"] = result.TitleObserved,
                ["rollout_path"] = result.RolloutPath,
                ["sidebar_or_default_list_observed"] = result.DefaultListObserved,
            };
        }
        catch (AppServerPhaseTimeoutException ex)
        {
            request["completed_at"] = DateTimeOffset.UtcNow.ToString("O");
            request["status"] = "blocked";
            blockers.Add($"codex app-server adapter timed out during `{ex.Method}` after {ex.Timeout.TotalSeconds:0} seconds.");
            request["app_server"] = new Dictionary<string, object?>
            {
                ["listen"] = "stdio://",
                ["request_timeout_seconds"] = options.AppServerRequestTimeoutSeconds,
                ["failure_phase"] = ex.Phase,
                ["failure_method"] = ex.Method,
                ["thread_start_observed"] = false,
                ["thread_name_set_observed"] = false,
                ["turn_start_observed"] = false,
                ["turn_completed_status"] = "blocked",
                ["thread_list_observed"] = false,
                ["transcript_path"] = File.Exists(transcriptPath) ? RelativeOrFull(transcriptPath) : null,
                ["stderr_path"] = File.Exists(stderrPath) ? RelativeOrFull(stderrPath) : null,
            };
            ((Dictionary<string, object?>)request["evidence_paths"]!)["app_server_transcript"] = File.Exists(transcriptPath) ? RelativeOrFull(transcriptPath) : null;
            request["session_visibility"] = new Dictionary<string, object?>
            {
                ["class"] = "app_server_blocked",
                ["visible_in_codex_app"] = false,
                ["proof_status"] = "blocked",
                ["proof_method"] = "app_server_thread_list",
                ["thread_id"] = null,
                ["thread_source_observed"] = null,
                ["source_kind_observed"] = null,
                ["cwd_observed"] = null,
                ["title_observed"] = null,
                ["rollout_path"] = null,
                ["sidebar_or_default_list_observed"] = false,
            };
        }
        catch (Exception ex)
        {
            request["completed_at"] = DateTimeOffset.UtcNow.ToString("O");
            request["status"] = "blocked";
            blockers.Add("codex app-server adapter failed: " + Redact(ex.Message, 1000));
            request["app_server"] = new Dictionary<string, object?>
            {
                ["listen"] = "stdio://",
                ["request_timeout_seconds"] = options.AppServerRequestTimeoutSeconds,
                ["failure_phase"] = "app_server_adapter_exception",
                ["thread_start_observed"] = false,
                ["thread_name_set_observed"] = false,
                ["turn_start_observed"] = false,
                ["turn_completed_status"] = "blocked",
                ["thread_list_observed"] = false,
                ["transcript_path"] = File.Exists(transcriptPath) ? RelativeOrFull(transcriptPath) : null,
                ["stderr_path"] = File.Exists(stderrPath) ? RelativeOrFull(stderrPath) : null,
            };
            request["session_visibility"] = new Dictionary<string, object?>
            {
                ["class"] = "app_server_blocked",
                ["visible_in_codex_app"] = false,
                ["proof_status"] = "blocked",
                ["proof_method"] = "app_server_thread_list",
                ["thread_id"] = null,
                ["thread_source_observed"] = null,
                ["source_kind_observed"] = null,
                ["cwd_observed"] = null,
                ["title_observed"] = null,
                ["rollout_path"] = null,
                ["sidebar_or_default_list_observed"] = false,
            };
        }
    }

    private async Task WriteBlockedEvidenceAsync(string runDir, DateTimeOffset createdAt, string handoffPath, Handoff? handoff, string? controlIndexPath, bool secretBlocked)
    {
        var evidence = new Dictionary<string, object?>
        {
            ["schema_version"] = SchemaVersion,
            ["status"] = "blocked",
            ["created_at"] = createdAt.ToString("O"),
            ["handoff_path"] = RelativeOrFull(handoffPath),
            ["target_id"] = options.TargetId,
            ["control_index"] = controlIndexPath,
            ["agent"] = new Dictionary<string, object?>
            {
                ["requested_provider"] = options.Agent,
                ["adapter_id"] = AdapterContract.For(options.Adapter!).AdapterId,
                ["adapter_status"] = "blocked_before_adapter_selection",
            },
            ["secret_guard_blocked_prompt_persistence"] = secretBlocked,
            ["blockers"] = blockers.Select(b => Redact(b, 500)).ToArray(),
            ["warnings"] = warnings,
        };
        await WriteJsonAsync(Path.Combine(runDir, "evidence.json"), evidence);
    }

    private static Dictionary<string, object?> RedactedEvidence(Dictionary<string, object?> request)
    {
        var copy = new Dictionary<string, object?>(request);
        copy.Remove("scope_summary");
        copy["secret_guard_blocked_prompt_persistence"] = true;
        return copy;
    }

    private static Dictionary<string, object?> NewSessionVisibility(AdapterContract adapter)
    {
        if (adapter.Kind == AdapterKind.CodexExec)
        {
            return new Dictionary<string, object?>
            {
                ["class"] = "queued_manual_start",
                ["visible_in_codex_app"] = false,
                ["proof_status"] = "not_visible",
                ["proof_method"] = "not_applicable",
                ["thread_id"] = null,
                ["thread_source_observed"] = null,
                ["source_kind_observed"] = null,
                ["cwd_observed"] = null,
                ["title_observed"] = null,
                ["rollout_path"] = null,
                ["sidebar_or_default_list_observed"] = false,
            };
        }

        return new Dictionary<string, object?>
        {
            ["class"] = "pending_app_server_visibility",
            ["visible_in_codex_app"] = false,
            ["proof_status"] = "pending",
            ["proof_method"] = "app_server_thread_list",
            ["thread_id"] = null,
            ["thread_source_observed"] = null,
            ["source_kind_observed"] = null,
            ["cwd_observed"] = null,
            ["title_observed"] = null,
            ["rollout_path"] = null,
            ["sidebar_or_default_list_observed"] = false,
        };
    }

    private static Dictionary<string, object?> NewAppServerEvidence(AdapterContract adapter, string transcriptPath)
    {
        return new Dictionary<string, object?>
        {
            ["listen"] = "stdio://",
            ["thread_start_observed"] = false,
            ["thread_name_set_observed"] = false,
            ["turn_start_observed"] = false,
            ["turn_completed_status"] = "not_started",
            ["thread_list_observed"] = false,
            ["transcript_path"] = adapter.Kind == AdapterKind.CodexAppServer ? RelativeOrFull(transcriptPath) : null,
        };
    }

    private static string BuildSessionTitle(string parentSpecAbbrevAndNumber, string sessionStage, string childSpecDesignation)
    {
        var title = $"{parentSpecAbbrevAndNumber}: {sessionStage} - {childSpecDesignation}".Trim();
        return title.Length <= 80 ? title : title[..80].Trim();
    }

    private static string BuildParentSpecAbbrevAndNumber(string targetId)
    {
        var match = Regex.Match(targetId, @"^(?<prefix>[A-Z][A-Z0-9-]*?)-S\d+$", RegexOptions.IgnoreCase);
        if (match.Success)
        {
            return match.Groups["prefix"].Value.ToUpperInvariant() + "-1";
        }

        return targetId.ToUpperInvariant();
    }

    private static string BuildSessionStage(string nextSkill)
    {
        if (nextSkill.Contains("child-spec-hardening", StringComparison.OrdinalIgnoreCase))
        {
            return "Hardening";
        }

        return "Implementation";
    }

    private static string BuildChildSpecDesignation(string targetId, string targetSpec, string scope)
    {
        var raw = Path.GetFileNameWithoutExtension(StripMarkdownPath(targetSpec));
        var index = raw.IndexOf(targetId, StringComparison.OrdinalIgnoreCase);
        if (index >= 0)
        {
            raw = raw[index..];
        }
        else
        {
            raw = $"{targetId} {scope}";
        }

        raw = Regex.Replace(raw, @"^\d{4}-\d{2}-\d{2}\s+", "");
        raw = Regex.Replace(raw, @"\s+", " ").Trim();
        raw = Regex.Replace(raw, @"\bVisible App\b", "Visible-App", RegexOptions.IgnoreCase);
        return raw;
    }

    private string ResolveInitiatingProjectCwd(Handoff handoff)
    {
        if (!string.IsNullOrWhiteSpace(options.InitiatingProjectCwd))
        {
            return Path.GetFullPath(options.InitiatingProjectCwd);
        }

        var cwd = Directory.GetCurrentDirectory();
        if (Path.IsPathRooted(cwd) && Directory.Exists(cwd))
        {
            return Path.GetFullPath(cwd);
        }

        return Path.GetFullPath(StripBackticks(handoff.TargetWorkspace));
    }

    private string ResolveProjectCwdSource()
    {
        if (!string.IsNullOrWhiteSpace(options.InitiatingProjectCwd))
        {
            return "explicit_cli_arg";
        }

        return "current_thread_cwd";
    }

    private void ValidateInitiatingProjectCwd(string initiatingProjectCwd)
    {
        if (!Path.IsPathRooted(initiatingProjectCwd))
        {
            blockers.Add($"Initiating project cwd must be absolute: {initiatingProjectCwd}");
            return;
        }

        if (!Directory.Exists(initiatingProjectCwd))
        {
            blockers.Add($"Initiating project cwd does not exist: {initiatingProjectCwd}");
        }
    }

    private static string[] BuildCodexCommand(string workspace, string lastMessagePath) =>
        ["codex", "exec", "--json", "-C", StripBackticks(workspace), "--output-last-message", lastMessagePath, "-"];

    private static bool CommandExists(string command)
    {
        try
        {
            using var process = Process.Start(new ProcessStartInfo
            {
                FileName = "/usr/bin/env",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                ArgumentList = { "sh", "-lc", $"command -v {ShellQuote(command)}" }
            });
            process!.WaitForExit();
            return process.ExitCode == 0;
        }
        catch
        {
            return false;
        }
    }

    private static bool ContainsSecret(string text, out string? finding)
    {
        var patterns = new Dictionary<string, string>
        {
            ["Authorization bearer header"] = @"Authorization:\s*Bearer\s+[A-Za-z0-9._~+/=-]{8,}",
            ["password assignment"] = @"(?i)\bpassword\s*=\s*[^;\s]{4,}",
            ["private key block"] = @"-----BEGIN [A-Z ]*PRIVATE KEY-----",
            ["OpenAI API key"] = @"sk-[A-Za-z0-9]{20,}",
            ["generic token assignment"] = @"(?i)\b(api[_-]?key|token|secret)\s*=\s*['""]?[A-Za-z0-9._~+/=-]{12,}",
            [".env style value"] = @"(?m)^[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY)=[^\s#]{8,}$",
        };

        foreach (var (label, pattern) in patterns)
        {
            if (Regex.IsMatch(text, pattern))
            {
                finding = label;
                return true;
            }
        }

        finding = null;
        return false;
    }

    private static string Sha256(string text)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(text));
        return Convert.ToHexString(bytes).ToLowerInvariant();
    }

    private static Task WriteJsonAsync(string path, object value)
    {
        var json = JsonSerializer.Serialize(value, JsonSupport.Options);
        return File.WriteAllTextAsync(path, json + Environment.NewLine, TextEncoding.Utf8NoBom);
    }

    private static string RelativeOrFull(string path)
    {
        var full = Path.GetFullPath(path);
        var cwd = Path.GetFullPath(Directory.GetCurrentDirectory());
        return full.StartsWith(cwd + Path.DirectorySeparatorChar, StringComparison.Ordinal)
            ? Path.GetRelativePath(cwd, full)
            : full;
    }

    private static string ShellQuote(string value) => "'" + value.Replace("'", "'\"'\"'") + "'";

    private static string Slug(string value) => Regex.Replace(value.ToLowerInvariant(), @"[^a-z0-9-]+", "-").Trim('-');

    private static bool SamePath(string left, string right) =>
        string.Equals(Path.GetFullPath(left).TrimEnd(Path.DirectorySeparatorChar), Path.GetFullPath(right).TrimEnd(Path.DirectorySeparatorChar), StringComparison.Ordinal);

    private static bool CellEquals(string left, string right) =>
        NormalizeCell(left).Equals(right.Trim(), StringComparison.OrdinalIgnoreCase);

    private static bool VerdictsAgree(string left, string right)
    {
        foreach (var verdict in new[] { "IMPLEMENTATION READY", "READY WITH NON-BLOCKING NOTES", "NEEDS HARDENING", "NEEDS PARENT/ORCHESTRATOR SYNC", "NEEDS USER DECISION", "ACCEPTED" })
        {
            if (ContainsVerdict(left, verdict) && ContainsVerdict(right, verdict))
            {
                return true;
            }
        }
        return false;
    }

    private static bool ContainsVerdict(string value, string verdict) =>
        value.Contains(verdict, StringComparison.OrdinalIgnoreCase);

    private static string NormalizeCell(string value) =>
        StripBackticks(value)
            .Replace("<br>", "; ", StringComparison.OrdinalIgnoreCase)
            .Replace("<br/>", "; ", StringComparison.OrdinalIgnoreCase)
            .Replace("<br />", "; ", StringComparison.OrdinalIgnoreCase)
            .Trim();

    private static string StripMarkdownPath(string value)
    {
        value = NormalizeCell(value);
        var markdownLink = Regex.Match(value, @"\[[^\]]+\]\(([^)]+)\)");
        if (markdownLink.Success) return markdownLink.Groups[1].Value.Trim();

        var codePath = Regex.Match(value, @"`([^`]+)`");
        if (codePath.Success) return codePath.Groups[1].Value.Trim();

        var sectionIndex = value.IndexOf(" section ", StringComparison.OrdinalIgnoreCase);
        if (sectionIndex >= 0) value = value[..sectionIndex];
        return value.Trim();
    }

    private static string StripBackticks(string value) => value.Replace("`", "").Trim();

    private static List<string> SplitListCell(string value)
    {
        value = NormalizeCell(value);
        if (string.IsNullOrWhiteSpace(value))
        {
            return [];
        }
        return value.Split(';', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries).ToList();
    }

    private static string Redact(string text, int maxLength)
    {
        text = Regex.Replace(text, @"Authorization:\s*Bearer\s+[^\s]+", "Authorization: Bearer [REDACTED]", RegexOptions.IgnoreCase);
        text = Regex.Replace(text, @"(?i)(password|token|secret|api[_-]?key)\s*=\s*[^\s;]+", "$1=[REDACTED]");
        return text.Length <= maxLength ? text : text[..maxLength];
    }
}

sealed record RunResult(int ExitCode);

sealed class Options
{
    public string? HandoffPath { get; private init; }
    public string? TargetId { get; private init; }
    public string? Agent { get; private init; } = "codex";
    public string Mode { get; private init; } = "queue";
    public string? Adapter { get; private init; } = "codex-exec";
    public string? InitiatingProjectCwd { get; private init; }
    public int AppServerTimeoutMinutes { get; private init; } = 30;
    public int AppServerRequestTimeoutSeconds { get; private init; } = 60;
    public string? OutPath { get; private init; }
    public string? ControlIndexPath { get; private init; }
    public bool DryRun { get; private init; }
    public bool ShowHelp { get; private init; }
    public bool IsValid => !string.IsNullOrWhiteSpace(HandoffPath) &&
                           !string.IsNullOrWhiteSpace(TargetId) &&
                           !string.IsNullOrWhiteSpace(Agent) &&
                           (Mode is "queue" or "launch" or "auto") &&
                           (Adapter is "codex-exec" or "codex-app-server") &&
                           AppServerTimeoutMinutes > 0 &&
                           AppServerRequestTimeoutSeconds > 0;

    public static Options Parse(string[] args)
    {
        string? handoff = null;
        string? targetId = null;
        string? agent = "codex";
        string mode = "queue";
        string adapter = "codex-exec";
        string? initiatingProjectCwd = null;
        var appServerTimeoutMinutes = 30;
        var appServerRequestTimeoutSeconds = 60;
        string? outPath = null;
        string? controlIndex = null;
        var dryRun = false;
        var showHelp = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--help":
                case "-h":
                    showHelp = true;
                    break;
                case "--handoff" when i + 1 < args.Length:
                    handoff = args[++i];
                    break;
                case "--target-id" when i + 1 < args.Length:
                    targetId = args[++i];
                    break;
                case "--agent" when i + 1 < args.Length:
                    agent = args[++i];
                    break;
                case "--mode" when i + 1 < args.Length:
                    mode = args[++i];
                    break;
                case "--adapter" when i + 1 < args.Length:
                    adapter = args[++i];
                    break;
                case "--initiating-project-cwd" when i + 1 < args.Length:
                    initiatingProjectCwd = args[++i];
                    break;
                case "--app-server-timeout-minutes" when i + 1 < args.Length && int.TryParse(args[i + 1], out var timeout):
                    appServerTimeoutMinutes = timeout;
                    i++;
                    break;
                case "--app-server-request-timeout-seconds" when i + 1 < args.Length && int.TryParse(args[i + 1], out var requestTimeout):
                    appServerRequestTimeoutSeconds = requestTimeout;
                    i++;
                    break;
                case "--out" when i + 1 < args.Length:
                    outPath = args[++i];
                    break;
                case "--control-index" when i + 1 < args.Length:
                    controlIndex = args[++i];
                    break;
                case "--dry-run":
                    dryRun = true;
                    break;
            }
        }

        return new Options
        {
            HandoffPath = handoff,
            TargetId = targetId,
            Agent = agent,
            Mode = mode,
            Adapter = adapter,
            InitiatingProjectCwd = initiatingProjectCwd,
            AppServerTimeoutMinutes = appServerTimeoutMinutes,
            AppServerRequestTimeoutSeconds = appServerRequestTimeoutSeconds,
            OutPath = outPath,
            ControlIndexPath = controlIndex,
            DryRun = dryRun,
            ShowHelp = showHelp
        };
    }

    public static void PrintUsage()
    {
        Console.WriteLine("""
        Usage:
          dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff <path> --target-id <id> [options]

        Options:
          --agent <provider>        Agent provider. Defaults to codex. v1 launches only codex.
          --mode <queue|launch|auto>
                                   queue writes launch artifacts, launch executes supported adapter, auto launches when possible.
          --adapter <codex-exec|codex-app-server>
                                   codex-exec is headless CLI evidence; codex-app-server starts a visible app-server-backed thread.
          --initiating-project-cwd <path>
                                   CWD used for app-server thread/start. Defaults to the current directory.
          --app-server-timeout-minutes <minutes>
                                   Timeout for app-server turn completion. Defaults to 30.
          --app-server-request-timeout-seconds <seconds>
                                   Timeout for individual app-server JSON-RPC requests such as initialize. Defaults to 60.
          --control-index <path>    Override Control Index path from the handoff.
          --out <dir>               Output root. Defaults to _specs/agent-delivery-session-launches.
          --dry-run                 Persist launch command/evidence without executing codex.
          --help                    Show this help.
        """);
    }
}

sealed class Handoff
{
    public required string SourcePath { get; init; }
    public required string RawText { get; init; }
    public required Dictionary<string, string> Fields { get; init; }
    public string Parent => Get("Parent");
    public string TargetId => GetOrDefault("", "Target ID", "Stable Child ID", "Child");
    public string TargetRole => Has("Child") || Has("Stable Child ID") || Has("Child Spec") ? "child" : GetOrDefault("workflow-step", "Target Role");
    public string TargetSpec => GetOrDefault("", "Target Spec", "Child Spec");
    public string ControlIndex => GetOrDefault("", "Control Index / Queue", "Child Index / Queue");
    public string HandoffFile => Get("Handoff File");
    public string TargetWorkspace => GetOrDefault("", "Target Repository / Working Directory", "Target Workspace");
    public string NextSkill => GetOrDefault("", "Next Mode / Skill", "Naechster Modus/Skill", "Nächster Modus/Skill");
    public string NextMode => NextSkill;
    public string CurrentVerdict => GetOrDefault("", "Current Verdict", "Aktueller Verdict");
    public string ScopeSummary => Get("Scope Summary");
    public string NonGoals => Get("Non-Goals");
    public string AllowedWriteSet => Get("Allowed Write-Set");
    public string ReadOnlyFiles => GetOrDefault("", "Shared / Read-only Files", "Read-only Files");
    public string Verification => GetOrDefault("", "Verification Commands", "Verification Lifecycle");
    public string EvidenceOpenSpec => Get("Evidence / OpenSpec");
    public string OpenNotes => GetOrDefault("None.", "Offene Blocker oder non-blocking Notes", "Open Notes");

    public static Handoff Parse(string text, string sourcePath)
    {
        var fields = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        var lines = text.Replace("\r\n", "\n").Split('\n');
        string? currentMultiline = null;
        var multiline = new StringBuilder();

        void Flush()
        {
            if (currentMultiline is not null)
            {
                fields[currentMultiline] = multiline.ToString().Trim();
                currentMultiline = null;
                multiline.Clear();
            }
        }

        foreach (var line in lines)
        {
            if (currentMultiline is not null && Regex.IsMatch(line, @"^\s{2,}[-*]\s+"))
            {
                if (multiline.Length > 0) multiline.Append("; ");
                multiline.Append(Regex.Replace(line.Trim(), @"^[-*]\s*", ""));
                continue;
            }

            var bullet = Regex.Match(line, @"^\s*[-*]\s*(?<label>[^:]+):\s*(?<value>.*)$");
            if (bullet.Success)
            {
                Flush();
                var label = bullet.Groups["label"].Value.Trim();
                var value = bullet.Groups["value"].Value.Trim();
                if (string.IsNullOrWhiteSpace(value))
                {
                    currentMultiline = label;
                }
                else
                {
                    fields[label] = value;
                }
                continue;
            }
        }
        Flush();

        return new Handoff
        {
            SourcePath = sourcePath,
            RawText = text,
            Fields = fields
        };
    }

    private bool Has(string label) => Fields.ContainsKey(label);

    private string Get(string label) => Fields.TryGetValue(label, out var value) ? Clean(value) : "";

    private string GetOrDefault(string fallback, params string[] labels)
    {
        foreach (var label in labels)
        {
            if (Fields.TryGetValue(label, out var value))
            {
                return Clean(value);
            }
        }
        return fallback;
    }

    private static string Clean(string value) => value.Replace("`", "").Trim();
}

enum AdapterKind
{
    CodexExec,
    CodexAppServer
}

sealed record AdapterContract(AdapterKind Kind, string AdapterId, string ExecutionChannel, string CommandContract)
{
    public static AdapterContract For(string adapter) =>
        adapter switch
        {
            "codex-app-server" => new AdapterContract(
                AdapterKind.CodexAppServer,
                "codex-app-server",
                "app_server",
                "codex app-server --listen stdio:// using initialize, thread/start, thread/name/set, turn/start, thread/list"),
            _ => new AdapterContract(
                AdapterKind.CodexExec,
                "codex-cli",
                "headless_cli",
                "codex exec --json -C <target_workspace> --output-last-message <last-message.md> -"),
        };
}

sealed record AgentContract(string Provider, string AdapterId, string AdapterStatus, string LaunchCapability, string CommandContract)
{
    public bool IsCodex => Provider.Equals("codex", StringComparison.OrdinalIgnoreCase);

    public static AgentContract For(string provider, AdapterContract adapter)
    {
        if (provider.Equals("codex", StringComparison.OrdinalIgnoreCase))
        {
            return new AgentContract("codex", adapter.AdapterId, "supported", "launch", adapter.CommandContract);
        }

        return new AgentContract(provider, "unsupported", "unsupported", "none", "No v1 adapter implemented for this provider.");
    }
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

    public static MarkdownTable? FindRequiredTable(string markdown)
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

    private static bool IsTableLine(string line) => line.TrimStart().StartsWith("|", StringComparison.Ordinal) && line.TrimEnd().EndsWith("|", StringComparison.Ordinal);

    private static bool IsSeparatorLine(string line)
    {
        var cells = SplitRow(line);
        return cells.Length > 0 && cells.All(c => Regex.IsMatch(c, @"^:?-{3,}:?$"));
    }

    private static string[] SplitRow(string line)
    {
        var trimmed = line.Trim();
        if (trimmed.StartsWith("|")) trimmed = trimmed[1..];
        if (trimmed.EndsWith("|")) trimmed = trimmed[..^1];
        return trimmed.Split('|').Select(c => c.Trim()).ToArray();
    }
}

sealed class AppServerLaunchRequest
{
    public required string Cwd { get; init; }
    public required string Prompt { get; init; }
    public required string SessionTitle { get; init; }
    public required string TranscriptPath { get; init; }
    public required string StderrPath { get; init; }
    public required TimeSpan Timeout { get; init; }
    public required TimeSpan RequestTimeout { get; init; }
}

sealed class AppServerPhaseTimeoutException : TimeoutException
{
    public AppServerPhaseTimeoutException(string phase, string method, TimeSpan timeout)
        : base($"{phase} after {timeout.TotalSeconds:0} seconds")
    {
        Phase = phase;
        Method = method;
        Timeout = timeout;
    }

    public string Phase { get; }
    public string Method { get; }
    public TimeSpan Timeout { get; }
}

sealed class AppServerLaunchResult
{
    public string? ThreadId { get; set; }
    public string? ThreadSourceObserved { get; set; }
    public string? SourceKindObserved { get; set; }
    public string? CwdObserved { get; set; }
    public string? TitleObserved { get; set; }
    public string? RolloutPath { get; set; }
    public string TurnCompletedStatus { get; set; } = "not_started";
    public bool ThreadStartObserved { get; set; }
    public bool ThreadNameSetObserved { get; set; }
    public bool TurnStartObserved { get; set; }
    public bool ThreadListObserved { get; set; }
    public bool DefaultListObserved { get; set; }
    public bool Visible => !string.IsNullOrWhiteSpace(ThreadId) &&
                           !string.IsNullOrWhiteSpace(CwdObserved) &&
                           !string.IsNullOrWhiteSpace(TitleObserved) &&
                           !string.IsNullOrWhiteSpace(RolloutPath) &&
                           string.Equals(SourceKindObserved, "vscode", StringComparison.OrdinalIgnoreCase);
}

static class CodexAppServerJsonRpcClient
{
    public static async Task<AppServerLaunchResult> LaunchVisibleSessionAsync(AppServerLaunchRequest request)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(request.TranscriptPath)!);
        await using var transcript = new StreamWriter(request.TranscriptPath, false, TextEncoding.Utf8NoBom);
        var stderr = new StringBuilder();
        var pending = new Dictionary<int, TaskCompletionSource<JsonNode?>>();
        var pendingLock = new object();
        var completed = new TaskCompletionSource<string?>(TaskCreationOptions.RunContinuationsAsynchronously);

        using var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "codex",
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                ArgumentList = { "app-server", "--listen", "stdio://" }
            },
            EnableRaisingEvents = true
        };

        if (!process.Start())
        {
            throw new InvalidOperationException("Could not start codex app-server process.");
        }

        var stderrTask = Task.Run(async () =>
        {
            while (await process.StandardError.ReadLineAsync() is { } line)
            {
                stderr.AppendLine(RedactStatic(line, 2000));
            }
        });

        var readTask = Task.Run(async () =>
        {
            while (await process.StandardOutput.ReadLineAsync() is { } line)
            {
                if (string.IsNullOrWhiteSpace(line))
                {
                    continue;
                }

                JsonNode? node = null;
                try
                {
                    node = JsonNode.Parse(line);
                }
                catch
                {
                    continue;
                }

                if (node is null)
                {
                    continue;
                }

                await WriteTranscriptLineAsync(transcript, "server", node);
                var id = node?["id"]?.GetValue<int?>();
                if (id is not null)
                {
                    TaskCompletionSource<JsonNode?>? tcs = null;
                    lock (pendingLock)
                    {
                        if (pending.TryGetValue(id.Value, out tcs))
                        {
                            pending.Remove(id.Value);
                        }
                    }
                    tcs?.TrySetResult(node);
                }

                var method = node?["method"]?.GetValue<string>();
                if (method == "turn/completed")
                {
                    var status = node?["params"]?["turn"]?["status"]?.GetValue<string>();
                    completed.TrySetResult(status);
                }
            }
        });

        async Task<JsonNode?> SendRequestAsync(int id, string method, JsonObject parameters)
        {
            var outbound = new JsonObject
            {
                ["jsonrpc"] = "2.0",
                ["id"] = id,
                ["method"] = method,
                ["params"] = parameters,
            };
            var tcs = new TaskCompletionSource<JsonNode?>(TaskCreationOptions.RunContinuationsAsynchronously);
            lock (pendingLock)
            {
                pending[id] = tcs;
            }

            await WriteTranscriptLineAsync(transcript, "client", outbound);
            await process.StandardInput.WriteLineAsync(outbound.ToJsonString());
            await process.StandardInput.FlushAsync();
            JsonNode? response;
            try
            {
                response = await tcs.Task.WaitAsync(request.RequestTimeout);
            }
            catch (TimeoutException)
            {
                lock (pendingLock)
                {
                    pending.Remove(id);
                }

                throw new AppServerPhaseTimeoutException($"app_server_{NormalizeMethodForPhase(method)}_timeout", method, request.RequestTimeout);
            }

            ThrowIfError(response, method);
            return response;
        }

        async Task SendNotificationAsync(string method, JsonObject parameters)
        {
            var outbound = new JsonObject
            {
                ["jsonrpc"] = "2.0",
                ["method"] = method,
                ["params"] = parameters,
            };
            await WriteTranscriptLineAsync(transcript, "client", outbound);
            await process.StandardInput.WriteLineAsync(outbound.ToJsonString());
            await process.StandardInput.FlushAsync();
        }

        try
        {
            await SendRequestAsync(1, "initialize", new JsonObject
            {
                ["clientInfo"] = new JsonObject
                {
                    ["name"] = "agent_delivery_session_launcher",
                    ["title"] = "Agent Delivery Session Launcher",
                    ["version"] = "0.1.0",
                },
                ["capabilities"] = new JsonObject
                {
                    ["experimentalApi"] = true,
                    ["optOutNotificationMethods"] = new JsonArray(),
                },
            });
            await SendNotificationAsync("initialized", new JsonObject());

            var result = new AppServerLaunchResult();
            var threadStart = await SendRequestAsync(2, "thread/start", new JsonObject
            {
                ["cwd"] = request.Cwd,
                ["approvalPolicy"] = "never",
                ["sandbox"] = "workspace-write",
                ["ephemeral"] = false,
                ["sessionStartSource"] = "startup",
                ["threadSource"] = "user",
            });
            result.ThreadStartObserved = true;
            result.ThreadId = threadStart?["result"]?["thread"]?["id"]?.GetValue<string>();
            if (string.IsNullOrWhiteSpace(result.ThreadId))
            {
                throw new InvalidOperationException("thread/start response did not include result.thread.id.");
            }

            await SendRequestAsync(3, "thread/name/set", new JsonObject
            {
                ["threadId"] = result.ThreadId,
                ["name"] = request.SessionTitle,
            });
            result.ThreadNameSetObserved = true;

            await SendRequestAsync(4, "turn/start", new JsonObject
            {
                ["threadId"] = result.ThreadId,
                ["cwd"] = request.Cwd,
                ["approvalPolicy"] = "never",
                ["sandboxPolicy"] = new JsonObject
                {
                    ["type"] = "workspaceWrite",
                    ["writableRoots"] = new JsonArray(request.Cwd),
                    ["networkAccess"] = true,
                    ["excludeTmpdirEnvVar"] = false,
                    ["excludeSlashTmp"] = false,
                },
                ["input"] = new JsonArray(new JsonObject
                {
                    ["type"] = "text",
                    ["text"] = request.Prompt,
                    ["text_elements"] = new JsonArray(),
                }),
            });
            result.TurnStartObserved = true;
            try
            {
                result.TurnCompletedStatus = await completed.Task.WaitAsync(request.Timeout) ?? "unknown";
            }
            catch (TimeoutException)
            {
                throw new AppServerPhaseTimeoutException("app_server_turn_completion_timeout", "turn/completed", request.Timeout);
            }

            var defaultList = await SendRequestAsync(5, "thread/list", new JsonObject
            {
                ["limit"] = 20,
                ["cwd"] = request.Cwd,
                ["archived"] = false,
            });
            result.ThreadListObserved = true;
            ApplyThreadListHit(result, defaultList, request);
            result.DefaultListObserved = !string.IsNullOrWhiteSpace(result.CwdObserved);

            var sourceList = await SendRequestAsync(6, "thread/list", new JsonObject
            {
                ["limit"] = 20,
                ["cwd"] = request.Cwd,
                ["sourceKinds"] = new JsonArray("vscode"),
                ["archived"] = false,
            });
            ApplyThreadListHit(result, sourceList, request);
            return result;
        }
        finally
        {
            try
            {
                if (!process.HasExited)
                {
                    process.Kill(entireProcessTree: true);
                }
            }
            catch
            {
                // Best-effort cleanup for the per-run app-server process.
            }

            await readTask.WaitAsync(TimeSpan.FromSeconds(2)).ContinueWith(_ => { });
            await stderrTask.WaitAsync(TimeSpan.FromSeconds(2)).ContinueWith(_ => { });
            if (stderr.Length > 0)
            {
                await File.WriteAllTextAsync(request.StderrPath, stderr.ToString(), TextEncoding.Utf8NoBom);
            }
        }
    }

    private static void ApplyThreadListHit(AppServerLaunchResult result, JsonNode? response, AppServerLaunchRequest request)
    {
        var data = response?["result"]?["data"]?.AsArray();
        if (data is null)
        {
            return;
        }

        foreach (var thread in data)
        {
            if (thread?["id"]?.GetValue<string>() != result.ThreadId)
            {
                continue;
            }

            result.CwdObserved ??= thread?["cwd"]?.GetValue<string>();
            result.TitleObserved ??= thread?["name"]?.GetValue<string>();
            result.RolloutPath ??= thread?["path"]?.GetValue<string>();
            result.ThreadSourceObserved ??= thread?["source"]?.GetValue<string>();
            result.SourceKindObserved ??= thread?["source"]?.GetValue<string>();
            if (string.Equals(result.CwdObserved, request.Cwd, StringComparison.Ordinal) &&
                string.Equals(result.TitleObserved, request.SessionTitle, StringComparison.Ordinal))
            {
                return;
            }
        }
    }

    private static void ThrowIfError(JsonNode? response, string method)
    {
        var error = response?["error"];
        if (error is not null)
        {
            throw new InvalidOperationException($"{method} failed: {error.ToJsonString()}");
        }
    }

    private static string NormalizeMethodForPhase(string method) =>
        Regex.Replace(method, @"[^A-Za-z0-9]+", "_").Trim('_').ToLowerInvariant();

    private static async Task WriteTranscriptLineAsync(StreamWriter writer, string direction, JsonNode node)
    {
        var copy = node.DeepClone();
        RedactPromptLikePayload(copy);
        var line = new JsonObject
        {
            ["at"] = DateTimeOffset.UtcNow.ToString("O"),
            ["direction"] = direction,
            ["id"] = copy?["id"]?.DeepClone(),
            ["method"] = copy?["method"]?.DeepClone(),
            ["message"] = copy,
        };
        await writer.WriteLineAsync(line.ToJsonString());
        await writer.FlushAsync();
    }

    private static void RedactPromptLikePayload(JsonNode? node)
    {
        if (node is JsonObject obj)
        {
            foreach (var property in obj.ToList())
            {
                if (property.Value is null)
                {
                    continue;
                }

                if ((property.Key.Equals("text", StringComparison.OrdinalIgnoreCase) ||
                     property.Key.Equals("preview", StringComparison.OrdinalIgnoreCase) ||
                     property.Key.Equals("aggregated_output", StringComparison.OrdinalIgnoreCase)) &&
                    property.Value is JsonValue value &&
                    value.TryGetValue<string>(out var text) &&
                    text.Length > 240)
                {
                    obj[property.Key] = text[..240] + " [TRUNCATED]";
                    continue;
                }

                RedactPromptLikePayload(property.Value);
            }
        }
        else if (node is JsonArray array)
        {
            foreach (var item in array)
            {
                RedactPromptLikePayload(item);
            }
        }
    }

    private static string RedactStatic(string text, int maxLength)
    {
        text = Regex.Replace(text, @"Authorization:\s*Bearer\s+[^\s]+", "Authorization: Bearer [REDACTED]", RegexOptions.IgnoreCase);
        text = Regex.Replace(text, @"(?i)(password|token|secret|api[_-]?key)\s*=\s*[^\s;]+", "$1=[REDACTED]");
        return text.Length <= maxLength ? text : text[..maxLength];
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

static class CodexAppInspector
{
    public static async Task<Dictionary<string, object?>> TryInspectAsync(string workspace, DateTimeOffset startedAt, string desiredTitle)
    {
        var result = new Dictionary<string, object?>
        {
            ["visibility_status"] = "launched_unverified",
            ["thread_id"] = null,
            ["rollout_path"] = null,
            ["thread_source"] = null,
            ["thread_cwd_observed"] = null,
            ["thread_title_observed"] = null,
            ["title_status"] = "not_observed",
        };

        var db = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".codex", "state_5.sqlite");
        if (!File.Exists(db) || !CommandExistsLocal("sqlite3"))
        {
            return result;
        }

        var sinceSeconds = startedAt.ToUnixTimeSeconds() - 5;
        var sql = $"select id, source, cwd, title, rollout_path from threads where source='exec' and created_at >= {sinceSeconds} order by created_at desc limit 1;";
        var psi = new ProcessStartInfo
        {
            FileName = "sqlite3",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };
        psi.ArgumentList.Add("-separator");
        psi.ArgumentList.Add("\t");
        psi.ArgumentList.Add(db);
        psi.ArgumentList.Add(sql);

        try
        {
            using var process = Process.Start(psi);
            if (process is null) return result;
            var stdout = await process.StandardOutput.ReadToEndAsync();
            await process.WaitForExitAsync();
            if (process.ExitCode != 0 || string.IsNullOrWhiteSpace(stdout))
            {
                result["visibility_status"] = "not_app_visible";
                return result;
            }

            var parts = stdout.Trim().Split('\t');
            if (parts.Length >= 5)
            {
                result["thread_id"] = parts[0];
                result["thread_source"] = parts[1];
                result["thread_cwd_observed"] = parts[2];
                result["thread_title_observed"] = parts[3];
                result["rollout_path"] = parts[4];
                result["visibility_status"] = SamePathLocal(parts[2], workspace) ? "verified_same_project" : "wrong_project";
                result["title_status"] = parts[3].Equals(desiredTitle, StringComparison.Ordinal) ? "observed_match" : "observed_different";
            }
        }
        catch
        {
            result["visibility_status"] = "launched_unverified";
        }

        return result;
    }

    private static bool CommandExistsLocal(string command)
    {
        try
        {
            using var process = Process.Start(new ProcessStartInfo
            {
                FileName = "/usr/bin/env",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                ArgumentList = { "sh", "-lc", $"command -v '{command}'" }
            });
            process!.WaitForExit();
            return process.ExitCode == 0;
        }
        catch
        {
            return false;
        }
    }

    private static bool SamePathLocal(string left, string right) =>
        string.Equals(Path.GetFullPath(left).TrimEnd(Path.DirectorySeparatorChar), Path.GetFullPath(right).TrimEnd(Path.DirectorySeparatorChar), StringComparison.Ordinal);
}
