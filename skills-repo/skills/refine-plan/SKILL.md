---
name: refine-plan
description: Iteratively translate a finished or nearly-finished spec/requirements set into a detailed, status-bearing implementation plan with explicit [MISSING ...] and [DECISION ...] markers. USE WHEN the user asks to create or refine an implementation plan, break a spec into concrete actions, refine requirements into implementation steps, assess what is already done versus still pending, or maintain iterative plan history.
---

# refine-plan

Iteratively translate requirements into a detailed, actionable implementation plan with explicit action status, append a new iteration, and maintain the history table at the bottom.

**Input:** Prefer a finished spec document (from `doc-coauthoring`) as the starting point. It can also accept raw requirements directly from the user, but the output must still separate requirement gaps from implementation actions.

## Spec vs Plan Boundary

This skill owns the **plan/execution layer** of the pipeline.

- The **spec** owns requirements, scope, behavior, rationale, constraints, and acceptance criteria.
- The **plan** owns execution steps, sequencing, dependencies, progress visibility, and verification strategy.

If planning reveals a missing requirement or unresolved product/scope decision, surface it explicitly as `[MISSING SPEC ...]` or `[DECISION SPEC ...]` in `Open Items` and tell the user it belongs back in the spec. Do not silently invent a requirement just to keep the plan moving.

Only translate:
- resolved requirements
- current-state observations
- explicit non-blocking assumptions

into implementation actions.

## Shared Delivery Gates

Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` as the canonical source for the shared delivery gates and terminology:
- **Definition of Ready (DoR)**
- **Definition of Done (DoD)**
- **Decision Freeze Pack**

This skill operationalizes those gates:
- turn the spec into an execution plan that can satisfy **DoR** before implementation starts,
- translate acceptance criteria into verification cases that later prove **DoD**,
- keep blocking gaps visible instead of hiding them in vague tasks.

## Scope Pressure Guardrail

This skill must proactively warn when the plan scope is too large for one executable plan increment.

Treat scope as "too large" when one or more signals are present:
- The plan contains many loosely coupled streams that could progress independently.
- The plan depends on multiple external blockers before core execution can start.
- The plan mixes foundational platform work, feature behavior, migration, and rollout in one undivided sequence.
- Verification is only possible at the very end instead of per change.
- The latest iteration cannot provide a realistic next executable tranche.

When scope pressure is detected:
1. Explicitly flag that the plan is oversized.
2. Propose 2-5 concrete split changes with:
   - goal,
   - dependency boundary,
   - done signal / verification.
3. Recommend a default execution order.
4. Mark cross-change dependencies explicitly instead of hiding them in one long task list.

If the user decides to keep a single plan, keep working but add a visible marker:
- `[REVIEW Scope risk accepted: <reason>]`

## CORE Response Format Compatibility

The optional `CORE` response wrapper (`📋 SUMMARY`, `🔍 ANALYSIS`, `⚡ ACTIONS`, `✅ RESULTS`, `➡️ NEXT`, `🎯 COMPLETED`) can be used for brief conversational framing before or after plan updates.

Do **not** replace the actual plan structure with the CORE wrapper. The generated plan artifact must keep iteration sections, action statuses, open items, verification cases, and history rows in the plan-native format.

## Workflow Routing
| Workflow | Trigger | File |
|----------|---------|------|
| **refine-plan** | "turn this spec into a plan" OR "iterative plan" OR "detailed implementation plan" OR "refine the plan" OR "what is already done vs pending" | `workflows/refine-plan.md` |

## Rules
- Keep plan files append-only by iteration (`# Iteration N`).
- Create exactly one new iteration per refine request.
- Every action item in the latest iteration must carry an explicit status: `[DONE]`, `[PENDING]`, or `[BLOCKED]`.
- Each action item should make progress legible by naming evidence of current state or an observable completion signal.
- Keep explicit `[MISSING ...]` and `[DECISION ...]` markers when unresolved.
- Prefix markers with `SPEC` when the unresolved item belongs to the requirements/spec layer rather than execution planning.
- `[MISSING ...]` and `[DECISION ...]` items may remain when explicitly marked as non-blocking.
- A plan is implementation-ready when no blocking unresolved spec/decision items remain and the next executable actions are clear.
- If the plan is implementation-ready in the latest iteration, automatically include concrete verification test cases in that same iteration.
- Test cases must verify the transition from the current/actual state to the planned desired state defined in the plan.
- Keep already-satisfied requirements visible as `[DONE]` actions instead of omitting them; the reader should be able to see what is already complete.
- Do not rewrite unresolved product/scope questions as implementation tasks. Route them back to the spec.
- Run a scope-pressure check each refine pass; if oversized, propose a split before declaring implementation-readiness.
- Do not mark a plan implementation-ready if the next executable tranche is not clearly bounded and verifiable.
- Maintain bottom history table with fixed columns: `Date | Iteration | Author | Delta`.
- If no history table exists yet, create it with the fixed columns before appending the current iteration row.
- Do not generate retro sections here; retros are handled by `retro-plan`.

## Examples

**Example 1: Refine a new requirement set**
```
User: "Turn this spec into a detailed implementation plan"
→ Invokes refine-plan workflow
→ Adds Iteration N with status-bearing actions and open items
```

**Example 2: Continue an existing plan**
```
User: "I marked my answers with =>. refine the plan"
→ Invokes refine-plan workflow
→ Adds Iteration N+1 and updates history table
```

**Example 3: Assess progress**
```
User: "Break this spec into actions and show what is already done"
→ Invokes refine-plan workflow
→ Emits [DONE], [PENDING], and [BLOCKED] actions tied to current state
```
