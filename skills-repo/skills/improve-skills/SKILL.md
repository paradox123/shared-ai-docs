---
name: improve-skills
description: Review Claude session history since the last run to find where existing skills were unclear, missing usage patterns, or failed to prevent avoidable tool discovery. USE WHEN the user asks to improve skills, review sessions for skill gaps, inspect tool usage for unclear instructions, find recurring discovery patterns, or turn repeated agent exploration into improved skills or new skill candidates.
---

# improve-skills

Review recent session history, improve weak skills when the evidence is strong enough, track repeated discovery patterns as future skill candidates, and produce a concise report. For Parent/Child Agent Delivery process reviews where the target is a specific parent spec, child index, handoffs, OpenSpec evidence, and workflow self-optimization, prefer `agent-delivery-retro-review` first and use this skill only for broader cross-session skill-gap aggregation.

## Goal

Use this skill to inspect sessions since the previous run and answer four questions:

1. Which existing skills should be improved because the instructions were not clear enough?
2. Which tool-usage failures or retries point to missing usage guidance inside a skill?
3. Which repeated discovery behaviors should become new skills or project-scoped playbooks?
4. What changed this run, and what should be escalated in the report?

## Codex Desktop Quick Start

For Codex Desktop automation reviews, start with this exact bootstrap sequence before any broader discovery or repo commands:

1. `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"`
2. Read `"$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml"`
3. Read the prompt-provided memory path, normalized through `CODEX_HOME_RESOLVED`
4. Read `"$CODEX_HOME_RESOLVED/session_index.jsonl"`
5. Run one bounded `python3` extractor against only the matching recent day folders under `~/.codex/sessions/YYYY/MM/DD/`
6. Parse session JSONL from `response_item` records first, not from assumed top-level `message` or `tool_call` rows

Do not begin with `git status`, broad `find ~/.codex`, broad `rg --files ~/.codex`, or raw `$CODEX_HOME/...` paths. Those detours are recurring evidence of this skill not being followed closely enough.

## Inputs

- Primary source: `~/.claude/projects/**/*.jsonl`
- Co-primary source for Codex Desktop runs: `~/.codex/sessions/**/*.jsonl` (and `~/.codex/archived_sessions/*.jsonl` when needed)
- Fast recent-session index for Codex Desktop runs: `~/.codex/session_index.jsonl`
- Supporting sources when useful: `~/.claude/history/sessions/**`, `~/.claude/history/research/**`, `~/.claude/history/raw-outputs/**`, `~/.claude/debug/latest`
- Skill files to inspect or update: prefer `.agents/skills/*/SKILL.md`; if unavailable use `~/.claude/skills/*/SKILL.md`
- Persistent run cursor: prefer `.agents/skills/improve-skills/last-run.json`; if unavailable use `~/.claude/skills/improve-skills/last-run.json`
- Persistent candidate memory: prefer `/memories/improve-skills.md`; if `/memories` is unavailable, reuse an existing improve-skills report/memory file in the active docs workspace and note the fallback path in the report

Prefer project session logs first because they preserve tool calls, retries, and agent behavior in sequence. When `~/.claude/projects` does not include the active Codex thread, use `~/.codex/sessions` as the authoritative source for that run window.
When multiple unrelated workspaces are present in the same time window, filter candidate sessions by `cwd`/workspace relevance first to avoid cross-project noise in findings.

For automation threads, resolve Codex home before any memory or automation-path reads:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
```

Use `"$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md"` instead of assuming `$CODEX_HOME` is exported.
Do not probe raw `$CODEX_HOME` first and do not print paths like `"$CODEX_HOME/automations/..."` before normalization; when the variable is unset that produces misleading `/automations/...` output and usually triggers avoidable follow-up discovery.

For Codex Desktop automation runs, use this fast path before any broader discovery:

1. resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"`
2. read `"$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml"`
3. read the prompt-provided memory path, normalized through `CODEX_HOME_RESOLVED` when needed
4. read `"$CODEX_HOME_RESOLVED/session_index.jsonl"`
5. use one bounded `python3` extractor against the specific recent session dates from the index, built around Codex `response_item` records rather than Claude-style top-level `message` rows
6. if you need concrete session files for indexed ids, resolve them from `session_meta.payload.id` inside those bounded day folders; if a candidate id is missing there, check `~/.../.codex/archived_sessions` before broadening the search

