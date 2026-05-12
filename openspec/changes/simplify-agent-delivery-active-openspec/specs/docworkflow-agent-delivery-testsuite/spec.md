## ADDED Requirements

### Requirement: Simplified Agent Delivery active-scope checks

The testsuite SHALL validate the simplified Agent Delivery workflow by checking active OpenSpec scope boundaries instead of proving default multi-session orchestration.

#### Scenario: Parent-as-implementation is rejected

- **GIVEN** a large parent/master spec and no narrow active OpenSpec change
- **WHEN** the simplified Agent Delivery validator evaluates an implementation attempt
- **THEN** the result SHALL fail or block
- **AND** the failure SHALL state that implementation must start from one active OpenSpec change.

#### Scenario: Narrow OpenSpec slice is accepted

- **GIVEN** a narrow active OpenSpec change with bounded scope, out-of-scope statements, write-set expectations, tasks, and verification commands
- **WHEN** the simplified Agent Delivery validator evaluates the kickoff state
- **THEN** the result SHALL pass the active-scope gate
- **AND** parent/master material SHALL be reported as reference-only context.

#### Scenario: Deprecated session artifacts are not default gates

- **GIVEN** a valid active OpenSpec change and no child-session launch evidence
- **WHEN** simplified Agent Delivery validation runs
- **THEN** it SHALL NOT fail only because launcher, controller, visible-session, or archive evidence is absent.

#### Scenario: Large parent spec is delivered through active OpenSpec slices

- **GIVEN** a large simulated parent spec with five ordered work packages
- **WHEN** the Active OpenSpec E2E runner executes
- **THEN** it SHALL derive five narrow active OpenSpec changes instead of child specs
- **AND** each slice SHALL pass strict OpenSpec validation and active-scope validation
- **AND** the final output file SHALL contain exact ordered values `1`, `2`, `3`, `4`, and `5`.

#### Scenario: Cleanup does not leave stale default references

- **GIVEN** obsolete Agent Delivery artifacts have been deleted or archived
- **WHEN** canonical docs, Skill MDs, and simplified tests are scanned
- **THEN** no default workflow requirement SHALL reference deleted launcher/controller/session evidence paths
- **AND** any remaining legacy/debug reference SHALL be explicitly labelled as non-default.

### Requirement: Cleanup manifest checks

The testsuite SHALL include deterministic checks for the cleanup manifest produced by the simplification change.

#### Scenario: Cleanup manifest covers candidate classes

- **WHEN** cleanup validation reads `openspec/changes/simplify-agent-delivery-active-openspec/cleanup-manifest.json`
- **THEN** it SHALL include entries for OpenSpec changes, Skill MDs, docs, tools, tests, fixtures, generated evidence, and session/handoff artifacts considered during cleanup.

#### Scenario: Deleted paths are not referenced

- **GIVEN** a cleanup manifest with deleted paths
- **WHEN** cleanup validation scans canonical workflow docs, active Skill MDs, active tests, and active OpenSpec changes
- **THEN** deleted paths SHALL NOT be referenced as required workflow inputs.

#### Scenario: Retained paths have reasons

- **GIVEN** a cleanup manifest with retained or archive-reference paths
- **WHEN** cleanup validation runs
- **THEN** each retained or archive-reference entry SHALL include a reason
- **AND** accepted baseline evidence SHALL be distinguishable from obsolete generated evidence.

### Requirement: Skill prose budget checks

The testsuite SHALL include a deterministic guard against reintroducing long Agent Delivery prose blocks into Skill MDs.

#### Scenario: Affected skills stay short

- **WHEN** prose-budget validation scans affected Skill MDs
- **THEN** it SHALL fail if an affected Skill MD contains a long Agent Delivery session-orchestration rule block
- **AND** it SHALL pass when the skill uses short routing language plus validator command references.

#### Scenario: Validator commands are referenced

- **WHEN** affected Skill MDs mention active-scope or cleanup gates
- **THEN** prose-budget validation SHALL require a referenced command-line validator
- **AND** it SHALL fail if the skill restates the validator's full rule set instead.

## REMOVED Requirements

### Requirement: DWT-S2 L2 parent-first orchestration agent harness

**Reason**: The simplified workflow no longer treats parent-first child orchestration as the default proof path. Large parent specs are reduced to one active OpenSpec change before implementation.

