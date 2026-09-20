## ADDED Requirements

### Requirement: Finite batch with explicit target
The skill SHALL freeze a user-selected finite batch, use dedicated implementation tasks and keep product implementation out of the coordinator. It SHALL require an explicit user target branch before dispatch and SHALL NOT infer main, the default branch or current checkout. Batch execution SHALL include documented delivery and owned-resource cleanup subject to actual permissions and narrower user scope.

#### Scenario: Missing target
- **WHEN** the user supplies the skill and ticket range without a target
- **THEN** the coordinator asks for that required input and may perform read-only preparation, but creates no worker until it is supplied

#### Scenario: Non-default target
- **WHEN** the user names an existing release branch
- **THEN** workers start from and deliver to that branch, and delivered issues are explicitly closed if automatic closure did not run

### Requirement: Bounded independent parallelism
The coordinator SHALL allow up to three in-flight tickets by default with a positive user override. Pending registration and candidates awaiting integration SHALL count. Functional dependencies and foreseeable file/interface or mutable-resource conflicts SHALL prevent simultaneous work. Confirmed delivery SHALL unlock dependents independently of cleanup. Blockers SHALL affect only their dependency/conflict scope unless demonstrably batch-wide.

#### Scenario: Refill while another worker runs
- **WHEN** one of three workers is delivered and another independent eligible ticket exists
- **THEN** the coordinator dispatches it without waiting for the remaining workers or the next heartbeat

#### Scenario: Unresolved creation and overlapping tickets
- **WHEN** a creation is unresolved or an undelivered ticket overlaps a queued ticket
- **THEN** the unresolved creation retains its slot and the overlapping ticket waits, while unrelated eligible tickets may use remaining slots

#### Scenario: Blocked worker
- **WHEN** a worker has an external blocker
- **THEN** it releases its slot only after verified quiescence, keeps its conflict/dependency reservations, and needs a free slot to resume

### Requirement: Isolated implementation
Every new implementation task SHALL use a dedicated worktree and owned branch based on the user target. Workers SHALL verify the fresh remote base and isolate mutable test resources. Unexpected overlap SHALL cause safe checkpointing and serialization without discarding work.

#### Scenario: Two independent implementations
- **WHEN** two independent tickets are dispatched
- **THEN** their worktrees and working branches are distinct and shared mutable ports/databases/output resources are isolated or explicitly serialized

### Requirement: Confirmed identity and recovery
The coordinator SHALL distinguish provisional client IDs from real task IDs, persist dispatch intent and directly verify candidates. Missing listings SHALL NOT establish absence. Recovery SHALL remain bounded and read-only until identity is confirmed.

#### Scenario: Missing listing
- **WHEN** asynchronous creation returns a client ID and listing omits the worker
- **THEN** exact-title metadata recovery supplies candidates for direct verification without creating a replacement or requiring a pasted link as first fallback

#### Scenario: Ambiguous or malformed metadata
- **WHEN** the helper encounters multiple exact-title IDs or malformed metadata
- **THEN** it returns a bounded ambiguous/error result rather than a selected identity or false empty success

### Requirement: Evidence-bound acceptance
The coordinator SHALL request separate critical verification and inspect actual screenshots or readable measured outcomes against ticket criteria. Prototypes SHALL provide visual inspiration only. Acceptance SHALL identify contents and the target revision used for integration verification.

#### Scenario: Green counts without behavioral proof
- **WHEN** a worker supplies only passing test counts
- **THEN** the coordinator requests inspectable evidence and withholds acceptance

### Requirement: Serialized verified integration
Only one worker SHALL hold the target integration reservation. Acceptance/preparation SHALL be separate from a specific final merge grant. A changed head or target SHALL trigger relevant revalidation; substantive candidate changes SHALL require renewed acceptance. Remote merge, accepted-content inclusion and ticket closure SHALL be verified. Runtime approval denials SHALL NOT be bypassed.

#### Scenario: Target advances after acceptance
- **WHEN** a different ticket or external writer advances the target before merge
- **THEN** the holder revalidates against the current target and obtains a matching grant before merging; combined behavior is verified if an external change races with the merge

#### Scenario: Delegated approval rejected
- **WHEN** automatic review requires direct user authority for a merge
- **THEN** the coordinator preserves the PR, requests the concrete required approval, holds dependent integration and permits unrelated authorized work without retrying through another identity; a ticket-specific holder may release integration only after acknowledged grant cancellation, verified quiescence and reconciliation of any uncertain mutation

### Requirement: Durable continuation
The coordinator SHALL checkpoint every ticket's phase, identity, cursor, evidence, pending operation and next action plus slot and integration reservations. Resume SHALL reconcile workers, remote state and owned worktrees before mutations. Completed transitions SHALL be processed during the same active run when possible.

#### Scenario: Interrupted create or merge
- **WHEN** a checkpoint has an unresolved creation or merge
- **THEN** the coordinator reconciles that operation before retrying or releasing its reservation

#### Scenario: Older ledger adoption
- **WHEN** a sequential ledger is adopted
- **THEN** its known IDs, authority, evidence and pending operations are preserved as per-ticket records, without assuming cleanup or inferring an absent user target

