# isolated-issue-worker Specification

## Purpose

Define how claimed GitHub issues are implemented by a policy-controlled Codex worker in an isolated Git worktree with durable, observable Red-Green evidence.
## Requirements
### Requirement: Prepare a bounded implementation assignment and evidence plan
The workflow MUST create and persist a versioned implementation assignment before worker execution. The assignment MUST contain only the claimed issue, its acceptance requirements, configured repository context, a criterion-by-criterion evidence matrix, and current findings. Each evidence entry MUST identify a public observation surface, expected result, and planned proof.

#### Scenario: Claimed feature is prepared
- **WHEN** an eligible claimed feature contains acceptance criteria
- **THEN** the persisted assignment contains every criterion and a matching evidence entry before the worker is invoked, without unrelated webhook, session, secret, or repository content

### Requirement: Isolate each implementation run in its own worktree
Before creating a new run worktree, the workflow MUST fetch the configured base branch from the repository's publication remote, resolve the fetched ref to an immutable commit SHA, and create the run branch from that SHA. It MUST durably retain that immutable base for later diff, publication, and recovery operations. It MUST create a distinct Git worktree and branch owned by the persistent run before starting implementation, pass that worktree as the worker's only writable repository root, and MUST NOT use Daniel's checkout or another run's worktree as the implementation directory. Recovery MUST adopt an existing valid run worktree with its original base SHA and MUST NOT move it to a newer base.

#### Scenario: Local base branch is stale
- **WHEN** a newly selected sequential issue starts while local `main` lags the fetched `origin/main`
- **THEN** its run branch and worktree start at the fetched remote commit SHA and the durable implementation record retains that SHA as its fixed base

#### Scenario: Existing worktree is adopted after interruption
- **WHEN** recovery encounters the deterministic worktree and branch for the same run after the remote base has advanced
- **THEN** it adopts the existing worktree with its original immutable base and does not fetch, rebase, or replace it

### Requirement: Enforce versioned model and rights policy
The workflow MUST select model, reasoning effort, and filesystem rights from a versioned policy. Deterministic control-plane work MUST use no model; presentation-only work MUST use `gpt-5.6-luna` with `medium`; triage, slicing, implementation, findings repair, and regular reviews MUST use `gpt-5.6-terra` with `xhigh`; defined difficult escalations alone MUST use `gpt-5.6-sol` with `xhigh`. Only implementer and findings-repair roles MUST receive `workspace-write`; other agent roles MUST be read-only.

#### Scenario: Regular implementation policy is selected
- **WHEN** the workflow prepares an implementation node
- **THEN** it selects `gpt-5.6-terra`, `xhigh`, and `workspace-write` scoped to the run worktree

#### Scenario: Unsupported combination is requested
- **WHEN** a caller requests a model, reasoning effort, or rights profile that differs from the versioned node policy
- **THEN** the workflow rejects the request before creating a worktree or launching a worker

#### Scenario: Defined escalation is selected
- **WHEN** a documented architecture, persistence, security, data-migration, explicit-escalate, or final-repair-round condition selects escalation
- **THEN** the workflow permits `gpt-5.6-sol` with `xhigh`; any other Sol selection is rejected

### Requirement: Route task-specific skills with provenance
The workflow MUST route Matt-Pocock skills by task: triage to `triage`, large-requirement slicing to `to-tickets`, feature implementation to `implement` and `tdd`, and bug implementation to `diagnosing-bugs` and `tdd`. Every worker invocation MUST record the routed skill names and their versions or content hashes.

#### Scenario: Feature and bug skills are routed
- **WHEN** feature and bug assignments are prepared
- **THEN** the feature receives `implement` and `tdd`, the bug receives `diagnosing-bugs` and `tdd`, and every selected skill has recorded provenance

### Requirement: Execute through a replaceable non-interactive worker adapter
The implementer MUST run behind a replaceable worker port. The production Codex adapter MUST use non-interactive `codex exec` in the assigned worktree with the selected model, reasoning effort, skill contract, output schema, and access profile, without depending on an experimental Codex server interface.

#### Scenario: Codex implementation is invoked
- **WHEN** a valid feature assignment and isolated worktree are ready
- **THEN** the adapter invokes Codex non-interactively with Terra/`xhigh`, feature skills, `workspace-write`, JSONL diagnostics, and the versioned result schema

### Requirement: Validate and persist observable Red-Green results
Feature and bug workers MUST return a versioned structured result. A completed result MUST contain at least one observable Red-Green slice; a schema-valid blocked or intervention result MAY report incomplete slices as allowed by its packaged schema. The final schema-constrained result channel MUST be parsed and validated independently from JSONL diagnostics. Malformed diagnostic lines MUST NOT invalidate an otherwise schema-valid final result. The workflow MUST permanently associate the assignment, worktree, policy selection, skill provenance, rights profile, result or bounded failure, retained redacted diagnostics, and timestamps with the persistent run.

#### Scenario: Valid blocked result accompanies malformed diagnostics
- **WHEN** the worker exits successfully, writes a schema-valid `blocked` final result, and emits one malformed JSONL diagnostic line beside valid completion events
- **THEN** the workflow retains and exposes the blocked result, records a bounded diagnostic-parse event, and does not replace the result with `InvalidWorkerResult`

#### Scenario: Final result is genuinely missing or invalid
- **WHEN** the worker result file is missing, invalid JSON, or schema-invalid
- **THEN** the workflow persists a stable bounded failure code plus safely parsed redacted diagnostic events and does not expose raw malformed output or arbitrary process text

### Requirement: Contain worker failures to the assigned run
Only the implementer MUST have write access to the run worktree. A failed or invalid worker result MUST NOT change Daniel's checkout, another run's worktree, or an existing pull request, and duplicate delivery MUST NOT create another worktree or worker invocation.

#### Scenario: Invalid worker output is isolated
- **WHEN** an implementer modifies its worktree but returns an invalid result
- **THEN** the run records failure while Daniel's checkout, sibling worktrees, and existing pull requests have no worker-result-driven change

#### Scenario: Delivery is repeated
- **WHEN** the accepted GitHub delivery is submitted again after worker execution
- **THEN** the existing run, worktree, assignment, and worker execution remain the only ones for the issue

### Requirement: Initial implementation can request policy-authorized intervention
The initial implementation result contract MUST support one schema-valid intervention for contradictory or incomplete product requirements, material scope expansion, missing access to a human-operable surface, or unavoidable manual evidence. The implementer MUST continue autonomously for small reversible implementation and presentation details and MUST NOT synthesize a product decision or continue indefinitely after returning an intervention.

#### Scenario: Initial implementation needs a product decision
- **WHEN** the writing worker cannot choose between materially different product behaviors from the existing assignment
- **THEN** it returns a complete structured intervention and the run pauses before publication or further worker activity

#### Scenario: Initial implementation faces a reversible detail
- **WHEN** only a small reversible implementation or presentation choice is unspecified
- **THEN** the worker chooses within repository guidance and continues without an intervention
