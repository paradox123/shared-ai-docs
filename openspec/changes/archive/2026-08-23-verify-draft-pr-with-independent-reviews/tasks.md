## 1. Review Contracts and Routing

- [x] 1.1 Add versioned review-assignment and verdict schemas with loader coverage for all axes, valid verdicts, concrete findings, head binding, and forbidden requirements `not_applicable`.
- [x] 1.2 Add failing policy/routing contract tests for Terra/`xhigh`/read-only review roles, separated `code-review` axes, architecture skills, and retained content hashes; implement the minimum declarative routing to pass.

## 2. Independent Read-only Worker Boundary

- [x] 2.1 Add a failing reviewer-adapter contract that proves three fresh invocations use one head, isolated inputs, the prescribed schemas/skills, and a read-only sandbox; implement the review worker port and production Codex adapter behavior.
- [x] 2.2 Add failing adapter cases for invalid output, wrong axis/head/policy/routing, worker failure, and prohibited requirements `not_applicable`; fail closed without source, repair, merge, or deploy effects.

## 3. Persistent Review and GitHub Projection

- [x] 3.1 Add failing persistence/read-model behavior for one review batch per run/head and one result per axis; implement additive durable records and restart-safe HTTP serialization.
- [x] 3.2 Add failing repository-adapter contracts for current-head read-back and convergent success labels; implement projection that adds `verified`/`awaiting-review` and removes `agent-running` only for the reviewed current head.

## 4. Primary Workflow Slices

- [x] 4.1 Add a failing signed-delivery system test with one failed axis, then execute and expose three separate reviews with fail-closed aggregation and no success-label projection.
- [x] 4.2 Add a failing signed-delivery system test where every applicable axis passes, then project and expose the exact verified head and successful labels through the productive workflow seam.
- [x] 4.3 Add failing head-mismatch and restart cases, then block stale projection and reuse the durable completed batch without another reviewer or GitHub write.

## 5. Refactoring, Documentation, and Direct Evidence

- [x] 5.1 Refactor touched contracts, policy, workflow, adapters, persistence, and tests for DRY, SOLID, and KISS issues while preserving behavior.
- [x] 5.2 Update pilot runtime/configuration documentation and the canonical capability specification.
- [x] 5.3 Run focused and full behavior/adapter suites, lint and lock checks, `git diff --check`, and strict OpenSpec validation.
- [x] 5.4 Record criterion-level implementation evidence and update Issue 04 only for criteria directly proven through public or external-boundary behavior.
