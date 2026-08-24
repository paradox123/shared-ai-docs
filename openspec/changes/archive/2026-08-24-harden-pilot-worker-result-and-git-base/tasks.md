## 1. Worker result ingestion

- [x] 1.1 Add a failing adapter contract test reproducing a schema-valid `worker-result-v2` blocked final result together with one malformed JSONL diagnostic line.
- [x] 1.2 Parse the final result independently, retain valid diagnostic events, and represent malformed diagnostic lines with bounded synthetic events.
- [x] 1.3 Add a failing workflow/read-back test proving genuine result-file failures retain parsed diagnostics and a stable concrete failure code after redaction.
- [x] 1.4 Implement typed bounded failure propagation and persistence without raw malformed output or arbitrary exception text.

## 2. Fresh immutable worktree base

- [x] 2.1 Add a failing real-Git adapter test where local `main` is stale behind `origin/main` and assert the run worktree starts at the fetched remote SHA.
- [x] 2.2 Fetch, resolve, and pin the remote base SHA for new worktrees; retain the same SHA when adopting an existing run worktree.

## 3. Verification and completion

- [x] 3.1 Update the pilot README for result-channel independence, bounded failure diagnostics, and fresh immutable bases.
- [x] 3.2 Perform the required DRY/SOLID/KISS refactoring pass and rerun targeted tests, the full pilot suite, lint, lock validation, strict OpenSpec validation, and `git diff --check`.
- [x] 3.3 Record direct implementation evidence from the retained regression tests.
