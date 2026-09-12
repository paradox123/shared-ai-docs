# Ticket 08 acceptance evidence

Implementation: `transfer-run-control-atomically`, branch `codex/transfer-run-control`
in isolated worktree `shared-ai-docs-ticket-08`, based on
`df43a56bf2b46474414d98dd22c106266d278730`. The source checkout's unrelated dirty
AGENTS/CONTEXT/LLM-wiki documentation was preserved. No merge, deployment, live
provider write or real Codex App session was performed.

## Public behavior observed

The tests use real disposable PostgreSQL, independent API/CLI/worker processes,
a controlled GitHub HTTP boundary, independent durable fake adapter receipts and
real local Git repositories. Product state is read through HTTP/CLI only.

| Ticket requirement | Expected and observed result | Direct evidence |
| --- | --- | --- |
| Request without writing rights | A contributor in observer mode requests control; holder/epoch remain unchanged, and the requester cannot release or decide the request. API replacement retains the same request. | `test_request_survives_restart_and_only_holder_can_reject` |
| Holder decides current request | Only the holder approves/rejects the current UUID. Approval rechecks the recipient and installs that immutable human once. Revoked contribution prevents approval. Closed IDs and stale decisions do not transfer again. | `test_approval_moves_lease_once_and_revalidates_recipient`, `test_closed_transfer_request_identity_cannot_be_reused`, `test_release_expires_pending_request_and_new_holder_can_request_again` |
| Forced Takeover without admin | Explicit CLI/HTTP action succeeds for another ordinary contributor, requires a reason, and exposes the old/new holder and forced mode. Read-only, inaccessible and bot identities are denied. | `test_transfer_permissions_fences_and_redacted_reason` |
| Old fences and pending commands fail | Old and rotated credentials for the old human cannot write with even fresh run state. A pending write becomes `fenced`; a pending live queue entry becomes `rejected`, and neither is dispatched after takeover. | `test_takeover_fences_pending_opened_session_write_across_restart`, `test_takeover_invalidates_queue_but_preserves_running_operation` |
| Twenty competing requests | Twenty calls race across two separate API processes sharing PostgreSQL. Each of two expected epochs produces one 200 and nineteen 409 responses, advances the epoch once and records one forced change. | `test_twenty_takeovers_across_two_api_hosts_have_one_winner_per_epoch`; exported `facts.epochRound0/1` |
| Workflow/session/head/effects stay intact | Immediate before/after read-back retains phase, activities, attempts, session, head and repository execution. A managed delivery retains its real Git/provider receipts and existing session after worker replacement. | `test_takeover_preserves_managed_session_head_and_accepted_effects` in repository suite; `test_voluntary_transfer_fences_old_window_and_new_holder_writes_same_session` |
| Former holder observes complete history | Former holder still reads control and events after replacement; history carries prior/current immutable identity, run, timestamp, reason and voluntary/forced mode. Redaction metadata and markers remain truthful. | request/restart, race, permissions and voluntary-transfer tests |
| Open writing session is fenced | Old window writes are denied; the new holder writes the same opened session. SIGKILL removes the accepting API while its adapter request is in flight; takeover installs a durable tombstone, and releasing the delayed old request creates zero interactions, including after replacement. | `test_api_sigkill_then_takeover_fences_inflight_adapter_write`; exported exit code and interaction count |
| Accepted external effect survives | A write succeeds externally but loses its reply. Takeover first adopts that exact receipt and asks for fresh fences; the next decision changes ownership without another interaction. | `test_takeover_reconciles_accepted_write_before_preserving_it` |
| Invalid receipts fail closed | Malformed external interaction events cannot append a partial canonical transcript during reconciliation, and ownership stays unchanged. | `test_invalid_external_reconciliation_does_not_append_partial_history` |

