**Date:** 2026-05-09
**Status:** 🟢 Accepted
**Scope:** .NET 10 validator for Agent Delivery orchestration packs.
**SessionId:** workflow-tooling-validate-orchestration-pack-delivery

---

## Review Control Surface

- Spec-Variante: Tool delivery spec for Agent Delivery workflow automation.
- Goldstandard Status: accepted; OpenSpec archived.
- Ziel: Create `skills-repo/tools/ValidateOrchestrationPack.cs`, a .NET 10 file-based app that validates an Agent Delivery orchestration pack as a control artifact before follow-up hardening, launch, or implementation claims are trusted.
- In Scope: exact Child Index structure, required row cells, child spec and handoff pointer existence, handoff child-id consistency, Hardening Queue / Child Index consistency, status / next-action contradictions, conservative false-advancement claim detection, JSON and Markdown output, deterministic exit codes, fixture-based tests.
- Out of Scope: skill integration, handoff generation, launch automation, deciding the next workflow step, validating implementation readiness for one child, editing MD-E2E specs, launching agents, proving arbitrary final-answer wording.
- Wichtigste Test-/Harness-Cases: `ORCH-PACK-VALID`, `ORCH-PACK-MISSING-HANDOFF`, `ORCH-PACK-STALE-NEXT-ACTION`, `ORCH-PACK-COMPRESSED-INDEX`, `ORCH-PACK-FALSE-ADVANCEMENT-CLAIM`.
- Wichtigste Verification Commands: from `/tmp`, `dotnet run ...ValidateOrchestrationPack.cs -- --help`; one valid fixture command; four invalid fixture commands that must exit `1`; `openspec validate docworkflow-agent-delivery-testsuite --strict`; `git diff --check`.
- Offene Entscheidungen: none blocking. False-advancement detection is intentionally conservative and only targets explicit workflow advancement / launch / delivery claims without matching evidence, not every possible natural-language success phrase.
- Readiness Status: ACCEPTED. Tool, fixtures, OpenSpec archive, canonical spec validation and verification evidence exist.

## Session Briefing

- Modus/Skill: `doc-review-autoresolve` for hardening, then `spec-change-delivery` in OpenSpec mode.
- Source of Truth: this spec; existing tools `ValidateChildReadiness.cs`, `EvaluateOrchestrationNextStep.cs`, `ValidateAgentDeliveryLaunchEvidence.cs`; current Agent Delivery orchestration pack examples.
- Ziel: Move brittle orchestration-pack sanity checks out of manual review into a deterministic local validator.
- Nicht-Ziele: No edits to `skills-repo/skills/spec-orchestrator/SKILL.md`, no skill integration, no session launches, no changes to MD-E2E specs.
- In Scope: one new tool, OpenSpec change artifacts, fixtures under `skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/`, and verification evidence.
- Erwarteter Output: accepted tool spec, archived OpenSpec change, implemented tool, fixtures, and replayable evidence.
- Verification/Review: local .NET file-based app checks, OpenSpec validation, and `git diff --check`.
- Offene Entscheidungen: none blocking.

## Problem

Agent Delivery orchestration packs are high-leverage control artifacts. If the Child Index is compressed, a handoff pointer is stale, the Hardening Queue disagrees with row verdicts, or the pack claims the workflow advanced when it only created queue/handoff files, later sessions can start from a false premise.

Existing tools cover adjacent slices:

- `ValidateChildReadiness.cs` validates one child row and handoff before implementation.
- `EvaluateOrchestrationNextStep.cs` decides the next workflow skill after orchestration.
- `ValidateAgentDeliveryLaunchEvidence.cs` validates launch/queue evidence for a handoff.

This tool validates the orchestration pack itself before those narrower checks are trusted.

## Goal

Implement `ValidateOrchestrationPack.cs` as a .NET 10 file-based application that:

1. reads one Markdown orchestration pack,
2. finds the exact operational Child Index table,
3. validates all child rows and referenced child spec / handoff files,
4. checks Hardening Queue consistency when the queue is present,
5. reports stale status / next-action contradictions,
6. rejects compressed or aliased index columns by default,
7. rejects explicit advancement, launch, delivery, closeout, or hardening-complete claims when the pack only contains queue/handoff setup and no matching evidence,
8. emits stable JSON and optional Markdown for downstream tools.

## Non-Goals

- Do not mutate packs, specs, handoffs, or evidence files.
- Do not replace `ValidateChildReadiness.cs`; this pack-level validator may say a pack is structurally valid while one child still needs later readiness validation.
- Do not choose the next skill; `EvaluateOrchestrationNextStep.cs` owns that.
- Do not generate missing handoffs.
- Do not launch agents.
- Do not integrate into `spec-orchestrator/SKILL.md` in this change.

