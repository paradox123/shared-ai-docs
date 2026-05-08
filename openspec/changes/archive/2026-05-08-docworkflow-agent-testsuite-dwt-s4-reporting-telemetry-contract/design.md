# DWT-S4 Reporting Contract Design

## Scope

DWT-S4 is a contract and deterministic validator slice. It prepares summary, telemetry, style and efficiency reporting for the DocWorkflow Agent Delivery Testsuite without executing agents or runtime delivery.

## Contract Shape

- Summary artifacts are JSON and carry suite version, roots, fixture manifest reference, per-case results, evidence truth labels, evidence links and runner environment.
- The accepted DWT-S1 retained `l1-summary.json` is treated as a legacy compatibility baseline. It may omit new v1 fields only when the DWT-S1 baseline fields remain present and valid.
- Telemetry manifests capture command classes, cwd/target categories, file-read/tool-call counters, forbidden command classes, budgets, verdict and justifications.
- Style gates validate Review Control Surface, Child Index, handoff, write-set, verification and next-action consistency.
- Efficiency gates fail forbidden runtime command classes in reporting-only/spec-only runs and distinguish justified warnings from hidden command drift.

## Boundaries

DWT-S4 does not create an L2 runner, does not run Promptfoo/Codex/Inspect, does not provision credentials and does not release DWT-S2, DWT-S3 or DWT-S5.
