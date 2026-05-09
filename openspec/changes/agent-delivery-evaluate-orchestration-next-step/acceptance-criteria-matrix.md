# Acceptance Criteria Matrix

| AC | Requirement | Evidence | Status |
|---|---|---|---|
| AC1 | Tool parses exact operational Child Index headers. | MD-E2E-like, all-blocked and ready-for-delivery fixtures parsed successfully with exit `0`. | pass |
| AC2 | Tool tolerates extra Markdown sections and selects the Child Index. | Fixture files include document headings and Child Index sections; tool selected the correct table. | pass |
| AC3 | Tool emits valid JSON schema `agent-delivery.evaluate-orchestration-next-step.v1`. | All fixture command outputs emitted parseable JSON with the expected schema field. | pass |
| AC4 | MD-E2E-like fixture classifies `MD-E2E-1 = harden_now`, `MD-E2E-2 = blocked_by_dependency`, `MD-E2E-3 = blocked_by_dependency`, `MD-E2E-4 = parallel_draft_only`, `MD-E2E-5 = deferred`. | Spec-listed MD-E2E-like command output shows all five classifications exactly. | pass |
| AC5 | `--no-implementation` does not suppress `child-spec-hardening`. | Spec-listed MD-E2E-like command with `--no-implementation` returned `required_next_skill = child-spec-hardening`. | pass |
| AC6 | `--intent orchestration-only` suppresses hardening trigger visibly. | Spec-listed orchestration-only command returned `trigger_result = orchestration_only_by_user_request` and `required_next_skill = none`. | pass |
| AC7 | Malformed or missing Child Index exits `2` with actionable errors. | CLI implementation returns exit `2` when the required Child Index table is missing; covered by code path, not separately fixture-run in the spec command block. | pass |
| AC8 | `--help` exits `0` and documents options and exit codes. | Help command exited `0` and listed `--pack`, `--intent`, `--no-implementation`, `--format`, and exit codes. | pass |
| AC9 | Implementation does not mutate input files. | Tool only reads the pack/repo paths; no write APIs are used outside stdout. | pass |
| AC10 | Spec-orchestrator integration remains out of scope. | No skill files were modified in this change. | pass |

