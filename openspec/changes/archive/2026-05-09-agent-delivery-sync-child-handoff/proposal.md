# Agent Delivery Sync Child Handoff

## Why

Child Session Handoffs are currently assembled from long workflow prose and copied fields. This makes stale verdicts, mismatched write-sets and missing handoff files easy to miss before a later `child-spec-hardening`, `spec-change-delivery` or `spec-closeout` session starts.

## What

- Add `skills-repo/tools/SyncChildHandoff.cs` as a .NET 10 file-based app.
- Read one exact operational Child Index row and render the shared Child Session Handoff template.
- Support `--check`, `--dry-run` and explicit `--write` modes.
- Report deterministic text or JSON findings for missing, stale, mismatched and approximate write-set handoffs.
- Preserve only the explicit `## Notes Preserved By Sync` manual section while overwriting controlled fields.
- Add synthetic fixtures for generate, current check, stale verdict, dry-run no-write, preserve notes and approximate write-set blocking.

## Impact

- Gives workflow agents a deterministic companion tool before handoff launch/readiness checks.
- Reduces duplicated handoff-template prose in future skill integration work.
- Keeps this change isolated from `spec-orchestrator/SKILL.md`, real `_specs/child-session-handoffs/*.md` files and any agent-session launch behavior.
