# AGENTS.md Principles

Source guide: https://www.aihero.dev/a-complete-guide-to-agents-md

## Core Principles

- Treat `AGENTS.md` as always-loaded context with a tight instruction budget.
- Keep the root file as small as possible.
- Start with a one-sentence project description.
- Include package manager/build/test commands only when they are non-obvious or canonical.
- Use progressive disclosure: link to docs, nested `AGENTS.md` files, or skills for details that are not relevant to every task.
- Prefer stable capabilities, domain concepts, and canonical entry points over exhaustive file maps.
- Avoid generated, comprehensive, or "just in case" guidance.
- Avoid obvious rules such as "write clean code" or "follow best practices."
- Remove or resolve contradictions instead of adding another rule on top.

## What Goes Where

Root `AGENTS.md`:
- repo purpose
- shared package manager/tooling
- canonical commands that every agent should know
- critical guardrails that prevent costly mistakes
- breadcrumbs to deeper docs

Nested `AGENTS.md`:
- package/service purpose
- package-specific commands and conventions
- local runtime details
- local test strategy

Separate docs:
- language conventions
- testing patterns
- API design rules
- deployment/runbooks
- security policies
- domain glossaries and architecture decisions

Skills:
- reusable workflows that should not load on every prompt
- task-specific procedures such as TDD, diagnosis, release, review, or doc research

## Migration Pattern From This Session

When replacing a deprecated context-bootstrap skill with repo `AGENTS.md` files:

1. Read the deprecated skill and all files it references.
2. Identify durable knowledge:
   - canonical README/spec/doc entry points
   - build/test/runtime command locations
   - architecture or service-boundary summaries
   - ops/security docs that agents should know exist
   - incident or watcher workflows that are specific to the repo
3. Exclude skill mechanics:
   - auto-load triggers
   - output contracts
   - workflow routing tables
   - confidence rubric details
   - copied reference docs
4. Add concise summaries and breadcrumbs to each affected repo's `AGENTS.md`.
5. Delete the deprecated skill only after verifying important content is represented.

## Smell Checklist

Before finalizing, ask:
- Would this instruction matter for almost every task in the repo?
- Is this path likely to stay valid?
- Could this be a link to a canonical doc instead of pasted text?
- Is this a repo-specific guardrail, or something the base agent already knows?
- Does this duplicate another file that is easier to keep current?
- Will a future agent know where to go next without loading a wall of context?
