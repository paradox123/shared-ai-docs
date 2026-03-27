# Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1) Implementierungsplan

Bezugsspezifikationen:
- `../_specs/2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`
- `../_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
- `../_specs/2026-03-26 Stromkosten-Datenkorrektur und Test-Oracle Alignment.md`

Codebasis (analysiert):
- `private/Vermietung/nebenkosten-abrechnung/src`
- `private/Vermietung/nebenkosten-abrechnung/tests`

# Iteration 1

## Summary
- Aus der dedizierten Strom-/Warmwasser-Spec wurde ein umsetzungsorientierter Plan mit Ist-Analyse des bestehenden .NET-Codes erstellt.
- Bereits korrekt implementierte Regeln wurden als `[DONE]` markiert; offene Pflichtpunkte aus der Spec wurden als `[PENDING]` priorisiert.
- Schwerpunkt der naechsten Umsetzung: maschinell pruefbarer WP-Formelvertrag in `consumption_items` und Oracle-/Regression-Angleichung fuer 2024.

## Requirements Snapshot
- Direkter Wohnungsstrom (`strom`) und Waermepumpenstrom als Warmwasser-Kostenbasis muessen fachlich getrennt bleiben.
- Tarifmodus ist exklusiv: `stromtarife` vorhanden => keine `kostenbelege` mit `kostenart_id = "strom"`.
- Abgeleiteter WP-Strom muss in `consumption_items` maschinell pruefbar als Formelableitung erscheinen.
- Oracle 2024 fuer direkten Strom muss mindestens NE1 = 497.15 EUR, NE2 = 541.90 EUR, NE4 = 83.70 EUR abdecken.
- BE2 (NE3/NE4/NE5) bekommt keinen separaten Warmwasser-Posten (`verbrauchskosten_warmwasser`).

## Current State Snapshot
- [DONE] Tarifmodus-Konfliktregel ist fail-fast umgesetzt.
  - Evidence: `src/Nebenkosten.Core/Validation/InputValidator.cs` (StromInputModeConflict)
  - Evidence: `tests/Nebenkosten.Tests/ValidationTests.cs` (`ShouldFailFast_WhenTariffModeIsMixedWithDirectStromKostenbelege`)
- [DONE] WP-Strom-Herleitung wird technisch abgeleitet (`BE1 gesamt - NE1 - NE2`) und als abgeleiteter Verbrauch markiert.
  - Evidence: `src/Nebenkosten.Core/Services/ConsumptionCalculator.cs` (`TryDeriveWpStrom`)
- [DONE] Kostenarten fuer `strom` und `verbrauchskosten_warmwasser` sind getrennt konfiguriert.
  - Evidence: `src/Nebenkosten.Core/Domain/CostMatrixConfig.cs`
- [DONE] Tarifbasierte Stromkostenaufteilung inkl. Anhangsdaten ist umgesetzt.
  - Evidence: `src/Nebenkosten.Core/Services/ConsumptionCalculator.cs` (`CalculateStromCostBreakdownForNe`)
  - Evidence: `src/Nebenkosten.Core/Services/StatementAssembler.cs` (`StromkostenAnhang`)
- [PENDING] Normativer Output-Mindestvertrag fuer WP-Formel in `consumption_items` ist nicht vollstaendig (fehlende strukturierte Felder).
  - Evidence: `src/Nebenkosten.Core/Output/StatementResult.cs` (`StatementConsumption` hat aktuell nur `ist_abgeleitet` + `herleitung`)
- [PENDING] 2024-Regression T12 nutzt fuer NE2 aktuell den alten Excel-Bug-Referenzwert (497.15) statt den in der neuen Spec festgelegten Wert 541.90.
  - Evidence: `tests/Nebenkosten.Tests/Regression2024Tests.cs` (`excelOracleStrom["mp-ne2"] = 497.15m`)
- [PENDING] Es fehlt eine explizite Regression auf die neuen Warmwasser-Oraclewerte NE1 (403.21) und NE2 (376.28).
  - Evidence: `tests/Nebenkosten.Tests/Regression2024Tests.cs` (kein expliziter Warmwasser-Oracle-Test)
- [PENDING] Die BE2-Regel ist fachlich in der Spec vorhanden, aber als eigener Regressionstest noch nicht abgesichert.
  - Evidence: keine dedizierte Assertion in `tests/Nebenkosten.Tests/Regression2024Tests.cs`

## Action Plan
1. [DONE] Bestehende Trennlogik Strommodus verifizieren und als unveraenderte Guardrail festschreiben.
   - Done signal: `InputValidator`-Regeln und Validation-Tests bleiben gruen.
2. [PENDING] WP-Formelvertrag in `consumption_items` auf strukturierte Felder erweitern.
   - Done when: `StatementConsumption` enthaelt fuer WP mindestens:
     - `item_type = "derived_formula_wp_strom"`
     - `formula = "Zaehler_BE1_Gesamtanlage - Zaehler_NE1_individual - Zaehler_NE2_individual"`
     - `meter_refs = ["Zaehler_BE1_Gesamtanlage", "Zaehler_NE1_individual", "Zaehler_NE2_individual"]`
     - `derived_value` (numerisch)
3. [PENDING] Mapping `ConsumptionEntry -> StatementConsumption` fuer den WP-Fall normativ umsetzen.
   - Done when: `StatementAssembler` schreibt den WP-Fall maschinell pruefbar und ohne Parser-Abhaengigkeit auf Freitext.
4. [PENDING] T12-Strom-Oracle auf neue Spec-Werte ausrichten.
   - Done when: `Regression2024Tests` verwendet NE2 = 541.90 EUR als Sollwert und klassifiziert keine absichtliche Bug-Abweichung mehr fuer NE2.
5. [PENDING] Neue Warmwasser-Oracletests fuer 2024 ergaenzen.
   - Done when: Tests validieren explizit:
     - NE1 `verbrauchskosten_warmwasser` = 403.21 EUR
     - NE2 `verbrauchskosten_warmwasser` = 376.28 EUR
6. [PENDING] BE2-Warmwasserregel als Regression absichern.
   - Done when: Ein Test stellt sicher, dass fuer NE3/NE4/NE5 kein separater `verbrauchskosten_warmwasser`-Posten ausgewiesen wird.
7. [PENDING] Render-Vertrag fuer die strukturierte WP-Herleitung absichern.
   - Done when: `RenderingContractTests` prueft, dass die WP-Herleitung im Dokument sichtbar ist und den strukturierten Output korrekt widerspiegelt.
8. [PENDING] Fixture-Strategie direct vs tariff klar trennen und im Testnamen kenntlich machen.
   - Done when: 2024-Direct-Oracle und Tarif-Fixture-Tests sind als getrennte Pfade dokumentiert und laufen ohne semantische Vermischung.

## Open Items
- [DECISION NON-BLOCKING] Soll die detaillierte WP-Formel nur im JSON-vertraglich strukturiert sein oder zusaetzlich als eigener Abschnitt in `stromkosten_anhang` normiert werden?
- [MISSING SPEC NON-BLOCKING] Toleranzen fuer Oracle-Vergleich je Kostenart (z. B. feste 0.01 vs. 0.10 bei Rundungsdifferenzen) sind noch nicht zentral normiert.

## Verification Test Cases
1. Given ein Input mit `stromtarife` und gleichzeitigem `kostenbelege.strom`, when validiert wird, then bricht der Lauf mit `StromInputModeConflict` fail-fast ab.
2. Given BE1-Stromzaehlerdaten, when die WP-Herleitung erzeugt wird, then erscheint ein `consumption_items`-Element mit `item_type`, `formula`, `meter_refs` und `derived_value` gemaess Spec.
3. Given 2024-Direct-Fixture, when Strom-Oracletests laufen, then gilt: NE1 = 497.15, NE2 = 541.90, NE4 = 83.70 (jeweils innerhalb der festgelegten Toleranz).
4. Given 2024-Direct-Fixture, when Warmwasser-Oracletests laufen, then gilt: NE1 = 403.21 und NE2 = 376.28 unter `verbrauchskosten_warmwasser`.
5. Given 2024-Direct-Fixture fuer BE2, when `cost_items` ausgewertet werden, then gibt es fuer NE3/NE4/NE5 keinen separaten `verbrauchskosten_warmwasser`-Posten.
6. Given gerenderte Einzelabrechnung mit abgeleiteter WP-Formel, when RenderingContractTests laufen, then ist die Herleitung sichtbar und fachlich mit dem JSON konsistent.

# Iteration 2

## Summary
- Plan auf implementation-ready geschliffen: keine Ausnahme-Logik fuer NE2-Strom mehr, nur korrigierte Oracle-Werte.
- Offene Detailentscheidungen wurden nicht an den Nutzer delegiert, sondern konkret beantwortet und in ausfuehrbare Schritte uebersetzt.
- Naechste Implementierungsschritte sind jetzt direkt umsetzbar, inklusive klarer Fixture-Strategie fuer Warmwasser-Oracles.

## Current State Snapshot
- [DONE] T12-Strom-Oracle nutzt korrigierte Werte ohne Excel-Bug-Ausnahme.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Regression2024Tests.cs` (`mp-ne2 = 541.90`, Klassifizierung nur `gleich`/`Implementierungsfehler`)
- [DONE] Strom-Ausnahmebehandlung wurde aus der laufenden Regression entfernt.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Regression2024Tests.cs` (kein Zweig `bekanntes Excel-Delta` mehr)
- [PENDING] Normativer WP-Formelvertrag in `consumption_items` bleibt offen (strukturierte Felder fehlen weiterhin).
  - Evidence: `src/Nebenkosten.Core/Output/StatementResult.cs`
- [PENDING] Warmwasser-Oracletests auf Spec-Stichproben sind noch nicht als stabile Regression umgesetzt.
  - Evidence: kein expliziter T13/T14-Block in `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Regression2024Tests.cs`
- [PENDING] BE2-Regel (`kein separater verbrauchskosten_warmwasser`) ist noch nicht als dedizierter Regressionstest abgesichert.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Regression2024Tests.cs`

