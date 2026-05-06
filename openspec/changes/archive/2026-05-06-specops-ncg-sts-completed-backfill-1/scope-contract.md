# Scope Contract

## In Scope

1. Import the first bounded NCG docs Specs subset from `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/Completed/`.
2. Use the coherent 2026-04-06 STS completed slice group:
   - `01 STS Security Flow Correctness Hotfixes`
   - `02 STS Registration and Enumeration Hardening`
   - `03 STS Compose and Pipeline Contract Alignment`
   - `05 STS Reverse Proxy Reintroduction and Edge Exposure Model`
   - `07 STS Legacy Cutover Execution and Release Gate`
   - `08 STS Legacy-to-New E2E Cutover Validation`
   - `09 STS User Data Migration Execution`
3. Create one primary SpecOps `type: spec` entity note per selected source.
4. Update inventory, Control Spec and backlog counts for NCG docs Specs from 0/29 to 7/29.

## Out Of Scope

1. No edits to NCG source specs.
2. No runtime implementation or validation inside `ncg-backend` or `ncg-security-token`.
3. No import of active NCG root specs in this run.
4. No import of the large MariaDB migration history spec in this run.
5. No OpenSpec relationship audit.

## Acceptance Targets

1. Exactly 7 new entity notes exist for batch `historical-001-ncg-sts-1`.
2. All 7 selected source paths are represented exactly once.
3. NCG docs Specs represented-source count increases from 0/29 to 7/29.
4. No duplicate NCG docs Specs source paths exist across SpecOps spec/document entities.
5. No `source_type: openspec_change_artifact` primary entity is created.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Count all NCG docs Specs source files.
2. Count NCG docs Specs sources represented in SpecOps entities.
3. Count batch `historical-001-ncg-sts-1`.
4. Run selected-source missing guard.
5. Run duplicate NCG docs Specs source guard.
6. Run negative OpenSpec artifact guard.
7. Run `openspec validate specops-ncg-sts-completed-backfill-1 --strict --json`.
8. Run `openspec status --change specops-ncg-sts-completed-backfill-1 --json`.
9. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. The active parent STS onboarding spec is referenced by `parent_source` because it is not imported in this run.
2. Runtime validation is not applicable because this change only creates SpecOps metadata/entity notes.
3. The selected Completed sources are treated as accepted because each source has an Accepted status header and no formal missing/decision/blocked markers.
