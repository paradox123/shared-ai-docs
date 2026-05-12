---
name: spec-change-delivery
description: Execute one bounded change from a narrow active OpenSpec change or direct small request. For Agent Delivery work, implementation must start from Active OpenSpec Scope, not a parent/master spec or session handoff.
---

# spec-change-delivery

Purpose: implement exactly one bounded change. For Agent Delivery, the active OpenSpec change is the implementation contract.

Canonical workflow: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` -> `Active OpenSpec Scope`.

Before edits:
- identify the active OpenSpec change or confirm the work is a truly small direct edit,
- keep parent/master specs reference-only,
- verify scope, non-goals, impact/write-set, tasks, and verification,
- do not require child-session launch, visible-session controller, or archive evidence by default.

Stop if implementation would start from a parent/master spec as a whole.

Validator:

```sh
dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change <change-name> [--parent <path>]
```
