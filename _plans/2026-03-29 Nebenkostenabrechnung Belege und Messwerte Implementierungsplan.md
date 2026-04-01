# Nebenkostenabrechnung Belege und Messwerte Implementierungsplan

Bezugsspezifikationen:
- `../_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
- `../_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`

Codebasis (analysiert):
- `private/Vermietung/nebenkosten-abrechnung/src`
- `private/Vermietung/nebenkosten-abrechnung/tests`
- `private/Vermietung/nebenkosten-abrechnung/data/2024/input_tariff_from_excel.json`

Quellmaterial (operativ):
- `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2025`

# Iteration 1

## Summary
- Aus der finalen Import-Spec wurde ein umsetzungsorientierter Plan fuer eine vorgelagerte Import-/Vorverarbeitungsschicht abgeleitet.
- Die bestehende .NET-Anwendung bleibt ab `input.json` unveraendert; neue Arbeitspakete liegen vor dem bestehenden Rechenkern und referenzieren dessen Input-Vertrag.
- Bereits vorhanden sind Zielschema, Beispiel-Inputs, CLI, Validierung und Rendering fuer operative JSONs; noch nicht vorhanden sind 2025-Importautomation, Manifest, Review-Output und 2025-Scaffold.

## Requirements Snapshot
- Die Vorverarbeitung muss 2025er PDFs in operative Datensaetze fuer `zaehler[]`, `ablesungen[]`, `kostenbelege[]` und `stromtarife[]` ueberfuehren.
- Ab dem Einlesen der finalen `input.json` muessen Rechenkern, bestehende Validierung und Rendering fachlich unveraendert bleiben.
- Das kanonische Zaehlerregister ist die `zaehler[]`-Liste der Ziel-`input.json`; aus Belegen oder Messwerten duerfen keine neuen Zaehler erzeugt werden.
- PDFs werden mit nativer Textlage bevorzugt, sonst per OCR verarbeitet; Bundle-PDFs muessen in logische Einzelbelege segmentiert werden.
- Provenienz-, OCR- und Review-Informationen gehoeren in ein separates Import-Manifest, nicht in das operative JSON.
- Nicht eindeutig zuordenbare Belege muessen in einem Review-Output landen; solange Review-Faelle offen sind, gilt die erzeugte `input.json` nicht als final.
- Tibber-Rechnungen muessen als monatliche `stromtarife[]` mit Direktpreis-Prioritaet modelliert werden, nicht als direkte Strom-`kostenbelege[]`.
- ista-Monatswerte muessen auf genau eine kanonische Periodenablesung je relevantem Zeitraum verdichtet werden.
- Restbestand und `Rest aus Vorjahr` fuer Oel, Holz und Pellets muessen mit Durchschnittspreislogik, `Fm -> Rm`-Normalisierung und ohne negative operative `kostenbelege` verarbeitet werden.

## Current State Snapshot
- [DONE] Die normative Import-Spec und die Hauptspec sind abgestimmt und plan-ready.
  - Evidence: `../_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`, `../_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
- [DONE] Die bestehende Anwendung akzeptiert das Zielmodell bereits inklusive `ista_ablese`, `ista_monatsmittel`, `manuell`, mehrerer Zaehler je NE und `stromtarife[]`.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Input/InputDto.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Validation/InputValidator.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Services/AbrechnungsContext.cs`
- [DONE] Eine laufbare Downstream-CLI samt Validierung, Berechnung und Rendering existiert bereits fuer operative JSONs.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Cli/Program.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/README.md`
- [DONE] 2024-Beispielinputs und Fixtures existieren als strukturelle Referenz fuer das 2025-Scaffold.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/2024/`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Fixtures/2024/`
- [PENDING] Es gibt noch kein dediziertes Import-/Vorverarbeitungsprojekt fuer PDF-Extraktion, OCR, Manifest oder Review-Output.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/` enthaelt aktuell nur `Nebenkosten.Cli`, `Nebenkosten.Core`, `Nebenkosten.Rendering`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/` enthaelt aktuell keine Import-/OCR-Contract-Tests
- [PENDING] Ein 2025er Datenordner und ein gepflegtes 2025-Scaffold mit kanonischer `zaehler[]`-Liste fehlen noch.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/` enthaelt aktuell nur `2024/`
- [PENDING] Die OneDrive-Quelldokumente sind noch nicht in einen reproduzierbaren Importlauf mit stabilen Artefakten eingebunden.
  - Evidence: Die operative Quelle liegt ausserhalb des Repos unter dem oben referenzierten 2025-Pfad.

## Action Plan
1. [DONE] Downstream-Vertrag der bestehenden Anwendung einfrieren.
   - Done signal: Dieser Plan behandelt `InputDto.cs`, `InputValidator.cs`, `Program.cs`, Rechenkern und Rendering ab `input.json` als unveraenderten Zielvertrag.
2. [PENDING] Dedizierte Import-Schicht innerhalb von `private/Vermietung/nebenkosten-abrechnung` anlegen, getrennt vom bestehenden Laufzeitpfad.
   - Done when: Die Solution enthaelt `src/Nebenkosten.Import` und `tests/Nebenkosten.Import.Tests` oder aequivalente Zuschnitte, die `Nebenkosten.Core` als DTO-/Vertragsreferenz nutzen, ohne `ConsumptionCalculator`, `AllocationCalculator`, `StatementAssembler` oder Rendering fachlich zu aendern.
3. [PENDING] 2025-Scaffold mit Stammdaten und kanonischem Zaehlerregister anlegen.
   - Done when: Unter `private/Vermietung/nebenkosten-abrechnung/data/2025/` existiert ein gepflegtes Scaffold-JSON mit den 2025er Stammdaten und der autoritativen `zaehler[]`-Liste fuer das Matching.
4. [PENDING] Import-CLI-Vertrag und Artefaktlayout festlegen.
   - Done when: Ein reproduzierbarer Aufruf akzeptiert mindestens `--source-dir`, `--scaffold-json`, `--output-dir`, optional `--year`, und schreibt deterministische Artefakte:
     - `input.generated.json`
     - `import-manifest.json`
     - `review-output.json`
     - optionalen Extraktions-Cache je Quelle
5. [PENDING] Deterministische Quellerkennung fuer den 2025er Ordner implementieren.
   - Done when: Der Importpfad kann `Belege/` gegen `Messwerte/` unterscheiden und innerhalb davon mindestens Tibber, generische Einzelbelege, Bundle-PDFs, Ableseprotokolle und ista-Monatswerte klassifizieren; unbekannte Typen fuehren zu expliziten Fehlern.
6. [PENDING] PDF-Extraktion mit native-text-first und OCR-Fallback samt Provenienz implementieren.
   - Done when: Jede Seite bzw. jedes Segment dokumentiert Extraktionsmethode, Vertrauensgrad, Quellseiten und extrahierte Rohkennungen im Manifest.
7. [PENDING] Bundle-Segmentierung fuer `Belege_*.pdf` nach atomarer Seitenregel und konservativer Merge-Logik implementieren.
   - Done when: Logische Einzelbelege haben stabile `source_pages`, Lieferanten-/Datums-/Referenzmetadaten, und unklare Seitengruppen bleiben getrennt plus `review_required`.
8. [PENDING] Internes Normalisierungsmodell fuer Belege, Messwerte, Tarife und Bestandswerte definieren.
   - Done when: Extraktionsdaten werden vor der JSON-Kanonisierung in typisierte interne Datensaetze ueberfuehrt, die Roh-OCR-Werte und kanonische Werte sauber trennen.
9. [PENDING] Beleg-Normalisierung fuer Betrag, Datum, Lieferant, Scope und `kostenart_id` mit Review-Workflow umsetzen.
   - Done when: Die Scope-Prioritaet `Dokumenttext > Dateiname > Domain-Regel` technisch erzwungen wird, unklare `kostenart_id`- oder Scope-Faelle in `review-output.json` landen, und solche Faelle eine operative Finalisierung blockieren.
10. [PENDING] Messwert-Normalisierung fuer beide Quellformate und ista-Monatsverdichtung implementieren.
    - Done when:
      - Zeitraumquellen zu kanonischen `ista_ablese`- oder `ista_monatsmittel`-Eintraegen werden
      - echte Stichtagswerte `manuell` bleiben
      - monatliche ista-Exporte nicht monatlich persistiert werden, sondern je relevantem Zeitraum genau eine kanonische Periodenablesung erzeugen
11. [PENDING] Zaehler-Matching und OCR-Korrektur gegen das Scaffold-`zaehler[]` implementieren.
    - Done when: Kandidatenbildung normalisierte Rohwerte, alphanumerische Varianten, Ziffernvarianten und OCR-Ersatzregeln abdeckt; Auto-Korrektur nur bei genau einem plausiblen Kandidaten greift; Mehrdeutigkeiten oder Fehlmatches fail-fast abbrechen.
12. [PENDING] Tibber-Tarifpfad als eigenen Normalisierungsschritt implementieren.
    - Done when: Jede Tibber-Rechnung genau einen Monats-`stromtarif` je Rechnungsmonat und `be_id` erzeugt, direkte Brutto-Preisfelder Vorrang vor Rueckrechnungen haben, und im Tarifmodus keine direkten Strom-`kostenbelege[]` geschrieben werden.
13. [PENDING] Bestandsabgrenzung und Folgejahres-Uebergang fuer Oel, Holz und Pellets implementieren.
    - Done when: Die Vorverarbeitung
      - positive `Rest aus Vorjahr`-Belege fuer das Zieljahr beruecksichtigen kann
      - Restbestaende per Durchschnittspreis bewertet
      - Holz `Fm -> Rm` normiert
      - laufende Brennstoffkosten auf netto verbrauchte Werte reduziert
      - und den Folgejahres-Uebergang im Manifest bzw. einem Carryover-Artefakt dokumentiert, ohne negative operative `kostenbelege`
14. [PENDING] Kanonisierung in das operative `NebenkostenInput` implementieren.
    - Done when: `input.generated.json` nur vom bestehenden Runtime-Vertrag akzeptierte Felder enthaelt, Provenienz ausserhalb des operativen JSON bleibt, IDs/Namensregeln stabil sind und die Ausgabe durch bestehende DTOs serialisierbar ist.
15. [PENDING] Finalisierungs-Guards implementieren.
    - Done when: Der Importlauf eine operative Freigabe verweigert, solange eines der folgenden Probleme offen ist:
      - fehlendes Scaffold-Zaehlerregister
      - offene Review-Faelle
      - negativer oder unplausibler Verbrauch
      - unsegmentierbares Bundle-PDF
      - Tibber ohne belastbaren Monatszeitraum oder Preisbasis
      - widerspruechliche Brennstoff-Bewertungsbasis
16. [PENDING] Import-spezifische Contract-, Unit- und Regressionstests aufbauen.
    - Done when: Tests mindestens Segmentierung, Scope-Prioritaet, Zaehler-Autokorrektur, ista-Monatsverdichtung, Tibber-Tarifbildung, Bestandsabgrenzung, Manifest-/Review-Output und die Kompatibilitaetsvalidierung ueber den bestehenden `InputValidator` absichern.
17. [PENDING] Reproduzierbaren E2E-Pfad fuer die dokumentierten 2025er Stichproben etablieren.
    - Done when: Ein Test oder ein skriptbarer Fixture-Lauf die in der Spec referenzierten Stichproben fuer Tibber, Monatswerte, `Ablesungen24_25.pdf`, Oel, `Belege_BE1.pdf` und `Belege_Liegenschaft.pdf` auf kanonische Soll-Ergebnisse prueft.
18. [PENDING] Operator-Workflow ohne Aenderung des bestehenden Abrechnungslaufs dokumentieren und absichern.
    - Done when: Die operative Reihenfolge stabil ist:
      - 2025-Scaffold pflegen
      - Import laufen lassen
      - `review-output.json` abarbeiten
      - finale `data/2025/input.json` ablegen
      - bestehende `abrechnung`-CLI unveraendert auf diese finale Eingabe anwenden

## Open Items
- Keine offenen blocking Spec- oder Decision-Punkte fuer diese Planiteration.
- [MISSING NON-BLOCKING] Eine repo-taugliche Ablage fuer sanitisierte 2025er Sample-PDFs existiert noch nicht; bis dahin koennen E2E-Tests mit lokal bereitgestellten Fixtures oder manueller Sample-Zufuhr starten. => die PDFs werden nicht im Repo abgelegt, ich kopiere sie in den Dokumentenordner in OneDrive z.B. '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2025'
- [DECISION NON-BLOCKING] Ob die Import-Schicht als eigener CLI-Entry-Point in derselben Solution oder als separates Hilfsprojekt unter `scripts/` gestartet wird, kann ergonomisch noch verfeinert werden; der Plan geht bis auf Weiteres von einem separaten .NET-Projekt in derselben Solution aus. => keine Präferenz, vielleicht machen wir am Ende auch einen Skill mit enstprechendem Workflow, damit dürfte der Aufbau eh egal sein. Strukturiere es so dass es am einfachsten zu pflegen und weiter zu entwickeln ist.

## Verification Test Cases
1. Given ein vorbereitetes `data/2025/`-Scaffold mit kanonischer `zaehler[]`-Liste, when der Importlauf `Messwerte/Ablesungen24_25.pdf` verarbeitet, then werden OCR-Varianten wie `2108757522` oder `2008222190` nur auf genau einen plausiblen Zielzaehler gemappt oder der Lauf bricht fail-fast ab.
2. Given `Messwerte/Monatswerte - 2025 -  - NE0001(P621593463).pdf`, when die Messwert-Normalisierung laeuft, then bleiben die Geraete `120298189`, `120298011`, `120298110`, `120298127` als getrennte Quellen nachvollziehbar, erzeugen operativ aber nur eine kanonische Periodenablesung je relevantem Zeitraum.
3. Given `Belege/Rechnung_1167054194.pdf`, when Tibber-Tarifbildung laeuft, then entsteht genau ein Monats-`stromtarif` fuer Juni 2025 mit Direktpreis-Prioritaet, ohne direkten Strom-`kostenbeleg`, und die bestehende Validierung akzeptiert den Tarifmodus.
4. Given `Belege/Belege_Liegenschaft.pdf`, when Bundle-Segmentierung und Beleg-Normalisierung laufen, then werden die Seiten in logische Einzelbelege mit erhaltener Provenienz aufgeteilt und unklare Seitengruppen bleiben review-pflichtig statt still zusammenzufliessen.
5. Given ein Beleg, dessen Dateiname auf einen Scope hinweist, dessen Dokumenttext aber einen engeren oder anderen Scope nennt, when Scope-Inferenz laeuft, then gewinnt der Dokumenttext und das Manifest dokumentiert die angewendete Konfliktregel.
6. Given Restbestaende fuer Oel, Holz und Pellets, when die Bestandsabgrenzung laeuft, then werden laufende Brennstoffkosten auf netto verbrauchte Werte reduziert, Holz ueber `1 Fm = 1,5 Rm` normiert, und Folgejahres-Anfangsbestaende als positive Uebergangsartefakte erzeugt, ohne negative operative `kostenbelege`.
7. Given offene Belegklassifikation oder Scope-Mehrdeutigkeit, when der Importlauf endet, then listet `review-output.json` die offenen Faelle und `input.generated.json` wird nicht als operative Finaleingabe freigegeben.
8. Given ein vollstaendig aufgeloester 2025-Importlauf, when die bestehende `abrechnung`-CLI auf der finalen `input.json` gestartet wird, then laufen Validierung, Berechnung und Rendering ohne fachliche Aenderungen in `Nebenkosten.Core` oder `Nebenkosten.Rendering` durch.

## Readiness
- Dieser Plan ist in Iteration 1 implementation-ready: die Spec ist stabil, die Grenze zur bestehenden Anwendung ist klar, und die naechsten ausfuehrbaren Schritte sind konkret.
- Faktisch zuerst zu liefern ist das 2025-Scaffold mit kanonischer `zaehler[]`-Liste; dieses Thema ist hier bereits als explizites Arbeitspaket enthalten und keine offene Spec-Luecke mehr.

# Iteration 2

## Summary
- Die inline im Plan hinterlegten `=>`-Antworten wurden in konkrete Planentscheidungen uebersetzt: 2025er Sample-PDFs bleiben ausserhalb des Repos in OneDrive, und die Import-Schicht wird aus Wartbarkeitsgruenden als eigenes .NET-Projekt in derselben Solution geplant.
- Die zuvor offenen Blocker wurden auf Ausfuehrungsebene geschlossen: Scaffold-Seed, Quellerkennung, Manifest-/Review-Vertrag, Scope-Inferenz, ista-Monatswerte-Kanonisierung und Finalisierungs-Gate sind jetzt algorithmisch beschrieben.
- Der Plan ist mit dieser Iteration nicht nur fachlich, sondern auch auf Ausfuehrungsebene implementation-ready; offene Punkte sind nur noch nicht-blockende Ergonomie- oder Spaeter-Optimierungen.

## Requirements Snapshot
- Reale 2025er PDFs werden nicht ins Repository kopiert; der operative Quellpfad bleibt der OneDrive-Ordner unter `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2025`.
- Repo-Tests muessen deshalb ohne eingecheckte Original-PDFs auskommen: Kernlogik wird mit synthetischen/sanitisierten Text-, OCR- und Segment-Fixtures getestet; ein lokaler E2E-Smoke-Test darf den OneDrive-Ordner direkt verwenden.
- Die Import-Schicht soll so strukturiert werden, dass sie spaeter sowohl als CLI als auch hinter einem Skill/Workflow wiederverwendbar bleibt; deshalb wird ein separates .NET-Projekt in derselben Solution als Standardpfad festgelegt.
- Das 2025er Zaehlerregister bleibt operator-gepflegt und wird nicht aus OCR oder PDFs abgeleitet; die Vorverarbeitung darf nur gegen dieses Register matchen.
- Operative Freigabe heisst: `input.json` existiert nur nach erfolgreichem Finalisierungsschritt ohne offene Review-Faelle; bis dahin bleiben nur Vorstufenartefakte erhalten.

## Current State Snapshot
- [DONE] Der Speicherort der echten 2025er Quell-PDFs ist geklaert: ausserhalb des Repos im OneDrive-Dokumentenordner.
  - Evidence: Nutzerantwort in Iteration 1 Open Items (`=> die PDFs werden nicht im Repo abgelegt ...`)
- [DONE] Die Strukturentscheidung fuer die Import-Schicht ist geklaert: Wartbarkeit und Weiterentwicklung gewinnen vor kurzfristiger Skript-Einfachheit; Standardpfad ist ein eigenes .NET-Projekt in derselben Solution.
  - Evidence: Nutzerantwort in Iteration 1 Open Items (`=> keine Praeferenz ... Strukturiere es so dass es am einfachsten zu pflegen und weiter zu entwickeln ist.`)
- [DONE] Die bestehende .NET-Codebasis bietet mit `Nebenkosten.Core` bereits den stabilen Downstream-Vertrag fuer das operative JSON.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Input/InputDto.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Validation/InputValidator.cs`
- [DONE] 2024-Inputdaten koennen als Seed fuer 2025-Stammdaten und `zaehler[]`-Grundbestand dienen.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/2024/input_tariff_from_excel.json`
- [PENDING] Ein 2025er Scaffold-Template mit initial uebernommenen 2024-Stammdaten und pruefbarer `zaehler[]`-Liste existiert noch nicht.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/` enthaelt aktuell nur `2024/`
- [PENDING] Ein expliziter Artefaktvertrag fuer `import-manifest.json`, `review-output.json`, `carryover-output.json` und den Finalisierungsschritt existiert noch nicht als Code.
  - Evidence: keine Import-Artefakte und kein Import-Projekt unter `src/`
