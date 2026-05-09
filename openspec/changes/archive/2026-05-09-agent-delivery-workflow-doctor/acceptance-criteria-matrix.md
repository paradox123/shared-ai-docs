# Acceptance Criteria Matrix

| Acceptance Criterion | Evidence | Status |
|---|---|---|
| Help exits `0` and documents Slice A scope and exit codes. | `dotnet run skills-repo/tools/WorkflowDoctor.cs -- --help` | PASS |
| Post-orchestration fixture exits `0`, emits aggregate JSON, includes one evaluator run and reports `child-spec-hardening`. | Positive fixture run in `implementation-evidence.md`. | PASS |
| `--fail-on-required-next-step` exits `1` and keeps parsed JSON visible. | Required-next-step run in `implementation-evidence.md`. | PASS |
| Missing `--pack` exits `2` with actionable error. | Missing-pack run in `implementation-evidence.md`. | PASS |
| Unsupported `pre-delivery` exits `2` and states Slice A boundary. | Unsupported-phase run in `implementation-evidence.md`. | PASS |
| Missing `EvaluateOrchestrationNextStep.cs` exits `2` with missing-underlying-tool finding. | Temp-directory copied-doctor run in `implementation-evidence.md`. | PASS |
| `git diff --check` passes. | Verification table. | PASS |
| OpenSpec change validates in strict mode. | `openspec validate agent-delivery-workflow-doctor --strict`. | PASS |
