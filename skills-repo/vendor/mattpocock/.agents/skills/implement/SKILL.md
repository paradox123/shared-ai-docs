---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Before editing, record the owning Git root, current branch or detached state, and intended target branch from the user's request, issue, PRD, or repository workflow. If the current branch is unrelated or the target is unclear, resolve that mismatch before changing files; preserve existing work and use an isolated worktree when moving immediately would be unsafe. Do not assume that "current branch" is the intended delivery target.

Before implementation, inspect the repository's OpenSpec policy. When an `openspec/` directory exists, run `openspec list --json` as a routing gate; an empty or non-matching list does not by itself mean OpenSpec is unnecessary.

- Apply a matching active change through the repository's local `$openspec-apply-change` skill.
- When no active change matches, use the local `$openspec-propose` skill before editing if the work changes a public API or wire status, stored data or persistence behavior, cross-cutting runtime safety or configuration, or spans multiple tickets—unless repository policy explicitly treats the supplied ticket or spec as the accepted change artifact.
- Record a brief evidence-backed reason whenever OpenSpec is skipped. Configuration that changes runtime or wire semantics is not narrow configuration.

If the local skills are unavailable, follow the equivalent `openspec status` and `openspec instructions` CLI workflow. Do not install or rely on global OpenSpec skills for a repo-local workflow, and do not force OpenSpec onto genuinely narrow documentation, configuration, or mechanical work unless repository guidance requires it. For OpenSpec-backed work, keep active tasks and evidence current and run `openspec validate <change> --strict` before review.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /code-review to review the work.

Commit your work only to the confirmed intended target branch.
