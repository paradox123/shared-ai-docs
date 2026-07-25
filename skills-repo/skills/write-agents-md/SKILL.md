---
name: write-agents-md
description: Create, refactor, migrate, or review repository AGENTS.md files using progressive disclosure. Use when the user asks to write or update AGENTS.md, consolidate repo agent instructions, migrate bootstrap/skill knowledge into repo guidance, split oversized AGENTS.md files, add repo-specific agent guardrails, or ensure important context is preserved before deleting deprecated skills or docs.
---

# Write AGENTS.md

## Overview

Write compact, durable repo guidance for coding agents. Preserve important context by summarizing stable facts and routing agents to the right docs, not by copying reference files into `AGENTS.md`.

Default to creating strong, operational `AGENTS.md` files modeled on the recommended OpenSpec/TDD example below unless the user asks for a different style. Keep the file concise, but make sure an agent can tell what to read before touching files, how to work during behavior changes, and what evidence is required before calling the task done.

Read [agents-md-principles.md](references/agents-md-principles.md) when the task involves refactoring a large file, migrating context from another source, or deciding what belongs in root vs nested guidance.

If this task is running inside a Codex automation and the prompt or local workflow expects an automation memory file, resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` before any memory read or write. Do not read from or write to raw `$CODEX_HOME/...` paths when `$CODEX_HOME` may be unset. If this skill is only a support skill inside a session-review automation, defer startup order to the primary review skill instead of applying the AGENTS-maintenance workflow below.
If an AGENTS-maintenance automation asks for "newly discovered workflows", "newly discovered commands", or other session-derived updates since the last run, read the named automation state first, then inspect `"$CODEX_HOME_RESOLVED/session_index.jsonl"` with the normalized cutoff from the canonical review contract before repo discovery. Keep that session pass bounded to the target repo/worktree and only open resolved session files when the index shows relevant post-cutoff activity.
For the automation bootstrap, cutoff comparison, index resolver, and rollout JSONL shapes, follow [codex-desktop-session-review.md](../improve-skills/references/codex-desktop-session-review.md). Do not maintain a second parser recipe here.
Do not guess skill installation paths such as `~/.codex/skills/.system/write-agents-md/SKILL.md`. When the active session already lists this skill, use the listed path. In Daniel's shared setup the reusable copy normally lives at `~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/write-agents-md/SKILL.md`.

## Workflow

### 1. Establish Scope

Determine whether the target is:
- a new root `AGENTS.md`
- an update to an existing root `AGENTS.md`
- a nested `AGENTS.md` for a package/service/subtree
- a migration from a deprecated skill, `CLAUDE.md`, README, runbook, or bootstrap document

If moving context from another source, inspect the source and its references before deleting anything. Separate durable repo knowledge from workflow mechanics that no longer belong in always-loaded context.
Before drafting, explicitly list:
- contradictions between current guidance sources
- redundant or obvious instructions that can be deleted
- content that belongs in a deeper doc or nested `AGENTS.md` instead of the root file

When the prompt already provides repo-local `AGENTS.md` instructions or an explicit target `cwd`, treat that as the target scope immediately. Do not start with `pwd`, `ls`, `find ..`, or sibling-worktree probing just to rediscover which repository you are in.
If the task runs from a Codex automation worktree, resolve the actual repo root with `git rev-parse --show-toplevel 2>/dev/null` once if needed, then inspect the target repo directly. Do not substitute hand-guessed absolute paths such as `~/Documents/NCG/...` for the actual `cwd`, configured automation `cwds`, or `git rev-parse` result.
If the task is an AGENTS-maintenance automation run with `Automation ID:` / memory metadata in the prompt, normalize Codex home first and use the canonical bootstrap linked above before resolving the target repo. The visible index read must be a recent bounded tail, such as `tail -n 120`; never print the full ledger or a stale beginning slice. Parse the full index only inside the compact cutoff/worktree resolver.

Do not probe raw `$CODEX_HOME` with `printf`, `ls`, or `test -f` inside `set -u` shells before this normalization. In Daniel's environment, `~/.codex` is the default unless the prompt proves otherwise.

### 2. Inspect Before Writing

Use local sources first:
- existing `AGENTS.md`, nested `AGENTS.md`, `CLAUDE.md`, and `.codex`/`.agents` files
- `README.md`, package manifests, solution files, compose files, task runners, test configs
- local specs or architecture docs such as OpenSpec, ADRs, docs folders, and runbooks
- repo-local skills when they document operational workflows

For recurring AGENTS-maintenance automations, use this startup order:
1. resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` once
2. read the named automation `automation.toml` and the character-capped memory excerpt from the canonical bootstrap
3. if the prompt asks for newly discovered workflows or commands since the last run, normalize all configured cutoff candidates, show only a recent bounded index tail, and run the central full-index resolver before repo discovery
4. resolve the target repo from the current `cwd` or `git rev-parse --show-toplevel`, not from hardcoded sibling paths
5. read the target repo `AGENTS.md` plus one canonical root doc such as `README.md`
6. run one bounded `rg --files` inventory for manifests, test runners, compose/task files, and nested `AGENTS.md`
7. read only the repo-local docs or skills that the bounded inventory points to

