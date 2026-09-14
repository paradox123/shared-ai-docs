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

The first live stack omitted the already-required artifact directory in its test
service environment. This produced a persisted worker failure before response
capture. The harness now supplies the shared directory; the product additionally
rejects unavailable storage before admission to execution. This initial attempt
is not counted as successful execution. No source content or human credential was
added to the worker environment.

Focused verification: 13 HTTP/browser/intake tests passed. Separate real adapter
proof passed; both real GitHub/real Codex GUI success and controlled outage proofs
passed (2 tests, 64.589 seconds). Desktop and mobile screenshots were visually
inspected. JavaScript/module syntax, .NET compilation, strict OpenSpec validation
and whitespace checks are part of final verification.

Full regression is running in the pinned Python environment. Its final outcome
will be recorded here and in [full-regression.log](evidence/issue-02/full-regression.log).

## Review and limits

Two-axis code review uses baseline `a77418a`; final findings and corrections are
recorded here after review. The refactoring pass shares the session workflow
between fake, real implementation and analysis modes, retains the existing result
validators and history boundary, and extracts only the analysis-specific runtime
adapter and GUI projection.

The retained topology is independent processes on one Mac with disposable
PostgreSQL in Docker. It proves the first background step and launcher/browser
independence; it does not substitute for the separate-machine overall acceptance
in Ticket 16. The current Azure deployment remains Ticket 01 intake. Local file
intake, the full unattended implementation/evidence/review/repair chain,
workstation Handover and the detailed graph remain their existing later tickets.
The main Codex task was available to run/assert the tests; it did not implement or
coordinate the admitted live issue. The launcher's actual exit is the direct
process-lifetime evidence.
