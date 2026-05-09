**Date:** 2026-05-09
**Status:** 🔵 Implemented
**Scope:** .NET 10 tool that deterministically selects the next Agent Delivery workflow step after spec orchestration.
**SessionId:** workflow-tooling-evaluate-next-step-delivery

---

## Review Control Surface

- Spec-Variante: Tool delivery spec for Agent Delivery workflow automation.
- Goldstandard Status: hardened draft, ready for direct implementation via `spec-change-delivery`.
- Ziel: Create `skills-repo/tools/EvaluateOrchestrationNextStep.cs`, a .NET 10 file-based app that reads an orchestration pack/Child Index and emits the required next workflow step, first unblocked child, lane classification, and stop-before-delivery decision.
- In Scope: CLI contract, markdown Child Index parsing, hardening lane classification, user-intent flags, JSON output contract, Markdown summary output, deterministic exit codes, fixture-based tests, docs snippet for skill usage.
- Out of Scope: editing child specs, generating handoffs, launching agents, running `child-spec-hardening`, implementing runtime/product features, replacing `ValidateChildReadiness.cs`.
- Wichtigste Test-/Harness-Cases: `ORCH-NEXT-HARDEN-NOW`, `ORCH-NEXT-NO-IMPLEMENTATION-STILL-HARDENS`, `ORCH-NEXT-ORCHESTRATION-ONLY`, `ORCH-NEXT-ALL-BLOCKED`, `ORCH-NEXT-PARALLEL-DRAFT-ONLY`.
- Wichtigste Verification Commands: from `/tmp`, `dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- --help`; fixture runs under `skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/`; `git diff --check`.
- Offene Entscheidungen: None blocking. Default output is JSON plus optional Markdown; future integration into `spec-orchestrator/SKILL.md` is a separate spec.
- Readiness Status: READY FOR DIRECT IMPLEMENTATION PLANNING. Command contract rehearsal for the new file waits until the file exists; .NET 10 availability was checked on 2026-05-09 with `dotnet --version == 10.0.203`.

## Session Briefing

- Modus/Skill: `doc-coauthoring`.
- Source of Truth: this spec; existing tools `ValidateChildReadiness.cs`, `AgentDeliverySessionLauncher.cs`, `ValidateAgentDeliveryLaunchEvidence.cs`; current Agent Delivery orchestration artifacts.
- Ziel: Move the fragile post-orchestration decision out of long skill prose and into a deterministic local tool.
- Nicht-Ziele: No broad skill rewrite and no runtime feature implementation.
- In Scope: one tool with fixtures and clear contracts.
- Erwarteter Output: implementation-ready spec for one direct delivery session.
- Verification/Review: local .NET file-based app checks and fixture assertions.
- Offene Entscheidungen: none blocking.

## Problem

The Agent Delivery workflow currently relies on prose to decide what happens after `spec-orchestrator` creates a Child Index and Hardening Queue. The recent MD-E2E orchestration showed the failure mode: a queue and handoffs existed, `MD-E2E-1` was explicitly the first hardening target, but the workflow stopped as if "no implementation" also meant "no hardening".

This tool makes that transition machine-readable. The agent should not infer the next phase from a long paragraph when a local tool can produce a concrete verdict.

## Goal

Implement `EvaluateOrchestrationNextStep.cs` as a .NET 10 file-based application that:

1. reads a Markdown orchestration pack containing a Child Index,
2. optionally reads child handoff files referenced by the index,
3. classifies every child into a hardening lane,
4. identifies the first unblocked child,
5. decides whether the next required skill is `child-spec-hardening`, `spec-change-delivery`, `spec-orchestrator`, or no immediate action,
6. distinguishes "no implementation" from "no hardening",
7. emits stable JSON for other tools and a compact Markdown summary for humans.

## Non-Goals

- Do not generate or mutate specs.
- Do not start subagents or launch Codex sessions.
- Do not validate implementation readiness; delegate that to `ValidateChildReadiness.cs`.
- Do not parse arbitrary natural language chat history. The caller must pass explicit intent flags.
- Do not become a broad workflow doctor. That is a later wrapper spec.

## CLI Contract

Primary command:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- \
  --pack /absolute/path/to/orchestration-pack.md \
  --repo /absolute/path/to/repo \
  --intent expects-hardening \
  --no-implementation
