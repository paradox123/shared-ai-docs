## MODIFIED Requirements

### Requirement: Execute direct evidence on the committed head
The worker SHALL execute every planned phase with explicit business assertions
after committing safe implementation changes. REST SHALL require request,
response and read-back; UI interaction, screenshot and read-back; idempotency
request, response, repeat and read-back; documents generate, render, inspect and
read-back. Each phase SHALL retain executable command, expected result, observed
result and head SHA. Operational logs, agent assertions and dashboards alone
SHALL NOT qualify. Missing phases or failed assertions SHALL enter bounded
capture recovery; head/worktree/branch drift SHALL block immediately. No incomplete
or stale evidence SHALL authorize push or PR creation.

#### Scenario: Evidence is incomplete or becomes stale
- **WHEN** a phase is missing, fails or changes the worktree/head/branch
- **THEN** the worker reports the missing or failed phase, attempts bounded recovery only on an unchanged head, and blocks publication if evidence remains incomplete or stale

#### Scenario: Completed result is externalized
- **WHEN** the accepted completed result exceeds the dossier inline limit
- **THEN** publication resolves its checksum-verified artifact before executing evidence; unavailable bytes never count as completion

## ADDED Requirements

### Requirement: Distinguish worker schema validity from evidence completeness
The pilot SHALL qualify the accepted original completed worker result against the
trusted plan, report schema validity separately from semantic completeness and
publish every missing criterion/phase pair. Rejected verdicts and log surrogates
SHALL NOT satisfy required phases. Original worker result, qualification and
capture results SHALL remain separate redacted observations correlated by run,
source attempt/session and capture head.

#### Scenario: Structurally valid result omits required phases
- **WHEN** a completed schema-valid result omits request, response, repeat, read-back or screenshot observations
- **THEN** public qualification names exactly those missing phases and retains the original result unchanged

### Requirement: Bound evidence correction and converge repository ownership
The pilot SHALL persist one committed head and branch before capture and run at
most two numbered deterministic capture activities. It SHALL NOT restart source
implementation, change branch or commit code during correction. Every activity
start and result SHALL survive replacement; an interrupted dispatch SHALL consume
its numbered round. Redelivery SHALL NOT reset the limit or revive an exhausted
run. Successful capture SHALL produce redacted head-bound evidence readable in
the draft PR and authenticated Operator surface. Exhaustion or drift SHALL end
in an explicit block with concrete reason and next action. Terminal dispositions
SHALL clear active run projections, resolve superseded native preparation Human
Requests and release repository serialization unless
an already dispatched external publication remains uncertain under existing policy.

#### Scenario: Missing evidence is captured successfully
- **WHEN** a numbered correction captures the trusted scenarios successfully
- **THEN** one draft and Operator history expose the same redacted evidence/head without another implementation or branch change

#### Scenario: Recovery is accepted against real GitHub
- **WHEN** Issue 12 is accepted using a controlled incomplete worker result
- **THEN** an isolated real GitHub repository proves authorized push, draft creation and adoption after interruption, head-bound redacted PR/Operator read-back, and successor publication after terminal capture exhaustion; a simulated provider alone does not complete acceptance

#### Scenario: Recovery limit is reached
- **WHEN** both capture rounds fail or are interrupted
- **THEN** the run is terminally blocked, no active agent projection remains, a successor can start, and repeating the command performs no more capture

#### Scenario: Replacement resumes an interrupted capture
- **WHEN** a worker dies after recording capture dispatch and a replacement runs
- **THEN** the interrupted round is preserved and counted, the same head is used, and at most the remaining round executes

#### Scenario: Capture mutates the repository
- **WHEN** a capture changes source, head or branch, even while failing its assertion
- **THEN** no further capture or publication occurs and the explicit terminal drift blocker releases pre-dispatch ownership

#### Scenario: Worker dies while a capture command is executing
- **WHEN** the delivery worker or adapter dies during an evidence command
- **THEN** independent process supervision stops its command group, records interruption on replacement and preserves the remaining capture bound

#### Scenario: Native preparation request is superseded
- **WHEN** completed native work reaches a terminal evidence/publication disposition
- **THEN** its earlier preparation Human Request is resolved in the same terminal transaction, with the original request retained in history
