# Bounded work and context

## Role profile

Daniel's token-saving profile uses Sol/medium for coordination and code-review structural reviewers, Astra/high for implementation and separate critical verification, and scripts for mechanical bookkeeping. At start record requested roles, their authorization and actual runtime selections; disclose a mismatch once. Preserve explicit user choices and current tool restrictions. Do not silently substitute models, change global defaults, restart a task to simulate a model switch or assume a prompt changed the current model. Difficult structural findings may receive a focused Astra/high escalation within the authorized profile.

## Work packets

Add ticket/spec paths, relevant standards, expected scope, base, isolation requirements, original authorization and applicable model profile to the task-specific instruction. The CLI supplies assignment fields and phase rules. Review subagents use fresh context (`fork_turns="none"`) and the scoped packets/receipts owned by [code-review](../../code-review/SKILL.md); do not copy the batch conversation or invent another receipt schema.

For large repetitive work, prove a few complete normal/boundary cases before broad generation. Seek an early decision only when interpretation, method or scope needs it. A valid sample proves the approach, not ticket completion. This is not an extra approval gate for small changes.

Ticket concurrency and nested-agent capacity are separate. Both default to three across the batch; per-worker allowances include nested agents and may be reused for sequential reviews. The CLI reserves capacity. Workers must honor their packet's allowance. Required reviews wait for capacity instead of being skipped. Reallocation requires confirmed quiescence and reconciliation of any old grant; an idle coordinator does not release reservations.

Repairs identify finding, criterion, affected scope, contents and needed evidence delta. The same worker repairs; code-review owns affected rechecks. If a failure recurs or helper rebuilding keeps expanding, secure the useful result, reassess cause/method and provide bounded remaining packages before another equivalent round. Reuse suitable deterministic tools and valid evidence. Do not lower acceptance or call locally solvable work externally blocked to save tokens.

## Metrics and closeout

At real phase milestones record already-available input, cached-input subset, output and optional reasoning subset, owner and coverage interval in compact evidence. Use cumulative-counter deltas and avoid double-counting children. Mark unavailable counters; do not scan transcripts or add polling solely for metrics. Track repair rounds and reserved allowances; the helper counts repair commands. Explicit user budgets take precedence; a rising trend alone does not authorize abandoning work.

After inspected implementation readiness, the coordinator delegates [change-accepted](../../change-accepted/SKILL.md). It owns critical verification and code-review; retain its current completion record and revalidate affected coverage after substantive/target changes.

Record each delivery immediately, unlocking prerequisites independently of cleanup. Keep required spec updates and productive activation proof per ticket. Where repo policy permits, consolidate only pure versioned status/archive bookkeeping into one final change. Reuse an idle verified worker under normal identity, capacity, integration and acceptance rules. Behavioral changes in closeout require change-accepted. Verify that final delivery and cleanup before declaring the batch complete; partial closeout retains undelivered tickets explicitly.
