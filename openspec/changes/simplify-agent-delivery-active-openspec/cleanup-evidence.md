# Cleanup Evidence

Status: applied.

The authoritative cleanup classification is `cleanup-manifest.json`.

## Deleted Paths

- `tests/docworkflow-agent-delivery/e2e/evidence`
- `tests/docworkflow-agent-delivery/e2e/fixtures`
- `tests/docworkflow-agent-delivery/e2e/mock-runner`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live`
- `tests/docworkflow-agent-delivery/l1`
- `tests/docworkflow-agent-delivery/l2`
- `tests/docworkflow-agent-delivery/l3`
- `tests/docworkflow-agent-delivery/mock-data`
- `tests/docworkflow-agent-delivery/reporting`
- `tests/docworkflow-agent-delivery/spikes`
- `tests/docworkflow-agent-delivery/testcases`
- `tests/docworkflow-agent-delivery/scripts/run-l1-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-l2-parent-orchestration-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-l2-single-child-closeout-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-l3-runtime-temp-repo-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-reporting-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/run-contract-checks.sh`
- `tests/docworkflow-agent-delivery/scripts/setup-fixture.sh`
- `skills-repo/tools/AgentDeliverySessionLauncher.cs`
- `skills-repo/tools/AgentDeliveryVisibleSessionController.cs`
- `skills-repo/tools/ArchiveVisibleCodexAppSession.cs`
- `skills-repo/tools/EvaluateOrchestrationNextStep.cs`
- `skills-repo/tools/SyncChildHandoff.cs`
- `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`
- `skills-repo/tools/ValidateChildReadiness.cs`
- `skills-repo/tools/ValidateOrchestrationPack.cs`
- `skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs`
- `skills-repo/tools/WorkflowDoctor.cs`
- `openspec/changes/agent-delivery-run-profiles-compact-debug`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike`
- `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s1-l1-deterministic-harness`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s2-l2-parent-first-orchestration-agent-harness`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s3-l2-single-child-delivery-closeout-gate-harness`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s4-reporting-telemetry-contract`
- `openspec/changes/archive/2026-05-08-docworkflow-agent-testsuite-dwt-s5-l3-runtime-temp-repo-delivery-pilot`
- `openspec/changes/archive/2026-05-09-agent-delivery-evaluate-orchestration-next-step`
- `openspec/changes/archive/2026-05-09-agent-delivery-spec-orchestrator-gate-integration`
- `openspec/changes/archive/2026-05-09-agent-delivery-sync-child-handoff`
- `openspec/changes/archive/2026-05-09-agent-delivery-validate-orchestration-pack`
- `openspec/changes/archive/2026-05-09-agent-delivery-workflow-doctor`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-1-mock-fixtures`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-2-local-runner`
- `openspec/changes/archive/2026-05-09-docworkflow-agent-mock-e2e-md-e2e-3-standard-gate-migration`
- `openspec/changes/archive/2026-05-11-agent-delivery-evidence-resolver-skill-slimming`
- `openspec/changes/archive/2026-05-11-agent-delivery-md-e2e-5-external-controller-integration`
- `openspec/changes/archive/2026-05-11-agent-delivery-visible-app-launcher-adapter`
- `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-closeout-archive`
- `openspec/changes/archive/2026-05-11-agent-delivery-visible-session-controller-mvp`

## Retained Paths

- `docs/doc-workflow.md`: canonical workflow document.
- `openspec/changes/simplify-agent-delivery-active-openspec`: active change and cleanup evidence.
- `tests/docworkflow-agent-delivery/active-scope`: simplified validation fixtures.
- `tests/docworkflow-agent-delivery/e2e/active-openspec`: deterministic Active OpenSpec E2E.
- `tests/docworkflow-agent-delivery/scripts/run-active-openspec-e2e-checks.sh`: Active OpenSpec E2E entrypoint.
- `tests/docworkflow-agent-delivery/scripts/run-simplified-agent-delivery-checks.sh`: simplified validation entrypoint.
- `skills-repo/tools/ValidateActiveOpenSpecScope.cs`: active-scope validator.
- `skills-repo/tools/ValidateAgentDeliveryCleanup.cs`: cleanup validator.
- `skills-repo/tools/ValidateSkillProseBudget.cs`: prose-budget validator.

## Archive-Reference Paths

None.

## Unresolved Cleanup Decisions

None.
