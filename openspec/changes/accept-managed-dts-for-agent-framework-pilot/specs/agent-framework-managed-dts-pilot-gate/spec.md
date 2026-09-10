## ADDED Requirements

### Requirement: Managed scheduler use requires an explicit bounded exception
The pilot gate SHALL permit Azure Durable Task Scheduler only when an operator has explicitly accepted the managed-service dependency, the scheduler uses the Consumption SKU, the Azure subscription reports an active spending limit, and a resource-group budget with notifications is observable before workflow execution. The historical OSS gate decision SHALL remain unchanged, and Temporal SHALL remain excluded.

#### Scenario: Governed Consumption exception is ready
- **WHEN** the operator-approved Azure scheduler, Trial spending limit, resource-group budget, task hub, developer access, and exact endpoint are all observed
- **THEN** the gate records those controls and permits the managed durability probe to start

#### Scenario: Cost or service control is missing
- **WHEN** the scheduler is not Consumption, the spending limit is inactive, the budget is unavailable, or the operator exception is absent
- **THEN** the gate fails before starting a workflow and does not reinterpret the OSS no-go as a passing result

### Requirement: Pinned Agent Framework tuple runs against Azure DTS without stored credentials
The managed gate SHALL restore and compile the exact pinned Agent Framework and Durable Task package tuple immediately before execution and SHALL connect to the freshly observed task hub using a `DefaultAzureCredential` constrained to the Azure CLI user without persisting a client secret, storage key, or access token.

#### Scenario: Pinned tuple and developer identity match
- **WHEN** the package lock, .NET runtime, scheduler endpoint, task hub, and Azure CLI tenant/subscription match the approved configuration
- **THEN** the probe starts with `Authentication=DefaultAzure`, excludes non-Azure-CLI credentials, and records correlated source, binary, package-lock, and runtime provenance

#### Scenario: Runtime or Azure target drifts
- **WHEN** a package, runtime, subscription, tenant, endpoint, task hub, or authentication mode differs from the approved configuration
- **THEN** the probe fails before creating a workflow run

### Requirement: A replacement worker continues one durable workflow run
The managed probe SHALL start one Agent Framework workflow on worker one, observe a completed first activity and an incomplete second activity, terminate worker one, and have a separately started worker two finish the same run without restarting a completed activity or duplicating a committed effect.

#### Scenario: Worker one is terminated during incomplete work
- **WHEN** worker one has durably completed the first activity and entered the second activity without completing it
- **THEN** the controller terminates worker one, worker two resumes the pending work under the same run identity, and the final ledger contains every expected committed effect exactly once

#### Scenario: Replacement creates a duplicate or new run
- **WHEN** worker two starts another workflow identity, re-executes a completed activity, omits an effect, or records an effect more than once
- **THEN** the managed gate records a no-go with worker, run, attempt, checkpoint, and effect evidence

### Requirement: Managed pilot evidence remains isolated and reproducible
The managed gate SHALL produce machine-readable and human-readable evidence correlating the operator exception, Azure resource identities, cost controls, package lock, runtime, run identity, worker processes, activity checkpoints, effect ledger, and before/after fingerprints of every protected existing system.

#### Scenario: Managed durability proof passes in isolation
- **WHEN** the cost guard, provenance, worker replacement, effect, and boundary checks all pass
- **THEN** the result is `go-managed-pilot`, Issue 01 remains closed `wontfix` under its preserved OSS criteria with the managed exception recorded complete, and only the next Microsoft pilot ticket becomes eligible to start

#### Scenario: Existing system changes or evidence is incomplete
- **WHEN** a protected LangGraph, Cloudflare, macOS runtime/worktree, GitHub, or ProBara boundary changes, or required evidence is missing
- **THEN** the result is no-go and no downstream Microsoft pilot ticket is unblocked
