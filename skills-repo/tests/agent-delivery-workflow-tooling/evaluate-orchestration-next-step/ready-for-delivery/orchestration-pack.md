# Ready For Delivery Orchestration Pack Fixture

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MD-E2E-1 | `_specs/md-e2e-1.md` | `MD-PR1`, `MD-PR2`, `MD-PR3` | `IMPLEMENTATION READY` | `_specs/child-session-handoffs/md-e2e-1-session-handoff.md` | Proposed `openspec/changes/md-e2e-1/` | Parent spec only | `_specs/md-e2e-1.md`; `tests/mock-data/**` | `git diff --check` | hardening evidence retained | none | Start `spec-change-delivery` for `MD-E2E-1` |
| MD-E2E-2 | `_specs/md-e2e-2.md` | `MD-PR4`, `MD-PR5`, `MD-PR6` | `NEEDS HARDENING` | `_specs/child-session-handoffs/md-e2e-2-session-handoff.md` | Proposed `openspec/changes/md-e2e-2/` | `MD-E2E-1` accepted | `_specs/md-e2e-2.md`; `tests/e2e/**` | runner commands after hardening | none yet | Re-enter after `MD-E2E-1` | Harden after `MD-E2E-1` |

