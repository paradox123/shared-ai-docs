## Why

The pilot currently stops after an eligible GitHub issue is claimed, so the persistent run never turns the bounded issue into isolated implementation work. This change adds the worker boundary and policy needed to start that work reproducibly without modifying Daniel's checkout or coupling LangGraph to an experimental Codex server.

## What Changes

- Build a versioned implementation assignment and evidence matrix from the claimed issue, repository context, requirements, and current findings only.
- Create one isolated Git worktree for the run and give only the implementer write access to it.
- Invoke a replaceable Codex CLI worker adapter non-interactively with a validated structured result.
- Route Matt-Pocock skills by issue type and record model, reasoning, skill versions or hashes, assignment, result, and rights profile with the persistent run.
- Enforce a versioned node policy: deterministic work uses no model, presentation-only work uses Luna/`medium`, regular agent work uses Terra/`xhigh`, and only defined escalations use Sol/`xhigh`.
- Reject unsupported model/reasoning combinations and keep failed or invalid worker results from affecting other worktrees or existing pull requests.

## Capabilities

### New Capabilities

- `isolated-issue-worker`: Defines bounded implementation assignments, evidence planning, isolated worktrees, worker contracts, skill/model policy, structured persistence, and failure isolation for a claimed issue.

### Modified Capabilities

None.

## Impact

- Extends `langgraph-github-issue-pilot` workflow state, persistence, configuration, and HTTP read-back.
- Adds Git worktree and Codex CLI boundary adapters plus versioned JSON schemas and node policy data.
- Adds contract and workflow behavior tests; no experimental Codex app-server or exec-server dependency is introduced.
- Write-set is limited to `langgraph-github-issue-pilot/`, this OpenSpec change, the canonical `isolated-issue-worker` spec, the pilot documentation, and Issue 02 evidence/status.
