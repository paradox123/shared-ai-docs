# Acceptance Criteria Matrix

| Criterion | Target | Evidence |
|---|---:|---|
| Completed source files | 32 | `find Completed ... | wc -l` |
| Selected source files | 14 | selected source query |
| Existing pre-run selected source entities | 1 | exact source-path search |
| New batch entities | 13 | `backfill_batch: historical-001-completed-1b` count |
| Total selected source entities after run | 14 | exact source-path search |
| Completed coverage after run | 24/32 | exact Completed source-path count |
| Missing selected source paths | 0 | source/entity `comm -23` guard |
| Extra selected source paths | 0 | source/entity `comm -13` guard |
| Duplicate selected source paths | 0 duplicates | source duplicate guard |
| OpenSpec artifact entities | 0 | negative guard |
| OpenSpec strict validation | pass | `openspec validate specops-completed-nebenkosten-2025-backfill --strict --json` |
