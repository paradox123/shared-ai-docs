# Scheduled Index Maintenance

Use this reference for recurring QMD index/update automations.

Opening sequence:

```bash
CODEX_HOME_RESOLVED="${CODEX_HOME:-$HOME/.codex}"
sed -n '1,220p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/automation.toml"
test -f "$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md" && \
  sed -n '1,220p' "$CODEX_HOME_RESOLVED/automations/<automation-id>/memory.md" || \
  echo "(missing memory)"
```

Rules:

1. Read the automation definition and memory before repo orientation, vault startup docs, or broad filesystem scans.
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
3. Run maintenance commands from `/` so QMD does not inherit a fragile project working directory:

```bash
"$QMD_BIN" update
"$QMD_BIN" embed
"$QMD_BIN" status
```

4. Run `qmd embed` only if `qmd update` succeeds.
5. Capture run time with a portable command such as `date '+%Y-%m-%dT%H:%M:%S%z'`. Do not use GNU-only forms such as `date -Is`; macOS `date` rejects them.
6. Update the automation memory with run time, command outcomes, indexed file count, vector count, collections touched, and blockers.
7. Do not repair macOS privacy/TCC, QMD installation, runtime, or permission issues during a routine index run; record the blocker and stop.
