---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Delegate the reading to one **background agent** while the parent continues useful local work.

## Handoff

Before spawning, resolve one exact Markdown output path from the repo's existing convention. Give the agent:

- the concrete research question and decision it should inform
- the exact output path and allowed repository scope
- the requirement to use **primary sources** (official docs, source code, specs, or first-party APIs) and trace each claim to the source that owns it
- the required artifact: one concise Markdown file with source links beside the claims they support

The background agent owns source collection and the first artifact draft. The parent owns task scope, repository safety, final verification, and the user-facing synthesis. Do not have several agents write the same file.

## Coordination And Recovery

Use bounded waits instead of repeated status polling. If the agent has not produced a usable artifact after a reasonable wait:

1. Send one concise follow-up asking for the current blocker and the smallest remaining step.
2. Wait once more. Interrupt only when the agent is stuck, working outside scope, or needs a materially narrower brief.
3. After interruption, continue the same agent with a narrowed task when practical; spawn a replacement only when the existing run cannot be recovered.

Do not duplicate the delegated source-reading while waiting. Continue independent repo work or verification preparation, then collect the agent's final result before declaring the research complete.

## Parent Verification

Open the finished Markdown file and verify that it answers the question, stays in scope, distinguishes sourced fact from inference, and cites primary sources directly. Then inspect only the artifact's repository state and whitespace:

```bash
git status --short -- "$artifact_path"

diff_check_code=0
git diff --no-index --check /dev/null "$artifact_path" || diff_check_code=$?
if [ "$diff_check_code" -gt 1 ]; then
  echo "artifact whitespace check failed to run: $diff_check_code"
fi
```

For an untracked artifact, ordinary `git diff --check -- "$artifact_path"` proves nothing; use the `--no-index --check` form above. Exit `1` means the new file differs from `/dev/null` and is expected. In zsh, do not assign to the read-only `status` parameter; use a task-specific name such as `diff_check_code`.

If the artifact is tracked, also review its focused diff. Keep the file where the repo already stores research notes; if no convention exists, choose a sensible location and report it.
