# Scope Contract

## Batch Size Decision

The full KI legacy OpenSpec pool has 35 markdown files and is therefore XL under the current Auto-Resolve Scale. This run selects the first three cohesive legacy change groups, 21 files total, which is Scale L and remains bounded.

## In Scope

1. Audit these KI legacy OpenSpec change groups under `/Users/dh/Documents/DanielsVault/ki-fuer-kmu/_legacy/v1-node-prototype/openspec/changes/`:
   - `bootstrap-kickstart-foundation`,
   - `spec-01-runner-hardening`,
   - `spec-02-03-parallel-delivery`.
2. Map all 21 selected markdown files as relationship/evidence sources.
3. Link selected sources to existing Mittelstand KI Startbahn SpecOps targets:
   - `mittelstand-ki-startbahn-free-entry-onboarding-2026-04-22`,
   - `mittelstand-ki-startbahn-onboarding-runner-core-2026-05-01`,
   - `mittelstand-ki-startbahn-entry-services-browser-register-2026-05-01`,
   - `mittelstand-ki-startbahn-discovery-compliance-survey-2026-05-01`,
   - `mittelstand-ki-startbahn-free-entry-v2-s0-repo-freeze-legacy-quarantine-2026-05-05`.
4. Update the shared OpenSpec relationship audit reference with KI legacy batch 1.
5. Update the source inventory, Control Spec and backlog evidence.

## Out Of Scope

1. No import of KI legacy OpenSpec files as new primary SpecOps spec entities.
2. No edits to `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`.
3. No audit of `integration-01-04-e2e-gate` or `spec-04-artifact-pipeline-delivery` in this run.
4. No shared-ai-docs archived artifact or Nebenkosten OpenSpec audit.
5. No dashboard UI changes.

## Acceptance Targets

1. Selected KI legacy OpenSpec markdown count is exactly 21.
2. The relationship audit contains exactly 21 KI legacy batch 1 rows.
3. Full KI legacy OpenSpec pool remains visible as 35 total, with 21 mapped and 14 remaining.
4. No primary SpecOps entity is created with `source_type: openspec_change_artifact`.
5. Marker scan shows no current blocking marker in selected sources.
6. OpenSpec validation and status checks for this change pass.

## Planned Verification

1. Marker scan for `[MISSING]`, `[DECISION]` and `[BLOCKED]` in selected KI legacy sources.
2. Count selected KI legacy markdown files.
3. Count full KI legacy markdown files and remaining unselected markdown files.
4. Count KI legacy batch 1 rows in `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/openspec-relationship-audit.md`.
5. Run the negative guard for primary entities with `source_type: openspec_change_artifact`.
6. Run `openspec validate specops-ki-legacy-openspec-relationship-audit-1 --strict --json`.
7. Run `openspec status --change specops-ki-legacy-openspec-relationship-audit-1 --json`.
8. Run `openspec validate --all --strict --json`.

## Open Risks And Assumptions

1. KI legacy OpenSpec material belongs to the old v1 Node prototype and remains relationship/evidence only; v2 sources stay canonical for current implementation planning.
2. Runtime validation is not applicable because this change only edits SpecOps metadata/reference documentation and OpenSpec delivery artifacts.
3. The remaining 14 KI legacy OpenSpec files should be handled as a second bounded batch.