## CLI Contract

Primary command:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack /absolute/path/to/orchestration-pack.md \
  --repo /absolute/path/to/repo \
  --format json
```

Options:

| Option | Required | Meaning |
|---|---:|---|
| `--pack <path>` | yes | Markdown file containing the orchestration pack. |
| `--repo <path>` | no | Repository root for resolving repo-relative child spec, handoff and evidence paths. Defaults to current directory. |
| `--child-index-section <name>` | no | Section heading to prefer for Child Index parsing. Default: `Child Index`. |
| `--hardening-queue-section <name>` | no | Section heading to prefer for Hardening Queue parsing. Default: `Hardening Queue`. |
| `--allow-extra-columns` | no | Permit extra Child Index columns beyond the exact operational minimum. Compressed/aliased substitute columns still fail. |
| `--format <json|markdown|both>` | no | Default: `json`. |
| `--help` | no | Print usage and exit `0`. |

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | Validation completed and no error-severity findings were found. |
| `1` | Validation completed and one or more error-severity findings were found. |
| `2` | Invalid arguments, unreadable pack, unreadable repo path, unsupported format, or missing required Child Index table. |

## JSON Output Contract

The tool writes JSON to stdout for `--format json` and `--format both`.

```json
{
  "schema": "agent-delivery.validate-orchestration-pack.v1",
  "pack_path": "/absolute/path/to/orchestration-pack.md",
  "repo_path": "/absolute/path/to/repo",
  "valid": false,
  "child_count": 2,
  "finding_counts": {
    "errors": 1,
    "warnings": 0
  },
  "findings": [
    {
      "severity": "error",
      "code": "missing-handoff",
      "child": "MD-E2E-1",
      "message": "Session Handoff file not found: /absolute/path/_specs/child-session-handoffs/md-e2e-1-session-handoff.md"
    }
  ]
}
```

Allowed `severity` values:

- `error`
- `warning`

Required finding codes:

- `missing-child-index`
- `compressed-child-index`
- `extra-child-index-columns`
- `empty-required-cell`
- `missing-child-spec`
- `missing-handoff`
- `handoff-child-mismatch`
- `queue-child-missing-from-index`
- `queue-missing-child`
- `queue-status-mismatch`
- `status-next-action-mismatch`
- `false-advancement-claim`

The implementation may add narrower codes if useful, but the required fixture cases must exercise the codes above where applicable.

## Child Index Contract

The Child Index MUST use the exact operational columns shared with `ValidateChildReadiness.cs`:

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|

Rules:

1. The table may contain additional columns only when `--allow-extra-columns` is passed.
2. Compressed or aliased substitute columns always fail. Examples: `Slice`, `Spec`, `Status`, `Hardening Verdict`, `Dependencies / Evidence`, `Allowed Next Mode`, `Implementation Gate`, `Closeout Sync`, `Notes`.
3. Every required cell must be non-empty and must not be a placeholder such as `TBD`, `TODO`, `unknown`, `n/a`, `pending`, `not hardened`, `?`, or `-`.
4. `Child` must be stable and exact. Combined labels such as `S3 Content Bundle` are invalid when later handoffs and queues use only `S3`.
5. `Child Spec` and `Session Handoff` paths must resolve to existing files. Resolution order is:
   - absolute path as written,
   - path relative to the pack directory,
   - path relative to `--repo`.
6. The resolved handoff file must mention the same child id in a recognizable `Target ID`, `Stable Child ID`, `Child`, or direct child-id occurrence.

## Hardening Queue Consistency

If a `Hardening Queue` section exists, the tool MUST parse the first Markdown table in that section with at least `Child` plus one status/order column. The expected shape is:

| Order | Child | Hardening Need | Blocking Questions For Hardening |
|---|---|---|---|

Rules:

1. Every queue child must exist in the Child Index.
2. Every Child Index row whose verdict contains `NEEDS HARDENING` must appear in the queue unless the row is explicitly deferred.
3. Queue order/status `complete` requires the Child Index verdict to contain `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`.
4. Numeric queue order requires the Child Index verdict to contain `NEEDS HARDENING`.
5. Queue order/status `deferred` requires the Child Index verdict or next action to contain deferred/do-not-start wording.
6. Queue text that claims "all children ready" while any Child Index row still says `NEEDS HARDENING`, blocked, or deferred is an error.

## Status / Next Action Consistency

The validator MUST check obvious contradictions:

1. `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES` requires `Next Action` to name `spec-change-delivery` or otherwise say implementation may start for that child.
2. `NEEDS HARDENING` requires `Next Action` to name `child-spec-hardening`, hardening, or a hardening dependency. It must not route directly to `spec-change-delivery`.
3. `DEFERRED` or `DEFERRED FOLLOW-UP` requires `Next Action` to say do not start, future, deferred, or follow-up.
4. `BLOCKED` / `NEEDS USER DECISION` requires `Next Action` to keep the block visible rather than claiming implementation can start.

## False-Advancement Claim Detection

The tool MUST reject explicit workflow advancement claims that are not backed by pack evidence.

Error when the pack contains phrases matching any of these intent families and there is no matching evidence:

- `workflow advanced`, `advanced to`, `moved to hardening`, `hardening started`, `hardening completed`
- `agent queued`, `agent launched`, `launch evidence exists`
- `delivery started`, `implementation started`, `implementation complete`
- `closeout accepted`, `accepted and closed`

Matching evidence means at least one of:

- a Child Index row has an implementation-allowing verdict and the claim is about hardening completion for that same child,
- a `Session Launch / Queue Evidence` section or `Evidence / Closeout` cell contains a path to an existing `evidence.json`,
- a handoff-linked launch evidence file validates separately by `ValidateAgentDeliveryLaunchEvidence.cs`; this tool only checks path existence and obvious `evidence.json` naming.

The tool MUST NOT reject neutral orchestration-only language such as "orchestration complete", "queue created", "handoff created", "ready for child hardening", or "recommended next action".

## Fixture Cases

Fixtures live under:

```text
skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/
```

Required cases:

| Case | Input Shape | Expected |
|---|---|---|
| `ORCH-PACK-VALID` | Exact Child Index, existing child specs, existing handoffs, matching queue states. | Exit `0`; JSON `valid=true`; no errors. |
| `ORCH-PACK-MISSING-HANDOFF` | One Child Index handoff path points to a missing file. | Exit `1`; finding code `missing-handoff`; child id present. |
| `ORCH-PACK-STALE-NEXT-ACTION` | A `NEEDS HARDENING` row says `spec-change-delivery` may start. | Exit `1`; finding code `status-next-action-mismatch`. |
| `ORCH-PACK-COMPRESSED-INDEX` | Child Index uses compressed/aliased columns such as `Slice`, `Status`, or `Implementation Gate`. | Exit `2` for missing exact Child Index or exit `1` with `compressed-child-index`; message names the aliased columns. |
| `ORCH-PACK-FALSE-ADVANCEMENT-CLAIM` | Pack says "workflow advanced" / launch or hardening happened, but only queue/handoff artifacts exist and no evidence path exists. | Exit `1`; finding code `false-advancement-claim`. |

## Acceptance Criteria

1. `ValidateOrchestrationPack.cs` exists and runs as a .NET 10 file-based app.
2. The tool parses the exact operational Child Index header used by `ValidateChildReadiness.cs`.
3. The tool fails compressed/aliased Child Index tables by default.
4. The tool validates every row for required cells, child spec existence, handoff existence and child-id handoff consistency.
5. The tool validates Hardening Queue / Child Index consistency for the required cases.
6. The tool detects status / next-action contradictions for implementation-ready, needs-hardening, blocked and deferred rows.
7. The tool detects the false-advancement fixture without rejecting the valid fixture's neutral orchestration wording.
8. JSON output matches `agent-delivery.validate-orchestration-pack.v1` and includes stable finding codes.
9. `--help` exits `0` and documents all options and exit codes.
10. The implementation does not mutate input files.
11. OpenSpec change artifacts exist, were validated strictly, and are archived.
12. No edits are made to `skills-repo/skills/spec-orchestrator/SKILL.md` or MD-E2E specs.

## Verification Commands

Run from `/tmp` to prove file-based tool behavior is not dependent on current working directory:

```sh
dotnet --version
```

Success: exits `0` and prints a `10.x` SDK version. Authoring evidence on 2026-05-09: `10.0.203`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- --help
```

