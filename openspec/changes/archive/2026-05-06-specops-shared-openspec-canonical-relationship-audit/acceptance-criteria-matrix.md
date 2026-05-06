# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly 11 canonical shared-ai-docs OpenSpec specs are in scope. | Canonical `openspec/specs/*/spec.md` count returned `11`. | pass |
| AC2 | The relationship audit contains exactly 11 canonical rows. | Audit-row count over exact canonical OpenSpec paths returned `11`. | pass |
| AC3 | OpenSpec artifacts are not promoted into new primary entities. | Negative guard for `source_type: openspec_change_artifact` returned no output; legacy OpenSpec-derived primary count remains `1`. | pass |
| AC4 | Current shared-ai-docs OpenSpec counts are represented. | Source-pool markdown count excluding this active delivery change returned `119`; canonical count `11`; archived artifact count `108`. | pass |
| AC5 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
