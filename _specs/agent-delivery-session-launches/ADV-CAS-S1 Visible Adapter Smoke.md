**Date:** 2026-05-10
**Status:** IMPLEMENTATION READY
**Scope:** S1-local visible app-server smoke for the implemented ADV-CAS-S1 launcher adapter.

---

## Smoke Target Contract

- Target ID: `ADV-CAS-S1`
- Target Role: `workflow-step`
- Parent: `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`
- Handoff File: `_specs/agent-delivery-session-launches/adv-cas-s1-visible-smoke-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Current Verdict: `IMPLEMENTATION READY`
- Scope Summary: Reply exactly `ADV_CAS_S1_VISIBLE_SMOKE_OK` after launcher gate validation succeeds.
- Non-Goals: No implementation work; no file edits by the smoke turn; no `MD-E2E-5`; no downstream validator or archive behavior.
- Allowed Write-Set: `_specs/agent-delivery-session-launches/**`
- Shared / Read-only Files: `_specs/2026-05-09 Agent Delivery Visible Codex App Sessions.md`; `_specs/2026-05-10 Agent Delivery Visible Codex App Sessions ADV-CAS-S1 Launcher Visible App Adapter.md`
- Verification: app-server smoke evidence must show `execution_channel: app_server`, `visible_codex_app_session`, matching cwd/title, completed turn and app-server transcript method order.

## Child Index

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ADV-CAS-S1 | `_specs/agent-delivery-session-launches/ADV-CAS-S1 Visible Adapter Smoke.md` | S1-local launcher smoke evidence only | `IMPLEMENTATION READY` | `adv-cas-s1-visible-smoke-handoff.md` | `openspec/changes/agent-delivery-visible-app-launcher-adapter/` | Implemented S1 launcher adapter | `_specs/agent-delivery-session-launches/**` | Launcher app-server smoke evidence must show app-server channel, visible class, matching cwd/title, completed turn and transcript method order | `_specs/agent-delivery-session-launches/**` | This smoke is not downstream workflow completion | Run launcher visible app-server smoke only |
