# RSW-PARENT External Controller Handoff

- Parent: MD-E2E-5 External Controller Integration
- Target ID: RSW-PARENT
- Target Role: workflow-step
- Target Spec: openspec/changes/agent-delivery-md-e2e-5-external-controller-integration/specs/docworkflow-agent-delivery-testsuite/spec.md
- Handoff File: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/parent-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Next Mode / Skill: controller-request-publication
- Current Verdict: IMPLEMENTATION READY
- Scope Summary: Publish exactly five external-controller child requests for RSW-C1 through RSW-C5 and stop.
- Non-Goals: Do not launch children; do not run AgentDeliverySessionLauncher.cs; do not run codex app-server; do not edit target/output/count.txt.
- Allowed Write-Set: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/controller/requests/**
- Shared / Read-only Files: skills-repo/tools/AgentDeliveryVisibleSessionController.cs; tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh; openspec/changes/agent-delivery-md-e2e-5-external-controller-integration/specs/docworkflow-agent-delivery-testsuite/spec.md
- Verification Commands: Controller owns verification after this parent publishes the requests.
- Evidence / OpenSpec: openspec/changes/agent-delivery-md-e2e-5-external-controller-integration; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live
- Open Notes: This parent session exists only to publish request artifacts. The external controller launches the children.

## Goal

Publish exactly five external-controller child launch requests for `MD-E2E-5`, then stop.

## Scope

- Target Repository: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`
- Run Directory: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live`
- Parent Target ID: `RSW-PARENT`
- Child Target IDs: `RSW-C1`, `RSW-C2`, `RSW-C3`, `RSW-C4`, `RSW-C5`

## Required Behavior

1. Create the directory `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/controller/requests` if missing.
2. Write the five JSON request files below using an atomic temp-file-then-rename pattern.
3. Do not run `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs`.
4. Do not run `codex app-server`.
5. Do not edit `target/output/count.txt`.

## Request Files

Write `controller/requests/RSW-C1.request.json`:

```json
{"schema_id":"agent-delivery.visible-session-controller.request.v1","request_id":"RSW-C1","created_at":"2026-05-11T12:36:09Z","requested_by":{"target_id":"RSW-PARENT","role":"parent"},"child":{"target_id":"RSW-C1","handoff_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/rsw-c1-handoff.md","expected_output_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt","expected_output_text":"1\n"},"launch":{"agent":"codex","adapter":"codex-app-server","mode":"launch","initiating_project_cwd":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs","out":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/launches/children"}}
```

Write `controller/requests/RSW-C2.request.json`:

```json
{"schema_id":"agent-delivery.visible-session-controller.request.v1","request_id":"RSW-C2","created_at":"2026-05-11T12:36:09Z","requested_by":{"target_id":"RSW-PARENT","role":"parent"},"child":{"target_id":"RSW-C2","handoff_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/rsw-c2-handoff.md","expected_output_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt","expected_output_text":"1\n2\n"},"launch":{"agent":"codex","adapter":"codex-app-server","mode":"launch","initiating_project_cwd":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs","out":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/launches/children"}}
```

Write `controller/requests/RSW-C3.request.json`:

```json
{"schema_id":"agent-delivery.visible-session-controller.request.v1","request_id":"RSW-C3","created_at":"2026-05-11T12:36:09Z","requested_by":{"target_id":"RSW-PARENT","role":"parent"},"child":{"target_id":"RSW-C3","handoff_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/rsw-c3-handoff.md","expected_output_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt","expected_output_text":"1\n2\n3\n"},"launch":{"agent":"codex","adapter":"codex-app-server","mode":"launch","initiating_project_cwd":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs","out":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/launches/children"}}
```

Write `controller/requests/RSW-C4.request.json`:

```json
{"schema_id":"agent-delivery.visible-session-controller.request.v1","request_id":"RSW-C4","created_at":"2026-05-11T12:36:09Z","requested_by":{"target_id":"RSW-PARENT","role":"parent"},"child":{"target_id":"RSW-C4","handoff_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/rsw-c4-handoff.md","expected_output_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt","expected_output_text":"1\n2\n3\n4\n"},"launch":{"agent":"codex","adapter":"codex-app-server","mode":"launch","initiating_project_cwd":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs","out":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/launches/children"}}
```

Write `controller/requests/RSW-C5.request.json`:

```json
{"schema_id":"agent-delivery.visible-session-controller.request.v1","request_id":"RSW-C5","created_at":"2026-05-11T12:36:09Z","requested_by":{"target_id":"RSW-PARENT","role":"parent"},"child":{"target_id":"RSW-C5","handoff_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/rsw-c5-handoff.md","expected_output_path":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt","expected_output_text":"1\n2\n3\n4\n5\n"},"launch":{"agent":"codex","adapter":"codex-app-server","mode":"launch","initiating_project_cwd":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs","out":"/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/launches/children"}}
```

## Completion Report

Report only that the five request files were published and that no child launch command was run.
