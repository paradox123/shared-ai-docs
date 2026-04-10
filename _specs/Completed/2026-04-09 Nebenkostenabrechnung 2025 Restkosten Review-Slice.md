# Nebenkostenabrechnung 2025 - Restkosten Review-Slice

## Status

Accepted and closed on 2026-04-10.

Closeout summary:

- Verification Commands im Closeout erneut gruen replayt.
- Zugehoeriger OpenSpec-Change archiviert unter `openspec/changes/archive/2026-04-10-2026-04-09-2025-restkosten-review`.

## Zweck

Diese Child-Spec definiert genau einen weiteren bounded Delivery-Slice aus der Parent-Spec `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`:

- die verbleibenden Review-Belege fuer Standardkosten, Brennstoffkosten und Heiznebenkosten in eine belastbare `input.reviewed.json` zu ueberfuehren

Der Slice ist bewusst von der separaten Warmwasser-Stromkosten-Ableitung getrennt.

## Parent-Bezug

Massgebliche Parent-Spec:

- `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`

## In Scope

Dieser Slice umfasst ausschliesslich die folgenden noch offenen Review-Quellen:

- `Belege/Belege_BE1.pdf`
- `Belege/Belege_BE2.pdf`
- `Belege/Belege_BE2_II.pdf`
- `Belege/Belege_Liegenschaft.pdf`
- `Belege/Oel_25.pdf`

Und nur die daraus abgeleiteten Aufgaben:

1. Uebernahme der objektweiten Standardkosten 2025 in `kostenbelege[]`
2. Uebernahme der BE1-/BE2-Brennstoffkosten 2025 in `kostenbelege[]`
3. Uebernahme der BE1-/BE2-Heiznebenkosten 2025 in `kostenbelege[]`
4. explizite dokumentierte Nicht-Uebernahme nicht-kanonischer Einzelpositionen innerhalb der Sammelbelege
5. Entfernung genau dieser fuenf Review-Punkte aus `review-output.json`

## Out of Scope

Explizit nicht Teil dieses Slices:

- Warmwasser-Stromkosten BE1 (`verbrauchskosten_warmwasser`)
- weitere Messwerte-Aenderungen
- neue Parser-/OCR-Logik
- Nachbearbeitung bereits geschlossener Versicherungs- oder Tibber-Slices

## Operatives Zielartefakt

Ziel dieses Slices ist ein aktualisiertes `input.reviewed.json`, das folgende `kostenbelege[]` zusaetzlich enthaelt:

- `kb-grundsteuer`
- `kb-muell`
- `kb-oberflaechenwasser`
- `kb-kaltabwasser`
- `kb-brennstoff-be1`
- `kb-brennstoff-be2`
- `kb-heiznebenkosten-be1`
- `kb-heiznebenkosten-be2`

Zusaetzlich wird `review-output.json` so bereinigt, dass fuer die fuenf oben genannten Quellen keine offenen Items mehr bestehen.

## Normative Festlegungen

### 1. Aggregationsstil

Die finalen `kostenbelege[]` folgen fuer 2025 bewusst dem vereinfachten Aggregationsstil des validierten 2024er Inputs:

- pro Kostenart und Scope genau ein kanonischer Jahresbeleg
- keine 1:1-Abbildung jeder Einzelrechnung in `input.reviewed.json`
- dokumentierte Aggregation mehrerer Einzelquellen in einen operativen Jahreswert

### 2. Standardkosten Objekt

Aus `Belege_Liegenschaft.pdf` sind normativ zu uebernehmen:

- `kb-grundsteuer`
  - `kostenart_id = grundsteuer`
  - `betrag = 924.80`
  - `datum = 2025-02-01`

- `kb-muell`
  - `kostenart_id = muellabfuhr`
  - `betrag = 401.28`
  - `datum = 2025-02-01`

- `kb-oberflaechenwasser`
  - `kostenart_id = oberflaechenwasser`
  - `betrag = 790.02`
  - `datum = 2025-02-01`

- `kb-kaltabwasser`
  - `kostenart_id = kalt_abwasser`
  - `betrag = 2650.38`
  - `datum = 2025-03-01`

Herleitung fuer `kb-kaltabwasser`:

- Wasser brutto `1793.32 EUR`
- Schmutzwasser `1613.15 EUR`
- Abrechnung Wasser/Schmutzwasser `-756.09 EUR`
- Summe operativer Jahreswert `2650.38 EUR`

### 3. Brennstoffkosten BE1

Aus `Oel_25.pdf` ist normativ zu uebernehmen:

- `kb-brennstoff-be1`
  - `kostenart_id = brennstoffkosten`
  - `betrag = 3000.00`
  - `datum = 2025-03-01`
  - `scope.berechnungseinheit = be1`

Herleitung:

- Omnert/Adam-Ommert Lieferung 1: `1500.00 EUR`
- Omnert/Adam-Ommert Lieferung 2: `1500.00 EUR`
- Aggregierter Jahreswert BE1: `3000.00 EUR`

### 4. Brennstoffkosten BE2

Aus `Belege_BE2.pdf` sind normativ zu uebernehmen:

- `kb-brennstoff-be2`
  - `kostenart_id = brennstoffkosten`
  - `betrag = 3337.30`
  - `datum = 2025-03-01`
  - `scope.berechnungseinheit = be2`

Herleitung:

- HessenForst Holz: `2196.68 EUR`
- Hessen-Pellets: `1140.62 EUR`
- Aggregierter Jahreswert BE2: `3337.30 EUR`

### 5. Heiznebenkosten BE1

