# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 8 final Completed sources are imported as entity notes. | Batch count returned `8`. | pass |
| AC2 | The entity split is 5 specs and 3 documents. | Batch split returned `5` specs and `3` documents. | pass |
| AC3 | Completed source coverage reaches 32/32. | Completed source count returned `32`; represented-source count returned `32`. | pass |
| AC4 | No duplicate Completed source paths exist across spec/document entities. | Duplicate guard returned no output. | pass |
| AC5 | Support/history files are not promoted to primary spec entities. | Support files are under `Entities/documents` with `type: document`. | pass |
| AC6 | No OpenSpec change artifact is used as a primary entity source type. | Negative guard returned no output. | pass |
| AC7 | OpenSpec change is valid and tasks are complete. | `openspec validate` passed; `openspec status` returned `isComplete: true`; `openspec validate --all` passed 7/7. | pass |
