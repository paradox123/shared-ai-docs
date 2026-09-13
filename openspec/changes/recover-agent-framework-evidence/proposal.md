## Why

Issue 12 requires a schema-valid but incomplete worker result to converge through
bounded evidence recovery rather than strand repository serialization. Issue 11
is accepted and merged, but currently checks completion without reporting the
worker's exact evidence gaps.

## What Changes

- Qualify the original completed result against the trusted plan and retain exact missing criterion/phase pairs.
- Persist a committed capture head and numbered, bounded deterministic capture activities; never start another implementation for evidence recovery.
- Preserve original result, qualification and capture outcomes as correlated redacted history.
- Finish with head-bound draft evidence or an explicit terminal blocker and release repository ownership according to existing publication uncertainty policy.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agent-framework-evidence-publication`: distinguish structural validity and semantic completeness, bound recovery at an immutable head, and converge terminal state.

## Impact

Publication worker, deterministic Python adapter, additive PostgreSQL JSON projection,
public worker/HTTP tests and operator documentation. No new runtime dependency,
merge action, or review qualification. Owning Git root is shared-ai-docs; current
and user-confirmed delivery branch is `main`, baseline `76f4c51`. Worktree was clean.
