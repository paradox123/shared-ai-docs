# Nebenkostenabrechnung 2025 - Messwerte Review-Slice

## Zweck

Diese Child-Spec definiert **genau einen** naechsten Delivery-Slice aus der Parent-Spec `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`:

- die review-pflichtigen **Messwert-Dokumente 2025** in eine belastbare `input.reviewed.json` zu ueberfuehren

Sie dient ausdruecklich dazu, den naechsten Implementierungsschritt **ohne Freestyle** zu schneiden. Daher enthaelt sie fuer diesen Slice:

- klaren Scope
- explizite Akzeptanzkriterien
- konkrete Test Cases
- Verification Commands

## Parent-Bezug

Massgebliche Parent-Spec:

- `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`

Diese Child-Spec ersetzt die Parent-Spec nicht, sondern schneidet aus ihr nur den naechsten operativen Delivery-Slice heraus.

## Warum eine eigene Child-Spec

Die Parent-Spec ist bewusst breit und beschreibt den gesamten 2025er Ausfuehrungspfad. Fuer `spec-change-delivery` ist der naechste Schritt

- "alle 16 Review-Punkte in `input.reviewed.json` ueberfuehren"

zu gross und nicht hinreichend als einzelner verifizierbarer Slice definiert.

Normative Split-Entscheidung:

- die Parent-Spec bleibt die uebergeordnete 2025-Ausfuehrungsspec
- die konkrete Delivery-Arbeit wird in Child-Specs mit eigenem DoD geschnitten
- dieser erste Child-Slice behandelt **nur die Messwerte-Dokumente**

## In Scope

Dieser Slice umfasst ausschliesslich die folgenden 2025er Quellen:

- `Messwerte/Ablesungen24_25.pdf`
- `Messwerte/Monatswerte - 2025 -  - NE0001(P621593463).pdf`
- `Messwerte/026490450 - AQ -2025-NE0000(P621450654).pdf`

Und nur die daraus abgeleiteten Aufgaben:

1. fachliche Einordnung der drei Dokumente in die operative Messwertkette 2025
2. Uebernahme der belastbar ableitbaren Messwerte in `input.reviewed.json`
3. Entfernung genau der zugehoerigen Review-Punkte aus `review-output.json`
4. technische Validierung, dass die uebernommenen Messwerte von `finalize-year-input` und dem Rechenkern getragen werden

## Out of Scope

Explizit **nicht** Teil dieses Slices:

- Tibber-/BE1-Stromrechnungen
- Gebaeudeversicherungen
- Sammelbelege `Belege_BE1`, `Belege_BE2`, `Belege_BE2_II`, `Belege_Liegenschaft`
- `Öl_25.pdf`
- OCR- oder Parser-Neuentwicklung als generische Plattformfunktion
- vollstaendige Finalisierung der 2025er Abrechnung

## Operatives Zielartefakt

Ziel dieses Slices ist **nicht** bereits das finale `input.json`, sondern:

1. ein aktualisiertes `input.reviewed.json`, in dem die Messwerte fuer die drei oben genannten Dokumente sauber vorliegen
2. ein aktualisiertes `review-output.json`, in dem die zu diesen drei Dokumenten gehoerigen Review-Items entfernt sind
3. optional zusaetzlich ein **technisches** Hilfsartefakt `review-output.messwerte-validation.json` mit leerer `items[]`-Liste, um nur die Messwert-Struktur gegen `finalize-year-input` und den Rechenkern zu pruefen

## Normative Festlegungen

### 1. Dokumentrollen

Die drei Messwerte-Dokumente sind fuer diesen Slice normativ wie folgt zu behandeln:

- `Ablesungen24_25.pdf`:
  - primaere Quelle fuer manuelle Jahresstichtagsablesungen der Stromzaehler
  - insbesondere fuer `z-strom-ne1` fachlich massgeblich

