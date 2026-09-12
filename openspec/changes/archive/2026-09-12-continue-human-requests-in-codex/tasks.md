## 1. Durable continuation model

- [x] 1.1 Add versioned Human Request, decision, session-lineage and interaction contracts plus safe PostgreSQL schema evolution.
- [x] 1.2 Persist a blocked fake attempt's Human Request and expose per-attempt session lineage without changing existing attempt history.
- [x] 1.3 Extend the controlled fake adapter with truthful open, continuation, handoff and write receipts that support independent lookup/adoption.

## 2. Fenced Operator operations

- [x] 2.1 Add atomic, provider-authorized and lease-fenced idempotent Resume, Fork, Fresh Retry and confirmed Handoff decisions.
- [x] 2.2 Add side-effect-bounded selected-session opening and lease-fenced interactive write operations to the public API and CLI.
- [x] 2.3 Recover persisted continuation/interaction intents after API or worker replacement without duplicate adapter effects.

## 3. Behavioral proof

- [x] 3.1 Add public multi-process black-box coverage for durable request context and the Resume/Fork/Fresh Retry lineage contract.
- [x] 3.2 Add public black-box coverage for truthful opening/handoff, lease/fence rejection, write-back history and exactly-once recovery.

## 4. Verification and evidence

- [x] 4.1 Update pilot operating documentation and record concise implementation evidence with direct public proof.
- [x] 4.2 Run locked restore/build, targeted and full regression suites, strict OpenSpec validation, diff checks, and two-axis review; resolve findings.
