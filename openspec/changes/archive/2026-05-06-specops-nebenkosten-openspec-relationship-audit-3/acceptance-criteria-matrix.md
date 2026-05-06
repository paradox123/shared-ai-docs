# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 25 selected Nebenkosten OpenSpec markdown files are in scope. | Selected Nebenkosten batch 3 markdown count returned `25`. | pass |
| AC2 | The relationship audit contains exactly 87 Nebenkosten rows after batch 3. | Audit-row count over Nebenkosten OpenSpec paths returned `87`. | pass |
| AC3 | Nebenkosten OpenSpec coverage is complete and measurable as 87/87 mapped. | Full Nebenkosten count returned `87`; total Nebenkosten audit-row count returned `87`. | pass |
| AC4 | No OpenSpec artifact is promoted into a primary entity. | Negative guard for `source_type: openspec_change_artifact` returned no output. | pass |
| AC5 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
