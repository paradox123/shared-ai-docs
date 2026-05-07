# DWT-S0 Promptfoo-First Framework Spike

## Why

The DocWorkflow Agent Delivery Testsuite must reuse an existing agent/coding-agent eval framework rather than creating a generic custom harness. The parent spec and ADR recommend Promptfoo first, but final adoption is intentionally gated by a one-time spike.

## What

- Validate whether Promptfoo can drive Codex/Coding-Agent execution, or an accepted adapter, against isolated fixtures in this repository.
- Persist agent outputs, runner metadata, and deterministic assertion results as evidence.
- Produce an ADR re-evaluation result: `ADOPT_PROMPTFOO`, `ADOPT_WITH_LIMITATIONS`, `FALLBACK_TO_INSPECT`, or `REOPEN_EVALUATION`.
- Keep KI-fuer-KMU original specs read-only and use only temp fixtures or spike-local artifacts.

## Impact

- Blocks later L2/L3 agentic tests until the framework path is proven or redirected.
- Enables `DWT-S1` deterministic harness planning with clear reporting/evidence integration.
- Prevents green results based on static fake outputs, hidden fixture normalization, or manual-only workarounds.