- [PENDING] Es gibt noch keinen Importlauf, der echte OneDrive-Quellen mit reproduzierbaren Contracts verarbeitet.
  - Evidence: keine Import-CLI, keine Import-Tests, kein `data/2025/`

## Action Plan
1. [DONE] Import-Schicht als eigenstaendiges .NET-Arbeitspaket in derselben Solution festlegen.
   - Done signal: Kein `scripts/`-only Pfad ist mehr Planannahme; die Standardarchitektur bleibt skill-/workflow-kompatibel und direkt testbar.
2. [PENDING] 2025-Scaffold-Template und Ownership explizit festlegen.
   - Done when: Unter `private/Vermietung/nebenkosten-abrechnung/data/2025/` existieren mindestens:
     - `scaffold.template.json` als aus 2024 abgeleitete Vorlage
     - `scaffold.json` als operator-gepflegte Arbeitsdatei fuer 2025
   - Done when: `scaffold.template.json` initial aus `data/2024/input_tariff_from_excel.json` seeded wird, mindestens fuer:
     - Objekt-/BE-/NE-Stammdaten
     - vorhandene `zaehler[]`
     - bekannte feste Zuordnungen `zaehler -> ne_id|be_id|objektweit`
   - Done when: Der Plan festlegt, dass neue oder geaenderte 2025-Zaehler ausschliesslich manuell in `scaffold.json` gepflegt werden, bevor Matching laeuft.
3. [PENDING] Import-Projektstruktur und Kerninterfaces definieren.
   - Done when: Die Solution zusaetzlich mindestens diese Projekte oder aequivalente Zuschnitte fuehrt:
     - `src/Nebenkosten.Import` fuer Orchestrierung, CLI, Artefaktpersistenz
     - `src/Nebenkosten.Import.Core` oder aequivalente interne Namespaces fuer Extraktion, Segmentierung, Normalisierung und Matching
     - `tests/Nebenkosten.Import.Tests` fuer Unit-, Contract- und lokalen Smoke-Test
   - Done when: Provider-Interfaces fuer `IPdfTextExtractor`, `IOcrProvider`, `ISourceClassifier`, `IBundleSegmenter`, `IMeterMatcher` und `IImportFinalizer` oder aequivalente Bausteine festgelegt sind.
4. [PENDING] Artefaktvertrag der Import-Schicht final festlegen.
   - Done when: Der Importlauf genau diese Dateien im Zielordner verwendet:
     - `input.generated.json` als maschinell erzeugter, noch nicht final freigegebener Operativ-Entwurf
     - `import-manifest.json` als vollstaendige Provenienz- und Laufdokumentation
     - `review-output.json` nur wenn offene manuelle Zuordnungen bestehen
     - `carryover-output.json` fuer Restbestand/`Rest aus Vorjahr` und Folgejahres-Uebergang
     - `input.json` nur nach erfolgreicher Finalisierung ohne offene Review-Faelle
   - Done when: `import-manifest.json` mindestens folgende Top-Level-Struktur fuehrt:
     - `run`
     - `sources[]`
     - `outputs[]`
     - `summary`
   - Done when: jede `sources[]`-Position mindestens diese Felder fuehrt:
     - `source_path`
     - `source_pages`
     - `document_type`
     - `extraction_method`
     - `confidence`
     - `raw_identifiers`
     - `canonical_identifiers`
     - `scope_inference`
     - `auto_corrections`
     - `review_required`
     - `review_reason`
     - `output_entity_type`
     - `output_entity_id`
