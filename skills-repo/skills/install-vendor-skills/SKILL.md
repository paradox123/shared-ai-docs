---
name: install-vendor-skills
description: Install, import, update, or activate global/shared skills from external vendors while preserving Daniel's shared skill setup. Use when the user asks to install, set up, pull, import, vendor, activate, sync, or update third-party global skills, external skill repositories, Matt Pocock skills, Vercel skills, custom vendor skills, non-local skill sources, or anything "as described in" hybrid-skill-sync.md for global Codex, Claude, Agents, or Copilot; also use when scope is ambiguous so the agent first distinguishes global skills from repo-specific skills.
---

# Install Vendor Skills

## Overview

Use this skill as a global-skill setup guardrail. The canonical global active skill list is `skills-repo/skills`; external global vendor content belongs under `skills-repo/vendor`; runtime links are synchronized from the global active list with the host's existing helper.

This setup does not apply to repo-specific skills. If the user wants skills installed or configured for one repository only, follow that repository's `AGENTS.md`, README, local `.agents/skills`, local `.codex/skills`, or other repo-local convention instead.

## Canonical Files

For a global/shared request, resolve the configured shared-ai-docs checkout or authorized worktree for the current host; do not assume a macOS home path or switch to another checkout. Confirm that it contains `skills-repo/skills`, `skills-repo/vendor` and `docs/skills/hybrid-skill-sync.md`, then verify its Git root. If the canonical checkout cannot be resolved, stop and ask rather than invent a second global source.

Before installing or changing global vendor skills, read [hybrid-skill-sync.md](../../../docs/skills/hybrid-skill-sync.md) in that checkout. It owns runtime mappings, host-specific verification and vendor provenance mechanics.

Use these existing repo-relative tools instead of inventing parallel installers or runtime paths:

```text
Windows: skills-repo\tools\sync-windows-skill-links.ps1
macOS/POSIX: skills-repo/tools/sync-codex-skill-links.sh
macOS/POSIX hooks: skills-repo/tools/install-git-hooks.sh
```

On Windows, Git may check out symlinks as text files (`core.symlinks=false`). Use the Windows helper to resolve vendor entrypoints and derive runtime Junctions without elevation; a single Junction to `skills-repo\skills` does not make those placeholders usable. Keep detailed mechanics in the canonical documentation.

## Required Workflow

1. Determine scope before editing:

- Global/shared skill setup: continue with this workflow.
- Repo-specific skill setup: do not apply the global `skills-repo/skills` policy. Work inside the target repo, read its local agent instructions, and keep the skill local to that repo unless the user explicitly asks to promote it globally.
- Ambiguous request: inspect the current cwd/repo context and ask only if the scope cannot be inferred.

2. Confirm the resolved global skills Git root before global edits. Use the current host's shell and the resolved path, not a hard-coded home directory:

```bash
git -C "$shared_repo" rev-parse --show-toplevel
git -C "$shared_repo" status --short
find "$shared_repo/skills-repo/skills" -mindepth 1 -maxdepth 1 \( -type d -o -type l \) -exec basename {} \; | sort
```

```powershell
git -C $SharedRepo rev-parse --show-toplevel
git -C $SharedRepo status --short
Get-ChildItem -LiteralPath (Join-Path $SharedRepo 'skills-repo\skills') -Force | Sort-Object Name | Select-Object Name, LinkType, Target
```

3. Inspect the active entries and their actual source ownership before changing anything. On Windows, include Git symlink-text files in that inventory; do not mistake them for owned skill directories or write through them into vendor content.

4. Classify the vendor source before updating it:

- Git checkout: update it through that checkout and preserve its repository boundary.
- Pinned snapshot with a lock file: use the staged three-way update workflow below. Do not treat the snapshot directory as a Git checkout or overwrite local divergences with a blind copy.
- Legacy copied snapshot without a lock file: bootstrap provenance with the fail-closed workflow below before updating any vendored content.

5. Place external global vendor source under `skills-repo/vendor/<vendor-name>/`. Do not install external global vendor skills directly into `~/.codex/skills`, `~/.agents/skills`, `~/.claude/skills`, or `skills-repo/active-skills`.

6. Activate a global vendor skill only by adding an entry under `skills-repo/skills`:

```text
skills-repo/skills/<skill-name> -> ../vendor/<vendor-path>/<skill-name>
```

Use a normal directory in `skills-repo/skills` only for Daniel-owned global skills. Use a Git symlink for vendor-managed global skills so future vendor pulls update the active source immediately. On Windows, preserve the Git link entry and let the existing sync helper resolve its checked-out representation; do not require elevation or convert source entries into runtime Junctions.

7. If the vendor has multiple agent-specific entrypoints, choose the Codex-specific entrypoint for Codex-facing `SKILL.md` when one exists. Example: `council/SKILL.md` points to the vendor's `SKILL.codex.md`.

8. Before activating or synchronizing a new or updated vendor entrypoint, validate its required sibling-skill dependency closure:

- Follow direct skill invocations and links in the entrypoint and its bundled references. Treat wording such as "always call", "requires", or a named primitive used by the workflow as required; do not promote merely descriptive examples to dependencies.
- Every required sibling must exist in the staged vendor snapshot and be active under `skills-repo/skills` when runtime dispatch addresses it by skill name, or the entrypoint must contain and document a self-contained replacement.
- If a required sibling is absent, stop before activation. Reconcile the vendor version, activate the missing sibling, or create an explicitly Daniel-owned adaptation; do not leave a router active with a known missing primitive and do not silently rewrite vendor-managed files through active symlinks.
- Record the checked dependency set and any optional-versus-required judgment in the update evidence.

