# Implementation Evidence

Verified at `2026-08-23T07:42:30Z` against working-tree changes based on commit `ce05a3498f23d60f4fdd4bea24ca59714b1c8d21` on branch `main` in `shared-ai-docs`.

## Acceptance Matrix

| Issue 04 criterion | Direct verification | Observed result | Verdict |
| --- | --- | --- | --- |
| Active OpenSpec change defines goal, scope, write-set, and direct verification before implementation | `proposal.md`, `design.md`, capability spec, `tasks.md`, pre-implementation `acceptance-criteria-matrix.md`, and `openspec validate verify-draft-pr-with-independent-reviews --strict` | The apply-ready change was strictly valid before the first pilot runtime edit. Its write-set is limited to pilot code/tests/docs, this change/future canonical spec, and Issue 04. | proven |
| Three fresh independent read-only reviews use the same PR head | `test_codex_review_adapter_starts_three_fresh_read_only_axis_specific_invocations` and `test_one_failed_axis_blocks_verification_after_three_independent_reviews_through_http_seam` | Three separate `codex exec` calls used distinct invocation/thread identities, `read-only`, one worktree, one adapter-derived 40-character SHA, no peer verdicts, and axis-only prompts that prohibit sub-agents, writes, repair, merge, deploy, and product decisions. | proven |
| Every reviewer returns a schema-valid structured verdict | `test_review_assignment_and_result_contracts_accept_every_axis`, `test_review_result_contract_rejects_malformed_verdicts`, `test_requirements_review_can_never_be_not_applicable`, and invalid-output adapter cases | The versioned contracts accept only `pass`, `fail`, or `not_applicable`, require rationale and structured findings, bind axis/invocation/head, reject extra or malformed output, require findings for `fail`, and reject Requirements `not_applicable`. | proven |
| Axis-specific substantive scope is preserved | Signed-HTTP failure case plus persisted `review.results[*].assignment.scope` | Requirements explicitly compares requirements, implementation, and qualified behavioral evidence; code checks repository standards and code smells; architecture checks domain language, ADRs, modules, interfaces, seams, adapters, depth, and test surfaces. | proven |
| Terra/xhigh policy and skill provenance remain traceable | `test_versioned_node_policy_selects_exact_model_reasoning_and_rights`, review routing/worker contracts, and signed-HTTP read-back assertions | Every persisted result exposes policy version/task, `gpt-5.6-terra`, `xhigh`, `read-only`, route axis, skill names, and 64-character content hashes. Tampered skill provenance is rejected before process launch. | proven |
| Requirements/code use separate `code-review` axes; architecture uses design/domain skills | `test_review_skill_routing_preserves_each_independent_axis_with_content_hashes` and the three-invocation adapter/system contracts | Requirements routes to `code-review`/`spec`, code to `code-review`/`standards`, and architecture to `codebase-design` plus `domain-modeling`/`architecture`; the public review record retains this separation. | proven |
| One fail blocks; all applicable passes project successful labels | `test_one_failed_axis_blocks_verification_after_three_independent_reviews_through_http_seam`, `test_all_applicable_axes_pass_and_project_verified_current_head_through_http_seam`, and `test_github_adapter_reads_current_pr_head_and_converges_verified_workflow_labels` | `pass/fail/pass` preserved all results and performed no success projection. `pass/pass/not_applicable` first read the current head, then convergently added `verified`/`awaiting-review`, removed `agent-running`, and retained unrelated/triage labels. | proven |
| Reviewers cannot mutate, repair, merge, deploy, or decide product behavior | Review-worker CLI contract plus signed-HTTP controlled source/GitHub effects | All reviewer processes use enforced `read-only`; their interface has no source, repair, merge, deploy, or product-decision operation. The blocked system case observed only the one pre-review publication and no verification-label write. | proven |
| Primary system seam proves separation, fail-closed behavior, projection, head binding, and restart | Signed webhook POST plus workflow-state GET cases for failure, success, head mismatch, and restart with real SQLite/LangGraph | HTTP read-back exposes three separate results and their provenance. A moved head produced durable `head_changed` and no labels. Reconstruction returned the identical review batch without another reviewer, head read, or GitHub write. | proven |

## Verification Commands

```text
uv run pytest -q
uvx ruff check .
uv lock --check
git diff --check
openspec validate verify-draft-pr-with-independent-reviews --strict
```

Observed summary:

- full suite: `135 passed`
- Ruff: `All checks passed!`
- lockfile: resolved `54 packages` without change
- diff check: passed
- strict OpenSpec validation: passed

The test runner emits one upstream FastAPI/Starlette deprecation warning recommending the future `httpx2` TestClient path. It does not affect the verified signed-HTTP behavior.
