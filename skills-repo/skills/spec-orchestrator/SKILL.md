---
name: spec-orchestrator
description: Orchestrate an existing parent/master spec, parent draft, or child-spec set into child delivery packs, coverage matrices, hardening queues, and parallelization plans. Use this skill whenever the user wants to speed up work after an initial spec exists, split a master/parent spec into child specs, compare child specs against a master spec, create a readiness/coverage matrix, decide what can run in parallel, or asks "what is the next spec/slice?" Do not use this as the first step for a blank/new spec prompt; use doc-coauthoring first. Use child-spec-hardening after this skill when child specs need implementation-ready depth.
---

# Spec Orchestrator

Turn a large spec into a delivery control pack: parent coverage, child-spec readiness, hardening queue, backlog re-entry, parallel lane options, and next-slice recommendation.

Use this skill to reduce the repeated hand work of discovering child boundaries and readiness gaps. Use `child-spec-hardening` to create the deeper implementation-ready child contract.

## Core Promise

Do not implement feature code. Produce the orchestration layer that makes later implementation faster and safer.

The default output is a **Delivery Orchestration Pack**:

1. Parent/child inventory.
2. Child Index as the operational control surface.
3. Coverage matrix.
4. Parent scope conformance matrix.
5. Child readiness matrix.
6. Hardening queue or missing delivery-pack patches/instructions.
7. Parallel Work Control Surface.
8. Recommended execution order.
9. Closeout sync checklist.
10. Persisted Child Session Handoff for the next child/hardening/delivery session.
11. OpenSpec ledger recommendation or setup notes for Parent/Child work.

If the user explicitly asks to also update files, update only spec/planning/workflow artifacts unless they explicitly ask for runtime implementation.

## Shared Workflow Contract

Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` as the canonical reference for the Session Briefing, Review Control Surface, Parallel Work Control Surface, DoR/DoD, Decision Freeze Pack, Spec Goldstandard, and Mini-Retro.

At the start of larger orchestration work, clarify or infer:
- active mode/skill,
- source of truth parent/index/spec files,
- goal and non-goals,
- in-scope orchestration output,
- expected deliverable,
- verification/review path,
- open decisions.

When reading or generating specs, require the Review Control Surface to expose spec variant, Goldstandard status, goal, in scope, out of scope, key test/harness cases, key verification commands, open decisions, and readiness status. Missing or stale control surfaces become readiness gaps.

For Parent/Child work, treat the Child Index as the operational control surface. It tracks slice status, parent coverage, hardening verdict, session handoff pointer, dependencies, next action, evidence/closeout links, backlog/re-entry, and OpenSpec/direct ledger pointers. It must not duplicate fine-grained OpenSpec tasks or implementation plan tasks.

## When To Use

Use this skill when the request includes any of these patterns:

- the Spec Sizing Gate fired in `doc-coauthoring` or `spec-change-delivery`
- "large spec", "master spec", "parent spec", "child specs", "slices"
- "which child specs are implementation-ready?"
- "what needs hardening before implementation?"
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
- Parallel Work Control Surface when parallel work is plausible,
- recommended next slice.

### Mode B: Generate Child Delivery Packs

Use when a parent spec or parent draft exists but child specs are missing or too thin.

Output or create:

- child spec skeletons,
- parent coverage table,
- shared verification recipe,
- backlog entries,
- child index updates.

For Parent/Child work, default to OpenSpec as the preferred delivery ledger unless the user explicitly chooses direct mode or the target repo has no useful OpenSpec context. Keep OpenSpec as the formal change/audit ledger; do not duplicate its task detail in the child index or hardening queue.

### Mode C: Batch Readiness Assessment

Use when several child specs should be assessed before hardening or implementation starts.

Output or create:

- batched child-spec readiness updates,
- a readiness report,
- explicit non-ready reasons,
- a hardening queue for `child-spec-hardening`.

### Mode D: Parallelization Plan

Use when the user wants parallel agents/sessions.

Output:

- Parallel Work Control Surface with child/work block, lane mode, owner/agent, allowed write-sets, shared/read-only files, dependencies, verification commands, integration owner, and merge/sync order,
- serial prerequisites,
- cross-slice verification replay.

Recommend parallel spec/doc hardening whenever child/doc write-sets are separated and dependencies allow it. Recommend parallel implementation only when implementation-ready specs, runtime/code write-sets, and contracts are clearly separated and one integration owner owns shared control-file updates.

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

### 2. Establish Or Update Child Index

Create or update a Child Index whenever Parent/Child orchestration is active. If no separate index file exists, place the control surface in the parent spec, slice plan, or Delivery Orchestration Pack and list where it should live.

Minimum Child Index columns:

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|

Rules:

- Every known child, planned child, deferred parent requirement, and blocked/re-entry item needs a row or named destination.
- The `Child` cell must be a stable child id such as `S3`, not a combined display label such as `S3 Content Bundle`. Keep human-readable names in `Child Spec`, `Parent Coverage`, or an optional extra column.
- Child id, handoff filename, handoff `Child` field, validator/delivery invocation, and OpenSpec/ledger pointer must agree; the concrete child-spec path belongs in the handoff `Child Spec` field. If they disagree, treat the row/handoff as stale and do not report implementation readiness.
- Do not treat a legacy, partial, aliased, or compressed index table as operational. A table that only contains `Slice`, `Spec`, `Status`, `Hardening Verdict`, `Session Handoff`, `Dependencies / Evidence`, `Allowed Next Mode`, `Implementation Gate`, `Closeout Sync`, or similar substitute columns is a migration intermediate and cannot support `IMPLEMENTATION READY`.
- Before marking any child ready, make sure the table contains the exact minimum column names shown above and that the target child's row has non-empty values for each required column. Do not accept renamed, merged, or semantically equivalent substitute columns as satisfying the gate.
- For `IMPLEMENTATION READY`, the `Allowed Write-Set` cell must be a firm enforceable list or pattern list. Avoid uncertain language such as `likely`, `probably`, `expected`, `TBD`, `as needed`, `related files`, or `etc.`; if write-set uncertainty remains, mark the child `needs_hardening` or `needs_parent/orchestrator_sync`.
- `ready_candidate` is not implementation permission. Only a documented hardening verdict of `IMPLEMENTATION READY` or explicitly accepted `READY WITH NON-BLOCKING NOTES` can feed `spec-change-delivery`.
- Be precise in final wording: `spec-orchestrator` is complete when the parent control surface, Child Index, coverage/dependency shape, hardening queue, ledger pointers, and next handoff exist. Do not say "the children are ready" or imply implementation permission unless `child-spec-hardening` has produced a documented implementation-allowing verdict and the readiness validator has passed for that child.
- Keep the Hardening Queue as the subset of Child Index rows that still need contract, case, verification, conformance, or DoR/DoD depth.
- Keep OpenSpec as the formal delivery ledger when active. The Child Index points to OpenSpec changes and evidence; it does not mirror their task detail.
- After recommending a next child, update `Next Action`, create or update the persisted Child Session Handoff, and write its path into `Session Handoff`.
- Default handoff location is `child-session-handoffs/<child-id>-session-handoff.md` beside the Child Index. If the Child Index is only a section in another artifact, name the exact file/section or patch target that owns the handoff.
- Mark a handoff as stale/blocking instead of reusing it when its child path, verdict, next action, evidence/OpenSpec pointer, or index row disagrees with the current orchestration state.
- After creating or updating the leading handoff, create Agent Delivery Session Launch/Queue Evidence with `skills-repo/tools/AgentDeliverySessionLauncher.cs --mode queue` or document the explicit `manual_start_required`, `blocked`, or `failed` reason. Do not describe a handoff as an automated fresh-session transition unless matching `_specs/agent-delivery-session-launches/**/launch-request.json` and `evidence.json` exist for the same target id and handoff path.
- Do not use a semantic `SessionId` label as the only future session proof. Record matching launch evidence, a real Codex session id plus `.codex/...jsonl` log path, `manual_start_required` evidence, or explicit `legacy_reconstructed` source/date for historical pre-launcher transitions.

### 3. Normalize Parent Requirements

Extract parent requirements into stable rows:

- id or inferred id,
- title,
- summary,
- source section,
- required evidence,
- owning child slice,
- current coverage status.

If the parent lacks requirement IDs, infer temporary IDs and recommend adding stable IDs before broad automation.

### 4. Build Coverage Matrix

For each parent requirement, classify:

- `done`: accepted evidence exists,
- `partial`: some child/slice covers it,
- `pending`: visible future work exists,
- `blocked`: dependency prevents work,
- `missing`: no child/backlog entry covers it,
- `out_of_scope`: explicitly excluded with rationale.

Missing rows are the most important finding. They are where work falls through.

### 5. Run Parent Scope Conformance Gate

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

### 6. Assess Child Readiness

Every implementation-ready child spec needs:

- header/status/scope,
- Review Control Surface,
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
- `ready_candidate`,
- `needs_hardening`,
- `blocked`,
- `too_broad`,
- `candidate_parallel_lane`.

Use `ready` only when the child already contains a documented hardening verdict plus implementation-ready depth: status provenance/evidence, normative contract, concrete harness cases, hardened verification commands, DoR/DoD, and no blocking parent conformance or content-quality findings. Otherwise use `ready_candidate` or `needs_hardening` and route to `child-spec-hardening`.

### 7. Generate Delivery Packs

For each child that is not ready, propose a delivery skeleton or hardening queue entry with these sections:

```md
## Goal
## Review Control Surface
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

