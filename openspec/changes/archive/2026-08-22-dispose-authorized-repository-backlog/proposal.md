## Why

The local pilot can durably claim one eligible issue, but it cannot yet evaluate inherited authorization or safely schedule a complete repository backlog. This slice adds the repository-neutral control-plane rules needed to select deterministic, unblocked work for `probare-crm` while preventing parallel implementations and stacked pull requests.

## What Changes

- Introduce a versioned `RepositoryAdapter` contract that owns repository-specific labels, event allowlists, issue provenance and blocking relationships, and GitHub projections.
- Configure `probare-crm` through that adapter without repository-specific branches in the workflow core, and prove portability with a second in-memory adapter contract test.
- Treat `ready-for-agent` as the sole implementation authorization for every issue type, including agent-applied authorization when a Daniel-authored issue, linked PRD, or valid parent/child chain proves the inherited mandate.
- Interrupt unverifiable provenance or a material expansion beyond inherited scope as a product decision instead of claiming the issue.
- Build a deterministic per-repository frontier that admits at most one active implementation, retains simultaneous candidates without losing events, and never creates stacked pull requests.
- Keep issues with open `Blocked by` relationships queued until the blocker pull request is human-merged and the blocker issue is closed, then release the next deterministic candidate.
- Extend the productive workflow read model so queued, interrupted, blocked, and selected outcomes are directly observable.

## Capabilities

### New Capabilities

- `authorized-repository-backlog-dispatch`: Repository-neutral authorization, blocking, deterministic frontier selection, and per-repository serialization for the GitHub issue pilot.

### Modified Capabilities

- `local-github-issue-claim`: Generalize claim eligibility and external projections behind the versioned repository adapter while preserving durable, idempotent HTTP acceptance and workflow-state observation.

## Impact

- **Write-set:** `langgraph-github-issue-pilot/src/github_issue_pilot/`, its behavior tests and package documentation, this OpenSpec change, the durable OpenSpec specs named above, implementation evidence, and the local issue-07 checklist.
- **Interfaces:** the application factory accepts repository adapters; adapters expose current issue state, provenance, blocking/merge state, and idempotent projections; the HTTP webhook and workflow-state endpoints remain the productive public seam.
- **Data:** SQLite gains durable candidate and disposition state needed to retain concurrent frontier events and resume scheduling after restart.
- **Dependencies:** no new external service or live repository is activated; tests control GitHub through repository adapters and use real HTTP, SQLite, and LangGraph persistence.
- **Direct verification:** submit signed deliveries for authorized, self-authorizable, invalid-provenance, open/closed-blocker, all-issue-type, and simultaneous-candidate scenarios through the HTTP interface; observe dispositions and adapter effects; reconstruct the application over the same database; run the same contract suite against `probare-crm` and a minimal second adapter.
