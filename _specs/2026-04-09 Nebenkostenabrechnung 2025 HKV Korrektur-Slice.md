# Nebenkostenabrechnung 2025 - HKV Korrektur-Slice

## Zweck

Diese Child-Spec definiert genau einen bounded Fix-Slice fuer die 2025er Heizkostenverteiler-Modellierung.

Der Slice korrigiert den aktuell bekannten Fehlstand in den bereits erzeugten 2025er Artefakten:

- HKV-Werte wurden pro Nutzeinheit aggregiert
- physische HKV-Geraete mit unterschiedlichen Faktoren wurden dadurch unzulaessig zusammengezogen
- `umrechnungsfaktor` ist im aktuellen 2025er Stand fuer HKV nicht belastbar hinterlegt

Diese Child-Spec dient ausdruecklich dazu, die HKV-Datenmodellierung sauber zu ziehen, ohne dabei Stromtarif-, Beleg- oder Warmwasser-Slices still mitzuveraendern.

## Parent-Bezug

Massgebliche Referenzen:

- `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `2026-04-09 Nebenkostenabrechnung 2025 Messwerte Review-Slice.md`
- `2026-04-09 Nebenkostenabrechnung 2025 Stromtarif Korrektur-Slice.md`
- `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`

## Problemstellung

Der aktuelle 2025er Stand enthaelt verdichtete HKV-Zeilen wie `z-hkv-ne1`, `z-hkv-ne2`, `z-hkv-ne3` und `z-hkv-ne4`, deren Ablesewerte bereits auf Nutzeinheitsebene aufsummiert wurden oder als unvollstaendige Platzhalter vorliegen.

Das ist fachlich nicht belastbar, sobald mehrere physische HKV-Geraete mit unterschiedlichen Faktoren beteiligt sind, weil allgemein gilt:

`(a * f1) + (b * f2) != (a + b) * ein_gesamtfaktor`

Die bestehende Rechenlogik kann Faktoren pro Geraet bereits verarbeiten. Das Problem liegt daher nicht im Rechenkern, sondern in der 2025er Eingabemodellierung.

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die Aufloesung aggregierter HKV-Zeilen in physische Einzelgeraete
2. die Uebernahme belastbarer `umrechnungsfaktor`-Werte je physischem HKV
3. die Uebernahme der zugehoerigen Alt-/Neuablesungen je physischem HKV
4. die Erzeugung neuer korrigierter Zwischenartefakte fuer diesen Slice
5. die technische Verifikation, dass der Rechenkern die gewichteten HKV-Einzelwerte traegt

## Out of Scope

Explizit nicht Teil dieses Slices:

- Korrektur der Stromtarifkette selbst
- Aenderung der Strommesswerte
- Restkostenbelege
- Neuberechnung oder Freigabe des finalen Warmwasser-Endwerts
- generische OCR- oder Parser-Neuentwicklung
- inhaltliche Aenderung von Kostenverteilungsschluesseln ausser der korrekten HKV-Gewichtung

## Abhaengigkeit und Reihenfolge

Normative Reihenfolge:

- dieser Slice wird fachlich nach dem Stromtarif-Korrektur-Slice eingeordnet
- die HKV-Korrektur soll auf dem dann aktuellsten reviewed Zwischenstand aufsetzen

Implementierungs-Baseline, sobald der Slice ausgefuehrt wird:

- primaere Baseline: `data/2025/work/build/input.reviewed.tibber-fixed.json`
- falls diese Datei zum Implementierungszeitpunkt noch nicht existiert, bleibt diese Child-Spec dennoch gueltig, aber nicht implementation-ready

## Baseline-Artefakte mit bekanntem Fehlstand

Diese Artefakte bleiben als historische Zwischenstaende erhalten, gelten fuer HKV jedoch als fachlich ueberholt:

- `data/2025/work/build/input.reviewed.json`
- `data/2025/work/input.messwerte.json`
- `data/2025/work/input.versicherung.json`
- `data/2025/work/input.tibber.json`
- `data/2025/work/input.restkosten.json`
- `data/2025/input.json`

Normative Einordnung:

- diese Dateien belegen den bisherigen Bearbeitungsstand
- sie sind fuer HKV jedoch kein kanonischer Sollstand
- insbesondere duerfen die dort enthaltenen aggregierten HKV-Eintraege nicht in Folgeartefakte uebernommen werden

## Zielartefakte dieses Slices

Dieser Slice erzeugt oder aktualisiert genau die folgenden Artefakte:

- `data/2025/work/build/input.reviewed.hkv-fixed.json`
- `data/2025/work/build/review-output.hkv-fixed.validation.json`
- `data/2025/work/input.hkv-fixed.json`

Optional zusaetzlich ein reines Vergleichsartefakt:

- `data/2025/work/build/hkv-weighted-summary.hkv-fixed.json`

## Normative Festlegungen

### 1. Physisches HKV-Geraet statt NE-Sammelwert

Fuer jede Nutzeinheit mit belastbar identifizierbaren 2025er HKV-Einzelgeraeten gilt:

- pro physischem HKV genau ein `zaehler[]`-Eintrag
- pro physischem HKV genau ein `ablesungen[]`-Eintrag fuer die relevante Periode
- es darf kein zusammengezogener NE-Sammel-HKV als operative Verbrauchsquelle stehen bleiben

### 2. Faktoren sind Pflichtdaten je Geraet

Fuer jeden operativen HKV-Eintrag gilt:

- `umrechnungsfaktor` ist verpflichtend
- `null` ist fuer operative HKV-Geraete unzulaessig
- der Faktor muss auf eine belastbare 2025er Quelle zurueckgehen

### 3. Affected Scope der 2025er HKV-Korrektur

Fuer diesen Slice gelten als betroffen, sofern die 2025er Quellen dies belastbar tragen:

- `NE1`
- `NE2`
- `NE3`
- `NE4`

Normative Begrenzung:

- diese vier Nutzeinheiten sind im aktuellen Fehlstand bereits als aggregierte oder unvollstaendige HKV-Strukturen modelliert
- `NE3` ist ab Iteration 1 dieses Slices ausdruecklich pflichtig einzubeziehen, weil die 2025er AQ-Quelle eine belastbare Einzelgeraet-Spur mit Faktoren und Jahreswerten traegt

### 4. Bestehende Platzhalter-HKV sind nicht kanonisch

Die folgenden Verdichtungsartefakte gelten fuer Folgeartefakte dieses Slices als nicht kanonisch:

- `z-hkv-ne1`
- `z-hkv-ne2`
- `z-hkv-ne3`
- `z-hkv-ne4`
- `z-hkv-be1-total`

Normative Regel:

- diese IDs duerfen in `input.reviewed.hkv-fixed.json` nicht mehr als operative HKV-Verbrauchsquelle verwendet werden
- falls sie aus technischen Gruenden voruebergehend im Artefakt verbleiben, duerfen sie keine HKV-Ablesungen mehr tragen

### 5. Periodenlogik bleibt erhalten, sofern die Quelle nichts anderes sagt

Die HKV-Korrektur aendert nicht stillschweigend die bereits fachlich gesetzten Perioden.

Normative Regel:

- fuer `NE1` bleibt die relevante HKV-Periode grundsaetzlich die Teilperiode `2025-03-31` bis `2025-12-31`, sofern die Quelle keine abweichende belastbare Periode zeigt
- fuer `NE2`, `NE3` und `NE4` bleibt grundsaetzlich die Jahresperiode `2025-01-01` bis `2025-12-31`
- periodische Abweichungen sind nur mit belastbarer Quellspur zulaessig

### 6. Gewichtung erfolgt im bestehenden Rechenkern

Dieser Slice fuehrt keine neue HKV-Rechenlogik ein.

Normative Regel:

- die Gewichtung erfolgt weiterhin je Geraet als `Differenz * UmrechnungsFaktor`
- die Summation je Nutzeinheit erfolgt weiterhin im bestehenden Rechenkern
- dieser Slice liefert nur die dafuer noetige korrekte Eingabestruktur

## Akzeptanzkriterien

Dieser Slice ist fachlich fertig, wenn alle folgenden Punkte erfuellt sind:

1. `input.reviewed.hkv-fixed.json` enthaelt fuer die betroffenen Nutzeinheiten physische HKV-Einzelgeraete statt NE-Sammel-HKV.
2. Kein operativer HKV-Eintrag in `input.reviewed.hkv-fixed.json` hat `umrechnungsfaktor = null`.
3. Die verdichteten HKV-Artefakte `z-hkv-ne1`, `z-hkv-ne2`, `z-hkv-ne3`, `z-hkv-ne4` und `z-hkv-be1-total` sind im korrigierten Slice nicht mehr operative Verbrauchsquellen.
4. Die HKV-Ablesungen liegen je physischem Geraet in kanonischer Struktur vor und respektieren die fachlich gesetzten Perioden.
5. Ein technischer Validierungslauf mit `finalize-year-input` auf dem HKV-korrigierten reviewed Input endet erfolgreich.
6. Ein technischer CLI-Lauf auf `input.hkv-fixed.json` endet erfolgreich.
7. Dieser Slice aendert weder Stromtarifkette noch finale Warmwasser-Freigabe.

## Test Cases

### TC1 HKV-Einzelgeraete statt NE-Sammelwerte

Ziel:

- sicherstellen, dass die betroffenen Nutzeinheiten keine aggregierten HKV-Verbrauchsquellen mehr verwenden

Expected Result:

- fuer `NE1`, `NE2`, `NE3` und `NE4` existieren operative HKV-Geraete auf Einzelgeraet-Ebene
- `z-hkv-ne1`, `z-hkv-ne2`, `z-hkv-ne3`, `z-hkv-ne4` tragen keine operativen HKV-Ablesungen mehr
- `z-hkv-be1-total` wird nicht mehr als operative HKV-Verbrauchsquelle verwendet

### TC2 Jeder operative HKV hat einen Faktor

Ziel:

- sicherstellen, dass die Gewichtung je Geraet in den Eingabedaten ueberhaupt moeglich ist

Expected Result:

- jeder operative HKV-Zaehler in `input.reviewed.hkv-fixed.json` besitzt einen numerischen `umrechnungsfaktor`
- kein operativer HKV-Zaehler hat `umrechnungsfaktor = null`

### TC3 Perioden und Zuordnung bleiben fachlich konsistent

Ziel:

- sicherstellen, dass die Umstellung auf Einzelgeraete keine stillen Perioden- oder Zuordnungsfehler einfuehrt

Expected Result:

- alle operativen HKV-Ablesungen sind genau einer Nutzeinheit und Berechnungseinheit zugeordnet
- `NE1` bleibt ohne belastbare Gegenquelle in der Teilperiode `2025-03-31` bis `2025-12-31`
- `NE2`, `NE3` und `NE4` bleiben ohne belastbare Gegenquelle in der Jahresperiode `2025-01-01` bis `2025-12-31`

### TC4 Gewichtete HKV-Summen sind technisch reproduzierbar

Ziel:

- sicherstellen, dass sich aus dem korrigierten reviewed Input je Nutzeinheit gewichtete HKV-Summen ableiten lassen

Expected Result:

- fuer jede betroffene Nutzeinheit laesst sich eine gewichtete Summe als `sum((messwert_neu - messwert_alt) * umrechnungsfaktor)` bilden
- keine betroffene Nutzeinheit ist fuer die HKV-Gewichtung auf einen NE-Sammel-HKV angewiesen

### TC5 Finalisierung des HKV-Fix-Zwischenstands erfolgreich

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.hkv-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.hkv-fixed.validation.json" \
  --output-json "$NK_2025_WORK/input.hkv-fixed.json"
```

