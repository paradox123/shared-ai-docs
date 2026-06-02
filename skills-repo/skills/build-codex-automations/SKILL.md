---
name: build-codex-automations
description: Design, create, inspect, update, or troubleshoot Codex automations and local scheduled workflows in Daniel's macOS environment. USE WHEN the user asks for recurring tasks, reminders, monitors, scheduled Codex runs, automation prompts/configs, helper scripts for automations, or deciding whether automation should be direct Codex, scripted, or hybrid.
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
- For automation prompts that inspect Codex session history or other automation state, write the state bootstrap into the prompt explicitly instead of assuming the agent will infer it:

```text
Automation state:
- Resolve Codex home with `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` before reading automation files.
- Read the automation definition from `"$CODEX_HOME_RESOLVED/automations/<id>/automation.toml"` before broader discovery.
- Read memory from `"$CODEX_HOME_RESOLVED/automations/<id>/memory.md"`.
- If memory already records `Processed window end` or `Last review`, derive the working cutoff from that value and use any prompt-level `Last run:` only as a fallback.
- Prefer `"$CODEX_HOME_RESOLVED/session_index.jsonl"` plus a bounded extractor against matching `sessions/YYYY/MM/DD/*.jsonl` files instead of broad home-directory scans or raw `rg` across every session file.
- Do not probe alternate Codex-home candidates such as `~/Library/Application Support/Codex` unless the user or environment explicitly says the session store is elsewhere.
- Do not start with repo orientation commands such as `git status`, `README.md`, `pwd`, `ls`, repo-wide `git log`, or prompt-fragment searches like `rg -n "Last run|Automation ID|Create User Todo"` across `~/` or `~/.codex`.
- Do not load automation-authoring or project skills during that bootstrap unless the bounded session pass already proved they are needed for a concrete finding.
- If the automation will run inside repos that inject `AGENTS.md` startup checklists, say explicitly that repo-local startup guidance is deferred until after the automation-state bootstrap and the first bounded session pass.
- If the first user-visible content may include both an injected `# AGENTS.md instructions for ...` block and automation metadata such as `Automation ID:` or `Last run:`, tell the automation to treat the automation metadata as authoritative bootstrap inputs and the AGENTS block as background context.
```

- If the prompt names a specific tool or action primitive such as a task/todo creator, either confirm that tool is available in the target environment or write a fallback path into the prompt.
- Treat named tool availability as a run-environment contract, not a filesystem-discovery task. Check the active tool context when you have it; otherwise assume the tool is unavailable and use the fallback. Do not search `~/`, `~/.codex`, session logs, or prompt files just to prove whether a named tool such as `Create User Todo` exists.
- If the prompt expects shell snippets to pass values into embedded Python via `os.environ`, state that the snippet must `export` those variables first or invoke Python as `VAR=value python3 ...`. A plain shell assignment on the line before `python3 - <<'PY'` is not visible inside Python.
- Do not put shell parameter expansion such as `${CODEX_HOME:-~/.codex}` inside Python strings, `Path(...)`, or `os.path.expanduser(...)`. Resolve Codex home in shell first and pass it as `sys.argv` or an exported environment variable, or use `Path.home() / ".codex"` directly when no shell override is required.
- For session-driven review automations, include an explicit stop condition for no-change audits. If the bounded session pass shows no relevant product/repo work beyond the current automation thread, tell the automation to stop there instead of widening into repo-wide `git status`, `git log`, or documentation sweeps.
- Include constraints, output format, and what to do when nothing changed.
- Do not ask the automation to edit files unless that is truly desired.
- For repo work, specify whether it may modify files, create commits, or only report findings.

For review-style automations that inspect Codex sessions, prefer including a short literal bootstrap contract instead of paraphrasing the rules. A copy-pasteable prompt fragment is more reliable than a looser summary:

```text
Bootstrap rules:
- Treat `Automation ID`, `Automation memory`, and `Last run` as automation metadata, not as strings to rediscover.
- Resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` once, then read `automation.toml`, normalized `memory.md`, and `session_index.jsonl` before any repo inspection.
- If `memory.md` contains `Processed window end` or `Last review`, that value overrides the prompt `Last run:` header.
- If the run starts inside a repo with injected `AGENTS.md` startup instructions, defer those repo-local startup steps until after the bounded session pass proves repo context is needed.
- Do not begin with `git status`, `README.md`, `pwd`, `ls`, broad `find ~/.codex`, raw `$CODEX_HOME/...` probes, or prompt-fragment searches across `~/` or `~/.codex`.
- If the required task/todo tool is unavailable, record the pending diff/action in `memory.md` and report it instead of searching the filesystem for the tool.
```

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
4. Make wrappers fail clearly when inner commands fail. Do not return empty success-looking output after a non-zero inner exit.
5. Add or run a small verifier for:
   - happy path
   - empty/no-op path
   - forced failing-helper path
6. Create or update the Codex automation prompt so it calls the helper and interprets the output.
7. For review automations, keep operational state in `memory.md` rather than encoding per-run state into `automation.toml`.
8. If the prompt asks the automation to create a task/todo via a tool that may not exist in every environment, define a fallback that records the suggested diff or action in `memory.md` with an explicit waiting status.
   Do not ask the automation to hunt for the task/todo tool with `rg`, `find`, or prompt-text searches. If the named tool is not available in the run context, record the pending action in memory and report the mismatch.
9. If the automation inspects Codex session history, anchor it to `~/.codex/session_index.jsonl`, bounded `~/.codex/sessions/YYYY/MM/*.jsonl` windows, and the automation memory before any broad home-directory scan.
10. When an automation prompt or helper needs `$CODEX_HOME`, normalize once with `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` instead of probing multiple candidate directories.
11. If your helper shell uses `set -u`, never read raw `$CODEX_HOME/...` paths before that normalization step; make the prompt/helper show `CODEX_HOME_RESOLVED` explicitly instead of implying the variable is always exported.
12. Prefer a short bounded `python3` extractor for rollout/session JSONL inspection over broad `rg` scans across raw session files, especially when you need timestamps, `cwd`, prompts, or tool-call metadata.
13. When you use `session_index.jsonl`, treat `id` and `updated_at` as coarse routing fields only. Do not ask the automation to reconstruct rollout filenames from the id; have it resolve bounded candidate files first and confirm ids from `session_meta`.
14. If the automation narrows candidate files by rollout filename timestamps, use that only to find the right day/window. Make the actual cutoff decision from `session_meta.payload.timestamp`, not from the filename alone.
15. If the automation depends on `updated_at` filtering, note in the prompt or helper that timestamp precision may vary. Normalize timestamps in one parser instead of mixing shell date parsing with repeated `datetime.fromisoformat(...)` retries.
16. Keep bounded Python helpers dependency-light. Prefer stdlib modules such as `json`, `datetime`, `glob`, `re`, and `pathlib` for session parsing unless the automation explicitly provisions another package. Do not assume `python-dateutil` is installed for simple cutoff parsing.
17. When a shell helper feeds values into embedded Python through `os.environ`, either `export` them first or use inline environment assignment on the Python command itself. Do not rely on non-exported shell variables surviving into `python3 - <<'PY'`.
18. Do not copy shell fallback expressions such as `${CODEX_HOME:-~/.codex}` into Python path code. Shell expansion happens before Python starts; inside Python, pass the resolved value as an argument/environment variable or construct `Path.home() / ".codex"`.
19. Keep session-inspection shell snippets portable. Avoid bash-only features such as `mapfile` unless you explicitly run them under `bash -lc`; default zsh shells should use portable loops or the bounded Python path instead.
20. For cross-repo review automations, do not front-load `git status`, `git log`, or repo sweeps across every configured workspace. Let the bounded session pass decide which repos, if any, need follow-up inspection.
21. If a review automation includes both a prompt-level `Last run:` header and persisted memory, make the prompt say which one wins. Default to memory `Processed window end` or `Last review`, with the header as a first-run fallback only, and tell the automation not to run duplicate extractors for both windows once the authoritative cutoff is known.
22. Verify one full run or the closest safe dry run before declaring completion.

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
