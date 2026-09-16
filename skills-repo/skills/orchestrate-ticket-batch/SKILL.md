---
name: orchestrate-ticket-batch
description: "Orchestrate a finite batch of tickets sequentially in dedicated Codex tasks, with implement/OpenSpec routing, independent acceptance, durable recovery and verified merge. Use when the user asks for a ticket batch or an orchestrator session; not for implementing one ticket locally or operating a separate agent-pilot service."
---

# Orchestrate Ticket Batch

Run the named batch from ticket selection through accepted delivery. Keep this task as the coordinator: read requirements, dispatch, inspect evidence, request repairs and verify delivery. Put implementation, tests, OpenSpec changes and Git delivery in each ticket's dedicated Codex task.

A short invocation is sufficient: `$orchestrate-ticket-batch Bearbeite paradox123/probare-crm #7–#13.` Optional inputs are an order, target branch, prototype/reference, existing worker or stopping point. When the user requests batch execution with this skill, the default requested workflow is implementation, critical verification, coordinator acceptance, then commit/push/merge and ticket closure. State this scope once and proceed; do not ask for the same authorization again. A request only to plan/review does not authorize execution. Actual tool permissions and explicit user limits still govern; a skill is not an approval bypass.

## Establish the batch

1. Resolve the owning repository, applicable AGENTS/README, issue tracker, target branch and original user request. Use repository-prescribed tracker tools (for example `gh`). Read enough ticket detail to establish dependencies and acceptance criteria; leave implementation discovery to workers.
2. Expand the requested range/query to an explicit finite list. Snapshot “all open tickets” at start. Preserve user order where dependencies permit; explain necessary reordering. Do not silently add new tickets or prerequisites outside the batch. Closed tickets require no new worker; record their actual status and delivery evidence where relevant.
3. Resolve the Codex project with `list_projects`. For Git repositories use an isolated worktree unless the user explicitly chose the saved checkout. Use the configured model without override. Resolve `$implement` from the skill catalog/shared collection; in Daniel's setup the canonical vendor entry is `~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/vendor/mattpocock/.agents/skills/implement/SKILL.md`. Resolve its absolute path and verify it exists before dispatch.
4. Read repository documentation for any prototype reference. Pass it only as visual inspiration; tickets/specifications define behavior. Do not force a prototype onto unrelated work or invent one when absent.
5. Find any known existing worker/PR for the current ticket before creating a task. An `agent-running` label alone proves neither activity nor ownership. Never run two workers for one ticket or advance while the current ticket is unfinished.
6. Establish the compact ledger and one heartbeat using [recovery-and-state.md](references/recovery-and-state.md). Reuse a matching existing heartbeat. The skill invocation requests sustained batch work, so continuation is within scope. Load `build-codex-automations` when creating/changing its definition; do not duplicate that skill's tool-schema knowledge. Do not alter unrelated automations or pilot services.

## Execute one ticket at a time

Use the phase table as the gate. `idle`/`completed` is a tool execution status, not proof that a ticket is delivered.

| Phase | Required next action | Exit condition |
| --- | --- | --- |
| queued | Check dependencies/current remote base; checkpoint dispatch intent; create or adopt worker | Creation response recorded |
| registering | Resolve and directly verify real task ID | Issue, repository, worker and worktree match |
| implementing | Monitor worker; handle a concrete blocker | Worker explicitly reports implementation ready |
| verifying | Send the separate critical-verification prompt once | Worker completes it with inspectable evidence |
| reviewing | Inspect artifacts and compare outcomes with acceptance criteria | Accept identified contents or request repair |
| repairing | Send outcome-focused findings to the same worker | Revised evidence ready for review |
| delivering | Send acceptance/delivery prompt once; monitor | Worker reports concrete PR/commit and merge result |
| confirming | Read back remote merge, accepted contents and ticket status | Merge and closure verified |
| done | Record evidence and immediately select next eligible ticket | Batch exhausted |
| blocked | Record failed operation and exact recovery condition | New evidence, permission or repaired prerequisite |

### Dispatch and registration

Use [messages.md](references/messages.md) to compose the worker prompt. Substitute real values; never send unresolved placeholders. Include the original user authorization and its source task ID when known, desired branch/base, implement path, repository guidance, evidence expectations and the separate acceptance gate.

