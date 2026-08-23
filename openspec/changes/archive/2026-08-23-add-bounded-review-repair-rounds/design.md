## Context

The pilot currently performs one linear implementation, publication, and independent review pass. `ReviewCoordinator` persists one batch per run/head and returns `review_blocked` for a schema-valid `fail`, while the run worktree, implementation worker port, draft PR, and all three verdicts remain available. The packaged policy already distinguishes `findings_repair` and defined Sol escalation reasons, but there is no repair contract, attempt persistence, deterministic post-commit verifier, updated-head publication path, or terminal handoff projection.

The implementation must preserve the existing module seams: signed HTTP delivery and workflow GET are the system seam; Codex, Git, deterministic commands, and GitHub remain replaceable boundary ports; SQLite and LangGraph state remain durable. Reviewers stay fresh and read-only. The same configured writing worker and existing run worktree perform all repairs.

## Goals / Non-Goals

**Goals:**

- Turn actionable findings from a failed three-axis review batch into at most three durable repair rounds.
- Bind every round to one repair assignment, worker result, repair commit/head, deterministic verification, fresh review batch, and retained PR update.
- Enforce Terra/Sol and write-access policy without allowing reviewers or a separate writer to repair findings.
- End with either current-head verification or an observable `needs-info`/`ready-for-human` handoff with attempts and open findings intact.
- Keep the workflow testable through public HTTP read-back and narrow boundary contracts.

**Non-Goals:**

- Human PR feedback batches, independent counters for them, or invalidating an already verified head (Issue 06).
- General crash-time resumption of an in-flight node (Issue 08).
- Automatic merge, deploy, release, or synthesized product decisions.
- Repairing invalid/missing reviewer output as if it were a code finding; those fail closed as non-actionable review infrastructure conflicts.

## Decisions

### Add a dedicated repair coordinator behind the existing workflow

After the initial review node, a repair node reads the persisted batch. A schema-valid `fail` with concrete findings starts a `ReviewRepairCoordinator`; a verified batch is a no-op, while missing/invalid/stale-head review outcomes remain fail-closed. The coordinator owns the bounded loop and delegates worker execution, publication, verification, reviewing, and label projection to existing or new ports.

This keeps `WorkflowRuntime` as orchestration glue instead of duplicating implementation/publication/review internals in graph nodes. Conditional graph cycles were considered, but a coordinator is simpler for this synchronous slice and the durable attempt tables provide the later Issue 08 resume seam.

### Use the same worker port and worktree with repair-specific contracts

`WorkerPort` gains a repair operation invoked on the same injected worker object and the original run-owned worktree. A versioned repair assignment contains the initial review batch/head, round number and limit, all failed-axis findings with axis/location/description, original requirements and repository guidance, prior repair summaries, and explicit decision boundaries. It does not include passing-axis verdicts as advice, reviewer conversations, secrets, or unrelated issue context.

A versioned repair result reports `completed`, `blocked`, or structured `escalate`; changed files, Red-Green observations, verification/evidence, remaining findings, and an optional terminal classification are schema validated and redacted. `blocked` requires one of the permitted interruption reasons. `escalate` requires one of the allowed policy reasons and may cause one Sol continuation inside the same numbered round; it does not create a fourth round.

A separate repair worker was considered, but it would weaken the guarantee that findings go exclusively to the writing implementer and would duplicate the Codex CLI boundary.

### Count rounds by the initial failed review batch and persist every attempt

One repair batch is keyed to the initial failed review batch and stores a hard limit of three. Each numbered attempt records assignment, policy and skills, access profile, diagnostics/result, repair head, deterministic verification, linked fresh review batch, remaining findings, and timestamps. The controller inserts rounds monotonically and refuses round numbers above three. A structured escalation can add an invocation record to the same attempt, but never increments beyond the third attempt.

The public read model exposes the repair batch and ordered attempts. Existing `review` continues to expose the latest head-bound review; each repair attempt links its own review batch so history is not lost.

### Publish first, then verify and review the exact new head

For a schema-valid completed repair, the existing source-control adapter commits and pushes the worktree, returning a new head. The controller rejects reuse of the previous head. It qualifies the repair evidence, updates the one existing draft PR and persisted publication to the new head/body, then runs the configured deterministic verification command through a new `DeterministicVerificationPort`. Regardless of deterministic pass/fail, it launches all three fresh review axes for that same head. A round succeeds only when deterministic verification passes, every applicable review passes, and GitHub still reports that head current.

Running checks before the commit was considered, but would not prove the exact head later reviewed. Skipping reviews after a failed deterministic check was considered, but contradicts the required complete rerun and would omit potentially useful findings for the next repair assignment.

### Keep model escalation separate from handoff classification

Rounds one and two select `findings_repair` (Terra/`xhigh`/workspace-write) unless the assignment or structured worker result identifies an allowed material architecture, persistence, security, data-migration, or explicit worker escalation. Round three always selects an escalated repair policy using Sol/`xhigh` while retaining the implementer's workspace-write boundary. No other reason may select Sol.

After three unsuccessful rounds, an explicit missing/contradictory-requirements classification projects `needs-info`; every other unresolved non-agentic conflict projects `ready-for-human`. Earlier `blocked` results may make the same transition only for genuine product behavior/scope, missing access, unavoidable manual evidence, or an unresolvable conflict. Reversible presentation details remain inside the repair assignment; warnings, consent, domain actions, security meaning, or other semantic UI behavior are classified as product decisions.

### Keep the draft PR as the canonical retained artifact

Every new head updates the existing draft PR body with current evidence plus a compact repair history and open findings. Terminal handoff adds exactly one of `needs-info` or `ready-for-human`, removes `agent-running`, and does not add `verified` or `awaiting-review`. Successful verification uses the existing success projection and leaves the repair history observable in both persistence and the PR.

## Risks / Trade-offs

- **[A worker reports a misleading terminal category]** → Require structured reasons, preserve all review findings, default exhausted ambiguous cases to `ready-for-human`, and expose the raw redacted assessment for Daniel.
- **[A deterministic command hangs or mutates the worktree]** → Run it through a timeout-bounded port on the committed head and record command/exit/observation; a changed head or dirty follow-up cannot be verified without another repair commit.
- **[Review and repair histories grow]** → Cap automatic rounds at three and retain only structured, redacted assignments, results, diagnostics, and compact PR summaries.
- **[Existing SQLite databases lack new tables/columns]** → Use additive `CREATE TABLE IF NOT EXISTS` tables and additive publication update methods; no destructive migration is required.
- **[Synchronous rounds extend webhook background execution]** → Preserve current background-task behavior and configured worker timeouts; general asynchronous continuation belongs to Issue 08.

## Migration Plan

1. Add contracts and additive persistence/read-model structures; existing runs return `repair: null`.
2. Add repair worker and deterministic verifier boundary contracts.
3. Add the coordinator and workflow node, initially acting only on actionable schema-valid review failures.
4. Enable updated-head PR rendering/projection and terminal labels.
5. Verify focused contracts and signed-HTTP system scenarios, then run the full pilot suite and strict OpenSpec validation.

Rollback removes the repair node/ports while leaving additive tables unread; existing implementation, publication, and initial review behavior remains valid.

## Open Questions

None for Issue 05. Event-driven resumption and human feedback batch semantics are intentionally deferred to Issues 08 and 06.