Do not start a Codex Desktop improve-skills run by probing the home directory, searching for the session store, or experimenting with multiple filesystem roots. Assume `~/.codex` unless the prompt or environment proves otherwise.

## First Run And Cursor Handling

Before creating any new memory file, view `/memories/` and reuse an existing improve-skills note if present.
If `/memories/` does not exist, locate an existing improve-skills note/report in the active docs workspace and reuse that path instead of inventing a new random location.

If the automation prompt explicitly provides `Automation memory: ...`, treat that file as the primary persisted state for this run. Do not invent a parallel memory file elsewhere unless the prompt explicitly asks for one.
If a prompt references `$CODEX_HOME` and that variable is unset, normalize to `~/.codex` immediately instead of probing broad home-directory candidates.
When writing paths that refer to the user's home directory in the final report or memory, prefer `~/...` over absolute `/Users/...` paths.
If the automation memory already contains a newer `Last review` or processed-window end than the prompt's `Last run`, treat the memory file as authoritative and use the prompt timestamp only as a fallback.
If the prompt also includes a human-written or auto-inserted `Last run:` header and it disagrees with the memory file's latest processed window, trust the memory file, note the mismatch in the report, and do not rescan the older prompt window just because the header is stale.
If the automation memory path from the prompt does not exist yet, create it at the end of the run instead of falling back to unrelated workspace notes.

Read `.agents/skills/improve-skills/last-run.json` if it exists; otherwise read `~/.claude/skills/improve-skills/last-run.json`.

- If it exists, only inspect sessions newer than the stored timestamp.
- If it does not exist, do a bounded first pass over the most recent relevant sessions and say clearly in the report that this was an initial baseline run.
- At the end of a successful run, update the cursor file you used with the timestamp of the newest processed session and a short run summary.

Use a bounded first pass rather than scanning everything blindly.
Before running git commands during session review, confirm the actual repo root with `git rev-parse --show-toplevel 2>/dev/null`. Do not start with `git status` or other repo commands from an unverified workspace, because automation fan-out worktrees and wrapper folders may not expose `.git` at the current `cwd`. If `git rev-parse` fails, skip git-based context instead of retrying more git commands from the same path.

## What Counts As Evidence

Treat the following as strong signals that a skill needs improvement:

- The agent used a relevant skill but still had to inspect documentation to learn a basic usage pattern that the skill should have explained.
- The agent retried several tools for the same job because the expected tool choice or invocation pattern was unclear.
- The agent searched the repo or surrounding filesystem to rediscover a stable workflow that should have been codified in a skill.
- The agent had to break a routine task into helper scripts or smaller manual steps because the skill lacked an execution pattern.
- The agent missed a relevant skill entirely because the description under-triggered.

Do not file an issue just because a task was genuinely novel or required domain research beyond what a skill should reasonably contain.

## Classification Rules

For every finding, classify it along two axes:

### 1. Action Type

- `improve-existing-skill`: A current skill exists but needs clearer instructions, trigger language, examples, decision rules, or CLI usage patterns.
- `new-skill-candidate`: No suitable skill exists and the behavior repeats enough to justify one.
- `project-scoped-playbook`: The pattern is real but tied to one repository, folder layout, environment, or project workflow.
- `no-action`: Interesting observation, but not strong enough yet.

### 2. Scope

- `general`: Useful across projects.
- `project:<name>`: Clearly tied to one project or workspace.

## Required Workflow

### Step 1: Collect candidate sessions

Inspect session artifacts newer than the last-run cursor.

For Codex Desktop session selection, prefer bounded, portable methods in this order:

1. `~/.codex/session_index.jsonl` filtered by timestamp and `cwd`
2. sorted file paths under `~/.codex/sessions/**` and `~/.codex/archived_sessions/**`, using the ISO-like timestamp embedded in the filename only as a coarse locator for the right day/window
3. `jq` filtering on `session_meta.payload.timestamp` inside a bounded set of recent files

