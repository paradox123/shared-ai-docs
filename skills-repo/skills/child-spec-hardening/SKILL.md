---
name: child-spec-hardening
description: Harden a planned slice into a narrow OpenSpec change with clear scope, non-goals, write-set/impact, tasks, and verification. Legacy child-spec handoff/index machinery is not required for default Agent Delivery.
---

# Child Spec Hardening

Purpose: improve the active slice contract before implementation. Prefer creating or updating a narrow OpenSpec change over expanding parent/child handoff artifacts.

Canonical workflow: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` -> `Active OpenSpec Scope`.

Use this skill when:
- a slice is plausible but not implementable yet,
- scope, non-goals, verification, or write-set are unclear,
- old child-spec material must be converted into an active OpenSpec change.

Required result:
- one active OpenSpec change or a clear blocker,
- parent/master sources marked reference-only,
- no separate Micro-Spec/Scope Capsule source of truth,
- no default session launch, controller, or archive evidence requirement.

Validator:

```sh
dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change <change-name> [--parent <path>]
```
