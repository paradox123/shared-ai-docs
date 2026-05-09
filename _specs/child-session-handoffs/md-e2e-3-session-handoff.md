## Child Session Handoff

- Parent: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`
- Child: `MD-E2E-3`
- Child Spec: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`
- Child Index / Queue: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md` section `Child Index`
- Handoff File: `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Codex Session / Log: not created; delivery launch is blocked until hardening verdict exists.
- Session Evidence: no launch evidence; orchestration-only handoff.
- Handoff Timestamp: 2026-05-09
- Naechster Modus/Skill: `child-spec-hardening` for `MD-E2E-3` after MD-E2E-2 runner contract stabilizes.
- Aktueller Verdict: NEEDS HARDENING; not implementation-ready.
- Scope Summary: Harden the migration/deactivation plan for old standard gates so default Agent Delivery checks use mock data and no KI-fuer-KMU compatibility fixture remains.
- Non-Goals: No fixture authoring, no runner internals, no broad historical rewrite, no final docs closeout beyond command references needed for standard gate behavior.
- Allowed Write-Set: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`; `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/README.md` only for command references directly coupled to standard gate behavior.
- Shared / Read-only Files: accepted `tests/docworkflow-agent-delivery/mock-data/**`; accepted `tests/docworkflow-agent-delivery/e2e/**`; DWT retained evidence; KI-fuer-KMU and real product repositories.
- Verification Lifecycle:
  - Rehearsal / Preflight: inspect current default KI-fuer-KMU references and freeze allowed historical references.
  - Delivery Gate: `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep`; selected standard `all` command; no-default-KI-fuer-KMU guard.
  - Pre-Archive Closeout: evidence that legacy real fixture default is removed/replaced/non-gating.
  - Post-Archive / Current Replay: not available yet.
- Evidence / OpenSpec: proposed ledger `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/`; not created in orchestration pass.
- Retained Evidence: none yet.
- Offene Blocker oder non-blocking Notes: Exact migration strategy is not frozen. Do not keep KI-fuer-KMU as default, fallback or compatibility mode.
- Fresh Session empfohlen: Yes.

