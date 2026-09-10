# Microsoft Agent Framework primary-source research

**Decision date:** 2026-09-05
**Question:** Can a local falsification spike test whether Microsoft Agent Framework (MAF) Workflows plus its Durable Extension preserves the LangGraph pilot's behavior and satisfies the distributed durability requirements through a self-hostable open-source path?

## Conclusion

**Yes—run the local spike, but treat it as a falsification test of a preview integration, not a parity demonstration.** The documented and source-visible pieces are sufficient to test graph routing, distributed durable workers, replay after worker loss, human waits, an external Codex process, and at-least-once failure handling. They do **not** supply the product's canonical event store, authenticated Operator API, control lease/fencing, idempotency ledger, or `interrupt`/`queue` command semantics. Those remain application responsibilities.

The hypothesis survives only if a small amount of custom application code can close the gaps without obscuring evidence and if Gate 0 proves a production-capable self-hostable open-source backend without a mandatory paid workflow service. If a hard trigger in [Stop triggers](#stop-triggers) fires, the Microsoft candidate stops and the existing LangGraph pilot remains the working baseline while another open-source approach is evaluated separately.

Labels below mean:

- **Documented** — stated by Microsoft or OpenAI documentation/API reference.
- **Source-confirmed** — visible in an official repository at the linked revision.
- **Inference** — architectural conclusion from documented/source behavior; must be tested.
- **Unknown** — the primary sources do not establish the required behavior.
- **Spike question** — an executable way to resolve an inference or unknown.

## What MAF covers, and what only Durable Task covers

| Required responsibility | Evidence-based assessment |
|---|---|
| Explicit graph, typed executors, edges/conditions, fan-out/fan-in, shared state, sub-workflows | **Documented MAF capability.** .NET uses `WorkflowBuilder`; executors, edges, events, and state share a graph/run model, with checkpoints at superstep boundaries. [MAF workflow concepts](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/) |
| Workflow and executor observability | **Documented MAF capability.** Built-ins include workflow start/output/error/warning, executor invoked/completed/failed, superstep start/completion, agent response/update, and request events; custom events are supported and consumed as a live stream. [MAF events](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/events) |
| In-process resume | **Documented MAF capability, not distributed durability.** Standard checkpoints contain executor state, pending messages, pending requests/responses, and shared state, but require a checkpoint manager/store and topology-compatible reconstruction. [MAF checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints) |
| Durable recovery across worker/process loss and distributed stateless workers | **Documented Durable Extension capability.** The extension runs graph workflows on Durable Task infrastructure; standard MAF checkpoint storage alone is explicitly distinguished from this distributed execution boundary. [Durable Extension, durable workflows](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions#durable-agent-framework-workflows) |
| Durable timers, imperative branching, activities, and external events | **Documented Durable Task capability.** Microsoft explicitly recommends durable orchestrations for these and durable MAF graphs for declarative typed routing. [Durable Extension](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions#durable-agent-framework-workflows) |
| External deterministic/non-agent work | **Source-confirmed.** A regular durable MAF executor is registered and invoked as a Durable Task activity; only agent, request-port, and sub-workflow executors receive special dispatch. This is a clean seam for a fake or external `AgentSessionAdapter`; Codex does not need to become a model-native MAF agent. [dispatcher](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs#L15-L89), [activity executor](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableActivityExecutor.cs#L13-L70) |
| Canonical `ImplementationRun` history, authorization, Control Lease/fencing, redaction, artifact retention, read projections | **Not a framework capability found in primary sources.** These must be domain/application services. Durable Task orchestration history and MAF agent/session history must remain implementation evidence, not the canonical domain history. |

## Exact local topology that can be tested

**Documented topology:**

```text
Operator/API client process
    |  DurableTaskClient (same or separate process)
    v
Durable Task Scheduler emulator container
    - gRPC endpoint: localhost:8080
    - task hub: default
    - dashboard: localhost:8082
    - orchestration/entity state: memory only
    ^
    |  worker polls the same task hub
Self-hosted .NET Generic Host worker process(es)
    - ConfigureDurableWorkflows / ConfigureDurableAgents
    - MAF workflow executors dispatched as Durable Task work
    - deterministic fake adapter, then bounded Codex child process
```

The official portable-SDK quickstart runs the emulator in Docker, then a worker and a separate client process; ports `8080` and `8082` are the scheduler connection and dashboard. [Durable Task SDK quickstart](https://learn.microsoft.com/en-us/azure/durable-task/sdks/quickstart-portable-durable-task-sdks) MAF's self-hosted model starts a Durable Task worker in the application's process, connects worker and client builders to the scheduler, and permits the client in the same process or a separate service. The host must provide its own APIs, networking, authentication, lifecycle, and deployment. [MAF self-hosted hosting](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions#bring-your-own-compute--self-hosted-hosting)

**Constraint:** the emulator stores orchestration and entity state only in local memory and is explicitly unsuitable for production. A worker/host crash is a valid recovery test only while the emulator remains alive; killing the emulator tests total backend loss, not durable recovery. [Durable Task Scheduler emulator](https://learn.microsoft.com/en-us/azure/durable-task/durable-task-scheduler/durable-task-scheduler#emulator-for-local-development)

**Inference:** the smallest useful spike should keep the emulator container alive, kill/restart worker and API processes independently, and run at least two worker instances once to prove task-hub handoff. Do not include Azurite unless using Azure Functions; the portable self-hosted topology requires only the scheduler emulator. Redis is needed only if evaluating the extension's distributed reliable token streaming; domain events should use the application event store instead. [MAF reliable streaming](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions#reliable-streaming)

**Unknown / Gate 0 stop condition:** Microsoft documents a production managed Durable Task Scheduler behind bring-your-own-compute workers, but the official emulator is not a persistent self-hosted production backend. Prove that another production-capable self-hosted open-source Durable backend works with the exact extension tuple before continuing beyond bootstrap. If it does not, stop this candidate.

## Failure, replay, external effects, and idempotency

### Durable Task / MAF

- **Documented:** Durable Task orchestrators are deterministic and are rebuilt by event-sourcing replay. Activities may perform I/O and nondeterministic work. [Durable Task programming model](https://learn.microsoft.com/en-us/azure/durable-task/common/programming-model-overview)
- **Documented:** activities have **at-least-once** execution. If an external effect succeeds and the worker fails before the result is recorded, the activity can run again. Microsoft therefore recommends idempotent activity logic. [Durable Task activity semantics](https://learn.microsoft.com/en-us/azure/durable-task/common/programming-model-overview#activities)
- **Documented:** external events are also at-least-once and can be duplicated after restarts/scaling/crashes; Microsoft recommends application event IDs and manual deduplication. [Durable external events](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-external-events)
- **Source-confirmed:** a regular MAF workflow executor is called through `CallActivityAsync` and receives a cancellation token in its executor body. [MAF durable dispatcher](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs#L68-L89), [executor invocation](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableActivityExecutor.cs#L27-L59)

**Inference:** neither framework provides exactly-once Git/GitHub/Codex effects. The adapter/activity needs an application-owned operation key such as `(run_id, activity_id, attempt_id, operation_kind)`, a durable state machine (`reserved -> started -> effect_observed -> adopted -> completed`), and reconciliation before any retry. For Git, adopt by expected branch/head/worktree markers. For GitHub, use deterministic marker/operation IDs. For Codex, persist and verify the returned thread ID; never infer success solely from process exit.

**Executable spike question — effect/result gap:**

1. A fake adapter atomically records external effect `E(operation_id)` in a separate local store and then blocks before returning.
2. Kill the worker at that point; restart another worker.
3. Pass only if the activity is redelivered or recovered, the adapter reconciles `E`, the effect count remains exactly one, and the orchestration completes with the adopted result.
4. Repeat with the real bounded Codex adapter at two gaps: after `thread.started` is observed but before the adapter mapping is committed, and after a file/Git effect but before activity completion.

If the real adapter cannot deterministically find/adopt the already-started Codex session or completed repository effect, the hypothesis fails for autonomous writes.

## Events, history, reconnect, and human waits

### What is emitted and retained

- **Documented MAF:** workflow/executor/superstep/request events and custom `WorkflowEvent` values are emitted for real-time consumption. [MAF event types](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/events#built-in-event-types)
- **Source-confirmed Durable Extension:** the current .NET streaming wrapper does not expose a broker log. It polls Durable Task `SerializedCustomStatus`, starts a consumer-local `lastReadEventIndex` at zero, and tracks pending request names in a process-local set. [Durable streaming implementation](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableStreamingWorkflowRun.cs#L87-L169)
- **Source-confirmed:** live custom status is capped at 16 KB and may retain only a trailing event window. Earlier workflow events are backfilled from the complete orchestration output **only after successful completion**. [live-status window](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowLiveStatus.cs#L30-L52), [completion backfill](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableStreamingWorkflowRun.cs#L171-L197)
- **Documented Durable Task Scheduler:** the dashboard exposes a timestamped orchestration History feed and lifecycle operations. Current Durable Task .NET source also exposes `GetOrchestrationHistoryAsync`, but this is scheduler history, not automatically the product's redacted domain event stream. [DTS dashboard](https://learn.microsoft.com/en-us/azure/durable-task/durable-task-scheduler/durable-task-scheduler-dashboard), [current .NET history API](https://github.com/microsoft/durabletask-dotnet/blob/bc2bc12ca5ee3a12a6e633250ade5efe6ae90ef4/src/Client/Core/DurableTaskClient.cs#L498-L516)

**Inference:** built-in workflow streaming is inadequate as the sole Operator event contract. A client that disconnects while the live window advances can wait until completion for missing events; a failed/terminated long run may never provide the complete MAF event list. There is no documented acknowledged-cursor protocol. Use an application event store/outbox with monotonically increasing per-run sequence, unique event ID, redaction before commit, and `GET/stream after=<cursor>` semantics.

**Spike question — reconnect:** emit more than 16 KB of numbered events, disconnect the observer, restart API/worker, reconnect from an acknowledged domain cursor, then fail the workflow before normal completion. Pass only if the public Operator seam returns every redacted event exactly once and in order. The Durable Task history/dashboard may be corroborating evidence but cannot be the only read-back surface.

### Human-in-the-loop restoration

- **Documented standard MAF:** checkpoints include pending requests; after restore, pending requests are re-emitted as `RequestInfoEvent`, and the caller can resume with responses. [MAF HITL checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop#checkpoints-and-requests)
- **Source-confirmed Durable Extension:** a request port is written to durable orchestration custom status, then waits on a Durable Task external event; the pending record is removed only after receipt. [durable request-port implementation](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs#L91-L132)
- **Documented Durable Task:** if an external event arrives before the orchestrator waits, it is saved and dispatched when the wait is registered; each received event completes one wait. [Task orchestration context](https://github.com/microsoft/durabletask-dotnet/blob/bc2bc12ca5ee3a12a6e633250ade5efe6ae90ef4/src/Abstractions/TaskOrchestrationContext.cs#L337-L377)

**Inference:** durable waiting is credible, but product-level exactly-one command acceptance is not supplied. Because external events are at-least-once and request-port names can be reused, responses need `command_id`, target activity/attempt, expected lease epoch, expected head SHA, and a domain inbox uniqueness constraint. The orchestrator must consume commands in domain sequence order and reject stale/duplicate/fenced commands before raising the framework event.

**Spike question — HITL:** kill the worker while a request is pending; submit duplicated, stale-lease, and valid commands from separate authenticated client processes; restart with two workers. Pass only if the pending request reappears, only the valid command advances the target attempt, and all accepted/rejected decisions remain in stable domain-event order.

## Cancellation, interruption, and exactly one next command

- **Documented Durable Task client surface:** clients can query, raise events, suspend, resume, and terminate orchestration instances. Suspend stops processing; terminate ends the orchestration. [Durable Task client operations](https://learn.microsoft.com/en-us/azure/durable-task/common/programming-model-overview#client), [DTS dashboard lifecycle](https://learn.microsoft.com/en-us/azure/durable-task/durable-task-scheduler/durable-task-scheduler-dashboard#manage-orchestrations)
- **Source-confirmed MAF wrapper limitation:** `IStreamingWorkflowRun` exposes event watching and request-port response, while its cancellation token only ends the observer stream; it does not define workflow cancellation. Use the underlying `DurableTaskClient` or a domain command/external event. [streaming interface](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/IStreamingWorkflowRun.cs#L11-L55)
- **Unknown:** primary MAF sources do not promise that terminating/suspending an orchestration promptly kills an already-running external child process, nor that one and only one queued domain command is delivered after interruption.

**Required application protocol:** `Cancel`, `interrupt`, and `queue` are commands against one explicit `(run, activity, attempt)` under the current Control Lease epoch. The worker must cooperatively cancel/kill Codex, record terminal process evidence, fence all later output from that attempt, then atomically select at most one next queued command. Orchestration termination alone is insufficient evidence.

**Spike question — cancellation race:** while the fake and then real Codex process are active, concurrently submit `interrupt`, two queued commands, a stale takeover, and cancellation. Kill/restart the API at each acknowledgment boundary. Pass only if the targeted process stops, no post-fence output mutates canonical state, one deterministic command becomes next, duplicates are rejected, and the final domain event order is identical from two clients.

## Versioned Codex `AgentSessionAdapter`

### Stable surfaces documented by OpenAI

- `codex exec` is a **Stable** non-interactive command. `--json` emits JSONL events including `thread.started`, turn lifecycle, item lifecycle, and errors. `codex exec resume <SESSION_ID>` resumes a specific stored non-interactive session. [OpenAI non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode#make-output-machine-readable), [resume](https://learn.chatgpt.com/docs/non-interactive-mode#resume-a-non-interactive-session)
- Interactive `codex resume` and `codex fork` are **Stable** CLI commands. `codex fork` creates a new chat from a previous interactive session, but the command reference does not document it as a headless `exec` subcommand. [OpenAI developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli#codex-resume)
- The stable Python SDK starts and resumes local Codex threads and pins a compatible Codex runtime; the TypeScript SDK documents start/continue/resume. [OpenAI Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)

### Programmatic but maturity-sensitive surface

`codex app-server` is labeled **Experimental** in the official command reference. Its JSON-RPC API nevertheless documents the exact primitives the desired adapter needs: `thread/start`, `thread/resume`, `thread/fork` with `forkedFromId`/session ancestry, `thread/read`, event notifications, `turn/steer`, and `turn/interrupt`; a successful interrupt ends the turn with status `interrupted`. [command maturity](https://learn.chatgpt.com/docs/developer-commands?surface=cli#command-overview), [app-server lifecycle](https://learn.chatgpt.com/docs/app-server#lifecycle-overview), [resume/fork/read](https://learn.chatgpt.com/docs/app-server#resume-a-thread), [interrupt](https://learn.chatgpt.com/docs/app-server#interrupt-a-turn)

OpenAI documents steering an active turn and queuing tool output into an active turn, but no general durable `queue exactly one next user command` contract. [app-server turn control](https://learn.chatgpt.com/docs/app-server#steer-an-active-turn)

### Adapter decision

Define `AgentSessionAdapter/v1` as a capability-negotiated boundary, not a mirror of whichever Codex binary is installed:

| Operation | v1 implementation/evidence |
|---|---|
| `StartFresh` | Stable `codex exec --json`; capture `thread.started.thread_id` before accepting later output. |
| `Resume(session_id)` | Stable `codex exec resume <id> --json`; require first emitted thread ID to equal the requested ID or fail closed. |
| `FreshRetry` | New persisted `codex exec` session; store ancestry only in the control-plane domain, never copy prior conversation automatically. |
| `Fork(session_id, last_turn?)` | Experimental app-server `thread/fork` in the spike; preserve returned `sessionId` and `forkedFromId`. Do not promise production support until the chosen pinned interface is accepted. |
| `Read` | Experimental app-server `thread/read`, or application-captured redacted JSONL evidence; do not parse undocumented rollout files as a stable API. |
| `Interrupt` | Experimental app-server `turn/interrupt` when available; otherwise terminate the owned OS process and mark capability-degraded. |
| `OpenInCodex(session_id)` | Required product capability with no assumed transport mapping. The spike must prove that the pinned Codex distribution can surface the same session or disclose the limitation and require explicit confirmation before a correlated handoff fork. |
| `QueueNext` | Domain inbox only. Start the next turn/process after the current attempt reaches a fenced terminal state. |

Pin both the adapter contract version and the Codex runtime/SDK version, capture the capability set at run start, and preserve raw process exit plus redacted JSONL as evidence. Do not mark a resume successful until the returned thread identity matches. The real-Codex portion of the spike should be bounded, non-ephemeral (so it can be resumed), sandboxed to a disposable worktree, and should not exercise irreversible remote effects.

## Package maturity and upgrade risk

As of 2026-09-05:

- `Microsoft.Agents.AI.Workflows` has a stable `1.20.0` package. [NuGet](https://www.nuget.org/packages/Microsoft.Agents.AI.Workflows/1.20.0)
- `Microsoft.Agents.AI.DurableTask` is still prerelease; the current gallery version is `1.16.0-preview.260730.1`, targeting .NET 8+, and depends on MAF/Workflows `>=1.16.0` and Durable Task client/worker `>=1.18.0`. [NuGet metadata](https://www.nuget.org/packages/Microsoft.Agents.AI.DurableTask/1.16.0-preview.260730.1)
- The AzureManaged Durable Task client and worker packages have stable `1.25.0` releases, but the Durable Extension's current repository pins `1.18.0` internally. This version skew is a compatibility test, not permission to mix latest versions casually. [client 1.25.0](https://www.nuget.org/packages/Microsoft.DurableTask.Client.AzureManaged/1.25.0), [worker 1.25.0](https://www.nuget.org/packages/Microsoft.DurableTask.Worker.AzureManaged/1.25.0), [extension dependency pins](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/Directory.Packages.props#L139-L146)
- **Source-confirmed defect risk:** the preview durable graph runner caps execution at 100 supersteps, logs when work remains, then still returns a normal result. [runner source](https://github.com/microsoft/agent-framework-durable-extension/blob/522e1d98afff58c251c4402578cb4d1187f91a84/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowRunner.cs#L173-L228) The official repository tracks this as an open bug against the published `1.16.0-preview.260730.1`. [issue #71](https://github.com/microsoft/agent-framework-durable-extension/issues/71)

For the spike, use a central package file plus lock file; pin the full resolved graph and emulator image digest, not `latest`. Start with the published Durable Extension `1.16.0-preview.260730.1` and its minimum compatible MAF/Workflows `1.16.0`; test AzureManaged `1.25.0` separately from the repository-aligned `1.18.0` tuple. Whichever tuple passes becomes the recorded spike baseline. Treat any package upgrade as a replay/contract migration: rerun saved-history recovery, event-order, HITL, cancellation, and effect-gap tests before adoption.

## Minimal executable falsification spike

1. **Topology proof:** start emulator (record digest), one worker, one API/client; schedule a named run ID and read it from a second process. Kill/restart only worker/API. **Fail** if another worker cannot resume the same run.
2. **Graph proof with fake adapter:** use a small MAF graph containing deterministic executors, fan-out/fan-in, a request port, and an external adapter executor. Emit numbered domain and MAF events. **Fail** if executor identity/topology cannot be reconstructed across restart.
3. **Effect-gap proof:** inject crashes immediately after the fake external effect and after session/effect observation but before activity return. **Fail** on duplicate or unadoptable effect.
4. **Event-store proof:** exceed the 16 KB live window, disconnect/reconnect by acknowledged domain cursor, then fail/terminate. **Fail** on gap, duplicate, unstable order, or reliance on successful workflow completion.
5. **HITL/control proof:** concurrent duplicate/stale/valid events from separate authenticated clients; transfer/takeover the lease; enforce lease epoch and Head-SHA fencing. **Fail** if more than one controller or next command wins.
6. **Cancellation proof:** interrupt/cancel while activity and child process run, then queue two commands and restart hosts. **Fail** if the child survives unowned, post-fence output is accepted, or more than one next command starts.
7. **Real Codex proof:** repeat StartFresh, Resume, Fork, FreshRetry, interrupt, and `OpenInCodex` with a pinned Codex runtime in a disposable worktree. **Fail closed** on session-ID mismatch, silent handoff-fork substitution, uncorrelated interactive output, undocumented transcript parsing, or inability to reconcile the `thread.started` commit gap.
8. **Upgrade/replay proof:** replay/recover the same fixtures under the alternate supported package tuple. **Fail** if the new tuple silently changes output, event order, pending-request restoration, or terminal classification.

## Stop triggers

Stop the Microsoft Durable candidate, retain the existing LangGraph pilot, and require a separately approved open-source architecture evaluation when any of these results is observed:

1. **External-effect safety:** a worker crash after Git/GitHub/Codex success but before activity completion can duplicate an irreversible effect, and a deterministic operation ID plus reconciliation/adoption cannot prevent it.
2. **Live evidence:** a failed, canceled, or long-running workflow cannot feed the public event store with gap-free, duplicate-free, stably ordered events from an acknowledged cursor without depending on terminal output or internal status polling.
3. **Control correctness:** duplicate/out-of-order external events can cause more than one command, approval, takeover, or queued successor to be accepted despite domain inbox deduplication and fencing.
4. **Cancellation ownership:** suspend/terminate/interrupt cannot promptly stop or fence the targeted external Codex process, or a restarted worker cannot determine whether it is safe to adopt, kill, or retry that process.
5. **HITL recovery:** pending requests are lost, cannot be rediscovered from a fresh client process, or accept a response against the wrong activity attempt after restart/rolling deployment.
6. **Durable backend fit:** production requires a supported persistent self-hosted scheduler and the extension cannot use one; the in-memory emulator does not satisfy this requirement.
7. **Preview/version cost:** the pinned package tuple cannot compile/run the vertical slice, has silent-success behavior such as unfinished work at `MaxSupersteps`, or an upgrade breaks saved-history recovery and no bounded compatibility layer fixes it.
8. **Operational complexity:** closing MAF gaps requires inventing a custom scheduler, replay/history engine, command protocol, or cancellation system whose correctness cannot be bounded and proved in the spike.
9. **Codex contract:** required Resume/Fork/Read/Interrupt behavior is available only through an experimental Codex surface that cannot be pinned, capability-negotiated, and made to fail closed for the product's risk level.

Passing the spike does not establish general equivalence. It establishes only that the selected, pinned MAF + Durable Task + adapter tuple can satisfy the control plane's observed contract with an acceptable amount of application code.
