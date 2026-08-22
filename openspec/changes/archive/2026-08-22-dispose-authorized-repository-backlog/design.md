## Context

Issue 01 established a signed HTTP ingress, durable inbox, one-running-issue database constraint, a persistent LangGraph claim checkpoint, and a controlled GitHub port. Eligibility is currently a repository-specific boolean check over one event issue, so a second accepted candidate is forgotten after the active-run check and there is no way to reconcile provenance, blocker completion, or the repository frontier.

This slice turns that claim path into a small repository-neutral control plane. GitHub remains an external boundary, SQLite remains the durable local store, and the HTTP workflow interface remains the direct verification seam. The first production configuration is `probare-crm`; a second adapter exists only in tests to prove the core contract.

## Goals / Non-Goals

**Goals:**

- Define a versioned `RepositoryAdapter` whose domain-shaped outputs hide labels, allowed webhook events, provenance lookup, blocking relations, and GitHub writes from the scheduler.
- Evaluate the complete adapter-provided open backlog on each accepted repository event and persist every candidate disposition before selecting work.
- Treat human-applied `ready-for-agent` as sufficient authorization and allow agent self-authorization only from a Daniel-authored issue, linked PRD, or valid parent/child chain whose derived scope does not materially expand its mandate.
- Select candidates deterministically by issue number, serialize active implementation per repository, and retain simultaneous candidates for later reevaluation.
- Reconcile an active run to completed only when its implementation pull request is human-merged and its issue is closed, then select the next authorized, unblocked candidate in the same scheduling pass.
- Keep the public read model stable enough to observe queued, blocked, interrupted, selected, and completed outcomes across restart.

**Non-Goals:**

- Creating worktrees, running Codex, opening pull requests, merging, or deploying.
- Activating a live repository besides `probare-crm`.
- Inventing risk- or issue-type allowlists, a second start label, or a mandatory issue-body authorization section.
- Implementing Cloudflare ingress, startup reconciliation, or cross-process scheduling.
- Automatically deciding whether an unproven material scope expansion is acceptable.

## Decisions

### Make the adapter contract domain-shaped and explicitly versioned

`RepositoryAdapter` exposes its repository identity, contract version, accepted event/action pairs, current backlog snapshots, current state for one issue, and idempotent label projection. A snapshot includes issue type for observability, labels, provenance evidence, blocker completion, issue closure, and implementation-PR merge state. The workflow core compares only canonical meanings and never repository names or raw GitHub payload fields.

The production `probare-crm` binding uses a policy/configuration object for its label names and Daniel identity. A minimal second controlled adapter runs the same contract scenarios in tests without being included in application startup.

Alternative considered: add repository-name conditionals to `WorkflowRuntime`. That would make every new repository a core workflow change and would fail the portability criterion.

### Schedule the repository frontier, not just the webhook subject

Every newly accepted allowed event wakes one repository scheduling pass. The adapter returns the current backlog; the core sorts snapshots by issue number, evaluates authorization and blockers, and persists a disposition for every candidate. The webhook subject is retained for correlation but does not limit the scheduling pass. This means concurrent label events are durable wakeups rather than ephemeral attempts to acquire the active-run slot.

Alternative considered: keep dispatching only the event issue. A candidate that loses the one-running-issue race would require a later unrelated event and therefore could be lost indefinitely.

### Store dispositions as the durable queue read model

SQLite stores one current disposition per repository issue with the latest delivery identity, status, reason, and evaluation timestamp. `selected` is backed by an `issue_runs` row and LangGraph checkpoint; `queued` includes blocked and repository-busy reasons; `interrupted` records invalid provenance or a product-decision boundary. The existing partial unique index remains the final serialization guard.

Alternative considered: infer the queue on each GET solely from GitHub. That would not prove that simultaneous accepted events were retained or make restart behavior observable.

### Encode authorization as evidence plus a conservative core decision

An existing ready label authorizes every issue type. Without it, the adapter returns canonical provenance evidence: direct Daniel-authored issue, linked Daniel-authored PRD, valid Daniel-rooted parent chain, or unproven. Evidence also states whether the derived scope stays within or narrows the inherited mandate. Proven in-scope evidence causes the adapter's configured ready label to be projected before selection. Unproven evidence interrupts as `invalid-provenance`; proven ancestry with material scope expansion interrupts as `product-decision-required`.

Alternative considered: trust every agent-created issue or require a new structured mandate section. The former exceeds the human mandate; the latter contradicts the accepted use of existing issue/PRD relationships.

### Require both merge and issue closure for completion and blocker release

At the start of a scheduling pass, the runtime rereads the repository's active issue. Only `implementation_pr_merged == true` and `open == false` changes its run to completed. A blocker is resolved by the same pair of facts. Thus either event order is safe: the first event leaves work queued, while the event establishing the second fact can release the next candidate immediately.

Alternative considered: release on PR merge alone. That would violate the explicit close condition and could start a successor while the blocker remains open.

### Verify through HTTP with real persistence and controlled adapters

Behavior tests submit signed webhook events and observe the GET workflow read model plus adapter-visible label projections. SQLite and LangGraph checkpoint persistence stay real. A shared adapter contract suite is applied to `probare-crm` policy and a second fake repository. No test asserts private node ordering or raw database rows.

## Risks / Trade-offs

- [A full backlog read on every accepted event adds GitHub requests] → Keep the pilot single-repository and page through only open candidates; optimization waits for measured need.
- [Issue-number ordering is simple rather than priority-aware] → Make it the documented deterministic pilot ordering; later priority policy can remain adapter output without changing serialization semantics.
- [Relationship APIs or PRD conventions differ across repositories] → Keep raw resolution in adapters and test only the canonical versioned contract in the core.
- [A process can fail after a label write but before local projection] → Require adapter label projection to be idempotent and reevaluate persisted candidates on the next accepted event.
- [Existing local pilot databases lack disposition columns/tables] → Use additive idempotent schema migration and preserve the current inbox, runs, projections, and checkpoints.

## Migration Plan

1. Add the adapter contract, `probare-crm` policy binding, and additive SQLite disposition storage.
2. Move event authorization and scheduling from application globals into the adapter registry.
3. Drive each behavior slice through the signed HTTP interface and retain the issue-01 scenarios.
4. Start the local pilot with the single configured `probare-crm` adapter; rollback is the previous package version against the same preserved core tables, while the new disposition table can remain unused.

## Open Questions

None for this slice. Priority beyond issue-number ordering and activation of another live repository require later product decisions.
