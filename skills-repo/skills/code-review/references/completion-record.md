# Completion record

Use one durable record per change/write set, available without a batch ledger. Prefer `completion.md` in the active change directory; otherwise use the repository's evidence convention or `.scratch/completion/<scope>/completion.md`. Callers and batch ledgers link to it. Keep raw logs in linked artifacts.

Record:

- **Scope and identity:** repository, change/ticket, exact write set, fixed base SHA, current head or reproducible content manifest, relevant untracked files, and excluded unrelated changes. Include behavior-bearing docs/config in the identity. Keep generated receipts/logs outside the reviewed-content identity to avoid self-referential hashes; explain their separate evidence role.
- **Applicability:** substantive review or editorial `not-required`, with the effect-based reason.
- **Requirements evidence:** source and version, each requirement's expected behavior, observed result, counterexample/limit coverage, inspected artifact or code location, verification command/result and candidate identity. State unverified coverage explicitly.
- **Standards coverage:** repository rule sources and mapping to a reviewer or an existing automated check.
- **Reviewer receipts:** dimension, reviewer identity, fixed base, reviewed contents, covered properties/rules, stable finding IDs, disposition, result and evidence paths. A delta receipt links its prior receipt and old/new identities, lists rechecked properties and explicitly retained coverage. Never attribute earlier approval to a replacement reviewer.
- **Final checks and state:** commands/results and content identity, remaining limitations, `awaiting-acceptance`, `verification-incomplete`, `review-incomplete` or `technically-complete`. Editorial completion uses documented checks, not fabricated reviewer receipts.
- **Delivery:** separately record authorized target/actions and their verified outcome when performed. Technical completion is not delivery authority.

Reuse requires both content correspondence and sufficient requirement/standards coverage. Matching hashes alone cannot supply omitted criteria. Later relevant changes reopen affected checks. Archive/squash/rebase mappings must show which current contents the receipts cover. Keep previous observations attributable instead of overwriting them as if reviewers had inspected a new candidate.
