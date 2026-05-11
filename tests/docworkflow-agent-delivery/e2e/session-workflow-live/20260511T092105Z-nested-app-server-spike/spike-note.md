# Nested App-Server Spike Note

## Verdict

NOT READY for nested visible child launch from inside an already app-server-launched Codex parent session.

This closes the current visible AppSession spike as diagnosed, bounded, and reusable. It is not an S3 or MD-E2E-5 acceptance result.

## Canonical Evidence

- Parent launch: `launches/parent/20260511T093128Z-spike-parent/evidence.json`
- Child launch: `launches/20260511T093315Z-spike-c1/evidence.json`
- Parent transcript: `launches/parent/20260511T093128Z-spike-parent/app-server-transcript.jsonl`
- Child transcript: `launches/20260511T093315Z-spike-c1/app-server-transcript.jsonl`
- Child stderr: `launches/20260511T093315Z-spike-c1/app-server-stderr.log`
- Process snapshot: `process-list-during-child-initialize-exact-parent.txt`

## Repro Commands

Parent launch from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T092105Z-nested-app-server-spike/handoffs/parent-handoff.md --target-id SPIKE-PARENT --mode launch --agent codex --adapter codex-app-server --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs --out tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T092105Z-nested-app-server-spike/launches/parent
```

Nested child command executed by the parent:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T092105Z-nested-app-server-spike/handoffs/spike-c1-handoff.md --target-id SPIKE-C1 --mode launch --agent codex --adapter codex-app-server --initiating-project-cwd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs --out tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T092105Z-nested-app-server-spike/launches
```

## Finding

The parent visible app-server session launches and completes normally. The nested child launcher starts from inside that parent session and creates child launch artifacts, but its `codex app-server --listen stdio://` transport does not answer the first JSON-RPC `initialize` request.

The child transcript contains exactly one line: the client `initialize` request. No server response, `thread/start`, `thread/name/set`, `turn/start`, or `thread/list` is observed.

The child stderr contains:

```text
WARNING: proceeding, even though we could not update PATH: Operation not permitted (os error 1)
Error: Operation not permitted (os error 1)
```

The launcher now records this as deterministic blocked evidence:

```json
{
  "status": "blocked",
  "failure_phase": "app_server_initialize_timeout",
  "failure_method": "initialize"
}
```

The child did not write `target/output/spike.txt`, so this is not a successful nested child delivery.

## Closeout Decision

The visible AppSession primitive is accepted only for launches initiated outside an already-running app-server-backed Codex turn. Nested child launch from the parent session is explicitly closed as unsupported for the current MD-E2E-5 path.

The implemented timeout/evidence change is retained because it prevents future nested or otherwise blocked app-server launches from hanging indefinitely and preserves phase-specific evidence for review.

## Transport Recommendation

A child launch from inside the parent session cannot safely reuse the parent's existing app-server stdio transport with the current launcher contract. The parent has no exposed transport handle or IPC channel that can be passed to a nested `AgentDeliverySessionLauncher.cs` process, and the launcher contract currently starts a fresh `codex app-server --listen stdio://` process per launch.

For the MD-E2E-5 runner, the practical safe design is an external control process:

1. Parent visible session produces explicit child launch requests only.
2. External controller reads those requests and starts visible child sessions from outside the parent app-server session.
3. Controller persists child `evidence.json`, transcripts, stderr, and process snapshots.
4. Parent closeout consumes persisted child evidence instead of starting nested `codex app-server` processes itself.

A future optimization could keep one external app-server client process and issue multiple `thread/start` calls over that single controlled transport, but that should still live outside the parent Codex turn.
