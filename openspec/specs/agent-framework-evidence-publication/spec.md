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
SHALL NOT qualify. Missing phases, failed assertions or head/worktree drift SHALL
block publication with a terminal public disposition.

#### Scenario: Evidence is incomplete or becomes stale
- **WHEN** a phase is missing, fails or changes the worktree/head
- **THEN** no push or PR create occurs and the run exposes evidence rejection

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
