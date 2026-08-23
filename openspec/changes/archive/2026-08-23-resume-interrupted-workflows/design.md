## Context

The pilot acknowledges webhook deliveries only after SQLite persistence and uses each run ID as its LangGraph thread ID. Implementation, publication, review, repair, and feedback records are also durable, but execution is started only from the webhook background task. A process exit can therefore leave a `running`, `publishing`, or `pending` record with no startup continuation. Re-entering current nodes is also unsafe in several places because they create a worktree or invoke a worker/reviewer before checking an existing durable result.

The recovery boundary spans SQLite, LangGraph checkpoints, the deterministic run worktree/branch, and idempotent GitHub adapters. The database remains authoritative for correlation and terminality; Git/GitHub read-back resolves effects that may have completed just before a crash.

## Goals / Non-Goals

**Goals:**

- Resume every active run automatically during application startup before accepting new deliveries.
- Preserve one run, LangGraph thread, worktree, branch, draft PR, head, repair batch, feedback batch, and deterministic operation identity.
- Make every graph node and coordinator re-entrant: completed durable results are reused; incomplete operations reconcile their bounded external state and retry only under the same operation identity.
- Expose redacted recovery status and phase events through the existing workflow read model.
- Prove crash recovery through a real terminated/restarted process and signed HTTP observation.

**Non-Goals:**

- Distributed multi-host execution, concurrent recovery leaders, or a general job queue.
- Resuming an operating-system process or a partially generated Codex response in memory.
- Creating replacement runs, worktrees, branches, or pull requests during recovery.
- Merging, deploying, releasing, or changing the existing three-round limits.

## Decisions

### Treat existing phase records as durable operation ledgers

Each externally active phase receives or reuses a stable operation key derived from persisted identities (`run_id`, head SHA, review axis, repair/feedback batch and round). Recovery consults the existing stage record before invoking an external port. A completed stage is returned without another invocation; an incomplete stage is retried under the same key and existing ownership.

This extends the existing storage model instead of adding a second workflow engine. A separate generic outbox was considered, but it would duplicate domain state and still require phase-specific reconciliation.

### Recover at application startup and remain re-entrant afterward

The FastAPI lifespan calls `WorkflowRuntime.recover()` before yielding. Recovery enumerates active runs, first honors terminal merge completion, then resumes unfinished graph work from the persisted LangGraph thread and unfinished feedback/coordinator work from its durable batch records. Nodes also check their durable outputs so a crash between a domain commit and the following LangGraph checkpoint cannot repeat the effect.

Startup recovery was chosen over waiting for another webhook because recovery must not depend on unrelated traffic. Recovery remains callable and idempotent so tests and future supervision can safely repeat it.

### Reconcile deterministic Git/GitHub resources; retry opaque workers under one identity

The run ID deterministically owns the worktree path and branch. Worktree preparation adopts a valid pre-existing run worktree instead of creating another. Publication reuses the same pushed branch and draft PR lookup. Label projection remains set-convergent. Reviewer results, repair invocations, and feedback attempts are read before invocation so already persisted results are never run again.

If the process died while an opaque Codex subprocess was executing and no valid result was committed, recovery may start that same durable operation again in the same worktree. The operation is not counted as a new workflow/round and all downstream publication remains idempotent. This is the only safe local resolution because the killed process has no queryable result service.

### Record bounded recovery diagnostics

A recovery table stores only generated event ID, run ID, phase, stable operation key, outcome code, and timestamp. It stores no webhook body, assignment, feedback text, source diff, token, email, secret, or arbitrary exception string. Workflow read-back exposes the current recovery status and ordered bounded events.

### Terminal completion wins over all resumable state

`issue_runs.status = completed` plus its human-merge completion record is authoritative. Startup never reconstructs graph/coordinator work for a completed run, even if an earlier phase row still says `running` because the process died after terminal reconciliation.

## Risks / Trade-offs

- [An opaque worker can be killed after modifying files but before persisting a result] → Retry only the same operation in the same run-owned worktree and require fresh evidence/verification before publication.
- [A Git or GitHub call can complete immediately before process death] → Re-read deterministic branch, PR-head, and label state and use existing idempotent ensure/update operations.
- [Schema migration runs against existing pilot databases] → Use additive `CREATE TABLE IF NOT EXISTS` and indexes; do not rewrite existing domain rows.
- [Startup recovery can be slow because worker phases are synchronous] → Recovery completes before accepting new work, preserving the single-active-run invariant; its status remains observable after startup.
- [Recovery loops could consume repair/feedback rounds twice] → Existing unique batch/round keys are authoritative and completed attempts are folded into continuation state before selecting the next round.

## Migration Plan

1. Deploy the additive recovery schema and re-entrant stage logic.
2. On the first startup, enumerate existing active runs and reconcile them using their stored checkpoints and stage records.
3. Verify the signed HTTP workflow read-back and external effect counts after a forced process termination/restart.
4. Roll back application code if necessary; the additive recovery rows are inert for older code and existing workflow data remains readable.

## Open Questions

None for this local single-process pilot slice.
