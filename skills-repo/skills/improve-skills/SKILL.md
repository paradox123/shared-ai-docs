---
name: improve-skills
description: Review Claude/Codex session history to find where existing skills were unclear, missing usage patterns, or caused avoidable discovery. USE WHEN the user asks to improve skills, review sessions for skill gaps, inspect tool-usage failures, evaluate a named skill from recent sessions, or turn repeated agent exploration into skill/playbook candidates.
---

# improve-skills

Review recent session evidence, improve skills only when the evidence supports a compact reusable change, track repeated discovery patterns, and produce a concise report.

For Parent/Child Agent Delivery retrospectives that target a specific parent spec, child index, handoffs, OpenSpec evidence, or workflow self-optimization, prefer `agent-delivery-retro-review` first. Use this skill for broader cross-session skill-gap aggregation.

## Scope Gate

Choose the narrowest review mode that matches the request:

1. **Open diff or current skill text review**: inspect the repo diff or named skill files first. Do not start session-log analysis unless the user asks for session evidence.
2. **Named skill quality review**: inspect only the target skill, its direct repo guidance dependencies, and bounded recent sessions for the named project.
3. **Codex Desktop automation/session review**: use [codex-desktop-session-review.md](references/codex-desktop-session-review.md) for bootstrap, memory, session-index, JSONL, and extractor details.
4. **General cross-session review**: inspect sessions newer than the last-run cursor, filtered by workspace/project relevance.

If multiple modes apply, start with the most concrete evidence source already named by the user. Treat repo-local startup instructions as background unless the chosen mode says repo context is needed.

## Evidence Rules

Treat these as strong signals:

- A relevant skill triggered, but the agent still had to rediscover a basic workflow, path, CLI syntax, tool choice, or output shape.
- The agent retried several tools for the same job because the expected invocation pattern was unclear.
- The agent searched the repo, home directory, session store, or plugin cache to rediscover a stable workflow that should be codified.
- The agent missed a relevant skill because the description under-triggered.
- Several sessions show the same bounded discovery pattern, even if each single instance looks small.

Do not edit a skill for one-off user preference, genuinely novel research, random drift without a clear missing instruction, or facts better owned by project docs, automation prompts, or repo-local `docs/agents/` guidance.

## Skill Entropy Guard

Every skill improvement must reduce net future confusion. Before editing any skill, classify the proposed change as one of:

- replace unclear guidance
- delete misleading or redundant guidance
- move detailed workflow into a reference or script
- narrow the trigger or scope
- add genuinely missing reusable guidance

Prefer the first four over appending new instructions. If a skill already contains the same kind of warning twice, consolidate before adding anything.

Ask these questions before patching:

1. Is this reusable across multiple tasks?
2. Does it belong in this skill, or in repo docs, automation prompts, AGENTS.md, ADRs, a reference, or a script?
3. Is there nearby guidance that should be clarified instead?
4. Would this create a second source of truth?
5. Can the fix be one decision rule instead of a playbook?

## Edit Budget

A skill update should usually be one of:

- description change only
- replace 1-3 bullets
- add one short decision rule
- move a long section into `references/`
- create a script/helper instead of adding procedural text

Avoid net-new long sections in `SKILL.md`. If adding more than about 15 lines, explain in the report why the content cannot live in a reference file, helper script, automation prompt, or project guidance.

## Ownership Rule

Reusable task behavior belongs in one owning skill. Project-specific conventions belong in repo-local guidance. Automation/session startup belongs in the automation/review owner. Tool syntax belongs in the tool skill or a script. Detailed examples belong in references.

Do not copy the same bootstrap, path map, CLI recipe, or policy into support skills. Support skills should defer to the owner.

## Regression Check

After every skill edit, check:

- Did `SKILL.md` get longer?
- Did it add another negative guard?
- Did it duplicate instructions from another skill?
- Did it encode one automation/project incident as global policy?
- Did it make the skill harder to scan in the first 30 seconds?

If yes, revise toward replacement, deletion, delegation, or reference extraction before finishing.

## Classification

Classify each finding by action type:

- `improve-existing-skill`: a current skill needs clearer trigger language, decision rules, examples, path conventions, or tool usage.
- `new-skill-candidate`: no suitable skill exists and the behavior repeats enough to justify one.
- `project-scoped-playbook`: the pattern is real but tied to one repository, folder layout, environment, or project workflow.
- `automation-instruction-change`: the root cause is a task-specific automation prompt/config, not reusable skill knowledge.
- `no-action`: useful evidence, but no durable change is warranted.

Classify scope as `general` or `project:<name>`.

For named skill reviews, keep the output distinction explicit:

- `target-skill-change`: concrete instructions patched into the named skill
- `review-skill-change`: improvements to this workflow because the review itself required avoidable discovery
- `project-playbook-candidate`: repeated project-specific workflow discovery that is not yet general enough for the named skill
- `no-change`: evidence was useful, but the current skill already covers it or the task was novel

## Workflow

1. **Collect bounded evidence.** Use the selected scope gate. For Codex Desktop automation/session reviews, load the reference file and follow its bootstrap exactly.
2. **Identify root cause.** Explain what guidance was missing, not just that the agent explored.
3. **Choose the owner.** Put reusable task knowledge in skills, project conventions in repo docs/playbooks, run-specific scope/state in automation prompts or memory, and detailed mechanics in references/scripts.
4. **Patch sparingly.** Prefer replacing or moving text over appending. Keep `SKILL.md` bodies compact; move fragile command recipes, long examples, and runtime-specific parsers into referenced files or scripts.
5. **Track candidates.** Increment existing candidate counters in the provided automation memory or the configured improve-skills memory. Do not duplicate candidate names.
6. **Report clearly.** Include what changed, why, evidence, deferred items, and cursor/memory updates.

## Update Rules

Good reasons to edit a skill:

- missing CLI syntax, flags, or output shape for a repeated workflow
- missing decision criteria for choosing between tools
- missing path conventions or stable folder anchors
- weak trigger description that caused a missed invocation
- missing "when not to use" or owner-boundary guidance
- repeated bloating of always-loaded skill text that should move into references

Bad reasons to edit a skill:

- one-off task details
- project-specific doctrine that belongs in `docs/agents/`, AGENTS.md, OpenSpec, ADRs, or a project playbook
- automation prompt state that belongs in `automation.toml` or `memory.md`
- external documentation that is expected to change and should be researched when needed

When editing, include in the report:

- which file changed
- what evidence triggered the update
- what instruction was added, removed, replaced, or moved
- why the change should reduce future discovery cost or context load

## Candidate Memory

Store recurring discovery patterns in the explicit automation memory when one was provided. Otherwise use the configured improve-skills memory/cursor path for the environment.

For each candidate, keep one concise entry:

- `name`
- `scope`
- `counter`
- `signal`
- `latest_evidence`
- `suggested_skill_or_playbook`

Escalate a candidate in the report when its counter is greater than 3 or it is obviously high leverage.

## Report Format

Use this structure:

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

If no skill changes are warranted, say so explicitly. If active-thread evidence has not yet been persisted to session logs, mark it as provisional and do not advance the cursor past the newest persisted session timestamp.
