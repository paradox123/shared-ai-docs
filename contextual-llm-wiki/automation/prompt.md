Maintain the common production DanielsVault LLM wiki, then the single QMD index and embeddings.

Startup and state:
- This is the existing Codex/QMD maintenance task. Load the QMD skill and its Scheduled Index Maintenance reference when available. Their required loading may precede task-state reads; otherwise defer injected repository/vault startup until automation state is read.
- Automation ID: `update-qmd-index-daily`.
- Resolve `CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"` in each shell that reads automation state.
- Read `$CODEX_HOME_RESOLVED/automations/update-qmd-index-daily/automation.toml` and the newest-first memory at `$CODEX_HOME_RESOLVED/automations/update-qmd-index-daily/memory.md` before repository, Node or QMD commands. Limit visible memory to the first 8000 characters including any omission marker; create it if missing. Do not run broad filesystem scans or vault orientation for this maintenance task.

Execution:
1. Follow the QMD Scheduled Index Maintenance runtime/database preflight. Load Homebrew shellenv where available, then prepend `/opt/homebrew/opt/node@22/bin` if its existing Node binary is executable, resolve QMD_BIN and Node, and check the QMD database directory is writable. If runtime or permissions are unavailable, record the blocker and stop; do not repair installations or macOS TCC.
2. Run this repository-owned helper once from the local checkout. The common config includes all eight selected original repositories and recursive Meetings and Projects including Projects/Private. Inventory reports actual present files; never substitute fixtures. In the same shell as QMD_BIN resolution, use:

```bash
if [ -x /opt/homebrew/opt/node@22/bin/node ]; then
  export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
fi
if ! command -v node >/dev/null 2>&1; then
  echo "QMD blocker: existing Node runtime unavailable" >&2
  exit 1
fi
if ! command -v codex >/dev/null 2>&1 && [ -x /Applications/ChatGPT.app/Contents/Resources/codex ]; then
  export PATH="/Applications/ChatGPT.app/Contents/Resources:$PATH"
fi
WIKI_HOME="/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/contextual-llm-wiki"
WIKI_RUN_DIR="$WIKI_HOME/.local/operations-runs/$(date '+%Y%m%dT%H%M%S')-$$"
LLMWIKI_PROVIDER=codex-agent python3 "$WIKI_HOME/scripts/maintain-index.py" \
  --config "$WIKI_HOME/.local/common.json" \
  --artifacts "$WIKI_RUN_DIR" \
  --lock-file "$WIKI_HOME/.local/operations-runs/maintenance.lock" \
  --qmd "$QMD_BIN" \
  --reconcile "/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/scripts/sync-qmd-collections.py"
```

3. The first JSON event gives the artifact directory. Save that exact path and keep polling the same execution handle until it finishes. The first full compilation may take much longer than a daily incremental run. Do not launch another copy to recover output. The helper owns reconciliation, provider preflight, wiki maintain/status/lint and global QMD update/embed/status in that order. Do not duplicate its commands.
4. Read `report.json` from the reported directory. Complete success requires helper exit 0, `ok: true`, and no failed or pending work. A verified bounded failure may complete independent work and safe QMD steps while retaining exit 1 and `ok: false`. Read each context's `failures`, `pending`, `completed`, `unchanged` and exact wiki `report` path plus top-level `remaining`. Missing/malformed output is never success. For a failed step, read its bounded stdout/stderr and recorded exitcode. Stop after reporting failure; no automatic source edits, scope changes or repeated repairs. A held lock means another run owns maintenance.
5. Immediately before updating memory, reread a bounded current header excerpt. Record run time, artifact path, context, no-op versus compilation, source/page counts, last completed wiki maintenance, reconciliation summary, QMD document/vector counts from the qmd-status output, exit outcomes, failures and remaining work, and any blocker. Distinguish full success, partial failure and an incomplete run; never advance the last completed maintenance time based on partial results. Preserve earlier entries. If the header changed concurrently, reread and retry the memory insertion once.

Ownership:
- Original project sources and source configuration remain read-only. The helper may write the configured generated wiki and its state, its QMD collection, existing QMD data, ignored local run artifacts and this automation's memory.
- Only `.local/common.json` is selected; personal and professional sources share this wiki. Do not substitute acceptance configs, reduce source coverage, create other schedulers/watchers, commit, push or merge.
- QMD remains the only persisted retrieval engine. Do not create or inspect a legacy `.rag/store`.
- Query and merge do not trigger maintenance; do not claim real-time freshness. Activation of this automation is not proof that the first full import completed.

Report briefly: wiki updated or no-op, source/page counts, QMD update/embed result, artifact link, and any actionable blocker. Distinguish full production completion from earlier acceptance-only evidence.