Do not probe raw `$CODEX_HOME/...` first when the variable may be unset.
Prefer targeted file reads and `rg --files` from the confirmed repo root. Avoid `pwd && ls -la && find .. -name AGENTS.md` style orientation probes unless the target repo truly cannot be identified from the prompt, cwd, or git root.
Do not start recurring AGENTS-maintenance runs with `git remote -v`, `git log`, `git ls-tree -r HEAD`, or broad `find` over parent directories just to infer the repo structure. Use those only if local docs and bounded file inventory still leave a concrete uncertainty that matters for the guidance.
For update-style automation runs, start from the existing root `AGENTS.md`, the main `README.md`, and the few canonical docs or specs most likely to contain new durable workflow facts. Do not escalate to broad repo inventories such as `git ls-tree -r`, `find . -maxdepth 4`, `git remote -v`, or multi-tree `find openspec ...` scans unless those first reads fail to identify the relevant workflow source.
When the repo is still sparse or mostly scaffolding, prefer a minimal `AGENTS.md` derived from the concrete files that exist. Do not pad the discovery pass with commit history or remote inspection just to manufacture more guidance.

Use web only when the user asks for a specific external guide or the local source points to one. When using external guidance, cite the URL in the final response.

### 3. Decide What Belongs

Keep root `AGENTS.md` small. Include only guidance that is relevant to nearly every task in that repo:
- one-sentence project orientation
- source-of-truth docs and requirement locations, especially `README.md` and OpenSpec files when present
- `Start Work Checklist` with `git status --short`, relevant spec discovery, and change-scope decision
- `Development Cycle` with TDD, vertical slices, behavior tests through public interfaces, and active task tracking
- `OpenSpec Change Policy` when the repo uses OpenSpec or an equivalent spec/change system
- `Change Completion` with operational verification, refactoring pass, and rerun-test expectations
- package manager or non-obvious build/test/runtime commands
- critical guardrails that prevent expensive mistakes
- pointers to deeper docs for language rules, testing, CI, architecture, ops, security, or domain details

Prefer capabilities over brittle file maps. Mention stable directories and canonical docs, but avoid long inventories that will go stale.
Do not spend space on obvious defaults that Codex already knows unless the repo has a meaningful local variant.

### 4. Use the Recommended Default Example

Use this example as the default for new and existing root `AGENTS.md` files unless the user states otherwise. Replace placeholders with repo-specific details. If a repo does not actually use OpenSpec, TDD, tests, code, or subagents, preserve the lifecycle intent but adapt or omit the false parts instead of adding stale paths or commands.

