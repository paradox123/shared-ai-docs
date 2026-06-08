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
2. Run maintenance commands from `/` so QMD does not inherit a fragile project working directory:

```bash
qmd update
qmd embed
qmd status
```

3. Run `qmd embed` only if `qmd update` succeeds.
4. Update the automation memory with run time, command outcomes, indexed file count, vector count, collections touched, and blockers.
5. Do not repair macOS privacy/TCC, QMD installation, or permission issues during a routine index run; record the blocker and stop.
