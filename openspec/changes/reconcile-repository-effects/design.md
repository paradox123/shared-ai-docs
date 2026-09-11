## Context

Owning root: `shared-ai-docs`; clean baseline `1875642`; user-confirmed delivery branch: `main`. Ticket 04 is committed and archived. Its PostgreSQL history, Agent Framework graph and independently durable fake session adapter are the foundations. This ticket adds repository execution, not live Codex or publication.

## Goals / Non-Goals

Goals: exact authoritative base checks, stable effect intents and receipts, explicit recovery decisions, repository serialization that survives worker death, and public process-level proof.

Non-goals: automatic DTS dispatch, real GitHub writes, PR creation/merge, resume/fork/fresh conversation retry, and modifying the LangGraph pilot. A controlled provider contract is the external provider-write seam for this slice.

## Decisions

- A worker-supplied repository plan is pinned against the admitted repository identity. Repository configuration is immutable once registered. Local Git path, remote, base branch and controlled HTTP origins are trusted service configuration, never Operator request parameters. Existing unconfigured Ticket 04 tests remain supported; once a repository is registered the standalone fake path cannot bypass repository execution.
- Record expected SHA, provider head, local base and predecessor completion before writes. Read provider state and actual Git refs; do not trust a caller-supplied observation. Retry may refresh an expected base only before any effect intent exists. Fetch/update of the local base remains an explicit repository operation outside this worker. Provider and local heads must agree again immediately before missing effects or a new session start.
- Persist a repository owner separately from the worker connection lock. A crashed owner retains its slot. PostgreSQL advisory delivery locks prevent simultaneous workers and fence Operator decisions against an in-flight delivery. Terminal settled outcomes release the slot and clear active projections; unresolved effects retain ownership until reconciliation or a safe retirement.
- Before each controlled effect persist its stable operation ID and immutable intent. Git creates a run-specific branch with compare-and-swap and an operation-marked reflog receipt. Provider writes use a versioned idempotent HTTP boundary with independent receipts. Session creation retains Ticket 04's attempt operation key and receipt. Recovery reads existing effects before issuing missing work.
- Normal replacement adopts a unique matching effect automatically. Reconcile is read-only externally and surfaces missing, adoptable or conflicting receipts. Adopt rereads and validates the selected receipt; it cannot override incompatible intent. Retry resumes missing work with the same IDs, not a fresh conversation. Retire only releases a stopped run after pending effects have been settled; ambiguity becomes a concrete human decision.
- Operator commands reuse fresh provider authorization, holder identity, attempt/version/head/epoch fences and canonical history. Commands queue durable recovery intent for explicit worker delivery; the API never performs Git or provider writes. Read projections expose the selected action, base evidence, operation IDs, receipts and active ownership.

## Risks / Trade-offs

- External success cannot share a PostgreSQL transaction → independent receipts, deterministic lookup, real SIGKILL at each success/commit gap and concurrent redelivery tests.
- Provider state can change → reread before new effects, block on changed base, never rebase an existing intent silently. This is a point-in-time preflight, not a lock on third-party repository administration.
- A generic provider response is not evidence → validate contract, repository, operation, kind and SHA; redact before history and expose sanitized failure codes.
- Explicit local delivery is not scheduler durability → state this limit in evidence and retain the separate managed DTS proof.

## Migration Plan

Add repository ownership and execution-journal tables. Historical unconfigured runs remain readable. Opt into the repository plan for this bounded execution slice; once registered, the repository cannot run unfenced through the legacy fake invocation. Rollback stops repository deliveries and retains journals/history. No live database or repository migration is performed.
