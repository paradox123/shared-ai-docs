# Nebenkostenabrechnung 2025 - Gebaeudeversicherungen Review-Slice

## Zweck

Diese Child-Spec definiert genau einen bounded Delivery-Slice aus dem 2025er Review-Backlog:

- die drei Gebaeudeversicherungsbelege 2025 in belastbare `kostenbelege[]` fuer `input.reviewed.json` zu ueberfuehren

## In Scope

- `Belege/GebaeudeversicherungI.pdf`
- `Belege/GebaeudeversicherungII.pdf`
- `Belege/GebaeudeversicherungIII.pdf`
- Zuordnung zu den bestehenden Versicherungsvertraegen 2025
- Entfernung genau dieser drei Review-Punkte aus `review-output.json`
- technischer Validierungslauf gegen `finalize-year-input` und `Nebenkosten.Cli`

## Out of Scope

- Tibber-Rechnungen
- Sammelbelege
- `Öl_25.pdf`
- Neudefinition der Versicherungsstruktur ausserhalb der drei bestehenden Vertraege

## Normative Festlegungen

### 1. Vertragszuordnung

Die drei 2025er AXA-Beitragsrechnungen sind wie folgt den bestehenden Vertraegen zuzuordnen:

- Versicherungsnummer `A-56003644333` -> `vertrag-ne1-ne2`
- Versicherungsnummer `A-56003644335` -> `vertrag-ne3`
- Versicherungsnummer `A-56003644342` -> `vertrag-ne4-ne5`

### 2. Kostenbelege 2025

Fuer diesen Slice gelten folgende 2025er Kostenbelege als belastbar:

- `vertrag-ne1-ne2`: `1289.33 EUR`, Belegdatum `2025-04-15`
- `vertrag-ne3`: `551.09 EUR`, Belegdatum `2025-04-15`
- `vertrag-ne4-ne5`: `2013.16 EUR`, Belegdatum `2025-04-15`

### 3. Anbieterpflege

Die drei Versicherungsvertraege duerfen fuer 2025 in `input.reviewed.json` auf Anbieter `AXA` aktualisiert werden, da die 2025er Beitragsrechnungen eindeutig von AXA stammen.

## Akzeptanzkriterien

1. `input.reviewed.json` enthaelt drei Kostenbelege der Kostenart `gebaeude_versicherung`.
2. Jeder Kostenbeleg referenziert genau einen bestehenden `versicherungsvertrag`.
3. `review-output.json` enthaelt keine offenen Items mehr fuer die drei Gebaeudeversicherungs-PDFs.
4. `finalize-year-input` scheitert nicht an versicherungsbezogenen Referenzen oder Kostenbelegstrukturen.
5. Ein technischer CLI-Lauf mit dem Slice-Zwischenstand ist moeglich.

## Test Cases

### TC1 Gebaeudeversicherungsbelege im reviewed input

Verification:

- JSON-Check auf `input.reviewed.json`

Expected Result:

- drei Kostenbelege mit `kostenart_id = gebaeude_versicherung`
- Scope verweist auf `vertrag-ne1-ne2`, `vertrag-ne3`, `vertrag-ne4-ne5`
- Betraege `1289.33`, `551.09`, `2013.16`

### TC2 Versicherungs-Review-Punkte entfernt

Verification:

- JSON-Check auf `review-output.json`

Expected Result:

- keine offenen `items[]` fuer die drei Gebaeudeversicherungs-PDFs
- andere Review-Punkte duerfen weiter vorhanden sein

### TC3 Finalisierung mit technischer Leer-Reviewdatei

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Import -- \
  finalize-year-input \
  --reviewed-input-json "$NK_2025_WORK/build/input.reviewed.json" \
  --review-output-json "$NK_2025_WORK/build/review-output.versicherung-validation.json" \
  --output-json "$NK_2025_WORK/input.versicherung.json"
```

Expected Result:

- kein Fehler wegen unbekannter Versicherungsvertraege oder ungueltiger Kostenbelege

### TC4 Technischer Statement-Lauf

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_2025_WORK/input.versicherung.json" \
  --output-dir "$NK_2025_WORK/statements-versicherung" \
  --skip-pdf
```

Expected Result:

- technischer Lauf erfolgreich
- Statement-Artefakte fuer alle Mietparteien vorhanden

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

base = Path("/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build")
with open(base / "input.reviewed.json", encoding="utf-8") as f:
    reviewed = json.load(f)
with open(base / "review-output.json", encoding="utf-8") as f:
    review = json.load(f)

insurance = [x for x in reviewed["kostenbelege"] if x["kostenart_id"] == "gebaeude_versicherung"]
print("insurance_belege", insurance)
print("review_sources", [x["source_relative_path"] for x in review["items"]])
PY
```

TC3 preparation:

```bash
python3 - <<'PY'
import json
from pathlib import Path

base = Path("/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2025/work/build")
with open(base / "review-output.json", encoding="utf-8") as f:
    review = json.load(f)

review["items"] = []

with open(base / "review-output.versicherung-validation.json", "w", encoding="utf-8") as f:
    json.dump(review, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
```

Danach TC3 und TC4 wie oben.

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-09 | 0 | Codex | Child-Spec fuer den bounded Slice `Gebaeudeversicherungen 2025 -> reviewed kostenbelege` erstellt |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
