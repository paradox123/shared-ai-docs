## MODIFIED Requirements

### Requirement: Isolate each implementation run in its own worktree
Before creating a new run worktree, the workflow MUST fetch the configured base branch from the repository's publication remote, resolve the fetched ref to an immutable commit SHA, and create the run branch from that SHA. It MUST durably retain that immutable base for later diff, publication, and recovery operations. It MUST create a distinct Git worktree and branch owned by the persistent run before starting implementation, pass that worktree as the worker's only writable repository root, and MUST NOT use Daniel's checkout or another run's worktree as the implementation directory. Recovery MUST adopt an existing valid run worktree with its original base SHA and MUST NOT move it to a newer base.

#### Scenario: Local base branch is stale
- **WHEN** a newly selected sequential issue starts while local `main` lags the fetched `origin/main`
- **THEN** its run branch and worktree start at the fetched remote commit SHA and the durable implementation record retains that SHA as its fixed base

#### Scenario: Existing worktree is adopted after interruption
- **WHEN** recovery encounters the deterministic worktree and branch for the same run after the remote base has advanced
- **THEN** it adopts the existing worktree with its original immutable base and does not fetch, rebase, or replace it

### Requirement: Validate and persist observable Red-Green results
Feature and bug workers MUST return a versioned structured result. A completed result MUST contain at least one observable Red-Green slice; a schema-valid blocked or intervention result MAY report incomplete slices as allowed by its packaged schema. The final schema-constrained result channel MUST be parsed and validated independently from JSONL diagnostics. Malformed diagnostic lines MUST NOT invalidate an otherwise schema-valid final result. The workflow MUST permanently associate the assignment, worktree, policy selection, skill provenance, rights profile, result or bounded failure, retained redacted diagnostics, and timestamps with the persistent run.

#### Scenario: Valid blocked result accompanies malformed diagnostics
- **WHEN** the worker exits successfully, writes a schema-valid `blocked` final result, and emits one malformed JSONL diagnostic line beside valid completion events
- **THEN** the workflow retains and exposes the blocked result, records a bounded diagnostic-parse event, and does not replace the result with `InvalidWorkerResult`

#### Scenario: Final result is genuinely missing or invalid
- **WHEN** the worker result file is missing, invalid JSON, or schema-invalid
- **THEN** the workflow persists a stable bounded failure code plus safely parsed redacted diagnostic events and does not expose raw malformed output or arbitrary process text
