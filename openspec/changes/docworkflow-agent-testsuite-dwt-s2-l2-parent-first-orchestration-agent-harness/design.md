# DWT-S2 L2 Parent-first Orchestration Harness Design

## Scope

DWT-S2 implements the L2 parent-first orchestration proof only. It does not implement DWT-S3 single-child delivery/closeout gates, DWT-S5 runtime delivery, or any KI-fuer-KMU runtime changes.

## Runner Strategy

Promptfoo/Codex is the primary runner path, reusing the accepted DWT-S0 result `ADOPT_WITH_LIMITATIONS`. Because S0 found explicit auth and network limitations, DWT-S2 also implements fallback artifact mode. Fallback mode validates stored output bundles and blocked-agent evidence, but it cannot produce accepted L2 agent proof unless the summary records `agent_execution_status: ran-target`.

## Output Contract

The runner writes an output bundle with source manifest, raw agent output, child index, coverage matrix, dependency graph, hardening queue, generated child specs, optional child handoffs, telemetry manifest and DWT-S4-compatible summary.

The validator fails direct implementation, missing child-control artifacts, invalid Child Index header, missing coverage/dependencies/hardening queue, skeleton ready claims, ambiguous next child states, stale output provenance, blocked-agent-as-pass reporting, forbidden runtime/repo writes and invalid DWT-S4 summary or telemetry fields.

## Boundaries

DWT-S2 may identify a valid next child state but must not kick off child delivery. DWT-S3 remains responsible for single-child delivery and closeout gating. DWT-S5 remains blocked until L2 control-flow evidence exists.