5. [PENDING] Quellerkennung als expliziten, testbaren Entscheidungsbaum implementieren.
   - Done when: Die Klassifikation in genau dieser Reihenfolge prueft:
     1. Dateiname/Seitentitel enthaelt `Monatswerte` -> `ista_monthly_export`
     2. Dateiname/Seitentitel enthaelt `Ablesungen` oder `Ablesequittung` -> `ista_period_or_snapshot`
     3. Dateiname passt auf `Belege_*.pdf` -> `bundle_belege`
     4. extrahierter Text enthaelt `Tibber` oder tibber-typische Kennungen wie `1ISK` -> `tibber_invoice`
     5. sonst `generic_invoice`
   - Done when: `generic_invoice` nur fuer Einzelbelege ohne Bundle-Merkmale verwendet wird; unklare oder widerspruechliche Faelle werden nicht blind klassifiziert, sondern mit `review_required = true` im Manifest gekennzeichnet.
   - Done when: Alle sechs in der Spec genannten 2025er Stichproben je einem erwarteten `document_type` zugeordnet und als Contract-Test abgesichert sind.
6. [PENDING] PDF-Extraktionspfad mit providerbasierter OCR-Strategie implementieren.
   - Done when: Die Extraktion immer zuerst nativen Text versucht und nur seitenweise auf OCR faellt, wenn der native Text leer oder fachlich unbrauchbar ist.
   - Done when: Erste Implementierung fuer OCR auf dem lokalen Darwin-Setup macOS Vision als Provider nutzt, aber ueber `IOcrProvider` austauschbar bleibt.
   - Done when: `import-manifest.json` fuer jede Seite den tatsaechlich verwendeten Pfad (`native_text`, `ocr_vision`) dokumentiert.
7. [PENDING] Bundle-Segmentierung als deterministischen Mehrschrittalgorithmus implementieren.
   - Done when: Die atomare Grundeinheit zunaechst immer die einzelne Seite ist.
   - Done when: Seiten nur dann zusammengefuehrt werden, wenn mindestens eines der folgenden Merkmale uebereinstimmt:
     - identische Rechnungs- oder Vertragsnummer
     - expliziter Fortsetzungsvermerk (`Seite x/y`, `Fortsetzung`)
     - identischer Briefkopf plus gleiches Rechnungsdatum plus keine neue Rechnungskennung auf der Folgeseite
   - Done when: Das Auftreten einer neuen Rechnungskennung auf einer Folgeseite immer einen Segmentbruch erzwingt.
   - Done when: Unklare Nachbarschaftspaare nicht gemerged, sondern als getrennte Segmente mit `review_required = true` ausgegeben werden.
8. [PENDING] Scope-Inferenz als geordneten Algorithmus implementieren.
   - Done when: Scope-Ermittlung in genau diesen Schritten erfolgt:
     1. Dokumenttext auf explizite BE-/NE-/Objekt-Hinweise scannen
     2. Dateiname auf explizite Hinweise wie `BE1`, `BE2`, `Liegenschaft` scannen
     3. Domain-Regel aus Kostenart-/Objektwissen nur anwenden, wenn 1 und 2 leer bleiben
   - Done when: Bei Konflikt immer `Dokumenttext > Dateiname > Domain-Regel` gilt.
   - Done when: Das Manifest pro Entscheidung `detected_from`, `candidates`, `winner`, `conflict_resolved` oder aequivalente Felder fuehrt.
   - Done when: Wenn weder Text noch Dateiname eindeutig sind und die Domain-Regel mehrere plausible Scopes offenlaesst, kein stiller Default entsteht, sondern `review_required = true`.
9. [PENDING] Belegnormalisierung inkl. Kostenartzuordnung und Review-Output operationalisieren.
   - Done when: `review-output.json` mindestens diese Felder pro offenem Fall fuehrt:
     - `source_path`
     - `source_pages`
     - `document_type`
     - `review_reason`
     - `beschreibung`
     - optional `proposed_kostenart_id`
     - optional `proposed_scope`
   - Done when: Der Importlauf fuer offene Belege nur Platzhalter im Manifest, aber keine finale operative Freigabe erzeugt.
10. [PENDING] Kanonische Ausgabeform fuer `ista`-Monatswerte verbindlich festlegen und implementieren.
    - Done when: Fuer jeden Zaehler aus einem `ista_monthly_export` genau ein operativer `AblesungDto` entsteht.
    - Done when: Dieser Datensatz mindestens so gebildet wird:
      - `quelle = "ista_monatsmittel"` oder `quelle = "ista_ablese"` gemaess Dokumenttyp/Legende
      - `periode.von = fruehestes fachlich belastbares Datum der Dokumentperiode`
      - `periode.bis = spaetestes fachlich belastbares Datum der Dokumentperiode`
      - `messwert_alt = erster belastbarer Anfangswert (AN oder VJ gemaess Legende)`
      - `messwert_neu = letzter belastbarer End-/Stichtagswert (ST gemaess Legende)`
    - Done when: Die Kanonisierung nie 12 Monatszeilen 1:1 in operative `ablesungen[]` schreibt.
    - Done when: Fuer unvollstaendige oder widerspruechliche Legenden-/Wertlagen ein fail-fast oder `review_required`-Pfad explizit getestet ist.
11. [PENDING] Zaehler-Matching und OCR-Korrektur auf Kandidatenebene implementieren.
    - Done when: Pro erkannter Zaehlerkennung mindestens diese Varianten gegen `scaffold.json` gebildet werden:
      - Rohtext
      - alphanumerisch normalisiert
      - nur Ziffern
      - OCR-normalisiert (`O->0`, `I/l->1`, `S->5`, Satzzeichen/Leerzeichen entfernt)
    - Done when: Auto-Korrektur nur dann greift, wenn genau ein Kandidat nach Nummer, Zaehlertyp und Scope plausibel bleibt.
    - Done when: Mehrdeutigkeit oder Nulltreffer den Lauf mit explizitem Fehler abbrechen.
12. [PENDING] Tibber-Tarifbildung inklusive Nicht-Standardfaellen implementieren.
    - Done when: Standardfall `ein Rechnungslauf = ein Kalendermonat = ein Stromtarif` gilt.
    - Done when: Direkte Brutto-Preisangaben pro `kWh` Vorrang vor Rueckrechnungen haben, und periodische Brutto-Fixkosten Vorrang fuer den Grundpreis haben.
    - Done when: Nicht-Standardfaelle wie Teilmonat, mehrmonatige Periode oder mehrere Preiszonen im Dokument nicht still geglaettet, sondern dokumentiert werden:
      - wenn sauber auf einen Monatsmittelwert verdichtbar -> Manifest dokumentiert Herleitung
      - wenn nicht belastbar -> `review_required = true`
    - Done when: Im Ergebnis niemals direkte Strom-`kostenbelege[]` parallel zu `stromtarife[]` entstehen.
13. [PENDING] Bestandsabgrenzung als eigenes Carryover-Artefakt konkretisieren.
    - Done when: `carryover-output.json` mindestens je Energietraeger und BE fuehrt:
      - `anfangsbestand_menge`
      - `anfangsbestand_wert`
      - `zugaenge_menge`
      - `zugaenge_wert`
      - `restmenge_jahresende`
      - `restwert_jahresende`
      - `brennstoffkosten_laufendes_jahr`
      - `next_year_opening_entry`
    - Done when: Die operative `input.generated.json` nur die netto verbrauchten Brennstoffkosten enthaelt und das Folgejahres-Opening als eigener strukturierter Output vorliegt.
14. [PENDING] Finalisierungs-Gate als zweistufigen Workflow implementieren.
    - Done when: `import build` oder aequivalenter Erstlauf immer `input.generated.json` plus Manifest und optionalen Review-Output schreibt, aber niemals ungeprueft `input.json`.
    - Done when: `input.json` nur ueber einen expliziten Finalisierungsschritt entsteht, der
      - ein operatorisch ueberarbeitetes Kandidat-JSON entgegennimmt
      - gegen `InputValidator` validiert
      - prueft, dass keine offenen `review_required`-Faelle mehr uebrig sind
      - und erst dann `input.json` schreibt
    - Done when: Solange `review-output.json` nicht leer ist oder der Kandidat die offenen Faelle nicht aufloest, der Finalisierungsschritt mit eindeutigem Fehler abbricht.
15. [PENDING] Handoff in den bestehenden Abrechnungslauf technisch absichern.
    - Done when: Ein erfolgreicher Finalisierungslauf die finale Datei exakt dort ablegt, wo der bestehende CLI-Pfad sie nutzen kann, ohne Aenderungen an `Nebenkosten.Cli/Program.cs`.
    - Done when: Ein negativer Test bestaetigt, dass `input.generated.json` ohne Finalisierung nicht als operative Datei missverstanden wird.
16. [PENDING] Teststrategie in Repo-Tests und lokalen Smoke-Test aufteilen.
    - Done when: Repo-Tests mindestens folgende Kategorien fuehren:
      - Source classification tests
      - Bundle segmentation tests
      - Scope inference tests
      - Meter matching tests
      - Tibber tariff derivation tests
      - Carryover calculation tests
      - Finalization gate tests
    - Done when: Lokaler Smoke-Test optional den echten OneDrive-Ordner verwendet, aber nicht fuer gruene Repo-Tests vorausgesetzt wird.
17. [PENDING] Operator-Workflow als ausfuehrbare Reihenfolge abschliessen.
    - Done when: Der Betriebsablauf dokumentiert und testbar ist als:
      1. `scaffold.template.json` aus 2024 erzeugen
      2. `scaffold.json` fachlich fuer 2025 pflegen
      3. Import-Build gegen OneDrive-Quelle laufen lassen
      4. `review-output.json` und `carryover-output.json` auswerten
      5. Kandidat-JSON manuell vervollstaendigen
      6. Finalisierung laufen lassen
      7. bestehende `abrechnung`-CLI gegen finale `input.json` starten

## Open Items
- Keine offenen blocking Spec-, Decision- oder Ausfuehrungsluecken fuer die naechste Implementierung.
- [NON-BLOCKING] Ein spaeterer Skill-/Workflow-Wrapper kann auf der Import-CLI aufsetzen; das ist bewusst kein Startblocker fuer die erste Implementierung.

