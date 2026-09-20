## Context

This is an agent-operated Codex Desktop workflow, separate from the LangGraph/Microsoft Agent Framework pilots. The implement skill owns per-ticket engineering. The accepted interview is recorded in parallel-batch-design.md; the existing active change keeps its historical name.

## Goals / Non-Goals

Goals: short invocation with ticket scope and explicit target, bounded independent parallelism, isolated worktrees, reliable recovery, inspectable acceptance, serialized delivery and safe cleanup.
Non-goals: implement product code in the coordinator, bypass approvals, guarantee scheduler liveness, modify pilots or build another workflow engine.

## Decisions

- The completion extension in [completion-contract-design.md](completion-contract-design.md) supersedes the earlier two-axis review sequence: change-accepted owns critical requirements verification followed by code-review; code-review alone owns structural review and follow-up. Direct work waits for contextual acceptance after implementation and initial tests; authorized coordinators trigger the same entrypoint. Repository instructions and skill callers reference this contract.
- Default to three tickets in flight from registration through delivery confirmation. Count uncertain creations and waiting candidates. Park a blocked worker only after confirming it is quiescent; retain its conflict/dependency reservations. This avoids an unbounded integration queue while unrelated work continues.
- Require the actual user target branch before worker creation. Start every new worker in a separate worktree on a dedicated working branch from that target, verifying the fresh remote base and isolating mutable test resources.
- Build dependency and anticipated file/interface overlap constraints before dispatch. Refill slots after actionable transitions; no whole-wave barrier. Pause unexpected conflicting work safely and reassess.
- Keep separate per-ticket state and one integration reservation per target. An acceptance plus preparation message allows final candidate preparation; a later merge grant identifies the exact head and tested target. Target movement triggers relevant revalidation; substantive candidate changes require renewed acceptance.
- Verify actual remote delivery including squash/rebase mapping and non-default-target issue closure. Retain evidence outside worktrees, verify ownership and absence of unintegrated work, then conditionally remove owned worktrees/refs and archive idle workers. Cleanup is resumable and distinct from delivery.
- Persist mutable state beside the batch automation, keeping stable instructions in the skill. Record each pending action before dispatch and reconcile reality before retry. Only the coordinator writes the ledger.
- Use read_thread/wait_threads for known IDs. The existing stdlib helper reads only session_index.jsonl and emits capped exact-title candidates; direct task verification remains required. Later updated_at values remain eligible.
- Carry original user authority in worker prompts. A denied mutation cannot be rerouted to bypass review. Block only the affected scope and present concrete required approval when necessary.
- Validate this instruction workflow through independent fixture-based forward evaluation and the helper's existing subprocess tests. Technical completion after contextual acceptance uses the central completion contract; the earlier Standards/Spec results remain historical evidence for the preceding helper implementation.
- The token-saving extension in [scripted-batch-design.md](scripted-batch-design.md) adds local compare/checkpoint/manifest/verify/retain commands, preserving the coordinator's decision and execution authority. Put critical verification before final independent review, retain reviewer coverage across deltas, and consolidate pure status/archive closeout work. Use scoped context and the recorded role profile without silently changing global defaults or existing batches.

## Risks / Trade-offs

- Conservative overlap detection reduces parallel throughput in exchange for fewer conflicts; bounded investigation avoids assuming either safety or universal conflict.
- External writers can move the target despite the coordinator's reservation. Recheck before granting and before merging; honor branch protection and verify resulting combined behavior when a race occurs.
- Squash merges break simple ancestor tests. Cleanup needs PR-head-to-merge mapping and guarded deletion; uncertainty retains the work instead of forcing removal.
- Incomplete task listings and interrupted actions require bounded recovery and pending reservations, not duplicate workers or repeated blind mutations.
- Heartbeat latency/runtime downtime remains outside skill control. Process actionable completions during active turns and preserve recovery state.

## Migration Plan

Update the canonical skill; existing discovery links resolve to it. Do not rewrite live automations in this task. On explicit adoption, migrate sequential ledger entries into per-ticket records without losing IDs, authority, evidence or pending actions. Require any previously missing explicit user target and isolate adopted shared-checkout workers before parallel writing. Existing completed deliveries must have cleanup reconciled, not assumed. Other application pilots retain their own policies.