Do not try to fully elaborate every normative contract, canonical example, fixture, and harness case inside this skill when multiple children are involved. Capture the required depth as a `child-spec-hardening` work order.

Hardening queue format:

| Child | Current Status | Required Hardening | Sources To Read | Blockers | Next Handoff Target |
|---|---|---|---|---|---|

For contract-heavy children, include `Canonical Examples/Fixtures decision` in Required Hardening.

### 8. Decide Parallelization

Create a Parallel Work Control Surface:

| Lane | Child/Work Block | Mode | Owner/Agent | Allowed Write-Sets | Shared Files / Read-only Files | Dependencies | Verification Commands | Integration Owner | Merge/Sync Order |
|---|---|---|---|---|---|---|---|---|---|

Classify every lane as either `spec/doc hardening` or `implementation`.

Parallel spec/doc hardening is allowed when:

- each lane owns a distinct child spec, plan, or doc artifact,
- parent spec, child index, slice plan, backlog, and shared contracts are read-only for lane workers,
- dependencies are visible and acyclic,
- each lane has review/consistency verification,
- one integration owner updates shared control files after lane completion.

Parallel implementation is allowed only when:

- allowed write-sets are disjoint,
- every editing lane uses an isolated branch/worktree/OpenSpec change or clearly separated files,
- target specs are implementation-ready,
- shared contracts, schemas, helpers, and harnesses are stable before implementation lanes begin,
- shared control files are read-only for every lane except the named integration owner,
- each lane has its own verification commands and done signal,
- dependencies are acyclic and visible,
- merge/sync order is explicit,
- one owner updates parent spec, child index, slice plan, backlog, and shared verification evidence after integration.

Parallel spec/doc hardening should be serialized only when dependencies are unclear, child/doc write-sets overlap, or shared-file ownership is missing. Parallel implementation is not allowed when runtime/code write-sets overlap, shared files are ambiguous, contracts are still changing, verification only works after a combined merge, dependencies are unclear, or no integration owner is named. Isolated branches/worktrees do not make overlapping implementation write-sets safe; they only contain edits until the serial integration step. If two implementation slices need the same contract/helper/harness, make that shared contract a serial prerequisite slice.

### 9. Recommend Execution Order

Prefer this order:

1. Contract/harness foundations.
2. Independent content/spec hardening.
3. Runtime implementation slices.
4. Cross-slice integration/harness.
5. Closeout sync.

Recommend the next single slice and, separately, any batch/parallel work that can happen safely.

For each next child, include and persist a Child Session Handoff using the shared workflow template: parent path, stable child id, child spec path, child index/queue path, handoff file path, target repository / working directory, Codex session/log metadata when available, real session evidence or explicit `legacy_reconstructed` marker when historical, next mode/skill, current verdict, scope summary, non-goals, allowed write-set, shared/read-only files, verification lifecycle, evidence/OpenSpec, retained evidence, open blockers or non-blocking notes, and whether the next step should start in a fresh session. Link the same file from the Child Index. Then run or recommend `AgentDeliverySessionLauncher.cs --mode queue --handoff <handoff> --target-id <child> --agent codex --out _specs/agent-delivery-session-launches`; if that cannot produce `queued` or `launched`, keep the blocked/manual state visible.

