# Nebenkostenabrechnung 2025 - BE2 Heiznebenkosten Sonderverteilung Korrektur-Slice

## Status

Accepted and closed on 2026-04-10.

Closeout summary:

- TC1 bis TC7 wurden im Closeout erneut ausgefuehrt und waren gruen.
- Der kanonische PDF-Lauf fuer diesen Slice liegt in `data/2025/output/final-pdf-be2-heiznebenkosten-fixed-2026-04-10_1818`.
- Der zugehoerige OpenSpec-Change `2026-04-10-2025-be2-heiznebenkosten-correction` wurde per `openspec archive --skip-specs` archiviert.

## Zweck

Diese Child-Spec definiert genau einen letzten bounded 2025-Korrektur-Slice fuer die verbleibende fachliche Auffaelligkeit im `BE2`-Pfad:

- die `BE2`-Heiznebenkosten laufen im aktuellen 2025er Endstand noch ueber die generische Heizverbrauchsumlage zwischen `NE3` und `NE4`
- fuer 2025 soll jedoch dieselbe temporaere Sonderverteilung gelten wie bereits fuer `BE2`-Brennstoffkosten

Ziel ist, den verbleibenden Plausibilitaetsbruch fuer `NE4` zu beseitigen, ohne daraus eine generische Dauerregel fuer 2026+ zu machen.

## Parent-Bezug

Massgebliche Referenzen:

- `Completed/2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `Completed/2026-04-10 Nebenkostenabrechnung 2025 BE2 Wasser und Sonderverteilung Korrektur-Slice.md`
- `Completed/2026-04-10 Nebenkostenabrechnung 2025 HKV Korrektur-Slice.md`
- `docs/input-json-pattern.md`

Codeanker:

- `src/Nebenkosten.Core/Domain/CostMatrixConfig.cs`
- `src/Nebenkosten.Core/Services/AllocationCalculator.cs`
- `src/Nebenkosten.Import/Services/FinalizationService.cs`

## Problemstellung

Aktueller Befund aus dem zuletzt finalisierten 2025er Stand `data/2025/input.json` und dem kanonischen PDF-Lauf `data/2025/output/final-pdf-be2-water-fixed-*`:

- `BE2`-Brennstoffkosten wurden bereits als 2025-only Direktbelege fuer `NE3`, `NE4`, `NE5` materialisiert
- `BE2`-Heiznebenkosten laufen jedoch weiterhin ueber die Standardregel
  - Scope `be2`
  - Schluessel `Heizverbrauch`
  - Verteilung nur auf `NE3` und `NE4`
- dadurch traegt `NE4` aktuell den vollen grossen Heiznebenkostenanteil aus der Standardlogik

Konkreter Ist-Stand im letzten PDF-Lauf:

- `NE3 heiznebenkosten = 142.13 EUR`
- `NE4 heiznebenkosten = 404.12 EUR`
- `NE5 heiznebenkosten = 0 EUR`

Das entspricht exakt der generischen Heizverbrauchsverteilung:

- `NE3 = 1769.487 / 6800.685 * 546.25 = 142.13 EUR`
- `NE4 = 5031.198 / 6800.685 * 546.25 = 404.12 EUR`

Diese Verteilung ist fuer 2025 fachlich nicht gewollt.

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die 2025-only Sonderverteilung der `BE2`-Heiznebenkosten gemaess `76 % / 24 %`
2. die Materialisierung dieser Sonderregel auf Datenebene als direkte Kostenbelege
3. die Neu-Finalisierung von `data/2025/input.json`
4. die Neu-Erzeugung der finalen Abrechnungsartefakte

## Out of Scope

Explizit nicht Teil dieses Slices:

- neue Wasserregeln
- neue Brennstoffregeln
- neue HKV- oder Strompfade
- Aenderungen an Vorauszahlungen
  - insbesondere bleibt `NE5 / Hecht` mit `0 EUR` Vorauszahlung bewusst unveraendert
- generische Rechenkern-Aenderungen fuer 2026+

## Code-Realitaet und Design-Freeze

Der aktuelle Rechenkern konfiguriert `heiznebenkosten` generisch als verbrauchsabhaengige BE-Umlage:

- `CostMatrixConfig.cs` setzt `heiznebenkosten` auf
  - `ScopeTyp.BerechnungsEinheit`
  - `UmlageArt.Verbrauch`
  - `SchluesselTyp.Heizverbrauch`
- `AllocationCalculator.cs` verteilt diesen Kostenblock deshalb standardmaessig ueber den gesamten `BE2`-Heizverbrauch

Normative Freeze-Entscheidung fuer diesen Slice:

- fuer 2025 wird **kein generischer Engine-Umbau** verlangt
- die `BE2`-Heiznebenkosten-Sonderregel darf wie bei den `BE2`-Brennstoffkosten als **direkt materialisierte 2025-only Kostenbeleg-Verteilung** umgesetzt werden
- bevorzugte Materialisierung:
  - `kb-heiznebenkosten-be2-ne5-2025-temp`
  - `kb-heiznebenkosten-be2-ne3-2025-temp`
  - `kb-heiznebenkosten-be2-ne4-2025-temp`
- die generische `BE2`-Heiznebenkosten-Allokation darf im finalen 2025er Endstand nicht parallel dazu weiterlaufen
- normative Zielentscheidung:
  - `kb-heiznebenkosten-be2` wird fuer den 2025er reviewed/finalen Stand als generischer `BE2`-Kostenbeleg entfernt
  - ersetzt wird er ausschliesslich durch die drei 2025-only Direktbelege fuer `NE3`, `NE4`, `NE5`

## Normative Regeln 2025

### 1. Ausgangsbasis `BE2`-Heiznebenkosten

Der netto umlagewirksame 2025er Kostenblock bleibt:

- `kb-heiznebenkosten-be2 = 546.25 EUR`

### 2. 2025-only Sonderverteilung

Fuer 2025 gilt einmalig dieselbe Sonderlogik wie fuer `BE2`-Brennstoffkosten:

- `76 %` hiervon entfallen direkt auf `NE5`
- die restlichen `24 %` entfallen nur auf `NE3` und `NE4`, verteilt nach dem 2025er Heizverbrauch der beiden NEs

Normative Zielwerte:

- `NE5 direct = 546.25 * 0.76 = 415.15 EUR`
- `Resttopf NE3+NE4 = 131.10 EUR`
- Heizverbrauchsverhaeltnis 2025:
  - `NE3 = 1769.487`
  - `NE4 = 5031.198`
  - `Summe = 6800.685`
- daraus:
  - `NE3 = 34.11 EUR`
  - `NE4 = 96.99 EUR`

Wichtig:

- diese Werte sind **2025-only Sonderwerte**
- aus dieser Spec darf keine Dauerregel fuer `heiznebenkosten` in 2026+ abgeleitet werden
- die bisherigen generischen `BE2`-Heiznebenkosten duerfen im finalen 2025er Endstand nicht parallel zu den drei 2025-only Direktbelegen zu Doppelallokation fuehren

## Akzeptanzkriterien

Dieser Slice ist fachlich ausreichend geloest, wenn:

1. `NE5` im finalen 2025er Stand `415.15 EUR` `BE2`-Heiznebenkosten traegt
2. `NE3` im finalen 2025er Stand `34.11 EUR` `BE2`-Heiznebenkosten traegt
3. `NE4` im finalen 2025er Stand `96.99 EUR` `BE2`-Heiznebenkosten traegt
4. die generische `BE2`-Heiznebenkosten-Allokation im finalen 2025er Stand entfernt, ersetzt oder anderweitig neutralisiert ist
5. die finalen Einzelabrechnungen fuer `NE3`, `NE4`, `NE5` sichtbar plausibilisiert sind
6. `data/2025/input.json` neu finalisiert ist
7. CLI-/PDF-Lauf auf dem korrigierten Endstand erfolgreich ist

## Baseline und Zielartefakte

Aktuelle problematische Baseline:

- `data/2025/input.json`
- `data/2025/output/final-pdf-be2-water-fixed-*`

Kanonische reviewed Baseline fuer diesen Slice:

- `data/2025/work/build/input.reviewed.be2-water-fixed.json`

Normative Baseline-Regel:

- dieser Slice wird ausschliesslich von `input.reviewed.be2-water-fixed.json` abgeleitet
- keine aeltere reviewed Baseline oder ein frueherer Slice-Stand darf als Ausgangspunkt verwendet werden

Neue Zielartefakte dieses Slices:

- `data/2025/work/build/input.reviewed.be2-heiznebenkosten-fixed.json`
- `data/2025/work/build/review-output.be2-heiznebenkosten-fixed.validation.json`
- `data/2025/work/input.be2-heiznebenkosten-fixed.json`
- `data/2025/work/build/be2-heiznebenkosten-oracle.json`
- `data/2025/output/final-pdf-be2-heiznebenkosten-fixed/`
- neu finalisierte `data/2025/input.json`

## Test Cases

### TC1 - Heiznebenkosten-Orakel 2025 materialisieren

Ziel:

- die 2025er Zielwerte fuer `NE3`, `NE4`, `NE5` sind reproduzierbar dokumentiert

Expected Result:

- Orakeldatei mit:
  - `ne5 = 415.15`
  - `ne3 = 34.11`
  - `ne4 = 96.99`

### TC2 - Reviewed Input enthaelt die 2025er Heiznebenkosten-Sonderbelege

Ziel:

- der reviewed Stand enthaelt die drei 2025-only Direktbelege fuer `NE3`, `NE4`, `NE5`

Expected Result:

- `kb-heiznebenkosten-be2-ne5-2025-temp = 415.15`
- `kb-heiznebenkosten-be2-ne3-2025-temp = 34.11`
- `kb-heiznebenkosten-be2-ne4-2025-temp = 96.99`

### TC3 - Generische `BE2`-Heiznebenkosten-Allokation ist neutralisiert

Ziel:

- die Standard-`BE2`-Heiznebenkosten verteilen sich im finalen 2025er Stand nicht mehr parallel zu den 2025-only Direktbelegen

Expected Result:

- `kb-heiznebenkosten-be2` existiert im finalen 2025er Stand nicht mehr als generischer `BE2`-Kostenbeleg
- keine generische `heiznebenkosten`-Allokation auf Scope `be2`
- nur die drei 2025-only Direktbelege sind wirksam

### TC4 - Finalisierung des korrigierten reviewed Inputs

Ziel:

- `finalize-year-input` schreibt einen technisch gueltigen `input.be2-heiznebenkosten-fixed.json`

Expected Result:

- keine Validierungsfehler

### TC5 - Finale `data/2025/input.json` synchronisieren

Ziel:

- der korrigierte reviewed Stand wird als kanonische `data/2025/input.json` finalisiert

Expected Result:

- `data/2025/input.json` enthaelt die drei 2025-only `BE2`-Heiznebenkostenbelege

### TC6 - CLI-/PDF-Lauf auf korrigiertem Endstand

Ziel:

- die Einzelabrechnungen lassen sich aus der neu finalisierten `data/2025/input.json` erneut erzeugen

Expected Result:

- `NE3`, `NE4`, `NE5` enthalten exakt:
  - `NE3 = 34.11 EUR`
  - `NE4 = 96.99 EUR`
  - `NE5 = 415.15 EUR`
- keine zusaetzliche zweite generische `BE2`-Heiznebenkosten-Position bleibt in den Einzelabrechnungen bestehen

### TC7 - Plausibilitaetsvergleich fuer `NE3..NE5`

Ziel:

- der neue Stand ist gegen den letzten BE2-Wasser-Fix-Lauf nachvollziehbar veraendert

Expected Result:

- `NE4` sinkt sichtbar
- `NE5` steigt sichtbar
- `NE3` sinkt fuer den Heiznebenkostenanteil sichtbar

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
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path

heiz = Decimal('546.25')
ne5 = (heiz * Decimal('0.76')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
rest = heiz - ne5
ne3_units = Decimal('1769.487')
ne4_units = Decimal('5031.198')
total = ne3_units + ne4_units
ne3 = (rest * ne3_units / total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
ne4 = (rest - ne3).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
out = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build/be2-heiznebenkosten-oracle.json')
out.write_text(json.dumps({
  'heiznebenkosten': {
    'ne5': float(ne5),
    'ne3': float(ne3),
    'ne4': float(ne4)
  }
}, indent=2))
print(out)
print(out.read_text())
PY
```

