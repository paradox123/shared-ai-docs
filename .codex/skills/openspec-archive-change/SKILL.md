---
name: openspec-archive-change
description: Archive a completed OpenSpec change with the OpenSpec CLI. Use when the user wants to finalize and archive a change after implementation is complete.
license: MIT
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.2.0"
---

# Archive an OpenSpec Change

Finalize one completed OpenSpec change, update canonical specs when appropriate, archive the change, and validate the resulting repository state.

This skill owns the OpenSpec status, spec-sync, archive, and validation steps. Repository issue status, labels, and closeout evidence remain separate. In this repository, follow `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` for that work; do not infer issue transitions from the OpenSpec archive result.

## Resolve the Change

Use the exact change name supplied by the user or established unambiguously in the current conversation. Otherwise run `openspec list --json`, show only active changes, and ask the user to select one. Never guess.

In command examples below, set `CHANGE` to that exact name.

## Completion Gates

1. Run `openspec status --change "$CHANGE" --json` and inspect `schemaName` plus every artifact status.
2. Read `openspec/changes/$CHANGE/tasks.md` when present and count incomplete `- [ ]` tasks.
3. If an artifact or task is incomplete, list it and obtain explicit confirmation before continuing. Warnings do not silently block an authorized archive.
4. Run the pre-archive validation:

   ```bash
   openspec validate "$CHANGE" --strict --no-interactive
   ```
5. Resolve the dated target and fail before any mutation if it already exists:

   ```bash
   ARCHIVE_TARGET="openspec/changes/archive/$(date +%F)-$CHANGE"
   test ! -e "$ARCHIVE_TARGET"
   ```

## Choose One Archive Path

| Situation | Path | Canonical-spec owner |
|---|---|---|
| Delta specs should update the canonical specs | Standard, preferred | `openspec archive` |
| The change is infrastructure/tooling/docs-only with no canonical spec update, or its delta was already merged and verified manually | Skip specs | The caller |
| The CLI cannot represent the repository's archive layout or fails for a diagnosed non-validation reason | Manual fallback, exceptional | The caller |

### Standard path

Let the CLI apply delta specs and archive the change:

```bash
openspec archive -y "$CHANGE"
```

Do not manually sync or move files first. If delta specs exist, summarize their intended canonical effect before executing when that decision has not already been accepted.

### Skip-specs path

Use this only after stating why no CLI-managed spec update is appropriate. If specs were merged manually, validate their final state before archiving:

```bash
openspec validate --specs --strict --no-interactive
openspec archive -y --skip-specs "$CHANGE"
```

### Manual fallback

Do not choose a raw move because the CLI syntax is uncertain; the standard commands are defined above. Use a manual move only after the CLI path is known to be unsuitable, record the reason, and own any required canonical-spec merge first.

```bash
openspec validate --specs --strict --no-interactive
mkdir -p openspec/changes/archive
mv "openspec/changes/$CHANGE" "$ARCHIVE_TARGET"
```

An existing target is a hard stop. Do not overwrite or rename it without user direction.

## Verify and Report

Run the repository-wide postcondition check:

```bash
openspec validate --all --strict --no-interactive
```

Confirm that the active change directory is gone and the dated archive target exists. Then report:

- change name and schema
- archive path
- archive path chosen: standard, skip-specs, or manual fallback
- whether canonical specs were updated, already verified, or intentionally skipped
- any incomplete-artifact/task warning that the user accepted
- the separate issue-closeout action taken, or that it remains outstanding

Do not rediscover these normal commands with `openspec archive --help` or `openspec validate --help`. Consult help only if the installed CLI rejects a documented invocation, and report that version mismatch explicitly.
