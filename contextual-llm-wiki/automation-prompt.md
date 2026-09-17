Maintain the common production DanielsVault wiki with independent source indexing and bounded resumable wiki work.

Startup:
- Automation ID: `update-qmd-index-daily`. In each state shell resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"`.
- Read its `automation.toml` and at most the first 8000 characters of adjacent `memory.md` (including any omission marker) before repository/runtime commands. Create missing memory. Load the QMD skill and its Scheduled Index Maintenance reference; required skill loading may precede state reads. No broad filesystem discovery.
- Follow the reference's existing Homebrew/Node/QMD and database-directory writability preflight. Prepend `/opt/homebrew/opt/node@22/bin` when executable. Resolve QMD_BIN in the same shell as execution. Make the existing Codex binary available from `/Applications/ChatGPT.app/Contents/Resources` if needed. Unavailable runtime, login, or storage is a blocker; do not repair installs, permissions or TCC.

Execution:
1. Start exactly once with a new artifact directory. The repository-owned runner captures its single helper's stdout, stderr and numeric exit status; do not duplicate reconciliation, collection, maintenance, update or embedding commands.

```bash
WIKI_HOME="/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/contextual-llm-wiki"
WIKI_RUN_DIR="$WIKI_HOME/.local/operations-runs/$(date '+%Y%m%dT%H%M%S')-$$"
LLMWIKI_PROVIDER=codex-agent python3 "$WIKI_HOME/scripts/run-maintenance.py" \
  --config "$WIKI_HOME/.local/common.json" \
  --artifacts "$WIKI_RUN_DIR" \
  --lock-file "$WIKI_HOME/.local/operations-runs/maintenance.lock" \
  --qmd "$QMD_BIN" \
  --reconcile "/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/scripts/sync-qmd-collections.py" \
  --budget-seconds 1200 --termination-grace-seconds 10 \
  --observation-margin-seconds 30 --stall-seconds 180
```

2. Retain the exact first `artifacts` event path and the execution handle. Read progress only at that path: `maintenance/progress.json` and its named detail. The runner's absolute observation bound is 1240 seconds, plus at most 11 seconds to terminate its own helper. Check the same handle in waits of at most 60 seconds; at most 22 observations, never restart this allowance after a context switch. After 180 seconds without durable progress the runner saves one diagnosis; a living process alone is not progress. Maximum 20 new source extractions per helper (existing default); concurrency stays configured at 8. This is a safety bound, not a next-day throughput guarantee.
3. At completion read `observation.json`, `helper.exitcode` and `maintenance/report.json`. Full success requires runner/helper exit 0, explicit `ok:true`, no pending/remaining work, and completed context results. If the observation bound is reached or a final report is missing/malformed, perform one diagnosis: read `process.json`, `diagnosis.json`, bounded progress and at most 4000 characters of the failing stderr. Record incomplete/failed with exact remaining-work/process evidence, then stop observing. No second collector, polling loop, inferred success or broad process termination. A still-running/unknown owner or custody marker blocks another run; report it for diagnosis. Do not automatically delete locks or retry maintenance.
4. Source indexing runs before model-dependent wiki work. Record source-index status separately from source-summary publication, daily pending/overdue work, initial pending/unextracted backlog, capacity/fairness, global completion and later outer QMD update/embed/status. `completedAt` is only run end. Inner wiki `lastCompleted` is not an outer job success. Unknown or absent dimensions remain unknown.
5. Immediately before updating newest-first memory, reread its bounded current header. Preserve prior entries; if changed, reread and retry insertion once. Record time, exact artifacts, limits/elapsed/exit outcomes, source index, daily work/deadlines, initial backlog, last completed wiki time, global completion, QMD document/vector counts when available, blockers and remaining work. A manual run or config readback does not prove a scheduled run; retain separate open acceptance for the first actual scheduled execution and full multi-day import plus no-op.

Ownership:
- Select only the existing `.local/common.json`, all eight original repositories and recursive Meetings/Projects including Projects/Private. Keep source files/configuration read-only. Do not narrow scope or change models/dependencies.
- Writes are limited to configured generated wiki/state, existing QMD data, task-owned ignored artifacts and this automation's memory. Honor the common maintenance lock and wiki writer lock. No additional scheduler/watcher, commit, push or merge.
- WikiQuery remains the knowledge entry and checks original freshness; query and merge do not trigger maintenance. Current original search does not certify wiki completion.

Report briefly with the artifact link: source search result, daily work and missed deadlines, initial backlog, overall complete/incomplete/failed, and actionable blocker. Keep isolated, manual productive and actual scheduled evidence distinct.
