# independent-pr-review-verification Specification

## Purpose
Define how an evidence-backed draft pull request is independently reviewed on requirements, code quality, and architecture and verified only for the unchanged reviewed head.
## Requirements
### Requirement: Execute three independent head-bound reviews
After publishing an evidence-backed draft pull request, the workflow MUST execute requirements, code-quality, and architecture review as three separate worker invocations with fresh context, read-only access, and the same adapter-observed pull-request head SHA. Reviewer input MUST NOT include another reviewer's verdict or conversational state, and reviewers MUST NOT modify the branch, repair findings, merge, deploy, or synthesize a product decision.

#### Scenario: Published head enters review
- **WHEN** a draft pull request with qualified evidence is published for a run
- **THEN** three distinct read-only invocations receive the same requirements, implementation, evidence, repository guidance, diff, and immutable head SHA without receiving one another's results

### Requirement: Validate and retain structured reviewer verdicts
Every reviewer MUST return a versioned, schema-valid result containing its axis, reviewed head SHA, a verdict of `pass`, `fail`, or `not_applicable`, a non-empty rationale, and concrete findings. Requirements review MUST be applicable and MUST NOT return `not_applicable`. The workflow MUST retain each result separately with invocation identity, model, reasoning effort, access profile, skill names, and skill content hashes.

#### Scenario: Reviewer returns a valid verdict
- **WHEN** a reviewer returns a schema-valid result for its assigned axis and current head
- **THEN** the workflow persists that axis result and its complete policy and skill provenance without combining it with another axis

#### Scenario: Reviewer result is missing or invalid
- **WHEN** any invocation fails or returns missing, malformed, schema-invalid, wrong-axis, wrong-head, or forbidden requirements `not_applicable` output
- **THEN** the review batch is durably blocked and the pull request is not projected as verified

### Requirement: Route each review axis to its prescribed policy and skills
Regular reviews MUST use `gpt-5.6-terra` with `xhigh` reasoning and read-only access. Requirements review MUST use the specification axis of `code-review` to compare requirements, implementation, and behavioral evidence. Code-quality review MUST use the standards axis of `code-review` to check repository standards and relevant code smells. Architecture review MUST use `codebase-design` and `domain-modeling` to check domain language, ADRs, modules, interfaces, seams, adapters, depth, and test surfaces.

#### Scenario: Review routing is prepared
- **WHEN** the workflow prepares the three reviewer invocations
- **THEN** each invocation has Terra/`xhigh`/read-only policy and exactly the prescribed axis-specific skills with recorded content hashes

#### Scenario: Unsupported review routing is requested
- **WHEN** an invocation requests a different model, reasoning effort, access profile, or skill routing for a regular review
- **THEN** the worker adapter rejects it before launching a reviewer

### Requirement: Aggregate independent verdicts without compensation
The workflow MUST preserve all three axes and aggregate them deterministically. Any `fail`, invalid result, or missing result MUST block verification. A batch MAY pass only when requirements returns `pass` and code-quality and architecture each return `pass` or a valid `not_applicable`; one axis MUST NOT override or compensate for another.

#### Scenario: One review axis fails
- **WHEN** requirements and architecture pass but code quality fails
- **THEN** the batch remains blocked with all three results observable and no verification labels are projected

#### Scenario: Every applicable review axis passes
- **WHEN** requirements passes and the other two axes each pass or validly report `not_applicable`
- **THEN** the batch qualifies for current-head verification

### Requirement: Project verification only for the unchanged reviewed head
Before successful projection, the workflow MUST read the pull request's current head and match it to the reviewed SHA. Only an unchanged head with a passing batch MUST receive `verified` and `awaiting-review` and lose `agent-running`. A failed batch or head mismatch MUST NOT receive that projection. The workflow MUST NOT merge, deploy, or alter the source branch.

#### Scenario: Passing batch still targets current head
- **WHEN** every applicable axis passes and GitHub reports the reviewed SHA as the current pull-request head
- **THEN** the adapter adds `verified` and `awaiting-review`, removes `agent-running`, and records the exact verified head

#### Scenario: Pull-request head changed during review
- **WHEN** all verdicts pass but GitHub reports a different current head
- **THEN** verification fails closed and no success-label projection is performed for either head

### Requirement: Expose durable review behavior through the primary system seam
The workflow MUST expose the head-bound review batch, three separate results, aggregation outcome, provenance, and projected labels through workflow-state read-back. Acceptance verification MUST drive the authenticated GitHub delivery with real SQLite and LangGraph persistence and controlled worker/GitHub boundaries, and MUST NOT assert private graph node order, helper calls, raw database rows, or checkpoint tables.

#### Scenario: System seam observes blocked and successful review batches
- **WHEN** behavior tests submit a published implementation whose controlled reviewers include one failure and another whose applicable reviewers all pass
- **THEN** signed HTTP read-back exposes three separate verdicts and fail-closed blocking for the first, and the exact verified head plus successful GitHub label projection for the second

#### Scenario: Application restarts after successful review
- **WHEN** the application is reconstructed against the same database after successful projection
- **THEN** HTTP read-back exposes the same batch, verdicts, provenance, verified head, and labels without another reviewer or GitHub invocation

### Requirement: Independent reviews can request intervention without losing isolation
Each requirements, code-quality, or architecture review result contract MUST support one schema-valid intervention when its existing read-only mandate encounters a policy-authorized human decision or action. The affected review MUST preserve its axis, immutable head, findings, policy, and fresh invocation identity; it MUST NOT receive peer verdicts, write source, synthesize the answer, or let an influenced or stale review qualify a later head.

#### Scenario: One review axis needs a product decision
- **WHEN** a fresh head-bound reviewer finds contradictory acceptance behavior that cannot be classified as pass or actionable implementation failure without human input
- **THEN** that axis persists an intervention and the review batch pauses with its completed peer results retained and no verification projection

#### Scenario: Review resumes after an answer without a head change
- **WHEN** the same immutable head remains current after the answer
- **THEN** the affected axis receives only the bounded answer context and the batch can aggregate only after every required independent result is valid for that head
