# Acceptance evidence — parallel ticket batch extension

Verified 2026-09-16. This report supersedes the sequential behavior assertions in verification.md, which remains historical evidence for the original helper and diagnosis. No live batch, worker, automation or GitHub delivery was started by this evaluation.

## Observable decision outcomes

An independent evaluator read the completed skill and references and received seven fixture scenarios without expected answers. It produced these operational decisions:

| Scenario | Expected | Observed |
| --- | --- | --- |
| Ticket range without target; checkout main | Require explicit target before dispatch | Asked for target; allowed read-only preparation only; did not infer main |
| Three slots: review worker, provisional creation, delivered worker with cleanup pending | Retain uncertain creation slot; unlock dependencies on delivery; refill without wave barrier | Counted review and provisional creation; after delivered worker's idle confirmation selected the first eligible dependent; held overlapping ticket and queued another independent ticket at the limit |
| Accepted candidate on T0 while target is T1 | Revalidate current combination before merge | Refused stale grant; required integration reservation, target update, relevant combined checks and a matching head/target grant |
| Timed-out merge, idle worker | Keep uncertain integration reservation | Required remote reconciliation before releasing reservation or letting another candidate merge |
| Squash merge; new remote commit; untracked notes; worktree-relative evidence | Preserve unexpected work and evidence | Required durable report/image copy and verification; blocked destructive cleanup; kept unrelated work eligible |
| Worktree/local ref gone; remote absent; archive outcome unknown | Reconcile partial cleanup | Verified individual outcomes; did not recreate or blindly delete resources; retained archival uncertainty |
| Parked worker receives approval while all three slots occupied | Respect resource limit on resume | Waited for capacity, then required PR reconciliation and fresh head/target verification |

The evaluator identified missing fixture facts (idle confirmation and explicit parking) rather than assuming them. It also noted that archival verification lacked a concrete lookup hint; the cleanup procedure now uses the archive result or scoped archived-task lookup, never ordinary-list absence as proof.

## Standards

One actionable finding: the initial assignment required a working branch already confirmed before asynchronous task creation. Corrected the worker bootstrap to verify/create and report the actual branch, then confirm ownership during registration. Independent focused re-review confirmed resolution. No remaining actionable standards finding.

## Spec

One actionable finding: a ticket-specific blocked integration holder could retain its reservation indefinitely. Added acknowledged grant cancellation, known mutation outcome, confirmed quiescence and checkpointed release; resume requires new capacity/reservation and fresh validation. Recovery and specification agree. Independent focused re-review confirmed resolution. No remaining actionable spec finding.

Totals: Standards 0 unresolved (1 fixed); Spec 0 unresolved (1 fixed).

## Reproducible checks and limits

- Existing metadata helper: all 8 subprocess CLI behavior tests passed using `/usr/bin/python3`; helper and tests were unchanged by this extension.
- `OPENSPEC_TELEMETRY=0 openspec validate add-sequential-ticket-orchestration-skill --strict`: passed.
- Scoped `git diff --check`: passed.
- Full coherence read: SKILL.md, all three referenced documents, script, tests and UI metadata. Checked default-three accounting, explicit target, worktree bootstrap, acceptance versus merge grant, scoped blocking, resume and cleanup. Reused existing implement/automation/session-recovery owners; no new scheduling engine or dependencies.
- Canonical discovery symlink, required frontmatter/name, all relative Markdown reference targets and quoted UI metadata were checked directly. The bundled quick_validate.py could not run because the default Python lacks PyYAML; this is a validator-environment limitation, not a claimed pass.

The fixture evaluation demonstrates interpretation of the instructions, not live end-to-end scheduling, remote branch deletion, GitHub race protection or future automatic approval outcomes. These depend on the runtime and repository protections. No actual worktrees or remote working branches were removed for this documentation evaluation. Active production orchestration remains untouched.