For the common Learn-automation case, first collect the candidate days from `session_index.jsonl` and then inspect only those day folders under `~/.codex/sessions/YYYY/MM/DD/` plus any matching `archived_sessions` entries. Do not iterate every month folder when the index already narrows the date range.
Do not assume a same-day automation run still lives under `~/.codex/sessions/YYYY/MM/DD/`; completed Codex Desktop automation runs may already have moved into `~/.codex/archived_sessions/` even when the index entry is from the current day.
Codex Desktop session files currently use rollout-style names such as `rollout-2026-05-20T09-01-36-<id>.jsonl`; use the filename timestamp only to narrow the search window, then make the real cutoff decision from `session_meta.payload.timestamp`.
Treat the embedded id as something you verify from `session_meta`, not as a filename pattern you have to guess manually.
When an automation runs in worktree mode, do not expect `session_meta.cwd` to equal the source repo path from `automation.toml`. Match both the configured source `cwd` and Codex worktree variants such as `~/.codex/worktrees/*/<repo-tail>` where `<repo-tail>` is the trailing project path like `private/Portfolio` or `shared-ai-docs`.

Avoid starting with broad `find ~/.codex ...` scans, and do not rely on GNU-only `find -newermt` semantics because they are not portable across Daniel's macOS environment.
Do not start with broad `rg --files ~/ ... ~/.codex` discovery either; it pulls in unrelated shell history, prompts, and app resources and adds noise without improving session selection.
Do not assume `~/.codex/session_index.jsonl` contains `cwd` or file paths. In current Codex Desktop runs it may expose only `id`, `thread_name`, and `updated_at`. Use it as a coarse recency index first, then resolve `cwd`, prompt, and workspace scope from `session_meta` inside the actual session file.
Do not assume `session_meta` repeats the thread title from the index. In current Codex Desktop logs it may have no `title` or `thread_name` at all, so use the index for human-readable names and the session file for authoritative `id`, `cwd`, and timestamps.
Do not convert a session id directly into a guessed rollout filename. Resolve candidate files from bounded day folders first, then confirm the id from each file's `session_meta` payload.
If an id from `session_index.jsonl` is not present in the bounded day folders you already chose, check `~/.codex/archived_sessions/` for `rollout-*<id>*.jsonl` next. Do not escalate to `rg ~/.codex/sessions ~/.codex/archived_sessions` across the whole store just to rediscover one archived file.
`session_index.jsonl` timestamps may vary in fractional-second precision. Normalize them once in a bounded parser instead of retrying ad hoc `datetime.fromisoformat(...)` snippets or shell date conversions.
When you need `cwd` or a prompt snippet from the actual session files, prefer a short bounded `python3` extractor over ad hoc retries. Example:

```bash
python3 - <<'PY'
import json, glob, os, re
from datetime import datetime
cutoff = datetime.fromisoformat("2026-05-18T07:50:46+00:00")

def parse_ts(raw):
    raw = raw.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    m = re.match(r"^(.*\.)(\d+)([+-]\d\d:\d\d)$", raw)
    if m:
        frac = m.group(2)
        raw = m.group(1) + frac[:6].ljust(6, "0") + m.group(3)
    return datetime.fromisoformat(raw)

for path in sorted(glob.glob(os.path.expanduser("~/.codex/sessions/2026/05/18/*.jsonl"))):
    meta = None
    for line in open(path):
        obj = json.loads(line)
        if obj.get("type") == "session_meta":
            meta = obj["payload"]
            break
    if not meta:
        continue
    ts = parse_ts(meta["timestamp"])
    if ts > cutoff:
        print(meta["timestamp"], meta.get("cwd"), path)
PY
```

When reviewing several sibling automation sessions, do not inspect JSONL structure one file at a time. Start with one bounded extractor that prints `session_meta`, first user prompt snippet, and function-call names for all candidate files so you can identify the few logs worth deeper inspection before reading raw events.
Do not start raw session inspection with `sed -n`, `head`, or wide `rg` against individual JSONL files just to discover their structure. Use those only after a bounded extractor has already identified a specific session and you need one targeted evidence snippet.

For Codex Desktop JSONL logs, do not assume Claude-style top-level `message` or `tool_call` records. In current Codex session files:

- `session_meta` still contains the authoritative session id, timestamp, and `cwd`
- `session_meta` often does not carry a useful thread title; use the `session_index.jsonl` `thread_name` as the human label and join it back by session id when you need that context
- user and assistant messages usually appear as `response_item` records whose payload has `type == "message"` plus `role`
- tool calls usually appear as `response_item` records whose payload has `type == "function_call"` and may also be nested under `payload.item.type == "function_call"` depending on recorder/version

