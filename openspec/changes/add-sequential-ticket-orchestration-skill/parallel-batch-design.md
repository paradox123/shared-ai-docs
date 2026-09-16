# Parallel ticket batches — design interview

Status: interview concluded via grill-with-docs, 2026-09-16. The user accepted all three recommendations. This note records the decisions for the parallel extension of the same active skill change.

## Confirmed user requirements

- Replace strictly sequential execution with parallel execution where tickets are independent and no blocker prevents their execution.
- Require the user to explicitly name the delivery target branch at the beginning of the orchestration session. Do not infer main, the default branch or the current checkout when this input is missing.
- Run parallel implementation tasks in separate worktrees.
- Use conservative parallel eligibility: start clearly separated changes together; serialize tickets with foreseeable overlapping file or interface changes, even if functionally independent. The user accepted this trade-off to reduce conflicts and rework. Reassess eligibility when implementation reveals previously unknown overlap.
- After verified delivery and merge into the selected target branch, preserve acceptance evidence durably outside the worktree, remove the owned worktree and associated owned local/remote working branches, and archive the implementation task. The user accepted this cleanup scope during the interview. Preserve unrelated or unintegrated changes; do not remove the delivery target branch.
- Limit concurrent implementation sessions to three by default; allow an explicit per-batch override. The user accepted this resource/cost limit.
- Preserve the existing critical-verification, evidence review, acceptance, identity recovery and approval-boundary rules.

## Exit audit

No unresolved product, scope, cleanup or resource-policy question remains. Remaining details are implementation choices and do not require further interview. Proceed with the skill, templates and spec updates; preserve the existing runtime permission boundaries.

## Implementation assumptions

- Serialize merges into the shared target branch and verify each candidate against the latest integrated state while implementation remains parallel. Treat this as an integration-safety implementation assumption, not another user preference question.
- A dependency becomes available only when the prerequisite is verified on the selected target branch; no implicit stacked worker branches.
- A blocked ticket holds back its dependents; independent eligible tickets may continue, unless the blocker affects a shared prerequisite or batch-wide permission.
- Cleanup must preserve unrelated/unmerged work and retain inspectable acceptance evidence outside any removed worktree.
- Operational details such as polling cadence, ledger layout and temporary directory names remain delivery choices, not interview questions.

## Vocabulary and scope

Root CONTEXT.md now defines Ticket-Batch separately from the serial Implementierungswarteschlange used by the independent agent-pilot workflows. Those workflows are unchanged. No additional ADR: these are reversible skill workflow choices, documented in this change rather than promoted into architecture rules for the separate pilots. Cleanup remains guarded because deleted unmerged work or lost evidence would be irreversible.
