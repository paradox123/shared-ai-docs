# Microsoft Agent Framework managed durability gate

Decision: **go-managed-pilot**

## Operator exception and Azure controls

- Approval: accepted `True` on `2026-09-06` for `isolated-agent-framework-pilot`.
- Azure DTS Consumption scheduler: `dh-agent-framework-pilot` at `https://dh-agent-framew-c2f7endt.northeurope.durabletask.io`.
- Subscription/tenant: `3c8f1707-52b9-43cc-9486-30faab0af3f0` / `3602223d-667f-4cff-a98a-6c4ecb75f18c`; spending limit `On`.
- Task hub: `agent-framework-isolated-pilot-v1`; network `Enabled`; allowlist `['92.211.110.7/32']`.
- Budget: `agent-framework-pilot-5`, amount `5.0`, monthly thresholds `[50.0, 80.0, 100.0]`.
- Authentication: DefaultAzure constrained to the observed Azure CLI user `9f604eb0-2adb-47a0-9e5d-382bf6897c40`; no stored cloud credential is forwarded.

## Durability proof

Run `managed-gate-71d21049-4f6b-4b4a-9a20-bff0f1ac2642` was started as one durable run. The worker replacement used distinct processes `{'managed-probe-worker-1': 48056, 'managed-probe-worker-2': 48128}`. Worker 1 was terminated after entering checkpoint two; Worker 2 resumed that checkpoint and completed the existing run. Activity attempts: `{'checkpoint-one': ['managed-probe-worker-1'], 'checkpoint-two': ['managed-probe-worker-1', 'managed-probe-worker-2']}`.

The exactly-once effect ledger contains `{'checkpoint-one': 1, 'checkpoint-two': 1}` and the run-start count is `1`.

## Immutable provenance

- Repository revision: `b31fea73491294280d0a7615980da629a551ebac`.
- Pilot source SHA-256: `249c1a9d54f6ed34a7fccb875bc75748d97b64bb21cfdc7d99fd09acb6f30744`.
- Package lock SHA-256: `fc558079f3b1947b020e10eeeef454700d4a6bcb2647cdc72da5d450fe60f4ef`.
- Runtime: .NET `10.0.203` / `osx-arm64`.
- Packages: `{'azureIdentity': '1.17.1', 'agentFrameworkDurableTask': '1.16.0-preview.260730.1', 'agentFrameworkWorkflows': '1.16.0', 'durableTaskClientAzureManaged': '1.18.0', 'durableTaskWorkerAzureManaged': '1.18.0'}`.
Config digest: `e9a692aa9e21f8032154f71500f09d97b18e178dbb138938f71df58990ff5aca`. Observation digest: `a2455e0acf211a66adfe5ab197ae2069d6770cbc0518ba6cc89c2758cbaddfc3`.

## Isolation

All protected boundaries unchanged: `True`.

- `cloudflare-relay-source`: before `679d8b681c9a6b2075d44cea64fefd86a29926f9d3ef48f126d77ec57b6caa4a`, after `679d8b681c9a6b2075d44cea64fefd86a29926f9d3ef48f126d77ec57b6caa4a`
- `github-repository-config`: before `cd50f79e9b455bfa00e67cec11a7bf544977d45e837308085e7575035bd06834`, after `cd50f79e9b455bfa00e67cec11a7bf544977d45e837308085e7575035bd06834`
- `langgraph-launch-agent`: before `07ec25459b32754999dd2dff2392a8d4d681b378c2a29a04767183c4c3cb38ce`, after `07ec25459b32754999dd2dff2392a8d4d681b378c2a29a04767183c4c3cb38ce`
- `langgraph-managed-worktrees`: before `4404ddb036ce3a840dd23cdcf8c77f37824be59ccbf2b9afd93c4e6174713647`, after `4404ddb036ce3a840dd23cdcf8c77f37824be59ccbf2b9afd93c4e6174713647`
- `langgraph-runtime`: before `fabb4e78e571f7fc79f0d9cb14ca51ef41efba7b38d511d154b0925c7a1d32f8`, after `fabb4e78e571f7fc79f0d9cb14ca51ef41efba7b38d511d154b0925c7a1d32f8`
- `langgraph-source`: before `9b71089dcdc77180a1fa51aa52d0865508a53884468c60749cbd5e3627400ca5`, after `9b71089dcdc77180a1fa51aa52d0865508a53884468c60749cbd5e3627400ca5`
- `macos-operations-source`: before `8592f9c226b305b176c8226c8f5d3c7f177eab422312e4194ff9b0e3cca208a7`, after `8592f9c226b305b176c8226c8f5d3c7f177eab422312e4194ff9b0e3cca208a7`
- `probara-crm`: before `d95d900c6520103ab023e8aa82028d5b73447f5d361c50cc261aa7bd8ba6d420`, after `d95d900c6520103ab023e8aa82028d5b73447f5d361c50cc261aa7bd8ba6d420`

## Gate failures

- None.
