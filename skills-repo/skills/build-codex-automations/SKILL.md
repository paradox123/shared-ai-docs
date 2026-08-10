---
name: build-codex-automations
description: Design, create, inspect, update, or troubleshoot Codex automations and local scheduled workflows in Daniel's macOS environment. USE WHEN the user asks for recurring tasks, reminders, monitors, scheduled Codex runs, automation prompts/configs, helper scripts for automations, or deciding whether automation should be direct Codex, scripted, or hybrid. Do not use as the primary skill for Learn-style retrospective session reviews or skill-gap audits; use improve-skills first and open this only after the canonical automation/session bootstrap shows a concrete automation-definition issue.
---

# Build Codex Automations

Use this skill to design and implement automations in Daniel's environment.

Do not use this skill as the primary workflow for retrospective session-review tasks such as `Learn`, skill-gap audits, or "review sessions since last run" requests. Use `improve-skills` first for those reviews, and only come back here after the bounded evidence pass confirms a concrete automation prompt/config change or helper-design question.
For Learn-style Codex Desktop reviews, the earliest acceptable point to open this skill is after the canonical `automation.toml`, normalized automation memory, and `session_index.jsonl` bootstrap reads are already on screen.

Default environment assumptions:

- User home is `~/`.
- Codex automation definitions live under `~/.codex/automations/<automation-id>/automation.toml`.
- Codex automation working memory should live under `~/.codex/automations/<automation-id>/memory.md` when the automation needs persisted run state.
- Personal/shared skills live in `~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills`.
- Prefer the Codex app `automation_update` tool for create, update, view, and delete operations when it is available.
- Use direct TOML reads for inspection, explanation, and prompt extraction.
- Do not use Windows paths, `.lnk` shortcuts, PowerShell-specific snippets, Node-RED, Home Assistant, Traefik, or homelab assumptions unless the user explicitly introduces that stack.
- If a prompt references `$CODEX_HOME` and it is unset, normalize to `~/.codex` instead of probing multiple candidate directories.

## Decision Tree

First classify the request:

1. Existing Codex automation: show, inspect, explain, update, pause, resume, delete, or extract the prompt/config.
2. New direct Codex automation: the task can be expressed as an agent prompt using existing tools and workspace context.
3. Hybrid Codex automation: deterministic data collection or preprocessing is needed before agentic interpretation.
4. macOS local scheduled workflow: the task should run on the local machine as a deterministic script outside Codex.
5. Remote or infrastructure automation: the target system is external to the local Codex/workspace environment.

Execute only the matching branch unless the user asks for alternatives.

## Existing Codex Automation

Use this branch for requests about automations that already exist.

1. Locate `~/.codex/automations/<automation-id>/automation.toml`.
2. Treat `automation.toml` as the automation definition, and inspect `memory.md` beside it when the automation uses persisted run state.
3. Read these fields when present: `id`, `kind`, `name`, `prompt`, `status`, `rrule`, `model`, `reasoning_effort`, `execution_environment`, `cwds`, `created_at`, and `updated_at`.
4. If the user asks for the automation text or prompt, return the decoded `prompt` value.
5. If the user asks for the file verbatim, return the TOML contents exactly enough to satisfy the request.
6. For create/update/delete operations, prefer `automation_update` when available.
7. If editing TOML manually, create a timestamped backup in the automation folder first and change only the requested fields.

Useful inspection commands:

```bash
find ~/.codex/automations -maxdepth 2 -name automation.toml -print
sed -n '1,220p' ~/.codex/automations/<automation-id>/automation.toml
```

## New Direct Codex Automation

Use this branch when no custom helper script is needed.

1. Define the task prompt so it is self-contained and includes the expected output.
2. Choose automation kind:
   - `heartbeat` for continuing the current thread later, especially short follow-ups.
   - `cron` for detached recurring workspace jobs.
3. Choose execution environment for cron jobs:
   - `worktree` when the automation should safely operate on repositories.
   - `local` only when it needs the current local environment directly.
4. Choose `cwds` for cron jobs. Include only relevant workspaces, not broad parent folders.
5. Choose model and reasoning effort based on risk:
   - routine checks: medium is usually enough.
   - cross-repo analysis or code changes: high may be justified.
6. Use `automation_update` to create the automation when available.
7. Verify the created definition with `automation_update` view or by reading `automation.toml`.

Prompt guidance:

