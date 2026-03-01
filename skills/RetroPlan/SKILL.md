---
name: RetroPlan
description: Review implementation results against the plan, evaluate plan quality, and feed actionable deltas into future plan definitions (including skill/prompt updates). USE WHEN the user asks to retro the plan, review what worked, capture bugs/refactorings, improve planning quality, or run a final retro.
---

# RetroPlan

Run interim or final retrospectives for an implementation plan and convert findings into actionable follow-up deltas.

## Workflow Routing
| Workflow | Trigger | File |
|----------|---------|------|
| **RetroPlan** | "retro the plan" OR "retro plan" OR "retro the plan finally" OR "final retro the plan" | `workflows/RetroPlan.md` |

## Rules
- Keep retro format: What worked well / What needs improvement / Next refine adjustments.
- Interim retro may run multiple times during feature development.
- Final retro aggregates insights from all prior retros and overall plan quality.
- Capture bugs/refactorings as concrete follow-up deltas and ensure they are reflected in plan history.
- Explicitly assess plan quality as: Good / Partially Good / Poor, with reasons.
- Identify root causes of planning gaps (for example: missing constraints, ambiguous acceptance criteria, sequencing gaps, missing verification).
- When gaps are found, produce concrete updates for future planning instructions (skill/workflow wording and prompt guidance), not only implementation follow-ups.
- Each retro must include at least one concrete planning-improvement delta when any planning weakness is identified.

## Examples

**Example 1: Interim retro**
```
User: "retro the plan"
→ Invokes RetroPlan workflow
→ Produces retro and actionable follow-up deltas
```

**Example 2: Final retro**
```
User: "final retro the plan"
→ Invokes RetroPlan workflow
→ Produces aggregate final retro across prior retros and implementation outcome
```
