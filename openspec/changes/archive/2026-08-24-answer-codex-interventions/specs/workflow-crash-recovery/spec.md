## ADDED Requirements

### Requirement: Recover intervention lifecycle operations without duplicate effects
Startup recovery MUST reconcile persisted intervention delivery, open waiting, answer capture, applying continuation, and applied history before resuming ordinary machine phases. It MUST preserve the same request, Codex thread, LangGraph checkpoint thread, run ownership, phase operation, worktree, branch, pull request, head, review batch, repair attempt, and recovery correlations and MUST NOT execute a completed delivery or answer application again.

#### Scenario: Crash follows Codex delivery before its durable session record
- **WHEN** session creation may have completed but the delivery transition is not durably complete
- **THEN** recovery reconciles by the stable intervention identity and either adopts that session or reports a bounded uncertain delivery without creating an uncorrelated second task

#### Scenario: Crash occurs while applying an answer
- **WHEN** the accepted answer is durable but the resumed phase has not reached its next durable result
- **THEN** recovery resumes the same applying operation and existing phase identity until it completes, without accepting another answer or duplicating completed external effects
