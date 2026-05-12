## ADDED Requirements

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

#### Scenario: Missing active scope blocks implementation

- **GIVEN** a large or scope-sensitive Agent Delivery request without a narrow active OpenSpec change
- **WHEN** a skill would otherwise start implementation
- **THEN** it SHALL stop before edits
- **AND** it SHALL create or request the missing active OpenSpec change instead of implementing from the whole parent/master spec.

### Requirement: No duplicate Micro-Spec artifact

The workflow SHALL NOT introduce a separate mandatory Micro-Spec, Scope Capsule, or Active Context Contract file that duplicates OpenSpec change content.

#### Scenario: Active context view is derived

- **GIVEN** an active OpenSpec change with proposal, optional design, spec deltas, and tasks
- **WHEN** the agent needs a short kickoff summary
- **THEN** it MAY derive a concise active context view from those OpenSpec files
- **AND** the derived view SHALL NOT become a separate source of truth.

#### Scenario: Duplicate scope document is stale

- **GIVEN** a separate scope summary conflicts with the active OpenSpec change
- **WHEN** implementation scope is evaluated
- **THEN** the OpenSpec change SHALL win
- **AND** the conflicting summary SHALL be corrected or ignored before implementation continues.

### Requirement: Default session orchestration is deprecated

Agent Delivery SHALL NOT require fresh child sessions, visible Codex-App sessions, launcher/controller evidence, or session archive proof as default scope-control mechanisms.

#### Scenario: Default delivery succeeds without session launch evidence

- **GIVEN** an active OpenSpec change with bounded scope and passing verification
- **WHEN** the workflow evaluates default delivery readiness
- **THEN** it SHALL NOT require Agent Delivery Session Launch/Queue Evidence, visible-session controller evidence, or archive evidence
- **AND** it SHALL use OpenSpec artifacts, diff evidence, and verification results as the default proof.

#### Scenario: Legacy debug tooling is explicit

- **GIVEN** a workflow or test still needs visible-session diagnosis
- **WHEN** the user explicitly selects legacy/debug session tooling
- **THEN** that tooling MAY run as a non-default diagnostic path
- **AND** its evidence SHALL NOT be required for normal Agent Delivery success.

### Requirement: Skill slimming

The affected Skill MDs SHALL route to the simplified OpenSpec-first workflow without duplicating long Agent Delivery contracts.

#### Scenario: Skill points to canonical workflow

- **WHEN** a skill handles Agent Delivery planning, hardening, implementation, closeout, or retro-review
- **THEN** it SHALL point to `docs/doc-workflow.md` as the canonical workflow source
- **AND** it SHALL instruct the agent to work from the active OpenSpec change for implementation-scope work.

#### Scenario: Skill does not carry obsolete matrices

- **WHEN** Skill MDs are reviewed after this change
- **THEN** they SHALL NOT contain large duplicated child-session handoff schemas, run-profile matrices, visible-session controller contracts, or archive-evidence rules as default workflow requirements.

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

#### Scenario: Skills call tools instead of restating rules

- **WHEN** an affected Skill MD references active-scope or cleanup gates
- **THEN** it SHALL name the relevant validator command
- **AND** it SHALL NOT restate the validator's full rule set in prose.

### Requirement: Obsolete artifact cleanup

The implementation SHALL inventory and remove obsolete Agent Delivery artifacts that exist only to support the deprecated default session-orchestration workflow.

#### Scenario: Cleanup inventory classifies candidates

- **GIVEN** existing Agent Delivery OpenSpec changes, tools, tests, fixtures, generated evidence, session-workflow data, and handoff/index artifacts
- **WHEN** cleanup starts
- **THEN** each cleanup candidate SHALL be classified as `delete`, `retain`, or `archive-reference`
- **AND** the classification SHALL include a short reason
- **AND** the classification SHALL be recorded in `openspec/changes/simplify-agent-delivery-active-openspec/cleanup-manifest.json`.

#### Scenario: Cleanup order is bounded

- **WHEN** cleanup is applied
- **THEN** generated evidence and live-session run directories SHALL be handled before tests and fixtures
- **AND** tests and fixtures SHALL be handled before tools
- **AND** tools SHALL be handled before archived or active OpenSpec experiment changes.

#### Scenario: Deletion is conservative for retained history

- **GIVEN** an artifact is accepted baseline evidence, canonical documentation, active implementation input, or still-needed simplified regression coverage
- **WHEN** cleanup is applied
- **THEN** that artifact SHALL NOT be deleted
- **AND** it SHALL be listed as retained in cleanup evidence.

#### Scenario: Obsolete generated evidence is removed

- **GIVEN** generated session evidence, temporary live-session run directories, obsolete visible-session fixtures, or controller/launcher debug artifacts that are not retained baselines
- **WHEN** cleanup is applied
- **THEN** those artifacts SHALL be deleted or moved to an explicit archive-reference location
- **AND** no simplified workflow gate SHALL reference them as default success evidence.

#### Scenario: Cleanup evidence is produced

- **WHEN** cleanup completes
- **THEN** `openspec/changes/simplify-agent-delivery-active-openspec/cleanup-evidence.md` SHALL list deleted paths, retained paths, archive-reference paths, and unresolved cleanup decisions
- **AND** verification SHALL prove that no deleted path is still referenced by canonical workflow docs, active Skill MDs, or simplified tests.

### Requirement: Simplified workflow documentation

`docs/doc-workflow.md` SHALL become the canonical description of the simplified OpenSpec-first Agent Delivery workflow.

#### Scenario: Documentation states the new default

- **WHEN** `docs/doc-workflow.md` is updated
- **THEN** it SHALL state that the default active implementation context is one narrow OpenSpec change
- **AND** it SHALL state that parent/master specs are reference and coverage inputs, not direct implementation contracts.

#### Scenario: Documentation retires obsolete defaults

- **WHEN** `docs/doc-workflow.md` is updated
- **THEN** it SHALL remove or clearly mark as legacy/debug-only the default requirements for child-session launches, controller-backed visible sessions, launcher evidence, run profiles, and archive proof.
