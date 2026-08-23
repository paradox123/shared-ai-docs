## Why

The pilot currently treats the verified pull-request head as the end of its automatic work, so Daniel's later change requests cannot safely resume the persistent run without risking stale evidence, stale review approval, or a second implementation assignment. Issue 06 must make human feedback and human merge observable lifecycle events while retaining the existing human-only merge boundary.

## What Changes

- Accept relevant pull-request review and review-comment deliveries as human feedback only when they come from the configured human and target the run's existing pull request.
- Resume the same persistent run, run-owned worktree, branch, and pull request with an assignment containing only the new feedback batch plus the still-valid issue and requirements context.
- Give every human feedback batch an independent maximum of three repair rounds without reusing the initial review batch's counter.
- On every new implementation head, converge GitHub labels to `agent-running`, remove `verified` and `awaiting-review`, and invalidate previous-head evidence and review verdicts for qualification purposes.
- Recreate commit-bound evidence, deterministic verification, and all three independent reviews for the new head before it can become verified again.
- Treat a human merge of the associated pull request as terminal: close the persistent run and converge the issue and workflow read model to the same completed state.
- Reject or ignore unrelated pull-request activity, non-human feedback, unsupported approval-only events, and any attempt by the workflow to merge, deploy, or release.
- Prove feedback continuation, batch-local counters, head invalidation, complete re-verification, and human merge completion through signed HTTP system tests with real SQLite and LangGraph persistence.

## Capabilities

### New Capabilities

- `human-feedback-run-continuation`: Defines authenticated human feedback intake, same-run continuation, independent feedback-batch repair limits, new-head invalidation and re-verification, and terminal human-merge reconciliation.

### Modified Capabilities

None.

## Impact

- **Code:** `langgraph-github-issue-pilot/src/github_issue_pilot/` webhook admission, GitHub adapter contract, persistence/read model, feedback orchestration, publication, review, and workflow lifecycle; Cloudflare relay event/action allowlist configuration.
- **Tests:** focused contracts plus `langgraph-github-issue-pilot/tests/test_workflow_interface.py` signed-delivery system coverage and Cloudflare relay ingress allowlist coverage.
- **External behavior:** the existing webhook endpoint accepts narrowly authorized pull-request feedback and merge events; workflow-state read-back exposes feedback batches, superseded head-bound records, current labels, and terminal completion.
- **Write-set:** only this OpenSpec change, pilot source/contracts/tests, the Cloudflare relay allowlist/configuration contract, the Issue 06 checklist, and direct implementation evidence. The unrelated dirty archive-skill file remains untouched.
- **Direct verification:** focused tests, the complete pilot test suite, strict OpenSpec validation, `git diff --check`, and signed HTTP POST/GET behavior proving the public lifecycle without a workflow-owned merge, deploy, or release effect.
