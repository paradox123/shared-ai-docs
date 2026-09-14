# Ticket 03 — observe a GUI-started run

Implementation branch: `codex/operator-gui-issue-03`, isolated worktree
`shared-ai-docs-operator-issue-03`, owning Git repository `shared-ai-docs`.
Baseline `dded7d4` contains accepted Tickets 01–02. OpenSpec routing selected the
existing `add-agent-framework-operator-gui` change. Original untracked research
and three-identity coexistence material are preserved. This bounded slice does
not complete or archive the parent change.

## Acceptance overview

| Requirement | Expected behavior and observed result | Evidence |
| --- | --- | --- |
| Start and discover a real run | GUI input and Starten create the submission/run through the existing public intake, without a prewritten run or fixture import. The started-run list opens that same persisted association. | `tests.test_workflow_browser`; actual GitHub `paradox123/probare-crm#4` in the live proof below. |
| Observe activities, attempts and sessions | The graph displays actual admission and requirements-analysis activities and their attempts, observed states and real session identity. Selecting the analysis attempt displays its associated retained events; the full-run action restores shared history. | Live run `125fbcd9-4f74-4e60-9cb5-813ede7d9276`, attempt `02604786-631d-4219-8046-2bbc9858b31f`, Codex session `01a0a002-0e43-72d3-8242-8f1f1c38f78a`. |
| Full observable content | Both browsers compare every selected event payload with public History, not just successful HTTP status. They compare parsed artifact content with authenticated public bytes. The real analysis retained 22 canonical events, 18 belonging to the analysis attempt, plus two available artifacts (4,001 and 26,154 bytes). | [Public live proof](evidence/issue-03/live-workflow.json), `tests.test_workflow_live`. Assignment, observable conversation, tool inputs/results, actual analysis findings and provenance are retained. Unrecorded fields are identified rather than inferred. |
| Confirmed pagination and replay | A controlled issue emits over 200 observations and large results. A fresh browser initially loads 100 canonical positions, explicitly reports partial history, and loads further pages using the delivered cursor. Both clients display the same ordered event IDs without duplicates. An open browser reconnects after an API process restart; filter round-trips retain canonical order. | `test_paged_history_and_artifact_bytes_are_complete_in_both_clients`; `test_live_history_reconnects_after_api_restart_and_clears_after_revocation`. |
| Access boundaries | A distinct read-only provider identity examines the same run. Revocation terminates observation, clears displayed submission/run/session/artifact content and the in-memory event cache, and removes filter callbacks. A triggered filter event cannot redisplay revoked content. Credentials and history are absent from browser storage. | Controlled two-identity browser tests; existing public authorization/artifact regressions. |
| Unavailable and redacted evidence | Configured sensitive input is redacted before browser/API readback. Deleting only disposable artifact bytes causes explicit unavailable/410 readback in both clients; no external source link or filesystem fallback appears. Oversized results remain fully retrievable. | `test_missing_artifact_remains_explicit_without_source_link_fallback`; paged artifact test and public content comparisons. |
| Restart and second-client acceptance | Two isolated authenticated browser contexts read the real controlled GitHub issue's analysis. The worker is independently launched. After stopping the worker and replacing the API, fresh browsers read identical run/attempt/session identities, events and artifact contents. | Live proof `browsers` and `afterApiRestart`; final real probe passed in 135.909 seconds at corrective commit `eacce49`. |
| Rendered behavior | Actual production portal renders the graph and session inspector on desktop and mobile with no horizontal page overflow, no browser JavaScript errors and no browser credential/history persistence. Both screenshots were visually inspected. | [Desktop](evidence/issue-03/live-workflow-desktop.png), [mobile](evidence/issue-03/live-workflow-mobile.png). |

## TDD and direct verification

Public seams: production Chrome against public HTTP, actual disposable PostgreSQL,
and controlled external GitHub/agent HTTP boundaries. No test creates a run by
writing database rows. Artifact deletion is an explicit fault injection only.