Success after implementation: exits `0`, prints usage, includes `--pack`, `--repo`, `--format`, `--allow-extra-columns`, and exit codes.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/valid/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --format json
```

Success: exits `0`; JSON has `valid = true` and `finding_counts.errors = 0`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/missing-handoff/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --format json
```

Success: exits `1`; JSON includes `missing-handoff`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/stale-next-action/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --format json
```

Success: exits `1`; JSON includes `status-next-action-mismatch`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/compressed-index/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --format json
```

Success: exits non-zero; JSON or stderr names compressed/aliased Child Index columns.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/false-advancement/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --format json
```

Success: exits `1`; JSON includes `false-advancement-claim`.

```sh
openspec validate docworkflow-agent-delivery-testsuite --strict
```

Success: exits `0` after OpenSpec archive updates the canonical spec.

```sh
git diff --check
```

Success: exits `0`.

## Definition of Ready

- This spec has no blocking `[MISSING]`, `[DECISION]`, or `[REVIEW]` markers.
- The target path and allowed write-set are explicit.
- CLI options, exit codes, JSON schema, required finding codes and fixture cases are explicit.
- Verification commands define cwd, success criteria and SDK assumptions.
- The false-advancement heuristic is bounded and testable.

## Definition of Done

- `skills-repo/tools/ValidateOrchestrationPack.cs` exists.
- Fixture files for all required cases exist.
- OpenSpec change `agent-delivery-validate-orchestration-pack` is archived.
- All verification commands above pass.
- The target spec status is updated to `🔵 Implemented` with closeout evidence.
- No changes are made to `skills-repo/skills/spec-orchestrator/SKILL.md`.
- No MD-E2E spec files are changed.

## Allowed Write-Set

- `_specs/2026-05-09 Agent Delivery Workflow Tooling Validate Orchestration Pack.md`
- `skills-repo/tools/ValidateOrchestrationPack.cs`
- `skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/**`
- `openspec/changes/archive/2026-05-09-agent-delivery-validate-orchestration-pack/**`

## Content Quality Review

- Correctness/domain fit: the spec targets orchestration-pack integrity, not child readiness or next-step selection.
- Scope discipline: one tool, fixtures and OpenSpec artifacts only; skill integration and MD-E2E changes are excluded.
- Completeness: structure, path existence, handoff consistency, queue/index consistency, status contradictions and false advancement claims are covered.
- Testability: each important behavior maps to a fixture command with a concrete exit-code expectation.
- Traceability: requirements derive from the existing Agent Delivery control surfaces and adjacent validator tools.
- Residual risk: natural-language false-advancement detection is heuristic by design; the tool must report conservative findings and avoid claiming proof over arbitrary prose.

## Implementation Evidence

- OpenSpec archive: `openspec/changes/archive/2026-05-09-agent-delivery-validate-orchestration-pack/`.
- Canonical spec updated and validated: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`.
- Implemented tool: `skills-repo/tools/ValidateOrchestrationPack.cs`.
- Fixture root: `skills-repo/tests/agent-delivery-workflow-tooling/validate-orchestration-pack/`.
- Real example smoke: `_specs/2026-05-09 DocWorkflow Agent Delivery Mock Data E2E Harness Orchestration Pack.md` validated with `valid = true`.

Verification replay on 2026-05-09:

- `dotnet --version` -> `10.0.203`.
- `dotnet run ...ValidateOrchestrationPack.cs -- --help` -> exited `0`; help includes `--pack`, `--repo`, `--format`, `--allow-extra-columns`, and exit codes.
- `ORCH-PACK-VALID` -> exited `0`; JSON `valid = true`, `errors = 0`.
- `ORCH-PACK-MISSING-HANDOFF` -> exited `1`; JSON includes `missing-handoff`.
- `ORCH-PACK-STALE-NEXT-ACTION` -> exited `1`; JSON includes `status-next-action-mismatch`.
- `ORCH-PACK-COMPRESSED-INDEX` -> exited `1`; JSON includes `compressed-child-index`.
- `ORCH-PACK-FALSE-ADVANCEMENT-CLAIM` -> exited `1`; JSON includes `false-advancement-claim`.
- `openspec validate agent-delivery-validate-orchestration-pack --strict` before archive -> exited `0`.
- `openspec archive -y agent-delivery-validate-orchestration-pack` -> archived as `openspec/changes/archive/2026-05-09-agent-delivery-validate-orchestration-pack/`; canonical spec updated.
- `openspec validate docworkflow-agent-delivery-testsuite --strict` after archive -> exited `0`.
- `git diff --check` -> exited `0`.
- Parallel-safety note: this change's write-set excludes `skills-repo/skills/spec-orchestrator/SKILL.md` and MD-E2E specs.

Docs/source-discovery closeout:

- `rag workflow spec-closeout --scope all --change "agent-delivery-validate-orchestration-pack ValidateOrchestrationPack" --top-k 8 --format json` returned no actionable project-doc page for this shared tool change; results were generic README strategy/private backlog/skill-maintenance sources.
- Exact repository search found references in the target spec, the implemented tool, fixtures, and separate in-progress Workflow Doctor artifacts. No shared `docs/` or root `README.md` update was required for this closeout.

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |
| 2026-05-09 | workflow-tooling-validate-orchestration-pack-delivery | Hardened into an implementation-ready tool spec with CLI, JSON, fixture, OpenSpec and verification contracts. |
| 2026-05-09 | workflow-tooling-validate-orchestration-pack-delivery | Implemented the validator tool, fixtures, OpenSpec change and verification evidence. |
| 2026-05-09 | workflow-tooling-validate-orchestration-pack-delivery | Accepted and closed: archived OpenSpec change, validated canonical spec and recorded closeout evidence. |
