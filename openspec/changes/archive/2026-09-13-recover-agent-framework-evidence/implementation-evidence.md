# Issue 12 acceptance evidence

The implementation qualifies incomplete worker evidence, captures it within two
numbered rounds on one committed head, and converges to a readable draft or an
explicit terminal blocker. The user confirmed `main` as delivery branch after
Issue 11 was merged. The original checkout was clean at `76f4c51`; unrelated wiki
work during this session is outside this change.

## Correction: real GitHub acceptance

The earlier complete-acceptance claim was premature: controlled provider tests
did not prove GitHub publication. Neither Ticket 13 (review qualification) nor
Ticket 14 (three human identities and coexistence) explicitly owns this missing
proof. It belongs to Issue 12 and was completed here on 2026-09-13.

The new opt-in public-interface test passed against the real private repository
[`paradox123/wpcp-evidence-recovery-20260913`](https://github.com/paradox123/wpcp-evidence-recovery-20260913).
GitHub authenticated the actual `paradox123` human account, authorized access to
the real repository ID, accepted Git pushes, and returned authoritative draft PR
receipts. API/worker processes and disposable PostgreSQL ran locally. The worker
result intentionally omits evidence, as the issue requests; the business API is
synthetic. Neither GitHub authorization nor publication used the test provider.

| Live scenario | Expected behavior | Observed result |
| --- | --- | --- |
| Incomplete result and bounded correction | Preserve the schema-valid original; report exact gaps and capture once without another implementation | Run `5168832f-a933-4206-938c-ea15361e159b` reports exactly response, repeat and read-back missing. Round 1 succeeds; original result, qualification and capture have separate correlated events; one implementation start. |
| Immutable, redacted evidence | Operator and actual GitHub PR show identical evidence at the unchanged source head | [Draft PR #4](https://github.com/paradox123/wpcp-evidence-recovery-20260913/pull/4), head `cc99a805e8fec5a761a6bdaa3e3dde0017608a1c`. Local HEAD, remote Git ref, GitHub commit, PR head and intent match; one outgoing commit, clean source, unchanged branch. PR body equals Operator intent byte-for-byte. Repeated business request retains count 1; controlled canary is redacted. |
| Worker killed after actual PR creation | Replacement adopts the existing draft without repeating implementation or capture | Worker killed at `after-provider-effect` before receipt persistence; API replaced; new worker returns `adopted=true`. Terminal replay still finds exactly one PR for the branch and one correction round. |
| Capture exhaustion and replay | Two rounds, concrete terminal block, no active projection or external publication | Run `d518977f-c5c6-4a3b-ad75-25ec3b195802`: rounds 1 and 2 fail read-back; `publication-blocked`, exact `evidence-failed:AC1:read-back`, `exhausted=true` and concrete `requiredAction`. No running activity/attempt, no GitHub PR or remote branch. Repeating the worker leaves the execution count at two. |
| Same-repository successor | The terminal failure releases serialization | Run `1ba82961-6dd9-43e1-94e5-b64a23ca647f` publishes [Draft PR #5](https://github.com/paradox123/wpcp-evidence-recovery-20260913/pull/5), head `7ac0fa8c49fa00b8cde1c34f78bff7be228e0265`, in that same GitHub repository. It also has one implementation/correction and no running projection. |

[Retained GitHub receipts, Operator projections and events](evidence/live-github-recovery.json),
[compact result](evidence/live-github-summary.json),
[executed test log](evidence/live-github-tests.txt).
The live test passed in 108.506 seconds. Both PRs remain open drafts for inspection;
the test repository's `main` SHA is unchanged after the initial synthetic seed.

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

The initial regression matrix uses a controlled HTTP GitHub provider backed by a
real bare Git repository. The additional live acceptance above closes the actual
GitHub authorization/publication/read-back gap. REST calls, browser interaction,
screenshot bytes, document render, local Git, PostgreSQL and the additional native
Codex/TUI run are real. Screenshot/document combinations and native Codex remain
covered by those earlier controlled-provider runs; Issue 12 explicitly requires
a controlled incomplete worker result, which the live GitHub test supplies.
Loopback business/evidence URLs belonged to disposable test servers; retained
JSON and PNGs preserve their observations after teardown. GitHub draft text remains
readable independently. Deployed image plans must provide a durable artifact
surface. No merge was requested or performed.

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