TC2:

```bash
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build/input.reviewed.be2-heiznebenkosten-fixed.json').read_text())
ids = {x['id']: x for x in data['kostenbelege']}
for key in ['kb-heiznebenkosten-be2-ne5-2025-temp', 'kb-heiznebenkosten-be2-ne3-2025-temp', 'kb-heiznebenkosten-be2-ne4-2025-temp']:
    print(key, ids[key])
print('generic_be2_heiznebenkosten_reviewed', [x for x in data['kostenbelege'] if x['kostenart_id'] == 'heiznebenkosten' and ((x.get('scope') or {}).get('berechnungseinheit') == 'be2')])
PY
```

TC3:

```bash
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/input.json').read_text())
print('generic_be2_cost_beleg', [x for x in data['kostenbelege'] if x['id'] == 'kb-heiznebenkosten-be2'])
print('generic_be2_heiznebenkosten', [x for x in data['kostenbelege'] if x['kostenart_id'] == 'heiznebenkosten' and ((x.get('scope') or {}).get('berechnungseinheit') == 'be2')])
print('direct_temp', [x for x in data['kostenbelege'] if x['id'] in ['kb-heiznebenkosten-be2-ne5-2025-temp', 'kb-heiznebenkosten-be2-ne3-2025-temp', 'kb-heiznebenkosten-be2-ne4-2025-temp']])
PY
```