9. Synchronize only when runtime updates are authorized, using the checkout intended to own the live runtime links. Source-only work in an isolated worktree does not authorize pointing global runtimes at that worktree. Run the host's sync from the resolved repository root:

```powershell
powershell.exe -NoProfile -File .\skills-repo\tools\sync-windows-skill-links.ps1
```

On macOS/POSIX:

```bash
./skills-repo/tools/sync-codex-skill-links.sh
```

10. On macOS/POSIX, install missing hooks only in an authorized main checkout whose `.git` is a directory:

```bash
./skills-repo/tools/install-git-hooks.sh
```

Do not run that Bash hook installer in a worktree or on Windows. Windows sync is manual after pulls or branch changes; rerun it for added/removed skills and vendor entrypoint updates as documented in the canonical workflow.

## Bootstrapping A Legacy Copied Snapshot

Use this branch when copied vendor content exists but no lock identifies its previous upstream base.

1. Clone or fetch upstream into one task-owned temporary checkout and bind every history command with `git -C "$upstream_repo"`.
2. Reconstruct exactly one previous upstream ref from multiple stable content anchors in the copied tree. Exclude known local-only files and likely overlays from the anchors; do not infer provenance from timestamps or one locally editable entrypoint.
3. If no prior ref matches or more than one materially different ref remains plausible, stop without changing the snapshot and report the ambiguity.
4. Diff the copied tree against the reconstructed ref to inventory local overlays. Use that ref as the merge base for the staged three-way update; never use the locally modified snapshot itself as the base.
5. Create the initial lock in staging. Record the old base as `reconstructedPreviousRef`, record the selected new upstream commit as `sourceRef`, preserve canonical-upstream hash semantics, and inventory merged local content separately under the lock's overlay field.
6. Continue with the pinned-snapshot workflow only after the reconstructed base, overlay inventory, staged lock, and target path all validate.

Use the canonical documentation's "Legacy-Kopie ohne Lockdatei bootstrapen" section for the detailed provenance contract.

## Updating An Existing Pinned Snapshot

Use this branch when `skills-repo/vendor/<vendor-name>/` contains copied vendor content plus a lock file with an old upstream `sourceRef`.

1. Read the lock's source URL, pinned ref, vendor path, per-skill source paths, and hash meaning. Treat the lock as provenance, not proof that locally overlaid files still equal upstream.
2. Clone or fetch upstream into one task-owned temporary directory. Bind every upstream history operation to that checkout with `git -C "$upstream_repo"`; a plain `git show`, `git diff`, or `git rev-parse` may silently address the parent repo.
3. Compare the current vendored tree with the old pinned upstream ref before changing anything. Inventory every local divergence and preserve unrelated parent-repo changes.
4. Build the new upstream snapshot in a staging directory. For each local divergence, use old pinned upstream as the merge base, the current vendored file as local, and the new upstream file as other. Stop for conflicts, ambiguous renames, or locally changed files deleted upstream.
5. Generate provenance hashes from the canonical new upstream tree when the existing lock defines hashes that way. Verify local overlays separately; do not redefine a lock field silently to hash the merged overlay.
6. Review upstream skill additions, removals, renames, and direct sibling-skill dependencies. Validate required dependency closure in the staged snapshot before changing active links. Change only active symlinks already managed by that vendor, and validate their expected old targets before unlinking them.
7. Apply the staged snapshot to the exact validated vendor directory only after merge and link checks pass. Never run `rsync --delete` or an equivalent destructive copy directly from an unvalidated source or against a broad/unresolved target.
8. Verify the pinned ref, canonical hashes, expected overlay-only differences, active vendor skill-name set, removed and added runtime links, broken links, and `git diff --check` before finishing.

Use the canonical documentation's "Gepinnte Vendor-Snapshots sicher aktualisieren" section for the detailed lock and overlay contract.

## Hard Rules

- Do not create or restore `skills-repo/active-skills`.
- Do not make `~/.codex/skills` the source of truth.
- Do not apply this global setup to repo-specific skill folders.
- Do not copy global vendor skills into `skills-repo/skills` when a symlink to `vendor/...` can preserve update behavior.
- Do not edit vendor-managed content through an active entrypoint. Apply an explicitly authorized local overlay only at the verified vendor source, preserving active links and canonical upstream hash semantics; otherwise fork a local adaptation into a Daniel-owned skill under `skills-repo/skills/<new-name>`.
- Do not overwrite unrelated dirty work in `shared-ai-docs`.

## Verification

Run the current host's verification from the canonical documentation, not POSIX `readlink`/`find` commands on Windows. Verify:

- `active-skills` is absent.
- On macOS/POSIX, `.agents/skills` and `.claude/skills` point to `skills-repo/skills`; on Windows they point to the derived Copilot runtime list.
- Managed runtime-visible skill names and readable `SKILL.md` entrypoints match the active source list, preserving foreign skills and system/plugin entries.
- Required sibling skills referenced by active vendor routers exist and are active when invoked by skill name, or the router documents a self-contained replacement.
- No managed runtime entrypoint contains unresolved Git link text or a broken target.
- Source changes remain limited to the authorized scope and `git diff --check` passes.

For isolated Windows helper verification without live runtime changes, run `powershell.exe -NoProfile -File .\skills-repo\tests\test-sync-windows-skill-links.ps1` from the repository root. The test uses its own fixture source and user home.
