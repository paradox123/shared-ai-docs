# agent-framework-evidence-publication Specification

## Purpose
Require executable readiness and commit-bound, redacted business evidence before
publishing a draft PR, and reconcile repeated publication without duplicate PRs.
## Requirements
### Requirement: Bind and execute readiness before agent work
The pilot SHALL bind an immutable trusted evidence plan to the admitted repository
and issue before starting Codex. Every criterion SHALL declare kind, required
phases, executable surface and expected business read-back. Readiness SHALL check
local/remote/provider base, contracts, tools, dependencies, access, sandbox and
each required evidence surface. A failed or missing check SHALL expose a concrete
blocker and SHALL NOT start an agent.

#### Scenario: Required surface or prerequisite is unavailable
- **WHEN** a surface, dependency, sandbox permission or contract probe fails
- **THEN** the public run exposes the failed prerequisite and no agent session exists

#### Scenario: Immutable plan or repository differs
- **WHEN** a repeated worker command changes its plan or targets a different admitted repository
- **THEN** it is rejected without agent or publication effects

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

### Requirement: Publish and adopt one exact draft
The pilot SHALL persist publication intent before push or PR create. It SHALL
push only the explicit run branch and publish exactly one draft PR for the
admitted issue, base and committed head. Redelivery SHALL read provider state and
adopt the matching draft without creating a duplicate. Missing evidence of an
already dispatched create, conflicting head/body/base, ambiguity or a non-draft
SHALL block further writes. No command SHALL merge or mark ready.

#### Scenario: Worker loses a successful create response
- **WHEN** a replacement repeats publication after provider success
- **THEN** the same PR is adopted and provider read-back exposes exactly one draft

#### Scenario: Dispatched creation has no authoritative receipt
- **WHEN** reconciliation cannot find a unique matching draft
- **THEN** the run reports uncertainty and performs no second create

### Requirement: Publish redacted authoritative evidence
The PR body SHALL map every criterion to direct phase observations and exact head
SHA. It SHALL embed compact request/response/repeat/read-back or document phases
and decisive screenshot references. All persisted/published observations SHALL
be redacted first; sensitive outgoing source SHALL be rejected. The authenticated
Operator projection/history SHALL retain the same publication identity and
evidence after API/worker replacement. Provider PR read-back SHALL verify the
body, draft, branch, base and head; logs alone SHALL NOT establish acceptance.

#### Scenario: Sensitive output and repeated public read
- **WHEN** executable evidence contains configured secrets and the worker/API restart
- **THEN** provider body and Operator evidence retain redacted business observations at the same head

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
