# AGENTS.md

## Project Orientation
shared-ai-docs is Daniel's shared repository for AI documentation, Codex skills, prompts, hooks, RAG/QMD guidance, n8n workflow assets, and automation support material used across the DanielsVault repositories. When starting work in this repository, read `README.md` first, then read the OpenSpec and documentation sources relevant to the request before changing code or docs:

- `README.md`
- `openspec/specs`
- active change material under `openspec/changes/*`
- `docs/rag` for RAG and QMD operating guidance
- `docs/specops` for SpecOps architecture and workflow notes
- `docs/skills` and `skills-repo/skills` for skill authoring and maintenance
- `n8n/README.md` and `n8n/workflows/README.md` for n8n workflow work

Do not treat scripts or skill bodies as the only source of truth. Requirements and accepted behavior belong in OpenSpec specs and active changes when the work affects durable workflow behavior.

## Start Work Checklist
Before editing specs, skills, automation assets, or docs:

1. Run `git status --short` and note existing user or agent changes.
2. Identify whether an active OpenSpec change is relevant to the request.
3. Read relevant specs or docs before implementation details.
4. Decide whether the request belongs to an existing change or needs a new change.
5. State that decision and the reason before editing requirements or code.

## Development Cycle
Use the `$tdd` skill for feature work and bug fixes in scripts, testable tooling, and behavior-bearing automation code. Work in small vertical slices:

1. Add or update the relevant OpenSpec requirement, scenario, or durable workflow note.
2. Add one failing behavior test or the narrowest reproducible verification through the public interface.
3. Implement the minimum change needed to pass.
4. Repeat for the next behavior.
5. Refactor only after tests or checks are green.
6. Run relevant tests or validation, plus `openspec validate <change-id> --strict` when an OpenSpec change is involved.

For feature/spec work, keep active `tasks.md` files current enough that another agent can resume the work. Skip task churn for tiny documentation, config, or mechanical maintenance edits.

## OpenSpec Change Policy
- Create a new change when the user explicitly asks for one.
- If a current-session open change already covers the same behavior, continue that change.
- If no open change exists, create one for behavior or requirement changes unless the request is very small or not a spec change.
- Documentation-only edits, skill wording fixes, workflow examples, and narrow maintenance usually do not need a new spec change.
- Bug fixes still start with a failing test or reproducible check. Add intended behavior to the original spec/change rather than creating an unrelated requirement.
- When in doubt, state the reasoning before editing specs or code.

## Change Completion
A spec/change is not done only because files were edited, checks pass, or OpenSpec validation succeeds. It is ready for acceptance/archive only after the intended behavior has been verified through the most direct surface available: skill invocation behavior, script output, generated docs, RAG/QMD results, n8n workflow behavior, or automation logs.

Before archiving any OpenSpec change, perform a refactoring pass over the code, skills, and specs touched by that change. Inspect both the current diff and nearby context for:

1. DRYness: duplication introduced by the change or nearby repeated patterns now worth consolidating.
2. SOLID issues: mixed responsibilities, hard-to-test boundaries, or abstractions that are difficult to replace.
3. KISS issues: accidental complexity, unclear names, needless branching, or structure larger than the current spec requires.

Preserve behavior during this pass and rerun the relevant tests or checks afterward. 

For langgraph-github-issue-pilot, prefer verification through:
- local application endpoints
- behavior tests
- application logs proving the end-to-end flow
- screenshots of UIs
- GitHub Issues you created to show end-to-end behavior

If end-to-end verification is not possible, state exactly why and what lower-level verification was performed instead.
If end-to-end verification is not possible, state exactly why and what lower-level verification was performed.

## Implementation Notes
- `skills-repo/skills` contains reusable Codex skills. Keep skill instructions concise, task-focused, and backed by referenced docs or scripts when details are too large for `SKILL.md`.
- `docs/rag` and `docs/specops` are canonical documentation areas for RAG/QMD and SpecOps work.
- `n8n` contains workflow assets and local runtime data. Do not commit secrets from `.env`, runtime databases, logs, or generated n8n data unless the user explicitly asks and the file is safe to version.
- Prefer repo-relative paths in examples. Avoid hard-coded absolute paths unless documenting a known local-only integration.

## Build & Test Commands
Use the narrowest command that proves the change:

```bash
openspec validate <change-id> --strict
git diff --check
```

When changing a specific script, skill, or workflow, run its local verification command or document why no executable check exists.

## Do / Don't Rules
- Do preserve existing user changes and mention unrelated dirty state when it affects verification.
- Do keep generated guidance and examples truthful to the files that exist in this repo.
- Do update OpenSpec specs or active changes for durable behavior changes.
- Don't commit local secrets, runtime databases, logs, or private payloads from n8n or automation runs.
- Don't bulk-copy reference docs into AGENTS files; link to canonical docs instead.

## Agent skills

### Issue tracker

Issues are tracked as local Markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Triage uses the five default canonical label strings. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses the single-context layout. See `docs/agents/domain.md`.