TC4:

```bash
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.be2-heiznebenkosten-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.be2-heiznebenkosten-fixed.validation.json" \
  --output-json "$NK_2025_WORK/input.be2-heiznebenkosten-fixed.json"
```

TC5:

```bash
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.be2-heiznebenkosten-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.be2-heiznebenkosten-fixed.validation.json" \
  --output-json "$NK_REPO/data/2025/input.json"
```

TC6:

```bash
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_REPO/data/2025/input.json" \
  --output-dir "$NK_REPO/data/2025/output/final-pdf-be2-heiznebenkosten-fixed"
python3 - <<'PY'
import json
from pathlib import Path
base = sorted(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output').glob('final-pdf-be2-heiznebenkosten-fixed-*'))[-1]
expected = {'mp-ne3': 34.11, 'mp-ne4': 96.99, 'mp-ne5': 415.15}
for mid in ['mp-ne3', 'mp-ne4', 'mp-ne5']:
    data = json.loads((base / mid / 'einzelabrechnung.json').read_text())
    items = [x for x in data['cost_items'] if x['cost_type_id'] == 'heiznebenkosten']
    print(mid, items)
    amounts = [round(x['party_amount_eur'], 2) for x in items]
    print('expected', expected[mid], 'actual_amounts', amounts)
PY
```

TC7:

```bash
python3 - <<'PY'
import json
from pathlib import Path
old_base = sorted(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output').glob('final-pdf-be2-water-fixed-*'))[-1]
new_base = sorted(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output').glob('final-pdf-be2-heiznebenkosten-fixed-*'))[-1]
for mid in ['mp-ne3', 'mp-ne4', 'mp-ne5']:
    old = json.loads((old_base / mid / 'einzelabrechnung.json').read_text())['result_summary']
    new = json.loads((new_base / mid / 'einzelabrechnung.json').read_text())['result_summary']
    print(mid, {'old': old, 'new': new})
PY
```

## Ready-Check fuer Implementierung

Diese Child-Spec ist implementierungsreif, wenn vor dem Coding zusaetzlich klar ist:

- dass die 2025-only `BE2`-Heiznebenkosten-Sonderregel als direkte Materialisierung in `kostenbelege[]` zulaessig ist
- dass `NE5 / Hecht` mit `0 EUR` Vorauszahlung bewusst unveraendert bleibt
- dass die bisherige generische `BE2`-Heiznebenkosten-Allokation im 2025er Endstand neutralisiert werden darf

Diese drei Punkte sind durch die Nutzerangabe und die bestehende 2025-only Sonderbehandlungslogik fuer `BE2`-Brennstoffkosten normativ beantwortet.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-10 | 0 | Codex | Neuer letzter 2025-only Korrektur-Slice fuer `BE2`-Heiznebenkosten angelegt; Zielwerte, Akzeptanzkriterien und Verification Commands aus dem aktuellen Endstand abgeleitet |
| 2026-04-10 | 1 | Codex | Slice umgesetzt, Closeout replayt und OpenSpec-Change archiviert; kanonischer PDF-Lauf auf `final-pdf-be2-heiznebenkosten-fixed-2026-04-10_1818` bestaetigt |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
