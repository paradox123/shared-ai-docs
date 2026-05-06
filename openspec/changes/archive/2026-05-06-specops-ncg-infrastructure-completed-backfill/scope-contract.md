# Scope Contract

## In Scope

1. Import the final 8 NCG docs Specs sources from `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Specs/Completed/`.
2. Create one primary SpecOps `type: spec` entity note per selected source.
3. Mark historical marker conflicts with `metadata_quality: conflict` where Completed-path status conflicts with old open markers.
4. Update inventory, Control Spec and backlog counts for NCG docs Specs from 21/29 to 29/29.

## Out Of Scope

1. No edits to NCG source specs.
2. No runtime implementation or validation inside `ncg-backend`.
3. No OpenSpec relationship audit.
4. No automated metadata reconstruction or marker cleanup.

## Acceptance Targets

1. Exactly 8 new entity notes exist for batch `historical-001-ncg-infrastructure-final`.
2. All 8 selected source paths are represented exactly once.
3. NCG docs Specs represented-source count increases from 21/29 to 29/29.
4. No duplicate NCG docs Specs source paths exist across SpecOps spec/document entities.
5. No `source_type: openspec_change_artifact` primary entity is created.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Count all NCG docs Specs source files.
2. Count NCG docs Specs sources represented in SpecOps entities.
3. Count batch `historical-001-ncg-infrastructure-final`.
4. Run selected-source missing guard.
5. Run duplicate NCG docs Specs source guard.
6. Run negative OpenSpec artifact guard.
7. Run `openspec validate specops-ncg-infrastructure-completed-backfill --strict --json`.
8. Run `openspec status --change specops-ncg-infrastructure-completed-backfill --json`.
9. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. Several sources contain old `[MISSING]`/`[DECISION]` markers; these are preserved as historical metadata conflicts rather than treated as current blockers for a classification-only import.
2. Runtime validation is not applicable because this change only creates SpecOps metadata/entity notes.
