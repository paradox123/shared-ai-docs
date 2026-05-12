# docworkflow-active-openspec-scope Specification

## Purpose

Define the simplified Agent Delivery operating model: one narrow OpenSpec change is the active implementation context, while parent/master specs and research material remain reference-only.

## Requirements

### Requirement: Active OpenSpec scope

Agent Delivery workflow execution SHALL use one narrow OpenSpec change as the active implementation context for large or scope-sensitive work.

#### Scenario: Large workflow work starts from a narrow OpenSpec change

- **GIVEN** a large parent/master spec, research-heavy documentation set, or prior Agent Delivery workflow artifact
- **WHEN** implementation work is requested
- **THEN** the workflow SHALL identify or create exactly one active OpenSpec change for the current slice before editing runtime or workflow files
- **AND** the active OpenSpec change SHALL define the current goal, in-scope behavior, out-of-scope behavior, impacted files or write-set class, and verification expectations.

#### Scenario: Parent spec is reference-only during implementation

- **GIVEN** a parent/master spec and an active OpenSpec change for one slice
- **WHEN** the implementation run starts
- **THEN** the parent/master spec SHALL be treated as read-only reference and conformance context
- **AND** the active OpenSpec change SHALL be the leading implementation contract
- **AND** requirements not pulled into the active OpenSpec change SHALL remain out of scope for that run.

### Requirement: Tool-enforced workflow gates

The simplified workflow SHALL enforce active-scope and cleanup rules through small deterministic command-line tools instead of long Skill-MD prose.

#### Scenario: Active scope validator is available

- **WHEN** Agent Delivery implementation scope is evaluated
- **THEN** a command-line validator SHALL be available to check the active OpenSpec change
- **AND** the validator SHALL fail when implementation would start from a parent/master spec without a narrow active OpenSpec change
- **AND** the validator SHALL report missing goal, in-scope behavior, out-of-scope behavior, tasks, or verification expectations.

#### Scenario: Cleanup validator is available

- **WHEN** cleanup evidence is evaluated
- **THEN** a command-line validator SHALL be available to read `cleanup-manifest.json`
- **AND** it SHALL fail if deleted paths are still referenced as default workflow inputs by canonical docs, active Skill MDs, active tests, or active OpenSpec changes
- **AND** it SHALL fail if retained or archive-reference paths lack reasons.

### Requirement: Default session orchestration is deprecated

Agent Delivery SHALL NOT require fresh child sessions, visible Codex-App sessions, launcher/controller evidence, or session archive proof as default scope-control mechanisms.

#### Scenario: Default delivery succeeds without session launch evidence

- **GIVEN** an active OpenSpec change with bounded scope and passing verification
- **WHEN** the workflow evaluates default delivery readiness
- **THEN** it SHALL NOT require Agent Delivery Session Launch/Queue Evidence, visible-session controller evidence, or archive evidence
- **AND** it SHALL use OpenSpec artifacts, diff evidence, and verification results as the default proof.
