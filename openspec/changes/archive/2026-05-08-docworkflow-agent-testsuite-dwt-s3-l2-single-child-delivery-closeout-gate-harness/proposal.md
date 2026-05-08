# DWT-S3 L2 Single-Child Delivery and Closeout Gate Harness

## Why

The testsuite has accepted DWT-S2 evidence that parent-first orchestration can produce a valid child-control surface. It still needs L2 proof that the next step is gated: `spec-change-delivery` may act on exactly one implementation-ready child from a fresh handoff, and `spec-closeout` must not release DWT-S5 merely because DWT-S3 closed.

## What

- Define and implement a Promptfoo-first L2 single-child delivery and closeout gate runner with explicit fallback artifact mode.
- Validate DWT-S3-only delivery kickoff from the current Child Index row, persisted handoff, concrete write-set and isolated temp workspace.
- Reject stale handoffs, out-of-workspace writes, approximate write-sets and DWT-S5 auto-release attempts.
- Validate synthetic closeout output for Parent Coverage preservation, evidence/OpenSpec ledger sync and DWT-S5 blocked state.
- Emit DWT-S4-compatible summary, telemetry, style and efficiency artifacts.

## Impact

- Adds the L2 control-flow proof that follows accepted DWT-S2 parent-first orchestration.
- Makes stale handoff and next-child-release failures deterministic before any L3 runtime pilot exists.
- Preserves DWT-S5 as a blocked future child until its own child spec and handoff gates authorize work.
