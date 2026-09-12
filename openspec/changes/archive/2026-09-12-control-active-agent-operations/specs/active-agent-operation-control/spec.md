## ADDED Requirements

### Requirement: Authorize and explicitly target active commands
The pilot SHALL accept queue, interrupt and cancel only from the current contributing human Control Lease holder with a command identity and current attempt/run-version/head/lease fences. Multiple active attempts SHALL be observable and an omitted, foreign or terminal target SHALL be rejected without adapter effects. Replay SHALL compare the redacted immutable command intent; conflicting reuse SHALL be rejected.

#### Scenario: Select one of two active attempts
- **WHEN** the holder submits an ambiguous command and then explicitly targets one of two active attempts
- **THEN** the first is rejected and only the selected attempt accepts the command; observers, non-holders and stale clients cannot mutate either attempt

### Requirement: Queue in durable acceptance order
Queue SHALL preserve all accepted commands with visible acceptance positions and deliver them serially after the current operation completes. An adapter receipt and stable delivery identity SHALL correlate each command with one subsequent agent response in the same Run History.

#### Scenario: Multiple commands wait behind a running operation
- **WHEN** two commands are accepted and the current operation completes
- **THEN** they execute once in acceptance order, each after the previous operation completes

### Requirement: Interrupt stops and reconciles before the next command
Interrupt SHALL durably fence and request stop of the addressed operation before delivering exactly one accepted interrupt command next. Delivery SHALL wait for an identity-bound stopped-process receipt and successful reconciliation of existing effects. Conflicting or unavailable reconciliation SHALL leave commands pending. Queued commands SHALL retain their relative order behind the interrupt; competing pending interrupts SHALL be rejected.

#### Scenario: Interrupt overtakes queued work safely
- **WHEN** an interrupt is accepted while queued commands wait
- **THEN** the addressed process stops, its fence advances, effects are reconciled, and the interrupt executes once before the FIFO queue

### Requirement: Cancel only the selected scope without repair consumption
Cancel SHALL require an explicit `operation` or `attempt` scope and a documented reason. Operation cancel SHALL stop only the selected operation; attempt cancel SHALL terminate the selected attempt and explicitly reject its pending commands. Neither cancel nor interrupt SHALL allocate a repair round or automatically retry cancelled work. Other attempts SHALL continue unchanged.

#### Scenario: Cancel one parallel attempt
- **WHEN** the holder cancels one attempt with pending commands
- **THEN** its process stops and its pending commands become visibly rejected, while the parallel attempt and repair accounting remain unchanged

### Requirement: Recover delivery and reject stale output
API or worker replacement between acceptance, dispatch, process stop and response persistence SHALL preserve command identity, order and logical exactly-once effects. Stop-before-start SHALL prevent a delayed start from resurrecting the fenced operation. Late output SHALL remain identifiable as history-only evidence and SHALL NOT update the head, active operation or canonical business state.

#### Scenario: Replacement adopts external success
- **WHEN** a worker dies after start or stop succeeded externally but before saving the receipt
- **THEN** replacement adopts the original receipt and performs only missing delivery work, with no duplicate process or message

#### Scenario: Fenced output arrives after replacement
- **WHEN** a delayed response from the old operation arrives after interrupt or cancel
- **THEN** history records its old operation and fence, while the active operation, head and business state are unchanged

### Requirement: Observe command and process lifecycle together
Public Operator HTTP/CLI read-back SHALL show each attempt, delivery mode, command acceptance/queue position, state, reason, process status, operation fence epoch and correlated agent response in the same Run History after host replacement. Messages, reasons and adapter receipts SHALL be redacted before persistence and read-back.

#### Scenario: Reconnect from a second operator
- **WHEN** an authorized reader reconnects after API replacement
- **THEN** the reader sees the same target identities, ordered commands, stop/reconciliation receipts and subsequent replies without original-worker access
