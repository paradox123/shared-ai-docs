# Design

## Tool Shape

`ValidateOrchestrationPack.cs` follows the existing file-based .NET tool pattern used by `ValidateChildReadiness.cs` and `EvaluateOrchestrationNextStep.cs`.

The tool reads one Markdown pack, emits JSON by default, and exits:

- `0` when no error findings exist,
- `1` when validation completed and error findings exist,
- `2` for invalid CLI input, missing pack, missing required Child Index, or unsupported output format.

## Parsing

The Child Index parser requires the exact operational columns shared with `ValidateChildReadiness.cs`. Compressed aliases such as `Slice`, `Status`, `Implementation Gate`, or `Dependencies / Evidence` are rejected.

Paths resolve in this order:

1. absolute path as written,
2. path relative to the pack directory,
3. path relative to `--repo`.

The Hardening Queue parser is intentionally smaller: it reads the first Markdown table in the configured section and requires `Child` plus a status/order column.

## Findings

Findings use stable machine codes such as `missing-handoff`, `status-next-action-mismatch`, `queue-status-mismatch`, and `false-advancement-claim`. JSON output is designed for both human inspection and later wrapper tooling.

## False Advancement

The false-advancement heuristic only targets explicit progression claims: workflow advanced, hardening started/completed, agent queued/launched, implementation started/complete, or closeout accepted. Neutral orchestration language is allowed.

Evidence is recognized conservatively through implementation-ready row verdicts for hardening-complete claims, existing `evidence.json` paths in pack evidence sections or cells, and launch/queue evidence references. Deep launch evidence validation remains owned by `ValidateAgentDeliveryLaunchEvidence.cs`.
