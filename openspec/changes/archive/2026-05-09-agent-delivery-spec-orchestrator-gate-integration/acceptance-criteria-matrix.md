# Acceptance Criteria Matrix

| AC | Requirement | Evidence | Status |
|---|---|---|---|
| AC1 | Skill requires `EvaluateOrchestrationNextStep.cs` after Child Index/Hardening Queue update. | `rg` output shows the evaluator command in `skills-repo/skills/spec-orchestrator/SKILL.md`. | pass |
| AC2 | Skill follows `required_next_skill = child-spec-hardening` and states `--no-implementation` does not block hardening. | `rg` output shows both the hardening verdict row and `--no-implementation` note. | pass |
| AC3 | Skill follows `required_next_skill = spec-change-delivery` as a gated stop unless implementation was requested and gates are valid. | `rg` output shows the gated `spec-change-delivery` verdict row. | pass |
| AC4 | Final response wording includes `final_status_token`. | `rg` output shows `final_status_token` in the Tool Gate and default output format. | pass |
| AC5 | Existing readiness, handoff and launch-evidence guardrails remain in place. | Focused diff only adds Tool Gate/output wording and a routing note; existing guardrail sections remain intact. | pass |
| AC6 | Evaluator smoke still returns JSON for a temporary Child Index pack. | Smoke command returned JSON with `required_next_skill = child-spec-hardening`, `first_unblocked_child = S1`, and `final_status_token = hardening_started_required`. | pass |
| AC7 | Patch is whitespace-clean. | `git diff --check` exited `0`. | pass |
| AC8 | OpenSpec change is structurally valid. | `openspec validate agent-delivery-spec-orchestrator-gate-integration --strict` exited `0`. | pass |
