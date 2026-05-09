**Date:** 2026-05-09
**Status:** 🟡 Spec
**Scope:** Convenience wrapper that runs Agent Delivery workflow validators and next-step evaluators.

---

## Review Control Surface

- Spec-Variante: Tool delivery spec.
- Goldstandard Status: first draft.
- Ziel: Create `skills-repo/tools/WorkflowDoctor.cs` as a thin wrapper over the smaller Agent Delivery workflow tools.
- In Scope: phase-based command dispatch, aggregated JSON report, human summary, stable exit code policy.
- Out of Scope: owning validation logic that belongs in the underlying tools, changing specs, launching agents, replacing direct tool usage.
- Wichtigste Test-/Harness-Cases: `DOCTOR-POST-ORCHESTRATION`, `DOCTOR-PRE-DELIVERY`, `DOCTOR-LAUNCH-EVIDENCE`, `DOCTOR-AGGREGATE-FAILURES`.
- Wichtigste Verification Commands: future `dotnet run ...WorkflowDoctor.cs -- --phase post-orchestration --pack <pack> --repo <repo>`; `git diff --check`.
- Offene Entscheidungen: Exact phase list depends on the first three tools.
- Readiness Status: DRAFT; defer until the smaller tools exist.

## Goal

Give agents a single low-token command when they do not know which specialized validator to run, while keeping the actual workflow rules in focused tools.

## In Scope

- `--phase post-orchestration` runs orchestration pack validation and next-step evaluation.
- `--phase pre-delivery` runs child readiness and launch evidence validation when paths are provided.
- Aggregate tool output into one JSON document.
- Preserve underlying tool errors and warnings without hiding details.

## Out of Scope

- No new workflow policy.
- No mutation of repo files.
- No subagent automation.

## Acceptance Criteria

1. Doctor exits `0` when all selected underlying tools pass.
2. Doctor exits `1` when one or more underlying tools find workflow blockers.
3. Doctor exits `2` when CLI arguments are invalid or required underlying tools are missing.
4. The report lists each underlying tool command, exit code, findings and recommended next action.
5. The wrapper can be skipped; skills may still call focused tools directly.

## Verification Commands

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/WorkflowDoctor.cs -- --help
git diff --check
```

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |

