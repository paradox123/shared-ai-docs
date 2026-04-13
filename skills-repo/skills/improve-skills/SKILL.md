---
name: improve-skills
description: Review Claude session history since the last run to find where existing skills were unclear, missing usage patterns, or failed to prevent avoidable tool discovery. USE WHEN the user asks to improve skills, review sessions for skill gaps, inspect tool usage for unclear instructions, find recurring discovery patterns, or turn repeated agent exploration into improved skills or new skill candidates.
---

# improve-skills

Review recent session history, improve weak skills when the evidence is strong enough, track repeated discovery patterns as future skill candidates, and produce a concise report.

## Goal

Use this skill to inspect sessions since the previous run and answer four questions:

1. Which existing skills should be improved because the instructions were not clear enough?
2. Which tool-usage failures or retries point to missing usage guidance inside a skill?
3. Which repeated discovery behaviors should become new skills or project-scoped playbooks?
4. What changed this run, and what should be escalated in the report?

## Inputs

- Primary source: `.claude/projects/**/*.jsonl`
- Supporting sources when useful: `.claude/history/sessions/**`, `.claude/history/research/**`, `.claude/history/raw-outputs/**`, `.claude/debug/latest`
- Skill files to inspect or update: prefer `.agents/skills/*/SKILL.md`; if unavailable use `.claude/skills/*/SKILL.md`
- Persistent run cursor: prefer `.agents/skills/improve-skills/last-run.json`; if unavailable use `.claude/skills/improve-skills/last-run.json`
- Persistent candidate memory: prefer `/memories/improve-skills.md`; if `/memories` is unavailable, reuse an existing improve-skills report/memory file in the active docs workspace and note the fallback path in the report

Prefer the project session logs first because they preserve tool calls, retries, and agent behavior in sequence.

## First Run And Cursor Handling

Before creating any new memory file, view `/memories/` and reuse an existing improve-skills note if present.
If `/memories/` does not exist, locate an existing improve-skills note/report in the active docs workspace and reuse that path instead of inventing a new random location.

Read `.agents/skills/improve-skills/last-run.json` if it exists; otherwise read `.claude/skills/improve-skills/last-run.json`.

- If it exists, only inspect sessions newer than the stored timestamp.
- If it does not exist, do a bounded first pass over the most recent relevant sessions and say clearly in the report that this was an initial baseline run.
- At the end of a successful run, update the cursor file you used with the timestamp of the newest processed session and a short run summary.

Use a bounded first pass rather than scanning everything blindly.

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

For each candidate session, capture:

- session id or file path
- timestamp
- project or workspace scope
- relevant user request
- evidence snippets showing tool retries, doc lookup, or out-of-skill discovery

### Step 2: Identify improvement-worthy patterns

Look for patterns such as:

- repeated `grep` or folder traversal to learn structure before work starts
- repeated attempts to find the correct CLI or invocation syntax
- fallback chains like Python, JS REPL, shell, then another shell strategy
- repeated manual chunking or helper-script creation for tasks that recur
- repeated documentation fetches after a skill already triggered

Focus on root cause. Do not just say "the agent explored." Explain what guidance was missing.

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

### Step 4: Track new-skill candidates in memory

Store recurring discovery patterns in `/memories/improve-skills.md`.
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

## Practical Heuristics

- Prefer a small number of high-confidence skill edits over many speculative edits.
- If one finding can be fixed by improving an existing skill, prefer that over creating a brand new skill.
- Project-specific structure-discovery patterns usually belong in project playbooks, not global skills.
- If the same discovery pattern appears in multiple unrelated projects, upgrade it from project-scoped to general.
- When unsure whether something is a skill gap or a one-off, record it as a candidate and wait for another occurrence.

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
