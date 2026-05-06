# Scope Contract

## In Scope

1. Audit the remaining KI legacy OpenSpec change groups under `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_legacy/v1-node-prototype/openspec/changes/`:
   - `integration-01-04-e2e-gate`,
   - `spec-04-artifact-pipeline-delivery`.
2. Map all 14 selected markdown files as relationship/evidence sources.
3. Link selected sources to existing Mittelstand KI Startbahn SpecOps targets:
   - `mittelstand-ki-startbahn-free-entry-onboarding-2026-04-22`,
   - `mittelstand-ki-startbahn-artifact-pipeline-roi-rag-2026-05-01`,
   - `mittelstand-ki-startbahn-free-entry-v2-s0-repo-freeze-legacy-quarantine-2026-05-05`.
4. Update the shared OpenSpec relationship audit reference with KI legacy batch 2.
5. Update the source inventory, Control Spec and backlog evidence to close KI legacy OpenSpec coverage at 35/35.

## Out Of Scope

1. No import of KI legacy OpenSpec files as new primary SpecOps spec entities.
2. No edits to `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`.
3. No shared-ai-docs archived artifact or Nebenkosten OpenSpec audit.
4. No dashboard UI changes.

## Acceptance Targets

1. Selected KI legacy OpenSpec markdown count is exactly 14.
2. The relationship audit contains exactly 14 KI legacy batch 2 rows.
3. Full KI legacy OpenSpec coverage is 35/35 across batch 1 and batch 2.
4. No primary SpecOps entity is created with `source_type: openspec_change_artifact`.
5. Marker scan shows no current blocking marker in selected sources.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in selected KI legacy sources.
2. Count selected KI legacy batch 2 markdown files.
3. Count full KI legacy markdown files and total KI legacy audit rows.
4. Count KI legacy batch 2 rows in `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/openspec-relationship-audit.md`.
5. Run the negative guard for primary entities with `source_type: openspec_change_artifact`.
6. Run `openspec validate specops-ki-legacy-openspec-relationship-audit-2 --strict --json`.
7. Run `openspec status --change specops-ki-legacy-openspec-relationship-audit-2 --json`.
8. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. KI legacy OpenSpec material belongs to the old v1 Node prototype and remains relationship/evidence only; v2 sources stay canonical for current implementation planning.
2. Runtime validation is not applicable because this change only edits SpecOps metadata/reference documentation and OpenSpec delivery artifacts.
