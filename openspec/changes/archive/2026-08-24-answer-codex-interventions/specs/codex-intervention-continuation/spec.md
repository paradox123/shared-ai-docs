## ADDED Requirements

### Requirement: Persist a complete redacted intervention before handoff
The pilot MUST validate and redact an intervention request before external delivery. The request MUST retain repository and issue, durable run and phase identities, affected role, existing worktree or current pull-request head, policy classification, concrete problem, required decision or human action, available options and impacts, a reasoned recommendation, and all findings or results needed to decide. The controller MUST NOT synthesize a missing product decision.

#### Scenario: Agent node reaches an existing interrupt boundary
- **WHEN** implementation, an independent review, or findings repair returns a schema-valid policy interruption
- **THEN** workflow read-back exposes one persisted redacted request with the complete decision context before any Codex session delivery occurs

#### Scenario: Agent output does not contain a valid request
- **WHEN** an agent claims an intervention but omits required context or violates the intervention schema
- **THEN** the phase fails closed without a Codex handoff, invented decision, or continued autonomous loop

### Requirement: Deliver only interventions through a supported stable Codex surface
The pilot MUST present each persisted request as one clearly named, visible, answerable Codex App task using only a supported stable protocol surface. Production use MUST NOT enable experimental app-server capabilities or transports, invoke `exec-server`, inspect private Codex persistence, or silently fall back to logs. If the stable surface cannot be established, workflow read-back MUST report a bounded technical delivery blocker without weakening persistence, redaction, or access boundaries.

#### Scenario: Stable Codex session delivery succeeds
- **WHEN** the configured Codex runtime supports the required non-experimental stdio thread methods
- **THEN** the intervention records one Codex thread and delivery turn whose visible title and content identify the issue, run phase, problem, options, recommendation, and requested answer

#### Scenario: Stable Codex surface is unavailable
- **WHEN** the runtime cannot negotiate or execute the required stable methods without experimental capabilities
- **THEN** the request becomes `delivery_blocked`, remains visible through workflow read-back, and no experimental or private fallback is attempted

### Requirement: Apply one answer to the same interrupted run
The pilot MUST durably correlate the first later human user turn to exactly one open intervention and resume the same LangGraph run, checkpoint thread, worktree, branch, pull request, head, role, and workflow phase. The answer MUST resolve only the recorded question inside the existing work mandate and MUST NOT reconfigure model policy, permissions, round limits, repository scope, or workflow topology.

#### Scenario: Daniel answers an open intervention in Codex App
- **WHEN** the adapter observes the first user turn after the recorded delivery turn
- **THEN** read-back records that answer once and the same run resumes its interrupted phase with all prior correlations preserved

#### Scenario: Answer attempts to expand the mandate
- **WHEN** answer text requests work outside the recorded decision or existing assignment
- **THEN** the continuation remains bounded by the original mandate and does not treat the answer as workflow reconfiguration or new authorization

### Requirement: Make delivery, answer, continuation, and history idempotent
Repeated delivery attempts, repeated user replies, process restart, repeated reconciliation, and late correlated observations MUST converge on one session, one accepted answer, and one continuation operation without duplicated source, Git, GitHub, review, or workflow effects. An applied intervention MUST remain visible as history and MUST NOT be accepted again as an open request.

#### Scenario: Process restarts while intervention is open
- **WHEN** the pilot restarts after session delivery but before an answer
- **THEN** startup reuses the same request and Codex thread and leaves the same run waiting without starting another worker, worktree, branch, or pull request

#### Scenario: Answer is observed repeatedly across a crash
- **WHEN** the same answer turn is read before and after process restart while continuation is incomplete
- **THEN** the pilot reuses the same applying operation until completion and exposes exactly one applied answer and no duplicate external effect

### Requirement: Requalify every answer-produced head
If intervention continuation creates a new implementation or pull-request head, the pilot MUST invalidate prior head-bound evidence and verification, run deterministic verification on the new exact committed head, and execute all required independent reviews freshly against that head. A review task that was influenced by the intervention session or targets an older head MUST NOT qualify the new head.

#### Scenario: Intervention answer produces a new head
- **WHEN** the resumed phase commits and pushes source changes
- **THEN** the existing draft pull request moves to the new head and only new deterministic evidence plus fresh requirements, code, and architecture reviews can verify it

### Requirement: Expose and verify the complete intervention lifecycle publicly
Workflow read-back MUST expose the request, stable phase operation, Codex task identity, delivery state, accepted answer identity and bounded content, continuation state, preserved run correlations, and timestamps. Acceptance verification MUST use a newly created marked test issue through the productive GitHub, Cloudflare, and pilot path, a decisive Codex App screenshot and human answer, and public workflow read-back; it MUST close the test issue without merge or deployment and MUST NOT use or modify ProBara CRM issue #2.

#### Scenario: Productive marked test issue completes its intervention proof
- **WHEN** the dedicated test issue deterministically requests an existing policy decision and Daniel answers its visible Codex task
- **THEN** the screenshot and HTTP read-back prove one request, one answer, the same continued run and worktree, and no duplicate effects before the issue is closed with no test work left active
