# Microsoft Agent Framework OSS durability Gate 0

Decision: **no-go**

## Correlated provenance

- Source revision: `b31fea73491294280d0a7615980da629a551ebac` (live `b31fea73491294280d0a7615980da629a551ebac`)
- Gate source digest: `7611ea7f24e2a6014f1306a940b443f64114c47faf4c438ac7755281211b0f54`
- Dirty-state digest: `484d775e0f7a2af3b23b1a1bf30307eedcf104f2b1a37984544e76c18d6fb6eb`
- Package lock SHA-256: `4164a400b10eb8b8be7e4affe5e93d006333746fdb0765eecf2262afce96dadc`
- Component inventory SHA-256: `688fb89790c219cf539c90160d2f6b0f619f07a7f038201e53c4fd1386cbeef2`
- Runtime: .NET `10.0.203`, RID `osx-arm64`
- Configuration / contract: `v1` / `v1`
- Backend revision / protocol: `documentation-2026-05-05` / `Durable Task Scheduler gRPC via Microsoft.DurableTask.*.AzureManaged 1.18.0`
- Manifest SHA-256: `2d33ba1f78e7501bc2eeb85c299046775dccd21ef31a8a60a2b20b72737e4076`
- Live observation SHA-256: `d2dfd7e11e73cfa4ccf884246a184840c7e4163e512f12f7fc041e2b8031e4c8`

## Worker replacement

- Orchestration: `None`
- Workers / PIDs: `{}`
- Checkpoints: `[]`
- Effects: `{}`

## Failures

- `backend.managed-service`
- `backend.not-self-managed`
- `backend.not-open-source`
- `backend.unavoidable-service-cost`

## Protected boundaries

- `cloudflare-relay-source`: unchanged
- `langgraph-launch-agent`: unchanged
- `langgraph-managed-worktrees`: unchanged
- `langgraph-runtime`: unchanged
- `langgraph-source`: unchanged
- `macos-operations-source`: unchanged
- `probara-crm`: unchanged
