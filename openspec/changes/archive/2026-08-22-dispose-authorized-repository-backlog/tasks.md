## 1. Change Gate and Adapter Boundary

- [x] 1.1 Strictly validate the complete active OpenSpec change before runtime implementation.
- [x] 1.2 Add a failing shared HTTP behavior contract for `probare-crm` and a minimal second adapter, then implement the versioned repository adapter registry, adapter-owned event allowlist, labels, and projections without repository branches in the core.

## 2. Vertical Scheduling Slices

- [x] 2.1 Add failing behavior cases for ready issues of every type plus proven direct, PRD, and parent-chain self-authorization, then minimally implement canonical provenance and inherited-scope decisions.
- [x] 2.2 Add failing behavior cases for invalid provenance and material scope expansion, then persist directly observable interrupted dispositions without a run or running projection.
- [x] 2.3 Add failing behavior cases for each incomplete blocker state and the fully completed blocker state, then implement durable blocked dispositions using both human merge and issue closure.
- [x] 2.4 Add a failing simultaneous-candidate behavior case, then implement repository-wide deterministic issue-number frontier evaluation, durable queued dispositions, and one active run without lost deliveries or stacked work.
- [x] 2.5 Add a failing active-completion behavior case, then reconcile a run only after human merge plus issue closure and select the next candidate in the same scheduling pass.
- [x] 2.6 Add a failing restart behavior case for queued and interrupted candidates, then expose their durable delivery correlation, dispositions, reasons, runs, projections, and checkpoints through the productive read model.

## 3. Production Binding and Closeout

- [x] 3.1 Bind the production entry point to the single `probare-crm` adapter configuration and document its repository-neutral contract and runtime configuration without activating a second live repository.
- [x] 3.2 Refactor the touched runtime, tests, and specs for DRY, SOLID, and KISS issues while preserving behavior, then rerun the behavior suite.
- [x] 3.3 Run direct signed-HTTP evidence scenarios, the complete locked test suite, dependency audit, `git diff --check`, and strict OpenSpec validation; record implementation evidence and update local issue 07.
