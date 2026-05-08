## Delivery Orchestration Pack

### Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DWT-LAUNCH-1 | `tests/agent-delivery-session-launcher/fixtures/valid-ready/child-spec.md` | Launcher automation acceptance criteria | IMPLEMENTATION READY | `child-session-handoff.md` | direct fixture ledger | self-contained launcher fixture | `skills-repo/tools/AgentDeliverySessionLauncher.cs`; `tests/agent-delivery-session-launcher/fixtures/valid-ready/**`; `tests/agent-delivery-session-launcher/fixtures/invalid-stale/**` | `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help`; `git diff --check` | `tests/agent-delivery-session-launcher/fixtures/valid-ready/evidence.json` | no deferred launcher fixture scope | `spec-change-delivery` |
