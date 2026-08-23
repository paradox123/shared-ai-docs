# Implementation Evidence

Verified at `2026-08-23T07:13:55Z` against working-tree changes based on commit `306164fe35d43c31b6fae844951ce828dde067e2` on branch `main` in `shared-ai-docs`.

## Acceptance Matrix

| Issue 03 criterion | Direct verification | Observed result | Verdict |
| --- | --- | --- | --- |
| Active OpenSpec change defines goal, scope, write-set, and direct verification before implementation | `proposal.md`, `design.md`, capability spec, `tasks.md`, pre-implementation `acceptance-criteria-matrix.md`, and `openspec validate create-evidence-backed-draft-pr --strict` | The change was apply-ready and strictly valid before the first runtime edit. Its write-set is limited to the pilot package, this change/future capability spec, pilot docs, and Issue 03. | proven |
| Implementation is committed/pushed and creates exactly one draft PR | `test_source_control_commits_and_pushes_the_explicit_run_branch`, `test_source_control_pushes_an_already_committed_implementation_without_extra_commit`, `test_sufficient_evidence_publishes_one_commit_bound_draft_pr_through_http_seam`, and duplicate-delivery behavior | A real temporary Git remote observed the run branch at the returned 40-character commit SHA; uncommitted work received the fixed issue commit and pre-committed work received no extra commit. The signed HTTP flow exposed one draft PR, and duplicate delivery caused no second worker, source publish, or PR write. | proven |
| PR body contains every criterion with verdict, interface, expected result, proof, and head | `test_sufficient_evidence_publishes_one_commit_bound_draft_pr_through_http_seam` through signed POST and workflow GET | Both assignment criteria appeared once in the stored evidence and canonical body; the matrix and detail sections exposed pass verdicts, HTTP interface, expected results, concrete artifacts, and the adapter-derived head SHA. | proven |
| REST, UI, recovery, and idempotency evidence use direct observations | `test_complete_direct_evidence_is_qualified_for_every_criterion`, six `test_each_evidence_kind_requires_its_direct_observations` cases, and renderer assertions | REST required request/response/read-back, UI required interaction/screenshot, recovery required restart/read-back, and idempotency required repeat/read-back. Removing any required phase failed qualification. REST excerpts and a Markdown screenshot reference were rendered inline. | proven |
| Negative gate proves rejection and absent forbidden side effect | Known-good `negative_gate` package plus `negative-without-side-effect-read-back` HTTP case | The complete negative-gate pair qualified. Removing `side_effect_read_back` produced durable `missing_direct_observation`, with zero source or PR effects through the productive seam. | proven |
| Background work proves eventual business result | Known-good `background` package plus `background-surrogate` HTTP case | `eventual_result` qualified only with an embedded business observation. Queue/process/health evidence produced durable `infrastructure_surrogate` and no publication effects. | proven |
| Infrastructure-only evidence is rejected | Ten `test_operational_surrogate_alone_never_qualifies_as_background_result` cases plus missing-kind/log-correlation gate tests | Build, process start, container state, healthcheck, naked HTTP status/2xx, queue acceptance, enqueue, log claim, and static starting screenshot each failed as sole evidence; logs additionally require correlation and never replace the kind's direct phases. | proven |
| Decisive screenshots, REST excerpts, and correlated logs are embedded | `test_qualified_evidence_is_redacted_and_rendered_with_embedded_artifacts` and the sufficient signed-HTTP behavior | The renderer embedded REST artifacts in fenced excerpts, UI screenshots as Markdown images, and correlated logs adjacent to the criterion. The public draft body returned by HTTP contained compact REST and correlation evidence rather than raw-artifact-only links. | proven |
| Evidence is head-bound and sensitive output is redacted or blocked | Sufficient HTTP test, `test_sensitive_worker_evidence_and_diagnostics_are_redacted_before_read_back`, and `test_source_control_rejects_sensitive_diff_before_commit_or_push` | Every matrix/detail entry used the source adapter's exact SHA. Configured secrets, GitHub tokens, authorization values, and email addresses were absent from persisted result, diagnostics, evidence, and body; a sensitive staged diff produced neither commit nor remote branch. | proven |
| Primary-seam behavior covers sufficient and deliberately insufficient packages | Signed webhook POST plus workflow-state GET tests for success, three insufficient modes, duplicate delivery, and restart | Sufficient evidence produced one durable draft identity/body/head. Missing criterion coverage, incomplete negative-gate evidence, and background surrogates produced durable safe rejections with no source/PR effects. Restart returned the identical published record without another write. | proven |

## Verification Commands

```text
uv run pytest -q
uvx ruff check .
uv lock --check
git diff --check
openspec validate create-evidence-backed-draft-pr --strict
```

Observed summary:

- full suite: `110 passed`
- Ruff: `All checks passed!`
- lockfile: resolved `54 packages` without change
- diff check: passed
- strict OpenSpec validation: passed

The test runner emits one upstream FastAPI/Starlette deprecation warning recommending the future `httpx2` TestClient path. It does not affect the verified HTTP behavior.
