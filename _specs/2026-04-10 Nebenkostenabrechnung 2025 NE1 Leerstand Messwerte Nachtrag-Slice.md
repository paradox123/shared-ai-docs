# Nebenkostenabrechnung 2025 - NE1 Leerstand Messwerte Nachtrag-Slice

## Zweck

Diese Child-Spec definiert genau einen bounded Nachtrags-Slice fuer den 2025er Operativpfad:

- die fehlenden Messwerte fuer den Leerstand der Nutzeinheit `NE1` im Zeitraum `2025-01-01` bis `2025-03-31` belastbar in die 2025er Artefakte nachzuziehen

Der Slice ist notwendig, weil der aktuelle 2025er Endstand fuer `NE1` bislang nur die Mieter-Teilperiode ab `2025-03-31` bzw. `2025-04-01` traegt. Fuer verbrauchsabhaengige Verteilungen ist diese Modellierung unvollstaendig.

## Parent-Bezug

Massgebliche Referenzen:

- `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `2026-04-10 Nebenkostenabrechnung 2025 Periodische Verbrauchsverteilung Nachtrag-Slice.md`
- `2026-04-09 Nebenkostenabrechnung 2025 Messwerte Review-Slice.md`
- `2026-04-09 Nebenkostenabrechnung 2025 HKV Korrektur-Slice.md`
- `2026-04-09 Nebenkostenabrechnung 2025 Warmwasserkosten Ableitung-Slice.md`
- `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`

## Abhaengigkeit und Reihenfolge

Dieser Slice ist ein Daten-Nachtrag und haengt normativ vom separaten Rechenkern-Slice

- `2026-04-10 Nebenkostenabrechnung 2025 Periodische Verbrauchsverteilung Nachtrag-Slice.md`

ab.

Begruendung:

- der aktuelle Rechenkern summiert verbrauchsabhaengige Segmente je Nutzeinheit derzeit noch periodisch unbewusst auf
- ohne den vorgeschalteten Rechenkern-Slice wuerde ein nachgezogener `NE1`-Leerstandsverbrauch weiterhin implizit der spaeteren Mietpartei zugeschlagen

Normative Reihenfolge:

1. zuerst periodische Verbrauchsverteilung im Rechenkern korrigieren
2. danach `NE1`-Leerstands-Messwerte in die 2025er Artefakte nachziehen

## Baseline und Zielartefakte

Primaere Baseline fuer diesen Slice:

- `data/2025/work/build/input.reviewed.warmwasser-revalidated.json`
- `data/2025/work/build/review-output.warmwasser-revalidated.validation.json`
- `data/2025/work/input.warmwasser-revalidated.json`
- `data/2025/input.json`

Neue Zielartefakte dieses Slices:

- `data/2025/work/build/input.reviewed.ne1-vacancy-fixed.json`
- `data/2025/work/build/review-output.ne1-vacancy-fixed.validation.json`
- `data/2025/work/input.ne1-vacancy-fixed.json`

Anschliessend erneut als finaler 2025er Endstand:

- `data/2025/input.json`

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die Nachziehung der fehlenden `NE1`-Leerstands-Messwerte fuer `2025-01-01` bis `2025-03-31`
2. die kanonische Modellierung dieser Leerstandssegmente in `ablesungen[]`
3. die Revalidierung der davon direkt betroffenen Verteilungen im technischen Abrechnungslauf
4. die erneute Finalisierung des 2025er `input.json` auf Basis des nachgezogenen `NE1`-Leerstandsstands

## Out of Scope

Explizit nicht Teil dieses Slices:

- neue Stromtarif-Aenderungen
- weitere HKV- oder Warmwasser-Formelkorrekturen ausser soweit sie durch die nachgezogenen `NE1`-Leerstands-Messwerte im Ergebnis sichtbar werden
- Aenderungen an anderen Nutzeinheiten als `NE1`
- Aenderungen an Kostenbelegen ausser der daraus resultierenden Re-Finalisierung des Inputs
- OCR-/Parser-Neuentwicklung als generische Plattformfunktion
- Personenanzahl-Aenderungen der Mietparteien

Normative Einordnung fuer den letzten Punkt:

- die vom Nutzer bereits angepasste Personenanzahl der Mietparteien gilt fuer diesen Slice als Baseline und ist nicht Teil der hier zu implementierenden Aenderung

## Problemstellung

Der aktuelle 2025er Stand enthaelt fuer `NE1` nur die folgenden operativen Verbrauchssegmente:

- `z-kw-ne1`: `2025-03-31 -> 2025-12-31`
- `z-ww-ne1`: `2025-03-31 -> 2025-12-31`
- `z-hkv-ne1-*`: jeweils `2025-03-31 -> 2025-12-31`
- `z-strom-ne1`: direkte Wohnungsstromablesungen fuer die Mieterperiode

Fuer die fachlich korrekte Verteilung fehlt damit der Leerstandsabschnitt von `2025-01-01` bis `2025-03-31`.

## Normative Festlegungen

### 1. Betroffene Messwertarten in `NE1`

Dieser Nachtrags-Slice betrifft in `NE1` genau die Messwertarten, die fuer verbrauchsabhaengige Verteilungen relevant sind und aktuell erst ab `2025-03-31` modelliert sind:

- `z-kw-ne1`
- `z-ww-ne1`
- `z-hkv-ne1-*` fuer alle physischen HKV-Geraete der `NE1`

Direkter Wohnungsstrom `z-strom-ne1` ist fuer diesen Slice kein Nachtragsziel, weil die operativen Stichtagsablesungen fuer den Mieterzeitraum bereits vorliegen und die jahresbezogene Warmwasser-Herleitung in der Warmwasser-Spec separat geregelt ist.

### 2. Quelle fuer den Leerstands-Nachtrag

Fuer `NE1` ist das Dokument

- `Messwerte/Monatswerte - 2025 -  - NE0001(P621593463).pdf`

normativ die Primaerquelle fuer den Leerstands-Nachtrag.

Zusaetzliche Plausibilisierungsquellen duerfen verwendet werden, wenn sie dem bestehenden Datenmodell nicht widersprechen, insbesondere:

- `data/2024/input_tariff_from_excel.json`
- `tests/Nebenkosten.Tests/Fixtures/2024/input_tariff.json`

### 3. Zielmodell fuer den Leerstands-Nachtrag

Die fehlenden `NE1`-Leerstands-Messwerte muessen als eigener operativer Abschnitt modelliert werden.

Normative Regel:

- fuer jede betroffene Messwertart in `NE1` existiert nach diesem Slice ein belastbarer Abschnitt fuer den Leerstand bis `2025-03-31`
- der bestehende Abschnitt fuer die Mieterperiode ab `2025-03-31` bzw. `2025-04-01` bleibt erhalten
- der Rechenkern darf dadurch den Leerstandsverbrauch von der Mietperiode trennen, statt implizit nur die Mieter-Teilperiode als Gesamtverbrauch zu sehen

### 4. Zeitlogik fuer den Nachtrag

Normative Zielperiode fuer den Nachtrag:

- `2025-01-01` bis `2025-03-31`

Zulaessige technische Modellierung:

- entweder als eigener Periodeneintrag `2025-01-01 -> 2025-03-31`
- oder als quellenbedingt aequivalente Modellierung mit direkt anschliessenden Stichtagen / Teilperioden, sofern der fachliche Leerstandsverbrauch fuer `NE1` dadurch eindeutig und reproduzierbar wird

Nicht zulaessig:

- der Leerstandsverbrauch bleibt implizit unmodelliert
- die Leerstandsmenge wird nur ausserhalb von `ablesungen[]` verbal dokumentiert

### 5. HKV fuer den Leerstand bleiben geraetebezogen

Fuer die `NE1`-HKV gilt weiterhin die Geraetemodellierung aus dem HKV-Korrektur-Slice.

Normative Regel:

- der Leerstands-Nachtrag darf keine Rueckkehr zu aggregierten `z-hkv-ne1`-Summen erzeugen
- falls HKV-Leerstandswerte nachgezogen werden, geschieht dies weiterhin pro physischem HKV-Geraet mit bestehendem `umrechnungsfaktor`

### 6. Erwartete Folge fuer die Verteilung

Nach diesem Slice muss der technische Abrechnungslauf den `NE1`-Leerstand als eigenen Verbrauchsabschnitt tragen koennen.

Normative Erwartung:

- diese Erwartung ist erst nach Abschluss des vorgeschalteten Rechenkern-Slices zur periodischen Verbrauchsverteilung erreichbar
- der `NE1`-Leerstandsverbrauch darf nicht implizit `mp-ne1-hainz` zugeschlagen werden
- die kostenrelevanten Verteilungen fuer `NE1` muessen auf einer vollstaendigen Jahresspur statt auf einer reinen Mieter-Teilperiode beruhen

## Akzeptanzkriterien

Dieser Slice ist fachlich fertig, wenn alle folgenden Punkte erfuellt sind:

1. `input.reviewed.ne1-vacancy-fixed.json` enthaelt fuer `NE1` zusaetzliche belastbare Leerstands-Messwertsegmente bis `2025-03-31` fuer alle betroffenen Messwertarten.
2. Bestehende `NE1`-Mieterperioden-Messwerte bleiben erhalten und werden nicht stillschweigend ueberschrieben.
3. Die `NE1`-HKV bleiben geraetebezogen; es entstehen keine neuen aggregierten HKV-Sammelwerte.
4. `finalize-year-input` schreibt `data/2025/work/input.ne1-vacancy-fixed.json` erfolgreich.
5. Ein CLI-Lauf gegen `data/2025/work/input.ne1-vacancy-fixed.json` endet erfolgreich.
6. Aus dem nachgezogenen reviewed Stand wird das finale `data/2025/input.json` erneut erfolgreich geschrieben.
7. Die geaenderte Personenanzahl der Mietparteien bleibt im Slice unveraendert erhalten.

## Test Cases

### TC1 Reviewed Input enthaelt `NE1`-Leerstandssegmente

Expected Result:

- in `input.reviewed.ne1-vacancy-fixed.json` existieren fuer `NE1` zusaetzliche Segmente bis `2025-03-31`
- betroffen sind mindestens `z-kw-ne1`, `z-ww-ne1` und die `z-hkv-ne1-*`-Geraete, soweit die Quelle dies belastbar traegt

### TC2 `NE1`-HKV bleiben geraetebezogen

Expected Result:

- keine neuen operativen Ablesungen auf aggregierten Platzhalter-IDs wie `z-hkv-ne1`
- operative `NE1`-HKV-Leerstandssegmente referenzieren weiterhin physische `z-hkv-ne1-*`

### TC3 Finalisierung des `ne1-vacancy-fixed`-Zwischenstands erfolgreich

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.ne1-vacancy-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.ne1-vacancy-fixed.validation.json" \
  --output-json "$NK_2025_WORK/input.ne1-vacancy-fixed.json"
```

