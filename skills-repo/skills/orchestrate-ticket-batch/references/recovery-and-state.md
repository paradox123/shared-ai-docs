# Conditional identity and interruption recovery

Routine managed state uses [local-helpers.md](local-helpers.md); do not reconstruct its schema or patch it by hand. Start with `status`, reconcile pending actions and only then mutate. Preserve exact creation/send/merge/cleanup outcomes, permissions and reservation ownership. A changed cursor alone does not justify a shell call or detailed audit.

Keep durable state outside worker worktrees. Prefer the existing batch heartbeat directory, or `~/.codex/batches/<confirmed-coordinator-id>/` without scheduling. Normalize CODEX_HOME with ~/.codex as fallback. If the coordinator ID is unavailable, use a recorded unique local directory and resolve identity through supported tools; never guess.

## Missing worker identity

1. Preserve the creation response and dispatch timestamp. `clientThreadId` is provisional and must never be passed to task read/wait tools. Honor the initial required wait when a confirmed ID becomes available.
2. Use a registration callback or one bounded list_threads lookup; omission is inconclusive. A callback is helpful but never required to continue permitted registration.
3. If needed, resolve candidates with the bundled read-only metadata helper:

```sh
python3 "$SKILL_DIR/scripts/find_task_candidates.py" --index "$CODEX_HOME_RESOLVED/session_index.jsonl" --title "$RECORDED_TASK_TITLE" --not-before "$DISPATCH_LOWER_BOUND_RFC3339"
```

It reads one index snapshot, matches exact title and lower timestamp, deduplicates IDs and emits at most ten candidates. It does not read rollouts or write the index. Exit 0 means one candidate, 2 none/multiple, 3 malformed/unreadable. Check count/omitted; update time is not creation time.

4. Verify candidates directly with read_thread against ticket, repository/worktree and creation window. Never select by recency alone. Reconcile duplicates without creating more tasks or merging both.
5. For renamed titles/unavailable metadata, use the bounded session-review workflow owned by improve-skills only when permitted and task tools cannot resolve identity. Limit it to dispatch window, repo and known clues. Do not scan raw rollouts inline or search the whole home directory.
6. Allow one later bounded retry for lagging metadata. An unchanged failure needs a concrete recovery condition; do not ask repeatedly for links, infer absence or create a substitute.

Normalize task-tool JSON once. Use top-level turns, with legacy page.turns only as fallback; start with threadId alone when tool-version compatibility requires it.

## Scheduling and interruption

Messaging availability does not establish idle wake. Confirm it from an actual phase callback delivered after the coordinator ended its turn, not a probe task. Otherwise use an authorized recovery heartbeat or bounded active waits. If the user stops execution, save for manual resume rather than promise background continuation.

Use build-codex-automations and automation_update to reuse/configure the batch heartbeat within existing authorization; ten minutes is a recovery default, not a latency guarantee. Preserve notification preferences and remain quiet when unchanged. A wake observes known workers once, reconciles missing callbacks/uncertain operations and processes actionable work. Inspect affected ownership, worktrees and remote facts after interruption; ordinary callbacks do not require a whole-batch audit. Runtime downtime cannot be fixed by prompt instructions.

An unchanged pending send must not be retried blindly. Inspect destination messages or remote state and record confirmed, not-sent or unknown against the same request ID. Callback duplicates do not resolve unknown dispatch. Preserve reservations until the external fact is known. Worker results remain durable even if callback transport was denied.

## Old ledgers and permission failures

Do not migrate live batches merely because the shared skill changed. Explicit adoption preserves the old ledger as backup and all identities, original authority, receipts, custom fields, artifacts and uncertain operations. Reconcile live facts and isolation before activating a new path. A managed ledger must not be bootstrapped by inventing successful history; unsupported existing states remain on their original workflow until a verified migration is provided. Any heartbeat path change follows build-codex-automations.

Record an automatic approval denial verbatim with operation, worker, PR/head, target and original authority. Do not reinterpret it as a code failure. New evidence may justify a bounded retry only when it addresses the stated reason. If direct approval is required, present that concrete reviewable action with actual values and the worker link. Do not evade denial through another tool, identity, account or target. Park/release a holder only through the integration rules and confirmed cancellation; unrelated authorized work can continue. Recheck remote state on resume because the user may have completed the operation manually.
