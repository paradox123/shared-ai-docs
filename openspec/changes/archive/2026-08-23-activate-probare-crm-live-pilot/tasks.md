## 1. Change Gate

- [x] 1.1 Strictly validate the active change before any live activation or runtime implementation.

## 2. Test-Driven Activation Tooling

- [x] 2.1 Add a failing public CLI contract for the shared production activation profile and secret-safe read-only live readiness, then implement adapter/version, checkout/origin/base, GitHub permission, label, webhook event-group, relay-route, and complete-backlog checks without repository paths in the workflow core.
- [x] 2.2 Add a failing public CLI contract for explicit idempotent workflow-label bootstrap, then implement creation of missing definitions only and prove that existing labels and issue assignments are preserved.
- [x] 2.3 Add a failing public CLI contract for exact-head evidence capture, then implement allowlisted redacted correlation output that requires deterministic verification, all three fresh reviews, current PR head/body, and converged workflow labels.
- [x] 2.4 Wire `pilotctl` operator commands to the tested pilot CLI modes, document activation/monitoring/rollback, and retain bounded fixed-schema output without secret or external-body leakage.

## 3. Live Activation and Direct Proof

- [x] 3.1 Run local tests and quality checks, verify the real private configuration read-only, idempotently bootstrap only missing workflow labels, confirm the GitHub webhook plus Cloudflare Queue/DLQ/Tunnel route, and start the current macOS LaunchAgent generation.
- [x] 3.2 Record the unfiltered live backlog readiness and prove blockers plus one-active-run serialization, then allow the deterministic eligible frontier issue to start from a real signed GitHub event without another product approval signal.
- [x] 3.3 Follow one real delivery through Queue, Tunnel, inbox, LangGraph, isolated worktree, deterministic verification, repair if needed, and all three independent reviews until it reaches either an exact-head verified draft PR or a truthful human-handoff state.
- [x] 3.4 For a successful run, capture the redacted correlation manifest and verify the current PR has `verified` and `awaiting-review`, lacks `agent-running`, and embeds the criterion matrix plus decisive evidence; prove that no merge, deployment, or release occurred.

## 4. Closeout

- [x] 4.1 Refactor touched code, tests, docs, and specs for DRY, SOLID, and KISS issues while preserving behavior, then rerun focused and complete checks.
- [x] 4.2 Record criterion-level implementation/live evidence, update issue 12 truthfully, run `git diff --check`, and strictly validate the completed active change without archiving it.