## Action Plan
1. [DONE] T12 final auf korrigierte Strom-Oracles ohne Ausnahme gebracht.
  - Done signal: `Regression2024Tests` prueft NE1=497.15, NE2=541.90, NE4=83.70 und akzeptiert keine Sonderkategorie mehr.
2. [DONE] Plan-Entscheidung getroffen: Es gibt keine fachliche Sonderbehandlung mehr fuer den alten Excel-NE2-Wert.
  - Done signal: Specs und Testvertrag sprechen nur noch von korrigierten Sollwerten.
3. [DONE] Plan-Entscheidung getroffen: Oracle-Toleranz wird fix auf 0.01 EUR gesetzt.
  - Done signal: Toleranz ist in Spec und Verifikationsfaellen explizit normiert.
4. [PENDING] WP-Formelvertrag in `StatementConsumption` um strukturierte Felder erweitern (`item_type`, `formula`, `meter_refs`, `derived_value`).
  - Done when: WP-Herleitung ist im JSON ohne Freitext-Parser maschinell pruefbar.
5. [PENDING] Warmwasser-Oracles als eigene, stabile Direct-Fixture-Regressionsfaelle T13/T14 umsetzen.
  - Done when: Tests validieren NE1=403.21 und NE2=376.28 gegen eine dafuer fixierte 2024-Direct-Fixture.
