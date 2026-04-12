# Nebenkostenabrechnung 2025 - Carryover Brennstoffkosten Korrektur-Slice

## Status

Accepted and closed on 2026-04-10.

Closeout summary:

- TC1 bis TC5 wurden im Closeout erneut ausgefuehrt und waren gruen.
- Die Carryover-`Rest-vorjahr`-Belege sind im kanonischen 2025er Endstand nicht mehr als umlagewirksame Kostenbelege enthalten.
- Der zugehoerige OpenSpec-Change `2026-04-10-2025-carryover-brennstoff-correction` wurde per `openspec archive --skip-specs` archiviert.

## Zweck

Diese Child-Spec definiert genau einen bounded Korrektur-Slice fuer den 2025er Endstand:

- die fachliche und technische Korrektur des Brennstoffkosten-/Carryover-Pfads, falls der aktuell eingerechnete `Rest-vorjahr` die 2025er Jahreskosten unzulaessig erhoeht

Der Slice ist notwendig, weil der Vergleich `2024 -> 2025` einen plausiblen systematischen Ueberhang zeigt:

- 2025 enthaelt zusaetzliche Opening-Carryover-Belege in Hoehe von `6063.63 EUR`
- gleichzeitig ist kein gegenlaeufiger Endbestands-/Closing-Mechanismus im finalen 2025er Input sichtbar
- die resultierenden Nachzahlungen wirken deshalb fachlich auffaellig hoch

## Parent-Bezug

Massgebliche Referenzen:

- `Completed/2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`
- `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
- `docs/input-json-pattern.md`

Codeanker:

- `src/Nebenkosten.Import/Services/YearInputBuilder.cs`
- `src/Nebenkosten.Carryover/Services/CarryoverCalculator.cs`
- `src/Nebenkosten.Core/Services/AllocationCalculator.cs`

## Problemstellung

Aktueller Befund aus dem finalen 2025er Stand:

- `data/2025/input.json` enthaelt die Opening-Carryover-Belege
  - `kb-rest-vorjahr-2025-be1-heizoel = 3395.37 EUR`
  - `kb-rest-vorjahr-2025-be2-holz = 2242.40 EUR`
  - `kb-rest-vorjahr-2025-be2-pellets = 425.86 EUR`
- Summe: `6063.63 EUR`

Vergleichswerte:

- Summe `kostenbelege` 2024: `18670.90 EUR`
- Summe `kostenbelege` 2025: `22404.25 EUR`
- 2025 ohne `Rest-vorjahr`: `16340.62 EUR`

Das ist ein starker Hinweis darauf, dass der Opening-Carryover aktuell als voll umlagefaehiger Jahreskostenblock behandelt wird, ohne dass der 2025er Endbestand gegenlaeufig beruecksichtigt wird.

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die fachliche Klaerung, wie `Opening-Carryover` fuer Brennstoffe im Jahresinput 2025 behandelt werden muss
2. die Ueberpruefung, ob `kb-rest-vorjahr-*` 2025
   - voll umlagefaehige Kostenbelege,
   - reine Hilfs-/Bewertungsbelege,
   - oder nur Input fuer einen spaeteren Netto-Brennstoffpfad sein duerfen
3. die Korrektur der 2025er Brennstoffkosten-Artefakte
4. die Neu-Finalisierung von `data/2025/input.json`
5. die Neu-Erzeugung der finalen Abrechnungsartefakte

## Out of Scope

Explizit nicht Teil dieses Slices:

- neue Stromtarif-Aenderungen
- neue Messwerte-Nachtraege ausserhalb des Carryover-Kontexts
- Layout-/Rendering-Aenderungen an der Einzelabrechnung
- generische Neudefinition des gesamten Carryover-Subsystems fuer andere Jahre

## Normative Leitfragen des Slices

Vor Umsetzung muss fuer 2025 explizit beantwortet und danach normativ festgelegt sein:

1. Soll der `Opening-Carryover` 2025 als voll umlagefaehiger Kostenbeleg in `kostenbelege[]` verbleiben?
2. Falls nein: ueber welches Modell wird er stattdessen fachlich korrekt beruecksichtigt?
3. Gibt es fuer 2025 einen Endbestand, der gegen den Opening-Carryover zu saldieren ist?
4. Welche Netto-Brennstoffkosten fuer `be1` und `be2` sollen am Ende wirklich umlagewirksam sein?

## Akzeptanzkriterien

Dieser Slice ist fachlich ausreichend geloest, wenn:

1. eindeutig geklaert ist, ob die drei `kb-rest-vorjahr-2025-*`-Belege im 2025er Endinput verbleiben duerfen
2. die Brennstoffkosten 2025 gegen die fachlich korrekte Carryover-Regel neu aufgestellt sind
3. der 2025/2024-Vergleich danach nicht mehr denselben unplausiblen Carryover-Ueberhang zeigt
4. `data/2025/input.json` neu finalisiert ist
5. der PDF-/CLI-Lauf auf dem korrigierten 2025er Endinput erfolgreich ist
6. die resultierenden Mietersalden gegen den bisherigen Fehlstand sichtbar veraendert und plausibilisiert sind

## Baseline und Zielartefakte

Aktuelle problematische Baseline:

- `data/2025/input.json`
- `data/2025/output/final-pdf-2026-04-10_1535/`

Neue Zielartefakte dieses Slices:

- `data/2025/work/build/input.reviewed.carryover-fixed.json`
- `data/2025/work/build/review-output.carryover-fixed.validation.json`
- `data/2025/work/input.carryover-fixed.json`
- `data/2025/output/final-pdf-carryover-fixed/`
- neu finalisierte `data/2025/input.json`

## Test Cases

### TC1 - Carryover-Belege explizit pruefen

Ziel:

- der Slice zeigt reproduzierbar, welche `kb-rest-vorjahr-*`-Belege vor dem Fix im 2025er Endstand enthalten sind
- und welche Belegmenge nach dem Fix verbleibt

Expected Result:

- die Carryover-Brennstoffbelege sind im diff eindeutig sichtbar

### TC2 - Brennstoffkosten-Summe 2024 vs. 2025 plausibilisieren

Ziel:

- der korrigierte 2025er Brennstoffpfad ist gegen 2024 vergleichbar
- der aktuell auffaellige Ueberhang durch `Rest-vorjahr` ist verschwunden oder fachlich sauber begruendet

Expected Result:

- eine reproduzierbare Vergleichsausgabe `2024 vs 2025`

### TC3 - Finalisierung des carryover-korrigierten reviewed Inputs

Ziel:

- `finalize-year-input` schreibt einen technisch gueltigen `input.carryover-fixed.json`

Expected Result:

- keine Validierungsfehler

### TC4 - CLI-/PDF-Lauf auf korrigiertem Endstand

Ziel:

- die Einzelabrechnungen lassen sich erneut erzeugen

Expected Result:

- JSON/HTML/PDF je Mietpartei werden erfolgreich geschrieben

### TC5 - Saldenvergleich Fehlstand vs. Korrekturstand

Ziel:

- die Mietersalden des korrigierten Stands werden gegen den bisherigen Fehlstand verglichen

Expected Result:

- eine tabellarische Vergleichsausgabe mit altem und neuem Saldo je Mietpartei

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
data = json.loads(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/input.json').read_text())
carry = [x for x in data['kostenbelege'] if x['id'].startswith('kb-rest-vorjahr-2025-')]
print('carryover_belege', carry)
print('carryover_summe', round(sum(x['betrag'] for x in carry), 2))
PY
```