## Verification Test Cases
1. Given `data/2024/input_tariff_from_excel.json`, when das 2025-Scaffold-Template erzeugt wird, then entsteht ein `scaffold.template.json` mit uebernommenen Stammdaten und `zaehler[]`, aber ohne automatisch erfundene neue 2025-Zaehler.
2. Given die sechs in der Spec referenzierten 2025er Stichproben, when die Quellerkennung laeuft, then wird jede Datei deterministisch einem erwarteten `document_type` zugeordnet oder explizit als Review-Fall markiert.
3. Given ein `bundle_belege` mit drei Seiten und einer neuen Rechnungskennung auf Seite 3, when Segmentierung laeuft, then entstehen zwei Segmente und die dritte Seite wird nicht in das erste Segment gemerged.
4. Given ein Beleg mit `BE1` im Dateinamen, aber `BE2` im Dokumenttext, when Scope-Inferenz laeuft, then gewinnt `BE2`, und das Manifest protokolliert die Konfliktaufloesung.
5. Given ein `ista_monthly_export` mit AN/VJ/ST-Legende, when Kanonisierung laeuft, then entsteht genau ein operativer `AblesungDto` pro Zaehler mit `periode`, `messwert_alt` und `messwert_neu`, aber keine 12 Monatszeilen im finalen JSON.
6. Given `Ablesungen24_25.pdf` und ein passendes `scaffold.json`, when Zaehler-Matching laeuft, then werden OCR-Drifts wie `2108757522 -> 210875752` nur bei eindeutigem Einzelkandidaten auto-korrigiert; Mehrdeutigkeiten brechen fail-fast ab.
7. Given eine Tibber-Rechnung fuer einen vollen Kalendermonat, when Tarifbildung laeuft, then entsteht genau ein Monats-`stromtarif`; Given ein nicht belastbarer Teilmonats- oder Mehrzonenfall, when Tarifbildung laeuft, then wird kein still geratener Tarif geschrieben, sondern Review oder Fehler erzeugt.
8. Given Restbestand fuer Oel, Holz in `Fm` und Pellets, when Carryover-Berechnung laeuft, then enthaelt `carryover-output.json` die normierten Mengen und Werte, und `input.generated.json` bleibt frei von negativen operativen `kostenbelege`.
9. Given ein Importlauf mit offenen Review-Faellen, when nur der Build-Schritt laeuft, then entstehen `input.generated.json` und `review-output.json`, aber keine finale `input.json`.
10. Given ein operatorisch vervollstaendigtes Kandidat-JSON ohne offene Review-Faelle, when der Finalisierungsschritt laeuft, then wird `input.json` geschrieben und vom bestehenden `InputValidator` akzeptiert.

## Readiness
- Der Plan ist in Iteration 2 implementation-ready: keine offenen blocking Spec- oder Ausfuehrungsluecken, klare Projektstruktur, klarer Artefaktvertrag und klarer Operator-Workflow.
- Die ersten direkt umsetzbaren Schritte sind jetzt eindeutig: `scaffold.template.json` definieren, Import-Projekt anlegen, Artefaktvertrag coden, Quellerkennung/Extraktion als erste testbare Pipeline aufbauen.

# Iteration 3

## Summary
- Der Plan wurde um die fehlende Klarstellung geschaerft, dass die 2025er Anfangsbestaende bzw. `Rest aus Vorjahr` fachlich **aus dem Abschluss 2024** herzuleiten sind und nicht erst isoliert aus 2025er Belegen entstehen.
- Damit ist die Bruecke zwischen altem und neuem Abrechnungsjahr jetzt explizit: 2024 liefert den normativen Carryover-Ausgangszustand, 2025 konsumiert diesen als Opening-Entries.
- Die Readiness bleibt erhalten; geaendert wurde nicht die Architektur, sondern die explizite Reihenfolge und Herkunft der Restwerte.

## Requirements Snapshot
- Die 2025er `Rest aus Vorjahr`-Werte fuer Oel, Holz und Pellets muessen aus der **finalen 2024er Abrechnung bzw. deren Carryover-Berechnung** stammen.
- Massgeblich ist nicht irgendein heuristisch aus 2025 rekonstruiertes Opening, sondern der 2024er Jahresabschluss mit:
  - Restmenge zum 31.12.2024
  - Restwert zum 31.12.2024
  - zugehoerigem Energietraeger
  - zugehoeriger Berechnungseinheit
- Falls 2024 noch keine belastbare Carryover-Berechnung vorliegt, ist dies kein still auffuellbarer Importfall, sondern ein vorgelagerter Pflichtschritt vor der Finalisierung von 2025.

## Current State Snapshot
- [DONE] Die Spec fordert bereits fachlich, dass der Restbestand des Vorjahres als `Rest aus Vorjahr` in das Folgejahr uebernommen wird.
  - Evidence: `../_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md` Abschnitt `Edgecases: Restbestand, Rest aus Vorjahr, Festmeter und Raummeter`
- [DONE] Der Plan adressiert Carryover bereits als eigenes Artefakt und Operator-Schritt.
  - Evidence: Iteration 2, Action 13 (`carryover-output.json`) und Action 17 Schritt 4
- [PENDING] Bislang war noch nicht explizit genug festgelegt, dass die 2025-Opening-Werte aus dem **finalen 2024er Ergebnis** zu seeden sind.
  - Evidence: Iteration 2 sprach von 2024 als Seed fuer Stammdaten und `zaehler[]`, aber noch nicht explizit als normative Quelle fuer 2025-Opening-Werte.

## Action Plan
1. [DONE] Carryover als eigenes Arbeitsobjekt zwischen 2024 und 2025 festgeschrieben.
   - Done signal: Iteration 2 fuehrt bereits `carryover-output.json` als verpflichtendes Import-Artefakt.
2. [PENDING] 2024-zu-2025-Carryover-Seed explizit in den Scaffold- und Finalisierungsfluss einbauen.
   - Done when: `scaffold.template.json` fuer 2025 nicht nur Stammdaten und `zaehler[]`, sondern auch einen dedizierten Abschnitt oder begleitenden Input fuer erwartete Opening-Werte aus 2024 referenziert.
   - Done when: Der Seed fuer diese Opening-Werte aus einem **finalen 2024-Artefakt** kommt, bevorzugt aus:
     - einem vorhandenen 2024-`carryover-output.json`, falls bereits verfuegbar, oder
     - einer reproduzierbaren 2024-Carryover-Berechnung auf Basis der finalen 2024er operativen Eingabe und dokumentierten 2024-Restmengen
3. [PENDING] Eigenen vorgelagerten Arbeitsschritt `2024 Carryover berechnen/validieren` im Operator-Workflow fest verankern.
   - Done when: Vor jedem 2025-Importlauf klar ist, dass zuerst einer dieser Zustaende erreicht sein muss:
     - belastbares 2024-Carryover-Artefakt liegt vor, oder
     - der Importlauf erstellt dieses 2024-Carryover-Artefakt zuerst aus den 2024-Daten
   - Done when: Ohne diesen Zustand keine operative Finalisierung von `data/2025/input.json` moeglich ist.
4. [PENDING] 2025-Opening-Entries deterministisch aus 2024-Carryover uebernehmen.
   - Done when: Fuer jeden Energietraeger/BE mit 2024-Restwert genau ein passender 2025-Opening-Eintrag entsteht oder vorbereitet wird:
     - `beschreibung = "Rest aus Vorjahr ..."`
     - korrekter `scope`
     - Betrag exakt gleich dem 2024er `restwert_jahresende`
   - Done when: Ein Konflikt zwischen 2024-Carryover und 2025er manueller Pflege nicht still ueberschrieben wird, sondern als Review- oder Fail-fast-Fall sichtbar wird.
5. [PENDING] Test- und Artefaktvertrag fuer den Jahresuebergang ergaenzen.
   - Done when: Repo-Tests explizit absichern:
     - 2024-Restwert -> 2025-Opening-Wert
     - fehlender 2024-Carryover -> kein finales 2025-`input.json`
     - abweichender manuell gepflegter 2025-Opening-Wert -> Review/Fail-fast
   - Done when: `carryover-output.json` die Herkunft des Opening-Werts dokumentiert, z. B. mit `source_year = 2024`.
6. [PENDING] Operator-Workflow um die Jahresgrenze herum korrigieren.
   - Done when: Die dokumentierte Reihenfolge mindestens lautet:
     1. 2024-Carryover berechnen oder bestaetigen
     2. `scaffold.template.json` / `scaffold.json` fuer 2025 vorbereiten
     3. 2025-Import-Build laufen lassen
     4. `review-output.json` und `carryover-output.json` gegen 2024 plausibilisieren
     5. Kandidat-JSON vervollstaendigen
     6. Finalisierung laufen lassen
     7. bestehende `abrechnung`-CLI gegen finale `input.json` starten

## Open Items
- Keine offenen blocking Spec-Luecken.
- [NON-BLOCKING] Falls spaeter ein automatischer Mehrjahres-Workflow entsteht, kann die 2024->2025-Carryover-Erzeugung als eigener Subcommand oder Skill-Schritt gekapselt werden; fuer die Erstumsetzung reicht die jetzt festgelegte explizite Reihenfolge.

## Verification Test Cases
1. Given ein finales 2024-Carryover-Artefakt mit `restwert_jahresende` fuer Oel, Holz und Pellets, when das 2025-Scaffold bzw. der 2025-Import vorbereitet wird, then werden daraus die erwarteten 2025-Opening-Werte `Rest aus Vorjahr` abgeleitet.
2. Given 2024-Daten ohne bestaetigten Carryover-Ausgangszustand, when der 2025-Finalisierungsschritt gestartet wird, then bricht er ab und verlangt zuerst die Berechnung bzw. Bestaetigung des 2024-Carryovers.
3. Given ein 2024-Restwert von X EUR und ein manuell gepflegter 2025-Opening-Wert von Y EUR fuer denselben Energietraeger und dieselbe BE, when Finalisierung laeuft, then wird die Abweichung nicht still akzeptiert, sondern als Review- oder Fail-fast-Fall ausgewiesen.

## Readiness
- Ja: Der Plan bleibt implementation-ready, und der Jahresuebergang 2024 -> 2025 ist jetzt explizit und operativ ausreichend beschrieben.
- Fuer die Umsetzung bedeutet das praktisch: Die ersten Schritte beginnen nicht direkt mit 2025-PDF-OCR, sondern mit der belastbaren Ableitung bzw. Bestaetigung der 2024er Carryover-Werte.

# Iteration 4

## Summary
- Diese Iteration ist der **in sich geschlossene Umsetzungsplan**. Fuer die Implementierung soll sie allein ausreichen; Iteration 1-3 bleiben nur historische Herleitung.
- Der volle Funktionsumfang wird in drei klar getrennte, spaeter separat nutzbare Funktionsbloecke geschnitten:
  1. `derive-opening-carryover` fuer `Rest aus Vorjahr` aus dem finalen Vorjahresstand
  2. `build-year-input` fuer Belege + Messwerte -> `input.generated.json` / `input.json`
  3. `derive-next-year-carryover` fuer den Uebergang in das Folgejahr
- Die Trennung dient Testbarkeit, Mehrjahresfaehigkeit und spaeterer Workflow-/Skill-Integration, ohne den bestehenden Rechenkern ab `input.json` anzutasten.

## Requirements Snapshot
- Die 2025er operative `input.json` muss aus drei fachlichen Quellen zusammengesetzt werden:
  - Vorjahres-Carryover (`Rest aus Vorjahr`) aus 2024
  - 2025er Belege und Messwerte
  - 2025er Jahresend-Carryover fuer 2026 als separater Output
- Die bestehende Anwendung unter `private/Vermietung/nebenkosten-abrechnung` bleibt ab Einlesen der finalen `input.json` fachlich unveraendert.
- Das kanonische Zaehlerregister fuer 2025 ist operator-gepflegt; aus OCR, Belegen oder Messwerten werden keine neuen Zaehler erzeugt.
- Bundle-PDFs, OCR, Scope-Inferenz, Tibber-Tarife, ista-Monatswerte und Review-Output muessen in der Vorverarbeitung geloest werden, nicht im Rechenkern.
- Restbestandslogik gilt je Energietraeger und Berechnungseinheit; Holz wird normativ mit `1 Fm = 1,5 Rm` in `Rm` normalisiert.
- Solange offene Review-Faelle oder ein fehlender/unklarer Vorjahres-Carryover bestehen, darf kein finales `input.json` fuer 2025 freigegeben werden.
- Echte 2025er PDFs bleiben ausserhalb des Repos im OneDrive-Ordner; Repo-Tests muessen ohne eingecheckte Original-PDFs auskommen.