- `Monatswerte - 2025 -  - NE0001(P621593463).pdf`:
  - spezialisierte Zusatzquelle fuer NE1
  - relevant fuer Heizkosten-/Warmwasser-/ggf. Kaltwasserwerte in der Teilperiode von Ingeborg Hainz

- `026490450 - AQ -2025-NE0000(P621450654).pdf`:
  - Hauptquelle fuer die allgemeinen Ablesewerte 2025 ausserhalb des NE1-Sonderfalls

### 2. NE1-Strom ist Pflichtbestandteil dieses Slices

Die folgenden bereits feststehenden Werte muessen in diesem Slice in `input.reviewed.json` vorhanden sein:

- `z-strom-ne1`, `stichtag = 2025-03-29`, `messwert = 34684`
- `z-strom-ne1`, `stichtag = 2025-12-31`, `messwert = 35005.6`

Diese beiden Werte gelten fuer diesen Slice als **nicht mehr offen**.

### 3. Messwerte nur bei belastbarer Lesung

Fuer alle weiteren aus den drei Dokumenten uebernommenen Werte gilt:

- nur Werte mit fachlich belastbarer Lesung duerfen in `input.reviewed.json` uebernommen werden
- unsichere, mehrdeutige oder nicht sauber lesbare Werte bleiben ausserhalb dieses Slices offen
- dieser Slice darf also kleiner enden als "alle Werte aus allen drei Dokumenten", wenn einzelne Werte fachlich nicht belastbar sind

### 4. Review-Entfernung nur dokumentbezogen

Es duerfen nur die Review-Punkte entfernt werden, die direkt zu den drei Messwerte-Dokumenten gehoeren.

Alle anderen Review-Punkte bleiben fuer nachfolgende Child-Slices bestehen.

## Akzeptanzkriterien

Dieser Slice ist fachlich fertig, wenn alle folgenden Punkte erfuellt sind:

1. Die drei Messwerte-Dokumente sind in der Umsetzung explizit verarbeitet oder bewusst als nicht belastbar begrenzt dokumentiert.
2. `input.reviewed.json` enthaelt mindestens die beiden verbindlichen NE1-Stromablesungen fuer `z-strom-ne1`.
3. Alle aus den drei Messwerte-Dokumenten belastbar ableitbaren weiteren Ablesungen sind in kanonischer Struktur in `ablesungen[]` uebernommen.
4. `review-output.json` enthaelt keine offenen Items mehr fuer genau diese drei Messwerte-Dokumente.
5. Ein technischer Validierungslauf mit `finalize-year-input` und leerem `review-output.messwerte-validation.json` scheitert nicht an Messwert-bezogenen Struktur-/Referenzproblemen.
6. Ein technischer Abrechnungslauf auf dem daraus erzeugten `input.messwerte.json` ist moeglich.

## Test Cases

### TC1 NE1-Stromablesungen sind im reviewed input vorhanden

Ziel:

- sicherstellen, dass die beiden verbindlichen manuellen NE1-Stromablesungen im reviewed input stehen

Verification:

- JSON-Check auf `input.reviewed.json`

Expected Result:

- genau ein Eintrag fuer `z-strom-ne1` am `2025-03-29` mit `34684`
- genau ein Eintrag fuer `z-strom-ne1` am `2025-12-31` mit `35005.6`

### TC2 Messwerte-Review-Punkte sind aus review-output entfernt

Ziel:

- sicherstellen, dass nur die drei Messwerte-Dokumente aus dem Review-Backlog verschwinden

Verification:

- JSON-Check auf `review-output.json`

Expected Result:

- keine `items[]` mehr mit
  - `Messwerte/Ablesungen24_25.pdf`
  - `Messwerte/Monatswerte - 2025 -  - NE0001(P621593463).pdf`
  - `Messwerte/026490450 - AQ -2025-NE0000(P621450654).pdf`
- nicht-messwertbezogene Review-Punkte duerfen weiter vorhanden sein

### TC3 Finalisierung scheitert nicht an Messwert-Struktur

Ziel:

