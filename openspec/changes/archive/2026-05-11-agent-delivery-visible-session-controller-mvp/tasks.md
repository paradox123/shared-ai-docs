# Tasks

## 1. Controller Contracts

- [x] 1.1 Add `AgentDeliveryVisibleSessionController.cs` with CLI parsing, help, live mode, fixture mode, and deterministic exit codes.
- [x] 1.2 Implement request validation, response writing, summary writing, path safety, and state recording.
- [x] 1.3 Implement launcher subprocess invocation and evidence interpretation for parent and child launches.

## 2. Fixture Suite

- [x] 2.1 Add deterministic fixture manifest and positive, malformed-request, unsafe-path, missing-request, blocked-child, and missing-output cases.
- [x] 2.2 Ensure fixture mode exercises the same validation/result/summary code paths without starting live Codex or launcher processes.

## 3. Live Minimal Run

- [x] 3.1 Create a minimal external-controller live run directory with parent and child handoffs.
- [x] 3.2 Run the live controller so the parent publishes a child request and the controller launches the child from outside the parent turn.

## 4. Verification And Evidence

- [x] 4.1 Run controller help verification.
- [x] 4.2 Run deterministic fixture verification.
- [x] 4.3 Run live minimal controller verification and summary assertion.
- [x] 4.4 Run `openspec validate agent-delivery-visible-session-controller-mvp --strict`.
- [x] 4.5 Run `git diff --check`.
- [x] 4.6 Update implementation evidence and mark tasks complete only after evidence exists.
