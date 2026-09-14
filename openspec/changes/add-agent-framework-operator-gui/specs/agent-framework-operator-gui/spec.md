## ADDED Requirements

### Requirement: Graphical background admission
The graphical Operator Client SHALL accept a GitHub issue URL or a local issue or PRD Markdown path as a work input and SHALL expose the admitted run or an actionable admission failure. Admission SHALL preserve the applicable authorization and repository boundaries.

#### Scenario: Start an eligible input
- **WHEN** a user submits an eligible authorized work input through the graphical client
- **THEN** the client identifies its admitted background run and provides access to its state and history

### Requirement: PRD decomposition within the work mandate
The system SHALL treat a submitted PRD as an Arbeitsmandat, autonomously derive linked issues within its scope, and process eligible issues under the existing per-repository serial queue. Each derived issue SHALL retain its own ImplementationRun and traceable authorization ancestry. The GUI SHALL expose the PRD, derived issues, dependencies and associated runs. Routine decomposition and implementation within the mandate SHALL NOT require another start approval; unresolved product decisions, actionable blockers and human approval gates SHALL surface for human action.

#### Scenario: Process an authorized PRD
- **WHEN** the user submits an eligible PRD with sufficient product requirements
- **THEN** the pilot derives linked issues and starts eligible work in the background without a foreground Codex task manually coordinating the decomposition or implementation

#### Scenario: A dependent issue awaits the predecessor merge
- **WHEN** a predecessor has a qualified or human-approved PR that has not yet been human-merged and its blocking issue closed
- **THEN** its dependent successor remains waiting, the GUI shows that dependency, and the pilot neither merges automatically nor starts the successor early

#### Scenario: Decomposition exposes an unresolved product decision
- **WHEN** a derived issue cannot be defined or executed within the accepted mandate without deciding new product behavior
- **THEN** the pilot presents a targeted intervention linked to the mandate and affected issue instead of silently widening the authorized scope

### Requirement: Preserve the submitted issue source
The system SHALL preserve the Issue-Quelle of submitted work. A PRD submitted as a GitHub issue SHALL produce linked GitHub issues; a PRD submitted as a Markdown file SHALL produce linked local issue files. Directly submitted issues SHALL retain their source. Both sources SHALL use the same implementation workflow, qualification and human-control gates, and graphical run view. The system SHALL retain stable source identity and mandate ancestry without requiring every issue to have a GitHub issue number.

#### Scenario: Decompose a GitHub PRD
- **WHEN** the pilot decomposes a PRD submitted as a GitHub issue
- **THEN** its derived issues are created in GitHub, linked to their originating PRD, and navigable with their runs through the common Operator view

#### Scenario: Decompose a local PRD
- **WHEN** the pilot decomposes a PRD submitted as a Markdown file
- **THEN** its derived issues are created as linked local Markdown files without automatically publishing GitHub issues, and their runs use the same workflow and Operator view

#### Scenario: Recover interrupted decomposition
- **WHEN** processing resumes after a child issue was created in the originating source but decomposition did not finish
- **THEN** the system reconciles and reuses that child issue rather than creating a duplicate or overwriting unrelated local files

#### Scenario: Local dependency completion
- **WHEN** a local predecessor issue's corresponding PR is human-merged and the local issue is recorded as closed
- **THEN** its dependent successor can become eligible under the same queue rules used for GitHub issues, without requiring a mirrored GitHub issue

### Requirement: Execution is independent of the observing client
An admitted background run SHALL execute independently of the initiating browser or foreground Codex task. The system SHALL retain progress and actionable intervention or readiness state for later observation.

#### Scenario: Close the starting client
- **WHEN** the user closes the graphical client and the initiating Codex task after admission
- **THEN** background processing continues without that foreground task implementing or coordinating the issue, and reopening the run exposes its subsequent progress or concrete blocker

### Requirement: Submissions and run relationships are database-backed
The system SHALL persist every admitted Einreichung in its database with a stable identity, submitted content/version, source provenance, target repository and links to its issues and ImplementationRuns. PRD decomposition SHALL retain parent/child and dependency relationships. The graphical overview SHALL read these records independently of the originating browser or foreground task. Retaining source references alone SHALL NOT satisfy submission persistence. Existing redaction requirements SHALL apply to stored submission content.

#### Scenario: Inspect a PRD after restart
- **WHEN** an authorized user reconnects after the client and service restart
- **THEN** the overview displays the persisted PRD submission and its admitted version, derived issues, dependencies and associated runs without requiring the original client to resubmit the file or URL

#### Scenario: Source content changes after admission
- **WHEN** the source issue or PRD file is edited after admission
- **THEN** the run remains traceable to its admitted content/version and the source edit does not silently replace the active mandate

### Requirement: The pilot exercises the server and separate human clients
The pilot SHALL support and directly verify a server-hosted control plane accessed by authenticated humans from separate work machines. Human-action requests and their run/attempt associations SHALL remain centrally durable when every Operator Client is closed. Notification and targeted session-opening paths SHALL address the receiving human's client rather than the server's local desktop. A same-machine local demonstration SHALL NOT substitute for this distributed behavior proof.

#### Scenario: Human receives a server-originated intervention
- **WHEN** a background run needs intervention while the responsible human's Operator Client is closed
- **THEN** the service retains the request and uses the configured recipient notification channel, and the human can open the exact authorized run and target attempt from their separate machine

#### Scenario: Notification delivery fails
- **WHEN** the recipient channel cannot deliver an actionable notification
- **THEN** the underlying request remains pending and visible in the graphical inbox with its delivery failure, without being treated as answered or approved

#### Scenario: File submission from another machine
- **WHEN** a human submits a PRD file from a machine separate from the service
- **THEN** the system ingests and persists the intended file contents with explicit source/workspace provenance instead of interpreting the path as an unrelated server-local file

### Requirement: Workflow and persisted run inspection
The graphical Operator Client SHALL list authorized runs and display each run's workflow progress and persisted correlated history, including observable session messages, tool calls/results, activity attempts, handoffs and outcomes. Missing or redacted evidence SHALL be explicit rather than represented as complete content.

#### Scenario: Inspect a background failure
- **WHEN** an authorized user opens a run with a failed activity
- **THEN** the user can identify the activity and attempt, its session, retained observable messages and tool results, the failure and any recorded handoff without access to the original foreground task

### Requirement: Complete graphical human operation
The first release SHALL provide graphical actions for intervention answers, Resume, Fork, Fresh Retry, Cancel, targeted queue/interrupt, control claim/release, voluntary transfer, Forced Takeover, targeted Open in Codex, and qualified-head human approval according to the existing product contracts. Ordinary Operator actions SHALL NOT require manual CLI commands. Mutations SHALL enforce current repository authorization, the run-wide Control Lease and stale-state fencing and SHALL remain in the same canonical Run History.

#### Scenario: Diagnose and continue through the GUI
- **WHEN** an authorized controller answers an intervention or chooses an available continuation for an explicit attempt through the GUI
- **THEN** the accepted action and its actual session/ancestry are observable in the original run and background processing continues without a coordinating foreground task

#### Scenario: Another human takes control
- **WHEN** an authorized observer completes a voluntary transfer or an explicit Forced Takeover through the GUI
- **THEN** the new controller and audited transfer are visible to all authorized clients and stale mutations from the previous controller are rejected

#### Scenario: Open an exact attempt in Codex
- **WHEN** the controller chooses Open in Codex on a specific attempt
- **THEN** the system opens its existing session where supported or requires explicit confirmation for a labelled handoff fork, preserving correlation and control boundaries

### Requirement: Interactive human approval in the GUI
The GUI SHALL allow an authenticated authorized human with the required Control Lease to explicitly approve the exact currently qualified head. Background workers and monitors SHALL NOT perform this action on the human's behalf. Approval SHALL NOT trigger mark-ready, merge, deployment or release.

#### Scenario: Head changes while the approval view is open
- **WHEN** the displayed qualified head is superseded before the human submits approval
- **THEN** the system rejects approval of the stale view and displays the current head and its qualification state

### Requirement: Local-agent Handover remains an independent access path
The graphical client SHALL supplement rather than supersede existing pilot access paths. A human SHALL be able to use their local agent to inspect and assist with an existing central run through a correlated Handover and authorized read/control interfaces without keeping the GUI open. Sessions, workflow execution and execution workspaces SHALL remain centrally managed. Handover SHALL NOT implicitly create a session fork, move execution or transfer the Control Lease.

The Handover SHALL identify the submission, run, target activity/attempt and central session, relevant head, pending request or failure, current control state and supported next actions. It SHALL provide authorized access to database-backed submission contents, observable messages, tool calls/results, artifacts and further Run History rather than only a static summary. Existing redaction and artifact-availability semantics SHALL apply. Supported commands, answers and evidence returned through this route SHALL remain correlated in the original Run History and enforce the same authorization and fencing as GUI actions. Local-agent access SHALL NOT confer authority to perform an interactive human approval.

#### Scenario: Local agent diagnoses a run while the GUI is closed
- **WHEN** a human supplies the targeted Handover to their local agent with authorized access to the run
- **THEN** that agent can retrieve the persisted submission, failure, relevant session observations and retained evidence through public interfaces without a GUI session or raw database access

#### Scenario: Local-agent intervention is visible in the common history
- **WHEN** the local agent submits a supported intervention authorized by the controlling human against the current attempt and control state
- **THEN** the central service records and applies it to the existing run, and reopening the GUI shows the accepted action and its correlated outcome without an untracked implementation run

#### Scenario: Another human takes control during local diagnosis
- **WHEN** control changes after a local agent reads the Handover and that agent then submits a mutation using the previous control state
- **THEN** the mutation is fenced without changing the run and the authorized caller can retrieve the current control state

