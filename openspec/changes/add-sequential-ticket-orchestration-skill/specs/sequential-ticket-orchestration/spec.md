## ADDED Requirements

### Requirement: Finite sequential batch
The skill SHALL resolve and freeze a user-selected batch, use one dedicated Codex task per ticket and avoid implementing product changes in the coordinator. User invocation for batch execution SHALL select the documented implementation-to-merge workflow subject to actual runtime permissions.

#### Scenario: Minimal invocation
- **WHEN** the user supplies only the skill and a repository ticket range
- **THEN** the coordinator resolves the project, dependencies and target branch and dispatches only the first eligible ticket using implement and repository OpenSpec policy

### Requirement: Confirmed identity and recovery
The coordinator SHALL distinguish client IDs from confirmed task IDs, persist dispatch intent and verify candidates through task tools before adopting them. Missing listings SHALL NOT establish task absence.

#### Scenario: Missing listing
- **WHEN** asynchronous creation returns a client ID and listing omits the worker
- **THEN** bounded exact-title local metadata recovery yields candidates for direct verification without creating a replacement or requiring a pasted user link as the first fallback

#### Scenario: Ambiguous or malformed metadata
- **WHEN** the metadata helper encounters multiple exact-title IDs or malformed metadata
- **THEN** it returns a bounded ambiguous/error result rather than a silently selected identity or false empty success

### Requirement: Evidence-bound acceptance
The coordinator SHALL request a separate critical verification and inspect actual screenshots or readable measured results against acceptance criteria for the identified implementation state. Prototypes SHALL provide visual inspiration only.

#### Scenario: Green test counts without adequate proof
- **WHEN** the worker reports passing tests but supplies no inspectable behavioral evidence
- **THEN** the coordinator requests missing evidence and withholds acceptance

### Requirement: Verified delivery and authorization
The coordinator SHALL advance only after verifying remote merge, included accepted contents and ticket closure. A runtime approval denial SHALL be reported accurately without routing around it.

#### Scenario: Delegated approval rejected
- **WHEN** automatic review rejects the merge because direct user authority is missing
- **THEN** the batch preserves the open PR and asks for the exact required approval without starting the next ticket or retrying through another identity

### Requirement: Durable continuation
The coordinator SHALL checkpoint phase, identity, cursor, pending actions and next action and reconcile fresh state on resume. Completed transitions SHALL be handled in the same active run when possible.

#### Scenario: Resume after uncertain creation
- **WHEN** a checkpoint records pending task creation without a confirmed response
- **THEN** the coordinator searches for that existing dispatch before considering any new creation

#### Scenario: Merge completes during a wait
- **WHEN** a worker finishes delivery while the coordinator is actively waiting
- **THEN** it verifies delivery and starts the next eligible ticket without intentionally deferring the transition to the next heartbeat
