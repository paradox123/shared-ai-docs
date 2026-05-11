## ADDED Requirements

### Requirement: Agent Delivery evidence resolver gate

The Agent Delivery testsuite SHALL provide a deterministic evidence resolver gate that classifies Launcher-only, controller-backed visible multi-session, and closeout archive evidence without requiring the skills to restate every low-level evidence rule.

#### Scenario: Launcher-only evidence resolves to pass

- **GIVEN** a Child Session Handoff with matching `launch-request.json`, `start-prompt.md`, and `evidence.json` for the same target id and handoff path
- **WHEN** the resolver evaluates the handoff evidence
- **THEN** it SHALL emit `verdict: "pass"`
- **AND** it SHALL emit `mode: "launcher_only"`
- **AND** the launcher status SHALL satisfy the requested claim level, such as `queued` for a queued handoff claim or `launched` for a launched-session claim
- **AND** it SHALL include the matched launch request, start prompt, and evidence paths.

#### Scenario: Controller-backed visible workflow resolves to pass

- **GIVEN** a retained controller-backed visible multi-session run with controller summary, request artifacts, response artifacts, retained visible-session summary, and matching per-session launcher evidence
- **WHEN** the resolver evaluates the run
- **THEN** it SHALL emit `verdict: "pass"`
- **AND** it SHALL emit `mode: "controller_visible_multi_session"`
- **AND** it SHALL include controller artifacts, the visible-session summary, and all matched per-session launcher evidence paths.

#### Scenario: Parent-started child launch blocks controller-backed workflow

- **GIVEN** a workflow that claims controller-backed visible multi-session success
- **WHEN** evidence shows that the parent session started a child launcher, `codex app-server`, or any other child-start command itself
- **THEN** the resolver SHALL emit `verdict: "fail"` or `verdict: "not_ready"`
- **AND** it SHALL include a blocker explaining that parent-started child launches do not satisfy the controller-backed gate.

#### Scenario: Closeout archive evidence resolves to pass

- **GIVEN** closeout evidence with an archive summary that records archived visible sessions, explicit no-thread statuses, or accepted retained-session notes
- **WHEN** the resolver evaluates the closeout evidence
- **THEN** it SHALL emit `verdict: "pass"` only when the archive summary is valid for closeout according to the accepted visible-session archive summary contract
- **AND** it SHALL emit `mode: "closeout_archive"`
- **AND** it SHALL include the archive summary path and relevant session evidence paths.

#### Scenario: Incomplete evidence is not ready

- **GIVEN** a handoff or retained run with missing launch evidence, missing controller responses, mismatched target ids, mismatched handoff paths, `manual_start_required`, `blocked`, `failed`, queued evidence for a claim that requires launched or visible proof, unarchived visible session, or manual-visible missing-thread statuses
- **WHEN** the resolver evaluates the evidence
- **THEN** it SHALL NOT emit `verdict: "pass"`
- **AND** it SHALL include blocker details and evidence paths for the failed or missing checks.

#### Scenario: Verdict schema is stable

- **GIVEN** any resolver evaluation
- **WHEN** the resolver emits JSON
- **THEN** the output SHALL include `schema_id`, `verdict`, `mode`, `evidence_paths`, `blockers`, `warnings`, and `recommended_next_action`
- **AND** `verdict` SHALL be one of `pass`, `not_ready`, or `fail`
- **AND** `mode` SHALL be one of `launcher_only`, `controller_visible_multi_session`, or `closeout_archive`.

### Requirement: Skill slimming through resolver handoff

The Agent Delivery skills SHALL delegate Launcher/Controller/archive evidence consistency checks to the resolver gate while retaining only role, stop-condition, and handoff instructions.

#### Scenario: Skills call resolver instead of duplicating evidence rules

- **GIVEN** an Agent Delivery skill must decide whether a fresh-session, controller-backed, or closeout-evidence claim is acceptable
- **WHEN** the resolver command is available
- **THEN** the skill SHALL call or require the resolver command
- **AND** it SHALL obey `pass`, `not_ready`, and `fail` verdicts instead of independently reimplementing the detailed evidence matrix.

#### Scenario: Skills preserve stop conditions

- **GIVEN** the resolver emits `not_ready` or `fail`
- **WHEN** a skill is preparing implementation, closeout, or next-child release
- **THEN** the skill SHALL stop the transition
- **AND** it SHALL surface resolver blockers and recommended next action in its output.

#### Scenario: Skills are not slimmed before resolver is available

- **GIVEN** the resolver command or fixture replay is not yet implemented
- **WHEN** an implementation attempts to remove existing detailed evidence checks from a skill
- **THEN** the change SHALL remain incomplete
- **AND** the affected skill SHALL keep its existing stop conditions until resolver verification passes.

#### Scenario: Workflow docs remain canonical

- **GIVEN** the skills are slimmed
- **WHEN** a future reviewer compares the skills with `docs/doc-workflow.md`
- **THEN** the workflow document SHALL remain the canonical source for Launcher, Controller, and archive role definitions
- **AND** the skills SHALL not introduce alternate role definitions.
