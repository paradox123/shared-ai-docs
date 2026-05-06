# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 21 selected KI legacy OpenSpec markdown files are in scope. | Selected KI legacy markdown count returned `21`. | pass |
| AC2 | The relationship audit contains exactly 21 KI legacy batch 1 rows. | Audit-row count over exact selected KI legacy OpenSpec paths returned `21`. | pass |
| AC3 | KI legacy OpenSpec coverage is partial and measurable: 21 mapped, 14 remaining. | Full/selected/remaining count checks returned `35`, `21`, and `14`. | pass |
| AC4 | No OpenSpec artifact is promoted into a primary entity. | Negative guard for `source_type: openspec_change_artifact` returned no output. | pass |
| AC5 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
