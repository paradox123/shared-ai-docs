## ADDED Requirements

### Requirement: Preserve identity truth in a scoped rehearsal
Acceptance evidence SHALL distinguish a single authenticated person acting in several roles from three distinct human identities. It SHALL NOT manufacture takeover, interactive human approval or external agent-definition approval. The original full-acceptance gates SHALL remain open until directly verified.

#### Scenario: One account acts as A B and C
- **WHEN** one person performs the rehearsal's role actions
- **THEN** evidence retains the same provider identity and explicitly marks cross-identity takeover and third-person approval unproven

### Requirement: Isolate the authorized CRM implementation
The issue 3 implementation SHALL use a separate clone on a branch ending in `-issue14-test`. Evidence SHALL record the source base, target branch, checks and changed files. The existing CRM main checkout, real mailbox, LangGraph source/runtime/worktrees, Cloudflare and macOS service configuration SHALL NOT be changed by the rehearsal.

#### Scenario: Implement the selected issue
- **WHEN** the agent implements CRM issue 3
- **THEN** its filtering and deduplication changes and synthetic verification remain in the isolated test checkout and production configuration remains untouched

### Requirement: Correlate actual public observations
Rehearsal evidence SHALL retain actual run, attempt, session, head, qualification and export observations where executed. Failed or unavailable capabilities SHALL be reported without substituting fabricated events or claiming controlled-provider results as live evidence.

#### Scenario: A required capability is absent
- **WHEN** the real run cannot establish a mandatory acceptance gate
- **THEN** the report identifies that gate, the observed limitation and the lower-level evidence that is available

### Requirement: Make a fail-closed candidate decision
The acceptance report SHALL include a Go/Stop decision based on every original Ticket 14 gate. Missing mandatory evidence SHALL produce Stop for replacing LangGraph. A working CRM test branch SHALL NOT imply candidate acceptance, human approval, mark-ready, merge, deployment or release.

#### Scenario: Rehearsal succeeds with unresolved governance gates
- **WHEN** CRM behavior passes but third-person approval or definition governance remains unproven
- **THEN** the candidate decision is Stop, LangGraph remains in place, and no unapproved replacement begins
