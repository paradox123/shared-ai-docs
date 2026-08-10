---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

# Resolving Merge Conflicts

1. **See the current state** of the merge/rebase. Check git history and the conflicting files with `git status --short`, `git diff --name-only --diff-filter=U`, and `git ls-files -u`.

   For an in-progress merge, resolve the merge base without the unsupported `git merge-base --short` form:

   ```bash
   merge_base=$(git merge-base HEAD MERGE_HEAD)
   git rev-parse --short "$merge_base"
   ```

   Inspect index stages with the entire revision spec quoted so zsh does not reinterpret the colons or variable name:

   ```bash
   conflict_path="path/to/file"
   git show ":1:${conflict_path}"  # merge base
   git show ":2:${conflict_path}"  # current side
   git show ":3:${conflict_path}"  # incoming side
   ```

   Do not write `git show :$stage:$path`; shell parsing can turn that into the wrong variable expansion. If the stage spec still fails, get the blob ids with `git ls-files -u -- "$conflict_path"` and inspect the selected blob with `git cat-file -p "$blob_id"`. During a rebase, remember that Git's `ours` is the branch being rebased onto and `theirs` is the commit being replayed.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

4. Discover the project's **automated checks** and run them — typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
