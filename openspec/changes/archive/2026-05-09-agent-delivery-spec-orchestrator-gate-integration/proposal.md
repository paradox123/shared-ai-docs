# Agent Delivery Spec Orchestrator Gate Integration

## Why

`spec-orchestrator` still carries detailed post-orchestration transition prose even though `EvaluateOrchestrationNextStep.cs` now provides the deterministic gate. The skill should create or update the Child Index/Hardening Queue, run the tool, and follow the verdict so queue creation is not confused with workflow advancement.

## What

- Add a terse Tool Gate section to `skills-repo/skills/spec-orchestrator/SKILL.md`.
- Require the evaluator after Child Index and Hardening Queue creation/update.
- Route `required_next_skill` results by following the tool verdict.
- Preserve existing Child Index, handoff, launch-evidence, readiness and implementation guardrails.
- Keep the change limited to skill instructions and OpenSpec/evidence artifacts.

## Impact

- Reduces duplicated skill prose for the post-orchestration next step.
- Makes final orchestration wording include the evaluator's `final_status_token`.
- Keeps runtime/product implementation and evaluator-tool changes out of scope.
