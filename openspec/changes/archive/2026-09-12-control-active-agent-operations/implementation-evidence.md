# Ticket 07 acceptance evidence

The local pilot now accepts durable, explicitly targeted `queue`, `interrupt`
and scoped `cancel` commands through authenticated HTTP and the Operator CLI.
PostgreSQL owns command order and operation fences. Independent workers adopt
external receipts, including after SIGKILL, and never need the original worker
or a separate Codex task.

## Observed behavior

All evidence below comes from public Operator HTTP/CLI surfaces, separate API
and worker processes, disposable PostgreSQL, and a separate adapter with durable
SQLite receipts and real child processes. Tests do not read or edit application
tables. Exported JSON contains synthetic, redaction-checked data only: 15 proof files covering 21 runs and 164 canonical events.

| Issue criterion | Expected behavior | Observed result and evidence |
| --- | --- | --- |
| Explicit target among parallel attempts | Reject ambiguity and protect each attempt with current authorization, version, head and lease. | Two active attempts were visible. A null target returned `explicit-target-required`; observer/non-holder writes and stale/foreign targets were rejected. Only the selected attempt changed. [Target proof](evidence/test_parallel_attempts_require_explicit_authorized_target.json), [fence/identity proof](evidence/test_invalid_commands_preserve_history_and_human_attribution.json). |
| Stable queue order | Preserve all accepted commands and deliver after the active operation, one at a time. | Two commands retained positions 1/2 through API replacement. Completion started the first command, then the second; three external operations existed (initial plus two commands) and each response retained its command ID. [Queue proof](evidence/test_queue_delivers_one_response_at_a_time_after_completion.json), [replay/read-back](evidence/test_queue_replay_retains_order_and_redacts_cli_readback.json). |
| Controlled interrupt | Fence and stop the selected operation, reconcile, then deliver one interrupt before previous queued work. | The operation fence advanced while the Control Lease stayed unchanged. The selected child exited; the parallel child stayed alive. `ActiveAgentEffectsReconciled` preceded `ActiveAgentCommandDeliveryRequested`. A competing pending interrupt was rejected. [Interrupt proof](evidence/test_interrupt_stops_reconciles_and_runs_next_before_queue.json). |
| Scoped cancel with reason, no automatic retry | Cancel the operation or whole attempt, leaving parallel attempts alone. | Operation cancel permitted already queued work; attempt cancel rejected its queue with `attempt-cancelled`. The completion timestamp remained null until stop confirmation. Repeating worker preparation did not resurrect cancelled work. [Cancel proof](evidence/test_cancel_scopes_preserve_parallel_attempt_without_automatic_retry.json). |
| No repair-round consumption | Human stop decisions do not start another business repair round. | Stop intents record `repairRoundConsumed: false`; no repair events, replacement attempt or automatic retry were created. Same [cancel proof](evidence/test_cancel_scopes_preserve_parallel_attempt_without_automatic_retry.json) and [interrupt proof](evidence/test_interrupt_stops_reconciles_and_runs_next_before_queue.json). |
| Failure between acceptance, stop, dispatch and reply | Recover the same command identities without duplication or reordering. | API SIGKILL after acceptance headers but before reading the response body retained one accepted command. Worker SIGKILL after external start, after external stop, before command dispatch and after command start was recovered by two concurrent workers with exactly one command delivery and one external operation per identity. [API proof](evidence/test_api_replacement_before_response_read_preserves_accepted_command.json), [worker proof](evidence/test_worker_replacement_adopts_process_and_command_receipts_once.json). |
| Fenced late output is history-only | Preserve evidence without replacing current operation, head or business state. | A delayed start could not bypass a prior stop tombstone. A captured old running receipt after interrupt produced history-only evidence, preserving the current operation and head. A separate regression proves late running output cannot overwrite an already completed response. [Fence proof](evidence/test_stop_before_delayed_start_and_late_output_are_history_only.json), [terminal monotonicity](evidence/test_delayed_running_receipt_cannot_regress_completed_operation.json). |
| One observable Run History | Show mode, queue position, process status, fence and response after reconnect, with redaction. | Operator `attempt` after API replacement returned the same inbox and redacted content; history linked accepted commands, stop intents, receipts and replies. Controlled canaries were absent from every exported run/history. [Operator proof](evidence/test_queue_replay_retains_order_and_redacts_cli_readback.json). |

