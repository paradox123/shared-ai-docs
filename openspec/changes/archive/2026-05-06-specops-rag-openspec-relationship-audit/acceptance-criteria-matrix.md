# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 17 RAG OpenSpec markdown files are in scope. | RAG OpenSpec markdown count returned `17`. | pass |
| AC2 | The relationship audit contains exactly 17 RAG OpenSpec rows. | Audit-row count over exact RAG OpenSpec paths returned `17`. | pass |
| AC3 | No OpenSpec artifact is promoted into a primary entity. | Negative guard for `source_type: openspec_change_artifact` returned no output. | pass |
| AC4 | Historical RAG blocked evidence remains visible as context. | Marker scan found old `[BLOCKED]` evidence in the 2026-04-22 hardening archive; audit row notes mark it as historical conflict context. | pass |
| AC5 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
