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

- `dotnet build Wpcp.WorkPackageControlPlane.sln --no-restore`: passed, zero warnings/errors.
- `python3 -m unittest discover -s tests -v`: **59/59 passed in 70.610 seconds**, including 17 Ticket 05 tests.
- `openspec validate reconcile-repository-effects --strict`: passed.
- `git diff --check`: passed.
- Independent [Standards and Spec reviews](review.md): **0 open findings** after fixes; Spec reviewer independently repeated 5 regression tests.

The completed [compact proof](../../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-05-proof-2026-09-11/proof.md) links the raw public snapshots, effect receipts, process exit codes and complete test output. Machine evidence was collected against implementation commit `c4147a4` on `main`. Each central Git/provider/session crash proof reports `adopted`, worker exit `-9`, and an independently observed operation count of exactly one.

## Acceptance and archive

2026-09-11: Explicit user acceptance. Pre-archive DRY/SOLID/KISS review of the implementation diff and nearby code found no further refactoring needed. The 17 Ticket 05 tests passed again (63.512 seconds). Standard CLI archive synchronized all five requirements into the canonical specification.

Post-archive validation: `openspec validate --all --strict --no-interactive` passed **39/39** items; archive state and local Markdown links verified.
