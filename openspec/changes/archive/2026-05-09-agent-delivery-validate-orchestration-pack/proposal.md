# Validate Orchestration Pack

## Why

Agent Delivery orchestration packs are control artifacts for later hardening, handoff and delivery sessions. A compressed Child Index, stale handoff pointer, inconsistent Hardening Queue, or false "workflow advanced" claim can make a later session start from the wrong state.

## What

- Add `skills-repo/tools/ValidateOrchestrationPack.cs` as a .NET 10 file-based validator.
- Validate exact Child Index structure, required row cells, child spec and handoff existence, handoff child-id consistency, Hardening Queue consistency, status/next-action contradictions and conservative false-advancement claims.
- Add valid and negative fixtures under `skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/`.
- Keep skill integration and handoff generation out of scope.

## Impact

- Gives spec-orchestration and delivery sessions a deterministic preflight for pack integrity.
- Reduces manual table and handoff review.
- Keeps existing single-child readiness and launch-evidence validators focused on their narrower responsibilities.
