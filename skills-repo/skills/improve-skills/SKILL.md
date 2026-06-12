---
name: improve-skills
description: Review Claude/Codex session history to find where existing skills were unclear, missing usage patterns, or caused avoidable discovery. USE WHEN the user asks to improve skills, review sessions for skill gaps, inspect tool-usage failures, evaluate a named skill from recent sessions, or turn repeated agent exploration into skill/playbook candidates.
---

# improve-skills

Review recent session history, improve weak skills when the evidence is strong enough, track repeated discovery patterns as future skill candidates, and produce a concise report.

## Scope Gate

Choose the narrowest review mode that matches the request:

1. **Open diff or current skill text review**: inspect the repo diff or named skill files first. Do not start session-log analysis unless the user asks for session evidence.
2. **Named skill quality review**: inspect only the target skill, its direct repo guidance dependencies, and bounded recent sessions for the named project.
3. **Codex Desktop automation/session review**: use [codex-desktop-session-review.md](references/codex-desktop-session-review.md) for bootstrap, memory, session-index, JSONL, and extractor details.
4. **General cross-session review**: inspect sessions newer than the last-run cursor, filtered by workspace/project relevance.

If multiple modes apply, start with the most concrete evidence source already named by the user. Treat repo-local startup instructions as background unless the chosen mode says repo context is needed.

When the prompt supplies `Automation ID:`, `Automation memory:`, `Automation:`, or `Last run:`, load the Codex Desktop reference before reading memory paths or probing Codex state. Do not batch memory/Codex-state probes in the same first tool call as this `SKILL.md` read. Normalize `CODEX_HOME` through that reference first; a literal `$CODEX_HOME/...` read is not valid evidence of missing memory when the environment variable is unset.

## Skill Patch Integrity Gate

Before editing any skill, state the skill's current scope in one sentence and compare the requested change against that scope. The skill's scope is not allowed to creep silently.

- If the evidence fits the current scope, patch the existing skill.
- If the evidence is adjacent but would broaden the skill into a new workflow, notify the user and recommend creating a new skill or project playbook instead.
- If only a small boundary clarification is needed, add a "when not to use" or owner-boundary rule rather than expanding the skill's responsibilities.

Do not treat user-provided text as content to paste into a skill. First decide what durable rule it implies, what existing instruction it replaces, and what content becomes obsolete.

## Evidence Rules

Treat these as strong signals:

- A relevant skill triggered, but the agent still had to rediscover a basic workflow, path, CLI syntax, tool choice, or output shape.
- The agent retried several tools for the same job because the expected invocation pattern was unclear.
- The agent searched the repo, home directory, session store, or plugin cache to rediscover a stable workflow that should be codified.
- The agent missed a relevant skill because the description under-triggered.
- Several sessions show the same bounded discovery pattern, even if each single instance looks small.

Do not edit a skill for one-off user preference, genuinely novel research, random drift without a clear missing instruction, or facts better owned by project docs, automation prompts, or repo-local `docs/agents/` guidance.

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
4. **Plan the integration.** Before editing, list whether the patch will add, replace, move, or remove instructions. For every new rule, identify any older wording that becomes redundant, weaker, or contradictory.
5. **Patch by integration, not accumulation.** Prefer replacing, tightening, moving, or deleting text over appending. Keep `SKILL.md` bodies compact; move fragile command recipes, long examples, and runtime-specific parsers into referenced files or scripts.
6. **Review consistency.** After editing, reread the changed skill plus all directly referenced files and metadata in that skill directory. Check that trigger language, workflow steps, references, examples, and reports all describe the same scope and behavior.
7. **Track candidates.** Increment existing candidate counters in the provided automation memory or the configured improve-skills memory. Do not duplicate candidate names.
8. **Report clearly.** Include what changed, why, evidence, deferred items, consistency review, scope decision, and cursor/memory updates.

## Update Rules

Good reasons to edit a skill:

- missing CLI syntax, flags, or output shape for a repeated workflow
- missing decision criteria for choosing between tools
- missing path conventions or stable folder anchors
- weak trigger description that caused a missed invocation
- missing "when not to use" or owner-boundary guidance
- repeated bloating of always-loaded skill text that should move into references
- repeated additive patching that made a skill internally inconsistent or harder for an agent to follow

Bad reasons to edit a skill:

- one-off task details
- project-specific doctrine that belongs in `docs/agents/`, AGENTS.md, OpenSpec, ADRs, or a project playbook
- automation prompt state that belongs in `automation.toml` or `memory.md`
- external documentation that is expected to change and should be researched when needed
- a request that would change the skill's scope instead of clarifying or improving its existing workflow

When editing, include in the report:

- which file changed
- what evidence triggered the update
- what instruction was added, removed, replaced, or moved
- what obsolete or conflicting content was deleted or rewritten instead of merely appended to
- which referenced files and metadata were reviewed for consistency
- whether the change stayed within scope; if not, what new skill or project playbook was recommended instead
- why the change should reduce future discovery cost or context load

After editing, run a "skill coherence check":

- Re-open the edited `SKILL.md` from top to bottom.
- Re-open every directly referenced file used by the skill, plus lightweight metadata such as `agents/*.yaml` when present.
- Search for old terminology, duplicate templates, conflicting startup order, stale examples, and widened trigger language.
- Confirm the skill still has one clear owner, trigger, workflow, and "when not to use" boundary.
- If the consistency pass finds drift, patch it immediately before reporting success.

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
- [skill-name] scope=<general|project:...> reason=... change=... removed_or_replaced=... consistency_check=... evidence=...

## New Or Escalated Candidates
- [candidate-name] scope=<general|project:...> counter=<n> signal=... recommendation=...

## Notable Discovery Patterns
- session=... pattern=... classification=... note=...

## Deferred Items
- item=... reason=...

## Scope Decisions
- skill=... decision=<within-scope|scope-creep-new-skill|project-playbook> note=...

## Cursor Update
- newest_session_timestamp:
- last-run file updated:
```

If no skill changes are warranted, say so explicitly. If active-thread evidence has not yet been persisted to session logs, mark it as provisional and do not advance the cursor past the newest persisted session timestamp.