Expected Result:

- `input.ne1-vacancy-fixed.json` wird erfolgreich geschrieben
- kein Fehler wegen ungueltiger `NE1`-Referenzen oder periodischer Leerstandssegmente

### TC4 Technischer CLI-Lauf auf dem `ne1-vacancy-fixed`-Zwischenstand erfolgreich

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.ne1-vacancy-fixed.json" \
  --output-dir "$NK_2025_WORK/statements-ne1-vacancy-fixed" \
  --skip-pdf
```

Expected Result:

- der Lauf endet technisch erfolgreich
- Statement-Artefakte werden geschrieben

### TC5 Finales 2025er `input.json` wird aus dem nachgezogenen Stand re-finalisiert

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.ne1-vacancy-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.ne1-vacancy-fixed.validation.json" \
  --output-json "$NK_REPO/data/2025/input.json"
```

Expected Result:

- `data/2025/input.json` wird erfolgreich neu geschrieben
- der finale 2025er Input basiert danach auf dem nachgezogenen `NE1`-Leerstandsstand

## Verification Commands

Vorbereitung:

```bash
export NK_REPO="/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung"
export NK_2025_WORK="$NK_REPO/data/2025/work"
cd "$NK_REPO"
```

TC1 und TC2 JSON-Sichtpruefung:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
reviewed = json.loads((base / 'input.reviewed.ne1-vacancy-fixed.json').read_text())

ne1 = [a for a in reviewed['ablesungen'] if a.get('ne_id') == 'NE1']
print('ne1_readings_count', len(ne1))
print('ne1_readings', ne1)
print('aggregated_hkv_ne1', [a for a in ne1 if a['zaehler_id'] == 'z-hkv-ne1'])
PY
```

TC3 bis TC5 siehe oben.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-10 | 0 | Codex | Child-Spec fuer fehlende `NE1`-Leerstands-Messwerte im 2025er Operativpfad angelegt; Personenanzahl-Aenderung des Nutzers explizit als Baseline, nicht als Slice-Inhalt markiert |
| 2026-04-10 | 1 | Codex | Abhaengigkeit vom neuen Rechenkern-Slice fuer periodische Verbrauchsverteilung explizit gemacht; Reihenfolge und Umsetzbarkeit gegen Code-Realitaet geschaerft |
