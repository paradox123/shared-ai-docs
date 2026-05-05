## Context

SpecOps already has an accepted `historical-001` slice, a current source inventory and a Control Spec for the remaining full historical backfill. The project layout changed after Mittelstand KI Startbahn moved into `/Users/dh/Documents/DanielsVault/ki-fuer-kmu`, so the delivery-control plan must use the refreshed inventory counts.

## Goals / Non-Goals

Goals:

1. Establish a current active OpenSpec delivery-control plan.
2. Keep the source inventory as the baseline for future runs.
3. Require exact Scope Contracts for every delivery run.
4. Keep narrative specs, document entities and OpenSpec evidence distinct.
5. Prevent duplicate primary entities for `historical-001` and OpenSpec change artefacts.

Non-goals:

1. No direct entity creation in this change.
2. No metadata reconstruction automation.
3. No historical source file edits.
4. No NCG backend runtime validation beyond watcher availability/status evidence.

## Decisions

1. **Active change replaces archived false start**
   - Decision: Use `specops-full-historical-backfill-delivery-plan` as the active implementation frame.
   - Rationale: The previous archived change is explicitly not a valid implementation basis.

2. **Inventory count baseline**
   - Decision: Current closeout counts are 45 shared specs, 19 `ki-fuer-kmu` specs, 29 NCG specs, 17 RAG OpenSpec files, 87 Nebenkosten OpenSpec files, 35 `ki-fuer-kmu` legacy OpenSpec files and 3 `ki-fuer-kmu` ADRs.
   - Rationale: Future runs need deterministic coverage accounting.

3. **Scope Contract before entity edits**
   - Decision: Every delivery run must name exact source files or a reproducible source query before editing SpecOps entities.
   - Rationale: This avoids drift and prevents accidental broad imports.

4. **First run scale**
   - Decision: The first recommended execution run is Phase 1A, a Scale-S run over five completed shared-ai-docs specs.
   - Rationale: It exercises classification and duplicate guards at low blast radius.

## Source Baseline

| Source group | Count | Treatment |
|---|---:|---|
| shared-ai-docs `_specs` all markdown | 45 | split into Completed and active root phases |
| shared-ai-docs `_specs/Completed` | 32 | primary `type: spec` or `type: document` by classification |
| shared-ai-docs active root specs | 13 | primary `type: spec` candidates |
| `ki-fuer-kmu/_specs` | 19 | primary `type: spec` candidates |
| NCG `docs/Specs` | 29 | primary `type: spec` candidates |
| shared-ai-docs OpenSpec | 19 | relationship/evidence unless explicitly promoted later |
| DanielsVault RAG OpenSpec | 17 | relationship/evidence |
| Nebenkosten OpenSpec | 87 | relationship/evidence after narrative dedupe |
| `ki-fuer-kmu` legacy OpenSpec | 35 | legacy relationship/evidence |
| `ki-fuer-kmu/v2/docs/adr` | 3 | already imported document entities |

## Risks / Trade-offs

- [Risk] Future broad runs import too much at once. Mitigation: run-scale rules cap manual imports and require exact Scope Contracts.
- [Risk] OpenSpec artefacts duplicate narrative user specs. Mitigation: negative guard forbids `openspec_change_artifact` as primary spec entity by default.
- [Risk] Metadata appears more certain than source evidence allows. Mitigation: keep `metadata_quality` explicit/inferred/missing/conflict visible.

## Runtime Notes

This change has no runnable application component. Runtime validation is not applicable beyond confirming that no NCG backend runtime path is changed. The check-build watcher can be inspected as requested, but it is pipeline-health evidence only.
