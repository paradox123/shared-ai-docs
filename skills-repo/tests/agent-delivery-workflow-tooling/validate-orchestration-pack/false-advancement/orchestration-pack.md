# False Advancement Orchestration Pack Fixture

Workflow advanced to child hardening and hardening started for `S1`.

Only queue and handoff artifacts exist in this fixture; there is no launch or hardening evidence.

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | `child-s1.md` | `PR1` | `NEEDS HARDENING`; fixture contract needs detail | `handoff-s1.md` | Proposed `openspec/changes/s1/` | Parent spec only | `child-s1.md`; `handoff-s1.md`; `tests/s1/**` | `git diff --check` | Closeout pending until hardening evidence exists | Re-enter hardening if ambiguous | Run `child-spec-hardening` for `S1` |

## Hardening Queue

| Order | Child | Hardening Need | Blocking Questions For Hardening |
|---|---|---|---|
| 1 | `S1` | Define fixture contract. | No product decision. |
