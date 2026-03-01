---
name: RefinePlan
description: Iteratively convert requirements into a detailed implementation plan with explicit [MISSING ...] and [DECISION ...] markers. USE WHEN the user asks to refine requirements OR create an implementation plan iteratively OR asks to iterate/refine an existing plan and maintain iteration history.
---

# RefinePlan

Iteratively refine requirements into a detailed, actionable implementation plan, append a new iteration, and maintain the history table at the bottom.

## Workflow Routing
| Workflow | Trigger | File |
|----------|---------|------|
| **RefinePlan** | "refine requirements" OR "iterative plan" OR "detailed implementation plan" OR "refine the plan" | `workflows/RefinePlan.md` |

## Rules
- Keep plan files append-only by iteration (`# Iteration N`).
- Create exactly one new iteration per refine request.
- Keep explicit `[MISSING ...]` and `[DECISION ...]` markers when unresolved.
- `[MISSING ...]` and `[DECISION ...]` items may remain when explicitly marked as non-blocking.
- A plan is implementation-ready when no blocking unresolved items remain.
- If the plan is implementation-ready in the latest iteration, automatically include concrete verification test cases in that same iteration.
- Test cases must verify the transition from the current/actual state to the planned desired state defined in the plan.
- Maintain bottom history table with fixed columns: `Date | Iteration | Author | Delta`.
- If no history table exists yet, create it with the fixed columns before appending the current iteration row.
- Do not generate retro sections here; retros are handled by `RetroPlan`.

## Examples

**Example 1: Refine a new requirement set**
```
User: "Refine these requirements into a detailed implementation plan"
→ Invokes RefinePlan workflow
→ Adds Iteration N with detailed steps and open items
```

**Example 2: Continue an existing plan**
```
User: "I marked my answers with =>. refine the plan"
→ Invokes RefinePlan workflow
→ Adds Iteration N+1 and updates history table
```
