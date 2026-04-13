# refine-plan

## Goal
Refine an existing implementation plan by appending a new iteration, maintaining the history table at the bottom, and making action status explicit.

## Steps
1) Read the existing plan file and identify the highest iteration number.
2) Parse user answers marked with `=>` and apply them as resolved decisions/missing info.
3) Create exactly one new `# Iteration N` section (N = highest + 1).
4) Derive or restate the current/actual state before writing actions so the plan can distinguish what is already done from what is still pending.
5) Include sections: Summary, Requirements Snapshot, Current State Snapshot, Action Plan, Open Items in each iteration.
6) In `Action Plan`, express every item with an explicit status marker: `[DONE]`, `[PENDING]`, or `[BLOCKED]`.
7) For each action, include either evidence of current state or an observable completion signal so readers can tell whether the work is already complete.
8) If planning reveals a missing requirement or unresolved product/scope decision, record it under `Open Items` as `[MISSING SPEC ...]` or `[DECISION SPEC ...]` instead of disguising it as an implementation action.
9) Allow unresolved `[MISSING ...]` and `[DECISION ...]` items only when explicitly marked non-blocking.
10) Determine whether the latest iteration is implementation-ready (no blocking unresolved items and next executable actions are clear).
11) If implementation-ready, automatically add `Verification Test Cases` to that same latest iteration.
12) Test cases must verify movement from actual/current state to desired target state described in the plan.
13) If no history table exists, create one with columns `Date | Iteration | Author | Delta`.
14) Update the history table at the bottom by appending exactly one row for this iteration.
15) Keep the document append-only; never overwrite prior iteration content.
16) Preserve repository/file-system references when refining implementation details.
17) Write the SessionId at file bottom if not already present; use the same resume SessionId used at agent startup.

## Output Template

### Iteration N
- Summary: {What changed from previous iteration}
- Requirements Snapshot:
  - {Requirement}
  - {Requirement}
- Current State Snapshot:
  - {What already exists / is already complete}
  - {What is missing / partially implemented}
- Action Plan:
  1) [DONE] {Action already satisfied} — Evidence: {How we know this is already complete}
  2) [PENDING] {Next implementation action} — Done when: {Observable completion signal}
  3) [BLOCKED] {Action that cannot proceed yet} — Blocked by: {Dependency or unresolved issue}
- Open Items:
  - [MISSING SPEC {what is missing in the requirements/spec}]
  - [DECISION SPEC {product/scope/behavior decision still needed}]
  - [MISSING {execution detail still needed, if this is truly a planning gap}]
- Verification Test Cases (required when implementation-ready; count is flexible, examples below):
  1) Given {actual/current state}, when {implementation steps are applied}, then {desired state outcome is observed}.
  2) Given {actual/current state}, when {migration/transition action runs}, then {data/system behavior matches desired state}.
  3) Given {failure/edge condition from actual state}, when {transition is attempted}, then {safe/expected desired-state handling occurs}.

## History Table Row
| {YYYY-MM-DD} | {N} | Claude | {Concise delta summary for this iteration} |
