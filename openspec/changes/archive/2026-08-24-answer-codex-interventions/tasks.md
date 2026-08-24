## 1. Contracts and durable lifecycle

- [x] 1.1 Add a failing contract slice for complete redacted intervention requests from implementation, review, and repair, then add the shared versioned schema and nullable strict-output fields.
- [x] 1.2 Add a failing public read-back slice for one persisted pre-delivery request and restart-safe active-run ownership, then implement intervention lifecycle storage and serialization.
- [x] 1.3 Add failing idempotency slices for duplicate session delivery, repeated answer turns, and crash-time answer application, then implement stable operation identities and compare-and-set transitions.

## 2. Codex App boundary

- [x] 2.1 Add a failing adapter contract for a named read-only Codex intervention task over the stable non-experimental stdio methods, then implement the session port and fail-closed protocol client.
- [x] 2.2 Add a failing adapter contract for reading the first later user turn and archiving answered history, then implement bounded answer polling without private Codex storage access.
- [x] 2.3 Wire explicit production configuration plus startup/heartbeat intervention reconciliation and document the stable-surface boundary and technical blocker state.

## 3. Same-run phase continuation

- [x] 3.1 Add a failing signed-HTTP slice for initial implementation interruption and same-checkpoint continuation, then integrate durable LangGraph interrupt/resume with bounded answer context.
- [x] 3.2 Add a failing signed-HTTP slice for one review-axis interruption that preserves peer results and immutable head identity, then resume only the affected review operation.
- [x] 3.3 Add a failing signed-HTTP slice for repair interruption inside the same numbered attempt and for exhausted-round intervention without a fourth round, then implement both paths.
- [x] 3.4 Add a failing restart slice proving an answered/applying intervention converges on the same run, worktree, branch, pull request, head, review/repair identities, and external effects.
- [x] 3.5 Add a failing new-head slice proving answer-driven changes invalidate old qualification and execute deterministic verification plus three fresh independent reviews on the exact new head.

## 4. Verification and acceptance

- [x] 4.1 Run focused contract/public-seam tests after each vertical slice, then run the full pytest, Ruff, lock, diff, and strict OpenSpec validations.
- [x] 4.2 Review the touched contracts, modules, specs, and tests for DRY, SOLID, and KISS issues; refactor without behavior change and rerun verification.
- [ ] 4.3 Through the normal productive GitHub/Cloudflare/pilot path, create and authorize one uniquely marked ProBara CRM test issue that deterministically requests an existing-policy intervention and does not touch issue #2.
- [ ] 4.4 Capture the decisive Codex App screenshot, have Daniel answer there, and record public read-back evidence for one request, one accepted answer, same-run continuation, and absence of duplicate worktree/PR/effects.
- [ ] 4.5 Close the test issue without merge or deployment, confirm no test work remains active, and write the bounded implementation evidence artifact.
