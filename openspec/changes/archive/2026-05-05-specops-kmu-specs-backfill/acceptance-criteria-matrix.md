# Acceptance Criteria Matrix

| Criterion | Target | Evidence |
|---|---:|---|
| Source files in `ki-fuer-kmu/_specs` | 19 | `find ... | wc -l` |
| Existing pre-run KI entities | 2 | exact source-path search |
| New batch entities | 17 | `backfill_batch: historical-001-kmu` count |
| Total KI spec source entities after run | 19 | exact source-path search |
| Duplicate source paths | 0 duplicates | source duplicate guard |
| OpenSpec artifact entities | 0 | negative guard |
| OpenSpec strict validation | pass | `openspec validate specops-kmu-specs-backfill --strict --json` |
