## 1. Contracts and Evidence Qualification

- [x] 1.1 Add a versioned structured worker-evidence contract and package loader coverage for all supported observation kinds.
- [x] 1.2 Add failing evidence-gate tests for exact criterion coverage, type-specific direct observations, infrastructure surrogates, redaction, and body rendering; implement the minimum qualifier/redactor/renderer to pass.

## 2. Source and GitHub Publication Boundaries

- [x] 2.1 Add failing source-control adapter contract tests for safe commit/head/push, already-committed work, and sensitive-diff rejection; implement the Git adapter.
- [x] 2.2 Add failing GitHub adapter contract tests for draft creation and existing-head-branch reuse; implement idempotent draft-pull-request projection.

## 3. Persistent Workflow Slices

- [x] 3.1 Add a failing signed-delivery HTTP behavior test for sufficient Evidence, then persist and expose one commit-bound draft pull request through the productive workflow seam.
- [x] 3.2 Add failing signed-delivery HTTP behavior tests for deliberately insufficient Evidence and duplicate delivery, then persist safe rejection without source or PR effects.
- [x] 3.3 Add a failing restart behavior test, then expose the same publication identity, body, head, evidence, and timestamps after application reconstruction without another external write.

## 4. Refactoring, Documentation, and Direct Evidence

- [x] 4.1 Refactor touched contracts, workflow code, adapters, storage, and tests for DRY, SOLID, and KISS issues while preserving behavior.
- [x] 4.2 Update pilot runtime/configuration documentation and the canonical capability specification.
- [x] 4.3 Run focused and full behavior/adapter suites, lint and lock checks, `git diff --check`, and strict OpenSpec validation.
- [x] 4.4 Record criterion-level implementation evidence and update Issue 03 only for criteria directly proven through public or external-boundary behavior.
