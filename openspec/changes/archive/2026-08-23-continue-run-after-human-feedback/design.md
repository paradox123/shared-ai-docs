## Context

The pilot has one persistent issue run, one run-owned worktree and branch, one draft pull request, head-bound evidence and reviews, and repair batches keyed to an initial failed review batch. The signed webhook seam and its Cloudflare relay allowlist currently admit only issue-label events and store normalized delivery metadata rather than feedback content. A verified run remains `running` until a later delivery causes issue-state reconciliation; arbitrary PR activity is not yet correlated to the run's stored pull-request identity.

Issue 06 crosses webhook admission, durable state, GitHub projection, writer assignments, source publication, deterministic verification, independent review, and terminal lifecycle reconciliation. The configured human login is already the authority used by the GitHub adapter for human-rooted authorization and must also be the only feedback/merge actor accepted for continuation semantics.

## Goals / Non-Goals

**Goals:**

- Normalize authorized human PR feedback and merge deliveries without admitting arbitrary PR activity.
- Correlate by repository plus persisted pull-request number, then continue the same run, worktree, branch, and PR.
- Persist each feedback batch and its own at-most-three numbered attempts.
- Invalidate old-head qualification as soon as a new commit is published, then regenerate evidence, deterministic verification, and three reviews on that head.
- Reconcile a human merge to one durable completed state visible through the workflow GET response.
- Preserve idempotency across repeated deliveries and process restarts.

**Non-Goals:**

- Automatic merge, deployment, release, or interpretation of PR activity as approval.
- New implementation runs, worktrees, branches, or pull requests for feedback.
- Carrying earlier human comments into a later feedback batch or allowing prior review/evidence to qualify a new head.
- General crash-time continuation beyond delivery idempotency and persisted feedback outcomes (Issue 08).
- Automatic changes for feedback from bots, other users, unrelated PRs, or plain approvals without requested changes.

## Decisions

### Normalize lifecycle deliveries at the authenticated HTTP boundary

Extend the persisted delivery envelope with a redacted event payload that distinguishes issue dispatch, human feedback, and human merge. Feedback is admitted only for the supported `pull_request_review`/`pull_request_review_comment` change-request actions, the configured human login, non-empty feedback, and an existing PR identity. Merge is admitted only from the associated `pull_request.closed` payload with `merged=true` and a human merger matching the configured human. The runtime still revalidates correlation against stored run and publication state before effects.

Alternative considered: fetch all review state from GitHub after any PR event. That broadens authorization, makes duplicate semantics opaque, and risks treating activity or approvals as feedback.

### Store feedback as a first-class batch, not as another initial implementation

Add feedback-batch and feedback-attempt records keyed by run and source delivery. The batch stores only the newly normalized feedback entries, their author and source identities, the starting head, status, and a round limit of three. Each attempt retains its assignment, invocation provenance, result, produced head, fresh evidence, deterministic verification, review batch, remaining feedback/findings, and projected labels.

The assignment is built from the new feedback plus the existing implementation assignment's issue, requirements, and repository guidance. It uses the existing writing worker policy, skill routing, and run-owned write profile but never creates another worktree or initial implementation execution.

Alternative considered: model human feedback as synthetic review findings in the existing repair batch. Existing repair batches are keyed one-to-one to an initial review batch; reusing them would share counters and conflate independent human requests with reviewer findings.

### Reuse publication, verification, and review ports with explicit new-head invalidation

After a schema-valid feedback implementation, publish on the existing branch and require a SHA different from the batch's prior head. Qualify the worker's criterion-level evidence for the unchanged issue requirements, update the existing PR body with that head and feedback history, then project labels by adding `agent-running` and removing `verified` and `awaiting-review`. Persist the old review/evidence records as history but mark them superseded in the feedback read model; qualification always selects records whose head equals the current publication head.

Run deterministic verification and all three independent reviews against every produced head. A passing current head converges back to `verified` and `awaiting-review`; failure feeds only fresh findings into the next attempt in that feedback batch. Three unsuccessful attempts terminate with the existing precise `needs-info` or `ready-for-human` handoff semantics.

Alternative considered: keep verified labels until re-review completes. That exposes a stale approval window and violates commit-exact verification.

### Complete only from an explicit correlated human merge event

For `pull_request.closed`, require the persisted PR number, `merged=true`, a configured human merger, and the stored run branch/head relationship. Then mark the run and feedback lifecycle terminal and expose a completed disposition/checkpoint without launching backlog implementation from that PR delivery. Duplicate merge delivery is a no-op.

Alternative considered: infer completion from any later issue event and GitHub timeline inspection. Existing issue reconciliation remains a fallback for backlog progression, but an explicit PR merge event gives direct, auditable convergence for this capability.

### Test through signed POST and workflow GET

The stable seam is `POST /webhooks/github` followed by `GET /workflows/{owner}/{repository}/issues/{issue_number}` with real SQLite and LangGraph checkpoint persistence. Controlled GitHub, source-control, writer, verifier, and reviewer boundaries make actor, head, labels, and forbidden effects observable without asserting private node order or raw tables.

## Risks / Trade-offs

- **[Webhook payloads can contain secrets or excessive comment context]** → Normalize only the minimum supported fields, bound the body, redact before persistence, and never retain the raw payload.
- **[A feedback commit races with another PR-head change]** → Read and compare the current PR head before assignment and before verification projection; fail closed on mismatch.
- **[Label invalidation occurs after publication but later verification fails]** → Persist publication/head and converge invalidation immediately; retries are idempotent and cannot restore old verdicts.
- **[Legacy databases lack feedback tables or delivery columns]** → Use additive `CREATE TABLE IF NOT EXISTS` migration and backward-compatible nullable/defaulted fields.
- **[One delivery can contain only part of a review conversation]** → Treat each accepted delivery as one explicit batch; later accepted deliveries create independent batches and counters.
- **[Synchronous controlled tests hide production duration]** → Keep orchestration behind the existing background task and worker ports; general interrupted-run recovery remains Issue 08.

## Migration Plan

1. Add backward-compatible persistence and normalized delivery handling.
2. Deploy read-path support before enabling new allowed event/action pairs in repository settings and the Cloudflare relay allowlist.
3. Enable feedback and merge actions after focused adapter, relay-ingress, and signed-HTTP tests pass.
4. Roll back by restoring the prior allowed-event set and runtime; additive historical records remain inert and no source or PR is deleted.

## Open Questions

None for Issue 06. General crash-time continuation and queue wake-up semantics remain assigned to Issue 08.