6. [PENDING] BE2-Regel als Regressionstest fixieren.
  - Done when: Test garantiert fuer NE3/NE4/NE5 kein separater `verbrauchskosten_warmwasser`-Posten.
7. [PENDING] Render-Vertrag fuer strukturierte WP-Herleitung absichern.
  - Done when: `RenderingContractTests` prueft Sichtbarkeit und Konsistenz zwischen JSON und HTML.
8. [PENDING] Fixture-Set klar trennen und benennen (`2024-direct-strom-oracle`, `2024-direct-warmwasser-oracle`, `2024-tariff`).
  - Done when: Keine semantische Vermischung mehr zwischen Strom- und Warmwasser-Oraclepfaden.

## Open Items
- Keine offenen blocking Spec-/Decision-Punkte fuer die naechste Umsetzung.

## Verification Test Cases
1. Given ein Input mit `stromtarife` und gleichzeitigem `kostenbelege.strom`, when validiert wird, then bricht der Lauf mit `StromInputModeConflict` fail-fast ab.
2. Given BE1-Stromzaehlerdaten, when die WP-Herleitung erzeugt wird, then erscheint ein `consumption_items`-Element mit `item_type`, `formula`, `meter_refs` und `derived_value` gemaess Spec.
3. Given 2024-Direct-Strom-Oracle-Fixture, when T12 laeuft, then gilt: NE1=497.15, NE2=541.90, NE4=83.70 mit Toleranz 0.01 und ohne Ausnahme-Kategorie.
4. Given 2024-Direct-Warmwasser-Oracle-Fixture, when Warmwasser-Oracletests laufen, then gilt: NE1=403.21 und NE2=376.28 unter `verbrauchskosten_warmwasser` mit Toleranz 0.01.
5. Given 2024-Direct-Fixture fuer BE2, when `cost_items` ausgewertet werden, then gibt es fuer NE3/NE4/NE5 keinen separaten `verbrauchskosten_warmwasser`-Posten.
6. Given gerenderte Einzelabrechnung mit abgeleiteter WP-Formel, when RenderingContractTests laufen, then ist die Herleitung sichtbar und fachlich mit dem JSON konsistent.

## Readiness
- In dieser Iteration ist der Plan implementation-ready: keine offenen blocking Spec-/Decision-Themen, klare naechste Implementierungsschritte, klare Verifikation.

# Iteration 3

## Summary
- Plan nach Review geschaerft: Sequenz fuer Fixture-Aufbau und Warmwasser-Regression ist jetzt widerspruchsfrei.
- Readiness wurde praezisiert: der Plan ist auf Planungsebene implementation-ready, die Codebasis erfuellt die Spec aber noch nicht vollstaendig.
- T10 ist im Plan jetzt explizit als historischer Gesamtkosten-Regressionstest eingeordnet; die entsprechende Klarstellung im Testartefakt bleibt als Umsetzungsschritt sichtbar.

## Current State Snapshot
- [DONE] T12 prueft korrigierte direkte Strom-Oracles ohne Ausnahmekategorie.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Regression2024Tests.cs`
- [PENDING] `consumption_items` erfuellt den normativen WP-Mindestvertrag noch nicht.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Output/StatementResult.cs`
- [PENDING] Fuer Warmwasser-Oracles existiert noch keine getrennte 2024-Direct-Warmwasser-Fixture.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/TestDataFactory.cs`
- [PENDING] T10 fuehrt weiterhin historische Excel-Deltas fuer Gesamtkosten; die Klarstellung im Code/Testartefakt ist noch nicht nachgezogen.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Regression2024Tests.cs`

## Action Plan
1. [DONE] T12-Stromvertrag auf korrigierte Sollwerte ohne Ausnahme fixiert.
  - Done signal: `gleich`/`Implementierungsfehler` sind die einzigen zulaessigen Kategorien fuer direkte Strom-Oracles.
2. [PENDING] Fixture-Set zuerst fachlich und technisch trennen (`2024-direct-strom-oracle`, `2024-direct-warmwasser-oracle`, `2024-tariff`).
  - Done when: `TestDataFactory` oder aequivalente Fixture-Loader bieten getrennte, eindeutig benannte Eingabepfade fuer diese drei Faelle.
3. [PENDING] WP-Formelvertrag in `StatementConsumption` um strukturierte Felder erweitern (`item_type`, `formula`, `meter_refs`, `derived_value`).
  - Done when: WP-Herleitung ist im JSON ohne Freitext-Parser maschinell pruefbar.
4. [PENDING] Warmwasser-Oracles T13/T14 auf der getrennten Warmwasser-Fixture umsetzen.
  - Depends on: Action 2.
  - Done when: Tests validieren NE1=403.21 und NE2=376.28 unter `verbrauchskosten_warmwasser` mit Toleranz 0.01.
5. [PENDING] BE2-Regel als dedizierten Regressionstest auf einer passenden Direct-Fixture absichern.
  - Done when: Test garantiert fuer NE3/NE4/NE5 kein separater `verbrauchskosten_warmwasser`-Posten.
6. [PENDING] Render-Vertrag fuer strukturierte WP-Herleitung absichern.
  - Done when: `RenderingContractTests` prueft Sichtbarkeit und Konsistenz zwischen JSON und HTML fuer die neuen strukturierten WP-Felder.
7. [PENDING] T10 als historischen Gesamtkosten-Regressionstest explizit dokumentieren oder aus dem neuen Strom-/Warmwasser-Vertrag herausloesen.
  - Done when: Plan, Testname oder Testkommentar stellen klar, dass T10 nicht der normative direkte Strom-Oracle-Test ist.

## Open Items
- Keine offenen blocking Spec-/Decision-Punkte.

## Verification Test Cases
1. Given getrennte Fixture-Loader fuer `2024-direct-strom-oracle`, `2024-direct-warmwasser-oracle` und `2024-tariff`, when Testdaten geladen werden, then ist jeder Pfad fachlich eindeutig und ohne Mischsemantik benannt.
2. Given BE1-WP-Herleitung, when `consumption_items` serialisiert werden, then existieren `item_type`, `formula`, `meter_refs` und `derived_value` gemaess Spec.
3. Given `2024-direct-strom-oracle`, when T12 laeuft, then gilt: NE1=497.15, NE2=541.90, NE4=83.70 mit Toleranz 0.01 und ohne Ausnahmekategorie.
4. Given `2024-direct-warmwasser-oracle`, when T13/T14 laufen, then gilt: NE1=403.21 und NE2=376.28 unter `verbrauchskosten_warmwasser` mit Toleranz 0.01.
5. Given eine BE2-Direct-Fixture, when `cost_items` ausgewertet werden, then gibt es fuer NE3/NE4/NE5 keinen separaten `verbrauchskosten_warmwasser`-Posten.
6. Given gerenderte Einzelabrechnung mit strukturierter WP-Herleitung, when `RenderingContractTests` laufen, then ist die Herleitung sichtbar und mit dem JSON konsistent.
7. Given T10, when der Testvertrag beschrieben wird, then ist klar, dass er historische Gesamtkosten mit dokumentierten Deltas prueft und nicht den normativen direkten Strom-Oracle-Vertrag repraesentiert.

## Readiness
- Der Plan ist in dieser Iteration auf Planungsebene implementation-ready: keine offenen blocking Spec-/Decision-Themen, saubere Reihenfolge der naechsten Umsetzungsschritte, klare Verifikation.
- Die Implementierung selbst ist weiterhin nicht requirements-complete, solange WP-Strukturvertrag, Warmwasser-Oracles, BE2-Regression und Render-Vertrag noch fehlen.

# Iteration 4

## Summary
- Umsetzungspakete fuer die ersten drei Commits wurden konkretisiert (Dateien, Reihenfolge, Abnahme je Paket).
- Ziel ist ein risikoarmer Start: zuerst Fixture-Trennung, dann strukturierter WP-Vertrag, danach Regressionen/Rendering.
- Paketgrenzen sind so gesetzt, dass jedes Paket einzeln testbar und revertierbar bleibt.

## Commit Packages (First 3)
1. [PENDING] Commit 1 - Fixture-Split und Test-Loader entkoppeln.
   - Scope:
     - `tests/Nebenkosten.Tests/TestDataFactory.cs`
     - neue Fixtures unter `tests/Nebenkosten.Tests/Fixtures/2024/`:
       - `input_direct_strom_oracle.json`
       - `input_direct_warmwasser_oracle.json`
       - `input_tariff.json`
   - Regeln:
     - keine semantische Vermischung zwischen Strom- und Warmwasser-Oracles
     - eindeutige Benennung in Loader-Methoden (`RunPipeline2024DirectStrom`, `RunPipeline2024DirectWarmwasser`, `RunPipeline2024Tariff`)
   - Done when:
     - alle betroffenen Tests greifen explizit auf den passenden Loader zu
     - bestehende Testsuite bleibt gruen

