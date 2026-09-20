# Identity recovery and durable batch state

## Ledger and heartbeat

Use one ledger for one batch. Prefer `~/.codex/automations/<actual-automation-id>/memory.json` beside the existing heartbeat; for a run without scheduling use `~/.codex/batches/<confirmed-coordinator-id>/memory.json`. Normalize `CODEX_HOME` with `~/.codex` as fallback. Do not assume shell variables survive tool calls. If the current task ID is unavailable, use a recorded unique local batch directory and resolve the coordinator identity through supported tools; never guess an ID.

For new batches use the versioned JSON ledger and CLI in [local-helpers.md](local-helpers.md). Retain an existing ledger in its original format until explicit adoption; do not rename or overwrite it merely because the default changed.

Read the current ledger before deciding or writing. Keep one compact batch header, one state row/record per ticket and a short transition history. Never collapse concurrent workers into a single current-ticket field. Store:

- Batch identity: original user task/request reference, repository/remote, Codex projectId/hostId, explicit user target branch and provenance, concurrency limit (default 3), dependency/conflict graph, fixed ordered ticket list, scope/permission limits, optional prototype, automation ID.
- Each ticket: issue URL, requested title, UTC dispatch time, clientThreadId separately from threadId, worker host/worktree/owned local and remote branch refs, starting target SHA, change areas, dependencies, slot reservation/parked status, phase, wait cursor, last observation and concrete next action.
- Technical completion: delegated acceptance request and outcome, current completion-record path from code-review, content identity and next pending action. Preserve old reviewer receipts during adoption without inventing missing coverage.
- Closeout: per-ticket deferred status/archive paths and batch closeout PR/head/merge/verification; keep activation evidence per ticket.
- Evidence: critical verification requested/completed, artifact paths, inspected results, accepted SHA/manifest and tested target SHA, material limitations, durable copied evidence paths/hash verification.
- Integration reservation: one holder, candidate PR/head, tested target SHA, preparation/merge-grant status and unresolved merge outcome. Never release an uncertain mutation just because the worker is idle.
- Delivery per ticket: PR URL/number/head/base, remote merge commit and accepted-content mapping, combined checks and closed-ticket verification.
- Cleanup per ticket: evidence preservation, worktree removal, local/remote branch removal and worker archival, each with pending/outcome status and verified ownership/head. Preserve exact retained refs/paths and causes for cleanup-blocked items.
- Pending action: operation, destination, payload/brief intent, timestamp, dispatch outcome; plus any unresolved rejection and required recovery event.

For a versioned JSON ledger use `batch_state.py checkpoint` with the last observed revision and a scoped patch. It preserves omitted fields, rejects stale writes and replaces atomically under a local lock; it does not validate acceptance or authorize phases. For older ledgers preserve their format and write atomically until adoption. Only the coordinator updates the ledger; workers return facts through task results. Re-read before update and avoid overlapping coordinators. Do not rewrite stable automation instructions with thousands of characters of new runtime history at every poll. Store its real ledger path in the heartbeat prompt and point it to this skill.

Create/update the heartbeat via `automation_update` using `build-codex-automations` and current tool schema. Ten minutes is a reasonable recovery default if the user provided no interval; it is not a latency guarantee. Reuse an existing batch heartbeat, preserve notification settings, and stay quiet on unchanged state. Persistent scheduling does not replace processing actionable completions during a running turn.

Before each create/send/merge/cleanup mutation, save its ticket-specific `pending_action`; one global field must not overwrite another worker's pending operation. After a response, save returned IDs or outcome. If the response is lost, use identity recovery or inspect the destination's latest messages before retrying. Do not claim exactly-once dispatch when tools cannot guarantee it. If whether a mutating action happened remains uncertain, preserve that uncertainty and stop the dependent step.

## Adopt an older ledger

Explicitly select this batch for adoption, keep its original ledger as a backup, and map all existing fields (including custom fields) into a new versioned JSON ledger. Never fabricate a missing identity, target, review, pending-action outcome or cleanup result. Confirm the mapping against live facts before activating the new ledger path. A live heartbeat path update follows `build-codex-automations`.