Build extractors around `response_item` first, and only fall back to raw event inspection if a bounded sample shows a different shape. Do not spend multiple retries on parsers that expect top-level `message` or `tool_call` rows.
If your first bounded extractor already yields `session_meta`, user messages, and function-call names, do not switch back to ad hoc per-file probing unless you need a quoted evidence excerpt for the final report.

Starter extractor for Codex Desktop sessions:

```bash
python3 - <<'PY'
import json, glob, os
for path in sorted(glob.glob(os.path.expanduser("~/.codex/sessions/2026/05/21/*.jsonl"))):
    meta = None
    first_user = None
    calls = []
    with open(path) as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("type") == "session_meta":
                meta = obj["payload"]
                continue
            if obj.get("type") != "response_item":
                continue
            payload = obj.get("payload", {})
            if payload.get("type") == "message" and payload.get("role") == "user" and not first_user:
                texts = [item.get("text", "") for item in payload.get("content", []) if item.get("type") == "input_text"]
                first_user = " ".join(texts)[:220]
            elif payload.get("type") == "function_call":
                calls.append(payload.get("name"))
    if meta:
        print(meta["timestamp"], meta.get("cwd"), first_user, calls[:10], path)
PY
```

If you need to parse JSON piped from another command, do not combine the producer with `python3 - <<'PY'` on the same pipeline because the heredoc consumes stdin. Use `python3 -c '...'`, a temp file, or inspect the raw JSON first.

For each candidate session, capture:

- session id or file path
- timestamp
- project or workspace scope
- relevant user request
- evidence snippets showing tool retries, doc lookup, or out-of-skill discovery

Session selection rule:

- Prefer sessions whose `cwd` matches the active workspace/task path.
- For automation worktree runs, also treat `~/.codex/worktrees/*/<repo-tail>` as in-scope when the suffix matches one of the automation `cwds`; do not drop those sessions as cross-workspace noise.
- Only include cross-workspace sessions if the user explicitly asked for a cross-project review.
- For automation runs, inspect `~/.codex/automations/<automation-id>/automation.toml` and `memory.md` before broad session-log discovery so prompt intent and pending diffs are known up front.
- Exclude sibling `Learn` runs created by the same automation fan-out unless they provide direct evidence of automation drift or a weakness in this skill itself.
- If sibling `Learn` fan-out runs all show the same discovery pattern, treat that repetition as one skill-gap finding with multiple evidence points, not as unrelated noise.

### Step 2: Identify improvement-worthy patterns

Look for patterns such as:

- repeated `grep` or folder traversal to learn structure before work starts
- repeated attempts to find the correct CLI or invocation syntax
- fallback chains like Python, JS REPL, shell, then another shell strategy
- repeated manual chunking or helper-script creation for tasks that recur
- repeated documentation fetches after a skill already triggered

Focus on root cause. Do not just say "the agent explored." Explain what guidance was missing.

For automation-run sessions, compare the automation prompt against the tools actually available in that run. If the prompt calls for a missing tool or workflow primitive, classify that as an automation-instruction issue first instead of letting repeated tool or filesystem probing dominate the diagnosis.

### Step 3: Improve existing skills when justified

If the evidence points to a specific skill weakness, update that skill directly.

Typical improvements:

- make the description more trigger-friendly
- add missing tool-choice rules
- add CLI invocation examples
- add path conventions, folder anchors, or search strategy guidance
- add "when not to use" boundaries to reduce confusion
- add required report format when outcomes were inconsistent

Keep edits minimal and evidence-driven. Do not rewrite unrelated sections.

Automation-instruction review:

- When the reviewed session is itself an automation run, separately decide whether the drift came from a weak skill or from weak automation instructions.
- Skills should contain the reusable "how to do this kind of task" knowledge.
- Automation prompts should contain task-specific scope, project paths, required outputs, and state-file conventions.
- Automation prompts should not depend on a named task/todo tool without a fallback when that tool may be absent from some run environments.
- Do not auto-edit automations during an improve-skills run unless the user explicitly asked for that behavior.
- Record high-value automation prompt changes as proposed diffs in the report and memory. If a dedicated task or todo tool is unavailable in the current environment, mark the suggestion as deferred rather than silently dropping it.
- When a high-value automation prompt diff is deferred because the task/todo tool is unavailable, persist a `Pending automation prompt diffs` section in memory with the target automation, rationale, and a unified diff snippet.
- On the next run, check that pending section before reviewing new sessions. If the user has accepted a deferred automation diff in the meantime, back up the target `automation.toml` first and then apply the approved change.
- If the automation prompt explicitly says "Create User Todo" but no such tool exists in the run, do not spend time searching for a substitute tool. Record the diff under `Pending automation prompt diffs`, call out the missing-tool mismatch in the report, and continue.

