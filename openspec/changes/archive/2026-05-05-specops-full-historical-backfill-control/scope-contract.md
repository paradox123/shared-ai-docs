# Scope Contract

## Mode

OpenSpec mode. This change creates the control-plane OpenSpec artefacts for the remaining SpecOps Full Historical Backfill.

## In Scope

1. Create the OpenSpec change artefacts for `specops-full-historical-backfill-control`.
2. Define the capability `specops-historical-backfill-control`.
3. Use `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md` as the baseline.
4. Treat `historical-001` as already completed and not re-importable.
5. Define phased source groups, entity rules, duplicate guards and acceptance evidence for future delivery runs.
6. Update the Control Spec with status/evidence for this OpenSpec planning implementation.

## Out Of Scope

1. No new SpecOps entity imports in this change.
2. No mass migration or metadata reconstruction automation.
3. No edits to historical source specs, documents or OpenSpec archives.
4. No release, environment or skill-learning model decisions.
5. No work on the parallel `SpecOps Dashboard UX Overview` spec.
6. No NCG backend build/runtime change.

## Acceptance Targets

1. OpenSpec change contains `proposal.md`, `design.md`, `tasks.md`, `specs/specops-historical-backfill-control/spec.md`, `acceptance-criteria-matrix.md` and `implementation-evidence.md`.
2. Source groups from the inventory are represented in phases.
3. `type: spec` versus `type: document` rules are explicit.
4. `source_type: openspec_change_artifact` remains forbidden for primary spec entities.
5. Backlog item `full-historical-spec-backfill` remains linked to the accepted `historical-001` slice and the Control Spec.
6. The Control Spec verification commands all pass.

## Planned Verification

1. Run all four verification commands from the Control Spec.
2. Run OpenSpec validation for the new change.
3. Run OpenSpec status for the new change.
4. Run marker/task sanity checks.

Runtime validation and `check-build-watcher` are not applicable because this change creates planning/control artefacts only and does not touch NCG backend runtime code.
