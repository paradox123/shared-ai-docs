# Nebenkostenabrechnung 2025 - Stromtarif Korrektur-Slice

## Zweck

Diese Child-Spec definiert genau einen bounded Fix-Slice fuer die 2025er Stromtarifkette.

Der Slice korrigiert den aktuell bekannten Fehlstand in den bereits erzeugten 2025er `work/`-Artefakten:

- kuenstlicher 1-Tages-Tibber-Tarif
- falsche oder inkonsistente `be_id`-Zuordnung in Teilen der Tarifkette
- veraltete Annahme eines Vattenfall-/Grueeuen-Pfads fuer `be1`

Der Slice dient ausdruecklich dazu, die Stromtariflogik **vor** der HKV-Korrektur und **vor** einer erneuten finalen Warmwasser-Bestaetigung sauber zu ziehen.

## Parent-Bezug

Massgebliche Referenzen:

- `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `2026-04-09 Nebenkostenabrechnung 2025 Tibber Review-Slice.md`
- `2026-04-09 Nebenkostenabrechnung 2025 Warmwasserkosten Ableitung-Slice.md`
- `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`

## Problemstellung

Der aktuelle 2025er Stand enthaelt in den bereits erzeugten Artefakten einen bewusst dokumentierten, aber nun fachlich verworfenen Zwischenstand:

- Tibber wurde uebergangsweise als synthetischer 1-Tages-Tarif modelliert
- die operative Tarifkette wurde nicht konsistent auf die vom Nutzer korrigierte Berechnungseinheit ausgerichtet
- der aktuelle Stand in `data/2025/input.json` ist deshalb fuer Stromtarife fachlich nicht kanonisch

Diese Child-Spec ersetzt den alten Zwischenstand nicht rueckwirkend, sondern definiert den naechsten korrigierenden Delivery-Slice.

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die Korrektur der 2025er `stromtarife[]`
2. die saubere operative Zuordnung der Stromtarifsegmente zur korrigierten Berechnungseinheit
3. die Ablage neuer korrigierter Zwischenartefakte fuer diesen Slice
4. die technische Verifikation der korrigierten Tarifkette
5. die Dokumentation, dass der bisherige `input.json`-Tarifstand historisch, aber nicht mehr kanonisch ist

## Out of Scope

Explizit **nicht** Teil dieses Slices:

- HKV-/Heizkostenverteiler-Korrektur
- Aenderung der Messwerte
- Aenderung der Restkostenbelege
- finale Warmwasser-Neuberechnung
- finale Neu-Finalisierung des 2025er `input.json`
- neue Parser- oder OCR-Logik

## Baseline-Artefakte mit bekanntem Fehlstand

Diese Artefakte bleiben als historische Zwischenstaende erhalten, gelten fuer Stromtarife aber als **fachlich ueberholt**:

- `data/2025/work/input.tibber.json`
- `data/2025/work/input.restkosten.json`
- `data/2025/input.json`

Normative Einordnung:

- diese Dateien werden fuer diesen Slice **nicht** als kanonischer Sollstand betrachtet
- sie dienen nur als Nachweis des bisherigen Bearbeitungsstands
- der korrigierte Slice schreibt neue Folgeartefakte statt den Fehlstand stillschweigend zu legitimieren

## Zielartefakte dieses Slices

Dieser Slice erzeugt oder aktualisiert genau die folgenden Artefakte:

- `data/2025/work/build/input.reviewed.tibber-fixed.json`
- `data/2025/work/build/review-output.tibber-fixed.validation.json`
- `data/2025/work/input.tibber-fixed.json`

Optional zusaetzlich ein reines Vergleichsartefakt:

- `data/2025/work/build/tariff-diff.tibber-fixed.json`

## Normative Festlegungen

### 1. Keine synthetischen 1-Tages-Tarife

Die bisherige Sonderlogik eines kuenstlichen Tibber-Tarifs fuer `2025-03-02` ist verworfen.

Normative Regel:

- es darf kein `stromtarife[]`-Eintrag existieren, dessen einziger Zweck die Schliessung eines rein synthetischen 1-Tages-Uebergangs ist
- wenn zwischen zwei belastbaren Segmenten genau ein Kalendertag offen bliebe, wird das erste folgende reale Tarifsegment um genau diesen Tag vorgezogen

### 2. Tibber als operative Rechnungssegmente

Die vorliegenden Tibber-Rechnungen werden fuer diesen Slice als operative Monats- oder Teilperiodensegmente modelliert.

Normative Regel:

- pro Tibber-Rechnung genau ein operativer `stromtarife[]`-Eintrag
- insgesamt `6` Tibber-Tarife fuer 2025
- Arbeitspreis und Grundpreis werden aus der dedizierten Monats- oder Teilperiodensektion der Rechnung abgeleitet
- Rechnungs-Uebersichten mit Verbrauchsanpassungen duerfen nicht als direkte Tarifbasis verwendet werden

### 3. Korrigierte Berechnungseinheit

Die bisherige Annahme eines Vattenfall-/Grueeuen-Pfads fuer `be1` ist verworfen.

Normative Nutzerentscheidung fuer diesen Slice:

- der Vattenfall-vor-Grueeuen-Pfad betrifft `be2`
- die dazugehoerigen Tibber-Segmente sind ebenfalls gegen `be2` zu modellieren, sofern sie Teil derselben Lieferantenkette sind
- `be_id` jeder korrigierten Tarifzeile ist explizit gegen die Nutzerkorrektur zu pruefen

### 4. Lueckenlose operative Tarifkette

Fuer die korrigierte betroffene Berechnungseinheit gilt:

- die Vattenfall-/Tibber-/Grueeuen-Kette muss ohne unerklaerte Luecken aufgebaut sein
- Ueberlappungen sind unzulaessig
- synthetische Interimssegmente sind unzulaessig
- jedes Segment muss auf eine belastbare Tarifquelle zurueckfuehrbar sein

Normative Nutzerpraezisierung:

- das Vertragsmetadatum fuer Gruueeuen bleibt `Lieferbeginn 2025-03-03`
- fuer die operative 2025er Tarifkette darf das Gruueeuen-Segment zur Vermeidung von Ueberlappungen pragmatisch auf den ersten Tag nach der letzten belastbaren Tibber-Periode verschoben werden
- fuer diesen Slice ist Gruueeuen daher operativ ab `2025-10-01` zu modellieren

### 5. Keine Kostenbeleg-Alternative in diesem Slice

Auch wenn Stromkosten theoretisch ueber `kostenbelege[]` modelliert werden koennten, wird fuer diesen Slice normativ **nicht** auf Belegmodellierung gewechselt.

Dieser Slice bleibt im bestehenden Modell:

- Strom ueber `stromtarife[]`
- keine neuen `kostenbelege[]` mit `kostenart_id = "strom"`

## Akzeptanzkriterien

Dieser Slice ist fachlich fertig, wenn alle folgenden Punkte erfuellt sind:

1. `input.reviewed.tibber-fixed.json` enthaelt fuer die korrigierte Berechnungseinheit genau `6` Tibber-Tarife.
2. Kein Tarif in `input.reviewed.tibber-fixed.json` ist ein synthetischer 1-Tages-Tarif.
3. Die korrigierte Tarifkette fuer die betroffene Berechnungseinheit ist lueckenlos und nicht ueberlappend.
4. Alle betroffenen Tarife haben die fachlich korrekte `be_id` gemaess Nutzerkorrektur.
5. `finalize-year-input` erzeugt aus `input.reviewed.tibber-fixed.json` erfolgreich `input.tibber-fixed.json`.
6. Ein technischer CLI-Lauf auf `input.tibber-fixed.json` endet erfolgreich.
7. Dieser Slice aendert weder HKV-Modellierung noch Warmwasser-Endwert.

## Test Cases

### TC1 Sechs operative Tibber-Tarife vorhanden

Ziel:

- sicherstellen, dass die Tibber-Rechnungen nicht mehr zu einem 1-Tages-Uebergangsartefakt verdichtet sind

Expected Result:

- genau `6` Tarife mit `lieferant = "Tibber"`
- alle `6` Tarife gehoeren zur korrigierten Berechnungseinheit

### TC2 Kein synthetischer 1-Tages-Tarif mehr vorhanden

Ziel:

- sicherstellen, dass die verworfene Zwischenlogik nicht mehr im korrigierten Review-Stand steckt

Expected Result:

- kein Tarif mit `gueltig_von == gueltig_bis`, sofern er nur als Uebergangskonstrukt erzeugt wurde
- insbesondere kein `Tibber 2025-03-02`-Spezialtarif

### TC3 Tarifkette ist lueckenlos und nicht ueberlappend

Ziel:

- sicherstellen, dass die korrigierte operative Kette technisch konsistent ist

Expected Result:

- die Segmente der betroffenen Berechnungseinheit bilden eine sortierbare, lueckenlose Kette gemaess Nutzerkorrektur
- keine Datumsueberlappungen zwischen zwei Segmenten derselben Berechnungseinheit

### TC4 Korrigierte `be_id`-Zuordnung

Ziel:

- sicherstellen, dass die Tarifkette auf die richtige Berechnungseinheit zeigt

Expected Result:

- alle betroffenen Vattenfall-/Tibber-/Grueeuen-Segmente tragen die vom Nutzer korrigierte `be_id`

### TC5 Finalisierung des Tibber-Fix-Zwischenstands erfolgreich

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.tibber-fixed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.tibber-fixed.validation.json" \
  --output-json "$NK_2025_WORK/input.tibber-fixed.json"
```

