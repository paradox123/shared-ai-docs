# Stale Next Action Orchestration Pack Fixture

Orchestration complete. This fixture intentionally routes a non-ready child to implementation.

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | `child-s1.md` | `PR1` | `NEEDS HARDENING`; fixture contract needs detail | `handoff-s1.md` | Proposed `openspec/changes/s1/` | Parent spec only | `child-s1.md`; `handoff-s1.md`; `tests/s1/**` | `git diff --check` | Closeout pending until hardening evidence exists | Re-enter hardening if ambiguous | `spec-change-delivery` may start for `S1` |

## Hardening Queue

| Order | Child | Hardening Need | Blocking Questions For Hardening |
|---|---|---|---|
| 1 | `S1` | Define fixture contract. | No product decision. |
