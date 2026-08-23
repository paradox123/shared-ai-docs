# workflow-crash-recovery Specification

## Purpose
TBD - created by archiving change resume-interrupted-workflows. Update Purpose after archive.
## Requirements
### Requirement: Recover active workflows automatically from durable state
The pilot MUST recover every non-terminal run during application startup from the same SQLite database and LangGraph thread before accepting new deliveries. Recovery MUST preserve the existing delivery, run, issue, worktree, branch, pull request, head, worker, review, repair, feedback, and checkpoint correlations and MUST NOT create a second run or worktree.

#### Scenario: Process exits during an active workflow
- **WHEN** the pilot process terminates after an active transition has durable state and is restarted with the same database and configured boundaries
- **THEN** startup continues the existing run from its last recoverable transition and workflow read-back exposes the same ownership identities

#### Scenario: Recovery is invoked repeatedly
- **WHEN** startup recovery or an equivalent supervisor call is repeated for the same active state
- **THEN** it converges on the same workflow status without creating another run, worktree, branch, batch, attempt, or checkpoint thread

### Requirement: Make external transitions idempotent across uncertain crash boundaries
Every claim, implementation, draft-publication, review, repair, and human-feedback external transition MUST have a stable durable operation identity. A transition with a durably completed result MUST NOT execute externally again. A transition whose effect is uncertain after a crash MUST reconcile deterministic worktree, Git, GitHub, head, and label state and MAY retry an opaque worker only under the same operation, batch, and round identity.

#### Scenario: Crash follows an external effect but precedes the next checkpoint
- **WHEN** an external claim, worker result, push, draft PR update, review result, repair result, feedback result, or label projection completed durably before the process terminated but LangGraph had not written its next checkpoint
- **THEN** recovery reuses that result and does not execute the completed external transition again

#### Scenario: Crash leaves an opaque worker outcome uncertain
- **WHEN** the process terminates while a worker invocation has a durable operation identity but no durable valid result
- **THEN** recovery continues that same operation in the same worktree and round without allocating a second workflow identity or publishing duplicate work

### Requirement: Resume every supported workflow phase without duplicate publication
Recovery MUST handle interruption during claim, initial implementation, draft PR creation or update, independent review, bounded repair, and human-feedback waiting or execution. At most one draft pull request MAY exist for the run branch, and every resumed review or repair MUST remain bound to the current persisted pull-request head.

#### Scenario: Restart occurs during publication or review
- **WHEN** the process terminates while publishing the initial or repaired head or while one or more review axes are incomplete
- **THEN** recovery reuses the run branch and existing draft PR, completes only missing head-bound work, and exposes one review result per axis for that batch

#### Scenario: Restart occurs during repair or feedback
- **WHEN** the process terminates during a numbered repair or human-feedback attempt
- **THEN** recovery retains the batch-local round count and findings, completes or resumes that round, and never starts a fourth attempt or a second feedback batch for the same delivery

#### Scenario: Workflow is waiting for human feedback or merge
- **WHEN** a published run has no incomplete machine transition and is waiting for a new human event
- **THEN** restart preserves the waiting state and does not invoke a worker, reviewer, source publication, or GitHub projection

### Requirement: Preserve terminal human completion across restart
A run completed by the configured human merging its associated pull request MUST remain terminal. Recovery MUST prioritize the durable completion over incomplete older phase records and MUST NOT reactivate implementation, review, repair, feedback, publication, or repository scheduling for that run.

#### Scenario: Restart follows human merge completion
- **WHEN** the process restarts after the associated pull request and issue were durably reconciled as human merged and completed
- **THEN** read-back reports the same terminal run and no external workflow effect is executed

### Requirement: Expose bounded redacted recovery observability
Workflow-state read-back MUST expose the recovery status and ordered events with run, phase, stable operation key, outcome code, and timestamp. Recovery checkpoints and diagnostics MUST NOT contain secrets, tokens, authorization values, email addresses, webhook bodies, arbitrary exception text, source payloads, or duplicated human-feedback content.

#### Scenario: Recovery completes after restart
- **WHEN** startup reconciles an interrupted active run
- **THEN** `GET /workflows/{owner}/{repository}/issues/{issue_number}` exposes a completed recovery record with bounded phase events and preserved correlations

#### Scenario: Sensitive values are present at configured boundaries
- **WHEN** configured secrets or personal data appear in worker, webhook, or external error material during recovery
- **THEN** neither recovery storage, LangGraph checkpoint values, nor workflow read-back contains those values

### Requirement: Verify recovery through the productive process and HTTP seam
Acceptance verification MUST terminate a real pilot process during representative active phases, restart a new process against the same SQLite database, and use signed `POST /webhooks/github` plus `GET /workflows/{owner}/{repository}/issues/{issue_number}` read-back to prove convergence. Verification MUST observe controlled worker, worktree, Git, reviewer, and GitHub effects and MUST NOT rely only on raw database queries or logs.

#### Scenario: End-to-end crash and restart converges
- **WHEN** a signed delivery starts a workflow, the serving process is forcibly terminated at a controlled phase boundary, and a new serving process starts on the same persistent files
- **THEN** HTTP read-back eventually reports the continued or terminal state with one run, worktree, branch, pull request, current head, and bounded batch identities while controlled boundaries show no completed effect was duplicated