### 10. Closeout Sync Checklist

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

**Child Index**
| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|

**Parent Scope Conformance**
| Child | Parent Requirement | Conformance | Action |
|---|---|---|---|

**Child Readiness**
| Child | Status | Main Gap | Required Hardening |
|---|---|---|---|

**Hardening Queue**
| Child | Current Status | Required Hardening | Sources To Read | Blockers | Next Handoff Target |
|---|---|---|---|---|---|

**Parallelization**
| Lane | Child/Work Block | Mode | Safe? | Owner/Agent | Allowed Write-Sets | Shared Files / Read-only Files | Dependencies | Verification Commands | Integration Owner | Merge/Sync Order |
|---|---|---|---|---|---|---|---|---|---|---|

**Recommended Next Moves**
1. ...
2. ...
3. ...

**Child Session Handoff**
- Parent:
- Child:
- Child Spec:
- Child Index / Queue:
- Handoff file:
- Target repository / working directory:
- Next mode/skill:
- Current verdict:
- Scope summary:
- Non-goals:
- Allowed write-set:
- Shared / read-only files:
- Verification commands:
- Evidence / OpenSpec:
- Open blockers or non-blocking notes:
- Fresh session recommended:

**Files To Update**
- ...

**Mini-Retro**
- What was decided?
- What changed?
- What remains open?
- Which evidence/verification is missing?
- Which skill/workflow friction showed up?
- Session/context state: continue here or start a new session?
```

If files were edited, include changed files and verification performed. Include the Mini-Retro after substantial orchestration blocks or before handoff/context loss.

## Guardrails

- Do not let "accepted" specs hide future work. Future work must become parent coverage, backlog, or child spec rows.
- Do not let a missing or stale Review Control Surface pass as ready; it must match the detailed spec variant, Goldstandard status, scope, cases, commands, open decisions, and readiness verdict.
- Do not mark a child ready when it lacks verification commands.
- Do not mark a child ready when it contradicts the parent spec or omits expected parent scope without a named re-entry path.
- Do not mark a child ready when its content-quality review has blockers, even if formal sections are present. This includes ambiguous, inconsistent, infeasible, incomplete, untestable, non-traceable, or semantically broken requirements, plus data/artifact/status contract flaws.
- Do not mark a child implementation-ready just because the split is plausible. If normative contract depth, concrete cases, hardened verification commands, DoR/DoD, or status evidence are missing, route to `child-spec-hardening`.
- Do not finish Parent/Child orchestration without a Child Index update or a clearly named Child Index patch target.
- Do not report an `IMPLEMENTATION READY` child from a partial, compressed, or aliased Child Index. Use `NEEDS PARENT/ORCHESTRATOR SYNC` until the exact operational row exists and agrees with the child spec and handoff.
- Do not report an `IMPLEMENTATION READY` child while the `Allowed Write-Set` is approximate or advisory instead of enforceable.
- Do not recommend `spec-change-delivery` for a child that has no documented hardening verdict.
- Do not leave the next child without a persisted Child Session Handoff and matching Child Index pointer.
- Do not mark `done`, `accepted`, or `reference_done` unless evidence/closeout can be cited; otherwise use `parent_claims_done`.
- Do not let parallel lanes edit shared control files independently or start without explicit shared/read-only file rules.
- Do not recommend parallel work when merge/sync order, lane verification, or integration ownership is missing; serialize instead.
- Do not implement feature/runtime code from this skill unless the user explicitly switches to `spec-change-delivery`.
- Prefer a small generated delivery pack over a long narrative essay.

## Hand-Off To Other Skills

- Use `doc-coauthoring` first when no parent spec/draft exists yet, or when parent/child requirement text itself needs authoring.
- Use `child-spec-hardening` after this skill when a child draft or hardening queue item must become implementation-ready.
- Use `doc-review-autoresolve` when findings are clear and safe to fix in spec/docs.
- Use `refine-plan` when the user wants an iterative implementation plan artifact.
- Use `spec-change-delivery` when one child is ready and the user asks to implement it.
- Use `spec-closeout` after a child implementation is accepted.
- Use `improve-skills` when recurring orchestration failures should be folded back into skills.
