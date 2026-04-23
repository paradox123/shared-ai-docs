# Nebenkostenabrechnung Einzelabrechnung Implementierungsplan

Bezugsspezifikation:
- `/Users/dh/Documents/DanielsVault/_shared/_specs/2026-03-23 Nebenkostenabrechnung Einzelabrechnung.md`

Bezug zur bestehenden Pipeline-Kurzreferenz:
- `/Users/dh/Documents/DanielsVault/_shared/_specs/2026-03-14 Nebenkostenabrechnung Pipeline.md`
  - insbesondere Iteration 13 = autoritative Kurzreferenz
  - Iteration 14 = operative Checkliste


# Iteration 1

## Summary
- Aus der fertigen Einzelabrechnungs-Spec wurde ein separater, umsetzungsorientierter Plan abgeleitet.
- Der Plan trennt klar zwischen:
  - bereits vorhandener Pipeline-Basis,
  - noch fehlenden Einzelabrechnungs-v2-Bausteinen,
  - nicht-blockierenden Restfragen aus der Spec.
- Der Plan ist **implementation-ready**, weil keine blocking Spec-Entscheidungen mehr offen sind und die naechsten Arbeitspakete eindeutig sind.

## Requirements Snapshot
- Die Einzelabrechnung muss fuer einen durchschnittlichen Mieter gedanklich und rechnerisch nachvollziehbar sein.
- Pflichtinhalte:
  - Abrechnungszeitraum
  - Ergebnisuebersicht (Gesamtkosten, Vorauszahlungen, Nachzahlung/Guthaben)
  - Verbrauchs-/Ablesewerte, soweit fuer die Partei relevant
  - Gesamtkosten je **relevantem Umlagescope**, nicht blind je Gesamtliegenschaft
  - Verteilerschluessel in lesbarer Form
  - konkrete Mieteranteilsberechnung
  - Hinweis auf Belegeinsicht
- Heiz-/Warmwasserkosten muessen **scope-richtig** dargestellt werden, ohne verwirrende Vermischung irrelevanter Verbrauchseinheiten.
- Die Einzelabrechnung bleibt bewusst schlanker als das ista-Beispiel; der technische Tiefenpfad bleibt im Pruefbericht.
- Zusaetzlich zur Einzelabrechnung und zum Pruefbericht entsteht ein **separates Anschreiben** mit Zahlungsziel/Kontoverbindung.
- Aenderungen an Output, Templates oder Rechenkern duerfen nur zusammen mit bestehenden Pipeline-Tests und Reader-/Oracle-Regressionen erfolgen.

## Current State Snapshot
- `nebenkosten_pipeline/output_writer.py` erzeugt aktuell `statement_payload_v1` und `audit_payload`; die Einzelabrechnung rendert heute eine relativ flache `line_items`-Tabelle plus Ergebnisbox.
- `renderer.py` und `templates/statement_template_v1.typ` erzeugen bereits PDF-Artefakte ueber Typst; der Grund-Renderpfad `JSON -> Typst -> PDF` ist vorhanden.
- Die Pipeline erzeugt bereits:
  - `statement_payload_{jahr}.json`
  - `audit_payload_{jahr}.json`
  - `einzelabrechnung_{jahr}.pdf`
  - `pruefbericht_{jahr}.pdf`
- Der technische Datenunterbau ist deutlich reicher als das aktuelle Hauptdokument:
  - `cost_entries`
  - `allocation_lines`
  - `billing_parties`
  - `monthly_costs`
  - `ww_audit`
  - `meter_observations`
  - `receipt_documents`
  - `canonical_snapshot.json`
- Die bestehende Pipeline-Testsuite ist bereits umfangreich und laeuft; sie ist die Pflichtbasis fuer jede spaetere Einzelabrechnungs-v2-Aenderung.
- Noch nicht vorhanden:
  - `statement_payload_v2` mit Scope-/Berechnungsstruktur
  - Einzelabrechnung mit expliziten Kostenartenblöcken und mieterlesbarer Schluesselerklaerung
  - separates Anschreiben
  - Reader-/Layout-Oracles fuer die v2-Ausgabe

## Action Plan
1. [DONE] Bestehenden Render- und Artefaktpfad als Basis beibehalten — Evidence: `output_writer.py`, `renderer.py`, Typst-Templates und PDF-Ausgaben existieren bereits; die Pipeline-Spec legt `JSON -> Typst -> PDF` verbindlich fest.
2. [DONE] Produktentscheidungen fuer Einzelabrechnung v2 aus der Spec uebernehmen — Evidence: In der Spec sind Scope-Regel, CO2-Block im Hauptdokument, separates Anschreiben und Pflicht-Regressionen bereits als resolved decisions festgehalten.
3. [PENDING] `statement_payload_v2` als neues Dokumentenmodell definieren — Done when: ein Payload-Schema mit `document_header`, `summary_box`, `meter_sections`, `cost_type_sections`, `subtotals`, `prepayment_section`, `notices` und `document_policy` in Code und Tests verankert ist.
4. [PENDING] Scope-richtige Kostenblöcke aus bestehenden Pipeline-Daten ableiten — Done when: `output_writer.py` Kostenarten nicht nur als flache `line_items`, sondern als Blöcke mit `scope_label`, Scope-Gesamtkosten, Schlüssel, Einheiten/Quote und Mieterbetrag erzeugt.
5. [PENDING] Parteirelevante Verbrauchs- und Ablesewerte in die Einzelabrechnung heben — Done when: für relevante Parteien Meter-/Verbrauchssektionen aus `monthly_costs`, `ww_audit`, `meter_observations` und vorhandenen Verbrauchsdaten im Statement-Output erscheinen.
6. [PENDING] `statement_template_v2` in Typst bauen und `renderer.py` darauf erweitern — Done when: die neue PDF auf Seite 1 klar Zeitraum, Partei, Ergebnisbox und erste Kosten-/Verbrauchsabschnitte zeigt und das alte Template nicht mehr die Zielversion ist.
7. [PENDING] Mieterlesbare Schlüssel- und Berechnungstexte einführen — Done when: technische Codes wie `heating_consumption_share` oder `persons_share_excluding_vacancy_with_dayshare` im Hauptdokument nur noch als verständliche Beschreibungen erscheinen.
8. [PENDING] separates `cover_letter_payload` plus Anschreiben-Template implementieren — Done when: pro renderbarer Mieter zusätzlich `anschreiben_{jahr}.pdf` erzeugt wird und Zahlungsziel/Kontoverbindung aus dem Hauptdokument ausgelagert sind.
9. [PENDING] Reader-/Oracle-Regressionen in die bestehende Pipeline-Testsuite integrieren — Done when: Tests für Seite-1-Lesbarkeit, Heizkosten-Scope, Kostenarten-Transparenz, Vorauszahlungsabzug, Belegeinsicht und Anschreiben in `tests/test_pipeline_tdd.py` oder gleichwertiger Pipeline-Testlandschaft laufen.
10. [PENDING] Vergleich gegen die Referenzwelt verankern — Done when: das ista-Beispiel 2023 als Inhalts-/Pflichtfeld-Oracle und die Excel-/Einzelabrechnungswelt 2024 als Werte-Orakel in den Test-/Review-Schritten ausdrücklich genutzt werden.
11. [PENDING] Fixture- und Snapshot-Artefakte auf v2 aktualisieren — Done when: `statement_payload`, PDFs und relevante Snapshot-/Audit-Artefakte konsistent mit dem neuen Dokumentenmodell regeneriert und geprüft sind.
12. [PENDING] Abschlussreview auf Leserqualitaet durchführen — Done when: ein frischer Reader-Test bestätigt, dass Zeitraum, Kosten, Scope, Schlüssel, Mieteranteil und Vorauszahlungen ohne Zusatzkontext gefunden werden können.

## Open Items
- [MISSING SPEC NON-BLOCKING] Juristische Endformulierung für den Belegeinsicht-Hinweis und ggf. optionale Begleittexte im Anschreiben final abstimmen; die aktuelle Spec erlaubt Umsetzung mit Platzhalter-/Arbeitsfassung, aber nicht die endgültige Formulierungssicherheit.
- [MISSING NON-BLOCKING] Festlegen, aus welchen konkreten Datenquellen die v2-Metersektion je Kostenart priorisiert gespeist wird, falls mehrere konkurrierende Herkünfte gleichzeitig vorliegen (z. B. OCR-Zählerbeobachtung vs. bereits normalisierte Verbrauchswerte).
- [DECISION NON-BLOCKING] Ob `statement_template_v2.typ` als neue Datei neben `statement_template_v1.typ` geführt oder `v1` direkt abgelöst werden soll.

## Verification Test Cases
1. Given die aktuelle v1-Einzelabrechnung mit flacher Positionstabelle, when `statement_payload_v2` und `statement_template_v2` umgesetzt werden, then zeigt Seite 1 für jede Mieterabrechnung direkt Partei, Zeitraum, Gesamtkosten, Vorauszahlungen und Nachzahlung/Guthaben.
2. Given Heiz-/Warmwasserkosten mit fachlich begrenztem Umlagescope, when die v2-Einzelabrechnung gerendert wird, then werden nur die relevanten Scope-Gesamtkosten und keine irreführend vermischten irrelevanten Verbrauchseinheiten angezeigt.
3. Given eine Kostenart wie Grundsteuer, Müll, Kalt-/Abwasser oder Brennstoffkosten, when sie in der v2-Einzelabrechnung erscheint, then sind Scope, Gesamtkosten des Scopes, Verteilerschlüssel, Ihre Einheiten/Quote und Ihr Betrag explizit sichtbar.
4. Given vorhandene Zahlungen in der Pipeline, when die v2-Einzelabrechnung erzeugt wird, then wird `bereits gezahlt` sichtbar vom Kostenblock getrennt und korrekt gegen die Gesamtkosten verrechnet.
5. Given eine finale Mieterabrechnung, when die Output-Artefakte geschrieben werden, then entstehen `einzelabrechnung_{jahr}.pdf`, `pruefbericht_{jahr}.pdf` und zusätzlich `anschreiben_{jahr}.pdf` im Parteiordner.
6. Given Änderungen an Output-Writer, Renderer, Templates oder Rechenkern, when die Pipeline-Tests laufen, then bestehen sowohl die bestehende Pipeline-Regression als auch die neuen Reader-/Oracle-Tests gemeinsam.

# Iteration 2

## Summary
- Der Plan wurde nach Review gegen Spec und Code geschärft.
- Die vorher zu groben Punkte wurden in konkrete Umsetzungsentscheidungen übersetzt:
  - Migrationsstrategie `v1 -> v2`
  - exakteres `statement_payload_v2`-Gerüst
  - Gruppierungsregel fuer Scope-Kostenbloecke
  - Prioritaet der Meter-/Verbrauchsdaten fuer das Hauptdokument
  - CO2-Einschlussregel
  - stufenweiser Test- und Oracle-Pfad
- Der Plan ist in dieser Iteration **implementation-ready**, weil keine blocking Spec-Fragen mehr offen sind und die nächsten Schritte ohne weiteres Requirements-Raten ausführbar sind.

## Requirements Snapshot
- Die Einzelabrechnung v2 muss die Spec-Struktur aus Identifikation/Ergebnis, parteirelevanten Verbrauchswerten, scope-richtigen Kostenarten, Teilsummen und Hinweisen sichtbar machen.
- Die Einzelabrechnung darf fachlich irrelevante Fremd-Scope-Daten nicht mit anzeigen; besonders Heiz-/Warmwasserkosten sind nur im relevanten Umlagescope darzustellen.
- Das Hauptdokument bleibt mieterlesbar und knapp; technische Konflikte, OCR-Spuren und tiefe Herleitungen bleiben im Prüfbericht.
- Zahlungsziel und Kontoverbindung bleiben außerhalb des Hauptdokuments und werden nur im separaten Anschreiben geführt.
- Bestehende Pipeline-Tests, Excel-/Bestandsorakel 2024, ista-Inhaltsorakel 2023 und neue Reader-/Snapshot-Tests bilden zusammen die Pflicht-Gates.

## Current State Snapshot
- `_build_statement_payload()` in `output_writer.py` liefert heute nur `schema_version`, `title`, `property_line`, `party_line`, `period_line`, `line_items`, `totals`, `payments`, `writeoff_summary` und `notes`; es gibt noch keine gruppierten Kostenblöcke, keine Metersektionen und keine Subtotals.
- `render_party_documents()` in `renderer.py` rendert aktuell genau zwei Dokumente (`statement`, `audit`) und verdrahtet das Hauptdokument hart auf `statement_template_v1.typ`.
- `statement_template_v1.typ` kann aktuell nur Titel, Objekt/Partei/Zeitraum, eine flache Tabelle, eine Summenzeile, Zahlungen und Hinweise ausgeben.
- Die bestehende Testsuite prüft bereits Existenz der Payloads/PDFs, einzelne `line_items`, Zahlungs-/Review-Verhalten, Vacancy-Outputs und Meter-Reconciliation; sie prüft aber noch keine `statement_payload_v2`-Struktur und kein Anschreiben.
- Die Codebasis hat bereits die noetigen Rohdaten fuer v2:
  - `allocation_lines` fuer verteilte Kosten
  - `totals` und `already_paid_eur` fuer Ergebnisbox
  - `monthly_costs`, `ww_audit` und strukturierte Inputs fuer billed consumption
  - `meter_observations` fuer Provenienz/Anzeigedaten

## Action Plan
1. [DONE] Bestehenden Renderpfad und Artefakt-Namen als Migrationsanker festhalten — Evidence: `statement_payload_{jahr}.json`, `audit_payload_{jahr}.json`, `einzelabrechnung_{jahr}.pdf` und `pruefbericht_{jahr}.pdf` werden bereits erzeugt; diese Dateinamen bleiben waehrend der v2-Migration stabil.
2. [DONE] Produktscope aus der Spec uebernehmen — Evidence: Scope-Richtigkeit, CO2 im Hauptdokument, separates Anschreiben und Pflicht-Regressionen sind in der Spec bereits als resolved decisions festgelegt.
3. [PENDING] Kompatible v1->v2-Migrationsstrategie festschreiben — Done when: die Umsetzung intern `statement_payload_v2` und `statement_template_v2.typ` einfuehrt, aber waehrend der Migration weiterhin dieselben Artefakt-Dateinamen ausliefert; ein Rueckbau von v1-internen Hilfsstrukturen erfolgt erst nach gruener Regression.
4. [PENDING] `statement_payload_v2` als expliziten Vertrag definieren — Done when: das Payload mindestens diese Top-Level-Bloecke besitzt und Tests auf ihre Schluessel pruefen:
   - `document_header` mit `title`, `property_line`, `party_name`, `unit_id`, `statement_kind`, `billing_date`, `period_start`, `period_end`, `period_label`
   - `summary_box` mit `total_costs_eur`, `already_paid_eur`, `result_label`, `result_value_eur`
   - `meter_sections[]` mit `section_label`, `meter_type`, `meter_id`, `unit`, `reading_old`, `reading_new`, `difference`, `factor`, `normalized_value`, `source_label`
   - `cost_type_sections[]` mit `cost_type_id`, `cost_type_label`, `scope_type`, `scope_id`, `scope_label`, `scope_reason`, `allocation_scope_total_eur`, `allocation_scope_units_total`, `tenant_units`, `tenant_share_fraction`, `tenant_amount_eur`, `allocation_key_text`, `calculation_text`, `items[]`
   - `subtotals[]` mit gruppierten Zwischensummen
   - `notices[]`
   - `document_policy` mit `include_co2_block`, `include_belegeinsicht_notice`, `separate_cover_letter`
5. [PENDING] Gruppierungs- und Scope-Regel fuer `cost_type_sections[]` konkretisieren — Done when: die Hauptdarstellung Kostenzeilen sichtbar nach `cost_type_id + scope_type + scope_id` gruppiert, `scope_label` lesbar erzeugt (z. B. Objekt, Berechnungseinheit, direkte Zuordnung) und `calculation_text` erklaert, welcher Topf verteilt wird und warum genau dieser Partei-Anteil entsteht.
6. [PENDING] Subtotal- und Ergebnisregeln definieren — Done when: `subtotals[]` mindestens die Buckets `heating_hotwater`, `house_operating_costs`, `direct_party_costs` und `grand_total` abbilden und die Ergebnisbox immer `Gesamtkosten -> Vorauszahlungen -> Nachzahlung/Guthaben` in dieser Reihenfolge zeigt.
7. [PENDING] Meter-/Verbrauchsdaten-Prioritaet als Ausfuehrungsannahme fixieren — Done when: fuer das Hauptdokument billed values immer primaer aus den normalisierten/abrechnungswirksamen Quellen kommen (`monthly_costs`, `ww_audit`, strukturierte Verbrauchsinputs bzw. daraus abgeleitete Resultate), `meter_observations` nur fuer Meterkennungen/Lesewerte/Provenienz genutzt werden und Konflikte/OCR-Unklarheiten im Zweifel nur im Prüfbericht oder als Review-Item auftauchen.
8. [PENDING] Teiljahres- und Dayshare-Transparenz in die Darstellungslogik aufnehmen — Done when: `period_start`/`period_end` aus der Partei im Header landen und `calculation_text` bei dayshare-/teiljahresbezogenen Formeln explizit den zeitanteiligen Bezug erkennen laesst, statt ihn nur indirekt im Formelcode zu verstecken.
9. [PENDING] CO2-Einschlussregel operationalisieren — Done when: der Hauptbeleg einen CO2-Block genau dann enthaelt, wenn die Partei einen von null verschiedenen CO2-bezogenen Kostenanteil traegt; fuer Null-/Nichtvorhanden-Faelle wird kein leerer CO2-Block gerendert und mindestens ein Include- und ein Omit-Test existieren.
10. [PENDING] Lesbare Schluesseltexte als feste Mapping-Liste planen — Done when: die heute im Audit sichtbaren `formula_code`-Werte in einer expliziten Mapping-Tabelle auf verstaendliche Hauptdokument-Texte abgebildet sind und Tests fuer mindestens die heute sichtbaren Kernfaelle (`persons_share_excluding_vacancy_with_dayshare`, Heizverbrauchsanteile, direkte Zuordnung, Strom-Monatskostenpfad) existieren.
11. [PENDING] `cover_letter_payload` als separaten Vertrag und Renderpfad definieren — Done when: ein drittes Artefakt vorgesehen ist mit mindestens `salutation`, `party_name`, `period_label`, `result_label`, `result_value_eur`, `payment_due_text`, `bank_details_block`, `belegeinsicht_reference`, `attachments_overview`; `renderer.py` kann dieses Payload optional mitschreiben/rendern, ohne den Prüfberichtspfad zu verändern.
12. [PENDING] Template-/Renderer-Sequenz in Phasen umsetzen — Done when: Phase A nur Payload/Tests vorbereitet, Phase B `statement_template_v2.typ` und Renderer-Verdrahtung ergänzt, Phase C das Anschreiben ergänzt und Phase D erst danach Fixtures/Snapshots aktualisiert; jede Phase bleibt für sich testbar.
13. [PENDING] Reader-/Regressionstests in vier Stufen planen — Done when: die Testsuite explizit trennt zwischen:
   - Schema-Contract-Tests fuer `statement_payload_v2`
   - Reader-Tests fuer Seite 1 und Kostenblock-Lesbarkeit
   - Inhalts-/Oracle-Tests gegen Excel 2024 und ista 2023
   - Artefakt-/Render-Tests fuer Statement, Prüfbericht und Anschreiben
