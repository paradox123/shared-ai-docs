## ADDED Requirements

### Requirement: Isolate repository semantics behind a versioned adapter
The control plane MUST obtain repository identity, label meanings, accepted event/action pairs, current issue and backlog state, provenance and blocking relationships, implementation-merge state, and GitHub projections through a versioned `RepositoryAdapter`. The workflow core MUST NOT branch on `probare-crm` or another repository identity.

#### Scenario: Probare CRM uses the repository contract
- **WHEN** the pilot is configured for `probare-crm`
- **THEN** its repository-specific labels, events, relationships, and projections are supplied by its adapter configuration while the core executes only canonical adapter operations

#### Scenario: A second adapter satisfies the same contract
- **WHEN** a minimal controlled adapter for a second repository is used by the behavior suite
- **THEN** the same authorization and scheduling outcomes are produced without changing the workflow core or activating that repository in production

### Requirement: Treat readiness as authorization for every issue type
The scheduler MUST treat the adapter's ready label as both maturity state and implementation authorization. It MUST NOT require another start signal, a mandatory mandate section, or an issue-type or risk-class allowlist.

#### Scenario: Ready issues of every type enter eligibility evaluation
- **WHEN** open issues of different repository issue types carry the configured ready label and have no unresolved blockers
- **THEN** each issue is eligible for deterministic frontier selection regardless of type

### Requirement: Self-authorize only proven inherited work
For an open issue without the ready label, the scheduler MUST allow the adapter to project that label only when provenance establishes a Daniel-authored issue, linked PRD, or valid Daniel-rooted parent/child chain and the derived scope stays within or narrows the inherited mandate. It MUST interrupt unproven provenance as invalid and MUST interrupt material scope expansion as a product decision.

#### Scenario: Proven direct or inherited mandate is self-authorized
- **WHEN** an unready issue has adapter evidence of a Daniel-authored issue, linked PRD, or valid parent chain and its scope is within the inherited mandate
- **THEN** the ready label is projected idempotently and the issue continues through normal frontier selection without another start signal

#### Scenario: Provenance cannot be established
- **WHEN** an unready issue has no provable Daniel-authored mandate or linked inheritance chain
- **THEN** its disposition is interrupted with an invalid-provenance reason and no implementation run or running projection is created

#### Scenario: Derived scope materially expands the mandate
- **WHEN** provenance is valid but the derived issue materially expands beyond inherited scope
- **THEN** its disposition is interrupted as a product decision and no implementation run or running projection is created

### Requirement: Queue unresolved blockers until merge and closure
The scheduler MUST keep a candidate queued while any `Blocked by` relation lacks either a human-merged implementation pull request or a closed blocker issue. It MUST release the candidate only after both facts are true for every blocker.

#### Scenario: Open blocker prevents claim
- **WHEN** an authorized candidate has a blocker whose pull request is unmerged or whose issue remains open
- **THEN** the candidate remains queued with a blocker reason and has no implementation run or running projection

#### Scenario: Completed blocker releases successor
- **WHEN** every blocker pull request is human-merged and every blocker issue is closed
- **THEN** the authorized successor becomes part of the selectable repository frontier on that scheduling pass

### Requirement: Serialize a deterministic durable repository frontier
On each accepted repository event, the scheduler MUST durably evaluate all adapter-provided backlog candidates in ascending issue-number order. It MUST retain the disposition of every simultaneous candidate, create at most one active implementation run per repository, and MUST NOT create a successor or stacked pull request while another implementation remains active.

#### Scenario: Two candidates become ready together
- **WHEN** two authorized unblocked issues in one repository are visible during the same or concurrent accepted events and no implementation is active
- **THEN** the lower issue number is selected, the other remains durably queued, exactly one run starts, and no accepted event is lost

#### Scenario: Repository already has active implementation
- **WHEN** an authorized unblocked candidate is evaluated while another issue owns the repository's active run
- **THEN** the candidate remains queued and no second worktree, implementation run, or stacked pull request is started

#### Scenario: Completed active issue advances the frontier
- **WHEN** the active issue's implementation pull request is human-merged and the issue is closed
- **THEN** the active run becomes completed and the next authorized unblocked issue is selected in the same scheduling pass

### Requirement: Expose backlog disposition across restart
The productive workflow read model MUST expose an issue's latest accepted delivery correlation, disposition status and reason, selected run and projection when present, and checkpoint state. Reconstructing the application on the same database MUST preserve those outcomes without duplicate selection or projections.

#### Scenario: Queued and interrupted outcomes survive restart
- **WHEN** the application is restarted after candidates were queued or interrupted
- **THEN** the same dispositions and reasons are returned through workflow-state lookup without creating a new run or GitHub write
