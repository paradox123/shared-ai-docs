# Nebenkostenabrechnung 2025 - BE2 Wasser und Sonderverteilung Korrektur-Slice

## Status

Accepted and closed on 2026-04-10.

Closeout summary:

- TC1 bis TC7 wurden im Closeout erneut ausgefuehrt und waren gruen.
- Der kanonische 2025er Endstand liegt in `data/2025/input.json`.
- Der kanonische PDF-Lauf fuer diesen Slice liegt in `data/2025/output/final-pdf-be2-water-fixed-2026-04-10_1756`.
- Der zugehoerige OpenSpec-Change `2026-04-10-2025-be2-water-fuel-correction` wurde per `openspec archive --skip-specs` archiviert.

## Zweck

Diese Child-Spec definiert genau einen bounded 2025-Korrektur-Slice fuer die verbleibenden fachlichen Auffaelligkeiten bei:

- `NE2` / `mp-ne2` (Schaefer)
- `NE3` / `mp-ne3` (Koenig)
- `NE4` / `mp-ne4` (Waldheim)
- `NE5` / `mp-ne5` (Hecht)

Der Slice schliesst zwei konkrete 2025-Sonderfaelle:

1. der 2025er Kaltwasserpfad fuer `NE3` und `NE5` ist im aktuellen Endstand unvollstaendig
2. fuer `BE2` gilt 2025 einmalig eine abweichende Brennstoffkostenverteilung, weil in `NE5` noch keine HKV verbaut waren

Ziel ist, den verbleibenden Plausibilitaetsbruch im 2025er `input.json` zu beseitigen, ohne daraus eine generische Dauerregel fuer 2026+ zu machen.

## Parent-Bezug

Massgebliche Referenzen:

- `Completed/2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `2026-04-10 Nebenkostenabrechnung 2025 Carryover Brennstoffkosten Korrektur-Slice.md`
- `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
- `docs/input-json-pattern.md`

Codeanker:

- `src/Nebenkosten.Core/Domain/CostMatrixConfig.cs`
- `src/Nebenkosten.Core/Services/AllocationCalculator.cs`
- `src/Nebenkosten.Import/Services/FinalizationService.cs`

## Problemstellung

Aktueller Befund aus dem carryover-korrigierten 2025er Stand `data/2025/input.json`:

- `NE3` traegt 2025 keine Kalt-/Warmwasserkosten, obwohl fuer den Kaltwasserzaehler ein plausibler Jahresendwert vorliegt
- `NE5` traegt 2025 keine Kalt-/Abwasserkosten, obwohl laut Nutzerregel der Verbrauch aus dem Hauptanschluss abzuleiten ist
- `NE2` und `NE4` tragen deshalb einen unplausibel grossen Anteil der Objekt-Kaltwasserkosten
- `BE2`-Brennstoffkosten werden aktuell ueber die Standard-Mischumlage des Rechenkerns verteilt, obwohl fuer 2025 einmalig gilt:
  - `76 %` der gesamten `BE2`-Brennstoffkosten entfallen auf `NE5`
  - nur die restlichen `24 %` werden zwischen `NE3` und `NE4` nach Heizverbrauch verteilt

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die Nachpflege des 2025er Kaltwasserpfads fuer `NE3`
2. die Ableitung und Materialisierung des 2025er Kaltwasserverbrauchs fuer `NE5`
3. die 2025-only Sonderverteilung der `BE2`-Brennstoffkosten gemaess `76 % / 24 %`
4. die Neu-Finalisierung von `data/2025/input.json`
5. die Neu-Erzeugung der finalen Abrechnungsartefakte

## Out of Scope

Explizit nicht Teil dieses Slices:

- neue Stromtarif-Aenderungen
- neue HKV- oder Warmwasser-Regeln ausserhalb der hier beschriebenen 2025-Sonderbehandlung
- generische Rechengrundsatz-Aenderungen fuer 2026+
- Aenderungen an Vorauszahlungen ausser der fachlichen Plausibilisierung im Review
- Layout-/Rendering-Aenderungen an der Einzelabrechnung

## Code-Realitaet und Design-Freeze

Der aktuelle Rechenkern kennt fuer `brennstoffkosten` nur die generische Mischumlage `30 % Wohnflaeche / 70 % Heizverbrauch`:

- `CostMatrixConfig.cs` konfiguriert `brennstoffkosten` fest als Mischumlage
- `AllocationCalculator.cs` wendet diese Regel generisch auf die jeweilige Berechnungseinheit an

