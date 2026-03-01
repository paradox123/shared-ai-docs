# RefinePlan

## Goal
Refine an existing implementation plan by appending a new iteration and maintaining the history table at the bottom.

## Steps
1) Read the existing plan file and identify the highest iteration number.
2) Parse user answers marked with `=>` and apply them as resolved decisions/missing info.
3) Create exactly one new `# Iteration N` section (N = highest + 1).
4) Include sections: Summary, Requirements Snapshot, Detailed Plan, Open Items.
5) Allow unresolved `[MISSING ...]` and `[DECISION ...]` items only when explicitly marked non-blocking.
6) Determine whether the latest iteration is implementation-ready (no blocking unresolved items).
7) If implementation-ready, automatically add `Verification Test Cases` to that same latest iteration.
8) Test cases must verify movement from actual/current state to desired target state described in the plan.
9) Keep unresolved gaps as `[MISSING ...]` and unresolved choices as `[DECISION ...]`.
10) If no history table exists, create one with columns `Date | Iteration | Author | Delta`.
11) Update the history table at the bottom by appending exactly one row for this iteration.
12) Keep the document append-only; never overwrite prior iteration content.
13) Preserve repository/file-system references when refining implementation details.
14) Write the SessionId at file bottom if not already present; use the same resume SessionId used at agent startup.

## Output Template

### Iteration N
- Summary: {What changed from previous iteration}
- Requirements Snapshot:
  - {Requirement}
  - {Requirement}
- Detailed Plan:
  1) {Detailed implementation step}
  2) {Detailed implementation step}
  3) {Detailed implementation step}
- Open Items:
  - [MISSING {what is missing}]
  - [DECISION {options/decision needed}]
- Verification Test Cases (required when implementation-ready; count is flexible, examples below):
  1) Given {actual/current state}, when {implementation steps are applied}, then {desired state outcome is observed}.
  2) Given {actual/current state}, when {migration/transition action runs}, then {data/system behavior matches desired state}.
  3) Given {failure/edge condition from actual state}, when {transition is attempted}, then {safe/expected desired-state handling occurs}.

## History Table Row
| {YYYY-MM-DD} | {N} | Copilot | {Concise delta summary for this iteration} |
