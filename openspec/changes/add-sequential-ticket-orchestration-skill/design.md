## Context

This is an agent-operated Codex Desktop workflow, independent of the LangGraph/Microsoft Agent Framework pilots. The current user request supplies the lifecycle and named batch; the implement skill owns per-ticket engineering.

## Goals / Non-Goals

Goals: start from a short invocation, keep at most one ticket in flight, recover missing IDs, assess real evidence, and advance only after verified delivery.
Non-goals: implement application code in the coordinator, bypass approvals, guarantee scheduler liveness, or build another workflow engine.

## Decisions

- Separate orchestration from implement; put full reusable messages in one reference rather than duplicate them in every heartbeat.
- Persist mutable state beside the batch automation in a compact ledger, keeping stable instructions in the skill. Record pending dispatch before creation; inspect reality before retrying uncertain calls.
- Use read_thread/wait_threads for known IDs. A stdlib helper reads only session_index.jsonl and emits capped exact-title candidates. It does not claim identity or read rollouts. Do not use updated_at as creation time: later activity can move it beyond dispatch.
- Bind acceptance to a commit or manifest, plus inspected artifact paths. Test counts alone do not prove issue completion.
- Carry original user authorization provenance in worker prompts. An approval rejection remains binding; never move the same denied mutation into another task to bypass it.
- Use independent fixture-only forward tests for the complex instruction workflow and subprocess tests for the helper.

## Risks / Trade-offs

- Incomplete task listings → bounded local metadata fallback and direct identity verification.
- Duplicate dispatch after interruption → pending-action record and reconciliation before create/send retries.
- Runtime permission boundaries → one concrete direct-approval request if required; no repeated approval laundering.
- Heartbeat delay/app unavailability → sustained bounded waits during an active turn; persisted recovery state and honest scheduler limits.
- Existing unrelated changes in shared-ai-docs → add scoped files only; do not pull, reset or include unrelated edits.

## Migration Plan

Add skill in the canonical shared collection and a targeted Codex symlink. Existing batch prompts remain untouched; adoption is explicit. Rollback removes only this skill/link.
