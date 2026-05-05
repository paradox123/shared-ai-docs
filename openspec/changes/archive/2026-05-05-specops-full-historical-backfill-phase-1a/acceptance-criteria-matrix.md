# Acceptance Criteria Matrix

| Criterion | Status | Evidence |
|---|---|---|
| Five Phase 1A entity notes exist | pass | `_shared/SpecOps/Entities/specs/*` with `backfill_batch: historical-001-phase-1a` |
| All source paths exist | pass | `test -f` checks in implementation evidence |
| Duplicate guard applied | pass | no existing entity had these exact source paths before import |
| Negative OpenSpec artefact guard passes | pass | all five use narrative/completed source types |
| Dashboards can discover entities | pass | entities live under `_shared/SpecOps/Entities/specs` and include `type: spec` |
| OpenSpec change validates | pass | `openspec validate specops-full-historical-backfill-phase-1a --strict --json` |