Fuer die 2025-only Sonderregel `76 % / 24 %` gibt es daher zwei denkbare Umsetzungswege:

1. ein expliziter 2025-Sonderpfad im Rechenkern
2. die Materialisierung bereits auf Datenebene als 2025-only direkte Kostenbelege

Normative Freeze-Entscheidung fuer diesen Slice:

- fuer 2025 wird **kein generischer Engine-Umbau** verlangt
- die `BE2`-Brennstoff-Sonderregel darf als **direkt materialisierte 2025-only Kostenbeleg-Verteilung** umgesetzt werden
- damit bleibt die Sonderbehandlung lokal auf das Jahr 2025 begrenzt und vermeidet neue Dauerkomplexitaet
- bevorzugte Materialisierung:
  - `kb-brennstoff-be2-ne5-2025-temp`
  - `kb-brennstoff-be2-ne3-2025-temp`
  - `kb-brennstoff-be2-ne4-2025-temp`
  - jeweils als direkte 2025-only Kostenbelege mit Scope auf die betroffene Nutzeinheit

## Normative Regeln 2025

### 1. Kaltwasser `NE3`

Belastbare operative Regel fuer 2025:

- Zaehler: `z-kw-ne3`
- Startwert: `61.788 m3`
  - normative Quelle: 2024er Endstand aus `data/2024/input.json`
- Endwert: `143.88 m3`
  - normative Quelle: Nutzerangabe aus `Ableseprotokoll 31.12.2025`
- Jahresverbrauch 2025:
  - `143.88 - 61.788 = 82.092 m3`

### 2. Kaltwasser Hauptanschluss

Belastbare operative Regel fuer 2025:

- Zaehler: `z-kw-main`
- Startwert: `594.114 m3`
  - normative Quelle: 2024er Endstand aus `data/2024/input.json`
- Endwert: `865.503 m3`
  - normative Quelle: Nutzerangabe aus `Ableseprotokoll 31.12.2025`
- Jahresverbrauch 2025:
  - `865.503 - 594.114 = 271.389 m3`

### 3. Kaltwasser `NE5` als Differenz

Fuer 2025 gilt einmalig:

- `Kaltwasser NE5 = Hauptanschluss - (NE1 + NE2 + NE3 + NE4)`

Mit den normativen 2025er Verbrauchswerten:

- `NE1 = 11.24 m3`
- `NE2 = 29.4 m3`
- `NE3 = 82.092 m3`
- `NE4 = 21.32 m3`
- `Main = 271.389 m3`

Ergibt sich:

- `NE5 = 271.389 - 11.24 - 29.4 - 82.092 - 21.32 = 127.337 m3`

Diese Ableitung ist fuer 2025 als belastbare Uebergangsregel zu materialisieren.

Bevorzugte Materialisierung:

- neuer 2025-only Zaehler `z-kw-ne5`
- Jahresablesung 2025 mit Verbrauch `127.337 m3`
- Beschreibung/Herkunft verweist explizit auf `Hauptanschluss - NE1..NE4`

### 4. `BE2`-Brennstoffkosten 2025

Die netto umlagewirksamen `BE2`-Brennstoffkosten aus dem Carryover-Slice bleiben:

- `kb-brennstoff-be2 = 2922.26 EUR`

Fuer die interne 2025-Verteilung gilt einmalig:

- `76 %` hiervon entfallen direkt auf `NE5`
- die restlichen `24 %` entfallen nur auf `NE3` und `NE4`, verteilt nach dem 2025er Heizverbrauch der beiden NEs

Normative Zielwerte:

- `NE5 direct = 2922.26 * 0.76 = 2220.92 EUR`
- `Resttopf NE3+NE4 = 701.34 EUR`
- Heizverbrauchsverhaeltnis 2025:
  - `NE3 = 1769.487`
  - `NE4 = 5031.198`
  - `Summe = 6800.685`
- daraus:
  - `NE3 = 182.48 EUR`
  - `NE4 = 518.86 EUR`

Wichtig:

- diese Werte sind **2025-only Sonderwerte**
- aus dieser Spec darf keine Dauerregel fuer `BE2` in 2026+ abgeleitet werden
- die bisherigen generischen `BE2`-Brennstoffbelege duerfen im finalen 2025er Endstand nicht parallel zu den drei 2025-only Direktbelegen zu Doppelallokation fuehren

## Akzeptanzkriterien

Dieser Slice ist fachlich ausreichend geloest, wenn:

1. `NE3` im finalen 2025er Stand einen belastbaren Kaltwasserverbrauch von `82.092 m3` traegt
2. `NE5` im finalen 2025er Stand einen abgeleiteten Kaltwasserverbrauch von `127.337 m3` traegt
3. die Objekt-Kaltwasserverteilung 2025 wieder alle `NE1..NE5` umfasst
4. die `BE2`-Brennstoffkosten 2025 nicht mehr ueber die generische Standard-Mischumlage auf `NE3..NE5` laufen, sondern der 2025-Sonderregel entsprechen
5. die finalen Einzelabrechnungen fuer `NE2`, `NE3`, `NE4`, `NE5` sichtbar plausibilisiert sind
6. `data/2025/input.json` neu finalisiert ist
7. CLI-/PDF-Lauf auf dem korrigierten Endstand erfolgreich ist

## Baseline und Zielartefakte

Aktuelle problematische Baseline:

- `data/2025/input.json`
- `data/2025/output/final-pdf-carryover-fixed-2026-04-10_1613/`

Neue Zielartefakte dieses Slices:

- `data/2025/work/build/input.reviewed.be2-water-fixed.json`
- `data/2025/work/build/review-output.be2-water-fixed.validation.json`
- `data/2025/work/input.be2-water-fixed.json`
- `data/2025/work/build/be2-water-and-fuel-oracle.json`
- `data/2025/output/final-pdf-be2-water-fixed/`
- neu finalisierte `data/2025/input.json`

## Test Cases

### TC1 - Wasser-Orakel 2025 materialisieren

Ziel:

- die 2025er Wasserwerte fuer `Main`, `NE3` und `NE5` sind reproduzierbar dokumentiert

Expected Result:

- Orakeldatei mit:
  - `main = 271.389`
  - `ne3 = 82.092`
  - `ne5 = 127.337`

### TC2 - Reviewed Input enthaelt die 2025er Wasserkorrekturen

Ziel:

- der reviewed Stand enthaelt `NE3`-Kaltwasser und die 2025-Ableitung fuer `NE5`

Expected Result:

- `z-kw-ne3` hat einen 2025er Jahresverbrauch von `82.092 m3`
- `z-kw-ne5` ist vorhanden und traegt `127.337 m3`

### TC3 - 2025-only `BE2`-Brennstoffregel ist materialisiert

Ziel:

- die `BE2`-Brennstoffkosten folgen nicht mehr der generischen `30/70`-Verteilung des Standards, sondern den 2025-Sonderwerten

Expected Result:

- `NE5` traegt `2220.92 EUR`
- `NE3` traegt `182.48 EUR`
- `NE4` traegt `518.86 EUR`
- die generische `kb-brennstoff-be2`-Allokation ist im finalen 2025er Stand entfernt, ersetzt oder anderweitig neutralisiert, sodass keine Doppelallokation entsteht

### TC4 - Finalisierung des korrigierten reviewed Inputs

Ziel:

- `finalize-year-input` schreibt einen technisch gueltigen `input.be2-water-fixed.json`

Expected Result:

- keine Validierungsfehler

### TC5 - Finale `data/2025/input.json` synchronisieren

Ziel:

- der korrigierte reviewed Stand wird nicht nur als Zwischenartefakt, sondern als kanonische `data/2025/input.json` finalisiert

Expected Result:

- `data/2025/input.json` enthaelt die Wasserkorrekturen fuer `NE3` und `NE5` sowie die 2025-only `BE2`-Brennstoffregel

### TC6 - CLI-/PDF-Lauf auf korrigiertem Endstand

Ziel:

- die Einzelabrechnungen lassen sich aus der neu finalisierten `data/2025/input.json` erneut erzeugen

Expected Result:

- JSON/HTML/PDF je Mietpartei werden erfolgreich geschrieben

### TC7 - Plausibilitaetsvergleich fuer `NE2..NE5`

Ziel:

- die bisherigen Auffaelligkeiten werden gegen den Baseline-Stand sichtbar reduziert bzw. korrekt erklaert

Expected Result:

- tabellarischer Vergleich `Baseline 16:13 -> neuer Stand` fuer `NE2`, `NE3`, `NE4`, `NE5`

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
from decimal import Decimal
import json
from pathlib import Path

main = Decimal('865.503') - Decimal('594.114')
ne1 = Decimal('11.24')
ne2 = Decimal('29.4')
ne3 = Decimal('143.88') - Decimal('61.788')
ne4 = Decimal('21.32')
ne5 = main - ne1 - ne2 - ne3 - ne4
out = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build/be2-water-and-fuel-oracle.json')
out.write_text(json.dumps({
  'kaltwasser': {
    'main': float(main),
    'ne1': float(ne1),
    'ne2': float(ne2),
    'ne3': float(ne3),
    'ne4': float(ne4),
    'ne5': float(ne5)
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
data = json.loads(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build/input.reviewed.be2-water-fixed.json').read_text())
print('ne3_kw', [a for a in data['ablesungen'] if a['zaehler_id'] == 'z-kw-ne3'])
print('ne5_kw', [a for a in data['ablesungen'] if a['zaehler_id'] == 'z-kw-ne5'])
print('main_kw', [a for a in data['ablesungen'] if a['zaehler_id'] == 'z-kw-main'])
PY
```

TC3:

```bash
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build/input.reviewed.be2-water-fixed.json').read_text())
ids = {x['id']: x for x in data['kostenbelege']}
for key in ['kb-brennstoff-be2-ne5-2025-temp', 'kb-brennstoff-be2-ne3-2025-temp', 'kb-brennstoff-be2-ne4-2025-temp']:
    print(key, ids[key])
print('generic_be2_fuel', [x for x in data['kostenbelege'] if x['kostenart_id'] == 'brennstoffkosten' and ((x.get('scope') or {}).get('berechnungseinheit') == 'be2')])
PY
```

TC4:

```bash
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.be2-water-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.be2-water-fixed.validation.json" \
  --output-json "$NK_2025_WORK/input.be2-water-fixed.json"
```

TC5:

```bash
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.be2-water-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.be2-water-fixed.validation.json" \
  --output-json "$NK_REPO/data/2025/input.json"
python3 - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/input.json').read_text())
print('ne3_kw', [a for a in data['ablesungen'] if a['zaehler_id'] == 'z-kw-ne3'])
print('ne5_kw', [a for a in data['ablesungen'] if a['zaehler_id'] == 'z-kw-ne5'])
print('be2_fuel', [k for k in data['kostenbelege'] if (k['kostenart_id'] == 'brennstoffkosten' and ((k.get('scope') or {}).get('berechnungseinheit') == 'be2' or (k.get('scope') or {}).get('nutzeinheit') in ['NE3','NE4','NE5']))])
PY
```

TC6:

```bash
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_REPO/data/2025/input.json" \
  --output-dir "$NK_REPO/data/2025/output/final-pdf-be2-water-fixed"
python3 - <<'PY'
import json
from pathlib import Path
base = sorted(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output').glob('final-pdf-be2-water-fixed-*'))[-1]
for mid in ['mp-ne3', 'mp-ne4', 'mp-ne5']:
    data = json.loads((base / mid / 'einzelabrechnung.json').read_text())
    fuel = [x for x in data['cost_items'] if x['cost_type_id'] == 'brennstoffkosten']
    print(mid, fuel)
PY
```

TC7:

```bash
python3 - <<'PY'
import json
from pathlib import Path
old_base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output/final-pdf-carryover-fixed-2026-04-10_1613')
new_base = sorted(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output').glob('final-pdf-be2-water-fixed-*'))[-1]
for mid in ['mp-ne2', 'mp-ne3', 'mp-ne4', 'mp-ne5']:
    old = json.loads((old_base / mid / 'einzelabrechnung.json').read_text())['result_summary']
    new = json.loads((new_base / mid / 'einzelabrechnung.json').read_text())['result_summary']
    print(mid, {'old': old, 'new': new})
PY
```

## Ready-Check fuer Implementierung

Diese Child-Spec ist implementierungsreif, wenn vor dem Coding zusaetzlich klar ist:

- dass die 2025-only `BE2`-Sonderregel als direkte Materialisierung in `kostenbelege[]` zulaessig ist
- dass `z-kw-main` fuer 2025 mit `594.114 -> 865.503` verwendet werden darf
- dass `z-kw-ne3` fuer 2025 mit `61.788 -> 143.88` verwendet werden darf

Diese drei Punkte sind durch die Nutzerangaben und die 2024er Baseline in dieser Spec normativ beantwortet.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-10 | 0 | Codex | Neuer 2025-Sonderfall-Slice fuer BE2-Wasserpfad und 76%/24%-Brennstoffregel angelegt; exakte Orakelwerte und Verification Commands aus dem aktuellen 2025er Stand abgeleitet |
| 2026-04-10 | 1 | Codex | Closeout replayt; TC1-TC7 erneut gruen, kanonischen PDF-Lauf auf `final-pdf-be2-water-fixed-2026-04-10_1756` bestaetigt und OpenSpec-Change archiviert |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
