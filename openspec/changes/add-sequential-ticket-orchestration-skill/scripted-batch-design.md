# Script support for ticket-batch orchestration — design interview

Status: interview started; no implementation or expansion of runtime authority decided.

## User objective and preserved contract

Reduce repeated model reasoning and token consumption by moving mechanically checkable parts of orchestrate-ticket-batch into scripts. Preserve the accepted batch contract: explicit user target, default three independent worktree tasks, conservative overlap constraints, separate critical verification and acceptance, serialized integration, durable recovery and guarded cleanup.

This is an extension of the existing shared skill. Product implementation and the separate agent-pilot/control-plane projects remain outside this change. The user invoked grill-with-docs to clarify scope before specification and implementation.

## Current evidence

The skill currently describes per-ticket state, capacity accounting, dependencies, integration reservations, pending actions and cleanup gates in prose. A read-only metadata candidate helper already exists. Mechanical transition validation, compact next-action output and prompt rendering are candidates for scripting. Interpreting requirements, discovering semantic dependencies and evaluating acceptance evidence still need agent judgment.

## First unresolved decision

What should the first script-supported release execute itself?

Recommendation, not yet accepted: persist and validate state, compute eligible next actions and render complete worker messages. Codex continues executing task tools and Git delivery/cleanup under the existing contract. Add script-executed evidence retention and guarded cleanup in a later increment. This gives an initial usable release with fewer repeated bookkeeping decisions while keeping the first implementation bounded.

Alternative: include script-executed evidence retention and guarded Git cleanup in the first release, accepting the larger delivery and verification scope.

## Questions to reassess after the scope decision

- Whether existing running batches must be adoptable in the first release or only newly started batches use the scripted state.
- Whether any further user-visible failure or execution requirement remains unsettled. Existing uncertain-action and approval rules remain authoritative; do not re-interview already accepted policy.

## Implementation assumptions, not user decisions

Python/SQLite and the name batchctl are proposals, not requirements. Storage and command details can be chosen during implementation unless they change portability or externally visible behavior. No automatic token-saving percentage is claimed; compare equivalent orchestration work to measure the result.

No glossary addition or ADR yet: no new domain term or hard-to-reverse architecture choice has been settled.
