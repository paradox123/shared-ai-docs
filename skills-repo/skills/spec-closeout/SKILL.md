---
name: spec-closeout
description: Finalize an accepted spec change with mandatory verification replay, OpenSpec close/archival, and synchronized project documentation updates. Use when a change is accepted and must be closed cleanly with evidence.
---

# spec-closeout

## Use This Skill When

Use this skill when implementation is already done and the user asks to close or finalize the change, for example:
- "change ist akzeptiert, schließe spec/open-spec"
- "update spec status and docs"
- "final closeout" / "abschluss"

Do not use this skill for feature implementation. Use `spec-change-delivery` (Workflow 2) or the legacy direct implementation run (Workflow 1) for implementation.

## Workflow Compatibility

This closeout can finalize accepted changes from both workflows:
- Workflow 1: `spec -> refine-plan -> direct-mode implementation -> (optional) spec-closeout`
- Workflow 2: `spec -> spec-change-delivery -> (optional) spec-closeout`

## Core Outcome

Close one accepted change with a strict evidence gate:
1. all required verification commands are executed and reported,
2. OpenSpec change is closed when possible,
3. spec status and project documentation are synchronized,
4. final verdict is `READY` or `NOT READY`.

## Canonical References

Use these as source of truth:
- Shared workflow gates (DoR/DoD, Parallel Work Control Surface, Mini-Retro): `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md`
- Delivery behavior and verification rigor: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-change-delivery/SKILL.md`

For Parent/Child closeout, the Child Index is the operational closeout control surface. It must reflect accepted evidence, OpenSpec/archive state, parent coverage, deferred scope, the next child action, and the next child `Session Handoff` pointer before any next child becomes leading.

## Required Inputs

1. Repository path containing the implementation.
2. Spec file path to finalize.
3. OpenSpec change id or path (if OpenSpec is used).
4. Project docs root.
   - Default for NCG: `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs`
5. Parent/Child role of the target spec when applicable (`parent`, `child`, or `normal`).

If input 4 is omitted and context is NCG, assume the default above.

## Non-Negotiables

1. Every command listed in the spec `Verification` section is a hard checklist item.
2. Never silently skip verification commands.
3. If a required verification command fails or is blocked, final verdict must be `NOT READY`.
4. OpenSpec is closed only after required verification is green.
5. Documentation sync is mandatory at the appropriate level: normal specs sync project docs directly; child specs sync parent/index/backlog/OpenSpec evidence first; parent closeout runs the broad project docs sync.
6. Do not mark spec as accepted if evidence is incomplete.
7. Do not mark a child spec as accepted while Parent Coverage, Child Index/Slice Plan, Backlog/Re-entry, Evidence Links, OpenSpec Status, or Child Session Handoff state are stale or contradictory.
8. Do not advance the next leading child until the previous child closeout sync is complete and the next child handoff is current, or explicitly blocked/stale in the Child Index.

## Closeout Workflow

### 1) Build Closeout Contract

Capture briefly before edits:
- In scope closeout artifact(s)
- out of scope
- required verification command list
- docs to check for synchronization

### 2) Run Required Verification

1. Parse the spec `Verification` section.
2. Execute each listed command from the correct working directory.
3. Record one result per command with `ran`, `failed`, or `blocked`.
4. Keep key evidence (exit status + short meaningful output).

If any required command is `failed` or `blocked`, stop closeout updates that would imply completion and return `NOT READY`.

### 3) Close OpenSpec Change (when applicable)

If change uses OpenSpec and verification is fully green:
1. Validate active change exists (`openspec list --json`).
2. Archive/close change (`openspec archive -y <change-id>`).
3. Confirm archive path and resulting canonical spec path.
4. Record those paths in the closeout report and (if appropriate) in the spec file.

If OpenSpec cannot be closed, report blocker and return `NOT READY`.

### 4) Update Spec Status

Update target spec file with:
1. header status set to `🟢 Accepted`,
2. execution result summary for required verification commands,
3. OpenSpec close status (if applicable),
4. one new history row (`Date | Author | Change`) with a short closure summary sentence,
5. `SessionId` preserved (or added if missing).

### 5) Synchronize Parent/Project Documentation

For normal specs and Parent Spec closeout, check and update project docs root (NCG default below):
- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs`

