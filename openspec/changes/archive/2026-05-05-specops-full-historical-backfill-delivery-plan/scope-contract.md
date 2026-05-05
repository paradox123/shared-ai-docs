# Scope Contract

## Mode

OpenSpec mode. This change implements the active delivery-control plan for the remaining SpecOps Full Historical Backfill.

## In Scope

1. Create one active OpenSpec change named `specops-full-historical-backfill-delivery-plan`.
2. Use `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/spec-source-inventory.md` as the current baseline.
3. Represent current source counts and phase boundaries from the Control Spec.
4. Define source-to-entity rules for `type: spec`, `type: document`, OpenSpec relationships and metadata quality.
5. Define bounded delivery by Scope Contract, including the first proposed Scale-S run.
6. Define verification and evidence expectations for future delivery runs.
7. Update the Control Spec status and evidence for this OpenSpec implementation.

## Out Of Scope

1. No SpecOps entity imports in this change.
2. No automatic mass migration or metadata reconstruction.
3. No edits to historical source specs, documents or OpenSpec archives.
4. No NCG backend runtime/build code changes.
5. No work on the parallel SpecOps Dashboard UX Overview.
6. No release, environment, skill-learning or agent-learning model decisions.

## Acceptance Targets

1. OpenSpec change contains proposal, design, tasks, spec delta, acceptance matrix and implementation evidence.
2. The source inventory and Control Spec agree on the current baseline counts:
   - shared-ai-docs `_specs`: 45 total, 32 Completed, 13 active root files at closeout recount time.
   - `ki-fuer-kmu/_specs`: 19.
   - NCG `docs/Specs`: 29.
   - shared-ai-docs OpenSpec: 19.
3. `historical-001` remains the accepted baseline and is not re-imported.
4. OpenSpec change artefacts remain forbidden as primary `type: spec` entities by default.
5. Future delivery runs must start from an exact Scope Contract with concrete source files or source queries.
6. The first proposed delivery run is Phase 1A with exactly five completed shared-ai-docs source files.

## Planned Verification

Run all verification commands from the Control Spec:

1. `test -f "_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Backfill Control Spec.md"`
2. `rg -n 'spec-source-inventory|historical-001|OpenSpec|full-historical-spec-backfill' "_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Backfill Control Spec.md"`
3. `rg -n 'type: spec|type: document|openspec_change_artifact|metadata_quality' "_shared/shared-ai-docs/_specs/2026-05-05 SpecOps Full Historical Backfill Control Spec.md"`
4. `rg -n 'control_spec: .+2026-05-05 SpecOps Full Historical Backfill Control Spec.md|promoted_to: .+2026-05-05 SpecOps Full Historical Spec Backfill.md' _shared/SpecOps/Entities/backlog/full-historical-spec-backfill.md`
5. `find "_shared/shared-ai-docs/_specs/Completed" -type f -name "*.md" | wc -l`
6. `find "_shared/shared-ai-docs/_specs" -maxdepth 1 -type f -name "*.md" | wc -l`
7. `find "ki-fuer-kmu/_specs" -type f -name "*.md" | wc -l`
8. `find "ncg/ncg-docs/docs/Specs" -type f -name "*.md" | wc -l`
9. `find "_shared/shared-ai-docs/openspec" -path "_shared/shared-ai-docs/openspec/changes/specops-full-historical-backfill-delivery-plan" -prune -o -type f -name "*.md" -print | wc -l`

Additional OpenSpec verification:

1. `openspec validate specops-full-historical-backfill-delivery-plan --strict --json`
2. `openspec validate --all --strict --json`
3. Marker sanity check for open missing, decision and blocked markers.
4. Task sanity check for open checkbox tasks and blocked-as-done patterns.

Runtime validation:

This change is documentation/control-plane only. No runnable NCG backend path is modified. `check-build-watcher` status may be inspected as requested, but NCG pipeline health is not functional evidence for this SpecOps control-plane change.
