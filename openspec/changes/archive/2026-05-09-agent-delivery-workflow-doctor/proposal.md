# Agent Delivery Workflow Doctor

## Why

Agent Delivery now has a deterministic post-orchestration evaluator, but agents still need to know the exact focused tool name and output mode. A tiny doctor wrapper can provide a low-token first command while preserving direct use of specialized tools.

The broader wrapper originally imagined validation, handoff sync and pre-delivery checks, but `ValidateOrchestrationPack.cs` and `SyncChildHandoff.cs` are not accepted or locally implemented. This change intentionally delivers only Slice A over the accepted `EvaluateOrchestrationNextStep.cs`.

## What

- Add `skills-repo/tools/WorkflowDoctor.cs` as a .NET 10 file-based app.
- Support only `--phase post-orchestration` in this first slice.
- Invoke `EvaluateOrchestrationNextStep.cs` with JSON output and aggregate the result into a doctor report.
- Emit JSON, Markdown, or both.
- Provide stable wrapper exit codes without adding new workflow policy.

## Impact

- Gives agents a safer convenience entry point for the accepted post-orchestration transition check.
- Keeps full orchestration pack validation, handoff sync, pre-delivery checks, skill integration and agent launches out of scope.
- Leaves specialized tools callable directly.
