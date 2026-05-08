# DWT-S2 L2 Parent-first Orchestration Agent Harness

## Why

The testsuite needs L2 evidence that a large parent/master spec is not directly implemented. DWT-S1 proves deterministic readiness/provenance gates, and DWT-S4 proves reporting/telemetry contracts, but neither proves agentic parent-first orchestration.

## What

- Define and implement a Promptfoo-first L2 parent-first orchestration runner with explicit fallback artifact mode.
- Validate that oversized parent input produces child specs, exact Child Index, Coverage Matrix, Dependencies, Hardening Queue and at least one valid next child state.
- Reject direct implementation attempts, stale copied outputs, thin-child ready claims and blocked-agent results mislabeled as pass.
- Emit DWT-S4-compatible summary, telemetry, style and efficiency artifacts.
- Keep DWT-S3 and DWT-S5 unreleased until their own child specs and gates authorize them.

## Impact

- Adds the first agentic dry-run proof layer for parent-first orchestration.
- Gives later DWT-S3 delivery/closeout tests a stable DWT-S2 output contract to consume.
- Preserves evidence integrity by distinguishing real agent proof from blocked or fallback-only validation.
