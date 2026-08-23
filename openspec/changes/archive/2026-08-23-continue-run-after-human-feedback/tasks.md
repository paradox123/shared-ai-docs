## 1. OpenSpec Contract

- [x] 1.1 Validate the proposal, design, capability spec, scoped write-set, and direct verification plan with `openspec validate continue-run-after-human-feedback --strict` before production implementation.

## 2. Authorized Lifecycle Intake

- [x] 2.1 Add failing request-boundary and GitHub-adapter contract tests for configured-human change requests and merge identity, then implement minimal normalized/redacted feedback and merge delivery admission while rejecting approvals, unrelated PRs, bots, other users, empty feedback, and unsupported activity.
- [x] 2.2 Add failing persistence/read-model tests for delivery-idempotent feedback batches correlated to the stored run and pull request, then implement additive durable batch history and terminal merge metadata.
- [x] 2.3 Add a failing Cloudflare relay ingress contract for every supported feedback/merge event-action pair, then update the configured allowlist and generated Worker environment type without widening repositories or other actions.

## 3. Same-Run Feedback Execution

- [x] 3.1 Add a failing signed-HTTP system test proving an authorized feedback delivery reuses the run, worktree, branch, and PR and passes only the new feedback plus valid issue/requirements context; implement the feedback coordinator and bounded writer assignment.
- [x] 3.2 Add failing behavior cases for exhausted initial repairs and multiple human feedback batches, then enforce an independent monotonic maximum of three attempts per feedback batch with no fourth invocation.

## 4. Head Invalidation And Re-verification

- [x] 4.1 Add a failing signed-HTTP case for a new feedback commit, then publish to the existing PR, require a distinct head, immediately add `agent-running`, remove `verified`/`awaiting-review`, and expose prior-head evidence/reviews as superseded history.
- [x] 4.2 Add a failing signed-HTTP case proving fresh criterion evidence, deterministic verification, and all three independent reviews are required for the feedback head; implement full head-bound re-verification and exact successful label convergence without prior-result reuse.

## 5. Human Merge Completion And Verification

- [x] 5.1 Add failing signed-HTTP merge cases, then complete only the correlated run merged by the configured human, preserve history across restart, avoid candidate dispatch, and prove non-merged/unrelated/non-human events have no completion effect.
- [x] 5.2 Refactor touched code/specs for DRY, SOLID, and KISS without behavior changes; run focused tests, the complete pilot suite, Ruff, strict OpenSpec validation, and `git diff --check`.
- [x] 5.3 Record an acceptance-criteria matrix and implementation evidence mapping every Issue 06 outcome to its direct signed-HTTP or adapter observation, including the absence of workflow merge, deploy, and release effects.
