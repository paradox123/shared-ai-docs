# atomic-run-control-transfer Specification

## Purpose
Define durable voluntary control transfer and explicit forced takeover between
repository contributors, with atomic lease changes, old-controller fencing,
preserved workflow state and complete responsibility history.

## Requirements
### Requirement: Request and decide a durable Control Transfer
A read-authorized non-holder with current contributor permission SHALL request transfer without gaining writing rights. Only the current holder SHALL approve or reject the current request using explicit request/attempt/version/head/epoch fences. Approval SHALL revalidate the recipient's immutable provider identity and current contribution permission. Requests and decisions SHALL persist across API replacement; duplicate or stale decisions SHALL NOT transfer twice.

#### Scenario: Request then reject or approve
- **WHEN** a contributing observer requests control and the holder decides that request
- **THEN** request alone leaves the holder/epoch unchanged, rejection keeps that holder, and approval atomically installs the requesting human with one higher epoch

#### Scenario: Request recipient loses contribution
- **WHEN** the provider revokes the recipient's contribution before approval
- **THEN** approval fails closed and grants no lease

### Requirement: Force an explicit atomic takeover without administrator permission
Another current contributor SHALL perform an explicitly named Forced Takeover with a reason and current attempt/version/head/epoch fences, without holder approval or administrator permission. At least twenty concurrent attempts across independent API processes using one expected epoch SHALL produce exactly one accepted ownership change and no overlapping control rights.

#### Scenario: Contributors race for one epoch
- **WHEN** twenty contributors' takeover requests race with the same expected epoch
- **THEN** exactly one succeeds and one canonical forced ownership change advances that epoch once

### Requirement: Invalidate old controller work without changing the running workflow
An ownership change SHALL immediately invalidate old lease fences, outstanding mutating requests and pending old-controller commands, including writes from an already opened session. Adapter fencing SHALL prevent delayed dispatch after process loss. Already accepted external receipts SHALL be retained and reconciled without duplicate effects. The ownership change itself SHALL preserve workflow phase, Activity Attempt, current agent operation/session, head and accepted external effects. An already accepted continuation, repository recovery, or promoted current operation with an unsettled receipt SHALL return an explicit pending conflict until its existing decision settles; the pilot SHALL NOT orphan that decision to grant control.

#### Scenario: Former holder writes after takeover
- **WHEN** an old credential, refreshed credential for the old human, stale command or pending write attempts to mutate after transfer or forced takeover
- **THEN** no new adapter write/session/effect is accepted from that old lease, including after API restart

#### Scenario: Existing external write precedes ownership change
- **WHEN** a write succeeded externally before its local receipt was saved
- **THEN** recovery preserves that exact effect once; a later ownership change does not recreate or discard it

#### Scenario: Accepted decision is still settling
- **WHEN** an accepted continuation, repository recovery or promoted live delivery has not settled
- **THEN** transfer/takeover returns an explicit pending conflict with unchanged ownership and succeeds with fresh fences after that existing decision settles

### Requirement: Observe responsibility changes with complete audit context
Public HTTP/CLI and canonical Run History SHALL expose the transfer request/decision and the ownership change with old/new immutable human identity, run identity, timestamp, redacted reason and voluntary/forced mode. The former holder with continuing repository read permission SHALL remain an observer and retrieve that same history after reconnect.

#### Scenario: Former holder reconnects
- **WHEN** the old holder reconnects after API replacement
- **THEN** the changed holder, epoch and one explicit transfer event remain visible, and no credential or unredacted reason leaks
