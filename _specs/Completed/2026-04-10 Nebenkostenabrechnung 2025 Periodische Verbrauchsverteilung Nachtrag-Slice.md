# Nebenkostenabrechnung 2025 - Periodische Verbrauchsverteilung Nachtrag-Slice

## Status

Accepted and closed on 2026-04-10.

Closeout summary:

- Verification Commands im Closeout erneut gruen replayt.
- Zugehoeriger OpenSpec-Change archiviert unter `openspec/changes/archive/2026-04-10-2026-04-10-2025-periodic-consumption-allocation`.

## Zweck

Diese Child-Spec definiert genau einen bounded Nachtrags-Slice fuer den 2025er Operativpfad:

- die periodische, mietzeitbewusste Verteilung verbrauchsabhaengiger Kosten bei unterjaehriger Belegung bzw. Leerstand

Der Slice ist notwendig, weil der aktuelle Rechenkern verbrauchsabhaengige Mengen je Nutzeinheit ueber alle Periodensegmente aufsummiert und danach vollstaendig den aktiven Mietparteien dieser Nutzeinheit zuordnet. Damit kann ein nachgezogener `NE1`-Leerstandsverbrauch aktuell nicht sauber von der Mietzeit getrennt werden.

## Parent-Bezug

Massgebliche Referenzen:

- `2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- `2026-04-10 Nebenkostenabrechnung 2025 NE1 Leerstand Messwerte Nachtrag-Slice.md`
- `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`
- Codeanker:
  - `src/Nebenkosten.Core/Services/AllocationCalculator.cs`
  - `src/Nebenkosten.Core/Services/ConsumptionCalculator.cs`
  - `src/Nebenkosten.Core/Services/AbrechnungsContext.cs`

## Problemstellung

Der aktuelle Rechenkern verhaelt sich fuer verbrauchsabhaengige Verteilungen wie folgt:

1. `ConsumptionCalculator` erzeugt Verbrauchseintraege je Zaehler und Periode.
2. `AllocationCalculator.GetVerbrauchForNe(...)` summiert diese Eintraege je Nutzeinheit auf.
3. `AllocationCalculator.AllocateVerbrauchsMenge(...)` weist die gesamte Verbrauchsmenge der Nutzeinheit den aktiven Mietparteien zu.

Dadurch fehlt fuer `NE1` eine periodische Ueberlappungslogik zwischen

- Verbrauchssegment (`2025-01-01 -> 2025-03-31` Leerstand, `2025-03-31 -> 2025-12-31` Mieterperiode)
- und Mietzeit (`Einzug Ingeborg Hainz ab 2025-04-01`).

## In Scope

Dieser Slice umfasst ausschliesslich:

1. die fachlich korrekte Abgrenzung verbrauchsabhaengiger Mengen nach Periodenueberlappung zwischen Verbrauchssegment und Mietzeit
2. die dafuer noetige Anpassung im Rechenkern fuer mindestens
   - `Heizverbrauch`
   - `Warmwasserverbrauch`
   - `Kaltwasserverbrauch`
3. gezielte Tests, die Leerstands- und Teilperiodenfaelle absichern
4. die technische Verifikation, dass ein nachtraeglicher `NE1`-Leerstands-Messwertslice darauf aufsetzen kann

## Out of Scope

Explizit nicht Teil dieses Slices:

- das Einpflegen der fehlenden `NE1`-Leerstands-Messwerte selbst
- neue Stromtarif-Aenderungen
- neue OCR-/Parser-Logik
- Aenderungen an Kostenbelegen oder Artefakten ausser fuer gezielte Test-/Fixture-Abdeckung
- Aenderungen an Personen-, Wohnflaechen- oder sonstigen Schluesselverteilungen

## Normative Festlegungen

### 1. Verbrauchssegment und Mietzeit muessen ueberlappen

Fuer verbrauchsabhaengige Verteilungen gilt normativ:

- eine Mietpartei darf nur den Anteil eines Verbrauchssegments erhalten, dessen Periode sich mit ihrer effektiven Mietzeit ueberlappt
- Verbrauch ausserhalb dieser Ueberlappung darf der Mietpartei nicht zugerechnet werden

### 2. Leerstand erzeugt keinen Mieteranteil an Verbrauchssegmenten

Wenn fuer eine Nutzeinheit in einem Verbrauchssegment keine aktive Mietpartei existiert, gilt normativ:

- das Segment bleibt in der Gesamtmenge der Nutzeinheit bzw. des Scope enthalten
- es erzeugt aber keinen Mieteranteil fuer diese Nutzeinheit im Leerstandszeitraum

### 3. Scope-Gesamtmengen bleiben vollstaendig

Die periodische Verbrauchsverteilung darf nicht dazu fuehren, dass Scope-Gesamtmengen kuenstlich auf Mietzeiten gekuerzt werden.

Normative Regel:

- die Gesamtmenge eines Verbrauchsscope bleibt die Summe aller relevanten Verbrauchssegmente
- nur die Zurechnung auf Mietparteien wird ueber die Periodenueberlappung begrenzt

### 4. Warmwasser-Sonderpfad bleibt konsistent

Die bestehende Warmwasser-Zeitlogik in `GetEffectiveVerbrauchsTotalAmount(...)` darf durch diesen Slice nicht fachlich widerspruechlich werden.

Normative Regel:

- falls vorhandene Sonderlogik mit der neuen periodischen Verbrauchsverteilung ueberlappt, ist sie zu harmonisieren oder gezielt zu ersetzen
- das Ergebnis fuer den 2025er BE1-Warmwasserfall muss mit der neuen Periodenlogik konsistent bleiben

### 5. Strom bleibt ausserhalb dieses Slices

Direkter Wohnungsstrom wird in diesem Slice nicht neu modelliert.

Normative Regel:

- der Slice betrifft nur verbrauchsabhaengige Verteilungsschluessel, nicht die tarifbasierte direkte Stromkostenberechnung

## Akzeptanzkriterien

Dieser Slice ist fachlich fertig, wenn alle folgenden Punkte erfuellt sind:

1. Der Rechenkern kann mehrere Verbrauchssegmente pro Nutzeinheit verarbeiten, ohne den Leerstandsanteil automatisch einer spaeteren Mietpartei zuzuschlagen.
2. Fuer verbrauchsabhaengige Verteilungen erhalten Mietparteien nur noch Verbrauchssegmente, deren Periode mit ihrer effektiven Mietzeit ueberlappt.
3. Leerstandssegmente bleiben in den Scope-Gesamtmengen enthalten, erzeugen aber keinen Mieteranteil.
4. Bestehende 2024er Regressionen fuer Warmwasser/Strom bleiben gruen oder werden gezielt auf die neue korrekte Periodenlogik angepasst.
5. Der Rechenkern bleibt fuer den aktuellen 2025er Stand technisch lauffaehig.

## Test Cases

### TC1 Periodischer Verbrauch ausserhalb der Mietzeit wird nicht zugerechnet

Expected Result:

- ein Verbrauchssegment vor Einzug einer Mietpartei erzeugt fuer diese Mietpartei keinen Anteil
- ein Verbrauchssegment innerhalb der Mietzeit erzeugt weiterhin einen Anteil

### TC2 Leerstand bleibt in der Scope-Gesamtmenge enthalten

Expected Result:

- die Scope-Gesamtmenge eines verbrauchsabhaengigen Kostenpostens enthaelt weiterhin alle Segmente
- der Leerstandsanteil verschwindet nicht aus der Gesamtmenge, wird aber nicht auf eine Mietpartei gebucht

### TC3 HKV-/Warmwasser-/Kaltwasser-Verbrauch folgen derselben Periodenlogik

Expected Result:

- die periodische Ueberlappungslogik greift konsistent fuer die betroffenen verbrauchsabhaengigen Schluessel

### TC4 Repo-Regression bleibt gruen

Verification Command:

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet test Nebenkosten.sln
```

Expected Result:

- bestehende und neue Tests laufen erfolgreich

## Verification Commands

Vorbereitung:

```bash
export NK_REPO="/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung"
cd "$NK_REPO"
```

Gezielte Rechenkern-/Regressionstests fuer diesen Slice:

```bash
dotnet test tests/Nebenkosten.Tests/Nebenkosten.Tests.csproj --filter "AllocationCalculatorTests|Regression2024Tests"
```

TC4 siehe oben.

Optionaler technischer Smoke-Check auf aktuellem 2025er Stand nach Implementierung:

```bash
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json "$NK_REPO/data/2025/input.json" \
  --output-dir "$NK_REPO/data/2025/work/statements-periodic-consumption-smoke" \
  --skip-pdf
```

Expected Result:

- der CLI-Lauf endet technisch erfolgreich
- keine Regression durch die periodische Verbrauchslogik

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-10 | 0 | Codex | Child-Spec fuer periodenbewusste verbrauchsabhaengige Verteilung als separaten Rechenkern-Nachtrags-Slice angelegt |
| 2026-04-10 | 1 | Codex | Closeout abgeschlossen; gezielte Rechenkern- und CLI-Verifikationen erneut gruen ausgefuehrt und OpenSpec-Change archiviert |
