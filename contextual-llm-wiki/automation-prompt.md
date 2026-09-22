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
  --budget-seconds 10800 --termination-grace-seconds 10 \
  --observation-margin-seconds 30 --stall-seconds 180
```

2. Retain the exact first `artifacts` event path and the execution handle. Read progress only at that path: `maintenance/progress.json` and its named detail. The runner's absolute observation bound is 10840 seconds, plus at most 11 seconds to terminate its own helper. Check the same handle in waits of at most 60 seconds until it completes or the absolute elapsed-time bound is reached; polling frequency is not a work budget. Never reset the elapsed-time allowance after a context switch. After 180 seconds without durable progress the runner saves one diagnosis; a living process alone is not progress. Maximum 2500 new source extractions per helper (production catch-up capacity); actual concurrency is 8, including bounded packages. Compatible extractions are reused and a completed unchanged wiki is a no-op. These remain finite upper bounds, not a throughput guarantee.
3. At completion read `observation.json`, `helper.exitcode` and `maintenance/report.json`. Full success requires runner/helper exit 0, explicit `ok:true`, no pending/remaining work, and completed context results. If the observation bound is reached or a final report is missing/malformed, perform one diagnosis: read `process.json`, `diagnosis.json`, bounded progress and at most 4000 characters of the failing stderr. Record incomplete/failed with exact remaining-work/process evidence, then stop observing. No second collector, polling loop, inferred success or broad process termination. A still-running/unknown owner or custody marker blocks another run; report it for diagnosis. Do not automatically delete locks or retry maintenance.
4. Source indexing runs before model-dependent wiki work. Record source-index status separately from source-summary publication, daily pending/overdue work, initial pending/unextracted backlog, capacity/fairness, global completion and later outer QMD update/embed/status. `completedAt` is only run end. Inner wiki `lastCompleted` is not an outer job success. Unknown or absent dimensions remain unknown.
5. Immediately before updating newest-first memory, reread its bounded current header. Preserve prior entries; if changed, reread and retry insertion once. Record time, exact artifacts, limits/elapsed/exit outcomes, source index, daily work/deadlines, initial backlog, last completed wiki time, global completion, QMD document/vector counts when available, blockers and remaining work. A manual run or config readback does not prove a scheduled run; retain separate open acceptance for the first actual scheduled execution and full multi-day import plus no-op.

Ownership:
- Select only the existing `.local/common.json`, all eight original repositories and recursive Meetings/Projects including Projects/Private. Keep source files/configuration read-only. Do not narrow scope or change models/dependencies.
- Writes are limited to configured generated wiki/state, existing QMD data, task-owned ignored artifacts and this automation's memory. Honor the common maintenance lock and wiki writer lock. No additional scheduler/watcher, commit, push or merge.
- WikiQuery remains the knowledge entry and checks original freshness; query and merge do not trigger maintenance. Current original search does not certify wiki completion.

Human-readable reporting contract (mandatory):
- Before the final status block, report these labels exactly once, each with concrete evidence:
  - `LLM-Wiki:` one of `ERFOLGREICH`, `TEILWEISE`, `FEHLER`, or `NICHT AUSGEFÜHRT`, followed by source-summary publication, `lastCompleted`, `globalComplete`, pending/remaining counts and the relevant step exit.
  - `QMD:` one of `ERFOLGREICH`, `TEILWEISE`, `FEHLER`, or `NICHT AUSGEFÜHRT`, followed by the separate exit status of reconcile, update, embed and status, plus document/vector counts when available.
  - `Gesamt:` one of `ERFOLG`, `UNVOLLSTÄNDIG`, or `FEHLER`, derived only from the completion criteria above.
  - `Belegter Grund:` the actual reason from the report, diagnosis or bounded stderr, translated into plain German without changing its meaning.
  - `Offene Arbeit:` the exact remaining phase and counts, or `keine` when none remains.
- Never summarize a run only as `Wiki-Synthese wegen offener Dependency-Discovery unvollständig`, `Synthesis incomplete`, `shared-provider-failure`, `Fehler im Provider`, or another internal label. Explain what completed, what did not complete, how much remains, and which evidence supports the statement. For example, if the report says that source statements do not close dependent work, say that source summaries were saved but dependent synthesis pages could not be completed, then give the remaining source/page counts and `lastCompleted`/`globalComplete` values.
- Never infer a provider, runtime, storage, login, lock, or permission cause from a generic nonzero exit. If the artifacts do not identify the root cause, write `Ursache nicht bestimmt; belegt ist nur: <exact failed step, exit, and bounded stderr/report evidence>`. Do not call an absent or unknown cause a blocker.
- Never let successful QMD steps imply successful LLM-Wiki work. Always state both statuses independently, including when one is successful and the other is incomplete or failed. Keep scheduled-run evidence separate from manual runs and from the open full-import/no-op acceptance.
- Include the artifact directory link, source-index result, source-summary result, daily pending/overdue counts, initial pending/unextracted backlog, capacity/missed-round evidence, overall status, exact blocker or explicitly unknown cause, and next actionable step. Do not recommend retrying, deleting locks, changing configuration, or repairing installations unless the artifacts and prompt explicitly authorize that action.

Finaler Abschlussstatus (verbindlich):
- Die letzte sichtbare Ausgabe muss ein eigener, sehr auffälliger Statusblock sein. Keine weiteren Sätze, Links oder Listen nach diesem Block.
- Verwende exakt einen dieser drei Banner als erste Zeile des letzten Blocks:
  - Bei vollständigem Erfolg nach den oben definierten Kriterien:
    `🟢 ✅ ERFOLG – QMD-WARTUNG ABGESCHLOSSEN`
  - Wenn der Lauf technisch weiterarbeiten konnte, aber Wiki-/Backlog-/Lint-Arbeit offen oder nur teilweise erledigt ist:
    `🟠 ⚠️ UNVOLLSTÄNDIG – QMD-WARTUNG NICHT ABGESCHLOSSEN`
  - Bei Runtime-, Storage-, Login-, Provider-, Prozess- oder sonstigem Abbruchfehler:
    `🔴 ❌ FEHLER – QMD-WARTUNG ABGEBROCHEN`
- Direkt darunter höchstens drei kurze Zeilen: `Grund:`, `Ergebnis:`, `Nächster Schritt:`. `Grund:` muss den belegten technischen oder fachlichen Grund verständlich nennen oder ausdrücklich `Ursache nicht bestimmt` sagen. `Ergebnis:` muss mindestens `LLM-Wiki: <Status>` und `QMD: <Status>` enthalten; ergänze `Gesamt: <Status>`, wenn es in die Zeile passt. `Nächster Schritt:` muss die konkrete offene Arbeit oder den sicheren nächsten Schedulerlauf nennen. Nutze keine grünen Erfolgssymbole für einen nicht vollständigen Lauf.
- Der Banner muss am Ende der Antwort stehen und auch dann erscheinen, wenn ein Preflight, der Helper oder das Beobachten scheitert.
