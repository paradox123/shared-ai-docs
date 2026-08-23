## Why

The pilot currently stops after publishing an evidence-backed draft pull request, so Daniel has no independent, head-bound decision that requirements, repository quality, and architecture all passed before human review begins. Issue 04 adds that fail-closed review boundary while preserving reviewer independence and read-only access.

## What Changes

- Run requirements, code-quality, and architecture reviews as three fresh, independent, read-only worker executions against the same published pull-request head.
- Validate and persist a structured verdict with rationale, findings, policy, and skill provenance for every review axis; requirements review is always applicable.
- Route requirements and code review to the separate axes of `code-review`, and architecture review to `codebase-design` plus `domain-modeling`.
- Aggregate the three verdicts without compensation: one failure or invalid/missing result blocks verification, while all applicable passes project `verified` and `awaiting-review` for the reviewed head and remove `agent-running`.
- Expose review results and the head-bound verification outcome through the productive workflow read model and cover both blocked and successful paths through public behavior and boundary contracts.

## Capabilities

### New Capabilities

- `independent-pr-review-verification`: Defines independent reviewer execution, versioned verdicts and routing provenance, fail-closed aggregation, current-head verification, GitHub label projection, and durable public read-back.

### Modified Capabilities

None.

## Impact

- Extends `langgraph-github-issue-pilot` contracts, policy/routing, worker boundary, workflow state, persistence, repository adapter, and HTTP read-back after draft-PR publication.
- Adds contract and signed-HTTP system tests with real SQLite/LangGraph persistence and controlled worker/GitHub boundaries; no live GitHub or model calls are introduced into the suite.
- Review workers remain read-only and cannot change source, repair findings, merge, deploy, or make product decisions.
- Write-set is limited to `langgraph-github-issue-pilot/`, this OpenSpec change, the new canonical capability spec, pilot documentation, and Issue 04 status/evidence.