```

Options:

| Option | Required | Meaning |
|---|---:|---|
| `--pack <path>` | yes | Markdown file containing the Child Index or Hardening Queue. |
| `--repo <path>` | no | Repository root for resolving relative handoff and child spec paths. Defaults to current directory. |
| `--child-index-section <name>` | no | Section heading to prefer when multiple tables exist. Default: `Child Index`. |
| `--intent <value>` | no | One of `expects-hardening`, `expects-implementation-ready`, `hardening-queue-only`, `orchestration-only`, `stop-before-hardening`, `unknown`. Default: `unknown`. |
| `--no-implementation` | no | Explicitly means runtime/product implementation is forbidden; it must not block spec hardening. |
| `--format <json|markdown|both>` | no | Default: `json`. |
| `--fail-on-required-next-step` | no | Exit `1` when a next workflow action is required. Useful for CI-style guardrails, not default agent usage. |
| `--help` | no | Prints usage and exits `0`. |

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | Evaluation succeeded, even if the recommended workflow state is blocked. |
| `1` | Evaluation succeeded and `--fail-on-required-next-step` found an unperformed required next action. |
| `2` | Invalid CLI arguments, unreadable files, or malformed required table structure. |

## JSON Output Contract

The tool writes JSON to stdout for `--format json` and `--format both`.

```json
{
  "schema": "agent-delivery.evaluate-orchestration-next-step.v1",
  "pack_path": "/absolute/path/to/orchestration-pack.md",
  "repo_path": "/absolute/path/to/repo",
  "intent": "expects-hardening",
  "no_implementation": true,
  "workflow_phase": "post_orchestration",
  "required_next_skill": "child-spec-hardening",
  "first_unblocked_child": "MD-E2E-1",
  "delivery_allowed": false,
  "hardening_expected": true,
  "trigger_result": "hardening_required_not_started",
  "final_status_token": "hardening_started_required",
  "lane_classification": [
    {
      "child": "MD-E2E-1",
      "classification": "harden_now",
      "reason": "needs hardening and has no unresolved predecessor dependency",
      "handoff": "_specs/child-session-handoffs/md-e2e-1-session-handoff.md"
    }
  ],
  "warnings": [],
  "errors": []
}
```

Allowed `required_next_skill` values:

- `child-spec-hardening`
- `spec-change-delivery`
- `spec-orchestrator`
- `none`

Allowed `trigger_result` values:

- `hardening_required_not_started`
- `hardening_blocked`
- `hardening_deferred_by_user`
- `orchestration_only_by_user_request`
- `ready_for_delivery`
- `no_action_required`

Allowed `final_status_token` values:

- `hardening_started_required`
- `hardening_blocked`
- `hardening_deferred_by_user`
- `parallel_hardening_requires_explicit_agent_authorization`
- `orchestration_only_by_user_request`
- `ready_for_spec_change_delivery`
- `no_action_required`

Allowed lane classifications:

- `harden_now`
- `parallel_draft_only`
- `blocked_by_dependency`
- `deferred`
- `ready_for_delivery`
- `needs_orchestrator_sync`

## Classification Rules

The tool should be conservative and deterministic.

1. A child with `DEFERRED`, `DEFERRED FOLLOW-UP`, or a Next Action beginning with "Do not start" is `deferred`.
2. A child with `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES` is `ready_for_delivery`; `delivery_allowed` can become true only for that child and only when `--no-implementation` is absent.
3. A child with `NEEDS HARDENING` and no unresolved predecessor child dependency is a candidate for `harden_now`.
4. If several children are candidates, choose the first row order as `harden_now`; later independent spec/doc children may be `parallel_draft_only` only when their row or parallelization surface explicitly says draft/partial parallel work is safe.
5. A child is `blocked_by_dependency` when its Dependencies cell names predecessor child ids whose row is not `IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, `accepted`, `frozen`, or equivalent accepted/frozen wording.
6. If the Child Index is missing exact operational columns, return `needs_orchestrator_sync` lanes and `required_next_skill = spec-orchestrator`.
7. `--intent orchestration-only` and `--intent stop-before-hardening` override hardening start and produce the corresponding deferred/orchestration status token.
8. `--no-implementation` never prevents `required_next_skill = child-spec-hardening`; it only prevents `required_next_skill = spec-change-delivery`.

## Fixture Cases

Fixtures should live under:

```text
skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/
```

Required cases:

