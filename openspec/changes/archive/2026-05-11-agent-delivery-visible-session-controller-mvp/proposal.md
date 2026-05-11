## Why

The nested app-server spike showed that launching a child `codex app-server --listen stdio://` from inside an app-server-backed parent turn can block at JSON-RPC `initialize`. The Agent Delivery workflow needs visible parent and child Codex App sessions, but the child launch must be owned by a process outside the parent turn.

## What Changes

Add a minimal external visible-session controller for exactly one parent/child workflow:

- launches the parent through `AgentDeliverySessionLauncher.cs --adapter codex-app-server`
- waits for the parent to publish one child request artifact
- validates the request contract and path boundaries
- launches the child through the existing launcher from the controller process
- writes deterministic response and summary artifacts for pass, blocked, failed, timeout, and rejected outcomes
- provides a no-live-launch fixture mode for state-machine and contract validation

## Capabilities

### New Capabilities

- `visible-session-controller`: external controller for one visible Codex App parent/child Agent Delivery workflow.

### Modified Capabilities

- `docworkflow-agent-delivery-testsuite`: adds fixture and live-gate requirements for the external visible-session controller MVP.

## Impact

- Adds `skills-repo/tools/AgentDeliveryVisibleSessionController.cs`
- Adds fixture files under `tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-mvp/`
- Adds retained live evidence under `tests/docworkflow-agent-delivery/e2e/session-workflow-live/*-external-controller-mvp/`
- Does not change the full `MD-E2E-5` runner or the app-server protocol implementation in `AgentDeliverySessionLauncher.cs`
