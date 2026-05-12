---
name: spec-orchestrator
description: Route large specs or parent/master scopes into narrow OpenSpec changes, coverage notes, and next-slice recommendations without releasing implementation directly. Use when a scope is too large, needs slicing, or asks what the next bounded OpenSpec change should be.
---

# spec-orchestrator

Purpose: turn a large scope into one or more small OpenSpec candidates. Do not implement runtime changes and do not release work through child-session handoffs.

Canonical workflow: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` -> `Active OpenSpec Scope`.

Use this skill when:
- a parent/master spec is too large for one implementation pass,
- the user asks for the next slice,
- existing child/session artifacts need to be translated into narrow OpenSpec work.

Output:
- recommended active OpenSpec change name,
- parent/reference sources,
- slice goal, in scope, out of scope,
- write-set or impact area,
- verification expectation,
- deferred scope/backlog notes.

Stop before implementation unless a narrow active OpenSpec change already exists and the user explicitly asks to continue outside this skill.

Validator:

```sh
dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change <change-name> [--parent <path>]
```
