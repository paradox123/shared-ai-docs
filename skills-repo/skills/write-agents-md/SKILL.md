---
name: write-agents-md
description: Create, refactor, migrate, or review repository AGENTS.md files using progressive disclosure. Use when the user asks to write or update AGENTS.md, consolidate repo agent instructions, migrate bootstrap/skill knowledge into repo guidance, split oversized AGENTS.md files, add repo-specific agent guardrails, or ensure important context is preserved before deleting deprecated skills or docs.
---

# Write AGENTS.md

## Overview

Write compact, durable repo guidance for coding agents. Preserve important context by summarizing stable facts and routing agents to the right docs, not by copying reference files into `AGENTS.md`.

Read [agents-md-principles.md](references/agents-md-principles.md) when the task involves refactoring a large file, migrating context from another source, or deciding what belongs in root vs nested guidance.

## Workflow

### 1. Establish Scope

Determine whether the target is:
- a new root `AGENTS.md`
- an update to an existing root `AGENTS.md`
- a nested `AGENTS.md` for a package/service/subtree
- a migration from a deprecated skill, `CLAUDE.md`, README, runbook, or bootstrap document

If moving context from another source, inspect the source and its references before deleting anything. Separate durable repo knowledge from workflow mechanics that no longer belong in always-loaded context.

### 2. Inspect Before Writing

Use local sources first:
- existing `AGENTS.md`, nested `AGENTS.md`, `CLAUDE.md`, and `.codex`/`.agents` files
- `README.md`, package manifests, solution files, compose files, task runners, test configs
- local specs or architecture docs such as OpenSpec, ADRs, docs folders, and runbooks
- repo-local skills when they document operational workflows

Use web only when the user asks for a specific external guide or the local source points to one. When using external guidance, cite the URL in the final response.

### 3. Decide What Belongs

Keep root `AGENTS.md` small. Include only guidance that is relevant to nearly every task in that repo:
- one-sentence project orientation
- essential startup checklist, if this repo needs one
- package manager or non-obvious build/test/runtime commands
- critical guardrails that prevent expensive mistakes
- pointers to deeper docs for language rules, testing, CI, architecture, ops, security, or domain details

Prefer capabilities over brittle file maps. Mention stable directories and canonical docs, but avoid long inventories that will go stale.

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

### 5. Migrate From Deprecated Sources

When replacing a skill or bootstrap document:
- read the skill body and every referenced file
- extract stable, important content such as canonical docs, command entry points, deployment constraints, and security rules
- discard invocation mechanics, output contracts, auto-load triggers, and duplicated docs
- summarize the extracted content into `AGENTS.md` as breadcrumbs and durable rules
- remove the deprecated source only after verifying the replacement covers the important content

### 6. Validate

Before finishing:
- run `git status --short` in every affected repo
- inspect the diff for accidental bulk copy, stale paths, contradictions, and over-specific file maps
- search for deprecated source names if deleting or migrating one
- confirm the target `AGENTS.md` points to deeper docs instead of embedding them
- mention any unrelated dirty worktree state separately
