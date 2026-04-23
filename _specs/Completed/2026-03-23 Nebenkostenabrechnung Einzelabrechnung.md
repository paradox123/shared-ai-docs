# Nebenkostenabrechnung Einzelabrechnung

Zweck dieses Dokuments:
- eigener Plan-/Spec-Strang fuer die **formell und inhaltlich ausreichende Einzelabrechnung** als Endprodukt der Nebenkosten-Pipeline,
- aufbauend auf der bestehenden Pipeline-Spec `2026-03-14 Nebenkostenabrechnung Pipeline.md`,
- mit Fokus auf **Darstellung, Nachvollziehbarkeit, juristische Mindestangaben und Reader-Qualitaet** der Mieter-Abrechnung.

Bezug zur bestehenden Pipeline-Spec:
- Die Pipeline-Spec bleibt fuer Datenfluss, OCR, Rechenkern, Artefakte, Review-Logik und Output-Ordner autoritativ.
- Dieses Dokument verfeinert speziell den Teil **Einzelabrechnung als lesbares Enddokument**.
- Es ersetzt nicht Iteration 13/14 der Pipeline-Spec, sondern konkretisiert das dort noch zu duenne Ergebnisdokument.


# Iteration 0

Quelle: Nutzerprompt vom 2026-03-23, inhaltlich uebernommen und auf die Kernaussagen verdichtet.

## Ausgangslage

Das aktuell erzeugte Ergebnis der Pipeline ist **nicht ausreichend als Einzelabrechnung**. Die Werte koennen in der MVP-Version bzw. in Iteration 14 weitgehend zusammen sein, aber die erzeugte PDF hat noch nicht genug "Fleisch an den Knochen".

Beispiel fuer aktuelle Pipeline-Ausgabe:
- `private/Vermietung/nebenkosten_pipeline/fixtures/2024/Einzelabrechnungen/Koenig/einzelabrechnung_2024.pdf`

Beispiel fuer externe Referenz:
- `.../Nebenkostenabrechnung/2023/.../Einzelabrechnung_026490450_2023_0001_0_Kraft_Hühne_03_09_2024_4.pdf`

Nutzer-Einschaetzung zum ista-Beispiel:
- es enthaelt im Wesentlichen die erforderlichen Werte,
- aber es hat zu viel allgemeinen Text,
- und die Vermischung zwischen Verbrauchseinheit 1 und 2 verwirrt eher, als dass sie hilft.

## Formelle Mindestanforderungen laut Prompt

Die Einzelabrechnung muss mindestens so aufgebaut sein, dass ein durchschnittlicher Mieter sie **gedanklich und rechnerisch nachvollziehen** kann. Enthalten sein muessen mindestens:

- Abrechnungszeitraum,
- Gesamtkostenaufstellung fuer das gesamte Gebaeude je Kostenart, => das lässt sich so allgemein nicht sagen, Gesamtheizkosten müssen nach Verbrauchseinheit aufgestellt werden - sonst gibt es diese Vermischung zwischen Verbrauchseinheit 1 und 2 was die Mieter verwirrt.
- Verteilerschluessel inkl. Erlaeuterung,
- Berechnung des konkreten Mieteranteils,
- Abzug der Vorauszahlungen.

## Weitere fachliche Anforderungen laut Prompt

- Fristlogik und formale Wirksamkeit muessen mitgedacht werden.
- Es duerfen nur umlagefaehige Kosten abgerechnet werden.
- Heiz- und Warmwasserkosten muessen den Regeln der Heizkostenverordnung genuegen.
- Der Mieter muss Belegeinsicht nehmen koennen.
- Die Abrechnung soll **wesentlich klarer, knapper und besser strukturiert** sein als das ista-Beispiel.
- Werte sollen **tabellarisch und nachvollziehbar** dargestellt werden; kein Copy/Paste von Bildinhalten.

## Ziel fuer diesen neuen Plan

Es soll ein **neuer Implementierungsplan** erstellt werden, der:
- diese Anforderungen als neuen Spec-Strang festhaelt,
- das Beispiel-PDF und den aktuellen Source Code beruecksichtigt,
- die Requirements fuer eine bessere Einzelabrechnung verfeinert,
- und als Grundlage fuer die naechste Umsetzungsstufe dient.

Begleitende Rechts-/Praxisreferenzen:
- Der Nutzerprompt enthaelt 16 externe Referenzen zu Form, Frist, BetrKV, HeizkostenV, Belegeinsicht und typischen Fehlern.
- Diese werden in diesem Dokument als rechtlicher Kontext akzeptiert; die konkrete juristische Schlussredaktion der Textbausteine bleibt spaeterer Review-Schritt.


# Iteration 1

Delta zu Iteration 0:
- Beispiel-PDF der ista gelesen.
- aktuellen Source Code der Pipeline fuer Statement-/Render-Pfad gelesen.
- daraus die Luecke zwischen **vorhandenen Daten** und **formal ausreichender Einzelabrechnung** abgeleitet.
- daraus einen umsetzbaren Plan fuer **Einzelabrechnung v2** formuliert.

## Gelesene Referenzen

Beispiel-PDF:
- `.../Einzelabrechnung_026490450_2023_0001_0_Kraft_Hühne_03_09_2024_4.pdf`

Wesentliche aktuelle Codepfade:
- `private/Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/output_writer.py`
- `private/Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/renderer.py`
- `private/Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/templates/statement_template_v1.typ`
- `private/Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/templates/audit_template_v1.typ`
- `private/Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/pipeline.py`
- `private/Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/run_artifacts.py`
- `private/Vermietung/nebenkosten_pipeline/tests/test_pipeline_tdd.py`
- Bezug zur bestehenden Spec:
  - `private/_shared/_specs/2026-03-14 Nebenkostenabrechnung Pipeline.md`

## Erkenntnisse aus dem ista-Beispiel

Das Beispiel-PDF zeigt, was fuer eine formal belastbare Abrechnung mindestens sichtbar sein muss:

1. **klare Identifikation**
   - Mieter / Nutzeinheit / Objekt / Abrechnungsdatum / Abrechnungszeitraum

2. **klare Ergebnisbox**
   - Gesamtkosten
   - Vorauszahlungen
   - Nachzahlung / Guthaben

3. **Ablese- und Verbrauchswerte**
   - konkrete Zaehler/Geraete
   - alt/neu/differenz
   - Umrechnungsfaktoren bzw. Verbrauchseinheiten

4. **Gesamtkostenaufstellung**
   - gesamte Liegenschaftskosten je Kostenart
   - bei Heizkosten zusaetzlich Untergliederung in Brennstoff, Heiznebenkosten, Zusatzkosten etc.

5. **Verteilungslogik sichtbar**
   - Gesamteinheiten der Liegenschaft
   - Betrag pro Einheit
   - Ihre Einheiten
   - Ihr Kostenanteil

6. **Heiz-/Warmwasser-Sonderlogik**
   - getrennte Darstellung von Heiz- und Warmwasserkosten
   - 30/70-Logik bzw. Verbrauchslogik sichtbar

Gleichzeitig bestaetigt das Beispiel die Nutzerkritik:
- zu viel allgemeiner Boilerplate-Text,
- zu viel fremde Nutzergruppen-Information im Hauptdokument,
- fuer den Mieter sind nicht alle ista-Zwischenschritte gleich wertvoll.

## Erkenntnisse aus dem aktuellen Code

Der aktuelle Pipeline-Output ist fuer ein MVP brauchbar, aber fuer eine belastbare Einzelabrechnung noch zu duenn:

- `output_writer.py` baut aktuell eine relativ flache `line_items`-Liste plus Summe/Zahlungsergebnis.
- `statement_template_v1.typ` rendert im Wesentlichen:
  - Titel,
  - Objekt/Partei/Zeitraum,
  - einfache Positionstabelle,
  - Summe,
  - bereits gezahlt,
  - Ergebnis,
  - Notizen.
- `audit_payload`/`pruefbericht` enthaelt deutlich mehr technische Nachvollziehbarkeit als die eigentliche Einzelabrechnung.

Das heisst:
- die **Datenbasis** ist inzwischen deutlich reicher als das gerenderte Enddokument,
- aber die **formale Darstellung fuer den Mieter** nutzt diese Daten noch nicht aus.

## Kernaussage der Verfeinerung

Die naechste Stufe ist **nicht primaer ein Rechenproblem**, sondern ein **Dokumentenmodell-/Renderproblem**:

- aus `cost_entries`, `allocation_lines`, `billing_parties`, `monthly_costs`, `ww_audit`, `receipt_documents`, `meter_observations` und `review_queue` muss eine **formal lesbare Einzelabrechnung v2** gebaut werden,
- waehrend der bestehende `Pruefbericht` weiterhin die technische Tiefenspur liefert.

Mit anderen Worten:
- **Einzelabrechnung = juristisch/formal/mieterlesbar**
- **Pruefbericht = technischer Rechenweg / Herkunft / Audit**

## Zielbild Einzelabrechnung v2

Die Einzelabrechnung v2 soll aus Sicht des Mieters folgende Frage beantworten:

> Welche Gesamtkosten sind fuer das Haus angefallen, nach welchem Schluessel wurden sie verteilt, welcher Anteil entfaellt auf mich, was habe ich schon bezahlt, und warum ist daraus genau dieses Ergebnis entstanden?

### Pflichtbereiche der Einzelabrechnung v2

1. **Kopf / Identifikation**
   - Objekt
   - Partei / Wohnung / Nutzeinheit
   - Abrechnungsdatum
   - Abrechnungszeitraum

2. **Ergebnisuebersicht**
   - Ihre Gesamtkosten
   - Ihre Vorauszahlungen
   - Ihre Nachzahlung oder Ihr Guthaben

3. **Verbrauchs- und Ablesewerte (nur soweit fuer diese Partei relevant)**
   - Strom / Warmwasser / Kaltwasser / Heizverbrauch / HKV
   - jeweils mit klarer Herkunft:
     - Geraet / Zaehler / Einheit
     - Alt / Neu / Differenz
     - ggf. Umrechnungsfaktor

4. **Gesamtkosten des Hauses je Kostenart**
   - z. B. Grundsteuer, Muellabfuhr, Gebaeudeversicherung, Oberflaechenwasser, Kalt- und Abwasser, Heiznebenkosten, Brennstoffkosten, Strom
   - inkl. ggf. Teilsummen fuer:
     - Heizung
     - Warmwasser
     - Hausnebenkosten

5. **Verteilerschluessel je Kostenart**
   - Schluesseltyp in lesbarer Form:
     - Wohnflaeche
     - Personen
     - Heizverbrauch
     - Warmwasserverbrauch
     - Kaltwasserverbrauch
     - direkte Zuordnung
   - Gesamteinheiten der Liegenschaft / des Scopes
   - Ihre Einheiten
   - Betrag pro Einheit oder rechnerische Quote

6. **Ihr Kostenanteil je Kostenart**
   - tabellarisch und rechnerisch nachvollziehbar
   - mit klarer Trennung:
     - Kostenart gesamt
     - Verteilerschluessel
     - Ihr Anteil
     - Ihr Betrag

7. **Abzug der Vorauszahlungen**
   - bereits gezahlt gesamt
   - idealerweise zusaetzlich:
     - Monatsabschlag x Anzahl Monate
     - nur als Erlaeuterung, nicht als Ersatz fuer den echten Zahlungswert

8. **Hinweisblock**
   - Belegeinsicht-Hinweis
   - ggf. kurzer Hinweis zur Pruefbarkeit / Quellen
   - keine unnötige Marketing-/Boilerplate

## Gestaltungsprinzipien

Die Einzelabrechnung v2 soll bewusst **nicht** wie ein Vollabzug des ista-Dokuments wirken.

Stattdessen gelten diese Regeln:

- Hauptdokument knapp und klar.
- Nur die fuer die Partei noetigen Werte im Hauptdokument.
- Fremde Nutzergruppen und unnoetige Objekt-Details nicht im Zentrum.
- Technisch tiefe Herleitung in den `Pruefbericht`, nicht in den Haupttext.
- Keine Bild-Collagen oder eingefuegte Screenshot-Beweise im Hauptdokument.
- Tabellen vor Freitext.

## Explizite Produktentscheidungen

- PDF bleibt Zielausgabe.
- Hauptdokument bleibt **deutlich schlanker** als das ista-Beispiel.
- Die bisher in `audit_payload`/`Pruefbericht` versteckte Rechenlogik wird **selektiv** in die Einzelabrechnung gehoben, aber nur in mieterlesbarer Form.
- Verbrauchseinheiten anderer Nutzergruppen sollen im Hauptdokument **nur dann** erscheinen, wenn sie fuer die konkrete Verteilung zwingend noetig sind.
- Die Heiz-/Warmwasser-Sonderlogik darf im Hauptdokument vorkommen, aber in **vereinfachter und erklaerter** Form.

## Ziel-Payload fuer Einzelabrechnung v2

Der aktuelle `statement_payload_v1` reicht inhaltlich nicht aus. Fuer v2 werden mindestens folgende Bereiche benoetigt:

- `document_header`
  - objekt
  - partei
  - nutzeinheit
  - abrechnungsdatum
  - abrechnungszeitraum

- `summary_box`
  - gesamtkosten_eur
  - vorauszahlungen_eur
  - nachzahlung_eur | guthaben_eur

- `meter_sections[]`
  - title
  - readings[]
    - meter_label
    - meter_id
    - unit
    - old_value
    - new_value
    - delta
    - factor
    - normalized_consumption

- `cost_type_sections[]`
  - cost_type_id
  - title
  - total_cost_eur
  - scope_label
  - items[]
    - label
    - source_ref
    - total_cost_eur
    - allocation_basis_label
    - denominator_total
    - tenant_units
    - rate_or_share
    - tenant_amount_eur

- `subtotals`
  - heating_total_eur
  - warmwater_total_eur
  - house_nebenkosten_total_eur
  - overall_total_eur

- `prepayment_section`
  - already_paid_eur
  - optional_explanation

- `notices`
  - belegeinsicht
  - kurze rechtliche/praktische Hinweise

## Explizite Abgrenzung zur Audit-Ausgabe

Die Einzelabrechnung v2 soll **nicht** den technischen Pruefbericht ersetzen.

Im Pruefbericht bleiben insbesondere:
- Fingerprints / OCR-Herkunft,
- `formula_code`,
- `denominator_group`,
- Review-Flags,
- technische Trace-Werte,
- tiefe Zwischenschritte und Spezialnormalisierung.

Die Einzelabrechnung enthaelt davon nur die **mieterlesbare Uebersetzung**.

## Umsetzungsplan

### Arbeitspaket 1 - Statement-Payload v2 definieren

Dateien:
- `output_writer.py`
- ggf. `models.py`

Ziel:
- neues, reichhaltigeres `statement_payload`-Schema erzeugen,
- ohne die vorhandene Audit-Struktur zu verlieren.

Kernaufgaben:
- Kostenzeilen nach Kostenarten gruppieren.
- Gesamtkosten je Kostenart sichtbar machen.
- lesbare Verteilerschluesseltexte ableiten.
- Verbraucher-/Zaehlerwerte fuer die jeweilige Partei aufbereiten.
- Vorauszahlungssektion ausbauen.

### Arbeitspaket 2 - Typst-Template fuer Einzelabrechnung v2

Dateien:
- `templates/statement_template_v1.typ` oder neues `statement_template_v2.typ`
- `renderer.py`

Ziel:
- aus Payload v2 eine formal starke PDF erzeugen.

Kernaufgaben:
- neue Template-Abschnitte:
  - Kopf
  - Ergebnisbox
  - Verbrauchswerte
  - Gesamtkosten je Kostenart
  - Verteilung / Ihr Anteil
  - Vorauszahlungen
  - Hinweise
- Layout so gestalten, dass zentrale Ergebniswerte auf Seite 1 klar sichtbar sind.

### Arbeitspaket 3 - Mieterlesbare Erlaeuterungen

Dateien:
- `output_writer.py`
- `renderer.py`
- Template-Datei

Ziel:
- aus technischen Schluesseln mieterlesbare Texte machen.

Beispiele:
- statt `persons_share_excluding_vacancy_with_dayshare`
  - "Verteilung nach Personenzahl, Leerstand nicht umlagefaehig, zeitanteilig"
- statt `heating_consumption_share`
  - "Verteilung nach Heizverbrauch"
- statt `electricity_tariff_monthly_direct`
  - "Direkte Stromkosten gemaess monatlicher Tarifbewertung"

### Arbeitspaket 4 - Beispiel-PDF als Reader-Oracle nutzen

Ziel:
- nicht den ista-Stil kopieren,
- aber pruefen, dass die **juristisch/inhaltlich notwendigen Werte** sichtbar vorhanden sind.

Vorgehen:
- Mapping-Tabelle:
  - Welche Pflichtinformation steht im ista-Beispiel?
  - Wo erscheint sie in Einzelabrechnung v2?
  - Falls bewusst weggelassen: wo steht die kompaktere Ersatzdarstellung?

### Arbeitspaket 5 - Regression und Reader-Tests

Ziel:
- sicherstellen, dass die neue Ausgabe nicht nur schoen, sondern pruefbar ist.

Verifikation:
- Snapshot-/Payload-Tests fuer neue Statement-Sektionen
- PDF-/Template-Regression
- frischer Reader-Test:
  - "Kann ein uninformierter Leser Zeitraum, Gesamtkosten, Schluessel, Mieteranteil und Ergebnis ohne Zusatzkontext finden?"

## Konkrete Akzeptanzkriterien

Die Einzelabrechnung v2 ist fuer MVP ausreichend, wenn fuer jede Mieter-Abrechnung gilt:

1. Zeitraum, Objekt, Partei und Ergebnis sind auf der ersten Seite direkt sichtbar.
2. Jede relevante Kostenart zeigt:
   - Gesamtkosten,
   - Verteilerschluessel,
   - Mieteranteil,
   - Betrag.
3. Vorauszahlungen sind explizit abgezogen.
4. Heiz-/Warmwasserlogik ist fuer die Partei sichtbar, aber nicht mit fremden Nutzergruppen ueberladen.
5. Ein Mieter kann das Dokument gemeinsam mit dem Pruefbericht und den Belegen nachvollziehen.
6. Das Dokument ist deutlich knapper und lesbarer als das ista-Beispiel, ohne formale Mindestangaben zu verlieren.

## Neue Marker

- [MISSING NON-BLOCKING] Finale juristische Formulierung fuer den Belegeinsicht-Hinweis und ggf. Zusatzhinweise zu Frist/Widerspruch festlegen. => keine Ahnung, macht da die ista Abrechnung was?
- [DECISION NON-BLOCKING] CO2-Kostenblock im Hauptdokument nur bei Relevanz anzeigen vs. immer in Anhang/Pruefbericht verschieben. => CO2 Kostenblock im Hauptdokument
- [DECISION NON-BLOCKING] Ob Zahlungsziel/Kontoverbindung Teil der Einzelabrechnung selbst sein sollen oder nur eines separaten Anschreibens. => Teil eines seperaten Anschreibens 8soll auch erstellt werden)
- [REVIEW] Vor finaler Umsetzung einmal Reader-Test gegen frische Claude-Instanz: "Finde Zeitraum, Gesamtkosten, Verteilerschluessel, Mieteranteil, Vorauszahlungen." => ja das ist ein guter Ansatz
=> es müsste auch noch betrachtet werden dass der code der pipeline nicht geändert werden darf ohne dass die testcases der pipeline getriggert werden (mit dem Reader-Oracle aus der Excel Abrechnung '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/Nebenkostenabrechnung_2024.xlsx'). entweder du nimmst die tests hier mit auf oder die editierst den code der pipeline nicht oder du nimmst die testcases aus der pipeline hier mit auf.

## Implementation-Ready-Startpunkt

Der Startpunkt fuer die naechste Umsetzung sollte sein:

1. `statement_payload_v2` spezifizieren,
2. `statement_template_v2` bauen,
3. vorhandene Daten (`allocation_lines`, `cost_entries`, `monthly_costs`, `ww_audit`, `meter_observations`) auf die neue Darstellung mappen,
4. das ista-Beispiel als formales Vergleichs-Oracle verwenden,
5. den Pruefbericht bewusst als technische Anlage erhalten.


# Iteration 2

Delta zu Iteration 1:
- Nutzer-Edits aus dem Dokument uebernommen und in konkrete Entscheidungen/Anforderungen umgewandelt.
- Unklare pauschale Formulierung "Gesamtkosten des Hauses je Kostenart" fuer Heiz-/Warmwasserkosten praezisiert.
- separates Anschreiben als zusaetzliches Artefakt aufgenommen.
- verpflichtende Test-/Regression-Gates gegen bestehende Pipeline-Tests und Reader-Oracle explizit gemacht.

## Uebernommene Korrekturen aus den Nutzer-Edits

### 1. Heiz-/Warmwasserkosten duerfen nicht pauschal als "gesamtes Gebaeude" dargestellt werden

Die bisherige Formulierung aus Iteration 0/1 war fuer Heizkosten zu grob.

Korrigierte Regel:
- **nicht jede Kostenart wird auf Ebene der Gesamtliegenschaft dargestellt**, sondern auf der **fachlich richtigen Verteilungsebene**.
- Das Hauptdokument muss deshalb Kostenarten nach **Abrechnungsscope** ausweisen:
  - **Objekt-/Haus-Scope** fuer echte globale Hausnebenkosten,
  - **Verbrauchseinheit/Berechnungseinheit-Scope** fuer Heiz-/Warmwasserkosten,
  - **direkter Einzelscope** fuer direkt zugeordnete Positionen.

Konsequenz fuer die Einzelabrechnung:
- Der Mieter soll **nicht** mit irrelevanten fremden Verbrauchseinheiten vermischt werden.
- Statt "Gesamtkosten des gesamten Hauses" als starre Pflicht gilt:
  - "Gesamtkosten des fuer diese Kostenart relevanten Umlagescopes".

Praxisbeispiele:
- `Grundsteuer`, `Muellabfuhr`, `Gebaeudeversicherung`, `Oberflaechenwasser`:
  - meist Objektscope
- `Brennstoffkosten`, `Heiznebenkosten`, `Warmwasserkosten`:
  - Scope der relevanten Heiz-/Verbrauchseinheit
- `Strom`:
  - direkter Parteien-/Zaehler-/Tarifpfad

Damit wird die ista-Schwachstelle "Vermischung VE1/VE2" fuer die neue Ausgabe explizit vermieden.

## Verfeinertes Zielbild: 3 Dokumente statt 2

Fuer die Mieter-Kommunikation werden kuenftig drei Ebenen unterschieden:

1. **Einzelabrechnung**
   - formal/juristisch/mieterlesbar
   - tabellarische Kerndarstellung

2. **Pruefbericht**
   - technischer Rechenweg
   - Quellen, Fingerprints, Formeln, OCR-/Normalisierungsspuren

3. **Anschreiben**
   - separates kurzes Begleitdokument
   - Zahlungsziel / Kontoverbindung / Begleittext
   - ausdruecklich **nicht** Teil des Kernbelegs der Einzelabrechnung

## Harte Entscheidungen aus den Nutzer-Edits

- [DECISION RESOLVED] Heiz-/Warmwasser-Gesamtkosten werden **scope-richtig** dargestellt, nicht pauschal als Gesamtliegenschaft, wenn das fachlich irrefuehrend ist.
- [DECISION RESOLVED] CO2-Kostenblock bleibt im **Hauptdokument**, sofern fuer die Partei relevant.
- [DECISION RESOLVED] Zahlungsziel/Kontoverbindung wandern in ein **separates Anschreiben**, nicht in die eigentliche Einzelabrechnung.
- [DECISION RESOLVED] Aenderungen am Pipeline-Code duerfen **nicht** ohne Test-/Oracle-Gates erfolgen.

## Verfeinerte Struktur der Einzelabrechnung v2

### Abschnitt A - Identifikation und Ergebnis

Pflicht:
- Objekt
- Partei / Nutzeinheit / ggf. Wohnungsbezeichnung
- Abrechnungsdatum
- Abrechnungszeitraum
- Gesamtkosten
- Vorauszahlungen
- Nachzahlung / Guthaben

### Abschnitt B - Verbrauchswerte der Partei

Nur parteirelevante Werte:
- Heizverbrauch / HKV
- Warmwasser
- Kaltwasser
- Strom

Darstellung:
- Geraet / Zaehler
- Einheit
- Alt / Neu / Differenz
- ggf. Umrechnungsfaktor
- ggf. normierter Verbrauch

### Abschnitt C - Kostenarten mit richtigem Scope

Jede Kostenart bekommt:
- Kostenartname
- **Scope-Label**
  - z. B. "Objekt Hauptstraße 2"
  - "Berechnungseinheit BE1"
  - "Direkte Zuordnung zu Ihrer Nutzeinheit"
- Gesamtkosten des relevanten Scopes
- Verteilerschluessel in lesbarer Form
- Ihre Einheiten / Ihre Quote
- Ihr Betrag

Pflichtregel:
- Es muss fuer jede Zeile fuer einen durchschnittlichen Mieter klar sein:
  - **welcher Topf verteilt wird,**
  - **nach welchem Schluessel verteilt wird,**
  - **warum genau dieser Anteil auf ihn entfaellt.**

### Abschnitt D - Teilsummen und Endsumme

Empfohlene Struktur:
- Heiz-/Warmwasserkosten gesamt
- Hausnebenkosten gesamt
- ggf. direkte Sonderkosten
- Gesamtkosten
- Vorauszahlungen
- Ergebnis

### Abschnitt E - Hinweise

Pflichtnah:
- Hinweis auf Belegeinsicht
- Hinweis, dass der detaillierte Rechenweg im Pruefbericht dokumentiert ist

Nicht in die Einzelabrechnung:
- Zahlungsziel
- Kontoverbindung
- langes Begleitschreiben

## Payload-/Template-Konsequenzen

Das Payload v2 aus Iteration 1 wird wie folgt geschaerft:

- `cost_type_sections[]` brauchen zusaetzlich:
  - `scope_type`
  - `scope_label`
  - `scope_reason`

- `items[]` brauchen zusaetzlich:
  - `allocation_scope_total_eur`
  - `allocation_scope_units_total`
  - `tenant_units`
  - `tenant_share_fraction`
  - `calculation_text`

- neues Feld:
  - `document_policy`
    - `include_co2_block`
    - `include_belegeinsicht_notice`
    - `separate_cover_letter`

- neues zusaetzliches Payload:
  - `cover_letter_payload`

## Verbindliche Test- und Change-Gates

Die Nutzer-Ergaenzung zur Testsicherheit wird verbindlich uebernommen.

### Regel 1 - Keine ungetestete Pipeline-Aenderung

Jede Aenderung an:
- Rechenkern,
- Output-Writer,
- Templates,
- Render-Payload,
- Scope-/Allocation-Logik

muss mindestens folgende Gates ausloesen:

1. bestehende Pipeline-Testsuite
2. Reader-Oracle-Checks gegen die bestehende Excel-/Abrechnungswelt
3. spezifische Einzelabrechnungs-Payload-/PDF-Regressionen

### Regel 2 - Bestehende Pipeline-Testfaelle sind Pflichtbestandteil dieses Plans

Die Tests fuer die Einzelabrechnung duerfen **nicht separat "frei schwebend"** entstehen, sondern muessen in die bestehende Pipeline-Testlandschaft integriert werden.

Konsequenz:
- diese Spec darf keine Umsetzung erlauben, die das Einzelabrechnungs-Layout aendert, ohne dass die Pipeline-Regression mitlaeuft.

### Regel 3 - Reader-Oracle aus vorhandenen Artefakten

Als Reader-/Format-Oracles werden kombiniert verwendet:

1. **Excel-/Bestandsorakel 2024**
   - `Nebenkostenabrechnung_2024.xlsx`
   - insbesondere die bisherigen Einzelabrechnungs-Sheets als Werte-Orakel

2. **ista-Beispiel 2023**
   - nicht als Layout-Kopiervorlage,
   - sondern als **Inhalts-/Pflichtfeld-Oracle**

3. **PDF-/Payload-Snapshots der neuen Einzelabrechnung**
   - fuer Regression auf Sichtbarkeit und Struktur

## Neue Arbeitspakete

### Arbeitspaket 6 - Scope-Richtige Kostenblöcke

Ziel:
- Kostenarten nicht mehr nur "nach Art", sondern "nach Art + Umlagescope" rendern.

Ergebnis:
- keine irrefuehrende Vermischung von BE1/BE2/anderen Nutzergruppen im Hauptdokument.

### Arbeitspaket 7 - Anschreiben als separates Artefakt

Ziel:
- kurzes Begleitdokument mit:
  - Anrede
  - Abrechnungsergebnis
  - Zahlungsziel / Kontoverbindung
  - Verweis auf Belegeinsicht

Ergebnisdatei:
- `{root}/Einzelabrechnungen/{party_slug}/anschreiben_{jahr}.pdf`

### Arbeitspaket 8 - Reader-/Regression-Gates

Ziel:
- jede Aenderung an der Einzelabrechnung muss gegen:
  - Werte-Orakel,
  - Inhalts-Orakel,
  - Lesbarkeits-Orakel
  abgesichert werden.

## Konkrete Verifikationstestfaelle

Da der Plan jetzt implementation-ready ist, sind folgende Testfaelle verbindlich:

1. **Seite-1-Reader-Test**
   - Given eine erzeugte Einzelabrechnung,
   - when ein Leser nur Seite 1 sieht,
   - then findet er:
     - Partei
     - Zeitraum
     - Gesamtkosten
     - Vorauszahlungen
     - Nachzahlung/Guthaben

2. **Scope-Test Heizkosten**
   - Given eine Abrechnung fuer NE1 in BE1,
   - when Heizkosten dargestellt werden,
   - then wird nur der fachlich relevante Scope gezeigt,
   - und keine verwirrende Vermischung irrelevanter Verbrauchseinheiten.

3. **Kostenart-Test**
   - Given jede relevante Kostenart,
   - when sie im Hauptdokument erscheint,
   - then sind sichtbar:
     - Scope,
     - Gesamtkosten des Scopes,
     - Schluessel,
     - Ihre Einheiten/Quote,
     - Ihr Betrag.

4. **Vorauszahlungs-Test**
   - Given vorhandene Zahlungen,
   - when die Einzelabrechnung erzeugt wird,
   - then wird `bereits gezahlt` klar ausgewiesen und von den Gesamtkosten abgezogen.

5. **Belegeinsicht-Test**
   - Given eine finale Einzelabrechnung,
   - when der Hinweisblock gerendert wird,
   - then enthaelt die Abrechnung einen klaren Belegeinsicht-Hinweis.

6. **Anschreiben-Test**
   - Given eine finale Mieterabrechnung,
   - when Artefakte geschrieben werden,
   - then existiert zusaetzlich ein separates Anschreiben mit Zahlungsinformationen.

7. **Regression-Gate-Test**
   - Given eine Aenderung an Output-Writer/Template/Rechenkern,
   - when CI/Testlauf ausgefuehrt wird,
   - then werden bestehende Pipeline-Tests plus Einzelabrechnungs-Reader-Oracles gemeinsam ausgefuehrt.

## Status der offenen Marker nach Nutzer-Edit

- [MISSING NON-BLOCKING] Juristische Endformulierung des Belegeinsicht-Hinweises final abstimmen; ista-Beispiel ist dafuer nur Hilfsreferenz, nicht autoritativer Rechtstext.
- [DECISION RESOLVED] CO2-Kostenblock im Hauptdokument.
- [DECISION RESOLVED] Zahlungsziel/Kontoverbindung im separaten Anschreiben.
- [DECISION RESOLVED] Reader-Test gegen frische Modellinstanz ist Pflicht.
- [DECISION RESOLVED] Pipeline-Code-Aenderungen nur mit Pipeline-Test-/Oracle-Gates.

## Implementation-Ready-Schluss

Der Plan ist jetzt fuer den naechsten Umsetzungszyklus ausreichend geschaerft.

Empfohlene Reihenfolge:

1. `statement_payload_v2` um Scope-/Berechnungsfelder erweitern
2. `statement_template_v2` bauen
3. `cover_letter_payload` + Anschreiben-Template ergaenzen
4. Pipeline-Tests um Reader-/Scope-/Anschreiben-Faelle erweitern
5. danach erst Layout-Feinschliff


# Iteration 3

Delta zu Iteration 2:
- Tatsächlichen v2-Output gegen Nutzerziel gespiegelt und explizit als unzureichend bewertet.
- Klargestellt, dass der bisherige Schritt vor allem Datenmodell und Renderpfad validiert hat, aber **nicht** die eigentliche Dokumentqualität.
- Strategiewechsel auf **design-first Redesign** der Einzelabrechnung festgelegt.

## Review des implementierten v2-Zwischenstands

Der implementierte Stand mit `statement_payload_v2`, `statement_template_v2` und separatem Anschreiben ist **kein akzeptables Mieter-Dokument**.

Diese Bewertung ist nicht kosmetisch, sondern fachlich:
- Die Ausgabe ist schwer lesbar.
- Sie wirkt technisch statt abrechnungsartig.
- Sie ist zu stark als Listen-/Debug-Dokument organisiert.
- Zentrale Werte sind nicht in einer für Mieter schnellen und plausiblen Struktur zusammengefasst.

Die Nutzerbewertung war eindeutig:
- zu viele Stichpunkte
- fehlende Formatierung
- fehlende Tabellen mit relevanten Detaildaten
- technische Begriffe wie `scope`
- insgesamt nicht nachvollziehbar und nicht nah genug am gewünschten Ergebnis

## Wichtigste Erkenntnis

Der bisherige Weg hat einen **brauchbaren Daten- und Testpfad** geliefert, aber **noch kein brauchbares Dokumentenprodukt**.

Damit wird die Arbeit in zwei Ebenen getrennt:

1. **Was bereits wertvoll ist**
   - `statement_payload_v2`
   - scope-richtige Datenaggregation
   - Meter-/Kosten-/Subtotal-Struktur im Payload
   - Regressionstests und Renderpfad

2. **Was als Dokumentenprodukt gescheitert ist**
   - visuelle Struktur
   - Leserführung
   - Klartextsprache
   - mietergeeignete Tabellenform
   - überzeugende Seite 1

Die Konsequenz ist:
- Der bisherige v2-Code ist **kein Endergebnis**, sondern ein technischer Zwischenstand.
- Ab hier darf die Einzelabrechnung **nicht mehr datengetrieben „aus den vorhandenen Feldern zusammengeklebt“** werden.
- Stattdessen muss zuerst das **Zielbild des Dokuments** präzise definiert werden.

## Neue Arbeitsregel: design-first statt template-first

Für die nächste Spezifikations-/Planungsiteration gilt:

1. **Zuerst Zielbild/Mockup**
   - Seite 1
   - Folgeseiten
   - Tabellenstruktur
   - visuelle Gewichtung
   - sprachliche Konventionen

2. **Dann Dokumentmodell gegen Zielbild prüfen**
   - Welche Payload-Felder braucht dieses Zielbild wirklich?
   - Welche Felder gehören in Tabellen?
   - Welche Felder gehören nur in Prüfbericht oder Anschreiben?

3. **Erst danach Rendering neu umsetzen**

## Abgeleitete Produktanforderungen nach dem Fehlversuch

### A. Verbotene Muster im Hauptdokument

Die neue Einzelabrechnung darf **nicht**:
- als Stichpunktwüste aufgebaut sein
- technische Begriffe wie `scope`, `formula_code`, `source_label`, `normalized_value` verwenden
- wie ein Debug-/Audit-Output wirken
- pro Kostenart nur aus Fließ- oder Listen-Text bestehen
- Tabellen nur simulieren, ohne echte tabellarische Leserführung zu bieten

### B. Zwingende Eigenschaften des neuen Zielbilds

Die neue Einzelabrechnung soll:
- auf Seite 1 eine **klare Ergebnisübersicht** zeigen
- die wichtigsten Werte visuell priorisieren:
  - Zeitraum
  - Partei
  - Gesamtkosten
  - Vorauszahlungen
  - Nachzahlung/Guthaben
- Kostenarten in **echten Tabellen** oder klar tabellarischen Blöcken darstellen
- pro Kostenblock nur mieterverständliche Begriffe nutzen
- nur die für diese Partei relevanten Informationen zeigen
- ohne Vorwissen lesbar sein

### C. Sprachregel für das Hauptdokument

Im Hauptdokument sind technische Entwicklerbegriffe verboten.

Beispiele:
- nicht `scope`
- nicht `source_label`
- nicht `normalized_value`
- nicht `formula_code`

Stattdessen:
- `Abrechnungskreis` / `verteilte Gesamtkosten`
- `Verteilerschlüssel`
- `Ihr Anteil`
- `Ihre Verbrauchswerte`
- `Bereits gezahlt`
- `Nachzahlung` / `Guthaben`

### D. Tabellenpflicht

Die Einzelabrechnung braucht mindestens:

1. **Ergebnistabelle / Ergebnisbox auf Seite 1**
   - Gesamtkosten
   - Vorauszahlungen
   - Ergebnis

2. **Verbrauchstabelle**
   - nur soweit fachlich belastbar und mieterrelevant
   - keine erfundenen Alt-/Neu-Werte

3. **Kostenartentabelle(n)**
   - Kostenart
   - verteilte Gesamtkosten
   - Verteilerschlüssel
   - Ihr Anteil / Ihre Einheiten
   - Ihr Betrag

4. **Abschlusstabelle / Ergebnisblock**
   - Zwischensummen
   - Vorauszahlungen
   - Endergebnis

## Neue Zieldefinition für Iteration 4

Die nächste Iteration dieser Spec soll **nicht sofort neue Codearbeit** beschreiben, sondern zuerst das Zielbild der Einzelabrechnung präzisieren:

- Seitenaufbau
- Abschnittsreihenfolge
- konkrete Tabellenstruktur
- Textstil
- Pflicht-/Optionalinformationen pro Abschnitt

Erst wenn dieses Zielbild klar ist, wird der Implementierungsplan angepasst.

## Status nach Iteration 3

- [DONE] Datenpfad und Renderpfad für `statement_payload_v2`
- [DONE] scope-richtige Aggregation im Datenmodell
- [DONE] separates Anschreiben als Artefakt
- [DONE] erste Reader-/Regressionstests
- [NOT ACCEPTED] Hauptdokument als tatsächliche Einzelabrechnung für Mieter

## Offene Leitentscheidung für die nächste Spec-Iteration

- [DECISION SPEC] Welches Zielbild soll Seite 1 haben?
  - eher kompakte Ergebnisbox + 1 Kernkostentabelle => so
  - oder stärker im Stil klassischer Abrechnungsformulare mit mehreren klaren Tabellenblöcken

=> es fehlt noch die erläuterung der Verteilschlüssel siehe Worksheet Allgmein in Excel '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/Nebenkostenabrechnung_2024.xlsx' es muss ja klar ersichtlich sein wie sich der Schlüssel überhaupt zusammensetzt.
=> auch möchte ich dass du (zusätzlich) in zukunft ein review aus sicht des mieters durchführst, dabei sollen die zuvor definierten anforderungen in (iteration 0) diese dokuments geprüft werden 


# Iteration 4

Delta zu Iteration 3:
- Nutzer-Entscheidung fuer Seite 1 übernommen: **kompakte Ergebnisbox + eine Kernkostentabelle**.
- Fehlende Anforderung zur **Erlaeuterung der Verteilerschluessel** aus dem Excel-Kontext ergaenzt.
- Verbindliches **Mieter-Review** als zusaetzlicher Qualitaetsgate aufgenommen.

## Uebernommene Nutzer-Edits

### 1. Seite 1 wird bewusst kompakt

Die offene Leitentscheidung aus Iteration 3 ist hiermit aufgeloest:

- [DECISION RESOLVED] Seite 1 der Einzelabrechnung folgt dem Muster:
  - **kompakte Ergebnisbox**
  - darunter **eine Kernkostentabelle**

Das bedeutet:
- Seite 1 soll **nicht** mit vielen Teilbloecken oder Parallelstrukturen ueberladen werden.
- Seite 1 muss in wenigen Sekunden lesbar sein.
- Die erste Seite dient primaer der Orientierung und Ergebniserklaerung, nicht der Vollausbreitung aller Detailinformationen.

### 2. Verteilerschluessel muessen nicht nur benannt, sondern erklaert werden

Der bisherige Stand war hier zu schwach.

Es reicht **nicht**, nur Formulierungen wie:
- `nach Wohnflaeche`
- `nach Personen`
- `nach Warmwasserverbrauch`

zu zeigen.

Zusaetzlich muss fuer den Mieter erkennbar sein:
- **woraus sich der Schluessel zusammensetzt**
- **welche Einheit/Basis dahintersteht**
- **welcher Wert fuer ihn selbst gilt**
- **welcher Gesamtwert fuer den verteilten Topf gilt**

Die Referenz fuer diese Erklaerung kommt aus der bisherigen Logik im Worksheet `Allgemein` der Excel-Welt:
- dort sind die verteilschluesselrelevanten Grundlagen hinterlegt
- also z. B. Wohnflaeche, Personenzahl, Zuordnung zu Berechnungseinheiten/Nutzeinheiten

Folgerung fuer die neue Einzelabrechnung:
- Pro Kostenart reicht nicht `Verteilerschluessel: Wohnflaeche`.
- Stattdessen braucht es eine **lesbare Schluessel-Erlaeuterung**.

Beispielhaft:
- `Verteilerschluessel: Wohnflaeche`
- `Ihre Wohnflaeche: 180 m²`
- `Gesamtwohnflaeche des Abrechnungskreises: 785 m²` => Abrechnungskreis gibt es nicht, das ist entweder die Berechnungseinheit oder die Liegenschaft je nach scope. nutze präsized Wording keinen kauderwälsch
- `Ihr Anteil: 180 / 785`

oder:
- `Verteilerschluessel: Personen`
- `Ihre beruecksichtigten Personen: 2`
- `Beruecksichtigte Personen gesamt: 10,8`
- `Ihr Anteil: 2 / 10,8`

oder:
- `Verteilerschluessel: Warmwasserverbrauch`
- `Ihr Warmwasserverbrauch: 32,56 m³`
- `Warmwasserverbrauch gesamt im relevanten Abrechnungskreis: 57,95 m³`
- `Ihr Anteil: 32,56 / 57,95`

### 3. Der Begriff des verteilten Kreises muss lesbar, aber nicht technisch sein

Die bisherige Entwickler-/Datenmodell-Sprache (`scope`) bleibt ungeeignet.

Gleichzeitig muss fuer den Mieter klar sein, **auf welchen Kreis sich die Gesamtsumme bezieht**.

Neue Sprachregel:
- Im Hauptdokument kein `scope`
- stattdessen ein lesbarer Begriff wie:
  - `Abrechnungskreis` => siehe oben
  - `verteilte Gesamtkosten`
  - `Gesamtkosten dieses Kostenkreises`

Wichtig ist:
- nicht der technische Begriff,
- sondern dass der Mieter versteht,
  - ob sich eine Zahl auf das ganze Objekt,
  - eine Berechnungseinheit,
  - eine Verbrauchseinheit,
  - oder eine direkte Zuordnung bezieht.

## Neue Pflichtanforderung: Schluessel-Erlaeuterungsblock in der Kernkostentabelle

Die Kernkostentabelle auf Seite 1 braucht je Zeile bzw. Kostenart mindestens:

1. **Kostenart**
2. **verteilte Gesamtkosten**
3. **Verteilerschluessel (Name)**
4. **Schluesselbasis erklaert**
   - z. B. `Ihre Wohnflaeche / Gesamtwohnflaeche`
   - z. B. `Ihre Personen / Personen gesamt`
   - z. B. `Ihr WW-Verbrauch / WW-Verbrauch gesamt`
5. **Ihr Anteil**
6. **Ihr Betrag**

Damit wird aus der Tabelle keine reine Ergebnisliste, sondern eine **kompakte Rechentabelle**.

## Neue Zielstruktur fuer Seite 1

Seite 1 soll jetzt mindestens diese Reihenfolge haben:

### Abschnitt A - Kopf
- Objekt
- Partei
- Zeitraum
- Abrechnungsdatum

### Abschnitt B - Ergebnisbox
- Gesamtkosten
- Vorauszahlungen
- Nachzahlung / Guthaben

Die Ergebnisbox ist das visuelle Hauptelement der ersten Seite.

### Abschnitt C - Kernkostentabelle

Ziel:
- wichtigste Kostenarten direkt auf Seite 1 nachvollziehbar machen
- aber ohne die Seite zu ueberladen

Pflichtspalten:
- Kostenart
- Gesamtkosten des relevanten Kostenkreises
- Verteilerschluessel
- Ihre Basis / Gesamtbasis
- Ihr Anteil
- Ihr Betrag

Wenn die Detailtiefe fuer alle Kostenarten nicht auf Seite 1 tragbar ist, gilt:
- Seite 1 zeigt die wichtigsten/relevantesten Kostenarten und/oder eine verdichtete Form
- Folgeseiten duerfen die vollstaendige Tabelle enthalten
- aber das Grundprinzip der **tabellarischen Nachvollziehbarkeit** bleibt Pflicht

## Neues Qualitaetsgate: Mieter-Review

Zusätzlich zu Reader-/Oracle-/Regressionstests wird ein eigenes **Mieter-Review** verpflichtend.

Dieses Review hat einen anderen Fokus als technische Tests:
- keine Payload-Vollstaendigkeit
- keine Modellkonsistenz
- keine Entwicklerlogik

Sondern:
- versteht ein durchschnittlicher Mieter das Dokument?
- findet er die zentralen Werte schnell?
- ist die Kostenverteilung im Kopf nachvollziehbar?
- wirken Begriffe und Tabellen natuerlich statt technisch?

### Verbindliche Prueffrage fuer das Mieter-Review

Das Mieter-Review prueft die Anforderungen aus Iteration 0 dieses Dokuments erneut gegen das **tatsaechliche Dokument**.

Mindestens folgende Fragen muessen positiv beantwortet werden koennen:
- Wo steht der Abrechnungszeitraum?
- Welche Gesamtkosten werden verteilt?
- Nach welchem Schluessel wird verteilt?
- Wie setzt sich dieser Schluessel zusammen?
- Was ist mein Anteil?
- Welche Vorauszahlungen wurden abgezogen?
- Ergibt sich Nachzahlung oder Guthaben klar und schnell?

### Rolle des Mieter-Reviews im Prozess

Neue Regel:
- Eine Einzelabrechnung gilt nicht als akzeptiert, nur weil Tests gruen sind.
- Sie gilt erst dann als akzeptiert, wenn:
  - technische Tests gruen sind
  - Reader-/Oracle-Checks bestehen
  - **und** das Mieter-Review das Dokument als nachvollziehbar bestaetigt

## Konkrete Auswirkungen auf die naechste Planiteration

Die naechste Planiteration muss deshalb zusaetzlich enthalten:

1. ein Arbeitspaket fuer die **Schluessel-Erlaeuterungslogik**
2. ein Arbeitspaket fuer die **Seite-1-Kernkostentabelle**
3. ein explizites **Mieter-Review-Gate**
4. Testfaelle, die nicht nur Felder pruefen, sondern die **Erklaerbarkeit der Verteilung**

## Status nach Iteration 4

- [DONE] Design-first als neue Arbeitsregel
- [DONE] Leitentscheidung fuer kompakte Seite 1
- [DONE] Verteilerschluessel-Erlaeuterung als neue Pflichtanforderung
- [DONE] Mieter-Review als zusaetzlicher Akzeptanzgate
- [NEXT] Zielbild/Mockup von Seite 1 und der Kernkostentabelle konkret ausarbeiten


# Iteration 5

Delta zu Iteration 4:
- Nutzer-Edit zu unpräzisem Wording übernommen.
- Der Hilfsbegriff `Abrechnungskreis` wird im Hauptdokument verworfen.
- Sprachregel für präzise Benennung von `Liegenschaft`, `Berechnungseinheit`, `Verbrauchseinheit` und `direkter Zuordnung` geschärft.

## Uebernommene Korrektur

Die Formulierung `Abrechnungskreis` war zu unpräzise und erzeugt neuen Kauderwelsch statt Klarheit.

Nutzerkorrektur:
- Wenn sich Gesamtkosten auf das ganze Objekt beziehen, muss dies als **Liegenschaft / gesamtes Objekt** benannt werden.
- Wenn sich Gesamtkosten auf eine Heiz-/Berechnungseinheit beziehen, muss dies als **Berechnungseinheit** benannt werden.
- Wenn sich Gesamtkosten auf eine Verbrauchseinheit beziehen, muss dies als **Verbrauchseinheit** benannt werden.
- Wenn es sich um direkte Einzelzuordnung handelt, muss das auch so benannt werden.

Folgerung:
- `Abrechnungskreis` wird in der Einzelabrechnung **nicht** verwendet.

## Neue Sprachregel fuer den Hauptbeleg

Im Hauptdokument ist nur noch präzises fachliches Wording erlaubt.

Erlaubte Begriffe je Fall:

1. **Liegenschaft / gesamtes Objekt**
   - fuer echte Haus-/Objektkosten
   - Beispiel:
     - `Gesamtwohnflaeche der Liegenschaft`
     - `Gesamtkosten der Liegenschaft fuer diese Kostenart`

2. **Berechnungseinheit**
   - fuer Kosten, die sich fachlich auf eine Heiz-/Berechnungseinheit beziehen
   - Beispiel:
     - `Gesamtwohnflaeche der Berechnungseinheit BE1`
     - `Gesamtkosten der Berechnungseinheit BE1`

3. **Verbrauchseinheit**
   - fuer verbrauchsbezogene Topfe, wenn die Fachlogik auf Verbrauchseinheiten abstellt
   - Beispiel:
     - `Warmwasserverbrauch gesamt der Verbrauchseinheit BE1`

4. **Direkte Zuordnung**
   - fuer eindeutig zugeordnete Einzelpositionen
   - Beispiel:
     - `Direkt Ihrer Nutzeinheit zugeordnete Stromkosten`

Nicht mehr erlaubt:
- `Abrechnungskreis`
- andere Sammelbegriffe, die den fachlichen Bezug vernebeln

## Praezisierung der Schluessel-Erlaeuterung

Die Schluessel-Erlaeuterung muss daher nicht nur den Schluessel selbst nennen, sondern auch den **fachlich exakten Bezugsraum**.

Beispiel Wohnflaeche:
- `Verteilerschluessel: Wohnflaeche`
- `Ihre Wohnflaeche: 180 m²`
- `Gesamtwohnflaeche der Liegenschaft: 785 m²`
- `Ihr Anteil: 180 / 785`

Beispiel Berechnungseinheit:
- `Verteilerschluessel: Wohnflaeche`
- `Ihre Wohnflaeche in der Berechnungseinheit BE1: 180 m²`
- `Gesamtwohnflaeche der Berechnungseinheit BE1: 260 m²`
- `Ihr Anteil: 180 / 260`

Beispiel Warmwasser:
- `Verteilerschluessel: Warmwasserverbrauch`
- `Ihr Warmwasserverbrauch: 32,56 m³`
- `Warmwasserverbrauch gesamt der Verbrauchseinheit BE1: 57,95 m³`
- `Ihr Anteil: 32,56 / 57,95`

Wichtig:
- Die Einzelabrechnung muss jeweils den **korrekten fachlichen Bezug** nennen.
- Nicht die sprachlich bequemste Sammelbezeichnung.

## Wirkung auf das Zielbild von Seite 1

Die kompakte Seite 1 bleibt bestehen.

Aber:
- In der Kernkostentabelle darf die Spalte fuer den Bezugsraum nicht diffus formuliert sein.
- Wenn eine Zusatzzeile oder Unterzeile den Bezugsraum erklaert, dann mit präzisem Wort:
  - `Liegenschaft`
  - `Berechnungseinheit BE1`
  - `Verbrauchseinheit BE1`
  - `direkte Zuordnung zu Ihrer Nutzeinheit`

## Zusätzliche Prueffrage fuer das Mieter-Review

Das Mieter-Review muss kuenftig auch diese Frage beantworten koennen:

- Ist für jede relevante Kostenart klar, ob sich die Gesamtkosten auf die **Liegenschaft**, eine **Berechnungseinheit**, eine **Verbrauchseinheit** oder auf eine **direkte Zuordnung** beziehen?

Wenn diese Frage nicht schnell beantwortbar ist, gilt das Dokument als nicht akzeptiert.

## Status nach Iteration 5

- [DONE] Unpräziser Begriff `Abrechnungskreis` verworfen
- [DONE] Präzise Sprachregel fuer fachliche Bezugsräume ergänzt
- [DONE] Schlüssel-Erklärung um exakten Bezugsraum geschärft
- [NEXT] Zielbild/Mockup mit diesen präzisen Begriffen konkret ausformulieren


# Iteration 6

Delta zu Iteration 5:
- Verbliebene Unschärfen aus Iteration 4/5 bereinigt.
- Nicht nur `Abrechnungskreis`, sondern auch diffuse Sammelbegriffe wie `Kostenkreis` fuer das sichtbare Dokument ausgeschlossen.
- Tabellen- und Beispielsprache weiter auf **präzise, mieterlesbare Bezüge** geschärft.

## Bereinigung der Restunschärfen

Die bisherige Richtung war richtig, aber noch nicht konsequent genug.

Problem:
- Auch wenn `Abrechnungskreis` verworfen wurde, blieben noch Formulierungen wie:
  - `Gesamtkosten des relevanten Kostenkreises`
  - `Gesamtkosten dieses Kostenkreises`
- Auch das ist fuer das eigentliche Dokument noch zu diffus.

Neue Regel:
- Im sichtbaren Hauptdokument werden **keine abstrakten Sammelbegriffe** wie
  - `Abrechnungskreis`
  - `Kostenkreis`
  - andere unklare Hilfsworte
  verwendet.

Stattdessen muss die Zuordnung **direkt benannt** werden.

## Endgueltige Sprachregel fuer sichtbare Bezüge

Im Dokument soll fuer jede Kostenart klar lesbar sein, worauf sich die Gesamtkosten beziehen.

Erlaubte sichtbare Bezüge:
- `gesamte Liegenschaft`
- `Berechnungseinheit BE1`
- `Berechnungseinheit BE2`
- `Verbrauchseinheit BE1`
- `Verbrauchseinheit BE2`
- `direkte Zuordnung zu Ihrer Nutzeinheit`

Wenn noetig, kann dies auch sprachlich leicht ausgeschrieben werden:
- `Die Gesamtkosten beziehen sich auf die gesamte Liegenschaft`
- `Die Gesamtkosten beziehen sich auf die Berechnungseinheit BE1`

Aber:
- nicht allgemein `Kostenkreis`
- nicht allgemein `relevanter Bereich`
- nicht allgemein `Abrechnungskreis`

## Korrektur der Beispielsprache

Die Beispiele aus Iteration 4/5 werden dadurch wie folgt praezisiert:

### Beispiel Wohnflaeche auf Liegenschaftsebene

- `Verteilerschluessel: Wohnflaeche`
- `Bezieht sich auf: gesamte Liegenschaft`
- `Ihre Wohnflaeche: 180 m²`
- `Gesamtwohnflaeche der Liegenschaft: 785 m²`
- `Ihr Anteil: 180 / 785`

### Beispiel Wohnflaeche auf Ebene einer Berechnungseinheit

- `Verteilerschluessel: Wohnflaeche`
- `Bezieht sich auf: Berechnungseinheit BE1`
- `Ihre Wohnflaeche in BE1: 180 m²`
- `Gesamtwohnflaeche der Berechnungseinheit BE1: 260 m²`
- `Ihr Anteil: 180 / 260`

### Beispiel Warmwasser

- `Verteilerschluessel: Warmwasserverbrauch`
- `Bezieht sich auf: Verbrauchseinheit BE1`
- `Ihr Warmwasserverbrauch: 32,56 m³`
- `Warmwasserverbrauch gesamt der Verbrauchseinheit BE1: 57,95 m³`
- `Ihr Anteil: 32,56 / 57,95`

### Beispiel direkte Zuordnung

- `Verteilerschluessel: direkte Zuordnung`
- `Bezieht sich auf: direkte Zuordnung zu Ihrer Nutzeinheit`
- `Ihr Betrag: 162,86 EUR`

## Korrektur der Tabellenlogik fuer Seite 1

Die Kernkostentabelle auf Seite 1 soll daher nicht mit einer diffusen Spalte wie
- `Kostenkreis`
- `Abrechnungskreis`

arbeiten.

Stattdessen wird die Logik wie folgt praezisiert:

Pflichtspalten fuer die Kernkostentabelle:
1. **Kostenart**
2. **Bezieht sich auf**
3. **Gesamtkosten**
4. **Verteilerschluessel**
5. **Ihre Basis / Gesamtbasis**
6. **Ihr Anteil**
7. **Ihr Betrag**

Die Spalte `Bezieht sich auf` enthaelt dann direkt einen der erlaubten sichtbaren Bezüge:
- `gesamte Liegenschaft`
- `Berechnungseinheit BE1`
- `Verbrauchseinheit BE1`
- `direkte Zuordnung zu Ihrer Nutzeinheit`

Damit wird der fachliche Bezug klar, ohne mit einem neuen Kunstwort zu arbeiten.

## Zusatzregel fuer Formulierungen im Hauptdokument

Das Hauptdokument soll so formuliert sein, dass ein Mieter saetze gedanklich direkt lesen kann.

Bevorzugt:
- `Bezieht sich auf: gesamte Liegenschaft`
- `Bezieht sich auf: Berechnungseinheit BE1`

Nicht bevorzugt:
- verschachtelte Fachformeln
- Entwickleretiketten
- Sammelbegriffe, die erst erklaert werden muessen

## Erweiterung des Mieter-Reviews

Das Mieter-Review prueft kuenftig nicht nur, **ob** ein Bezug genannt ist, sondern auch:

- ist der genannte Bezug sprachlich unmittelbar verständlich?
- steht dort ein präziser Begriff wie `Liegenschaft`, `Berechnungseinheit BE1`, `Verbrauchseinheit BE1`?
- oder wurde erneut ein künstlicher Sammelbegriff eingeführt?

Ein Dokument faellt das Mieter-Review durch, wenn:
- die Zuordnung nur mit Hilfsbegriffen statt mit präzisen Bezügen beschrieben wird
- ein Leser erst interpretieren muss, worauf sich die Gesamtkosten beziehen

## Status nach Iteration 6

- [DONE] `Abrechnungskreis` verworfen
- [DONE] `Kostenkreis` ebenfalls als sichtbarer Dokumentbegriff verworfen
- [DONE] sichtbare Bezüge fuer Tabellen und Beispiele final präzisiert
- [NEXT] Mockup der ersten Seite mit genau diesen Spalten und Formulierungen ausarbeiten


# Iteration 7

Delta zu Iteration 6:
- Workbook `Nebenkostenabrechnung_2024.xlsx` gesichtet, damit das Mock nicht generisch bleibt.
- Reale Kostenarten, reale Schluesselarten und reale Dokumentlogik aus der Excel-Welt in das Zielbild uebernommen.
- Erstes konkretes Mock fuer die Einzelabrechnung als Zielbild definiert.

## Erkenntnisse aus der Excel als Grundlage fuer das Mock

Das Mock soll sich an der vorhandenen fachlichen Welt orientieren, nicht an einem frei erfundenen Demo-Fall.

Aus dem Workbook ergeben sich fuer die Einzelabrechnung insbesondere:

### Reale Kostenarten

- `Brennstoffkosten`
- `Gebaeudeversicherung`
- `Heiznebenkosten`
- `Grundsteuer`
- `Muellabfuhr`
- `Kalt- und Abwasser`
- `Oberflaechenwasser`
- `Strom`
- `Verbrauchskosten Warmwasser`
- `Grundkosten Heizung`
- `Verbrauchskosten Heizung`

### Reale Schluesselarten

Aus `Stammdaten` und `Allgemein` sind aktuell relevant:
- `Wohnflaeche`
- `Personen`
- `Nutzflaeche`
- `Verbrauch`
- `Pauschal`
- `direkte Zuordnung` (fachlich fuer Strom bzw. direkt zurechenbare Positionen)

### Reale Bezugsraeume

Die Excel-Welt bildet bereits genau die Bezuege ab, die im neuen Dokument lesbar gemacht werden muessen:
- `gesamte Liegenschaft`
- `Berechnungseinheit BE1 / BE2`
- `Verbrauchseinheit BE1` fuer Warmwasser-/verbrauchsnahe Toepfe
- `direkte Zuordnung zu Ihrer Nutzeinheit`

### Reale Nachvollziehbarkeits-Bausteine

Die Excel enthaelt bereits die Rohlogik, aus der die spaetere lesbare Abrechnung gebaut werden muss:
- Wohnflaechen je Nutzeinheit
- Wohnflaechen innerhalb der Berechnungseinheit
- Personenzahlen
- Zaehlernummern
- Messwerte/Verbraeuche
- Betriebskostenbelege
- Stromtarife mit Zeitraeumen

Folgerung:
- Das Mock darf **konkret** mit diesen Kostenarten und Schluesseln arbeiten.
- Es soll nicht bei abstrakten Platzhaltern wie `Kostenart A` oder `Schluessel B` bleiben.

## Ziel des Mocks

Das Mock beschreibt das **gewuenschte spaetere Mieter-Dokument**.

Es ist:
- noch **kein Payload-Vertrag**
- noch **kein Render-Template**
- noch **keine finale juristische Formulierung**

Sondern:
- ein fachlich und visuell klares Zielbild,
- gegen das spaeter Plan, Tests und Implementierung ausgerichtet werden.

## Mock: Seite 1

Seite 1 bleibt kompakt, aber nicht mehr stichpunktartig.

Sie besteht aus vier klaren Zonen:
1. Dokumentkopf
2. Ergebnisbox
3. kleine Orientierungstabelle zur Verteilungsbasis
4. Kernkostentabelle

### Mock fuer den Dokumentkopf

Der obere Bereich soll in normaler Brief-/Abrechnungslogik lesbar sein:

| Feld | Inhalt |
|------|--------|
| Objekt | `Hauptstraße 2, 36381 Schlüchtern` |
| Art des Dokuments | `Nebenkostenabrechnung 2024` |
| Mietpartei | `Kraft / Hühne` |
| Nutzeinheit | `Geb. Ost - Loftwohnung (Nutzeinheit 1)` |
| Zeitraum | `01.01.2024 bis 31.10.2024` |
| Abrechnungsdatum | `[Datum der Erstellung]` |

Wichtig:
- kein technischer Payload-Kopf
- keine Entwicklerbegriffe
- normale Briefsprache

### Mock fuer die Ergebnisbox

Direkt darunter steht eine gut sichtbare Ergebnisbox als wichtigstes Element der ersten Seite.

| Zusammenfassung | Betrag |
|-----------------|--------|
| Umlagefaehige Kosten | `x.xxx,xx EUR` |
| Abzueglich Vorauszahlungen | `x.xxx,xx EUR` |
| Ergebnis | `Nachzahlung x.xxx,xx EUR` oder `Guthaben x.xxx,xx EUR` |

Gestaltungsregel:
- grosse, ruhige Box
- kein Fliesstextblock
- `Nachzahlung` bzw. `Guthaben` optisch hervorgehoben

### Mock fuer die kleine Orientierungstabelle

Zwischen Ergebnisbox und Kernkostentabelle kommt eine kleine Lesehilfe.

Sie dient nicht der Vollstaendigkeit, sondern der schnellen Einordnung:

| Verteilung nach | Ihr Wert | Gesamtwert | Gilt fuer |
|-----------------|----------|------------|-----------|
| Wohnflaeche | `180 m²` | `654 m²` | `gesamte Liegenschaft` |
| Wohnflaeche | `180 m²` | `260 m²` | `Berechnungseinheit BE1` |
| Personen | `2` | `10` | `gesamte Liegenschaft` |
| Warmwasserverbrauch | `[Ihr Wert]` | `[Gesamtwert]` | `Verbrauchseinheit BE1` |

Zweck:
- der Mieter erkennt vorab, welche Grundlagen in der Tabelle immer wieder auftauchen
- die Haupttabelle selbst kann dadurch kompakt bleiben

## Mock fuer die Kernkostentabelle auf Seite 1

Die Tabelle auf Seite 1 nutzt die **realen Sparten** aus der Excel-Welt.

Pflichtspalten:

| Kostenart | Bezieht sich auf | Gesamtkosten | Verteilung | Ihre Basis / Gesamtbasis | Ihr Betrag |
|-----------|------------------|--------------|------------|--------------------------|------------|
| Grundsteuer | gesamte Liegenschaft | `x.xxx,xx EUR` | Wohnflaeche | `180 m² / 654 m²` | `xxx,xx EUR` |
| Muellabfuhr | gesamte Liegenschaft | `xxx,xx EUR` | Personen | `2 / 10` | `xx,xx EUR` |
| Kalt- und Abwasser | gesamte Liegenschaft | `x.xxx,xx EUR` | Verbrauch | `[Ihr Verbrauch] / [Gesamtverbrauch]` | `xxx,xx EUR` |
| Oberflaechenwasser | gesamte Liegenschaft | `xxx,xx EUR` | Wohnflaeche | `180 m² / 654 m²` | `xx,xx EUR` |
| Gebaeudeversicherung | Berechnungseinheit BE1 | `x.xxx,xx EUR` | Wohnflaeche | `180 m² / 260 m²` | `xxx,xx EUR` |
| Brennstoffkosten - Grundkosten 30 % | Berechnungseinheit BE1 | `x.xxx,xx EUR` | Wohnflaeche | `180 m² / 260 m²` | `xxx,xx EUR` |
| Brennstoffkosten - Verbrauch 70 % | Berechnungseinheit BE1 | `x.xxx,xx EUR` | Verbrauch | `[Ihr Heizverbrauch] / [Gesamtverbrauch BE1]` | `xxx,xx EUR` |
| Heiznebenkosten | Berechnungseinheit BE1 | `xxx,xx EUR` | Verbrauch | `[Ihr Heizverbrauch] / [Gesamtverbrauch BE1]` | `xx,xx EUR` |
| Verbrauchskosten Warmwasser | Verbrauchseinheit BE1 | `xxx,xx EUR` | Warmwasserverbrauch | `[Ihr WW-Verbrauch] / [WW gesamt BE1]` | `xx,xx EUR` |
| Strom | direkte Zuordnung zu Ihrer Nutzeinheit | `xxx,xx EUR` | direkte Zuordnung | `direkt ermittelt` | `xxx,xx EUR` |

### Regeln fuer diese Kernkostentabelle

1. Die Tabelle ist die **zentrale Erklaerung** auf Seite 1.
2. Jede Zeile muss allein lesbar sein.
3. `Bezieht sich auf` muss immer explizit den Bezugsraum nennen.
4. `Ihre Basis / Gesamtbasis` muss die Verteilung rechnerisch nachvollziehbar machen.
5. Bei `direkter Zuordnung` darf statt einer Quote klarer Text stehen.

## Mock fuer Seite 2: Detailseite Heizung und Warmwasser

Die komplexen Heiz- und Warmwasserkosten duerfen nicht nur als Einzelzeilen auf Seite 1 stehen.

Sie bekommen eine eigene Detailseite.

### Tabelle A - Bildung des Heizkostentopfes

| Position | Betrag |
|----------|--------|
| Brennstoffkosten gesamt Berechnungseinheit BE1 | `x.xxx,xx EUR` |
| Heiznebenkosten Berechnungseinheit BE1 | `xxx,xx EUR` |
| Heizkosten gesamt | `x.xxx,xx EUR` |
| davon Grundkosten 30 % | `xxx,xx EUR` |
| davon Verbrauchskosten 70 % | `x.xxx,xx EUR` |

### Tabelle B - Ihr Anteil an den Grundkosten

| Beschreibung | Wert |
|--------------|------|
| Ihre Wohnflaeche in BE1 | `180 m²` |
| Gesamtwohnflaeche der Berechnungseinheit BE1 | `260 m²` |
| Ihr Anteil | `180 / 260` |
| Ihr Betrag aus den Grundkosten | `xxx,xx EUR` |

### Tabelle C - Ihr Anteil an den Verbrauchskosten

| Beschreibung | Wert |
|--------------|------|
| Ihr Heizverbrauch | `[Verbrauchseinheiten]` |
| Heizverbrauch gesamt BE1 | `[Gesamtwert]` |
| Ihr Anteil | `[Ihr Verbrauch / Gesamtverbrauch]` |
| Ihr Betrag aus den Verbrauchskosten | `xxx,xx EUR` |

### Tabelle D - Warmwasser

| Beschreibung | Wert |
|--------------|------|
| Warmwasserkosten gesamt Verbrauchseinheit BE1 | `xxx,xx EUR` |
| Ihr Warmwasserverbrauch | `[m³]` |
| Warmwasserverbrauch gesamt BE1 | `[m³]` |
| Ihr Anteil | `[Ihr Wert / Gesamtwert]` |
| Ihr Betrag | `xx,xx EUR` |

## Mock fuer Seite 3: Weitere Betriebskosten im Detail

Diese Seite zeigt die nicht-heizungsbezogenen Kostenarten aus der Excel-Welt mit nachvollziehbarer Herleitung.

Pro Kostenart werden zwei Ebenen gezeigt:
- oben der verteilte Gesamttopf
- darunter die Einzelbelege bzw. Teilpositionen

### Beispielstruktur

#### Grundsteuer

| Beleg / Position | Betrag |
|------------------|--------|
| Grundsteuerbescheid | `x.xxx,xx EUR` |
| Summe Grundsteuer | `x.xxx,xx EUR` |

| Verteilung | Wert |
|------------|------|
| Bezieht sich auf | `gesamte Liegenschaft` |
| Verteilerschluessel | `Wohnflaeche` |
| Ihre Wohnflaeche / Gesamtwohnflaeche | `180 m² / 654 m²` |
| Ihr Betrag | `xxx,xx EUR` |

Dieselbe Logik gilt fuer:
- `Muellabfuhr`
- `Kalt- und Abwasser`
- `Oberflaechenwasser`
- `Gebaeudeversicherung`

## Mock fuer Seite 4: Stromkosten

Da die Excel `Stromkosten` zeitabschnittsbezogene Tarife mit Grundpreis und Arbeitspreis fuehrt, bekommt Strom eine eigene Detailseite.

### Tabelle A - Zaehler und Zeitraum

| Feld | Wert |
|------|------|
| Stromzaehler | `[Zaehlernummer]` |
| Abrechnungszeitraum | `01.01.2024 bis 31.10.2024` |
| Anfangsstand | `[kWh]` |
| Endstand | `[kWh]` |
| Verbrauch | `[kWh]` |

### Tabelle B - Tarifabschnitte

| Zeitraum | Lieferant / Tarif | Grundpreis | Arbeitspreis | Verbrauch im Zeitraum | Kosten |
|----------|-------------------|------------|--------------|-----------------------|--------|
| `01.01.2024 - 13.02.2024` | `ePrimo / eprimo Strom PrimaKlima` | `...` | `...` | `...` | `...` |
| `14.02.2024 - 31.10.2024` | `Vattenfall / easy12 Strom` | `...` | `...` | `...` | `...` |
| **Summe Stromkosten** |  |  |  |  | `xxx,xx EUR` |

Regel:
- Strom darf nicht nur als Endbetrag erscheinen.
- Die zeitanteilige Tariflogik muss sichtbar werden.

## Mock fuer Seite 5: Messgeraete und Ablesewerte

Diese Seite dient dem gemeinsamen Durchgehen mit dem Mieter, wenn Rueckfragen zu Ablesungen entstehen.

### Tabelle A - Relevante Messgeraete

| Raum / Bereich | Geraetetyp | Seriennummer | Umrechnungsfaktor |
|----------------|------------|--------------|-------------------|
| Wohnzimmer | Heizkostenverteiler | `...` | `...` |
| Schlafzimmer | Heizkostenverteiler | `...` | `...` |
| Bad | Warmwasserzaehler | `...` |  |
| Bad | Kaltwasserzaehler | `...` |  |

### Tabelle B - Ablesewerte

| Messgroesse | Anfang | Ende | Verbrauch / Differenz |
|-------------|--------|------|------------------------|
| Heizung | `...` | `...` | `...` |
| Warmwasser | `...` | `...` | `...` |
| Kaltwasser | `...` | `...` | `...` |
| Strom | `...` | `...` | `...` |

Diese Seite ist bewusst sachlich und tabellarisch.

Sie ist nicht primaer fuer Seite 1 gedacht, aber wichtig fuer:
- Nachvollziehbarkeit
- Rueckfragen
- gemeinsames Durchgehen vor Ort

## Mock fuer das separate Anschreiben

Das Anschreiben bleibt getrennt von der eigentlichen Einzelabrechnung.

Es enthaelt:
- kurze Einleitung
- Ergebnis in einem Satz
- Zahlungsziel oder Hinweis auf Guthaben
- Kontoverbindung bzw. weiteres Vorgehen
- Hinweis auf Belegeinsicht

Es enthaelt **nicht** den kompletten Rechenweg.

Der Rechenweg gehoert in die Einzelabrechnung selbst.

## Neue Anforderung an die naechste Planiteration

Die naechste Planiteration muss dieses Mock explizit in Arbeitspakete uebersetzen:

1. Seite-1-Layout mit Ergebnisbox, Orientierungstabelle und Kernkostentabelle
2. Heiz-/Warmwasser-Detailseite
3. Betriebskosten-Detailseiten
4. Strom-Detailseite mit Tarifabschnitten
5. Messgeraete-/Ablesewerteseite
6. separates Anschreiben

## Status nach Iteration 7

- [DONE] Excel-basierte reale Kostenarten und Schluessel in das Zielbild uebernommen
- [DONE] Erstes konkretes Mock fuer Seite 1 bis Seite 5 beschrieben
- [DONE] separates Anschreiben im Zielbild verankert
- [NEXT] Mock gegen Nutzerfeedback pruefen und danach in einen aktualisierten Implementierungsplan ueberfuehren


# Iteration 8

Delta zu Iteration 7:
- Die offenen Punkte aus dem Mock-Review wurden aufgeloest.
- Das Zielbild enthaelt jetzt eine **konkret ausgefuellte Beispielseite** auf Basis von `Kraft/Huehne` aus der Excel 2024.
- Verknuepfung zwischen Orientierungstabelle und Kernkostentabelle, Vorauszahlungsdarstellung, Hinweisblock, Umlagefaehigkeitsregel und Zeitraumanteil wurden praezisiert.

## Neue Festlegung: Beispielseite mit echten Zahlen ist Pflichtbestandteil der Spec

Ab dieser Iteration reicht kein schematisches Mock mit Platzhaltern mehr.

Die Spec braucht mindestens:
- eine **voll ausgefuellte Beispielseite 1**
- mindestens eine **teilweise ausgefuellte Detailseite**

Der Referenzfall fuer das Zielbild ist:
- Mietpartei: `Kraft / Huehne`
- Nutzeinheit: `Geb. Ost - Loftwohnung (Nutzeinheit 1)`
- Zeitraum: `01.01.2024 bis 31.10.2024`

Wichtig:
- Diese Beispielseite ist kein fachlicher Zwang fuer alle Jahre
- aber sie ist der verbindliche **Lesbarkeits-Orakel-Fall** fuer Plan und Umsetzung

## Neue Festlegung: Zeitraumanteil muss sichtbar werden

Das bisherige Mock war fuer unterjaehrige Mietzeiträume noch nicht stark genug.

Problem:
- Bei `Kraft / Huehne` entstehen mehrere Betraege nicht nur aus Verteilerschluessel und Gesamtkosten,
- sondern zusaetzlich aus einem **Zeitraumanteil** (`304 / 365 Tage`).

Neue Regel:
- Wenn eine Kostenart zeitanteilig umgelegt wird, muss dies im sichtbaren Dokument auftauchen.
- Seite 1 bekommt dafuer eine eigene Spalte `Zeitraum`.

Werte in dieser Spalte:
- `304 / 365 Tage`
- `365 / 365 Tage`
- `im Verbrauch enthalten`
- `direkt fuer Ihren Zeitraum ermittelt`

Dadurch kann ein Mieter erkennen, warum z. B. bei Wohnflaechen- oder Personenumlage nicht automatisch der volle Jahresbetrag angesetzt wird.

## Neue Festlegung: Verknuepfung zwischen Orientierungstabelle und Haupttabelle

Die kleine Orientierungstabelle bleibt bestehen, bekommt aber einen klaren Zweck:
- Sie ist die **Legende** fuer die Haupttabelle.

Neue Struktur:
- Die Orientierungstabelle enthaelt eine Spalte `Referenz`.
- Die Kernkostentabelle nutzt in der Spalte `Verteilung` genau dieselben Referenzbegriffe.

Verbindliche Referenzen fuer den Beispiel-Fall `Kraft / Huehne`:

| Referenz | Bedeutung | Ihr Wert | Gesamtwert | Gilt fuer |
|----------|-----------|----------|------------|-----------|
| Wohnflaeche Liegenschaft | Wohnflaeche auf Ebene des gesamten Objekts | `180 m²` | `654 m²` | `gesamte Liegenschaft` |
| Wohnflaeche BE1 | Wohnflaeche innerhalb der Berechnungseinheit 1 | `180 m²` | `260 m²` | `Berechnungseinheit BE1` |
| Personen Liegenschaft | Personen auf Ebene des gesamten Objekts | `2` | `9` | `gesamte Liegenschaft` |
| Heizverbrauch BE1 | Heizverbrauch innerhalb der Berechnungseinheit 1 | `7.586,527` | `17.444,165` | `Berechnungseinheit BE1` |
| Warmwasser BE1 | Warmwasserverbrauch innerhalb der Verbrauchseinheit BE1 | `32,56 m³` | `57,95 m³` | `Verbrauchseinheit BE1` |
| Kaltwasser Liegenschaft | Kaltwasserverbrauch auf Ebene des gesamten Objekts | `24,95 m³` | `385,542 m³` | `gesamte Liegenschaft` |
| Zeitraum 2024 | Nutzungszeitraum innerhalb des Jahres | `304 Tage` | `365 Tage` | `01.01.2024 bis 31.10.2024` |

Regel:
- Die Orientierungstabelle erklaert die Basen.
- Die Haupttabelle wiederholt diese Basen nicht abstrakt, sondern mit denselben lesbaren Referenzen.

## Verbindliches Beispiel: Seite 1 fuer Kraft / Huehne

### Dokumentkopf

| Feld | Inhalt |
|------|--------|
| Objekt | `Hauptstrasse 2, 36381 Schluechtern` |
| Art des Dokuments | `Nebenkostenabrechnung 2024` |
| Mietpartei | `Kraft / Huehne` |
| Nutzeinheit | `Geb. Ost - Loftwohnung (Nutzeinheit 1)` |
| Zeitraum | `01.01.2024 bis 31.10.2024` |
| Abrechnungsdatum | `[Erstellungsdatum]` |

### Ergebnisbox

Die Ergebnisbox ist nicht nur inhaltlich, sondern auch visuell spezifiziert:

- volle Seitenbreite unter dem Kopf
- helle Flaeche mit klarer Umrandung
- Labelgroesse normal
- Ergebnisbetrag gross und fett
- das Wort `Nachzahlung` oder `Guthaben` steht ueber dem Betrag
- Farbe darf unterstuetzen, aber nicht die einzige Information sein

Verbindliches Beispiel:

| Zusammenfassung | Betrag |
|-----------------|--------|
| Umlagefaehige Kosten | `4.250,01 EUR` |
| Vorauszahlungen | `2.500,00 EUR` |
| Ergebnis | `Nachzahlung 1.750,01 EUR` |

Zusatzzeile direkt unter der Box:
- `Vorauszahlungen: 10 Monate x 250,00 EUR = 2.500,00 EUR`

Damit ist die Vorauszahlungszahl nicht nur genannt, sondern auch fuer den Mieter plausibilisiert.

### Orientierungstabelle

| Referenz | Ihr Wert | Gesamtwert | Gilt fuer |
|----------|----------|------------|-----------|
| Wohnflaeche Liegenschaft | `180 m²` | `654 m²` | `gesamte Liegenschaft` |
| Wohnflaeche BE1 | `180 m²` | `260 m²` | `Berechnungseinheit BE1` |
| Personen Liegenschaft | `2` | `9` | `gesamte Liegenschaft` |
| Heizverbrauch BE1 | `7.586,527` | `17.444,165` | `Berechnungseinheit BE1` |
| Warmwasser BE1 | `32,56 m³` | `57,95 m³` | `Verbrauchseinheit BE1` |
| Kaltwasser Liegenschaft | `24,95 m³` | `385,542 m³` | `gesamte Liegenschaft` |
| Zeitraum 2024 | `304 Tage` | `365 Tage` | `01.01.2024 bis 31.10.2024` |

### Kernkostentabelle

Die Beispielseite fuer `Kraft / Huehne` wird damit wie folgt konkretisiert:

| Kostenart | Bezieht sich auf | Verteilung | Ihre Basis / Gesamtbasis | Zeitraum | Ihr Betrag |
|-----------|------------------|------------|--------------------------|----------|------------|
| Grundsteuer | gesamte Liegenschaft | Wohnflaeche Liegenschaft | `180 m² / 654 m²` | `304 / 365 Tage` | `307,66 EUR` |
| Muellabfuhr | gesamte Liegenschaft | Personen Liegenschaft | `2 / 9` | `304 / 365 Tage` | `74,27 EUR` |
| Kalt- und Abwasser | gesamte Liegenschaft | Kaltwasser Liegenschaft | `24,95 m³ / 385,542 m³` | `im Verbrauch enthalten` | `384,48 EUR` |
| Oberflaechenwasser | gesamte Liegenschaft | Wohnflaeche Liegenschaft | `180 m² / 654 m²` | `304 / 365 Tage` | `181,10 EUR` |
| Gebaeudeversicherung | Berechnungseinheit BE1 | Wohnflaeche BE1 | `180 m² / 260 m²` | `304 / 365 Tage` | `726,72 EUR` |
| Brennstoffkosten - Grundkosten 30 % | Berechnungseinheit BE1 | Wohnflaeche BE1 | `180 m² / 260 m²` | `304 / 365 Tage` | `509,40 EUR` |
| Brennstoffkosten - Verbrauch 70 % | Berechnungseinheit BE1 | Heizverbrauch BE1 | `7.586,527 / 17.444,165` | `im Verbrauch enthalten` | `896,50 EUR` |
| Heiznebenkosten | Berechnungseinheit BE1 | Heizverbrauch BE1 | `7.586,527 / 17.444,165` | `im Verbrauch enthalten` | `190,20 EUR` |
| Verbrauchskosten Warmwasser | Verbrauchseinheit BE1 | Warmwasser BE1 | `32,56 m³ / 57,95 m³` | `im Verbrauch enthalten` | `482,54 EUR` |
| Strom | direkte Zuordnung zu Ihrer Nutzeinheit | direkter Stromzaehler | `direkt ueber Zaehler und Tarif berechnet` | `direkt fuer Ihren Zeitraum ermittelt` | `497,15 EUR` |
| **Summe** |  |  |  |  | **4.250,01 EUR** |

## Neue Festlegung: Heizungsdetail darf keine falsche Sammellogik erzeugen

Iteration 7 war an einer Stelle noch zu grob:
- Dort wurde ein einheitlicher Heizkostentopf mit anschliessender 30/70-Aufteilung suggeriert.

Fuer den Referenzfall in der Excel 2024 gilt stattdessen:
- `Brennstoffkosten` werden in `30 % Grundkosten` und `70 % Verbrauchskosten` getrennt
- `Heiznebenkosten` werden als eigener Topf ausgewiesen und im Beispiel ueber `Heizverbrauch BE1` verteilt

Das Zielbild darf diese fachliche Trennung nicht wieder in einem unscharfen Gesamtblock verstecken.

### Verbindliches Beispiel: Seite 2 fuer Kraft / Huehne

#### Tabelle A - Bildung der heizungsbezogenen Kosten

| Position | Betrag |
|----------|--------|
| Brennstoffkosten gesamt Berechnungseinheit BE1 | `2.944,83 EUR` |
| davon Grundkosten 30 % | `883,45 EUR` |
| davon Verbrauchskosten 70 % | `2.061,38 EUR` |
| Heiznebenkosten Berechnungseinheit BE1 | `437,34 EUR` |

#### Tabelle B - Ihr Anteil an den Grundkosten

| Beschreibung | Wert |
|--------------|------|
| Wohnflaeche BE1 | `180 m² / 260 m²` |
| Zeitraum 2024 | `304 / 365 Tage` |
| Ihr Betrag | `509,40 EUR` |

#### Tabelle C - Ihr Anteil an den verbrauchsabhaengigen Heizkosten

| Beschreibung | Wert |
|--------------|------|
| Heizverbrauch BE1 | `7.586,527 / 17.444,165` |
| Ihr Anteil aus Brennstoffkosten 70 % | `896,50 EUR` |
| Ihr Anteil aus Heiznebenkosten | `190,20 EUR` |

#### Tabelle D - Warmwasser

| Beschreibung | Wert |
|--------------|------|
| Warmwasserkosten gesamt Verbrauchseinheit BE1 | `858,82 EUR` |
| Warmwasserverbrauch BE1 | `32,56 m³ / 57,95 m³` |
| Ihr Betrag | `482,54 EUR` |

## Neue Festlegung: Kostenarten-Matrix fuer Plan und Implementierung

Die Spec braucht jetzt eine explizite Matrix, damit der naechste Implementierungsplan nicht raten muss.

### Kostenarten-Matrix fuer den Referenzfall 2024

| Kostenart | Sichtbarer Bezugsraum | Verteilung | Zeitraumspalte | Detailseite |
|-----------|------------------------|------------|----------------|-------------|
| Grundsteuer | gesamte Liegenschaft | Wohnflaeche Liegenschaft | ja | Seite 3 |
| Muellabfuhr | gesamte Liegenschaft | Personen Liegenschaft | ja | Seite 3 |
| Kalt- und Abwasser | gesamte Liegenschaft | Kaltwasser Liegenschaft | nein, im Verbrauch enthalten | Seite 3 |
| Oberflaechenwasser | gesamte Liegenschaft | Wohnflaeche Liegenschaft | ja | Seite 3 |
| Gebaeudeversicherung | Berechnungseinheit BE1 oder BE2 | Wohnflaeche der Berechnungseinheit | ja | Seite 3 |
| Brennstoffkosten - Grundkosten | Berechnungseinheit BE1 oder BE2 | Wohnflaeche der Berechnungseinheit | ja | Seite 2 |
| Brennstoffkosten - Verbrauchskosten | Berechnungseinheit BE1 oder BE2 | Heizverbrauch der Berechnungseinheit | nein, im Verbrauch enthalten | Seite 2 |
| Heiznebenkosten | Berechnungseinheit BE1 oder BE2 | Heizverbrauch der Berechnungseinheit | nein, im Verbrauch enthalten | Seite 2 |
| Verbrauchskosten Warmwasser | Verbrauchseinheit BE1 oder BE2 | Warmwasserverbrauch der Verbrauchseinheit | nein, im Verbrauch enthalten | Seite 2 |
| Strom | direkte Zuordnung zu Ihrer Nutzeinheit | direkter Stromzaehler plus Tarifabschnitte | nein, direkt fuer Ihren Zeitraum ermittelt | Seite 4 |

## Neue Festlegung: Umlagefaehigkeit wird nicht als Spalte gezeigt, aber inhaltlich abgesichert

Die Haupttabelle soll nicht durch eine zusaetzliche Spalte `umlagefaehig ja/nein` ueberladen werden.

Stattdessen gilt:
- Im tenant-facing Hauptdokument werden nur die **beruecksichtigten umlagefaehigen Kosten** gezeigt.
- Nicht umgelegte oder nicht umlagefaehige Positionen gehoeren nicht in die Hauptsumme.
- Wenn eine Rechnung nur teilweise beruecksichtigt wird, muss die Detailseite dies sprachlich sauber sagen, z. B.:
  - `In die Abrechnung einbezogener umlagefaehiger Anteil aus Rechnung vom ...`

Zusatzsatz im Hinweisblock:
- `In dieser Abrechnung sind nur die beruecksichtigten umlagefaehigen Kosten enthalten.`

## Neue Festlegung: Hinweisblock und Belegeinsicht haben festen Ort

Das bisherige Mock hatte den Hinweisinhalt, aber noch keinen festen Platz.

Neue Regel:
- Auf **Seite 1 unten** steht ein kurzer Hinweis:
  - `Die Detailseiten dieser Abrechnung enthalten die Rechengrundlagen. Belege koennen nach Terminvereinbarung eingesehen werden.`
- Auf der **letzten Seite** steht ein eigener Abschnitt `Hinweise und Pruefbarkeit`.

Dieser Abschnitt enthaelt mindestens:
1. Belegeinsicht-Hinweis
2. Quellenhinweis:
   - Betriebskostenbelege
   - ista-Messwerte
   - Ableseprotokoll
   - Stromtarife / Stromrechnungen
3. Satz zur Umlagefaehigkeit

Das separate Anschreiben enthaelt dagegen nur:
- Ergebnis in Kurzform
- Zahlungsziel oder Guthabenhinweis
- Kontoverbindung / weiteres Vorgehen

Es enthaelt **nicht** den Hinweisblock mit der eigentlichen Rechen- und Quellenlogik.

## Wirkung auf das Mieter-Review

Mit dieser Iteration wird das Mieter-Review praeziser.

Ein Mock besteht das Mieter-Review nur dann, wenn ein Mieter auf Seite 1 schnell beantworten kann:
- Wie hoch sind meine Gesamtkosten?
- Welche Vorauszahlungen wurden angesetzt und wie setzen sie sich zusammen?
- Warum sind manche Kosten nur zeitanteilig?
- Wo sehe ich die Basis fuer Wohnflaeche, Personen, Heizung, Warmwasser und Kaltwasser?
- Wo finde ich die Belege und Messwerte, wenn ich nachfragen moechte?

## Status nach Iteration 8

- [DONE] voll ausgefuellte Beispielseite 1 fuer `Kraft / Huehne` definiert
- [DONE] Zeitraumanteil als sichtbare Pflichtinformation eingefuehrt
- [DONE] Orientierungstabelle mit Haupttabelle verbindlich verknuepft
- [DONE] Heizungsdetail fachlich praezisiert
- [DONE] Hinweisblock, Umlagefaehigkeit und Vorauszahlungsdarstellung fest verortet
- [NEXT] Mock noch einmal gegen die Anforderungen und aus Mietersicht gegenlesen; wenn stabil, dann Implementierungsplan aktualisieren


# Iteration 9

Delta zu Iteration 8:
- Die letzten Lesbarkeitsluecken aus dem Mock-Review geschlossen.
- Heizverbrauch nun mit sichtbarer Einheit benannt.
- Stromzeile auf Seite 1 mit konkretem Zaehlerbezug und Verweis auf Seite 4 geschaerft.
- Vorauszahlungszeile eindeutig an den Mietzeitraum gekoppelt.
- Seite-1-Hinweis explizit auf Belegeinsicht und Detailseiten ausformuliert.

## Praezisierung: Heizverbrauch immer mit sichtbarer Einheit

Die Zahlen fuer den Heizverbrauch duerfen nicht nackt im Dokument stehen.

Neue Regel:
- Heizverbrauch wird im tenant-facing Dokument immer mit einer sichtbaren Einheit bezeichnet.
- Im Referenzfall 2024 lautet diese Bezeichnung:
  - `Heizverbrauch (Verbrauchseinheiten aus Heizkostenverteilern)`

Dadurch werden die bisher abstrakten Werte sprachlich eingeordnet.

Verbindliche Ersetzung im Beispiel:

| Referenz | Ihr Wert | Gesamtwert | Gilt fuer |
|----------|----------|------------|-----------|
| Heizverbrauch BE1 | `7.586,527 Verbrauchseinheiten` | `17.444,165 Verbrauchseinheiten` | `Berechnungseinheit BE1` |

Entsprechend auch in den Detailtabellen:
- nicht nur `Heizverbrauch BE1`
- sondern `Heizverbrauch BE1 (Verbrauchseinheiten aus Heizkostenverteilern)`

## Praezisierung: Strom auf Seite 1 braucht Identifikationsanker

Die Stromzeile auf Seite 1 darf nicht nur einen Geldbetrag zeigen.

Neue Regel:
- Die Stromzeile auf Seite 1 enthaelt mindestens
  - die Formulierung `siehe Seite 4`
  - und einen konkreten Zaehlerbezug

Verbindliches Beispiel fuer `Kraft / Huehne`:

| Kostenart | Bezieht sich auf | Verteilung | Ihre Basis / Gesamtbasis | Zeitraum | Ihr Betrag |
|-----------|------------------|------------|--------------------------|----------|------------|
| Strom | direkte Zuordnung zu Ihrer Nutzeinheit | Stromzaehler `34877025`, Tarifabschnitte siehe Seite 4 | `direkt ueber Zaehlerstand und Tarif berechnet` | `01.01.2024 bis 31.10.2024` | `497,15 EUR` |

Folgerung:
- Schon auf Seite 1 ist erkennbar, **welcher Zaehler** betroffen ist.
- Die Detailseite wird dadurch zur nachvollziehbaren Vertiefung statt zu einem zweiten Dokument ohne Anker.

## Praezisierung: Vorauszahlungen muessen an den konkreten Mietzeitraum gekoppelt sein

Die Zusatzzeile unter der Ergebnisbox wird verbindlich praezisiert.

Nicht ausreichend:
- `Vorauszahlungen: 10 Monate x 250,00 EUR = 2.500,00 EUR`

Verbindliches Beispiel:
- `Fuer Ihren Mietzeitraum 01.01.2024 bis 31.10.2024 wurden 10 Vorauszahlungen zu je 250,00 EUR beruecksichtigt.`
- `Berechnung: 10 Monate x 250,00 EUR = 2.500,00 EUR`

Dadurch ist klar:
- die Vorauszahlungen beziehen sich auf den **konkreten Abrechnungszeitraum der Mietpartei**
- es handelt sich nicht um einen abstrakten Jahreswert

## Praezisierung: Seite-1-Hinweis muss Belegeinsicht und Detailseiten explizit nennen

Der bisherige Hinweis auf Seite 1 wird verbindlich ausgeschrieben.

Verbindlicher Kurztext auf Seite 1 unten:
- `Die folgenden Detailseiten enthalten die Rechengrundlagen zu dieser Abrechnung. Belege koennen nach Terminvereinbarung eingesehen werden.`

Damit beantwortet bereits Seite 1 zwei typische Mieterfragen:
- Wo finde ich die Berechnung im Dokument?
- Kann ich die Belege einsehen?

## Wirkung auf das Zielbild von Seite 1

Die Beispielseite fuer `Kraft / Huehne` ist damit nicht nur rechnerisch, sondern auch leselogisch vollstaendig.

Sie beantwortet jetzt auf einer Seite:
- Was ist das Ergebnis?
- Fuer welchen Zeitraum gilt es?
- Welche Vorauszahlungen wurden fuer diesen Zeitraum angesetzt?
- Welche Basen wurden verwendet?
- Warum sind manche Kosten zeitanteilig?
- Welcher Stromzaehler wurde verwendet?
- Wo finde ich Details und Belegeinsicht?

## Status nach Iteration 9

- [DONE] Heizverbrauch mit sichtbarer Einheit versehen
- [DONE] Stromzeile auf Seite 1 mit Zaehleranker und Seitenverweis geschaerft
- [DONE] Vorauszahlungsdarstellung an konkreten Mietzeitraum gekoppelt
- [DONE] Seite-1-Hinweis fuer Detailseiten und Belegeinsicht verbindlich formuliert
- [NEXT] Letztes Review: ist die Spec jetzt planreif?


# Iteration 10

Delta zu Iteration 9:
- Nutzerhinweis zu Heizkostenverteilern mit Umrechnungsfaktor uebernommen.
- Die Spec unterscheidet jetzt ausdruecklich zwischen **Rohablesewert**, **Umrechnungsfaktor** und **Verbrauchseinheiten**.
- Es wird verbindlich festgelegt, dass fuer Vergleiche und Umlage **nie rohe HKV-Werte**, sondern nur die daraus berechneten Verbrauchseinheiten verwendet werden.

## Kritische Klarstellung: HKV-Rohwerte sind nicht direkt vergleichbar

Die Heizkostenverteiler in der Liegenschaft haben geraeteindividuelle Umrechnungsfaktoren.

Beispiele aus der vorhandenen Excel-Welt:
- Loftwohnung / Wohnzimmer: Umrechnungsfaktor `1,891`
- Loftwohnung / Bad: Umrechnungsfaktor `0,33`
- Wohnung 2 / Schlafzimmer: Umrechnungsfaktor `1,788`

Folgerung:
- Ein reiner HKV-Ablesewert eines Geraets ist **nicht** unmittelbar mit dem Ablesewert eines anderen Geraets vergleichbar.
- Erst durch Multiplikation mit dem Umrechnungsfaktor entstehen die fuer die Abrechnung relevanten **Verbrauchseinheiten**.

## Neue verbindliche Begriffsregel fuer HKV

Ab dieser Iteration muessen im Dokument und in den nachfolgenden Plan-/Implementierungsartefakten drei Ebenen sauber getrennt werden:

1. **Rohablesewert**
   - der am Heizkostenverteiler abgelesene Wert
   - noch **nicht** fuer die Umlage geeignet

2. **Umrechnungsfaktor**
   - geraeteindividueller Faktor aus der Messgeraete-/ista-Logik

3. **Verbrauchseinheiten**
   - `Rohablesewert bzw. Differenzwert x Umrechnungsfaktor`
   - **nur diese** Werte duerfen fuer den Heizkostenvergleich und die Kostenverteilung verwendet werden

## Neue Pflichtregel fuer das tenant-facing Dokument

Im tenant-facing Dokument gilt:
- Die Haupttabelle auf Seite 1 zeigt fuer Heizung **nur Verbrauchseinheiten**, niemals rohe HKV-Ablesewerte.
- Die Orientierungstabelle zeigt fuer `Heizverbrauch BE1` ebenfalls **nur Verbrauchseinheiten**.
- Die Detailseite fuer Heizung muss die Umrechnung transparent machen.

Nicht zulaessig waere also z. B.:
- `Ihr Heizverbrauch: 920`
- `Gesamtheizverbrauch: 2.345`

wenn dabei nicht klar ist, dass dies nur rohe HKV-Ablesewerte ohne Faktor sind.

Zulaessig ist nur:
- `Ihr Heizverbrauch: 7.586,527 Verbrauchseinheiten`
- `Gesamtheizverbrauch BE1: 17.444,165 Verbrauchseinheiten`

## Neue Pflichtstruktur fuer die Heizungs-Detailseite

Die Detailseite fuer Heizung braucht daher zusaetzlich eine **Geraete-/Umrechnungstabelle** fuer die betroffene Nutzeinheit.

Verbindliche Struktur:

| Raum | Geraet | Seriennummer | Rohwert Anfang/Ende oder Differenzwert | Umrechnungsfaktor | Verbrauchseinheiten |
|------|--------|--------------|----------------------------------------|-------------------|---------------------|
| Wohnzimmer | Heizkostenverteiler | `120298189` | `...` | `1,891` | `...` |
| Schlafzimmer | Heizkostenverteiler | `120298011` | `...` | `0,835` | `...` |
| Schlafzimmer | Heizkostenverteiler | `120298110` | `...` | `1,244` | `...` |
| Bad | Heizkostenverteiler | `129136000` | `...` | `0,33` | `...` |

Darunter folgt die Summenzeile:

| Beschreibung | Wert |
|--------------|------|
| Summe Verbrauchseinheiten Ihrer Nutzeinheit | `7.586,527 Verbrauchseinheiten` |
| Summe Verbrauchseinheiten Berechnungseinheit BE1 | `17.444,165 Verbrauchseinheiten` |

## Neue Pflichtformulierung fuer die Lesererklaerung

Die Heizungsdetailseite enthaelt einen kurzen Erklaersatz:

- `Die Heizkostenverteiler in den Raeumen haben unterschiedliche Umrechnungsfaktoren. Fuer die Abrechnung werden daher nicht die reinen Ablesewerte, sondern die daraus berechneten Verbrauchseinheiten verwendet.`

Dieser Satz ist wichtig, weil er eine typische Mieterfrage direkt beantwortet:
- Warum kann man die angezeigten Geraetewerte nicht einfach 1:1 vergleichen?

## Praezisierung der bisherigen Heizverbrauch-Referenz

Die bisherige Formulierung aus Iteration 9 wird hiermit geschaerft.

Statt nur:
- `Heizverbrauch (Verbrauchseinheiten aus Heizkostenverteilern)`

gilt fuer die Detailseite zusaetzlich:
- `Verbrauchseinheiten = Rohablesewert bzw. Differenzwert x Umrechnungsfaktor`

Damit ist nicht nur die Einheit genannt, sondern auch ihre Herkunft.

## Wirkung auf Planreife

Diese Klarstellung aendert **nicht** das Zielbild der Seite 1.

Sie verhindert aber einen moeglichen schweren Plan-/Implementierungsfehler:
- rohe HKV-Werte direkt auszuweisen oder zu vergleichen
- statt die umgerechneten Verbrauchseinheiten zu verwenden

## Status nach Iteration 10

- [DONE] HKV-Rohwert, Umrechnungsfaktor und Verbrauchseinheiten explizit getrennt
- [DONE] Verbot direkter Vergleiche mit rohen HKV-Werten festgelegt
- [DONE] Heizungsdetailseite um Geraete-/Umrechnungstabelle erweitert
- [NEXT] Kurz bestaetigen, dass die Spec mit dieser Klarstellung weiterhin planreif ist


# Iteration 11

Delta zu Iteration 10:
- Die Einzelabrechnungs-Spec wird explizit auf die neue Pipeline-Logik fuer
  - `objektweit gebucht -> fachlich Berechnungseinheit -> Partei`
  - und die lesbare Aufloesung von `Berechnungseinheit 1/2`
  abgestimmt.
- Ziel ist, dass das tenant-facing Dokument nicht nur korrekte Zahlen, sondern auch den **richtigen Bezugsraum** sichtbar macht.

## Neue Pflichtregel fuer lesbare Berechnungseinheiten

Ab dieser Iteration gilt fuer das tenant-facing Dokument:
- Interne Kurzformen wie `BE1` oder `BE2` duerfen nur verwendet werden, wenn sie beim **ersten sichtbaren Auftreten** lesbar aufgeloest werden.
- Mindestinhalt der Aufloesung:
  - `Berechnungseinheit 1 = Gebaeude Ost (Energietraeger: Oel und Waermepumpe, Nutzeinheiten 1 und 2)`
  - `Berechnungseinheit 2 = Gebaeude Nord und Gebaeude West (Energietraeger: Holz und Pellets, Nutzeinheiten 3, 4 und 5)`

Zulaessige Umsetzung im Dokument:
- direkt ausgeschrieben in Tabellen und Detailseiten,
- oder einmalige kurze Erklaerbox / Fussnote / Einfuehrung vor der ersten Tabelle, danach kuerzere Verweise.

Nicht zulaessig ist:
- `Berechnungseinheit BE2`
- ohne dass der Leser im Dokument erkennen kann, was diese Einheit konkret bedeutet.

## Neue Pflichtregel fuer den Fall `objektweit gebucht, aber nach Berechnungseinheit verteilt`

Wenn eine Kostenposition:
- im Legacy-Workbook objektweit gebucht ist,
- fachlich aber gemaess Kostenartdefinition nach Berechnungseinheiten weiterverteilt wird,

dann gilt fuer die Einzelabrechnung:
- Seite 1 und die Detailseiten zeigen als **Bezugsraum** die relevante Berechnungseinheit,
- nicht die gesamte Liegenschaft als finale Umlagebasis.

Das heisst konkret:
- Die Buchungsherkunft kann objektweit sein,
- die fuer den Mieter sichtbare Berechnungsbasis muss aber die **abrechnungswirksame Berechnungseinheit** zeigen.

Beispiel:
- Eine objektweit gebuchte heizungsbezogene Position kann fuer `Kraft / Huehne` auf Seite 1 als
  - `Berechnungseinheit 1`
  - mit ihrer zugehoerigen Basis
  erscheinen,
  obwohl die urspruengliche Betriebskostenzeile keine explizite `C`- oder `D`-Zuordnung hatte.

## Wirkung auf die Tabellen von Seite 1

Die Haupttabelle auf Seite 1 muss daher nicht nur Kosten, Schluessel und Zeitraum erklaeren, sondern auch den **richtigen Bezugsraum**.

Verbindliche Folge:
- Wenn der finale Verteilungsraum eine Berechnungseinheit ist, dann zeigt die Scope-/Bezugsraumspalte:
  - `Berechnungseinheit 1`
  - oder `Berechnungseinheit 2`
  mit lesbarer Aufloesung gemaess obiger Pflichtregel.
- Die Basisspalte zeigt dann ebenfalls die zur Berechnungseinheit gehoerige Basis:
  - z. B. Wohnflaeche innerhalb Berechnungseinheit 1,
  - Heizverbrauch innerhalb Berechnungseinheit 2,
  - Warmwasserverbrauch innerhalb Berechnungseinheit 1.

Nicht zulaessig ist:
- eine objektweit gebuchte, aber BE-gebundene Kostenposition auf Seite 1 mit globaler Basis darzustellen,
- wenn fuer die Mieterabrechnung tatsaechlich nur die jeweilige Berechnungseinheit relevant ist.

## Verbindliche Leserwirkung

Die Einzelabrechnung muss fuer den Mieter klar beantworten koennen:
- Was bedeutet `Berechnungseinheit 1` bzw. `Berechnungseinheit 2`?
- Warum wird diese Kostenposition nicht ueber die gesamte Liegenschaft, sondern nur ueber meine Berechnungseinheit verteilt?

Das Dokument soll damit gerade bei heizungsnahen Kosten Missverstaendnisse vermeiden wie:
- `Warum zahle ich fuer Kosten aus anderen Gebaeuden mit?`
- `Warum steht hier nur eine Teilmenge der Wohnflaeche / des Verbrauchs als Basis?`

## Acceptance / Verification Test Cases
1. Given ein tenant-facing Dokument mit dem ersten Auftreten von `Berechnungseinheit 1` oder `Berechnungseinheit 2`, when der Leser die Seite ohne Zusatzwissen liest, then ist die Einheit im Dokument lesbar aufgeloest.
2. Given eine objektweit gebuchte, aber BE-gebundene Kostenposition, when sie auf Seite 1 gerendert wird, then zeigt die Bezugsraumspalte die relevante Berechnungseinheit und nicht die gesamte Liegenschaft als finale Umlagebasis.
3. Given eine heizungsbezogene Position fuer `Kraft / Huehne`, when die Basis angezeigt wird, then ist klar erkennbar, dass sich die Basis auf die relevante Berechnungseinheit 1 bezieht und nicht auf das Gesamtobjekt.
4. Given die Detailseiten, when dort `Berechnungseinheit 1/2` auftaucht, then wird die gleiche Begriffsbedeutung konsistent wie auf Seite 1 verwendet.

# Iteration 12

Delta zu Iteration 11:
- Die lesbare Aufloesung von `Berechnungseinheit 1/2` wird nicht mehr nur inhaltlich, sondern auch **platzierungsseitig** festgezogen.
- Ziel ist, dass der Renderplan nicht mehr raten muss, wo diese Erklaerung im Dokument sitzt.

## Verbindliche Platzierung der Berechnungseinheiten-Erklaerung
- Wenn Seite 1 mindestens eine kostenrelevante Zeile mit finalem Bezugsraum `Berechnungseinheit 1` oder `Berechnungseinheit 2` enthaelt, dann muss Seite 1 eine kompakte Erklaerbox tragen:
  - Titel: `Berechnungseinheiten im Objekt`
  - Position: **vor der ersten Kosten-/Bezugsraumtabelle auf Seite 1**

Pflichtinhalt der Box:
- `Berechnungseinheit 1 = Gebaeude Ost (Energietraeger: Oel und Waermepumpe, Nutzeinheiten 1 und 2)`
- `Berechnungseinheit 2 = Gebaeude Nord und Gebaeude West (Energietraeger: Holz und Pellets, Nutzeinheiten 3, 4 und 5)`

Verbindliche Folge:
- Nach dieser Box duerfen die Tabellen auf Seite 1 und den Detailseiten die Kurzform
  - `Berechnungseinheit 1`
  - `Berechnungseinheit 2`
  verwenden.
- Die kuerzere Form `BE1` / `BE2` bleibt im tenant-facing Dokument weiterhin unzulaessig.

## Renderregel fuer Faelle ohne BE-bezogene Kostenzeile
- Wenn die Einzelabrechnung auf Seite 1 **keine** kostenrelevante Zeile mit Bezugsraum `Berechnungseinheit 1/2` enthaelt,
  - darf die Erklaerbox entfallen.
- In diesem Fall darf auch spaeter im Dokument keine unverstandene `Berechnungseinheit 1/2` erstmals auftauchen; falls doch, muss die Box oder eine gleichwertige Einfuehrung vorgezogen werden.

## Acceptance / Verification Test Cases
1. Given eine Einzelabrechnung mit mindestens einer Seite-1-Kostenzeile fuer `Berechnungseinheit 1` oder `Berechnungseinheit 2`, when Seite 1 gerendert wird, then erscheint vor der ersten Kosten-/Bezugsraumtabelle die Box `Berechnungseinheiten im Objekt`.
2. Given dieselbe Einzelabrechnung, when der Leser die Haupttabelle liest, then sind `Berechnungseinheit 1/2` bereits unmittelbar davor erklaert.
3. Given eine Einzelabrechnung ohne BE-bezogene Kostenzeilen auf Seite 1, when das Dokument gerendert wird, then darf die Box entfallen, aber `Berechnungseinheit 1/2` duerfen nicht spaeter erstmals unerklaert auftauchen.

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-03-23 | 0 | User | Initial requirements for a formally sufficient Einzelabrechnung, sample PDF reference, and request for a new dedicated plan/spec |
| 2026-03-23 | 1 | Claude | Reviewed sample PDF and current output code; refined requirements, target payload, document structure, and implementation plan |
| 2026-03-23 | 2 | Claude | Incorporated user edits: scope-correct heating presentation, separate cover letter, and mandatory pipeline regression/reader-oracle gates |
| 2026-03-23 | 3 | Claude | Recorded that the implemented v2 output fails as a tenant-facing document and reset the next cycle to a design-first Einzelabrechnung target image |
| 2026-03-23 | 4 | Claude | Incorporated user edits for compact page 1, mandatory allocation-key explanations, and a required tenant-perspective document review gate |
| 2026-03-23 | 5 | Claude | Replaced vague wording with precise object/billing-unit/consumption-unit/direct-assignment language for allocation explanations |
| 2026-03-23 | 6 | Claude | Removed remaining vague grouping language and fixed the visible table wording to use only precise, reader-facing allocation references |
| 2026-03-23 | 7 | Claude | Added an Excel-grounded multi-page mock with real cost categories, key types, and separate tenant letter/document roles |
| 2026-03-23 | 8 | Claude | Resolved the mock review gaps with a fully instantiated page-1 specimen, time-share rules, cost-type mapping, and fixed placement for notices and payment explanation |
| 2026-03-23 | 9 | Claude | Closed the last readability gaps by adding heating units, a page-1 electricity anchor, explicit advance-payment period wording, and a stronger page-1 inspection notice |
| 2026-03-23 | 10 | Claude | Explicitly separated HKV raw readings, conversion factors, and billed consumption units, and required a device-level conversion table on the heating detail page |
| 2026-03-23 | 11 | Copilot | Added readable Berechnungseinheit 1/2 output rules and clarified that objectwide-booked but BE-distributed costs must render with the relevant Berechnungseinheit as the final visible basis |
| 2026-03-23 | 12 | Copilot | Fixed the exact page-1 placement of the Berechnungseinheit explanation box so the tenant-facing document no longer leaves the glossary position open |

Claude session ID: `5ff61b4a-8355-4271-b526-26f6f9832807`