- sicherstellen, dass die uebernommenen Messwerte schema- und referenzkonform sind

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.messwerte-validation.json" \
  --output-json "$NK_2025_WORK/input.messwerte.json"
```

Expected Result:

- kein Fehler wegen unbekannter Zaehler, fehlender Stichtage, ungueltiger Messwertstruktur oder meterbezogener Referenzen
- der Lauf verwendet bewusst ein technisches Review-Artefakt mit leerer `items[]`-Liste, damit nur die Messwert-Struktur geprueft wird

### TC4 Technischer Abrechnungslauf mit messwert-bereinigtem Input

Ziel:

- sicherstellen, dass der Rechenkern die uebernommenen Messwerte technisch verarbeiten kann

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.messwerte.json" \
  --output-dir "$NK_2025_WORK/statements-messwerte" \
  --skip-pdf
```

Expected Result:

- der Lauf endet technisch erfolgreich
- fuer `mp-ne1-hainz` ist ein Statement-Artefakt vorhanden
- der direkte Wohnungsstrom fuer NE1 ist aus den beiden manuellen Stichtagen ableitbar

## Verification Commands

Vorbereitung:

```bash
export NK_REPO="/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung"
export NK_2025_WORK="$NK_REPO/data/2025/work"
cd "$NK_REPO"
```

Build-Artefakte fuer den Slice vorausgesetzt:

```bash
dotnet run --project src/Nebenkosten.Import -- \
  build-year-input \
  --scaffold-json "$NK_2025_WORK/scaffold.json" \
  --scaffold-state-json "$NK_2025_WORK/scaffold.state.json" \
  --carryover-json "$NK_2025_WORK/carryover-output.json" \
  --source-dir "/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2025" \
  --output-dir "$NK_2025_WORK/build"
```

TC1 / TC2 als JSON-Sichtpruefung:

```bash
python3 - <<'PY'
import json
from pathlib import Path

base = Path("/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build")
with open(base / "input.reviewed.json", encoding="utf-8") as f:
    reviewed = json.load(f)
with open(base / "review-output.json", encoding="utf-8") as f:
    review = json.load(f)

reads = [x for x in reviewed["ablesungen"] if x["zaehler_id"] == "z-strom-ne1"]
print("ne1_reads", reads)
print("review_sources", [x["source_relative_path"] for x in review["items"]])
PY
```

TC3:

```bash
python3 - <<'PY'
import json
from pathlib import Path

base = Path("/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build")
with open(base / "review-output.json", encoding="utf-8") as f:
    review = json.load(f)

review["items"] = []

with open(base / "review-output.messwerte-validation.json", "w", encoding="utf-8") as f:
    json.dump(review, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
```

```bash
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.messwerte-validation.json" \
  --output-json "$NK_2025_WORK/input.messwerte.json"
```

TC4:

```bash
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.messwerte.json" \
  --output-dir "$NK_2025_WORK/statements-messwerte" \
  --skip-pdf
```

## Definition of Done fuer diesen Slice

Der Slice ist nur dann `ready for implementation`, wenn:

- Scope und Out-of-Scope unveraendert bleiben
- die Implementierung ausschliesslich die drei Messwerte-Dokumente adressiert
- alle vier Test Cases mit frischer Evidenz abgehakt werden
- verbleibende offene Themen explizit an nachfolgende Child-Slices uebergeben werden

## Nachfolgende Child-Slices

Voraussichtliche naechste Slices nach Abschluss dieser Child-Spec:

1. Gebaeudeversicherungen 2025 -> reviewed kostenbelege
2. Liegenschaftsbelege 2025 -> reviewed kostenbelege
3. BE1-/BE2-Sammelbelege und `Öl_25.pdf` -> reviewed kostenbelege

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-09 | 0 | Codex | Child-Spec aus Parent-Spec herausgeschnitten, um den naechsten Delivery-Slice `Messwerte -> input.reviewed.json` mit Akzeptanzkriterien, Test Cases und Verification Commands explizit zu definieren |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
