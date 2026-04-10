# Nebenkostenabrechnung 2025 - Tibber Review-Slice

## Zweck

Diese Child-Spec definiert einen bounded Slice fuer die offenen Tibber-Rechnungen 2025.

Ziel ist, die Tibber-Rechnungen als operative Monats- oder Teilperioden-Tarife in die 2025er Tarifkette einzuordnen, ohne kuenstliche 1-Tages-Segmente zu erzeugen.

- pro Rechnung einen kanonischen Tarif anzulegen
- die korrekte Berechnungseinheit gemaess Nutzerreview zu verwenden
- die zugehoerigen Review-Punkte aus `review-output.json` zu entfernen

## In Scope

- `Belege/Rechnung_1167054681.pdf`
- `Belege/Rechnung_1167054673.pdf`
- `Belege/Rechnung_1167054194.pdf`
- `Belege/Rechnung_1167054608.pdf`
- `Belege/Rechnung_1167054756.pdf`

## Out of Scope

- Anpassung der Messwerte
- Sammelbelege, Versicherungen, Oel

## Normative Festlegungen

### 1. Operative Tarifkette fuer die betroffene Berechnungseinheit

Normative Praezisierung nach Nutzerkorrektur:

- der Vattenfall-vor-Grüüün-Pfad betrifft `be2`
- die Tibber-Rechnungen sind daher ebenfalls gegen `be2` zu modellieren, sofern sie diesen Vertragsstrang betreffen
- fuer den finalen 2025er Input sind aus den vorliegenden Tibber-Rechnungen `6` operative Monats- oder Teilperioden-Tarife zu erzeugen
- eine kuenstliche 1-Tages-Luecke bzw. ein synthetischer 1-Tages-Tarif ist nicht zulaessig
- falls eine ansonsten saubere Tarifkette exakt einen einzelnen Kalendertag offen liesse, wird das erste nachfolgende Tibber-Segment um einen Tag vorgezogen

### 2. Ableitungsregel aus den Rechnungen

Fuer jede Tibber-Rechnung gilt:

- aus der dedizierten Monats- oder Teilperiodensektion werden Arbeitspreis, Grundgebuehr und Gueltigkeitszeitraum abgeleitet
- pro Rechnung wird genau ein operativer `stromtarife[]`-Eintrag erzeugt
- die Zeitraeume der `5` Rechnungen ergeben zusammen die operative Tibber-Kette fuer 2025
- ein rein synthetischer `Tibber 2025-03-02`-Tarif ist nicht zulaessig

### 4. Abweichende Zaehlernummer

Die in `1167054756` genannte Zaehlernummer `1ISK0094903173` wird gemaess Parent-Spec als Dokumentfehler behandelt.

## Akzeptanzkriterien

1. `input.reviewed.json` enthaelt fuer die betroffene Berechnungseinheit `6` operative Tibber-Tarife.
2. Keiner dieser Tarife ist ein synthetischer 1-Tages-Tarif.
3. `review-output.json` enthaelt keine offenen Tibber-Items mehr.
4. `finalize-year-input` scheitert nicht an tarifbezogenen Strukturproblemen.
5. Ein technischer CLI-Lauf ist moeglich.

## Test Cases

### TC1 Operative Tibber-Tarifkette vorhanden

Expected Result:

- `6` Tibber-Tarife fuer die betroffene Berechnungseinheit
- kein 1-Tages-Tarif
- lueckenlos innerhalb der Tibber-Teilperioden

### TC2 Tibber-Review-Punkte entfernt

Expected Result:

- keine `review-output.items[]` mehr fuer `Rechnung_116705*.pdf`

### TC3 Finalisierung mit technischer Leer-Reviewdatei

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.tibber-validation.json" \
  --output-json "$NK_2025_WORK/input.tibber.json"
```

### TC4 Technischer Statement-Lauf

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.tibber.json" \
  --output-dir "$NK_2025_WORK/statements-tibber" \
  --skip-pdf
```

## Verification Commands

```bash
export NK_REPO="/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung"
export NK_2025_WORK="$NK_REPO/data/2025/work"
cd "$NK_REPO"
```

```bash
python3 - <<'PY'
import json
from pathlib import Path

base = Path("/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build")
with open(base / "input.reviewed.json", encoding="utf-8") as f:
    reviewed = json.load(f)
with open(base / "review-output.json", encoding="utf-8") as f:
    review = json.load(f)

be_tarife = [x for x in reviewed["stromtarife"] if x["lieferant"] == "Tibber"]
print("tibber_tarife", be_tarife)
print("review_sources", [x["source_relative_path"] for x in review["items"]])
PY
```

```bash
python3 - <<'PY'
import json
from pathlib import Path

base = Path("/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build")
with open(base / "review-output.json", encoding="utf-8") as f:
    review = json.load(f)

review["items"] = []

with open(base / "review-output.tibber-validation.json", "w", encoding="utf-8") as f:
    json.dump(review, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
```

Danach TC3 und TC4 wie oben.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-09 | 0 | Codex | Child-Spec fuer den bounded Slice `Tibber 2025 -> operative Resttarifkette + Review-Aufloesung` erstellt |
| 2026-04-09 | 1 | Codex | Nutzerkorrektur eingearbeitet: keine 1-Tages-Sonderlogik, stattdessen 5 operative Tibber-Tarife und Zuordnung zum Vattenfall/Grüüün-Strang von `be2` |
| 2026-04-10 | 2 | Codex | Neue Tibber-Rechnung `1167054111` fuer Mai 2025 eingearbeitet; Erwartung von `5` auf `6` operative Tarife korrigiert |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
