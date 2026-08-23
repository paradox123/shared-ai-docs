## 1. Change Gate and Contracts

- [x] 1.1 Strictly validate the active change before implementation and record the accepted scope, write set, and direct HTTP verification matrix.
- [x] 1.2 Add failing packaged-contract and policy tests, then implement versioned repair assignment/result schemas plus Terra/Sol repair selection with bounded implementer write access.

## 2. Durable Repair State

- [x] 2.1 Add failing persistence/read-model tests, then implement additive repair-batch, attempt, invocation, verification, review-link, finding, and terminal-projection storage with a hard three-round constraint.

## 3. Repair Boundaries

- [x] 3.1 Add failing worker-adapter contract tests, then implement the same Codex writing worker's repair operation, structured escalation, decision-boundary prompt, schema validation, redaction, and provenance.
- [x] 3.2 Add failing deterministic-verifier and updated-publication contract tests, then implement exact committed-head verification and idempotent existing-draft-PR head/body updates.

## 4. End-to-End Repair Loop

- [x] 4.1 Add a failing signed-HTTP system test for a multi-axis initial failure repaired successfully in round one, then implement finding aggregation, repair orchestration, new-head publication, deterministic verification, and full fresh review.
- [x] 4.2 Add failing signed-HTTP system tests for three unsuccessful rounds and no fourth invocation, then enforce the per-initial-batch limit and retain ordered attempts/open findings.
- [x] 4.3 Add failing signed-HTTP restart tests for exhausted `needs-info` and `ready-for-human` outcomes, then implement precise terminal label projection and restart-safe public read-back without duplicate external effects.

## 5. Documentation and Acceptance

- [x] 5.1 Update the pilot README and Issue 05 with the implemented repair policy, state surface, limits, escalation rules, and criterion-level evidence references.
- [x] 5.2 Refactor the touched code/spec context for DRY, SOLID, and KISS without changing behavior, then rerun focused/full pytest, Ruff, lock check, `git diff --check`, and strict OpenSpec validation.
