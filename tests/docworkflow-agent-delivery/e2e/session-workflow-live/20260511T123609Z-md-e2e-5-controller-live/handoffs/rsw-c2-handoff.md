# RSW-C2 Delivery Handoff

- Parent: MD-E2E-5 External Controller Integration
- Target ID: RSW-C2
- Target Role: workflow-step
- Target Spec: openspec/changes/agent-delivery-md-e2e-5-external-controller-integration/specs/docworkflow-agent-delivery-testsuite/spec.md
- Handoff File: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/rsw-c2-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Next Mode / Skill: spec-change-delivery
- Current Verdict: IMPLEMENTATION READY
- Scope Summary: Append the second MD-E2E-5 output line and child evidence.
- Non-Goals: Do not write values 1, 3, 4, or 5; do not launch other sessions; do not edit controller files.
- Allowed Write-Set: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/delivery-evidence/rsw-c2/**; tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/closeout/children/rsw-c2.json
- Shared / Read-only Files: tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/parent-handoff.md; skills-repo/tools/AgentDeliveryVisibleSessionController.cs
- Verification Commands: Controller validates expected output after this child exits.
- Evidence / OpenSpec: openspec/changes/agent-delivery-md-e2e-5-external-controller-integration
- Open Notes: none.

Verify `target/output/count.txt` is exactly `1\n`, then append exactly `2\n`.

Allowed write-set:

- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/delivery-evidence/rsw-c2/delivery.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/closeout/children/rsw-c2.json`

After writing the output, write delivery and closeout JSON with `target_id: "RSW-C2"`, `final_status: "ran-target"`, and `closeout_status: "closed"`.
