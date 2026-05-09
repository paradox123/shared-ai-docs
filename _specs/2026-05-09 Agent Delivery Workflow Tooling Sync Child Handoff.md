**Date:** 2026-05-09
**Status:** 🟡 Spec
**Scope:** .NET 10 tool for generating and synchronizing Child Session Handoff files from Child Index rows.

---

## Review Control Surface

- Spec-Variante: Tool delivery spec.
- Goldstandard Status: first draft.
- Ziel: Create `skills-repo/tools/SyncChildHandoff.cs` so handoff templates and consistency checks move out of long skill prose.
- In Scope: generate/update handoff markdown for one child, preserve manual notes where possible, sync key fields from Child Index, report drift, dry-run mode.
- Out of Scope: deciding next workflow step, launching sessions, validating implementation readiness beyond handoff/index consistency, editing child specs.
- Wichtigste Test-/Harness-Cases: `HANDOFF-GENERATE-MISSING`, `HANDOFF-SYNC-STALE-VERDICT`, `HANDOFF-DRY-RUN`, `HANDOFF-PRESERVE-NOTES`, `HANDOFF-BLOCK-APPROX-WRITESET`.
- Wichtigste Verification Commands: future `dotnet run ...SyncChildHandoff.cs -- --index <pack> --child <id> --out <handoff>`; `git diff --check`.
- Offene Entscheidungen: Preserve/overwrite policy needs hardening before implementation.
- Readiness Status: DRAFT; needs hardening before implementation.

## Goal

Make Child Session Handoff creation boring and repeatable. The agent should not manually retype the same template fields or drift from the Child Index.

## In Scope

- Read the exact operational Child Index row for `--child`.
- Generate a handoff file when missing.
- Update controlled fields when stale.
- Preserve a marked manual section such as `## Notes Preserved By Sync`.
- Support `--dry-run` and `--check`.
- Emit JSON findings for CI-like checks.

## Out of Scope

- No broad Markdown formatter.
- No launch evidence creation.
- No implementation-ready verdict assignment.

## Acceptance Criteria

1. Missing handoff can be generated from a valid Child Index row.
2. `--check` fails when existing handoff child id, verdict, child spec, target repo or allowed write-set disagrees with the index.
3. `--dry-run` prints the proposed patch without writing files.
4. The generated handoff matches the shared workflow fields needed by `AgentDeliverySessionLauncher.cs`.
5. Approximate write-sets produce a blocking finding unless explicitly allowed for non-delivery hardening handoffs.

## Verification Commands

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/SyncChildHandoff.cs -- --help
git diff --check
```

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |

