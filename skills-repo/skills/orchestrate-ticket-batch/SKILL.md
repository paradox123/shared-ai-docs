---
name: orchestrate-ticket-batch
description: "Orchestrate a finite ticket batch with up to three independent Codex worktree tasks in parallel by default, evidence-based acceptance, serialized merges to a user-specified branch and verified cleanup. Use for batch implementation or orchestrator sessions, not local implementation of one ticket or operation of a separate agent-pilot service."
---

# Orchestrate Ticket Batch

Coordinate a finite batch through implementation, evidence-based acceptance, delivery and owned-resource cleanup. Workers implement; the coordinator judges evidence and uses the task tools. The local CLI owns mechanical state, correlated reports, command packets and reservations. It never grants authority or executes external tools.

Require an **explicit user target branch** before dispatch; never infer main, the default or current branch. Reuse a previously explicit target for the same batch. If the target does not exist, obtain its intended starting ref. A batch-execution request normally includes commit/push/merge to that target, ticket closure, evidence retention and owned worktree/branch/task cleanup; state that scope once. Planning-only or narrower instructions override it. Preserve actual tool permissions.

## Start or resume

1. Read repo AGENTS/README, tickets and relevant specs. Freeze the finite ticket list, original authorization, dependencies and foreseeable file/interface/mutable-resource conflicts. Resolve uncertain overlap before parallel dispatch. Prototypes are inspiration, not requirements.
2. Resolve project and known workers. Initialize managed state in step 3 before creating any new worker. New workers use dedicated worktrees and owned branches from the explicit target via `create_thread`; follow current task-creation authority. Never duplicate an existing ticket worker. Directly confirm IDs, ownership and fresh remote base; `clientThreadId` is provisional. Honor the required initial wait and created-task directive. Read [recovery-and-state.md](references/recovery-and-state.md) only for missing identity, interruption, old-ledger adoption or permission failure.
3. For a new batch read [local-helpers.md](references/local-helpers.md), initialize a managed ledger outside disposable worktrees, and use `status` for compact context thereafter. Keep old ledgers on their existing workflow until explicit adoption. Establish the role profile and bounded-work rules in [efficient-execution.md](references/efficient-execution.md).
4. Record a usable continuation mode: verified callback wake; callbacks plus an authorized recovery heartbeat; otherwise bounded active waits. Messaging availability alone does not prove idle wake. Configure/reuse scheduling through build-codex-automations only when authorized. A recovery wake performs one compact observation pass, processes actionable changes and ends; it is not a new polling loop.

## Coordinate decisions

Use `coordinate` to prepare commands and record outcomes. Dispatch the generated packet's `message` through the appropriate task tool only after preparation succeeds. New commands get new identities; unknown sends remain pending and must be reconciled. `status` returns the packet path and next required decision. Workers use [worker-events.md](references/worker-events.md) to persist reports and return callback text. No manual sequence arithmetic, receipt hashing or JSON ledger patches are needed.

Consume an event with the CLI; optionally include the inspected next decision in the same operation. Duplicate/stale events do not repeat commands. A new ready report means evidence is available, not accepted. Open the actual measured results/screenshots and compare them with ticket criteria. Green counts and tool idle status alone are insufficient.

- **Implementation ready:** inspect substantive expected/actual evidence and bind the decision to reported contents. Prepare the delegated change-accepted command. That skill owns critical verification followed by code-review; do not duplicate its review workflow.
- **Technical completion ready:** inspect the current completion record; advance to awaiting integration. Findings produce scoped repair commands to the same worker, preserving valid evidence and requiring fresh proof for changed behavior.
- **Integration:** read [parallel-delivery.md](references/parallel-delivery.md). Reserve the single target slot through preparation, grant and remote confirmation. Verify the final candidate, PR base/head, required checks and current target. Bind a specific grant to candidate and tested target; changes require relevant revalidation and substantive changes require renewed acceptance.
- **Delivery and cleanup:** verify remote merge, accepted-content mapping, ticket closure and worker quiescence. Retain inspectable evidence outside every worker worktree before guarded cleanup. Record each operation's actual outcome; only then mark done.

The helper enforces declared dependencies/conflicts and capacity, but cannot discover overlap or verify external facts. Inspect affected evidence and required live facts; do not inventory the whole batch for each callback. Fill eligible slots after actionable transitions. Parked workers retain conflict reservations; uncertain creates/merges retain capacity. Never route a denied operation through another identity or tool.

## Wait and finish

When only waiting remains, checkpoint the current outcome and end the turn if the recorded background continuation works. Otherwise continue bounded `wait_threads` with confirmed IDs, hosts and latest cursors within current runtime limits. Do not add detailed reads, messages or shell checkpoints to unchanged timeouts. A timeout is not completion. Explicit user stop means checkpoint for manual resume.

Record available usage only at milestones. Bundle pure versioned status/archive bookkeeping into one batch closeout when repo policy permits; required pre-merge documentation and productive activation evidence remain per ticket. Track and verify deferred delivery. A delivered prerequisite can unlock work while cleanup continues; the batch is complete only after delivery, closeout and owned cleanup are verified. Pause only its recovery heartbeat and report durable evidence plus exact retained resources or blockers.