```markdown
# AGENTS.md

## Project Orientation
[Description of the repo and what it is about]. When starting work in this repository, read `README.md` first for the current runtime architecture, then read the OpenSpec documents so you understand the current scope and capabilities before changing code:

- `README.md`
- `openspec/config.yaml`
- all specs under `openspec/specs`
- all active change specs under `openspec/changes/*/specs`
- active change `proposal.md`, `design.md`, and `tasks.md` only when more context is needed
- past change `proposal.md` and `design.md` if a new spec is in conflict with an old one.

Do not treat implementation code as the only source of truth. Requirements belong in OpenSpec changes.

## Start Work Checklist

Before editing specs or code, do the following:

1. Run `git status --short` and note existing user or agent changes.
2. Identify whether there is an active OpenSpec change relevant to the request.
3. Read the relevant specs before reading implementation details.
4. Decide whether the request belongs to an existing change or needs a new change.
5. State that decision and the reason before editing requirements or code.

## Development Cycle

Use the `$tdd` skill for feature work and bug fixes. Work in small vertical slices:

1. Add or update the relevant OpenSpec requirement/scenario.
2. Add one failing behavior test through the public interface.
3. Implement the minimum code needed to pass that test.
4. Repeat for the next behavior.
5. Refactor only after tests are green.
6. Run the relevant tests and `openspec validate <change-id> --strict`.

Tests should describe observable behavior and avoid coupling to implementation details.

For feature/spec work, keep the active OpenSpec `tasks.md` current enough that another agent can resume the work. Add or update task entries for meaningful behavior changes, but skip task churn for tiny documentation, config, or mechanical maintenance edits.

## OpenSpec Change Policy

If the user explicitly asks to create a new change, create one.

If the user does not explicitly say whether to create a new change, decide from context:

- If an open change is already being worked in the current session and the user's request concerns that same behavior, treat it as part of that change.
- If there is no open change, create a new OpenSpec change for behavior or requirement changes unless the request is very small or not a spec change.
- Documentation-only edits, deployment variable fixes, build plumbing, and similarly narrow maintenance work usually do not need a new spec change.
- Bug fixes should still start with a failing test. The required behavior should be added as an addendum to the original spec/change that defined the intended behavior, rather than as an unrelated new requirement.

When in doubt, make the reasoning explicit before editing specs or code.

## Change Completion

A spec/change is not considered done merely because code is merged, tests pass, or `openspec validate` succeeds. A change is ready to be accepted or archived only after the agent has verified the intended behavior through the most direct operational surface available.

Before archiving any OpenSpec change, perform a refactoring pass over the code and specs touched by that change. The pass must inspect both the current diff and the surrounding implementation context, because a small diff may reveal repeated patterns or structural problems that only become obvious when compared with nearby code.

Do the refactoring pass in these distinct areas in sequence so they are less likely to converge on the same issues, first start a subagent (`Explorer`) to identify potential improvements, then implement them, then start the repeat for the next area:

1. Check for DRYness. Look for duplication introduced by the change and for existing nearby duplication that the change now makes worth consolidating. A change may be small on its own, but if it is the fifth copy of the same idea, it is a refactoring target.
2. Check for SOLID violations. Look for responsibilities that are mixed together, abstractions that are hard to replace or test, interface shapes that force unrelated dependencies, and code paths that require modifying stable code for each new variant.
3. Check whether the implementation can be made simpler under KISS. Remove accidental abstractions, reduce branching, clarify names, and prefer the smallest structure that still supports the tested behavior and current spec.

Treat these instructions as user instructions, and do not skip or shortcut them. If you find that you cannot follow these instructions, state exactly which part you are having trouble with and why.

Preserve behavior during this pass and rerun the relevant tests afterward.

[Concrete steps for verification depending on the given repo / app]

## Implementation Notes

[Implementation-specific notes]
```

Keep this example high-signal. Add repo-specific sections such as `Context & Docs`, `Do / Don't Rules`, `Build & Test Commands`, or `Commit / PR Guidelines` only when they add concrete local value.

### 5. Adapt the Example Without Diluting It

Keep the recommended example as the structural default. Adapt it only to make the generated `AGENTS.md` truthful and repo-specific:
- Replace placeholders with concrete repo description, verification steps, and implementation notes.
- Remove optional add-on sections such as `Build & Test Commands`, `Do / Don't Rules`, or `Commit / PR Guidelines` when they would add no local value.
- Keep `Project Orientation`, `Start Work Checklist`, `Development Cycle`, `OpenSpec Change Policy`, `Change Completion`, and `Implementation Notes` for OpenSpec/TDD repos unless the user asks for a different style.
- If the repo is not OpenSpec/TDD-driven, preserve the same lifecycle roles but rename or adapt the spec/test/change language to the repo's actual source-of-truth workflow.

For monorepos, keep root guidance about the monorepo and shared tooling. Add nested `AGENTS.md` files for package-specific commands, conventions, and runtime details.
If the existing file is oversized, split detailed workflows into deeper docs or nested `AGENTS.md` files and leave short breadcrumbs in the root file.

### 6. Migrate From Deprecated Sources

When replacing a skill or bootstrap document:
- read the skill body and every referenced file
- extract stable, important content such as canonical docs, command entry points, deployment constraints, and security rules
- discard invocation mechanics, output contracts, auto-load triggers, and duplicated docs
- summarize the extracted content into `AGENTS.md` as breadcrumbs and durable rules
- when the source contains too much detail for root `AGENTS.md`, create or reuse a deeper doc and link to it instead of flattening everything into the root file
- remove the deprecated source only after verifying the replacement covers the important content

### 7. Validate

Before finishing:
- run `git status --short` in every affected repo
- compare the new guidance against the old sources for unresolved contradictions
- inspect the diff for accidental bulk copy, stale paths, contradictions, and over-specific file maps
- confirm the generated `AGENTS.md` follows the recommended example unless the user requested a different style
- confirm OpenSpec, `$tdd`, test, and subagent instructions are present only when true or clearly adapted to the repo
- check whether any line is redundant, vague, or obvious enough to delete
- search for deprecated source names if deleting or migrating one
- confirm the target `AGENTS.md` points to deeper docs instead of embedding them
- mention any unrelated dirty worktree state separately
- when writing automation memory or user-facing notes, normalize home-directory paths to `~/...` instead of `/Users/...`
