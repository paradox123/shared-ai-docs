## Context

Issue 11/12 publication already owns a trusted plan, run/repository delivery locks, immutable original evidence and one draft receipt. The new section follows `independent-pr-review-verification` and `bounded-review-repair`, with PostgreSQL and the existing .NET worker as the public system seam.

## Goals / Non-Goals

**Goals:** Exact-head deterministic verification, independent structured reviews, complete invalidation on new heads, three bounded same-writer repairs, durable observations and human handoff.

**Non-Goals:** Changing the LangGraph pilot, provider approvals, automatic merge/deployment/release, or introducing another orchestration service.

## Decisions

- Add optional `headQualification` configuration to the immutable publication plan. Existing publication-only assignments remain compatible and explicitly unqualified. Validate configuration before agent work.
- Keep initial publication evidence immutable. Store a separate qualification object containing ordered head rounds, check/review observations, repair assignments, current evidence, and Human Request in the existing publication JSON. Existing history/export then retain the full result without a parallel source of truth.
- Use the existing run and repository delivery locks throughout qualification. Save dispatch identities before external effects; adapter receipts reconcile repeated review/repair calls. Interrupted deterministic work fails closed instead of repeating a possibly mutating command.
- Read local head, branch, clean worktree and provider PR head before and after verification/review and before qualification. Checks and verdicts are usable only within their head round. Invalidate readiness before dispatching a writer repair.
- Review input contains original requirements, guidance, diff, current evidence and pinned axis skills. Each fresh session gets only this shared input and its axis. Validate version, axis, head, rationale, findings, policy and unique session identity. Requirements is always applicable.
- Repair the same writer session in the same worktree. Persist the round before dispatch; require a new descendant head, recapture direct evidence, and update only the recorded draft with a conditional branch push. A publication success gap is reconciled by reading the existing draft.
- Use Terra/xhigh/read-only for reviews, Terra/xhigh for ordinary repairs and Sol/xhigh with `final_repair_round` for round three. Restrict writer tools to the admitted worktree. Unsupported policies fail before runtime launch.

## Risks / Trade-offs

- External provider state can change after any read → verify at every boundary, expose the qualified SHA, and revalidate on worker redelivery; this slice is not a webhook monitor.
- A crash can leave an external operation uncertain → retain the dispatch identity and block ambiguous receipts, never silently allocate another writer or reset the limit.
- Controlled reviewer/provider fixtures do not prove live model quality → separate deterministic integration evidence from real runtime verification and report any untested live boundary.
- Product decisions during repair require a human → preserve the writer, draft and findings in an explicit handoff; exhaustion cannot reset through redelivery.

## Migration Plan

Deploy additive code and opt new plans into qualification. Existing plans remain publication-only. Do not remove qualification state or change the immutable plan to retry an exhausted run.
