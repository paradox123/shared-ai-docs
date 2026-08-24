## Context

`CodexCliWorker._execute_codex()` currently parses the final result file and every stdout JSONL line inside one exception boundary. One malformed diagnostic line therefore raises `InvalidWorkerResult` after a valid result file was already written. The workflow catches only the exception type, persists `worker execution failed`, and has no diagnostic events because the adapter never returned them. Separately, `GitWorktreeAdapter.create()` branches directly from the caller's local `main`, which can lag `origin/main` in a serialized issue workflow.

## Goals / Non-Goals

**Goals:**

- Treat the schema-constrained final result file as the authoritative result channel.
- Make diagnostic JSONL ingestion loss-tolerant and observable through bounded synthetic events.
- Preserve useful parsed diagnostics and stable failure codes for genuine result/process failures.
- Resolve a new run's configured base from a successful remote fetch and pin worktree creation and later publication comparisons to that immutable SHA.
- Keep crash adoption on the same run branch and base SHA.

**Non-Goals:**

- Retrying or implementing `probare-crm` Issue #2.
- Installing React packages, designing mailbox credentials/protocols, or changing worker sandbox permissions.
- Persisting raw malformed JSONL, arbitrary stderr, temporary files, or secrets.
- Rewriting an already-created run worktree onto a newer base during recovery.

## Decisions

### Separate result and diagnostic channels

The adapter reads and validates the final JSON object independently. JSONL lines are parsed one at a time; valid object events are retained and each malformed/non-object line becomes one bounded controller-owned diagnostic event containing only a stable code and line number. Diagnostic corruption therefore cannot invalidate an otherwise schema-valid result.

Genuine failures use a typed worker exception carrying a stable failure code plus any safely parsed diagnostic events. The workflow redacts those events and persists the stable code instead of arbitrary exception text.

### Fetch and pin before creating a new worktree

For a new run, the adapter fetches `refs/heads/<base_ref>` from `origin`, resolves `refs/remotes/origin/<base_ref>^{commit}`, and creates the run branch from that exact SHA. The returned worktree's durable base value is the SHA, so later diff/publication operations cannot silently follow a moving branch.

A pilot-owned Git ref keyed by the safe run ID records the original base for the narrow crash window between worktree creation and SQLite persistence. Adoption validates the run branch/path and reads that immutable ref; it never fetches and rebases an existing worktree.

## Risks / Trade-offs

- A malformed diagnostic line loses its raw content. This is intentional data minimization; its position and stable parse code retain the actionable distinction.
- Remote fetch failure now prevents worktree creation instead of silently using stale local state. This is fail-closed and avoids implementing on an unverified prerequisite.
- Pilot-owned base refs add small local Git metadata. They are deterministic, scoped by run ID, and necessary for crash-safe base adoption.

## Migration Plan

No database schema migration is required: the existing durable `base_ref` worktree field stores the immutable SHA for newly prepared runs. Existing records retain their historical value and remain recoverable.
