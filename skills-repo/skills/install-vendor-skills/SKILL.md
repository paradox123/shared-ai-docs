---
name: install-vendor-skills
description: Install, import, update, or activate skills from external vendors while preserving Daniel's shared skill setup. Use when the user asks to install, set up, pull, import, vendor, activate, sync, or update third-party skills, external skill repositories, Matt Pocock skills, Vercel skills, custom vendor skills, or any non-local skill source for Codex, Claude, Agents, or Copilot.
---

# Install Vendor Skills

## Overview

Use this skill as a setup guardrail. The canonical active skill list is `skills-repo/skills`; external vendor content belongs under `skills-repo/vendor`; Codex links are synchronized from the active list.

## Canonical Files

Before installing or changing vendor skills, read:

```text
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md
```

Use these tools instead of inventing parallel runtime paths:

```text
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/install-git-hooks.sh
```

## Required Workflow

1. Confirm the git root before edits:

```bash
git -C /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs rev-parse --show-toplevel
```

2. Inspect current state before changing anything:

```bash
git -C /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs status --short
find /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills -mindepth 1 -maxdepth 1 \( -type d -o -type l \) -exec basename {} \; | sort
```

3. Place external vendor source under `skills-repo/vendor/<vendor-name>/`. Do not install external vendor skills directly into `/Users/dh/.codex/skills`, `/Users/dh/.agents/skills`, `/Users/dh/.claude/skills`, or `skills-repo/active-skills`.

4. Activate a vendor skill only by adding an entry under `skills-repo/skills`:

```text
skills-repo/skills/<skill-name> -> ../vendor/<vendor-path>/<skill-name>
```

Use a normal directory in `skills-repo/skills` only for Daniel-owned local skills. Use a symlink for vendor-managed skills so future vendor pulls update the active skill immediately.

5. If the vendor has multiple agent-specific entrypoints, choose the Codex-specific entrypoint for Codex-facing `SKILL.md` when one exists. Example: `council/SKILL.md` points to the vendor's `SKILL.codex.md`.

6. After changing `skills-repo/skills`, synchronize Codex:

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
```

7. If hooks are missing or the setup was freshly cloned, install them:

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/install-git-hooks.sh
```

## Hard Rules

- Do not create or restore `skills-repo/active-skills`.
- Do not make `/Users/dh/.codex/skills` the source of truth.
- Do not copy vendor skills into `skills-repo/skills` when a symlink to `vendor/...` can preserve update behavior.
- Do not edit a vendor-managed skill through the active symlink unless the user explicitly wants to patch the vendored source. For local adaptations, fork it into a Daniel-owned skill under `skills-repo/skills/<new-name>`.
- Do not overwrite unrelated dirty work in `shared-ai-docs`.

## Verification

Run these checks before finishing:

```bash
test ! -e /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/active-skills
readlink /Users/dh/.agents/skills
readlink /Users/dh/.claude/skills
find -L /Users/dh/.codex/skills -mindepth 1 -maxdepth 2 -name SKILL.md -print | sed 's#/SKILL.md$##' | sed 's#^.*/skills/##' | sort
find /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills -maxdepth 1 -type l -exec sh -c 'for p do [ -e "$p/SKILL.md" ] || echo "broken active skill: $p -> $(readlink "$p")"; done' sh {} +
find /Users/dh/.codex/skills -maxdepth 1 -type l -exec sh -c 'for p do [ -e "$p/SKILL.md" ] || echo "broken codex skill: $p -> $(readlink "$p")"; done' sh {} +
```

Expected:

- `active-skills` is absent.
- `.agents/skills` and `.claude/skills` point to `skills-repo/skills`.
- Codex-visible skill names match the active list in `skills-repo/skills`.
- Broken-link checks print nothing.

## References
hybrid skill documentation: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/skills/hybrid-skill-sync.md
