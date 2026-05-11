# Scope Contract

## In Scope

1. Harden and implement the missing `MD-E2E-5` external-controller integration contract.
2. Specify and execute five ordered child launch requests: `RSW-C1`, `RSW-C2`, `RSW-C3`, `RSW-C4`, and `RSW-C5`.
3. Specify and execute controller-owned child launches from outside the parent app-server turn.
4. Implement runner consumption of controller summary and response artifacts.
5. Retain evidence required for S2, S4, S5, final output, and controller provenance.

## Out Of Scope

1. No change to the accepted one-child controller MVP contract semantics.
2. No single-session simulation as success.
3. No nested child launches from inside the parent session.
4. No cleanup of unrelated live-run processes or evidence.
5. No replacement of the mock-only standard gate.

## Acceptance Targets

1. The OpenSpec change captures why the accepted one-child controller MVP is insufficient for a full `MD-E2E-5` pass.
2. The spec delta defines parent request publication, controller response/summary evidence, runner validation, and negative cases for the multi-child integration.
3. The controller MVP fixture remains passing.
4. The new MD-E2E-5 controller fixture passes.
5. A retained live run passes with one parent plus five externally launched child visible Codex App sessions.
6. OpenSpec validation for this change passes.

## Planned Verification

1. `bash -n tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh`
2. `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --help`
3. `dotnet run skills-repo/tools/AgentDeliveryVisibleSessionController.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-session-controller-mvp`
4. `openspec validate agent-delivery-md-e2e-5-external-controller-integration --strict`
5. `git diff --check`

## Open Risks And Assumptions

1. The existing one-child controller code may be extended or wrapped in a dedicated MD-E2E-5 controller mode; the implementation approach remains a future decision.
2. The runner must support controller evidence paths without weakening the existing fixed-layout checks for historical retained runs.
3. S5 archive/retention evidence may need a clear mapping from controller response evidence paths to archive records before a live pass can be accepted.
