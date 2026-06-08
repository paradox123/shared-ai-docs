# Issue Publishing

Load this reference when publishing issue batches, especially to GitHub Issues.

## GitHub Issues

Prefer `gh issue create --body-file <file>` over long inline `--body` strings. Put the body in a temporary Markdown file or other real file, then pass that path to `gh`.

Avoid shell-sensitive placeholders like `<number>` in command text; use `{number}` or a concrete example in Markdown body text.

After creating each issue, inspect it with:

```bash
gh issue view <number> --json title,body,labels,milestone,url
```

Patch malformed body text, missing labels, missing milestone, or broken dependency references before moving on.

## Batch Checks

After publishing a batch:

- comment on the parent PRD/issue with the final slice map and implementation order
- verify every `Blocked by` entry references a real tracker issue
- verify spec labels/rationales only when the repo uses them
- verify project-specific guards appear only on relevant issues
- report intentionally deferred follow-up slices

Use concrete artifact paths in issue bodies only when the issue is explicitly about a runbook, generated evidence location, fixture path, CLI contract, or repository-specific workflow where the path is itself part of the requirement.