Migrate its known current ticket into one ticket record and completed tickets into verified delivery records; preserve IDs, original authority, artifacts and uncertain actions. Do not invent cleanup success for previously delivered work. Reconcile actual worktrees/branches before adopting cleanup. If the original user explicitly named the target, retain it; an inferred old main/default value is insufficient and requires user input before new dispatch. Existing shared-checkout workers need safe isolation before concurrent writing. Do not restart them merely to obtain worktree setup.

Update only this batch's heartbeat definition when adopting the new workflow. Reconcile pending delivery before introducing parallel dispatch. Never upgrade an unrelated live batch or pilot automatically merely because its shared skill file changed.

## Resolve asynchronous creation

1. Record the exact create_thread response and dispatch time. A real threadId can be checked directly. A clientThreadId is only a UI creation reference.
2. Try the worker's available callback or one bounded `list_threads` call. Missing listing is inconclusive. Do not require a callback: it can be unavailable or denied.
3. If still unresolved, perform a read-only, batch-scoped metadata lookup with the bundled helper. This recovery is part of locating this batch's created tasks; respect higher-priority filesystem/privacy limits. Read only the exact metadata index, filter by the exact requested title and a lower timestamp bound just before dispatch, and emit matching fields only.

Resolve the actual skill directory and assign real values before running this example:

```sh
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
python3 "$SKILL_DIR/scripts/find_task_candidates.py" \
  --index "$CODEX_HOME_RESOLVED/session_index.jsonl" \
  --title "$RECORDED_TASK_TITLE" \
  --not-before "$DISPATCH_LOWER_BOUND_RFC3339"
```

The helper uses only Python's standard library, never writes to the index and never opens rollouts. It snapshots the file once, matches exact `thread_name`, deduplicates IDs and emits at most ten candidates. Exit 0 = one **candidate**, 2 = none/multiple, 3 = malformed/unreadable input. Inspect `status`, `count` and `omitted`; a candidate is never a confirmed identity. Later `updated_at` values must remain eligible because update time is not creation time.

4. Check candidates with `read_thread`. Confirm actual ticket assignment, repository/worktree context and creation time near dispatch, not just a matching title. For multiple candidates, do not select the most recent merely by ordering. If two valid workers exist, record the duplicate and reconcile ownership without starting more work or merging both.
5. If the title was normalized/renamed, the index is unavailable or no candidate validates, use the **bounded** session review workflow owned by `improve-skills` only when authorized and tools cannot supply the needed identity. Its `references/codex-desktop-session-review.md` owns resolver/evidence parsing; do not create inline raw-rollout scanners. Restrict to dispatch window, repository and recorded identity clues; do not search the whole home directory. This deeper fallback is conditional, not startup work on every heartbeat.
6. Metadata may lag creation. Record the attempt and permit one later check after a bounded wait. After an unchanged failure, report the specific unavailable/ambiguous source and recovery condition once. Do not repeatedly ask the user for a link, declare the task nonexistent, or create a substitute. If user input is ultimately essential, ask for the smallest missing fact without sending a placeholder-filled repair prompt.

## Approval failure recovery

Record the exact denied operation, PR/head/target, reviewing tool's stated reason and original authorization provenance. Do not reinterpret an automatic denial as a code failure or a missing acceptance artifact.

If direct approval is required, make the result reviewable and present an executable instruction containing actual values, for example: “Ich autorisiere PR [tatsächliche Nummer], Head [tatsächlicher SHA], nach [expliziter Nutzer-Zielbranch] in [Repository] zu mergen und das zugehörige Ticket zu schließen.” Replace these fields with real values before presenting it. Link the specific worker where approval is required. Preserve the open PR and park the affected ticket. Follow the integration reference to revoke any outstanding grant and release its reservation only after confirmed quiescence and no uncertain mutation; unrelated authorized delivery may then continue. Do not route the same denied action through another task/tool, change account identities, disable review or promise that another prompt will always fix the runtime policy.

Fresh evidence may justify a bounded retry when it addresses the reason (for example, proving the already-authorized destination repository). An unchanged refusal needs new authority or an external-state change, not repeated rewording. On resume, verify actual PR state before retrying because the user may have merged it manually.