Tests: [control transfer suite](../../../microsoft-agent-framework-work-package-pilot/tests/test_control_transfer.py),
[repository tests](../../../microsoft-agent-framework-work-package-pilot/tests/test_repository_reconciliation.py).
Public observations and test output:
[Ticket 08 proof directory](../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-08-proof-2026-09-12/).

## TDD and validation

Each implementation slice first executed a discovered, compiled public behavior
test that failed for missing behavior: unsupported request, unsupported approval,
unsupported forced takeover, pending session write still deliverable, live queue
still queued, reuse of closed request UUID, stale pending request after release,
missing projection redaction metadata, partial malformed-receipt history and
unsettled repository recovery allowing takeover, partial local fencing on a rejected takeover, and blocked restart replay of an already accepted fenced write. Those failures were corrected
through the production API/store/adapter path. Test-harness setup failures were
fixed separately and were not treated as behavioral red.

The 27-test intermediate run (six transfer tests plus the existing 21 session
regressions) passed. The first full isolated suite passed all 102 tests. Review
then reproduced two additional crash/rejection paths; both new public tests
failed for that behavior and passed after their corrections. Final full-suite
results: **104/104 tests passed** (139.714 seconds). The final incremental
`dotnet build --no-restore` reported zero warnings and zero errors. The contention
fixture was then tightened to use twenty distinct eligible non-holders in each
round, and its focused rerun passed. Locked restore, strict OpenSpec validation
and the complete diff whitespace check passed. Machine-readable
[summary](../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-08-proof-2026-09-12/summary.json),
[full test output](../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-08-proof-2026-09-12/full-test-output.txt)
and [build output](../../../.scratch/distributed-codex-work-package-control-plane/evidence/ticket-08-proof-2026-09-12/build-output.txt)
are retained. The full suite required one rerun after the review-driven fixes;
no unrelated suite was substituted for the public behavior proof.

## Standards

Initial review: one P3 heuristic, duplicated attempt/version/head/epoch checks.
Resolution: `ControlFenceFailure` centralizes the rule while preserving the
existing authorization and replay ordering. Independent re-review:

> No remaining actionable Standards findings.

## Spec

Initial review: one P1 (409 takeover committed a partial local fence before
noticing pending live delivery) and one P2 (an applied-write tombstone blocked
receipt replay after API replacement). Resolution: preflight pending live
operations, defer local fencing changes until required adapter fences succeed,
reconcile an existing effect independently with savepoint rollback on malformed
completion, and replay an existing immutable receipt before rejecting a missing
tombstoned write. Public regression tests:
`test_pending_live_delivery_rejects_transfer_without_partial_session_fencing` and
`test_restart_adopts_applied_write_after_adapter_fence_success_gap`.
Independent re-review:

> No remaining actionable Spec findings.

Remaining findings: Standards **0**; Spec **0**. No unresolved issue on either axis.
The review used `git diff df43a56` over the staged work in this worktree; it was
performed before the final commit. The refactoring pass kept provider policy,
storage, adapter dispatch and Operator surfaces at their established boundaries;
no new framework, generic command abstraction or extra membership authority was
introduced.

## Limits and recovery boundaries

This is the isolated pilot's controlled adapter proof. It does not verify a live
Codex App window, real GitHub human accounts, automatic managed DTS delivery or
mixed-version service operation; Tickets 10/14 retain those live integration
boundaries. No UI screenshot would prove the adapter's fencing contract.

An already accepted continuation/repository recovery, or a promoted live command
without a settled process receipt, returns an explicit pending conflict before
changing ownership. Complete/recover that same accepted decision, read current
fences and retry. A write receipt discovered during fencing is adopted once and
returns `control-effects-reconciled`; unavailable or invalid adapter evidence
returns `control-fencing-unavailable`. These conflicts preserve ownership instead
of orphaning accepted work. Adapter tombstones can survive a failed database
transaction; retry converges on the tombstone. No transfer-created session,
operation cancel, retry or phase transition is hidden behind a successful
ownership change.
