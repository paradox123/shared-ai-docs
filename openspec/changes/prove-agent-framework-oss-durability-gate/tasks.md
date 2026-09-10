## 1. Contract and isolated workspace

- [x] 1.1 Create the gate-only workspace, versioned manifest schema, fixture manifests, and protected-boundary inventory without creating the later Microsoft pilot directory.
- [x] 1.2 Add public CLI tests that first fail for manifest drift, forbidden backends, missing licence/cost data, and attempted workflow startup after ineligibility.

## 2. Fail-closed gate implementation

- [x] 2.1 Implement manifest and observed-provenance validation through the public CLI, including immutable versions, lock/source/runtime/config/contract correlation, and forbidden dependency checks.
- [x] 2.2 Add isolated before/after fingerprinting and correlated JSON/Markdown decision evidence with nonzero no-go exit semantics.

## 3. Backend and dependency proof

- [x] 3.1 Resolve and record the exact Agent Framework/Durable Task dependency graph, source revisions, licences, protocol compatibility, storage dependencies, and unavoidable service costs from primary sources and restored packages.
- [x] 3.2 Run the gate against the audited production-backend candidate; if eligibility fails, prove that no workflow/worker started and record the Microsoft candidate no-go.
- [x] 3.3 If and only if backend eligibility passes, compile and run the real two-worker replacement probe and verify one orchestration identity with exactly-once observable effects. (Not run: backend eligibility failed; prohibited probe path verified.)

## 4. Evidence and completion

- [x] 4.1 Verify protected LangGraph, Cloudflare, macOS/runtime/worktree, and ProBara boundaries are unchanged and retain scoped before/after evidence.
- [x] 4.2 Update the issue outcome and dependency stop/go state, run focused/full tests, type/build checks, `git diff --check`, and strict OpenSpec validation.
- [x] 4.3 Refactor the touched gate/spec surface for DRY, SOLID, and KISS issues, rerun checks, and complete the two-axis code review.