Expected Result:

- `input.tibber-fixed.json` wird erfolgreich geschrieben
- keine tarifbezogenen Validierungsfehler

### TC6 Technischer CLI-Lauf auf dem Tibber-Fix-Zwischenstand erfolgreich

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.tibber-fixed.json" \
  --output-dir "$NK_2025_WORK/statements-tibber-fixed" \
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
from datetime import date, timedelta

base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
reviewed = json.loads((base / 'input.reviewed.tibber-fixed.json').read_text())

tibber = [x for x in reviewed['stromtarife'] if x['lieferant'] == 'Tibber']
print('tibber_count', len(tibber))
print('tibber_tarife', tibber)

# Beispielhafte Konsistenzpruefung fuer die betroffene BE
be_id = 'be2'
chain = sorted([x for x in reviewed['stromtarife'] if x['be_id'] == be_id], key=lambda x: x['gueltig_von'])
print('chain', chain)

for left, right in zip(chain, chain[1:]):
    left_end = date.fromisoformat(left['gueltig_bis'])
    right_start = date.fromisoformat(right['gueltig_von'])
    print('pair', left['id'], right['id'], 'gap_days', (right_start - left_end).days - 1)
PY
```

TC5 Vorbereitung:

```bash
python3 - <<'PY'
import json
from pathlib import Path
base = Path('/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build')
(base / 'review-output.tibber-fixed.validation.json').write_text(
    json.dumps({'target_year': 2025, 'items': []}, ensure_ascii=False, indent=2) + '\n',
    encoding='utf-8'
)
PY
```

TC5 und TC6 siehe oben.

## Ready-Check fuer Implementierung

Diese Child-Spec ist implementierungsreif, wenn vor dem Coding zusaetzlich klar ist:

- welche `6` Tibber-Rechnungen die operative Tarifkette bilden
- welche exakten Datumsgrenzen nach Nutzerkorrektur gelten
- wie die korrigierte Vattenfall-/Grueeuen-Kette fuer dieselbe Berechnungseinheit vor und nach Tibber verlaeuft

Wenn diese drei Punkte in den Artefakten bereits manuell korrigiert wurden, darf direkt auf deren Basis implementiert werden.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-09 | 0 | Codex | Child-Spec fuer den Stromtarif-Korrektur-Slice mit neuer Artefaktkette, Testcases und Verification Commands angelegt |
| 2026-04-10 | 1 | Codex | Neue Tibber-Rechnung `1167054111` fuer Mai 2025 eingearbeitet; Erwartung von `5` auf `6` operative Tibber-Segmente angehoben |
| 2026-04-10 | 2 | Codex | Nutzerpraezisierung zum Gruueeuen-Cutover eingearbeitet; operatives Gruueeuen-Segment fuer `be2` auf `2025-10-01` gesetzt, um Ueberlappungen zu vermeiden |
