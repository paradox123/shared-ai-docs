---
name: install-vendor-skills
description: Install, import, update, or activate global/shared skills from external vendors while preserving Daniel's shared skill setup. Use when the user asks to install, set up, pull, import, vendor, activate, sync, or update third-party global skills, external skill repositories, Matt Pocock skills, Vercel skills, custom vendor skills, non-local skill sources, or anything "as described in" hybrid-skill-sync.md for global Codex, Claude, Agents, or Copilot; also use when scope is ambiguous so the agent first distinguishes global skills from repo-specific skills.
---

# Install Vendor Skills

## Overview

Use this skill as a global-skill setup guardrail. The canonical global active skill list is `skills-repo/skills`; external global vendor content belongs under `skills-repo/vendor`; Codex links are synchronized from the global active list.

This setup does not apply to repo-specific skills. If the user wants skills installed or configured for one repository only, follow that repository's `AGENTS.md`, README, local `.agents/skills`, local `.codex/skills`, or other repo-local convention instead.

## Canonical Files

Before installing or changing global vendor skills, read:

```text
~/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md
```

Use these tools instead of inventing parallel runtime paths:

```text
~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/install-git-hooks.sh
```

## Required Workflow

1. Determine scope before editing:

- Global/shared skill setup: continue with this workflow.
- Repo-specific skill setup: do not apply the global `skills-repo/skills` policy. Work inside the target repo, read its local agent instructions, and keep the skill local to that repo unless the user explicitly asks to promote it globally.
- Ambiguous request: inspect the current cwd/repo context and ask only if the scope cannot be inferred.

2. Confirm the global skills git root before global edits:

```bash
git -C ~/Documents/DanielsVault/_shared/shared-ai-docs rev-parse --show-toplevel
```

3. Inspect current global state before changing anything:

```bash
git -C ~/Documents/DanielsVault/_shared/shared-ai-docs status --short
find ~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills -mindepth 1 -maxdepth 1 \( -type d -o -type l \) -exec basename {} \; | sort
```

4. Classify the vendor source before updating it:

- Git checkout: update it through that checkout and preserve its repository boundary.
- Pinned snapshot with a lock file: use the staged three-way update workflow below. Do not treat the snapshot directory as a Git checkout or overwrite local divergences with a blind copy.

5. Place external global vendor source under `skills-repo/vendor/<vendor-name>/`. Do not install external global vendor skills directly into `~/.codex/skills`, `~/.agents/skills`, `~/.claude/skills`, or `skills-repo/active-skills`.

6. Activate a global vendor skill only by adding an entry under `skills-repo/skills`:

```text
skills-repo/skills/<skill-name> -> ../vendor/<vendor-path>/<skill-name>
```

Use a normal directory in `skills-repo/skills` only for Daniel-owned global skills. Use a symlink for vendor-managed global skills so future vendor pulls update the active skill immediately.

7. If the vendor has multiple agent-specific entrypoints, choose the Codex-specific entrypoint for Codex-facing `SKILL.md` when one exists. Example: `council/SKILL.md` points to the vendor's `SKILL.codex.md`.

8. After changing `skills-repo/skills`, synchronize Codex:

```bash
~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
```

9. If hooks are missing or the setup was freshly cloned, install them:

```bash
~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/install-git-hooks.sh
```

## Updating An Existing Pinned Snapshot

Use this branch when `skills-repo/vendor/<vendor-name>/` contains copied vendor content plus a lock file with an old upstream `sourceRef`.

1. Read the lock's source URL, pinned ref, vendor path, per-skill source paths, and hash meaning. Treat the lock as provenance, not proof that locally overlaid files still equal upstream.
2. Clone or fetch upstream into one task-owned temporary directory. Bind every upstream history operation to that checkout with `git -C "$upstream_repo"`; a plain `git show`, `git diff`, or `git rev-parse` may silently address the parent repo.
3. Compare the current vendored tree with the old pinned upstream ref before changing anything. Inventory every local divergence and preserve unrelated parent-repo changes.
4. Build the new upstream snapshot in a staging directory. For each local divergence, use old pinned upstream as the merge base, the current vendored file as local, and the new upstream file as other. Stop for conflicts, ambiguous renames, or locally changed files deleted upstream.
5. Generate provenance hashes from the canonical new upstream tree when the existing lock defines hashes that way. Verify local overlays separately; do not redefine a lock field silently to hash the merged overlay.
6. Review upstream skill additions, removals, and renames. Change only active symlinks already managed by that vendor, and validate their expected old targets before unlinking them.
7. Apply the staged snapshot to the exact validated vendor directory only after merge and link checks pass. Never run `rsync --delete` or an equivalent destructive copy directly from an unvalidated source or against a broad/unresolved target.
8. Verify the pinned ref, canonical hashes, expected overlay-only differences, active vendor skill-name set, removed and added runtime links, broken links, and `git diff --check` before finishing.

The detailed lock and overlay contract is maintained in `~/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md` under “Gepinnte Vendor-Snapshots sicher aktualisieren”.

## Hard Rules

- Do not create or restore `skills-repo/active-skills`.
- Do not make `~/.codex/skills` the source of truth.
- Do not apply this global setup to repo-specific skill folders.
- Do not copy global vendor skills into `skills-repo/skills` when a symlink to `vendor/...` can preserve update behavior.
- Do not edit a vendor-managed skill through the active symlink unless the user explicitly wants to patch the vendored source. For local adaptations, fork it into a Daniel-owned skill under `skills-repo/skills/<new-name>`.
- Do not overwrite unrelated dirty work in `shared-ai-docs`.

## Verification

Run these checks before finishing:

```bash
test ! -e ~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/active-skills
readlink ~/.agents/skills
readlink ~/.claude/skills
find -L ~/.codex/skills -mindepth 1 -maxdepth 2 -name SKILL.md -print | sed 's#/SKILL.md$##' | sed 's#^.*/skills/##' | sort
find ~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills -maxdepth 1 -type l -exec sh -c 'for p do [ -e "$p/SKILL.md" ] || echo "broken active skill: $p -> $(readlink "$p")"; done' sh {} +
find ~/.codex/skills -maxdepth 1 -type l -exec sh -c 'for p do [ -e "$p/SKILL.md" ] || echo "broken codex skill: $p -> $(readlink "$p")"; done' sh {} +
```

Expected:

- `active-skills` is absent.
- `.agents/skills` and `.claude/skills` point to `skills-repo/skills`.
- Codex-visible skill names match the active list in `skills-repo/skills`.
- Broken-link checks print nothing.

## References
hybrid skill documentation: ~/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md
