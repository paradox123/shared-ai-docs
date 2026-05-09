**Date:** 2026-05-09
**Status:** 🟢 Accepted
**Scope:** Reduced .NET 10 convenience wrapper for Agent Delivery workflow tooling.
**SessionId:** workflow-tooling-workflow-doctor-hardening

---

## Review Control Surface

- Spec-Variante: Tool delivery spec, reduced first implementation.
- Goldstandard Status: hardened for Slice A only.
- Ziel: Create `skills-repo/tools/WorkflowDoctor.cs` as a thin convenience wrapper over accepted Agent Delivery workflow tools.
- In Scope: phase `post-orchestration`, aggregated JSON report, human summary, stable wrapper exit codes, transparent forwarding of the accepted `EvaluateOrchestrationNextStep.cs` result.
- Out of Scope: new workflow policy, validation rules that belong in specialized tools, `pre-delivery`, handoff sync, agent launches, skill integration, mutation of repo files, replacement of specialized tools.
- Wichtigste Test-/Harness-Cases: `DOCTOR-POST-ORCHESTRATION-EVALUATE-PASS`, `DOCTOR-POST-ORCHESTRATION-REQUIRED-NEXT-STEP`, `DOCTOR-POST-ORCHESTRATION-MISSING-PACK`, `DOCTOR-INVALID-ARGS`, `DOCTOR-MISSING-UNDERLYING-TOOL`.
- Wichtigste Verification Commands: `dotnet run skills-repo/tools/WorkflowDoctor.cs -- --help`; post-orchestration fixture runs against existing `EvaluateOrchestrationNextStep.cs` fixtures; `openspec validate agent-delivery-workflow-doctor --strict`; `git diff --check`.
- Offene Entscheidungen: full orchestration pack validation waits for accepted `ValidateOrchestrationPack.cs`; handoff generation/sync waits for accepted `SyncChildHandoff.cs`; pre-delivery doctor phase remains out of Slice A.
- Readiness Status: ACCEPTED for the reduced implemented Slice A only; NOT READY for the broader wrapper.

## Goal

Give agents one low-token command for the first post-orchestration workflow check while keeping actual workflow rules in focused tools.

The Slice A doctor is a convenience wrapper. It MUST NOT decide workflow policy itself. It runs accepted specialized tools, captures their exit codes and output, emits one aggregate report, and returns a stable wrapper exit code.

## Dependency Gate

### Accepted and Locally Available

- `skills-repo/tools/EvaluateOrchestrationNextStep.cs`
  - accepted via archived OpenSpec change `2026-05-09-agent-delivery-evaluate-orchestration-next-step`;
  - local evidence says `.NET 10.0.203` and fixture runs passed;
  - usable for `post-orchestration` next-step evaluation.

### Not Accepted / Not Locally Implemented

- `skills-repo/tools/ValidateOrchestrationPack.cs`
  - only draft spec exists;
  - MUST NOT be invoked or simulated in Slice A.
- `skills-repo/tools/SyncChildHandoff.cs`
  - only draft spec exists;
  - MUST NOT be invoked or simulated in Slice A.

### Existing But Out Of Slice A

- `skills-repo/tools/ValidateChildReadiness.cs`
- `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`

These tools are local, but wiring them into a `pre-delivery` doctor phase would create a broader workflow surface. That waits for a later spec after the post-orchestration wrapper is accepted.

## Scope Contract

### In Scope

1. Implement `WorkflowDoctor.cs` as a .NET 10 file-based app.
2. Support exactly one phase in Slice A: `--phase post-orchestration`.
3. For `post-orchestration`, run `EvaluateOrchestrationNextStep.cs` with:
   - `--pack <path>`;
   - `--repo <path>` when provided;
   - `--child-index-section <name>` when provided;
   - `--intent <value>` when provided;
   - `--no-implementation` when provided;
   - `--format json`;
   - `--fail-on-required-next-step` only when the doctor receives `--fail-on-required-next-step`.
