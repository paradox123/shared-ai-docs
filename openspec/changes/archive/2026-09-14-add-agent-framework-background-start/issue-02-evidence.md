# Ticket 02 — first real background activity

Implemented on `codex/operator-gui-issue-02` from `a77418a` (accepted Ticket 01 on
`main`) in the owning `shared-ai-docs` Git root. The matching active OpenSpec
change was selected with `openspec list --json` and the local apply skill. Existing
untracked research and `prove-three-identity-coexistence` material were preserved.
The parent change remains active for subsequent tickets; this slice is not its
archive or a human approval of any implementation head.

## Behavior and direct evidence

| Requirement | Expected and observed | Evidence |
| --- | --- | --- |
| Start a new or saved issue | A GUI URL start persists its original submission, one run and a durable disposition. A saved submission can be started through its own button. Eight concurrent start deliveries returned one new run and seven replays. Source changes preserve the original content/hash. | `tests.test_submission_execution`; `tests.test_submission_execution_browser` (saved/new starts). |
| A real agent step | The real pinned Codex runtime read `paradox123/probare-crm#4` (“Extract project facts with source provenance”) through its scoped tool and produced substantive scope, acceptance criteria, dependencies and missing decisions. This is requirements analysis, not completed implementation. | [Live public readback](evidence/issue-02/live-execution.json). Run `a05741ef-40b7-4625-8af7-da769ca5b2cf`; session `01a09f95-4fa1-7d61-913d-cdfc479244d0`. |
| Durable, correlated history | The run retained 22 canonical events, the actual session, assignment, observable messages, tool calls/results and result. Both artifact records are available; their SHA-256 values and byte counts are retained. The analysis JSON is 4,014 bytes; the full captured response is 26,134 bytes. | Live run/events/artifact manifest above; [independent real adapter receipt](evidence/issue-02/real-analysis-adapter.json). |
| Truthful GUI state and result | Waiting/running correspond to the stored queue and active worker. Completed means the first analysis is complete (`analysis-completed` on the run). Reopening shows its actual summary and findings; an oversized result is loaded from the shared artifact API. | [Live desktop](evidence/issue-02/live-execution-desktop.png), [live mobile](evidence/issue-02/live-execution-mobile.png), public/large-result browser tests. |
| Independence from the starting client | The real Chrome process exited and the API was stopped before the real worker was launched. Its short-lived launcher exited; `ps` verified worker PPID 1. The worker finished without the launcher/browser/API coordinating the model. A replacement API and new Chrome read the same run. | `browserClosedBeforeExecution`, `apiStoppedBeforeWorkerStarted`, `workerLauncherExited` and `workerParentPid` in live public proof. |
| Controlled failure is inspectable later | After successful GUI admission/runtime preflight, the real adapter was stopped before dispatch. The worker retained `failed / transport-failure`. After the worker stopped and API restarted, a new browser displayed that exact failure under the same run. No nonexistent session was invented. | [Failure public readback](evidence/issue-02/live-execution-failed.json), [failure GUI](evidence/issue-02/live-execution-failed.png). Run `d5659e66-42c9-4001-bf97-28f73a330f7a`. A separate controlled process-exit test retains an already-created session and its tool observations. |
| Restart/redelivery safety | A worker killed while awaiting its external session response was replaced; the replacement reconciled the same operation/session and committed one session-start and one result event. URL redelivery while the runtime is unavailable returns the existing run. | `test_replacement_worker_reconciles_external_session_after_worker_crash`; concurrent-start and unavailable-runtime replay tests. |
| Uncertain transport and late results | A ten-second HTTP timeout leaves the original attempt reconcilable and the GUI explicitly displays “Ergebnis wird abgeglichen”. A replacement ingests the eventual original receipt, one actual session and one result. If the first worker dies before recording timeout and the adapter then refuses connections, the attempt likewise stays open until that receipt returns. | `test_late_response_after_timeout_is_reconciled_by_replacement_without_new_attempt` (HTTP and real Chrome); `test_disconnected_adapter_after_worker_crash_preserves_uncertainty_until_receipt_returns`. |
| Preconditions and existing contracts | Current contributor/human access, repository and issue identity, ready-for-agent mandate, runtime readiness and writable/readable artifact storage are checked before new execution. Unauthorized/read-only/bot starts and changed source identity are rejected. The immutable admitted version is used. Existing central HTTP/CLI/history/artifact/dossier contracts remain shared. | Authorization/mandate/storage tests, unchanged intake regression, and full regression below. |

## TDD and verification

Tests use the stable public HTTP/GUI/adapter boundaries, actual disposable
PostgreSQL and independent worker/API processes. GitHub and the agent are
controlled external boundaries for deterministic tests; the live proof uses both
actual GitHub and actual Codex without GitHub writes.

Observed red → green slices:

- Start endpoint: HTTP 404 → atomic, idempotent 202/200 and restart-stable mapping.
- Dispatcher: run stayed queued → independent execution, session and central history.
- Real adapter: readiness HTTP 404 → real scoped-tool analysis and receipt replay.
- Browser: Starten button absent → new/saved starts and later result readback.
- Replay during runtime outage: 503 → original run returned with HTTP 200.
- Artifact precondition: invalid artifact directory incorrectly accepted a run → specific 503 before start.
- Direct live artifact check: withheld placeholder → actual available artifact bytes.
- Large result GUI: empty result for an artifact reference → full result including its terminal sentinel.
- Review timeout finding: terminal `failed/timeout` with lost session → visible reconciliation and eventual original session/tools/result after replacement.
- Review legacy fixture finding: extracted generated test failed with `IndentationError` → restored indentation compiles; the real Codex/native implementation fixture completed successfully again after the mode refactoring (45.499 seconds).

