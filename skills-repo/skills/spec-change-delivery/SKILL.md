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
- **Parallel Work Control Surface**
- **Mini-Retro**

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
10. Never present a verification as completed before the command has actually run and returned.
11. Never label a local rehearsal as an environment gate-run (`develop_hetzner`, production, etc.) unless executed in that actual target runtime.
12. When a spec distinguishes legacy vs candidate endpoints, assert and report both concrete values before execution (`OLD != CANDIDATE`).
13. If required spec checks depend on missing foundational runtime prerequisites (for example missing CLI, missing service repo, missing runtime manifests), stop early and ask for a scope decision before continuing.
14. Verification commands must be shell/platform explicit enough to run on the declared target operator environment (for example macOS vs Linux) without hidden behavior differences.
15. Verification commands must fail on assertion mismatches, not on benign pre-existing state (for example copying already-existing files).
16. If a scope guard compares branch history (`origin/develop...HEAD`), the spec must either require a dedicated clean branch or define a working-tree-only fallback guard for long-lived branches.
17. Runtime smoke checks after `docker compose up` must include a deterministic readiness strategy (poll/retry/restart policy) before first HTTP assertions.
18. Before full verification execution, run a risk-based preflight only for high-failure-risk commands (runtime boot, TLS/bootstrap, branch-history guards, first endpoint smokes).
19. Preflight is preparation only: it must never be treated as a substitute for the required verification checklist.
20. Never recurse into "verification of verification". One preflight pass is allowed; then run the canonical spec verification block.
21. If command simplifications are beneficial, propose them first with rationale and trade-offs; do not silently alter the spec command contract.
22. For child-spec implementation, check parent/master conformance before editing when the parent path is known. If the child contradicts the parent or omits expected scope without re-entry, stop and route to `child-spec-hardening`.
23. If pre-implementation analysis finds a blocking content-quality flaw, stop before coding and route to `child-spec-hardening`. This includes requirements that are ambiguous, internally inconsistent, infeasible, untestable, incomplete for critical failure/edge cases, not traceable to the stated goal, or semantically broken in data/artifact/status contracts.
24. If a child spec lacks implementation-ready depth (normative contract, concrete harness/verification cases, hardened verification commands, DoR/DoD, parent conformance, and status/evidence provenance), stop before coding and route to `child-spec-hardening`.
25. If this run is one lane of parallel child-spec execution, edit only the lane's allowed write-set. Treat shared/read-only files as read-only unless this run is explicitly the integration-owner run.

## Risk-Based Verification Preflight

Use a short preflight phase before the main verification run when command fragility risk is high.

1. Select only high-risk commands for preflight.
2. Mark preflight outcomes separately (`pass`, `warn`, `fail`) from verification statuses.
3. If preflight exposes command-contract flaws, pause and propose explicit simplifications/fixes to the user before modifying commands.
4. Keep preflight bounded to one pass; do not create recursive loops.
5. After preflight, run the full spec verification block and report gate-relevant statuses (`planned`, `ran-target`, `ran-rehearsal`, `failed`, `blocked`).

## Verification Truth Contract

Use exact status language for every verification item:

- `planned`: not run yet.
- `ran-target`: executed in the required target runtime/environment.
- `ran-rehearsal`: executed only in local/simulated context.
- `failed`: executed and assertion failed.
- `blocked`: could not execute due to missing prerequisites.

Rules:

1. `READY` is only possible when all required spec checks are `ran-target`.
2. Any required check that is `ran-rehearsal`, `failed`, `blocked`, or still `planned` forces `NOT READY`.
3. If a rehearsal is still useful, keep it, but label it explicitly as rehearsal and non-gate evidence.
4. If you discover environment mismatch after earlier claims, issue an explicit status correction immediately and downgrade verdict until re-verified.

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

## Parallel Child-Spec Execution Guardrail

If the user explicitly asks to run child specs in parallel, act as an orchestrator first:

