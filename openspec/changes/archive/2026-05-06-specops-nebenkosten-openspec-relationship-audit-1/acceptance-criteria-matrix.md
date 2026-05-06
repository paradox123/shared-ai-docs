# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 32 selected Nebenkosten OpenSpec markdown files are in scope. | Selected Nebenkosten batch 1 markdown count returned `32`. | pass |
| AC2 | The relationship audit contains exactly 32 Nebenkosten batch 1 rows. | Audit-row count over exact selected Nebenkosten OpenSpec paths returned `32`. | pass |
| AC3 | Nebenkosten OpenSpec coverage is measurable as 32/87 mapped. | Full Nebenkosten count returned `87`; total Nebenkosten audit-row count returned `32`. | pass |
| AC4 | No OpenSpec artifact is promoted into a primary entity. | Negative guard for `source_type: openspec_change_artifact` returned no output. | pass |
| AC5 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
