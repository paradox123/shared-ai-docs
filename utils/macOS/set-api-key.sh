#!/usr/bin/env bash
set -euo pipefail

ENV_VAR_NAME="${1:-}"
ACCOUNT_NAME="${2:-$USER}"
ZSHRC="${HOME}/.zshrc"

usage() {
  echo "Usage: $0 ENV_VAR_NAME [ACCOUNT_NAME]"
  echo "Beispiel: $0 PROMPTFOO_API_KEY"
}

if [ -z "$ENV_VAR_NAME" ]; then
  usage
  exit 1
fi

if [[ ! "$ENV_VAR_NAME" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "Fehler: Ungueltiger Umgebungsvariablenname: $ENV_VAR_NAME"
  echo "Erlaubt sind Buchstaben, Zahlen und Unterstriche; das erste Zeichen darf keine Zahl sein."
  exit 1
fi

if ! command -v security >/dev/null 2>&1; then
  echo "Fehler: macOS 'security' Tool nicht gefunden."
  exit 1
fi

SERVICE_NAME="env_api_key_${ENV_VAR_NAME}"
BEGIN_MARKER="# >>> api key ${ENV_VAR_NAME} >>>"
END_MARKER="# <<< api key ${ENV_VAR_NAME} <<<"

read -rsp "${ENV_VAR_NAME} eingeben: " API_KEY
echo

if [ -z "$API_KEY" ]; then
  echo "Fehler: Kein API-Key eingegeben."
  exit 1
fi

# API-Key im macOS Keychain speichern/ueberschreiben
security add-generic-password -a "$ACCOUNT_NAME" -s "$SERVICE_NAME" -w "$API_KEY" -U >/dev/null

# Lade-Block in ~/.zshrc idempotent aktualisieren
mkdir -p "$(dirname "$ZSHRC")"
touch "$ZSHRC"

TMP_FILE="$(mktemp)"
awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" '
  $0 == begin { skip=1; next }
  $0 == end { skip=0; next }
  skip==0 { print }
' "$ZSHRC" > "$TMP_FILE"

cat >> "$TMP_FILE" <<ZSH_BLOCK

$BEGIN_MARKER
if [ -z "\${${ENV_VAR_NAME}:-}" ]; then
  ${ENV_VAR_NAME}="\$(security find-generic-password -a "$ACCOUNT_NAME" -s "$SERVICE_NAME" -w 2>/dev/null || true)"
  export ${ENV_VAR_NAME}
fi
$END_MARKER
ZSH_BLOCK

mv "$TMP_FILE" "$ZSHRC"

echo "OK: ${ENV_VAR_NAME} gespeichert und ~/.zshrc aktualisiert."
echo "Jetzt ausfuehren: source ~/.zshrc"
echo "Test: [ -n \"\$${ENV_VAR_NAME}\" ] && echo '${ENV_VAR_NAME} geladen' || echo '${ENV_VAR_NAME} fehlt'"
