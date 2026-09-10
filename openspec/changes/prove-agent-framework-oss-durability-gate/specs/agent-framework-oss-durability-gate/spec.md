## ADDED Requirements

### Requirement: Reproducible eligibility manifest
The gate SHALL validate a committed manifest that correlates the exact repository source revision, package lock, runtime, configuration version, contract version, every direct and transitive workflow/backend component, immutable component version, licence, storage dependency, and unavoidable service cost.

#### Scenario: Complete pinned manifest
- **WHEN** the operator evaluates a manifest whose resolved graph and observed environment match every immutable declaration
- **THEN** the gate records the manifest and observed-provenance digests and permits backend qualification to continue

#### Scenario: Drift or incomplete provenance
- **WHEN** a package, source revision, runtime, configuration, contract, backend, licence, or cost value is missing, floating, incompatible, or differs from the observed value
- **THEN** the gate rejects the combination before starting a workflow or worker

### Requirement: Production open-source backend qualification
The gate SHALL pass backend eligibility only for a production-capable, self-managed open-source backend compatible with the exact Agent Framework Durable Extension tuple and SHALL reject the in-memory emulator, Temporal, and paid managed workflow services as qualifying backends or fallbacks.

#### Scenario: Supported open-source production path
- **WHEN** immutable source and package evidence proves that the pinned client and worker protocol is supported by the selected self-managed open-source production backend without mandatory framework or workflow-service licence charges
- **THEN** the gate permits the isolated durability probe and records the supporting revision, protocol, storage dependencies, licences, and zero unavoidable service charge

#### Scenario: Only development or managed path is available
- **WHEN** the pinned tuple can use only a development emulator, a managed scheduler, a paid service, Temporal, or a backend whose exact compatibility or licence terms cannot be proved
- **THEN** the gate returns a documented no-go and starts neither the durability probe nor any subsequent Microsoft pilot ticket

### Requirement: Worker replacement preserves one durable run
For an eligible backend, the gate SHALL execute one durable run through two separate worker processes, terminate the first after checkpointed progress, and have the second continue the same run without workflow restart, missing effect, or duplicate effect.

#### Scenario: Controlled worker termination
- **WHEN** worker one records the pre-termination checkpoint and is terminated before completing the durable run
- **THEN** worker two resumes the same orchestration identity, completes the remaining step, and the public effect ledger contains each expected effect exactly once

#### Scenario: Restart or duplicate is observed
- **WHEN** the replacement creates a new orchestration identity, replays an already committed effect, omits an effect, or cannot continue without manual backend mutation
- **THEN** the gate records a no-go with the correlated worker, checkpoint, orchestration, and effect evidence

### Requirement: Evidence is correlated and fail-closed
The gate SHALL produce machine-readable and human-readable results that correlate source revision, package lock, runtime, configuration, contract, backend revision, manifest digest, orchestration identity, worker identities, checkpoints, effects, and final decision; an incompatible combination SHALL be rejected before execution.

#### Scenario: Passing result
- **WHEN** manifest validation, backend qualification, worker replacement, and isolation checks all pass
- **THEN** the result is `go`, cites all correlated immutable evidence, and authorizes only the next explicitly requested pilot ticket

#### Scenario: Failing result
- **WHEN** any required check fails or evidence is unavailable
- **THEN** the result is `no-go`, names the failed criterion, exits nonzero for automation, and does not silently downgrade the criterion

### Requirement: Existing systems remain unchanged
The gate SHALL use separate packages, processes, state, ports, temporary worktrees, and cleanup boundaries and SHALL prove by scoped before/after evidence that the LangGraph pilot, Cloudflare relay, macOS operation, runtime data, worktrees, and ProBara CRM remain unchanged.

#### Scenario: Isolated gate execution
- **WHEN** the gate completes with either `go` or `no-go`
- **THEN** its report contains matching before/after fingerprints for every protected boundary and all gate-created resources remain within the gate-owned paths and process namespace

#### Scenario: Protected boundary changes
- **WHEN** any protected fingerprint changes or a gate resource overlaps a protected path, port, process name, database, or worktree
- **THEN** the gate records a no-go and preserves the evidence for diagnosis without cleaning or rewriting the protected resource