### Step 4: Track new-skill candidates in memory

Store recurring discovery patterns in the explicit automation memory when one was provided.
Otherwise store them in `/memories/improve-skills.md`.
If `/memories` is unavailable, store them in the reused fallback note path and explicitly mention that path in the report.

For each candidate, keep one concise entry with:

- `name`
- `scope`
- `counter`
- `signal`
- `latest_evidence`
- `suggested_skill_or_playbook`

When the same candidate appears again, increment the existing counter instead of creating a duplicate entry.

Good candidate examples:

- understanding a recurring nested folder structure before acting
- finding the right CLI for a specialized file transformation
- iterating through multiple execution environments to find one that works
- repeatedly splitting oversized tasks into stable helper flows
- repeatedly hunting for session stores, automation files, or missing task/todo tooling before the real review work can begin

### Step 5: Escalate strong candidates

Always call out a candidate in the report when either condition is true:

- the counter is greater than 3
- the pattern is obviously high leverage even with fewer occurrences

Explain whether it should become:

- a new general skill
- a project-scoped playbook
- an addition to an existing skill

## Update Rules For Skills

Only update a skill when the evidence is specific enough to support a concrete improvement.

Good reasons to edit a skill:

- missing CLI syntax or required flags
- missing decision criteria for choosing between tools
- missing examples for a repeated workflow
- weak trigger description that caused a missed invocation
- missing instructions for bounded discovery before action

Bad reasons to edit a skill:

- one-off user preference changes with no recurrence
- genuinely new external documentation that the skill could not have predicted
- random agent drift without a clear pattern

When editing a skill, include in the report:

- which file changed
- what evidence triggered the update
- what instruction was added or clarified
- why the change should reduce future discovery cost

## Report Format

Use this structure exactly:

```markdown
# Improve Skills Report

## Run Summary
- Processed window:
- Sessions reviewed:
- Existing skills updated:
- New candidate counters changed:

## Skill Updates
- [skill-name] scope=<general|project:...> reason=... change=... evidence=...

## New Or Escalated Candidates
- [candidate-name] scope=<general|project:...> counter=<n> signal=... recommendation=...

## Notable Discovery Patterns
- session=... pattern=... classification=... note=...

## Deferred Items
- item=... reason=...

## Cursor Update
- newest_session_timestamp:
- last-run file updated:
```

If no skill changes are warranted, say so explicitly. Still report candidate counter changes and deferred items.

If active-thread evidence exists but has not yet been persisted to session logs, mark it as provisional in the report and do not advance the cursor past the newest persisted session timestamp.

## Practical Heuristics

- Prefer a small number of high-confidence skill edits over many speculative edits.
- If one finding can be fixed by improving an existing skill, prefer that over creating a brand new skill.
- Project-specific structure-discovery patterns usually belong in project playbooks, not global skills.
- If the same discovery pattern appears in multiple unrelated projects, upgrade it from project-scoped to general.
- When unsure whether something is a skill gap or a one-off, record it as a candidate and wait for another occurrence.
- If the automation text itself is the root cause, prefer one explicit deferred prompt diff over repeated attempts to rediscover an equivalent missing tool.

## Example Findings

**Example 1: Existing skill unclear**

- Session shows a PDF-related skill was used.
- Agent still searched docs for the basic CLI flags needed to merge files.
- Action: update the PDF skill with the exact CLI pattern and a short tool-choice note.

**Example 2: New project-scoped playbook**

- Agent repeatedly walks the same nested project directories to discover build artifacts.
- Pattern only appears in one repository.
- Action: record a `project-scoped-playbook` candidate and increment its counter.

**Example 3: High-value general candidate**

- Multiple sessions show fallback across Python, shell, and alternate CLIs just to process one file type.
- Action: raise the candidate prominently in the report even if no new skill is created yet.
