## ADDED Requirements

### Requirement: Acceptance-triggered technical completion
Direct implementation SHALL establish initial behavioral evidence and report technical completion as pending until contextual user acceptance or an equivalent completion request. An authorized coordinator SHALL trigger the same change-accepted workflow for fully delegated work without another human gate. Design agreement, quoted text and unrelated uses of accepted SHALL NOT trigger implementation closeout. Delivery actions and target SHALL derive from actual authorization, not a trigger word.

#### Scenario: Direct implementation ready
- **WHEN** implementation and initial tests finish without a completion request
- **THEN** the agent reports readiness for substantive acceptance and does not start the complete closure reviews, archive or deliver

#### Scenario: Delegated acceptance
- **WHEN** an authorized coordinator accepts a worker's implementation for technical completion
- **THEN** change-accepted runs the same completion contract without requesting additional human acceptance

#### Scenario: Design agreement
- **WHEN** the user accepts a design option or quotes an acceptance phrase
- **THEN** no implementation closeout or delivery authority is inferred

### Requirement: Requirements verification before structural review
change-accepted SHALL critically verify requirement coverage, actual behavior, counterexamples, limits and the implementation-to-spec comparison before invoking code-review. Missing or incorrect behavior SHALL be repaired and affected evidence refreshed first. A list of passing checks SHALL NOT substitute for requirement-level evidence. code-review SHALL check that current requirements evidence is available before structural reviewers start and SHALL NOT add another blanket Spec review afterward.

#### Scenario: Green tests miss a requirement
- **WHEN** a required behavior lacks evidence or the spec comparison reveals a gap
- **THEN** the gap is repaired and verified before structural review starts

### Requirement: Single owner of review methodology
code-review SHALL alone define three independent sequential reviews DRY, SOLID and KISS, each using its own reviewer. Findings SHALL be addressed and affected checks run before the next review. Review SHALL inspect both the scoped diff and surrounding context. Relevant documented repository standards SHALL be assigned explicit coverage within these reviews or existing automated checks; they SHALL NOT disappear when the former Standards/Spec wrapper is replaced. Callers, AGENTS.md and generated guidance SHALL reference the skill instead of copying its methodology.

#### Scenario: All implementation entrypoints
- **WHEN** direct work, a delegated worker or an archive entrypoint needs technical review
- **THEN** it uses code-review or verifies its current receipt without defining a separate review sequence

#### Scenario: Explicit standalone review
- **WHEN** the user asks code-review to inspect a branch or PR
- **THEN** no acceptance trigger is required, missing requirements verification is completed before structural review, and review grants no delivery authority

### Requirement: Content-bound reusable evidence
Completion evidence SHALL bind scope, base, current content identity, requirements, measured results, limitations and per-reviewer coverage. Later repairs SHALL use the same reviewer for affected coverage and retain unaffected findings and coverage. A full repeat SHALL require a recorded reason. Refactoring that invalidates behavioral evidence SHALL reopen affected verification. Repeated acceptance or archival of unchanged content SHALL reuse valid evidence. Relevant final tests SHALL follow final repairs; unchanged applicable results MAY be reused.

#### Scenario: Repair after a later structural pass
- **WHEN** a repair also affects an earlier review dimension or a behavioral requirement
- **THEN** those affected checks reopen against the delta and their final coverage is recorded without routinely restarting every review

#### Scenario: Repeated acceptance and archival
- **WHEN** valid completion evidence covers the current scope and requirements
- **THEN** the caller reuses it and only completes outstanding authorized actions

### Requirement: Central applicability boundary
The complete review contract SHALL apply to substantive code, requirements, effective configuration and binding workflow rules, including skills and AGENTS.md. Pure spelling, formatting or editorial link corrections SHALL receive relevant document checks. Classification SHALL depend on effect, not extension, and SHALL be defined centrally in code-review.

#### Scenario: Documentation changes workflow behavior
- **WHEN** a Markdown edit changes binding agent behavior
- **THEN** it requires the full completion contract after acceptance

#### Scenario: Editorial correction
- **WHEN** a change only corrects spelling without changing meaning
- **THEN** appropriate document checks suffice and the scope rationale is recorded
