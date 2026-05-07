# DWT-S0 Promptfoo-First Spike

This directory contains the one-time DWT-S0 framework spike. It is not part of
the recurring DocWorkflow Agent Delivery testsuite.

The probe uses Promptfoo `0.121.9` with the OpenAI Codex SDK provider against a
small read-only fixture. The required command contract pins the bundled Node
runtime and isolates `HOME` plus `npm_config_cache`.

Evidence is written under `evidence/`:

- `promptfoo-debug.txt`
- `promptfoo-validate-config.txt`
- `promptfoo-eval.txt`
- `promptfoo-eval.json` when the provider produces a result file
- `blocker-output.txt` when the provider cannot run reproducibly
- `assertion-output.txt`
- `spike-summary.json`

