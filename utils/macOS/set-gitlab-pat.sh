#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="ncg_gitlab_pat"
ACCOUNT_NAME="${1:-$USER}"
ZSHRC="${HOME}/.zshrc"

if ! command -v security >/dev/null 2>&1; then
  echo "Fehler: macOS 'security' Tool nicht gefunden."
  exit 1
fi

read -rsp "GitLab PAT eingeben: " GITLAB_PAT
echo

if [ -z "$GITLAB_PAT" ]; then
  echo "Fehler: Kein PAT eingegeben."
  exit 1
fi

# PAT im macOS Keychain speichern/ueberschreiben
security add-generic-password -a "$ACCOUNT_NAME" -s "$SERVICE_NAME" -w "$GITLAB_PAT" -U >/dev/null

# Lade-Block in ~/.zshrc idempotent aktualisieren
mkdir -p "$(dirname "$ZSHRC")"
touch "$ZSHRC"

TMP_FILE="$(mktemp)"
awk '
  BEGIN { skip=0 }
  /^# >>> ncg gitlab pat >>>$/ { skip=1; next }
  /^# <<< ncg gitlab pat <<</ { skip=0; next }
  skip==0 { print }
' "$ZSHRC" > "$TMP_FILE"

cat >> "$TMP_FILE" <<'ZSH_BLOCK'

# >>> ncg gitlab pat >>>
if [ -z "${GITLAB_PAT:-}" ]; then
  GITLAB_PAT="$(security find-generic-password -a "$USER" -s "ncg_gitlab_pat" -w 2>/dev/null || true)"
  export GITLAB_PAT
fi
# <<< ncg gitlab pat <<<
ZSH_BLOCK

mv "$TMP_FILE" "$ZSHRC"

echo "OK: PAT gespeichert und ~/.zshrc aktualisiert."
echo "Jetzt ausfuehren: source ~/.zshrc"
echo "Test: [ -n \"$GITLAB_PAT\" ] && echo 'PAT geladen' || echo 'PAT fehlt'"
