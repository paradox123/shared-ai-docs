# Implementation Evidence

## 2026-05-11 Pre-Implementation Analysis

Verdict: `NOT READY` for runtime edits.

Reason: the accepted external visible-session controller MVP is intentionally a one-child controller. It proves the required process boundary, but it does not define or implement the five-child `MD-E2E-5` controller contract, multi-response summary, runner evidence-path mapping, S4/S5 integration mapping, or negative cases needed for a passing live `MD-E2E-5` run.

Observed state:

- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh` already implements an evidence-evaluation `--run-id <id> --keep` path.
- The runner still expects the old parent plus `launches/rsw-c1` through `launches/rsw-c5` evidence layout.
- `skills-repo/tools/AgentDeliveryVisibleSessionController.cs` processes one parent-published child request and writes one response.
- Retained controller MVP evidence has one visible parent and one visible child, `CTRL-C1`, not `RSW-C1` through `RSW-C5`.
- Previous S3 live evidence under `20260511T111500Z-adv-cas-s3-live` remains `overall_workflow_status: "not_ready"`.

Retained evidence reviewed:

- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/controller-summary.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/requests/CTRL-C1.request.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/responses/CTRL-C1.response.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/launches/parent/20260511T120647Z-ctrl-parent/evidence.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/launches/children/20260511T120906Z-ctrl-c1/evidence.json`
- `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T111500Z-adv-cas-s3-live/visible-session-summary.json`

Verification replay:

- `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`: pass.
- `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help`: pass.
- `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-mvp`: pass, six fixture cases.
- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh control-boundary`: pass, nine S4 cases.
- `node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary`: pass, nine S4 cases.
- `dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence`: pass, eleven S2 cases.
- `dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate`: pass, ten S5 cases.
- Retained MVP summary assertion: pass for exactly one controller child.
- `openspec validate agent-delivery-md-e2e-5-external-controller-integration --strict`: pass.
- `git diff --check`: pass.

Runtime edits performed: none.

## 2026-05-11 Implementation And READY Evidence

Verdict: `READY`.

Implemented scope:

- `AgentDeliveryVisibleSessionController.cs` now supports optional ordered multi-child workflows via `--expected-child-target-ids`.
- Existing one-child controller MVP behavior remains the default when no expected child list is supplied.
- Fixture mode validates response counts and includes a new `visible-session-controller-md-e2e-5` multi-child fixture suite.
- `run-visible-app-session-workflow-checks.sh` now consumes controller summary and response artifacts to resolve `RSW-PARENT` and `RSW-C1` through `RSW-C5` evidence paths.
- The runner still rejects missing controller summaries, missing child responses, wrong output, missing S4 summary, missing S5 summary, and non-visible evidence.

Retained live evidence:

- Live run root: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/`
- Controller summary: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/controller/controller-summary.json`
- Runner summary: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/visible-session-summary.json`
- Control summary: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/control/control-boundary-summary.json`
- Archive summary: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/closeout/archive-summary.json`
- Final output: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/target/output/count.txt`

Live command:

```sh
dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --run-dir tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live --parent-handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/handoffs/parent-handoff.md --parent-target-id RSW-PARENT --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs --expected-child-target-ids RSW-C1,RSW-C2,RSW-C3,RSW-C4,RSW-C5 --request-timeout-seconds 120 --parent-timeout-minutes 10 --child-timeout-minutes 10 --app-server-request-timeout-seconds 60
```

Result: `pass`.

Runner command:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id 20260511T123609Z-md-e2e-5-controller-live --keep --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
```

Result: `MD-E2E-5 pass`.

Fresh verification replay:

- `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`: pass.
- `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help`: pass.
- `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-mvp`: pass, six cases.
- `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-md-e2e-5 --expected-child-target-ids RSW-C1,RSW-C2,RSW-C3,RSW-C4,RSW-C5`: pass, two cases.
- `tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh control-boundary`: pass, nine cases.
- `node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/control/control-boundary-summary.json`: pass, one case.
- `dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --validate-summary tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T123609Z-md-e2e-5-controller-live/closeout/archive-summary.json --mode validate`: pass.
- Live summary assertion: pass.
- S2 fixture replay: pass, eleven cases.
- S4 fixture replay: pass, nine cases.
- S5 fixture replay: pass, ten cases.

Parent/child status:

- Parent `RSW-PARENT`: visible Codex App session, launched externally by controller.
- Children `RSW-C1` through `RSW-C5`: visible Codex App sessions, launched externally by controller in order.
- Final output: exact `1\n2\n3\n4\n5\n`.
