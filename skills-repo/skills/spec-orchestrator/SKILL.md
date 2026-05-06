---
name: spec-orchestrator
description: Orchestrate an existing parent/master spec, parent draft, or child-spec set into implementation-ready child delivery packs. Use this skill whenever the user wants to speed up work after an initial spec exists, split a master/parent spec into child specs, make several child specs implementation-ready, compare child specs against a master spec, create a readiness/coverage matrix, decide what can run in parallel, or asks "what is the next spec/slice?" Do not use this as the first step for a blank/new spec prompt; use doc-coauthoring first to create the initial parent spec, then use this skill before refine-plan/spec-change-delivery when scope spans multiple slices.
---

# Spec Orchestrator

Turn a large spec into a delivery control pack: parent coverage, child-spec readiness, backlog re-entry, parallel lane options, and next-slice recommendation.

Use this skill to reduce the repeated hand work of making each child spec implementation-ready one by one.

## Core Promise

Do not implement feature code. Produce the orchestration layer that makes later implementation faster and safer.

The default output is a **Delivery Orchestration Pack**:

1. Parent/child inventory.
2. Coverage matrix.
3. Parent scope conformance matrix.
4. Child readiness matrix.
5. Missing delivery-pack patches or instructions.
6. Parallelization lane matrix.
7. Recommended execution order.
8. Closeout sync checklist.

If the user explicitly asks to also update files, update only spec/planning/workflow artifacts unless they explicitly ask for runtime implementation.

## When To Use

Use this skill when the request includes any of these patterns:

- "large spec", "master spec", "parent spec", "child specs", "slices"
- "make these child specs implementation-ready"
- "speed this up", "this takes too long", "orchestrate"
- "which specs can run in parallel?"
- "what is the next slice/spec?"
- "do not let the rest fall through"
- "compare child specs against the main spec"
- "generate delivery packs"

Use `doc-coauthoring` first when the user is starting from an initial idea, raw context dump, or blank spec and needs the parent spec authored. Come back to this skill once there is at least a parent draft, master spec, slice plan, or child-spec set to orchestrate.

If the user asks to implement one already-ready slice, use `spec-change-delivery` instead.

## Required Inputs

Try to discover these from the repo before asking:

1. Parent/master spec path or parent draft.
2. Child spec index or slice plan path, if it exists.
3. Child spec files, if they exist.
4. Current status/coverage source, if it exists.
5. Target implementation repo/path.
6. Verification conventions from prior accepted slices.

Ask a concise question only if there is no parent draft/spec and no target project can be inferred safely. If the user is clearly still drafting the parent spec, hand off to `doc-coauthoring` instead of forcing orchestration.

## Operating Modes

### Mode A: Orchestrate Existing Children

Use when child specs already exist.

Output:

- readiness gaps per child,
- generated patch plan for missing sections,
- lane matrix,
- recommended next slice.

### Mode B: Generate Child Delivery Packs

Use when a parent spec or parent draft exists but child specs are missing or too thin.

Output or create:

- child spec skeletons,
- parent coverage table,
- shared verification recipe,
- backlog entries,
- child index updates.

### Mode C: Batch Hardening

Use when several child specs should be made implementation-ready before implementation starts.

Output or create:

- batched child-spec updates,
- a readiness report,
- explicit non-ready reasons for remaining slices.

### Mode D: Parallelization Plan

Use when the user wants parallel agents/sessions.

Output:

- lane matrix with disjoint write-sets,
- integration owner responsibilities,
- serial prerequisites,
- cross-slice verification replay.

Only recommend parallel implementation when write-sets and contracts are clearly separated.

## Workflow

### 1. Discover Control Files

Search for:

- parent/master specs,
- child spec index,
- slice plan,
- OpenSpec changes/specs,
- backlog or SpecOps entities,
- accepted prior slices and their verification commands.

Prefer `rg`/`rg --files`. Use exact file reads once candidate files are found.

### 2. Normalize Parent Requirements

Extract parent requirements into stable rows:

- id or inferred id,
- title,
- summary,
- source section,
- required evidence,
- owning child slice,
- current coverage status.

If the parent lacks requirement IDs, infer temporary IDs and recommend adding stable IDs before broad automation.

### 3. Build Coverage Matrix

For each parent requirement, classify:

- `done`: accepted evidence exists,
- `partial`: some child/slice covers it,
- `pending`: visible future work exists,
- `blocked`: dependency prevents work,
- `missing`: no child/backlog entry covers it,
- `out_of_scope`: explicitly excluded with rationale.

Missing rows are the most important finding. They are where work falls through.

### 4. Run Parent Scope Conformance Gate

After reading or editing any child spec, compare the child claim against every parent requirement it touches.

Use these statuses:

- `preserves`: child carries the parent requirement without weakening it.
- `extends`: child adds implementation detail while staying compatible.
- `narrows_with_rationale`: child intentionally narrows this delivery slice and documents where the rest goes.
- `defers_to_child`: child explicitly delegates remaining scope to another named child/backlog item.
- `missing_from_child`: parent expects this child to cover something but the child does not.
- `contradicts_parent`: child conflicts with parent order, non-goals, security constraints, data contracts, or acceptance criteria.

Implementation readiness is blocked when:

- any touched parent requirement is `contradicts_parent`,
- any expected child coverage is `missing_from_child` without a named backlog/child destination,
- the child narrows parent scope without rationale and re-entry path.

Every child hardening pass should leave a compact conformance table:

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|

### 5. Assess Child Readiness

Every implementation-ready child spec needs:

- header/status/scope,
- parent/master coverage,
- parent scope conformance table,
- content-quality review result for the child scope,
- in scope,
- out of scope,
- Decision Freeze Pack,
- acceptance criteria,
- verification commands,
- runtime/container gates when relevant,
- negative cases when contracts/security/data are involved,
- dependencies,
- expected changed areas or write-set,
- closeout sync targets.

Mark each child:

- `ready`,
- `needs_hardening`,
- `blocked`,
- `too_broad`,
- `candidate_parallel_lane`.

### 6. Generate Delivery Packs

For each child that is not ready, propose or apply a delivery pack with these sections:

```md
## Parent Coverage
## Parent Scope Conformance
## In Scope
## Out of Scope
## Decision Freeze Pack
## Acceptance Criteria
## Verification Commands
## Dependencies and Write-Set
## Closeout Sync Targets
```

Use prior accepted slices as verification recipes. For example, if S1/S2 used local harness plus Docker harness, later runtime slices should inherit that pattern unless explicitly out of scope.

### 7. Decide Parallelization

Create a lane matrix:

| Lane | Child Spec | Goal | Allowed Write-Set | Shared Files Read-Only | Dependencies | Verification | Integration Owner |
|---|---|---|---|---|---|---|---|

Parallel is allowed only when:

- write-sets are disjoint,
- shared contracts are stable,
- each lane has its own verification,
- one owner updates shared control files after integration.

If two slices need the same contract/helper/harness, make that shared contract a serial prerequisite slice.

### 8. Recommend Execution Order

Prefer this order:

1. Contract/harness foundations.
2. Independent content/spec hardening.
3. Runtime implementation slices.
4. Cross-slice integration/harness.
5. Closeout sync.

Recommend the next single slice and, separately, any batch/parallel work that can happen safely.

### 9. Closeout Sync Checklist

Every accepted child should update:

- child spec status/history,
- parent/master coverage,
- slice plan,
- child-spec index,
- backlog/re-entry items,
- OpenSpec archive/canonical spec if used,
- SpecOps/dashboard entities if the project uses them.

## Output Format

Use this structure by default:

```md
**Spec Orchestration Result**

Parent:
Child set:
Mode:

**Coverage**
- done:
- partial:
- pending:
- missing:
- blocked:

**Parent Scope Conformance**
| Child | Parent Requirement | Conformance | Action |
|---|---|---|---|

**Child Readiness**
| Child | Status | Main Gap | Required Hardening |
|---|---|---|---|

**Parallelization**
| Lane | Child | Safe? | Reason | Write-Set | Integration Owner |
|---|---|---|---|---|---|

**Recommended Next Moves**
1. ...
2. ...
3. ...

**Files To Update**
- ...
```

If files were edited, include changed files and verification performed.

## Guardrails

- Do not let "accepted" specs hide future work. Future work must become parent coverage, backlog, or child spec rows.
- Do not mark a child ready when it lacks verification commands.
- Do not mark a child ready when it contradicts the parent spec or omits expected parent scope without a named re-entry path.
- Do not mark a child ready when its content-quality review has blockers, even if formal sections are present. This includes ambiguous, inconsistent, infeasible, incomplete, untestable, non-traceable, or semantically broken requirements, plus data/artifact/status contract flaws.
- Do not let parallel lanes edit shared control files independently.
- Do not implement feature/runtime code from this skill unless the user explicitly switches to `spec-change-delivery`.
- Prefer a small generated delivery pack over a long narrative essay.

## Hand-Off To Other Skills

- Use `doc-coauthoring` first when no parent spec/draft exists yet, or when parent/child requirement text itself needs authoring.
- Use `doc-review-autoresolve` when findings are clear and safe to fix in spec/docs.
- Use `refine-plan` when the user wants an iterative implementation plan artifact.
- Use `spec-change-delivery` when one child is ready and the user asks to implement it.
- Use `spec-closeout` after a child implementation is accepted.
- Use `improve-skills` when recurring orchestration failures should be folded back into skills.
