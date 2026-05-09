# All Blocked Orchestration Pack Fixture

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MD-E2E-2 | `_specs/md-e2e-2.md` | `MD-PR4`, `MD-PR5`, `MD-PR6` | `NEEDS HARDENING` | `_specs/child-session-handoffs/md-e2e-2-session-handoff.md` | Proposed `openspec/changes/md-e2e-2/` | `MD-E2E-1` fixture contract accepted or frozen | `_specs/md-e2e-2.md`; `tests/e2e/**` | runner commands after hardening | none yet | Re-enter after `MD-E2E-1` | Harden after `MD-E2E-1` |
| MD-E2E-3 | `_specs/md-e2e-3.md` | `MD-PR1`, `MD-PR7` | `NEEDS HARDENING` | `_specs/child-session-handoffs/md-e2e-3-session-handoff.md` | Proposed `openspec/changes/md-e2e-3/` | `MD-E2E-2` runner command stable | `_specs/md-e2e-3.md`; `tests/scripts/**` | standard gate commands after hardening | none yet | Re-enter after runner contract | Harden after `MD-E2E-2` |

