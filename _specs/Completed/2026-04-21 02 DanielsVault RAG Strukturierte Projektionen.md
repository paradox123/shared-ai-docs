**Date:** 2026-04-21  
**Status:** 🟢 Accepted  
**Scope:** Phase-1-Definition fuer strukturierte Projektionen und exakte Datenabfragen mit Quellenbezug

---

# 02 DanielsVault RAG Strukturierte Projektionen

## Zweck

Diese Child-Spec definiert den minimalen strukturierten Retrieval-Kanal fuer exakte Fragen (z. B. Variablen, IDs, konkrete Werte).

## Reihenfolge und Abhaengigkeiten

- Reihenfolge: `02`
- setzt `01` voraus
- Voraussetzung fuer `03` (hybrides Retrieval) und `05` (agentische Nutzung)

## Kernanforderung

Semantische Suche bleibt Hauptpfad fuer freie Fragen.

Zusaetzlich muss Phase 1 mindestens einen strukturierten Record-Typ bereitstellen, um exakte Fragen robust und mit Quellenbezug beantworten zu koennen.

## Phase-1-Mindestumfang

Verbindlich:

- ein initialer `record_type` fuer exakte Nachweise in `ncg/ncg-docs`
- Query-Pfad fuer exakte Filterabfragen
- Rueckfuehrbarkeit jedes Facts auf konkrete Quelle

### Verbindlicher erster Record-Typ (Phase 1)

Der erste verpflichtende `record_type` in Phase 1 ist:

- `ci_setting_fact`

Ziel:

- exakte Fragen zu CI-Pipelines, Umgebungsvariablen und gesetzten CI-Variablen belastbar beantworten

Pflichtfelder fuer `ci_setting_fact`:

- `record_type` (fix: `ci_setting_fact`)
- `setting_name` (z. B. Variablen- oder Key-Name)
- `setting_value` (wenn vorhanden; sonst `null` mit Nachweis)
- `setting_scope` (z. B. global/job/pipeline)
- `path`
- `source_anchor`
- `domain`
- `git_root`

## Record-Metadatenminimum

Jeder strukturierte Record muss mindestens enthalten:

- `record_type`
- `path`
- `git_root`
- `domain`
- `source_anchor` (z. B. Abschnitt/Key-Pfad/Zeilenanker)
- fachlicher Schluessel (z. B. `name` oder `entity_id`)

## Antwortanforderung fuer exakte Queries

Mindestens:

- gefundener Wert/Fakt
- Quellenpfad
- Source-Anchor
- kurzer Nachweis warum der Fakt passt

## Filter-Semantik (Phase 1, verbindlich)

Fuer `rag retrieve structured --filter` gelten in Phase 1 folgende Operatoren:

- `field=value`:
  exakter Vergleich (case-sensitive)
- `field~value`:
  Teilstring-Suche (case-insensitive)
- `field~A|B`:
  OR-Suche ueber Teilstrings (case-insensitive), entspricht `field~A OR field~B`

Normative Regel:

- Andere Operatoren sind in Phase 1 nicht verpflichtend und duerfen nicht stillschweigend anders interpretiert werden.

## Akzeptanzkriterien

1. `ci_setting_fact` ist end-to-end abfragbar.
2. Exakte Queries liefern reproduzierbar Facts mit Quellenbezug.
3. Fehlende strukturierte Treffer werden transparent gemeldet (statt halluziniert).

## Verifikation (Nachweisform)

```bash
mkdir -p .rag/runs
command -v rag >/dev/null
rag --version > .rag/runs/00-rag-version.txt
test -s .rag/runs/00-rag-version.txt
rag records project --scope ncg/ncg-docs --record-type ci_setting_fact --output .rag/runs/02-ci-setting-facts.jsonl
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name~BUILD" --top-k 5 --format json > .rag/runs/02-q1-build-vars.json
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name=DEPLOY_TARGET" --top-k 5 --format json > .rag/runs/02-q2-deploy-target.json
rag retrieve structured --scope ncg/ncg-docs --record-type ci_setting_fact --filter "setting_name~BASE_URL|ENDPOINT" --top-k 5 --format json > .rag/runs/02-q3-endpoints.json
python3 - <<'PY'
import json
from pathlib import Path
for name in [
    ".rag/runs/02-q1-build-vars.json",
    ".rag/runs/02-q2-deploy-target.json",
    ".rag/runs/02-q3-endpoints.json",
]:
    rows = json.loads(Path(name).read_text())
    hits = rows.get("facts", [])
    assert hits, f"keine facts: {name}"
    for fact in hits:
        assert fact.get("source_path"), f"fehlender source_path: {name}"
        assert fact.get("source_anchor"), f"fehlender source_anchor: {name}"
PY
```

Gate-Regel:

- Jeder Schritt in der Verifikationsstrecke muss real mit Exit-Code `0` laufen.
- `blocked` oder `failed` ist ein Abnahmefehler (kein gueltiger Teilerfolg).

Verbindliche Beispielqueries fuer Phase-1-Abnahme:

1. `Welche CI-Umgebungsvariablen sind fuer den Build definiert?`
2. `Welche CI-Variable steuert das Deployment-Target, und wo ist sie dokumentiert?`
3. `Welche Pipeline-Settings verweisen auf BaseUrl/Endpoint-Konfigurationen?`

## Nicht in dieser Spec

- Wahl eines finalen Persistenzbackends als Architekturentscheidung
- Re-Ranking
- Eval-Harness-Metrikberechnung

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-21 | Codex | Child-Spec fuer strukturiertes Retrieval aus Parent-Spec abgeleitet. |
| 2026-04-21 | Codex | Verbindlichen Phase-1-Record-Typ `ci_setting_fact` mit Pflichtfeldern und konkretisierter Verifikation festgelegt. |
| 2026-04-22 | Codex | Drei verbindliche Beispielqueries fuer die Abnahme von `ci_setting_fact` in die Verifikation aufgenommen. |
| 2026-04-22 | Codex | Verifikationskommandos fuer Projektion und drei strukturierte Beispielqueries inkl. Source-Anchor-Checks konkretisiert. |
| 2026-04-22 | Codex | Filteroperator-Semantik (`=`, `~`, `~...|...`) verbindlich definiert, um Implementierungsdrift zu vermeiden. |
| 2026-04-23 | User + Codex | Verifikation um harten `rag`-Install-Preflight (`command -v`, `--version`, non-empty Nachweisdatei) und eindeutige `blocked/failed`-Gate-Regel erweitert. |
| 2026-04-23 | User + Codex | Status auf `🔵 Implemented` gesetzt: Runtime-Implementierung liefert `ci_setting_fact` inkl. Filtersemantik (`=`, `~`, `~A|B`) und gruene Verifikationsausfuehrung gemaess 01-05-Evidenz. |
| 2026-04-23 | User + Codex | Status auf `🟢 Accepted` gesetzt: Closeout-Verification ist gruen und der zugehoerige OpenSpec-Change wurde archiviert. |

SessionId: codex-desktop-current-thread