Observed red → green cycles:

- Workflow heading absent after successful GUI start → correlated graph and history.
- Artifact content controls absent → authenticated complete artifact readback.
- Filter round-trip reordered retained tool events → stable canonical DOM order.
- Filter callback redisplayed history after revocation → aborted-view cache and
  callbacks are cleared as well as visible nodes.
- A normal message containing an SSE control phrase disconnected the browser →
  parse transport event fields without interpreting message contents.
- History caught up while the graph remained running after a failed final read →
  retain and retry pending projection refresh without requiring another event.
- Idle live keepalives closed expanded session metadata → projection refresh only
  on new events, coalesced without concurrent projection requests.

Five focused browser tests passed after both review corrections (39.877 seconds).
.NET build/typechecking passed with zero warnings or errors; JavaScript syntax
and strict OpenSpec validation passed. Both independent review axes confirmed their findings resolved at `eacce49`;
there are zero remaining Standards findings and zero remaining Spec findings.
Full discovery passed: **223 tests, 198 passed, 25 optional integration tests
skipped, no failures, 939.937 seconds**. See [full-regression.log](evidence/issue-03/full-regression.log).
The added review race test was introduced after full discovery had started and
passed separately within the five-case focused run; the full suite's GUI cases
ran after the corrective implementation was built. The explicitly enabled real
GitHub/Codex test also passed separately ([live-regression.log](evidence/issue-03/live-regression.log)).
The dossier regression restored 10,015 events with equal history/projection
checksums and zero raw canary matches across 35 inspected surfaces.

The first real-browser attempt exceeded the harness's original 90-second budget;
a later attempt completed analysis but timed out connecting the second browser.
The harness now gives real model work its configured latency budget and reports
connection errors. Idle keepalives no longer trigger redundant projection reads.
The final real probe passed through both browsers and API replacement (135.909 seconds). These
failed preliminary attempts are not counted as acceptance evidence; provider
rate limiting was not established as their cause.

The final live probe was repeated after the corrections. Its artifact bytes were
also retrieved independently through authenticated HTTP and verified against each
manifest SHA-256. Retained public artifact responses:

- [4,001-byte artifact](evidence/issue-03/live-artifact-2b21c2fa2472cdc85e55532474f89c36317ce13559a2ee6bff7204cc68801a50.json)
- [26,154-byte artifact](evidence/issue-03/live-artifact-86fb3d7327224d5ab59cc98f1b307dd8361742865f55119457cd98e48f44a8ae.json)

## Scope and limits

The graph is deliberately limited to observed issue-run activities. It reuses the
current production portal; the nonbinding Backstage/React Flow prototype informs
composition, while its runtime migration and nested PRD graph are not imported.
Workstation observation ingestion and handoff remain later tickets. Private model
reasoning is outside the observable-history contract.

The real probe uses one actual human identity in separate browser contexts;
controlled tests use contributor and observer identities, including real adapter
permission evaluation against the controlled provider. The topology is independent
processes/browser contexts on one Mac, with PostgreSQL in Docker. Browsers use
public HTTP only and need no originating client's files or database access. This
is not the separate-physical-machine/Ticket 16 proof, nor the three-real-identity
Ticket 14 gate. No Azure deployment, GitHub mutation, merge or human head approval
is claimed. The existing Azure deployment is unchanged by this implementation.

## Completion

Ticket 03 is implemented and locally verified (`resolved` in the local tracker).
OpenSpec tasks 2.5a–c are complete; broader lifecycle task 2.5 retains its central
and workstation scope. The parent remains active with 23 of 35 tasks complete.
No user acceptance/archive of this slice is inferred. A final DRY/SOLID/KISS pass
kept the existing backend contracts and portal boundaries, consolidated refresh
scheduling, and retained explicit content/transport separation. Both review axes
confirmed the final correction. Strict OpenSpec, JavaScript syntax, .NET build,
whitespace, artifact checksum, redaction and evidence-link checks passed.
