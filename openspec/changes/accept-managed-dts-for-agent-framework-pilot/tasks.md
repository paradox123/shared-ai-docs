## 1. Managed exception contract

- [x] 1.1 Add the sibling managed-gate workspace, versioned configuration/evidence schemas, protected-boundary inventory, and public CLI tests that fail for absent operator approval, non-Consumption SKU, inactive spending limit, missing budget, target drift, and stored credentials.
- [x] 1.2 Implement the fail-closed Azure/preflight observation and immutable provenance checks through the public CLI without changing the historical OSS gate.

## 2. Real Agent Framework worker replacement

- [x] 2.1 Add public process-controller tests for one run, two distinct workers, an incomplete-activity termination point, bounded recovery, and exactly-once committed effects.
- [x] 2.2 Implement the pinned .NET Agent Framework workflow worker and controller with separate attempt and idempotent-effect evidence.
- [x] 2.3 Restore/build in locked mode and run the real two-worker probe against the provisioned Azure DTS task hub using `DefaultAzure` developer authentication.

## 3. Evidence and issue completion

- [x] 3.1 Produce correlated JSON/Markdown managed-pilot evidence and verify all protected LangGraph, Cloudflare, macOS/runtime/worktree, GitHub, and ProBara boundaries are unchanged.
- [x] 3.2 Preserve Issue 01 as closed `wontfix` under its OSS criteria, append the completed managed exception outcome, and make Issue 02 eligible only after a `go-managed-pilot` result.

## 4. Validation and review

- [x] 4.1 Run focused/full tests, locked restore/build checks, `git diff --check`, and `openspec validate accept-managed-dts-for-agent-framework-pilot --strict`.
- [x] 4.2 Refactor the touched surface for DRY, SOLID, and KISS issues, rerun verification, and complete standards/spec review before acceptance.