### Requirement: Evidence preservation and guarded cleanup
After verified delivery the coordinator SHALL preserve inspectable evidence outside worker worktrees, verify idle workers and exact ownership, and remove only integrated owned worktrees/working branches before archiving worker tasks. Target/protected/foreign refs and unintegrated changes SHALL be preserved. Cleanup SHALL be checkpointed and idempotently reconciled; failures SHALL remain explicit unfinished work without undoing confirmed delivery.

#### Scenario: Cleanup after squash
- **WHEN** a PR was squash-merged and the worktree is clean
- **THEN** retained evidence is verified and PR-head-to-merge mapping plus unchanged owned heads establishes safe conditional cleanup; ancestry failure alone neither proves unmerged work nor permits blind force deletion

#### Scenario: New work or missing evidence
- **WHEN** an owned branch gained unintegrated commits or evidence still exists only in the worktree
- **THEN** deletion waits until the work is preserved/reconciled and evidence is durably verified; unrelated eligible batch work continues

#### Scenario: Interrupted cleanup
- **WHEN** the worktree was removed but archival was interrupted
- **THEN** the coordinator verifies completed cleanup items and resumes remaining ones without recreating resources or repeating unchecked deletions

### Requirement: Review after critical verification
Workers SHALL implement and establish behavioral evidence before a separate critical verification. The worker SHALL use change-accepted for technical completion and code-review for structural review after that verification and its repairs; orchestration SHALL reference their contracts rather than redefine the review method. Local checkpoint commits on the owned working branch SHALL be allowed before acceptance; push, merge, closure and archive gates SHALL remain unchanged. Review records SHALL identify reviewer, axis, base, reviewed contents, covered requirements, findings and outcome.

#### Scenario: Critical verification repairs behavior
- **WHEN** critical verification finds a defect before final review
- **THEN** the worker repairs it and refreshes affected evidence before invoking code-review for structural review

#### Scenario: Repair after review
- **WHEN** a review finding is repaired
- **THEN** the same reviewer checks the delta and affected behavior, retaining earlier coverage; a full repeat requires a recorded reason such as changed requirements, a broad behavioral change or an unusable review baseline

### Requirement: Compact coordination and context
The skill SHALL use bounded context packets for workers and independent reviewers, with explicit fresh context for subagents. It SHALL define a role profile of Sol/medium for coordination and routine structural review, Astra/high for implementation and critical requirements verification, with focused escalation of difficult structural findings, subject to explicit user model choices and actual runtime support. It SHALL NOT silently change global model defaults or claim that text instructions switched a running coordinator's model. Unchanged observations SHALL NOT trigger extra detail reads, filesystem probes or follow-up prompts; recovery and required pre-mutation checks remain mandatory.

#### Scenario: Unchanged worker snapshot
- **WHEN** only a wait cursor or observation timestamp changes
- **THEN** the coordinator saves the cursor and continues a bounded wait without redundant messages or file reads

#### Scenario: Scoped reviewer context
- **WHEN** a reviewer is launched
- **THEN** it receives the fixed base/head, relevant requirements and standards, file scope and review brief without the full batch conversation or the other reviewer's conclusions

### Requirement: Local mechanical helpers
The skill SHALL provide standard-library CLI helpers for atomic revision-checked JSON ledger updates, compact observation comparison, recorded identity comparison, explicit file manifests and verified evidence retention. Helpers SHALL NOT execute task APIs, Git mutations, scheduling, acceptance or cleanup. They SHALL preserve unknown ledger fields, reject stale writes and invalid inputs without replacing the ledger, and retain uncertain actions for coordinator reconciliation. Existing batches SHALL be adopted explicitly rather than silently rewritten.

#### Scenario: Stale ledger writer
- **WHEN** a checkpoint uses an outdated revision
- **THEN** the helper reports blocked and leaves the current ledger unchanged

#### Scenario: Identity mismatch
- **WHEN** an observed task, worktree, branch or target differs from the recorded assignment
- **THEN** comparison reports divergence without rebinding ownership or authorizing an action

#### Scenario: Changed manifest or unsafe retention
- **WHEN** evidence differs from its recorded manifest, a path escapes its root, or a retention destination contains different content
- **THEN** the helper reports the problem without overwriting existing evidence or reporting successful preservation

### Requirement: Consolidated closeout and stable verification
Ticket delivery and merge evidence SHALL be recorded in the ledger immediately. Pure status and archival documentation SHALL be consolidated into at most one batch closeout change when repository policy permits. Required per-ticket operational activation evidence and pre-merge specification validation SHALL remain per ticket. Workers SHALL establish representative fixtures early, run focused checks during repairs and run the relevant full suite after the last behavioral repair, while retaining required CI checks.

#### Scenario: Six ticket deliveries
- **WHEN** six tickets have been merged and only status/archival bookkeeping remains
- **THEN** their merge facts remain individually recorded and one closeout change collects the versioned bookkeeping, instead of six routine follow-up PRs

#### Scenario: Activation and final repair
- **WHEN** a ticket includes productive activation or a final behavioral repair
- **THEN** its own activation proof remains required and the final suite covers the repaired contents before delivery; a changed target triggers relevant integration checks
