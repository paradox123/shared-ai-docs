## Why

The current pilot stops at a failed independent review batch, leaving a draft pull request blocked even when the same implementer could repair the concrete findings. Issue 05 requires a bounded, observable continuation that either verifies a new pull-request head or hands the preserved work to Daniel with a precise reason.

## What Changes

- Aggregate concrete findings from every failed review axis into one versioned repair assignment that only the writing implementer receives.
- Run at most three repair rounds per initial review batch, with a repair commit, deterministic verification, and a fresh three-axis review batch bound to each new pull-request head.
- Keep regular repairs on Terra/`xhigh`, and use Sol/`xhigh` only for defined material escalations, a structured worker escalation, or the third and final repair round.
- Preserve every attempt and open finding on the draft pull request; after the third failed round, project `needs-info` for missing or contradictory requirements and `ready-for-human` for conflicts that cannot be resolved agentically.
- Treat small reversible presentation details autonomously while retaining semantic warnings, consent, domain actions, and other product behavior as human product decisions.
- Prove successful repair, the hard three-round stop, and both human handoff outcomes through the signed HTTP workflow seam with real SQLite and LangGraph persistence plus controlled worker, Git, and GitHub boundaries.

## Capabilities

### New Capabilities

- `bounded-review-repair`: Defines finding aggregation, repair execution, full re-verification, round limits, escalation, durable attempt history, and terminal human handoff.

### Modified Capabilities

None.

## Impact

- **Write set:** `langgraph-github-issue-pilot/src/github_issue_pilot/` workflow, implementation/review/publication adapters, persistence/read model, policy use, and new versioned repair contracts; focused pilot tests; pilot README; this OpenSpec change and its new capability spec.
- **External behavior:** workflow-state read-back gains repair attempts, current findings, round count, and terminal handoff state; GitHub projection can update the existing draft PR head/body and add `needs-info` or `ready-for-human` without merging or deploying.
- **Direct verification:** focused contract tests plus signed `POST /webhooks/github` and `GET /workflows/{owner}/{repository}/issues/{issue_number}` system tests must observe a repaired verified PR, exactly three unsuccessful rounds with no fourth worker invocation, restart-safe persisted attempt/PR state, and both terminal label projections.
- Human feedback batches (Issue 06), general crash-time continuation (Issue 08), merge, deployment, and release remain out of scope.
