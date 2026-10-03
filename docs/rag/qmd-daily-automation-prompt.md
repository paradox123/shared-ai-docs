Maintain the DanielsVault QMD index and embeddings. This automation does not run the contextual LLM Wiki, its compiler, WikiQuery, or any wiki maintenance runner.

Startup:
- Automation ID: `update-qmd-index-daily`. Resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` in each shell that reads automation state.
- Before repository or runtime commands, read this automation's `automation.toml` and at most the first 8000 characters of its newest-first `memory.md`. Load the QMD skill and its Scheduled Index Maintenance reference.
- Resolve the existing Homebrew QMD and Node 22 runtime. Check the QMD database file and containing directory for writability as described in that reference. Do not install software, change permissions, move the database, or alter source documents.
- If only the task sandbox blocks the QMD database, use the already authorized local execution route for this automation to repeat the same preflight and run the same command. If that route is unavailable or the database is still unwritable, stop before maintenance and report the exact blocker. Do not start a second job to recover output.

Execution:
- Start this repository-owned QMD runner exactly once after preflight, using a fresh artifact path. It owns baseline status, manifest reconciliation, `qmd update`, conditional `qmd embed`, and final status. Do not run those commands again outside the runner.

```bash
for brew in /opt/homebrew/bin/brew /usr/local/bin/brew; do
  if [ -x "$brew" ]; then eval "$("$brew" shellenv)"; break; fi
done
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
QMD_RUN_DIR="$CODEX_HOME_RESOLVED/automations/update-qmd-index-daily/runs/$(date '+%Y%m%dT%H%M%S')-$$"
python3 /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/scripts/run-qmd-daily.py \
  --artifacts "$QMD_RUN_DIR"
```

- Retain the exact first `artifacts` path and execution handle. Wait on that same handle until it exits. Read its `report.json`; command outputs and stderr are in that artifact directory. A valid success requires `ok:true` and exit 0 for reconciliation check, update, embed, and final status. If update fails, embedding is skipped and final status still runs.
- Immediately before updating the adjacent memory, reread a bounded current header. Prepend a concise result with run time, artifact path, reconciliation, update/embed/status exits, document and vector counts, and any blocker. Preserve prior entries. A manual verification run is not evidence of a later scheduled run.
- Report QMD result and exact failed step in plain German. A QMD success does not assert that generated LLM Wiki pages are current. Do not use wiki backlog or `lastCompleted` as a QMD success gate. Do not change schedule, model, project, notification settings, collection manifest, or unrelated jobs.