14. [PENDING] Excel-/ista-Oracles ausformulieren — Done when: fuer mindestens eine Partei aus 2024 ein automatisierter oder halbautomatisierter Vergleich der Kernwerte (`Gesamtkosten`, `bereits gezahlt`, `Ergebnis`, ausgewaehlte Kostenarten) gegen die bisherige Excel-/Einzelabrechnungswelt dokumentiert ist und das ista-PDF 2023 als Pflichtfeld-Checkliste fuer Sichtbarkeit verwendet wird.
15. [PENDING] Fixture-Refresh erst nach gruener Vertrags- und Reader-Regression durchfuehren — Done when: neue Snapshot-/PDF-Artefakte nur nach bestandenem Payload-, Reader- und Oracle-Lauf aktualisiert werden; damit bleibt die Reihenfolge `Code -> Tests gruen -> Fixtures erneuern` explizit verbindlich.
16. [PENDING] Abschlussreview als frischen Leser-Test fest einplanen — Done when: ein Reviewer ohne Codekontext in der finalen PDF Seite 1 und den Kostenabschnitten Zeitraum, Ergebnis, relevanten Scope, Verteilerschluessel, Partei-Anteil und Hinweis auf Belegeinsicht finden kann.

## Open Items
- [MISSING SPEC NON-BLOCKING] Juristische Endformulierung des Belegeinsicht-Hinweises und die exakte Endfassung optionaler Anschreiben-Formulierungen bleiben Spec-Thema; die Umsetzung darf bis dahin mit einer klar als Arbeitsfassung markierten Formulierung vorgehen.

## Verification Test Cases
1. Given die aktuelle Pipeline mit `statement_payload_v1` und `statement_template_v1.typ`, when die v2-Migration beginnt, then bleiben `statement_payload_{jahr}.json` und `einzelabrechnung_{jahr}.pdf` als Dateinamen stabil, waehrend der interne Vertrag auf `statement_payload_v2` umgestellt wird.
2. Given eine Partei mit Heiz-/Warmwasserkosten in einem begrenzten Umlagescope, when `cost_type_sections[]` gerendert werden, then enthaelt der Hauptbeleg nur den relevanten Scope-Topf, den Schluessel, die Partei-Einheiten/Quote und den Partei-Betrag ohne irrelevante Fremd-Scope-Daten.
3. Given eine Partei mit bereits abgeleiteten billed consumption-Werten und zusaetzlichen `meter_observations`, when die Metersektion erzeugt wird, then stammen die abrechnungsrelevanten Zahlen aus den normalisierten Ergebnisquellen und `meter_observations` dienen nur der Identifikation/Provenienz; Konfliktfaelle erscheinen nicht als ungepruefter Rechnungswert im Hauptdokument.
4. Given eine Teiljahrespartei oder eine dayshare-bezogene Formel, when die v2-Einzelabrechnung erzeugt wird, then zeigen Header und `calculation_text` den zeitlichen Bezug explizit und verstecken ihn nicht nur im internen Formelcode.
5. Given eine Partei mit und ohne CO2-Anteil, when der Hauptbeleg gerendert wird, then erscheint genau im relevanten Fall ein CO2-Block und im irrelevanten Fall kein leerer Platzhalter.
6. Given die v2-Rendererweiterung, when `compile_pdf=True` ausgefuehrt wird, then entstehen Statement, Prüfbericht und Anschreiben als drei getrennte PDF-Artefakte; bei `compile_pdf=False` werden mindestens die zugehoerigen Payloads geschrieben.
7. Given die 2024-Referenzwelt und das ista-Beispiel 2023, when die Reader-/Oracle-Tests laufen, then stimmen Kernwerte gegen das Werte-Orakel und Pflichtfelder gegen das Inhalts-Orakel, ohne das ista-Layout kopieren zu muessen.
8. Given geaenderte Payload-, Template- oder Rendererlogik, when die Regression laeuft, then werden zuerst Vertrags-/Reader-/Oracle-Tests und erst danach Fixture-Refreshes akzeptiert.

# Iteration 3

## Summary
- Diese Iteration schliesst den zuletzt offenen Umsetzungs-Gap fuer `meter_sections[]`.
- Die Planstelle "Datenquellen-Prioritaet fuer Meter-/Verbrauchswerte" wurde auf Feldniveau operationalisiert:
  - welche bestehenden Resultat-Daten in das Hauptdokument duerfen,
  - welche Felder dabei bewusst `null` bleiben duerfen,
  - wann ein Meterblock im Hauptdokument **nicht** erzeugt werden darf,
  - wie `canonical_meters` und `meter_observations` nur zur Identifikation/Provenienz verwendet werden.
- Der Gesamtplan bleibt implementation-ready; diese Iteration schärft nur die letzte relevante Ausfuehrungsstelle.

## Requirements Snapshot
- Die Einzelabrechnung soll nur parteirelevante Verbrauchswerte zeigen und keine technisch klingenden, aber abrechnungslos eingeblendeten Meterfragmente.
- Das Hauptdokument darf keine Alt-/Neu-/Differenzwerte erfinden, wenn diese in der aktuellen Pipeline nicht als abrechnungswirksame Daten vorliegen.
- `meter_sections[]` muessen deshalb billed consumption und Meteridentifikation sauber trennen:
  - abrechnungswirksame Mengen aus normalisierten Rechenkernquellen,
  - Zählerkennung und Provenienz aus `canonical_meters`/`meter_observations`,
  - Konflikte/Missing-Matches nur im Prüfbericht bzw. als Review-Item.
- Leere oder rein technische Metersektionen ohne belastbaren Rechnungswert gehoeren nicht in die MVP-Einzelabrechnung.

## Current State Snapshot
- `MonthlyCost` liefert aktuell je Monat nur Strom-Kosten- und Verbrauchsableitungen (`month`, `verbrauch_pro_tag_kwh`, `monat_kosten_eur`, optional `reported_monat_kosten_eur`), aber keine Alt-/Neu-Ablesestaende und keine Meter-ID.
- `ww_audit` liefert für NE1/NE2 abrechnungswirksame Warmwasser-Werte (`ww_m3_ne1`, `ww_m3_ne2`, `ww_total_be1`, `cost_ne1`, `cost_ne2`, `factor_year`), aber ebenfalls keine Alt-/Neu-Staende.
- `MeterObservation` liefert aktuell nur `observed_meter_id`, `canonical_meter_id`, `match_status`, `meter_type`, `unit_id`, also Identifikation/Matchingstatus, jedoch keine Verbräuche oder Ablesewerte.
- `CanonicalMeter` liefert `canonical_meter_id`, `unit_id`, `meter_type`, `unit`, `external_id`, `aliases`, also die richtige Quelle fuer Meterkennung und Einheit.
- Daraus folgt: mit der heutigen Codebasis koennen im Hauptdokument belastbar angezeigt werden:
  - Strom-Verbrauchs-/Kostenpfade aus `monthly_costs`
  - Warmwasser-Mengen fuer NE1/NE2 aus `ww_audit`
  - Meterkennung/Einheit aus `canonical_meters`
  - Beobachtungs-/Matchingprovenienz aus `meter_observations`
- Nicht belastbar verfuegbar sind heute im Hauptdokument:
  - Alt-/Neu-Staende fuer Strom/WW/KW/HKV
  - Kaltwasser- oder HKV-Verbrauchswerte, sofern sie nicht spaeter als normalisierte Rechenkernquelle eingefuehrt werden

## Action Plan
1. [DONE] Datenquellenrollen technisch abgrenzen — Evidence: `MonthlyCost`, `WwDistribution`/`ww_audit`, `CanonicalMeter` und `MeterObservation` zeigen in den aktuellen Modellen bereits klar getrennte Verantwortungen fuer billed values vs. Meteridentifikation vs. Matchingstatus.
2. [DONE] Nicht vorhandene Ablesedaten explizit als Nicht-Ziel fuer die aktuelle MVP-Ausgabe anerkennen — Evidence: weder `MonthlyCost` noch `ww_audit` noch `MeterObservation` enthalten heute Alt-/Neu-/Differenzwerte; diese duerfen daher im Hauptdokument nicht synthetisch erzeugt werden.
3. [PENDING] Render-Eignungsregel fuer `meter_sections[]` festschreiben — Done when: ein Meterblock nur dann erzeugt wird, wenn fuer die Partei mindestens ein abrechnungswirksamer normierter Wert existiert; reine `meter_observations` ohne billed value erzeugen **keinen** Hauptdokument-Block.
4. [PENDING] Feldmapping fuer Strom-Sektionen definieren — Done when: fuer Parteien mit `result.monthly_costs[party.party_name]` genau eine Strom-Sektion erzeugt wird mit:
   - `section_label = "Strom"`
   - `meter_type = "electricity"`
   - `meter_id` bevorzugt aus `canonical_meters` fuer `unit_id == party.unit_id` und passendem `meter_type`, sonst `null`
   - `unit = "kWh"`
   - `normalized_value = Summe(verbrauch_pro_tag_kwh * Tage_im_Monat)`
   - `source_label` aus der Herkunft (`structured_inputs monthly_costs` oder workbook-basierter Monatskostenpfad)
   - `reading_old`, `reading_new`, `difference`, `factor` = `null`, solange keine belastbaren Ablesewerte/Faktoren im Rechenkern existieren
5. [PENDING] Feldmapping fuer Warmwasser-Sektionen definieren — Done when: fuer Parteien in `NE1`/`NE2` bei vorhandenem `ww_audit` genau eine Warmwasser-Sektion erzeugt wird mit:
   - `section_label = "Warmwasser"`
   - `meter_type = "warm_water"`
   - `meter_id` bevorzugt aus `canonical_meters` fuer `unit_id == party.unit_id` und passendem `meter_type`, sonst `null`
   - `unit = "m3"`
   - `normalized_value = ww_m3_ne1` oder `ww_m3_ne2`
   - `source_label = "ww_audit"`
   - `factor = null` im Hauptblock; der dynamische Jahresfaktor bleibt Berechnungs-/Prüfberichtskontext, solange er nicht direkt der angezeigte Parteienverbrauch ist
   - `reading_old`, `reading_new`, `difference` = `null`, solange keine belastbaren Staende vorliegen
6. [PENDING] Meter-ID-Prioritaet und Fallbacks fixieren — Done when: die Reihenfolge fuer `meter_id` dokumentiert und getestet ist:
   - zuerst `canonical_meters.external_id` fuer passende `unit_id` + fachlich passenden `meter_type`
   - danach bei fehlendem Canonical-Match ein eindeutiger `meter_observations.observed_meter_id` mit `match_status in {"exact", "alias"}` fuer dieselbe Partei/Zaehlerart
   - sonst `null`
   Konflikt- oder Missing-Matches duerfen nie ungeprueft als Hauptdokument-Meter-ID erscheinen.
7. [PENDING] Nullability-Regeln fuer `meter_sections[]` vertraglich machen — Done when: Tests absichern, dass `reading_old`, `reading_new`, `difference`, `factor` bewusst `null` sein duerfen, waehrend `normalized_value`, `unit` und `source_label` fuer gerenderte Sektionen Pflichtfelder bleiben.
8. [PENDING] Nicht verfuegbare Meterarten bewusst unterdruecken — Done when: Kaltwasser- und HKV-/Heizverbrauchs-Sektionen in der MVP nur dann erscheinen, wenn eine spaetere normalisierte Verbrauchsquelle dafuer existiert; bis dahin erscheinen sie nicht als leere Platzhalter im Hauptdokument.
9. [PENDING] Prüfbericht-Anbindung fuer Meterprovenienz ergänzen — Done when: Konflikte, fehlende Matches und beobachtete Meter-IDs weiterhin im Prüfbericht bzw. Review-Flow sichtbar bleiben, auch wenn im Hauptdokument kein Meterblock erzeugt wird.
10. [PENDING] Cover-letter/Statement-Abgrenzung fuer Meterdaten bewahren — Done when: keine meterbezogenen Provenienz- oder Konflikthinweise ins Anschreiben ausweichen; das Anschreiben bleibt rein kommunikativ, das Hauptdokument rein abrechnungsbezogen, der Prüfbericht technisch.

## Open Items
- [MISSING SPEC NON-BLOCKING] Falls spaeter fuer die Einzelabrechnung zwingend Alt-/Neu-Ablesestaende auch ohne normalisierte Rechenkernquelle angezeigt werden sollen, braucht die Spec zusaetzlich eine ausdrueckliche Regel, ob OCR-/Ableseprotokollwerte direkt im Hauptdokument erscheinen duerfen oder weiter nur Pruefberichtsmaterial bleiben.

## Verification Test Cases
1. Given eine Partei mit `monthly_costs`, when `meter_sections[]` gebaut werden, then entsteht genau eine Strom-Sektion mit `unit = "kWh"`, annualisiertem `normalized_value` und `null`-Ablesefeldern statt erfundener Alt-/Neu-Werte.
2. Given eine Partei in `NE1` oder `NE2` mit vorhandenem `ww_audit`, when die Metersektion erzeugt wird, then entsteht genau eine Warmwasser-Sektion mit `normalized_value = ww_m3_neX`, `unit = "m3"` und ohne synthetische Staende.
3. Given vorhandene `meter_observations` ohne abrechnungswirksamen Parteienverbrauch, when das Hauptdokument gerendert wird, then entsteht kein leerer Meterblock; die Beobachtung bleibt nur im Prüfbericht/Review sichtbar.
4. Given ein eindeutiger Canonical-Meter fuer Partei und Meterart, when `meter_id` gesetzt wird, then wird `canonical_meters.external_id` bevorzugt; alias-/exact-Matches aus `meter_observations` dienen nur als Fallback.
5. Given ein Konflikt- oder Missing-Match in `meter_observations`, when die Einzelabrechnung erzeugt wird, then erscheint diese ID nicht ungeprueft im Hauptdokument und der Review-/Prüfberichtspfad bleibt erhalten.
6. Given eine Partei ohne `monthly_costs` und ohne passende `ww_audit`-Ableitung, when `statement_payload_v2` gebaut wird, then ist `meter_sections[]` leer statt mit technischen Platzhaltern gefuellt.


# Iteration 4

## Summary
- Die finale Spec (insbesondere Iterationen 8 bis 10) ist jetzt planreif und ersetzt die bisher nur technisch validierte v2-Ausgabe als Zielbild.
- Der bestehende Code liefert bereits einen nutzbaren Redesign-Ausgangspunkt:
  - `statement_payload_v2`
  - separates Anschreiben
  - Typst-Renderpfad
  - gruene Pipeline-Tests
- Diese Iteration verschiebt den Planfokus deshalb von "v2 einfuehren" auf "bestehenden v2-Prototyp auf das freigegebene tenant-facing Dokumentenmodell umbauen".
- Der Plan bleibt **implementation-ready**; es gibt keine blocking Spec-Entscheidungen mehr.

## Requirements Snapshot
- Seite 1 der Einzelabrechnung ist nun fachlich und visuell festgelegt:
  - Dokumentkopf
  - Ergebnisbox
  - Vorauszahlungs-Erklaerung mit Zeitraumbezug
  - Orientierungstabelle mit Referenzen
  - Kernkostentabelle mit exakten Spalten
  - kurzer Hinweis auf Detailseiten und Belegeinsicht
- Die Kernkostentabelle verwendet sichtbar genau diese Spalten:
  - `Kostenart`
  - `Bezieht sich auf`
  - `Verteilung`
  - `Ihre Basis / Gesamtbasis`
  - `Zeitraum`
  - `Ihr Betrag`
- Die Detailstruktur ist als mehrseitiges Zielbild festgelegt:
  - Seite 2 = Heizung / Warmwasser
  - Seite 3 = weitere Betriebskosten mit Beleg- und Verteilungsdarstellung
  - Seite 4 = Strom mit Zaehler- und Tarifabschnitten
  - Seite 5 = Messgeraete / Ablese- und Umrechnungsdarstellung
- Fuer Heizkostenverteiler gilt nun explizit:
  - Rohablesewert
  - Umrechnungsfaktor
  - Verbrauchseinheiten
  muessen sauber getrennt werden; fuer Umlage und Vergleich duerfen nur die umgerechneten Verbrauchseinheiten verwendet werden.
- Das Anschreiben bleibt ein separates, kurzes Kommunikationsdokument ohne Rechenweg.
- Akzeptanz erfolgt erst bei:
  - gruener Pipeline-Regression
  - Reader-/Oracle-Pruefungen
  - bestandenem Mieter-Review