2. [PENDING] Commit 2 - WP-Formelvertrag im Output strukturieren.
   - Scope:
     - `src/Nebenkosten.Core/Output/StatementResult.cs`
     - `src/Nebenkosten.Core/Services/StatementAssembler.cs`
   - Regeln:
     - `StatementConsumption` enthaelt `item_type`, `formula`, `meter_refs`, `derived_value`
     - fuer nicht-abgeleitete Zaehler bleiben die neuen Felder null/leer nach Vertrag
   - Done when:
     - WP-Herleitung ist maschinell pruefbar ohne Freitext-Parsing
     - JSON-Vertrag bleibt rueckwaertskompatibel fuer bestehende Felder

3. [PENDING] Commit 3 - Regressionen und Rendering-Vertrag nachziehen.
   - Scope:
     - `tests/Nebenkosten.Tests/Regression2024Tests.cs`
     - `tests/Nebenkosten.Tests/RenderingContractTests.cs`
   - Regeln:
     - T13/T14 fuer Warmwasser (NE1=403.21, NE2=376.28, Toleranz 0.01)
     - BE2-Regeltest: kein separater `verbrauchskosten_warmwasser` fuer NE3/NE4/NE5
     - Rendering prueft strukturierte WP-Felder sichtbar/konsistent
     - T10 wird explizit als historischer Gesamtkostenvertrag markiert (Name oder Kommentar)
   - Done when:
     - neue Regressionen sind stabil gruen
     - Render-Vertrag referenziert strukturierte Felder statt nur Freitext

## Execution Order
1. Commit 1
2. Commit 2
3. Commit 3

## Verification Gates
1. Nach Commit 1: `dotnet test --filter "FullyQualifiedName~TestDataFactory|FullyQualifiedName~ValidationTests|FullyQualifiedName~Regression2024Tests"`
2. Nach Commit 2: `dotnet test --filter "FullyQualifiedName~Regression2024Tests|FullyQualifiedName~RenderingContractTests"`
3. Nach Commit 3: `dotnet test`

## Readiness
- Diese Iteration ist implementation-ready fuer den unmittelbaren Start der Umsetzung: klare Paketgrenzen, klare Reihenfolge, klarer Verifikationspfad pro Paket.

# Iteration 5

## Summary
- Umsetzung gemaess Iteration 4 in TDD-Schritten durchgefuehrt: erst neue Tests (rot), dann Implementierung bis gruen.
- Fixture-Split, strukturierter WP-Formelvertrag und neue Regressionen/Rendering-Checks sind umgesetzt.
- Gesamtsuite ist nach Abschluss gruen.

## Delivery Status
1. [DONE] Commit 1 - Fixture-Split und Test-Loader entkoppelt.
   - Evidence:
     - `tests/Nebenkosten.Tests/Fixtures/2024/input_direct_strom_oracle.json`
     - `tests/Nebenkosten.Tests/Fixtures/2024/input_direct_warmwasser_oracle.json`
     - `tests/Nebenkosten.Tests/Fixtures/2024/input_tariff.json`
     - `tests/Nebenkosten.Tests/TestDataFactory.cs`
     - `tests/Nebenkosten.Tests/Nebenkosten.Tests.csproj`
2. [DONE] Commit 2 - WP-Formelvertrag im Output strukturiert.
   - Evidence:
     - `src/Nebenkosten.Core/Output/StatementResult.cs` (`item_type`, `formula`, `meter_refs`, `derived_value`)
     - `src/Nebenkosten.Core/Services/StatementAssembler.cs` (Mapping inkl. strukturierter WP-Felder und BE-bezogener abgeleiteter Eintraege)
