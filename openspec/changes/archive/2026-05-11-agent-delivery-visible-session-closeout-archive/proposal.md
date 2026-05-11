# Agent Delivery Visible Session Closeout Archive

## Why

Visible Codex-App Agent Delivery sessions must not be left open while child closeout reports `READY`. Closeout needs a machine-checkable archive summary that distinguishes archived visible threads from headless/no-thread evidence.

## What Changes

- Add `ArchiveVisibleCodexAppSession.cs` as the S5 closeout archive companion tool.
- Add S5 fixture coverage for visible archived, already archived, headless, queued/no-thread, archive failure, proof failure, mixed child runs, unarchived-visible negative, manual-visible missing thread, and retained-session acceptance.
- Extend the visible-session evidence validator to understand S5 archive summaries without weakening the S2 failure class `unarchived_visible_session`.
- Synchronize `spec-closeout`, workflow docs, and testsuite README wording around explicit archive statuses.

## Scope Control

No Launcher adapter changes, no S3 runner changes, no direct SQLite mutation, no live `thread/archive` call, and no `MD-E2E-5` run are included in this change.