## Current State Snapshot
- `output_writer.py` erzeugt bereits `statement_payload_v2` mit `document_header`, `summary_box`, `meter_sections`, `cost_type_sections`, `subtotals`, `notices` und `document_policy`.
- `renderer.py` kann bereits drei Artefakte pro Partei schreiben/rendern:
  - Einzelabrechnung
  - Pruefbericht
  - Anschreiben
- `statement_template_v2.typ` ist jedoch noch deutlich unter dem freigegebenen Zielbild:
  - es rendert heute Ueberschriften plus Text-/Bullet-Bloecke
  - es kennt noch keine echte Seite-1-Ergebnisbox
  - keine Orientierungstabelle
  - keine Kernkostentabelle mit Zeitraumspalte
  - keine ausmodellierten Detailseiten 2 bis 5
- `_statement_tokens_v2()` rendert `SUMMARY_BLOCK`, `METER_BLOCK`, `COST_BLOCK` und `SUBTOTAL_BLOCK` noch als Listen-/Textfragmente statt als freigegebene Tabellenstruktur.
- Die bestehende Testsuite prueft bereits den Prototyp-Pfad (`statement_payload_v2`, Anschreiben, Artefakte, Gruppierungen), aber noch nicht den final freigegebenen Mock-Vertrag aus der Spec.
- Die Spec liefert nun mit `Kraft / Huehne` 2024 einen konkreten Lesbarkeits- und Werte-Orakel-Fall inklusive:
  - `4.250,01 EUR` Gesamtkosten
  - `2.500,00 EUR` Vorauszahlungen
  - `1.750,01 EUR` Nachzahlung
  - `180 / 654 m²`
  - `180 / 260 m²`
  - `2 / 9`
  - `7.586,527 / 17.444,165 Verbrauchseinheiten`
  - `32,56 / 57,95 m³`
  - Stromzaehler `34877025`
  - Zeitraum `304 / 365 Tage`

## Action Plan
1. [DONE] Finales Produktziel aus der Spec festgeschrieben — Evidence: Die Bezugsspec definiert mit Iterationen 8 bis 10 jetzt das freigegebene tenant-facing Zielbild inklusive Beispielseite, Kostenarten-Matrix, HKV-Regel und Mieter-Review-Gate.
2. [DONE] Bestehenden v2-/Renderer-/Anschreiben-Pfad als Redesign-Basis akzeptieren — Evidence: `output_writer.py`, `renderer.py`, `statement_template_v2.typ`, `cover_letter_template_v1.typ` und die bestehenden v2-Tests/Artefakte sind bereits vorhanden.
3. [DONE] Aktuelle v2-Ausgabe als technischer Baseline-Prototyp und nicht als fachliches Zielbild eingeordnet — Evidence: Die Spec dokumentiert die Ablehnung der bisherigen v2-Darstellung; das aktuelle Template rendert weiterhin die bekannte Bullet-/Blockstruktur statt des freigegebenen Mocks.
4. [PENDING] Code-seitigen Vertrag fuer die finale Seite-1-Struktur festziehen — Done when: `statement_payload_v2` (oder eine kompatible Weiterentwicklung unter stabilen Artefaktnamen) explizite Felder fuer `document_header`, `result_box`, `advance_payment_explanation`, `reference_table` und `page1_cost_rows[]` traegt und diese die sichtbaren Spalten des freigegebenen Mocks direkt abbilden.
5. [PENDING] Bullet-/Listen-Ausgabe in `statement_template_v2.typ` durch tabellengetriebene Seite 1 ersetzen — Done when: das Template keine generischen `SUMMARY_BLOCK`-/`COST_BLOCK`-Listen mehr fuer das Hauptdokument nutzt, sondern Ergebnisbox, Orientierungstabelle, Kernkostentabelle und Seite-1-Hinweis im freigegebenen Layout rendert.
6. [PENDING] `Kraft / Huehne` 2024 als primaeres Seiten-1-Orakel in Tests verankern — Done when: Tests die freigegebenen Referenzwerte und Referenztexte aus der Spec fuer Seite 1 pruefen, insbesondere Ergebnisbox, Vorauszahlungsformulierung, Verteilungsreferenzen, Zeitraumspalte und Belegeinsicht-Hinweis.
7. [PENDING] Zeitraumdarstellung fachlich pro Kostenart operationalisieren — Done when: die Seite-1-Kostenzeilen die Matrixwerte `304 / 365 Tage`, `365 / 365 Tage`, `im Verbrauch enthalten` oder `direkt fuer Ihren Zeitraum ermittelt` genau nach Spec verwenden und die Ergebnisbox die Vorauszahlungen explizit an den Mietzeitraum koppelt.
8. [PENDING] Heiz-/Warmwasser-Detailseite auf das freigegebene Vier-Tabellen-Modell umbauen — Done when: Seite 2 die Tabellen fuer Heizkostentopf, Grundkostenanteil, verbrauchsabhaengige Heizkosten und Warmwasser im Spec-Wording rendert statt generischer Kostenbloecke.
9. [PENDING] HKV-Geraete-/Umrechnungstabelle einfuehren und semantisch absichern — Done when: die Heizungsdetailseite fuer HKV-Geraete pro Raum Seriennummer, Rohwert/Differenz, Umrechnungsfaktor und daraus resultierende Verbrauchseinheiten zeigt und Tests absichern, dass Seite 1 und die Referenztabelle niemals rohe HKV-Werte als Umlagebasis verwenden.
10. [PENDING] Betriebskosten-Detailseiten im Beleg-plus-Verteilungs-Muster umsetzen — Done when: Grundsteuer, Muellabfuhr, Kalt-/Abwasser, Oberflaechenwasser und Gebaeudeversicherung auf Seite 3 jeweils aus Beleg-/Positionsdarstellung plus kurzer Verteilungszusammenfassung bestehen.
11. [PENDING] Strom-Detailseite mit Zaehleranker und Tarifabschnitten umsetzen — Done when: Seite 1 die Stromzeile mit Zaehler `34877025` und Verweis auf Seite 4 zeigt und Seite 4 den Strompfad mit Zaehlerbezug, Zeitraum, Tarifabschnitten und Summenkosten im Spec-Sinn ausgibt.
12. [PENDING] Messgeraete-/Ablese-Seite availability-aware bauen — Done when: Seite 5 relevante Geraete und Mess-/Ablesewerte fuer Mietergespräche zeigt, HKV dort mit Rohwert/Faktor/Verbrauchseinheiten darstellt und nicht verfuegbare Werte leer bzw. explizit unverfuegbar bleiben statt synthetisch erfunden zu werden.
13. [PENDING] Anschreiben auf die finalen Dokumentrollen trimmen — Done when: das Anschreiben nur Ergebnis, Zahlungsziel/Guthabenhinweis, Kontoverbindung und Belegeinsicht-Referenz enthaelt und keine Rechenweg-, Meter- oder Provenienzdetails uebernimmt.
14. [PENDING] Test- und Oracle-Suite vom Prototyp-Contract auf den finalen Mock-Contract umstellen — Done when: Tests nicht nur das Vorhandensein von `statement_payload_v2` pruefen, sondern den finalen Seiten-1-Vertrag, die HKV-Faktor-Semantik, die Strom-Detailseite, die Seite-1-Hinweislogik und das separate Anschreiben gegen Spec und Excel-Orakel absichern.
15. [PENDING] Fixture-/Snapshot-Refresh erst nach gruener Redesign-Regression durchfuehren — Done when: 2024-Statement-Payloads, Typst-Dateien, PDFs und ggf. Snapshots erst nach bestandenem Vertrags-, Reader-, Oracle- und HKV-Semantik-Testlauf neu erzeugt und kontrolliert werden.
16. [PENDING] Abschliessenden Reader- und Mieter-Review-Gate ausfuehren — Done when: ein frischer Reviewer in der final gerenderten `Kraft / Huehne`-Abrechnung Zeitraum, Ergebnis, Vorauszahlungen, Verteilungsbasis, Zeitraumanteile, Stromzaehleranker, HKV-Umrechnungserklaerung und Belegeinsichtspfad ohne Codekontext findet.

## Open Items
- [MISSING SPEC NON-BLOCKING] Juristische Endfassung der Belegeinsicht-/Umlagefaehigkeits-Hinweise bleibt ein spaeterer Review-Schritt; fuer die Implementierung ist die jetzige Arbeitsfassung ausreichend konkret. => ziehe die juristischen Texte aus der ista Vorlage falls notwendig und möglich

## Verification Test Cases
1. Given die aktuelle bullet-/blockorientierte `statement_template_v2.typ`, when das Redesign umgesetzt wird, then rendert Seite 1 Ergebnisbox, Orientierungstabelle, Kernkostentabelle und den kurzen Belegeinsicht-Hinweis statt generischer Listenbloecke.
2. Given den Referenzfall `Kraft / Huehne` 2024, when die neue Einzelabrechnung erzeugt wird, then enthaelt Seite 1 die Spec-Orakelwerte `4.250,01 EUR`, `2.500,00 EUR`, `1.750,01 EUR`, `180 / 654 m²`, `180 / 260 m²`, `2 / 9`, `7.586,527 / 17.444,165 Verbrauchseinheiten`, `32,56 / 57,95 m³`, `304 / 365 Tage` und den Stromzaehler `34877025`.
3. Given HKV-Geraete mit unterschiedlichen Umrechnungsfaktoren, when die Heizungsdetailseite gerendert wird, then zeigt die Umrechnungstabelle Rohwert/Differenz, Faktor und resultierende Verbrauchseinheiten je Geraet und Seite 1 verwendet fuer die Umlage ausschliesslich die Verbrauchseinheiten.
4. Given eine Kostenart mit Zeitraumanteil, eine verbrauchsbasierte Kostenart und eine direkte Zuordnung, when die Seite-1-Kernkostentabelle erzeugt wird, then verwendet die Spalte `Zeitraum` genau die Matrixwerte `304 / 365 Tage`, `im Verbrauch enthalten` oder `direkt fuer Ihren Zeitraum ermittelt`.
5. Given die Stromkosten fuer `Kraft / Huehne`, when die finalen Dokumente gerendert werden, then referenziert Seite 1 den Zaehler `34877025` und Seite 4 zeigt die Tarifabschnitte nachvollziehbar als eigene Detailseite.
6. Given die finalisierte Einzelabrechnung, when Seite 1 und die letzte Seite gelesen werden, then finden sich sowohl der kurze Hinweis `Die folgenden Detailseiten enthalten die Rechengrundlagen ...` als auch der ausfuehrlichere Abschnitt `Hinweise und Pruefbarkeit`.
7. Given das separate Anschreiben, when `compile_pdf=True` und `compile_pdf=False` ausgefuehrt werden, then bleiben Anschreiben-Artefakte separat erhalten und enthalten nur die kommunikativen Inhalte, nicht den Rechenweg.
8. Given die redesignte 2024-Ausgabe, when Reader-/Mieter-Review laufen, then koennen Zeitraum, Ergebnis, Vorauszahlungen, Verteilungsbasis, HKV-Erklaerung, Stromanker und Belegeinsichtspfad ohne Zusatzkontext gefunden werden.


# Iteration 5

## Summary
- Der Review gegen finale Spec und aktuellen Code hat gezeigt, dass Iteration 4 in der Richtung richtig war, aber an mehreren Stellen noch zu grob fuer eine sichere Umsetzung blieb.
- Diese Iteration schliesst genau diese Luecken:
  - expliziter Payload-Vertrag fuer Seite 1
  - expliziter Payload-Vertrag fuer HKV-/Heizungsdetail
  - expliziter Render-Vertrag fuer `statement_template_v2.typ`
  - explizite Orakel-/Matrix-Tests fuer `Kraft / Huehne` 2024
- Mit dieser Iteration ist der Plan **implementation-ready**, weil die naechsten Schritte nun ohne Raten zu Vertrag, Sequenz oder Verifikation ausgefuehrt werden koennen.

## Requirements Snapshot
- Die finale Einzelabrechnung ist nicht nur ein `statement_payload_v2` mit beliebigen Blöcken, sondern ein tenant-facing Dokument mit festem Seiten-1-Vertrag:
  - Ergebnisbox
  - Vorauszahlungs-Erklaerung fuer den konkreten Mietzeitraum
  - Orientierungstabelle
  - Kernkostentabelle mit sechs festen Spalten
  - Kurz-Hinweis auf Detailseiten und Belegeinsicht
- Die Seite-1-Kernkostentabelle muss sichtbar exakt diese Spalten transportieren:
  - `Kostenart`
  - `Bezieht sich auf`
  - `Verteilung`
  - `Ihre Basis / Gesamtbasis`
  - `Zeitraum`
  - `Ihr Betrag`
- Die HKV-Logik verlangt explizit die Trennung von:
  - Rohablesewert
  - Umrechnungsfaktor
  - Verbrauchseinheiten
  wobei fuer Umlage und Vergleich nur Verbrauchseinheiten zulaessig sind.
- Das separate Anschreiben bleibt bewusst kurz und kommunikativ; Rechenweg, HKV-Herleitung und Meterprovenienz gehoeren in Einzelabrechnung bzw. Pruefbericht.

## Current State Snapshot
- Der aktuelle Code erzeugt bereits ein prototypisches `statement_payload_v2`, aber wichtige Spec-Vertragsfelder fehlen noch:
  - keine `reference_table`
  - keine strukturierte `advance_payment_explanation`
  - keine expliziten `page1_cost_rows[]`
  - keine feldgenaue `time_period_display` je Kostenart
  - keine HKV-Geraete-/Umrechnungstabelle auf Nutzereinheitsebene
- Die aktuelle `statement_template_v2.typ` rendert noch Ueberschrift + generische Blockausgaben (`SUMMARY_BLOCK`, `METER_BLOCK`, `COST_BLOCK`, `SUBTOTAL_BLOCK`) und bildet die final freigegebene Tabellenstruktur nicht ab.
- Die aktuelle Testsuite prueft den Prototyp-Vertrag, aber noch nicht die finalen Spec-Vertraege fuer:
  - Orientierungstabelle
  - Zeitraumspalte
  - Vorauszahlungs-Formulierung
  - Stromzaehler-Anker auf Seite 1
  - HKV-Faktor-Semantik
- Die benoetigten Fachwerte fuer den Referenzfall liegen in Code-/Fixture-Welt bereits vor:
  - `Kraft / Huehne`
  - `4.250,01 EUR`
  - `2.500,00 EUR`
  - `1.750,01 EUR`
  - `180 / 654 m²`
  - `180 / 260 m²`
  - `2 / 9`
  - `7.586,527 / 17.444,165 Verbrauchseinheiten`
  - `32,56 / 57,95 m³`
  - `304 / 365 Tage`
  - Stromzaehler `34877025`
- Fuer die HKV-Detailseite sind im Workbook/Messgeraete-Kontext bereits Seriennummern und Umrechnungsfaktoren vorhanden; sie muessen fuer den finalen Detailseitenvertrag nur noch in eine normalisierte Renderstruktur ueberfuehrt werden.

## Action Plan
1. [DONE] Finale Spec als stabilen Produktvertrag fixiert — Evidence: Die Bezugsspec Iterationen 8 bis 10 definiert jetzt Seite 1, Detailseiten, HKV-Regel, Stromanker und Mieter-Review ohne offene blocking Entscheidungen.
2. [DONE] Bestehenden v2-/Renderer-/Anschreiben-Pfad als technische Basis verifiziert — Evidence: `output_writer.py`, `renderer.py`, `statement_template_v2.typ`, `cover_letter_template_v1.typ` und die bestehende Testsuite erzeugen bereits den Prototyp-Pfad mit Statement, Pruefbericht und Anschreiben.
3. [PENDING] Seite-1-Payload als expliziten Vertrag einfuehren — Done when: `statement_payload_v2` (oder kompatible Weiterentwicklung) mindestens diese neuen/geschaerften Blöcke traegt:
   - `result_box` mit `total_costs_eur`, `already_paid_eur`, `result_label`, `result_value_eur`
   - `advance_payment_explanation` mit `period_start`, `period_end`, `payment_count`, `payment_interval_label`, `amount_per_payment_eur`, `total_paid_eur`, `display_text`, `formula_text`
   - `reference_table.rows[]` mit `reference_id`, `label`, `tenant_value_display`, `total_value_display`, `scope_label`
   - `page1_cost_rows[]` mit `row_id`, `cost_type_label`, `scope_label`, `distribution_label`, `basis_display`, `time_period_display`, `tenant_amount_eur`, optional `detail_page_ref`
   - `page1_notice_text`
4. [PENDING] Mapping-Regeln von Rechenkern -> `reference_table.rows[]` festziehen — Done when: fuer den Referenzfall `Kraft / Huehne` die sieben Referenzen aus der Spec exakt, in stabiler Reihenfolge und mit stabilem `reference_id` erzeugt werden:
   - `living_area_property`
   - `living_area_be1`
   - `persons_property`
   - `heating_units_be1`
   - `warmwater_be1`
   - `coldwater_property`
   - `period_2024`
5. [PENDING] Mapping-Regeln von Rechenkern -> `page1_cost_rows[]` festziehen — Done when: fuer jede kostenrelevante Zeile der Kernkostentabelle klar dokumentiert und getestet ist,
   - welche `scope_label` erscheint,
   - welcher `distribution_label`-Text erscheint,
   - wie `basis_display` gebaut wird,
   - welcher `time_period_display`-Wert verwendet wird,
   - in welcher festen Reihenfolge die Zeilen auf Seite 1 erscheinen.
6. [PENDING] Zeitraum-Matrix als harte Ausfuehrungsregel in Code und Tests abbilden — Done when: jede Seite-1-Kostenzeile genau einen der vier Spec-Werte nutzt:
   - `304 / 365 Tage`
   - `365 / 365 Tage`
   - `im Verbrauch enthalten`
   - `direkt fuer Ihren Zeitraum ermittelt`
   und diese Entscheidung nicht nur implizit in `calculation_text`, sondern explizit im Payload-Feld `time_period_display` sichtbar ist.
7. [PENDING] HKV-Detailvertrag fuer Seite 2 einfuehren — Done when: das Heizungsdetail zusaetzlich einen Block `heating_device_table` oder funktional gleichwertig traegt mit `rows[]`, deren Felder mindestens sind:
   - `room_label`
   - `device_type`
   - `serial_number`
   - `raw_value_start`
   - `raw_value_end`
   - `raw_value_difference`
   - `conversion_factor`
   - `consumption_units`
   sowie `tenant_total_consumption_units` und `scope_total_consumption_units`.
8. [PENDING] HKV-Datenquellen operationalisieren, ohne Hauptdokument zu verfälschen — Done when: die HKV-Geraete-/Umrechnungstabelle ihre Seriennummern/Faktoren aus verifizierten Meter-/Workbook-Quellen bezieht, rohe Werte nur als Detailseitenkontext zeigt und alle Umlage-/Quotenberechnungen auf Seite 1/Seite 2 ausschliesslich `consumption_units` verwenden.
9. [PENDING] Strom-Seite-1- und Detailseiten-Vertrag explizit machen — Done when: `page1_cost_rows[]` fuer Strom den Text `Stromzaehler 34877025, Tarifabschnitte siehe Seite 4` (bzw. generalisiert denselben Mustertext) tragen kann und ein separater `electricity_detail`-Block mindestens `meter_id`, `period_start`, `period_end`, `tariff_periods[]`, `total_cost_eur` transportiert.
10. [PENDING] Typst-Rendervertrag fuer Seite 1 konkretisieren — Done when: der Plan den Layout-Vertrag nicht nur funktional, sondern renderbar festlegt:
   - Ergebnisbox ueber gesamte Nutzbreite
   - Orientierungstabelle mit 4 Spalten direkt darunter
   - Kernkostentabelle als 6-Spalten-Tabelle mit fester Spaltenlogik
   - Kurz-Hinweis am Seitenende
   und `statement_template_v2.typ` bzw. neue Render-Helfer nicht mehr generische Listenblöcke, sondern diese Strukturen rendern.
11. [PENDING] Konkrete Typst-Tabellenstruktur fuer Seite 1 implementierungsnah vorgeben — Done when: die Umsetzung sich an diesem Vertrag orientiert:
   - Orientierungstabelle: 4 Spalten (`Referenz | Ihr Wert | Gesamtwert | Gilt fuer`)
   - Kernkostentabelle: 6 Spalten (`Kostenart | Bezieht sich auf | Verteilung | Ihre Basis / Gesamtbasis | Zeitraum | Ihr Betrag`)
   - Kernkostentabelle mit linksbuendigen Textspalten und rechtsbuendiger Betrags-Spalte
   - Zeilenumbrueche in `Verteilung` und `Ihre Basis / Gesamtbasis` sind erlaubt, aber die Spaltenzahl bleibt fest
12. [PENDING] Tests vom Prototyp-Vertrag auf den finalen Dokumentvertrag umstellen — Done when: mindestens folgende Testgruppen in `tests/test_pipeline_tdd.py` oder gleichwertig grün laufen:
   - Seiten-1-Orakeltest fuer `Kraft / Huehne`
   - Zeitraum-Matrix-Test
   - HKV-Faktor-Semantik-Test (`consumption_units` ja, rohe HKV-Werte als Umlagebasis nein)
   - Strom-Anker-Test fuer Zaehler/Seite-4-Verweis
   - Hinweistext-/Vorauszahlungs-Text-Test
   - Anschreiben-Rollentrennungs-Test
13. [PENDING] Detailseitenvertrag fuer Seite 3 bis 5 in strukturierte Renderbloecke uebersetzen — Done when:
   - Seite 3 belegs- plus verteilungsorientierte Betriebskosten-Bloecke rendert,
   - Seite 4 den Strompfad mit Tarifabschnitten rendert,
   - Seite 5 Messgeraete/Ablese-/Umrechnungstabellen availability-aware rendert,
   ohne fehlende Werte zu erfinden.
14. [PENDING] Juristische Arbeitsfassung aus vorhandener ista-Vorlage ableiten, falls fuer finalen Hinweistext noetig und moeglich — Done when: der Belegeinsicht-/Hinweistext entweder aus der vorhandenen ista-Referenz sinnvoll abgeleitet oder bewusst bei der freigegebenen Arbeitsfassung belassen ist; dies bleibt non-blocking gegenueber der eigentlichen Umsetzung.
15. [PENDING] Fixture-/Snapshot-Refresh erst nach gruener Vertragsregression ausfuehren — Done when: die 2024-Artefakte erst nach bestandenem Payload-, Render-, Oracle-, HKV- und Reader-Test aktualisiert werden.
16. [PENDING] Abschliessenden Reader- und Mieter-Review-Gate ausfuehren — Done when: eine frische Leserin bzw. ein frischer Leser in der finalen `Kraft / Huehne`-Abrechnung Seite 1 und Seite 2 die zentralen Informationen ohne Codekontext findet und keine rohe HKV-Verwechslungsgefahr mehr besteht.

## Open Items
- [MISSING NON-BLOCKING] Falls sich bei der Umsetzung zeigt, dass fuer die HKV-Geraete-Tabelle Rohwert-Start/Ende nicht fuer alle Jahre/Inputs belastbar vorliegen, darf die Detailseite alternativ mit `raw_value_difference` statt Start/Ende arbeiten; die Pflicht zur Ausweisung von `conversion_factor` und `consumption_units` bleibt bestehen.
- [MISSING NON-BLOCKING] Juristische Endfassung der Hinweistexte kann spaeter weiter geschaerft werden; fuer die Implementierung reicht die derzeit freigegebene Arbeitsfassung, mit optionaler Ableitung aus der ista-Vorlage.

## Verification Test Cases
1. Given den aktuellen Prototyp mit generischen Listenblöcken, when der neue Seiten-1-Vertrag umgesetzt wird, then rendert `statement_template_v2.typ` Ergebnisbox, Vorauszahlungs-Erklaerung, Orientierungstabelle, Kernkostentabelle und Kurz-Hinweis in genau dieser Reihenfolge.
2. Given den Referenzfall `Kraft / Huehne` 2024, when die redesignte Einzelabrechnung erzeugt wird, then stimmt `page1_cost_rows[]` in Reihenfolge, Texten und Betraegen mit dem Spec-Mock ueberein und die Summe bleibt `4.250,01 EUR`.
3. Given die sieben Referenzen fuer `Kraft / Huehne`, when `reference_table.rows[]` gebaut wird, then enthalten die Zeilen exakt `180 / 654 m²`, `180 / 260 m²`, `2 / 9`, `7.586,527 / 17.444,165 Verbrauchseinheiten`, `32,56 / 57,95 m³`, `24,95 / 385,542 m³` und `304 / 365 Tage`.
4. Given HKV-Geraete mit unterschiedlichen Umrechnungsfaktoren, when `heating_device_table.rows[]` gebaut und gerendert werden, then ist pro Geraet der Umrechnungsfaktor sichtbar und die für Seite 1 verwendete Umlagebasis entspricht ausschliesslich der Summe der `consumption_units`.
5. Given eine Seite-1-Stromzeile, when die Einzelabrechnung fuer `Kraft / Huehne` gerendert wird, then zeigt die Zeile den Zaehler `34877025` und verweist auf Seite 4; Seite 4 zeigt die passenden Tarifabschnitte.
6. Given die Vorauszahlungen fuer den Mietzeitraum `01.01.2024 bis 31.10.2024`, when die Ergebnisbox gerendert wird, then erscheinen sowohl der periodenbezogene Satz als auch die Formel `10 x 250,00 EUR = 2.500,00 EUR`.
7. Given ein Jahr/Input ohne belastbare HKV-Start-/Endwerte, when die Detailseite gerendert wird, then nutzt sie zulässig `raw_value_difference` oder leer bleibende Rohwertfelder, zeigt aber weiterhin `conversion_factor` und `consumption_units`.
8. Given die finalen Dokumente, when Reader-/Mieter-Review laufen, then koennen Zeitraum, Ergebnis, Vorauszahlungen, Verteilungsbasis, Zeitanteile, HKV-Umrechnung, Stromanker und Belegeinsichtspfad ohne Zusatzkontext gefunden werden.


# Iteration 6

## Summary
- Der letzte Readiness-Check hat keinen neuen Spec-Bedarf mehr aufgedeckt, sondern nur eine Sync-Luecke zwischen finaler Spec-Iteration 10 und dem Wortlaut des Plans.
- Diese Iteration stellt deshalb klar:
  - HKV-Semantik ist **bindender** Vertragsbestandteil, nicht nur ein optionales Detail
  - die Non-Blocking-Öffnung fuer fehlende Rohwert-Start/Ende lockert **nicht** die Pflicht, mit `conversion_factor` und `consumption_units` zu arbeiten
  - die Stromzeile auf Seite 1 verwendet dieselbe Meter-ID-Prioritaet wie die frueheren Meter-Regeln aus Iteration 3
  - die Reihenfolge der `page1_cost_rows[]` fuer den Referenzfall ist jetzt explizit als Ausfuehrungs- und Testregel im Plan verankert
- Mit dieser Iteration ist der Plan **implementation-ready**.

## Requirements Snapshot
- Die Spec Iteration 10 verpflichtet den Umsetzungsplan jetzt ausdruecklich darauf, dass im tenant-facing Dokument fuer Heizung:
  - keine rohen HKV-Ablesewerte als Umlage- oder Vergleichsbasis erscheinen duerfen
  - nur `consumption_units` in Orientierungstabelle, Kernkostentabelle und Heizkostenquote verwendet werden duerfen
  - die Heizungsdetailseite eine Geraete-/Umrechnungstabelle plus Erklaersatz tragen muss
- Die finale Seite 1 ist nicht nur inhaltlich, sondern auch in Zeilenreihenfolge und Ankertexten testbar festgelegt.

## Current State Snapshot
- Iteration 5 hat den fehlenden Payload-, Render- und Testvertrag bereits weitgehend geschlossen.
- Das verbleibende Missverstaendnis lag nicht in fehlenden Arbeitspaketen, sondern darin, dass die HKV-Semantik aus Spec Iteration 10 im Plan noch nicht ausdruecklich als **bindende** Ausfuehrungsregel markiert war.
- Die frueheren Meter-ID-Prioritaetsregeln existieren bereits in Plan Iteration 3, waren aber fuer die Seite-1-Stromzeile in Iteration 5 noch nicht explizit rueckgebunden.

## Action Plan
1. [DONE] HKV-Semantik aus Spec Iteration 10 als bindende Ausfuehrungsregel synchronisiert — Evidence: Diese Iteration stellt klar, dass `Rohablesewert`, `Umrechnungsfaktor` und `consumption_units` nicht nur Dokumentationssprache sind, sondern den Implementierungsvertrag bestimmen; Seite 1 und die Verteilungslogik duerfen fuer Heizung ausschliesslich `consumption_units` verwenden.
2. [DONE] Non-Blocking-HKV-Open-Item praezisiert — Evidence: Fehlende Rohwert-Start/Ende bleiben nur fuer die Detaildarstellung non-blocking; `conversion_factor` und `consumption_units` bleiben Pflicht und die HKV-Semantik bleibt voll bindend.
3. [DONE] Strom-Meteranker an die bestehende Meter-ID-Prioritaet rueckgebunden — Evidence: Fuer die Seite-1-Stromzeile gilt dieselbe Prioritaet wie bereits in Iteration 3 dokumentiert:
   - zuerst `canonical_meters.external_id`
   - dann eindeutiger `meter_observations.observed_meter_id` mit `match_status in {"exact", "alias"}`
   - sonst generischer Fallback ohne ungepruefte ID
   Done when: die Seite-1-Stromzeile und die Detailseite 4 dieselbe hergeleitete Meter-ID verwenden.
4. [DONE] Feste Seiten-1-Reihenfolge fuer den Referenzfall als Test- und Renderregel explizit gemacht — Evidence: Fuer `Kraft / Huehne` 2024 gilt diese Reihenfolge der `page1_cost_rows[]` verbindlich:
   1. `Grundsteuer`
   2. `Muellabfuhr`
   3. `Kalt- und Abwasser`
   4. `Oberflaechenwasser`
   5. `Gebaeudeversicherung`
   6. `Brennstoffkosten - Grundkosten 30 %`
   7. `Brennstoffkosten - Verbrauch 70 %`
   8. `Heiznebenkosten`
   9. `Verbrauchskosten Warmwasser`
   10. `Strom`
   11. `Summe`
5. [PENDING] Iteration-5-Arbeitspakete in dieser Reihenfolge umsetzen — Done when: die Implementierung nacheinander
   - zuerst den Payload-Vertrag (`result_box`, `advance_payment_explanation`, `reference_table`, `page1_cost_rows`, `heating_device_table`, `electricity_detail`) erweitert,
   - dann die neuen Tests rot zieht,
   - dann Renderer/Typst auf die neue Struktur umstellt,
   - dann Detailseiten und Anschreiben vervollstaendigt,
   - und erst danach Fixtures/Snapshots aktualisiert.
6. [PENDING] Contract-first-TDD-Gate durchziehen — Done when: kein Template-/Fixture-Redesign vor dem Vorliegen der neuen Payload-Felder und der dazugehoerigen Spec-/Oracle-Tests erfolgt.

## Open Items
- [MISSING NON-BLOCKING] Juristische Endfassung der Hinweistexte kann spaeter weiter geschaerft werden; fuer die Implementierung reicht die derzeit freigegebene Arbeitsfassung, optional mit Ableitung aus der ista-Vorlage.

## Verification Test Cases
1. Given den finalen HKV-Vertrag, when die Seite-1-Kernkostentabelle und die Orientierungstabelle fuer Heizung gebaut werden, then verwenden beide ausschliesslich `consumption_units` und niemals rohe HKV-Werte.
2. Given fehlende HKV-Start-/Endwerte, when die Heizungsdetailseite gerendert wird, then bleibt die Darstellung trotzdem spec-konform, solange `conversion_factor` und `consumption_units` sichtbar sind und keine rohe HKV-Quote fuer die Umlage verwendet wird.
3. Given die Stromzeile fuer `Kraft / Huehne`, when die Meter-ID aus den vorhandenen Quellen abgeleitet wird, then verwenden Seite 1 und Seite 4 dieselbe priorisierte ID und zeigen fuer den Referenzfall `34877025`.
4. Given den Referenzfall `Kraft / Huehne` 2024, when `page1_cost_rows[]` gerendert werden, then erscheint die Zeilenreihenfolge exakt in der hier festgelegten Folge und bleibt als Orakel stabil.
5. Given die Iteration-5-Vertragsarbeit und diese Iteration-6-Klarstellungen, when die Implementierung startet, then sind keine weiteren blocking Spec-/Plan-Entscheidungen mehr noetig.


# Iteration 7

## Summary
- Der letzte Review hat nicht mehr nach offenen Produktentscheidungen gefragt, sondern nach der letzten Bruecke von Planvertrag zu konkreter Ableitungslogik.
- Diese Iteration schliesst diese Bruecke:
  - feste Ableitungsregeln pro Kostenzeile
  - konkrete Datenlinie fuer den Stromzaehler des Referenzfalls
  - konditionale Render-Regeln fuer die HKV-Geraete-/Umrechnungstabelle
- Damit ist der Plan nicht nur fachlich vollstaendig, sondern auch in der Ableitungsschicht so konkret, dass ein Implementierer nicht mehr zwischen Spec, Code und Fixture raten muss.

## Requirements Snapshot
- Die finale Seite 1 ist fuer den Referenzfall `Kraft / Huehne` nicht nur textlich, sondern auch in Zeileninhalt und Reihenfolge bindend.
- Die Seite-1-Zeilen brauchen deshalb pro Kostenart feste Regeln fuer:
  - `scope_label`
  - `distribution_label`
  - `basis_display`
  - `time_period_display`
  - optional `detail_page_ref`
- Der Stromanker auf Seite 1 muss fuer den Referenzfall nachweisbar aus derselben Meterlinie stammen wie die Detailseite.
- Die HKV-Geraete-/Umrechnungstabelle ist fuer HKV-basierte Heizfaelle verpflichtend; ihre Render-Regeln muessen explizit sagen, wann sie erscheint und wann einzelne Rohwertfelder leer bleiben duerfen.

## Current State Snapshot
- Iteration 5 und 6 definieren die benoetigten Payload-Felder, Sequenzen und TDD-Gates bereits sauber.
- Was noch fehlte, war die letzte Konkretisierung:
  - welches Mapping fuer jede Zeile der Kernkostentabelle gilt
  - welche konkrete Fixture-/Workbook-Linie im Referenzfall den Stromzaehler liefert
  - welche Konditionen fuer die HKV-Geraetetabelle gelten
- Die benoetigte Referenzlinie ist jetzt aus der 2024-Workbook-Welt verifiziert:
  - Stromzaehler Referenzfall `Kraft / Huehne` = `Messwerte!P15 = 34877025`
  - Zeitraum Referenzfall Strom = `Messwerte!Q15 = 01.01.2024` bis `Messwerte!R15 = 31.10.2024`
  - HKV-Geraetefaktoren Loftwohnung liegen in `Messgeraete` fuer Wohnzimmer/Schlafzimmer/Kueche/Esszimmer/Bad/Flur vor, z. B. `120298189 -> 1,891`, `129136000 -> 0,33`

## Action Plan
1. [DONE] Ableitungsregeln pro Seite-1-Zeile explizit gemacht — Evidence: Fuer den Referenzfall gelten diese verbindlichen Mappings:
   - `Grundsteuer` -> `scope_label = gesamte Liegenschaft`, `distribution_label = Wohnflaeche Liegenschaft`, `basis_display = 180 m² / 654 m²`, `time_period_display = 304 / 365 Tage`, `detail_page_ref = Seite 3`
   - `Muellabfuhr` -> `scope_label = gesamte Liegenschaft`, `distribution_label = Personen Liegenschaft`, `basis_display = 2 / 9`, `time_period_display = 304 / 365 Tage`, `detail_page_ref = Seite 3`
   - `Kalt- und Abwasser` -> `scope_label = gesamte Liegenschaft`, `distribution_label = Kaltwasser Liegenschaft`, `basis_display = 24,95 m³ / 385,542 m³`, `time_period_display = im Verbrauch enthalten`, `detail_page_ref = Seite 3`
   - `Oberflaechenwasser` -> `scope_label = gesamte Liegenschaft`, `distribution_label = Wohnflaeche Liegenschaft`, `basis_display = 180 m² / 654 m²`, `time_period_display = 304 / 365 Tage`, `detail_page_ref = Seite 3`
   - `Gebaeudeversicherung` -> `scope_label = Berechnungseinheit BE1`, `distribution_label = Wohnflaeche BE1`, `basis_display = 180 m² / 260 m²`, `time_period_display = 304 / 365 Tage`, `detail_page_ref = Seite 3`
   - `Brennstoffkosten - Grundkosten 30 %` -> `scope_label = Berechnungseinheit BE1`, `distribution_label = Wohnflaeche BE1`, `basis_display = 180 m² / 260 m²`, `time_period_display = 304 / 365 Tage`, `detail_page_ref = Seite 2`
   - `Brennstoffkosten - Verbrauch 70 %` -> `scope_label = Berechnungseinheit BE1`, `distribution_label = Heizverbrauch BE1`, `basis_display = 7.586,527 / 17.444,165 Verbrauchseinheiten`, `time_period_display = im Verbrauch enthalten`, `detail_page_ref = Seite 2`
   - `Heiznebenkosten` -> `scope_label = Berechnungseinheit BE1`, `distribution_label = Heizverbrauch BE1`, `basis_display = 7.586,527 / 17.444,165 Verbrauchseinheiten`, `time_period_display = im Verbrauch enthalten`, `detail_page_ref = Seite 2`
   - `Verbrauchskosten Warmwasser` -> `scope_label = Verbrauchseinheit BE1`, `distribution_label = Warmwasser BE1`, `basis_display = 32,56 m³ / 57,95 m³`, `time_period_display = im Verbrauch enthalten`, `detail_page_ref = Seite 2`
   - `Strom` -> `scope_label = direkte Zuordnung zu Ihrer Nutzeinheit`, `distribution_label = Stromzaehler 34877025, Tarifabschnitte siehe Seite 4`, `basis_display = direkt ueber Zaehlerstand und Tarif berechnet`, `time_period_display = 01.01.2024 bis 31.10.2024`, `detail_page_ref = Seite 4`
2. [DONE] Datenlinie fuer den Stromanker des Referenzfalls festgezogen — Evidence: Fuer `Kraft / Huehne` 2024 ist die Orakel-ID `34877025` in der Workbook-Welt direkt als `Messwerte!P15` belegt; `Messwerte!Q15` und `Messwerte!R15` liefern den referenzierten Zeitraum. Die Implementierung darf diesen Wert in normalisierter Form aus `canonical_meters`/Meter-Mapping beziehen, das Orakel fuer Tests bleibt aber `34877025`.
3. [DONE] HKV-Geraete-/Umrechnungstabelle als konditionaler, aber verpflichtender Renderblock fuer HKV-Heizfaelle konkretisiert — Evidence:
   - wenn eine Partei heizkostenrelevante HKV-Verbrauchseinheiten hat und HKV-Geraetedaten/Faktoren fuer die Nutzeinheit vorliegen, ist `heating_device_table` Pflicht
   - die Tabelle enthaelt nur tatsaechlich vorhandene HKV-Geraete; Raeume ohne HKV erscheinen nicht als Leerzeilen
   - wenn Start-/Endwerte nicht belastbar vorliegen, duerfen `raw_value_start` und `raw_value_end` leer bleiben und `raw_value_difference` genutzt werden
   - `conversion_factor` und `consumption_units` bleiben in diesem Fall trotzdem Pflicht
   - fehlt fuer einen HKV-Heizfall sowohl Geraete-Faktorinfo als auch Verbrauchseinheitenbasis, ist dies ein Review-/Pruefbericht-Problem und darf nicht als scheinbar vollstaendige Heizungsdetailseite gerendert werden
4. [DONE] `basis_display`-Regel fuer direkte Zuordnung vs. Quotenfaelle explizit gemacht — Evidence:
   - Quotenfaelle zeigen immer `Ihr Wert / Gesamtwert`
   - direkte Zuordnungen zeigen einen sprechenden Satz (`direkt ueber Zaehlerstand und Tarif berechnet`) statt einer kuenstlichen Quote
5. [PENDING] Iteration-5- und Iteration-6-Arbeitspakete nun ohne weitere Ableitungsfragen umsetzen — Done when: Payload, Tests, Renderer/Typst, Detailseiten und Fixture-Refresh in der bereits festgelegten Contract-first-TDD-Sequenz abgearbeitet werden.

## Open Items
- [MISSING NON-BLOCKING] Juristische Endfassung der Hinweistexte kann spaeter weiter geschaerft werden; fuer die Implementierung reicht die derzeit freigegebene Arbeitsfassung, optional mit Ableitung aus der ista-Vorlage.

## Verification Test Cases
1. Given den Referenzfall `Kraft / Huehne` 2024, when `page1_cost_rows[]` gebaut werden, then entsprechen alle zehn Kostenzeilen exakt den hier festgelegten Ableitungsregeln fuer `scope_label`, `distribution_label`, `basis_display`, `time_period_display` und `detail_page_ref`.
2. Given die Stromzeile des Referenzfalls, when `page1_cost_rows[]` und `electricity_detail` erzeugt werden, then ist die verwendete Meter-ID `34877025`, ihr Zeitraum stammt aus derselben Referenzperiode und Seite 1 / Seite 4 bleiben konsistent.
3. Given die Loftwohnung-HKV-Geraete aus dem Workbook, when `heating_device_table.rows[]` gebaut werden, then enthalten die Zeilen die bekannten Seriennummern/Faktoren (z. B. `120298189 -> 1,891`, `129136000 -> 0,33`) und die resultierende Summe fuehrt zu den bekannten `7.586,527 Verbrauchseinheiten`.
4. Given fehlende HKV-Start-/Endwerte, when die Detailseite gerendert wird, then erscheint keine pseudo-genaue Rohwertdarstellung; stattdessen bleiben nur Start/Ende leer oder `raw_value_difference` wird verwendet, waehrend `conversion_factor` und `consumption_units` sichtbar bleiben.
5. Given diese Iteration 7 zusammen mit Iteration 5 und 6, when die Implementierung beginnt, then sind keine weiteren document-contract-, lineage- oder conditional-rendering-Entscheidungen mehr offen.


# Iteration 8

## Summary
- Der letzte Review hat nur noch exakte tenant-facing Wortlaute und Renderregeln als fehlende Planuebersetzung identifiziert.
- Diese Iteration zieht deshalb die finalen sichtbaren Texte aus der Spec direkt in den Plan:
  - HKV-Label der Orientierungstabelle
  - exakte Vorauszahlungsformulierung
  - exakter Seite-1-Hinweis
  - exakter Strom-Ankertext
  - exakte HKV-Erklaerformel und Spaltenreihenfolge
  - exakte Render-Regel fuer die Zeitraumspalte
- Damit ist auch die letzte Ruecksprungnotwendigkeit von Plan -> Spec fuer sichtbare Texte beseitigt.

## Requirements Snapshot
- Der Implementierungsplan muss jetzt nicht nur die Datenvertraege, sondern auch die finalen sichtbaren Standardformulierungen fuer die tenant-facing Ausgabe enthalten.
- Exakte Standardformulierungen sind hier kein kosmetisches Detail, sondern Teil des Abnahmevertrags fuer:
  - Mieterlesbarkeit
  - Reader-/Oracle-Tests
  - Referenzfall `Kraft / Huehne`

## Current State Snapshot
- Iteration 7 hat die Ableitungsregeln und Datenlinien geschlossen.
- Es fehlten nur noch die finalen, sichtbaren Default-Texte und die ausdrueckliche Renderregel fuer einzelne Tabellenfelder.
- Diese Texte stehen bereits in der Spec; sie werden jetzt in den Plan uebernommen, damit die Umsetzung nicht mehr zwischen Artefakten springen muss.

## Action Plan
1. [DONE] Exaktes HKV-Label fuer die Orientierungstabelle fixiert — Evidence: fuer `reference_id = heating_units_be1` gilt verbindlich:
   - `label = Heizverbrauch BE1 (Verbrauchseinheiten aus Heizkostenverteilern)`
   Done when: weder Payload noch Renderpfad fuer diesen Referenzeintrag eine kuerzere oder anders benannte Variante verwenden.
2. [DONE] Exakte Vorauszahlungs-Texte in den Plan uebernommen — Evidence: `advance_payment_explanation` verwendet fuer den Referenzfall verbindlich:
   - `display_text = Fuer Ihren Mietzeitraum 01.01.2024 bis 31.10.2024 wurden 10 Vorauszahlungen zu je 250,00 EUR beruecksichtigt.`
   - `formula_text = Berechnung: 10 x 250,00 EUR = 2.500,00 EUR`
   Generalisierte Regel:
   - `display_text = Fuer Ihren Mietzeitraum {period_start} bis {period_end} wurden {payment_count} Vorauszahlungen zu je {amount_per_payment_eur} EUR beruecksichtigt.`
   - `formula_text = Berechnung: {payment_count} x {amount_per_payment_eur} EUR = {total_paid_eur} EUR`
3. [DONE] Exakten Seite-1-Hinweis fixiert — Evidence: `page1_notice_text` lautet verbindlich:
   - `Die folgenden Detailseiten enthalten die Rechengrundlagen zu dieser Abrechnung. Belege koennen nach Terminvereinbarung eingesehen werden.`
4. [DONE] Exakten Strom-Ankertext fixiert — Evidence: fuer die Stromzeile des Referenzfalls gilt verbindlich:
   - `distribution_label = Stromzaehler 34877025, Tarifabschnitte siehe Seite 4`
   Generalisierte Regel:
   - `distribution_label = Stromzaehler {meter_id}, Tarifabschnitte siehe Seite 4`
   - falls keine belastbare ID vorliegt, nur `Tarifabschnitte siehe Seite 4`, aber keine ungepruefte Zaehlernummer
5. [DONE] Exakte HKV-Tabelle und Erklaerformel fixiert — Evidence: die Heizungsdetailseite rendert die HKV-Geraetetabelle in genau dieser Spaltenreihenfolge:
   - `Raum | Geraet | Seriennummer | Rohwert Anfang/Ende oder Differenzwert | Umrechnungsfaktor | Verbrauchseinheiten`
   und enthaelt den verbindlichen Erklaersatz:
   - `Die Heizkostenverteiler in den Raeumen haben unterschiedliche Umrechnungsfaktoren. Fuer die Abrechnung werden daher nicht die reinen Ablesewerte, sondern die daraus berechneten Verbrauchseinheiten verwendet.`
   Zusaetzliche Kurzformel im Rendervertrag:
   - `Verbrauchseinheiten = Rohablesewert bzw. Differenzwert x Umrechnungsfaktor`
6. [DONE] Zeitraumspalte als exakter Rendervertrag fixiert — Evidence:
   - fuer zeitanteilige Umlagen wird exakt `304 / 365 Tage` oder `365 / 365 Tage` gerendert
   - fuer verbrauchsbasierte Zeilen exakt `im Verbrauch enthalten`
   - fuer direkte Stromzuordnung im Referenzfall exakt `01.01.2024 bis 31.10.2024`
   Generalisierte Regel:
   - die Zeitraumsspalte rendert entweder ein Tage-Verhaeltnis, den Text `im Verbrauch enthalten` oder einen konkreten Datumszeitraum; freie Alternativformulierungen sind im tenant-facing Hauptdokument nicht zulaessig
7. [PENDING] Iteration-5- bis Iteration-7-Vertragsarbeit jetzt mit diesen festen Texten umsetzen — Done when: Payload, Renderer, Typst und Tests die hier fixierten Standardformulierungen und Renderregeln direkt verwenden und keine weitere Spec-Rueckfrage mehr benoetigen.

## Open Items
- [MISSING NON-BLOCKING] Juristische Endfassung der Hinweistexte kann spaeter weiter geschaerft werden; fuer die Implementierung reicht die derzeit freigegebene Arbeitsfassung, optional mit Ableitung aus der ista-Vorlage.

## Verification Test Cases
1. Given den Referenzfall `Kraft / Huehne`, when `reference_table.rows[]` gerendert wird, then lautet das Heizungs-Label exakt `Heizverbrauch BE1 (Verbrauchseinheiten aus Heizkostenverteilern)`.
2. Given die Ergebnisbox des Referenzfalls, when `advance_payment_explanation` gerendert wird, then erscheinen exakt die Texte `Fuer Ihren Mietzeitraum 01.01.2024 bis 31.10.2024 wurden 10 Vorauszahlungen zu je 250,00 EUR beruecksichtigt.` und `Berechnung: 10 x 250,00 EUR = 2.500,00 EUR`.
3. Given Seite 1 der finalen Einzelabrechnung, when der Hinweisblock gerendert wird, then lautet `page1_notice_text` exakt `Die folgenden Detailseiten enthalten die Rechengrundlagen zu dieser Abrechnung. Belege koennen nach Terminvereinbarung eingesehen werden.`
4. Given die Stromzeile des Referenzfalls, when `distribution_label` gerendert wird, then lautet sie exakt `Stromzaehler 34877025, Tarifabschnitte siehe Seite 4`.
5. Given die HKV-Geraetetabelle, when sie auf Seite 2 gerendert wird, then erscheinen die Spalten in der festgelegten Reihenfolge und der Erklaersatz plus die Kurzformel zur Umrechnung sind sichtbar.
6. Given die Zeitraumswerte in `page1_cost_rows[]`, when die Seite-1-Kernkostentabelle gerendert wird, then erscheinen nur die hier zugelassenen Darstellungsformen und keine alternativen Freitextvarianten.


# Iteration 9

## Summary
- Der letzte Review hat nur noch eine letzte semantische Planluecke gezeigt: HKV-Rohwerte, Faktoren und Verbrauchseinheiten mussten auf Payload- und Testebene noch ausdruecklicher getrennt werden.
- Diese Iteration macht genau das:
  - explizite Nullability-/Pflichtregeln fuer HKV-Felder
  - explizite Quellenzuordnung fuer HKV-Felder
  - expliziter Leak-Prevention-Test fuer Seite 1
- Damit ist der HKV-Vertrag nicht nur sprachlich, sondern auch strukturell und verifikatorisch geschlossen.

## Requirements Snapshot
- Die Spec Iteration 10 verbietet, rohe HKV-Werte als Vergleichs- oder Umlagebasis in Seite 1 oder in den heizungsbezogenen Quoten sichtbar zu machen.
- Der Plan muss daher nicht nur sagen, *dass* `consumption_units` verwendet werden, sondern auch:
  - welche Rohwert-Felder optional sind,
  - welche Felder Pflicht sind,
  - aus welcher Quellenklasse jedes HKV-Feld stammt,
  - und welcher Test ein versehentliches Leaken roher Werte ins Hauptdokument verhindert.

## Current State Snapshot
- Iteration 8 fixiert bereits die sichtbaren HKV-Texte, Spaltenreihenfolge und Umrechnungsformel.
- Es fehlte noch die explizite Payload-Disziplin:
  - `raw_value_*` duerfen in der Detailtabelle erscheinen, aber nie in Seite 1
  - `conversion_factor` und `consumption_units` sind in HKV-Heizfaellen Pflicht
  - `consumption_units` ist die einzige zulaessige Umlagebasis fuer Heizkosten auf Seite 1

## Action Plan
1. [DONE] HKV-Nullability-Vertrag explizit gemacht — Evidence: fuer `heating_device_table.rows[]` gelten nun diese bindenden Feldregeln:
   - `room_label`, `device_type`, `serial_number`, `conversion_factor`, `consumption_units` = Pflicht in HKV-Heizfaellen
   - `raw_value_start`, `raw_value_end`, `raw_value_difference` = nullable
   - mindestens eines der drei `raw_value_*`-Felder darf gesetzt sein, wenn belastbar verfuegbar; keines davon ist fuer Seite 1 erforderlich
2. [DONE] HKV-Quellenzuordnung explizit gemacht — Evidence:
   - `serial_number` und `conversion_factor` stammen aus verifizierten Messgeraete-/Meterquellen
   - `raw_value_*` stammen ausschliesslich aus belastbaren Ablese-/Messwertquellen
   - `consumption_units` stammen aus der abrechnungswirksamen, faktorbereinigten HKV-Herleitung
   - Seite 1 (`reference_table`, `page1_cost_rows`) darf fuer Heizung nur `consumption_units` verwenden, nie `raw_value_*`
3. [DONE] Leak-Prevention-Regel fuer Seite 1 vertraglich gemacht — Evidence:
   - `reference_table.rows[heating_units_be1].tenant_value_display` und `.total_value_display` duerfen ausschliesslich Verbrauchseinheiten enthalten
   - `page1_cost_rows[]` fuer `Brennstoffkosten - Verbrauch 70 %` und `Heiznebenkosten` duerfen in `basis_display` ausschliesslich `consumption_units`-basierte Darstellungen enthalten
   - kein `raw_value_start`, `raw_value_end` oder `raw_value_difference` darf in Seite-1-Renderhelfer oder Seite-1-Tokenpfade durchgereicht werden
4. [DONE] HKV-Testgate vervollstaendigt — Evidence: die Verifikation deckt jetzt nicht nur Faktor-Sichtbarkeit ab, sondern auch die Negativregel:
   - rohe HKV-Werte duerfen im Hauptdokument nicht erscheinen
