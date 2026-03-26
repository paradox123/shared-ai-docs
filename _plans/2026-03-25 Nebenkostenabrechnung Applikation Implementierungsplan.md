# Nebenkostenabrechnung Applikation Implementierungsplan

Bezugsspezifikation:
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`

# Iteration 1

## Summary
- Aus der fachlichen Spec wurde ein umsetzungsorientierter, statusbasierter Implementierungsplan abgeleitet.
- Bereits vorhandene Artefakte (Schema, Beispiel-Input, HTML-Mock, Beispiel-Rendering) wurden als Startpunkt markiert.
- Der Plan fokussiert v1 auf: validiertes JSON-Ingest, deterministische Umlagelogik, fail-fast Fehlermeldungen, nachvollziehbares Zwischenergebnis-JSON und renderbare Einzelabrechnung.

## Requirements Snapshot
- Pflichtinhalt je Einzelabrechnung: Gesamtkosten, Verteilerschluessel, Mieteranteil, Vorauszahlungen, Saldo.
- Verbindliche fachliche Quelle fuer Scope/Umlage ist die Kostenarten-Matrix.
- Fail-fast statt stiller Annahmen bei fehlenden oder unplausiblen Eingaben.
- Ausgabe in zwei Stufen: `einzelabrechnung.json` (Zwischenergebnis) und `einzelabrechnung.pdf` (finales Dokument).
- T10-Regression gegen Excel2024 fuer NE1-NE4 mit dokumentierten, begruendeten Abweichungen.

## Current State Snapshot
- [DONE] Fachliche Spec mit Domänenmodell, Regeln, Testfaellen und Oracle-Werten liegt vor.
  - Evidence: `_shared/_specs/2026-03-24 Nebenkostenabrechnung Applikation.md`
- [DONE] JSON-Schema und Beispiel-Input existieren.
  - Evidence: `_shared/_specs/nebenkosten_input_schema.json`, `_shared/_specs/nebenkosten_input_example.json`
- [DONE] Ziel-Layout und Beispiel-Rendering existieren als Referenz.
  - Evidence: `_shared/_specs/mock_einzelabrechnung.html`, `_shared/_specs/render_einzelabrechnung_example.py`, `_shared/_specs/rendered_example/mp-kraft-huehne/einzelabrechnung.html`, `_shared/_specs/rendered_example/mp-kraft-huehne/einzelabrechnung.pdf`
- [PENDING] Produktionsreifer Rechenkern fuer validierte Umlage inkl. Sonderregeln ist noch nicht als durchgaengig getestete Anwendung in diesem Planstand nachgewiesen.

## Action Plan
1. [DONE] Plan-Basis aus der finalen Spec herstellen und Scope auf v1 begrenzen (ohne Vermieter-Gesamtuebersicht).
   - Done signal: Dieser Implementierungsplan existiert und referenziert die autoritative Spec.
2. [PENDING] Laufzeit-Skelett fuer die Anwendung festlegen (CLI-Aufruf, Pflichtparameter `--input-json`, `--output-dir`, Exitcodes).
   - Done when: Ein reproduzierbarer Lauf erzeugt pro Mietpartei Unterordner mit Ergebnisdateien oder einen eindeutigen Fehlerabbruch.
3. [PENDING] Strikte Eingabevalidierung gegen Schema plus Referenz-/Logikpruefungen implementieren.
   - Done when: Struktur-, Referenz- und Datenlogikfehler liefern fail-fast Fehlermeldungen mit Feld/ID/Periode.
4. [PENDING] Domänenmodell in Code abbilden (Objekt, BE, NE, Mietpartei, Zaehler, Ablesung, Kostenbeleg, Vertrag, Vorauszahlung, Stromtarif).
   - Done when: Alle fuer Matrix/Umlage relevanten Entitaeten sind typisiert und testbar instanziierbar.
5. [PENDING] Kostenarten-Matrix als technische Konfiguration implementieren (Scope, Umlageart, Schlüssel/Verbrauch).
   - Done when: Jede Kostenart wird deterministisch ueber genau einen konfigurierten Rechenpfad verarbeitet.
6. [PENDING] Verbrauchsermittlung implementieren (ista-Differenz, manuelle Alt/Neu-Paare, Teilperioden bei Ein-/Auszug).
   - Done when: Verbrauchswerte je NE/Zaehlertyp sind reproduzierbar und fuer Teilperioden korrekt begrenzt.
7. [PENDING] Sonderregeln implementieren: NE5-Restverbrauch Kaltwasser, Waermepumpen-Strom BE1, Versicherungs-Vertragsgruppen.
   - Done when: T4, T5 und T9 fachlich korrekt passieren; negative/unplausible Ableitungen brechen fail-fast ab.
8. [PENDING] Umlagelogik implementieren: Schluessel-, Verbrauchs- und Mischumlage inkl. Zeitanteiligkeit nur fuer schluesselbasierte Positionen.
   - Done when: Brennstoffkosten 30/70 werden korrekt getrennt behandelt; Verbrauchsanteile nicht zeitanteilig.
9. [PENDING] Rundungs- und Restcent-Regeln deterministisch implementieren.
   - Done when: Summe gerundeter NE-Anteile je Kostenart entspricht exakt dem Kostenart-Gesamtbetrag.
10. [PENDING] Saldo-Berechnung und Vorauszahlungsabzug je Mietpartei implementieren.
    - Done when: `saldo = gesamtkosten - vorauszahlungen` ist je Partei nachvollziehbar im Output enthalten.
11. [PENDING] Ausgabe-Builder fuer `einzelabrechnung.json` mit Zwischenwerten und Herleitungen erstellen.
    - Done when: JSON enthaelt mindestens die spezifizierten Bloecke (`schluessewerte`, `verbraeuche`, `kostenpositionen`, `vorauszahlungen`, `saldo`).
12. [PENDING] Dokumentenrendering auf Basis des vorhandenen Mock/Beispiels stabilisieren (HTML als Entwicklungsstufe, PDF als finales Artefakt).
    - Done when: Pro Mietpartei entstehen drucktaugliche PDFs im konfigurierten Zielordner.
13. [PENDING] Testsuite fuer T1-T10 aufbauen, automatisiert ausfuehren und dokumentierte Abweichungen (Spec vs Excel) als erwartete Deltas hinterlegen.
    - Done when: Pflichttests sind grün; bekannte Abweichungen erscheinen explizit als akzeptierte, begruendete Differenzen.
14. [PENDING] End-to-End Regression fuer 2024-Datensatz etablieren (NE1-NE4 Oracle, NE5 separat fachlich pruefen).
    - Done when: Regression reportet Vergleichswerte je Partei/Kostenart inklusive Delta-Begruendung.
15. [PENDING] Ausgabeablage und Namenskonvention finalisieren (`{mietpartei_id}/einzelabrechnung.json|pdf`).
    - Done when: Artefakte werden reproduzierbar im Zielpfad erzeugt und sind durch die Anwendung konfigurierbar.

## Open Items
- [DECISION NON-BLOCKING] Soll die v1-Anwendung zunaechst nur als CLI laufen oder parallel bereits eine minimal nutzbare API bereitstellen? => mit minimaler nutzbarer CLI
- [MISSING SPEC NON-BLOCKING] Einheitliches Fehlermeldungsformat (z. B. strukturierter Fehlercodekatalog) ist fachlich gewuenscht, aber noch nicht explizit in der Spec normiert.
- [DECISION NON-BLOCKING] Festlegung, ob PDF-Erzeugung synchron im Hauptlauf erfolgt oder optional per Flag abgeschaltet werden kann (nur JSON-Mode fuer schnelle Regressionen). => das kann zum Testen sinnvoll sein, ja

## Verification Test Cases
1. Given vollstaendige 2024-Eingaben fuer alle 5 NE, when die Anwendung laeuft, then entstehen 5 Einzelabrechnungen und die Summenkonsistenz je Kostenart bleibt erhalten.
2. Given eine leerstehende NE ohne Mietpartei, when die Umlage nach Personen berechnet wird, then geht diese NE mit 0 Personen ein und es wird kein Dokument fuer diese NE erzeugt.
3. Given unterjaehriger Ein-/Auszug, when schluesselbasierte Kosten verteilt werden, then erfolgt die Zeitanteiligkeit monatsgenau und Verbrauchskosten bleiben nicht-zeitanteilig.
4. Given Hauptanschluss und NE1-NE4 Kaltwasserverbraeuche, when NE5 als Rest berechnet wird, then fuehrt ein negativer Rest sofort zu einem fail-fast Abbruch.
5. Given BE1-Stromzaehler plus NE1/NE2-Strom, when Waermepumpenstrom berechnet wird, then wird die Herleitung als Formel ausgewiesen und auf WW-Verbrauch umgelegt.
6. Given fehlende Pflichtablesung oder ungueltige Referenz-ID, when der Lauf startet, then bricht die Anwendung mit eindeutiger Fehlermeldung inkl. betroffener ID/Periode ab.
7. Given gemischte Brennstoffkosten, when die Umlage erfolgt, then sind 30% Schluesselanteil und 70% Verbrauchsanteil getrennt, konsistent und ohne Ueberschreitung des Gesamtbelegs.
8. Given Rundungsfaelle mit Restcent, when Betraege auf 2 Nachkommastellen gerundet werden, then wird der Restcent deterministisch der groessten Position (Tie-Breaker: kleinste NE-ID) zugewiesen.
9. Given 2024-Oracle fuer NE1-NE4, when Regression ausgefuehrt wird, then stimmen die Kernwerte mit Excel ueberein oder Abweichungen sind als bekannte Spec-Deltas dokumentiert.
10. Given NE5 ohne Excel-Oracle, when die Abrechnung erzeugt wird, then wird NE5 fachlich vollstaendig berechnet, aber nicht als Fehler gegen T10 gewertet.

# Iteration 2

## Summary
- Der Plan wurde auf Umsetzungsreife nachgeschaerft, insbesondere bei Render-Pflichten, Artefaktvertrag und Testabdeckung.
- Die in Iteration 1 bereits angedeuteten Entscheidungen wurden in konkrete Ausfuehrungsannahmen uebersetzt, damit kein falscher Open-Item-Status mehr bleibt.
- Die Umsetzung ist mit dieser Iteration in klaren Phasen planbar: Vertragsfestlegung, Rechenkern, Zwischenergebnis, Dokumentenmodell, Rendering, Regression.

## Requirements Snapshot
- Die Anwendung muss nicht nur korrekt rechnen, sondern die Pflichtbestandteile der Nebenkostenabrechnung sichtbar und mieterverstaendlich ausgeben.
- Die Einzelabrechnung muss je relevanter Position Alt/Neu/Differenz oder bei abgeleiteten Werten eine explizite Formel-Herleitung zeigen.
- Der Dateivertrag fuer CLI-Lauf und Artefakte muss vor Renderer- und E2E-Umsetzung feststehen.
- Drucklayout, A4-Tauglichkeit, Seitenumbrueche, verstaendliche Begriffe und nachvollziehbare Verteilerschluessel sind Teil der Abnahme und nicht nur kosmetische Nacharbeit.

## Current State Snapshot
- [DONE] Die Grundstruktur aus Iteration 1 deckt Rechenkern, Validierung, Sonderregeln und Regression bereits ab.
  - Evidence: Iteration 1 Action Plan und Verification Test Cases liegen vor.
- [DONE] Produktentscheidung fuer den ersten Auslieferungspfad ist getroffen: minimale nutzbare CLI statt paralleler API.
  - Evidence: Iteration 1 Open Item ist durch Nutzerkommentar beantwortet.
- [DONE] Ein optionaler JSON-only Modus ist als sinnvolle Test-/Regressionserleichterung fachlich akzeptiert.
  - Evidence: Iteration 1 Open Item ist durch Nutzerkommentar beantwortet.
- [PENDING] Die Ausgabeanforderungen aus der Spec sind in Iteration 1 noch nicht fein genug in eigene Umsetzungs- und Testschritte zerlegt.
  - Evidence: Rendering war bisher nur als allgemeines PDF-Artefakt beschrieben.

## Action Plan
1. [DONE] CLI als v1-Laufzeitmodell festschreiben.
   - Done signal: Kein weiterer API-Pfad ist fuer v1 Planvoraussetzung; die Anwendung wird als minimal nutzbare CLI geplant.
2. [DONE] Optionalen JSON-only Modus als Ausfuehrungsoption festschreiben.
   - Done signal: PDF-Erzeugung darf per Flag deaktivierbar sein, damit schnelle Regressionen und Fail-fast-Tests ohne Renderkosten laufen koennen.
3. [PENDING] Artefaktvertrag vor dem Implementieren des Renderpfads finalisieren.
   - Done when: CLI-Parameter, Exitcodes, Zielordnerstruktur und Dateinamen (`{mietpartei_id}/einzelabrechnung.json`, `{mietpartei_id}/einzelabrechnung.pdf`) sind vor Renderer-Start fest definiert und als Testvertrag abgesichert.
4. [PENDING] Eingabevalidierung in zwei Schichten planen: Schema zuerst, fachliche Integritaet danach.
   - Done when: Der Plan trennt explizit zwischen JSON-Schema-Pruefung, Referenzpruefung, Scope-/Kostenarten-Matrix-Pruefung und periodenspezifischer Datenlogikpruefung; jede Schicht hat eigene Fehlermeldungsklassen.
5. [PENDING] Rechenkern in klar getrennte Rechenschritte zerlegen.
   - Done when: Der Implementierungspfad benennt mindestens diese Module oder gleichwertigen Bausteine:
     - Input Loader / Parser
     - Validator
     - Scope Resolver
     - Verbrauchsrechner
     - Umlagerechner
     - Rundungs-/Ausgleichsrechner
     - Statement Result Builder
     - Renderer
6. [PENDING] Verbrauchslogik pro Quelle und Sonderfall separat operationalisieren.
   - Done when: Der Plan trennt explizit zwischen `ista_ablese`, `ista_monatsmittel`, manuellen Stichtagsablesungen, NE5-Restverbrauch und BE1-Waermepumpenableitung statt diese nur unter einem allgemeinen Verbrauchsschritt zu sammeln.
7. [PENDING] Dokumentenmodell fuer `einzelabrechnung.json` auf Pflichtfeld-Ebene definieren.
   - Done when: Das Zwischenergebnis nicht nur Blocknamen, sondern ein technisches Mindestmodell fuer Kopfdaten, Ergebnisbox, Verbrauchssektionen, Kostenartenzeilen, Schluesselherleitung, Vorauszahlungsblock, Hinweisblock und Saldo enthaelt.
8. [PENDING] Renderer-Arbeitspaket in fachliche Pflichtsektionen aufteilen.
   - Done when: Es separate Umsetzungsschritte gibt fuer:
     - Kopf/Identifikation
     - Ergebnisuebersicht
     - Verbrauchs- und Ablesewerte inkl. Alt/Neu/Differenz bzw. Formelableitung
     - Kostenarten des relevanten Scopes
     - Verteilerschluessel-Herleitung
     - Kostenanteil je Kostenart
     - Vorauszahlungsabzug
     - Hinweisblock
9. [PENDING] Sprach- und Layoutregeln als Abnahmekriterien verankern.
   - Done when: Die Umsetzung explizit vorsieht, dass Abkuerzungen vor erster Verwendung erklaert werden, Tabellen Vorrang vor Freitext haben, das PDF auf A4 mit sinnvollen Seitenumbruechen laeuft und keine irrelevanten Globaldaten im Hauptdokument erscheinen.
10. [PENDING] Teststrategie in Contract-, Fach-, Dokument- und Oracle-Tests aufspalten.
    - Done when: Es getrennte Tests oder Testgruppen gibt fuer:
      - Schema-/CLI-/Artefaktvertrag
      - Fail-fast und fachliche Rechenlogik
      - Render-Inhalt und Dokumentenpflichten
      - 2024-Oracle und bekannte Deltas
11. [PENDING] Dokumentenpflichten mit eigenen Verifikationstests absichern.
    - Done when: Zusaetzlich zu T1-T10 explizite Tests fuer Alt/Neu/Differenz, Formelanzeige abgeleiteter Werte, A4-Drucktauglichkeit, Abkuerzungserklaerung und nachvollziehbare Schluesselherleitung existieren.
12. [PENDING] Implementierungsreihenfolge als risikominimierende Phasen festlegen.
    - Done when: Die Reihenfolge verbindlich ist:
      - Phase A: Artefaktvertrag und Validierung
      - Phase B: Rechenkern ohne PDF
      - Phase C: `einzelabrechnung.json`
      - Phase D: HTML/PDF-Rendering
      - Phase E: Oracle-Regression und Delta-Dokumentation

## Open Items
- [MISSING SPEC NON-BLOCKING] Einheitliches Fehlermeldungsformat (z. B. strukturierter Fehlercodekatalog) ist weiterhin nicht normiert; Umsetzung kann mit konsistentem Arbeitsformat starten, aber die finale Fehleroberflaeche bleibt Spec-Thema.

## Verification Test Cases
1. Given den JSON-only Modus, when eine Regression ohne PDF gestartet wird, then entstehen validierte `einzelabrechnung.json`-Artefakte und identische Rechenergebnisse ohne Renderpflicht.
2. Given eine Partei mit manuellen oder ista-Ablesungen, when die Einzelabrechnung gerendert wird, then erscheinen je relevantem Wert Alt, Neu und Differenz oder bei abgeleiteten Werten stattdessen eine explizite Formelherleitung.
3. Given eine Partei mit mehreren Kostenarten aus unterschiedlichen Scopes, when das Dokument erzeugt wird, then zeigt jede Zeile den relevanten Scope, den Schluesseltyp, den Gesamtwert des Scopes, den Parteienwert und den daraus resultierenden Betrag.
4. Given ein Dokument mit mehr als einer Seite, when das PDF erzeugt wird, then bleibt das Layout A4-tauglich, Tabellenzeilen werden nicht abgeschnitten und Seitenumbrueche sind sinnvoll gesetzt.
5. Given technische Begriffe wie BE, NE oder HKV, when sie im Hauptdokument erscheinen, then werden sie vor erster Verwendung kurz erklaert oder durch mieterverstaendliche Begriffe ersetzt.
6. Given bekannte Spec-vs-Excel-Abweichungen, when der Oracle-Test laeuft, then werden diese Deltas explizit ausgewiesen statt als ungeklaerte Regression zu erscheinen.
7. Given eine leerstehende NE oder fachlich irrelevante Globaldaten, when das Dokument gerendert wird, then erscheinen keine irrelevanten Fremddaten im Hauptdokument.
8. Given Monatsabschlaege und Gesamtvorauszahlung, when der Vorauszahlungsblock ausgegeben wird, then sind Gesamtbetrag und auf Wunsch die Monatslogik nachvollziehbar dargestellt, ohne den echten Zahlungswert zu ersetzen.

# Iteration 3

## Summary
- Der Plan wurde auf konkrete Ausfuehrungsvertraege verdichtet: Projektstruktur, CLI, Exitcodes, Fehlerpfad, Artefaktpfad, Ergebnisobjekt und Testgruppen sind jetzt explizit benannt.
- Der bisher letzte nicht-blockende Spec-Punkt zum Fehlermeldungsformat ist inzwischen in der Spec aufgeloest und wird hier in den Plan uebernommen.
- In dieser Iteration ist der Plan implementation-ready: keine offenen blocking Spec-/Decision-Punkte, klare naechste Implementierungsschritte, klare Verifikation.

## Requirements Snapshot
- Der neue Produktpfad ist eine C#-Neuumsetzung; der bestehende Python-Pfad dient nur noch als Fixture-, Oracle- und Referenzquelle.
- Jede fachliche Phase muss isoliert testbar bleiben: laden, validieren, rechnen, serialisieren, rendern.
- Die Anwendung muss sowohl fuer Operatoren als auch fuer Regressionen deterministisch und vertragstreu arbeiten.
- Die v1-Abnahme ist erreicht, wenn Rechenkern, Zwischenresultat-JSON und tenant-facing PDF gemeinsam gegen T1-T10 plus Dokumententests bestehen.

## Current State Snapshot
- [DONE] Legacy-Python-Pipeline und Tests existieren als Referenzwelt fuer Fixtures, Regressionen und fachliche Vergleichslogik.
   - Evidence: `private/Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/*`, `private/Vermietung/nebenkosten_pipeline/tests/test_pipeline_tdd.py`
- [DONE] Die Spec normiert inzwischen auch das einheitliche Fehlermeldungsformat.
   - Evidence: Abschnitt `Einheitliches Fehlermeldungsformat (v1)` in der Bezugsspezifikation.
- [PENDING] Die C#-Neuumsetzung selbst ist noch nicht angelegt; der Plan muss daher den ersten umsetzbaren Zuschnitt eindeutig vorgeben.

## Action Plan
1. [DONE] C#-Neuumsetzung als Zielarchitektur festschreiben; Legacy-Python bleibt nur Referenzwelt.
    - Done signal: Kein Arbeitspaket nutzt Python-Komponenten als Laufzeit-Abhaengigkeit; Python wird nur fuer Vergleich, Fixture-Verstaendnis und Oracle-Checks herangezogen.
2. [PENDING] Projektstruktur innerhalb der vorhandenen Solution festlegen.
    - Done when: Die `DanielsVault.sln` enthaelt mindestens diese Projekte oder gleichwertige Zuschnitte:
       - `src/Nebenkosten.Cli` fuer CLI, Exitcodes und Dateisystem-Orchestrierung
       - `src/Nebenkosten.Core` fuer Domänenmodell, Validierung, Berechnung und Fehlerobjekte
       - `src/Nebenkosten.Rendering` fuer HTML/PDF-Ausgabe
       - `tests/Nebenkosten.Tests` fuer Unit-, Contract- und Regressionstests
3. [PENDING] V1-CLI-Vertrag final festlegen.
    - Done when: Der geplante Aufruf mindestens diese Form oder aequivalente Parameter hat:
       - `--input-json <path>` Pflicht
       - `--output-dir <path>` Pflicht
       - `--skip-pdf` optional
       - `--billing-date <yyyy-mm-dd>` optional; ohne Angabe = Laufdatum
    - Done when: Exitcodes festgelegt und getestet sind:
       - `0` Erfolg
       - `2` Schema-/Validierungsfehler
       - `3` Berechnungsfehler
       - `4` Rendering-/Ausgabefehler
       - `10` unerwarteter Systemfehler
4. [PENDING] Fehlervertrag aus der Spec in Core- und CLI-Schicht uebernehmen.
    - Done when: `Nebenkosten.Core` ein kanonisches Fehlerobjekt gemaeß Spec fuehrt und `Nebenkosten.Cli` bei Abbruch genau einen primaeren Fehler als strukturierte Ausgabe plus Ein-Zeilen-Zusammenfassung `FEHLER <error_code>: <message>` schreibt.
5. [PENDING] Input- und Validierungspfad in feste Ausfuehrungsstufen aufteilen.
    - Done when: Die Implementierungsreihenfolge im Code genau diese Stufen abbildet:
       - JSON laden und deserialisieren
       - Schema validieren
       - Referenzen validieren
       - fachliche Scope-/Kostenarten-Konsistenz pruefen
       - periodenbezogene Verbrauchs- und Vorauszahlungslogik pruefen
    - Done when: Jede Stufe eigene Fehlercodes bzw. Fehlerkategorien ausloest.
6. [PENDING] Core-Berechnung in deterministische Services schneiden.
    - Done when: Es mindestens folgende Services oder aequivalente Klassen gibt:
       - `ScopeResolver`
       - `ConsumptionCalculator`
       - `AllocationCalculator`
       - `RoundingAllocator`
       - `StatementAssembler`
    - Done when: jeder Service ohne Renderer und ohne Dateisystem unit-testbar ist.
7. [PENDING] Verbrauchsrechner auf Fallgruppen-Ebene konkretisieren.
    - Done when: eigene Codepfade und Tests bestehen fuer:
       - ista-Periodenablesung
       - manuelle Stichtagsdifferenz
       - Teilperiode bei Ein-/Auszug
       - Restverbrauch NE5
       - Waermepumpenstrom BE1
       - Heizkosten-HKV mit optionalem Umrechnungsfaktor
8. [PENDING] Ergebnisvertrag fuer `einzelabrechnung.json` final festlegen.
    - Done when: Das JSON mindestens diese Top-Level-Bloecke fuehrt:
       - `header`
       - `result_summary`
       - `consumption_items`
       - `cost_items`
       - `prepayments`
       - `notices`
       - `saldo`
    - Done when: `cost_items` pro Zeile mindestens `cost_type_id`, `cost_type_label`, `scope_type`, `scope_label`, `allocation_basis_type`, `scope_total_units`, `party_units`, `party_share`, `scope_total_amount_eur`, `party_amount_eur` und optional `days_prorated` enthaelt.
9. [PENDING] Dokumentenmodell fuer Render-Pflichtinhalte finalisieren.
    - Done when: Aus `einzelabrechnung.json` ohne Zusatzwissen direkt alle Spec-Pflichtbloecke gerendert werden koennen:
       - Kopf / Identifikation
       - Ergebnisuebersicht
       - Verbrauchs- und Ablesewerte
       - Gesamtkosten je relevantem Scope
       - Verteilerschluessel je Kostenart
       - Ihr Kostenanteil je Kostenart
       - Vorauszahlungsabzug
       - Hinweisblock
10. [PENDING] Renderstrategie verbindlich staffeln.
      - Done when: Phase 1 HTML-Rendering gegen den Mock stabil ist, Phase 2 PDF daraus oder aus demselben Datenmodell erzeugt und dieselben Inhaltsassertions besteht.
11. [PENDING] Testmatrix konkret auf Dateiebene und Verantwortlichkeit herunterbrechen.
      - Done when: `tests/Nebenkosten.Tests` mindestens diese Gruppen enthaelt:
         - `CliContractTests`
         - `ValidationTests`
         - `ConsumptionCalculatorTests`
         - `AllocationCalculatorTests`
         - `RoundingAllocatorTests`
         - `StatementAssemblerTests`
         - `RenderingContractTests`
         - `Regression2024Tests`
12. [PENDING] Oracle-Strategie explizit an Legacy-Artefakte anbinden.
      - Done when: 2024-Regressionen die Python-Fixtures/Quelldokumente und die in der Spec aufgelisteten Excel-Sollwerte nutzen, ohne Workbook-Daten in den operativen Lauf zurueckzufuehren.
13. [PENDING] Dokumenten- und Leserqualitaet als harte Gate-Kriterien fixieren.
      - Done when: Build/Test nur dann als v1-abnahmefaehig gilt, wenn neben T1-T10 auch folgende Gates gruen sind:
         - A4-/Seitenumbruch-Test
         - Pflichtfeld-Sichtbarkeit auf Dokumentebene
         - Alt/Neu/Differenz oder Formelherleitung pro relevantem Verbrauchsblock
         - Abkuerzungserklaerung / mieterverstaendliche Labels
         - keine irrelevanten Fremd-Scope-Daten
14. [PENDING] Implementierungsreihenfolge als Start-Backlog einfrieren.
      - Done when: Die ersten konkret ausfuehrbaren Schritte in dieser Reihenfolge feststehen:
         - Projekt/solution scaffolding
         - Fehlerobjekt + CLI contract
         - Input DTOs + Schema validation
         - Core domain model
         - Scope/consumption/allocation/rounding
         - statement JSON assembly
         - HTML rendering
         - PDF rendering
         - regression/oracle hardening

## Open Items
- Keine blocking oder non-blocking Open Items mehr im Planstand dieser Iteration.

## Verification Test Cases
1. Given eine frisch angelegte C#-Solutionstruktur, when der erste CLI-Smoke-Test ausgefuehrt wird, then akzeptiert die Anwendung `--input-json` und `--output-dir`, liefert bei gueltigem Input Exitcode `0` und schreibt Artefakte in den festgelegten Pfad.
2. Given ein strukturell defektes JSON, when die Anwendung startet, then wird mit Exitcode `2` genau ein primaerer Spec-konformer Fehler aus dem Bereich `NK-SCHEMA-*` ausgegeben.
3. Given ein fachlich gueltiger Datensatz ohne PDF-Flag-Ausgabe, when `--skip-pdf` gesetzt ist, then entsteht nur `einzelabrechnung.json`, aber kein PDF, bei identischem Rechenkernresultat.
4. Given der 2024-Kraft/Huehne-Fall, when der Rechenkern rechnet, then stimmen Verbrauch, Zeitanteiligkeit, Vorauszahlungen und Saldo mit dem Oracle bzw. dokumentierten Spec-Deltas ueberein.
5. Given der BE1-Waermepumpenfall, when `consumption_items` und das Renderdokument erzeugt werden, then wird die Ableitung als Formel und nicht als gefaelschter Einzelzaehlerstand ausgewiesen.
6. Given eine Partei mit mehreren Scope-Arten, when `cost_items` aufgebaut werden, then ist jede Kostenposition eindeutig einem `scope_type` und `scope_label` zugeordnet und fachlich nachvollziehbar renderbar.
7. Given ein mehrseitiges Dokument, when RenderingContractTests laufen, then bleiben alle Pflichtsektionen sichtbar, Tabellenzeilen intakt und das Dokument A4-tauglich.
8. Given bekannte Spec-vs-Excel-Abweichungen, when `Regression2024Tests` laufen, then erscheinen diese als erwartete Deltas mit Begruendung statt als unklassifizierte Fehler.

# Iteration 4

## Summary
- Der Plan wurde um die erkannte Spec-Luecke zum Excel2024-Stromkostenfluss erweitert (Worksheet `Stromkosten`: B-H als Tarifquelle, L-Q als Verteilungs-/Oracle-Bereich).
- Der aktuelle Umsetzungsstand wurde explizit in bereits umgesetzt vs. noch offen getrennt, damit die naechsten Schritte eindeutig priorisierbar sind.
- Schwerpunkt fuer die naechste Umsetzung ist mieterseitige Nachvollziehbarkeit der Stromkosten im Ergebnisobjekt und im Renderdokument.

## Requirements Snapshot
- Laufzeit bleibt JSON-only; Excel wird fuer Mapping/Fixture und Oracle genutzt.
- Tarifdaten aus Excel2024 `Stromkosten` B-H muessen reproduzierbar in `stromtarife` landen.
- Verteilungswerte aus Excel2024 `Stromkosten` L-Q sind als Regression/Delta-Referenz zu behandeln.
- Es werden keine vorab berechneten Stromkosten aus Excel oder JSON uebernommen; die Stromkostenberechnung erfolgt ausschliesslich im Rechenkern aus Verbrauchsdaten und Tarifzeilen.
- Die Einzelabrechnung muss fuer Stromkosten die Herleitung transparent ausweisen (Tarifparameter und Rechenschritte).

## Current State Snapshot
- [DONE] Domänen- und Eingabemodell kennt `stromtarife` inkl. Tarifmetadaten.
   - Evidence: `private/Vermietung/nebenkosten-abrechnung/dotnet/Nebenkosten.Core/Input/InputDto.cs`
- [DONE] Rechenkern kann Stromkosten tarifbasiert pro NE berechnen.
   - Evidence: `private/Vermietung/nebenkosten-abrechnung/dotnet/Nebenkosten.Core/Services/ConsumptionCalculator.cs` (`CalculateStromCostForNe`)
- [DONE] Stromkosten aus direkten Kostenbelegen sind im Allocation-Pfad abgedeckt.
   - Evidence: `private/Vermietung/nebenkosten-abrechnung/dotnet/Nebenkosten.Core/Services/AllocationCalculator.cs`
- [DONE] Spec-Ergaenzung fuer Excel2024-Stromkostenabbildung ist dokumentiert.
   - Evidence: `_specs/2026-03-24 Nebenkostenabrechnung Applikation.md` (Iteration-1-Ergaenzung)
- [DONE] Ergebnisobjekt (`einzelabrechnung.json`) enthaelt expliziten `stromkosten_anhang`-Block je Mietpartei mit Tarif-ID, Gueltigkeitszeitraum, Grundpreisanteil, Arbeitspreisanteil, kWh-Anteil, Summenbetrag und Herleitung.
   - Evidence: `private/Vermietung/nebenkosten-abrechnung/dotnet/Nebenkosten.Core/Output/StatementResult.cs` (`StromkostenAnhang`, `StatementStromkostenAnhangItem`)
- [DONE] HTML/PDF zeigt Tarifdetails (Grundpreis, Arbeitspreis, Tarifperiode, kWh, Kostenanteil, Herleitung) je Mietpartei im Abschnitt `3. Stromkosten-Anhang`.
   - Evidence: `private/Vermietung/nebenkosten-abrechnung/dotnet/Nebenkosten.Rendering/Templates/einzelabrechnung.html`
- [DONE] Regression gegen Excel2024 `Stromkosten` L-Q als eigener Testvertrag T12 implementiert; Deltas werden je Mietpartei als `gleich`, `bekanntes Excel-Delta` oder `Implementierungsfehler` klassifiziert.
   - Evidence: `private/Vermietung/nebenkosten-abrechnung/tests/Nebenkosten.Tests/Regression2024Tests.cs` (`T12_ShouldClassifyStromDeltaVsExcelOraclePerMietpartei`)

## Action Plan
1. [DONE] Spec-Luecke zum Excel2024-Stromkostenfluss in den Plan uebernommen und operationalisiert.
    - Done signal: Anforderungen B-H (Quelle) und L-Q (Oracle) sind als eigener Planfokus dokumentiert.
2. [DONE] Datenaufbereitungspfad fuer Excel2024 -> Input-JSON um einen expliziten Mapping-Check fuer `stromtarife` erweitert.
   - Evidence: Einmalige Uebernahme aus `Nebenkostenabrechnung_2024.xlsx`, Worksheet `Stromkosten` Spalten B-H in `data/2024/input_tariff_from_excel.json`.
   - Evidence: Direkte NE-Stromkostenbelege wurden fuer den Tarifmodus entfernt; Stromkosten entstehen nur noch aus Verbrauchsdaten + `stromtarife`.
   - Evidence: Tarifbasierte Einzelabrechnungen erzeugt in `output/2024-from-excel-tariff-2026-03-26_0940-2026-03-26_0940`.
3. [DONE] Ergebnisvertrag erweitern: eigener Block fuer Stromkosten-Herleitung je Mietpartei.
    - Evidence: `StatementResult.cs` → `StromkostenAnhang: List<StatementStromkostenAnhangItem>` mit Tarif-ID, Gueltigkeitszeitraum, Grundpreisanteil, Arbeitspreisanteil, kWh-Anteil und Summenbetrag.
4. [DONE] Assembler/Rechenkern-Output verbinden.
    - Evidence: `ConsumptionCalculator.cs` → `CalculateStromCostBreakdownForNe()` liefert `StromCostBreakdownEntry`-Liste; `StatementAssembler.cs` schreibt diese als `stromkosten_anhang` ins Statement.
5. [DONE] Rendervertrag fuer Mietersicht erweitern.
    - Evidence: `einzelabrechnung.html` → bedingter Abschnitt `3. Stromkosten-Anhang` mit Tarifparametern und Rechenschrittherleitung; Vorauszahlungen auf Abschnitt 4 verschoben.
6. [DONE] Regressionstest fuer Excel2024 `Stromkosten` L-Q ergaenzen.
    - Evidence: `Regression2024Tests.cs` → `T12_ShouldClassifyStromDeltaVsExcelOraclePerMietpartei` klassifiziert je Delta `gleich`, `bekanntes Excel-Delta` (NE2: +44.75) oder `Implementierungsfehler`.
7. [DONE] Dokumenthinweis auf technische Detaildatei entfernt/umformuliert.
    - Evidence: `einzelabrechnung.html` → Hinweis auf `"technische Detaildatei"` entfernt; `RenderingContractTests.cs` → `ShouldNotClaimTechnicalDetailFileExists` sichert dies als Regressionsschutz ab.

## Open Items
- [DECISION NON-BLOCKING] Soll die Strom-Detailaufschluesselung direkt im Hauptdokument stehen oder als zusaetzliches technisches Beiblatt mit Kurzreferenz im Hauptdokument?

## Verification Test Cases
1. Given Excel2024-Import mit Tarifzeilen in `Stromkosten` B-H, when das Input-JSON erzeugt wird, then ist `stromtarife[]` nicht leer und feldvollstaendig.
2. Given eine Mietpartei mit tarifbasierten Stromkosten, when `einzelabrechnung.json` erzeugt wird, then enthaelt der Stromblock Grundpreis-, Arbeitspreis- und kWh-Herleitung.
3. Given dieselbe Mietpartei, when HTML/PDF gerendert wird, then kann der Strombetrag aus ausgewiesenen Tarifparametern und Anteilen nachvollzogen werden.
4. Given Excel2024 `Stromkosten` L-Q als Oracle, when Regression laeuft, then werden Deltas je Mietpartei klassifiziert und dokumentiert.
5. Given ein aus Excel erzeugtes Input-JSON, when der Strompfad validiert wird, then existiert kein vorab berechnetes Stromkostenfeld als operative Eingabe und die Kosten werden erst im Rechenkern erzeugt.

## History
| Date | Iteration | Author | Delta |
|---|---|---|---|
| 2026-03-25 | 1 | Copilot (GPT-5.3-Codex) | Initialer Implementierungsplan aus Spec abgeleitet |
| 2026-03-25 | 2 | Copilot (GPT-5.4) | Plan auf Umsetzungsreife nachgeschaerft: Entscheidungen operationalisiert, Render-Pflichten und Teststrategie konkretisiert |
| 2026-03-25 | 3 | Copilot (GPT-5.4) | Plan auf konkrete Ausfuehrungsvertraege, C#-Projektzuschnitt und implementation-ready Start-Backlog verdichtet |
| 2026-03-25 | 4 | Copilot (GPT-5.3-Codex) | Spec-Luecke zu Excel2024-Stromkosten operationalisiert; klarer Done/Pending-Status fuer Stromtarif-Transparenz und L-Q-Regression ergänzt |
| 2026-03-26 | 5 | Copilot (Claude Sonnet 4.6) | Items 3-7 implementiert und als DONE markiert: `stromkosten_anhang`-Block im Ergebnisvertrag, Assembler/Rechenkern verbunden (`StromCostBreakdownEntry`), HTML-Template um Abschnitt 3 Stromkosten-Anhang erweitert, T12-Regression mit Delta-Klassifizierung, Detaildatei-Hinweis entfernt. Zusaetzlich: Validierungsguardrails NK-VALID-004 (StromTariffRequired) und NK-VALID-005 (StromInputModeConflict) ergaenzt. 46/46 Tests gruen. Item 2 (Excel→JSON Mapping-Check) bleibt PENDING (kein Excel-Importpfad im .NET-Projekt). |
| 2026-03-26 | 6 | Copilot (GPT-5.3-Codex) | Item 2 einmalig praktisch umgesetzt: Tarife aus Excel2024 Worksheet `Stromkosten` (B-H) in eigenes Tarif-Input uebernommen (`input_tariff_from_excel.json`), Tarifmodus ohne direkte NE-Strombelege gefahren, 5 Einzelabrechnungen neu erzeugt. |
