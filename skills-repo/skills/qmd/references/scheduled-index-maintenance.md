# Scheduled Index Maintenance

Use this reference for recurring QMD index/update automations.

Opening sequence:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
MEMORY_PATH="$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md"
sed -n '1,220p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml"
python3 - "$MEMORY_PATH" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
if not path.exists():
    print("(missing memory)")
    raise SystemExit(0)

text = path.read_text(errors="replace")
cap = 8000
marker = "\n...[older memory omitted]...\n"
if len(text) <= cap:
    print(text, end="" if text.endswith("\n") else "\n")
else:
    visible = max(0, cap - len(marker))
    print(text[:visible] + marker, end="")
PY
```

Rules:

1. Read the automation definition and the character-bounded newest-state memory excerpt before repo orientation, vault startup docs, or broad filesystem scans. QMD maintenance memory is newest-first, so do not print historical tail sections. Parse the complete file only inside a targeted helper that emits the exact state needed for the run.
2. Resolve the QMD CLI and its runtime before the maintenance commands. Codex automation shells may have a minimal `PATH`, so load Homebrew shellenv if available, then verify both `qmd` and `node`:

```bash
for brew in /opt/homebrew/bin/brew /usr/local/bin/brew; do
  if [ -x "$brew" ]; then
    eval "$("$brew" shellenv)"
    break
  fi
done

QMD_BIN="$(command -v qmd || true)"
NODE_BIN="$(command -v node || true)"

if [ -z "$QMD_BIN" ]; then
  echo "QMD blocker: qmd CLI is not on PATH"
fi

if [ -n "$QMD_BIN" ] && [ -z "$NODE_BIN" ]; then
  echo "QMD blocker: qmd CLI found at $QMD_BIN but node is not on PATH"
fi
```

If `qmd` or its required runtime is unavailable, record the blocker in automation memory and stop. Do not force QMD through `bun` unless the installed `qmd` shim itself selects `bun`; npm-installed QMD native modules can fail under the wrong runtime.
3. Preflight the QMD database location before maintenance. QMD uses `INDEX_PATH` when set; otherwise it stores the database under `${XDG_CACHE_HOME:-$HOME/.cache}/qmd/index.sqlite`. SQLite also needs the containing directory to be writable for journal or WAL files, so checking only the database file is insufficient:

```bash
if [ -n "${INDEX_PATH:-}" ]; then
  QMD_DB_PATH="$INDEX_PATH"
else
  QMD_DB_PATH="${XDG_CACHE_HOME:-$HOME/.cache}/qmd/index.sqlite"
fi
QMD_DB_DIR="$(dirname "$QMD_DB_PATH")"
QMD_DB_PARENT="$(dirname "$QMD_DB_DIR")"

if [ -e "$QMD_DB_PATH" ] && [ ! -w "$QMD_DB_PATH" ]; then
  echo "QMD blocker: index database is not writable: $QMD_DB_PATH"
elif [ -d "$QMD_DB_DIR" ] && [ ! -w "$QMD_DB_DIR" ]; then
  echo "QMD blocker: index directory is not writable: $QMD_DB_DIR"
elif [ ! -d "$QMD_DB_DIR" ] && { [ ! -d "$QMD_DB_PARENT" ] || [ ! -w "$QMD_DB_PARENT" ]; }; then
  echo "QMD blocker: index directory cannot be created under: $QMD_DB_PARENT"
fi
```

Stop before `qmd update` when this preflight finds a blocker. In a sandboxed automation, a non-writable `~/.cache/qmd` is an execution-environment/write-root problem, not evidence that Homebrew SQLite is missing. If QMD still returns `SQLITE_CANTOPEN` after a clean preflight, report database-path access as the primary symptom and preserve the exact stderr for later diagnosis; do not promote QMD's generic `sqlite-vec`/Homebrew suggestion to the root cause until storage access has been ruled out.
4. After collection reconciliation, run update, conditional embedding, and status in one shell operation from `/` so QMD does not inherit a fragile project working directory. Shell variables do not persist across tool calls: if reconciliation happened in an earlier call, repeat Rule 2's Homebrew/QMD/Node resolution once at the start of this operation. Do not rebuild that environment separately before each maintenance command. Capture every command's outcome and still run status after an update or embed failure:

```bash
cd /
qmd_update_rc=0
"$QMD_BIN" update || qmd_update_rc=$?

qmd_embed_rc=
if [ "$qmd_update_rc" -eq 0 ]; then
  qmd_embed_rc=0
  "$QMD_BIN" embed || qmd_embed_rc=$?
fi

qmd_status_rc=0
"$QMD_BIN" status || qmd_status_rc=$?
printf 'qmd_update_rc=%s\nqmd_embed_rc=%s\nqmd_status_rc=%s\n' \
  "$qmd_update_rc" "${qmd_embed_rc:-skipped}" "$qmd_status_rc"
```

5. Capture run time with a portable command such as `date '+%Y-%m-%dT%H:%M:%S%z'`. Do not use GNU-only forms such as `date -Is`; macOS `date` rejects them.
6. Update the automation memory with run time, command outcomes, indexed file count, vector count, collections touched, and blockers. Immediately before applying the patch, reread a small current header excerpt such as `sed -n '1,40p' "$MEMORY_PATH"` and anchor on the exact current title/header fields. Do not anchor a newest-first insertion on an older run body from the opening output. If the file changed concurrently, reread and retry once.
7. Do not repair macOS privacy/TCC, QMD installation, runtime, or permission issues during a routine index run; record the blocker and stop.