5. [PENDING] Iteration-5- bis Iteration-8-Arbeitspakete unter diesem finalen HKV-Vertrag umsetzen — Done when: die Implementierung die HKV-Detailseite, Seite-1-Heizbasis und zugehoerigen Tests genau entlang dieser Nullability-/Quellen-/Leak-Regeln umsetzt.

## Open Items
- [MISSING NON-BLOCKING] Juristische Endfassung der Hinweistexte kann spaeter weiter geschaerft werden; fuer die Implementierung reicht die derzeit freigegebene Arbeitsfassung, optional mit Ableitung aus der ista-Vorlage.

## Verification Test Cases
1. Given einen HKV-Heizfall mit vorhandenen Rohwerten, Faktoren und Verbrauchseinheiten, when `heating_device_table.rows[]` gebaut wird, then sind `conversion_factor` und `consumption_units` Pflichtfelder, waehrend `raw_value_start`, `raw_value_end` und `raw_value_difference` nur gesetzt sind, wenn belastbare Quelldaten vorliegen.
2. Given einen HKV-Heizfall, when `reference_table.rows[]` und `page1_cost_rows[]` fuer Heizung gebaut werden, then enthalten diese ausschliesslich `consumption_units`-basierte Anzeigen und keine `raw_value_*`-Felder oder Rohwertdarstellungen.
3. Given rohe HKV-Werte und daraus berechnete Verbrauchseinheiten, when die Seite-1-Kernkostentabelle gerendert wird, then sind rohe HKV-Werte im tenant-facing Hauptdokument nirgends sichtbar.
4. Given fehlende Rohwert-Start-/Enddaten, when die Heizungsdetailseite erzeugt wird, then bleibt die Seite weiterhin gueltig, solange `conversion_factor` und `consumption_units` sichtbar sind und rohe HKV-Werte nicht fuer Seite 1 missbraucht werden.
5. Given diese Iteration 9 zusammen mit Iteration 5 bis 8, when die Implementierung startet, then sind keine offenen document-contract-, wording-, lineage-, conditional-rendering- oder HKV-semantischen Planfragen mehr vorhanden.

# Iteration 10

## Summary
- Der letzte Restblocker war rein operational: die Formulierung `belastbar verfuegbar` fuer optionale HKV-Rohwerte war noch nicht als Lookup-Regel und Payload-Grenze definiert.
- Diese Iteration fixiert daher:
  - die Lookup-Reihenfolge fuer optionale HKV-Rohwerte,
  - die Definition von `belastbar verfuegbar`,
  - die Grenze zwischen internem Detail-Payload und tenant-facing Hauptdokument.

## Requirements Snapshot
- HKV-Rohwerte duerfen im tenant-facing Hauptdokument nie als Heizbasis, Vergleichswert oder Quotengrundlage erscheinen.
- HKV-Rohwerte duerfen nur auf der Heizungs-Detailseite auftauchen und auch dort nur, wenn sie aus einer verifizierten Ablesequelle der konkreten Geraetezeile stammen.

## Current State Snapshot
- Iteration 9 hat bereits Pflicht-/Optionalfelder und Leak-Prevention fixiert.
- Es fehlte noch die genaue Regel, wann `raw_value_* = null` korrekt ist und wann ein Implementierer Rohwerte aktiv nachladen muss.

## Action Plan
1. [DONE] `Belastbar verfuegbar` operational definiert — Evidence:
   - fuer `heating_device_table.rows[]` gilt folgende Lookup-Reihenfolge fuer `raw_value_start`, `raw_value_end`, `raw_value_difference`:
     1. verifizierte HKV-Ablese-/Messwertquelle der konkreten Geraetezeile im kanonischen Snapshot / normalisierten Messwertbestand,
     2. daraus eindeutig abgeleitete, geraetebezogene Workbook-/Importbeobachtung, sofern sie bereits in den normalisierten Pipeline-Daten angekommen ist,
     3. sonst `null`
   - Rohwerte werden **nicht** ad hoc aus beliebigen Fremdtabellen fuer das Rendering nachgezogen; massgeblich ist der normalisierte Pipeline-Datenstand
2. [DONE] Payload-Grenze explizit gemacht — Evidence:
   - `heating_device_table.rows[]` darf optionale `raw_value_*`-Felder tragen
   - `reference_table.rows[]`, `page1_cost_rows[]`, `result_box`, `advance_payment_explanation` und sonstige Seite-1-Renderpfade duerfen niemals `raw_value_*` enthalten oder daraus formatiert werden
   - damit ist erlaubt: Rohwerte im Detail-Payload; verboten: Rohwerte im Hauptdokument oder in dessen Tokenpfaden
3. [DONE] Nullability-Regel final praezisiert — Evidence:
   - `raw_value_* = null` ist korrekt, wenn nach Lookup-Reihenfolge keine verifizierte, geraetebezogene Rohwertquelle im normalisierten Datenstand vorliegt
   - `raw_value_* != null` ist nur korrekt, wenn der Wert derselben Geraetezeile belastbar zugeordnet ist
   - `conversion_factor` und `consumption_units` bleiben davon unberuehrt Pflicht
4. [DONE] Verifikationsorakel fuer den Grenzfall ergaenzt — Evidence:
   - Tests pruefen jetzt nicht nur, dass Rohwerte nicht in Seite 1 erscheinen, sondern auch, dass `null` fuer `raw_value_*` bei fehlender normalisierter Quelle zulaessig ist und kein Implementierungsfehler
5. [PENDING] Implementierung entlang des finalen HKV-Sourcing-Vertrags starten — Done when: Output-Builder, Template und Tests die Lookup-Reihenfolge, Nullability-Regel und Hauptdokument-Grenze exakt uebernehmen.

## Open Items
- [MISSING NON-BLOCKING] Juristische Endfassung der Hinweistexte kann spaeter weiter geschaerft werden; fuer die Implementierung reicht die derzeit freigegebene Arbeitsfassung, optional mit Ableitung aus der ista-Vorlage.

## Verification Test Cases
1. Given eine HKV-Geraetezeile mit verifizierten normalisierten Rohwerten, when `heating_device_table.rows[]` gebaut wird, then werden die passenden `raw_value_*`-Felder befuellt und `conversion_factor` plus `consumption_units` sichtbar gemacht.
2. Given eine HKV-Geraetezeile ohne verifizierte normalisierte Rohwertquelle, when `heating_device_table.rows[]` gebaut wird, then bleiben `raw_value_* = null`, waehrend `conversion_factor` und `consumption_units` weiterhin Pflicht bleiben.
3. Given denselben Heizfall, when Seite 1 (`reference_table.rows[]`, `page1_cost_rows[]`) gebaut oder gerendert wird, then erscheinen ausschliesslich `consumption_units`-basierte Anzeigen und niemals rohe HKV-Werte.
4. Given interne Detail-Payloads mit optionalen `raw_value_*`, when die finalen tenant-facing Hauptdokument-Tokens erzeugt werden, then wird kein `raw_value_*`-Feld in einen Seite-1-Tokenpfad uebernommen.
5. Given Iteration 10 zusammen mit Iteration 5 bis 9, when die Implementierung startet, then sind keine offenen HKV-Nullability-, Sourcing-, Leak-Prevention- oder Hauptdokument-Abgrenzungsfragen mehr vorhanden.

# Iteration 11

## Summary
- Die tenant-facing Dokumentstruktur ist implementiert, aber die restliche 2024-Kostenabdeckung scheitert upstream noch daran, dass Belege nicht workbook-treu in `cost_entries` mit dem richtigen Buchungsscope und Verteilschluessel ueberfuehrt werden.
- Diese Iteration uebersetzt die neuen Spec-Entscheidungen aus Pipeline Iteration 15/16 in einen umsetzbaren Arbeitsslice:
  - `Betriebskosten C/D -> Buchungsscope`
  - `Stammdaten -> Kostenart/Verteilschluessel/nach Berechnungseinheit`
  - objektweit gebucht, aber fachlich BE-gebunden
  - Benutzerentscheidung vor dem Lauf fuer mehrdeutige Heizungsbauer-/Kaminfeger-Belege
  - Spezialsplit Gebaeudeversicherung

## Requirements Snapshot
- Aus einem Eingangsbeleg muss die Pipeline fuer die restlichen 2024-Kostenarten nicht nur `cost_type_id`, sondern auch den **richtigen Buchungsscope** und die **richtige Verteilungslogik** kennen.
- Verbindliche Regeln aus Spec + User-Input:
  - `Betriebskosten.C/D` liefern den Buchungsscope
  - `Stammdaten` liefern Verteilschluessel und `nach Berechnungseinheit`
  - alles mit Oel gehoert zu Berechnungseinheit 1
  - alles mit Holz, Pellets und zugehoerigen Holz-/Saegezubehoer-Belegen gehoert zu Berechnungseinheit 2
  - Gebaeudeversicherung ist kein einfacher globaler Topf, sondern splitet sich 2024 in:
    - separater Vertrag fuer `NE3`
    - gemeinsamer Vertrag fuer `NE1 + NE2`
    - gemeinsamer Vertrag fuer `NE4 + NE5`
  - Heizungsbauer-/Kaminfeger-Belege muessen vor dem Lauf vom Nutzer der relevanten Berechnungseinheit bzw. Scope-Entscheidung zugeordnet werden, weil sie prinzipiell fuer beide Berechnungseinheiten anfallen koennen

## Current State Snapshot
- [DONE] Die Einzelabrechnung kann jetzt den finalen Seite-1-/Detailseiten-Vertrag rendern, wenn die korrekten `cost_entries` und Umlagezeilen vorliegen.
- [DONE] Einfache Receipt-Faelle haben bereits harte Defaults:
  - `grundsteuer -> living_area + global`
  - `muellabfuhr -> persons + global`
  - `gebaeudeversicherung -> living_area + global`
  - `oberflaechenwasser -> living_area + global`
- [DONE] Der Receipt-Pfad kann Belege klassifizieren und in `cost_entries` ueberfuehren; Spezialfall Stadt-/Abgabenbescheid splittet bereits in mehrere Kostenarten.
- [BLOCKED] `receipt_processing.py` benutzt fuer heizungsnahe Kosten noch globale Defaults (`heiznebenkosten`/`brennstoffkosten` -> `living_area + global`) statt workbook-treuer Scope-/Key-Herleitung.
- [BLOCKED] `calculation_engine.py` blockiert `brennstoffkosten` und `heiznebenkosten` derzeit noch pauschal, wenn kein expliziter `unit`/`calculation_unit`-Scope vorliegt; das widerspricht der neuen Spec fuer objektweit gebuchte, aber BE-gebundene Kosten.

## Action Plan
1. [DONE] Zielbild fuer den tenant-facing Output steht — Evidence: `statement_payload_v2`, Typst-Template und Contract-Tests decken jetzt Seite 1, Detailseiten und HKV-Semantik ab; der Engpass ist nicht mehr das PDF, sondern die Input-/Cost-Entry-Herleitung.
2. [DONE] Fachvertrag fuer workbook-treue Cost-Entry-Normalisierung liegt jetzt vor — Evidence: Pipeline Iteration 15/16 fixieren Scope aus `Betriebskosten`, Schluessel aus `Stammdaten`, global->BE-Split und explizite 2024-Kostenartenabdeckung.
3. [PENDING] `Betriebskosten`-Normalizer einfuehren — Done when: aus einer workbook-/OCR-gematchten Betriebskostenzeile verbindlich `scope_type`, `scope_id`, `cost_type_id`, `allocation_basis`, `booked_scope_type`, `booked_scope_id` abgeleitet werden und leere `C/D` nicht mehr als pauschales `scope_missing` enden.
4. [PENDING] `Stammdaten`-basierten Kostenartenresolver einfuehren — Done when: `Kostenart -> Verteilschluessel -> nach Berechnungseinheit` zentral aufgeloest wird und Widersprueche zwischen `Betriebskosten.Umlageschluessel` und `Stammdaten` ein Review-/Validation-Item erzeugen.
5. [PENDING] Heizungsnahe Energietraeger-/BE-Regeln umsetzen — Done when:
   - Oel-Belege automatisch `Berechnungseinheit 1` zugeordnet werden,
   - Holz-/Pellets-/zugehoerige Holz-/Saegezubehoer-Belege automatisch `Berechnungseinheit 2` zugeordnet werden,
   - objektweit gebuchte heizungsnahe Kosten bei `nach Berechnungseinheit = x` nicht global verteilt, sondern zuerst auf relevante Berechnungseinheit(en) heruntergebrochen werden.
6. [PENDING] Spezialfall Gebaeudeversicherung 2024 abbilden — Done when die Pipeline die drei 2024-Vertragsgruppen explizit kennt:
   - `NE3`
   - `NE1 + NE2`
   - `NE4 + NE5`
   und daraus korrekte `cost_entries`/Scopes fuer die betroffenen Parteien erzeugt.
7. [PENDING] Benutzerentscheidung vor dem Lauf fuer mehrdeutige Heizungsbauer-/Kaminfeger-Belege implementieren — Done when die Pipeline ohne diese Vorabentscheidung nicht still raten darf, sondern einen klaren Pflichtinput erwartet und erst danach die Scope-Zuordnung fuer solche Belege aufloest.
8. [PENDING] Receipt-Defaults auf workbook-treue Regeln umstellen — Done when `COST_ENTRY_DEFAULTS` nicht mehr die finale Wahrheit fuer `gebaeudeversicherung`, `heiznebenkosten` und `brennstoffkosten` sind, sondern nur noch Fallback fuer klar globale, nicht mehrdeutige Belegarten.
9. [PENDING] Rechenkern fuer `booked_scope` vs. `final_distribution_scope` erweitern — Done when `global` gebuchte, aber BE-gebundene Kosten nicht mehr vom alten Guard geblockt werden und stattdessen in einen expliziten Zwei-Stufen-Pfad (`booked_scope -> final_distribution_scope -> party lines`) laufen.
10. [PENDING] Testmatrix fuer 2024 erweitern — Done when die Suite mindestens folgende Orakel abdeckt:
    - objektweite Betriebskostenzeile mit leerem `C/D` wird als global erkannt
    - Oel-Beleg -> Berechnungseinheit 1
    - Holz-/Pellets-Beleg -> Berechnungseinheit 2
    - Gebaeudeversicherung split NE3 / (NE1+NE2) / (NE4+NE5)
    - Heizungsbauer-/Kaminfeger-Beleg ohne Vorabentscheidung blockiert den Lauf
    - dieselben Belege mit Vorabentscheidung ergeben deterministische `cost_entries` und renderbare Einzelabrechnungen

## Open Items
- [DECISION NON-BLOCKING] Vorlauf-Mechanik fuer Nutzerentscheidungen: bevorzugt dedizierte Datei wie `operator_scope_decisions_{jahr}.yaml` statt Ueberladung bestehender `review_overrides`; Implementierung kann dies entscheiden, solange die Entscheidung **vor** dem produktiven Lauf vorliegen muss.
- [MISSING NON-BLOCKING] Fuer `Kalt- und Abwasser` ist noch zu verifizieren, ob im 2024-Fall weitere engere Unter-Splits als die derzeit spezifizierte globale Verbrauchslogik existieren; falls ja, muss dies in einem spaeteren kleinen Spec-/Plan-Slice nachgezogen werden.

## Verification Test Cases
1. Given eine Betriebskostenzeile `Heiznebenkosten / 376.66` mit leerem `C/D` und `Stammdaten.nach Berechnungseinheit = x`, when der Cost-Entry-Normalizer laeuft, then entsteht kein pauschales `scope_missing`, sondern ein Eintrag mit `booked_scope = global` und fachlicher Weiterleitung in den BE-Verteilungspfad.
2. Given ein Oel-Beleg fuer 2024, when die Cost-Entry-Normalisierung laeuft, then wird die Kostenposition Berechnungseinheit 1 zugeordnet.
3. Given ein Holz- oder Pellets-Beleg fuer 2024, when die Cost-Entry-Normalisierung laeuft, then wird die Kostenposition Berechnungseinheit 2 zugeordnet.
4. Given ein Gebaeudeversicherungs-Beleg des 2024-Falls, when die Normalisierung laeuft, then landet er in genau einer der drei Vertragsgruppen `NE3`, `NE1+NE2` oder `NE4+NE5` und nicht in einem pauschalen globalen Versicherungstopf.
5. Given ein Heizungsbauer- oder Kaminfeger-Beleg ohne vorgelagerte Nutzerentscheidung, when `run-folder` produktiv gestartet wird, then blockiert der Lauf mit einem klaren Review-/Input-Hinweis statt einer still geratenen BE-Zuordnung.
6. Given dieselben Belege mit hinterlegter Vorabentscheidung, when `run-folder` ausgefuehrt wird, then entstehen deterministische `cost_entries`, korrekte Umlagezeilen und Einzelabrechnungen ohne Scope-Widerspruch.

# Iteration 12

## Summary
- Die Specs sind jetzt planready:
  - Pipeline-Spec Iterationen `15-18`
  - Einzelabrechnung-Spec Iterationen `11-12`
- Damit ist der verbleibende Arbeitsslice nicht mehr "fachlich unklar", sondern ein klar sequenzierbarer Umbau:
  - `scope_type/scope_id` repraesentieren den finalen Verteilungsscope
  - `metadata.booked_scope_*` konservieren den Legacy-Buchungsscope
  - `unit_group` ist fuer 2024-Gebaeudeversicherung zulaessig
  - `_inputs/operator_scope_decisions_{jahr}.yaml` ist verbindlicher Pflichtinput fuer mehrdeutige heizungsnahe Servicebelege
  - tenant-facing Seite 1 braucht die Box `Berechnungseinheiten im Objekt`, sobald BE-bezogene Kostenzeilen sichtbar sind
- Diese Iteration zerlegt den Slice in eine konkrete Implementierungsreihenfolge mit Dateizielen, Done-Signalen und Abschlussverifikation.

## Requirements Snapshot
- Verbindliche Zielanforderungen aus der jetzt planready Spec:
  - workbook-/belegbasierte `cost_entries` muessen finalen Verteilungsscope und Buchungsscope getrennt fuehren
  - objektweit gebuchte, aber BE-gebundene Kosten duerfen nicht global weiterverteilt oder global gerendert werden
  - Oel -> `calculation_unit = 1`
  - Holz/Pellets/Holz-/Saegezubehoer -> `calculation_unit = 2`
  - Gebaeudeversicherung 2024 nutzt `unit` bzw. `unit_group` mit festen Gruppenslugs `NE3`, `NE1_NE2`, `NE4_NE5`
  - mehrdeutige Heizungsbauer-/Kaminfeger-/Servicebelege brauchen einen blocking Pflichtinput via `_inputs/operator_scope_decisions_{jahr}.yaml`
  - Seite 1 des tenant-facing Dokuments braucht eine vorgeschaltete Box `Berechnungseinheiten im Objekt`, wenn dort BE-bezogene Bezugsraeume vorkommen

## Current State Snapshot
- [DONE] Tenant-facing Statement-v2 ist technisch implementiert — Evidence: `output_writer.py`, `renderer.py`, `statement_template_v2.typ`, Contract-Tests fuer Seite 1 / Detailseiten / HKV.
- [DONE] Der aktuelle Rechenkern kann `global`, `unit` und `calculation_unit` verteilen — Evidence: `_parties_in_scope(...)` in `calculation_engine.py`.
- [DONE] Receipt-Pfad kann OCR-Belege klassifizieren, Review-Overrides anwenden und `CostEntryInput` erzeugen — Evidence: `receipt_processing.py`.
- [BLOCKED] `CostEntryInput`/Persistenz behandeln `scope_type/scope_id` aktuell noch implizit als einzigen Scope und fuehren keinen expliziten `booked_scope`-/`scope_rule_source`-Vertrag — Evidence: `models.py`, `run_db.py`, `input_loader.py`.
- [BLOCKED] `receipt_processing.py` nutzt fuer `gebaeudeversicherung`, `heiznebenkosten` und `brennstoffkosten` weiterhin harte Defaults statt finalem workbook-/spec-treuem Scope-Normalizer — Evidence: `COST_ENTRY_DEFAULTS`.
- [BLOCKED] `_inputs/operator_scope_decisions_{jahr}.yaml` existiert noch nicht als Loader-/Validation-Pfad.
- [BLOCKED] `calculation_engine.py` kennt `unit_group` nicht und blockiert heizungsnahe Kosten weiterhin, wenn kein direkter `unit`/`calculation_unit`-Scope vorliegt.
- [BLOCKED] Die tenant-facing Renderstrecke kennt die verpflichtende Box `Berechnungseinheiten im Objekt` noch nicht.

## Action Plan
1. [DONE] Tenant-facing Dokumentvertrag und HKV-Semantik stabilisieren — Evidence: bestehende Statement-v2-Implementierung und gruene Contract-Tests; dieser Slice baut darauf auf, ersetzt ihn aber nicht.
2. [DONE] Spec-Basis fuer den Cost-Entry-Slice schliessen — Evidence: Pipeline Iterationen 15-18 und Einzelabrechnung Iterationen 11-12 sind jetzt planready; die alte offene Plan-Entscheidung zur Operator-Datei ist damit supersediert.
3. [PENDING] Datenvertrag fuer finalen Scope vs. Buchungsscope in den Modellen fixieren — Done when:
   - `CostEntryInput` semantisch `scope_type/scope_id = final_distribution_scope` fuehrt,
   - `metadata.booked_scope_type`,
   - `metadata.booked_scope_id`,
   - `metadata.scope_rule_source`
   als verpflichtend befuellte Felder fuer normalisierte workbook-/receipt-basierte Kostenpositionen eingefuehrt sind,
   - und Persistenz/Loader diese Informationen ohne Informationsverlust round-trippen.
   Evidence of completion:
   - `models.py`
   - `input_loader.py`
   - `run_db.py`
   - Fixture-/Roundtrip-Test fuer `cost_entries`.
4. [PENDING] Pflichtinput `_inputs/operator_scope_decisions_{jahr}.yaml` laden und validieren — Done when:
   - die Datei im Jahresinput erkannt wird,
   - Pflichtfelder gemaess Spec 18 validiert werden,
   - die blocking Review-Kinds
     - `operator_scope_decision_missing`
     - `operator_scope_decision_ambiguous`
     - `operator_scope_decision_conflict`
     produziert werden koennen,
   - und ungenutzte/unguelle Eintraege nicht still ignoriert werden.
   Evidence of completion:
   - Loader-/Validator-Pfad existiert
   - Tests fuer missing / ambiguous / conflict.
5. [PENDING] Dedizierten Cost-Entry-Normalizer zwischen Receipt-/Workbook-Herkunft und Rechenkern einfuehren — Done when:
   - ein klarer Normalisierungsschritt existiert, der aus Eingangskostenpositionen finale `CostEntryInput`s erzeugt,
   - `Betriebskosten.C/D` nur den `booked_scope` setzen,
   - `Stammdaten` `allocation_basis` / `nach Berechnungseinheit` liefern,
   - und danach `scope_type/scope_id` als finaler Verteilungsscope gesetzt werden.
   Evidence of completion:
   - explizite Funktionsgrenze im Code (dedizierter Normalizer statt verstreuter Ad-hoc-Regeln)
   - Test fuer `booked_scope = global`, aber `final scope = calculation_unit`.
6. [PENDING] Heizungsnahe Energietraegerregeln in den Normalizer ueberfuehren — Done when:
   - `metadata.energy_carrier_family = oil_be1` zu `scope_type = calculation_unit`, `scope_id = 1` fuehrt,
   - `metadata.energy_carrier_family = wood_pellet_be2` zu `scope_type = calculation_unit`, `scope_id = 2` fuehrt,
   - und heizungsnahe Kosten nicht mehr ueber harte globale Defaults laufen.
   Evidence of completion:
   - Oel-/Holz-/Pellet-Tests
   - keine finale Scope-Wahrheit mehr in `COST_ENTRY_DEFAULTS` fuer diese Faelle.
7. [PENDING] Spezialfall Gebaeudeversicherung 2024 mit `unit_group` implementieren — Done when:
   - `NE3`, `NE1_NE2`, `NE4_NE5` als finale Versicherungsscopes erzeugt werden,
   - `metadata.scope_unit_ids` fuer Gruppenscopes persistiert wird,
   - und `unit_group` im Rechenkern korrekt auf Parteien aufloest.
   Evidence of completion:
   - `_parties_in_scope(...)` unterstuetzt `unit_group`
   - Test fuer Versicherung `NE1_NE2`
   - keine pauschal globale Versicherungsallokation fuer 2024 mehr.
8. [PENDING] Rechenkern auf finalen Scope-Vertrag umstellen — Done when:
   - der alte Guard fuer `brennstoffkosten`/`heiznebenkosten` nicht mehr auf "expliziter Scope fehlt" fuer objektweit gebuchte, aber fachlich BE-gebundene Positionen feuert,
   - stattdessen nur noch dann blockiert wird, wenn nach dem Normalizer **kein finaler Scope** oder ein konflikthafter Scope vorliegt,
   - und `unit_group` / `calculation_unit` / `unit` konsistent in Allocation-Lines ueberfuehrt werden.
   Evidence of completion:
   - kein `scope_missing` fuer zulaessige `booked_scope = global` + `final scope = calculation_unit`
   - Tests fuer Allocation-Lines aus BE1/BE2 und `unit_group`.
9. [PENDING] Rendering auf finalen Scope und neue Seite-1-BE-Box angleichen — Done when:
   - die Seite-1-Box `Berechnungseinheiten im Objekt` vor der ersten Kosten-/Bezugsraumtabelle erscheint, sobald BE-bezogene Kostenzeilen sichtbar sind,
   - Seite 1 / Detailseiten den finalen Scope aus `scope_type/scope_id` verwenden,
   - und der Legacy-Buchungsscope nicht versehentlich als tenant-facing Bezugsraum gerendert wird.
   Evidence of completion:
   - `statement_payload_v2`/Renderer/Typst-Template tragen die Box-Regel
   - Render-Test fuer Box-Praesenz bei BE-Zeilen
   - Render-Test fuer Auslassung der Box ohne BE-Zeilen.
10. [PENDING] Receipt-/Workbook-Fallbacks auf die neue Wahrheit umbauen — Done when:
    - `COST_ENTRY_DEFAULTS` nur noch fuer klar globale, nicht mehrdeutige Faelle wie `grundsteuer`, `muellabfuhr`, `oberflaechenwasser` als Fallback dienen,
    - spec-sensitive Faelle (`gebaeudeversicherung`, `heiznebenkosten`, `brennstoffkosten`) immer durch den Normalizer laufen,
    - und gemischte / nicht sauber splitbare Mehrbereichs-Belege blocking Review-/Split-Hinweise erzeugen.
    Evidence of completion:
    - Tests fuer mixed-scope receipt blocking
    - keine stille globale Versicherungs-/Heizkosten-Zuordnung mehr.
11. [PENDING] Abschlussvalidierung auf Fixture- und Gesamtsuiten-Niveau fahren — Done when:
    - die erweiterten Unit-/Integrationstests gruen sind,
    - `python3 -m unittest discover -s tests -t .` im Ordner `Vermietung/nebenkosten_pipeline` gruen laeuft,
    - und ein `run-folder`-Fixturelauf 2024 die neuen Scopes/Review-Gates/Renderregeln sichtbar produziert.
    Evidence of completion:
    - gruene Testsuite
    - erfolgreicher 2024-Run mit kontrollierten Review-Ausgaengen bzw. renderbaren PDFs.

## Open Items
- [MISSING NON-BLOCKING] Fuer `Kalt- und Abwasser` ist weiter zu verifizieren, ob der 2024-Fall neben der derzeit spezifizierten globalen Verbrauchslogik noch engere Unter-Splits braucht; falls ja, folgt dafuer ein kleiner separater Spec-/Plan-Slice.

## Verification Test Cases
1. Given ein `cost_entry` mit `booked_scope = global` und finalem `scope_type = calculation_unit`, when Loader/Persistenz/DB-Roundtrip durchlaufen werden, then bleiben `booked_scope`, finaler Scope und `scope_rule_source` erhalten.
2. Given `_inputs/operator_scope_decisions_{jahr}.yaml` mit zwei Eintraegen fuer denselben `source_fingerprint`, when der Jahresinput geladen wird, then blockiert der Lauf mit `operator_scope_decision_ambiguous`.
3. Given ein objektweit gebuchter Oel-Beleg, when der Cost-Entry-Normalizer laeuft, then entsteht `scope_type = calculation_unit`, `scope_id = 1` statt globalem Heizkosten-Scope.
4. Given ein objektweit gebuchter Holz-/Pellet-Beleg, when der Cost-Entry-Normalizer laeuft, then entsteht `scope_type = calculation_unit`, `scope_id = 2`.
5. Given ein 2024er Gebaeudeversicherungsbeleg fuer `NE1 + NE2`, when der Rechenkern laeuft, then wird `scope_type = unit_group`, `scope_id = NE1_NE2` korrekt auf die Parteien dieser Gruppe verteilt.
6. Given ein Heizungsbauer-Beleg ohne eindeutige Workbook-Zuordnung und ohne Operatorentscheidung, when `run-folder` produktiv laeuft, then blockiert der Lauf mit `operator_scope_decision_missing`.
7. Given derselbe Beleg mit gueltiger Operatorentscheidung, when der produktive Lauf ausgefuehrt wird, then folgen finaler Scope und `metadata.operator_decision_ref` exakt der Entscheidung.
8. Given eine Einzelabrechnung mit mindestens einer BE-bezogenen Kostenzeile auf Seite 1, when das Dokument gerendert wird, then erscheint vor der ersten Kosten-/Bezugsraumtabelle die Box `Berechnungseinheiten im Objekt`.
9. Given eine Einzelabrechnung ohne BE-bezogene Kostenzeilen auf Seite 1, when das Dokument gerendert wird, then fehlt die Box und `Berechnungseinheit 1/2` taucht spaeter nicht erstmals unerklaert auf.

# Iteration 13

## Summary
- Diese Iteration schliesst die letzten planseitigen Ausfuehrungsgrenzen aus dem Review zu Iteration 12:
  - exakte Persistenzstrategie fuer Scope-Metadaten
  - exakter Loader-Ort fuer `_inputs/operator_scope_decisions_{jahr}.yaml`
  - dedizierte Modul-/Funktionsgrenze fuer Cost-Entry-Normalisierung
  - exakte `unit_group`-Aufloesung im Rechenkern
  - exakter Payload-/Template-Hook fuer die Box `Berechnungseinheiten im Objekt`
- Damit ist der Plan nicht nur fachlich vollstaendig, sondern auch auf Modul-/Datenfluss-Ebene ausfuehrbar.

## Operative Kurzreferenz
- Die Spec und der Plan muessen **nicht physisch gekuerzt** werden.
- Fuer die Umsetzung dieses Slices gilt als kurze operative Referenz:
  - Pipeline-Spec Iterationen `15-18`
  - Einzelabrechnung-Spec Iterationen `11-12`
  - Implementierungsplan Iteration `13`
- Aeltere Iterationen bleiben als Historie erhalten, sollen fuer diesen Slice aber nur noch herangezogen werden, wenn Iteration 13 explizit auf sie verweist.

## Current State Snapshot
- [DONE] `PipelineInputs` traegt bereits mehrere `_inputs/*`-Artefakte als Top-Level-Felder; ein weiteres Top-Level-Feld ist konsistent mit der bestehenden Architektur — Evidence: `payment_totals`, `allocation_bases`, `target_rules`, `review_overrides`, `canonical_meters` in `models.py` / `input_loader.py`.
- [DONE] `run_pipeline_from_belege_dir(...)` ist der gemeinsame Orchestrierungspunkt fuer `_inputs`, OCR, Receipt-Extraktion und Pipeline-Lauf — Evidence: `pipeline.py`.
- [DONE] `run_pipeline_year(...)` ist der richtige Hook vor `allocate_cost_entries(...)` fuer einen vorgelagerten Normalisierungsschritt — Evidence: `pipeline.py`.
- [BLOCKED] `run_db.py` persistiert `cost_entries` noch ohne `metadata_json`; Scope-Metadaten wuerden dort aktuell verloren gehen.
- [BLOCKED] `input_loader.load_pipeline_inputs(...)` laedt noch keine `operator_scope_decisions_{jahr}.yaml`.
- [BLOCKED] Es gibt noch kein dediziertes Modul, das rohe/receipt-basierte `cost_entries` vor dem Rechenkern in finale Scopes ueberfuehrt.
- [BLOCKED] `_parties_in_scope(...)` kennt `unit_group` noch nicht.
- [BLOCKED] `statement_payload_v2` und `statement_template_v2.typ` haben noch keinen expliziten Box-Hook fuer `Berechnungseinheiten im Objekt`.

## Action Plan
1. [DONE] Fachliche Spec-Basis schliessen — Evidence: Specs sind planready; offene Fragen sind nur noch Implementierungsgrenzen, nicht mehr Produktverhalten.
2. [PENDING] `PipelineInputs` um `operator_scope_decisions` als Top-Level-Input erweitern — Done when:
   - `models.PipelineInputs` ein neues Feld `operator_scope_decisions: Dict[str, Any] = field(default_factory=dict)` traegt,
   - `input_loader.load_pipeline_inputs(...)` direkt neben `review_overrides_{jahr}.yaml` auch `_inputs/operator_scope_decisions_{jahr}.yaml` laedt,
   - und `available` dieses Dokument als gueltigen Input beruecksichtigt.
   Code boundary:
   - `models.py`
   - `input_loader.py`
   Evidence of completion:
   - Loader-Test fuer vorhandene/fehlende Datei
   - `PipelineInputs.operator_scope_decisions` ist im Lauf sichtbar.
3. [PENDING] Persistenzstrategie fuer `cost_entries.metadata` explizit auf `metadata_json` in `run.db` festziehen — Done when:
   - Tabelle `cost_entries` eine Spalte `metadata_json TEXT NOT NULL` traegt,
   - `persist_pipeline_result(...)` `json.dumps(entry.metadata, ensure_ascii=False, sort_keys=True)` in diese Spalte schreibt,
   - und ein Re-Run auf bestehender DB das Schema migrationssicher erweitert (z. B. per `ALTER TABLE ... ADD COLUMN` falls die Spalte noch fehlt).
   Verbindliche Folge:
   - `booked_scope`, `scope_rule_source`, `scope_unit_ids`, `operator_decision_ref` gehen im DB-Roundtrip nicht verloren.
   Code boundary:
   - `run_db.py`
   Evidence of completion:
   - DB-Roundtrip-Test fuer `metadata_json`
   - bestaehende Runs brechen nicht auf altem Schema.
4. [PENDING] Dediziertes Modul `cost_entry_normalization.py` einfuehren — Done when:
   - ein neues Modul `nebenkosten_pipeline/cost_entry_normalization.py` existiert,
   - es mindestens diese Funktionsgrenzen enthaelt:
     - `validate_operator_scope_decisions(inputs: PipelineInputs, receipts: list[ReceiptDocument]) -> list[ReviewItem]`
     - `normalize_cost_entries(inputs: PipelineInputs, receipt_documents: list[ReceiptDocument]) -> tuple[list[CostEntryInput], list[ReviewItem]]`
   - und keine verteilungsrelevante Scope-Wahrheit mehr allein in `receipt_processing.py` oder `calculation_engine.py` versteckt ist.
   Verbindlicher Aufrufort:
   - `pipeline.run_pipeline_year(...)`
   - direkt **vor** `allocate_cost_entries(...)`
   - nachdem `run_pipeline_from_belege_dir(...)` eventuelle `receipt_cost_entries` an `inputs.calculation_inputs.cost_entries` angehaengt hat.
   Evidence of completion:
   - expliziter Import/Aufruf in `pipeline.py`
   - Normalizer-Unit-Tests.
