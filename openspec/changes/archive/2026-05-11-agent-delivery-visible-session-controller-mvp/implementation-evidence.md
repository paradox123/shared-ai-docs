# Implementation Evidence

## Scope

Implemented the external visible-session controller MVP for exactly one parent and one child visible Codex App workflow.

## Changed Behavior

- Added `AgentDeliveryVisibleSessionController.cs`.
- Added deterministic fixture mode for request validation, response/summary writing, blocked child, missing output, missing request timeout, and rejection semantics.
- Added live minimal controller run evidence where the parent publishes `CTRL-C1.request.json` and the controller launches `CTRL-C1` from outside the parent session.
- Preserved the existing `AgentDeliverySessionLauncher.cs` app-server protocol; the controller invokes it as a subprocess and interprets retained evidence.

## Verification

| Command | Status | Evidence |
|---|---|---|
| `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help` | ran-target/pass | Help printed live and fixture mode usage with run-dir, parent handoff, parent target id, parent/child timeout, request timeout, app-server request timeout, summary-out, and fixture options. |
| `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-mvp` | ran-target/pass | `RESULT: PASS (6 controller fixture cases)`. |
| `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --run-dir tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp --parent-handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/handoffs/parent-handoff.md --parent-target-id CTRL-PARENT --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs --request-timeout-seconds 180 --parent-timeout-minutes 5 --child-timeout-minutes 5 --app-server-request-timeout-seconds 30 --poll-interval-ms 1000` | ran-target/pass | Controller exited `0`: `pass: .../controller/controller-summary.json`. |
| `node -e "const fs=require('fs'); const s=JSON.parse(fs.readFileSync('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/controller-summary.json','utf8')); if (s.status !== 'pass') process.exit(1);"` | ran-target/pass | Summary assertion exited `0`. |
| Parent transcript commandExecution scan | ran-target/pass | `forbiddenCommandCount: 0` for child launcher/app-server commands in parent transcript. |
| Child initialize response scan | ran-target/pass | Child transcript has client `initialize` and server response for id `1`. |
| `openspec validate agent-delivery-visible-session-controller-mvp --strict` | ran-target/pass | OpenSpec change validates. |
| `git diff --check` | ran-target/pass | Final whitespace check exited `0`. |

## Retained Evidence

- Controller summary: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/controller-summary.json`
- Controller response: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/controller/responses/CTRL-C1.response.json`
- Parent evidence: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/launches/parent/20260511T120647Z-ctrl-parent/evidence.json`
- Parent transcript: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/launches/parent/20260511T120647Z-ctrl-parent/app-server-transcript.jsonl`
- Child evidence: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/launches/children/20260511T120906Z-ctrl-c1/evidence.json`
- Child transcript: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/launches/children/20260511T120906Z-ctrl-c1/app-server-transcript.jsonl`
- Child output: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T120609Z-external-controller-mvp/target/output/controller-spike.txt`
