---
name: code-review
description: Review a fixed change through separate sequential DRY, SOLID and KISS reviewers, including repository standards, after critical requirements verification. Use for branch, PR or work-in-progress review and technical completion; reuse current evidence and review only affected deltas after repairs.
---

# Code Review

This skill is the single owner of structural review, standards coverage and review follow-up. Callers reference it instead of copying the method. Requirements verification precedes structural review; there is no additional blanket Spec/Standards review afterward.

## Scope and inputs

The complete review applies to substantive code, requirements, effective configuration and binding workflow rules, including skills and AGENTS.md. Pure spelling, formatting and editorial link corrections need appropriate document checks, with a recorded `not-required` scope rationale. Classify by effect, not filename; mixed changes use the complete review for their substantive scope.

Resolve the repository, relevant instructions, requirement sources and exact write set. Pin the supplied base to a commit SHA; infer an unambiguous existing change baseline when available, otherwise ask for the missing baseline. Never assume HEAD represents uncommitted work. For a committed branch use the resolved merge-base and head; for work in progress include the scoped staged, unstaged and relevant untracked contents. Preserve unrelated dirty work. Record a content manifest when no commit identifies the candidate. No commit is required solely to review it.

Read the actual requirements verification for this candidate, not just test totals or a worker's approval claim. Missing, stale or incomplete evidence must be completed using [requirements-verification.md](../change-accepted/references/requirements-verification.md) before starting a structural reviewer. A standalone review request authorizes this verification without an Accepted trigger; it does not authorize delivery. Report unavailable verification honestly and do not claim completion.

Read [review-criteria.md](references/review-criteria.md) and the applicable repository standards. Assign each relevant standard to one review dimension or an existing automated check. Keep a coverage map so standards outside the three principle names are still checked. Record tooling results once rather than asking reviewers to repeat enforced checks.

## Three sequential reviews

Run **DRY → SOLID → KISS**, each with its own independent reviewer. Do not combine or parallelize the three passes. Use a fresh context (`fork_turns="none"` where available), the exact scoped diff/current content identity, nearby-context paths, requirements, assigned standards and that dimension's brief from the criteria reference. Follow an explicitly authorized model profile; otherwise retain runtime defaults. The reviewing agent reports findings; the implementing agent owns repairs.

For each dimension:

1. Ask its reviewer to inspect both the diff and surrounding context. Require actionable findings with file/line, affected rule or heuristic, expected improvement and material risk. Distinguish binding rules from judgment calls. Keep the result concise; do not mandate abstractions or edits merely to produce a finding.
2. Address justified findings within scope, preserve required behavior and run affected checks. Record the reason for any disputed or inapplicable finding; unresolved binding failures prevent completion.
3. Send the same reviewer the old-to-new delta, its prior findings and affected coverage. Obtain a current result before starting the next dimension. Carry unaffected coverage forward. Replace an unavailable reviewer only with the same bounded packet and recorded provenance.

A later repair may affect an earlier dimension or a behavioral requirement: reopen that affected coverage and refresh its evidence, not the entire sequence automatically. A complete restart needs a recorded reason such as broad changed behavior, changed requirements or an unusable baseline. If separate reviewers cannot be run, report the specific limitation rather than label self-review independent.

## Result and reuse

After the last repair, run the relevant final suite and required checks; reuse existing results when their inputs have not changed. Any new repair reopens affected verification/review. Do not rerun the whole suite merely because a status note changed.

Save the compact [completion record](references/completion-record.md) with requirements evidence and the three reviewer receipts. For repeated invocations, check content, requirements and coverage and perform only missing or invalidated checks. Path-only archive moves can retain evidence through an explicit content/path mapping; changed rules or behavior cannot.

Report the reviewed scope, per-dimension outcome, current evidence and remaining limitations. Review alone grants no commit, push, merge, archive or issue-close authority.
