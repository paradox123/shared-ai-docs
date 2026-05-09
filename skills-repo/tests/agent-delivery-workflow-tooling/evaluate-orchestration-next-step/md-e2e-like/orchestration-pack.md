# MD-E2E-Like Orchestration Pack Fixture

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MD-E2E-1 | `_specs/md-e2e-1.md` | `MD-PR1`, `MD-PR2`, `MD-PR3` | `NEEDS HARDENING` | `_specs/child-session-handoffs/md-e2e-1-session-handoff.md` | Proposed `openspec/changes/md-e2e-1/` | Parent spec only | `_specs/md-e2e-1.md`; `tests/mock-data/**` | `git diff --check` | none yet | Re-enter hardening if fixture contract is ambiguous | Start `child-spec-hardening` for `MD-E2E-1` first |
| MD-E2E-2 | `_specs/md-e2e-2.md` | `MD-PR4`, `MD-PR5`, `MD-PR6` | `NEEDS HARDENING` | `_specs/child-session-handoffs/md-e2e-2-session-handoff.md` | Proposed `openspec/changes/md-e2e-2/` | `MD-E2E-1` fixture contract accepted or frozen | `_specs/md-e2e-2.md`; `tests/e2e/**` | runner commands after hardening | none yet | Re-enter after `MD-E2E-1` | Harden after `MD-E2E-1` |
| MD-E2E-3 | `_specs/md-e2e-3.md` | `MD-PR1`, `MD-PR7` | `NEEDS HARDENING` | `_specs/child-session-handoffs/md-e2e-3-session-handoff.md` | Proposed `openspec/changes/md-e2e-3/` | `MD-E2E-1`; `MD-E2E-2` runner command stable | `_specs/md-e2e-3.md`; `tests/scripts/**` | standard gate commands after hardening | none yet | Re-enter after runner contract | Harden after `MD-E2E-2` |
| MD-E2E-4 | `_specs/md-e2e-4.md` | `MD-PR8` | `NEEDS HARDENING` | `_specs/child-session-handoffs/md-e2e-4-session-handoff.md` | Proposed `openspec/changes/md-e2e-4/` | `MD-E2E-1` through `MD-E2E-3` accepted for final sync | `_specs/md-e2e-4.md`; `tests/README.md` | docs checks after evidence exists | none yet | Can partially draft in parallel as docs-only; final sync waits | Draft-only parallel work is safe, final sync waits |
| MD-E2E-5 | `_specs/md-e2e-5.md` | `MD-PR9` | `DEFERRED FOLLOW-UP` | `_specs/child-session-handoffs/md-e2e-5-session-handoff.md` | Future `openspec/changes/md-e2e-5/` | `MD-E2E-1` through `MD-E2E-4` accepted | `_specs/md-e2e-5.md` | future only | none | Future follow-up only | Do not start until local baseline is accepted |

