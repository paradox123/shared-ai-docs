## ADDED Requirements

### Requirement: Optional deleted-session tolerance
Protected capture MUST accept an identity-bound `missing_session_policy` with strict default `block` and opt-in `ignore`. The NCG wiki automation MUST enable `ignore`: sessions selected by the review window, carry-forward, or both that have resolver status `missing`, null path, no stored rollout metadata and a matching `missing_rollout` diagnostic MUST be recorded as ignored and MUST NOT alone block complete resolution or bounded extraction. Raw resolver exit/safety fields and immutable evidence MUST remain unchanged. Other callers MUST retain their existing strict/explicit-allowlist behavior.

#### Scenario: Missing window and carry sessions
- **WHEN** an ignore-policy capture finds missing window-only, carry-only and window-plus-carry sessions alongside resolvable sessions
- **THEN** it retains the selection and raw failure diagnostics, reports the ignored IDs and permits full same-snapshot resolution and extraction of the remaining eligible sessions

#### Scenario: Unchanged capture resumes
- **WHEN** an ignore-policy capture resumes with the same bound policy and inputs
- **THEN** it reuses the captured snapshot without reading the changed live index
- **AND** changing the missing-session policy prevents silent reuse

#### Scenario: Missing session accompanied by another failure
- **WHEN** a missing session accompanies unreadable, ambiguous, malformed, corrupt, incomplete, hash-mismatched or timed-out evidence
- **THEN** the run remains blocked and the official checkpoint remains unchanged

#### Scenario: Successful completion prunes only ignored missing carries
- **WHEN** all normal session, Git, wiki and delivery gates succeed for an ignore-policy run
- **THEN** only the validated missing IDs are removed from the derived carry array during atomic finalization
- **AND** remaining carry objects and order, non-checkpoint memory, source pins and separate Docs-tip rules are preserved

#### Scenario: Capture or partial review is not completion
- **WHEN** missing sessions are ignored but the full review or required delivery is incomplete
- **THEN** no cursor/carry/source-tip checkpoint is advanced
