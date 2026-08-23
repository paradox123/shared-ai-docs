# bounded-review-repair Specification

## Purpose
TBD - created by archiving change add-bounded-review-repair-rounds. Update Purpose after archive.
## Requirements
### Requirement: Aggregate actionable review findings for the writing implementer
When an initial head-bound review batch contains one or more schema-valid `fail` verdicts, the workflow MUST aggregate every concrete finding from every failed axis into one versioned repair assignment. The assignment MUST retain axis, location, description, reviewed head, original requirements, repository guidance, round identity, prior attempt summaries, and decision boundaries, and MUST be delivered only to the same writing worker in the existing run-owned worktree. Reviewers MUST remain read-only and MUST NOT receive or execute the repair assignment.

#### Scenario: Multiple review axes fail
- **WHEN** requirements and architecture return schema-valid failures with concrete findings for the same current head
- **THEN** round one invokes the existing writing worker once with both axes' structured findings and the original worktree while no reviewer or second writer receives write access

#### Scenario: Review failure is not actionable
- **WHEN** a review batch is blocked by missing, invalid, wrong-head, or otherwise non-schema-valid reviewer output instead of concrete failed-axis findings
- **THEN** the workflow fails closed without inventing a repair finding or marking the pull request verified

### Requirement: Bound autonomous repair decisions and interruptions
The repair assignment MUST permit autonomous choices only for small, reversible implementation or presentation details within existing requirements, domain language, accessibility rules, and the design system. Product behavior, material scope expansion, missing access, unavoidable manual evidence, and non-agentically resolvable conflicts MUST interrupt autonomous repair. Warnings, consent, domain actions, security meaning, and other semantically relevant presentation behavior MUST be treated as product decisions rather than reversible details.

#### Scenario: Reversible presentation detail is unspecified
- **WHEN** a finding can be repaired by a small reversible visual or textual choice that does not change semantic behavior
- **THEN** the implementer chooses within existing repository guidance and continues the round without requesting human input

#### Scenario: Presentation question changes semantic behavior
- **WHEN** resolving a finding would choose the meaning of a warning, consent, domain action, security boundary, or other product behavior
- **THEN** the repair result records a product-decision interruption and the workflow does not synthesize the decision

### Requirement: Enforce at most three repair rounds per initial review batch
The workflow MUST associate one monotonic repair-round counter with the initial failed review batch and MUST begin no more than three automatic rounds for that batch. A structured escalation within a numbered round MUST NOT create another numbered round. After the third unsuccessful round, a further failure MUST NOT start a fourth repair assignment or writing-worker invocation.

#### Scenario: Third repaired head still fails
- **WHEN** the fresh review batch for repair round three contains another `fail`
- **THEN** the repair batch becomes terminal with exactly three numbered attempts and no fourth repair invocation

#### Scenario: Repair succeeds before the limit
- **WHEN** deterministic verification and every applicable review pass for the head produced by round one or two
- **THEN** the repair batch completes as verified and no later repair round starts

### Requirement: Enforce repair model, reasoning, and access policy
Regular repair work MUST use `gpt-5.6-terra` with `xhigh` reasoning and workspace-write access restricted to the existing run worktree. `gpt-5.6-sol` with `xhigh` MUST be selectable for a writing repair invocation only for a defined material architecture, persistence, security, or data-migration escalation, a schema-valid structured `escalate`, or the third and final repair round. Unsupported Sol reasons, other reasoning levels, other write roots, and reviewer write access MUST be rejected before worker execution.

#### Scenario: Ordinary first repair round starts
- **WHEN** failed review findings require no defined escalation
- **THEN** the writing worker receives Terra/`xhigh`/workspace-write for the existing run worktree with policy and skill provenance persisted

#### Scenario: Final repair round starts
- **WHEN** two prior numbered repair rounds have not produced a verified head
- **THEN** round three receives Sol/`xhigh` with the same bounded implementer write root and records `final_repair_round` as its allowed escalation reason