`create_thread` can return only `clientThreadId` while worktree creation continues. Save it as a provisional ID; never pass it to `read_thread`/`wait_threads`. Emit the required created-task UI directive with the actual returned ID type. Registration is complete only after a real ID has been directly checked. An empty `list_threads` result does not establish absence. Follow the bounded local recovery in the reference rather than ask the user to find a link or repeat list calls forever.

A worker callback is optional assistance, not a prerequisite for progress. Do not rely on a worker knowing its own ID or being allowed to send messages. Record callback failure without blocking implementation or creating a second worker.

### Monitoring and continuation

Use `wait_threads` on the confirmed ID with its latest cursor; use targeted `read_thread` when completion, error or required action needs explanation. Normalize JSON-string/tool content once; turns are top-level `turns`, with `page.turns` only as a compatibility fallback. Start a first read with only `threadId` where tool versions require the minimal call.

During an active run, continue bounded waits (up to 60 seconds each) and process changed state immediately. A timeout means “still waiting”, not “batch complete”. Do not deliberately stop after a one-second probe and leave every transition to a ten-minute timer. Keep user updates meaningful; do not narrate unchanged polls. If ending a run is necessary, checkpoint the next action first; the heartbeat is recovery, not proof of continuous execution. Never promise an exact wake time or progress while the app/runtime cannot execute.

Read ledger and reconcile live worker/remote state on resume. Persist a pending action before every create/send/merge request and its result afterward. If interrupted between them, inspect whether the action occurred before retrying. There is no assumed idempotency key on these tools. Do not use a stale cursor or missing response as grounds for duplicate dispatch.

### Verification and acceptance

After initial implementation, send a **separate** critical-verification request even if the worker already claims green tests. Require it to challenge coverage and close gaps itself, then present evidence for the resulting state.

Actually open screenshots with an image tool or the running/rendered report with file/browser tools. For nonvisual work, inspect a readable measured result with expected/actual values; do not manufacture screenshots of a checklist as proof. Check coverage of ticket criteria, relevant failure paths and persistence/restart/idempotency where affected. Test counts support evidence but do not replace it. Screenshots do not prove backend invariants.

Tie acceptance to a commit SHA or a reproducible manifest/fingerprint of the uncommitted implementation. Check that the evidence describes that state; a mismatch or substantive later edit invalidates acceptance until reverified. Archive-path/documentation-only bookkeeping may be reconciled explicitly without pretending it is a product change. Keep absolute artifact paths and concise evidence references in the ledger, not raw logs.

Do not repeat the whole implementation or review every internal detail. When a result is wrong or evidence is missing, identify the unmet criterion or observed outcome and let the worker diagnose and repair it. Repeated unchanged failures require a concrete blocker analysis rather than unlimited identical prompts.

### Delivery and permission failures

Send acceptance only after the evidence gate passes. Worker closes/archives OpenSpec if applicable, validates, commits on its confirmed delivery branch, pushes and merges to the agreed target, respecting required checks and branch protection. No force push or bypass. Any substantive conflict resolution returns to verification.

Preserve original user authorization provenance; coordinator acceptance is a quality decision, not newly invented user consent. If automatic approval rejects a mutation, inspect the stated reason. A bounded retry is appropriate only with new evidence that addresses it or actual new user approval. **Do not move the rejected merge into the coordinator, another account, API or task to evade the rejection.** If direct user approval is required, provide one concrete approval request with worker link, PR, target and head. Explain the automatic rejection separately; record `blocked: approval-required`. No repeated blanket permission requests for already-authorized work, and no claim that future approval checks can be guaranteed to pass.

Read back the PR's merged state, target branch and merge commit with the tracker API/CLI. Verify the accepted contents are included (allow squash/rebase commit mapping); check issue closure explicitly. “Pushed”, “PR open”, local `main`, or worker “done” alone are insufficient. Preserve dirty user checkouts; worker may fast-forward a clean checkout, but fresh remote target is the next worker's source of truth.

## Finish

Start the next eligible ticket in the same run after confirmed delivery. When the frozen batch is exhausted, pause only this batch's heartbeat and report tickets, PR/merge links, evidence locations and any real exceptions. Do not mark unresolved tickets complete or extend scope. Keep the ledger so the batch can be audited or resumed.
