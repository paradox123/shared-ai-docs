## MODIFIED Requirements

### Requirement: Authenticate and authorize local GitHub deliveries
The local workflow interface MUST accept only bounded requests with a valid `X-Hub-Signature-256`, a non-empty `X-GitHub-Delivery`, a registered version-compatible `RepositoryAdapter`, and an event/action combination allowed by that adapter. It MUST verify the signature over the unchanged raw body before parsing JSON.

#### Scenario: Allowed signed delivery
- **WHEN** a correctly signed delivery uses an event/action allowed by the registered repository adapter and stays within the request-size limit
- **THEN** the interface accepts the delivery for durable repository scheduling

#### Scenario: Invalid or unauthorized delivery
- **WHEN** a delivery has an invalid signature, exceeds the request-size limit, targets an unregistered repository, uses an adapter-incompatible contract version, or uses a non-allowed event/action combination
- **THEN** the interface rejects it without an inbox record, a workflow run, or a GitHub write

### Requirement: Claim one eligible issue as one persistent run
The dispatcher MUST create exactly one persistent LangGraph run for the first open, authorized, unblocked candidate in the registered adapter's deterministic repository frontier when no other active run exists. The run MUST use its persisted run identity as the LangGraph thread identity and MUST project the adapter's running label through that same adapter.

#### Scenario: Eligible issue is claimed
- **WHEN** a newly accepted delivery wakes a repository whose deterministic frontier contains an open, authorized, unblocked issue and no other active run
- **THEN** exactly one persistent run and checkpoint exist for the first candidate and the adapter visibly contains its running projection

#### Scenario: Ineligible issue is not claimed
- **WHEN** an issue is closed, unauthorized, interrupted, blocked, or another issue already owns the repository's active run
- **THEN** the delivery and disposition remain durable but no new run or running projection is created for that issue

### Requirement: Expose durable workflow state across restart
The productive workflow interface MUST expose the accepted delivery correlation, durable disposition and reason, run identity and status, adapter projection, and latest LangGraph checkpoint values for a repository issue. Reconstructing the application over the same database MUST expose the same state without creating a new run or projection.

#### Scenario: Claimed state survives process restart
- **WHEN** the application is closed after a successful claim and recreated against the same database
- **THEN** workflow-state lookup returns the original delivery correlation, selected disposition, run identity, running projection, and persisted checkpoint state

#### Scenario: Unselected state survives process restart
- **WHEN** the application is closed after an issue is queued or interrupted and recreated against the same database
- **THEN** workflow-state lookup returns the original durable disposition and reason without a run, checkpoint, or new GitHub projection

### Requirement: Verify behavior at stable system boundaries
Acceptance verification MUST drive the same HTTP workflow interface used in production, use real SQLite inbox, disposition, and LangGraph checkpoint persistence, and control only repository adapters, clock, and delivery inputs at external seams. A shared adapter contract MUST cover `probare-crm` plus a minimal second fake repository. Tests MUST NOT assert private node ordering, helper calls, raw database rows, or checkpoint implementation tables.

#### Scenario: Behavior test observes public outcomes
- **WHEN** authorization, invalid provenance, blocker release, deterministic serialization, idempotency, and restart behavior are tested
- **THEN** assertions use HTTP responses, workflow-state lookup, and controlled adapter effects as the observable results

#### Scenario: Repository contract is portable
- **WHEN** the adapter behavior contract runs for `probare-crm` and a minimal second repository
- **THEN** both produce the same canonical outcomes without workflow-core changes or live activation of the second repository