4. Emit an aggregate JSON report with wrapper metadata, phase, selected tool runs, tool command labels, tool exit codes, parsed JSON when available, raw stdout/stderr when parsing fails, findings, recommended next action, and final wrapper exit code.
5. Emit a human summary by default, and allow `--format json|markdown|both`.
6. Use stable wrapper exit codes:
   - `0`: selected tools ran and no selected tool reported a blocker according to the requested doctor mode;
   - `1`: selected tools ran and one or more selected tools reported workflow blockers or required next action under `--fail-on-required-next-step`;
   - `2`: invalid doctor arguments, required files missing, missing underlying tool, unsupported phase, or malformed tool output needed for aggregation.

### Out Of Scope

- No implementation of `ValidateOrchestrationPack.cs` or `SyncChildHandoff.cs`.
- No `pre-delivery` phase.
- No skill integration.
- No agent launch, queue, or session creation.
- No mutation of specs, handoffs, packs, OpenSpec files, or repo content.
- No new classification, readiness, handoff, evidence, or workflow-advancement policy inside `WorkflowDoctor.cs`.
- No hiding or rewriting findings from underlying tools.

## Behavioral Requirements

1. `WorkflowDoctor.cs` SHALL fail fast with exit `2` when an unsupported phase is requested.
2. `WorkflowDoctor.cs` SHALL fail with exit `2` when `--phase post-orchestration` is missing `--pack`.
3. `WorkflowDoctor.cs` SHALL fail with exit `2` when `EvaluateOrchestrationNextStep.cs` is not present next to the doctor in `skills-repo/tools`.
4. For Slice A, `WorkflowDoctor.cs` SHALL run only `EvaluateOrchestrationNextStep.cs`; it SHALL NOT attempt orchestration pack validation or handoff sync.
5. The aggregate JSON SHALL include one `tool_runs` item for `EvaluateOrchestrationNextStep.cs` with `tool`, `command`, `exit_code`, `stdout`, `stderr`, `parsed_json`, and `status`.
6. When the underlying tool returns valid JSON, the doctor SHALL surface `required_next_skill`, `first_unblocked_child`, `delivery_allowed`, `trigger_result`, and `final_status_token` in `recommended_next_action`.
7. The human summary SHALL identify the phase, each tool result, the recommended next action, and the final exit code.
8. The wrapper SHALL preserve direct use of specialized tools; no skill or workflow MUST call the doctor.

## Acceptance Criteria

1. `dotnet run skills-repo/tools/WorkflowDoctor.cs -- --help` exits `0` and documents Slice A scope and exit codes.
2. A post-orchestration doctor run against the accepted `md-e2e-like` fixture with `--intent expects-hardening --no-implementation --format json` exits `0`, emits valid aggregate JSON, includes exactly one `EvaluateOrchestrationNextStep.cs` tool run, and reports `required_next_skill = child-spec-hardening`.
3. The same fixture with `--fail-on-required-next-step` exits `1` and keeps the underlying parsed JSON visible in the aggregate report.
4. A missing `--pack` exits `2` and prints a human-actionable argument error.
5. An unsupported phase such as `pre-delivery` exits `2` and states that the phase is outside Slice A.
6. If `EvaluateOrchestrationNextStep.cs` is absent, the doctor exits `2` with a missing-underlying-tool finding. This may be verified by running a copied doctor from a temporary directory without the underlying tool.
7. `git diff --check` passes.
8. The OpenSpec change for this Slice A validates in strict mode.

## Verification Commands

Run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs` unless a command explicitly uses `/tmp`.

```sh
dotnet run skills-repo/tools/WorkflowDoctor.cs -- --help

dotnet run skills-repo/tools/WorkflowDoctor.cs -- \
  --phase post-orchestration \
  --pack skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/md-e2e-like/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --intent expects-hardening \
  --no-implementation \
  --format json

