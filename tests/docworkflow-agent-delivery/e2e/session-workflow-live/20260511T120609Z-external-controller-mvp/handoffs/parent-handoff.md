## External Controller Parent Handoff

- Parent: Agent Delivery External Visible Session Controller MVP
- Target ID: CTRL-PARENT
- Target Role: workflow-step
- Target Spec: _specs/2026-05-11 Agent Delivery External Visible Session Controller MVP.md
- Handoff File: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/handoffs/parent-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Next Mode / Skill: controller-request-publication
- Current Verdict: IMPLEMENTATION READY
- Scope Summary: Publish exactly one external-controller child request for CTRL-C1 and stop.
- Non-Goals: Do not launch the child; do not run AgentDeliverySessionLauncher.cs; do not run codex app-server; do not touch MD-E2E-5.
- Allowed Write-Set: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/requests/**
- Shared / Read-only Files: skills-repo/tools/AgentDeliverySessionLauncher.cs; skills-repo/tools/AgentDeliveryVisibleSessionController.cs; _specs/2026-05-11 Agent Delivery External Visible Session Controller MVP.md
- Verification Commands: Controller owns verification after this parent publishes the request.
- Evidence / OpenSpec: openspec/changes/agent-delivery-visible-session-controller-mvp; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp
- Open Notes: This parent session exists only to publish a request artifact. The external controller launches CTRL-C1.

## Task

Write the following JSON request to:

`/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/requests/CTRL-C1.request.json`

Use an atomic write pattern: create the directory if needed, write a temporary file in the same directory, then rename it to `CTRL-C1.request.json`.

Do not run `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs`.
Do not run `codex app-server`.
Do not start the child yourself.

```json
{
  "schema_id": "agent-delivery.visible-session-controller.request.v1",
  "request_id": "CTRL-C1",
  "created_at": "2026-05-11T00:00:00Z",
  "requested_by": {
    "target_id": "CTRL-PARENT",
    "role": "parent"
  },
  "child": {
    "target_id": "CTRL-C1",
    "handoff_path": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/handoffs/ctrl-c1-handoff.md",
    "expected_output_path": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/target/output/controller-spike.txt",
    "expected_output_text": "controller child reached\n"
  },
  "launch": {
    "agent": "codex",
    "adapter": "codex-app-server",
    "mode": "launch",
    "initiating_project_cwd": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
    "out": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/launches/children"
  }
}
```
