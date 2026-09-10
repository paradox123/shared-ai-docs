## Why

The OSS durability gate correctly proved that the pinned Microsoft Agent Framework tuple has no production-capable self-managed open-source backend. The operator has since explicitly accepted Azure Durable Task Scheduler Consumption for the isolated pilot, so the managed-service exception and the real worker-replacement evidence must be recorded without rewriting the historical no-go.

## What Changes

- Record an explicit, pilot-scoped operator override that permits Azure Durable Task Scheduler Consumption while keeping Temporal excluded.
- Require observable Trial/spending-limit and resource-group budget controls before the managed probe starts.
- Add an isolated sibling .NET probe using the pinned Agent Framework and Durable Task packages.
- Kill worker one during an incomplete activity, start worker two, and prove continuation of one run with every committed effect recorded exactly once.
- Correlate Azure resource identity, package lock, runtime, run identity, worker processes, checkpoints, effects, and protected-boundary fingerprints in machine- and human-readable evidence.
- Reopen only the Microsoft pilot dependency edge after the managed probe passes; preserve the original OSS gate result as a historical no-go.

## Capabilities

### New Capabilities

- `agent-framework-managed-dts-pilot-gate`: Explicitly governed Azure DTS Consumption exception and real two-worker durability qualification for the pinned Microsoft Agent Framework pilot.

### Modified Capabilities

None.

## Impact

- Adds an isolated `microsoft-agent-framework-work-package-pilot/` bootstrap probe and tests.
- Uses the already provisioned Azure DTS Consumption scheduler and a dedicated clean task hub through developer identity authentication; no credential secret is committed.
- Adds new managed-pilot evidence while leaving `microsoft-agent-framework-oss-gate/` evidence immutable.
- Updates the Microsoft pilot issue status and downstream dependency state only after direct Azure-backed verification passes.
- Does not modify the LangGraph pilot, Cloudflare relay, macOS services, their runtime data/worktrees, GitHub configuration, or ProBara CRM.
