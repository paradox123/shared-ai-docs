## Why

The live pilot can discard a schema-valid final worker result when an independent JSONL diagnostic line is malformed, and its failure record then collapses the cause to a generic message. A newly claimed sequential issue can also start from a stale local branch because worktree creation does not fetch and pin the configured remote base first.

## What Changes

- Parse the final `--output-last-message` result independently from best-effort JSONL diagnostics so a valid structured result remains authoritative.
- Persist bounded, redacted diagnostic parse/failure codes and already parsed events when worker execution fails, without storing arbitrary stderr, secrets, or an invalid result payload.
- Fetch the configured `origin` branch before creating a new run worktree, resolve it to one immutable commit SHA, create the run branch from that SHA, and retain that SHA as the durable worktree base.
- Preserve restart adoption of an existing run-owned worktree without moving its original immutable base.
- Keep `probare-crm` Issue #2 implementation, mailbox credentials/protocol design, frontend dependency installation, publication, and retry outside this change.

## Capabilities

### Modified Capabilities

- `isolated-issue-worker`: Make structured worker-result ingestion independent from diagnostic JSONL quality and pin every new implementation worktree to a freshly resolved remote base commit.
- `workflow-crash-recovery`: Retain bounded worker failure diagnostics and the immutable worktree base across recovery.

## Impact

- Write-set: focused changes in `langgraph-github-issue-pilot/src/github_issue_pilot/{implementation,workflow,storage}.py`, adapter/workflow contract tests, the pilot README, and this OpenSpec change.
- Existing public HTTP routes remain unchanged; workflow read-back gains more precise bounded worker failure information and exposes the already durable worktree base as a commit SHA.
- GitHub Issue #2 is not implemented, retried, published, labelled, or otherwise mutated by this change.
