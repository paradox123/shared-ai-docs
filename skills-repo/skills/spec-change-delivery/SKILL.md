---
name: spec-change-delivery
description: Execute one bounded change from a spec or requirements document with strict scope control, optional OpenSpec usage, deterministic verification, and handoff-ready evidence. Use whenever the user asks to implement one spec item, ship one change change, apply a planned task, deliver a single requirement safely, or avoid scope creep and partial implementations. Works with or without OpenSpec.
---

# spec-change-delivery

## Use This Skill When

Use this skill when the user wants **execution**, not more planning:
- "implement this spec item"
- "ship just this one change"
- "apply the next planned task"
- "do one safe change only"
- "avoid scope creep"

Do **not** use this skill to write or refine the whole spec from scratch. For that, prefer `doc-coauthoring` or `refine-plan`.

## Core Promise

Deliver exactly one bounded change from requirements to verified implementation.
Prioritize predictability: explicit scope, clear gates, runnable checks, and a final `READY` / `NOT READY` verdict.

## Workflow Compatibility

This skill is the primary delivery path for **Workflow 2 (current)**:
- `spec -> spec-change-delivery -> (optional retro) -> (optional spec-closeout)`

**Workflow 1 (legacy-compatible)** can continue without this skill:
- `spec -> refine-plan (iterative) -> direct-mode implementation -> (optional retro)`

Do not force migration from Workflow 1 to Workflow 2 unless the user explicitly asks to switch.