**Migration**: Replace with `Simplified Agent Delivery active-scope checks`, especially the parent-as-implementation rejection and narrow OpenSpec slice acceptance scenarios.

### Requirement: DWT-S3 L2 single-child delivery and closeout gate harness

**Reason**: The simplified workflow no longer depends on child handoffs and child closeout gates as the normal delivery boundary.

**Migration**: Use active OpenSpec change scope, tasks, and verification evidence for one slice. Preserve only any retained baseline evidence needed for historical comparison.

### Requirement: DWT-S5 L3 runtime temp-repo delivery pilot

**Reason**: The runtime temp-repo pilot belongs to the old staged Agent Delivery testsuite and is not required to validate the simplified workflow.

**Migration**: Keep runtime verification only when required by a specific active OpenSpec change. Delete or archive generic DWT-S5 pilot fixtures unless retained by cleanup classification.

### Requirement: Post-orchestration next-step evaluator

**Reason**: The simplified workflow does not need a child-orchestration next-step evaluator because the next implementation step is selected by creating or choosing a narrow active OpenSpec change.

**Migration**: Remove or archive `EvaluateOrchestrationNextStep.cs` unless another retained workflow still references it.

### Requirement: Child handoff synchronization tool

**Reason**: Child handoff synchronization is part of the deprecated default Parent/Child session workflow.

**Migration**: Remove or archive `SyncChildHandoff.cs` and related fixtures unless cleanup classification finds a retained historical reason.

### Requirement: Orchestration pack validation tool

**Reason**: Orchestration packs are no longer the default control surface for Agent Delivery implementation.

**Migration**: Replace orchestration-pack validation with active OpenSpec scope validation.

### Requirement: Spec-orchestrator uses post-orchestration evaluator gate

**Reason**: `spec-orchestrator` should no longer release downstream work through child orchestration gates.

**Migration**: Slim `spec-orchestrator` so it routes large work toward narrow OpenSpec changes and stops before implementation.

### Requirement: Workflow Doctor post-orchestration wrapper

**Reason**: Workflow Doctor orchestration wrappers exist to support the old child-control-surface workflow and are not part of the simplified default path.

**Migration**: Remove orchestration-wrapper behavior unless retained for a non-default legacy/debug path.

### Requirement: Mock E2E fixture family

**Reason**: Mock E2E fixtures that prove large parent/child session mechanics are obsolete under the simplified active OpenSpec workflow.

**Migration**: Replace with smaller active-scope and cleanup-manifest fixtures.

### Requirement: Local mock E2E runner

**Reason**: The local mock E2E runner validates old large/small Agent Delivery paths rather than the simplified default workflow.

**Migration**: Delete or archive the runner after adding simplified validators.

### Requirement: Mock-only standard Agent Delivery gate

**Reason**: The new standard gate is active OpenSpec scope, not mock-only proof of the old Agent Delivery orchestration path.

**Migration**: Replace with active-scope validation and cleanup-manifest validation.

### Requirement: Visible app-server launcher adapter

**Reason**: Visible Codex-App launcher behavior is no longer a default workflow requirement.

**Migration**: Retain only as explicitly labelled legacy/debug tooling if the cleanup inventory finds it still useful.

### Requirement: External visible-session controller MVP

**Reason**: Controller-backed visible multi-session orchestration is the mechanism being retired from the default workflow.

**Migration**: Delete or archive controller tooling and evidence unless kept as non-default debug reference.

### Requirement: MD-E2E-5 external controller integration

**Reason**: MD-E2E-5 validates the discarded visible-session controller path.

**Migration**: Replace with simplified active-scope tests and cleanup-manifest tests.

### Requirement: Agent Delivery evidence resolver gate

**Reason**: Evidence resolver gates for launcher/controller/archive proof are not needed for the simplified OpenSpec-first default.

**Migration**: Remove or narrow `WorkflowDoctor.cs --phase evidence-resolution` to any still-retained non-default debug use. Default validation SHALL use OpenSpec scope and cleanup checks.

### Requirement: Skill slimming through resolver handoff

**Reason**: Skill slimming should no longer depend on evidence resolver handoff language.

**Migration**: Replace with skill slimming through canonical OpenSpec-first workflow pointers and removal of obsolete session-orchestration detail.