| Case | Input Shape | Command | Expected |
|---|---|---|---|
| `ORCH-NEXT-HARDEN-NOW` | MD-E2E-like pack with first child `NEEDS HARDENING`, next children blocked/deferred. | `--intent expects-hardening` | `required_next_skill=child-spec-hardening`, first child `MD-E2E-1`, lane `harden_now`. |
| `ORCH-NEXT-NO-IMPLEMENTATION-STILL-HARDENS` | Same as above. | `--intent expects-hardening --no-implementation` | Still routes to `child-spec-hardening`; `delivery_allowed=false`. |
| `ORCH-NEXT-ORCHESTRATION-ONLY` | Same as above. | `--intent orchestration-only --no-implementation` | No hardening start required; status `orchestration_only_by_user_request`. |
| `ORCH-NEXT-ALL-BLOCKED` | Every hardening child depends on unresolved predecessor or decision. | `--intent expects-hardening` | `required_next_skill=none`, `trigger_result=hardening_blocked`, no first unblocked child. |
| `ORCH-NEXT-PARALLEL-DRAFT-ONLY` | One first child hardens now, docs child can draft in parallel, no agent authorization. | `--intent expects-hardening` | first child `harden_now`, docs child `parallel_draft_only`, final token includes `parallel_hardening_requires_explicit_agent_authorization` when requested by `--format markdown` summary. |
| `ORCH-NEXT-READY-FOR-DELIVERY-BUT-NO-IMPLEMENTATION` | First child is implementation-ready. | `--no-implementation` | `delivery_allowed=false`, no `spec-change-delivery` route. |
| `ORCH-NEXT-READY-FOR-DELIVERY` | First child is implementation-ready. | no no-implementation flag | `required_next_skill=spec-change-delivery`, `delivery_allowed=true`. |

## Acceptance Criteria

1. The tool parses the exact operational Child Index header used by `ValidateChildReadiness.cs`.
2. The tool tolerates extra Markdown sections and other tables by selecting the Child Index table first.
3. The tool emits valid JSON matching `agent-delivery.evaluate-orchestration-next-step.v1`.
4. The MD-E2E-like fixture classifies `MD-E2E-1 = harden_now`, `MD-E2E-2 = blocked_by_dependency`, `MD-E2E-3 = blocked_by_dependency`, `MD-E2E-4 = parallel_draft_only`, `MD-E2E-5 = deferred`.
5. `--no-implementation` does not suppress `child-spec-hardening`.
6. `--intent orchestration-only` and `--intent stop-before-hardening` suppress the hardening trigger and make the user deferral visible.
7. A malformed or missing Child Index exits `2` with actionable errors.
8. `--help` exits `0` and documents all options and exit codes.
9. The implementation does not mutate input files.
10. The spec-orchestrator integration remains out of scope except for a short usage note in the tool's help or a minimal docs snippet.

## Verification Commands

Run from `/tmp` to avoid repository-local SDK pinning:

```sh
dotnet --version
```

Success: exits `0` and prints a `10.x` SDK version. Authoring evidence on 2026-05-09: `10.0.203`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- --help
```

Success after implementation: exits `0`, prints usage, includes `--pack`, `--intent`, `--no-implementation`, `--format`, and exit codes.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/md-e2e-like/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --intent expects-hardening \
  --no-implementation
```

Success: exits `0`; JSON has `required_next_skill = "child-spec-hardening"`, `first_unblocked_child = "MD-E2E-1"`, `delivery_allowed = false`, and the required MD-E2E lane classifications.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/md-e2e-like/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --intent orchestration-only \
  --no-implementation
```

Success: exits `0`; JSON has `trigger_result = "orchestration_only_by_user_request"` and does not require hardening start.

```sh
git diff --check
```

Success: exits `0`.

## Definition of Ready

- This spec has no blocking `[MISSING]` or `[DECISION]` markers.
- The target path and CLI contract are explicit.
- JSON schema values are enumerated.
- Fixture cases cover the known workflow failure.
- Verification commands define cwd, success criteria, and SDK assumptions.

## Definition of Done

- `skills-repo/tools/EvaluateOrchestrationNextStep.cs` exists and is a .NET 10 file-based app.
- Fixture files for all required cases exist.
- All verification commands above pass.
- The final implementation notes include any heuristics that were intentionally conservative.
- No child specs, MD-E2E artifacts, or runtime product files are changed.

## Content Quality Review

- Correctness/domain fit: the spec targets the observed post-orchestration failure directly.
- Scope discipline: one tool only; skill integration is deferred.
- Completeness: normal, blocked, user-deferred, no-implementation and ready-for-delivery paths are covered.
- Testability: fixture cases and JSON assertions are concrete.
- Residual risk: markdown dependency parsing is necessarily heuristic; the tool must expose reasons and warnings instead of silently overclaiming.

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial hardened spec for `EvaluateOrchestrationNextStep.cs`. |
| 2026-05-09 | workflow-tooling-evaluate-next-step-delivery | Scope Contract locked in OpenSpec mode for direct implementation of `EvaluateOrchestrationNextStep.cs`. |
| 2026-05-09 | workflow-tooling-evaluate-next-step-delivery | Implemented the evaluator tool, fixture packs, OpenSpec change, and verification evidence. |
