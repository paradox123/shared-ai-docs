## ADDED Requirements

### Requirement: Admit only a verified isolated runtime
The pilot SHALL verify pinned executable identity, protocol methods, contract, tools, dependencies, sandbox and session capabilities before real issue work. All probes SHALL use disposable local repositories and separate runtime state with no remote Git effect. A failed or unknown mandatory capability SHALL stop the real candidate visibly without altering the LangGraph pilot.

#### Scenario: Runtime differs from the tested pin
- **WHEN** the executable version or digest differs from the configured pin
- **THEN** no session or issue work starts and the report identifies runtime drift

#### Scenario: Native interaction cannot be safely fenced
- **WHEN** no verified supported surface enforces the run lease before Codex writes
- **THEN** the candidate reports no-go and neither opens an unsafe writer nor silently creates a handoff fork

### Requirement: Keep complete validation separate from endpoint schema
The canonical worker-result-v3 schema SHALL retain all requirements. A separate endpoint schema SHALL preserve all result fields while projecting unsupported schema restrictions. Its acceptance SHALL be tested at the actual endpoint before issue implementation. Returned output SHALL still pass complete local validation; endpoint acceptance alone SHALL NOT qualify evidence.

#### Scenario: Structurally valid output omits completion evidence
- **WHEN** a completed result passes the endpoint schema but lacks canonical required evidence
- **THEN** canonical validation rejects it without weakening the result schema

### Requirement: Preserve process and session identity through failure
The adapter SHALL persist operation intent before session creation and correlate process start, timeout, stop and observations with the run and attempt. Recovery SHALL adopt only the exact existing session receipt or terminate explicitly unsafe; it SHALL NOT silently start a second session. Process stop SHALL target only its owned process group, and late output SHALL never qualify a stopped attempt.

#### Scenario: Crash loses the session-start reply
- **WHEN** the adapter dies after dispatch but before saving a session identity
- **THEN** replay adopts an exact independent receipt or returns unsafe without another start

### Requirement: Prove capabilities through public read-back
Preflight disposition, tested runtime provenance, real session identities and unverified capabilities SHALL remain readable through the authenticated Operator HTTP/CLI and ordered redacted Run History after process replacement. Real StartFresh, Read, Resume, Fork, Interrupt/Stop and safe Open in Codex SHALL be required for a go decision. Interactive writes SHALL obey the existing run-wide authorization, lease and fencing contract and reappear under the same run.

#### Scenario: Second operator diagnoses the stopped candidate
- **WHEN** an operator reconnects after a gate failure and worker/API replacement
- **THEN** the same run exposes the failure reasons and real versus unexecuted capability evidence without private database access

#### Scenario: A trusted prompt hook rejects a synthetic native input
- **WHEN** the pinned runtime receives a synthetic prompt covered by an explicitly trusted, isolated UserPromptSubmit hook
- **THEN** the probe records the blocked hook and completed turn with the original session and turn identities, separately from the still-required repository authorization and Control Lease integration
