## MODIFIED Requirements

### Requirement: Active OpenSpec scope

Large or scope-sensitive workflow work SHALL use one narrow OpenSpec change as the active implementation context.

#### Scenario: Large workflow work starts from a narrow OpenSpec change

- **GIVEN** a large parent/master spec, research-heavy documentation set, or prior orchestration artifact
- **WHEN** implementation work is requested
- **THEN** the workflow SHALL identify or create exactly one active OpenSpec change for the current slice before editing runtime or workflow files
- **AND** the active OpenSpec change SHALL define the current goal, in-scope behavior, out-of-scope behavior, impacted files or write-set class, and verification expectations.

#### Scenario: Parent spec is reference-only during implementation

- **GIVEN** a parent/master spec and an active OpenSpec change for one slice
- **WHEN** the implementation run starts
- **THEN** the parent/master spec SHALL be treated as read-only reference and conformance context
- **AND** the active OpenSpec change SHALL be the leading implementation contract
- **AND** requirements not pulled into the active OpenSpec change SHALL remain out of scope for that run.

#### Scenario: Missing active scope blocks implementation

- **GIVEN** a large or scope-sensitive request without a narrow active OpenSpec change
- **WHEN** implementation would otherwise start
- **THEN** it SHALL stop before edits
- **AND** it SHALL create or request the missing active OpenSpec change instead of implementing from the whole parent/master spec.

### Requirement: Tool-enforced workflow gates

Active-scope validation SHALL use a small deterministic command-line tool rather than a dedicated orchestration testsuite or long duplicated workflow prose.

#### Scenario: Active scope validator is available

- **WHEN** implementation scope is evaluated
- **THEN** `skills-repo/tools/ValidateActiveOpenSpecScope.cs` SHALL be available to check the active OpenSpec change
- **AND** it SHALL fail when required OpenSpec scope artifacts or fields are missing.

### Requirement: Default session orchestration is deprecated

Workflow delivery SHALL NOT require fresh child sessions, visible Codex-App sessions, launcher/controller evidence, or session archive proof as default scope-control mechanisms.

#### Scenario: Default delivery succeeds without session launch evidence

- **GIVEN** an active OpenSpec change with bounded scope and passing verification
- **WHEN** the workflow evaluates default delivery readiness
- **THEN** it SHALL NOT require launcher, controller, visible-session, or archive evidence
- **AND** it SHALL use OpenSpec artifacts, diff evidence, and verification results as the default proof.

#### Scenario: Legacy session tooling is not part of the active contract

- **GIVEN** historical documentation describes session-orchestration tooling
- **WHEN** current workflow requirements are evaluated
- **THEN** that historical material SHALL NOT become a default implementation or verification gate.

## ADDED Requirements

### Requirement: No duplicate active-scope artifact

The workflow SHALL NOT require a separate Micro-Spec, Scope Capsule, or Active Context Contract file that duplicates OpenSpec change content.

#### Scenario: Active context view is derived

- **GIVEN** an active OpenSpec change with proposal, optional design, spec deltas, and tasks
- **WHEN** the agent needs a short kickoff summary
- **THEN** it MAY derive a concise active-context view from those OpenSpec files
- **AND** the derived view SHALL NOT become a separate source of truth.
