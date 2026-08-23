## ADDED Requirements

### Requirement: Qualify complete criterion-level behavioral evidence
The workflow MUST require exactly one evidence entry for every acceptance criterion before publication. Each entry MUST contain a pass verdict, observed public interface, expected result, concrete proof observations, and an evidence kind whose required observations demonstrate the behavior rather than infrastructure health.

#### Scenario: Sufficient package covers every criterion
- **WHEN** a completed implementation returns every criterion once with the direct observations required for each evidence kind
- **THEN** the workflow accepts the package for source publication and retains the complete criterion matrix

#### Scenario: Package uses insufficient or incomplete proof
- **WHEN** an entry is missing, duplicated, failed, supported only by build, process, container, healthcheck, naked `2xx`, uncorrelated log, enqueue, or static initial screenshot evidence, or lacks a kind-specific public read-back
- **THEN** the workflow records a redacted evidence rejection and performs no commit, push, or pull-request write

### Requirement: Enforce evidence semantics by observation surface
REST evidence MUST include a request, relevant response, and business read-back. UI evidence MUST include executed interaction and a decisive screenshot. Recovery evidence MUST include restart and later public read-back. Idempotency evidence MUST include allowed repetition and a public read-back showing no duplicate effect. Negative-gate evidence MUST include the reasoned rejection or block and public read-back proving the forbidden business side effect is absent. Background evidence MUST include the eventually observable business result; enqueue, process start, or log output alone MUST NOT suffice. Logs MUST be correlated and supplemental.

#### Scenario: Direct surface observations qualify
- **WHEN** each evidence entry contains the required typed observations for its REST, UI, recovery, idempotency, negative-gate, or background surface
- **THEN** the workflow renders those decisive observations beside the matching criterion

#### Scenario: Surrogate evidence is offered alone
- **WHEN** an evidence entry offers only an operational surrogate or a correlated log without the required business observation
- **THEN** evidence qualification fails before source or GitHub mutation

### Requirement: Publish one committed branch as one draft pull request
After sufficient evidence, the workflow MUST inspect the outgoing worktree for sensitive data, commit any uncommitted implementation changes, verify that the run branch is ahead of its configured base, push the explicit run-owned branch, and ensure exactly one draft pull request for the claimed issue and branch. The pull request MUST close the claimed issue when human-merged and MUST NOT be merged by the workflow.

#### Scenario: Successful implementation is promoted
- **WHEN** a schema-valid completed implementation has sufficient evidence and a safe outgoing diff
- **THEN** the run branch is committed and pushed and exactly one draft pull request is observable for the claimed issue

#### Scenario: Delivery is repeated after publication
- **WHEN** the accepted GitHub delivery is submitted again or draft creation is retried for the same run branch
- **THEN** the existing head commit and draft pull request remain the only publication effects

### Requirement: Render the pull-request body as canonical evidence
The draft pull-request body MUST contain a matrix of all acceptance criteria with verdict, observed interface, expected result, concrete proof, and the exact published head SHA. Decisive screenshot references, compact REST request/response/read-back excerpts, and correlated log excerpts MUST be embedded adjacent to their criterion when technically available rather than represented only by links to raw artifacts.

#### Scenario: Canonical body is created
- **WHEN** qualified evidence is rendered for a pushed head
- **THEN** every criterion appears in the matrix and its decisive compact observations are embedded in the body with that same head SHA

### Requirement: Redact and bind every published or persisted output
The workflow MUST derive the evidence head binding from the source-control adapter after push. It MUST redact configured secrets, tokens, authorization values, email addresses, credential fields, and irrelevant payload content from evidence, diagnostics, errors, branch output, persistence, and the pull-request body. It MUST reject an outgoing source diff containing such data rather than silently rewriting implementation files.

#### Scenario: Sensitive evidence is provided
- **WHEN** otherwise sufficient evidence contains a secret, token, authorization value, email address, or credential field
- **THEN** the persisted evidence and pull-request body contain a redaction marker instead of the sensitive value

#### Scenario: Sensitive source diff is detected
- **WHEN** the outgoing staged implementation diff contains configured or recognizable sensitive data
- **THEN** publication fails closed before push or draft-pull-request creation and records only a safe rejection reason

#### Scenario: Application restarts after publication
- **WHEN** the application is recreated against the same database after a draft pull request was published
- **THEN** the HTTP workflow read model exposes the same PR identity, draft state, head SHA, body, evidence package, and publication timestamps without another external write

### Requirement: Verify publication through the primary system seam
Acceptance verification MUST submit the same authenticated GitHub delivery used in production, use real SQLite and LangGraph persistence, and observe publication through workflow-state read-back plus controlled Git/GitHub effects. It MUST cover both sufficient and deliberately insufficient evidence packages and MUST NOT assert private graph node ordering, helper calls, raw database rows, or checkpoint implementation tables.

#### Scenario: Behavior test drives sufficient and insufficient packages
- **WHEN** the publication behavior suite executes
- **THEN** a sufficient package yields one commit/push/draft-PR projection while each insufficient package yields a durable rejection and no source or pull-request effect through the same HTTP seam
