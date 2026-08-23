## Why

Cloudflare Queue retains deliveries for only 24 hours, so a longer Mac absence can leave the local pilot unaware of GitHub state changes that occurred while it was offline. The next Mac boot must close that gap once, without turning the pilot into a poller or duplicating work when a delayed Queue delivery arrives.

## What Changes

- Persist a bounded local liveness timestamp and the last reconciled operating-system boot session.
- On the first pilot start of a boot, trigger one startup reconciliation only when the previous liveness timestamp is at least 24 hours old; ordinary process restarts in the same boot do not trigger another run.
- Read current authorized/open and active issue state plus associated pull-request state through the repository adapter.
- Convert only missing domain transitions into deterministic synthetic commands and accept them through the same durable inbox/dispatch path as webhook deliveries.
- Make synthetic commands and later Queue deliveries for the same domain state converge on one durable transition in either arrival order.
- Return to webhook-driven operation after startup reconciliation; introduce no timer or periodic GitHub polling.
- Prove the threshold, once-per-boot behavior, durable restart behavior, current-state recovery, and both Queue/reconciliation races through the productive HTTP read-back with real SQLite persistence and controlled clock, boot-ID, and GitHub boundaries.

## Capabilities

### New Capabilities

- `startup-state-reconciliation`: Once-per-Mac-boot recovery of GitHub state after an offline interval of at least 24 hours, using the existing durable inbox and workflow transitions without duplicate effects.

### Modified Capabilities

None.

## Impact

- Write-set: `langgraph-github-issue-pilot/src/github_issue_pilot/{app,storage,workflow,github}.py` or a focused reconciliation module, `langgraph-github-issue-pilot/tests/`, the pilot README, Issue 10, and this OpenSpec change.
- SQLite gains additive liveness, boot-session, reconciliation-run, and domain-transition identity records; existing inbox, run, LangGraph, recovery, review, repair, and feedback records remain authoritative.
- The repository adapter gains a bounded current-state read surface for authorized/open and active issues with associated pull requests.
- Existing `POST /webhooks/github` and `GET /workflows/{owner}/{repository}/issues/{issue_number}` contracts remain the productive observation seam. Startup reconciliation runs before accepting new deliveries.
- No periodic job, additional service, merge/deploy/release capability, or guarantee beyond current GitHub read access is introduced.
