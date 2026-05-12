## Context

The current Agent Delivery workflow grew from a useful observation: large specs, research notes, child splits, verification history, and post-implementation follow-ups overload the agent context and make scope drift likely. The existing answer was to create Parent/Child control surfaces, child session handoffs, launcher/controller evidence, visible-session validation, closeout/archive checks, and a dedicated testsuite.

That answer is now too expensive. The Skill MDs are large, the agent has difficulty following every rule, and the repository contains many artifacts that describe or test orchestration mechanics rather than the desired workflow outcome. The new design keeps the useful intent and discards the heavy default mechanism.

## Goals / Non-Goals

**Goals:**

- Make one small OpenSpec change the active implementation context for Agent Delivery.
- Keep large specs, parent specs, and research material as reference-only inputs unless a new small OpenSpec change explicitly pulls a slice into active scope.
- Remove default reliance on fresh sessions, child-session launch evidence, visible Codex-App session proof, and controller-backed multi-session orchestration.
- Reduce Skill MD size by replacing long embedded rule matrices with short canonical pointers.
- Clean up obsolete Agent Delivery files and document what was retained, deleted, or archived.
- Keep enough validation to prevent silent scope drift: active change exists, active scope is narrow, write-set is bounded, verification is explicit, and stale session artifacts are not treated as default gates.

**Non-Goals:**

- Rebuild the old launcher/controller workflow under a new name.
- Require every small documentation edit to create a full OpenSpec change.
- Delete accepted historical evidence that is still needed to understand archived decisions or regression baselines.
- Change OpenSpec itself.
- Solve prompt-memory or native model context behavior.

## Decisions

### Decision 1: OpenSpec change is the active context source of truth

The active implementation context is not a new standalone Markdown schema. It is the active OpenSpec change directory:

- `proposal.md` states why and the bounded scope.
- `design.md` exists only when architectural choices need to be fixed before implementation.
- `specs/**/spec.md` contains normative requirement deltas.
- `tasks.md` is the implementation checklist.

The workflow documentation may describe a tiny "active context view" derived from those files, but it must not introduce another required long-form artifact that can drift from OpenSpec.

Alternatives considered:

- **Separate Scope Capsule file**: rejected as default because it creates another document to keep synchronized.
- **Fresh session per child**: rejected as default because it is a blunt tool and creates evidence overhead.
- **Full parent spec as active context**: rejected because it reintroduces the original context-drift problem.

### Decision 2: Parent/master specs are reference and coverage, not implementation contracts

Large specs can still exist, but implementation begins only after a narrow OpenSpec change has been created for the current slice. Parent material is used to check conformance and coverage, not to expand the current work.

### Decision 3: Cleanup is a required migration step

The implementation must inventory obsolete Agent Delivery artifacts before deleting them. Each candidate artifact is classified as:

- `delete`: obsolete generated evidence, fixtures, tests, or tooling for the discarded default workflow.
- `retain`: still useful as canonical documentation, active implementation source, accepted baseline evidence, or simplified regression coverage.
- `archive-reference`: historically useful but not part of the active workflow.

Deletion must be conservative where history is ambiguous. The cleanup report is part of closeout evidence.

Cleanup evidence lives in the active change directory:

- `openspec/changes/simplify-agent-delivery-active-openspec/cleanup-manifest.json`
- `openspec/changes/simplify-agent-delivery-active-openspec/cleanup-evidence.md`

The default cleanup policy is delete-by-default for artifacts that exist only for retired default session orchestration. An artifact is retained only when the manifest records a concrete reason: canonical documentation, accepted baseline evidence, active simplified regression coverage, or explicitly selected non-default legacy/debug reference.

### Decision 4: Skills become routers, not rule containers

Affected Skill MDs should answer: when to use the skill, what source is canonical, and when to stop. They should not duplicate the full workflow, OpenSpec schema, child index rules, launcher profiles, or visible-session evidence contracts.

Enforceable rules move into small tools. A Skill MD may name a command and explain in one or two lines when to run it, but the detailed rule lives in the tool implementation and its tests. This prevents the replacement workflow from becoming another wall of instructions that agents skim or ignore.

Initial command surface:

- `dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change <change-name> [--parent <path>]`
- `dotnet run skills-repo/tools/ValidateAgentDeliveryCleanup.cs -- --manifest <path> --root <repo-root>`

The exact implementation language may change if the repository standard changes, but the command surface must remain small, deterministic, and scriptable.

### Decision 5: Validation shifts from session proof to active-scope proof

The remaining tests should verify that:

- a large request is reduced to a small active OpenSpec change before implementation,
- the agent does not implement from the parent/master spec directly,
- obsolete session orchestration is not required for default success,
- cleanup removes or retires stale artifacts without deleting retained baselines,
- Skill MDs no longer contain large duplicated Agent Delivery matrices,
- command-line validators enforce active scope and cleanup references instead of relying on long prose instructions.

## Risks / Trade-offs

- **Risk: Too little structure lets scope drift return.** → Mitigate with a narrow active OpenSpec gate, explicit write-set, verification requirements, and tests that fail parent-as-implementation behavior.
- **Risk: Cleanup deletes useful historical evidence.** → Mitigate with inventory classification and a retained-artifact manifest before broad deletion.
- **Risk: Existing tests expect old session behavior.** → Mitigate by replacing or removing those tests in the same change, not by keeping contradictory gates.
- **Risk: Users may still ask for multi-session debug proof.** → Mitigate by documenting that such tooling is legacy/debug-only and not a default pass condition.
- **Risk: OpenSpec overhead is too high for tiny changes.** → Mitigate by allowing direct mode for small non-Agent-Delivery maintenance edits; the Agent Delivery simplification applies to large-scope delivery work.

## Migration Plan

1. Add the simplified OpenSpec-first Agent Delivery model to `docs/doc-workflow.md`.
2. Slim affected Skill MDs to point to the canonical model and remove duplicated session-orchestration detail.
3. Add lightweight command-line validators for active-scope behavior and cleanup-reference checks.
4. Inventory existing Agent Delivery artifacts and classify each cleanup candidate in `cleanup-manifest.json`.
5. Apply cleanup in this order: generated evidence and live-session run directories, obsolete tests/fixtures, obsolete tools, obsolete archived/active OpenSpec experiment changes.
6. Run documentation, spec, and cleanup validation.
7. Record cleanup evidence in `cleanup-evidence.md` with retained/deleted/archive-reference lists.

Rollback is documentation-level: if the simplified workflow is insufficient, restore deleted artifacts from git history and reintroduce only the smallest needed debug path as an explicit non-default capability.

## Open Questions

None. Cleanup defaults are intentionally explicit: delete obsolete default-session-orchestration artifacts unless `cleanup-manifest.json` records a concrete retention reason.
