## Why

All implementation, delivery, recovery, and review components of the local GitHub issue pilot are individually verified, but the production `probare-crm` repository has not yet been activated and proven through one real GitHub-to-review run. This final pilot slice turns the completed components into a bounded live service and captures enough correlated, redacted evidence for Daniel to decide whether to keep the pilot enabled.

## What Changes

- Add a repository-local live activation contract for `probare-crm` covering labels, allowed signed webhook events, complete backlog visibility, blocker handling, and one-active-run serialization through the existing versioned `RepositoryAdapter`.
- Add a preflight/readiness surface that validates the private runtime configuration and required GitHub repository state without placing repository-specific branches or paths in the workflow core.
- Activate the installed macOS pilot and Cloudflare relay, then drive one real eligible issue from GitHub delivery through the local workflow, isolated Codex worktree, deterministic verification, and all three independent reviews.
- Publish a verified draft pull request whose current head is marked `verified` and `awaiting-review` and whose body contains the acceptance matrix plus decisive redacted evidence.
- Record a secret-safe correlation manifest for delivery, run, checkpoints, worker policy, skill versions, review verdicts, and pull-request head.
- Stop at human review. The pilot does not merge, deploy, or release; rollback disables webhook/service ingress while preserving durable state for diagnosis.

## Capabilities

### New Capabilities

- `live-repository-pilot-activation`: Safe readiness validation, live activation, end-to-end proof, and rollback of the first production repository pilot.

### Modified Capabilities

None.

## Impact

- **Write-set:** this OpenSpec change; `langgraph-github-issue-pilot` operator configuration/readiness code, tests, and operating guidance; repository-local non-secret activation/evidence artifacts; and the issue-12 checklist.
- **External systems:** the existing `probare-crm` GitHub repository and webhook, Cloudflare Worker/Queue/DLQ/Tunnel, installed macOS LaunchAgent, local SQLite/checkpoint state, one isolated worktree, and one draft pull request.
- **Interfaces:** the existing `RepositoryAdapter`, pilot CLI/HTTP read model, `pilotctl`, GitHub REST boundary, and Cloudflare diagnostics. The central workflow remains repository-neutral.
- **Secrets and privacy:** credentials remain in the existing private mode-`600` environment and platform secret stores; evidence contains only bounded redacted excerpts and correlation identifiers.
- **Direct verification:** strict OpenSpec validation and readiness checks precede activation; a real allowed GitHub event must correlate through Queue, Tunnel, inbox, LangGraph, exact-head verification, three fresh reviews, labels, and the draft PR body.
- **Rollback:** disable the GitHub webhook and unload the user LaunchAgent (and, if needed, disable the relay consumer) without deleting the database, Queue/DLQ, worktrees, branches, pull request, or evidence needed for diagnosis.