## Shared Delivery Gates

Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` as the canonical source for:
- **Definition of Ready (DoR)**
- **Definition of Done (DoD)**
- **Decision Freeze Pack**

This skill keeps short local definitions for convenience, but execution and the final `READY` / `NOT READY` verdict must stay aligned with the shared workflow document.

## Key Terms

- **Change**: the smallest self-contained increment that can be implemented and verified with one concrete done signal.
- **Scope contract**: a short agreement listing in scope, out of scope, acceptance targets, and planned verification before editing starts.
- **DoR (Definition of Ready)**: what must be true before implementation begins. See the shared workflow doc for the full gate.
- **DoD (Definition of Done)**: what evidence must exist before the change can be marked complete. See the shared workflow doc for the full gate.
- **OpenSpec mode**: use the repo's OpenSpec workflow for proposal/tasks/spec deltas when the user asks for it or the repo already uses it.
- **Direct mode**: implement directly from the stated scope contract without creating a new OpenSpec change.

## Required Inputs

1. Target repository path.
2. One target spec/requirements artifact, or one clearly defined change request.
3. Execution mode: `openspec` or `direct`.
   - Default to `direct` unless the user explicitly wants OpenSpec or the repo already depends on it.
4. Verification commands or checks.
   - Use commands from the spec when present; otherwise derive the smallest safe set that proves the acceptance criteria.

## If Inputs Are Missing

Before editing, make sure the minimum contract exists.
Ask the user if any of these are missing or ambiguous:
- which repo/path to change,
- which single requirement is in scope,
- what outcome counts as success,
- what environment or credentials are required.

If verification commands are missing, derive them explicitly and say what you chose.

## Non-Negotiables

1. One change per run.
Do not blend multiple independent changes in one pass.
2. Scope is explicit before editing.
3. Baseline, migration, and cutover are optional patterns, not defaults.
Only include them when the spec explicitly requires them.
4. Do not silently descope acceptance criteria.
5. Do not claim done without fresh verification evidence.
6. Preserve behavior outside the change unless the spec requires a change.
7. If the spec provides explicit verification commands, execute all of them before final close-out.
8. Never silently skip verification commands from the spec.
9. If any required verification command cannot be run or fails, final verdict MUST be `NOT READY`.

## Spec Status, History, SessionId

When this skill is used with a spec artifact, update the spec metadata as work progresses:

1. Set status to `🟠 Plan` when the scope contract is locked (direct or OpenSpec mode).
2. Set status to `🔵 Implemented` only after implementation artifacts exist and required execution evidence is captured.
3. Preserve `Date` and `Scope` lines unless the user explicitly requests a scope/date correction.
4. Append one history row per status transition using `| Date | Author | Change |` with a short sentence.
5. Keep `SessionId` unchanged if present; add `SessionId: <session-id>` if missing.

## Scope Pressure Guardrail

When the requested scope is too large for one verifiable increment:
1. Flag the risk explicitly.
2. Propose 2-5 smaller changes.
3. For each change provide:
   - goal,
   - dependency boundary,
   - concrete done signal.
4. Recommend an execution order.
5. Implement only one change in the current run unless the user explicitly widens scope.

## Kickoff Contract

At the start of execution, normalize the request into this short contract:
- **In scope**
- **Out of scope**
- **Acceptance targets**
- **Planned verification**
- **Open risks / assumptions**

This prevents drift and creates a clean handoff record.

## Example Kickoff

If the user says, "Implement the retry-timeout requirement from the plan, nothing else," the kickoff should look like:
- **In scope**: retry/timeout behavior for the affected call path
- **Out of scope**: unrelated refactors, observability expansion, broader cleanup
- **Acceptance targets**: timeout is configurable, retry path works as specified
- **Planned verification**: targeted test(s) plus one affected-path smoke check

## Delivery Workflow

1. **Read and normalize scope**
   - Extract: in scope, out of scope, requirements, test cases, acceptance criteria, dependencies, decisions, open items.
   - Convert test cases into **DoR -> DoD** checkpoints.

2. **Build the execution contract**
   - Map each `requirement -> implementation task`.
   - Map each `acceptance criterion -> executable check`.
   - Capture risks for unresolved or environment-dependent points.
   - After this contract is fixed, update spec status to `🟠 Plan` and append a matching history row.

3. **Choose execution mode**
   - **`openspec` mode**
     - Create or update exactly one OpenSpec change for the change.
     - Keep proposal, tasks, and spec deltas aligned with the scope contract.
     - Implement only after tasks and acceptance mapping are clear.
   - **`direct` mode**
     - Implement directly from the scope contract.
     - Hold to the same verification and evidence standard.

4. **Implement**
   - Edit only the files needed for the current change.
   - Prefer the smallest root-cause change that satisfies the acceptance criteria.
   - Avoid opportunistic refactors unless they are required for correctness.
   - For bug fixes, reproduce first and prefer a targeted red -> green test when practical.

5. **Verify**
   - Run targeted tests for the modified behavior first.
   - Then run broader project checks required by the spec.
   - If runtime or infrastructure is in scope, run smoke checks for the affected path.
   - Record the exact commands, exit status, and meaningful output.
   - Treat the spec's `Verification` section as a hard checklist: every listed command must be attempted and reported.
   - If a command is blocked (missing creds/services/tools), report it explicitly as blocked and keep verdict `NOT READY`.

6. **Report**
   - Requirements covered vs not covered.
   - Commands run with pass/fail summary.
   - Files changed.
   - Residual risks, follow-ups, or blockers.
   - If implementation was completed with evidence, update spec status to `🔵 Implemented` and append a matching history row.
   - Final verdict: `READY` or `NOT READY`.

## Post-Acceptance Handover

If the user accepts the implemented change and asks to finalize statuses/docs:
1. Switch to `spec-closeout`.
2. Re-run or confirm all spec-listed verification commands as a full checklist.
3. Close/archive OpenSpec when possible.
4. Sync spec status and project documentation before final completion messaging.

## Stop-and-Ask Rules

Pause and ask the user before proceeding when:
1. Requirements conflict and materially change behavior.
2. Security, data, or production risk requires a policy choice.
3. Essential credentials, services, or environment prerequisites are missing.
4. Multiple non-equivalent fixes are possible with different tradeoffs.

Otherwise, make the safest reasonable assumption and state it in the report.

## Blocked Path

If you cannot finish the change, still produce a useful close-out:
1. What was attempted.
2. What evidence was gathered.
3. Exact blocker or missing dependency.
4. Smallest next step to unblock.
5. Final verdict: `NOT READY`.

## Output Contract

Use this close-out structure:

1. **Scope implemented**
   - and explicitly what was not implemented

2. **Evidence**
   - requirement / testcase / acceptance coverage summary
   - verification commands and results
   - include a full verification checklist: `ran`, `failed`, or `blocked` for each spec-listed command

3. **Changed artifacts**
   - files or resources touched

4. **Open risks or blockers**
   - unresolved items, assumptions, or follow-up work

5. **Final verdict**
   - `READY` = the agreed change is implemented and required checks pass
   - `NOT READY` = acceptance evidence is incomplete, checks fail, or blockers remain

Never report success if acceptance evidence is incomplete.
