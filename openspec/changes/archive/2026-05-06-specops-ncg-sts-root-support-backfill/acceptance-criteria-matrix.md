# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 7 selected NCG STS root/support sources are imported. | Batch count returned `7`. | pass |
| AC2 | Batch split is 6 specs and 1 document. | Batch split returned `6` specs and `1` document. | pass |
| AC3 | Each selected source path is represented exactly once. | Selected-source missing guard returned no output; duplicate guard returned no output. | pass |
| AC4 | NCG docs Specs coverage advances to 21/29. | NCG source count returned `29`; anchored represented-source count returned `21`. | pass |
| AC5 | Deferred Topics TODO is not promoted to primary spec. | Entity is under `Entities/documents` with `type: document`. | pass |
| AC6 | No OpenSpec change artifact is used as primary source type. | Negative guard returned no output. | pass |
| AC7 | OpenSpec change is valid and tasks are complete. | `openspec validate` passed; `openspec status` returned `isComplete: true`; `openspec validate --all` passed 10/10. | pass |
