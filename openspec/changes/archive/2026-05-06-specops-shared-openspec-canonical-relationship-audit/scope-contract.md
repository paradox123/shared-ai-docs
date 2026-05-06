# Scope Contract

## In Scope

1. Audit the current canonical OpenSpec specs under `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/specs/`.
2. Map all 11 canonical `spec.md` files to an existing SpecOps target entity, backlog item or accepted control spec.
3. Preserve the existing legacy OpenSpec-derived primary entity `rag-source-precision-gate-harmonization-2026-04-23` as an explicit exception.
4. Create a SpecOps reference audit artifact for the relationship mapping.
5. Update the source inventory, Control Spec and backlog next-action/evidence.

## Out Of Scope

1. No import of OpenSpec `proposal.md`, `tasks.md`, `design.md`, `implementation-evidence.md`, `acceptance-criteria-matrix.md`, `scope-contract.md` or `spec-deltas.md` as primary entities.
2. No audit of `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/openspec/`.
3. No audit of Nebenkostenabrechnung or KI legacy OpenSpec folders.
4. No dashboard UI changes.
5. No mutation of historical archived OpenSpec files.

## Acceptance Targets

1. Canonical shared-ai-docs OpenSpec spec count is exactly 11.
2. The relationship audit contains exactly 11 canonical OpenSpec rows.
3. No primary SpecOps entity is created with `source_type: openspec_change_artifact`.
4. The single legacy OpenSpec-derived entity is retained and documented as an exception.
5. The Control Spec phase 5 and source inventory reflect current shared-ai-docs OpenSpec counts: 119 markdown files total, 11 canonical specs and 108 archived change artifacts.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in the selected canonical OpenSpec specs and control artifacts.
2. Count canonical OpenSpec specs under `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/openspec/specs/`.
3. Count total shared-ai-docs OpenSpec markdown files and archived OpenSpec markdown artifacts.
4. Count canonical rows in `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/openspec-relationship-audit.md`.
5. Run the negative guard for primary entities with `source_type: openspec_change_artifact`.
6. Count retained legacy OpenSpec-derived primary entities.
7. Run `openspec validate specops-shared-openspec-canonical-relationship-audit --strict --json`.
8. Run `openspec status --change specops-shared-openspec-canonical-relationship-audit --json`.
9. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. The Control Spec's old phase 5 count of 19 is stale after the recent backfill archives; this run updates it to the current filesystem count.
2. Archived OpenSpec change artifacts remain out of scope because 108 files is an XL relationship group and should not be manually mapped in this S/M canonical audit.
3. Runtime validation is not applicable because this change only edits SpecOps metadata/reference documentation and OpenSpec delivery artifacts.
