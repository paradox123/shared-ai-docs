# Live completion evidence

This directory records an actually executed local completion workflow for the isolated ticket export fixture. It is synthetic application data; the CLI executions, defect, repairs and structural reviewer invocations are real.

- `events.jsonl` is an append-only chronology using actual UTC timestamps and runtime canonical agent IDs. The API exposes these canonical names, so no separate UUID is invented.
- Numbered JSON records contain commands, cwd, execution times, exact stdout/stderr, exit codes and reviewed-file hashes.
- `candidate-*.json` pins reviewed contents including requirement/standard source versions; corresponding diffs capture the untracked source additions against the fixed base.
- `requirements-pre-review.md` maps each requirement to observed behavior and limits before any structural reviewer starts.
- `*-receipt.md` files contain the reviewers' own raw findings; `*-commands.json` files capture their read-only inspections.
- `skill-sources/` and `skill-source-manifest.json` preserve the exact active instructions applied to this process.
- `snapshots/initial/` preserves the initially green but incomplete implementation/tests. `snapshots/red/` preserves the behavioral counterexample with the original implementation. `snapshots/pre-review/` preserves the first requirements-complete review candidate. Later candidates are preserved when created.

Replay a snapshot by changing into its directory and running `python3 -m unittest -v`. The initial snapshot passes two tests. For the exact counterexample, run `python3 -m unittest -v test_ticket_export.ExportTests.test_filter_matches_normalized_status_in_both_formats` inside `snapshots/red/`; the expected historical result is two assertion failures and exit 1. A snapshot contains all five local source/context files and needs only Python's standard library.

Evidence utilities and receipts do not belong to the reviewed application-content identity. This avoids hashing a manifest into itself. No push, merge, archival, issue closure or production operation is authorized here.
