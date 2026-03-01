# RetroPlan

## Goal
Compare implementation results against the current plan, evaluate plan quality, and produce interim or final retro outputs with actionable follow-ups for both implementation and future plan-definition quality.

## Modes
- Interim mode: `retro the plan`
- Final mode: `retro the plan finally` or `final retro the plan`

## Steps
1) Read the latest implementation-plan iterations and prior retro entries (if present).
2) Compare planned behavior against actual implemented state in the current session.
3) Evaluate plan quality as `Good`, `Partially Good`, or `Poor`, and capture the reasons.
4) Identify planning root causes behind misses/gaps (for example: ambiguity, missing constraints, sequencing, risk/test coverage).
5) Produce retro output in fixed format:
   - What worked well
   - What needs improvement
   - Next refine adjustments
6) Identify concrete bugs/refactorings and express them as actionable follow-up deltas.
7) Produce explicit `Prompt/Skill Update Deltas` so future plan generation improves.
8) Ensure follow-ups are written back into the implementation plan process (new iteration/history update on next refine).
9) In final mode, aggregate all retro findings into a closing evaluation.
10) Put the Copilot SessionId, at file bottom if not already there

## Output Format
- Plan quality assessment:
  - Verdict: {Good | Partially Good | Poor}
  - Rationale: {1-3 bullets}
- Planning root causes:
  - {Root cause}
- What worked well:
  - {1-3 bullets}
- What needs improvement:
  - {1-3 bullets}
- Next refine adjustments:
  - {1-3 bullets}
- Follow-up deltas (bugs/refactorings):
  - {Actionable item}
- Prompt/Skill update deltas (for future usage):
  - {Specific wording/process change to skills, workflows, or prompt templates}