3. [DONE] Commit 3 - Regressionen und Rendering-Vertrag nachgezogen.
   - Evidence:
     - `tests/Nebenkosten.Tests/Regression2024Tests.cs` (T13 Warmwasser-Oracles, T14 BE2-Regel)
     - `tests/Nebenkosten.Tests/StatementConsumptionContractTests.cs` (strukturierter WP-Vertrag)
     - `tests/Nebenkosten.Tests/RenderingContractTests.cs` (sichtbare strukturierte WP-Hinweise)
     - `src/Nebenkosten.Rendering/Templates/einzelabrechnung.html`

## Verification
1. `dotnet test --filter "FullyQualifiedName~StatementConsumptionContractTests|FullyQualifiedName~Regression2024Tests|FullyQualifiedName~RenderingContractTests"` -> gruen.
2. `dotnet test` -> `Passed: 52, Failed: 0`.

## Readiness
- Implementierung fuer die in Iteration 4 geschnittenen Pakete ist abgeschlossen und verifiziert.
- Die naechste fachliche Arbeit liegt bei optionaler Oracle-Feinabstimmung der Warmwasser-Fixturewerte gegen externe Fachherkunft, nicht bei fehlender technischer Umsetzung.

# Iteration 6

## Summary
- Nachlauf abgeschlossen: T10 ist jetzt im Testartefakt explizit als historischer Gesamtkostenvertrag markiert.
- Damit ist die zuvor offene Klarstellung aus Iteration 3/4 auch technisch im Codebestand umgesetzt.

## Delivery Status
1. [DONE] Historische Einordnung von T10 im Testartefakt nachgezogen.
   - Evidence:
     - `tests/Nebenkosten.Tests/Regression2024Tests.cs` (Testname `T10_HistoricalAggregate_...`)
     - Kommentar trennt historischen Gesamtkostencheck vom normativen Strom-/Warmwasservertrag.

## Verification
1. `dotnet test --filter "FullyQualifiedName~Regression2024Tests"` -> gruen (`Passed: 4, Failed: 0`).

## Readiness
- Plan- und Code-Stand sind fuer den aktuell vereinbarten Scope voll synchron.
- Offen bleibt nur optionale fachliche Feinabstimmung der Warmwasser-Oracle-Herkunftsdaten.

## History
| Date | Iteration | Author | Delta |
|---|---|---|---|
| 2026-03-27 | 1 | Copilot (GPT-5.3-Codex) | Neuer dedizierter Implementierungsplan aus Strom-/Warmwasser-Spec erstellt und gegen den aktuellen .NET-Codebestand im Pfad `private/Vermietung/nebenkosten-abrechnung` abgeglichen. |
| 2026-03-27 | 2 | Copilot (GPT-5.3-Codex) | Plan auf implementation-ready verfeinert: keine NE2-Ausnahme mehr, Oracle-Toleranz festgelegt, offene Detailfragen in konkrete Umsetzungsentscheidungen ueberfuehrt. |
| 2026-03-27 | 3 | Copilot (GPT-5.3-Codex) | Review-Befunde eingearbeitet: Fixture-Sequenz bereinigt, Readiness zwischen Plan und Implementierung getrennt, T10 als historischer Gesamtkostenvertrag eingeordnet. |
| 2026-03-27 | 4 | Copilot (GPT-5.3-Codex) | Umsetzung in drei konkrete Commit-Pakete geschnitten inkl. Datei-Scope, Done-Kriterien, Reihenfolge und Verifikations-Gates. |
| 2026-03-27 | 5 | Copilot (GPT-5.3-Codex) | TDD-Umsetzung abgeschlossen: Fixture-Split, strukturierter WP-Vertrag, neue Warmwasser/BE2/Rendering-Verifikation implementiert und mit 52/52 Tests validiert. |
| 2026-03-27 | 6 | Copilot (GPT-5.3-Codex) | Historische T10-Klarstellung im Testartefakt umgesetzt und gezielt verifiziert (Regression2024Tests gruen). |
