# Auto Resolve Review

## Goal
Convert review findings into immediate, bounded edits and re-review loops until stable.

## Steps
1. Review target artifact and emit findings with file/line evidence.
2. Fix all autonomous findings immediately.
3. Re-review touched regions and linked normative sections.
4. Repeat until no autonomous findings remain.
5. Escalate only true decision/missing-information blockers.

## Boundary
Do not escalate for simple wording/consistency/contract-alignment fixes that are safely inferable.
