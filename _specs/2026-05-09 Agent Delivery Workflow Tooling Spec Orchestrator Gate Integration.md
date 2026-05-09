**Date:** 2026-05-09
**Status:** 🟡 Spec
**Scope:** Integrate post-orchestration next-step tooling into the `spec-orchestrator` skill with minimal prose.

---

## Review Control Surface

- Spec-Variante: Workflow/skill integration spec.
- Goldstandard Status: first draft.
- Ziel: Reduce `spec-orchestrator/SKILL.md` prose by delegating the post-orchestration transition decision to `EvaluateOrchestrationNextStep.cs`.
- In Scope: skill instructions for when to run the tool, how to interpret JSON verdicts, how to report final status tokens, and how to stop before delivery.
- Out of Scope: building the evaluator tool, changing child specs, broad skill rewrite, changing `child-spec-hardening`, launching agents.
- Wichtigste Test-/Harness-Cases: `ORCH-SKILL-RUNS-EVALUATOR`, `ORCH-SKILL-FOLLOWS-HARDENING-VERDICT`, `ORCH-SKILL-NO-IMPLEMENTATION-STILL-HARDENS`, `ORCH-SKILL-FINAL-WORDING`.
- Wichtigste Verification Commands: `rg` for evaluator invocation and status tokens in `skills-repo/skills/spec-orchestrator/SKILL.md`; `git diff --check`.
- Offene Entscheidungen: Depends on accepted CLI from `EvaluateOrchestrationNextStep.cs`.
- Readiness Status: DRAFT; harden after the evaluator tool spec is implemented or accepted.

## Goal

Make the orchestrator skill smaller and less interpretive. The skill should create/update orchestration artifacts, run the evaluator tool, and follow the tool verdict instead of restating every transition rule in prose.

## In Scope

- Add a short "Tool Gate" section to `spec-orchestrator/SKILL.md`.
- Replace detailed hardening trigger prose with a command invocation and output interpretation table.
- Require final answers to include the evaluator's `final_status_token`.
- State that `--no-implementation` must be passed when the user forbids implementation.

## Out of Scope

- No runtime code implementation.
- No changes to the evaluator tool contract unless a later hardening pass finds a blocker.
- No large rewrite of unrelated orchestrator sections.

## Acceptance Criteria

1. `spec-orchestrator/SKILL.md` instructs agents to run `EvaluateOrchestrationNextStep.cs` after creating/updating a Child Index and Hardening Queue.
2. The skill maps `required_next_skill = child-spec-hardening` to actually starting child hardening unless the user explicitly stopped before hardening.
3. The skill maps `required_next_skill = spec-change-delivery` to a stop unless the user requested implementation and readiness gates are valid.
4. The final response must distinguish queue creation from workflow advancement using the tool's status token.
5. The patch removes or shortens duplicated prose when the tool covers the rule.

## Verification Commands

```sh
rg -n "EvaluateOrchestrationNextStep|final_status_token|required_next_skill|--no-implementation" skills-repo/skills/spec-orchestrator/SKILL.md
git diff --check
```

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |

