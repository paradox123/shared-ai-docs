---
status: accepted
date: 2026-09-05
---

# Prefer Microsoft Agent Framework for the .NET control-plane spike

The first local architecture spike for the `WorkPackageControlPlane` will use Microsoft Agent Framework for .NET together with its Durable Extension and Durable Task. Agent Framework's graph-based .NET workflows are a credible peer to the LangGraph workflow layer used by the existing pilot, while the Durable Extension addresses persistent sessions, checkpoints, distributed workers, external events, human-in-the-loop waits, and recovery. The team's existing .NET expertise makes this the preferred implementation direction when the product semantics and open-source operating constraints are satisfied.

This decision selects a **preferred spike candidate**, not an unverified claim of feature or operational equivalence. Microsoft Agent Framework becomes the preferred implementation foundation only if the local spike proves the specification's complete failure, remote-intervention, role-change, observability, and recovery path. The existing LangGraph pilot remains implemented, independently runnable, and unchanged as the behavioral baseline.

The candidate must have a production-capable, self-hostable open-source backend path without mandatory additional framework or managed workflow-service licence fees. Temporal and paid managed workflow services are excluded as candidates and fallbacks. If the Microsoft candidate cannot meet this Gate 0, the spike stops and the LangGraph pilot remains in service while a different open-source option is evaluated through a separate decision.

Codex remains the agent harness. Agent Framework may coordinate agent activities, but it must invoke Codex through a versioned `AgentSessionAdapter` that preserves observable events and the distinct semantics of new session, read, resume, fork, stop, `interrupt`, `queue`, and targeted `Open in Codex`. Opening uses the same session where safely supported or an explicitly confirmed, correlated handoff fork otherwise; it never bypasses the Control Lease. Framework-managed conversation state must not become the canonical `ImplementationRun` state or cause the complete run history to be loaded into every agent context.

## Considered Options

- **Continue with LangGraph:** retain as the executable reference, unchanged working pilot, and safe baseline if the additional .NET candidate does not pass.
- **Microsoft Agent Framework without Durable Extension:** insufficient for the target because ordinary workflow checkpoints alone are not the distributed durable-execution boundary required by the specification.
- **Microsoft Agent Framework with Durable Extension and Durable Task:** selected for the first local spike because it combines the workflow and durable-execution layers with first-class .NET support.
- **Temporal Core or Temporal Cloud:** excluded by product decision; neither is an implementation target nor a fallback.
- **Paid managed workflow services:** excluded from the pilot's viable production path even when a local development emulator exists.

## Consequences

- The spike starts locally with bring-your-own-compute workers. Before the larger semantic slices, Gate 0 must prove a production-capable, self-hostable open-source Durable backend compatible with the pinned integration. The in-memory Durable Task Scheduler emulator is development support only and cannot pass Gate 0.
- The .NET pilot will be created later under the new top-level directory `microsoft-agent-framework-work-package-pilot/`. It does not replace or modify `langgraph-github-issue-pilot/`, its Cloudflare relay, macOS operation, runtime state, managed worktrees, or ProBara CRM configuration.
- The implementation reuses the existing pilot's public contracts, failure cases, fixtures, and observable behavior as a comparison baseline; it is not a line-by-line Python-to-C# port or a migration.
- The spike must prove adoption of already completed Git/GitHub effects, stable correlation across run/activity/attempt/session/head, gap- and duplicate-free stream reconnect, context-isolated reviews, and the full Control-Lease/Transfer/Forced-Takeover contract.
- Operator Client, repository-derived authorization, redaction, artifact retention, Work-Package projections, and the Agent Evolution Loop remain application responsibilities unless the spike supplies direct contrary evidence.
- Preview or prerelease packages used by the Durable Extension are a recorded maturity risk and require version pinning plus an explicit upgrade and exit strategy that leaves the LangGraph pilot intact.

## Evidence

- [Make-or-Buy decision record](../../.scratch/distributed-codex-work-package-control-plane/make-or-buy-entscheidungsvorlage.md) compares the six sourcing and hosting variants against the same gates and weighted criteria.
- [Solution research](../../.scratch/distributed-codex-work-package-control-plane/make-or-buy-solution-research.md) records the primary-source findings, maturity caveats, TCO drivers, and historical comparisons.
- [Microsoft Agent Framework workflow concepts](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/) document graph-based .NET workflows with typed executors, events, fan-out/fan-in, checkpointing, and human-in-the-loop mechanisms.
- [Microsoft Agent Framework Durable Extension](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions) documents persistent sessions, durable Agent Framework workflows, recovery, distributed workers, external events, reliable streaming, and self-hosted or Azure Functions hosting.
- [Microsoft Agent Framework repository](https://github.com/microsoft/agent-framework) documents the MIT-licensed multi-language framework, including first-class .NET support, orchestration patterns, and OpenTelemetry observability.
