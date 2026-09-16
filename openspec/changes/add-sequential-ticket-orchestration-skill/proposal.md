## Why

Codex task `01a0a8fd-8d65-74b1-aae1-95bcd191fab3` repeatedly stalled because asynchronous worktree creation returned only client IDs, task listings omitted existing workers, and delegated merge authority was rejected. Daniel needs a reusable skill invoked with only the batch scope, preserving visual acceptance and sequential delivery.

## What Changes

- Add `orchestrate-ticket-batch` to the shared skill collection and Codex discovery.
- Define bounded batch scope, per-ticket tasks, durable phase checkpoints, identity recovery, evidence-based acceptance and verified delivery.
- Provide reusable worker, verification, acceptance and heartbeat prompt templates.
- Add a read-only metadata candidate helper with CLI behavior tests; final identity verification stays with task tools.

## Capabilities

### New Capabilities
- `sequential-ticket-orchestration`: Operate a finite ticket batch through dedicated Codex tasks with verified identity and delivery gates.

### Modified Capabilities
None. Existing application pilots and their no-merge contracts remain unchanged.

## Impact

Shared skill files and one runtime discovery link. No application implementation, active automation edits, vendor skill edits, new external dependencies or GitHub mutations.
