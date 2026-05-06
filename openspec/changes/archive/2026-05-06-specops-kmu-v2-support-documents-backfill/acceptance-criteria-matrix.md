# Acceptance Criteria Matrix

| ID | Acceptance Criterion | Evidence | Status |
|---|---|---|---|
| AC1 | Exactly three new KI-fuer-KMU v2 support document entities exist. | Entity-file verification returned `3`. | pass |
| AC2 | KI-fuer-KMU v2 docs coverage is 6/6. | Full v2 docs count returned `6`; document entity source coverage returned `6`. | pass |
| AC3 | Shared-ai-docs archived OpenSpec artifacts are excluded from remaining backfill scope. | Inventory, Control Spec and backlog all record the explicit exclusion. | pass |
| AC4 | Formal marker scan has no current blocking marker in selected source docs. | The only marker hit is a Slice Plan rule requiring shifted scope to stay visible as `[PENDING]` or `[BLOCKED]`; no current blocker exists. | pass |
| AC5 | OpenSpec change is valid and tasks are complete. | `openspec validate`, `openspec status`, and `openspec validate --all` passed; status reported `isComplete: true`. | pass |