5. [PENDING] Operator-Decision-Validierung im Normalizer verankern — Done when:
   - `validate_operator_scope_decisions(...)` Matching primaer ueber `source_fingerprint` ausfuehrt,
   - `cost_type_id` gegen die normalisierte Position validiert,
   - die Review-Kinds
     - `operator_scope_decision_missing`
     - `operator_scope_decision_ambiguous`
     - `operator_scope_decision_conflict`
     exakt dort entstehen,
   - und diese Reviews als blocking in den bestehenden Pipeline-Status einfliessen.
   Code boundary:
   - Validierung im neuen Modul `cost_entry_normalization.py`
   - Statusentscheidung bleibt in `pipeline.py` ueber bestehende `severity == 'blocking'`-Logik.
   Evidence of completion:
   - missing / ambiguous / conflict Tests
   - produktiver Lauf ohne passende Entscheidung endet in `status = needs_review`.
6. [PENDING] Population von `energy_carrier_family` an der Inputkante explizit festziehen — Done when:
   - `receipt_processing.py` fuer heizungsnahe Receipt-Faelle `metadata.energy_carrier_family` direkt beim Erzeugen der rohen `CostEntryInput`s setzt, sofern der OCR-/Keyword-Kontext Oel vs. Holz/Pellets eindeutig hergibt,
   - strukturierte/workbook-nahe `cost_entries` dieselbe Information optional bereits aus YAML-`metadata` mitbringen duerfen,
   - und der Normalizer fuer BE-gebundene heizungsnahe Kosten ohne
     - expliziten finalen Scope,
     - passende Operatorentscheidung,
     - oder `energy_carrier_family`
     einen blocking Review erzeugt statt still global zu bleiben.
   Evidence of completion:
   - Receipt-Tests fuer Oel/Holz/Pellets
   - blocking Test fuer fehlende Energietraegerfamilie in einem BE-gebundenen Heizkostenfall.
7. [PENDING] Final-Scope-Normalisierung im neuen Modul zentralisieren — Done when:
   - der Normalizer fuer jede Eingangsposition verbindlich setzt:
     - `scope_type/scope_id` als finaler Scope
     - `metadata.booked_scope_type`
     - `metadata.booked_scope_id`
     - `metadata.scope_rule_source`
   - `Betriebskosten.C/D` nur als `booked_scope` interpretiert werden,
   - und der Normalizer die Prioritaet aus der Spec exakt umsetzt:
     - `D`
     - dann `C`
     - dann Operatorentscheidung
     - dann deterministische Fachregel
     - dann sonstiger Buchungsscope.
   Evidence of completion:
   - Test fuer `booked_scope = global` -> `final scope = calculation_unit`
   - Test fuer Konflikt zwischen explizitem Workbook-Scope und Operatorentscheidung.
8. [PENDING] `unit_group` im Rechenkern explizit ueber `metadata.scope_unit_ids` aufloesen — Done when:
   - `calculation_engine._parties_in_scope(...)` einen Branch `scope_type == 'unit_group'` besitzt,
   - die betroffenen `unit_id`s ausschliesslich aus `entry.metadata['scope_unit_ids']` zieht,
   - und fuer leere/ungueltige `scope_unit_ids` einen blocking Review produziert statt leerer stiller Verteilung.
   Verbindliche Hilfsfunktion:
   - `_unit_ids_for_unit_group(entry: CostEntryInput) -> set[str]`
   Evidence of completion:
   - Test fuer `NE1_NE2`
   - Test fuer ungueltiges `unit_group` ohne `scope_unit_ids`.
9. [PENDING] Alten Heizkosten-Guard auf den finalen Scope-Vertrag umstellen — Done when:
   - `calculation_engine.allocate_cost_entries(...)` heizungsnahe Kosten nicht mehr anhand des rohen Legacy-Scopes blockiert,
   - sondern nur noch blockiert, wenn nach dem Normalizer kein gueltiger finaler Scope vorliegt,
   - und `scope_missing` fuer zulaessige `booked_scope = global`, `final scope = calculation_unit` verschwindet.
   Evidence of completion:
   - Regressionstest fuer bisherigen Guard
   - gruenes Szenario fuer objektweit gebuchte, aber BE-gebundene Heizkosten.
10. [PENDING] Page-1-BE-Box ueber expliziten Payload-Hook implementieren — Done when:
    - `output_writer._build_statement_payload_v2(...)` ein neues Feld wie `calculation_unit_box` oder `page1_calculation_unit_box` erzeugt,
    - dieses Feld aus `page1_cost_rows` bzw. den zugrunde liegenden Sections ableitet, ob Seite 1 BE-bezogene Kostenzeilen enthaelt,
    - und `statement_template_v2.typ` die Box **vor** `== Kostenuebersicht fuer Ihren Mietzeitraum` rendert.
    Verbindlicher Inhalt des Payload-Hooks:
    - Titel `Berechnungseinheiten im Objekt`
    - Zeilen fuer Berechnungseinheit 1 und 2 gemaess Spec 12
    - Flag/Leerseinheit fuer den Fall ohne Box
    Evidence of completion:
    - Render-Test mit Box
    - Render-Test ohne Box
    - kein unerklaertes erstes Auftreten von `Berechnungseinheit 1/2`.
11. [PENDING] Operative Abschlussverifikation auf den kuerzesten reproduzierbaren Pfad trimmen — Done when:
    - die neuen Unit-Tests fuer Loader, Normalizer, Rechenkern und Rendering gruen sind,
    - die Gesamtsuite `python3 -m unittest discover -s tests -t .` im Ordner `Vermietung/nebenkosten_pipeline` gruen laeuft,
    - und ein 2024-Fixturelauf mindestens einen Fall aus jeder neuen Klasse zeigt:
      - finaler `calculation_unit`-Scope
      - `unit_group`
      - blocking Operatorentscheidung
      - BE-Box auf Seite 1.
    Evidence of completion:
    - dokumentierter Fixturelauf
    - keine planseitig offenen BLOCKED-Items mehr fuer diesen Slice.

## Open Items
- [MISSING NON-BLOCKING] Fuer `Kalt- und Abwasser` ist weiter zu verifizieren, ob der 2024-Fall neben der derzeit spezifizierten globalen Verbrauchslogik noch engere Unter-Splits braucht; dies ist bewusst aus dem aktuellen Implementierungsslice ausgeklammert.

## Verification Test Cases
1. Given `_inputs/operator_scope_decisions_{jahr}.yaml`, when `load_pipeline_inputs(...)` laeuft, then steht der Inhalt in `PipelineInputs.operator_scope_decisions` zur Verfuegung.
2. Given ein `CostEntryInput` mit `metadata.booked_scope_type`, `metadata.scope_rule_source` und `metadata.scope_unit_ids`, when `persist_pipeline_result(...)` schreibt, then landen diese Felder in `cost_entries.metadata_json` und bleiben im DB-Roundtrip erhalten.
3. Given ein objektweit gebuchter Oel-Beleg ohne explizites `C/D`, when `normalize_cost_entries(...)` laeuft, then entsteht `scope_type = calculation_unit`, `scope_id = 1` und `metadata.scope_rule_source = energy_carrier_family`.
4. Given ein mehrdeutiger Heizungsservicebeleg ohne passende Operatorentscheidung, when `normalize_cost_entries(...)` laeuft, then entsteht `operator_scope_decision_missing` und der Lauf endet spaeter in `needs_review`.
5. Given ein 2024er Gebaeudeversicherungsbeleg fuer `NE1 + NE2`, when `allocate_cost_entries(...)` laeuft, then verteilt `_parties_in_scope(...)` nur auf die Parteien aus `metadata.scope_unit_ids = [NE1, NE2]`.
6. Given ein BE-bezogenes Statement auf Seite 1, when `_build_statement_payload_v2(...)` und `statement_template_v2.typ` rendern, then erscheint die Box `Berechnungseinheiten im Objekt` vor der Kostenuebersicht.
7. Given ein nicht-BE-bezogenes Statement auf Seite 1, when dasselbe Rendering laeuft, then erscheint keine Box und es gibt spaeter kein erstes unerklaertes Auftreten von `Berechnungseinheit 1/2`.

# Iteration 14

## Summary
- Diese Iteration schliesst die drei letzten lokalisierten Ausfuehrungsluecken aus dem Review zu Iteration 13:
  - wer `metadata.scope_unit_ids` fuer `unit_group` befuellt
  - worauf `_inputs/operator_scope_decisions_{jahr}.yaml` genau matcht
  - wie der Payload-Hook fuer die Seite-1-BE-Box konkret aussieht
- Damit ist der Plan jetzt bis zur Ebene konkreter Datenobjekte und Funktionsverantwortungen heruntergebrochen.

## Current State Snapshot
- [DONE] Receipt-basierte mehrdeutige Heizungsservicefaelle besitzen bereits `ReceiptDocument.source_fingerprint`; genau dort ist das Operator-Matching anschlussfaehig — Evidence: `receipt_processing.py`.
- [DONE] YAML-/strukturierte `cost_entries` koennen bereits `metadata` mitbringen; der Normalizer kann diese Quelle uebernehmen, ohne einen zweiten Inputpfad zu erfinden — Evidence: `input_loader.py`.
- [BLOCKED] Die Verantwortung fuer `scope_unit_ids` bei `unit_group` war im Plan noch nicht explizit dem Normalizer zugewiesen.
- [BLOCKED] Der Plan hatte noch nicht explizit gesagt, dass Operatorentscheidungen **nur** receipt-basierte mehrdeutige Servicebelege adressieren.
- [BLOCKED] Der BE-Box-Hook war als Feldidee beschrieben, aber noch nicht als konkreter Payloadvertrag.

## Action Plan
1. [DONE] Spec- und Modulgrenzen schliessen — Evidence: Iteration 13 hat Loader-/Persistenz-/Normalizer-/Rechenkern-/Rendering-Orte festgelegt.
2. [PENDING] Operatorentscheidungen explizit auf receipt-basierte mehrdeutige Servicebelege begrenzen — Done when:
   - der Plan festlegt, dass `_inputs/operator_scope_decisions_{jahr}.yaml` ausschliesslich gegen `ReceiptDocument.source_fingerprint` matched,
   - nur fuer receipt-basierte, mehrdeutige heizungsnahe Servicebelege gilt,
   - und **nicht** fuer bereits strukturierte YAML-/Workbook-`cost_entries` verwendet wird.
   Verbindliche Folge:
   - es ist keine zweite Fingerprint- oder Matching-Strategie fuer nicht-receipt-basierte Kostenpositionen noetig.
   Code boundary:
   - `receipt_processing.py` liefert die `ReceiptDocument`s
   - `cost_entry_normalization.py` matched Entscheidungen nur gegen diese Receipt-Liste.
3. [PENDING] Normalizer als alleinige Quelle fuer `unit_group.scope_unit_ids` festziehen — Done when:
   - `normalize_cost_entries(...)` fuer jede Position mit finalem `scope_type = unit_group` verpflichtend auch `metadata.scope_unit_ids` setzt,
   - die Aufloesung aus einer expliziten Mapping-Tabelle im Normalizer kommt:
     - `NE3 -> [NE3]`
     - `NE1_NE2 -> [NE1, NE2]`
     - `NE4_NE5 -> [NE4, NE5]`
   - und `calculation_engine._parties_in_scope(...)` diese Daten nur noch konsumiert/validiert, aber nicht mehr selbst herleitet.
   Verbindliche Folge:
   - die Wahrheit fuer Gruppenscopes liegt im Normalizer, nicht verteilt zwischen Normalizer und Rechenkern.
   Evidence of completion:
   - Test fuer `NE1_NE2` mit gesetztem `scope_unit_ids`
   - Test fuer fehlendes `scope_unit_ids` als Guard gegen inkonsistente Fremdeintraege.
4. [PENDING] Unified-Normalization-Input explizit festziehen — Done when:
   - der Plan festlegt, dass `normalize_cost_entries(...)` **die gesamte Liste** `inputs.calculation_inputs.cost_entries` verarbeitet,
   - also sowohl YAML-geladene als auch receipt-abgeleitete Eintraege,
   - nachdem `run_pipeline_from_belege_dir(...)` receipt-cost-entries angehaengt hat,
   - aber bevor `allocate_cost_entries(...)` startet.
   Verbindliche Folge:
   - es gibt genau **einen** finalen Normalisierungslauf fuer alle Inputquellen.
   Code boundary:
   - `pipeline.py`
5. [PENDING] Payloadvertrag fuer die Box `Berechnungseinheiten im Objekt` konkretisieren — Done when:
   - `output_writer._build_statement_payload_v2(...)` ein Feld `page1_calculation_unit_box` erzeugt mit exakt dieser Struktur:
     - `enabled: bool`
     - `title: "Berechnungseinheiten im Objekt"`
     - `definitions: list[str]`
   - `enabled` genau dann `True` ist, wenn mindestens eine `page1_cost_rows`-Zeile aus einem Section-Scope `calculation_unit` stammt,
   - `definitions` die zwei statischen Spec-12-Texte fuer Berechnungseinheit 1 und 2 enthaelt,
   - und `statement_template_v2.typ` die Box nur bei `enabled = true` vor der Seite-1-Kostentabelle rendert.
   Verbindliche Folge:
   - `unit_group` allein triggert die Box nicht; die Box ist nur fuer sichtbare Berechnungseinheit-1/2-Bezugsraeume auf Seite 1 da.
   Evidence of completion:
   - Render-Test mit `enabled = true`
   - Render-Test mit `enabled = false`.
6. [PENDING] Abschlussverifikation auf Implementation-Ready-Niveau einfrieren — Done when:
   - die neuen Tests aus Iteration 13 plus diese drei Praezisierungen ohne Plan-Luecken formulierbar sind,
   - und kein verbleibender Action-Point den Implementierer noch zu eigener Datenmodell- oder Matching-Erfindung zwingt.

## Open Items
- [MISSING NON-BLOCKING] Fuer `Kalt- und Abwasser` bleibt die moegliche spaetere Verfeinerung unveraendert ausserhalb dieses Slices.

## Verification Test Cases
1. Given `_inputs/operator_scope_decisions_{jahr}.yaml`, when der Normalizer laeuft, then werden Entscheidungen nur gegen `ReceiptDocument.source_fingerprint` gematcht und nie gegen nicht-receipt-basierte YAML-/Workbook-Eintraege.
2. Given ein `unit_group`-Eintrag mit `scope_id = NE1_NE2`, when `normalize_cost_entries(...)` laeuft, then setzt der Normalizer `metadata.scope_unit_ids = [NE1, NE2]`.
3. Given derselbe `unit_group`-Eintrag, when `_parties_in_scope(...)` laeuft, then konsumiert er nur `metadata.scope_unit_ids` und leitet die Gruppe nicht noch einmal selbst her.
4. Given ein Statement mit mindestens einer Page-1-Zeile aus `scope_type = calculation_unit`, when `_build_statement_payload_v2(...)` laeuft, then enthaelt `page1_calculation_unit_box` `enabled = true`, den festen Titel und die zwei Definitionen.
5. Given ein Statement ohne Page-1-Zeile aus `scope_type = calculation_unit`, when dasselbe Payload gebaut wird, then ist `page1_calculation_unit_box.enabled = false`.

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-03-23 | 1 | Claude | Derived a separate implementation plan from the Einzelabrechnung spec with executable actions, current-state snapshot, open items, and verification cases |
| 2026-03-23 | 2 | Claude | Refined the plan with migration strategy, explicit v2 payload contract, scope grouping rules, meter source priority, phased test plan, and oracle integration details |
| 2026-03-23 | 3 | Claude | Operationalized meter section mapping with source precedence, nullability rules, render eligibility, and proof/report fallbacks |
| 2026-03-23 | 4 | Claude | Rebased the implementation plan on the approved tenant-facing mock, turning the existing v2 output into a redesign baseline with explicit page, oracle, and HKV-conversion work packages |
| 2026-03-23 | 5 | Claude | Closed the remaining plan-readiness gaps with explicit page-1 payload fields, HKV device-table contract, render-layout rules, and contract-level oracle tests |
| 2026-03-23 | 6 | Claude | Synced the plan explicitly with the binding HKV semantics from the final spec, fixed page-1 row order, and clarified execution sequencing for implementation-readiness |
| 2026-03-23 | 7 | Claude | Added explicit per-row derivation rules, concrete reference-fixture lineage for the electricity anchor, and conditional rendering rules for the HKV device table |
| 2026-03-23 | 8 | Claude | Locked the exact tenant-facing wording and render rules for HKV labels, prepayment text, page-1 notice, electricity anchor text, and time-period display |
| 2026-03-23 | 9 | Claude | Finalized the HKV payload contract with explicit field nullability, source separation, and a verification gate preventing raw HKV values from leaking into page 1 |
| 2026-03-23 | 10 | Claude | Defined the operational lookup order for optional HKV raw values, clarified normalized-source nullability, and locked the payload boundary between heating detail and page 1 |
| 2026-03-23 | 11 | Claude | Extended the plan upstream from statement rendering to workbook-faithful cost-entry normalization, including Betriebskosten/Stammdaten derivation, BE1/BE2 energy rules, insurance split, and required pre-run operator decisions |
| 2026-03-23 | 12 | Copilot | Rebased the implementation plan on the now planready specs, adding an executable sequence for final-scope data contracts, operator decision loading, dedicated normalization, unit_group allocation, page-1 BE box rendering, and end-to-end verification |
| 2026-03-23 | 13 | Copilot | Closed the last execution-boundary gaps with exact loader, persistence, normalizer, unit_group, and page-1 box hooks; designated Iteration 13 as the operative short reference instead of physically shortening the append-only docs |
| 2026-03-23 | 14 | Copilot | Closed the final localized data-flow gaps by fixing receipt-only operator matching, normalizer-owned unit_group scope_unit_ids, unified normalization input, and the exact page1_calculation_unit_box payload contract |

Claude session ID: `5ff61b4a-8355-4271-b526-26f6f9832807`
