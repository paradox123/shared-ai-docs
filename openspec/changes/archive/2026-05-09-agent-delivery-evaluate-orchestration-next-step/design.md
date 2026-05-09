# Agent Delivery Evaluate Orchestration Next Step Design

## Scope Contract

In scope:

- Implement one .NET 10 file-based app at `skills-repo/tools/EvaluateOrchestrationNextStep.cs`.
- Add fixture orchestration packs under `skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/`.
- Update the source spec status/history for this implementation pass.
- Provide OpenSpec proposal, tasks, spec delta, acceptance matrix and implementation evidence.

Out of scope:

- No `spec-orchestrator/SKILL.md` integration.
- No child spec or MD-E2E artifact edits.
- No handoff generation/sync.
- No Agent Delivery Session Launcher usage.
- No runtime/product implementation.

Acceptance targets:

- The MD-E2E-like fixture routes to `child-spec-hardening` for `MD-E2E-1`, even when `--no-implementation` is passed.
- The same fixture can be explicitly treated as orchestration-only.
- The tool emits valid JSON with the expected schema and enumerated values.
- Help and spec verification commands pass from `/tmp`.

Planned verification:

- `dotnet --version`
- `dotnet run ...EvaluateOrchestrationNextStep.cs -- --help`
- MD-E2E-like hardening command from the spec.
- MD-E2E-like orchestration-only command from the spec.
- `openspec validate agent-delivery-evaluate-orchestration-next-step --strict`
- `git diff --check`

## Implementation Strategy

The tool uses the same zero-project file-based app style as the existing Agent Delivery tools. Markdown parsing stays intentionally simple and scoped to pipe tables with the exact operational Child Index columns used by `ValidateChildReadiness.cs`.

Dependency classification is conservative:

- Rows with `DEFERRED` or "Do not start" become `deferred`.
- Implementation-ready rows become `ready_for_delivery`, but `--no-implementation` prevents `spec-change-delivery`.
- Rows with unresolved child id dependencies become `blocked_by_dependency`.
- The first unblocked `NEEDS HARDENING` row becomes `harden_now`.
- Rows that explicitly mention partial/draft parallel work become `parallel_draft_only`.

## Trade-offs

The dependency parser is heuristic because existing Child Index rows use prose in the Dependencies cell. The tool therefore returns reasons and warnings rather than silently treating ambiguous prose as accepted evidence.

