# Local mechanical helpers

Run `python3 <resolved-skill-dir>/scripts/batch_state.py --help`. Python standard library only. These commands do not call task APIs, Git or automations. They compare supplied facts; they cannot establish live ownership, semantic coverage, acceptance or permission. Normalize task-tool responses before creating snapshots. Keep inputs, ledgers and manifests in the batch directory, outside disposable worker worktrees.

Exit codes: **0** ready/unchanged, **2** diverged/blocked, **3** invalid/unreadable input. Results are JSON; changed-field names and paths are reported, not raw worker prose. CLI usage errors use argparse's normal exit 2. A `ready` result from a mechanical check never means the ticket is accepted.

## Compare observations and assignment

```sh
python3 "$SKILL_DIR/scripts/batch_state.py" compare \
  --previous "$BATCH_DIR/previous.json" --current "$BATCH_DIR/current.json"
```

Both snapshots include nonempty `ticket`, `thread_id`, `worktree`, `branch`, `target` and `status` (`running`, `ready`, `blocked`, `error`). `ready` means the worker explicitly reported readiness for the **current phase**, not that a tool merely said idle/completed. An optional `pending_action` carries unresolved dispatch information. Include candidate head/target SHA, blocker, evidence revision and other meaningful facts when they change.

Only top-level `wait_cursor` and `observed_at` are ignored for comparison. Persist the latest cursor even for `unchanged`. A changed assignment reports `diverged`; an incomplete assignment reports `blocked`. A changed blocked/error or unresolved pending action reports `blocked`; a matching ready observation reports `ready`; other meaningful changes report `diverged`. Repeated identical blockers report `unchanged`; the ledger still retains their blocked phase and recovery condition.

On `unchanged`, continue a 60-second bounded wait without detail reads, file probes or extra worker messages. On change, inspect the affected result and act once. On resume or before external mutation, reconcile the required live facts regardless of the last comparison. Unregistered provisional IDs use the existing identity recovery flow, not fabricated snapshots.

## Checkpoint a JSON ledger

```sh
python3 "$SKILL_DIR/scripts/batch_state.py" checkpoint \
  --ledger "$BATCH_DIR/memory.json" --expect-revision 0 --patch "$BATCH_DIR/initial.json"
```

Initial patch shape (fill real values):

```json
{
  "batch": {"id": "batch-id", "repository": "/absolute/repo", "target": "release/wiki"},
  "tickets": {"01": {"phase": "queued", "pending_action": null}}
}
```

Add authority provenance, frozen scope, dependencies, identities, reviews and other fields required by recovery-and-state.md. The helper inserts `schema_version: 1` and `revision: 1`. Subsequent patches recursively merge object fields and replace explicit scalar/list/null values; omitted fields survive. Pass the last observed revision. Managed schema/revision and existing batch id/repository/target cannot be patched. Ticket objects cannot be removed with null. This is bookkeeping, not a phase-transition validator: only the coordinator may record a justified transition or clear a reconciled pending action.

For example, a cursor checkpoint patches only `tickets.<id>.wait_cursor`. Before sending a request, checkpoint that ticket's concrete `pending_action`; afterward checkpoint its observed result and clear the action only when reconciled. Never replace another ticket's unresolved action with one global field.

The command locks `<ledger>.lock`, rereads the latest ledger, checks the revision and atomically replaces it. A stale writer or existing lock blocks without a write. On interruption, inspect the recorded lock owner and actual pending operations before manually removing a stale lock. Do not delete a live writer's lock or retry a stale revision blindly. Existing Markdown/unversioned JSON ledgers require explicit, backed-up adoption as described in recovery-and-state.md. No live batch migration is automatic.

## Manifest, verify and retain evidence

Write an explicit JSON list of relative regular-file paths, including report dependencies:

```json
["acceptance.md", "images/result.png", "measurements.json"]
```

```sh
python3 "$SKILL_DIR/scripts/batch_state.py" manifest \
  --root "$ARTIFACT_ROOT" --files "$BATCH_DIR/files.json" > "$BATCH_DIR/manifest.json"
python3 "$SKILL_DIR/scripts/batch_state.py" verify \
  --root "$ARTIFACT_ROOT" --manifest "$BATCH_DIR/manifest.json"
python3 "$SKILL_DIR/scripts/batch_state.py" retain \
  --root "$ARTIFACT_ROOT" --manifest "$BATCH_DIR/manifest.json" \
  --destination "$BATCH_DIR/evidence/ticket-01/reviewed-revision"
```

Check the manifest command's exit status before consuming its output. Keep each accepted manifest immutable under a revision-specific path. A manifest binds exactly the listed bytes; it does not discover omitted files or prove the entire implementation. Prefer a Git SHA for source review, or supply a complete agreed content list when a source manifest is needed.

Paths must be normalized, relative and nonempty; no traversal, symlinks, directories or duplicates. Verification detects missing/changed files. Retention checks source bytes, copies into staging, checks copied hashes and publishes outside the source tree. An existing matching destination is reusable; differing/incomplete evidence is reported and never overwritten. Retain into a fresh revision directory after intentional content changes. Only helper-created temporary staging is removed; source and existing destination files are preserved.

The coordinator verifies the destination is outside **all** disposable worktrees, preserves the manifest and review/merge receipts, checks report links/assets and opens retained artifacts before cleanup. The helper checks only listed files; unlisted files in an existing destination are preserved. It never authorizes branch/worktree deletion.