Additional failure checks kept commands pending when reconciliation was
conflicting or a stop receipt named another process. Repeated bad receipts
produced one visible rejection and no next process. A failed adapter for one
attempt did not prevent delivery to a different attempt. See
[reconciliation](evidence/test_conflicting_reconciliation_is_visible_and_blocks_delivery.json),
[process identity](evidence/test_stop_receipt_must_match_the_bound_process.json), and
[parallel availability](evidence/test_unavailable_attempt_does_not_block_parallel_command_delivery.json).

The repository boundary also rejects fabricated later base provenance and
prevents first repository registration while a live process still exists, even
when its worker has exited. See [provenance](evidence/test_live_attempt_cannot_acquire_fabricated_repository_provenance.json)
and [registration](evidence/test_repository_registration_waits_for_live_process_even_after_worker_exit.json).

## Validation and review

- [15 active-operation tests](active-control-tests.log): passed after the final refactoring pass.
- [87 full pilot regression tests](regression-tests.txt): passed in 142.167 seconds; includes the existing control, fake session, Human Request, repository and managed-gate fixture tests.
- [Verification manifest](verification.json): source SHA-256 hashes for the validated implementation and tests.
- `openspec validate control-active-agent-operations --strict`: passed.
- `git diff --check -- microsoft-agent-framework-work-package-pilot openspec/changes/control-active-agent-operations`: passed. The repository-wide check reports pre-existing trailing whitespace in the independently edited `AGENTS.md:46`; that file was not changed by this implementation.

The refactoring pass centralized FIFO/interrupt ordering, kept HTTP transport in
the worker and transactional decisions in PostgreSQL, and simplified stop-state
classification. Review also found and corrected late-result regression,
premature cancellation timestamps, missing human attribution, unbound process
receipts and parallel-adapter starvation. Each behavioral correction has a
public regression test.

## Verification limits

This is the explicitly local fake-adapter slice. It uses real disposable
processes and databases, but has not controlled a real Codex process, opened a
Codex app session, run through managed DTS, or performed a live GitHub write.
Those integration proofs remain Tickets 10/14; this change does not claim them.

The live fixture has no repository write capability and declares
`effectScope: none`. Its successful stop reconciliation verifies the stopped
process and an empty repository-effect set. Nonempty/conflicting effects are
observable and block delivery; reconciliation of live Codex Git/GitHub writes
is not verified here. Existing Ticket 05 reconciliation is regression-tested
independently. No business repair allocator exists in this slice, so the repair
proof covers the absence of round allocation in these control paths.

Processing is an explicit bounded worker pass (`--deliver-active true`), which
can be run on replacement processes. The API durably accepts commands but does
not install a background poller. Real adapter integration must provide the same
idempotent operation/stop receipts and arrange continued delivery.


## Acceptance and archive — 2026-09-12

The user accepted this implementation and its documented pilot limits, and
authorized archive, commit and push. The standard `openspec archive -y`
path synchronized all six added requirements to the canonical
[active-agent-operation-control specification](../../../specs/active-agent-operation-control/spec.md).

The pre-archive DRY/SOLID/KISS review confirmed the earlier refactoring remains
intact and required no further source changes. All source/test hashes still
match `verification.json`; all 15 active-operation tests passed again in
32.173 seconds. The original 87-test regression result remains applicable to
the unchanged implementation. Ticket 07 remains resolved, with its acceptance
and archive references updated independently of the CLI archive operation.

Post-archive validation: `openspec validate --all --strict --no-interactive`
passed all 41 items. The commit-scoped whitespace check passed; the unrelated
`AGENTS.md:46` whitespace finding remains outside this commit.
