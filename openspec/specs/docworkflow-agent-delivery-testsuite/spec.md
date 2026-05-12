# docworkflow-agent-delivery-testsuite Specification

## Purpose

Capture the simplified Agent Delivery validation contract. The default testsuite now proves active OpenSpec scope, cleanup safety, and Skill-MD prose budgets instead of Parent/Child session orchestration, launcher/controller evidence, or visible Codex-App session proof.

## Requirements

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

### Requirement: Cleanup manifest checks

The testsuite SHALL include deterministic checks for the cleanup manifest produced by the simplification change.

#### Scenario: Cleanup manifest covers candidate classes

- **WHEN** cleanup validation reads `cleanup-manifest.json`
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