- Keep schedule details out of the prompt when using `automation_update`; schedule belongs in the automation fields.
- When the automation needs stable cross-run state, include `Automation ID: <id>` and `Automation memory: ~/.codex/automations/<id>/memory.md` in the prompt contract.
- Keep the prompt's `Automation ID`, memory path, definition path, and live TOML `id` aligned. When cloning an automation for another project or worktree, give the clone its own adjacent memory unless shared state is an explicit, documented design choice.
- For automation prompts that inspect Codex session history or other automation state, use the canonical bootstrap contract from `skills-repo/skills/improve-skills/references/codex-desktop-session-review.md`. Copy only the short prompt-facing rules needed for that automation; do not paraphrase a second full JSONL/session playbook here.
- If the prompt names a specific tool or action primitive such as a task/todo creator, either confirm that tool is available in the target environment or write a fallback path into the prompt.
- Treat named tool availability as a run-environment contract, not a filesystem-discovery task. Check the active tool context when you have it; otherwise assume the tool is unavailable and use the fallback. Do not search `~/`, `~/.codex`, session logs, or prompt files just to prove whether a named tool such as `Create User Todo` exists.
- If a shell snippet passes values into embedded Python, Perl, or another subprocess, make the binding mode explicit. Set values in a prior shell statement before expanding them as positional arguments, or use `VAR=value command ...` and read them from that command's environment. A prefix assignment is not available to expand a sibling argument on the same command line (`VAR=value command "$VAR"` expands the old/unset value), and an unexported assignment on a prior line is not visible through `os.environ`.
- Do not put shell parameter expansion such as `${CODEX_HOME:-~/.codex}` inside Python strings, `Path(...)`, or `os.path.expanduser(...)`. Resolve Codex home in shell first and pass it as `sys.argv` or an exported environment variable, or use `Path.home() / ".codex"` directly when no shell override is required.
- When a code-mode JavaScript call embeds shell source, do not paste deeply nested JavaScript -> shell -> Python programs into one template literal. Prefer a task-owned helper or pass arguments structurally. If a short template literal is unavoidable, escape shell `${name}` as `\${name}` so JavaScript does not interpolate it, and escape or avoid every raw backtick. A shell heredoc does not protect its contents from the outer JavaScript parser.
- For an automation that may trigger, send, deploy, move, or otherwise mutate external state, make the gate deterministic and fail closed. Name the exact response schema and tested parser/helper in the prompt; treat missing keys, `null`, empty output after a parse error, and disagreement with persisted state as blockers rather than a safe zero. For load- or safety-sensitive gates, require two consecutive valid safe observations before mutation.
- For session-driven review automations, include an explicit stop condition for no-change audits. If the bounded session pass shows no relevant product/repo work beyond the current automation thread, tell the automation to stop there instead of widening into repo-wide `git status`, `git log`, or documentation sweeps.
- When an automation reads a long or growing `memory.md`, make every visible state read character-bounded (for example, a first/last excerpt whose marker is included in the cap); never `cat` the full memory into tool output. Parse the complete file only inside a targeted helper that emits the fields needed for the run. If state-read order matters, put that contract at the start of the prompt and require the definition plus bounded memory read to finish before unrelated repo, startup, or skill reads. Immediately before patching newest-first memory, reread a small current header excerpt and anchor on stable header fields, not an older run body or a `tail` excerpt. If another run changes the anchor, reread and retry once rather than rebuilding memory from stale output.
- Include constraints, output format, and what to do when nothing changed.
- Do not ask the automation to edit files unless that is truly desired.
- For repo work, specify whether it may modify files, create commits, or only report findings.

## Hybrid Codex Automation

Use this branch when deterministic collection/preprocessing should happen before Codex interprets results.

Good examples:

- gather logs or metrics, then summarize anomalies
- export recent session data, then identify skill improvements
- query a CLI/API with stable parameters, then produce a recommendation

Workflow:

1. Identify the deterministic helper contract: inputs, outputs, exit codes, and failure behavior.
2. Put helper scripts in the closest sensible owner:
   - inside the relevant repo if the helper belongs to that project
   - inside a skill `scripts/` folder if it is reusable across requests
   - inside the automation folder only when it is unique to that automation
