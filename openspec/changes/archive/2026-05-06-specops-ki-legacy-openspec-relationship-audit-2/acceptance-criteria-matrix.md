# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 14 selected KI legacy OpenSpec markdown files are in scope. | Selected KI legacy batch 2 markdown count returned `14`. | pass |
| AC2 | The relationship audit contains exactly 14 KI legacy batch 2 rows. | Audit-row count over exact selected KI legacy OpenSpec paths returned `14`. | pass |
| AC3 | KI legacy OpenSpec coverage is complete and measurable: 35/35 mapped. | Full KI legacy count returned `35`; total KI legacy audit-row count returned `35`. | pass |
| AC4 | No OpenSpec artifact is promoted into a primary entity. | Negative guard for `source_type: openspec_change_artifact` returned no output. | pass |
| AC5 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
