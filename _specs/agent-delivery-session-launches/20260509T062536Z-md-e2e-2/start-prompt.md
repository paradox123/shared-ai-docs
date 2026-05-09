Session Title: MD-E2E-2 child-spec-hardening - harden the local mock

Wir arbeiten in /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs.

Starte eine frische Agent-Delivery-Session aus folgendem persistierten Handoff.

Pflicht: Lies zuerst das Handoff, den Control Index / die Queue und das Target-Artefakt. Validiere, dass Target-ID, Target-Rolle, Handoff-Pfad, Control Index, aktueller Verdict, Target Workspace und Allowed Write-Set konsistent sind. Arbeite nur im erlaubten Write-Set. Wenn ein Gate stale, widerspruechlich oder unvollstaendig ist, stoppe mit NOT READY und persistiere Evidence statt zu implementieren.

- Parent: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md
- Target ID: MD-E2E-2
- Target Role: child
- Target Spec: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md
- Control Index / Queue: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md
- Handoff File: _specs/child-session-handoffs/md-e2e-2-session-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Project CWD / App-Kontext: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Session Title: MD-E2E-2 child-spec-hardening - harden the local mock
- Next Mode / Skill: child-spec-hardening for MD-E2E-2 after MD-E2E-1 acceptance.
- Requested Agent Provider: codex
- Agent Adapter Status: supported; codex-cli
- Current Verdict: NEEDS HARDENING; runner contracts, command selectors and evidence schema need implementation-ready detail
- Scope Summary: Harden the local mock session runner and run-mock-e2e-checks.sh large/small/all contract, consuming the accepted MD-E2E-1 fixture/manifests/validator contracts and defining large/small E2E evidence, session state machine and output assertions.
- Non-Goals: No base fixture creation beyond compatibility fixes, no legacy standard gate migration, no docs closeout sync, no live-agent/Codex execution.
- Allowed Write-Set: _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md; _specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md; _specs/child-session-handoffs/md-e2e-2-session-handoff.md; tests/docworkflow-agent-delivery/e2e/**; tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh; tests/docworkflow-agent-delivery/mock-data/** only for accepted MD-E2E-1 compatibility fixes.
- Shared / Read-only Files: tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh; tests/docworkflow-agent-delivery/scripts/setup-fixture.sh; tests/docworkflow-agent-delivery/README.md; accepted DWT harnesses and evidence; KI-fuer-KMU and real product repositories.
- Verification Commands: Rehearsal / Preflight: confirm MD-E2E-1 accepted; git diff --check. Delivery Gate: bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh; tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep; small --keep; all --keep. Pre-Archive Closeout: retain summaries and session/output evidence. Post-Archive / Current Replay: not available yet.
- Evidence / OpenSpec: proposed ledger openspec/changes/docworkflow-agent-mock-e2e-md-e2e-2-local-runner/; not created in orchestration pass.
- Open Notes: MD-E2E-1 fixture contract is accepted. Network, Docker, Codex auth or manual-start dependency is out of scope for the local baseline.

## Persisted Handoff

## Child Session Handoff

- Parent: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness.md`
- Child: `MD-E2E-2`
- Child Spec: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md`
- Child Index / Queue: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md` section `Child Index`
- Handoff File: `_specs/child-session-handoffs/md-e2e-2-session-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Codex Session / Log: not created; delivery launch is blocked until hardening verdict exists.
- Session Evidence: no launch evidence yet; `MD-E2E-1` acceptance unblocks hardening start.
- Handoff Timestamp: 2026-05-09
- Naechster Modus/Skill: `child-spec-hardening` for `MD-E2E-2` after MD-E2E-1 acceptance.
- Aktueller Verdict: NEEDS HARDENING; not implementation-ready.
- Scope Summary: Harden the local mock session runner and `run-mock-e2e-checks.sh large/small/all` contract, consuming the accepted `MD-E2E-1` fixture/manifests/validator contracts and defining large/small E2E evidence, session state machine and output assertions.
- Non-Goals: No base fixture creation beyond compatibility fixes, no legacy standard gate migration, no docs closeout sync, no live-agent/Codex execution.
- Allowed Write-Set: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness MD-E2E-2 Local Mock Session Runner.md`; `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md`; `_specs/child-session-handoffs/md-e2e-2-session-handoff.md`; `tests/docworkflow-agent-delivery/e2e/**`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/mock-data/**` only for accepted MD-E2E-1 compatibility fixes.
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`; `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`; `tests/docworkflow-agent-delivery/README.md`; accepted DWT harnesses and evidence; KI-fuer-KMU and real product repositories.
- Verification Commands: Rehearsal / Preflight: confirm MD-E2E-1 accepted; `git diff --check`. Delivery Gate: `bash -n tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`; `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh large --keep`; `small --keep`; `all --keep`. Pre-Archive Closeout: retain summaries and session/output evidence. Post-Archive / Current Replay: not available yet.
- Evidence / OpenSpec: proposed ledger `openspec/changes/docworkflow-agent-mock-e2e-md-e2e-2-local-runner/`; not created in orchestration pass.
- Retained Evidence: none yet.
- Offene Blocker oder non-blocking Notes: MD-E2E-1 fixture contract is accepted. Network, Docker, Codex auth or manual-start dependency is out of scope for the local baseline.
- Fresh Session empfohlen: Yes.