Aus `Belege_BE1.pdf` sind normativ zu uebernehmen:

- `kb-heiznebenkosten-be1`
  - `kostenart_id = heiznebenkosten`
  - `betrag = 118.26`
  - `datum = 2025-03-01`
  - `scope.berechnungseinheit = be1`

Herleitung:

- Jens Orth `J-25-02027`: `81.93 EUR`
- Jens Orth `K-25-01855`: `36.33 EUR`
- Aggregierter Jahreswert BE1: `118.26 EUR`

### 6. Heiznebenkosten BE2

Aus `Belege_BE2.pdf` und `Belege_BE2_II.pdf` sind normativ zu uebernehmen:

- `kb-heiznebenkosten-be2`
  - `kostenart_id = heiznebenkosten`
  - `betrag = 546.25`
  - `datum = 2025-03-01`
  - `scope.berechnungseinheit = be2`

Herleitung:

- KWB Wartung: `474.05 EUR`
- Jens Orth `K-25-02799`: `36.33 EUR`
- Jens Orth `K-25-00823`: `35.87 EUR`
- Aggregierter Jahreswert BE2: `546.25 EUR`

### 7. Explizit nicht zu uebernehmen

Die folgenden Positionen gelten fuer diesen Slice normativ als nicht-kanonisch fuer den operativen Jahresinput und werden nicht in `kostenbelege[]` uebernommen:

- `Belege_Liegenschaft.pdf`: die beiden ista-Rechnungen (`291.48 EUR`, `395.52 EUR`)
  - Begruendung: sie wurden bereits 2024 nicht in den vereinfachten finalen Input uebernommen und sind fuer 2025 nicht neu als kanonischer Jahresbeleg zu modellieren

- `Belege_BE2_II.pdf`: `AP Werkzeuge 22.98 EUR`
- `Belege_BE2_II.pdf`: `die flora 38.99 EUR`
  - Begruendung: Werkzeuge/Material fuer Kettensaege sind in diesem Datenmodell keine kanonisch belegte Heiznebenkosten-Position

## Akzeptanzkriterien

Dieser Slice ist fachlich fertig, wenn alle folgenden Punkte erfuellt sind:

1. Die acht normativen `kostenbelege[]` sind in `input.reviewed.json` enthalten.
2. Alle acht Werte, Kostenarten und Scopes entsprechen den oben festgelegten Jahresaggregaten.
3. `review-output.json` enthaelt keine offenen Items mehr fuer die fuenf Restkosten-Quellen.
4. `review-output.json` ist nach diesem Slice leer.
5. `finalize-year-input` kann auf Basis von `input.reviewed.json` und leerem `review-output.restkosten-validation.json` erfolgreich laufen.
6. Ein technischer Abrechnungslauf auf dem daraus erzeugten `input.restkosten.json` ist moeglich.

## Test Cases

### TC1 Reviewed Input enthaelt alle normativen Restkostenbelege

Ziel:

- sicherstellen, dass die acht Restkostenbelege mit den normativen Jahreswerten vorliegen

Expected Result:

- `kb-grundsteuer = 924.80`
- `kb-muell = 401.28`
- `kb-oberflaechenwasser = 790.02`
- `kb-kaltabwasser = 2650.38`
- `kb-brennstoff-be1 = 3000.00`
- `kb-brennstoff-be2 = 3337.30`
- `kb-heiznebenkosten-be1 = 118.26`
- `kb-heiznebenkosten-be2 = 546.25`

### TC2 Review-Backlog ist nach dem Slice leer

Ziel:

- sicherstellen, dass die letzten fuenf offenen Review-Dokumente geschlossen sind

Expected Result:

- `review-output.json.items == []`

### TC3 Finalisierung auf dem Restkosten-Zwischenstand funktioniert

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.restkosten-validation.json" \
  --output-json "$NK_2025_WORK/input.restkosten.json"
```

Expected Result:

- technischer Erfolg ohne offene Review-Items
- `input.restkosten.json` wird geschrieben

### TC4 Technischer Abrechnungslauf mit Restkosten-Zwischenstand funktioniert

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.restkosten.json" \
  --output-dir "$NK_2025_WORK/statements-restkosten" \
  --skip-pdf
```

Expected Result:

- der Lauf endet technisch erfolgreich
- Statements fuer die aktiven Mietparteien werden erzeugt

## Verification Commands

Vorbereitung:

```bash
export NK_REPO="/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung"
export NK_2025_WORK="$NK_REPO/data/2025/work"
cd "$NK_REPO"
```

TC1 / TC2:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
reviewed = json.loads((base / 'input.reviewed.json').read_text())
review = json.loads((base / 'review-output.json').read_text())
ids = {item['id']: item for item in reviewed['kostenbelege']}
for key in [
    'kb-grundsteuer','kb-muell','kb-oberflaechenwasser','kb-kaltabwasser',
    'kb-brennstoff-be1','kb-brennstoff-be2','kb-heiznebenkosten-be1','kb-heiznebenkosten-be2'
]:
    print(key, ids[key]['betrag'])
print('review_items', review['items'])
PY
```

TC3 Vorbereitung:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
review = json.loads((base / 'review-output.json').read_text())
review['items'] = []
(base / 'review-output.restkosten-validation.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
PY
```

TC3 und TC4 siehe oben.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-09 | 0 | Claude | Child-Spec fuer die verbleibenden Restkostenbelege 2025 angelegt |
| 2026-04-10 | 1 | Codex | Closeout abgeschlossen; Verification Commands erneut gruen ausgefuehrt und OpenSpec-Change archiviert |
