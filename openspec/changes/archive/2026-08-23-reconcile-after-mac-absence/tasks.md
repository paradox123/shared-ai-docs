## 1. OpenSpec Contract and Startup Gate

- [x] 1.1 Strictly validate the bounded proposal, capability spec, design, write-set, task plan, and direct productive verification plan before production edits.
- [x] 1.2 Add one public-seam failing test for first-start, below-threshold, and exact-24-hour boot evaluation with real SQLite and controlled clock/boot ID; implement the additive liveness and durable boot-run store contract.
- [x] 1.3 Add one public-seam failing test for same-boot process restart and interrupted-run reuse; implement production boot-ID resolution and once-per-boot startup claiming.

## 2. Current-State Reconciliation

- [x] 2.1 Add one failing adapter/public workflow test for discovering a missed ready/authorized issue and a human-merged active pull request; implement the bounded repository reconciliation snapshot.
- [x] 2.2 Add one failing application-lifespan test proving active completion is processed before ready work and both enter the ordinary inbox/dispatch path; implement deterministic synthetic command generation and startup ordering.

## 3. Cross-Source Idempotency

- [x] 3.1 Add a failing signed-HTTP test for reconciliation-first then delayed Queue delivery; implement the semantic command ledger while retaining transport receipt and body-conflict behavior.
- [x] 3.2 Add a failing signed-HTTP test for Queue-first then reconciliation on a later qualifying boot; make both orders converge on one run/completion/external effect.

## 4. Liveness and Observability

- [x] 4.1 Add a failing lifespan/read-back test for local heartbeat advancement, bounded reconciliation summaries, and same-boot restart; implement heartbeat lifecycle and public reconciliation read-back without periodic GitHub work.
- [x] 4.2 Add a failing data-minimization test and ensure liveness, boot, command, and reconciliation records exclude payload bodies, feedback, tokens, email addresses, and arbitrary exception text.

## 5. Documentation and Completion

- [x] 5.1 Update the pilot README with the 24-hour boundary, first-start behavior, boot identity, local heartbeat, startup ordering, semantic idempotency, observability, and no-polling guarantee.
- [x] 5.2 Perform the required DRY/SOLID/KISS refactoring pass and rerun targeted tests, the full pilot suite, lint, lock validation, strict OpenSpec validation, and `git diff --check`.
- [x] 5.3 Record criterion-level implementation evidence and mark Issue 10 resolved only for behavior proven through the productive seams.
