# Nebenkostenabrechnung 2025 - Warmwasserkosten Revalidierung-Slice

## Zweck

Diese Child-Spec definiert genau einen bounded Delivery-Slice aus der Parent-Spec `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`:

- die Revalidierung und operative Neufestlegung des 2025er BE1-Warmwasser-Stromkostenbelegs `kb-warmwasser-be1`

Der Slice ist bewusst von den Sammelbelegen getrennt, weil die Kostenposition nicht aus einem einzelnen PDF-Beleg stammt, sondern aus Messwerten plus Tarifen abgeleitet wird.

Wichtige Einordnung nach den bereits umgesetzten Korrektur-Slices:

- die Stromtarif-Korrektur fuer 2025 ist umgesetzt
- die HKV-Korrektur fuer 2025 ist umgesetzt
- der bislang in den 2025er Artefakten gefuehrte Warmwasser-Beleg `718.04 EUR` ist damit nur noch als historischer Zwischenstand zu lesen
- dieser Slice zieht den Warmwasser-Beleg jetzt auf den stromtarif- und hkv-korrigierten Zwischenstand nach

## Parent-Bezug

Massgebliche Referenzen:

- `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `2026-04-09 Nebenkostenabrechnung 2025 Stromtarif Korrektur-Slice.md`
- `2026-04-09 Nebenkostenabrechnung 2025 HKV Korrektur-Slice.md`
- `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`

## Baseline und Zielartefakte

Primaere Baseline fuer diesen Slice:

- `data/2025/work/build/input.reviewed.hkv-fixed.json`
- `data/2025/work/build/review-output.hkv-fixed.validation.json`
- `data/2025/work/input.hkv-fixed.json`

Neue Zielartefakte dieses Slices:

- `data/2025/work/build/input.reviewed.warmwasser-revalidated.json`
- `data/2025/work/build/review-output.warmwasser-revalidated.validation.json`
- `data/2025/work/input.warmwasser-revalidated.json`

Optional anschliessend als finaler 2025er Endstand:

- `data/2025/input.json`

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die Revalidierung des 2025er Waermepumpenstroms BE1 nach der normativen Formel
2. die Revalidierung der 2025er BE1-Tarifkette fuer die Warmwasserableitung
3. die Neufestlegung des aggregierten Jahreskostenbelegs `kb-warmwasser-be1`
4. die technische Validierung, dass der warmwasser-revalidierte Zwischenstand erfolgreich finalisiert und abgerechnet werden kann

## Out of Scope

Explizit nicht Teil dieses Slices:

- neue Review-Punkte oder PDF-Parser
- Aenderungen an bereits uebernommenen Standardkosten-/Brennstoff-/Heiznebenkostenbelegen
- Aenderungen an direkten Wohnungsstromkosten
- weitere HKV-Korrekturen
- Aenderungen an der bereits korrigierten Stromtarifkette ausser ihrer Nutzung fuer die Warmwasserableitung

## Normative Festlegungen

### 1. Formel fuer den Waermepumpenstrom 2025

Fuer BE1 gilt auch 2025 normativ:

`WP_Strom = Zaehler_BE1_Gesamtanlage - Zaehler_NE1_individual - Zaehler_NE2_individual`

Fuer die Jahresableitung 2025 sind folgende Messwerte massgeblich:

- `z-strom-be1-total`: `15087.0 -> 19907.0`  => `4820.0 kWh`
- `z-strom-ne2`: `5572.65 -> 7150.6` => `1577.95 kWh`
- `z-strom-ne1` Jahresdifferenz fuer die Ableitung: `34683.2 -> 35005.6` => `322.4 kWh`

Quellspur fuer den jahresbezogenen NE1-Wert:

- Startwert `34683.2` aus `data/2024/input_tariff_from_excel.json` per `2024-12-31`
- Endwert `35005.6` aus dem 2025er manuellen Ableseprotokoll per `2025-12-31`

Daraus folgt fuer 2025 normativ:

- `WP_Strom_2025 = 4820.0 - 1577.95 - 322.4 = 2919.65 kWh`

Hinweis:

- fuer den direkten Wohnungsstrom von Ingeborg Hainz bleibt im Input weiterhin die mietperiodenbezogene Lesung `2025-03-29 -> 2025-12-31` bestehen
- die hier verwendete Jahresdifferenz `34683.2 -> 35005.6` dient ausschliesslich der Warmwasser-Stromkostenableitung

### 2. Tarifableitung 2025 fuer Warmwasser

Der operative Warmwasser-Jahresbeleg verwendet 2025 keinen Grundpreisanteil und folgt weiterhin dem 2024er Tarif-/Workbook-Muster:

- nur Arbeitspreis
- tagesgewichtete Verteilung auf die fuer die Waermepumpenstromquelle fachlich korrekten operativen Tarifperioden 2025

Fuer `be1` ist nach dem Stromtarif-Korrektur-Slice normativ massgeblich:

- `Vattenfall easy12 Strom`
  - `gueltig_von = 2025-01-01`
  - `gueltig_bis = 2025-03-01`
  - `arbeitspreis = 34.57 ct/kWh`
  - Tage inkl. Enddatum: `60`
- `CHECK24 / Grueeuen`
  - `gueltig_von = 2025-03-02`
  - `gueltig_bis = 2025-12-31`
  - `arbeitspreis = 22.66 ct/kWh`
  - Tage inkl. Enddatum: `305`

Normative Tagesgewichtung:

- `gewichteter_arbeitspreis = ((60 * 34.57) + (305 * 22.66)) / 365`
- `gewichteter_arbeitspreis = 24.617808219178... ct/kWh`

### 3. Normativer Jahresbeleg

Normativer revalidierter Stand:

- `kb-warmwasser-be1`
  - `kostenart_id = verbrauchskosten_warmwasser`
  - `betrag = 718.75`
  - `datum = 2025-03-01`
  - `scope.berechnungseinheit = be1`

Normative Herleitung:

- `2919.65 kWh * 24.617808219178... ct/kWh / 100 = 718.753837... EUR`
- kaufmaennisch auf zwei Nachkommastellen gerundet: `718.75 EUR`

### 4. Erwartetes Verteilungsverhalten

Mit vorhandenem `kb-warmwasser-be1` gilt fuer den finalen Rechenkernlauf:

- `mp-ne1-hainz` erhaelt einen positiven Kostenanteil `verbrauchskosten_warmwasser`
- `mp-ne2` erhaelt einen positiven Kostenanteil `verbrauchskosten_warmwasser`
- `mp-ne3`, `mp-ne4`, `mp-ne5` erhalten weiterhin keinen separaten Kostenposten `verbrauchskosten_warmwasser`

## Akzeptanzkriterien

Dieser Slice ist fachlich fertig, wenn alle folgenden Punkte erfuellt sind:

1. `input.reviewed.warmwasser-revalidated.json` enthaelt `kb-warmwasser-be1` mit dem normativen Betrag `718.75 EUR`.
2. `finalize-year-input` schreibt daraus `data/2025/work/input.warmwasser-revalidated.json` erfolgreich.
3. `data/2025/work/input.warmwasser-revalidated.json` ist validator-konform.
4. Ein CLI-Lauf gegen `data/2025/work/input.warmwasser-revalidated.json` endet erfolgreich.
5. Im Ergebnis erhalten `mp-ne1-hainz` und `mp-ne2` einen positiven Kostenanteil `verbrauchskosten_warmwasser`.
6. `mp-ne3`, `mp-ne4` und `mp-ne5` erhalten keinen separaten Kostenanteil `verbrauchskosten_warmwasser`.
7. Erst nach erfolgreicher Revalidierung wird aus diesem Zwischenstand wieder das finale `data/2025/input.json` erzeugt.

## Test Cases

### TC1 Reviewed Input enthaelt den normativen Warmwasser-Jahresbeleg

Expected Result:

- `kb-warmwasser-be1` existiert
- `betrag = 718.75`
- `datum = 2025-03-01`
- `scope.berechnungseinheit = be1`

### TC2 Finalisierung schreibt den warmwasser-revalidierten Zwischenstand

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.warmwasser-revalidated.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.warmwasser-revalidated.validation.json" \
  --output-json "$NK_2025_WORK/input.warmwasser-revalidated.json"
```

