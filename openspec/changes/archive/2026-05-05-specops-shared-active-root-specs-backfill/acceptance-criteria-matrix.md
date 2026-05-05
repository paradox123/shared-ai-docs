# Acceptance Criteria Matrix

| Criterion | Target | Evidence |
|---|---:|---|
| Root source files | 13 | `find ... -maxdepth 1 ... | wc -l` |
| Existing pre-run root source entities | 1 | exact source-path search |
| New batch entities | 12 | `backfill_batch: historical-001-shared-active-root` count |
| Total root source entities after run | 13 | exact source-path search |
| Missing source paths | 0 | source/entity `comm -23` guard |
| Extra source paths | 0 | source/entity `comm -13` guard |
| Duplicate source paths | 0 duplicates | source duplicate guard |
| OpenSpec artifact entities | 0 | negative guard |
| OpenSpec strict validation | pass | `openspec validate specops-shared-active-root-specs-backfill --strict --json` |
