# Proposal

## Why

The accepted external visible-session controller MVP proves the right process boundary for one parent and one child: the parent publishes a child launch request, and a controller outside the parent Codex App turn launches the child. That MVP is intentionally too small for `MD-E2E-5`.

`MD-E2E-5` still needs a hardened integration contract before runtime edits because the current S3 runner evaluates an older evidence layout and the accepted controller contract only processes one child request. A full live pass requires one parent plus five child visible Codex App sessions, five controller responses, exact final output, S2 validation, S4 control-boundary proof, and S5 archive/retention proof.

## What Changes

Define the next `MD-E2E-5` external-controller integration slice:

- parent workflow publishes child launch requests instead of starting child sessions
- external controller launches `RSW-C1` through `RSW-C5` from outside the parent turn
- controller writes one response per child and a multi-child summary
- runner validates parent/child visible evidence through controller response/summary evidence paths
- runner keeps single-session, one-child, nested-launch, mock, and output-only evidence as non-passing
- S4 and S5 summaries are explicitly mapped into the controller-backed live run directory

## Impact

- Adds a pending OpenSpec contract for `MD-E2E-5` controller integration.
- Does not change `AgentDeliveryVisibleSessionController.cs` in this preparatory step.
- Does not change `run-visible-app-session-workflow-checks.sh` in this preparatory step.
- Does not claim a passing `MD-E2E-5` live run.
