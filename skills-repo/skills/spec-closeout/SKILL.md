---
name: spec-closeout
description: Close an accepted OpenSpec/direct change with verification replay, cleanup evidence when applicable, and documentation sync. Visible-session archive proof is legacy/debug-only, not a default closeout gate.
---

# spec-closeout

Purpose: prove the active change is complete and safe to archive or mark accepted.

Canonical workflow: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` -> `Active OpenSpec Scope`.

Closeout requires:
- active OpenSpec validation when OpenSpec is used,
- verification evidence from the active change,
- cleanup evidence when files/artifacts were removed,
- docs/skills/tests free of references to deleted default workflow inputs.

Cleanup validator:

```sh
dotnet run skills-repo/tools/ValidateAgentDeliveryCleanup.cs -- --manifest openspec/changes/<change-name>/cleanup-manifest.json --root <repo-root>
```
