# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 8 selected NCG infrastructure sources are imported. | Batch count over `backfill_batch: historical-001-ncg-infrastructure-final` returned `8` entities. | pass |
| AC2 | Each selected source path is represented exactly once. | Selected-source missing guard and duplicate guard returned no output. | pass |
| AC3 | NCG docs Specs coverage advances to 29/29. | NCG source count returned `29`; represented-source count returned `29`. | pass |
| AC4 | Historical marker conflicts are visible. | Sources with old missing/decision markers are marked with `metadata_quality: conflict`; one inferred metadata case is marked `metadata_quality: inferred`. | pass |
| AC5 | No OpenSpec change artifact is used as primary source type. | Negative guard for `source_type: openspec_change_artifact` returned no output. | pass |
| AC6 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
