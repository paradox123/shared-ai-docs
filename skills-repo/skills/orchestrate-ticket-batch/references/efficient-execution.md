# Context, reviews and batch closeout

## Role profile

For the token-saving profile requested by Daniel, use:

| Role | Model | Reasoning |
| --- | --- | --- |
| Coordinator | `gpt-5.6-sol` | `medium` |
| Implementation and separate critical verification | `gpt-6-astra` | `high` |
| Structural reviewers through code-review | `gpt-5.6-sol` | `medium` |
| Mechanical bookkeeping | Local helper | None |

Record the user's profile authorization and the actual runtime selections in the batch ledger. Preserve later explicit choices. Check the current tool schema: task creation may allow a model override only when the user explicitly requested it. Without that authority, omit the override and use the configured runtime model. Do not replace an unavailable model silently; record the limitation and use an authorized available setting. Escalate a structural finding needing difficult concurrency/persistence reasoning to Astra/high with a focused question; retain the original finding and attribution.

A skill does not switch its own active task's model. Start a coordinator with Sol/medium using the app's model selector; for CLI use `codex -m gpt-5.6-sol -c model_reasoning_effort='"medium"'` when supported by the installed CLI. If already running with another model, disclose this once and continue permitted work. Never edit global defaults or create/restart a task solely to simulate a model change. Task tools use `model`/`thinking`; review subagent tools use `model`/`reasoning_effort` and `fork_turns="none"`. Verify supported values on the destination host. [Official model and reasoning selection](https://learn.chatgpt.com/docs/models).

## Context packets

New worker: ticket/spec paths or contents, relevant standards, expected file/interface scope, fixed starting target SHA, explicit target branch, isolated worktree requirements, authority provenance and phase/delivery contract from messages.md. Existing repository instructions still apply. Link primary sources instead of copying the full batch history.

Reviewer packets and receipts are defined in [code-review](../../code-review/SKILL.md). The coordinator passes the authorized role profile and scoped requirements/evidence; it links the returned completion record rather than maintaining a second receipt schema.

Worker result: current contents, ready/blocked phase, measured acceptance result, test and review artifact paths, limitations and next action. The coordinator opens only evidence needed for its decision. Do not require periodic prose updates or callbacks when the normal completion result is sufficient.

## Technical completion

Use [change-accepted](../../change-accepted/SKILL.md) after the coordinator's substantive acceptance of an implementation-ready candidate. It owns requirements verification followed by code-review. The coordinator inspects evidence, records the technical outcome and retains separate integration authority; it does not override implement or repeat the review instructions.

Record a path to the current completion record in the batch ledger. Local checkpoint commits do not grant delivery. Preserve applicable checks after target movement and use the common record to reopen affected coverage. Existing batches retain prior receipts as historical evidence; reconcile their coverage with the current contract only on explicit adoption, never invent missing review outcomes.

## One consolidated closeout

After each verified merge, record PR/head/merge/target, accepted-content mapping, ticket closure and deferred versioned status/archive paths in the ledger. This immediately unlocks delivered prerequisites. Keep evidence retention and owned-resource cleanup per ticket.

Do required specification updates and validation before each implementation merge. Keep productive activation, restart/persistence or deployment proof with its own ticket. A repository rule requiring per-ticket archive/docs before merge wins; record that exception. Otherwise defer only pure bookkeeping, including archive moves, to one batch closeout change. Do not create an automatic second PR per ticket for a checked task box or merge link.

At batch end, collect deferred paths and merge facts into one closeout change on an owned branch/worktree from the explicit target. Reuse an idle verified worker when practical; obey actual task-creation authority. Reserve the integration slot, inspect the complete documentation diff, run required OpenSpec/docs checks, bind acceptance to the closeout head and target, and use the normal preparation and specific merge grant. If the diff adds behavior, route that portion through change-accepted. Verify the remote closeout merge and cleanup before marking the batch done. If externally blocked, a partial closeout may record delivered work while explicitly retaining outstanding tickets; never mark undelivered work complete.
