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
- Shared workflow gates (DoR/DoD): `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md`
- Delivery behavior and verification rigor: `/Users/dh/.agents/skills/spec-change-delivery/SKILL.md`

## Required Inputs

1. Repository path containing the implementation.
2. Spec file path to finalize.
3. OpenSpec change id or path (if OpenSpec is used).
4. Project docs root.
   - Default for NCG: `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs`

If input 4 is omitted and context is NCG, assume the default above.

## Non-Negotiables

1. Every command listed in the spec `Verification` section is a hard checklist item.
2. Never silently skip verification commands.
3. If a required verification command fails or is blocked, final verdict must be `NOT READY`.
4. OpenSpec is closed only after required verification is green.
5. Project documentation sync is mandatory, not optional.
6. Do not mark spec as accepted if evidence is incomplete.

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

### 5) Synchronize Project Documentation

Always check and update project docs root (NCG default below):
- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs`

Minimum docs sync checks:
1. Search for references to the spec title/path and OpenSpec change id.
2. Check parent spec, index/overview pages, and deferred-topic trackers when present.
3. Update dependent docs if status/progress references are now stale.
4. If no additional update is needed, explicitly state this with the search evidence used.

## Output Contract

Respond with:
1. Scope closed
2. Verification checklist (every required command with `ran`/`failed`/`blocked`)
3. OpenSpec closure status and paths
4. Documentation updates performed (or explicit "none needed" with basis)
5. Changed artifacts
6. Final verdict: `READY` or `NOT READY`

Never claim completion without the verification checklist and docs-sync result.

## Blocked Path

When blocked, still provide:
1. commands attempted,
2. exact blocker,
3. smallest next step to unblock,
4. final verdict `NOT READY`.
