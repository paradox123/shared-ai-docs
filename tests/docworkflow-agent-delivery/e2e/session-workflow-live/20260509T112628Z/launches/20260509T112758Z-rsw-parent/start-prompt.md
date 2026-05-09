Session Title: RSW-PARENT spec-orchestrator - start a fresh session

Wir arbeiten in /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs.

Starte eine frische Agent-Delivery-Session aus folgendem persistierten Handoff.

Pflicht: Lies zuerst das Handoff, den Control Index / die Queue und das Target-Artefakt. Validiere, dass Target-ID, Target-Rolle, Handoff-Pfad, Control Index, aktueller Verdict, Target Workspace und Allowed Write-Set konsistent sind. Arbeite nur im erlaubten Write-Set. Wenn ein Gate stale, widerspruechlich oder unvollstaendig ist, stoppe mit NOT READY und persistiere Evidence statt zu implementieren.

- Parent: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md
- Target ID: RSW-PARENT
- Target Role: workflow-step
- Target Spec: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md
- Control Index / Queue: 
- Handoff File: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/parent-start-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Project CWD / App-Kontext: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Session Title: RSW-PARENT spec-orchestrator - start a fresh session
- Next Mode / Skill: spec-orchestrator
- Requested Agent Provider: codex
- Agent Adapter Status: supported; codex-cli
- Current Verdict: READY FOR ORCHESTRATION
- Scope Summary: Start a fresh-session Agent Delivery Workflow test from the parent input only; run spec-orchestrator, create child specs and child handoffs, then use AgentDeliverySessionLauncher.cs --mode launch to run child work across launcher-created child sessions before parent closeout validates final target/output/count.txt.
- Non-Goals: Do not use run-mock-e2e-checks.sh; do not reuse accepted MD-E2E child specs as outputs; do not perform all hardening and delivery in this parent session; do not treat single-session simulation as success; do not edit unrelated specs or project docs.
- Allowed Write-Set: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/orchestration-pack.md; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/child-specs/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/launches/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/**
- Shared / Read-only Files: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/parent-start-handoff.md; skills-repo/skills/spec-orchestrator/SKILL.md; skills-repo/skills/child-spec-hardening/SKILL.md; skills-repo/skills/spec-change-delivery/SKILL.md; skills-repo/skills/spec-closeout/SKILL.md; skills-repo/tools/ValidateChildReadiness.cs; skills-repo/tools/AgentDeliverySessionLauncher.cs
- Verification Commands: final launched-session verification must assert tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/summary.json has overall_status: pass; assert all five children have final_status: ran-target and closeout_status: closed; assert each child has launcher evidence under tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/launches/; assert tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt equals 1\n2\n3\n4\n5\n; run git diff --check
- Evidence / OpenSpec: Launcher evidence under tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/launches/; workflow evidence under tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/summary.json; direct smoke ledger only, no OpenSpec archive expected for this test.
- Open Notes: This test must prove launcher-started fresh-session execution for parent and child work. If parent or child codex exec launch fails, report NOT READY with launcher evidence instead of continuing in the same session.

## Persisted Handoff

# Agent Delivery Session Handoff: RSW-PARENT

- Parent: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`
- Target ID: RSW-PARENT
- Target Role: workflow-step
- Target Spec: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`
- Handoff File: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/parent-start-handoff.md`
- Target Repository / Working Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Next Mode / Skill: spec-orchestrator
- Current Verdict: READY FOR ORCHESTRATION
- Scope Summary: Start a fresh-session Agent Delivery Workflow test from the parent input only; run `spec-orchestrator`, create child specs and child handoffs, then use `AgentDeliverySessionLauncher.cs --mode launch` to run child work across launcher-created child sessions before parent closeout validates final `target/output/count.txt`.
- Non-Goals: Do not use `run-mock-e2e-checks.sh`; do not reuse accepted MD-E2E child specs as outputs; do not perform all hardening and delivery in this parent session; do not treat single-session simulation as success; do not edit unrelated specs or project docs.
- Allowed Write-Set: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/orchestration-pack.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/child-specs/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/launches/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/**`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/**`
- Shared / Read-only Files: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/input/test-parent.md`; `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/handoffs/parent-start-handoff.md`; `skills-repo/skills/spec-orchestrator/SKILL.md`; `skills-repo/skills/child-spec-hardening/SKILL.md`; `skills-repo/skills/spec-change-delivery/SKILL.md`; `skills-repo/skills/spec-closeout/SKILL.md`; `skills-repo/tools/ValidateChildReadiness.cs`; `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- Verification Commands: final launched-session verification must assert `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/summary.json` has `overall_status: pass`; assert all five children have `final_status: ran-target` and `closeout_status: closed`; assert each child has launcher evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/launches/`; assert `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt` equals `1\n2\n3\n4\n5\n`; run `git diff --check`
- Evidence / OpenSpec: Launcher evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/launches/`; workflow evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/summary.json`; direct smoke ledger only, no OpenSpec archive expected for this test.
- Open Notes: This test must prove launcher-started fresh-session execution for parent and child work. If parent or child `codex exec` launch fails, report `NOT READY` with launcher evidence instead of continuing in the same session.

## Required Launched-Session Behavior

The parent launched session must:

1. Read this handoff and the parent input.
2. Use `spec-orchestrator` to create `orchestration-pack.md`, five child specs and five child handoffs under the allowed write-set.
3. For each child, use `AgentDeliverySessionLauncher.cs --mode launch --agent codex` with that child handoff and an output root under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/launches/`.
4. Require child-session evidence before marking that child delivered.
5. Close out only after all five child launch evidences and delivery evidences exist and `target/output/count.txt` is exact.

