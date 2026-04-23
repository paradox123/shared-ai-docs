# Scope Contract

## Change
- Id: `rag-source-precision-gate-harmonization`
- Mode: `openspec`
- Target Finding: Parent-vs-Child metric contract ambiguity around `source_precision`

## In Scope
1. Harmonize wording between parent spec `2026-04-13 DanielsVault Local RAG Wissensplattform.md` and child spec `2026-04-21 04 DanielsVault RAG Evaluation und Qualitaetsgates.md`.
2. Keep `source_precision` explicitly non-blocking for Phase 1 unless child gates are changed in the future.
3. Provide OpenSpec proposal/design/specs/tasks + acceptance/evidence artifacts.
4. Execute verification commands for this bounded spec change and capture command statuses.
5. Capture check-build-watcher evidence.

## Out of Scope
1. RAG runtime/CLI implementation or deployment.
2. Execution of full RAG end-to-end runtime verification from child specs 01..05.
3. Broader refactors in unrelated specs/docs.

## Acceptance Targets
1. Parent and child metric semantics are non-contradictory.
2. Parent states child checklist authority unambiguously.
3. `source_precision` appears only as optional monitoring in this Phase-1 contract.
4. OpenSpec tasks complete with no fake-done blockers.

## Planned Verification
1. Marker check for blocking markers in affected specs.
2. grep/assertion checks for:
   - parent authoritative gate reference to child 01..05,
   - parent optional `source_precision` wording,
   - child-04 blocking metric list unchanged.
3. OpenSpec validation command for this change.
4. check-build-watcher show-state command.
