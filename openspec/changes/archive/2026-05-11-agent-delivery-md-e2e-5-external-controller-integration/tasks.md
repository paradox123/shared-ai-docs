# Tasks

## 1. Contract Hardening

- [x] 1.1 Extend the controller contract from one child request to five ordered `RSW-C1` through `RSW-C5` requests for `MD-E2E-5`.
- [x] 1.2 Define the multi-child controller summary shape, response list semantics, terminal status rules, and retained evidence mapping.
- [x] 1.3 Define parent behavior for publishing requests without invoking child launch commands.
- [x] 1.4 Define negative cases for one-child controller summaries, missing responses, duplicate thread ids, nested child launches, wrong final output, and mock/headless substitutes.

## 2. Runtime Implementation

- [x] 2.1 Update `AgentDeliveryVisibleSessionController.cs` or add a scoped MD-E2E-5 controller mode that serially launches five child requests from outside the parent turn.
- [x] 2.2 Update `run-visible-app-session-workflow-checks.sh` so live `--run-id <id> --keep` consumes controller summary/response evidence paths instead of assuming only the old `launches/rsw-cN/evidence.json` layout.
- [x] 2.3 Keep the accepted one-child controller MVP behavior and fixtures passing.
- [x] 2.4 Add retained deterministic controller-integration fixture evidence for multi-child request/response validation without live launches.

## 3. Live Verification

- [x] 3.1 Run a retained live `MD-E2E-5` controller integration slice with one visible parent and five visible child Codex App sessions.
- [x] 3.2 Assert final output is exactly `1\n2\n3\n4\n5\n`.
- [x] 3.3 Validate all six visible evidence records through the S2 visible-session validator.
- [x] 3.4 Validate S4 observed-only control behavior and S5 archive/retention evidence for all six sessions.
- [x] 3.5 Run `bash -n`, controller help, controller fixture checks, live summary assertion, `openspec validate agent-delivery-md-e2e-5-external-controller-integration --strict`, and `git diff --check`.