RAG-first source discovery is mandatory before deciding which docs to update:
1. Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/rag-documentation-research/SKILL.md`.
2. Start with `rag` retrieval/workflow commands to build a prioritized source shortlist.
3. Use `qmd` only as optional discovery add-on when `rag` results are too narrow.
4. Keep source-backed evidence for why each updated (or skipped) documentation file was selected.

Minimum docs sync checks:
1. Search for references to the spec title/path and OpenSpec change id.
2. Check parent spec, index/overview pages, and deferred-topic trackers when present.
3. For child/parallel-lane closeout, check parent coverage, child index, slice plan/backlog, and integration-owner notes for stale write-set, shared-file, verification, or merge-order references.
4. Update dependent docs if status/progress references are now stale.
5. If no additional update is needed, explicitly state this with the search evidence used.

Parent/Child-specific rule:
1. Child closeout must sync Parent Coverage, Child Index/Slice Plan, Backlog/Re-entry items, OpenSpec/Evidence links, integration-owner notes, and next Child Session Handoff before the next child becomes leading.
2. Child closeout runs broad project docs sync only when the child changed user-facing/project docs or would make public contract documentation stale.
3. Parent closeout runs the broad project docs sync and confirms the child set, coverage, accepted evidence, deferred scope, and public docs are aligned.

Child closeout sync details:

1. Parent Coverage: mark covered requirements as `done`, `partial`, `blocked`, `pending`, or `out_of_scope` with evidence links; never let an uncovered parent requirement disappear.
2. Child Index/Slice Plan: update child status, hardening/delivery/closeout verdict, `Session Handoff` pointer, dependencies unblocked or still blocked, next action, next leading child, and allowed write-set/shared-file notes.
3. Backlog/Re-entry: move deferred or narrowed scope into a named child/backlog row with trigger, dependency, and done signal.
4. Evidence Links: link implementation evidence, verification replay, changed artifacts, docs updates, and any blocked commands.
5. OpenSpec Status: record active, archived, canonical spec path, or blocked status; if OpenSpec archive fails, keep closeout `NOT READY`.
6. Handoff: update or create the next persisted Child Session Handoff so it points to current parent/index/evidence/OpenSpec state. If the next child is not allowed to proceed, keep or create the handoff but mark its verdict/notes as blocked or stale in both the file and the Child Index.

Parent closeout sync details:

1. Confirm every child row has accepted evidence, explicit deferral, or a blocker/re-entry destination.
2. Confirm Parent Coverage and Child Index agree.
3. Confirm OpenSpec canonical specs/archive paths are aligned with accepted children.
4. Run broad RAG-first project docs sync and update stale public/project docs when needed.
5. Record deferred scope and next re-entry path rather than hiding it in a final summary.

### 6) Capture Mini-Retro

Before final closeout messaging or handoff, capture the shared Mini-Retro checkpoint:
1. What was decided?
2. What changed?
3. What remains open?
4. Which evidence/verification is missing?
5. Which skill/workflow friction showed up?
6. Session/context state: continue here or start a new session?

Keep it short. Escalate to `retro-plan` only when the checkpoint reveals planning failures, repeated rework, or workflow/skill deltas worth preserving.

## Output Contract

Respond with:
1. Scope closed
2. Verification checklist (every required command with `ran`/`failed`/`blocked`)
3. OpenSpec closure status and paths
4. Synchronization result:
   - normal spec: project docs updated, or explicit "none needed" with basis,
   - child spec: Parent Coverage, Child Index/Slice Plan, Backlog/Re-entry, Evidence links, OpenSpec Status, integration-owner notes, and next persisted Child Session Handoff synced; broad project docs sync only if triggered,
   - parent spec: broad project docs sync plus child set, coverage, accepted evidence, OpenSpec archive/canonical status, and deferred scope alignment.
5. Changed artifacts
6. Mini-Retro
7. Final verdict: `READY` or `NOT READY`

Never claim completion without the verification checklist and appropriate sync result.

## Blocked Path

When blocked, still provide:
1. commands attempted,
2. exact blocker,
3. smallest next step to unblock,
4. final verdict `NOT READY`.
