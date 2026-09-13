# Issue 13 acceptance evidence

Target branch: `main`. Starting commit: `688d92d2680eda5cf92c03b8d03da26d2dde08d9`.
Implementation commits: `883e67a`, `21ffa83`, `573d208`.
The user’s pre-existing README/Renovate changes are excluded.

## Observable acceptance

| Requirement | Expected behavior | Observed result and direct evidence |
| --- | --- | --- |
| Unchanged expected head | Reject mutations even if the deterministic command fails | The test command creates a real commit then exits 1. Worker/HTTP exposes `qualification-head-drift`, with no qualified head. See mutation observation. |
| Three independent reviews | Fresh requirements, code-quality and architecture sessions share one SHA and no peer verdicts | Controlled and real pinned Codex runs expose three distinct session IDs, Terra/xhigh/read-only policy and independent structured results. Actual repository skill contents are checksum-pinned in the final native run. |
| Complete current-head gate | Require evidence, deterministic pass and every applicable axis | Successful HTTP read-back contains one qualified SHA equal to the provider draft head. Wrong-head results and requirements `not_applicable` are rejected; invalid receipts remain diagnostic data. |
| New-head invalidation | Never inherit old evidence/checks/verdicts | A repair produces a different real commit, fresh evidence, another check and three new reviewer sessions. Provider-head change on redelivery clears qualifiedHeadSha. |
| Same writer and worktree | Aggregate actionable findings into a numbered assignment | Requirements and architecture findings reach the original writer ID and existing checkout. The real Codex writer adds a deliberately missing module docstring in that same session. Prior repair result summaries are included in later assignments. |
| Complete re-verification | Recapture and re-review every repaired head | Two-head success has six unique reviewer sessions and the latest evidence/check SHA matches the updated one-and-only draft. Checks failing normally still execute all three axes. |
| Three-round bound | No fourth repair; preserve a concrete Human Request | Persistent failing reviews/checks yield repairs 1, 2, 3 and four head rounds/twelve reviews. Round three records Sol/xhigh/final_repair_round. Restart/redelivery preserves three repairs, the draft and actionable findings in the Human Request. |
| Human review boundary | Qualification must not approve or ship | Provider read-back remains draft=true with exactly one PR. The code has no approval, merge, deployment or release operation. |
| Recovery | Adopt completed external operations without another session/write | SIGKILL after a review or repair receipt is followed by adoption under the same operation ID. A lost repair reply retains repository ownership until read-back adopts it; a successor is blocked while uncertain. Interrupted deterministic work is not rerun. |
| Input integrity | Preserve schema checks, provenance and source paths | Tests under Python -O reject forbidden/malformed verdicts and changed skill bytes. Unicode and tab/newline Git paths preserve full source content via NUL-delimited raw reads. |

The executable scenarios are in [worker/HTTP tests](../../../microsoft-agent-framework-work-package-pilot/tests/test_head_qualification.py),
[adapter contract tests](../../../microsoft-agent-framework-work-package-pilot/tests/test_head_qualification_adapter.py) and
[real Codex tests](../../../microsoft-agent-framework-work-package-pilot/tests/test_head_qualification_native.py).
Direct public observations:

- [Failed command mutates the head](evidence/test_failed_verification_that_mutates_head_is_rejected.json)
- [Real three-session qualification with actual skills](evidence/test_real_three_session_review_qualifies_the_evidence_head.json)
- [Real same-session writer repair and re-qualification](evidence/test_real_writer_repairs_review_findings_in_original_session.json)
- [Exhaustion, findings and durable Human Request](evidence/test_three_unsuccessful_repairs_leave_concrete_human_request_and_no_fourth.json)
- [Lost repair reply and repository ownership](evidence/test_lost_repair_reply_remains_owned_until_same_operation_is_adopted.json)
- [Provider-head invalidation](evidence/test_changed_provider_head_invalidates_qualified_head_on_redelivery.json)

These JSON files contain authenticated run projection observations and independent provider read-back captured by the tests.

## TDD and review

Behavioral red cases included: publication stopped before qualification; failed-head mutation was unchecked;
actionable findings stopped before repair; Human Requests lacked concrete findings; invalid review receipts were dropped;
a lost repair reply incorrectly released the run; Python optimization disabled contract assertions;
prior repair summaries were absent; and Git display-quoted filenames could not be loaded.
Each was reproduced through the worker/HTTP or JSON adapter seam before its corresponding implementation.
The initial Python environment lacked jsonschema; the documented uv environment repaired the harness before counting a red result.

Standards review: no documented-standard violation; the follow-up pathname finding was fixed.
Spec review: prior summary omission and the subsequent pathname finding were fixed and re-reviewed.
Reviewer isolation and actual-skill compatibility were checked separately from code standards. [Independent review reports](reviews.md).

## Boundaries and limitations

- PostgreSQL, the .NET worker/API, local and bare Git, and the pinned Codex runtime/native writer session are real.
  GitHub is an independent controlled HTTP provider. This issue does not claim a live GitHub PR or human approval.
- The two native tests use the repository’s actual code-review, codebase-design and domain-modeling skill files.
  The reviewer role applies their assigned axis to supplied immutable source/evidence; it does not execute their setup,
  delegation or commit workflows. Reviewer tools remain disabled to prevent peer-context access.
- Provider changes are revalidated on each stage/redelivery. This change does not install a background webhook monitor.
- Human Requests retain findings and investigation links; an in-app answer/resume command for qualification handoff
  is outside this slice. Repeating the original command cannot reset the automatic repair limit.
- Existing publication policy rejects uninspectable/binary outgoing source before draft creation; this change retains that limit.
- OpenSpec remains active for user acceptance; no archive, push, merge, deployment or release was performed.

## Validation

- [.NET build](evidence/dotnet-build.txt): succeeded with zero warnings/errors.
- Strict OpenSpec validation and git diff --check: passed.
- [Worker/HTTP qualification suite](evidence/head-worker-tests.txt): 10 tests passed.
- [Adapter and publication regression](evidence/adapter-publication-tests.txt): 12 tests passed, including optimized Python and exact Git paths.
- [Real Codex with actual repository skills](evidence/real-codex-tests.txt): 2 tests passed, including one real writer repair and six fresh reviewer sessions across its two heads.
- [Full pilot regression](evidence/full-pilot-regression.txt): 196 tests in 1040.306 seconds; 176 passed, 20 opt-in external-runtime/live-provider probes skipped. The two new qualification native probes were run separately above. The 10,015-event process-failure/reconnect/restore stress test passed, with equal restored checksums and no raw canary matches.

The full run began before the final review follow-ups; the final targeted worker and adapter suites cover those fixes. Native actual-skill verification and the subsequent exact-path regression are recorded separately. This is not a claim that all external probes ran against one frozen final commit.

Reproduce from `microsoft-agent-framework-work-package-pilot` using:

```bash
uv run --python 3.14 --with-requirements codex-requirements.txt python -m unittest discover -s tests -p 'test_*.py' -v
uv run --python 3.14 --with-requirements codex-requirements.txt python -m unittest tests.test_head_qualification tests.test_head_qualification_adapter tests.test_publication_adapter -v
WPCP_CODEX_ENDPOINT_PROBE=1 uv run --python 3.14 --with-requirements codex-requirements.txt python -m unittest tests.test_head_qualification_native.NativeHeadQualificationTests -v
```

Set `WPCP_QUALIFICATION_PROOF_DIR` to a disposable output directory to capture the public JSON observations. No credentials or private adapter receipts are included in this evidence directory.