Expected Result:

- `input.hkv-fixed.json` wird erfolgreich geschrieben
- kein Fehler wegen unbekannter Zaehler, fehlender Faktoren oder ungueltiger HKV-Referenzen

### TC6 Technischer CLI-Lauf auf dem HKV-Fix-Zwischenstand erfolgreich

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.hkv-fixed.json" \
  --output-dir "$NK_2025_WORK/statements-hkv-fixed" \
  --skip-pdf
```

Expected Result:

- der Lauf endet technisch erfolgreich
- Einzelabrechnungsartefakte werden geschrieben

## Verification Commands

Vorbereitung:

```bash
export NK_REPO="/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung"
export NK_2025_WORK="$NK_REPO/data/2025/work"
cd "$NK_REPO"
```

TC1 bis TC4 JSON-Sichtpruefung:

```bash
python3 - <<'PY'
import json
from pathlib import Path

base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
reviewed = json.loads((base / 'input.reviewed.hkv-fixed.json').read_text())

zaehler = reviewed['zaehler']
ablesungen = reviewed['ablesungen']

operative_hkv = []
for z in zaehler:
    if z['typ'] != 'heizkostenverteiler':
        continue
    has_reading = any(a['zaehler_id'] == z['id'] for a in ablesungen)
    if has_reading:
        operative_hkv.append(z)

print('operative_hkv_count', len(operative_hkv))
print('operative_hkv_ids', [z['id'] for z in operative_hkv])

placeholder_ids = {'z-hkv-ne1', 'z-hkv-ne2', 'z-hkv-ne3', 'z-hkv-ne4', 'z-hkv-be1-total'}
placeholder_with_readings = [
    z['id'] for z in operative_hkv if z['id'] in placeholder_ids
]
print('placeholder_with_readings', placeholder_with_readings)

null_factors = [z['id'] for z in operative_hkv if z.get('umrechnungsfaktor') is None]
print('null_factors', null_factors)

weighted = {}
for a in ablesungen:
    zid = a['zaehler_id']
    z = next((item for item in zaehler if item['id'] == zid), None)
    if not z or z['typ'] != 'heizkostenverteiler':
        continue
    factor = z['umrechnungsfaktor']
    diff = (a['messwert_neu'] - a['messwert_alt']) * factor
    ne = a.get('ne_id') or z.get('zugeordnete_ne')
    weighted.setdefault(ne, 0)
    weighted[ne] += diff
print('weighted', weighted)
PY
```

TC5 Vorbereitung:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
(base / 'review-output.hkv-fixed.validation.json').write_text(
    json.dumps({'target_year': 2025, 'items': []}, ensure_ascii=False, indent=2) + '\n',
    encoding='utf-8'
)
PY
```

TC5 und TC6 siehe oben.

## Ready-Check fuer Implementierung

Diese Child-Spec ist implementierungsreif, wenn vor dem Coding zusaetzlich klar ist:

- welcher tibber-korrigierte reviewed Zwischenstand die Baseline bildet
- welche physischen HKV-Geraete je betroffener Nutzeinheit aus den 2025er Quellen belastbar identifizierbar sind
- welche Faktoren und Alt-/Neuablesungen je Geraet aus den 2025er Quellen gelten

Solange diese drei Punkte noch nicht festgezogen sind, ist die Child-Spec bewusst nur plan-ready, nicht implementation-ready.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-10 | 0 | Codex | Child-Spec fuer den HKV-Korrektur-Slice mit Artefaktkette, Akzeptanzkriterien, Testcases und Verification Commands angelegt |
| 2026-04-10 | 1 | Codex | Slice nach Nutzerreview auf `NE3` erweitert; Akzeptanzkriterien, Placeholder-Liste und Periodenlogik entsprechend nachgezogen |
