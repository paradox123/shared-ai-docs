## 1. Runtime and contract gate
- [x] 1.1 Pin the real binary/protocol and implement fail-closed disposable preflight.
- [x] 1.2 Preserve complete worker-result-v3 and separately verify its endpoint projection.
- [x] 1.3 Prove owned process cleanup and fail-closed recovery across the session-start gap.

## 2. Public evidence and real execution
- [x] 2.1 Persist correlated gate disposition through authenticated run/attempt/history read-back.
- [x] 2.2 Execute real StartFresh, Read, Resume, Fork and Interrupt/Stop with identities.
- [x] 2.3 Prove safe Open in Codex or explicitly confirmed handoff and lease-fenced interactive events under the same run.
- [x] 2.4 Execute the bounded disposable issue after all mandatory capabilities pass.

## 3. Acceptance
- [x] 3.1 Run regression checks and strict OpenSpec validation; document observed behavior and any no-go without claiming unverified acceptance.

## Implementation record — 2026-09-13

The official remote Codex TUI now opens the exact background session through the
real adapter's gateway. Native messages, PreToolUse checks and controlled MCP
execution use current repository authorization and the existing run-wide Control
Lease/fencing boundary. Direct native command/configuration bypass is rejected.

The real TUI completed the bounded greeting issue with the supplied tests passing
and interactive observations under the original run. Native interrupt, revoked
tool execution, stale-window takeover, public Resume/Fork replay and exact-session
reopening after adapter SIGKILL pass against the pinned runtime. A durable private
observation outbox retains events for non-qualifying recovery after outages.

The standalone diagnostic gate deliberately remains no-go without its own gateway;
that historical result no longer describes the full real adapter. Desktop sidebar
visibility is reported separately (`appTaskVisible:false`). No requirement change,
implicit handoff or additional user decision was needed.

Final validation passed: 143 tests in the broad opt-in regression, plus three
focused native checks including the additional double-crash recovery case
(144 distinct tests total). Locked restore, build with zero warnings/errors,
strict OpenSpec validation and the scoped diff check pass. The change is
accepted by the user and archived through the standard OpenSpec path on 2026-09-13.
