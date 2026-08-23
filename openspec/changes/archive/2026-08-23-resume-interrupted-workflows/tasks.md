## 1. Recovery Contract and Storage

- [x] 1.1 Add public-seam failing tests for recovery status, stable operation identities, completed-transition reuse, and terminal-run non-reactivation.
- [x] 1.2 Add the additive recovery event schema and store queries for active runs and incomplete batches without persisting sensitive payloads.

## 2. Re-entrant Workflow Execution

- [x] 2.1 Make claim, implementation preparation/execution, publication, and review graph nodes reuse durable completed state and deterministic run-owned resources.
- [x] 2.2 Make review, repair, and human-feedback coordinators resume existing batches/rounds and skip already persisted invocations/results.
- [x] 2.3 Run automatic recovery from the FastAPI lifespan before accepting deliveries and expose recovery through workflow-state read-back.

## 3. Productive Crash Verification

- [x] 3.1 Add a subprocess system test that kills the serving process at controlled phase boundaries, restarts it on the same SQLite/worktree state, and proves convergence through signed POST and GET requests plus controlled boundary effect counts.
- [x] 3.2 Cover restart while waiting for human input and after terminal human merge, including absence of duplicate run, worktree, PR, review, and worker effects.

## 4. Documentation and Completion

- [x] 4.1 Update the pilot README with startup recovery behavior, correlation guarantees, observability, and data-minimization boundaries.
- [x] 4.2 Perform the required DRY/SOLID/KISS refactoring pass and rerun targeted tests, the full pilot suite, lint, lock validation, strict OpenSpec validation, and `git diff --check`.
- [x] 4.3 Record direct implementation evidence and update Issue 08 acceptance checkboxes only for behavior proven through the productive interface.
