# Protect existing NCG documentation work during delivery

## Why

Daniel authorizes the wiki automation to stash pre-existing local documentation changes, commit and push only its own Markdown changes on main, then restore the prior work. Initial unrelated dirt alone must not abort delivery.

## What Changes

- Follow-up authorization: ordinary dirty state, concurrent normal-checkout work and append-only source advances are recovery/review inputs, not terminal blockers. Prefer a verified private main checkout of the same docs origin for automation delivery; preserve the canonical repository/cursor identity and leave the user's normal checkout untouched. Explicit opt-in accepts monotonic code advancement while checkpointing only actually reviewed pins; docs push races require refreshed main history/comparisons and a new normal push.

- Add protected, restartable `protect-worktree` and `restore-worktree` slices to the existing .NET delivery helper, scoped only to the bound docs repository.
- Preserve staged, unstaged and untracked work with an exact owned stash and protected snapshots; never pop/drop an arbitrary stash or overwrite conflicts. Keep the restored stash as a safety backup.
- Permit guarded main-only delivery on the cleaned tree and accept only validated restored state afterward. Derive expected overlapping tracked changes through Git three-way trees, rather than assuming unchanged old bytes.
- Require verified restoration before official checkpoint completion. A failed push, changed source or restoration conflict retains all evidence and stash; cleanup ownership does not depend on external source freshness.
- Update canonical schema/workflow and the existing heartbeat, preserving schedule, target and authoritative source gates; finish the pending actual wiki delivery after isolated verification.

## Impact

Local docs Git stash/object operations are newly authorized; Backend/STS and NCG infrastructure remain read-only. No reset, clean, branch switch, amend, rebase or force-push. No manual memory patch.
