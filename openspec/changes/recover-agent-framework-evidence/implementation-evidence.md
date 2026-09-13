# Issue 12 acceptance evidence

The implementation qualifies incomplete worker evidence, captures it within two
numbered rounds on one committed head, and converges to a readable draft or an
explicit terminal blocker. The user confirmed `main` as delivery branch after
Issue 11 was merged. The original checkout was clean at `76f4c51`; unrelated wiki
work during this session is outside this change.

## Expected and observed behavior

| Issue requirement | Expected behavior | Observed result and evidence |
| --- | --- | --- |
| Structurally valid but incomplete worker result | Schema validation succeeds while planned phases remain missing | Controlled worker output passes schema validation. The direct-surface run reports all 14 missing REST, repeat, UI and document phases. [Public proof](evidence/direct-surfaces.json), [compact summary](evidence/acceptance-summary.json). |
| Exact semantic qualification | Report criterion/phase pairs separately from schema validity | A result containing only the idempotency request reports exactly response, repeat and read-back; its original evidence array remains unchanged. `test_valid_worker_result_reports_exact_missing_phases_separately`. |
| Bounded numbered correction | Missing phases start capture work without another implementation | Public activities and events show correction round 1; transient failure shows failed round 1 and successful round 2. The worker starts the implementation adapter once. `test_missing_evidence_is_captured_in_numbered_activity_on_same_head`, `test_second_capture_recovers_transient_surface_failure`. |
| Same head and branch | Capture does not commit or switch source | Original capture head equals local Git HEAD, draft head and evidence intent head; source remains clean, branch is unchanged, and outgoing history has one implementation commit. A mutating capture blocks at round 1, even when its assertion fails. |
| Redacted, readable evidence | PR and Operator expose decisive observations tied to the head | REST request/response/read-back, repeated request with count still 1, browser interaction/screenshot and generated/rendered document all pass. Canary output is absent from public run, history and PR body. [UI screenshot](evidence/direct-ui.png), [document render](evidence/document.png), [public proof](evidence/direct-surfaces.json). |
| Explicit terminal failure | Exhaustion reports a concrete cause and action | Two failed read-backs produce `publication-blocked`, `evidence-failed:AC1:read-back`, exact failed phase and `requiredAction`; replay leaves the execution counter at two. Two interrupted rounds likewise block without a third capture. |
| Terminal convergence and repository release | No running projection or stale human request; successor can start according to policy | Exhaustion tests read no running activities/attempts and successfully publish a successor in the same repository. Native Codex/TUI publication resolves its original preparation request. [Native proof](evidence/real-native-publication.json), [native test](evidence/native-tests.txt). |
| Separate correlated observations | Preserve original, rejection and capture results | Session result remains immutable; `EvidenceQualificationObserved`, `EvidenceCaptureStarted` and `EvidenceCaptureObserved` carry original attempt/session/result-event correlation and capture head. Public history retains failed/interrupted rounds independently of the final result. |

## Replacement and safety boundaries

- Killing the worker during an executing capture stops its tool process; the
  replacement records interruption and finishes only the remaining round.
- Killing at capture dispatch twice consumes both rounds, ends blocked and
  releases serialization to a successor.
- Killing after a persisted drift result, restoring the repository and replaying
  still cannot start another round or publish. Drift is terminal in the result
  transaction, not an eventual follow-up write.
- An uncertain already-dispatched PR retains repository ownership under Issue
  11's existing policy; reconciliation still adopts a matching draft once.

The new cases use independent API/worker processes, disposable PostgreSQL and
real local Git, observing only public command/HTTP boundaries. Tests do not
inspect PostgreSQL tables to infer success.

## Verification record

- [Focused recovery/publication run](evidence/focused-tests.txt): first 32-case
  integration pass, before the additional review-boundary tests.
- [Real native regression](evidence/native-tests.txt): real pinned Codex and native
  TUI, successful draft and resolved preparation request.
- [Native failing test](evidence/native-red.txt): confirms the superseded open
  Human Request before its fix.
- [Full final pilot regression](evidence/regression-tests.txt): **180 discovered,
  163 passed, 17 opt-in cases skipped, zero failures**, in 682.849 seconds. This
  includes all **35 final recovery/publication cases** after review corrections.
  The separately enabled native Codex/TUI case also passed.
- [Final build](evidence/build-validation.txt): zero warnings and zero errors.
- [Strict OpenSpec validation](evidence/openspec-validation.txt): valid.
- [Standards and Spec review](review.md): no remaining findings after corrections
  and the behavior-preserving refactoring pass.

## Scope and limitations

GitHub publication uses the controlled HTTP provider backed by a real bare Git
repository. REST calls, browser interaction, screenshot bytes, document render,
local Git, PostgreSQL and the additional native Codex/TUI run are real. No live
GitHub PR or merge was created by this acceptance run. Loopback evidence URLs
belonged to disposable test servers; retained JSON and PNGs preserve the observed
read-back after teardown. Deployed plans must provide a durable artifact surface.

The controlled-result recovery cases do not require a model to deliberately
omit evidence. An additional real-native run exercises the same qualification
and publication pipeline. Recovery after process death requires a replacement
worker invocation; this change does not add a recovery scheduler. The worker's
trusted evidence commands remain responsible for meaningful, repeatable
business scenarios and sanitized images; assertion text alone cannot establish
that a dishonest trusted probe exercised the declared surface.

The previously accepted Issue 11 recorded a pre-existing 10,000-event stress-test
failure. It did **not recur**: the final run reconnected 9,765 events, retained
10,015 events, restored the same dossier and found zero canary matches across
35 scanned surfaces. The full default suite passed.
