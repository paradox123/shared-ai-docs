# Ticket 05 implementation evidence

Baseline: `1875642`; owning repository: `shared-ai-docs`; user-confirmed branch: `main`.

| Contract | Direct proof |
|---|---|
| Stale local base | Real bare Git provider advances; local main remains old; public projection reports `local-base-stale`, all three SHAs, and no new session. Fetch/reset then starts at the verified SHA. |
| Git success/commit gap | SIGKILL after `update-ref`; replacement adopts the same operation; actual reflog contains exactly one operation-marked entry. |
| Provider success/commit gap | SIGKILL after external PUT; replacement reads the independently committed receipt; external count for that operation is one. |
| Session success/commit gap | SIGKILL after fake session start; concurrent replacements keep attempt/session identity and one canonical result. |
| Public recovery | Separate Operator CLI processes request Reconcile, Adopt, Retry and Retire; accepted intent survives API replacement. No runtime database edits. |
| Conflict safety | Wrong Git SHA, ambiguous provider receipts, changed adoption evidence and disappeared committed receipt become explicit human decisions. |
| Serialization and retirement | Crashed owner blocks successor; settled terminal/retired owner releases; active attempts and lease clear; late standalone delivery cannot resurrect it. |
| Authorization | Observer, non-holder, stale attempt/version/head/epoch and active-delivery mutations are rejected without business-history changes. |

Tests use actual Git repositories, a disposable PostgreSQL container, independent HTTP provider/session processes and real worker process kills. The externally written provider artifact is a controlled run marker, not a real GitHub PR. The preceding merge/closed signal is supplied by the controlled provider alongside its actual bare Git head. Local synchronization is performed explicitly by the test, never hidden in preflight.

Delivery of this graph remains explicit/local. This does not establish automatic managed DTS dispatch, live GitHub writes or real Codex session control. The separate managed durability gate is unchanged.

## Validation

Final command output and review verdicts are recorded here after the completion pass.
