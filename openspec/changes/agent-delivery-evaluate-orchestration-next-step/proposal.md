# Agent Delivery Evaluate Orchestration Next Step

## Why

The Agent Delivery workflow currently relies on long skill prose for the post-orchestration transition. The recent MD-E2E orchestration showed that a generated Hardening Queue can be mistaken for workflow advancement, and that "no implementation" can be overinterpreted as "no hardening".

## What

- Add `skills-repo/tools/EvaluateOrchestrationNextStep.cs` as a .NET 10 file-based app.
- Add focused fixtures for post-orchestration next-step decisions.
- Emit stable JSON and optional Markdown summaries with first unblocked child, required next skill, delivery permission and per-child lane classification.
- Keep skill integration, handoff generation, agent launch and runtime/product changes out of this change.

## Impact

- Gives `spec-orchestrator` and future workflow wrappers a deterministic post-orchestration gate.
- Reduces reliance on ambiguous prose for "queue created" versus "workflow advanced".
- Provides regression fixtures for the "no implementation still allows hardening" failure.

