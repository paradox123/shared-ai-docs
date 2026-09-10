## Context

The completed OSS gate proved a real incompatibility: the pinned Agent Framework Durable Extension tuple supports Azure Durable Task Scheduler in production but not a production-capable self-managed open-source backend. The operator subsequently accepted DTS Consumption for this pilot and provisioned an isolated Free Trial subscription with spending protection, a five-unit resource-group budget, one scheduler, a dedicated clean task hub, an IP allowlist, and task-hub-scoped developer access.

The historical `microsoft-agent-framework-oss-gate/` evidence must remain truthful. The new work is therefore a separately named managed-pilot gate and a minimal sibling application, not an edit that changes `no-go` into `go` under the old OSS criteria.

## Goals / Non-Goals

**Goals:**

- Record the operator's managed-service exception and observable cost controls.
- Compile and run the exact pinned Agent Framework/Durable Task tuple against the provisioned DTS task hub.
- Prove one durable Agent Framework workflow continues across two distinct OS worker processes.
- Capture correlated JSON and Markdown evidence with protected-boundary fingerprints.
- Close Issue 01 honestly and restore Issue 02 to the eligible backlog only after direct verification.

**Non-Goals:**

- Claiming Azure DTS is open source or self-managed.
- Replacing or deleting the original OSS gate evidence.
- Implementing the semantic behavior of Issue 02 or later tickets.
- Introducing Temporal, Azure-hosted compute, client secrets, or shared writable state with the LangGraph pilot.

## Decisions

### Preserve the OSS result and add a distinct managed gate

The original result remains `No-Go (OSS)`. New evidence uses the decision `go-managed-pilot`, which means only that the explicitly accepted managed-service pilot passed. This prevents an operational override from corrupting the architectural audit trail.

Alternative considered: edit the original manifest so Azure becomes eligible. Rejected because the original schema intentionally treats managed service and unavoidable cost as disqualifying facts.

### Use a minimal sibling console probe

The new `microsoft-agent-framework-work-package-pilot/` directory contains only a pinned .NET console probe, its process controller, public CLI tests, configuration schema, and generated evidence. Worker one starts the workflow; worker two registers the identical workflow but never starts a second run.

Alternative considered: place the Azure probe inside the OSS gate. Rejected because the different decision semantics and allowed backend would blur the proven boundary.

### Terminate worker one inside the second activity's retry window

Activity one writes its committed effect and returns. Activity two writes a non-effect entry marker and waits before committing its effect. The controller observes the entry marker, terminates worker one, starts worker two, and waits for the original run to complete. The durable backend is responsible for redelivering the incomplete activity; completed activity one must be served from durable history.

The ledger uses an exclusive file lock and suppresses duplicate committed effect keys. The controlled proof expects one entry on each of the two workers for the interrupted activity and fails closed on any additional attempt; committed business effects must remain exactly once.

Alternative considered: kill immediately after activity one's local write. Rejected because a local write alone does not prove the activity completion was durably checkpointed.

### Separate committed effects from execution attempts

The evidence records activity entry attempts independently from committed effects. This avoids falsely claiming that activity code itself has exactly-once execution semantics. The proof is that completed work is not replayed and that the controlled idempotent effect boundary converges once.

### Use developer identity and external local configuration

The connection string uses `Authentication=DefaultAzure` and is read from the existing scratch env file. The worker constructs a `DefaultAzureCredential` with every provider except Azure CLI excluded, and the controller strips credential-bearing ambient variables before launch. The repository records only non-secret resource identities in evidence. No Azure token, client secret, or storage key is written to the application.

## Risks / Trade-offs

- **RBAC propagation or transient DTS delivery delays** → Use bounded waits and record explicit timeout evidence without creating a second run.
- **The laptop's public IP changes** → The DTS connection fails closed; update the scheduler allowlist deliberately before rerunning.
- **An activity is redelivered after its external side effect** → Use an operation-keyed idempotent effect ledger; record attempts separately from committed effects.
- **Trial credit or budget state changes** → Re-observe spending protection, SKU, and budget before every real probe.
- **Package preview behavior changes** → Restore in locked mode and correlate the exact source revision, lock digest, .NET SDK, and assembly versions.

## Migration Plan

1. Add the managed-gate contract and public CLI tests.
2. Add the pinned sibling console probe and fail-closed Azure preflight.
3. Run the real two-worker replacement against the dedicated clean task hub.
4. Record evidence and verify protected boundaries remain unchanged.
5. Update Issue 01 and the Issue 02 dependency state only on `go-managed-pilot`.

Rollback deletes only the sibling probe and its managed evidence. Azure resources are retained for the later pilot unless the operator explicitly requests deletion; the original OSS gate remains untouched.

## Open Questions

None for this bounded gate. Production hosting identity and long-term Azure budget policy belong to later deployment decisions.