## Current State Snapshot
- [DONE] Die fachliche Spec fuer Import/Vorverarbeitung und die Hauptspec sind stabil und konsistent.
  - Evidence: `../_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
  - Evidence: `../_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
- [DONE] Der bestehende Downstream-Vertrag fuer operative JSONs ist vorhanden.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Input/InputDto.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Validation/InputValidator.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Cli/Program.cs`
- [DONE] 2024-Daten koennen als Seed fuer 2025-Stammdaten und als fachliche Ausgangsbasis fuer den Vorjahres-Carryover dienen.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/2024/input_tariff_from_excel.json`
- [PENDING] Ein dediziertes Import-/Carryover-Projekt mit stabilen Artefakten existiert noch nicht.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/` enthaelt aktuell nur `Nebenkosten.Cli`, `Nebenkosten.Core`, `Nebenkosten.Rendering`
- [PENDING] `data/2025/` mit `scaffold.template.json`, `scaffold.json`, Opening-Carryover und finaler `input.json` existiert noch nicht.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/` enthaelt aktuell nur `2024/`
- [PENDING] Eine belastbare 2024->2025-Caryover-Ableitung ist noch nicht als eigener wiederverwendbarer Schritt formalisiert.
  - Evidence: kein separates Carryover-Artefakt und kein dedizierter Import-/Carryover-Command vorhanden

## Action Plan
1. [DONE] Downstream-Grenze festschreiben: alles ab finaler `input.json` bleibt unveraendert.
   - Done signal: Die Implementierung arbeitet ausschliesslich in vorgelagerten Import-/Carryover-Schritten; `Nebenkosten.Core`, `Nebenkosten.Cli` und `Nebenkosten.Rendering` werden nicht fuer Importlogik erweitert.
2. [PENDING] Import-/Carryover-Schicht als eigenstaendige .NET-Projekte in derselben Solution anlegen.
   - Done when: Die Solution mindestens diese Zuschnitte fuehrt:
     - `src/Nebenkosten.Import` fuer `build-year-input` und Finalisierung
     - `src/Nebenkosten.Carryover` fuer `derive-opening-carryover` und `derive-next-year-carryover`
     - `tests/Nebenkosten.Import.Tests` fuer Contract-, Unit- und Smoke-Tests
   - Done when: Die Kernbausteine ueber klare Interfaces getrennt sind (`IPdfTextExtractor`, `IOcrProvider`, `ISourceClassifier`, `IBundleSegmenter`, `IMeterMatcher`, `ICarryoverCalculator`, `IImportFinalizer` oder aequivalent).
3. [PENDING] `derive-opening-carryover` als eigenstaendigen Schritt fuer 2024 -> 2025 implementieren.
   - Done when: Der Schritt als Eingabe mindestens die finale 2024er operative Eingabe plus 2024er Restmengen-/Bewertungsbasis oder ein vorhandenes 2024-`carryover-output.json` akzeptiert.
   - Done when: Der Schritt als Output ein maschinelles Artefakt fuer 2025-Opening-Werte erzeugt, mindestens mit:
     - `source_year = 2024`
     - `target_year = 2025`
     - `energietraeger`
     - `be_id`
     - `restmenge_jahresende`
     - `restwert_jahresende`
     - `opening_kostenbeleg`
   - Done when: Fehlende oder widerspruechliche 2024-Bewertungsbasis fail-fast abbricht.
4. [PENDING] 2025-Scaffold aus 2024 seeden und operatorisch pflegbar machen.
   - Done when: Unter `data/2025/` mindestens entstehen:
     - `scaffold.template.json` aus 2024-Stammdaten und 2024-`zaehler[]`
     - `scaffold.json` als operator-gepflegte Arbeitsdatei fuer 2025
   - Done when: Das Scaffold die 2025er kanonische `zaehler[]`-Liste, feste Zuordnungen und erwartete Opening-Carryover-Referenzen fuehrt.
5. [PENDING] `build-year-input` als eigenstaendigen Schritt fuer 2025-Belege und -Messwerte implementieren.
   - Done when: Der Schritt mindestens diese Eingaben akzeptiert:
     - `--source-dir` fuer den OneDrive-2025-Ordner
     - `--scaffold-json`
     - `--opening-carryover`
     - `--output-dir`
   - Done when: Der Schritt genau diese Artefakte schreibt:
     - `input.generated.json`
     - `import-manifest.json`
     - `review-output.json` nur bei offenen Faellen
   - Done when: `input.generated.json` bereits die aus 2024 uebernommenen Opening-Werte enthaelt.
6. [PENDING] Quellerkennung, Extraktion und Segmentierung fuer `build-year-input` deterministisch implementieren.
   - Done when: Quellerkennung mindestens die Typen `ista_monthly_export`, `ista_period_or_snapshot`, `bundle_belege`, `tibber_invoice`, `generic_invoice` unterscheidet.
   - Done when: Native Text zuerst verwendet wird und nur bei unbrauchbarem/leerem Text OCR faellt; auf Darwin wird initial macOS Vision genutzt.
   - Done when: Bundle-Segmentierung seitenbasiert startet und nur unter den in der Spec genannten Merge-Regeln Seiten zusammenfuehrt.
7. [PENDING] Normalisierung fuer Belege, Messwerte und Tarife in `build-year-input` umsetzen.
   - Done when: Scope-Inferenz strikt `Dokumenttext > Dateiname > Domain-Regel` folgt und im Manifest dokumentiert wird.
   - Done when: `ista`-Monatswerte auf genau eine kanonische Periodenablesung pro Zaehler und relevantem Zeitraum verdichtet werden.
   - Done when: Tibber-Rechnungen genau einen Monats-`stromtarif` je belastbarem Rechnungsmonat erzeugen und nie als direkte Strom-`kostenbelege[]` importiert werden.
8. [PENDING] Zaehler-Matching gegen das operator-gepflegte 2025-Scaffold implementieren.
   - Done when: Kandidatenbildung mindestens Rohtext, alphanumerisch normalisiert, nur Ziffern und OCR-normalisierte Varianten prueft.
   - Done when: Auto-Korrektur nur bei genau einem plausiblen Kandidaten nach Nummer, Typ und Scope greift; sonst Fehler oder Review.
9. [PENDING] Finalisierungs-Gate fuer 2025 implementieren.
   - Done when: `build-year-input` niemals direkt `input.json` schreibt.
   - Done when: Ein expliziter Finalisierungsschritt nur dann `data/2025/input.json` erzeugt, wenn:
     - kein offener Review-Fall mehr besteht
     - der Opening-Carryover fuer 2025 vorhanden und plausibel ist
     - das Ergebnis den bestehenden `InputValidator` passiert
   - Done when: `input.generated.json` nicht versehentlich als produktive Eingabe verwendet werden kann.
10. [PENDING] `derive-next-year-carryover` als eigenstaendigen Schritt fuer 2025 -> 2026 implementieren.
    - Done when: Der Schritt als Eingabe mindestens die finale 2025-`input.json` plus 2025-Restmengen-/Bewertungsbasis akzeptiert.
    - Done when: Der Schritt ein `carryover-output.json` fuer 2026 erzeugt, mindestens mit:
      - `source_year = 2025`
      - `target_year = 2026`
      - `energietraeger`
      - `be_id`
      - `restmenge_jahresende`
      - `restwert_jahresende`
      - `opening_kostenbeleg`
    - Done when: Die operative 2025-`input.json` frei von negativen operativen `kostenbelege` bleibt.
11. [PENDING] Den End-to-End Operator-Workflow als zusammenhaengenden Jahresprozess dokumentieren und absichern.
    - Done when: Der dokumentierte Ablauf mindestens lautet:
      1. `derive-opening-carryover` fuer 2024 -> 2025 ausfuehren oder bestaetigtes 2024-Artefakt bereitstellen
      2. `scaffold.template.json` / `scaffold.json` fuer 2025 pflegen
      3. `build-year-input` gegen den 2025-OneDrive-Ordner ausfuehren
      4. `review-output.json` manuell abarbeiten
      5. Finalisierung zu `data/2025/input.json` ausfuehren
      6. bestehende `abrechnung`-CLI gegen finale `input.json` laufen lassen
      7. `derive-next-year-carryover` fuer 2025 -> 2026 ausfuehren
12. [PENDING] Testsuite an den drei getrennten Funktionsbloecken ausrichten.
    - Done when: Repo-Tests mindestens getrennte Gruppen haben fuer:
      - opening carryover derivation
      - year input build (Klassifikation, OCR-Fallback, Segmentierung, Scope, Matching, Tibber, ista-Kanonisierung)
      - finalization gate
      - next-year carryover derivation
    - Done when: Ein lokaler Smoke-Test optional den echten OneDrive-Ordner nutzt, aber nicht fuer gruene Repo-Tests vorausgesetzt wird.

## Open Items
- Keine offenen blocking Spec- oder Planluecken fuer diese Iteration.
- [NON-BLOCKING] Die drei Funktionsbloecke koennen spaeter als CLI-Commands, API-Endpunkte oder Skill-Schritte exponiert werden; fuer die erste Umsetzung ist nur die interne Trennung normativ wichtig.

## Verification Test Cases
1. Given eine finale 2024-Eingabe und belastbare 2024-Restmengen, when `derive-opening-carryover` laeuft, then entsteht ein 2025-Opening-Artefakt mit `source_year = 2024` und den erwarteten `Rest aus Vorjahr`-Werten je Energietraeger/BE.
2. Given ein fehlender oder widerspruechlicher 2024-Caryover-Ausgangszustand, when `derive-opening-carryover` oder die 2025-Finalisierung laeuft, then bricht der Lauf fail-fast ab und gibt keine finale 2025-`input.json` frei.
3. Given ein gepflegtes `scaffold.json`, Opening-Carryover und den 2025-OneDrive-Ordner, when `build-year-input` laeuft, then entstehen `input.generated.json`, `import-manifest.json` und bei Bedarf `review-output.json`, aber niemals direkt `input.json`.
4. Given ein Bundle-PDF und ein Konflikt zwischen Dateiname und Dokumenttext, when `build-year-input` laeuft, then wird nach den Spec-Regeln segmentiert und der Scope nach `Dokumenttext > Dateiname > Domain-Regel` aufgeloest.
5. Given ein `ista_monthly_export`, when `build-year-input` laeuft, then entsteht pro Zaehler genau eine kanonische operative Periodenablesung und keine 1:1-Uebernahme aller Monatszeilen.
6. Given eine Tibber-Rechnung fuer einen belastbaren Monatszeitraum, when `build-year-input` laeuft, then entsteht genau ein Monats-`stromtarif` und kein direkter Strom-`kostenbeleg`.
7. Given offene Review-Faelle, when der Finalisierungsschritt fuer 2025 gestartet wird, then wird keine finale `data/2025/input.json` geschrieben.
8. Given eine finalisierte `data/2025/input.json` und belastbare 2025-Restmengen, when `derive-next-year-carryover` laeuft, then entsteht ein 2026-Opening-Artefakt mit den erwarteten Restwerten, ohne die finale 2025-`input.json` nachtraeglich zu verbiegen.

## Readiness
- Diese Iteration ist implementation-ready und **alleinstehend ausfuehrbar**. Fuer die Umsetzung des vollen Funktionsumfangs muss nicht auf fruehere Iterationen zurueckgegriffen werden.
- Der empfohlene Startpunkt ist jetzt klar: zuerst `derive-opening-carryover`, dann `build-year-input`, danach Finalisierung und anschliessend `derive-next-year-carryover`.