TC2:

```bash
python3 - <<'PY'
import json
from pathlib import Path
for year in ['2024', '2025']:
    data = json.loads(Path(f'/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/{year}/input.json').read_text())
    total = round(sum(x['betrag'] for x in data['kostenbelege']), 2)
    carry = round(sum(x['betrag'] for x in data['kostenbelege'] if x['id'].startswith('kb-rest-vorjahr-')), 2)
    print(year, {'kostenbelege_total': total, 'carryover_total': carry, 'ohne_carryover': round(total - carry, 2)})
PY
```

TC3:

```bash
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.carryover-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.carryover-fixed.validation.json" \
  --output-json "$NK_2025_WORK/input.carryover-fixed.json"
```

TC4:

```bash
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.carryover-fixed.json" \
  --output-dir "$NK_REPO/data/2025/output/final-pdf-carryover-fixed" \
  --skip-pdf
```

Nach erfolgreicher Sachpruefung fuer den Endstand zusaetzlich:

```bash
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_REPO/data/2025/input.json" \
  --output-dir "$NK_REPO/data/2025/output/final-pdf-carryover-fixed" 
```

TC5:

```bash
python3 - <<'PY'
import json
from pathlib import Path

old_base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output/final-pdf-2026-04-10_1535')
new_candidates = sorted(Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/output').glob('final-pdf-carryover-fixed-*'))
new_base = new_candidates[-1]

def load(base):
    out = {}
    for p in base.glob('*/einzelabrechnung.json'):
        data = json.loads(p.read_text())
        rs = data['result_summary']
        out[data['mietpartei_id']] = rs
    return out

old = load(old_base)
new = load(new_base)
for key in sorted(new):
    old_rs = old.get(key)
    new_rs = new[key]
    print(key, {
        'old': {
            'saldo': old_rs['saldo'],
            'typ': 'nachzahlung' if old_rs['is_nachzahlung'] else 'guthaben'
        } if old_rs else None,
        'new': {
            'saldo': new_rs['saldo'],
            'typ': 'nachzahlung' if new_rs['is_nachzahlung'] else 'guthaben'
        }
    })
PY
```

## Ready-Check fuer Implementierung

Diese Child-Spec ist implementierungsreif, wenn vor dem Coding zusaetzlich klar ist:

- welche fachliche Soll-Regel fuer Opening-Carryover 2025 gilt
- ob 2025 ein Closing-/Endbestandsgegenposten modelliert werden muss
- ueber welche Zielartefakte der Carryover-Fix kanonisch eingepflegt wird

Solange diese drei Punkte noch nicht explizit beantwortet sind, ist die Child-Spec bewusst plan-ready, aber noch nicht implementation-ready.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-10 | 0 | Codex | Neuer Follow-up-Slice fuer den mutmasslich fehlerhaften 2025er Carryover-/Brennstoffkostenpfad angelegt; Vergleich 2024 vs. 2025 als Problemtrigger normativ verankert |
| 2026-04-10 | 1 | Codex | Slice umgesetzt: Netto-Brennstoffkosten `Opening + Zukauf - Closing` fuer `be1`/`be2` in die 2025er Artefakte uebernommen, finale PDFs neu erzeugt und Saldenvergleich gegen den Fehlstand dokumentiert |
| 2026-04-10 | 2 | Codex | Closeout replayt; TC1-TC5 erneut gruen und OpenSpec-Change archiviert |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
