---
name: write-agents-md
description: Create, refactor, migrate, or review repository AGENTS.md files using progressive disclosure. Use when the user asks to write or update AGENTS.md, consolidate repo agent instructions, migrate bootstrap/skill knowledge into repo guidance, split oversized AGENTS.md files, add repo-specific agent guardrails, or ensure important context is preserved before deleting deprecated skills or docs.
---

# Write AGENTS.md

## Overview

Write compact, durable repo guidance for coding agents. Preserve important context by summarizing stable facts and routing agents to the right docs, not by copying reference files into `AGENTS.md`.

Read [agents-md-principles.md](references/agents-md-principles.md) when the task involves refactoring a large file, migrating context from another source, or deciding what belongs in root vs nested guidance.

If this task is running inside a Codex automation and the prompt or local workflow expects an automation memory file, resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` before any memory read or write. Do not read from or write to raw `$CODEX_HOME/...` paths when `$CODEX_HOME` may be unset.

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
If the task runs from a Codex automation worktree, resolve the actual repo root with `git rev-parse --show-toplevel 2>/dev/null` once if needed, then inspect the target repo directly.
If the task is an automation run with `Automation ID:` / memory metadata in the prompt, normalize Codex home first and read those files before repo reads or memory-path debugging:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
sed -n '1,200p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml" 2>/dev/null || true
sed -n '1,200p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md" 2>/dev/null || true
```

Do not probe raw `$CODEX_HOME` with `printf`, `ls`, or `test -f` inside `set -u` shells before this normalization. In Daniel's environment, `~/.codex` is the default unless the prompt proves otherwise.

### 2. Inspect Before Writing

Use local sources first:
- existing `AGENTS.md`, nested `AGENTS.md`, `CLAUDE.md`, and `.codex`/`.agents` files
- `README.md`, package manifests, solution files, compose files, task runners, test configs
- local specs or architecture docs such as OpenSpec, ADRs, docs folders, and runbooks
- repo-local skills when they document operational workflows

When the task is an automation run with persisted memory, normalize Codex home once and read the named automation files directly instead of probing:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
sed -n '1,200p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md" 2>/dev/null || true
sed -n '1,200p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml" 2>/dev/null || true
```

For recurring AGENTS-maintenance automations, use this startup order:
1. resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` once
2. read the named automation `memory.md` and `automation.toml`
3. read the target repo `AGENTS.md` plus one canonical root doc such as `README.md`
4. run one bounded `rg --files` inventory for manifests, test runners, compose/task files, and nested `AGENTS.md`
5. read only the repo-local docs or skills that the bounded inventory points to

Do not probe raw `$CODEX_HOME/...` first when the variable may be unset.
Prefer targeted file reads and `rg --files` from the confirmed repo root. Avoid `pwd && ls -la && find .. -name AGENTS.md` style orientation probes unless the target repo truly cannot be identified from the prompt, cwd, or git root.
Do not start recurring AGENTS-maintenance runs with `git remote -v`, `git log`, `git ls-tree -r HEAD`, or broad `find` over parent directories just to infer the repo structure. Use those only if local docs and bounded file inventory still leave a concrete uncertainty that matters for the guidance.
For update-style automation runs, start from the existing root `AGENTS.md`, the main `README.md`, and the few canonical docs or specs most likely to contain new durable workflow facts. Do not escalate to broad repo inventories such as `git ls-tree -r`, `find . -maxdepth 4`, `git remote -v`, or multi-tree `find openspec ...` scans unless those first reads fail to identify the relevant workflow source.
When the repo is still sparse or mostly scaffolding, prefer a minimal `AGENTS.md` derived from the concrete files that exist. Do not pad the discovery pass with commit history or remote inspection just to manufacture more guidance.

Use web only when the user asks for a specific external guide or the local source points to one. When using external guidance, cite the URL in the final response.

### 3. Decide What Belongs

Keep root `AGENTS.md` small. Include only guidance that is relevant to nearly every task in that repo:
- one-sentence project orientation
- essential startup checklist, only when the repo truly needs one
- package manager or non-obvious build/test/runtime commands
- critical guardrails that prevent expensive mistakes
- pointers to deeper docs for language rules, testing, CI, architecture, ops, security, or domain details

Prefer capabilities over brittle file maps. Mention stable directories and canonical docs, but avoid long inventories that will go stale.
Do not spend space on obvious defaults that Codex already knows unless the repo has a meaningful local variant.

### 4. Draft Structure

Use only sections that fit the repo:

```markdown
# AGENTS.md

## Project Orientation
One sentence describing what this repo is and why it exists.

## Start Work Checklist
1. Run `git status --short`.
2. Read the canonical docs/specs relevant to this request.
3. State the change/spec decision before editing when the repo requires it.

## Context & Docs
Short breadcrumbs to canonical docs and what each is for.

## Do / Don't Rules
Small list of high-impact repo-specific guardrails.

## Build & Test Commands
Only non-obvious or canonical commands.

## Development Cycle
Repo-specific workflow expectations, if any.

## Commit / PR Guidelines
Only if the repo has a real convention.
```

For monorepos, keep root guidance about the monorepo and shared tooling. Add nested `AGENTS.md` files for package-specific commands, conventions, and runtime details.
If the existing file is oversized, split detailed workflows into deeper docs or nested `AGENTS.md` files and leave short breadcrumbs in the root file.

### 5. Migrate From Deprecated Sources

When replacing a skill or bootstrap document:
- read the skill body and every referenced file
- extract stable, important content such as canonical docs, command entry points, deployment constraints, and security rules
- discard invocation mechanics, output contracts, auto-load triggers, and duplicated docs
- summarize the extracted content into `AGENTS.md` as breadcrumbs and durable rules
- when the source contains too much detail for root `AGENTS.md`, create or reuse a deeper doc and link to it instead of flattening everything into the root file
- remove the deprecated source only after verifying the replacement covers the important content

### 6. Validate

Before finishing:
- run `git status --short` in every affected repo
- compare the new guidance against the old sources for unresolved contradictions
- inspect the diff for accidental bulk copy, stale paths, contradictions, and over-specific file maps
- check whether any line is redundant, vague, or obvious enough to delete
- search for deprecated source names if deleting or migrating one
- confirm the target `AGENTS.md` points to deeper docs instead of embedding them
- mention any unrelated dirty worktree state separately
- when writing automation memory or user-facing notes, normalize home-directory paths to `~/...` instead of `/Users/...`