Expected Result:

- `data/2025/work/input.warmwasser-revalidated.json` wird erfolgreich geschrieben

### TC3 Finaler CLI-Lauf ist technisch erfolgreich

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.warmwasser-revalidated.json" \
  --output-dir "$NK_2025_WORK/statements-warmwasser-revalidated" \
  --skip-pdf
```

Expected Result:

- der Lauf endet erfolgreich
- Statements fuer alle aktiven Mietparteien werden erzeugt

### TC4 Warmwasserkosten erscheinen nur bei BE1-Mietparteien

Expected Result:

- `mp-ne1-hainz`: positiver `verbrauchskosten_warmwasser`-Anteil
- `mp-ne2`: positiver `verbrauchskosten_warmwasser`-Anteil
- `mp-ne3`, `mp-ne4`, `mp-ne5`: kein `verbrauchskosten_warmwasser`

## Verification Commands

Vorbereitung:

```bash
export NK_REPO="/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung"
export NK_2025_WORK="$NK_REPO/data/2025/work"
cd "$NK_REPO"
```

TC1:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
reviewed = json.loads((base / 'input.reviewed.warmwasser-revalidated.json').read_text())
item = next(x for x in reviewed['kostenbelege'] if x['id'] == 'kb-warmwasser-be1')
print(item)
PY
```

TC2 und TC3 siehe oben.

TC4:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/statements-warmwasser-revalidated')
for mp in ['mp-ne1-hainz','mp-ne2','mp-ne3','mp-ne4','mp-ne5']:
    path = base / mp / 'einzelabrechnung.json'
    data = json.loads(path.read_text())
    warm = [x for x in data['cost_items'] if x['cost_type_id'] == 'verbrauchskosten_warmwasser']
    print(mp, warm)
PY
```

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-09 | 0 | Claude | Child-Spec fuer den 2025er Warmwasser-Stromkostenbeleg angelegt |
| 2026-04-09 | 1 | Codex | Tarifannahmen nach Nutzerkorrektur entschaerft: keine 1-Tages-Tibber-Sonderlogik mehr, Euro-Wert nur noch als vorlaeufiger Arbeitsstand markiert |
| 2026-04-10 | 2 | Codex | Slice auf stromtarif- und hkv-korrigierten Zwischenstand umgestellt; neue Artefaktkette definiert und `kb-warmwasser-be1 = 718.75 EUR` normativ revalidiert |
