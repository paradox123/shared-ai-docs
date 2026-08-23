# Implementation Evidence

## Outcome

Issue 06 is implemented through the signed production-shaped webhook and workflow-state interface. Human feedback is normalized and redacted at admission, correlated to the stored pull request, persisted as an independent batch, executed in the same run-owned worktree, and fully re-evidenced and re-reviewed on every new head. An explicit configured-human merge of the associated current head terminates the same run and LangGraph checkpoint without starting candidate work.

## Criterion Evidence

| Behavior | Verification | Observation | Status |
|---|---|---|---|
| Authorized feedback persists on the existing run and survives a service reconstruction without an available writer | `test_configured_human_feedback_is_correlated_and_persisted_on_the_existing_run` | Workflow GET retained one pending delivery-bound batch, original run/worktree identity, starting head, redacted feedback, prior evidence/review identity, and an unused three-round limit | proven |
| Approvals, bots, other users, empty feedback, and unrelated PRs have no continuation effect | `test_non_feedback_pr_activity_has_no_continuation_effect` and `test_github_adapter_recognizes_only_the_configured_human_user` | Signed cases created no feedback batch or repair invocation; real adapter identity matching is case-insensitive for the configured login but requires GitHub user type | proven |
| Cloudflare relay admits the new lifecycle event/action pairs without widening repositories | `allows the configured lifecycle delivery $event:$action` plus `npm run check` | All three new pairs produced one authenticated queue envelope; generated Worker environment types match configuration; 43 relay tests, type checks, and lint passed | proven |
| Feedback uses the existing ownership and only new active context | `test_human_feedback_reuses_run_ownership_and_fully_verifies_a_new_head` | Same run ID/worktree/branch/PR persisted; assignment retained issue/requirements and exactly the new review finding; one new head verified | proven |
| Batch counters are independent and hard-bounded | `test_feedback_gets_round_one_after_the_initial_repair_batch_exhausted_three_rounds`, `test_each_later_human_feedback_batch_starts_with_its_own_counter_and_context`, and `test_one_human_feedback_batch_stops_after_exactly_three_attempts` | New feedback began at round one after three initial repair rounds; two later batches each exposed count one with isolated text; exhausted batch exposed rounds 1/2/3 and exactly three writer invocations | proven |
| Prior-head evidence and reviews are invalidated but retained | `test_human_feedback_reuses_run_ownership_and_fully_verifies_a_new_head` | GET exposed superseded original evidence/review and `[True, False]` review history; GitHub projection added `agent-running` and removed stale verification/handoff labels before fresh verification | proven |
| Every feedback head receives complete fresh evidence, deterministic verification, and all reviews | `test_feedback_head_cannot_reuse_old_verification_and_runs_all_reviews_each_round` | First new head failed deterministic verification yet still received three reviews and stayed blocked; second new head reran all three reviews and alone became verified; nine reviewer invocations covered initial plus two feedback heads | proven |
| Configured-human current-head merge completes the same run/checkpoint across restart | `test_authorized_human_merge_completes_the_same_run_and_checkpoint_after_restart` | Run and checkpoint changed to `completed`; terminal record retained delivery, PR, head, actor, and timestamp; feedback/review histories were byte-equivalent before/after | proven |
| Unsupported PR close activity cannot complete | `test_pr_close_without_the_correlated_human_merge_does_not_complete_the_run` | Non-merged, other-user, bot, unrelated-PR, and wrong-head cases left run `running` with no completion record | proven |
| No autonomous merge, deployment, or release | Authorized merge system test plus workflow port surface | Merge processing left worktree, writer, source-publication, and reviewer call counts unchanged; workflow exposes no merge, deploy, or release command/port | proven |

## Verification Commands

- `uvx ruff check src tests` → all checks passed.
- `.venv/bin/pytest -q` → 191 tests passed; only the pre-existing upstream FastAPI/Starlette TestClient deprecation warning was emitted.
- `npm run check` in `cloudflare-github-webhook-relay` → Wrangler type generation check, TypeScript checks, Oxlint, and 43 Vitest cases passed; only local missing-secret and Node `punycode` development warnings were emitted.
- `openspec validate continue-run-after-human-feedback --strict` → change valid.
- `uv lock --check` → lockfile valid and unchanged.
- `git diff --check` → no whitespace errors.

## Refactoring Review

- **DRY:** latest-review read-back now delegates to the canonical review-history projection instead of duplicating SQL/result rendering.
- **SOLID:** human feedback orchestration is isolated in `feedback.py`; webhook admission, GitHub identity, persistence, source publication, verification, and reviews remain separate ports/modules.
- **KISS:** feedback reuses the existing versioned repair assignment/result, worker policy, evidence qualifier, publication adapter, deterministic verifier, and review coordinator rather than adding parallel worker contracts.

## Known Warning

The suite emits one upstream FastAPI/Starlette warning that the current `httpx` TestClient integration is deprecated in favor of `httpx2`. It does not affect signed-HTTP behavior or this change's results.
