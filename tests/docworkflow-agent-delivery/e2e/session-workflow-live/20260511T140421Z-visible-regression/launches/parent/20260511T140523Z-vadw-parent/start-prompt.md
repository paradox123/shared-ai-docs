Session Title: VADW-PARENT: Implementation - VADW-PARENT Start a fresh visible regression test

Wir arbeiten in /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs.

Starte eine frische Agent-Delivery-Session aus folgendem persistierten Handoff.

Pflicht: Lies zuerst das Handoff, den Control Index / die Queue und das Target-Artefakt. Validiere, dass Target-ID, Target-Rolle, Handoff-Pfad, Control Index, aktueller Verdict, Target Workspace und Allowed Write-Set konsistent sind. Arbeite nur im erlaubten Write-Set. Wenn ein Gate stale, widerspruechlich oder unvollstaendig ist, stoppe mit NOT READY und persistiere Evidence statt zu implementieren.

- Parent: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/input/test-parent.md
- Target ID: VADW-PARENT
- Target Role: workflow-step
- Target Spec: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/input/test-parent.md
- Control Index / Queue: 
- Handoff File: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/parent-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Initiating Project CWD / App-Kontext: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Target Workspace: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Session Title: VADW-PARENT: Implementation - VADW-PARENT Start a fresh visible regression test
- Next Mode / Skill: spec-orchestrator plus controller-request-publication
- Requested Agent Provider: codex
- Agent Adapter Status: supported; codex-app-server
- Current Verdict: READY FOR ORCHESTRATION
- Scope Summary: Start a fresh visible regression test of the Agent Delivery Workflow from the parent input only. Create an orchestration pack, exactly five child specs, exactly five child handoffs, then publish exactly five controller requests so AgentDeliveryVisibleSessionController.cs launches each child through AgentDeliverySessionLauncher.cs --mode launch --agent codex --adapter codex-app-server.
- Non-Goals: Do not use run-mock-e2e-checks.sh; do not reuse prior accepted output; do not launch child sessions directly from shell in the parent session; do not perform child delivery inside this parent session; do not treat queue-only, mock, manual, headless CLI, or single-session work as success; do not edit unrelated repository files.
- Allowed Write-Set: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/child-specs/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/controller/requests/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/closeout/summary.json
- Shared / Read-only Files: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/input/test-parent.md; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/parent-handoff.md; skills-repo/skills/spec-orchestrator/SKILL.md; skills-repo/tools/ValidateChildReadiness.cs; skills-repo/tools/AgentDeliverySessionLauncher.cs; skills-repo/tools/AgentDeliveryVisibleSessionController.cs
- Verification Commands: validate every child handoff with dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md --child <VADW-CN> --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/vadw-cN-handoff.md before publishing that child request; controller validates child output after launch; final controller-side verification must assert parent and child evidence is visible, every child closeout JSON has final_status: ran-target and closeout_status: closed, controller/controller-summary.json has status: pass, closeout/summary.json has overall_status: pass, and target/output/count.txt equals 1\n2\n3\n4\n5\n; run git diff --check
- Evidence / OpenSpec: Visible launcher evidence under tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/launches/; workflow evidence under tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/delivery-evidence/ and tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/closeout/; controller evidence under tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/controller/; direct regression ledger only, no OpenSpec archive expected.
- Open Notes: This run is intentionally visible. The parent session is launched by AgentDeliveryVisibleSessionController.cs, which delegates to AgentDeliverySessionLauncher.cs --adapter codex-app-server. The parent must create the control surface and publish request JSON files. The external controller launches children serially as visible Codex-App sessions. If a visible launch, readiness gate, or delivery fails, write NOT READY evidence with the exact failed child/step, existing evidence, missing evidence, and current count.txt content.

## Persisted Handoff

# Agent Delivery Session Handoff: VADW-PARENT

- Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/input/test-parent.md`
- Target ID: VADW-PARENT
- Target Role: workflow-step
- Target Spec: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/input/test-parent.md`
- Handoff File: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/parent-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Next Mode / Skill: spec-orchestrator plus controller-request-publication
- Current Verdict: READY FOR ORCHESTRATION
- Scope Summary: Start a fresh visible regression test of the Agent Delivery Workflow from the parent input only. Create an orchestration pack, exactly five child specs, exactly five child handoffs, then publish exactly five controller requests so `AgentDeliveryVisibleSessionController.cs` launches each child through `AgentDeliverySessionLauncher.cs --mode launch --agent codex --adapter codex-app-server`.
- Non-Goals: Do not use `run-mock-e2e-checks.sh`; do not reuse prior accepted output; do not launch child sessions directly from shell in the parent session; do not perform child delivery inside this parent session; do not treat queue-only, mock, manual, headless CLI, or single-session work as success; do not edit unrelated repository files.
- Allowed Write-Set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/child-specs/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/controller/requests/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/closeout/summary.json`
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/input/test-parent.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/parent-handoff.md`; `skills-repo/skills/spec-orchestrator/SKILL.md`; `skills-repo/tools/ValidateChildReadiness.cs`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`; `skills-repo/tools/AgentDeliveryVisibleSessionController.cs`
- Verification Commands: validate every child handoff with `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md --child <VADW-CN> --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/vadw-cN-handoff.md` before publishing that child request; controller validates child output after launch; final controller-side verification must assert parent and child evidence is visible, every child closeout JSON has `final_status: ran-target` and `closeout_status: closed`, `controller/controller-summary.json` has `status: pass`, `closeout/summary.json` has `overall_status: pass`, and `target/output/count.txt` equals `1\n2\n3\n4\n5\n`; run `git diff --check`
- Evidence / OpenSpec: Visible launcher evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/launches/`; workflow evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/delivery-evidence/` and `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/closeout/`; controller evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/controller/`; direct regression ledger only, no OpenSpec archive expected.
- Open Notes: This run is intentionally visible. The parent session is launched by `AgentDeliveryVisibleSessionController.cs`, which delegates to `AgentDeliverySessionLauncher.cs --adapter codex-app-server`. The parent must create the control surface and publish request JSON files. The external controller launches children serially as visible Codex-App sessions. If a visible launch, readiness gate, or delivery fails, write NOT READY evidence with the exact failed child/step, existing evidence, missing evidence, and current `count.txt` content.

## Required Parent-Session Behavior

1. Read this handoff and `input/test-parent.md`.
2. Use the `spec-orchestrator` workflow to create `orchestration-pack.md`.
3. Create exactly five child specs: `VADW-C1` through `VADW-C5`.
4. Create exactly five child handoffs: `handoffs/vadw-c1-handoff.md` through `handoffs/vadw-c5-handoff.md`.
5. Each child handoff must be implementation-ready and pass `ValidateChildReadiness.cs` before publishing that child's controller request.
6. Create `controller/requests/`.
7. Publish request files atomically as `controller/requests/VADW-C1.request.json` through `controller/requests/VADW-C5.request.json`.
8. Each request must use schema `agent-delivery.visible-session-controller.request.v1`, `launch.agent: codex`, `launch.adapter: codex-app-server`, `launch.mode: launch`, `launch.initiating_project_cwd: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`, and `launch.out: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/launches/children`.
9. Each request's `child.handoff_path` must point to the matching child handoff absolute path below this run directory.
10. Each request's `child.expected_output_path` must be `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/target/output/count.txt`.
11. Expected output text per request must be cumulative: C1 `1\n`, C2 `1\n2\n`, C3 `1\n2\n3\n`, C4 `1\n2\n3\n4\n`, C5 `1\n2\n3\n4\n5\n`.
12. Do not write `target/output/count.txt` from the parent session. Only launched child sessions may update it.
13. After publishing all requests, wait for controller responses and child closeout evidence, then write `closeout/summary.json` with `overall_status: pass` only if all required visible evidence and final output are exact. If waiting is unsafe or the controller owns final assertion timing, write no pass summary; the control session will treat missing pass closeout as NOT READY.

