# Ticket 01 implementation evidence

## Scope and Git ownership

- Owning Git root at intake: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`; initial branch `main`, HEAD `f6f5d15`.
- Delivery branch: `codex/operator-gui-issue-01`, created from that main baseline in the isolated sibling worktree `shared-ai-docs-operator-gui-issue-01`, following the repository's ticket-branch convention and Codex branch prefix. No target branch was named by the ticket.
- Existing modified glossary/ADR and untracked GUI specification/tracker were copied as accepted context. The original worktree and unrelated changes were preserved.
- OpenSpec routing: `openspec list --json` matched `add-agent-framework-operator-gui`; local apply skill, spec-driven schema, originally 14/25 tasks. Ticket 01 is only the GitHub intake portion of 2.2; background execution and file ingestion remain later tickets.
- Review baseline: `f6f5d15`; review the implementation and its accepted context against this fixed point.

## Verification in progress

The stable behavior seam is the public submission HTTP API, exercised with separate API processes and disposable PostgreSQL. GitHub is the controlled external boundary for deterministic cases. Rendered GUI and real GitHub readback supplement those tests; neither a health response nor a fabricated run establishes acceptance.

## Direct observations

| Ticket expectation | Observed behavior | Evidence |
| --- | --- | --- |
| Enter a real GitHub URL without a prepared run | An initially empty GUI accepted `probare-crm#4` through its form. Actual title: “Extract project facts with source provenance”; the provider body and repository appeared in the overview/detail. `state=admitted`, `runId=null`. | [Live public snapshot](evidence/issue-01/live-github-browser.json), [desktop](evidence/issue-01/live-github-desktop.png), [mobile](evidence/issue-01/live-github-mobile.png). |
| Server reads provider content, repository identity and implementation authorization | Admission uses GitHub's `/user`, repository and issue APIs. The deterministic provider tests rejected read-only humans, a bot, revoked access, repository ID mismatch, missing `ready-for-agent`, closed issues, pull requests, invalid URLs and unavailable providers. No issue plan or catalogue is supplied by the browser; deployment config holds only bindings/redaction. | `tests.test_submissions`; real GitHub proof above. |
| Durable content and provenance, immutable version, no duplicates | New Chrome process after API restart read the identical live snapshot. Controlled source edit preserved original title/body/revision. Twelve concurrent deliveries produced one 201 and eleven 200 results with one identity. | [Controlled browser snapshot](evidence/issue-01/controlled-browser.json), `tests.test_submissions`. |
| Redaction before storage and display; current read authorization | Controlled body token was replaced by the existing policy marker. Public browser read and supplementary PostgreSQL dump contained no canary or user credential. Provider `<script>` text remained inert. Revoked/unauthorized readers received no content. | [Controlled desktop](evidence/issue-01/controlled-desktop.png), [controlled mobile](evidence/issue-01/controlled-mobile.png); browser and HTTP tests. |
| Browser/service restart, no agent processing | Fresh browser authenticates again, retrieves the persisted submission and displays “Aufgenommen” and that agent processing has not started. Test harness starts API and database only. Existing synthetic admission/CLI restart contract still passes. | Live/controlled browser evidence; `test_authorized_issue_is_one_redacted_observable_run_across_restarts`. |
| Server and separate human workstation | **Not yet verified.** HTTPS-capable server listener and same-origin authenticated browser contract are implemented. All retained browser tests ran as separate processes on this Mac, with PostgreSQL in a disposable container. No separate reachable test server was provided; an asynchronous question for its SSH target or URL is pending. | Explicit `topology` limitation in live proof; do not count this as separate-machine acceptance. |

The feature uses the prototype's green portal/overview/detail direction in a minimal
server-delivered HTML/CSS/module client. It does not import the prototype's
simulation, Backstage integration or React Flow graph. Those libraries and graph
views are not Ticket 01 acceptance criteria; the wider ADR target and later
workflow views remain outstanding.

