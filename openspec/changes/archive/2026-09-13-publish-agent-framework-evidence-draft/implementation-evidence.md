# Ticket 11 acceptance evidence

Implementation: `codex/agent-framework-issue-11`, based on accepted Ticket 10 at
`6c2a4f2`. The worktree isolates unrelated ongoing Wiki edits on `main`.
Independent Standards and Spec reviews have no unresolved findings; see [review.md](review.md).

## Observed behavior

The same admitted run now carries the trusted readiness plan, real agent session,
committed source head, executed evidence phases, durable publication intent and
provider PR receipt. The real Codex/TUI proof fixes the supplied local issue,
then publishes through the controlled GitHub HTTP boundary and real local bare
Git. Repeating the worker command retains the same PR and does not merge it.

| Ticket requirement | Expected behavior | Observed result / public evidence |
| --- | --- | --- |
| Criterion-level plan before agent start | Kind, phases, executable surface and expected read-back are mandatory | Incomplete and unsupported log/dashboard kinds stop without a session. The readiness report retains all phase/probe commands before `AgentSessionStartRequested`. |
| Complete readiness | Verify base, contracts, tools, dependencies, access, sandbox and required surfaces | Worker tests remove dependency, contract/sandbox readiness and surface access; each exposes a named blocker. Wrong adapter checkout and stale local/remote/provider base prevent starts. The real adapter executes its pinned protocol/tools/sandbox probes before the model turn. |
| Missing prerequisite stops expensive work | Concrete blocker or Human Request; no hidden work | Negative HTTP read-backs contain `preflight-blocked` and no agent session or provider create. A registered plan cannot be bypassed by standalone dispatch; an existing standalone session cannot gain fabricated later readiness. |
| Exactly one draft on expected branch/head | One source branch and one draft, no merge | Provider read-back returns the explicit base/branch/commit and `draft:true`. The native proof repeats publication and observes one PR. No merge or mark-ready endpoint is implemented. |
| Evidence matrix with direct phases | Required phases execute and their business assertions pass | The surface proof calls a real local REST app, repeats the same idempotent write with count remaining one, clicks its button in Chrome, retains a decisive PNG, generates an HTML document, renders it and reads it back over HTTP. All phases and exact expectations appear in the provider body. |
| Redacted commit/head-bound evidence | Capture against the final commit and keep authoritative read-back | Evidence runs after source commit with `WPCP_EVIDENCE_HEAD`. Dirty/head-changing evidence prevents push. Configured secret output is absent from both Operator projection and provider body; sensitive source, including deleted historical content, rejects before push. Large completed results resolve through verified dossier artifacts. |
| Repeated publication adopts | Independent exact receipt survives lost reply or worker/API death | Lost create reply plus API replacement adopts the same PR. SIGKILL after successful provider response and before local receipt persistence also adopts it. An absent dispatched receipt produces explicit uncertainty without a second create; incompatible non-draft receipt blocks. |
| Operational surrogates do not qualify | No build/health/log-only verdict | Each planned phase needs a nonempty business output assertion. Unsupported log/dashboard kinds and missing REST/UI/repeat/document phases are rejected. The PR carries actual commands and output rather than a framework success badge. |

## Reproduction and proof files

Run the commands in [PUBLICATION.md](../../../../microsoft-agent-framework-work-package-pilot/PUBLICATION.md#verification).

- [Full default regression output](evidence/regression-tests.txt).
- [Publication suite after review corrections: 25 passing tests](evidence/publication-tests.txt).
- [Final native and adjacent-runtime regression](evidence/final-runtime-regression.txt).
- [Earlier real native test output](evidence/native-test.txt).
- [Real native run, accepted history and provider PR](evidence/real-native-publication.json).
- [Direct REST/UI/repeat/document proof](evidence/direct-surfaces.json).
- [Decisive UI image](evidence/direct-ui.png) and [rendered document](evidence/document.png).

These are snapshots obtained through public Operator/provider surfaces. Temporary
checkout paths and localhost artifact URLs identify the historical run; fixtures
are disposed after verification. PNGs are retained alongside the snapshots.

## Validation result

- The full default suite ran 162 tests: 144 passed, 17 opt-in tests skipped and
  one existing large-event stress test failed. This run preceded the review
  corrections. The corrected publication suite then passed all 25 tests;
  all 35 final native and adjacent-runtime tests also passed (one real Codex/TUI
  publication plus 34 repository/active-agent regressions).
- The failed test is
  `RunDossierTests.test_more_than_ten_thousand_events_reconnect_after_api_and_worker_kills_and_restore`.
  In the full suite it exceeded the terminal-event window. An isolated rerun
  missed the 90-second `after-source-sequence-5000` boundary. Running the same test
  on unchanged baseline `6c2a4f2` reproduced that exact boundary failure:
  [baseline log](evidence/baseline-dossier.txt),
  [Issue 11 isolated rerun](evidence/dossier-recheck.txt). This limitation was not
  hidden by changing the test or widening its deadlines; the stress-test path
  is not accepted as passing in this environment.
- New regressions first demonstrated failures for historical secrets, mismatched
  remote, absent screenshot fields, unbounded stderr, disabled Python assertions,
  malformed PNG pixels and externalized completion results; all now pass.
- Locked restore and build passed with zero warnings/errors. Strict OpenSpec
  validation and `git diff --check` passed; see [build and validation](evidence/build-validation.txt).
- Both retained PNGs were visually inspected: the application shows “Records: 1”
  after interaction and the rendered document shows the same result. Public
  snapshots match the provider draft and head; configured controlled canaries
  are absent from all retained evidence files.

## Boundaries of the proof

- GitHub publication and human identity services are controlled HTTP providers;
  no live GitHub PR or production repository was created or modified. The same
  publication adapter uses the GitHub REST resource shapes and API origin in
  production, but live account permissions/rate limits were not verified here.
- The Codex runtime and native TUI are real and pinned. Its existing preparation
  result remains immutable; publication accepts only the later completed turn
  recorded under the same session through the authorized native boundary.
  Quarantined late events cannot substitute for this completion.
- Evidence assertions and prerequisite scripts are trusted operator inputs.
  They must observe the claimed business surface; a fabricated test script is
  not made true by executing it. The body exposes commands, expectations and
  observations for independent review.
- Text redaction covers configured canaries and recognizable credentials, not
  general data-loss prevention. Screenshots require an already sanitized,
  durable public artifact surface; no OCR/PII classifier is claimed.
- This is explicit local worker delivery, not a new managed DTS scheduler or a
  complete production repository onboarding interface. Review qualification,
  repair and release remain their separate tickets.

## Acceptance — 2026-09-13

The user accepted the implementation after viewing the original UI/document
screenshots and the native run's provider receipt, including the explicit
controlled-provider limitation. Acceptance includes the documented baseline
stress-test failure. The user authorized OpenSpec closure, commit and push.
The reviewed implementation is unchanged since `866e118`; the closeout pass
confirmed the existing DRY/SOLID/KISS review and requires no code refactoring.

Closeout used the standard `spec-driven` archive path. The CLI created the
canonical `agent-framework-evidence-publication` spec with all four requirements.
Post-archive validation: 46 items passed, zero failed; diff and evidence links
passed. No behavior changed during closeout, so executable tests were not rerun.
