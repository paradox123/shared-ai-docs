## Why

The pilot persists many workflow records, but a process exit can leave an active run between durable transitions with no safe way to continue it. Recovery must converge on the same run, worktree, branch, pull request, review/feedback batch, and terminal outcome without repeating external effects.

## What Changes

- Add startup recovery for every non-terminal repository run and incomplete implementation, publication, review, repair, and human-feedback transition.
- Persist transition intent and completion identities so restart can distinguish completed work from work that must be reconciled or retried idempotently.
- Reuse existing run, worktree, branch, pull-request, head, worker, review, repair, feedback, delivery, and checkpoint correlations during recovery.
- Expose one explicit recovery status and redacted diagnostic history through the existing workflow-state HTTP read-back.
- Prove recovery by terminating a real pilot process at representative phase boundaries, restarting it on the same SQLite database, and observing convergence through the signed HTTP interface and controlled external boundaries.
- Keep completed human-merge outcomes terminal across restart.

## Capabilities

### New Capabilities

- `workflow-crash-recovery`: Durable, idempotent continuation of active pilot workflows after process termination across claim, implementation, publication, review, repair, and human-feedback phases.

### Modified Capabilities

None.

## Impact

- Write-set: `langgraph-github-issue-pilot/src/github_issue_pilot/{app,workflow,storage}.py`, focused recovery support in existing coordinators/adapters if required, `langgraph-github-issue-pilot/tests/`, the pilot README, and this OpenSpec change.
- Existing SQLite schema and LangGraph checkpoints gain recovery metadata without storing webhook bodies, credentials, feedback payload copies beyond the already bounded records, or unredacted diagnostics.
- The existing `POST /webhooks/github` and `GET /workflows/{owner}/{repository}/issues/{issue_number}` interfaces remain the productive seam; startup gains automatic reconciliation before new work is accepted.
- No merge, deployment, release, second worktree, second run, or second pull request capability is introduced.