The application databases used for these proofs were empty and disposable. The
live proof made no GitHub writes, started no worker, and did not touch the
existing Issue 14 database or LangGraph services. Real three-human identity and
coexistence acceptance remains separate. The provider credential stayed in the
client process and request headers; screenshots and retained JSON contain no
credential.

## TDD and checks

- First red: `test_admitted_provider_snapshot_survives_restart_without_a_run` executed through HTTP and failed with 404 instead of 201. Implemented live source intake and the redacted database snapshot, then green.
- Second red: GUI route check executed and failed with 404 instead of 200. Implemented server-delivered GUI, then green. A WebRoot startup configuration error during the green step was diagnosed and corrected; it was not counted as a behavioral red.
- Added explicit concurrent/source-change/authorization cases and rendered UI/reconnect cases through public surfaces.
- Targeted result: 6 tests passed, including all submission/browser cases and the existing synthetic admission restart test. Live GitHub GUI proof: 1 passed.
- .NET solution builds with zero warnings and errors. JavaScript syntax check and strict OpenSpec validation pass.
- One mistyped existing test class name was corrected to `ObservableRunBlackBoxTests`; the corrected behavior check passed. It was a test-selection error, not a product failure or behavioral red.

## Review

Review baseline: `f6f5d15`; two independent read-only agents reviewed the implementation staged in this ticket worktree. Accepted copied design material and later GUI tickets were excluded from implementation-scope findings.

### Standards

No confirmed documented-standard violations or correctness/security defects. One P3 maintenance judgement identified duplicated GitHub request headers and HTTP credential/error handling. Extracted `GitHubRequests` and `OperatorHttp`, and removed obsolete synthetic configuration DTO fields. A focused follow-up confirmed the finding resolved with no new findings. Rebuilt the solution successfully after this refactoring.

### Spec

No additional implementation mismatch or scope creep. One partial requirement: separate-machine GUI/service acceptance remains pending. Ticket 01 explicitly stays `needs-info`; it is not accepted or archived. Implementation subtask 2.2a is complete, and separate acceptance subtask 2.2b remains open. File input, run start and the wider GUI change are not marked complete.

Final review count: Standards 0 unresolved; Spec 1 evidence gap (separate-machine proof).

## Full regression

The initial system-Python run lacked `jsonschema`, causing unrelated existing contract/evidence tests to fail. It was interrupted and its owned API/database cleaned up. Both representative failures passed with the repository-pinned `codex-requirements.txt` environment. The corrected full run under that pinned environment completed successfully: **204 tests, 183 passed, 21 skipped**, in 893.329 seconds. The skipped tests require optional real runtime/provider gates; the live GitHub intake was separately executed explicitly. Retained output: [full-regression.log](evidence/issue-01/full-regression.log).

The large history scenario committed 10,015 events, reconnected for 9,765 events, restored equal history/projection, and found zero raw controlled canaries across 35 scanned surfaces. All new submission/browser tests and existing API/CLI, authorization, lease, recovery, publication and dossier regressions passed.

Final source checks: zero-warning/zero-error .NET solution build, JavaScript syntax validation, `git diff --check`, and `openspec validate add-agent-framework-operator-gui --strict`. The initial environment run is retained separately as [initial-environment-run.log](evidence/issue-01/initial-environment-run.log); it is not counted as a product regression or acceptance evidence.

The final refactored code also passed the explicit real GitHub GUI/restart proof again (1 test): [live-github-test.log](evidence/issue-01/live-github-test.log). The live screenshots and snapshot were refreshed from this final run.


## User-requested terminology correction

The user requested a product-facing name such as Featureidee, Anforderungen or Spec instead of Einreichung. The GUI now consistently uses **Anforderungen** in navigation, page/title/detail labels, accessible labels and error/empty-state messages. This is a copy-only follow-up in the same change. Two focused existing checks passed (rendered browser/restart and public GUI route), followed by the real GitHub GUI proof (1 passed in 17.936 seconds). Desktop/mobile screenshots and readback snapshots were refreshed. No full regression rerun was needed for these text changes; strict OpenSpec validation and diff checks passed.
