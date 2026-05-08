# DWT-S1 L1 Deterministic Contract Harness

## Why

The testsuite needs deterministic contract checks before agentic L2 runs can produce trustworthy workflow evidence.

## What

- Add L1 fixtures and validators for parent-only start state, generated control-surface provenance, thin child blocks, missing command rehearsal, hidden fixture normalization, and S0 limitation isolation.
- Add a narrow L1 runner and evidence summary.
- Keep L1 free of agent execution, Promptfoo/Inspect/Codex runner dependencies, credential provisioning, npm registry connectivity requirements, and runtime delivery.

## Impact

- Enables later L2 agent outputs to reuse proven deterministic assertions.
- Preserves the boundary between static contract proof and agent-orchestration proof.
- Keeps `DWT-S2`, `DWT-S3` and `DWT-S5` dependency-blocked until their own prerequisites and output contracts are ready.
