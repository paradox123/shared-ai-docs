**Date:** 2026-04-21  
**Status:** 🟢 Accepted  
**Scope:** Phase-1-Grundlage fuer DanielsVault-RAG: Domain-Scope, Datenquellen, Ignore-Regeln, Chunking und Metadaten

---

# 01 DanielsVault RAG Ingestion Scope und Metadaten

## Zweck

Diese Child-Spec definiert die verbindliche Grundlage fuer den ersten lauffaehigen RAG-Slice.

Sie legt fest:

1. welche Wissensraeume standardmaessig in Phase 1 indexiert werden
2. welche Dateien in Scope sind und welche ausgeschlossen werden
3. welches Chunking- und Metadaten-Minimum jede Indexeinheit tragen muss
4. welchen stabilen CLI-Contract Folge-Slices voraussetzen duerfen

## Reihenfolge und Abhaengigkeiten

- Reihenfolge: `01` (Startpunkt)
- Voraussetzung fuer `02`, `03`, `04`, `05`

## Domain- und Retrieval-Scope (Phase 1)

Verbindlicher Default-Scope:

- `/Users/dh/Documents/DanielsVault/ncg/ncg-docs`

Zusaetzlich im Phase-1-Index enthalten (nicht Default-Retrieval):

- `/Users/dh/Documents/DanielsVault/private`

Optionaler Opt-in (nicht Default):

- Full-Vault-Modus ueber `/Users/dh/Documents/DanielsVault`

Normative Regel:

- Default-Anfragen laufen ohne Zusatzparameter in `ncg/ncg-docs`.
- Zugriff auf `private` und Full-Vault erfolgt nur bewusst ueber explizite Scope-Parameter (`--scope private` oder `--scope all`).

## Datenquellen und Ignore-Regeln

In Scope (Phase 1):

- `*.md`
- ausgewaehlte `*.txt`
- ausgewaehlte `*.json`
- ausgewaehlte `*.yaml`

Out of Scope (Phase 1):

- `.git/`
- `.obsidian/`
- `node_modules/`
- Binaries
- Lockfiles
- grosse generierte Schema-Dateien

## Chunking- und Metadatenminimum

Jeder indexierte Chunk muss mindestens enthalten:

- `document_id`
- `path`
- `git_root`
- `domain`
- `section_title`
- `chunk_index`
- `last_modified`

## CLI-Contract (Phase-1-Stabilitaet)

Verbindlich in Phase 1:

- CLI-first Zugriff fuer Agenten
- stabile Basiskommandos fuer Ingestion und Retrieval

Beispielhafte Contract-Linie:

- `rag ingest run --scope ncg/ncg-docs`
- `rag retrieve semantic --scope ncg/ncg-docs --query "Wo ist die Migration zu Hetzner-Dev dokumentiert?"`

Normative Anforderung:

- Parameterkonventionen duerfen innerhalb Phase 1 nicht breaking geaendert werden.

## Akzeptanzkriterien

1. Ingestion laeuft fuer Default-Scope reproduzierbar.
2. Ignore-Regeln filtern ausgeschlossene Verzeichnisse/Dateitypen sicher aus.
3. Jeder Treffer traegt das definierte Metadatenminimum.
4. Default-Retrieval liefert keine ungewollte Full-Vault-Mischung.

## Verifikation (Nachweisform)

```bash
mkdir -p .rag/runs
command -v rag >/dev/null
rag --version > .rag/runs/00-rag-version.txt
test -s .rag/runs/00-rag-version.txt
rag ingest run --scope ncg/ncg-docs --output .rag/runs/01-ingest-ncg.json
rag ingest run --scope private --output .rag/runs/01-ingest-private.json
rag ingest run --scope ncg/ncg-docs --dry-run --list-files > .rag/runs/01-filelist.txt
python3 - <<'PY'
from pathlib import Path
text = Path(".rag/runs/01-filelist.txt").read_text()
blocked = ["/.git/", "/.obsidian/", "/node_modules/"]
assert not any(x in text for x in blocked), "ignore-regel verletzt"
PY
rag inspect chunks --scope ncg/ncg-docs --limit 20 --require-fields document_id,path,git_root,domain,section_title,chunk_index,last_modified > .rag/runs/01-metadata-check.json
rag retrieve semantic --scope ncg/ncg-docs --query "Wo ist die Migration zu Hetzner-Dev dokumentiert?" --top-k 5 --format json > .rag/runs/01-scope-gate.json
python3 - <<'PY'
import json
from pathlib import Path
rows = json.loads(Path(".rag/runs/01-scope-gate.json").read_text())
hits = rows.get("hits", [])
assert hits, "scope-gate lieferte keine Treffer"
assert all("/private/" not in h.get("path","") for h in hits), "default-scope leakage nach private"
PY
```

Gate-Regel:

- Jeder Schritt in der Verifikationsstrecke muss real mit Exit-Code `0` laufen.
- `blocked` oder `failed` ist ein Abnahmefehler (kein gueltiger Teilerfolg).

## Nicht in dieser Spec

- konkrete Embedding-Implementierung
- strukturierte Projektionen einzelner Record-Typen
- Eval-Harness-Implementierungsdetails
- Agent-Workflow-Orchestrierung

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-21 | Codex | Child-Spec aus Parent-Spec extrahiert und als Implementierungsstartpunkt definiert. |
| 2026-04-21 | Codex | Scope-Regeln praezisiert: `private` als Phase-1-Indexinhalt, aber nicht als Default-Retrieval ohne Scope-Override. |
| 2026-04-22 | Codex | Konkrete Verifikationskommandos fuer Ingestion, Ignore-Regeln, Metadaten und Scope-Gate ergaenzt. |
| 2026-04-22 | Codex | Beispielhafte CLI-Contract-Linie von Platzhaltern auf konkrete Commands umgestellt. |
| 2026-04-22 | Codex | Scope-Gate-Verifikation gehaertet: non-empty Treffer verpflichtend und Query auf erwartete Default-Domain ausgerichtet. |
| 2026-04-23 | User + Codex | Verifikation um harten `rag`-Install-Preflight (`command -v`, `--version`, non-empty Nachweisdatei) und eindeutige `blocked/failed`-Gate-Regel erweitert. |
| 2026-04-23 | User + Codex | Status auf `🔵 Implemented` gesetzt: Phase-1-Runtime und CLI wurden umgesetzt; Verifikationsstrecke 01-05 ist in `/Users/dh/Documents/DanielsVault/_shared/danielsvault-rag/.rag/status/verification-status-2026-04-23-runtime-open-spec.txt` vollstaendig gruen. |
| 2026-04-23 | User + Codex | Status auf `🟢 Accepted` gesetzt: Closeout-Verification wurde erneut vollstaendig gruen ausgefuehrt und OpenSpec-Change `rag-runtime-cli-delivery` ist archiviert. |

SessionId: codex-desktop-current-thread
