## ADDED Requirements

### Requirement: Prepare a bounded implementation assignment and evidence plan
The workflow MUST create and persist a versioned implementation assignment before worker execution. The assignment MUST contain only the claimed issue, its acceptance requirements, configured repository context, a criterion-by-criterion evidence matrix, and current findings. Each evidence entry MUST identify a public observation surface, expected result, and planned proof.

#### Scenario: Claimed feature is prepared
- **WHEN** an eligible claimed feature contains acceptance criteria
- **THEN** the persisted assignment contains every criterion and a matching evidence entry before the worker is invoked, without unrelated webhook, session, secret, or repository content

### Requirement: Isolate each implementation run in its own worktree
The workflow MUST create a distinct Git worktree and branch owned by the persistent run before starting implementation. It MUST pass that worktree as the worker's only writable repository root and MUST NOT use Daniel's checkout or another run's worktree as the implementation directory.

#### Scenario: Implementer receives an isolated worktree
- **WHEN** a claimed issue starts implementation
- **THEN** the worker invocation uses a new run-owned worktree and Daniel's checkout and sibling worktrees remain unchanged

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
Feature and bug workers MUST return a versioned structured result containing at least one observable Red-Green slice. The workflow MUST validate the result against its packaged schema and MUST permanently associate the assignment, worktree, policy selection, skill provenance, rights profile, result or failure, and timestamps with the persistent run.

#### Scenario: Valid feature result completes
- **WHEN** a feature worker returns a schema-valid result with an observed failing test followed by its passing result
- **THEN** the workflow persists the validated result on the run and exposes it through the workflow read model

#### Scenario: Invalid result fails closed
- **WHEN** the worker exits unsuccessfully or returns output that is missing, invalid JSON, schema-invalid, or lacks a required Red-Green slice
- **THEN** the workflow persists a failed worker execution and does not treat the implementation as completed

### Requirement: Contain worker failures to the assigned run
Only the implementer MUST have write access to the run worktree. A failed or invalid worker result MUST NOT change Daniel's checkout, another run's worktree, or an existing pull request, and duplicate delivery MUST NOT create another worktree or worker invocation.

#### Scenario: Invalid worker output is isolated
- **WHEN** an implementer modifies its worktree but returns an invalid result
- **THEN** the run records failure while Daniel's checkout, sibling worktrees, and existing pull requests have no worker-result-driven change

#### Scenario: Delivery is repeated
- **WHEN** the accepted GitHub delivery is submitted again after worker execution
- **THEN** the existing run, worktree, assignment, and worker execution remain the only ones for the issue