### Requirement: Automatically open the local agent through a Workstation Client
The system SHALL deliver actionable Handover requests to an authenticated Workstation Client associated with the addressed human. On delivery the client SHALL automatically create or reopen the correlated local agent assistance session with the Handover available, without requiring the user to copy a prompt or first open the GUI. The local assistance session SHALL be distinguished from the central execution session and linked to its Handover, run and target attempt. Automatic opening SHALL NOT relocate central execution, claim the Control Lease, answer the intervention or grant approval.

#### Scenario: Server requests help while the GUI is closed
- **WHEN** a central run produces an actionable Handover for a human whose Workstation Client is connected
- **THEN** the local agent opens on that human's machine with the targeted context and authorized evidence access, and the central history records the delivery and resulting local-session correlation

#### Scenario: Delivery repeats after an acknowledgement is lost
- **WHEN** the same Handover is delivered again after the local session was opened
- **THEN** the client reconciles the existing opening and reports its correlation instead of creating another independent session

#### Scenario: The human machine is offline
- **WHEN** a Handover is ready but the addressed Workstation Client is disconnected
- **THEN** delivery remains pending and visible centrally, and reconnect delivers it only if the request is still actionable and the recipient is still authorized

#### Scenario: Local agent cannot be opened
- **WHEN** the client lacks a supported agent capability or the opening operation fails
- **THEN** the system records an actionable opening failure and retains a supported retry path without claiming successful handoff or completing the underlying request

### Requirement: Automatic local diagnosis precedes human-directed intervention
After automatic Handover opening, the local agent SHALL retrieve relevant authorized evidence, perform read-only diagnosis and prepare a proposed resolution. Mutating intervention SHALL require the human's instruction and the existing authorization, Control Lease and fencing checks. Persisting diagnosis observations SHALL NOT grant workflow-control authority. Human head approval SHALL remain an explicit interactive human action.

#### Scenario: Agent prepares a diagnosis before the human responds
- **WHEN** the local agent receives a valid Handover for an actionable problem
- **THEN** it examines authorized evidence and records its findings and proposed resolution without changing implementation files, issuing mutating workflow commands or answering the intervention on the human's behalf

### Requirement: All participating agent work joins the central lifecycle history
The system SHALL centrally persist the complete observable work of every session participating in an admitted PRD or issue, regardless of execution host or responsible person. This SHALL include assignments and supplied context, user and agent messages, emitted findings, tool calls with parameters/results/duration/errors, artifacts, handovers, commands and decisions. Local-agent diagnosis and assistance SHALL be represented as workflow activities/attempts with session identity and relationships to the targeted central activity. Summary-only or final-result-only capture SHALL NOT satisfy this requirement.

Each observation SHALL be traceable to its submission/mandate, applicable issue and run, activity/attempt, session, execution host and actor. The centrally stored lifecycle SHALL retain intake and PRD-decomposition observations before child issue runs exist and SHALL link the child runs without collapsing their independent identities. Existing redaction, observable-content and artifact-availability contracts SHALL apply to both server and workstation sources.

#### Scenario: One issue moves between people and machines
- **WHEN** a central implementation is handed to a local agent for diagnosis and a different authorized person later continues the run
- **THEN** the workflow view includes all participating activities and their complete observable chats, findings, tools and artifacts with actor/host/session attribution under the same issue lifecycle

#### Scenario: Inspect the full PRD lifecycle
- **WHEN** a user opens a PRD whose decomposition produced several issues and subsequent implementation, review and Handover activities
- **THEN** the overview links the original admitted PRD, decomposition observations, derived issues and each issue's run history, allowing inspection across the lifecycle or filtering by issue, activity, session, actor or host

#### Scenario: Local diagnosis has no mutating result
- **WHEN** a local assistance session reads evidence, runs diagnostic tools and emits findings without changing the run
- **THEN** its observable conversation and every diagnostic tool call/result still appear centrally as the corresponding workflow activity rather than being omitted because no intervention command was sent

### Requirement: Distributed history synchronization exposes completeness
The system SHALL ingest central and workstation observations with stable source identity, per-session ordering, causal correlation and replay deduplication. Client disconnect/restart SHALL preserve recoverable unsynchronized observations and expose pending synchronization. The system SHALL NOT claim complete history for an activity with known unacknowledged, missing or unsupported observations. Observation ingestion SHALL NOT bypass command authorization or confer the Control Lease.

#### Scenario: Reconnect after local observations were buffered
- **WHEN** the workstation reconnects after collecting observations during a network interruption
- **THEN** its retained observations are ingested once in source-session order, preserving their original activity/session/actor relationships, and pending synchronization clears only after acknowledgement

#### Scenario: Agent integration cannot supply complete observations
- **WHEN** the selected local agent cannot expose a required conversation or tool-event surface
- **THEN** the pilot reports that capability limitation and does not count the session as proof of complete lifecycle observation
