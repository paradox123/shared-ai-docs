---
name: qmd-release
description: Manage releases for the QMD project only. Use when user explicitly asks to cut a QMD release (e.g. "release qmd 1.0.5", "cut qmd release"). NOT auto-invoked by the model in unrelated repositories.
disable-model-invocation: true
metadata:
  author: tobi
  imported_by: codex
  source_repo: https://github.com/tobi/qmd
  source_path: skills/release/SKILL.md
  imported_at: "2026-04-23"
---

# QMD Release

Cut a release, validate changelog, and ensure hooks are installed for QMD.

## Safety Boundary

Only run this workflow when:
- current repository is the QMD repository, and
- user explicitly requested a QMD release.

If not in QMD repo, stop and report boundary mismatch.

## Usage

`/release 1.0.5` or `/release patch`.

## Process (QMD repo only)

1. Run `skills/release/scripts/release-context.sh <version>`.
2. Commit outstanding release-relevant work.
3. Write or update `[Unreleased]` changelog content.
4. Run `scripts/release.sh <version>`.
5. Show final changelog extract and request confirmation.
6. Push: `git push origin main --tags` (only after explicit confirmation).
7. Watch publish CI workflow with `gh run watch ... --exit-status`.

Never force-push and never skip validation.
