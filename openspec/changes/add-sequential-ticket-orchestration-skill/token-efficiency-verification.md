# Token-efficiency extension — acceptance, 2026-09-18

Implemented locally in the canonical `orchestrate-ticket-batch` skill. The existing `~/.codex/skills/orchestrate-ticket-batch` link resolves to this directory, so subsequent skill loads see the changes. No vendor skill, global model default, running batch, automation definition or application pilot was modified by this extension. Existing unrelated working-tree changes were left outside its scope.

## Expected behavior and observed evidence

| Requested improvement | Observed result | Evidence |
| --- | --- | --- |
| Critical verification before final review | Independent forward evaluation routed implementation-ready ticket 01 to critical verification and critically verified ticket 02 to its first independent Standards/Spec review. | [Forward evaluation](evidence/token-efficiency-forward-check.md), skill phase table and messages.md |
| Delta reviews with retained coverage | Evaluation reused reviewers S/P for C→D; this implementation's Spec finding was itself fixed with a CLI regression test and checked by the same reviewers through a scoped follow-up. Both axes retained their earlier coverage. | [Review receipts](evidence/token-efficiency-reviews.json) |
| Mechanical coordination helpers | Cursor-only change returned `unchanged`; a different branch returned `diverged`; a stale checkpoint returned `blocked` without altering the ledger. CLI tests cover simultaneous writers, malformed input and preservation of other tickets/uncertain actions. Manifests detect changed/missing files; retention preserves matching bytes and refuses conflicting evidence. | [Measured CLI scenarios](evidence/token-efficiency-cli.json), [21 passing tests and validation](evidence/token-efficiency-checks.json) |
| Consolidated closeout | Evaluation retained per-ticket activation proof, deferred only permitted status/archive paths, and selected one batch closeout with normal integration gates. No routine follow-up PR per ticket was selected. | [Forward evaluation](evidence/token-efficiency-forward-check.md), efficient-execution.md |
| Small complete context packets | Evaluation and final reviewers used `fork_turns="none"` with the relevant files, fixed baseline/manifest and briefs. Standards used Sol/medium and Spec Astra/high; no full parent history or peer findings accompanied their independent first passes. | [Review receipts](evidence/token-efficiency-reviews.json), context-packet contract |
| Stable fixtures and final-suite timing | Synthetic CLI fixtures exercise real subprocesses/files without live task or Git effects. Evaluation required a new final suite after C→D's behavioral repair. The final local suite ran after the last status-validation repair: 21 tests passed (13 helper + 8 existing identity-recovery tests). | [Validation outputs](evidence/token-efficiency-checks.json) |
| Local intermediate commits | Worker assignment permits checkpoints only on the owned branch before acceptance; push/merge/closure remain gated. Evaluation issued no merge grant and retained uncertain operations. | messages.md, [forward evaluation](evidence/token-efficiency-forward-check.md) |
| Model distribution | Role-specific profile is wired into dispatch/review instructions. Actual independent reviews used Sol/medium and Astra/high successfully. The coordinator's current model and global defaults were not silently changed. | efficient-execution.md, [review receipts](evidence/token-efficiency-reviews.json) |

## Critical verification and review

Behavior tests were developed in red/green slices through the public CLI. Critical verification added concurrent/stale writes, malformed existing ledgers, tampered evidence and invalid input checks. It exposed an invalid-ledger traceback, repaired before independent review. The Spec review then reproduced one P2: list/object observation statuses raised TypeError. A regression test covered list, object, null and integer statuses; all now yield structured blocked JSON with exit 2. The same reviewer closed the finding; Standards found no issues in the fix.

Standards: **0 open findings**. Spec: **0 open findings, 1 repaired**. The reviewed base is `d6898ead386a36f2439b09326c25418f9578c695`; receipts preserve the initial content manifest and explicit final code/test hashes. Subsequent evidence files and completed task checkboxes are documented bookkeeping, with no behavioral changes.

Refactoring pass: shared ledger validation is reused for current/proposed state; artifact path and digest validation are reused by manifest/verify/retain. Kept orchestration policy in instructions rather than embedding a partial state machine in the helper. No unused dispatch, Git or cleanup abstraction was added. Skill validation, strict OpenSpec validation, link checks and `git diff --check` pass.

## Verification limits

The direct executable surface is the helper CLI; it was exercised with synthetic local files. Instruction behavior was evaluated by an independent agent on a six-ticket scenario. No real ticket batch or productive activation was launched, and no PR was created or merged for evaluation. Consequently real token savings, whole-batch costs and Sol coordinator quality remain unmeasured; compare a subsequent equivalent live batch before claiming a percentage.

A running coordinator cannot switch its own model through skill text or the available task tools. For the next coordinator select Sol/medium in the app, or use the documented CLI launch flags. Profile instructions respect explicit user model choices and runtime restrictions. Existing ledgers/heartbeats require explicit adoption with retained IDs, authority and uncertain actions; they were not migrated automatically.
