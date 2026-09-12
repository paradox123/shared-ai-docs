## ADDED Requirements

### Requirement: Persist a complete targeted Human Request before continuation
The pilot SHALL persist a redacted Human Request before waiting for a human
decision. The request SHALL bind immutable run, activity, attempt and session
identities; current phase; expected head SHA; concrete problem; evidence; allowed
actions; a redacted opening capability; and the current Control Lease context. A
read-authorized Operator Client SHALL retrieve the request through public
run/attempt read-back and CLI without worker, database, or original-machine
access. API and worker replacement SHALL preserve the request, its target, and
the canonical event prefix.

#### Scenario: Second operator reads a blocked request after replacement
- **WHEN** a fake attempt persists a blocked result, the API and worker are replaced, and a second read-authorized operator selects that attempt
- **THEN** the same Run, Attempt, Session, phase, expected head, problem, evidence, allowed actions and current lease context are readable in the same Run History

### Requirement: Continue a request through an explicit durable decision
An authorized Control Lease holder SHALL resolve an open Human Request only with
an explicit target request ID, target attempt, expected run version, expected
head SHA, lease epoch and idempotency command ID. `Resume` SHALL retain the
same session ID. `Fork` SHALL create a distinct session and record its direct
parent session ID. `Fresh Retry` SHALL create a distinct session with no parent
or automatically imported transcript. Every adapter completion receipt SHALL
declare `AgentSessionAdapter/v1` and echo the durably assigned operation
identity; a write receipt SHALL also echo the action's redacted canonical
message. Every new-session decision SHALL reject a receipt that reuses its
source session identity. Each accepted decision SHALL
preserve the old attempt/history and become observable in the same run.

#### Scenario: Holder chooses each continuation mode
- **WHEN** the current lease holder submits a fenced Resume, Fork, or Fresh Retry decision for an open request
- **THEN** public read-back shows respectively the original session, a distinct session with explicit origin, or a distinct session without origin/import while retaining the original attempt and history

### Requirement: Open only the selected session with truthful capability and explicit handoff
`Open in Codex` SHALL resolve only the selected persisted attempt/session. A
same-session-supported adapter SHALL open that exact session without changing
workflow phase, expected head, external effects, or session identity. If direct
display is not safely supported, the Operator surface SHALL disclose the reason
and SHALL create no fork until the current lease holder submits a separately
fenced, explicitly confirmed Handoff decision. A Handoff SHALL create one new
session marked with its source session and Handoff origin. A read-authorized
human's provider revalidation and durable open intent SHALL be one serialized
decision, and an open receipt SHALL echo that intent's operation identity.

#### Scenario: Unsupported direct display requires confirmation
- **WHEN** an operator opens an attempt whose adapter reports handoff-confirmation-required
- **THEN** the response names the limitation and source session, creates no new session or uncorrelated run, and only a later valid confirmed Handoff creates one lineage-marked session

### Requirement: Fence all writing interaction in an opened session
An interactive message, tool action, result, or decision directed to an opened session SHALL require current contributor authorization, the current run-wide Control Lease, a current request/attempt/run-version/head/epoch fence and an idempotency command ID. The pilot SHALL redact and append its observable
message, tool, result and decision records to the same Run History. Command
idempotency SHALL compare the redacted canonical message and retain the
associated redaction metadata. Observers,
non-holders, stale clients, duplicated commands and incorrectly addressed
requests SHALL produce no adapter write, new session, external effect, or
canonical business event.

#### Scenario: Only the current holder writes once
- **WHEN** a lease holder submits a current interactive write and a non-holder, stale client, and duplicate command submit competing writes
- **THEN** exactly one correlated adapter write and one redacted interaction history sequence exist for the original run and selected session

### Requirement: Recover continuation operations logically exactly once
The pilot SHALL persist a stable continuation or interaction operation identity
before calling the adapter and SHALL retain a redacted, independently readable
receipt. After process failure or restart, replacement processing SHALL adopt the
matching operation/receipt and execute only missing work. A repeated decision
command SHALL return the original logical result; conflicting reuse of its
command ID SHALL be rejected without an adapter or workflow effect.

#### Scenario: Replacement adopts a continuation success gap
- **WHEN** the adapter creates a continuation session or accepts a write and the worker exits before its local completion is persisted
- **THEN** replacement processing exposes the original operation and receipt, retains one logical continuation/write, and creates no second session or message
