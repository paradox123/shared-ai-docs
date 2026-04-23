---
name: doc-review-autoresolve
description: Automatically resolve review findings in specs/docs and rerun review until no autonomous inconsistencies remain. USE WHEN the user asks to review docs/specs and wants findings fixed immediately (e.g. "reviewe", "fix findings", "reviewe nochmals", "passe Findings an"). Prefer autonomous fix + re-review loops and only ask the user when a real decision or missing requirement blocks safe resolution.
---

# doc-review-autoresolve

## Purpose

Resolve documentation/spec review findings with minimal back-and-forth:
1. review,
2. fix autonomous findings immediately,
3. re-review in the same run,
4. repeat until only true decision blockers remain.

## Shared Workflow Contract

Use `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md` as the canonical reference for:
- marker meaning (`[MISSING ...]`, `[DECISION ...]`, `[REVIEW ...]`, `[BLOCKED ...]`),
- DoR/DoD expectations,
- history/session requirements.

This skill must not introduce conflicting gate definitions.

## Trigger Conditions

Use this skill when the user asks to:
- review specs/docs,
- apply review findings,
- resolve inconsistencies automatically,
- re-review after edits in the same thread.

Typical prompts:
- "reviewe die spec"
- "passe es an"
- "reviewe nochmals"
- "fix die findings"
- "mach das automatisch"

## Default Mode (Auto-Resolve)

Default behavior is **autonomous resolution**:
- Do not stop after listing findings when a safe textual/spec correction is possible.
- Apply fixes directly.
- Re-run review immediately.
- Continue until no autonomous findings remain.

## Stop-and-Ask Boundary

Ask the user only if one of these applies:
1. Multiple valid fixes with materially different product behavior.
2. Security/legal/compliance/policy implications.
3. Missing requirement or unresolved decision that cannot be inferred safely.
4. Any marker that requires owner input to close (`[MISSING ...]`, `[DECISION ...]`, blocking `[REVIEW ...]`).

If none apply, resolve findings without waiting for confirmation.

## Review-to-Resolution Loop

1. **Collect findings**
   - Review target docs/specs with file+line references.
   - Prioritize by severity/risk.

2. **Classify each finding**
   - `autonomous`: can be fixed safely now.
   - `needs-decision`: blocked by requirement/decision gap.

3. **Patch autonomous findings**
   - Apply minimal, targeted edits.
   - Preserve scope and existing accepted decisions.

4. **Re-review immediately**
   - Re-run focused review on touched sections and cross-references.
   - Catch regressions/secondary inconsistencies.

5. **Repeat until stable**
   - Stop when either:
     - no findings remain, or
     - only `needs-decision` findings remain.

6. **Report clearly**
   - What was fixed.
   - What remains and why user input is required.
   - Final state: clean vs pending decisions.

## Spec Hygiene Rules

When touching spec files:
- keep header contract intact,
- preserve `SessionId`,
- append one concise history row for meaningful changes,
- do not silently weaken acceptance/verification gates,
- keep parent/child specs consistent where one references the other as normative source.

## Output Contract

After each run, report:
1. **Applied fixes** (file + line references).
2. **Residual findings requiring user decision** (if any).
3. **Re-review result** (`no findings` or list of remaining blockers).
4. **Smallest next step** only when user input is needed.

Never claim "done" while unresolved blocking decision findings remain.