#### Scenario: Unsupported Sol repair is requested
- **WHEN** a caller requests Sol for an unlisted reason or a non-final ordinary round
- **THEN** policy validation rejects the invocation before source or GitHub mutation

### Requirement: Reverify every repair commit completely on its new head
Each schema-valid completed repair MUST produce a new committed and pushed head on the existing run branch and update the one existing draft pull request. The workflow MUST run the configured deterministic verification on that exact committed head and MUST execute fresh, independent requirements, code-quality, and architecture reviews in full against the same head, even when deterministic verification fails. Prior evidence, checks, verdicts, and verification labels MUST NOT qualify the new head. A repair round MUST pass only when deterministic verification passes, every applicable fresh review passes, and GitHub still reports the reviewed head as current.

#### Scenario: First repaired head verifies
- **WHEN** round one produces a new head whose deterministic command passes and whose three fresh reviews all pass or validly report `not_applicable`
- **THEN** the existing draft pull request is updated to that head, receives `verified` and `awaiting-review`, loses `agent-running`, and the repair batch completes without round two

#### Scenario: Deterministic verification fails
- **WHEN** a repair commit's deterministic verification fails
- **THEN** all three fresh review axes still execute for that same head, the attempt remains unsuccessful, and its verification observation plus failed-axis findings are retained for the next repair assignment

#### Scenario: Repair does not create a new head
- **WHEN** a completed repair result produces no commit or reuses the previously reviewed SHA
- **THEN** the attempt fails closed and the workflow does not reuse prior verification or represent the unchanged head as repaired

### Requirement: Preserve attempts and project a precise human handoff
Every repair assignment, invocation policy and skill provenance, redacted result and diagnostics, deterministic verification, produced head, linked review batch, and open finding MUST remain associated with the persistent run and existing draft pull request. After three unsuccessful rounds, missing or contradictory requirements MUST project `needs-info`; otherwise a conflict that cannot be resolved agentically MUST project `ready-for-human`. Terminal handoff MUST preserve the draft PR and attempt history, remove `agent-running`, add neither `verified` nor `awaiting-review`, and MUST NOT merge, deploy, or release.

#### Scenario: Exhausted rounds reveal missing requirements
- **WHEN** three unsuccessful rounds end with a structured missing-or-contradictory-requirements classification
- **THEN** the existing draft PR and all attempts remain observable and the issue has `needs-info` without `agent-running`, `verified`, or `awaiting-review`

#### Scenario: Exhausted rounds leave a technical conflict
- **WHEN** three unsuccessful rounds end without a missing-or-contradictory-requirements classification and the open conflict is not agentically resolvable
- **THEN** the existing draft PR and all attempts remain observable and the issue has `ready-for-human` without `agent-running`, `verified`, or `awaiting-review`

### Requirement: Expose repair behavior through the primary system seam
Workflow-state read-back MUST expose the repair batch, initial review identity, round limit and count, ordered attempts, assignments, policies, results, deterministic verification, per-attempt heads and review links, open findings, terminal disposition, projected labels, and timestamps. Acceptance verification MUST drive authenticated GitHub delivery with real SQLite and LangGraph persistence and controlled worker, Git, verifier, and GitHub boundaries, and MUST NOT assert private graph node order, helper calls, raw database rows, or checkpoint tables.

#### Scenario: System seam observes successful repair
- **WHEN** the initial controlled review fails and the first repair produces a passing deterministic check and fresh review batch
- **THEN** signed HTTP read-back exposes the initial failure, one persisted repair attempt, a new verified PR head, and the successful GitHub label projection

#### Scenario: System seam observes bounded terminal outcomes after restart
- **WHEN** controlled reviewers keep failing through three rounds for missing requirements in one run and an unresolvable conflict in another, and each application is reconstructed against its database
- **THEN** HTTP read-back preserves exactly three attempts, the draft PR and open findings, no fourth invocation, and respectively the `needs-info` and `ready-for-human` projection without repeated external effects
