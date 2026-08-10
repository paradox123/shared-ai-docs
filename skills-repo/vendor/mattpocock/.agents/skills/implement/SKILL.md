---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Before editing, record the owning Git root, current branch or detached state, and intended target branch from the user's request, issue, PRD, or repository workflow. If the current branch is unrelated or the target is unclear, resolve that mismatch before changing files; preserve existing work and use an isolated worktree when moving immediately would be unsafe. Do not assume that "current branch" is the intended delivery target.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /code-review to review the work.

Commit your work only to the confirmed intended target branch.
