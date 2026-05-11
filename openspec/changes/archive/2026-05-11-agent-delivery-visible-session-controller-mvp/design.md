## Context

`AgentDeliverySessionLauncher.cs` already knows how to start visible Codex App sessions through `codex app-server --listen stdio://` and retain evidence. The failure mode appears when a parent session tries to run a nested child app-server launch from inside its own app-server-backed turn. The controller MVP avoids that topology by keeping all launcher subprocesses under an external shell/control process.

## Goals / Non-Goals

**Goals:**

- Build one bounded controller that can launch one visible parent and one visible child.
- Keep parent responsibility limited to publishing a request artifact.
- Validate request schema, identity, adapter, cwd, and path safety before launching a child.
- Preserve enough evidence to diagnose blocked/failed launches.
- Provide deterministic fixture coverage without starting live Codex processes.

**Non-Goals:**

- No full `MD-E2E-5` migration.
- No five-child orchestration.
- No attempt to reuse a parent's private stdio transport.
- No changes to the existing launcher JSON-RPC app-server protocol.
- No broad runner refactor.

## Decisions

- The controller invokes `AgentDeliverySessionLauncher.cs` as a subprocess and interprets `evidence.json`; it does not reimplement app-server JSON-RPC.
- Fixture mode simulates launcher results from fixture files and must not spawn `codex`, `codex app-server`, or the launcher.
- Rejected requests produce response status `rejected`, summary status `setup_error`, exit `2`, and no launcher command.
- Missing request before timeout produces summary status `timeout`, exit `1`, and no response because there is no request id.
- Child paths from a request must resolve below the configured run directory.

## Risks / Trade-offs

- The live verification still depends on local Codex app-server behavior. Fixture mode provides fast contract coverage, but live success is the real visible-session proof.
- Parent and child handoffs are minimal spike fixtures, not the final `MD-E2E-5` orchestration format.
- The controller is intentionally linear for the MVP; future multi-child orchestration belongs in a separate spec/change.