# Iteration 5

## Summary
- Diese Iteration ersetzt Iteration 4 als **auszufuehrenden, in sich geschlossenen Umsetzungsplan**. Fruehere Iterationen bleiben nur Historie.
- Der Plan bleibt in drei getrennten Funktionsbloecken geschnitten, formalisiert jetzt aber die fehlenden Blocker sauber:
  1. standardisiertes `carryover-output.json` als Ein-/Ausgabe fuer Jahresuebergaenge
  2. expliziter `scaffold.template.json`/`scaffold.json`-Generator plus Preflight-Gate
  3. expliziter Review-Loop `input.generated.json` -> `input.reviewed.json` -> `input.json`
- Damit ist der volle Jahresprozess 2024 -> 2025 -> 2026 technisch eindeutig beschrieben, ohne Rueckgriff auf fruehere Iterationen.

## Requirements Snapshot
- Die Implementierung muss drei eigenstaendige Schritte bereitstellen:
  - `derive-opening-carryover` fuer Vorjahr -> Zieljahr
  - `build-year-input` fuer Zieljahr-Belege und -Messwerte
  - `derive-next-year-carryover` fuer Zieljahr -> Folgejahr
- Das **Standardartefakt** fuer beide Carryover-Schritte ist immer dasselbe `carryover-output.json`; `build-year-input` konsumiert genau dieses Artefakt ueber `--opening-carryover`.
- `carryover-output.json` fuehrt seine operativ nutzbaren Opening-Werte bereits als fertige `opening_kostenbeleg`-Objekte, die in `kostenbelege[]` der Ziel-`input.generated.json` uebernommen werden.
- `scaffold.template.json` wird reproduzierbar aus 2024 erzeugt; `scaffold.json` ist die davon abgeleitete, operator-gepflegte 2025-Arbeitsdatei.
- `scaffold.json` darf scaffold-spezifische Metadaten enthalten; diese Metadaten duerfen nicht in die finale operative `input.json` gelangen.
- `mietparteien[]` werden aus 2024 nur als **Draft** uebernommen und muessen fuer 2025 explizit ueberprueft/angepasst werden.
- `build-year-input` darf nur starten, wenn `scaffold.json` die kanonische `zaehler[]`-Liste enthaelt und die operatorischen Review-Freigaben fuer `zaehler[]` und `mietparteien[]` gesetzt sind.
- `build-year-input` schreibt nie direkt `input.json`, sondern nur `input.generated.json`, `import-manifest.json` und optional `review-output.json`.
- Der Review-Loop ist formal:
  - Operator kopiert `input.generated.json` nach `input.reviewed.json`
  - arbeitet `review-output.json` in `input.reviewed.json` ab
  - Finalisierung erzeugt daraus erst bei erfolgreicher Validierung `input.json`
- `ista`-Monatswerte werden je Zaehler nach Dokumentlegende kanonisiert:
  - Startwert = `AN`, sonst `VJ`
  - Endwert = `ST`
  - `periode.von = Datum(Startwert)`
  - `periode.bis = Datum(Endwert)`
  - `messwert_alt = Wert(Startwert)`
  - `messwert_neu = Wert(Endwert)`
  - mehrere Monatszeilen werden niemals 1:1 in operative `ablesungen[]` uebernommen
- Restbestandsabgrenzung erfolgt ausschliesslich in Vorverarbeitung und Carryover-Artefakten; negative operative `kostenbelege[]` sind weder Zwischenziel noch Finalziel.

## Current State Snapshot
- [DONE] Die normativen Specs sind vorhanden und konsistent genug fuer eine eigenstaendige Implementierung.
  - Evidence: `../_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
  - Evidence: `../_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
