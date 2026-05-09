## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SYNC-1 | tests/sync-child-handoff/fixtures/approx-write-set/child-spec.md | SYNC-P1 handoff synchronization | IMPLEMENTATION READY | child-session-handoff.md | openspec/changes/agent-delivery-sync-child-handoff/ | none | TBD and related files etc. | `dotnet run skills-repo/tools/SyncChildHandoff.cs -- --help`; `git diff --check` | tests/sync-child-handoff/fixtures/approx-write-set/evidence.json | no deferred fixture scope | spec-change-delivery |
