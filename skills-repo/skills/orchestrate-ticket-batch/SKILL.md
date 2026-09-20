---
name: orchestrate-ticket-batch
description: "Orchestrate a finite ticket batch with up to three independent Codex worktree tasks in parallel by default, evidence-based acceptance, serialized merges to a user-specified branch and verified cleanup. Use for batch implementation or orchestrator sessions, not local implementation of one ticket or operation of a separate agent-pilot service."
---

# Orchestrate Ticket Batch

Coordinate the named batch through accepted delivery and cleanup. Put product implementation, tests, OpenSpec changes and Git delivery in dedicated Codex tasks; keep this task focused on scheduling, evidence, recovery and acceptance.

Example: `$orchestrate-ticket-batch Bearbeite paradox123/probare-crm #7–#13, Zielbranch release/cockpit.` **Require an explicit target branch from the user before dispatch.** Never infer it from main, the default branch or the current checkout. If missing, ask for that single required input while performing independent read-only preparation. Reuse a previously explicit target when resuming the same batch. The target must exist; if absent, obtain its intended starting ref before creating it, rather than guessing.

Default scope of a batch-execution request: implement, separately verify, inspect and accept evidence, commit/push/merge to the named target, close delivered tickets, retain evidence and remove owned worktrees/working branches and archive worker tasks. State this scope once and proceed within actual tool permissions. Planning-only requests do not authorize execution. Optional inputs: concurrency limit (default **3**), priorities, prototype/reference, existing workers or stopping point. Explicit narrower user scope wins; a skill is not an approval bypass.

## Establish the batch

1. Read repository AGENTS/README and relevant ticket/specification guidance. Resolve repository, remote, user-named target and original authorization. Use the repository-prescribed tracker tools. Expand the requested range/query into a finite list; freeze “all open tickets” at start. Do not silently add new tickets or out-of-batch prerequisites.
2. Map ticket dependencies and anticipated file/interface changes from tickets and a bounded repository inspection. Keep conservative parallel eligibility: dependencies must already be delivered on the selected target, and concurrent tickets must have clearly separate changes. Foreseeable overlap in files/interfaces, migrations, shared generated outputs or test resources is a serialization constraint even without a functional dependency. Uncertain overlap needs focused investigation, not an optimistic launch. Use ticket order/priority as a tie-breaker, not a global barrier.
3. Resolve the project with `list_projects`; use `environment.type=worktree` and the **explicit target branch as startingState**, not the project's default branch. Every new implementation task in this batch gets its own worktree and owned working branch. Never run concurrent writers in a saved/shared checkout. Adopt an existing worker only after verifying identity and isolation; preserve its work if it requires safe relocation first. Use the role profile and runtime limits in [efficient-execution.md](references/efficient-execution.md); preserve explicit user model choices.
4. Resolve the active shared `$implement` and `$change-accepted` skills under `skills-repo/skills`, not the preserved vendor snapshot. Pass their verified absolute paths. They own implementation and technical completion for both direct and delegated work; no batch-specific review override is needed.
5. Read any documented prototype reference and pass it as visual inspiration only. Tickets/specifications determine behavior; do not infer new gates, states or scope from a prototype.
6. Locate known workers/PRs and establish one batch ledger/heartbeat using [recovery-and-state.md](references/recovery-and-state.md). Labels and task-list omissions do not prove ownership or absence. Never create a second worker for the same ticket. Reuse a matching heartbeat; load `build-codex-automations` when changing its definition. Do not alter unrelated automations or pilots.

Read [parallel-delivery.md](references/parallel-delivery.md) before scheduling or cleanup; it defines slot accounting, conflict handling, integration and deletion gates.

## Run the batch

Maintain phases **per ticket**, not one global “current ticket”. `idle`/`completed` is a tool execution status, not proof of accepted delivery.

| Phase | Next action | Exit condition |
| --- | --- | --- |
| queued | Select an eligible ticket within the limit; checkpoint dispatch intent | Create/adoption response recorded |
| registering | Resolve and directly verify real task ID and isolated worktree | Ticket, repository, target/base and worker match |
| implementing | Implement, stabilize fixtures and gather behavioral evidence | Worker reports ready for substantive acceptance |
| verifying | Issue the delegated change-accepted request once; track requirements verification | Critical evidence is ready for independent review |
| reviewing / repairing | Track code-review and its completion record | Evidence and current reviewed contents accepted |
| awaiting-integration | Wait for the one integration slot for the target | Slot reserved for this worker and target revision |
| integrating | Prepare final candidate against current target; check evidence | Accepted candidate plus target revision confirmed |
| delivering | Issue specific merge authorization to slot holder | Worker reports merge result |
| confirming | Read remote merge, accepted contents and ticket state | Delivery and closure verified |
| cleanup | Retain evidence, remove owned worktree/branches, archive worker | Cleanup checklist verified |
| done | Record result; refill eligible slots | Batch exhausted |
| blocked | Record cause, affected scope and recovery condition | Fresh evidence, permission or repaired prerequisite |

Fill free slots with eligible tickets and refill after relevant transitions in the same run. One blocked ticket holds its dependents and overlapping work; unrelated eligible tickets may continue unless the blocker affects the whole batch. Track delivery separately from cleanup: a cleanup-only failure does not undo a confirmed merge or block unrelated work, but remains unfinished batch work.

### Dispatch and identity

