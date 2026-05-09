# Valid Orchestration Pack Fixture

Orchestration complete. Queue and handoffs were created; follow-up sessions still own hardening or delivery.

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | `child-s1.md` | `PR1` | `IMPLEMENTATION READY`; hardening completed for fixture contract | `handoff-s1.md` | `openspec/changes/s1/` | Parent spec only | `child-s1.md`; `handoff-s1.md`; `tests/s1/**` | `git diff --check` | Closeout pending until implementation evidence is captured | Re-enter hardening if implementation discovers contract ambiguity | `spec-change-delivery` may start for `S1` |
| S2 | `child-s2.md` | `PR2` | `NEEDS HARDENING`; runner contract needs detail | `handoff-s2.md` | Proposed `openspec/changes/s2/` | `S1` accepted or frozen | `child-s2.md`; `handoff-s2.md`; `tests/s2/**` | Hardened commands after child-spec-hardening | Closeout pending until hardening evidence exists | Re-enter after `S1` delivery evidence | Run `child-spec-hardening` for `S2` after `S1` |
| S3 | `child-s3.md` | `PR3` | `DEFERRED FOLLOW-UP`; optional extension only | `handoff-s3.md` | Future `openspec/changes/s3/` | `S1` and `S2` accepted | `child-s3.md`; `handoff-s3.md` | Future only after baseline closeout | Future closeout evidence only | Future follow-up only | Do not start until local baseline is accepted |

## Hardening Queue

| Order | Child | Hardening Need | Blocking Questions For Hardening |
|---|---|---|---|
| complete | `S1` | Hardening complete; ready for one-child implementation. | No blocking hardening questions remain. |
| 2 | `S2` | Define runner contract. | Exact command and evidence shape. |
| deferred | `S3` | Optional follow-up. | Future provider decision. |
