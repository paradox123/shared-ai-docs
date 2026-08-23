## ADDED Requirements

### Requirement: Accept only explicit human feedback for the associated pull request
The workflow MUST accept a change-request review or review comment as implementation feedback only when the authenticated delivery targets the persistent run's stored pull request, contains non-empty new feedback, and identifies the configured human as author. It MUST reject or ignore approvals, generic pull-request activity, bot or other-user comments, unrelated pull requests, and unsupported actions without starting implementation or changing workflow labels.

#### Scenario: Daniel requests changes on the run pull request
- **WHEN** a signed supported review delivery from the configured human contains new change-request feedback for the pull request persisted on a running workflow
- **THEN** the workflow durably accepts one feedback batch for that delivery and associates it with the existing run

#### Scenario: Pull-request activity is not human feedback
- **WHEN** a signed delivery is an approval, a synchronize/open/edit activity, bot or other-user feedback, empty feedback, or feedback for another pull request
- **THEN** no feedback batch, writer invocation, source publication, or workflow-label change occurs

### Requirement: Continue the same run and bounded writing context
Every accepted human feedback batch MUST resume the existing LangGraph run, run-owned worktree, branch, and pull request rather than create an initial implementation execution or a second run. Its writing assignment MUST contain only that batch's new human feedback together with the still-valid issue, requirements, repository guidance, decision boundaries, and prior head identity; it MUST NOT include human feedback from earlier batches as active instructions.

#### Scenario: New feedback resumes existing ownership
- **WHEN** an accepted feedback batch starts implementation
- **THEN** its writer receives the original run ID, worktree, branch, pull-request identity, issue and requirements plus only the newly submitted feedback

#### Scenario: Later feedback arrives after an earlier feedback batch
- **WHEN** the configured human submits another supported change request after the earlier batch terminated
- **THEN** a distinct feedback batch starts without copying the earlier batch's feedback into the active assignment

### Requirement: Enforce three repair rounds independently per human feedback batch
The workflow MUST maintain a separate monotonic counter with a maximum of three numbered implementation attempts for each accepted human feedback batch. Initial review repair attempts and attempts from earlier or later human feedback batches MUST NOT consume or reset another batch's counter, and no fourth writer invocation MAY occur for one batch.

#### Scenario: Feedback follows exhausted initial review repair
- **WHEN** the initial review batch used three repair rounds and a new human feedback batch is accepted
- **THEN** the feedback batch may begin at round one with its own three-round limit

#### Scenario: One feedback batch exhausts its limit
- **WHEN** three produced heads for the same human feedback batch remain unsuccessful
- **THEN** that batch becomes terminal with exactly three attempts and no fourth writer invocation while a later new feedback batch would receive a new counter

### Requirement: Invalidate all prior-head qualification on a new feedback commit
Each completed feedback attempt MUST publish a new commit to the existing run branch and update the existing pull request. As soon as the new head is published, the workflow MUST add `agent-running`, remove `verified` and `awaiting-review`, and make every evidence package, deterministic verification, review verdict, and verification projection for earlier heads ineligible to qualify the new head. Historical records MUST remain observable with their original head identity.

#### Scenario: Human feedback produces a new head
- **WHEN** the writer publishes a commit whose SHA differs from the feedback batch's prior pull-request head
- **THEN** the existing pull request moves to the new SHA, old-head qualification is superseded, and GitHub labels contain `agent-running` without `verified` or `awaiting-review`

#### Scenario: Feedback produces no new commit
- **WHEN** a completed feedback attempt reuses the previous SHA or cannot prove a new committed head
- **THEN** the attempt fails closed and prior verification is not represented as satisfying the feedback

### Requirement: Regenerate complete evidence and independent reviews for every feedback head
For every new feedback head, the workflow MUST qualify fresh criterion-level evidence for the still-valid issue requirements, run deterministic verification on that exact committed head, and execute fresh requirements, code-quality, and architecture reviews in full against the same head. A head MUST receive `verified` and `awaiting-review` and lose `agent-running` only when its fresh evidence is sufficient, deterministic verification passes, every applicable fresh review passes, and GitHub still reports that head as current. No prior-head approval or evidence MAY be reused.

#### Scenario: Feedback head passes a complete new round
- **WHEN** the new head has sufficient newly produced evidence, passing deterministic verification, three fresh acceptable review verdicts, and remains current
- **THEN** the same pull request becomes verified for exactly that head and the feedback batch completes

#### Scenario: Previous head was verified
- **WHEN** the old head had passing evidence and three passing reviews but the new head lacks any fresh required result
- **THEN** the new head remains unverified and no old result is substituted for the missing head-bound result

### Requirement: Reconcile an explicit human merge to terminal completion
When the configured human merges the persistent run's associated pull request, the workflow MUST mark the existing run completed, preserve the pull request and head-bound history, and expose GitHub issue closure and LangGraph completion as the same terminal workflow outcome. A merge or close event for another pull request, a non-merged close, or non-human merger MUST NOT complete the run. Processing the merge event MUST NOT launch a new implementation candidate.

#### Scenario: Daniel merges the associated pull request
- **WHEN** a signed pull-request close delivery reports the persisted pull request as merged by the configured human and the linked issue is closed
- **THEN** workflow read-back reports the same run as completed with a human-merge terminal outcome and no further writer or review work

#### Scenario: Pull request closes without the authorized merge
- **WHEN** the pull request is merely closed, belongs to another run, or reports a bot or other user as merger
- **THEN** the workflow does not mark the run completed

### Requirement: Preserve the human-only delivery boundary through the public seam
The workflow MUST NOT invoke a merge, deployment, or release operation in any feedback or completion path and MUST NOT interpret pull-request activity as human approval. Acceptance verification MUST drive signed production-shaped webhook deliveries through `POST /webhooks/github`, use real SQLite and LangGraph persistence, and observe continuation through workflow-state `GET` read-back plus controlled writer, Git, reviewer, and GitHub effects.

#### Scenario: Signed system flow continues feedback and completes after merge
- **WHEN** the system suite submits an authorized feedback delivery, observes a new verified head, reconstructs the application, and submits the authorized human merge delivery
- **THEN** read-back preserves the run/worktree/PR identity, batch-local attempts, superseded prior-head records, fresh head-bound evidence and reviews, and terminal completion without any workflow merge, deploy, or release effect

#### Scenario: Signed system flow proves separate counters and invalidation
- **WHEN** system cases exercise an exhausted earlier repair batch and multiple human feedback batches
- **THEN** each feedback batch exposes an independent at-most-three counter and every new head exposes invalidated earlier qualification before fresh verification