Compose assignments with [messages.md](references/messages.md), replacing all placeholders. Include the exact user target, remote base, isolated worktree instruction, original authorization provenance, ownership limits and separate acceptance/merge gates. A task may not launch other tickets or choose its own merge time.

Give workers self-contained packets: ticket/spec, relevant standards and files, fixed base, target, authority and phase contract. Do not copy the batch conversation. For review subagents explicitly use fresh context (`fork_turns="none"`), with the packets and review receipts in [efficient-execution.md](references/efficient-execution.md).

Record creation intent and result immediately. `clientThreadId` is provisional; never pass it to `read_thread` or `wait_threads`. Emit the required created-task directive with the actual returned ID type. Registration requires direct verification of the real ID. A missing `list_threads` entry is inconclusive: use bounded local metadata recovery from the recovery reference rather than ask the user for a link or loop indefinitely.

Worker callbacks are optional assistance. Missing ID knowledge, unavailable tools or a denied callback must not block implementation or lead to another worker.

### Monitor and resume

Use one `wait_threads` call for confirmed active workers, each with its own host and latest cursor; respect the tool's target limit and rotate fairly if a user override exceeds it. Read a task in detail only for relevant completion, error or clarification. Normalize JSON-string/tool content once; use top-level `turns`, legacy `page.turns` only as fallback. Start first reads with `threadId` alone when needed for tool-version compatibility.

Use 60-second bounded waits during an active run and process actionable changes immediately. On unchanged observations, checkpoint the latest cursor without extra file/PR probes, detailed task reads or follow-up messages. Use `batch_state.py compare` and revision-checked checkpoints through [local-helpers.md](references/local-helpers.md); reconciliation after interruption and required pre-mutation checks still apply. A timeout is not completion. Do not intentionally defer every transition to the heartbeat after a one-second probe. Keep updates meaningful; stay quiet on unchanged heartbeat observations. If ending a run is necessary, checkpoint all workers and next actions. A heartbeat provides recovery, not a guarantee of exact wake time or execution while the runtime is unavailable.

Reconcile ledger with workers, remote PRs and actual worktrees before resuming mutations. Record each pending create/send/delivery/cleanup action before dispatch and its outcome afterward. After interruption inspect whether it occurred before retrying; never assume tool idempotency. An uncertain merge or creation retains its reservation until reconciled.

### Verification and acceptance

After inspecting initial implementation evidence, issue the delegated **change-accepted** request. This is substantive acceptance to begin technical completion, not a claim that verification is finished. The shared entrypoint completes critical requirements verification before code-review; track both outcomes without redefining their method or requesting another human acceptance for fully delegated work.

The worker continues through code-review under the same completion request. Inspect its current completion record and link it in the ledger. Review methodology, repairs and evidence reuse belong to that skill; do not dispatch a second generic review. See [efficient-execution.md](references/efficient-execution.md).

Actually open screenshots or rendered reports and inspect measured expected/actual outcomes. For nonvisual work use readable behavioral measurements. A screenshot of a checklist or test count alone is insufficient. Check relevant persistence, restart, idempotency and failure paths through appropriate tests; screenshots cannot establish backend invariants.

Bind acceptance to a SHA or reproducible content manifest **and the target revision used for integration verification**. Later behavior changes or a moved target require relevant revalidation before merge; substantive candidate changes require new acceptance. Reconcile archive-path/documentation-only bookkeeping explicitly. Keep artifacts and compact conclusions in the ledger, not raw logs.

Do not reimplement the ticket in the coordinator. State unmet criteria or observed outcome problems and let the same worker diagnose/repair them. Repeated unchanged failures require a concrete blocker analysis, not identical prompts forever.

### Integration, permissions and cleanup

Parallelize implementation; **serialize integration and merge into the shared target**. Acceptance alone does not grant an open-ended right to merge. Use the preparation and final merge messages in the template reference; check the final candidate and latest target before issuing that worker's merge authorization. No force-pushing implementation or target history, bypassing checks or silently changing PR base to main.

Preserve original user authority; coordinator acceptance is a quality decision, not newly invented consent. If automatic review denies a mutation, inspect its actual reason. Retry only with new evidence addressing it or actual new approval. Never move a denied merge into another task/tool/account to evade review. If direct user approval is required, present one concrete request with worker link, PR, head and target and record the blocker. Unrelated permitted work may continue; safely park/release a ticket-specific blocked integration holder using the reference procedure, never an uncertain mutation. Do not infer broader permission from another ticket's approval.

Verify remote PR merge into the named target, inclusion of accepted contents and ticket closure. Support squash/rebase mapping; a local branch or “PR open” is not delivery. For non-default targets, explicitly close the ticket after verified delivery when auto-close did not run. Do not change the target to obtain auto-close behavior. Only then perform the guarded cleanup in [parallel-delivery.md](references/parallel-delivery.md).

## Finish

Record ticket status and merge evidence in the ledger immediately. Bundle pure versioned status and OpenSpec archival bookkeeping into one batch closeout change when repository policy permits; keep required pre-merge docs and per-ticket productive activation evidence with their tickets. Track deferred closeout work explicitly and verify its delivery before declaring the batch complete. See [efficient-execution.md](references/efficient-execution.md).

A delivered prerequisite can unlock dependent work once it is verified on the target. A ticket is fully done only when evidence preservation and cleanup also succeed. Pause only this batch's heartbeat when all tickets are done; report ticket/PR/merge links, durable evidence paths and cleanup results. If only externally blocked work remains, report that precise state once and follow the saved recovery condition; do not claim completion or retry unchanged destructive operations.
