# Design

## Decision Context

Promptfoo is the first candidate because the ADR identifies explicit support for coding-agent evaluations and Codex-related provider paths. This change does not treat Promptfoo as finally adopted until the spike evidence is reviewed.

## Scope Boundary

This is a framework spike only. It may create the smallest useful probe under `tests/docworkflow-agent-delivery/spikes/dwt-s0/`, but it must not implement the recurring DocWorkflow testsuite or modify runtime repositories.

## Evidence Contract

The spike evidence must show:

- isolated fixture setup or a reproducible blocker,
- runner/config command used,
- stored agent output or explicit reason no agent output could be produced,
- deterministic post-run assertion or explicit blocker,
- tool/command/trace visibility assessment,
- ADR re-evaluation result and rationale.

## Fallback Rule

If Promptfoo cannot satisfy isolated, reproducible Codex/Coding-Agent execution without manual-only steps, static fake outputs, or non-reproducible workarounds, the result must be `FALLBACK_TO_INSPECT` or `REOPEN_EVALUATION`, not `ADOPT_PROMPTFOO`.
