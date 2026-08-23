## ADDED Requirements

### Requirement: Gate activation on a strictly valid bounded change
The operator MUST NOT enable live ingress or start a new live implementation run until an active OpenSpec change describes the activation target, scope, write-set, rollback, and direct live verification and passes strict validation.

#### Scenario: Activation change is incomplete or invalid
- **WHEN** the activation change is absent or fails strict validation
- **THEN** live activation stops before a GitHub, Cloudflare, worker, branch, pull-request, merge, deployment, or release write

### Requirement: Validate the live repository profile before activation
The pilot MUST expose a secret-safe readiness command that validates the private runtime configuration, the versioned `RepositoryAdapter` identity, repository checkout and base ref, a repository-local GitHub noreply author identity, required GitHub access, the workflow labels `ready-for-agent`, `agent-running`, `verified`, `awaiting-review`, `needs-info`, and `ready-for-human`, the active signed webhook at the exact Cloudflare Worker ingress for the adapter's allowed event groups, and a distinct exact Tunnel route for the relay's authenticated local hop. Repository-specific paths and identities MUST remain outside the workflow core.

#### Scenario: Complete production profile is ready
- **WHEN** the private configuration, `probare-crm` adapter, checkout, labels, webhook subscriptions, relay route, and permissions agree
- **THEN** readiness succeeds with bounded non-secret facts that identify adapter version and configuration hashes without printing secrets or repository content

#### Scenario: Production profile is incomplete or inconsistent
- **WHEN** any required path, permission, label, webhook event group, adapter identity, repository origin, Git author identity, base ref, or relay route is missing or inconsistent
- **THEN** readiness fails closed with a stable bounded category and does not start a worker or mutate GitHub

### Requirement: Bootstrap only missing workflow label definitions explicitly
The operator MUST provide a separate explicit idempotent command that creates only missing workflow label definitions for the configured repository. It MUST preserve existing labels and issue label assignments and MUST NOT start or authorize an implementation run.

#### Scenario: Required labels are missing
- **WHEN** the operator explicitly invokes label bootstrap for a validated `probare-crm` configuration
- **THEN** only missing workflow label definitions are created and a subsequent read confirms the complete required set

#### Scenario: Required labels already exist
- **WHEN** label bootstrap is repeated after all workflow labels exist
- **THEN** GitHub state and issue assignments remain unchanged and the command reports a converged result

### Requirement: Expose the complete eligible backlog without weakening scheduling gates
Live readiness and the runtime adapter MUST evaluate the complete open `probare-crm` issue backlog without an issue-type or risk-class filter. `ready-for-agent` MUST remain sufficient authorization, unresolved blockers MUST remain queued until human merge and issue closure, and at most one issue MUST own an active implementation run for the repository.

#### Scenario: Multiple issue types and ready items exist
- **WHEN** the live repository contains ready issues of different types
- **THEN** readiness reports all open and ready candidates by bounded counts and type counts while the scheduler applies deterministic issue-number ordering

#### Scenario: Backlog contains blocked or concurrent candidates
- **WHEN** more than one candidate is authorized or a candidate has an unresolved blocker
- **THEN** the workflow starts at most one unblocked frontier issue and durably retains the other dispositions without creating a stacked pull request

### Requirement: Prove one real workflow through the productive boundaries
Activation acceptance MUST use a real allowed GitHub event and correlate its delivery through Cloudflare Queue, the named Tunnel, local durable inbox, LangGraph run and checkpoints, one isolated Codex worktree, exact-head deterministic verification, and three independent read-only reviews. A start, health check, enqueue acknowledgement, or log line alone MUST NOT satisfy this requirement.

#### Scenario: Eligible live issue reaches review
- **WHEN** a signed allowed event exposes an eligible deterministic frontier issue and every implementation, verification, and review gate passes
- **THEN** one durable run produces one draft pull request for the run branch and public read-back correlates the delivery, checkpoints, worker model/reasoning/skills, verification, all review verdicts, and exact pull-request head

#### Scenario: A live gate cannot pass
- **WHEN** the run encounters missing product information, a non-agentic blocker, failed exact-head verification, stale or failed review output, or exhausted bounded repair
- **THEN** the pilot reports the truthful durable failure or human-handoff state and does not publish `verified`

### Requirement: Publish exact-head review evidence for the human gate
For a successful run, the current draft pull-request head MUST have passing deterministic verification and fresh passing or permitted-not-applicable verdicts from Requirements, Code, and Architecture review. The issue MUST carry `verified` and `awaiting-review` and not `agent-running`; the pull-request body MUST contain the acceptance-criterion matrix and the decisive direct evidence required by each declared evidence kind. UI evidence requires a redacted screenshot, REST evidence requires request/response/read-back excerpts, document evidence requires rendered-document read-back, and correlated logs remain supplemental rather than substitutes for public behavior.

#### Scenario: Evidence and labels converge on the current head
- **WHEN** evidence capture observes the live workflow and current GitHub pull request
- **THEN** it succeeds only if the workflow verification, all three reviews, PR body, PR head, and workflow labels agree on the same current commit

#### Scenario: Pull-request head changes after verification
- **WHEN** the current pull-request head differs from the verified or reviewed head
- **THEN** evidence capture fails closed and the issue is not represented as currently verified until checks and reviews rerun

### Requirement: Stop at human review and support evidence-preserving rollback
The activated pilot MUST NOT merge, deploy, or release. Its successful terminal boundary for the demonstration issue MUST be Daniel's human pull-request review. Rollback MUST stop new ingress and local processing without deleting the durable database, Queue/DLQ state, worktree, branch, pull request, or evidence needed for diagnosis.

#### Scenario: Successful automated run completes
- **WHEN** the current pull-request head becomes verified and awaiting review
- **THEN** the pilot performs no merge, deployment, or release action and leaves the draft pull request for Daniel

#### Scenario: Operator rolls back live activation
- **WHEN** the operator disables the GitHub webhook and stops the local LaunchAgent and relay consumer as needed
- **THEN** no new implementation starts while existing durable and review evidence remains recoverable
