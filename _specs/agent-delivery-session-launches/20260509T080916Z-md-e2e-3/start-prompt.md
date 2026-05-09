Session Title: MD-E2E-3 spec-change-delivery - migrate deactivate old standard

Wir arbeiten in /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs.

Starte eine frische Agent-Delivery-Session aus folgendem persistierten Handoff.

Pflicht: Lies zuerst das Handoff, den Control Index / die Queue und das Target-Artefakt. Validiere, dass Target-ID, Target-Rolle, Handoff-Pfad, Control Index, aktueller Verdict, Target Workspace und Allowed Write-Set konsistent sind. Arbeite nur im erlaubten Write-Set. Wenn ein Gate stale, widerspruechlich oder unvollstaendig ist, stoppe mit NOT READY und persistiere Evidence statt zu implementieren.

- Parent: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md
- Target ID: MD-E2E-3
- Target Role: child
- Target Spec: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md
- Control Index / Queue: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md
- Handoff File: _specs/child-session-handoffs/md-e2e-3-session-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Project CWD / App-Kontext: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Session Title: MD-E2E-3 spec-change-delivery - migrate deactivate old standard
- Next Mode / Skill: spec-change-delivery for MD-E2E-3
- Requested Agent Provider: codex
- Agent Adapter Status: supported; codex-cli
- Current Verdict: IMPLEMENTATION READY; migration strategy frozen: mock all --keep is leading standard, run-contract-checks.sh all can only survive as mock-only shim or non-leading legacy command, no KI-fuer-KMU default/fallback/compatibility fixture remains
- Scope Summary: Migrate/deactivate old standard Agent Delivery gates so the leading standard command is mock-only and no KI-fuer-KMU default, fallback or compatibility fixture remains.
- Non-Goals: No new fixture authoring; no accepted MD-E2E-1 mock-data contract edits; no MD-E2E-2 runner internals beyond standard routing integration; no broad DWT historical rewrite; no final parent/canonical docs closeout beyond README command references directly coupled to standard gate behavior; no live-agent/Codex execution.
- Allowed Write-Set: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md; _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md; _specs/child-session-handoffs/md-e2e-3-session-handoff.md; openspec/changes/docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/**; tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh; tests/docworkflow-agent-delivery/scripts/setup-fixture.sh; tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh; tests/docworkflow-agent-delivery/README.md
- Shared / Read-only Files: tests/docworkflow-agent-delivery/mock-data/**; tests/docworkflow-agent-delivery/e2e/mock-runner/**; tests/docworkflow-agent-delivery/e2e/validators/**; accepted MD-E2E-1 and MD-E2E-2 archived OpenSpec evidence; KI-fuer-KMU and all other real product repositories; retained DWT historical evidence.
- Verification Commands: Rehearsal completed: bash -n tests/docworkflow-agent-delivery/scripts/*.sh; tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id hardening-md-e2e-3-rehearsal; run-contract-checks.sh --help; setup-fixture.sh --help; node --version; .NET 10 SDK present; rg preflight found current forbidden defaults. Delivery gate: bash -n tests/docworkflow-agent-delivery/scripts/*.sh; tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-3-mock-all; tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep; no-default-KI-fuer-KMU guards over scripts and README; openspec validate docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration --strict; ValidateChildReadiness.cs; git diff --check. Pre-Archive Closeout: evidence that legacy real fixture default is removed/replaced/non-gating and no compatibility fixture remains. Post-Archive / Current Replay: not available yet.
- Evidence / OpenSpec: proposed ledger openspec/changes/docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/; hardening mock-runner rehearsal evidence at tests/docworkflow-agent-delivery/e2e/evidence/hardening-md-e2e-3-rehearsal/mock-e2e-summary.json; Agent Delivery queue evidence pending hardening closeout.
- Open Notes: None. Current scripts still contain forbidden defaults; removing them is the implementation work authorized by this handoff.

## Persisted Handoff

## Child Session Handoff

- Parent: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`
- Child: `MD-E2E-3`
- Child Spec: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`
- Child Index / Queue: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md` section `Child Index`
- Handoff File: `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Codex Session / Log: not created for implementation; hardening handoff only.
- Session Evidence: Agent Delivery queue evidence will be created by hardening closeout before implementation starts.
- Handoff Timestamp: 2026-05-09
- Next Mode / Skill: `spec-change-delivery` for `MD-E2E-3`
- Aktueller Verdict: IMPLEMENTATION READY
- Scope Summary: Migrate/deactivate old standard Agent Delivery gates so the leading standard command is mock-only and no KI-fuer-KMU default, fallback or compatibility fixture remains.
- Non-Goals: No new fixture authoring; no accepted MD-E2E-1 mock-data contract edits; no MD-E2E-2 runner internals beyond standard routing integration; no broad DWT historical rewrite; no final parent/canonical docs closeout beyond README command references directly coupled to standard gate behavior; no live-agent/Codex execution.
- Allowed Write-Set: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-3 Standard Gate Migration.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; `_specs/child-session-handoffs/md-e2e-3-session-handoff.md`; `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/**`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`; `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/README.md`
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/mock-data/**`; `tests/docworkflow-agent-delivery/e2e/mock-runner/**`; `tests/docworkflow-agent-delivery/e2e/validators/**`; accepted MD-E2E-1 and MD-E2E-2 archived OpenSpec evidence; KI-fuer-KMU and all other real product repositories; retained DWT historical evidence.
- Verification Lifecycle: Rehearsal completed: `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id hardening-md-e2e-3-rehearsal`; `run-contract-checks.sh --help`; `setup-fixture.sh --help`; `node --version`; `.NET 10 SDK present`; `rg` preflight found current forbidden defaults. Delivery gate: `bash -n tests/docworkflow-agent-delivery/scripts/*.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh all --keep --run-id closeout-md-e2e-3-mock-all`; `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh all --keep`; no-default-KI-fuer-KMU guards over scripts and README; `openspec validate docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration --strict`; `ValidateChildReadiness.cs`; `git diff --check`. Pre-Archive Closeout: evidence that legacy real fixture default is removed/replaced/non-gating and no compatibility fixture remains. Post-Archive / Current Replay: not available yet.
- Evidence / OpenSpec: proposed ledger `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration/`; hardening mock-runner rehearsal evidence at `tests/docworkflow-agent-delivery/e2e/evidence/hardening-md-e2e-3-rehearsal/mock-e2e-summary.json`; Agent Delivery queue evidence pending hardening closeout.
- Retained Evidence: MD-E2E-2 accepted runner evidence at `tests/docworkflow-agent-delivery/e2e/evidence/closeout-md-e2e-2-all/aggregate-summary.json`; MD-E2E-3 hardening rehearsal evidence at `tests/docworkflow-agent-delivery/e2e/evidence/hardening-md-e2e-3-rehearsal/mock-e2e-summary.json`.
- Offene Blocker oder non-blocking Notes: None. Current scripts still contain forbidden defaults; removing them is the implementation work authorized by this handoff.
- Fresh Session empfohlen: Yes; start a fresh `spec-change-delivery` implementation session from this handoff.