1. Create a Parallel Work Control Surface before delegating or editing:
   - child spec or work block,
   - lane mode, which is normally `implementation` for this skill,
   - owner/agent,
   - allowed write-sets,
   - shared files/read-only files for the lane,
   - dependencies,
   - required verification commands,
   - integration owner,
   - integration order.
2. Allow parallel implementation only when write-sets are disjoint and each editing lane has an isolated branch/worktree/OpenSpec change or clearly separated files.
3. Assign one integration owner for shared control files such as parent spec, slice plan, child-spec index, backlog, shared helpers, shared contracts, or common verification scripts.
4. Do not let parallel lanes change common contracts independently. If a contract, schema, helper, harness, or shared verification command must change, promote that as its own serial prerequisite slice.
5. If write-sets overlap, or if shared files, dependencies, verification commands, integration owner, or merge/sync order are unclear, recommend serial execution even when multiple child specs exist.
6. After lane completion, the integration owner performs integration review, reruns cross-slice verification, updates parent coverage/index/backlog, and reports a single final `READY` / `NOT READY` verdict.

If these conditions are not met, recommend serial execution even when multiple child specs exist.

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
   - Run a foundational runtime reality gate before substantial edits:
     - verify required CLI/tools exist,
     - verify required implementation repo/services exist,
     - verify required runtime artifacts exist when runtime validation is mandatory.
   - If prerequisites are missing, pause and ask the user to choose one path:
     1) extend the change to bootstrap prerequisites first, or
     2) keep this as documentation/spec-only work with explicit `NOT READY`.
   - Do not continue with implementation-like paperwork as a substitute for missing runtime unless the user explicitly chooses path (2).

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
   - If executing a parallel lane, edit only the lane's allowed write-set and do not touch shared/read-only files.
   - Prefer the smallest root-cause change that satisfies the acceptance criteria.
   - Avoid opportunistic refactors unless they are required for correctness.
   - For bug fixes, reproduce first and prefer a targeted red -> green test when practical.

5. **Verify**
   - Run targeted tests for the modified behavior first.
   - Then run broader project checks required by the spec.
   - If runtime or infrastructure is in scope, run smoke checks for the affected path.
   - Record the exact commands, exit status, runtime environment label, and meaningful output.
   - Treat the spec's `Verification` section as a hard checklist: every listed command must be attempted and reported.
   - Run risk-based preflight first when command fragility risk is high, but keep preflight reporting separate from gate verdict statuses.
   - If a check sequence is timing-sensitive (containers, proxies, startup migrations), apply the spec-defined readiness strategy before marking endpoint checks as failed.
   - If a command is blocked (missing creds/services/tools), report it explicitly as blocked and keep verdict `NOT READY`.
   - If checks involve endpoint identity (for example old vs candidate STS), log the concrete endpoint values used in each command.
   - Do not infer functional-path success from CI health/watcher success; run the functional command path explicitly when required by the spec.

6. **Report**
   - Requirements covered vs not covered.
   - Commands run with pass/fail summary.
   - Files changed.
   - Residual risks, follow-ups, or blockers.
   - Mini-Retro for larger delivery blocks or before handoff/context loss: decisions, changes, open items, missing evidence, skill/workflow friction, and whether to continue in this session or start a new one.
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
5. The request text includes multiple execution modes (for example OpenSpec and Direct) and no explicit selection is given.

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
   - include a full verification checklist with one of: `planned`, `ran-target`, `ran-rehearsal`, `failed`, `blocked` for each spec-listed command

3. **Changed artifacts**
   - files or resources touched

4. **Open risks or blockers**
   - unresolved items, assumptions, or follow-up work

5. **Mini-Retro**
   - include this when the delivery block was substantial, when context may be lost, or when handing off to `retro-plan`/`spec-closeout`
   - cover: what was decided, what changed, what remains open, which evidence/verification is missing, which skill/workflow friction appeared, and whether to continue in this session or start a new one

6. **Final verdict**
   - `READY` = the agreed change is implemented and required checks pass
   - `NOT READY` = acceptance evidence is incomplete, checks fail, or blockers remain

Never report success if acceptance evidence is incomplete.