dotnet run skills-repo/tools/WorkflowDoctor.cs -- \
  --phase post-orchestration \
  --pack skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/md-e2e-like/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --intent expects-hardening \
  --no-implementation \
  --fail-on-required-next-step \
  --format json

dotnet run skills-repo/tools/WorkflowDoctor.cs -- --phase post-orchestration

dotnet run skills-repo/tools/WorkflowDoctor.cs -- --phase pre-delivery

tmp_doctor_dir="$(mktemp -d)"
cp skills-repo/tools/WorkflowDoctor.cs "$tmp_doctor_dir/WorkflowDoctor.cs"
dotnet run "$tmp_doctor_dir/WorkflowDoctor.cs" -- \
  --phase post-orchestration \
  --pack skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/md-e2e-like/orchestration-pack.md \
  --format json

openspec validate agent-delivery-workflow-doctor --strict
git diff --check
```

Expected status for the `--fail-on-required-next-step`, missing pack, unsupported phase, and missing-underlying-tool commands is non-zero as specified above.

## Future Dependencies

The broader Workflow Doctor remains NOT READY until these are accepted and locally implemented:

1. `ValidateOrchestrationPack.cs` for full structural orchestration pack validation before next-step evaluation.
2. `SyncChildHandoff.cs` if the doctor ever reports or checks handoff sync readiness.
3. A separate hardened spec for any `pre-delivery` phase that wires `ValidateChildReadiness.cs` and `ValidateAgentDeliveryLaunchEvidence.cs`.

## Content Quality Review Result

- Correctness/domain fit: Slice A targets the accepted post-orchestration next-step evaluator and does not pretend missing validators exist.
- Scope discipline: full pack validation, handoff sync, pre-delivery, skill integration and agent launch remain explicit non-goals.
- Completeness: normal path, required-next-step path, invalid args, unsupported phase and missing underlying tool are covered.
- Consistency: exit codes match the wrapper role and do not override underlying tool policy.
- Verifiability: all acceptance criteria have runnable local checks.
- Traceability: Slice A traces to the accepted `EvaluateOrchestrationNextStep.cs`; broader dependencies are named as blockers.

## Implementation Readiness Verdict

`READY` for reduced Slice A only. `WorkflowDoctor.cs` exists, invokes only the accepted `EvaluateOrchestrationNextStep.cs`, and all Slice A verification commands passed.

`NOT READY` for the broader Workflow Doctor that also validates orchestration packs, syncs handoffs, or supports `pre-delivery`.

## Closeout

- Closeout Status: ACCEPTED.
- OpenSpec Change: archived as `openspec/changes/archive/2026-05-09-agent-delivery-workflow-doctor/`.
- Canonical Spec: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md` now includes `Workflow Doctor post-orchestration wrapper`.
- Closeout Evidence: `openspec/changes/archive/2026-05-09-agent-delivery-workflow-doctor/closeout-evidence.md`.
- Documentation Sync: RAG `spec-closeout --scope all` and exact `rg` discovery found no separate project documentation that needed a Workflow Doctor status update. Relevant durable docs are the source spec, archived OpenSpec evidence, and canonical OpenSpec spec.
- Final Verdict: READY for reduced Slice A; broader Workflow Doctor remains NOT READY until `ValidateOrchestrationPack.cs`, `SyncChildHandoff.cs`, and a hardened `pre-delivery` phase are accepted.

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |
| 2026-05-09 | workflow-tooling-workflow-doctor-hardening | Hardened spec into reduced Slice A over accepted `EvaluateOrchestrationNextStep.cs`; blocked broader wrapper on missing specialized tools. |
| 2026-05-09 | workflow-tooling-workflow-doctor-delivery | Implemented and verified reduced Slice A `WorkflowDoctor.cs`; broader wrapper remains blocked on missing specialized tools. |
| 2026-05-09 | workflow-tooling-workflow-doctor-closeout | Accepted and archived OpenSpec change `2026-05-09-agent-delivery-workflow-doctor`; synchronized canonical spec and closeout evidence. |