The first live stack omitted the already-required artifact directory in its test
service environment. This produced a persisted worker failure before response
capture. The harness now supplies the shared directory; the product additionally
rejects unavailable storage before admission to execution. This initial attempt
is not counted as successful execution. No source content or human credential was
added to the worker environment.

Focused verification before review: 13 HTTP/browser/intake tests passed. Separate
real adapter proof passed; both real GitHub/real Codex GUI success and controlled
outage proofs passed (2 tests, 64.589 seconds). After corrections, all 11 focused
execution/Chrome tests passed (32.605 seconds), including both new reconciliation
cases. See [review-regression.log](evidence/issue-02/review-regression.log).
The existing actual runtime/native implementation path also passed after the
final mode refactoring ([45.499 seconds](evidence/issue-02/legacy-fixture-runtime.log));
the [real background session/open descriptor check](evidence/issue-02/legacy-real-runtime.log)
passed separately (11.252 seconds). Desktop and mobile screenshots were visually
inspected. JavaScript/module syntax, .NET compilation (zero warnings/errors),
strict OpenSpec validation and whitespace checks passed.

The pre-review full regression passed: 216 tests, 192 passed and 24 optional
integration tests skipped, in 871.952 seconds
([log](evidence/issue-02/pre-review-regression.log)). Because the review corrections
touch the shared session worker, the complete discovery suite was rerun against
corrected commit `565d326`, including the two new tests. **Final result: 218 tests,
194 passed, 24 optional integration tests skipped, zero failures, 879.671 seconds.**
See [full-regression.log](evidence/issue-02/full-regression.log). The relevant
actual GitHub/Codex probes were enabled and passed separately as listed above;
the default discovery run does not automatically enable external endpoint or
publication probes. The dossier regression retained/restored 10,015 events,
verified matching checksums, and found zero raw canary matches across 35 surfaces.

Ticket 02 is implemented and locally verified; its tracker entry is resolved and
OpenSpec tasks 2.4a–c are complete. On 2026-09-14 the user accepted this slice and
authorized its archive, commit, push and merge to `main`. This acceptance concerns
the first background analysis; the parent change remains open for Tickets 03–16.

## Accepted proof and archive closeout

Immediately before acceptance, the five-case proof was repeated successfully in
92.541 seconds ([protocol](evidence/issue-02/acceptance-proof.log)). The real GitHub
input produced run `2763c4a0-ccd0-44ad-bbaf-95b75208dd7c` and actual Codex session
`01a09fcb-e025-7181-a8fb-38097fe5e697` with browser/API/launcher closed and all
result artifacts available. The new browser read the same run; the controlled
adapter outage likewise remained inspectable after restart. Concurrent starts
and both uncertain-delivery cases passed with a controlled external adapter.

- [Fresh actual run/history/artifact readback](evidence/issue-02/acceptance-live.json)
- [Fresh actual GUI success](evidence/issue-02/acceptance-success.png)
- [Fresh failure readback](evidence/issue-02/acceptance-failure.json) and [GUI](evidence/issue-02/acceptance-failure.png)

The closeout DRY/SOLID/KISS pass rechecked the reviewed workflow, dispatch/storage
and nearby result logic. The existing shared mode mapping and history boundary
remain sufficient; no runtime code changed. The accepted scenarios and evidence
are extracted into `add-agent-framework-background-start` and synced with the
standard OpenSpec archive path. Remaining GUI tasks retain their original scope.
All 11 focused public HTTP/browser checks passed again after that pass in 35.453
seconds ([closeout-regression.log](evidence/issue-02/closeout-regression.log)).
Archive schema: `spec-driven`; standard CLI archive updated the canonical spec.
All eight slice tasks are complete, without an incomplete-task exception.
Repository-wide post-archive validation passed all 52 items; moved document links
and whitespace checks passed.

## Review and limits

Two-axis code review uses baseline `a77418a`. Both independent reviewers confirmed
the corrections at `565d326`; there are **zero unresolved Standards findings and
zero unresolved Spec findings**. The [separate review reports](issue-02-review.md)
retain the original findings and their resolutions. The DRY/SOLID/KISS pass shares
the session/history workflow, explicitly selects one execution mode and its
metadata, preserves existing result validators, and keeps the analysis-specific
runtime adapter and GUI projection separate. No broader workflow rewrite was
needed.

The retained topology is independent processes on one Mac with disposable
PostgreSQL in Docker. It proves the first background step and launcher/browser
independence; it does not substitute for the separate-machine overall acceptance
in Ticket 16. The current Azure deployment remains Ticket 01 intake. Local file
intake, the full unattended implementation/evidence/review/repair chain,
workstation Handover and the detailed graph remain their existing later tickets.
The main Codex task was available to run/assert the tests; it did not implement or
coordinate the admitted live issue. The launcher's actual exit is the direct
process-lifetime evidence.