3. Keep helper output parseable and compact, preferably JSON for structured data.
4. Make wrappers fail clearly when inner commands fail or their expected JSON/schema is absent. Do not return empty success-looking output after a non-zero inner exit, parser mismatch, or missing required key.
5. If a collector can outlive one tool turn or its exit status is correctness-critical, run it once through a wrapper that creates one task-owned artifact directory and persists stdout, stderr, and the numeric exit status there. Print the validated artifact-directory path before the first yield. Shell variables do not survive a later tool/exec call, so resume with that explicit quoted path (or pass it as an actual positional argument); do not scan a temp root for the newest directory, reference `$1` without supplying it, or rerun the collector merely to recover state.
6. Keep macOS/zsh helpers portable:
   - use the shell builtin or `/bin/test`, not `/usr/bin/test`
   - never use zsh's special parameters such as the read-only `status` value or the `path` array as ordinary variables; prefer names such as `collector_rc` and `candidate_path`
   - for a local ISO-8601 timestamp, use `date '+%Y-%m-%dT%H:%M:%S%z'` or Python's timezone-aware `datetime.now().astimezone().isoformat(timespec="seconds")`; macOS `date` does not support GNU `-Is` or the colonized `%:z` directive
   - quote or explicitly guard optional globs so an empty match does not abort the command
   - create temporary work under `mktemp -d`, validate the exact task-owned directory before cleanup, and use a policy-compatible bounded deletion method
7. Add or run a small verifier for:
   - happy path
   - empty/no-op path
   - forced failing-helper path
8. Create or update the Codex automation prompt so it calls the helper and interprets the output.
9. For review automations, keep operational state in the memory adjacent to that automation's actual ID rather than encoding per-run state into `automation.toml` or silently sharing another automation's ledger. Capture the review-window watermark from the input/index snapshot and persist that as `Processed window end`; record completion wall clock separately as `Run time`.
10. If the prompt asks the automation to create a task/todo via a tool that may not exist in every environment, define a fallback that records the suggested diff or action in `memory.md` with an explicit waiting status.
   Do not ask the automation to hunt for the task/todo tool with `rg`, `find`, or prompt-text searches. If the named tool is not available in the run context, record the pending action in memory and report the mismatch.
11. If the automation inspects Codex session history, use `improve-skills/references/codex-desktop-session-review.md` as the source of truth for memory, `session_index.jsonl`, bounded session windows, timestamp normalization, and JSONL shape.
12. When an automation prompt or helper needs `$CODEX_HOME`, normalize once with `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` instead of probing multiple candidate directories.
13. If your helper shell uses `set -u`, never read raw `$CODEX_HOME/...` paths before that normalization step; make the prompt/helper show `CODEX_HOME_RESOLVED` explicitly instead of implying the variable is always exported.
14. Prefer a short bounded `python3` extractor for rollout/session JSONL inspection over broad `rg` scans across raw session files, especially when you need timestamps, `cwd`, prompts, or tool-call metadata.
15. Keep session-inspection shell snippets portable and dependency-light; put detailed parsers in helpers or the central reference instead of the automation prompt.
16. For cross-repo review automations, do not front-load `git status`, `git log`, or repo sweeps across every configured workspace. Let the bounded session pass decide which repos, if any, need follow-up inspection.
17. If a review automation includes both a prompt-level `Last run:` header and persisted memory, use the normalized cutoff-selection rule from `improve-skills/references/codex-desktop-session-review.md`. Do not restate a separate memory-vs-header precedence rule here.
18. Verify one full run or the closest safe dry run before declaring completion.

Only extract a new reusable skill when the helper pattern is clearly useful beyond one automation.

## macOS Local Scheduled Workflow

Use this branch when the automation should run as a deterministic local process outside Codex.

1. Put the script in a project repo, shared scripts repo, or another explicit owner. Avoid random one-off files in home directories.
2. Make the script idempotent when repeated runs are possible.
3. Test the script manually.
4. Use `launchd` with a LaunchAgent plist for scheduled or login-triggered macOS execution.
5. Store the plist or setup instructions next to the script so the workflow can be reinstalled.
6. Verify with `launchctl print`, logs, or a manual `launchctl kickstart` where appropriate.

Prefer Codex automations over `launchd` when the task needs agentic reasoning, repo-aware edits, or natural-language reporting.

## Remote Or Infrastructure Automation

Use this branch only when the target is outside the local Codex/workspace environment.

1. Identify the actual platform and ownership boundary before implementing anything.
2. Use a dedicated skill or project playbook if one exists for that platform.
3. Keep deterministic infrastructure tasks script-first and verify with dry runs, logs, and resulting state.
4. For agentic remote automation, state the support limits clearly and propose a small discovery/prototype step before productionizing it.

Do not invent entity IDs, service URLs, credentials, hostnames, or deployment conventions.

## Verification And Delivery

Before finishing, report:

- Chosen branch and why.
- Artifacts created or changed: automation definition, helper script, skill, LaunchAgent plist, repo files, or documentation.
- Schedule and execution environment if a Codex automation was created or updated.
- Verification performed and observed outcome.
- Any limitations, manual follow-up, or unsafe-to-run steps that were intentionally skipped.

If the request only asks for analysis or a design, do not create or modify automations without confirmation.
