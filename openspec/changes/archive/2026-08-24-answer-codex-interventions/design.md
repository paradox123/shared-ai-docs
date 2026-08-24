## Context

The workflow already persists run ownership and every implementation, review, repair, feedback, and recovery effect, but agent-node contracts express an interruption inconsistently. Initial implementation has only `completed`/`blocked`, reviews have only pass/fail/not-applicable, and repair turns a policy interruption into a terminal label. None provides a durable, answerable intervention identity.

Codex remains a worker rather than workflow persistence. The official Codex App Server documentation now distinguishes a stable protocol surface from methods and fields that require `capabilities.experimentalApi`. The installed command still carries an experimental CLI label, so this change must explicitly constrain production use to the documented stable stdio methods and fail closed when the runtime cannot establish that surface. `exec-server`, WebSocket transport, experimental capabilities, and raw Codex storage remain excluded.

## Goals / Non-Goals

**Goals:**

- Use the existing interrupt policy unchanged in implementation, review, and repair.
- Persist one redacted intervention before Codex delivery and expose its request, session, answer, and continuation through HTTP read-back.
- Let one Codex App answer resume the same LangGraph thread and affected phase in the existing bounded worktree.
- Make delivery, answer capture, continuation, restart, and late repeats converge without duplicate effects.
- Re-run deterministic verification and all fresh independent reviews whenever continuation changes the head.

**Non-Goals:**

- Mirror normal autonomous worker or review sessions in Codex App.
- Add new interruption reasons, let an answer widen the work mandate, or use a Codex session as workflow state.
- Use `exec-server`, `experimentalApi`, WebSocket transport, direct SQLite/rollout parsing, merge, deployment, or release.
- Use ProBara CRM issue #2 as a fixture or acceptance case.

## Decisions

### One canonical intervention contract

A versioned `intervention-request-v1` contract contains repository/issue, run and phase identities, role, bounded worktree or PR head, classification, problem, required decision/action, options and impacts, recommendation and rationale, and preserved findings/results. Agent result contracts carry either no intervention or exactly one contract-valid request. The workflow independently validates and redacts it before persistence.

This keeps the interrupt policy in one vocabulary and prevents a free-form blocked message from becoming an accidental workflow command. Deriving requests later from logs or findings was rejected because it would lose the agent's exact decision boundary and would encourage the controller to synthesize missing context.

### Durable request identity before external handoff

SQLite stores one intervention per stable phase operation key and a lifecycle of `pending_delivery`, `open`, `answered`, `applying`, `applied`, or `delivery_blocked`. The row retains request JSON, Codex thread/turn identity, one answer, and timestamps. Uniqueness on operation key, thread identity, and accepted answer turn makes retries converge.

The issue run remains the repository's active owner while LangGraph is interrupted. It is not changed into a schedulable idle run, so another issue cannot acquire a second worktree or branch during human wait.

### LangGraph interrupt/resume is the continuation boundary

After the phase result is durably stored and its intervention is persisted, the affected graph node calls LangGraph's durable interrupt primitive. An answer reconciliation resumes that same checkpoint thread with an envelope containing only intervention ID, answer turn ID, and redacted answer text. The restarted node reuses completed durable operations, validates the envelope against the open request, and passes the answer as bounded context to the same role and phase.

This is preferred over translating answers into GitHub feedback because that would change the workflow phase and would not work before a pull request exists. It is also preferred over starting another run or using the Codex thread as the checkpoint.

### Narrow Codex App adapter over stable stdio RPC

An `InterventionSessionPort` hides Codex. Its production adapter starts the documented app-server stdio transport, initializes without `experimentalApi`, creates a persistent thread, gives it a deterministic user-facing name, starts one read-only/no-approval turn containing the redacted request, and records the returned thread and delivery turn. Polling uses stable `thread/read` with turns included and accepts the first later user-message turn only. After durable capture, the adapter archives the answered thread so it remains history rather than an open request.

Only `initialize`, `thread/start`, `thread/name/set`, `turn/start`, `thread/read`, and `thread/archive` are allowed. The adapter rejects experimental capability negotiation, non-stdio transports, missing stable methods, malformed identities, and ambiguous history. Direct Codex database or rollout access is never a fallback. The worker persists `delivery_blocked` with a bounded technical reason when this stable surface is unavailable.

### Polling reconciles local Codex state, not GitHub

The existing local heartbeat loop invokes a bounded reconciliation of open intervention sessions in addition to updating liveness. Startup performs the same reconciliation before ordinary run recovery. This is not periodic GitHub polling: it reads only explicitly persisted local Codex thread identities. Test adapters expose deterministic delivery and answers without depending on Codex internals.

### Exactly-once answer application and fresh-head qualification

Answer capture is a compare-and-set from `open` to `answered`; repeated user messages and late reads cannot replace it. Continuation claims `answered` as `applying` under the same stable operation. A crash resumes that operation until the existing phase-specific durable result exists, then marks the intervention `applied`. A second resume envelope is ignored.

The answer is untrusted bounded input: it may resolve only the recorded decision/action within the existing assignment. It cannot alter model policy, permissions, repository, run, worktree, branch, or round limits. Any continuation that produces a new commit follows the existing exact-head publication, deterministic verification, and three fresh independent reviews; no previous evidence or verdict qualifies the new head.

## Risks / Trade-offs

- **[Codex runtime advertises only an experimental command despite documented stable protocol methods]** -> Require a successful non-experimental initialize/method handshake, record `delivery_blocked` otherwise, and do not inspect private storage or enable experimental capabilities.
- **[A user replies more than once before polling]** -> Persist the first later user turn atomically, archive after capture, and expose ignored repeats only as bounded history metadata.
- **[Crash between answer capture and continued external work]** -> Separate `answered`, `applying`, and `applied`; reuse existing phase operation identities and LangGraph checkpoint recovery.
- **[The intervention thread agent tries to act]** -> Create it read-only with approvals disabled and a prompt limited to displaying/capturing the decision; only the pilot's validated continuation worker may write.
- **[Polling delays continuation]** -> Reuse the minute heartbeat and startup reconciliation; correctness and durability take priority over sub-minute response.
- **[Schema additions affect existing fake worker fixtures]** -> Keep nullable intervention fields explicit for strict structured output and migrate fixtures in narrow contract-first slices.

## Migration Plan

1. Add nullable intervention fields/contracts and storage tables in a backward-compatible SQLite setup migration.
2. Add the adapter behind explicit production configuration; startup remains fail-closed when enabled but unsupported.
3. Enable phase interrupts and public read-back only after contract and restart behavior tests pass.
4. Configure the private production environment, restart the LaunchAgent, and run one dedicated marked test issue through the normal ingress.
5. Roll back by disabling the intervention adapter and reverting code; persisted rows remain inert history and no existing run/worktree/PR identity is deleted.

## Open Questions

- None for local implementation. Production acceptance still requires Daniel's deliberate answer in the generated Codex App task and a decisive screenshot; the test must stop before merge or deployment.
