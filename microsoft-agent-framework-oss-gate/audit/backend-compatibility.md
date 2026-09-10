# Backend compatibility audit

Audit date: 2026-09-05

Gate source revision: `b31fea73491294280d0a7615980da629a551ebac`

Gate outcome: **no-go**

## Restored and compiled tuple

The gate-only audit project restored with its committed NuGet lock and built on
.NET SDK `10.0.203` / `osx-arm64`:

| Direct package | Resolved version | Role |
| --- | --- | --- |
| `Microsoft.Agents.AI.DurableTask` | `1.16.0-preview.260730.1` | Agent Framework Durable Extension |
| `Microsoft.Agents.AI.Workflows` | `1.16.0` | Agent Framework workflow runtime |
| `Microsoft.DurableTask.Client` | `1.18.0` | Durable client abstraction |
| `Microsoft.DurableTask.Client.AzureManaged` | `1.18.0` | DTS client transport |
| `Microsoft.DurableTask.Worker` | `1.18.0` | Durable worker abstraction |
| `Microsoft.DurableTask.Worker.AzureManaged` | `1.18.0` | DTS worker transport |

`audit/packages.lock.json` resolves 57 direct and transitive NuGet components.
`audit/components.json` records each exact version, NuGet content hash, package
source, SPDX licence source, and unavoidable package-level service cost. The
licence inventory contains 50 MIT, six Apache-2.0, and one BSD-3-Clause
component. Two legacy packages without a NuSpec SPDX expression have explicit,
versioned source overrides in `audit/licence-overrides.json`.

Verification commands:

```bash
dotnet restore audit/Audit.csproj --locked-mode
dotnet build audit/Audit.csproj --no-restore
dotnet run --project audit/Audit.csproj --no-build
python3 audit/inventory.py --lock audit/packages.lock.json --output audit/components.json
```

## Compatibility finding

1. The Agent Framework Durable Extension package consumes the modern
   `Microsoft.DurableTask.Client` and `Microsoft.DurableTask.Worker`
   abstractions. Its self-hosted examples register the corresponding
   `AzureManaged` transports and connect them to Durable Task Scheduler.
2. Microsoft's hosting-model documentation states that standalone Durable Task
   SDKs use Durable Task Scheduler exclusively. Azure Storage, MSSQL, and
   Netherite are BYO providers for Durable Functions, not supported backends for
   the standalone SDK tuple used by the Agent Framework console/self-hosted
   integration.
3. Durable Task Scheduler is a Microsoft-operated managed backend billed
   separately by Capacity Unit or dispatched action. Its server implementation
   is not supplied as a production self-managed open-source backend.
4. The local DTS emulator stores state in memory and is documented as unsuitable
   for production. Keeping it alive while replacing workers would prove only a
   development scenario and cannot pass Gate 0.
5. The classic open-source Durable Task Framework has pluggable providers, but
   it is explicitly a different hosting stack from the modern standalone SDK.
   No production-supported worker adapter from the pinned Agent Framework tuple
   to an open-source PostgreSQL/SQLite scheduler is present in the pinned graph.

Primary evidence:

- [Agent Framework Durable Extension hosting](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions)
- [Durable Task hosting-model comparison](https://learn.microsoft.com/en-us/azure/durable-task/common/choose-orchestration-framework)
- [Durable Task SDK overview](https://learn.microsoft.com/en-us/azure/durable-task/sdks/)
- [Durable Task Scheduler billing](https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler-billing)
- [DTS emulator limitation](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-task-scheduler/durable-task-scheduler)
- [Modern .NET SDK versus classic DTFx](https://github.com/microsoft/durabletask-dotnet/tree/v1.18.0)
- [Pinned extension package references](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Microsoft.Agents.AI.DurableTask.csproj)
- [Pinned self-hosted sample uses AzureManaged transports](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/samples/DurableWorkflows/ConsoleApps/01_SequentialWorkflow/Program.cs)

## Gate consequence

The production-backend eligibility check fails on `managed-service`,
`not-self-managed`, `not-open-source`, and `unavoidable-service-cost`. The real
two-worker probe is therefore prohibited and was not started. The sibling
`microsoft-agent-framework-work-package-pilot/` directory remains absent, and
issues 02–14 must not begin under this Microsoft Durable candidate.

The retained decision and isolation fingerprints are under `evidence/`. They
show the LangGraph source/runtime/worktrees, Cloudflare relay, macOS LaunchAgent,
and ProBara CRM boundaries unchanged across the gate execution.
