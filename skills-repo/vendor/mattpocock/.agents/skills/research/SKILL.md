---
name: research
description: Investigate a question against high-trust primary sources and capture cited findings in a permitted Markdown artifact or read-only handoff. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Delegate the reading to one **background agent** while the parent continues useful local work.

## Handoff

Before spawning, resolve the current operating mode and permitted output scope. Plan or read-only execution does not authorize repository writes. Choose one output:

- Repository writes authorized: resolve one exact Markdown path from the repo's existing convention.
- Repository writes not authorized, but session artifacts permitted: resolve one exact Markdown path inside the allowed session artifact folder.
- No permitted writable location: request a sourced read-only handoff in the agent's response, with no file creation.

Give the agent:

- the concrete research question and decision it should inform
- the operating mode, allowed reading and writing scopes, and exact output path or read-only handoff format
- the requirement to use **primary sources** (official docs, source code, specs, or first-party APIs) and trace each claim to the source that owns it
- the required output: one concise Markdown artifact or read-only handoff with source links beside the claims they support

The background agent owns source collection and the first draft within that output scope. The parent owns operating-mode and scope decisions, final verification, and the user-facing synthesis. Do not have several agents write the same file. If a write is denied, report the denial and return a sourced read-only handoff; never retry the forbidden write through another tool, agent, or path. Publishing a session artifact or handoff into the repo later requires ordinary user-authorized execution, not a silent mode switch.

## Coordination And Recovery

Use bounded waits instead of repeated status polling. If the agent has not produced usable output after a reasonable wait:

1. Send one concise follow-up asking for the current blocker and the smallest remaining step.
2. Wait once more. Interrupt only when the agent is stuck, working outside scope, or needs a materially narrower brief.
3. After interruption, continue the same agent with a narrowed task when practical; spawn a replacement only when the existing run cannot be recovered.

Do not duplicate the delegated source-reading while waiting. Continue independent repo work or verification preparation, then collect the agent's final result before declaring the research complete.

## Parent Verification

Read the finished artifact or read-only handoff and verify that it answers the question, stays in the resolved output scope, distinguishes sourced fact from inference, and cites primary sources directly. Check a file's whitespace without treating a session artifact as a repository edit. For an authorized repository artifact, inspect only its repository state and whitespace:

```bash
git status --short -- "$artifact_path"

diff_check_code=0
git diff --no-index --check /dev/null "$artifact_path" || diff_check_code=$?
if [ "$diff_check_code" -gt 1 ]; then
  echo "artifact whitespace check failed to run: $diff_check_code"
fi
```

For an untracked artifact, ordinary `git diff --check -- "$artifact_path"` proves nothing; use the `--no-index --check` form above. Exit `1` means the new file differs from `/dev/null` and is expected. In zsh, do not assign to the read-only `status` parameter; use a task-specific name such as `diff_check_code`.

If the repository artifact is tracked, also review its focused diff. Report the actual output location or read-only delivery and any deferred repository publication; do not move a session artifact into the repo during restricted execution.