- [DONE] Die bestehende Anwendung bietet den unveraenderten Zielvertrag fuer finale operative JSONs.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Input/InputDto.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Validation/InputValidator.cs`
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Cli/Program.cs`
- [DONE] 2024-Daten liegen als struktureller Seed vor.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/2024/input_tariff_from_excel.json`
- [PENDING] Es existiert noch kein standardisiertes `carryover-output.json`-Schema im Code.
  - Evidence: kein Carryover-Projekt und kein Carryover-Artefakt unter `data/`
- [PENDING] Es existiert noch kein Scaffold-Generator und kein Scaffold-Preflight.
  - Evidence: kein `data/2025/`, kein Import-Projekt, kein Preflight-Validator
- [PENDING] Es existiert noch kein formalisierter Review-Loop mit `input.reviewed.json`.
  - Evidence: keine Import-/Finalisierungsbefehle und keine Review-Merge-Mechanik im Repo

## Action Plan
1. [DONE] Downstream-Grenze festschreiben: finale operative `input.json` geht unveraendert in den bestehenden Rechenkern.
   - Done signal: Import-, Review- und Carryover-Logik leben nur in vorgelagerten Projekten/Commands.
2. [PENDING] Die Projekt- und Command-Struktur fuer die drei Funktionsbloecke anlegen.
   - Done when: Die Solution mindestens diese Bausteine fuehrt:
     - `src/Nebenkosten.Import`
     - `src/Nebenkosten.Carryover`
     - `tests/Nebenkosten.Import.Tests`
   - Done when: Mindestens diese Commands oder aequivalente Entry-Points existieren:
     - `derive-opening-carryover`
     - `build-year-input`
     - `finalize-year-input`
     - `derive-next-year-carryover`
3. [PENDING] Das **Standard-Schema** fuer `carryover-output.json` definieren und implementieren.
   - Done when: Das Artefakt immer diese Struktur fuehrt:
     - `source_year`
     - `target_year`
     - `generated_at`
     - `entries[]`
   - Done when: Jede `entries[]`-Position mindestens fuehrt:
     - `energietraeger`
     - `be_id`
     - `restmenge`
     - `restmenge_einheit`
     - `restwert_eur`
     - `bewertungsbasis`
     - `opening_kostenbeleg`
   - Done when: `opening_kostenbeleg` exakt die spaeter in `kostenbelege[]` einzuschreibende Struktur fuehrt:
     - `id`
     - `kostenart_id = "brennstoffkosten"`
     - `betrag`
     - `datum`
     - `beschreibung`
     - `scope`
4. [PENDING] `derive-opening-carryover` fuer 2024 -> 2025 implementieren.
   - Done when: Der Schritt genau ein `carryover-output.json` gemaess Action 3 schreibt.
   - Done when: Der Schritt als Eingabe entweder
     - eine finale 2024-Eingabe plus separate 2024-Restmengen-/Bewertungsdatei, oder
     - ein bereits bestaetigtes 2024-Caryover-Artefakt
     akzeptiert.
   - Done when: Die separate 2024-Restmengen-/Bewertungsdatei als eigener, expliziter Inputvertrag beschrieben ist und mindestens fuehrt:
     - `source_year`
     - `entries[]`
     - je Entry: `energietraeger`, `be_id`, `restmenge`, `restmenge_einheit`, `bewertungsbasis`
   - Done when: Fehlende oder widerspruechliche Bewertungsbasis fail-fast abbricht.
5. [PENDING] Den Scaffold-Generator fuer 2025 implementieren.
   - Done when: `scaffold.template.json` reproduzierbar aus `data/2024/input_tariff_from_excel.json` erzeugt wird.
   - Done when: `scaffold.template.json` genau diese Bereiche seeded:
     - `objekt`
     - `berechnungseinheiten`
     - `nutzeinheiten`
     - `zaehler[]`
     - `mietparteien[]` als **Draft**
     - `scaffold_meta`
   - Done when: `scaffold_meta` mindestens fuehrt:
     - `generated_from_year = 2024`
     - `zaehler_review_completed = false`
     - `mietparteien_review_completed = false`
     - `opening_carryover_attached = false`
   - Done when: Das generierte Template keine stillen 2025-Annahmen erfindet.
6. [PENDING] Den Scaffold-Preflight fuer `build-year-input` implementieren.
   - Done when: `build-year-input` vor jeder Extraktion prueft:
     - `scaffold.json` ist parsebar
     - `zaehler[]` ist nicht leer
     - jeder Zaehler hat mindestens `id`, `typ`, `einheit`, `zaehlernummer`
     - `zaehler_review_completed = true`
     - `mietparteien_review_completed = true`
     - `opening_carryover_attached = true`
   - Done when: Fehlender oder unvollstaendiger Scaffold-Status zu einem klaren Fail-fast fuehrt, bevor PDF-Verarbeitung startet.
7. [PENDING] Die 2025-spezifische `mietparteien[]`-Pflege explizit in den Workflow einbauen.
   - Done when: Die Operator-Dokumentation klar festlegt, dass `mietparteien[]` aus 2024 nur Draft-Status haben und fuer 2025 auf Einzug, Auszug, Wechsel und Leerstand manuell angepasst werden muessen.
   - Done when: Der Preflight eine Freigabe ohne `mietparteien_review_completed = true` verweigert.
8. [PENDING] `build-year-input` mit klaren Ein-/Ausgabe-Contracts implementieren.
   - Done when: Eingaben mindestens sind:
     - `--source-dir`
     - `--scaffold-json`
     - `--opening-carryover` (immer ein `carryover-output.json` gemaess Action 3)
     - `--output-dir`
   - Done when: Ausgaben mindestens sind:
     - `input.generated.json`
     - `import-manifest.json`
     - `review-output.json` nur falls noetig
   - Done when: `input.generated.json` die `opening_kostenbeleg`-Eintraege aus `--opening-carryover` direkt in `kostenbelege[]` aufnimmt.
9. [PENDING] Quellerkennung, Extraktion, Segmentierung und Normalisierung vollstaendig operationalisieren.
   - Done when: Quellerkennung mindestens `ista_monthly_export`, `ista_period_or_snapshot`, `bundle_belege`, `tibber_invoice`, `generic_invoice` unterscheidet.
   - Done when: Native Text zuerst und macOS-Vision-OCR als Darwin-Initialpfad implementiert sind.
   - Done when: Bundle-Segmentierung nur unter den in der Spec definierten Merge-Regeln Seiten zusammenfuehrt.
   - Done when: Scope-Inferenz strikt `Dokumenttext > Dateiname > Domain-Regel` folgt.
   - Done when: Tibber genau einen Monats-`stromtarif` je belastbarem Zeitraum erzeugt.
10. [PENDING] Die `ista`-Monatswert-Kanonisierung algorithmisch exakt implementieren.
    - Done when: Pro Zaehler aus einem `ista_monthly_export` genau ein operativer Datensatz entsteht.
    - Done when: Der Algorithmus exakt ist:
      - identifiziere alle Werte des Zaehlerblocks im relevanten Zeitraum
      - waehle `AN`, sonst `VJ`, als Startwert
      - waehle `ST` als Endwert
      - setze `periode.von = Datum(Startwert)`
      - setze `periode.bis = Datum(Endwert)`
      - setze `messwert_alt = Wert(Startwert)`
      - setze `messwert_neu = Wert(Endwert)`
    - Done when: Mehrdeutige Mehrfach-Starts oder Mehrfach-Enden nicht geraten, sondern als Review- oder Fail-fast-Fall enden.
11. [PENDING] Zaehler-Matching und negative-Kostenbeleg-Guardrails implementieren.
    - Done when: Matching mindestens Rohtext, alphanumerisch normalisiert, nur Ziffern und OCR-normalisierte Varianten prueft.
    - Done when: Auto-Korrektur nur bei genau einem plausiblen Kandidaten nach Nummer, Typ und Scope greift.
    - Done when: Vor Finalisierung explizit geprueft wird, dass `input.generated.json` bzw. `input.reviewed.json` keine negativen operativen `kostenbelege[]` enthaelt.
12. [PENDING] Den Review- und Finalisierungs-Loop formal implementieren.
    - Done when: Der Loop exakt lautet:
      1. `build-year-input` schreibt `input.generated.json`
      2. Operator kopiert zu `input.reviewed.json`
      3. Operator arbeitet `review-output.json` in `input.reviewed.json` ab
      4. `finalize-year-input` validiert `input.reviewed.json`
      5. Nur dann wird `data/2025/input.json` geschrieben
    - Done when: Ohne `input.reviewed.json` oder bei offenen Review-Faellen keine Finalisierung erfolgt.
13. [PENDING] `derive-next-year-carryover` fuer 2025 -> 2026 mit demselben Standard-Schema implementieren.
    - Done when: Der Schritt wieder ein `carryover-output.json` gemaess Action 3 schreibt.
    - Done when: Die finale 2025-`input.json` dabei nur gelesen, aber nicht mutiert wird.
    - Done when: Restbestandsabgrenzung ausschliesslich im Carryover-Artefakt und nie als negativer operativer `kostenbeleg` persistiert wird.
14. [PENDING] Testsuite und Operator-Doku an dieser finalen Dreiteilung ausrichten.
    - Done when: Repo-Tests mindestens getrennte Gruppen haben fuer:
      - opening carryover derivation
      - scaffold generation + preflight
      - year input build
      - ista monthly canonicalization
      - finalization loop
      - next-year carryover derivation
    - Done when: Die Operator-Doku den Jahresprozess mindestens so beschreibt:
      1. 2024-Restmengen/Bewertungsbasis bereitstellen
      2. `derive-opening-carryover`
      3. `scaffold.template.json` erzeugen
      4. `scaffold.json` fuer 2025 pflegen und freigeben
      5. `build-year-input`
      6. `input.reviewed.json` pflegen
      7. `finalize-year-input`
      8. bestehende `abrechnung`-CLI laufen lassen
      9. `derive-next-year-carryover`

## Open Items
- Keine offenen blocking Spec- oder Ausfuehrungsluecken fuer diese Iteration.
- [NON-BLOCKING] Ein spaeterer Merge-Helper fuer `review-output.json` -> `input.reviewed.json` kann ergonomisch sinnvoll sein, ist aber kein Startblocker.

## Verification Test Cases
1. Given eine finale 2024-Eingabe plus separate 2024-Restmengen-/Bewertungsdatei, when `derive-opening-carryover` laeuft, then entsteht ein `carryover-output.json` gemaess Standard-Schema mit 2025-`opening_kostenbeleg`-Eintraegen.
2. Given ein fehlender oder widerspruechlicher 2024-Carryover-Input, when `derive-opening-carryover` oder `finalize-year-input` laeuft, then bricht der Lauf fail-fast ab und gibt keine finale 2025-`input.json` frei.
3. Given `scaffold.template.json` aus 2024, when es ohne Operator-Freigabe direkt an `build-year-input` uebergeben wird, then verweigert der Scaffold-Preflight den Lauf.
4. Given ein `scaffold.json` mit nicht geprueften `mietparteien[]`, when `build-year-input` startet, then bricht der Lauf vor PDF-Verarbeitung mit einem klaren Preflight-Fehler ab.
5. Given ein valides `scaffold.json`, valides `carryover-output.json` und den 2025-OneDrive-Ordner, when `build-year-input` laeuft, then entstehen `input.generated.json`, `import-manifest.json` und optional `review-output.json`, aber niemals direkt `input.json`.
6. Given ein `ista_monthly_export`, when die Kanonisierung laeuft, then entsteht pro Zaehler genau eine operative Periodenablesung mit `AN|VJ -> ST`-Mapping und nie eine 1:1-Uebernahme aller Monatszeilen.
7. Given ein `input.generated.json` mit einem negativen operativen `kostenbeleg`, when `finalize-year-input` laeuft, then bricht die Finalisierung vor dem Schreiben von `input.json` ab.
8. Given offene Review-Faelle, when `input.reviewed.json` nicht alle Punkte aus `review-output.json` aufloest, then wird keine finale `data/2025/input.json` geschrieben.
9. Given eine finalisierte `data/2025/input.json` und belastbare 2025-Restmengen/Bewertungsbasis, when `derive-next-year-carryover` laeuft, then entsteht wieder ein standardisiertes `carryover-output.json` fuer 2026, ohne die operative 2025-`input.json` zu aendern.

## Readiness
- Diese Iteration ist implementation-ready und **standalone**: sie beschreibt den vollen Funktionsumfang ohne Rueckgriff auf Iteration 1-4.
- Der empfohlene Startpunkt ist jetzt eindeutig und robust: zuerst Standard-Schema fuer `carryover-output.json`, dann `derive-opening-carryover`, dann Scaffold-Generator/Preflight, dann `build-year-input`, dann Review/Finalisierung, dann `derive-next-year-carryover`.

# Iteration 6

## Summary
- Diese Iteration ersetzt Iteration 5 als **allein auszufuehrende Implementierungsiteration**.
- Die beiden letzten Blocker sind jetzt explizit geschlossen:
  - `carryover-output.json` ist als **separates Vorverarbeitungsartefakt** formalisiert und wird bewusst **nicht** Teil des operativen App-Schemas.
  - Scaffold-Metadaten leben **nicht** in `scaffold.json`, sondern in einer separaten `scaffold.state.json`.
- Zusaetzlich ist der `ista`-Kanonisierungszeitraum jetzt praezise bestimmt: relevant ist immer der **objektweite Abrechnungszeitraum des Zieljahres**, geschnitten mit der tatsaechlich im Dokument belegten Periode des Zaehlerblocks.

## Requirements Snapshot
- Die Vorverarbeitung besteht aus genau vier Commands bzw. aequivalenten Entry-Points:
  - `derive-opening-carryover`
  - `build-year-input`
  - `finalize-year-input`
  - `derive-next-year-carryover`
- Das operative Anwendungsschema bleibt unveraendert. Neue Vorverarbeitungsartefakte (`carryover-output.json`, `scaffold.template.json`, `scaffold.json`, `scaffold.state.json`, `input.generated.json`, `input.reviewed.json`, `import-manifest.json`, `review-output.json`) sind **keine** neuen Runtime-Schemas der Abrechnungsanwendung.
- `carryover-output.json` ist ein reines Vorverarbeitungsartefakt. Es dient nur dazu,
  - Vorjahres-Restwerte in das Zieljahr zu uebertragen und
  - Zieljahres-Restwerte fuer das Folgejahr bereitzustellen.
- `carryover-output.json` enthaelt fertige `opening_kostenbeleg`-Objekte, deren Struktur **absichtlich** dem bestehenden `KostenbelegDto` entspricht. Bei der Uebernahme in `input.generated.json` werden diese Objekte 1:1 in `kostenbelege[]` geschrieben.
- `scaffold.json` enthaelt nur fachliche Scaffold-Daten fuer 2025; Status- und Freigabeinformationen liegen ausschliesslich in `scaffold.state.json`.
- `scaffold.template.json` und `scaffold.json` duerfen Draft-Stammdaten enthalten; erst `input.json` muss vollstaendig dem bestehenden operativen `NebenkostenInput`-Vertrag entsprechen.
- `mietparteien[]` werden aus 2024 nur als Ausgangsentwurf uebernommen. Fuer 2025 muessen Einzug, Auszug, Wechsel und Leerstand explizit ueberarbeitet und in `scaffold.state.json` freigegeben werden.
- Relevanter Zeitraum fuer `ista`-Monatswerte ist:
  - primär der Abrechnungszeitraum des Zieljahres (bei 2025 also `2025-01-01` bis `2025-12-31`)
  - geschnitten mit der im Dokument fachlich belastbar belegten Periode des Zaehlerblocks
  - nicht die spaetere Mietparteien-Teilperiode; diese bleibt Aufgabe des bestehenden Rechenkerns nach Import
- Negative operative `kostenbelege[]` sind in keinem Vorstufen- oder Finalisierungsschritt zulaessig.

## Current State Snapshot
- [DONE] Die Hauptspec und die Import-Spec beschreiben die Zielregeln fuer Vorverarbeitung, Restbestandslogik und operative JSON-Kompatibilitaet.
  - Evidence: `../_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
  - Evidence: `../_specs/2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
- [DONE] Die bestehende Anwendung akzeptiert operative `kostenbelege[]`, `ablesungen[]`, `zaehler[]` und `stromtarife[]`, aber keine neuen Vorverarbeitungsfelder.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Input/InputDto.cs`
- [DONE] Die bestehende Validierung lehnt negative `kostenbelege[].betrag` ab; deshalb muss Restbestandsabgrenzung vor dem Runtime-Import erfolgen.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Validation/InputValidator.cs`
- [DONE] 2024-Daten liegen als Seed fuer 2025-Stammdaten vor.
  - Evidence: `private/Vermietung/nebenkosten-abrechnung/data/2024/input_tariff_from_excel.json`
- [PENDING] Kein Vorverarbeitungsprojekt und keine standardisierten Vorverarbeitungsartefakte existieren bisher im Code.
- [PENDING] Kein `data/2025/` mit Scaffold-, Review- und Carryover-Artefakten existiert bisher.

## Action Plan
1. [DONE] Downstream-Vertrag fixieren: finale `input.json` bleibt das einzige operative Eingangsschema fuer die bestehende Anwendung.
   - Done signal: Kein Vorverarbeitungsartefakt wird direkt an `Nebenkosten.Cli/Program.cs` uebergeben.
2. [PENDING] Projektstruktur und Commands fuer die Vorverarbeitung anlegen.
   - Done when: Die Solution mindestens diese Projekte oder aequivalente Zuschnitte fuehrt:
     - `src/Nebenkosten.Import`
     - `src/Nebenkosten.Carryover`
     - `tests/Nebenkosten.Import.Tests`
   - Done when: Es Commands oder aequivalente Entry-Points gibt fuer:
     - `derive-opening-carryover`
     - `build-year-input`
     - `finalize-year-input`
     - `derive-next-year-carryover`
3. [PENDING] Das Standard-Schema fuer `carryover-output.json` definieren und implementieren.
   - Done when: `carryover-output.json` immer diese Top-Level-Felder fuehrt:
     - `source_year`
     - `target_year`
     - `generated_at`
     - `entries[]`
   - Done when: Jede `entries[]`-Position mindestens fuehrt:
     - `energietraeger`
     - `be_id`
     - `restmenge`
     - `restmenge_einheit`
     - `restwert_eur`
     - `bewertungsbasis`
     - `opening_kostenbeleg`
   - Done when: `opening_kostenbeleg` exakt als Vorverarbeitungs-Kopie eines bestehenden `KostenbelegDto`-Shape modelliert ist:
     - `id`
     - `kostenart_id = "brennstoffkosten"`
     - `betrag`
     - `datum`
     - `beschreibung`
     - `scope`
   - Done when: Klar dokumentiert ist, dass nur `opening_kostenbeleg` spaeter in `kostenbelege[]` der operativen Eingabe uebernommen wird; alle anderen Felder bleiben Vorverarbeitungsmetadaten.
4. [PENDING] `derive-opening-carryover` fuer 2024 -> 2025 implementieren.
   - Done when: Der Command als Input entweder
     - ein bestaetigtes 2024-`carryover-output.json`, oder
     - `data/2024/input_tariff_from_excel.json` plus eine separate `restbasis.2024.json`
     akzeptiert.
   - Done when: `restbasis.2024.json` mindestens fuehrt:
     - `source_year`
     - `entries[]`
     - je Entry: `energietraeger`, `be_id`, `restmenge`, `restmenge_einheit`, `bewertungsbasis`
   - Done when: Der Command immer ein standardisiertes `carryover-output.json` fuer `source_year = 2024`, `target_year = 2025` schreibt.
   - Done when: Fehlende oder widerspruechliche Restbasis fail-fast abbricht.
5. [PENDING] `scaffold.template.json` reproduzierbar aus 2024 generieren.
   - Done when: Der Generator aus `data/2024/input_tariff_from_excel.json` genau diese fachlichen Bereiche seeded:
     - `objekt`
     - `berechnungseinheiten`
     - `nutzeinheiten`
     - `zaehler[]`
     - `mietparteien[]` als Draft
   - Done when: Das Template keine Vorverarbeitungsmetadaten, keine Review-Flags und keine Runtime-fremden Felder enthaelt.
6. [PENDING] `scaffold.state.json` als separates Meta-Artefakt definieren und implementieren.
   - Done when: `scaffold.state.json` mindestens fuehrt:
     - `generated_from_year`
     - `zaehler_review_completed`
     - `mietparteien_review_completed`
     - `opening_carryover_attached`
   - Done when: Diese Datei bewusst **nicht** Teil von `scaffold.json` und spaeter **nicht** Teil der finalen `input.json` ist.
   - Done when: Die Operator-Doku klar trennt:
     - `scaffold.json` = fachliche Arbeitsdaten
     - `scaffold.state.json` = Freigabe-/Statusdaten
7. [PENDING] Scaffold-Preflight vor `build-year-input` implementieren.
   - Done when: `build-year-input` vor jeder PDF-Verarbeitung prueft:
     - `scaffold.json` ist parsebar
     - `zaehler[]` ist nicht leer
     - jeder Zaehler hat mindestens `id`, `typ`, `einheit`, `zaehlernummer`
     - `scaffold.state.json` ist parsebar
     - `zaehler_review_completed = true`
     - `mietparteien_review_completed = true`
     - `opening_carryover_attached = true`
   - Done when: Fehlender oder unvollstaendiger Scaffold-Zustand vor Start der Dokumentverarbeitung fail-fast endet.
8. [PENDING] 2025-spezifische `mietparteien[]`-Pflege als Pflichtschritt absichern.
   - Done when: Die Operator-Doku explizit fordert, dass aus 2024 uebernommene `mietparteien[]` fuer 2025 auf Wechsel, Leerstand, Einzug und Auszug angepasst werden.
   - Done when: Ohne `mietparteien_review_completed = true` keine Vorverarbeitung gestartet werden kann.
9. [PENDING] `build-year-input` mit klaren Ein-/Ausgabe-Contracts implementieren.
   - Done when: Eingaben mindestens sind:
     - `--source-dir`
     - `--scaffold-json`
     - `--scaffold-state`
     - `--opening-carryover`
     - `--output-dir`
   - Done when: Ausgaben mindestens sind:
     - `input.generated.json`
     - `import-manifest.json`
     - `review-output.json` nur falls noetig
   - Done when: `input.generated.json` die `opening_kostenbeleg`-Eintraege aus `--opening-carryover` direkt in `kostenbelege[]` aufnimmt.
10. [PENDING] Quellerkennung, Extraktion, Segmentierung und Normalisierung vollstaendig operationalisieren.
    - Done when: Quellerkennung mindestens `ista_monthly_export`, `ista_period_or_snapshot`, `bundle_belege`, `tibber_invoice`, `generic_invoice` unterscheidet.
    - Done when: Native Text zuerst und macOS Vision als Darwin-OCR-Provider initial implementiert sind.
    - Done when: Bundle-Segmentierung nur nach den in der Spec definierten Merge-Regeln zusammenfuehrt.
    - Done when: Scope-Inferenz strikt `Dokumenttext > Dateiname > Domain-Regel` folgt.
    - Done when: Tibber nur `stromtarife[]`, nie direkte Strom-`kostenbelege[]`, erzeugt.
11. [PENDING] `ista`-Monatswert-Kanonisierung mit praezisem Zeitraumvertrag implementieren.
    - Done when: Relevanter Zeitraum je Zaehlerblock exakt definiert ist als:
      - Schnittmenge aus Zieljahres-Abrechnungszeitraum und dokumentierter Zaehlerblock-Periode
    - Done when: Der Algorithmus exakt ist:
      - identifiziere alle fachlich belastbaren Werte des Zaehlerblocks im relevanten Zeitraum
      - waehle `AN`, sonst `VJ`, als Startwert
      - waehle `ST` als Endwert
      - setze `periode.von = Datum(Startwert)`
      - setze `periode.bis = Datum(Endwert)`
      - setze `messwert_alt = Wert(Startwert)`
      - setze `messwert_neu = Wert(Endwert)`
    - Done when: Mehrdeutige Mehrfach-Starts oder Mehrfach-Enden nicht geraten, sondern als Review- oder Fail-fast-Fall enden.
12. [PENDING] Zaehler-Matching und Negative-Guardrails implementieren.
    - Done when: Matching mindestens Rohtext, alphanumerisch normalisiert, nur Ziffern und OCR-normalisierte Varianten prueft.
    - Done when: Auto-Korrektur nur bei genau einem plausiblen Kandidaten nach Nummer, Typ und Scope greift.
    - Done when: Vor Finalisierung explizit geprueft wird, dass weder `input.generated.json` noch `input.reviewed.json` negative operative `kostenbelege[]` enthalten.
13. [PENDING] Den Review- und Finalisierungs-Loop formalisieren.
    - Done when: Der Loop exakt lautet:
      1. `build-year-input` schreibt `input.generated.json`
      2. Operator kopiert zu `input.reviewed.json`
      3. Operator arbeitet `review-output.json` in `input.reviewed.json` ab
      4. `finalize-year-input` validiert `input.reviewed.json`
      5. Nur dann wird `data/2025/input.json` geschrieben
    - Done when: Ohne `input.reviewed.json`, bei offenen Review-Faellen oder bei Verstoessen gegen `InputValidator` keine Finalisierung erfolgt.
14. [PENDING] `derive-next-year-carryover` fuer 2025 -> 2026 mit demselben Standardschema implementieren.
    - Done when: Der Command wieder ein standardisiertes `carryover-output.json` schreibt.
    - Done when: Die finale 2025-`input.json` dabei nur gelesen, nie mutiert wird.
    - Done when: Restbestandsabgrenzung ausschliesslich im Carryover-Artefakt und nie als negativer operativer `kostenbeleg` persistiert wird.
15. [PENDING] Testsuite und Operator-Doku an dieser finalen Struktur ausrichten.
    - Done when: Repo-Tests mindestens getrennte Gruppen haben fuer:
      - opening carryover derivation
      - scaffold generation
      - scaffold preflight
      - year input build
      - ista monthly canonicalization
      - review/finalization loop
      - next-year carryover derivation
    - Done when: Die Operator-Doku den Jahresprozess mindestens so beschreibt:
      1. `restbasis.2024.json` bereitstellen oder bestaetigtes 2024-`carryover-output.json` verwenden
      2. `derive-opening-carryover`
      3. `scaffold.template.json` erzeugen
      4. `scaffold.json` fachlich pflegen
      5. `scaffold.state.json` freigeben
      6. `build-year-input`
      7. `input.reviewed.json` pflegen
      8. `finalize-year-input`
      9. bestehende `abrechnung`-CLI laufen lassen
      10. `derive-next-year-carryover`

## Open Items
- Keine offenen blocking Spec- oder Ausfuehrungsluecken fuer diese Iteration.
- [NON-BLOCKING] Ein spaeterer Merge-Helper fuer `review-output.json` -> `input.reviewed.json` kann ergonomisch sinnvoll sein, ist aber kein Startblocker.

## Verification Test Cases
1. Given eine finale 2024-Eingabe plus `restbasis.2024.json`, when `derive-opening-carryover` laeuft, then entsteht ein standardisiertes `carryover-output.json` mit 2025-`opening_kostenbeleg`-Eintraegen.
2. Given ein bestaetigtes 2024-`carryover-output.json`, when es an `build-year-input` uebergeben wird, then werden die `opening_kostenbeleg`-Eintraege 1:1 in `kostenbelege[]` von `input.generated.json` uebernommen.
3. Given ein `scaffold.json` ohne separates `scaffold.state.json`, when `build-year-input` startet, then bricht der Scaffold-Preflight vor jeder PDF-Verarbeitung fail-fast ab.
4. Given ein `scaffold.state.json` mit `mietparteien_review_completed = false`, when `build-year-input` startet, then verweigert der Preflight den Lauf.
5. Given ein valides `scaffold.json`, valides `scaffold.state.json`, valides `carryover-output.json` und den 2025-OneDrive-Ordner, when `build-year-input` laeuft, then entstehen `input.generated.json`, `import-manifest.json` und optional `review-output.json`, aber niemals direkt `input.json`.
6. Given ein `ista_monthly_export`, when die Kanonisierung laeuft, then entsteht pro Zaehler genau eine operative Periodenablesung mit Mapping `AN|VJ -> ST` innerhalb des objektweiten Zieljahres-Zeitraums.
7. Given ein `input.generated.json` oder `input.reviewed.json` mit negativem operativen `kostenbeleg`, when `finalize-year-input` laeuft, then bricht die Finalisierung vor dem Schreiben von `input.json` ab.
8. Given offene Review-Faelle, when `input.reviewed.json` diese nicht vollstaendig aufloest, then wird keine finale `data/2025/input.json` geschrieben.
9. Given eine finalisierte `data/2025/input.json` und belastbare 2025-Restmengen/Bewertungsbasis, when `derive-next-year-carryover` laeuft, then entsteht wieder ein standardisiertes `carryover-output.json` fuer 2026, ohne die operative 2025-`input.json` zu aendern.

## Readiness
- Diese Iteration ist implementation-ready und **standalone**: sie beschreibt den vollen Funktionsumfang ohne Rueckgriff auf Iteration 1-5.
- Der empfohlene Startpunkt ist jetzt eindeutig: zuerst Standardschema fuer `carryover-output.json`, dann `derive-opening-carryover`, dann Scaffold-Generator plus `scaffold.state.json`, dann `build-year-input`, dann Review/Finalisierung, dann `derive-next-year-carryover`.

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-03-29 | 1 | Claude | Initial implementation plan for the 2025 receipt and meter import pipeline derived from the finalized import spec. |
| 2026-03-29 | 2 | Claude | Resolved inline user answers and closed execution-level blockers around scaffold seeding, source classification, manifest contracts, monthly ista normalization, and finalization gating. |
| 2026-03-29 | 3 | Claude | Clarified explicitly that 2025 opening stock values must be derived from the finalized 2024 carryover result before 2025 finalization. |
| 2026-03-29 | 4 | Claude | Reframed the latest iteration as a self-contained full implementation plan with three separable function blocks for opening carryover, year-input build, and next-year carryover. |
| 2026-03-29 | 5 | Claude | Replaced the latest execution plan with a stricter standalone iteration that formalizes carryover schemas, scaffold generation/preflight, mietparteien review gates, the reviewed-input loop, and exact ista monthly canonicalization. |
| 2026-03-29 | 6 | Claude | Closed the final blockers by formalizing carryover as a separate preprocessing artifact, moving scaffold metadata into a separate scaffold.state.json, and pinning the exact ista timeframe contract. |

SessionId: 33413792-7db3-4419-a68b-460f5a1b6e1e
