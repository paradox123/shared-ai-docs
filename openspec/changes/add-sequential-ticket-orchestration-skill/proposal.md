## Why

Codex task `01a0a8fd-8d65-74b1-aae1-95bcd191fab3` repeatedly stalled because asynchronous worktree creation returned only client IDs, task listings omitted existing workers, and delegated merge authority was rejected. Daniel needs a reusable skill retaining visual acceptance and recovery. The accepted extension replaces sequential implementation with conservative parallel work, a mandatory user-selected delivery branch and cleanup after delivery.

## What Changes

- Maintain `orchestrate-ticket-batch` in the shared collection and existing Codex discovery link.
- Freeze a finite ticket batch; run up to three independent workers by default, each in its own worktree, with a user override for concurrency.
- Require the user to name the target branch before dispatch; serialize overlapping changes and integration into that target.
- Retain critical verification, evidence-bound acceptance, permission provenance and durable identity recovery; track all workers and pending operations individually.
- Preserve evidence outside worktrees before removing owned worktrees/working branches and archiving worker tasks.
- Update reusable worker, verification, integration and heartbeat prompts. Retain the read-only metadata helper and its CLI behavior tests.

## Capabilities

### New Capabilities
- `sequential-ticket-orchestration`: Finite Codex ticket-batch orchestration with verified identity, parallel implementation, serialized delivery and cleanup. The identifier is retained from this active change's original sequential version.

### Modified Capabilities
None. Existing application pilots and their no-merge contracts remain unchanged.

## Impact

Shared skill files, catalog and batch glossary; no application implementation, active automation edits, vendor edits or new external dependencies. The skill is published in the shared repository for use on other computers with the existing skill-sync setup.
