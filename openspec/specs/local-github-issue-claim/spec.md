# local-github-issue-claim Specification

## Purpose

Define authenticated local GitHub delivery acceptance, durable idempotent issue claiming, persistent LangGraph execution, and workflow-state observation for the `probare-crm` pilot.

## Requirements

### Requirement: Authenticate and authorize local GitHub deliveries
The local workflow interface MUST accept only bounded requests using its configured authentication mode: either a valid GitHub `X-Hub-Signature-256` over the unchanged raw body or a valid internal `X-Pilot-Signature-256` over the delivery ID, event, and unchanged raw body. It MUST require a non-empty `X-GitHub-Delivery`, the configured repository, and an explicitly allowed event/action combination, and MUST verify the configured signature before parsing JSON. GitHub and internal relay secrets MUST be configured separately and an application instance MUST NOT accept both authentication modes simultaneously.

#### Scenario: Allowed directly signed delivery
- **WHEN** a correctly GitHub-signed `issues/labeled` delivery for the configured `probare-crm` repository arrives within the request-size limit in direct mode
- **THEN** the interface accepts the delivery for durable processing

#### Scenario: Allowed relay-signed delivery
- **WHEN** a correctly internally signed `issues/labeled` delivery with bound delivery ID and event for the configured `probare-crm` repository arrives within the request-size limit in relay mode
- **THEN** the same productive interface accepts the delivery for durable processing

#### Scenario: Invalid or unauthorized delivery
- **WHEN** a delivery has an invalid configured signature, exceeds the request-size limit, targets a non-allowed repository, or uses a non-allowed event/action combination
- **THEN** the interface rejects it without an inbox record, a workflow run, or a GitHub write

#### Scenario: Ambiguous authentication configuration
- **WHEN** an application instance is configured with both GitHub and internal relay secrets or with neither secret
- **THEN** application construction fails before serving requests

### Requirement: Persist acceptance before acknowledgement
The local workflow interface MUST atomically persist each accepted delivery under its `X-GitHub-Delivery` identity before sending a positive HTTP response. Persisted delivery data MUST exclude signatures, secrets, and fields not needed for workflow correlation.

#### Scenario: Newly accepted delivery is durable
- **WHEN** a valid allowed delivery is submitted
- **THEN** the positive response is sent only after its delivery identity, body digest, repository, issue, event, action, and acceptance time are committed to the local inbox

### Requirement: Claim one eligible issue as one persistent run
The dispatcher MUST create exactly one persistent LangGraph run for an open configured-repository issue that currently has `ready-for-agent`, has no open blockers, and does not conflict with another active run in that repository. The run MUST use its persisted run identity as the LangGraph thread identity and MUST project `agent-running` through the GitHub adapter.

#### Scenario: Eligible issue is claimed
- **WHEN** a newly accepted delivery identifies an open, unblocked issue whose current GitHub state includes `ready-for-agent` and the repository has no other active run
- **THEN** exactly one persistent run and checkpoint exist for the issue and GitHub visibly contains `agent-running`

#### Scenario: Ineligible issue is not claimed
- **WHEN** the issue is closed, lacks `ready-for-agent`, has an open blocker, or another issue already owns the repository's active run
- **THEN** the delivery remains accepted but no new run or GitHub claim is created

### Requirement: Deduplicate deliveries and claims
The workflow MUST use `X-GitHub-Delivery` as the end-to-end idempotency key. Repeating an accepted delivery with the same body MUST be successful without dispatching, creating another run, or issuing another GitHub claim; reusing the delivery ID with a different body MUST be rejected as a conflict.

#### Scenario: Identical delivery is repeated
- **WHEN** the same signed body is delivered again with the same `X-GitHub-Delivery`
- **THEN** the interface reports it as already accepted and the existing delivery, run, checkpoint, and GitHub claim counts remain unchanged

#### Scenario: Delivery identity is reused for different content
- **WHEN** a different signed body is submitted with an already persisted `X-GitHub-Delivery`
- **THEN** the interface rejects the conflict without changing workflow or GitHub state

### Requirement: Expose durable workflow state across restart
The productive workflow interface MUST expose the accepted delivery, run identity and status, claim projection, and latest LangGraph checkpoint values for a repository issue. Reconstructing the application over the same database MUST expose the same state without creating a new run or claim.

#### Scenario: Claimed state survives process restart
- **WHEN** the application is closed after a successful claim and recreated against the same database
- **THEN** workflow-state lookup returns the original delivery, run identity, `agent-running` projection, and persisted checkpoint state

### Requirement: Verify behavior at stable system boundaries
Acceptance verification MUST drive the same HTTP workflow interface used in production, use real SQLite inbox and LangGraph checkpoint persistence, and control only GitHub, clock, and delivery inputs at external seams. Tests MUST NOT assert private node ordering, helper calls, raw database rows, or checkpoint implementation tables.

#### Scenario: Behavior test observes public outcomes
- **WHEN** acceptance, rejection, idempotency, and restart behavior are tested
- **THEN** assertions use HTTP responses, workflow-state lookup, and controlled GitHub effects as the observable results
