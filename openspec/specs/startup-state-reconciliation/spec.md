# startup-state-reconciliation Specification

## Purpose
TBD - created by archiving change reconcile-after-mac-absence. Update Purpose after archive.
## Requirements
### Requirement: Track durable liveness and operating-system boot identity
The pilot MUST durably store `last_alive_at` and MUST obtain a stable operating-system boot-session ID that remains unchanged across process restarts in the same Mac boot and changes after a Mac reboot. Startup MUST atomically evaluate the prior liveness value against the current boot before advancing it. A missing prior value or a clock value earlier than `last_alive_at` MUST NOT qualify as a 24-hour absence.

#### Scenario: Process restarts in the same boot
- **WHEN** the pilot starts more than once with the same boot-session ID
- **THEN** every start observes the same boot evaluation and no start is treated as a new Mac boot

#### Scenario: First recorded start
- **WHEN** no durable `last_alive_at` exists
- **THEN** the pilot records current liveness and the boot evaluation without starting reconciliation

#### Scenario: Running process remains alive
- **WHEN** the pilot continues operating without GitHub traffic
- **THEN** a local heartbeat advances `last_alive_at` without polling GitHub

### Requirement: Run reconciliation once after the 24-hour boundary
On the first pilot start of a new boot, the pilot MUST start exactly one durable reconciliation run when the interval since the prior `last_alive_at` is greater than or equal to 24 hours and MUST start none when it is shorter. Later process starts in the same boot MUST NOT allocate or start another reconciliation run. An interrupted run MUST resume under the same boot/run identity.

#### Scenario: Absence is exactly 24 hours
- **WHEN** a new boot starts exactly 24 hours after the prior durable liveness timestamp
- **THEN** one reconciliation run is durably started for that boot

#### Scenario: Absence is shorter than 24 hours
- **WHEN** a new boot starts less than 24 hours after the prior durable liveness timestamp
- **THEN** the boot is durably recorded as not requiring reconciliation and later process restarts in that boot do not reconsider it

#### Scenario: Qualifying boot has multiple process starts
- **WHEN** reconciliation completed or was interrupted and the pilot process starts again with the same boot-session ID
- **THEN** it reuses the existing boot record, resumes it only if incomplete, and never allocates a second reconciliation run

### Requirement: Convert current GitHub state into ordinary inbox commands
A qualifying reconciliation MUST read current ready or otherwise authorized open issues and current pull-request state for the persisted active run through the configured repository adapter. It MUST convert only unobserved readiness and human-merge facts into deterministic synthetic commands and accept them through the same durable inbox and workflow dispatch path used by webhook deliveries. Active pull-request completion MUST be reconciled before ready-issue scheduling.

#### Scenario: Ready work was missed while offline
- **WHEN** GitHub currently contains an authorized unblocked ready issue for which the local workflow has not observed the readiness fact
- **THEN** reconciliation persists one synthetic readiness command and ordinary dispatch selects or durably queues that issue under the existing repository policy

#### Scenario: Active pull request was merged while offline
- **WHEN** the persisted active run's associated pull request is currently human-merged at the persisted head and its issue is closed
- **THEN** reconciliation persists one synthetic human-merge command and the ordinary workflow completion path terminates that same run

#### Scenario: No transition is missing
- **WHEN** every current readiness and active pull-request fact already has a semantic inbox command
- **THEN** reconciliation records the facts as deduplicated and executes no workflow effect for them

### Requirement: Deduplicate reconciliation and delayed Queue delivery by domain fact
The inbox MUST preserve each real GitHub delivery receipt and its `X-GitHub-Delivery` conflict rules while separately enforcing one semantic command for each deterministic domain fact. A synthetic command and a delayed Queue delivery representing the same fact MUST produce exactly one workflow effect regardless of arrival order. The delayed transport delivery MUST receive a durable already-accepted acknowledgement when its semantic command already exists.

#### Scenario: Reconciliation arrives before Queue delivery
- **WHEN** reconciliation accepts and dispatches a domain fact before a delayed Queue delivery for that same fact reaches the receiver
- **THEN** the receiver durably records or correlates the transport receipt, acknowledges it as already accepted, and does not dispatch the fact again

#### Scenario: Queue delivery arrives before reconciliation
- **WHEN** the receiver has already accepted and dispatched a Queue delivery before reconciliation discovers the same domain fact
- **THEN** reconciliation recognizes the existing semantic command and does not dispatch the fact again

#### Scenario: Delivery ID is reused with different content
- **WHEN** a real `X-GitHub-Delivery` already exists with a different body digest
- **THEN** the receiver still rejects the transport conflict even if either body maps to a known semantic command

### Requirement: Return to event-driven operation with bounded observability
After startup reconciliation completes, the pilot MUST perform no periodic GitHub reconciliation or polling. Existing workflow-state read-back MUST expose the latest boot reconciliation identity, threshold outcome, status, bounded timestamps and counts, without webhook bodies, issue/PR bodies, feedback, secrets, tokens, email addresses, or arbitrary external exception text.

#### Scenario: Startup reconciliation completes
- **WHEN** a qualifying reconciliation has processed its current-state snapshot
- **THEN** workflow read-back reports that boot's completed bounded summary and no timer schedules another GitHub read

#### Scenario: Normal operation continues
- **WHEN** the completed pilot remains running or the process restarts within the same boot
- **THEN** only incoming deliveries and existing workflow recovery can cause GitHub workflow work

### Requirement: Verify absence reconciliation through stable productive seams
Acceptance verification MUST use a controlled clock, controlled boot-session provider, controlled GitHub adapter, real SQLite persistence, application lifespan restarts, signed HTTP deliveries, and workflow GET read-back. It MUST prove the exact threshold, below-threshold behavior, once-per-boot behavior, interrupted-run reuse, current-state recovery, and both Queue/reconciliation arrival orders without asserting private helpers or raw database rows.

#### Scenario: Behavior suite exercises persisted startup boundaries
- **WHEN** the application is reconstructed across controlled boot IDs and times on the same database
- **THEN** public read-back and controlled external effects prove one qualifying run, no below-threshold run, same-boot reuse, and no duplicate workflow effect in either race order
