# Integration and owned cleanup

The CLI enforces declared dependencies/conflicts, ticket/subagent reservations, one integration holder and recorded prerequisites. The coordinator verifies semantic overlap, evidence and external facts. Use [local-helpers.md](local-helpers.md) for state operations; successful bookkeeping never authorizes a mutation.

## Isolation and scheduling

Tickets from registration through remote confirmation occupy capacity, including uncertain creation, review, repair and candidates waiting to integrate. Verified delivery/quiescence releases capacity independently of cleanup. Parking requires quiescence and no uncertain mutation; parked undelivered work keeps its conflict reservation. Ending a coordinator turn releases nothing. Refill eligible slots after actionable results rather than waiting for a whole wave.

Use create_thread worktree mode from the explicit target, with an owned branch; confirm actual checkout/branch and fresh remote base. Never run concurrent writers in a saved/shared checkout or reset existing work during adoption. Separate ports, databases, generated outputs and other mutable resources; serialize resources that cannot be isolated. Read-only shared dependencies need no global lock.

If overlap appears, stop new dispatch into that area, have the lower-priority worker secure its work and pause, then coordinate one owner until delivery. Preserve both candidates; update from the delivered target before safe resumption. Declared graphs cannot discover new overlap: record changed scope in evidence and do not dispatch newly conflicting work merely because the initial graph permits it.

## Prepare, grant, confirm

1. Reserve integration through `prepare` for an accepted awaiting-integration ticket. The worker fetches/integrates the latest target, resolves conflicts, performs required pre-merge docs/OpenSpec checks and relevant combined tests, and prepares its PR. It returns actual candidate and tested target. Preparation is not merge permission.
2. Inspect the candidate against accepted contents. Map documentation/archive bookkeeping explicitly; substantive changes need renewed evidence/acceptance. Verify PR base/head, required checks and latest remote target. If the target moved, request revalidation while retaining the reservation.
3. Prepare a grant for exactly the inspected content and tested/current target. The worker rechecks immediately before merging and stops if either changed. No unattended grant for a future head, force-pushing history, bypassing checks or changing the target to main for convenient defaults.
4. A delivery report moves to confirming, retaining reservations. Verify actual remote merge, inclusion of accepted contents (including squash/rebase mapping) and ticket closure. A non-default target may require explicit closure. External writers can race despite the reservation: inspect resulting combined behavior and required checks; failures block further integration until repaired and verified.
5. Record delivery plus worker/subagent quiescence to enter cleanup. This releases integration/capacity and unlocks delivered prerequisites. Cleanup failures remain unfinished work without undoing delivery.

A ticket-specific holder may park only after cancellation of outstanding grants is acknowledged, no merge is pending/uncertain and quiescence is verified. Record those facts through capacity; resumption requires a free slot, new integration reservation and fresh head/target validation. Prior grants never revive. A batch-wide permission blocker still applies to all affected tickets. Preserve the exact denied operation/reason; use [recovery-and-state.md](recovery-and-state.md) if actual user approval is required.

## Guarded cleanup

The coordinator acts from a surviving directory, never asking a worker to delete its own active checkout. Use prepare/record for each checklist step and reconcile uncertain outcomes before retrying.

- **evidence-preserved:** copy inspectable acceptance reports, images/measurements, dependencies, manifests and review/merge mapping outside every disposable worktree. Use manifest/verify/retain utilities, revise links when necessary, check hashes and open retained artifacts. A transient preview URL or a link into a removed worktree is insufficient.
- **worktree-removed:** immediately recheck remote delivery, exact ownership/path, accepted-to-merged content mapping, clean worktree and absence of writers/unintegrated work. Remove only the owned worktree using normal Git worktree removal; never force away unexpected files or commits.
- **local-branch-removed / remote-branch-removed:** prove all intended work integrated and recorded heads unchanged. Never delete target, protected/default or foreign branches. Prefer normal merged deletion. After squash/rebase, ancestry alone is insufficient: prove PR-head-to-merge mapping and no extra work, then use expected-old-SHA guarded deletion; remote deletion needs a lease against the verified head. If proof/guarding is unavailable, retain the branch and report cleanup-blocked. This permits no force-push of history.
- **worker-archived:** after verifying actual resource absence, archive with set_thread_archived and confirm its result or a scoped archived-task lookup. Omission from recent tasks is not archival proof. Preserve task history and retained evidence.

An already removed resource counts only after identity and delivery/evidence gates are verified. Never recreate it to replay cleanup. Record exact retained paths/refs and causes, continue unrelated work, and mark done only after all cleanup outcomes are verified (unless the user explicitly narrows scope).
