# Iteration 0

Ich möchte die Nebekostenabrechnugen die ich bisher mit Hilfe der Excel '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/Nebenkostenabrechnung_2024.xlsx' manuell erstellt hatte automatisieren. Die Excel enthält die Worksheets:
Stammdaten: enthält Kostenarten mit deren Zuordnung zu einem Verteilungsschlüssel sowie der Info ob nach Berechnungseinheit umgelegt wird oder nicht
Allgemein: enthält die Nutzeinheiten der Hauptstraße 2, 36381 Schlüchtern, deren Zähler(nummern), Vertielschlüssel, sowie die den verteilschlüssel zugrunde liegende Informationen (Fläche, Personen, etc)
Messgeräte: Auflistung von Messgeräten nach Nutzeinheit, deren Nummern und Umrechnungsfaktore sowie Art (Heizkostenverteilen Stromzähler, etc.)
Messwerte: enthält die gemessen Werte nach Nutzeinheit und Zeitraum sowie die daraus resultierenden Verbräuche nach Zähler
Verbräuche: beinhaltet die Verbreuachserte für Strom, WW (Warmwasser) und KW (Kaltwasser) nach Nutzeinheit und Periode = Mieter
Betriebskosten: beinhaltet alle Belege des Abrechnungszeitraums zugeordnet zu Kostenart und deren Umlageschlüssel
Stromkosten: beinhaltet die monatlichen Stromkosten eines Mieters, dabei wird der Verbrauch auf den Monat heruntergerechnet und mit den zu diesem Zeitraum gegeben Stromkosten multipliziert. Dies ergibt den Stromverbrauch pro Tag der mit der Anzahl der Tag in diesem MOnat multipliziert wird
Die Kosten "Allgemein - Warmwasser" werden dabei auf die Verbrauchseinheit 1 umgelegt nach dem Verältnis des Warmwasserverbrauchs (Allgemein - Warmwasser beinhaltet den Verbrauch der Wärmepumpe für die Warmwasseraufbereitung von Verbrauchseinheit 1)

Danach folgen die Einzelabrechnungen nach Mieter und Zeitraum, welche das Ergebnis der Nebenkostenabrechnung darstellen.

Die Grundlage der Abrechnung sind neben den Stamm- und Allgemeindaten sowie der Messgeräte in der Excel die Ablesewerte/Messwerte, welche ich jährlich von der Firma ista erhalte. Diese können monatlich vorliegen, wie hier '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2025/Messwerte/Monatswerte - 2025 -  - NE0001(P621593463).pdf' oder jährlich wie hier  (je nachdem ob in dem Jahr ein Nutzerwechsel statgefunden hat oder nicht). Ausserdem führe ich zum Jahreswechsel ein Ableseprotokoll aus, siehe "Ableseprotokoll Muster".

Die eigentliche Abrechnung funktionierte so, dass ich die Ablesewerte aus den ista Dokumenten sowie das Ableseprotkoll in das Worksheet Messwerte übertrage. Die Verbräuche in Worksheet Verbäcuhe berechne. Die Belege des Jahres erfasse und zuornde und daraus die Einzelabrechnungen erstelle.

Diesen vorgang möchte ich nun automatisieren. Ich stelle es mir so vor: Ich lade die Dokumente der ista, Ableseprotkoll als jpeg (Bild), sowie Belege als jpeg (Bild) in einen lokalen Ordner. Dann sage ich die mach die Nebenkostenabrechnung für das Jahr XXX die Belege liegen im Ordner Y und du erstellst die Einzelabrechnungen ausgehend vom {Ordner der Belege}/../Einzelabrechnungen/{Name des Mieters}.

Ob die Excel verwendet wird oder erhalten bleibt ist mir dabei egal, auch weiß ich nicht ob die Excel die passende Struktur hat, sie war ausreichen für die manuelle erstellen enthielt jedoch redundante und schwer nachvollziehbare daten. allerdings sofern die excel erstzt wird brauche ich eine für den mieter nachvollziehbare brechnungsdokumentation samt werte und berechnungen, da ich mich ab und an mit mietern zusammensetzen muss um die vereuchswerte und abrechnung zu eräutern.

Ich möchte dass du mit mit zunbächst einen implementierungsplan erstellst indem du diese anforderungen refinest

# Iteration 1

## Summary
- Erstes strukturiertes Refinement der Anforderungen in einen umsetzbaren, phasenbasierten Plan überführt.
- Fokus auf lokale Automatisierung, Nachvollziehbarkeit für Mieter und reproduzierbare Ergebnisartefakte gelegt.
- Aktuell **nicht implementation-ready**, da mehrere produktseitige Entscheidungen und Input-Beispiele als Blocking offen sind.

## Requirements Snapshot
- Automatisiere den manuellen Prozess aus der bisherigen Excel:
  - Quelle: `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/Nebenkostenabrechnung_2024.xlsx`
  - Relevante Arbeitsblätter: `Stammdaten`, `Allgemein`, `Messgeräte`, `Messwerte`, `Verbräuche`, `Betriebskosten`, `Stromkosten`.
- Inputs sollen lokal aus Ordnern kommen:
  - ista-Dokumente (monatlich oder jährlich, PDF),
  - Ableseprotokoll (JPEG/Bild),
  - Belege (JPEG/Bild, optional PDF).
- Berechnungslogik muss erhalten bleiben, inkl. Sonderregel:
  - `Allgemein - Warmwasser` wird auf Verbrauchseinheit 1 nach Verhältnis Warmwasserverbrauch umgelegt.
- Ergebnis:
  - Einzelabrechnungen je Mieter in Zielstruktur unterhalb des Belegordners,
  - prüfbare Herleitung jeder Zahl (Quellen + Berechnungsweg) für Mietertermine.
- Excel darf ersetzt werden, sofern Transparenz und Prüfbarkeit mindestens gleichwertig sind.

## Detailed Plan
1) Ziel-Datenmodell definieren (Excel-unabhängig, aber Excel-kompatibel)
   - Entitäten: Objekt, Nutzeinheit, Mieter, Zeitraum, Messgerät, Messwert, Verbrauch, Beleg, Kostenart, Umlageschlüssel, Tarif. => es gibt ausserdem eine Verbrauchseinheit in der Nutzeinheiten zusammengefasst werden. Hintergriund ist: 
----------------
    Anlage 1 - Verteilschlüssel											
                                                
    Erläuterungen:											
    Die Nebenkostenabrechnung für das Objekt Hauptstr. 2 basiert auf zwei verschiedenen Berechnungseinheiten, die sich insbesondere durch die unterschiedlichen Energieträger und Verteilerschlüssel unterscheiden. Im Folgenden erhalten Sie eine Übersicht über die Berechnungseinheiten und wie die Kosten für jede Einheit verteilt werden.											
                                                
    Berechnungseinheit 1: Gebäude Ost (Energieträger: Öl und Wärmepumpe)											
Die Nutzeinheiten im Gebäude Ost werden mit Öl beheizt, die Warmwasseraufbereitung erfolgt über eine strombetriebene Wärmepumpe.												
1. Gebäude Ost - Loftwohnung (Nutzeinheit 1): Wohnfläche 180 m², Verteilschlüssel Wohnfläche 28 % (gesamt) bzw. 69 % (innerhalb Gebäude Ost), 2 Personen (20 % Personenanteil), Nutzfläche 180 m² (13 % der Gesamtnutzfläche).												
2. Gebäude Ost - Wohnung 2 (Nutzeinheit 2): Wohnfläche 80 m², Verteilschlüssel Wohnfläche 12 % (gesamt) bzw. 31 % (innerhalb Gebäude Ost), 2 Personen (20 % Personenanteil), Nutzfläche 80 m² (6 % der Gesamtnutzfläche).												
                                                
Berechnungseinheit 2: Gebäude Nord und Gebäude West (Energieträger: Holz und Pellets)												
Die Nutzeinheiten im Gebäude Nord und Gebäude West werden mit Holz und Pellets beheizt.												
1. Gebäude Nord - Gesindehaus (Nutzeinheit 3): Wohnfläche 60 m², Verteilschlüssel Wohnfläche 9 % (gesamt) bzw. 15 % (innerhalb dieser Berechnungseinheit), 1 Person (10 % Personenanteil), Nutzfläche 60 m² (4 % der Gesamtnutzfläche).												
2. 1-Zimmer Appartement (Nutzeinheit 4): Wohnfläche 34 m², Verteilschlüssel Wohnfläche 5 % (gesamt) bzw. 9 % (innerhalb dieser Berechnungseinheit), 1 Person (10 % Personenanteil), Nutzfläche 34 m² (3 % der Gesamtnutzfläche).												
3. Gebäude West - Wohnhaus (Nutzeinheit 5): Wohnfläche 300 m², Verteilschlüssel Wohnfläche 46 % (gesamt) bzw. 76 % (innerhalb dieser Berechnungseinheit), 4 Personen (40 % Personenanteil), Nutzfläche 1000 m² (74 % der Gesamtnutzfläche).												
--------------


   - Persistenz: lokale SQLite-Datei + versionierbare JSON-Exports für Reproduzierbarkeit.
   - Mappingtabelle von Excel-Spalten auf kanonische Felder erstellen (Importadapter).

2) Ingestion-Pipeline (lokaler Jahreslauf)
   - CLI-Einstieg: `abrechnung run --jahr YYYY --belege <ordner> --out <ordner>`.
   - Ordnerkonvention:
     - `.../{YYYY}/Messwerte/`
     - `.../{YYYY}/Ableseprotokoll/`
     - `.../{YYYY}/Belege/`
   - PDF-Extraktion (Textlayer) mit OCR-Fallback für Scans.
   - Bild-OCR für Ableseprotokoll/Belege; Extraktion von Datum, Betrag, Lieferant, Kostenart, Zählerbezug.

3) Validierung und manuelle Prüfqueue
   - Regeln: fehlende Pflichtfelder, unplausible Messwertsprünge, Zählernummer-Mismatch, doppelte Belege.
   - Jede Unsicherheit erzeugt Prüfposten (blocking für Endabrechnung, non-blocking für Zwischenlauf).
   - Korrekturen werden protokolliert (wer, was, wann) zur Nachvollziehbarkeit.

4) Berechnungskern implementieren
   - Verbrauchsermittlung je Zähler/Zeitraum inkl. Nutzerwechsel.
   - Kostenumlage je Kostenart über hinterlegten Verteilungsschlüssel.
   - Stromkosten: periodisierte Tarifbewertung gemäß bisherigem Modell (Tag/Monat-Logik).
   - Sonderregel `Allgemein - Warmwasser` explizit als eigene Regelstufe mit Testabdeckung.

5) Ausgabe und Dokumentationsartefakte
   - Pro Mieter:
     - Einzelabrechnung (lesbares Enddokument),
     - Prüfbericht mit Rechenweg je Position,
     - maschinenlesbare JSON-Datei mit allen Zwischenwerten.
   - Laufbericht:
     - Summenkontrollen, offene Prüfposten, verwendete Quelldokumente.

6) Migrationsstrategie und Rollout
   - Phase A (Stabilisierung): Excel als Referenz + Importquelle.
   - Phase B (Parallelbetrieb): alte Excel-Abrechnung vs. neue Pipeline für ein Referenzjahr vergleichen.
   - Phase C (Ablösung): neue Pipeline führend, Excel nur noch optionaler Export/Archiv.

## Open Items
- [MISSING BLOCKING] Mindestens ein vollständiger Beispieldatensatz pro Dokumenttyp (ista monatlich, ista jährlich, Ableseprotokoll-Bild, 3-5 typische Belege) mit realer Feldstruktur. => ich habe dir unten den satz von 2024 gegeben
- [MISSING BLOCKING] Ziel-Template für die Einzelabrechnung (Pflichtfelder, Layout, juristisch nötige Hinweise). => ich habe mich bei meinen Abrechnungen an den templates der ista orientiert, siehe '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2023/ista_Dokumente_2024-09-23_16-07-26/Einzelabrechnung_026490450_2023_0001_0_Kraft_Hühne_03_09_2024_4.pdf', dabei habe ich die Abrechnungen aufs wesentliche beschränkt und CO-Zertifkate etc rausgelassen. das fertige ergbenis sah bei mir so '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Einzelabrechnung_NE1_Kraft_Huehne_2024.docx' bzw. so aus '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Einzelabrechnung_NE1_Kraft_Huehne_2024.pdf', allerdings sollte hier nicht einfach bilder copy&pasted werden so wie ich das gemacht hatte. stattdessen sollen die werte tabellarisch aufgeführt werden. vielleicht ist docx auch nicht das beste format, sondern eher markdown und dann typst, wie wir es auch bei den bewerbungen genutzt haben, siehe /Users/dh/Documents/DanielsVault/private/me
- [DECISION BLOCKING] Outputformat für Einzelabrechnung: nur PDF vs. DOCX+PDF. => PDF ist Ok
- [DECISION BLOCKING] MVP-Start: erst halbmanuelle strukturierte Eingaben (CSV/JSON) oder direkt OCR-first. => direkt OCR first, ich möchte dir die belege, samt Abrechungen für 2024 geben, diese kannst du als tests, sowohl für die OCR erkennung als auch der gesamten pipelinenutzen (beachte dabei dass der Vorgang manuell war, es können also fehler drin sein, aber zur ersten verifizierung sollte es reichen), hier die eingabewerte: 
    - belege von 2024: '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Belege_Nebenkostenabrechnung_2024' 
    - ablesequittungen der ista jährlich: '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Ablesequittungen AZ 2024.pdf'
    - ablesequittungen der ista monatlich: '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Monatswerte - 2024 -  - NE0001(P560620521).pdf'
    - ableseprotokoll nach muster: '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/20260314_121317.jpg'

    => die ergebnisse der abrechnung sind in den excel worksheets Einzelabrechnung_1, Einzelabrechnung_1.2, Einzelabrechnung_2, Einzelabrechnung_3, und Einzelabrechnung_4. analysiere das workbook um daraus testcases abzuleiten.
- [DECISION NON-BLOCKING] Technologie-Stack für Umsetzung (Python-CLI vs. n8n-orchestriert mit Rechenkern in Python). => n8n auf keine fall, python wäre gut, c# eine option oder eher nicht?

# Iteration 2

## Summary
- Die `=>`-Antworten aus Iteration 1 wurden in verbindliche Entscheidungen überführt.
- Das Fachmodell wurde um **Verbrauchseinheit (VE)** präzisiert, die mehrere Nutzeinheiten bündelt.
- Der Plan ist jetzt **implementation-ready**, da alle zuvor BLOCKING-markierten Punkte aufgelöst wurden.

## Requirements Snapshot
- OCR-first bleibt gesetzt, mit Referenzdatenjahr 2024 als erster End-to-End-Validierungslauf.
- Referenzinputs:
  - Belege: `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Belege_Nebenkostenabrechnung_2024`
  - ista jährlich: `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Ablesequittungen AZ 2024.pdf`
  - ista monatlich: `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/Monatswerte - 2024 -  - NE0001(P560620521).pdf`
  - Ableseprotokoll: `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024/20260314_121317.jpg`
- Sollwerte für den Erstvergleich kommen aus dem vorhandenen Workbook (`Einzelabrechnung_1`, `Einzelabrechnung_1.2`, `Einzelabrechnung_2`, `Einzelabrechnung_3`, `Einzelabrechnung_4`).
- Output ist festgelegt auf **PDF**.
- Dokumentdarstellung soll tabellarisch und nachvollziehbar sein (kein Bild-Copy&Paste).
- Technologieentscheidung für MVP: **Python**; **n8n ausgeschlossen**.

## Detailed Plan
1) Domänenmodell finalisieren
   - Entitäten: Objekt, Berechnungseinheit, Verbrauchseinheit, Nutzeinheit, Mieterzeitraum, Messgerät, Messwert, Verbrauch, Kostenart, Umlageschlüssel, Tarif, Beleg/Belegposition.
   - Beziehungen:
     - BE gruppiert NE fachlich nach Energieträger/Abrechnung.
     - VE gruppiert NE für verbrauchsbezogene Umlagen.
   - Sonderregel als deklarative Regel:
     - `Allgemein - Warmwasser` -> VE1 proportional zu WW-Verbrauch.

2) OCR-first Ingestion für 2024 implementieren
   - Parsermodule für ista jährlich/monatlich, Ableseprotokoll-Bild und Belegbilder.
   - Jeder extrahierte Wert bekommt `source_ref` (Datei, Seite/Region) und `confidence`.
   - Unsichere/fehlende Felder laufen in eine Prüfqueue, statt stiller Default-Werte.

3) Berechnungskern (deterministisch) aufbauen
   - Messwerte -> Verbräuche je Gerät/Zeitraum.
   - Umlage je Kostenart über Schlüsselraum (BE/VE/NE).
   - Stromkosten gemäß bestehender Tages-/Monatslogik.
   - Vollständiges Rechenprotokoll pro Zielwert (`inputs`, `formula`, `result`).

4) Reporting auf PDF umsetzen
   - Pipeline: strukturierte Daten -> tabellarisches Template -> PDF.
   - Template-Inspiration aus ista-Struktur und bestehender 2024-Abrechnung, aber rein datengetrieben.
   - Ausgabe je Mieter in:
     - `{Belegordner}/../Einzelabrechnungen/{Mietername}/Einzelabrechnung_{jahr}.pdf`
     - plus `Pruefbericht_{jahr}.pdf` und `abrechnung_{jahr}.json`.

5) Verifikation gegen manuellen 2024-Stand
   - Workbook-Blätter `Einzelabrechnung_*` als Sollvergleich einlesen.
   - Delta-Bericht je Mieter erzeugen (Abweichung + Begründung).
   - Manuelle Vorfehler im Altprozess werden als dokumentierte Abweichung behandelt, nicht blind übernommen.

## Open Items
- [MISSING NON-BLOCKING] Finale juristische Textbausteine/Hinweise für das PDF-Deckblatt und den Prüfbericht festlegen.
- [DECISION NON-BLOCKING] Nach MVP entscheiden, ob zusätzlich ein CSV-Export für externe Weiterverarbeitung (Steuerberater) standardmäßig erzeugt wird.

## Verification Test Cases
1) Given die 2024-Quelldokumente im Ist-Zustand (PDF/JPG), when der Pipeline-Lauf für 2024 gestartet wird, then werden je Mieter eine PDF-Einzelabrechnung, ein Prüfbericht und JSON-Artefakte erzeugt.

2) Given ein ista-Monatswerte-PDF, when OCR+Parser ausgeführt werden, then werden Zählernummer, Zeitraum und Messwerte mit Quellreferenz extrahiert oder als Prüfqueue-Fall markiert.

3) Given ista-Jahreswerte plus Ableseprotokoll-Bild, when Messwerte konsolidiert werden, then entsteht ein konsistenter Start-/Endstand pro Gerät bzw. ein expliziter Konfliktfall.

4) Given die Kostenart `Allgemein - Warmwasser`, when die Umlage berechnet wird, then erfolgt die Verteilung ausschließlich auf VE1 proportional zum WW-Verbrauch.

5) Given die Soll-Ergebnisse in den Blättern `Einzelabrechnung_1`, `Einzelabrechnung_1.2`, `Einzelabrechnung_2`, `Einzelabrechnung_3`, `Einzelabrechnung_4`, when der Delta-Vergleich ausgeführt wird, then wird pro Mieter ein nachvollziehbarer Differenzbericht erstellt.

6) Given unvollständige OCR-Felder in einem Beleg, when der Endlauf gestartet wird, then stoppt der Abschlussstatus auf „manuelle Prüfung erforderlich“ statt stiller Fortschreibung mit impliziten Defaults.

# Iteration 3

## Summary
- Review-Ergebnis: **Iteration 2 war zu früh als implementation-ready markiert**. Grund: Testfälle waren überwiegend strukturell und hatten keinen ausreichenden Input->Expected-Oracle mit Zahlen.
- Diese Iteration ergänzt einen **numerischen Golden-Oracle** (2024) mit konkreten Sollwerten und Formeln.
- Damit ist der Plan jetzt implementation-ready auf Basis eines klaren, datenbezogenen Abnahmerasters.

## Requirements Snapshot
- Akzeptanz erfolgt über zwei Ebenen:
  - **E1 Struktur/Verhalten** (Dateien, Fehlerstatus, Prüfqueue),
  - **E2 Zahlenkorrektheit** (konkrete Input->Output-Werte aus 2024-Referenzdaten).
- Primäre 2024-Oracle-Quellen:
  - Workbook `Nebenkostenabrechnung_2024.xlsx` (Blätter `Messwerte`, `Verbräuche`, `Stromkosten`, `Einzelabrechnung_*`).
  - zugehörige 2024-Dokumente (ista + Belege + Ableseprotokoll) als Inputquellen der Pipeline.
- Rundungsregeln für Tests:
  - interne Berechnung mit voller Präzision,
  - Assertion auf EUR-Werte mit Toleranz `<= 0,01`,
  - Anteile/Quoten mit Toleranz `<= 1e-9`.

## Detailed Plan
1) Test-Oracle als Fixture-Datei codifizieren
   - `tests/fixtures/oracle_2024.json` enthält pro Testfall:
     - input references (Dokument, Blatt, Zeile/Spalte),
     - erwartete Zwischenwerte,
     - erwartete Endwerte.

2) Deterministische Rechenkette pro Kostenblock absichern
   - Messwert -> Verbrauch -> Umlageanteil -> Kostenanteil -> Endsaldo.
   - Jede Stufe muss separat testbar sein (Unit) und im E2E reproduzierbar.

3) Abnahmekriterium schärfen
   - Ein Lauf gilt nur als „bestanden“, wenn:
     - alle E1-Checks grün sind,
     - alle E2-Assertions grün sind oder dokumentierte, begründete Abweichungen vorliegen.

4) Delta-Bericht mit Zahlenbezug
   - Für jede Abweichung: `expected`, `actual`, `delta`, `source_ref`, `formula_ref`.
   - Keine bloße „Differenz vorhanden“-Meldung mehr.

## Open Items
- [MISSING NON-BLOCKING] Nach MVP zusätzlich zweites Oracle aus direkt extrahierten ista-PDF-Werten versionieren (reduziert Abhängigkeit vom manuellen Excel-Stand).

## Verification Test Cases
1) **Messwert -> Verbrauch (NE1 Stromzähler 34877025)**
   - Given `Messwerte` (row 15): Start `33470.2`, Ende `34683.1`, Zeitraum `01.01.2024-31.10.2024`,
   - when Verbrauch berechnet wird,
   - then Verbrauch = `1212.9 kWh` (Workbook zeigt `1213` gerundet) und Tagesverbrauch `4.002970297029708 kWh`.

2) **Allgemein-Warmwasser Zählerverbrauch**
   - Given `Verbräuche` (row 9): Messwert Anfang `10100`, Ende `15087` (Allgemein Zähler Gebäude Ost),
   - when Warmwasser-Stromverbrauch gebildet wird,
   - then Rohdifferenz = `4987`, umlagefähiger Verbrauch = `2453.449999999999 kWh`, Tagesverbrauch = `6.703415300546445`.

3) **Monatskostenformel Allgemein-Warmwasser (Januar 2024)**
   - Given Arbeitspreis `37.22 ct/kWh` (`Stromkosten` row 51 col 15), Tagesverbrauch `6.703415300546445` (col 16), 31 Tage,
   - when Monatskosten berechnet werden,
   - then Kosten Januar = `77.34534642076498 €` (`0.3722 * 6.703415300546445 * 31`).

4) **Jahressumme Allgemein-Warmwasser**
   - Given `Stromkosten` rows `51..62` (col 17),
   - when Jahreskosten aggregiert werden,
   - then Summe = `858.8160953278683 €`.

5) **WW-Anteile NE1/NE2**
   - Given `Verbräuche`:
     - NE1 WW = `32.56 m³` (row 5 col 13),
     - NE2 WW = `25.389999999999986 m³` (row 6 col 13),
     - Gesamt = `57.94999999999999 m³`,
   - when Anteile berechnet werden,
   - then NE1-Anteil = `0.5618636755823988`, NE2-Anteil = `0.43813632441760125`, Summe = `1.0`.

6) **Allgemein-Warmwasser Umlage auf VE1 mit Euro-Werten**
   - Given Gesamtkosten WW `858.8160953278683 €` und Anteile aus TC5,
   - when Kosten verteilt werden,
   - then
     - NE1/VE1 Anteil = `482.5375679702399 €` (`Einzelabrechnung_1` row 22 col 10),
     - NE2/VE1 Anteil = `376.2785273576285 €` (`Einzelabrechnung_2` row 22 col 10).

7) **Endergebnis Einzelabrechnung NE1**
   - Given vollständige Kosten- und Umlagekette für `Einzelabrechnung_1`,
   - when Summe und Saldo berechnet werden,
   - then `Summe = 4250.010438061518 €` (row 26 col 10) und `Nachzahlung = 1750.0104380615176 €` (row 29 col 10).

8) **Endergebnis Einzelabrechnung NE2**
   - Given vollständige Kosten- und Umlagekette für `Einzelabrechnung_2`,
   - when Summe und Saldo berechnet werden,
   - then `Summe = 3558.2017735022396 €` und `Nachzahlung = 798.2017735022396 €`.

9) **Endergebnis Einzelabrechnung NE3/NE4**
   - Given vollständige Kosten- und Umlagekette für `Einzelabrechnung_3` und `Einzelabrechnung_4`,
   - when Summe und Saldo berechnet werden,
   - then
     - NE3: `Summe = 1688.74665610264 €`, `Nachzahlung = 188.74665610263992 €`,
     - NE4: `Summe = 1265.700879470499 €`, `Guthaben = 24.299120529500897 €`.

10) **Fail-safe bei fehlendem OCR-Feld**
   - Given ein Beleg ohne erkannten Betrag,
   - when der Endlauf ausgeführt wird,
   - then wird kein finales PDF als „fertig“ markiert; stattdessen entsteht ein Prüfposten mit `source_ref` und Status „manuelle Prüfung erforderlich“.

# Iteration 4

## Summary
- OCR-first wurde praktisch vorgezogen und mit den realen 2024-Quellen ausgeführt.
- Ergebnis: Es liegen jetzt belastbare OCR-Evidenzen vor, die als **Input-Orakel** für die Testfälle dienen (nicht nur Excel-Endwerte).
- Die Testfälle wurden auf **OCR -> kanonische Daten -> Berechnung -> Endergebnis** umgestellt.

## Requirements Snapshot
- Neue OCR-Artefakte (Session-Artefakte):
  - `/Users/dh/.copilot/session-state/5ff61b4a-8355-4271-b526-26f6f9832807/files/ocr_ista_pdfs_2024.json`
  - `/Users/dh/.copilot/session-state/5ff61b4a-8355-4271-b526-26f6f9832807/files/protocol_ocr_try.json`
  - `/Users/dh/.copilot/session-state/5ff61b4a-8355-4271-b526-26f6f9832807/files/ocr_belege_2024.json`
- OCR belegt u. a. folgende Kernwerte direkt aus Quellen:
  - Ableseprotokoll: `34877025 -> 34683,2`, `57374902 -> 5572,65`, `200240104 -> 103,51`, `ISK0083645388 -> 15087`.
  - ista Jahres/Monatswerte: `200822219` mit `135,98 / 110,59`, `210875752` mit `94,81 / 71,98`, `200240104` mit Monatsendwert `103,51`.
  - Belege-OCR: z. B. `20251116_144617.jpg` enthält `Gesamt-Betrag 338,46` und Datum `07.12.2024`.
- Für MVP wird die bereits im Bestand enthaltene Ableitung `4987 -> 2453,45 kWh` als explizit konfigurierter Rechenschritt geführt, bis die allgemeine Fachregel formalisiert ist.

## Detailed Plan
1) OCR-Normalisierung als verbindlicher Vorlauf
   - OCR-Output wird in kanonische `observations` überführt:
     - `source_type`, `source_file`, `meter_id`, `reading_value`, `reading_date`, `unit`, `confidence`.
   - Dezimalnormalisierung (`103,51` -> `103.51`), Meter-ID-Normalisierung, Datumsnormalisierung.

2) Cross-Source-Reconciliation
   - Jede Observation wird gegen `Messwerte` gematcht (Meter+Zeitpunkt).
   - Match-Status: `exact`, `fuzzy`, `conflict`, `missing`.
   - Nur `exact/fuzzy` gehen automatisiert in die Berechnung; `conflict/missing` in Prüfqueue.

3) Konfigurierter Übergangsbaustein für Allgemein-Warmwasser (MVP)
   - Konfigwert `ww_general_kwh_factor_be1_2024 = 0.491969119711249` (aus Bestandskalibrierung):
     - `4987 * 0.491969119711249 = 2453.449999999999`.
   - Als explizite, dokumentierte Regel im Rechenprotokoll; später durch allgemeine Fachregel ersetzbar.

4) Testorakel-Schichten
   - L1 OCR-Orakel (Quellwerte erkannt),
   - L2 Canonical-Orakel (Werte korrekt normalisiert/gemappt),
   - L3 Berechnungs-Orakel (Zwischen-/Endwerte korrekt).

5) Reporting-Orakel
   - Delta-Bericht muss je Abweichung enthalten:
     - `source_file`, `ocr_value`, `canonical_value`, `expected`, `actual`, `formula_ref`.

## Open Items
- [MISSING NON-BLOCKING] Fachliche Generalisierung der Regel `ww_general_kwh_factor_be1_2024` für Folgejahre (statt jahresspezifischer Kalibrierung). => ww_general_kwh_factor_be1_2024 ist kein festern faktor sondern ergbits sich aus dem verhältnis des warmwasserverbrauchs in berechnungseinheit 1
- [DECISION NON-BLOCKING] Ob Belegklassifikation ab MVP rein regelbasiert oder zusätzlich mit lernender Zuordnung (z. B. Lieferant->Kostenart-Mapping) erfolgen soll. => mit lernender zuorndung
=> wir haben bei den bsaisdaten den stromtarif vergessen, der liegt momentan in Worksheet Stromkosten und beinhaltet den arbeitspreis je kwh (verbrauchsbasiert) und den grundpreis (pauschaler wert). diese daten muss ich vor durchlauf der pipeline auch irgendwie angeben

## Verification Test Cases
1) **OCR Ableseprotokoll -> Stromzähler NE1**
   - Given `protocol_ocr_try.json` (Preview enthält `34877025` und `34683,2`),
   - when OCR normalisiert wird,
   - then Canonical Observation enthält `meter_id=34877025`, `reading_value=34683.2`, `source_file=20260314_121317.jpg`.

2) **OCR Ableseprotokoll -> Stromzähler NE2**
   - Given `protocol_ocr_try.json` (Preview enthält `57374902` und `5572,65`),
   - when OCR normalisiert wird,
   - then Canonical Observation enthält `meter_id=57374902`, `reading_value=5572.65`.

3) **OCR ista jährlich -> Warmwasser/Kaltwasser NE2**
   - Given `ocr_ista_pdfs_2024.json` (Seite mit `200822219`, `135,98`, `110,59` und `210875752`, `94,81`, `71,98`),
   - when OCR normalisiert + gemappt wird,
   - then Matching auf `Messwerte` erfolgt mit:
     - `200822219`: Ende `135.98`, Anfang `110.59`,
     - `210875752`: Ende `94.81`, Anfang `71.98`.

4) **OCR ista monatlich -> Monatsendwert Warmwasser**
   - Given `ocr_ista_pdfs_2024.json` (Monatswerte enthält `200240104` und `103,51`),
   - when Monatsreihe extrahiert wird,
   - then Monatsendwert `103.51` wird erkannt und gegen `Messwerte` konsistent gematcht.

5) **Allgemeinzähler Ost aus OCR/Bestand -> Messwerte**
   - Given Ablesewert `15087` (Protokoll-OCR) und Anfang `10100` (Bestandswert),
   - when Differenz berechnet wird,
   - then `raw_diff_kwh = 4987` und dies entspricht `Messwerte` (Allgemein, ISK0083645388).

6) **MVP-Regel Allgemein-Warmwasser**
   - Given `raw_diff_kwh=4987` und `ww_general_kwh_factor_be1_2024=0.491969119711249`,
   - when umlagefähiger WW-Stromverbrauch berechnet wird,
   - then `4987 * 0.491969119711249 = 2453.449999999999 kWh`.

7) **Monatskosten Januar Allgemein-Warmwasser**
   - Given Arbeitspreis `37.22 ct/kWh`, Tagesverbrauch `6.703415300546445`, 31 Tage,
   - when Kosten berechnet werden,
   - then `77.34534642076498 €`.

8) **VE1-Umlage der WW-Stromkosten**
   - Given Jahreskosten `858.8160953278683 €`, Anteile `0.5618636755823988 / 0.43813632441760125`,
   - when Verteilung erfolgt,
   - then `NE1=482.5375679702399 €` und `NE2=376.2785273576285 €`.

9) **Beleg-OCR Extraktion (struktur + Betrag)**
   - Given `ocr_belege_2024.json` für `20251116_144617.jpg`,
   - when Belegdaten extrahiert werden,
   - then Kandidaten enthalten `Gesamt-Betrag=338,46` und Datum `07.12.2024` zur späteren Kostenart-Zuordnung.

10) **Endergebnis-Orakel je Einzelabrechnung**
   - Given alle gemappten OCR-Eingaben + Rechenkern,
   - when Endlauf 2024 ausgeführt wird,
   - then:
     - `Einzelabrechnung_1`: Summe `4250.010438061518`, Nachzahlung `1750.0104380615176`,
     - `Einzelabrechnung_2`: Summe `3558.2017735022396`, Nachzahlung `798.2017735022396`,
     - `Einzelabrechnung_3`: Summe `1688.74665610264`, Nachzahlung `188.74665610263992`,
     - `Einzelabrechnung_4`: Summe `1265.700879470499`, Guthaben `24.299120529500897`.

# Iteration 5

## Summary
- Deine neuen `=>`-Antworten wurden übernommen und offene Punkte aus Iteration 4 konkretisiert.
- Die Regel zu `ww_general_kwh_factor_be1_2024` wurde präzisiert: Der Faktor ist **jahresdynamisch** und wird pro Jahr aus den Verbräuchen neu berechnet (nicht aus Vorjahreswerten übernommen).
- Belegklassifikation ist auf **lernende Zuordnung** festgelegt.
- Stromtarif wurde als fehlende Basisdatenquelle ergänzt und als Pflichtinput vor Laufstart spezifiziert.
- Diese Iteration ist zugleich der **maßgebliche Planstand** und enthält den aktuellen Umsetzungsstatus:
  - **Umgesetzt:** TDD-Basis, Tarifvalidierung, WW-Regel, Fixture-Regression, `run-folder`-CLI, Artefakt- und JSON-Ausgabe.
  - **Teilweise umgesetzt:** OCR-Ingestion und Belegklassifikation.
  - **Noch nicht umgesetzt:** vollständige OCR-zu-Rechenkern-Verarbeitung ohne Workbook-Abhängigkeit sowie PDF-Einzelabrechnung/Prüfbericht.

## Requirements Snapshot
- Allgemein-Warmwasser-Verteilung in BE1:
  - `share_ne = ww_m3_ne / sum(ww_m3 in BE1)`
  - `cost_ne = total_ww_cost_be1 * share_ne`
  - optionaler abgeleiteter Faktor nur als Reportinggröße:
    - `factor(year) = ww_kwh_allocated_be1(year) / raw_general_meter_kwh(year)`
    - Beispiel 2024: `2453.449999999999 / 4987 = 0.491969119711249`
  - der Faktor wird **jedes Jahr neu berechnet**.
- Belegklassifikation:
  - lernend (mit Review-Loop), nicht rein statisch-regelbasiert.
- Stromtarif als Pflicht-Basisdaten:
  - Quelle derzeit `Worksheet Stromkosten`,
  - enthält Arbeitspreis (`ct/kWh`) + Grundpreis (`€/Jahr`) + Gültigkeit (`Von/Bis`),
  - muss vor Pipeline-Lauf übergeben/importiert werden.

## Detailed Plan
1) Tarifdatenmodell als First-Class Input
   - Neue Entität `tariff_period`:
      - `meter_scope|tenant_scope`, `valid_from`, `valid_to`, `supplier`, `tariff_name`,
      - `arbeitspreis_ct_kwh`, `grundpreis_eur_year`, `currency`, `source_ref`.
   - Pflichtvalidierung vor Berechnung: mindestens eine lückenlose Tarifperiode für den Abrechnungszeitraum.
   - **Status:** umgesetzt.

2) Tarif-Importpfad spezifizieren
   - Primär: Import aus `Stromkosten`-Worksheet.
   - Sekundär: JSON/CSV-Datei (`tariffs_YYYY.json|csv`) als Laufparameter.
   - Laufabbruch mit klarer Fehlermeldung bei Tariflücken.
   - **Status:** umgesetzt.

3) Kostenberechnung mit Tarifperioden
   - Periodisierung je Monat/Teilmonat:
      - `arbeitspreis_cost = (ct/kWh / 100) * consumption_kwh_period`
      - `grundpreis_cost = (grundpreis_eur_year / days_in_year) * days_in_period`
   - Summierung über alle Perioden je Mieter/Verbrauchseinheit.
   - **Status:** umgesetzt für die vorhandenen workbook-basierten Eingaben und numerischen Testfälle; noch nicht vollständig auf rein OCR-normalisierte Eingaben umgestellt.

4) Allgemein-Warmwasser-Regel finalisieren
   - Verteilformel explizit auf WW-Verbrauchsverhältnis innerhalb BE1.
   - Der abgeleitete Umrechnungsfaktor wird als `factor(year)` geführt und pro Abrechnungsjahr neu bestimmt.
   - Rechenprotokoll muss `ww_m3_ne`, `ww_total_be1`, `share_ne`, `cost_ne` ausweisen.
   - **Status:** umgesetzt.

5) Lernende Belegzuordnung
   - Trainingsbasis: 2024-Belege + manuelle Labels (Kostenart/Umlageschlüssel).
   - Inferenz liefert `predicted_category`, `confidence`.
   - Unterhalb Schwellwert: manuelle Review; oberhalb Schwellwert: automatische Zuordnung.
   - **Status:** baseline umgesetzt (Classifier + Review-Loop), produktiver Trainingsprozess noch offen.

6) Abnahme-Orakel um Tarif-/Klassifikationspfad erweitern
   - Neben Endsummen explizite Assertions für:
      - korrekte Tarifperiodisierung,
      - korrekte WW-Verteilung BE1,
      - nachvollziehbare Beleg-Klassifikationsentscheidung.
   - **Status:** umgesetzt.

7) Ordnerbasierter Ziel-Workflow
   - Dokumente lokal in Jahresordner ablegen:
     - ista-PDFs,
     - Ableseprotokoll als Bild,
     - Belege als Bilder/PDFs.
   - CLI-Aufruf:
     - `python3 -m nebenkosten_pipeline.cli run-folder --jahr <YYYY> --belege-dir <Pfad> [--workbook <xlsx>]`
   - Laufartefakte:
     - `{Belegordner}/../_pipeline_runs/{jahr}/run.db`
     - `{Belegordner}/../_pipeline_runs/{jahr}/ocr_snapshot_<jahr>.json`
   - Ausgabe:
     - `{Belegordner}/../Einzelabrechnungen/{Mietername}/...`
   - **Status:** teilweise umgesetzt; aktuell werden JSON-Einzelabrechnungen erzeugt, PDF-Ausgabe fehlt noch.

8) Datenquellen und Regression
   - 2024-Quelldaten im Repo unter `Vermietung/nebenkosten_pipeline/fixtures/2024/`.
   - Regressionstest gegen echtes 2024-Workbook.
   - **Status:** umgesetzt.

## Open Items
- Keine offenen Nutzerentscheidungen oder Rückfragen in dieser Iteration.
- Verbleibende Implementierungsaufgaben:
  - Strukturierte OCR-Extraktion für Messwert-/Belegdaten als kanonische Eingaben in den Rechenkern vervollständigen.
  - Cross-Source-Reconciliation (`exact/fuzzy/conflict`) vollständig implementieren.
  - Vollständige End-to-End-Verarbeitung der Belege in Kostenart/Umlageschlüssel/Kostenpositionen umsetzen.
  - Workbook-Abhängigkeit im Rechenkern schrittweise durch OCR-/Stammdaten-basierte Eingaben ersetzen.
  - PDF-Einzelabrechnung und PDF-Prüfbericht pro Mieter im Zielpfad `{Belegordner}/../Einzelabrechnungen/{Mietername}` implementieren.
  - Produktiven Trainings-/Reviewprozess für die lernende Belegklassifikation aufbauen.
  - `confidence_threshold` und finale Lernmethode im Zuge des produktiven Trainings festziehen.

## Verification Test Cases
1) **Tarifpflicht vor Laufstart**
   - Given kein importierter Stromtarif für 2024,
   - when `abrechnung run --jahr 2024` gestartet wird,
   - then Laufstatus = `blocked` mit Meldung „Tarifdaten unvollständig“ und ohne finale Einzelabrechnung.
   - **Status:** PASS.

2) **Tarifperiodisierung aus Stromkosten**
   - Given Tarifperioden aus `Stromkosten`:
      - `01.09.2023-13.02.2024`: Arbeitspreis `37.22`, Grundpreis `301.37`,
      - `14.02.2024-14.02.2025`: Arbeitspreis `34.57`, Grundpreis `130.8`,
   - when der Verbraucher `Kraft/Hühne` für Januar/Februar/März 2024 bewertet wird,
   - then gelten folgende konkreten Sollwerte aus `Stromkosten` (inkl. Grundpreis-Pro-rata):
      - Januar 2024: `grundpreis_anteil=12.557083333333333`, `arbeitspreis=37.22`, `verbrauch_pro_tag=4.002970297029708`, `monat_kosten=58.7441552145215`
      - Februar 2024: `grundpreis_anteil=12.557083333333333`, `arbeitspreis=37.22`, `verbrauch_pro_tag=4.002970297029708`, `monat_kosten=55.764344125412585`
      - März 2024: `grundpreis_anteil=5.45`, `arbeitspreis=34.57`, `verbrauch_pro_tag=4.002970297029708`, `monat_kosten=48.34863178217827`
   - und die Monatskosten sind jeweils nachvollziehbar aus `grundpreis_anteil + (arbeitspreis/100 * verbrauch_pro_tag * tage_im_monat)` ableitbar.
   - **Status:** PASS.

3) **WW-Verhältnis statt fixer Faktor (BE1)**
   - Given `WW_NE1=32.56`, `WW_NE2=25.389999999999986`, `WW_total=57.94999999999999`, `WW_cost_total=858.8160953278683`,
   - when verteilt wird,
   - then `NE1=482.5375679702399`, `NE2=376.2785273576285` und der Faktor wird als `factor(2024)=2453.449999999999/4987=0.491969119711249` nur **jahresdynamisch abgeleitet**.
   - **Status:** PASS.

4) **Rechenprotokoll Allgemein-Warmwasser**
   - Given ein erzeugter Prüfbericht/JSON,
   - when Position „Allgemein - Warmwasser“ geprüft wird,
   - then enthält der Nachweis `ww_m3_ne`, `ww_total_be1`, `share_ne`, `total_ww_cost_be1`, `cost_ne` mit Quellenreferenzen.
   - **Status:** PASS für JSON-Auditdaten; PENDING für finalen PDF-Prüfbericht.

5) **Lernende Belegklassifikation mit Review-Loop**
   - Given ein Beleg (z. B. `20251116_144617.jpg`) und trainierte Zuordnung,
   - when Klassifikation läuft,
   - then wird `predicted_category` + `confidence` erzeugt; bei niedriger Confidence entsteht ein manueller Review-Posten.
   - **Status:** PASS für Baseline-Classifier; PENDING für produktiven Trainingsstand.

6) **E2E Ergebnis-Orakel bleibt stabil**
   - Given OCR+Tarif+Klassifikationspipeline mit 2024-Daten,
   - when Endlauf durchgeführt wird,
   - then bleiben Endwerte konsistent:
      - NE1 Summe `4250.010438061518`, Nachzahlung `1750.0104380615176`
      - NE2 Summe `3558.2017735022396`, Nachzahlung `798.2017735022396`
      - NE3 Summe `1688.74665610264`, Nachzahlung `188.74665610263992`
      - NE4 Summe `1265.700879470499`, Guthaben `24.299120529500897`.
   - **Status:** PASS für fixture-/workbook-basierte Regression; PENDING für echte End-to-End-Verarbeitung nur aus OCR-normalisierten Eingaben.

7) **run-folder Workflow**
   - Given lokale 2024-Fixtures im Repo,
   - when `python3 -m nebenkosten_pipeline.cli run-folder --jahr 2024 --belege-dir <.../Belege_Nebenkostenabrechnung_2024> --workbook <.../Nebenkostenabrechnung_2024.xlsx>` ausgeführt wird,
   - then entstehen:
     - `{belege_dir}/../_pipeline_runs/2024/run.db`
     - `{belege_dir}/../_pipeline_runs/2024/ocr_snapshot_2024.json`
     - `{belege_dir}/../Einzelabrechnungen/{Mieter}/einzelabrechnung_2024.json`
   - **Status:** PASS.

8) **Ausstehender Zieltest: echte End-to-End-PDF-Ausgabe**
   - Given lokale ista-PDFs + Ableseprotokoll-Bild + Belege-Bilder,
   - when Pipeline ohne workbook-gestützte Zwischenstütze läuft,
   - then entstehen pro Mieter nachvollziehbare PDF-Einzelabrechnung + PDF-Prüfbericht im Zielordner.
   - **Status:** PENDING.

# Iteration 6
 
 ## Summary
 - Source-Code-Review zeigt die aktuell noch fehlenden Architekturstücke klar:
   - `pipeline.py` ruft weiterhin direkt den workbook-basierten Pfad auf,
   - `ingest.py` persistiert bisher nur Preview-/Regex-Kandidaten statt kanonischer Fachobjekte,
   - `output_writer.py` schreibt statisch vier JSON-Ausgaben und bildet weder `Einzelabrechnung_1.2` noch dynamische Parteien-/Leerstandsabrechnungen ab.
 - Workbook-Review 2024 liefert zusätzliche fachliche Anforderungen, die im Plan bisher noch nicht präzise genug festgezogen waren:
   - NE1 wird in zwei Abrechnungsparteien aufgeteilt (`Kraft/Hühne` mit `304` Tagen und `Leerstand` mit `61` Tagen),
   - `Hecht`/NE5 wirkt als Verbrauchs- und Verteilschlüsselteilnehmer, erhält aber keine eigene `Einzelabrechnung_*`,
   - Meter-IDs treten quellenübergreifend mit Aliasen/Inkonsistenzen auf (`2008222190 ↔ 200822219`, `2108757522 ↔ 210875752`, `21082168 ↔ 21087968`).
 - Diese Iteration zieht daraus einen verbindlichen Zielzustand für Datenmodell, Persistenz, Reconciliation, Parteienlogik und PDF-Rendering.
 - Unter den in dieser Iteration festgelegten technischen Defaults ist der Plan jetzt **umsetzungsfähig**; weitere Nutzerentscheidungen sind dafür nicht erforderlich.
 
 ## Requirements Snapshot
 - Ziel-Workflow bleibt:
   - Dokumente in einen lokalen Jahresordner legen,
   - Pipeline für `jahr=YYYY` ausführen,
   - pro abrechnungsrelevanter Partei nachvollziehbare Einzelabrechnung + Prüfbericht unter `{Belegordner}/../Einzelabrechnungen/{Partei}` erzeugen.
 - Das Workbook bleibt Referenz-/Migrationsorakel, aber **nicht** mehr produktive Laufzeit-Abhängigkeit des Rechenkerns.
 - Produktive Eingaben werden in einen expliziten Kanon überführt:
   - statische Stammdaten,
   - jahresbezogene Miet-/Leerstandsintervalle,
   - Tarifperioden,
   - OCR-normalisierte Beobachtungen,
   - manuell bestätigte Review-Entscheidungen.
 - Das System muss abrechnungsrelevante Parteien unterscheiden können:
   - `tenant` (Mieterabrechnung),
   - `vacancy` (Leerstand / interne Abrechnung),
   - `owner_internal` (fließt in Verteilung ein, erhält aber keine Mieterausgabe),
   - `excluded` (nur technischer Hilfskontext, keine Ausgabe).
 - Für 2024 sind mindestens folgende Parteien/Outputs fachlich relevant:
   - `Kraft/Hühne` (NE1, Zeitraum `01.01.2024-31.10.2024`),
   - `Leerstand` (NE1, Zeitraum `01.11.2024-31.12.2024`),
   - `Schäfer` (NE2, `01.01.2024-31.12.2024`),
   - `König` (NE3, `01.01.2024-31.12.2024`),
   - `Waldheim` (NE4, `01.01.2024-31.12.2024`),
   - `Hecht` (NE5) nimmt an Verteilungsbasen teil, erhält aber keine finale Mieterausgabe.
 
 ## Detailed Plan
 1) Verbindliches Ziel-Dateisystem und Persistenzmodell festziehen
    - Produktiver Root bleibt `{Belegordner}/..`.
    - Eingaben:
      - `{root}/_inputs/master_data.yaml`
      - `{root}/_inputs/tenancies_{jahr}.yaml`
      - `{root}/_inputs/tariffs_{jahr}.yaml`
      - `{root}/_inputs/review_overrides_{jahr}.yaml` (nur bestätigte Korrekturen/Alias-Overrides)
    - Laufartefakte:
      - `{root}/_pipeline_runs/{jahr}/run.db`
      - `{root}/_pipeline_runs/{jahr}/canonical_snapshot.json`
      - `{root}/_pipeline_runs/{jahr}/review_queue.json`
      - `{root}/_pipeline_runs/{jahr}/delta_report.json`
    - Ausgaben:
      - `{root}/Einzelabrechnungen/{party_slug}/einzelabrechnung_{jahr}.pdf`
      - `{root}/Einzelabrechnungen/{party_slug}/pruefbericht_{jahr}.pdf`
      - optional zusätzlich `einzelabrechnung_{jahr}.json` als Debug-Artefakt.
    - Festlegung: `run.db` ist die persistente technische Wahrheit des Laufs; PDFs/JSON sind abgeleitete Ausgaben.
 
 2) Kanonisches Domänenmodell einführen und bestehende Module darauf umbauen
    - `models.py` wird erweitert um mindestens:
      - `SourceDocument`
      - `DocumentPage`
      - `Observation`
      - `CanonicalMeter`
      - `MeterAlias`
      - `BillingParty`
      - `OccupancyInterval`
      - `ReceiptDocument`
      - `ReceiptLine`
      - `CostEntry`
      - `AllocationLine`
      - `ReviewItem`
      - `StatementBundle`
    - `PipelineResult` wird von einer reinen Summenstruktur zu einem Bündel aus:
      - Status,
      - canonical snapshot refs,
      - review items,
      - allocations,
      - output files,
      - summary totals.
    - Bestehende workbook-spezifische Datentypen (`MonthlyCost`, `WwDistribution`) bleiben als Rechenkern-/Audit-Objekte nutzbar, werden aber aus kanonischen Eingaben gespeist statt direkt aus Excel.
 
 3) Stammdaten- und Jahresdaten als echte Source-of-Truth definieren
    - `master_data.yaml` enthält:
      - Objekt-/Adressdaten,
      - Berechnungseinheiten,
      - Nutzeinheiten,
      - Kostenarten und Verteilschlüssel aus `Stammdaten`,
      - Messgeräte-/Meterregister inkl. erwarteter Einheit und Aliasliste,
      - Kennzeichen, ob eine Partei gerendert werden soll.
    - `tenancies_{jahr}.yaml` enthält:
      - `party_name`,
      - `unit_id`,
      - `from`,
      - `to`,
      - `party_type`,
      - `monthly_advance_eur`,
      - `render_statement: true|false`.
    - `tariffs_{jahr}.yaml` enthält die bereits in Iteration 5 definierten Tarifperioden.
    - Workbook-Daten aus `Allgemein`, `Messgeräte`, `Stammdaten` und `Einzelabrechnung_*` werden einmalig in diese Struktur überführt; danach dient Excel nur noch als Oracle/Regression.
 
 4) Dokumenterkennung und Dokumentgruppierung vor OCR-Normalisierung ergänzen
    - Neue Vorstufe `document_types.py` oder äquivalent:
      - klassifiziert in `ista_annual`, `ista_monthly`, `reading_protocol`, `receipt`, `unknown`.
    - Mehrseitige JPEG-Belege werden zu einem fachlichen Dokument gruppiert über:
      - OCR-Rechnungsnummer,
      - Lieferant,
      - Rechnungsdatum,
      - Dateinamen-/Zeitstempel-Nähe.
    - Konkreter 2024-Fall:
      - `20251116_144607.jpg` + `20251116_144617.jpg` bilden gemeinsam Rechnung `20240502`.
    - Exit-Kriterium:
      - ein fachliches `ReceiptDocument` kann aus mehreren Bilddateien bestehen.
 
 5) OCR-Normalisierung von Preview-Kandidaten zu kanonischen Beobachtungen erweitern
    - `ingest.py` wird in zwei logische Stufen getrennt:
      - Rohtext-/OCR-Erfassung,
      - fachliche Normalisierung.
    - Jede Observation enthält mindestens:
      - `observation_id`,
      - `document_id`,
      - `page_no`,
      - `obs_type`,
      - `raw_value`,
      - `normalized_value`,
      - `unit`,
      - `observed_at`,
      - `meter_candidate`,
      - `confidence`,
      - `source_snippet`.
    - Zusätzliche Observation-Typen neben `meter/date/amount`:
      - `reading_start`,
      - `reading_end`,
      - `inventory_quantity`,
      - `invoice_number`,
      - `supplier_name`,
      - `cost_category_hint`.
    - Ziel: `ocr_snapshot_{jahr}.json` ist nicht mehr nur Preview-Liste, sondern vollständiger fachlicher Rohsnapshot.
 
 6) Meter-Reconciliation mit Alias- und Konfliktlogik festziehen
    - Matching-Reihenfolge:
      1. exakte Übereinstimmung mit `CanonicalMeter.external_id`
      2. Treffer auf expliziten `MeterAlias`
      3. fuzzy-Kandidat über `unit + meter_type + numeric_suffix/prefix`
      4. sonst `conflict` oder `missing`.
    - Beispiele aus 2024:
      - `2008222190` (Stammdaten) und `200822219` (ista/Messwerte) müssen via Alias auf denselben Warmwasserzähler NE2 zeigen.
      - `2108757522` und `210875752` analog für Kaltwasser NE2.
      - `21082168` vs. `21087968` (NE4 Warmwasser) darf **nicht** stillschweigend gemappt werden; hier muss ein `ReviewItem(kind='meter_conflict')` entstehen.
    - Exit-Kriterium:
      - Kein stilles Durchrutschen inkonsistenter Zählernummern in den Rechenkern.
 
 7) Parteien-/Intervalllogik als eigenen Rechenkern-Baustein modellieren
    - Neue Ableitung `billing_parties.py` oder äquivalent erzeugt aus `tenancies_{jahr}.yaml`:
      - abrechnungsfähige Parteien,
      - zugehörige Nutzeinheiten,
      - Anteilszeiträume,
      - Vorauszahlungen,
      - Renderziel.
    - Zeitanteilige Verteilung gilt für alle tagebasierten Schlüsselpositionen.
    - Konkreter 2024-Sollfall:
      - NE1 wird in zwei Parteien gesplittet:
        - `Kraft/Hühne`: `304/365` Tage,
        - `Leerstand`: `61/365` Tage.
      - Diese Split-Logik gilt für `Wohnfläche`-/`Personen`-basierte Positionen und für die in den Einzelabrechnungen ausgewiesenen tageanteiligen Zeilen.
    - `Hecht`/NE5 wird als `owner_internal` modelliert:
      - nimmt an Verbrauchs-/Verteilschlüsseln teil,
      - erhält aber keinen finalen Mieterausgabebund.
 
 8) Rechenkern in fachliche Teilstufen zerlegen
    - `pricing.py` bleibt für Tarifperiodisierung zuständig, erhält aber Eingaben aus kanonischen Tariff- und Verbrauchsobjekten.
    - Neuer Baustein `consumption_engine.py` oder äquivalent:
      - bildet Verbrauch je Meter und Intervall,
      - unterstützt Monats- und Jahresista-Dokumente,
      - verrechnet Leerstands-/Nutzerwechselintervalle.
    - Neuer Baustein `allocation_engine.py` oder äquivalent:
      - verarbeitet Kostenarten aus Belegen,
      - berechnet tageanteilige, flächenbezogene, personenbezogene und verbrauchsbezogene Umlagen,
      - bildet Summen-, Vorauszahlungs- und Differenzzeilen je Partei.
    - `ww.py` bleibt Spezialbaustein für BE1-Warmwasser:
      - WW-Kostenverteilung erfolgt über `ww_m3_ne / ww_total_be1`,
      - `factor(year)` bleibt reine Audit-/Reportinggröße.
 
 9) Belegverarbeitung end-to-end präzisieren
    - Receipt-Pipeline:
      - OCR -> Dokumentgruppierung -> ReceiptHeader/ReceiptLines -> Kostenartvorschlag -> Match auf Betriebskostenzeile.
    - Matching nutzt:
      - Lieferant/Absender,
      - Rechnungsdatum,
      - Bruttobetrag,
      - Rechnungsnummer,
      - Textanker (`SERVICERECHNUNG`, `Wartung`, `Grundsteuer`, `Müll`, etc.).
    - Baseline-Classifier bleibt erhalten, wird aber nur als Vorschlagsgeber verwendet; finaler CostEntry entsteht erst nach:
      - sicherem Match oder
      - bestätigtem Review-Override.
    - Konkreter 2024-Sollfall:
      - Rechnung `20240502` (`Haustechnik Albinger`) wird auf `Betriebskosten` Zeile `Wartung Heizung / Heiznebenkosten / 338.46` gemappt.
 
 10) Prüfbericht und Einzelabrechnung als echte Zielartefakte festlegen
    - Technische Festlegung: PDF-Rendering mit Python + `reportlab` (lokal, deterministisch, ohne zusätzliche Systemdienste).
    - `einzelabrechnung_{jahr}.pdf` enthält:
      - Kopf-/Objektdaten,
      - Partei/Zeitraum,
      - Kostenarten mit Formel-/Anteilsdarstellung,
      - Vorauszahlungen,
      - Nachzahlung/Guthaben.
    - `pruefbericht_{jahr}.pdf` enthält:
      - Quellenreferenzen,
      - OCR-/Canonical-/Allocation-Herkunft je Zeile,
      - Rechenformeln,
      - offene Review-Flags,
      - ggf. Delta gegen Oracle-Workbook.
    - `output_writer.py` wird durch dynamisches Rendering aus `BillingParty` ersetzt; harte `NE1..NE4`-Mappings entfallen.
 
 11) Workbook-Nutzung auf Migration und Regression begrenzen
    - `excel_loader.py` bleibt für:
      - Fixture-Import,
      - Sollwert-Extraktion,
      - Delta-Bericht gegen 2024-Oracle.
    - Produktiver Lauf `run-folder` darf ohne Workbook ausführbar sein, sobald:
      - `_inputs/*.yaml` vorhanden,
      - Review-Queue abgearbeitet oder leer ist.
    - Bis dahin bleibt `--workbook` nur als Übergangspfad/Oracle erlaubt, nicht als Endzustand.
 
 12) TDD-Reihenfolge für die Umsetzung festziehen
    - Testreihenfolge:
      1. BillingParty-/Intervallmodell,
      2. Meter-Alias- und Konflikterkennung,
      3. Dokumentgruppierung für mehrseitige Belege,
      4. Receipt-Matching auf CostEntry,
      5. kanonischer Rechenkern ohne Workbook,
      6. PDF-Rendering und Auditreport,
      7. vollständiger `run-folder`-E2E-Lauf ohne Workbook.
    - Definition of Done:
      - alle unten stehenden Verifikationstests grün,
      - `run-folder` funktioniert mit Ordner + `_inputs` ohne Excel-Laufzeitabhängigkeit,
      - Zielausgabe sind PDFs plus technische Audit-Artefakte.
 
 ## Open Items
 - Keine blockierenden Nutzerentscheidungen oder Informationslücken in dieser Iteration.
 - Für die Umsetzung sind folgende Defaults festgezogen:
   - Laufzeit-Persistenz: SQLite `run.db` + JSON-Snapshots,
   - PDF-Engine: `reportlab`,
   - produktive Basisdaten: `_inputs/*.yaml`,
   - Workbook nur noch als Oracle-/Migrationsquelle,
   - Standard für lernende Belegzuordnung: `confidence_threshold = 0.90`, darunter verpflichtender Review-Eintrag.
 
 ## Verification Test Cases
 1) **BillingParty-Menge 2024**
    - Given `master_data`, `tenancies_2024` und die 2024er Oracle-Daten,
    - when die BillingParty-Ableitung läuft,
    - then entstehen genau folgende ausgaberelevanten Parteien:
      - `Kraft/Hühne` (NE1, `01.01.2024-31.10.2024`),
      - `Leerstand` (NE1, `01.11.2024-31.12.2024`),
      - `Schäfer` (NE2),
      - `König` (NE3),
      - `Waldheim` (NE4),
    - und `Hecht`/NE5 wird als `owner_internal` geführt, aber **ohne** finale Mieterausgabe.
 
 2) **Tageanteilige NE1-Splittung auf Wohnflächenposition**
    - Given `Brennstoffkosten (30%) = 883.449 €`, BE1-Wohnflächenanteil NE1 `0.6923076923076923`, `304` Tage für `Kraft/Hühne` und `61` Tage für `Leerstand`,
    - when die tageanteilige Verteilung berechnet wird,
    - then entstehen exakt:
      - `Kraft/Hühne = 509.4028375131719 €`,
      - `Leerstand = 102.21570094836673 €`.
 
 3) **Tageanteilige NE1-Splittung auf Grundsteuer**
    - Given `Grundsteuer = 1342.12 €`, Liegenschaftsanteil NE1 `0.27522935779816515`, `304/61` Tage,
    - when verteilt wird,
    - then entstehen exakt:
      - `Kraft/Hühne = 307.6570164634913 €`,
      - `Leerstand = 61.73380922458213 €`.
 
 4) **Alias-Mapping Warm-/Kaltwasser NE2**
    - Given Stammdaten-Zähler `2008222190` und `2108757522`,
    - and OCR-/ista-Werte `200822219` mit `135.98/110.59` sowie `210875752` mit `94.81/71.98`,
    - when Reconciliation läuft,
    - then werden beide OCR-Zähler via Alias eindeutig NE2 zugeordnet und mit `status in ('exact','alias')` in den Rechenkern übernommen.
 
 5) **Konfliktfall NE4-Warmwasser wird nicht automatisch verschluckt**
    - Given Stammdaten-Zähler `21082168` und Messwert-/Oracle-Zähler `21087968`,
    - when Reconciliation läuft,
    - then entsteht ein `ReviewItem` vom Typ `meter_conflict` statt einer stillen automatischen Zuordnung.
 
 6) **Ableseprotokoll erzeugt Inventarbeobachtungen**
    - Given `protocol_ocr_try.json` mit Preview-Texten `Holz 40 m` und `Pellets 1500 kg`,
    - when Protokoll-OCR normalisiert wird,
    - then entstehen kanonische `inventory_quantity`-Observations mit Einheiten `m` und `kg` und Quellenreferenz auf das Protokolldokument.
 
 7) **Mehrseitiger Albinger-Beleg wird zu einem ReceiptDocument zusammengeführt**
    - Given `20251116_144607.jpg` mit `RECHNUNG - Nr.: 20240502` und `09.12.2024`,
    - and `20251116_144617.jpg` mit derselben Rechnungsnummer, Leistungsfortsetzung und `Gesamt-Betrag 338,46`,
    - when Dokumentgruppierung + Receipt-Normalisierung laufen,
    - then entsteht genau ein `ReceiptDocument(invoice_number='20240502', invoice_date='09.12.2024', gross_amount=338.46, supplier='Haustechnik Albinger')`.
 
 8) **Receipt-Matching auf Betriebskostenzeile Heiznebenkosten**
    - Given das ReceiptDocument `20240502` aus Testfall 7,
    - when CostEntry-Matching ausgeführt wird,
    - then entsteht ein Kostenposten:
      - `booking_date = 09.12.2024`
      - `usage_scope = Berechnungseinheit 1`
      - `cost_type = Heiznebenkosten`
      - `description = Wartung Heizung`
      - `amount = 338.46`
    - und dieser entspricht der 2024er `Betriebskosten`-Zeile.
 
 9) **run-folder Zielausgabe ohne Workbook-Abhängigkeit**
    - Given ein Jahresordner mit Belegen/PDFs/Bildern plus `_inputs/master_data.yaml`, `tenancies_2024.yaml`, `tariffs_2024.yaml`,
    - when `python3 -m nebenkosten_pipeline.cli run-folder --jahr 2024 --belege-dir <...>` ausgeführt wird,
    - then werden ohne Excel-Laufzeitpfad erzeugt:
      - `run.db`
      - `canonical_snapshot.json`
      - `review_queue.json`
      - fünf `einzelabrechnung_2024.pdf`
      - fünf `pruefbericht_2024.pdf`.
 
 10) **E2E-Orakel 2024 inklusive Leerstand**
    - Given vollständig reconciliierte 2024-Eingaben,
    - when der Endlauf ausgeführt wird,
    - then stimmen die Zielergebnisse mit dem Oracle überein:
      - `Kraft/Hühne`: Summe `4250.010438061518`, Nachzahlung `1750.0104380615176`
      - `Leerstand`: Summe `902.2339475336394`, Differenz `-902.2339475336394`
      - `Schäfer`: Summe `3558.2017735022396`, Nachzahlung `798.2017735022396`
      - `König`: Summe `1688.74665610264`, Nachzahlung `188.74665610263992`
      - `Waldheim`: Summe `1265.700879470499`, Guthaben `24.299120529500897`.
 
 11) **Prüfbericht enthält vollständige Herkunftskette**
    - Given eine erzeugte Warmwasser- oder Heiznebenkostenzeile im Prüfbericht,
    - when diese Zeile geprüft wird,
    - then sind mindestens sichtbar:
      - `source_document`
      - `ocr/raw value`
      - `canonical value`
      - `allocation formula`
      - `party`
      - `final amount`
      - optional `oracle_delta`.
 
# Iteration 7
 
 ## Summary
 - Die in der letzten Review identifizierten Restlücken wurden geschlossen:
   - formale Verträge für `_inputs/*.yaml`, `canonical_snapshot.json` und `run.db`,
   - verbindliche State-Machine für `review_queue` und `review_overrides`,
   - explizite Umlageregel-Matrix für `Kostenart × Scope × Verteilschlüssel × Parteienart`.
 - Zusätzlich wurden die Regeln für globale/unscharf gescopte Kostenpositionen präzisiert:
   - Kosten mit fehlendem Scope werden **nicht** stillschweigend verteilt, wenn die Kostenart scope-sensitiv ist, sondern erzeugen einen Review-Eintrag.
 - Die Rolle von `owner_internal` wurde jetzt fachlich eindeutig gemacht:
   - zählt in Nenner und Verbrauchsbasis mit,
   - erhält aber keine Mieter-Ausgabe.
 - Mit den Festlegungen dieser Iteration ist der Plan jetzt **implementation-ready**.
 
 ## Requirements Snapshot
 - Ein produktiver Lauf besteht aus drei Schichten:
   - `_inputs/*.yaml` als manuell gepflegte, versionierte Basisdaten,
   - OCR-/Normalisierungsartefakte als technische Zwischenschicht,
   - Rechen- und PDF-Ausgaben als finale, prüfbare Ergebnisse.
 - Ein Lauf darf nur dann finale Einzelabrechnungen/PDF-Prüfberichte erzeugen, wenn **keine blocking Review-Items** offen sind.
 - Alle Artefakte müssen schema-versioniert und deterministisch reproduzierbar sein.
 - Kostenverteilung nutzt immer zwei getrennte Fragen:
   - **Wer zählt im Nenner mit?**
   - **Für wen wird eine Ausgabe gerendert?**
 - `tenant`, `vacancy` und `owner_internal` zählen grundsätzlich im Nenner mit; nur `tenant` und `vacancy` werden standardmäßig gerendert.
 
 ## Detailed Plan
 1) Formale Verträge für `_inputs/*.yaml` festziehen
    - `master_data.yaml` Pflichtstruktur:
      - `schema_version`
      - `property`: `property_id`, `name`, `address`
      - `calculation_units[]`: `calculation_unit_id`, `label`, `energy_type`
      - `units[]`: `unit_id`, `calculation_unit_id`, `label`, `living_area_m2`, `usage_area_m2`, `persons_default`, `render_default`
      - `meters[]`: `canonical_meter_id`, `unit_id|null`, `meter_type`, `unit`, `external_id`, `aliases[]`, `scope_type`
      - `cost_types[]`: `cost_type_id`, `label`, `allocation_key`, `is_heating_cost`, `requires_scope`
    - `tenancies_{jahr}.yaml` Pflichtstruktur:
      - `schema_version`
      - `year`
      - `parties[]`: `party_id`, `party_name`, `party_slug`, `party_type`, `unit_id`, `from`, `to`, `monthly_advance_eur`, `render_statement`
    - `tariffs_{jahr}.yaml` Pflichtstruktur:
      - `schema_version`
      - `year`
      - `tariff_periods[]`: `tariff_id`, `scope_type`, `scope_id`, `valid_from`, `valid_to`, `supplier`, `tariff_name`, `arbeitspreis_ct_kwh`, `grundpreis_eur_year`
    - `review_overrides_{jahr}.yaml` Pflichtstruktur:
      - `schema_version`
      - `year`
      - `overrides[]`: `review_item_id`, `source_fingerprint`, `action`, `payload`, `comment`
 
 2) `canonical_snapshot.json` als verbindlichen technischen Vertrag definieren
    - Top-Level Felder:
      - `schema_version`
      - `run_context`
      - `documents`
      - `billing_parties`
      - `meters`
      - `observations`
      - `receipts`
      - `cost_entries`
      - `allocation_lines`
      - `review_items`
      - `outputs`
    - Jeder Datensatz besitzt eine deterministische ID und einen `source_fingerprint`.
    - Pflicht in `run_context`:
      - `year`, `input_root`, `started_at`, `code_version`, `oracle_mode`, `status`
    - `canonical_snapshot.json` ist der serialisierte Rechenstand; alle PDF-/JSON-Ausgaben müssen daraus alleine rekonstruierbar sein.
 
 3) `run.db` als relationale Ausprägung der Snapshot-Struktur festziehen
    - Minimale Tabellen:
      - `pipeline_runs(run_id, year, status, input_root, code_version, started_at, finished_at)`
      - `source_documents(document_id, path, kind, file_hash, page_count, ocr_engine, grouped_document_id)`
      - `observations(observation_id, document_id, page_no, obs_type, raw_value, normalized_value, unit, observed_at, meter_candidate, confidence, source_snippet, source_fingerprint)`
      - `canonical_meters(canonical_meter_id, unit_id, meter_type, unit, external_id, aliases_json)`
      - `billing_parties(party_id, party_name, party_slug, party_type, unit_id, from_date, to_date, monthly_advance_eur, render_statement)`
      - `receipt_documents(receipt_id, grouped_document_id, supplier, invoice_number, invoice_date, gross_amount, confidence, source_fingerprint)`
      - `cost_entries(cost_entry_id, cost_type_id, scope_type, scope_id, booking_date, description, amount_eur, source_ref, source_fingerprint)`
      - `allocation_lines(allocation_line_id, cost_entry_id, party_id, denominator_group, formula_code, share_value, amount_eur, rendered)`
      - `review_items(review_item_id, kind, severity, status, target_type, target_id, reason, suggested_payload_json, source_fingerprint)`
      - `output_files(output_id, party_id, output_type, path, file_hash)`
    - `run.db` und `canonical_snapshot.json` müssen inhaltlich äquivalent sein; `run.db` dient Abfrage/Audit, JSON dem Snapshot/Replay.
 
 4) Review-State-Machine als verbindliches Laufverhalten definieren
    - `review_items.status`:
      - `open`
      - `confirmed`
      - `overridden`
      - `dismissed`
      - `stale`
    - `review_items.severity`:
      - `blocking`
      - `non_blocking`
    - Blocking-Typen:
      - `meter_conflict`
      - `missing_required_reading`
      - `scope_missing`
      - `tariff_gap`
      - `stale_override`
      - `receipt_unmatched_required`
    - Laufstatus:
      - `ok`: keine offenen `blocking`-Items
      - `needs_review`: mindestens ein offenes `blocking`-Item
      - `blocked`: Basisinput oder Schema ungültig
      - `error`: technischer Fehler
    - Rendering-Regel:
      - Bei `ok`: finale PDFs + JSON + Auditdateien im Zielpfad
      - Bei `needs_review`: `run.db`, `canonical_snapshot.json`, `review_queue.json`, `delta_report.json`; **keine** finalen Mieter-PDFs
      - Bei `blocked/error`: nur Fehler-/Diagnoseartefakte
 
 5) Replay- und Override-Semantik festziehen
    - `review_overrides_{jahr}.yaml` wird vor Reconciliation/Allocation eingelesen.
    - Jedes Override referenziert exakt ein `review_item_id` plus `source_fingerprint`.
    - Wenn `review_item_id` existiert, aber der `source_fingerprint` nicht mehr passt:
      - Override wird **nicht** angewendet,
      - stattdessen neues `review_item(kind='stale_override', severity='blocking')`.
    - Erlaubte `action`-Werte:
      - `alias_meter`
      - `set_scope`
      - `set_cost_type`
      - `confirm_receipt_match`
      - `dismiss_false_positive`
    - Ziel: Review-Entscheidungen sind deterministisch replaybar und brechen sauber, wenn sich die Inputlage verändert.
 
 6) Verbindliche Umlageregel-Matrix definieren
    - Nenner-Inklusion:
      - `tenant`, `vacancy`, `owner_internal` zählen mit
      - `excluded` zählt nie mit
    - Render-Inklusion:
      - `tenant`, `vacancy` werden gerendert
      - `owner_internal` nur im Audit, nicht als Mieter-Ausgabe
    - Regeltabelle:
 
      | Kostenart | Scope-Auflösung | Nenner | Zeitanteil | Formel |
      | --- | --- | --- | --- | --- |
      | `Brennstoffkosten` | `Berechnungseinheit` Pflicht, sonst `scope_missing` | alle Parteien in BE | nur 30%-Grundkosten zeitanteilig | `0.30 * wohnflaeche_share * tage_share + 0.70 * heizverbrauch_share` |
      | `Heiznebenkosten` | `Berechnungseinheit` oder `Nutzeinheit` Pflicht, sonst `scope_missing` | alle Parteien im Scope | nein, sofern Verbrauchsintervall bereits periodisiert ist | `heizverbrauch_share` |
      | `Gebäudeversicherung` | `Nutzeinheit` > `Berechnungseinheit` > `global` | alle Parteien im Scope | ja | `wohnflaeche_share * tage_share` |
      | `Grundsteuer` | standardmäßig `global` | alle Parteien objektweit | ja | `wohnflaeche_share * tage_share` |
      | `Müllabfuhr` | standardmäßig `global` | alle Parteien objektweit | ja | `personen_share * tage_share` |
      | `Kalt- und Abwasser` | standardmäßig `global` | alle Parteien mit KW-Verbrauch im Objekt | nein | `kw_verbrauch_share` |
      | `Oberfächenwasser` | standardmäßig `global` | alle Parteien objektweit | ja | `wohnflaeche_share * tage_share` |
      | `Strom` | direkt über Zähler-/Tarifpfad, nicht aus Belegpauschale | Parteien am Zähler/Scope | gemäß Messintervall | `tariff_engine(consumption_interval)` |
      | `Verbrauchskosten Warmwasser` | abgeleitet aus Allgemein-WW-Strom in BE1 | Parteien mit WW-Verbrauch in BE1 | nein | `ww_m3_share_in_be1` |
    - Zusätzliche Scope-Regel:
      - Fehlt bei `Brennstoffkosten` oder `Heiznebenkosten` ein eindeutiger Scope, ist **kein** stiller `global`-Fallback zulässig.
 
 7) Ambige 2024-Belege explizit in den Review-Pfad nehmen
    - Konkrete 2024-Fälle:
      - `Wartungsrechnung ista` (`171.8`)
      - `Servicerechnung ista` (`376.66`)
    - Da im Workbook keine Berechnungseinheit/Nutzeinheit gesetzt ist, erzeugen diese Posten bei Import zunächst `scope_missing`.
    - Erst ein bestätigtes Override (`set_scope` oder `dismiss_false_positive`) darf daraus einen finalen `cost_entry` machen.
 
 8) CLI-/Run-Vertrag auf finalen Zielzustand schärfen
    - Produktiver Aufruf:
      - `python3 -m nebenkosten_pipeline.cli run-folder --jahr <YYYY> --belege-dir <Pfad>`
    - Optional nur für Oracle-/Migration:
      - `--workbook <xlsx>`
    - Exit-Verhalten:
      - `0` bei `ok`
      - `2` bei `needs_review`
      - `3` bei `blocked`
      - `1` bei technischem `error`
    - Idempotenz-Regel:
      - identische Inputs + identische Overrides => identische `canonical_snapshot.json` und identische finale PDFs/Hashes.
 
 9) Definition of Done auf Artefakt- und Schemaebene ergänzen
    - Done ist eine Iteration/Implementierung erst dann, wenn:
      - `_inputs/*.yaml` gegen die spezifizierten Verträge validiert werden,
      - `run-folder` ohne Workbook durchläuft,
      - `needs_review` sauber von `ok` getrennt wird,
      - die Regelmatrix in Tests und Code sichtbar ist,
      - 2024 inklusive Leerstand und Override-Replay grün ist.
 
 ## Open Items
 - Keine blockierenden offenen Punkte in dieser Iteration.
 - Keine zusätzlichen Nutzerentscheidungen erforderlich.
 - Der Plan ist mit dieser Iteration implementation-ready.
 
 ## Verification Test Cases
 1) **Schema-Validation `_inputs/master_data.yaml`**
    - Given ein `master_data.yaml` ohne `meters[].meter_type`,
    - when der Lauf startet,
    - then Status = `blocked` und der Fehler verweist konkret auf das fehlende Pflichtfeld.
 
 2) **Review-Blocking verhindert finale PDFs**
    - Given mindestens ein offenes `review_item(severity='blocking', kind='meter_conflict')`,
    - when `run-folder` ausgeführt wird,
    - then Status = `needs_review`, `review_queue.json` wird erzeugt und es entstehen **keine** finalen `einzelabrechnung_{jahr}.pdf`.
 
 3) **Override-Replay mit passendem Fingerprint**
    - Given ein `review_item_id` für `2008222190 ↔ 200822219`,
    - and `review_overrides_2024.yaml` mit `action='alias_meter'` und passendem `source_fingerprint`,
    - when der Lauf erneut ausgeführt wird,
    - then wird der Alias angewendet, das Review-Item ist nicht mehr offen und die Observation fließt in die Berechnung ein.
 
 4) **Stale Override blockiert sauber**
    - Given ein Override auf ein altes `source_fingerprint`,
    - when sich der zugrunde liegende OCR-Snapshot geändert hat,
    - then entsteht ein neues `review_item(kind='stale_override', severity='blocking')` statt einer stillen Fehlzuordnung.
 
 5) **Owner-internal zählt im globalen Wohnflächen-Nenner mit**
    - Given `Grundsteuer = 1342.12 €` und Gesamtwohnfläche `654 m²` inklusive `Hecht/NE5 = 300 m²`,
    - when global nach Wohnfläche verteilt wird,
    - then basiert der Nenner auf `654` und `Kraft/Hühne` erhält exakt `307.6570164634913 €` statt eines Werts mit reduziertem Nenner.
 
 6) **Scope-sensitive Heiznebenkosten ohne Scope erzeugen Review**
    - Given 2024-Betriebskostenzeile `Servicerechnung ista / Heiznebenkosten / 376.66` ohne BE/NE,
    - when CostEntry-Normalisierung läuft,
    - then wird **kein** finaler CostEntry verteilt, sondern ein `review_item(kind='scope_missing', severity='blocking')` erzeugt.
 
 7) **Brennstoffkosten trennen Grund- und Verbrauchsanteil korrekt**
    - Given `Brennstoffkosten` in BE1 mit Jahressumme `2944.83 €`, Grundkostenanteil `30%`, Verbrauchsanteil `70%`,
    - when auf `Kraft/Hühne` und `Leerstand` verteilt wird,
    - then wird der Grundkostenanteil tageanteilig (`304/61`) und der Verbrauchsanteil ausschließlich über `heizverbrauch_share` verteilt.
 
 8) **run-folder ist ohne Workbook deterministisch reproduzierbar**
    - Given identische Dokumente, identische `_inputs/*.yaml` und identische `review_overrides_2024.yaml`,
    - when `run-folder` zweimal ausgeführt wird,
    - then sind `canonical_snapshot.json` und die erzeugten PDF-Dateihashes identisch.
 
 9) **Laufstatus/Exit-Code-Mapping**
    - Given ein Lauf mit offenem blocking Review-Item,
    - when CLI beendet wird,
    - then Prozess-Exit-Code = `2` und `PipelineResult.status = 'needs_review'`.
 
 10) **2024 E2E mit bestätigten Overrides**
    - Given 2024-Dokumente, `_inputs/*.yaml` und alle für 2024 nötigen bestätigten Overrides,
    - when `run-folder` ohne Workbook ausgeführt wird,
    - then stimmen die finalen Ergebnisse mit dem Oracle überein:
      - `Kraft/Hühne`: `4250.010438061518 / 1750.0104380615176`
      - `Leerstand`: `902.2339475336394 / -902.2339475336394`
      - `Schäfer`: `3558.2017735022396 / 798.2017735022396`
      - `König`: `1688.74665610264 / 188.74665610263992`
      - `Waldheim`: `1265.700879470499 / 24.299120529500897`.
 
# Iteration 8

## Summary
- Die beiden in der Review zu Iteration 7 identifizierten Blocker wurden geschlossen:
  - `Bereits gezahlt` wird nicht mehr implizit aus `monthly_advance_eur` hergeleitet, sondern aus einem expliziten Zahlungsinput.
  - Die personenbasierte Umlage wird nicht mehr aus `party_type` oder bloßen Unit-Defaults erraten, sondern aus expliziten umlagerelevanten Basiswerten pro Partei und Zeitraum.
- Daraus folgen zwei neue produktive Input-Verträge:
  - `_inputs/payments_{jahr}.yaml`
  - `_inputs/allocation_bases_{jahr}.yaml`
- Die 2024er Orakelwerte lassen sich damit ohne implizite Heuristik erklären:
  - `Kraft/Hühne = 2500`
  - `Leerstand = 0`
  - `Schäfer = 2760`
  - `König = 1500`
  - `Waldheim = 1290`
  - Personenbasis objektweit = `2 + 2 + 1 + 1 + 4 = 10` wäre **falsch**; maßgeblich für 2024 ist die explizite Parteienbasis `2 + 1 + 1 + 1 + 4 = 9`, wobei `Leerstand` für NE1 im Müllschlüssel **2** Personen trägt und `Schäfer` **1** Person.
- Mit dieser Iteration ist der Plan wieder **implementation-ready**.

## Requirements Snapshot
- `monthly_advance_eur` ist nur eine erwartete Sollgröße bzw. Vertrags-/Plausibilitätsinformation, **nicht** die Quelle für `Bereits gezahlt`.
- `Bereits gezahlt` in der Einzelabrechnung ist immer:
  - `sum(payment_events.amount_eur)` der abrechnungsrelevanten Partei im Zeitraum.
- Nicht-verbrauchsbasierte Umlagegrundlagen sind eigenständige fachliche Inputs:
  - z. B. `persons_count`, `living_area_m2`, `usage_area_m2`.
- `vacancy` bedeutet **nicht automatisch** `0` Personen oder `0` Basiswerte:
  - die Basiswerte ergeben sich aus dem expliziten Allocation-Base-Vertrag.
- Für personenbasierte Umlagen ist die Autorität nicht `Allgemein`, sondern der aufgelöste Basisresolver aus `_inputs/allocation_bases_{jahr}.yaml` plus Fallback-Regeln.

## Detailed Plan
1) Zahlungsinput als First-Class Contract ergänzen
   - Neue Pflichtdatei für finale Läufe:
     - `{root}/_inputs/payments_{jahr}.yaml`
   - Struktur:
     - `schema_version`
     - `year`
     - `payment_events[]`
   - `payment_events[]` Pflichtfelder:
     - `payment_id`
     - `party_id`
     - `booking_date`
     - `amount_eur`
     - `kind` (`advance`, `refund`, `adjustment`)
     - `source_ref`
   - Semantik:
     - positive Beträge erhöhen `Bereits gezahlt`
     - negative Beträge (z. B. Rücklastschrift/Korrektur) reduzieren `Bereits gezahlt`
   - `monthly_advance_eur` bleibt in `tenancies_{jahr}.yaml`, wird aber nur für Plausibilitäts- und Erwartungschecks genutzt.

2) Zahlungsaggregation und Statement-Regel explizit machen
   - Rechenregel:
     - `bereits_gezahlt_eur = sum(payment_events.amount_eur where party_id matches statement party and booking_date in billing period)`
   - Daraus abgeleitete Prüfregel:
     - `expected_advance_eur = monthly_advance_eur * configured_expected_periods`
     - wenn `abs(expected_advance_eur - bereits_gezahlt_eur)` oberhalb konfigurierter Toleranz liegt, entsteht `review_item(kind='payment_delta_unexpected', severity='non_blocking')`
   - Finale Einzelabrechnung verwendet ausschließlich `bereits_gezahlt_eur`, nie die Erwartungsgröße.

3) Zahlungsdaten in Snapshot und SQLite aufnehmen
   - `canonical_snapshot.json` wird erweitert um:
     - `payment_events`
     - `payment_totals_by_party`
   - `run.db` erhält zusätzliche Tabellen:
     - `payment_events(payment_id, party_id, booking_date, amount_eur, kind, source_ref, source_fingerprint)`
     - `payment_totals(party_id, paid_total_eur, expected_total_eur, delta_eur)`
   - `PipelineResult`/StatementBundle weist aus:
     - `bereits_gezahlt_eur`
     - `expected_advance_eur`
     - `payment_delta_eur`

4) Allgemeine Allocation-Base-Verträge definieren
   - Neue produktive Datei:
     - `{root}/_inputs/allocation_bases_{jahr}.yaml`
   - Struktur:
     - `schema_version`
     - `year`
     - `bases[]`
   - `bases[]` Pflichtfelder:
     - `basis_id`
     - `party_id`
     - `basis_type` (`persons`, `living_area`, `usage_area`)
     - `from`
     - `to`
     - `value`
     - `source_ref`
   - Ziel:
     - alle nicht-verbrauchsbasierten Schlüsselwerte pro Partei/Zeitraum explizit machen, statt sie implizit aus Altblättern oder `party_type` abzuleiten.

5) Autoritätsregel für Umlagebasen festziehen
   - Basisauflösung in dieser Reihenfolge:
     1. exakte Periode aus `allocation_bases_{jahr}.yaml`
     2. default Basiswert am `party`-Eintrag in `tenancies_{jahr}.yaml` (optional, nur als Fallback)
     3. statischer Unit-Default aus `master_data.yaml`
     4. sonst `review_item(kind='allocation_base_missing', severity='blocking')`
   - Wenn mehrere Quellen für dieselbe Partei/Periode/Basis kollidieren:
     - `review_item(kind='allocation_base_conflict', severity='blocking')`
   - Wichtig:
     - `vacancy` bekommt **keinen** automatischen Nullwert.
     - Für 2024 ist explizit zulässig und erforderlich:
       - `Kraft/Hühne persons = 2`
       - `Leerstand persons = 2`
       - `Schäfer persons = 1`
       - `König persons = 1`
       - `Waldheim persons = 1`
       - `Hecht persons = 4`

6) Regelmatrix für `Personen` und `Bereits gezahlt` erweitern
   - Ergänzende Matrix:

     | Zielgröße | Autorität | Formel | Blocking-Fall |
     | --- | --- | --- | --- |
     | `Bereits gezahlt` | `payments_{jahr}.yaml` | `sum(payment_events.amount_eur)` | `payments_missing` |
     | `Personen` | `allocation_bases_{jahr}.yaml` > `tenancies` > `master_data` | `sum(persons value in denominator group)` | `allocation_base_missing` / `allocation_base_conflict` |

   - Für `Müllabfuhr` gilt damit explizit:
     - `personen_share = resolved_persons_party / sum(resolved_persons_denominator_group)`
     - `amount = gesamtkosten * personen_share * tage_share`
   - Für 2024 ergibt das:
     - `Kraft/Hühne`: `401.28 * (2/9) * (304/365) = 74.27039269406391`
     - `Leerstand`: `401.28 * (2/9) * (61/365) = 14.902940639269405`
     - `Schäfer`: `401.28 * (1/9) = 44.58666666666666`

7) Review-State-Machine um Zahlungs-/Basisfehler erweitern
   - Neue blocking Review-Typen:
     - `payments_missing`
     - `allocation_base_missing`
     - `allocation_base_conflict`
   - Neue non-blocking Review-Typen:
     - `payment_delta_unexpected`
   - Finale PDFs dürfen nur erzeugt werden, wenn:
     - keine blocking Payment-/Allocation-Review-Items offen sind.

8) Override-Payloads vollständig konkretisieren
   - `set_scope`:
     - `payload = { "scope_type": "property|calculation_unit|unit", "scope_id": "..." }`
   - `set_cost_type`:
     - `payload = { "cost_type_id": "..." }`
   - `alias_meter`:
     - `payload = { "canonical_meter_id": "...", "alias_value": "..." }`
   - `confirm_receipt_match`:
     - `payload = { "receipt_id": "...", "target_cost_entry_id": "..." }`
   - `dismiss_false_positive`:
     - `payload = { "reason_code": "..." }`
   - Payload-Validierung ist Pflicht vor Override-Anwendung.

9) 2024-Referenzinput für Zahlungs- und Personenbasis festhalten
   - Für das erste Oracle-Referenzjahr 2024 werden folgende explizite Zielwerte versioniert:
     - `payments_2024.yaml` Summen:
       - `Kraft/Hühne = 2500`
       - `Leerstand = 0`
       - `Schäfer = 2760`
       - `König = 1500`
       - `Waldheim = 1290`
     - `allocation_bases_2024.yaml` für `basis_type=persons`:
       - `Kraft/Hühne = 2`
       - `Leerstand = 2`
       - `Schäfer = 1`
       - `König = 1`
       - `Waldheim = 1`
       - `Hecht = 4`
   - Diese Werte sind Teil des Golden Datasets und werden regression-getestet.

10) Definition of Done um Zahlungs- und Basisreproduktion ergänzen
   - Done erst, wenn zusätzlich gilt:
     - `Bereits gezahlt` kommt vollständig aus `payments_{jahr}.yaml`
     - `Müllabfuhr`/andere personenbasierte Positionen kommen vollständig aus dem Basisresolver
     - 2024er Orakelwerte für `Bereits gezahlt` und `Müllabfuhr` ohne Workbook-Nachschlagen reproduziert werden.

## Open Items
- Keine blockierenden offenen Punkte in dieser Iteration.
- Keine weiteren Nutzerentscheidungen erforderlich.
- Der Plan ist mit dieser Iteration implementation-ready.

## Verification Test Cases
1) **Schema-Validation `payments_{jahr}.yaml`**
   - Given ein `payments_2024.yaml` mit Event ohne `amount_eur`,
   - when der Lauf startet,
   - then Status = `blocked` mit Feldfehler auf `payment_events[].amount_eur`.

2) **`Bereits gezahlt` wird nicht aus Monatsvorauszahlung abgeleitet**
   - Given `monthly_advance_eur=268` für `Schäfer`,
   - and `payments_2024.yaml` summiert für `Schäfer` auf `2760`,
   - when die Einzelabrechnung erzeugt wird,
   - then `Bereits gezahlt = 2760` und **nicht** ein aus `268` hergeleiteter Wert.

3) **Leerstand hat 0 Zahlungen, aber nicht automatisch 0 Personen**
   - Given `payments_2024.yaml` für `Leerstand = 0`,
   - and `allocation_bases_2024.yaml` für `Leerstand persons = 2`,
   - when `Bereits gezahlt` und `Müllabfuhr` berechnet werden,
   - then gilt:
     - `Bereits gezahlt = 0`
     - `Müllabfuhr = 14.902940639269405`.

4) **Personenbasis überschreibt widersprüchliche Altquelle**
   - Given `Allgemein` enthält für NE2 `2` Personen,
   - and `allocation_bases_2024.yaml` enthält für Partei `Schäfer` `persons = 1`,
   - when die personenbasierte Umlage berechnet wird,
   - then wird `1` verwendet und `Müllabfuhr = 44.58666666666666`.

5) **Fehlende Personenbasis blockiert**
   - Given eine Partei mit `Müllabfuhr`-relevantem Zeitraum ohne auflösbare `persons`-Basis,
   - when der Lauf die globale Personenverteilung aufbauen will,
   - then entsteht `review_item(kind='allocation_base_missing', severity='blocking')` und der Laufstatus ist `needs_review`.

6) **Kollidierende Personenbasen blockieren**
   - Given zwei unterschiedliche `persons`-Werte für dieselbe Partei und denselben Zeitraum,
   - when der Basisresolver läuft,
   - then entsteht `review_item(kind='allocation_base_conflict', severity='blocking')`.

7) **Zahlungsdelta ist nur Plausibilitätswarnung**
   - Given `monthly_advance_eur=250` und erwartete 10 Zahlungen, aber `payments_2024.yaml` summiert auf `2550`,
   - when die Abrechnung erstellt wird,
   - then wird `Bereits gezahlt = 2550` verwendet und zusätzlich `review_item(kind='payment_delta_unexpected', severity='non_blocking')` erzeugt.

8) **Override-Payload-Validation**
   - Given ein Override `set_scope` ohne `scope_id`,
   - when Overrides eingelesen werden,
   - then Status = `blocked` mit Validierungsfehler auf dem Override-Payload.

9) **2024 Oracle für Zahlungen + Personenbasis**
   - Given 2024-Dokumente plus `_inputs/payments_2024.yaml` und `_inputs/allocation_bases_2024.yaml`,
   - when `run-folder` ohne Workbook ausgeführt wird,
   - then stimmen zusätzlich zu den Endsummen mindestens folgende Orakelwerte:
     - `Bereits gezahlt Kraft/Hühne = 2500`
     - `Bereits gezahlt Leerstand = 0`
     - `Bereits gezahlt Schäfer = 2760`
     - `Bereits gezahlt König = 1500`
     - `Bereits gezahlt Waldheim = 1290`
     - `Müllabfuhr Kraft/Hühne = 74.27039269406391`
     - `Müllabfuhr Leerstand = 14.902940639269405`
     - `Müllabfuhr Schäfer = 44.58666666666666`.

# Iteration 9

## Summary
- Nutzerentscheidung zu Leerstand wurde fachlich verbindlich gemacht und supersediert die widersprüchlichen Leerstands-Annahmen aus Iteration 8:
  - Leerstand hat **0 Personen**.
  - Leerstand zahlt **nichts**.
  - nicht umlagefähige Leerstandskosten werden als **Vermieter-Abschreibung** erfasst.
  - Müllkosten des Leerstands werden **nicht** dem Leerstand zugeordnet, sondern auf die übrigen Personen der Liegenschaft verteilt.
- Dadurch wird der Sonderfall `vacancy` nicht mehr wie eine normale abrechenbare Partei behandelt.
- Zusätzlich wurde die Zahlungs-Completeness präzisiert, damit `0` Zahlungen nicht mit „Zahlungen fehlen“ verwechselt werden.
- Mit diesen Präzisierungen ist der Plan **implementation-ready**.

## Requirements Snapshot
- `vacancy` ist fachlich eine **nicht abrechenbare interne Phase**, keine Mieterpartei.
- Für `vacancy` gilt:
  - `Bereits gezahlt = 0`
  - `persons = 0`
  - keine Einzelabrechnung im Mieterordner
  - stattdessen interne Vermieter-Abschreibung/Audit-Ausgabe
- Personenbasierte Umlagen wie `Müllabfuhr` verwenden nur die **tatsächlich belegten Personen** der übrigen Parteien im Nenner.
- Zahlungsdaten müssen explizit zwischen
  - `complete with zero`
  - und `missing/incomplete`
  unterscheiden können.

## Detailed Plan
1) `vacancy`-Chargeability als feste Geschäftsregel definieren
   - `party_type = vacancy` erhält zusätzliche feste Semantik:
     - `billable_to_tenant = false`
     - `render_tenant_statement = false`
     - `owner_writeoff_enabled = true`
   - Alle dem Leerstand zugeordneten Kosten werden je Kostenart geprüft:
     - personenbasierte Kosten: nicht dem Leerstand zuordnen, sondern über Nenner ohne Leerstand verteilen
     - alle übrigen umlagefähigen Leerstandskosten: als `owner_writeoff_line` verbuchen

2) Zahlungsvertrag um explizite Completeness erweitern
   - `payments_{jahr}.yaml` erhält zusätzlich zu `payment_events[]`:
     - `party_payment_totals[]`
   - `party_payment_totals[]` Pflichtfelder:
     - `party_id`
     - `paid_total_eur`
     - `coverage_status` (`complete`, `none_expected`)
     - `source_ref`
   - Regeln:
     - `vacancy` wird mit `paid_total_eur = 0` und `coverage_status = none_expected` geführt
     - fehlt ein Eintrag in `party_payment_totals[]` für eine abrechnungsrelevante Partei, entsteht `payments_missing`
     - `payment_events[]` müssen zu `party_payment_totals[]` konsistent sein; Abweichungen erzeugen `payment_delta_unexpected`

3) Personenbasis für `persons` ohne Alt-Fallback festziehen
   - Die bisherige Fallback-Kette aus Iteration 8 wird für `basis_type = persons` ersetzt:
     1. feste Geschäftsregel `vacancy -> 0`
     2. explizite Partei-/Intervallbasis aus `allocation_bases_{jahr}.yaml`
     3. sonst `review_item(kind='allocation_base_missing', severity='blocking')`
   - Für `persons` gibt es **keinen** Fallback mehr auf `tenancies` oder `master_data`.
   - Für andere Basisarten (`living_area`, `usage_area`) kann der Fallback aus Iteration 8 bestehen bleiben.

4) Mülllogik explizit als Sonderregel dokumentieren
   - Für `Müllabfuhr` gilt:
     - Nennergruppe = alle nicht-vacancy Parteien mit `resolved_persons > 0`
     - `vacancy` trägt keinen Anteil und erhält keine Abschreibungslinie für Müll
   - Formel:
     - `amount_party = total_muell * (persons_party / sum(persons_non_vacancy)) * tage_share_party`
   - 2024-Sollwerte:
     - `Kraft/Hühne = 401.28 * (2/9) * (304/365) = 74.27039269406391`
     - `Schäfer = 401.28 * (1/9) = 44.58666666666666`
     - `König = 401.28 * (1/9) = 44.58666666666666`
     - `Waldheim = 401.28 * (1/9) = 44.58666666666666`
     - `Hecht(owner_internal) = 401.28 * (4/9) = 178.34666666666666`
     - `Leerstand = 0`

5) Vermieter-Abschreibung als eigenes Ergebnisobjekt modellieren
   - Neue Entitäten/Artefakte:
     - `owner_writeoff_lines`
     - `owner_writeoff_summary`
   - Ausgabeort:
     - `{root}/_pipeline_runs/{jahr}/owner_writeoffs/{scope_slug}.json`
     - optional zusätzlich `{root}/_pipeline_runs/{jahr}/owner_writeoffs/{scope_slug}.pdf`
   - Für 2024 Leerstand NE1 sind mindestens folgende Kosten als Vermieter-Abschreibung zu erfassen:
     - Brennstoffkosten Grundkostenanteil
     - Brennstoffkosten Verbrauchsanteil
     - Heiznebenkosten
     - Gebäudeversicherung
     - Grundsteuer
     - Oberflächenwasser
     - Strom
   - 2024-Sollsumme Vermieter-Abschreibung Leerstand NE1:
     - `887.33100689437`

6) Output-Vertrag an Zielverhalten anpassen
   - Finale Mieter-Ausgaben:
     - nur für `tenant`
   - Finale interne Audit-/Owner-Ausgaben:
     - für `vacancy`
     - für `owner_internal` optional nur aggregiert im Prüf-/Auditkontext
   - Damit ergibt sich für 2024 im Zielzustand:
     - `4` tenant `einzelabrechnung_{jahr}.pdf`
     - `4` tenant `pruefbericht_{jahr}.pdf`
     - `1` interner Owner-Writeoff-Report für Leerstand NE1

7) Oracle-Strategie zwischen Legacy-Workbook und Zielverhalten trennen
   - Das manuelle 2024-Workbook bleibt Legacy-Oracle für:
     - Messwerte
     - Tariflogik
     - die meisten Kostenpositionen
   - Für Leerstand/Müll/Zahlbarkeit gilt ab Iteration 9:
     - **Zielverhalten hat Vorrang vor Legacy-Workbook**
   - Delta-Bericht muss diese absichtliche Abweichung explizit markieren:
     - `delta_reason = target_rule_override`

## Open Items
- Keine blockierenden offenen Punkte in dieser Iteration.
- Keine weiteren Nutzerentscheidungen erforderlich.
- Der Plan ist mit dieser Iteration implementation-ready.

## Verification Test Cases
1) **Explizite Null-Zahlung für Leerstand**
   - Given `payments_2024.yaml` mit `party_payment_totals[Leerstand] = { paid_total_eur: 0, coverage_status: none_expected }`,
   - when der Lauf startet,
   - then entsteht **kein** `payments_missing` für `Leerstand`.

2) **Fehlende Payment-Completeness blockiert**
   - Given eine tenant-Partei ohne Eintrag in `party_payment_totals[]`,
   - when die Zahlungsaggregation läuft,
   - then entsteht `review_item(kind='payments_missing', severity='blocking')`.

3) **Leerstand hat fest 0 Personen**
   - Given Partei `Leerstand` im Zeitraum `01.11.2024-31.12.2024`,
   - when der Persons-Resolver läuft,
   - then `resolved_persons = 0` unabhängig von Altwerten aus Excel/Legacy-Quellen.

4) **Müll wird ohne Leerstand im Nenner verteilt**
   - Given `Müllabfuhr = 401.28 €` und Personenbasis `Kraft/Hühne=2, Schäfer=1, König=1, Waldheim=1, Hecht=4, Leerstand=0`,
   - when die Verteilung läuft,
   - then `Leerstand = 0` und die übrigen Parteien erhalten Anteile auf Basis des Nenners `9`.

5) **Leerstand erzeugt keine Mieter-Einzelabrechnung**
   - Given ein vollständiger 2024-Lauf ohne offene blocking Reviews,
   - when Outputs gerendert werden,
   - then existiert **keine** Datei unter `{root}/Einzelabrechnungen/Leerstand/`, aber ein interner Owner-Writeoff-Report für NE1.

6) **Vermieter-Abschreibung Leerstand 2024**
   - Given 2024-Daten und Zielregel aus Iteration 9,
   - when Leerstandskosten aggregiert werden,
   - then `owner_writeoff_summary(NE1 vacancy) = 887.33100689437`.

7) **Target-Rule-Override gegen Legacy-Workbook wird explizit ausgewiesen**
   - Given das Legacy-Workbook enthält `Müllabfuhr Leerstand = 14.902940639269405`,
   - when der Delta-Bericht erzeugt wird,
   - then wird diese Abweichung als `target_rule_override` dokumentiert und nicht als Berechnungsfehler.

8) **2024 Zielausgabeanzahl**
   - Given vollständige 2024-Eingaben und bestätigte Overrides,
   - when `run-folder` erfolgreich endet,
   - then entstehen:
     - `4` tenant Einzelabrechnungen,
     - `4` tenant Prüfberichte,
     - `1` Owner-Writeoff-Report,
   - und keine tenant-Ausgabe für `Leerstand`.

# Iteration 10

## Summary
- Review-Ergebnis vor dieser Verfeinerung:
  - Der fachliche Zielzustand aus Iteration 9 ist konsistent,
  - aber die Teststrategie war noch nicht sauber genug von älteren Legacy-Orakeln getrennt.
- Diese Iteration führt deshalb ein explizites **Dual-Orakel-Modell** ein:
  - **Legacy Oracle** für unveränderte Altlogik/Regression gegen das 2024-Workbook
  - **Target Rule Oracle** für bewusst geändertes Zielverhalten ab Iteration 9
- Damit wird verhindert, dass korrekte Zielimplementierungen fälschlich gegen das manuelle Excel „durchfallen“, obwohl die Abweichung fachlich beabsichtigt ist.
- Alle supersedierten Leerstands-/Müll-Testfälle aus älteren Iterationen gelten nur noch als Legacy-Referenz, nicht mehr als finaler Zieltest.

## Requirements Snapshot
- Das 2024-Workbook ist ab jetzt **kein monolithisches End-Orakel** mehr.
- Jede Verifikation muss einem von drei Typen zugeordnet sein:
  - `legacy_oracle`
  - `target_rule_oracle`
  - `invariant_oracle`
- `legacy_oracle` prüft nur Bereiche, in denen das Zielverhalten weiterhin dem Workbook entsprechen soll.
- `target_rule_oracle` prüft bewusst dokumentierte Abweichungen vom Workbook.
- `invariant_oracle` prüft allgemeine Systemregeln unabhängig von Excel oder Zielabweichung:
  - Schema-Validierung
  - Idempotenz
  - Exit-Codes
  - Review-State-Machine

## Detailed Plan
1) Verifikationsfälle verpflichtend klassifizieren
   - Jeder Testfall und jeder Delta-Berichtseintrag erhält:
     - `oracle_type`
     - `oracle_source`
     - `oracle_scope`
   - Erlaubte Werte:
     - `oracle_type in {legacy_oracle, target_rule_oracle, invariant_oracle}`
   - Beispiele:
     - Tarifperiodisierung Jan/Feb/März 2024 -> `legacy_oracle`
     - Leerstand zahlt nichts -> `target_rule_oracle`
     - `needs_review` erzeugt keine PDFs -> `invariant_oracle`

2) Legacy-Oracle explizit begrenzen
   - `legacy_oracle` darf nur für folgende Bereiche als maßgeblich gelten:
     - Messwert-/Verbrauchsorakel
     - Tariforakel
     - Warmwasserorakel BE1
     - unveränderte Kostenverteilungen ohne Zielregel-Override
     - Summen/Nachzahlungen für tenant-Parteien, sofern nicht von einer neueren Zielregel betroffen
   - `legacy_oracle` ist **nicht** maßgeblich für:
     - Chargeability von `vacancy`
     - Müllverteilung mit `vacancy = 0 Personen`
     - Owner-Writeoff-Summen
     - tenant-Ausgabeanzahl bei Wegfall der Leerstandsabrechnung

3) Target-Rule-Oracle als first-class Testquelle definieren
   - Neue Quelle:
     - `{root}/_inputs/target_rules_{jahr}.yaml`
   - Struktur:
     - `schema_version`
     - `year`
     - `rules[]`
   - `rules[]` Pflichtfelder:
     - `rule_id`
     - `rule_type`
     - `scope`
     - `expected_effect`
     - `supersedes_legacy_fields[]`
     - `source_ref`
   - Für 2024 mindestens:
     - `vacancy_chargeability_ne1_2024`
     - `muell_without_vacancy_2024`
     - `owner_writeoff_ne1_2024`

4) Supersedierte Legacy-Felder formal markieren
   - Delta-/Oracle-Layer erhält neue Markierung:
     - `legacy_status in {active, superseded_by_target_rule}`
   - Für 2024 sind mindestens folgende Legacy-Felder supersediert:
     - `Einzelabrechnung_1.2 -> Bereits gezahlt`
     - `Einzelabrechnung_1.2 -> Müllabfuhr`
     - `Einzelabrechnung_1.2 -> Summe/Differenz`
     - `run-folder` erwartete Ausgabemenge `5 tenant statements`
   - Diese Felder dürfen in der Endabnahme **nicht** mehr als Fehler gegen die Zielimplementierung gewertet werden.

5) Delta-Bericht auf Orakelkonflikte erweitern
   - Jeder Delta-Eintrag enthält zusätzlich:
     - `oracle_type`
     - `legacy_value`
     - `target_value`
     - `effective_expected_value`
     - `delta_reason`
   - Erlaubte `delta_reason`:
     - `target_rule_override`
     - `legacy_regression`
     - `input_data_issue`
     - `implementation_bug`
   - Regel:
     - Wenn `oracle_type = target_rule_oracle`, ist eine Abweichung vom Workbook **kein Fehler**, sondern erwartbar.

6) Test-Suite in drei Gruppen aufteilen
   - `tests/legacy_oracles/...`
   - `tests/target_rules/...`
   - `tests/invariants/...`
   - Ziel:
     - Legacy-Regression bleibt erhalten,
     - Zielabweichungen sind explizit und lokalisiert,
     - Review/CI kann sofort erkennen, ob ein Fail aus Altlogik, Zielregel oder Invariante stammt.

7) Iteration 9 Leerstandsfälle als Target-Rule-Tests präzisieren
   - Folgende Fälle werden ausdrücklich als `target_rule_oracle` geführt:
     - Leerstand hat `0` Personen
     - Leerstand zahlt `0`
     - Müll wird ohne Leerstand im Nenner verteilt
     - kein tenant-Output für Leerstand
     - Owner-Writeoff NE1 = `887.33100689437`
   - Die dazu widersprüchlichen Excel-Zellen bleiben dokumentierte Legacy-Referenzen, aber keine finalen Sollwerte.

8) Tenant-Endergebnisse gegenüber Legacy differenzieren
   - Tenant-Endsummen, die von supersedierten Leerstandsregeln beeinflusst werden, müssen entweder:
     - neu als `target_rule_oracle` ausgewiesen werden, oder
     - als `hybrid_oracle` verboten werden, indem der Fall in einzelne Linienorakel zerlegt wird.
   - Festlegung:
     - Keine gemischten E2E-Sollwerte, die teils aus Legacy und teils aus Target-Regeln stammen, ohne explizite Zerlegung.

9) Definition of Done für Orakelstrategie ergänzen
   - Done erst, wenn zusätzlich gilt:
     - jeder Testfall ist einem Orakeltyp zugeordnet,
     - supersedierte Legacy-Felder sind explizit markiert,
     - es gibt keinen End-to-End-Test mehr, der Leerstand gleichzeitig gegen Workbook **und** gegen Zielregel validieren will.

## Open Items
- Keine blockierenden offenen Punkte in dieser Iteration.
- Keine weiteren Nutzerentscheidungen erforderlich.
- Der Plan ist mit dieser Iteration implementation-ready.

## Verification Test Cases
1) **Legacy-Orakel bleibt für Tariflogik aktiv**
   - Given `Stromkosten` Januar/Februar/März 2024 aus dem Workbook,
   - when die Tariftests laufen,
   - then ist `oracle_type = legacy_oracle` und die bekannten Sollwerte bleiben unverändert maßgeblich.

2) **Leerstand-Müll ist Target-Rule-Orakel**
   - Given das Workbook enthält `Müllabfuhr Leerstand = 14.902940639269405`,
   - and `target_rules_2024.yaml` definiert `vacancy persons = 0`,
   - when der Zieltest läuft,
   - then ist `oracle_type = target_rule_oracle` und der effektive Sollwert für Leerstand-Müll ist `0`.

3) **Supersediertes Legacy-Feld erzeugt keinen Testfehler**
   - Given ein Delta zwischen Workbook-`Einzelabrechnung_1.2` und Zielimplementierung,
   - when das Feld in `supersedes_legacy_fields[]` der Zielregel aufgeführt ist,
   - then wird das Delta als `target_rule_override` markiert und nicht als `implementation_bug`.

4) **Output-Anzahl wird gegen Target Rule statt Workbook geprüft**
   - Given das Workbook impliziert indirekt 5 Abrechnungsparteien inkl. Leerstand,
   - when der finale Output validiert wird,
   - then ist `oracle_type = target_rule_oracle` und der Sollwert lautet `4 tenant statements + 1 owner writeoff report`.

5) **Kein gemischtes E2E-Orakel**
   - Given ein End-to-End-Testfall 2024,
   - when Sollwerte aus Legacy und Target Rules kombiniert würden,
   - then muss der Test in getrennte Legacy-/Target-Assertions zerlegt werden; ein gemischter E2E-Sollwert ist unzulässig.

6) **Delta-Bericht weist Orakeltyp aus**
   - Given eine beabsichtigte Zielabweichung beim Leerstand,
   - when `delta_report.json` erzeugt wird,
   - then enthält der Eintrag mindestens `oracle_type=target_rule_oracle`, `legacy_value`, `effective_expected_value` und `delta_reason=target_rule_override`.

# Iteration 11

## Summary
- Nutzerentscheidung aus der letzten Review wurde fachlich verbindlich gemacht:
  - Leerstand soll – analog zur ista-Logik – **eine eigene Abrechnung erhalten**,
  - aber **nicht** als Mieterabrechnung, sondern als **interne Leerstandsabrechnung**.
- Damit wird der bisherige Output-Konflikt zwischen Iteration 9/10 und älteren Iterationen aufgelöst:
  - Zielzustand 2024 ist **nicht** `4 tenant statements + 1 separater owner writeoff report`,
  - sondern `4 tenant statements + 1 vacancy_internal statement`, wobei die Vermieter-Abschreibung in dieser Leerstandsabrechnung ausgewiesen wird.
- Der technische Artefakttyp `owner_writeoff_summary` bleibt für Audit/JSON bestehen, ist aber nicht mehr das primäre fachliche Enddokument.
- Zusätzlich wurde der formale Dokumentationsfehler an `# Iteration 6` behoben, damit die Iterationsnavigation wieder konsistent ist.
- Für das Layout wird in dieser Iteration ein verbindlicher Template-Vertrag festgelegt; die konkrete visuelle Ausgestaltung erfolgt während der Implementierung des Reporting-Bausteins.

## Requirements Snapshot
- `vacancy` bleibt fachlich:
  - `persons = 0`
  - `billable_to_tenant = false`
  - `payments_expected = false`
- `vacancy` erhält jedoch:
  - `render_statement = true`
  - `statement_kind = vacancy_internal`
- Die finale Ausgabe unterscheidet damit drei Parteitypen:
  - `tenant` -> externe Mieterabrechnung
  - `vacancy_internal` -> interne Leerstandsabrechnung für Eigentümer/Vermieter
  - `owner_internal` -> nur Nenner-/Audit-Teilnehmer, keine eigene Parteiausgabe
- Für 2024 sind renderbare Parteien damit:
  - `Kraft/Hühne`
  - `Leerstand`
  - `Schäfer`
  - `König`
  - `Waldheim`
- `Hecht` bleibt `owner_internal` ohne eigene Einzelabrechnung.

## Detailed Plan
1) Leerstand als renderbare interne Partei präzisieren
   - `BillingParty.party_type` bleibt fachlich von der Abrechnungsart getrennt:
     - `tenant`
     - `vacancy`
     - `owner_internal`
   - Zusätzlich wird `statement_kind` eingeführt:
     - `tenant`
     - `vacancy_internal`
     - `none`
   - Regeln:
     - `tenant -> statement_kind = tenant`
     - `vacancy -> statement_kind = vacancy_internal`
     - `owner_internal -> statement_kind = none`
   - `vacancy_internal` bedeutet:
     - PDF/Prüfbericht wird erzeugt,
     - keine Zahlungsaufforderung an einen Mieter,
     - als Eigentümer-/Leerstandsphase gekennzeichnet,
     - Vermieter-Abschreibung wird darin explizit ausgewiesen.

2) Output-Vertrag auf fünf Parteibündel harmonisieren
   - Primäre PDF-Ausgaben werden je renderbarer Partei erzeugt unter:
     - `{root}/Einzelabrechnungen/{party_slug}/einzelabrechnung_{jahr}.pdf`
     - `{root}/Einzelabrechnungen/{party_slug}/pruefbericht_{jahr}.pdf`
   - Für 2024 gilt damit im Zielzustand:
     - `4` tenant `einzelabrechnung_{jahr}.pdf`
     - `1` vacancy_internal `einzelabrechnung_{jahr}.pdf`
     - `4` tenant `pruefbericht_{jahr}.pdf`
     - `1` vacancy_internal `pruefbericht_{jahr}.pdf`
   - `owner_writeoff_summary` und `owner_writeoff_lines` bleiben zusätzlich als technische Audit-Artefakte unter `_pipeline_runs/{jahr}/...` zulässig, sind aber nicht das primäre Endformat.

3) Template-Vertrag jetzt festlegen, visuelle Ausarbeitung in der Implementierung
   - Es wird **kein** separater Vorab-Arbeitsschritt für ein manuell designtes PDF-Template benötigt.
   - Stattdessen wird jetzt ein verbindlicher inhaltlicher Template-Vertrag festgelegt, der während der Implementierung in `reportlab` umgesetzt wird.
   - Gemeinsame Pflichtsektionen für `statement_template_v1`:
     - Überschrift/Objektdaten
     - Partei und Abrechnungszeitraum
     - Kostenzeilen mit Umlageformel und Anteilsbasis
     - Summenblock
     - Zahlungs-/Saldoblock
     - Quellen-/Prüfhinweise
   - Varianten:
     - `tenant`:
       - Überschrift `Nebenkostenabrechnung`
       - Block `Bereits gezahlt`
       - Ergebnis `Nachzahlung` oder `Guthaben`
     - `vacancy_internal`:
       - Überschrift `Interne Leerstandsabrechnung`
       - `Bereits gezahlt = 0`
       - Ergebnisblock `Vom Vermieter zu tragen / Abschreibung`
       - keine Formulierung als Forderung an einen Mieter
   - Umsetzungsvorgabe:
     - Der erste Reporting-Implementierungsschritt erstellt diesen Template-Vertrag als renderbare Baseline,
     - anschließend werden Fixture-basierte Regressionstests auf Struktur und numerische Inhalte ergänzt.

4) Orakel- und Delta-Strategie an interne Leerstandsabrechnung anpassen
   - Aus Iteration 10 bleiben gültig:
     - `legacy_oracle`
     - `target_rule_oracle`
     - `invariant_oracle`
   - Neu bzw. supersediert wird:
     - `kein tenant-Output für Leerstand` bleibt richtig,
     - aber `kein Output für Leerstand` ist **nicht** mehr Zielzustand.
   - Supersedierte Zielaussagen aus älteren Iterationen:
     - `4 tenant statements + 1 owner writeoff report` als primäre Endausgabe
   - Neuer Zielzustand:
     - `4 tenant statements + 1 vacancy_internal statement`
   - Delta-/Oracle-Layer muss deshalb unterscheiden zwischen:
     - Parteityp (`vacancy` ist kein tenant)
     - Renderbarkeit (`vacancy_internal` wird gerendert)
     - Zahlungswirksamkeit (`billable_to_tenant = false`)

## Open Items
- Keine blockierenden offenen Punkte in dieser Iteration.
- Keine weiteren Nutzerentscheidungen erforderlich.
- Der Plan ist mit dieser Iteration implementation-ready.

## Verification Test Cases
1) **Renderbare Parteien 2024 sind fachlich korrekt klassifiziert**
   - Given `tenancies_2024.yaml`, `allocation_bases_2024.yaml` und die Zielregeln,
   - when die BillingParty-Ableitung läuft,
   - then entstehen genau:
     - `4` Parteien mit `statement_kind = tenant`
     - `1` Partei (`Leerstand`) mit `statement_kind = vacancy_internal`
     - `1` Partei (`Hecht`) mit `statement_kind = none`.

2) **Leerstand erzeugt interne Abrechnung statt Mieterabrechnung**
   - Given ein vollständiger 2024-Lauf ohne offene blocking Reviews,
   - when die Outputs gerendert werden,
   - then existiert unter `{root}/Einzelabrechnungen/Leerstand/`:
     - `einzelabrechnung_2024.pdf`
     - `pruefbericht_2024.pdf`
   - und die Abrechnung ist als `Interne Leerstandsabrechnung` gekennzeichnet, nicht als Mieterabrechnung.

3) **Leerstandsabrechnung weist Vermieteranteil statt Zahlungsforderung aus**
   - Given die 2024-Zielregeln für Leerstand,
   - when die Leerstandsabrechnung NE1 gerendert wird,
   - then gilt:
     - `Bereits gezahlt = 0`
     - keine `Nachzahlung` an einen Mieter
     - ausgewiesener Block `Vom Vermieter zu tragen / Abschreibung`
     - Summenwert mindestens für den Ziel-Fall `887.33100689437`.

4) **Output-Anzahl 2024 ist fünf Parteibündel**
   - Given vollständige 2024-Eingaben und bestätigte Overrides,
   - when `run-folder` erfolgreich endet,
   - then entstehen genau:
     - `5` `einzelabrechnung_2024.pdf`
     - `5` `pruefbericht_2024.pdf`
   - aufgeteilt in `4 tenant` + `1 vacancy_internal`.

5) **Template-Familie ist gemeinsam, Variantenlogik bleibt korrekt**
   - Given je ein renderbarer Fall `tenant` und `vacancy_internal`,
   - when beide PDFs erzeugt werden,
   - then verwenden beide dieselbe Template-Familie mit identischer Grundstruktur,
   - aber unterscheiden sich korrekt in Überschrift, Zahlungsblock und Ergebnislabel.

6) **Legacy-Outputzählung wird semantisch supersediert statt blind übernommen**
   - Given ältere Iterationen oder Legacy-Artefakte implizieren `5 tenant statements`,
   - when der Delta-/Oracle-Layer die Endausgabe bewertet,
   - then wird dies als semantisch supersediert erkannt,
   - und der Sollzustand lautet `4 tenant statements + 1 vacancy_internal statement`.

# Iteration 12

## Summary
- Review-Ergebnis vor dieser Verfeinerung:
  - Die fachliche Zielstruktur aus Iteration 11 ist konsistent,
  - aber der Rendering-Stack war noch nicht sauber an die vorhandenen Dokument-Workflows und die frühere Nutzerpräferenz angeglichen.
- Diese Iteration supersediert deshalb die älteren `reportlab`-Festlegungen aus Iteration 6/7/11 und legt **Typst** als verbindliche PDF-Engine für die finalen Abrechnungsdokumente fest.
- Begründung:
  - Typst passt besser zu dokumentartigen, tabellarischen Abrechnungen,
  - ist im Repo-Umfeld bereits bekannt/verwendet,
  - trennt Rechenlogik und Layout sauberer als canvas-orientiertes PDF-Zeichnen.
- `md2pdf` bleibt für bestehende Bewerbungs-Workflows relevant, ist für die Nebenkostenabrechnung aber **nicht** die primäre Zieltechnologie.
- Damit ist der Plan weiterhin **implementation-ready**, jetzt mit konsistenterer Rendering-Architektur.

## Requirements Snapshot
- Finale Dokumente `einzelabrechnung_{jahr}.pdf` und `pruefbericht_{jahr}.pdf` sollen:
  - tabellarisch,
  - nachvollziehbar,
  - layout-stabil,
  - später leicht anpassbar
  sein.
- Die Nebenkosten-Pipeline trennt deshalb künftig strikt:
  - **Python** für Ingestion, Normalisierung, Rechenkern und Render-Payload,
  - **Typst** für PDF-Layout und PDF-Erzeugung.
- Bestehende frühere Planstellen mit `reportlab` gelten ab dieser Iteration als **superseded technical decision**.
- Es wird **kein** Markdown-Zwischenschritt als primäres Renderformat eingeführt; Zielpfad ist direkt:
  - `canonical data -> render payload JSON -> Typst -> PDF`

## Detailed Plan
1) PDF-Engine verbindlich auf Typst umstellen
   - Supersedierte technische Entscheidungen:
     - `PDF-Rendering mit Python + reportlab`
     - `PDF-Engine: reportlab`
     - `Template-Vertrag wird in reportlab umgesetzt`
   - Neuer Standard:
     - PDF-Rendering mit `Typst`
   - Begründung:
     - bessere Wartbarkeit des Layouts,
     - saubere Template-Sprache statt Low-Level-PDF-Code,
     - näher an den im Repo bereits vorhandenen Dokument-Workflows.

2) Render-Architektur als Zwei-Stufen-Modell festziehen
   - Stufe A: Python erzeugt pro renderbarer Partei strukturierte Render-Payloads:
     - `statement_payload.json`
     - `audit_payload.json`
   - Stufe B: Typst kompiliert daraus:
     - `einzelabrechnung_{jahr}.pdf`
     - `pruefbericht_{jahr}.pdf`
   - Artefakte je Partei:
     - `{root}/Einzelabrechnungen/{party_slug}/statement_payload_{jahr}.json`
     - `{root}/Einzelabrechnungen/{party_slug}/audit_payload_{jahr}.json`
     - `{root}/Einzelabrechnungen/{party_slug}/einzelabrechnung_{jahr}.pdf`
     - `{root}/Einzelabrechnungen/{party_slug}/pruefbericht_{jahr}.pdf`
   - Technische Wahrheit bleibt:
     - Rechenkern-/Auditdaten in JSON/SQLite,
     - PDFs sind gerenderte Enddokumente.

3) Typst-Template-Familie verbindlich definieren
   - Gemeinsame Template-Familie:
     - `statement_template_v1.typ`
     - `audit_template_v1.typ`
   - Ablage im Projekt:
     - `Vermietung/nebenkosten_pipeline/nebenkosten_pipeline/templates/`
   - `statement_template_v1.typ` deckt beide Renderfälle ab:
     - `statement_kind = tenant`
     - `statement_kind = vacancy_internal`
   - Pflichtbereiche der Einzelabrechnung:
     - Titelblock
     - Objekt- und Parteidaten
     - Abrechnungszeitraum
     - tabellarische Kostenzeilen
     - Formel-/Anteilsspalten
     - Summenblock
     - Zahlungs-/Saldoabschnitt
     - Quellen-/Hinweisblock
   - Layoutvorgabe:
     - optisch an den bisherigen ista-/Eigenabrechnungen orientiert,
     - aber **keine** Bildkopien oder Screenshot-Einbettungen,
     - stattdessen vollständig datengetriebene Tabellen und Textblöcke.

4) Render-Payload-Schema für Typst festziehen
   - `statement_payload.json` enthält mindestens:
     - `schema_version`
     - `statement_kind`
     - `property`
     - `party`
     - `billing_period`
     - `line_items[]`
     - `totals`
     - `payments`
     - `writeoff_summary`
     - `notes[]`
   - `audit_payload.json` enthält mindestens:
     - `schema_version`
     - `party`
     - `source_documents[]`
     - `allocation_lines[]`
     - `formula_traces[]`
     - `review_flags[]`
     - `oracle_deltas[]`
   - Typst liest diese Payloads direkt ein; der Rechenkern kennt kein Dokumentlayout.

5) Template-Entscheidung gegen Markdown/md2pdf abgrenzen
   - `md2pdf` bleibt für bestehende Fließtext-Dokumente nützlich,
   - ist hier aber nachrangig, weil:
     - Abrechnungen stärker tabellarisch und zahlenlastig sind,
     - Variantenlogik (`tenant` vs `vacancy_internal`) sauberer in einer Template-Sprache modelliert werden kann,
     - Formeln, Summenblöcke und Prüfreferenzen stabiler in Typst abbildbar sind.
   - Markdown kann optional weiterhin als Hilfs-/Debug-Ausgabe existieren, ist aber **nicht** Teil des primären Produktionspfads.

6) Tooling- und Teststrategie für Typst konkretisieren
   - Laufzeitvoraussetzung:
     - `typst` CLI ist lokal und in CI verfügbar.
   - Determinismus:
     - verwendete Typst-Version wird im Projekt-/Build-Setup festgehalten.
   - Testebenen:
     - Schema-Tests für Render-Payloads
     - Template-Compile-Smoke-Tests
     - inhaltliche Regressionstests auf Überschriften, Summen und Kernzeilen
     - E2E-Tests für `4 tenant + 1 vacancy_internal`
   - Primäres Testorakel für Rendering ist **nicht** binäre PDF-Gleichheit,
     sondern:
     - erfolgreiche Typst-Kompilation,
     - erwartete strukturierte Payload,
     - erwartete inhaltliche Kernaussagen im Render-Ergebnis.

## Open Items
- Keine blockierenden offenen Punkte in dieser Iteration.
- Keine weiteren Nutzerentscheidungen erforderlich.
- Der Plan ist mit dieser Iteration implementation-ready.

## Verification Test Cases
1) **Typst supersediert ReportLab als Render-Engine**
   - Given ältere Iterationen referenzieren `reportlab`,
   - when die aktuelle Iteration 12 als maßgeblich gelesen wird,
   - then gilt `Typst` als verbindliche PDF-Engine und frühere `reportlab`-Entscheidungen sind technisch supersediert.

2) **Render-Pfad ist JSON nach Typst, nicht Markdown nach PDF**
   - Given ein erfolgreicher Parteienlauf,
   - when Render-Artefakte erzeugt werden,
   - then existieren `statement_payload_{jahr}.json` und `audit_payload_{jahr}.json` als Vorstufe der PDFs,
   - und der primäre Produktionspfad ist nicht `markdown -> md2pdf`.

3) **Tenant- und Leerstandsabrechnung nutzen dieselbe Typst-Template-Familie**
   - Given je ein Fall `statement_kind = tenant` und `statement_kind = vacancy_internal`,
   - when beide PDFs kompiliert werden,
   - then werden beide aus `statement_template_v1.typ` gerendert,
   - aber mit unterschiedlicher Variantenlogik für Überschrift, Zahlungsblock und Ergebnislabel.

4) **Typst-Compile-Smoke-Test für 2024-Parteien**
   - Given vollständige 2024-Render-Payloads für `Kraft/Hühne`, `Leerstand`, `Schäfer`, `König` und `Waldheim`,
   - when der Rendering-Schritt läuft,
   - then kompilieren genau `5` Einzelabrechnungen und `5` Prüfberichte erfolgreich über die Typst-CLI.

5) **Leerstandsabrechnung bleibt intern, trotz gleichem Template-System**
   - Given die Leerstandspartei wird mit `statement_kind = vacancy_internal` gerendert,
   - when `statement_template_v1.typ` die Ausgabe erzeugt,
   - then erscheint die Überschrift `Interne Leerstandsabrechnung`,
   - `Bereits gezahlt = 0`,
   - und der Ergebnisblock lautet `Vom Vermieter zu tragen / Abschreibung`.

6) **Audit-Template zeigt Quellen- und Formelkette**
   - Given ein `audit_payload.json` mit Warmwasser-, Heiznebenkosten- oder Müllzeilen,
   - when `audit_template_v1.typ` kompiliert wird,
   - then enthält der Prüfbericht mindestens Quellenreferenzen, Normalisierungswerte, Rechenformeln und finale Parteibeträge.

# Iteration 13

## Summary
- Diese Iteration fasst die maßgeblichen Ergebnisse der Iterationen 6-12 zu einer **kompakten, autoritativen Implementierungsbasis** zusammen.
- Ziel ist, künftige Implementierung und Reviews gegen **eine kurze Referenz** zu führen, ohne frühere Fehlentscheidungen erneut aufzugreifen.
- Frühere Iterationen bleiben historische Herleitung, sind aber für die Umsetzung nur noch relevant, soweit sie in dieser Iteration ausdrücklich bestätigt werden.
- Maßgeblich für die Implementierung ist daher ab jetzt primär:
  - diese Iteration 13
  - plus die darin referenzierten Vertragsdateien/Artefakte
  - plus die numerischen Orakelwerte, soweit sie hier bestätigt sind.

## Requirements Snapshot
- Zielworkflow:
  - Benutzer legt ista-PDFs, Ableseprotokoll-Bilder und Belege lokal in einen Jahresordner.
  - Pipeline läuft für `jahr=YYYY`.
  - Ergebnis sind nachvollziehbare PDF-Abrechnungen und Prüfberichte im Zielordner.
- Produktive Eingaben stammen **nicht** aus dem Workbook zur Laufzeit, sondern aus:
  - `_inputs/master_data.yaml`
  - `_inputs/tenancies_{jahr}.yaml`
  - `_inputs/tariffs_{jahr}.yaml`
  - `_inputs/allocation_bases_{jahr}.yaml`
  - `_inputs/payments_{jahr}.yaml`
  - `_inputs/review_overrides_{jahr}.yaml`
  - `_inputs/target_rules_{jahr}.yaml`
- Das Workbook ist nur noch:
  - Migrationsquelle
  - Legacy-Orakel
  - Delta-/Regression-Referenz
  und **keine** produktive Laufzeitabhängigkeit.
- Render-Stack:
  - Python erzeugt kanonische Daten und Render-Payloads,
  - Typst rendert PDFs,
  - primärer Renderpfad ist `JSON -> Typst -> PDF`.
- 2024-Zielausgabe:
  - `4` tenant-Abrechnungen
  - `1` interne Leerstandsabrechnung (`vacancy_internal`)
  - `5` Prüfberichte

## Detailed Plan
1) Autoritative Domänen- und Eingaberegeln
   - Kanonische Laufzeitbasis sind `_inputs/*.yaml` plus OCR-normalisierte Beobachtungen.
   - `run.db`, `canonical_snapshot.json`, `review_queue.json` und `delta_report.json` bilden die technischen Laufartefakte.
   - Offene oder unsichere OCR-/Mapping-Fälle erzeugen Review-Items; finale PDFs nur ohne blocking Reviews.

2) Fachliche Kernregeln, die bei der Implementierung verbindlich gelten
   - `vacancy`:
     - `persons = 0`
     - `billable_to_tenant = false`
     - `statement_kind = vacancy_internal`
   - `owner_internal`:
     - zählt ggf. in Nenner/Verbrauch mit,
     - erhält aber keine eigene Einzelabrechnung.
   - Für `basis_type = persons` gilt:
     - nur explizite Basis oder feste Geschäftsregel,
     - **kein** Fallback auf `tenancies` oder `master_data`.
   - Für `Müllabfuhr` gilt:
     - Leerstand ist nicht im Nenner,
     - Leerstand erhält keinen Müllanteil,
     - übrige Parteien teilen die Kosten nach Personenbasis.
   - Leerstandskosten werden nicht einem Mieter belastet; Vermieteranteile werden in der internen Leerstandsabrechnung ausgewiesen.

3) Rendering- und Outputvertrag
   - Pro renderbarer Partei entstehen:
     - `statement_payload_{jahr}.json`
     - `audit_payload_{jahr}.json`
     - `einzelabrechnung_{jahr}.pdf`
     - `pruefbericht_{jahr}.pdf`
   - Renderbare Parteitypen:
     - `tenant`
     - `vacancy_internal`
   - Nicht renderbar:
     - `owner_internal`
   - Template-System:
     - `statement_template_v1.typ`
     - `audit_template_v1.typ`
   - Layout orientiert sich inhaltlich an bisherigen ista-/Eigenabrechnungen, aber vollständig datengetrieben und tabellarisch.

4) Verifikations- und Orakelstrategie
   - Jeder Testfall gehört genau zu einem Orakeltyp:
     - `legacy_oracle`
     - `target_rule_oracle`
     - `invariant_oracle`
   - Workbook-Werte bleiben nur dort Sollzustand, wo keine neue Zielregel sie supersediert.
   - Bewusste Zielabweichungen, insbesondere rund um Leerstand, Müll und Outputmenge, sind als `target_rule_oracle` zu testen.
   - Gemischte E2E-Orakel aus Legacy- und Target-Regeln sind unzulässig.

5) Nicht erneut zu treffende bzw. bereits supersedierte Entscheidungen
   - **Nicht wiederholen:** produktiver Rechenkern mit Workbook-Laufzeitabhängigkeit.
   - **Nicht wiederholen:** `reportlab` als PDF-Engine.
   - **Nicht wiederholen:** primärer Markdown->PDF-Pfad für Abrechnungen.
   - **Nicht wiederholen:** `vacancy` ohne Ausgabe.
   - **Nicht wiederholen:** `vacancy` als normale Mieterabrechnung.
   - **Nicht wiederholen:** Personen-Fallback über `tenancies`/`master_data`.
   - **Nicht wiederholen:** Workbook als monolithisches End-Orakel für Leerstandsregeln.
   - Wenn frühere Iterationen diesen Punkten widersprechen, gilt **diese Iteration 13**.

## Open Items
- Keine blockierenden offenen Punkte.
- Der Plan bleibt implementation-ready.
- Für künftige Implementierung soll standardmäßig nur noch diese Iteration als Kurzreferenz verwendet werden; ältere Iterationen dienen nur der Herleitung oder Belegführung.

## Verification Test Cases
1) **Implementierung folgt der kompakten Referenz statt supersedierter Altentscheidungen**
   - Given frühere Iterationen enthalten teils überholte Entscheidungen,
   - when die Umsetzung gegen Iteration 13 gestartet wird,
   - then werden PDF-Engine, Leerstandslogik, Inputquellen und Orakelstrategie nach Iteration 13 umgesetzt.

2) **2024-Ausgabemenge bleibt fachlich korrekt**
   - Given vollständige 2024-Eingaben und bestätigte Overrides,
   - when der produktive Lauf endet,
   - then entstehen genau `4` tenant-Abrechnungen, `1` interne Leerstandsabrechnung und `5` Prüfberichte.

3) **Produktiver Lauf benötigt kein Workbook**
   - Given vollständige `_inputs/*.yaml` und Dokumenteingaben,
   - when `run-folder` produktiv läuft,
   - then werden die Ergebnisse ohne Workbook-Laufzeitpfad erzeugt.

4) **Leerstand bleibt intern und nicht mieterseitig**
   - Given die Partei `Leerstand`,
   - when die Abrechnung erzeugt wird,
   - then ist `statement_kind = vacancy_internal`, `Bereits gezahlt = 0`, und es entsteht keine Zahlungsforderung an einen Mieter.

5) **Renderpfad ist JSON nach Typst**
   - Given ein renderbarer Parteienlauf,
   - when die Dokumente erzeugt werden,
   - then entstehen zuerst Render-Payload-JSONs und danach die PDFs via Typst.

6) **Müll- und Personenlogik ignoriert supersedierte Altfallbacks**
   - Given eine Müllverteilung mit Leerstand,
   - when der Rechenkern die Personenbasis auflöst,
   - then wird Leerstand mit `0` Personen behandelt und kein Fallback aus `tenancies` oder `master_data` verwendet.

# Iteration 14

## Summary
- Diese Iteration ergänzt zu Iteration 13 eine **ultrakurze Ausführungs-Checkliste** für die Umsetzung.
- Klarstellung: Die früheren Iterationen wurden **nicht physisch gekürzt**; wegen der append-only-Historie wurden sie nur durch Iteration 13 inhaltlich übersteuert.
- Für Kontextsparsamkeit in der Implementierung gelten ab jetzt:
  - **Iteration 13 = autoritative Kurzreferenz**
  - **Iteration 14 = operative Umsetzungs-Checkliste**

## Requirements Snapshot
- Alte Iterationen bleiben im Dokument, sollen aber bei der Implementierung standardmäßig ignoriert werden, außer wenn Iteration 13/14 explizit auf sie verweist.
- Die Umsetzung soll mit minimalem Plan-Kontext möglich sein, ohne alte Fehlentscheidungen zu wiederholen.

## Detailed Plan
1) `_inputs/*.yaml` für 2024 finalisieren
   - `master_data`, `tenancies`, `tariffs`, `allocation_bases`, `payments`, `review_overrides`, `target_rules`

2) OCR-/Dokumenteingang kanonisieren
   - Dokumenttypen erkennen
   - Belege gruppieren
   - Observations erzeugen
   - Review-Queue füllen

3) Fachliche Resolver bauen
   - Meter-Aliase/Konflikte
   - BillingParties/Intervalle
   - Personenbasis ohne Fallback

4) Rechenkern auf Zielregeln bringen
   - Verbrauch
   - Umlage
   - Zahlungen
   - Leerstand/Müll/Vermieteranteil

5) Render-Payloads erzeugen
   - `statement_payload_{jahr}.json`
   - `audit_payload_{jahr}.json`

6) Typst-Templates umsetzen
   - `statement_template_v1.typ`
   - `audit_template_v1.typ`
   - Varianten `tenant` / `vacancy_internal`

7) Produktiven Lauf ohne Workbook absichern
   - `run-folder` ohne Excel-Laufzeitpfad
   - PDFs nur ohne blocking Reviews

8) Tests in drei Orakelgruppen grün ziehen
   - `legacy_oracle`
   - `target_rule_oracle`
   - `invariant_oracle`

## Open Items
- Keine blockierenden offenen Punkte.
- Wenn echte Dateikürzung gewünscht ist, braucht es einen **separaten Konsolidierungsschritt**, weil die bisherige Planpflege append-only war.
- Für die Implementierung reichen Iteration 13 und 14 als Arbeitsgrundlage.

## Verification Test Cases
1) **Implementierung kann mit Iteration 13+14 allein gestartet werden**
   - Given die Kurzreferenz und Checkliste,
   - when die Umsetzung begonnen wird,
   - then sind Inputquellen, Zielregeln, Renderpfad und Teststrategie ohne Rückgriff auf ältere Iterationen klar.

2) **Workbook ist nicht mehr produktiv erforderlich**
   - Given vollständige `_inputs/*.yaml` und Quelldokumente,
   - when der Lauf produktiv ausgeführt wird,
   - then funktioniert der End-to-End-Prozess ohne Workbook-Laufzeitabhängigkeit.

3) **Typst-Output bleibt Zielpfad**
   - Given die Reporting-Implementierung,
   - when PDFs erzeugt werden,
   - then ist der Produktionspfad `JSON -> Typst -> PDF` und nicht `reportlab` oder `Markdown -> PDF`.

4) **Leerstand bleibt interne Abrechnung**
   - Given die Partei `Leerstand`,
   - when die Ausgabe erzeugt wird,
   - then entsteht eine interne Leerstandsabrechnung und keine normale Mieterabrechnung.

# Iteration 15

## Summary
- Diese Iteration formalisiert den bislang zu implizit behandelten Excel-Ableitungsvertrag fuer `Betriebskosten` und `Stammdaten`.
- Anlass war die zu Recht irritierende Luecke zwischen:
  - bereits spezifizierter tenant-facing Ausgabe
  - und noch nicht hinreichend verbindlich spezifizierter Herleitung der restlichen Kostenarten aus dem Legacy-Workbook.
- Kernpunkt:
  - Die Scope-Herkunft einer Kostenzeile kommt primaer aus `Betriebskosten`.
  - Der Verteilschluessel kommt primaer aus `Stammdaten`.
  - Die Begriffe `Berechnungseinheit 1/2` sind fachlich nicht nur interne Codes, sondern haben eine explizite fachliche Erklaerung und muessen in der Ausgabe/Pruefdokumentation entsprechend lesbar gemacht werden.

## Requirements Snapshot
- Das System muss die restlichen 2024-Kostenarten workbook-treu aus dem Legacy-Excel in strukturierte `cost_entries` und daraus in reproduzierbare Umlagezeilen ueberfuehren koennen.
- Diese Ueberfuehrung darf nicht auf ad-hoc-Heuristiken beruhen, sondern muss aus einem festen Ableitungsvertrag folgen:
  1. `Betriebskosten` bestimmt den Buchungs-/Nutzungsscope.
  2. `Stammdaten` bestimmt den erwarteten Verteilschluessel je Kostenart.
  3. `Anlage 1 - Verteilschluessel` / die Erlaeuterung in `Allgemein` definiert die lesbare Bedeutung von Berechnungseinheit 1 und 2.

## Verbindlicher Excel-Ableitungsvertrag

### 1) Scope-Autoritaet: Worksheet `Betriebskosten`
- Autoritative Spalten:
  - `C = Berechnungseinheit`
  - `D = Nutzeinheit`
- Verbindliche Scope-Regel:
  - Wenn `D` befuellt ist, ist die Kostenzeile direkt einer **Nutzeinheit** zugeordnet.
  - Sonst, wenn `C` befuellt ist, ist die Kostenzeile direkt einer **Berechnungseinheit** zugeordnet.
  - Sonst, wenn `C` und `D` leer sind, ist die Kostenzeile auf **Objekt-/Liegenschaftsebene** gebucht.
- Damit wird eine leere `C/D`-Kombination nicht als fehlender Scope interpretiert, sondern als **bewusste Objektzuordnung**.

### 2) Verteilschluessel-Autoritaet: Worksheet `Stammdaten`
- Autoritative Spalten:
  - `B = Kostenart`
  - `C = Verteilschluessel`
  - `D = nach Berechnungseinheit`
- Verbindliche Regel:
  - Der normalisierte Verteilschluessel einer Kostenzeile wird aus `Stammdaten[Kostenart]` abgeleitet, nicht aus frei interpretiertem Freitext.
  - Die in `Betriebskosten` mitgefuehrte Spalte `Umlageschluessel` ist eine Legacy-Spiegelung/Hilfe, aber die fachliche Source-of-Truth bleibt die Kostenartdefinition aus `Stammdaten`.
  - Ein Widerspruch zwischen `Betriebskosten.Umlageschluessel` und `Stammdaten[Kostenart].Verteilschluessel` erzeugt ein Review-/Validierungsereignis statt stiller Uebernahme.

### 3) Bedeutung des Flags `nach Berechnungseinheit`
- Wenn `Stammdaten.nach Berechnungseinheit = x`, dann bedeutet dies:
  - die Kostenart wird nicht direkt ueber die gesamte Liegenschaft auf Parteien verteilt,
  - sondern innerhalb der jeweils relevanten Berechnungseinheit(en) weiterverteilt.
- Verbindliche Ableitungsregel:
  - `Betriebskosten` liefert weiterhin den **Buchungsscope** der Zeile,
  - `Stammdaten.nach Berechnungseinheit` steuert die **fachliche Verteilungslogik** der Kostenart.
- Daraus folgt:
  - Eine auf Objektebene gebuchte Zeile mit leerem `C/D` kann trotzdem eine Kostenart sein, die fachlich nach Berechnungseinheiten weiterverteilt wird.
  - Leeres `C/D` ist daher **kein** Grund mehr fuer ein pauschales `scope_missing`, wenn die Scope-Herkunft objektweit zulassig ist.

### 4) Lesbare Bedeutung von Berechnungseinheit 1 und 2
- Die im Workbook enthaltene Erlaeuterung ist verbindlicher Teil des Begriffsvertrags:
  - **Berechnungseinheit 1 = Gebaeude Ost (Energietraeger: Oel und Waermepumpe)**  
    Nutzeinheiten 1 und 2; Oelbeheizung, Warmwasseraufbereitung ueber strombetriebene Waermepumpe.
  - **Berechnungseinheit 2 = Gebaeude Nord und Gebaeude West (Energietraeger: Holz und Pellets)**  
    Nutzeinheiten 3, 4 und 5.
- Tenant-facing Dokumente, Pruefberichte und Input-/Snapshot-Dokumentation duerfen interne Kuerzel wie `BE1`/`BE2` verwenden, muessen diese aber lesbar aufloesen oder beim ersten Auftreten ausschreiben.

## Superseded / Corrected Prior Assumption
- Die fruehere Annahme aus Iteration 6 / Verification Case `Scope-sensitive Heiznebenkosten ohne Scope erzeugen Review`
  - `Given 2024-Betriebskostenzeile Servicerechnung ista / Heiznebenkosten / 376.66 ohne BE/NE -> scope_missing`
  - ist in dieser pauschalen Form **supersediert**.
- Neue Regel:
  - Eine `Betriebskosten`-Zeile ohne `C/D` ist primaer **objektweit**.
  - Ob daraus ein direkt verteilbarer CostEntry entsteht oder eine weitere Verteilung ueber Berechnungseinheiten erforderlich ist, entscheidet die Kostenartdefinition aus `Stammdaten`, nicht die blosse Leere von `C/D`.

## Acceptance / Verification Test Cases
1) **Objektweite Betriebskostenzeile wird korrekt als global erkannt**
   - Given eine `Betriebskosten`-Zeile mit leerem `C` und leerem `D`,
   - when der Scope normalisiert wird,
   - then entsteht `scope_type = global` statt `scope_missing`.

2) **Berechnungseinheit hat Vorrang vor global**
   - Given eine `Betriebskosten`-Zeile mit befuelltem `C = 2` und leerem `D`,
   - when der Scope normalisiert wird,
   - then entsteht `scope_type = calculation_unit`, `scope_id = 2`.

3) **Nutzeinheit hat Vorrang vor Berechnungseinheit**
   - Given eine `Betriebskosten`-Zeile mit befuelltem `D = Geb. Nord - Gesindehaus (Nutzeinheit 3)`,
   - when der Scope normalisiert wird,
   - then entsteht `scope_type = unit`, `scope_id = NE3` bzw. die normalisierte Nutzeinheit 3.

4) **Verteilschluessel wird aus Stammdaten gezogen**
   - Given `Kostenart = Grundsteuer`,
   - when ein `cost_entry` normalisiert wird,
   - then ist der erwartete Verteilschluessel `Wohnflaeche` gemaess `Stammdaten`, auch wenn die Betriebskostenzeile nur eine Legacy-Spiegelung dieses Werts traegt.

5) **Widerspruch zwischen Betriebskosten- und Stammdaten-Schluessel wird nicht still geschluckt**
   - Given eine Betriebskostenzeile, deren `Umlageschluessel` nicht mit `Stammdaten[Kostenart]` uebereinstimmt,
   - when die Normalisierung laeuft,
   - then entsteht ein Review-/Validierungsereignis statt stiller Uebernahme.

6) **Objektweite Zeile mit BE-gebundener Kostenart bleibt zulaessig**
   - Given eine objektweit gebuchte Zeile ohne `C/D` fuer eine Kostenart mit `Stammdaten.nach Berechnungseinheit = x`,
   - when die Zeile normalisiert wird,
   - then ist sie nicht automatisch `scope_missing`, sondern ein zulaessiger objektweiter Eingang fuer nachgelagerte Verteilung ueber Berechnungseinheiten.

7) **BE-Begriffe bleiben fuer Leser aufgeloest**
   - Given tenant-facing Einzelabrechnung oder Pruefbericht,
   - when `Berechnungseinheit 1` oder `Berechnungseinheit 2` sichtbar werden,
   - then sind diese lesbar als:
     - `Berechnungseinheit 1 (Gebaeude Ost, Oel und Waermepumpe)`
     - `Berechnungseinheit 2 (Gebaeude Nord und Gebaeude West, Holz und Pellets)`
     oder eine inhaltlich gleichwertige Aufloesung dargestellt.

## Open Items
- [MISSING NON-BLOCKING] Fuer einzelne Kostenarten mit `nach Berechnungseinheit = x` ist die exakte Zwischenstufe `objektweite Buchung -> Split auf relevante Berechnungseinheiten -> Parteienverteilung` im Rechenkern noch nicht komplett implementiert; diese Iteration schliesst aber den fachlichen Vertrag, nicht die Umsetzung.
- [REVIEW NON-BLOCKING] Falls im Legacy-Workbook jemals gleichzeitig `C` und `D` auf derselben Zeile befuellt waeren, soll die Implementierung `D` als spezifischere Scope-Angabe behandeln und den Fall zusaetzlich markieren.

# Iteration 16

## Summary
- Diese Iteration schliesst die letzte spec-seitige Restluecke nach Iteration 15:
  - was bei **objektweit gebuchten**, aber fachlich **nach Berechnungseinheit** weiterzuverteilenden Kostenarten passiert,
  - und welche **2024-Kostenarten** jetzt verbindlich im Scope der workbook-treuen Cost-Entry-Erweiterung sind.
- Ziel ist, dass Plan und Implementierung die restlichen Kostenarten jetzt ohne weitere Produkt-Raterei in strukturierte `cost_entries` ueberfuehren koennen.

## Rendering- und Rechenkernvertrag fuer `global -> Berechnungseinheit -> Partei`
- Wenn eine `Betriebskosten`-Zeile:
  - auf Objektebene gebucht ist (`C/D` leer),
  - und die Kostenart in `Stammdaten` `nach Berechnungseinheit = x` traegt,
  - dann ist der Eintrag **nicht** direkt global auf Parteien umzulegen.
- Stattdessen gilt verbindlich die zweistufige fachliche Herleitung:
  1. objektweite Buchung / Eingangskostenposition,
  2. fachliche Zuordnung zu den relevanten Berechnungseinheiten gemaess Kostenart-/Workbook-Regel,
  3. erst danach Parteienverteilung innerhalb der jeweiligen Berechnungseinheit.
- Tenant-facing Folge:
  - In der Einzelabrechnung wird in diesem Fall **nicht** eine globale Basis angezeigt,
  - sondern die Basis der **relevanten Berechnungseinheit**.
- Beispiel:
  - Eine objektweit gebuchte heizungsbezogene Zeile ohne `C/D` kann in der Einzelabrechnung von `Kraft/Huehne` als Kostenposition der **Berechnungseinheit 1** erscheinen, wenn die fachliche Weiterverteilung dorthin fuehrt.

## Verbindliche 2024-Kostenarten-Abdeckung
- Die workbook-treue 2024-Erweiterung der `cost_entries` umfasst jetzt verbindlich mindestens diese Kostenfamilien:
  1. `Brennstoffkosten`
  2. `Gebaeudeversicherung`
  3. `Heiznebenkosten`
  4. `Grundsteuer`
  5. `Muellabfuhr`
  6. `Kalt- und Abwasser`
  7. `Oberflaechenwasser`
  8. `Strom`
  9. `Allgemein / Verbrauchskosten Warmwasser`
- Klarstellung:
  - `Strom` folgt weiter primär dem separaten Strom-/Tarifpfad,
  - `Allgemein / Verbrauchskosten Warmwasser` folgt weiter dem Warmwasser-/Waermepumpenpfad,
  - die uebrigen Kostenarten muessen workbook-treu aus `Betriebskosten` + `Stammdaten` normalisiert werden.

## Erwartete Scope-/Key-Kombinationen fuer 2024
- Verbindliche Erwartung fuer die workbook-nahe Normalisierung:
  - `Brennstoffkosten`
    - Key: `Verbrauch`
    - `nach Berechnungseinheit = x`
    - Scope aus `Betriebskosten`, ggf. objektweit gebucht, aber fachlich auf relevante Berechnungseinheit(en) herunterzubrechen
  - `Gebaeudeversicherung`
    - Key: `Wohnflaeche`
    - `nach Berechnungseinheit = x`
    - entweder direkt auf Nutzeinheit/Berechnungseinheit gebucht oder fachlich innerhalb der relevanten Berechnungseinheit verteilt
  - `Heiznebenkosten`
    - Key: `Verbrauch`
    - `nach Berechnungseinheit = x`
    - analog zu heizungsbezogenen Scope-Regeln; objektweite Buchung ist zulaessig, direkte Parteienverteilung aber erst nach BE-Herleitung
  - `Grundsteuer`
    - Key: `Wohnflaeche`
    - global / Objektebene
  - `Muellabfuhr`
    - Key: `Personen`
    - global / Objektebene
  - `Kalt- und Abwasser`
    - Key: `Verbrauch`
    - global / Objektebene, soweit keine explizite engere Scope-Zuordnung in `Betriebskosten` vorliegt
  - `Oberflaechenwasser`
    - Key: `Wohnflaeche`
    - global / Objektebene

## Superseded / Clarified
- Nach Iteration 16 gilt explizit:
  - Die Frage `steht in Betriebskosten C/D etwas drin?` beantwortet **nur** den Buchungsscope.
  - Die Frage `wie wird fuer die Abrechnung wirklich verteilt?` beantwortet die Kombination aus:
    - Kostenart,
    - `Stammdaten.Verteilschluessel`,
    - `Stammdaten.nach Berechnungseinheit`,
    - und ggf. weiteren kostenartspezifischen Regeln.
- Damit ist die alte implizite Kurzannahme
  - `global gebucht = global verteilt`
  - fuer BE-gebundene Kostenarten **supersediert**.

## Acceptance / Verification Test Cases
1) **Objektweit gebuchte, BE-gebundene Kostenart wird nicht global fehlgerendert**
   - Given eine objektweit gebuchte `Heiznebenkosten`- oder `Brennstoffkosten`-Zeile ohne `C/D`,
   - when die Einzelabrechnung einer Partei aus Berechnungseinheit 1 erzeugt wird,
   - then zeigt die Abrechnung die relevante **Berechnungseinheit 1** als Bezugsraum und nicht die gesamte Liegenschaft als finale Umlagebasis.

2) **2024-Kostenartenliste ist vollstaendig im Scope**
   - Given die workbook-treue Erweiterung des 2024-Falls,
   - when der Scope der Cost-Entry-Normalisierung beschrieben wird,
   - then sind die oben gelisteten Kostenfamilien explizit umfasst und keine davon ist nur implizit gemeint.

3) **Scope und Schluessel werden nicht verwechselt**
   - Given eine Betriebskostenzeile und ihre Kostenartdefinition,
   - when die Normalisierung laeuft,
   - then bestimmt `Betriebskosten` den Buchungsscope und `Stammdaten` den Verteilschluessel; ein globaler Buchungsscope bedeutet nicht automatisch globale Parteienverteilung.

4) **Tenant-facing Output bleibt lesbar**
   - Given eine Kostenposition mit zwischengeschaltetem `global -> Berechnungseinheit`-Split,
   - when sie im PDF erklaert wird,
   - then sind fuer den Leser die relevante Berechnungseinheit und deren Basis sichtbar, statt einer irrefuehrenden globalen Bezugsbasis.

# Iteration 17

## Summary
- Diese Iteration schliesst die letzte fachliche Restluecke zwischen Spec und Plan:
  - der Normalisierungsvertrag fuer `cost_entries` wird fuer workbook-/belegbasierte Kostenarten explizit gemacht,
  - der Unterschied zwischen **Buchungsscope** und **finalem Verteilungsscope** wird auf Feldniveau festgezogen,
  - und fuer mehrdeutige heizungsnahe Servicebelege wird ein verbindlicher Vorab-Inputvertrag festgelegt.
- Ziel ist, dass der naechste Plan-/Implementierungsslice keine Produktentscheidungen mehr erraten muss, sondern nur noch den jetzt geschlossenen Fachvertrag codiert.

## Verbindlicher Normalisierungsvertrag fuer workbook-/belegbasierte `cost_entries`
- Fuer aus `Betriebskosten`, OCR-Belegen oder deren Zusammenfuehrung normalisierte Kostenpositionen gilt ab dieser Iteration:
  - das Top-Level-Feld `scope_type` / `scope_id` repraesentiert den **finalen abrechnungswirksamen Verteilungsscope**,
  - die urspruengliche Legacy-Buchung aus `Betriebskosten.C/D` bleibt zusaetzlich erhalten als:
    - `metadata.booked_scope_type`
    - `metadata.booked_scope_id`
  - die fachliche Herleitungsquelle des finalen Scopes wird zusaetzlich festgehalten als:
    - `metadata.scope_rule_source`
  - optional zusaetzliche Hilfsfelder:
    - `metadata.energy_carrier_family`
    - `metadata.operator_decision_ref`
    - `metadata.scope_unit_ids` fuer Gruppenscopes.

Verbindliche Semantik:
- `scope_type` / `scope_id`
  - beschreibt, **innerhalb welches finalen fachlichen Raums** die Parteienverteilung stattfindet.
- `metadata.booked_scope_*`
  - beschreibt, **wie die Zeile im Legacy-Workbook bzw. Eingangsdokument gebucht war**.
- Damit gilt explizit:
  - `scope_type = global` darf nur stehen bleiben, wenn die Kostenposition auch fachlich global auf Parteien zu verteilen ist.
  - Bei `global -> Berechnungseinheit -> Partei` bleibt `metadata.booked_scope_type = global`, aber `scope_type` zeigt die relevante Berechnungseinheit.

## Zulaessige finale Scope-Typen
- Fuer die workbook-treue Kostenarten-Normalisierung sind ab jetzt zulaessig:
  - `global`
  - `calculation_unit`
  - `unit`
  - `unit_group`

Zusatzvertrag fuer `unit_group`:
- `scope_type = unit_group`
- `scope_id` ist ein stabiler Gruppen-Slug
- `metadata.scope_unit_ids` listet die enthaltenen Nutzeinheiten explizit und sortiert

Verbindliche 2024-Gruppen-Slugs:
- `NE3`
- `NE1_NE2`
- `NE4_NE5`

Beispiel:
- Eine Gebaeudeversicherungsposition fuer den gemeinsamen Vertrag von `NE1 + NE2` wird normalisiert als:
  - `scope_type = unit_group`
  - `scope_id = NE1_NE2`
  - `metadata.scope_unit_ids = [NE1, NE2]`
  - `allocation_basis = living_area`

## Verbindliche fachliche Ableitungsreihenfolge
Die fachliche Scope-Herleitung erfolgt ab jetzt in genau dieser Reihenfolge:
1. **Kostenart bestimmen**
   - aus Workbook-/Belegklassifikation bzw. Review-Obersteuerung.
2. **Buchungsscope bestimmen**
   - ausschliesslich aus `Betriebskosten.C/D` gemaess Iteration 15:
     - `D` befuellt -> `metadata.booked_scope_type = unit`
     - sonst `C` befuellt -> `metadata.booked_scope_type = calculation_unit`
     - sonst -> `metadata.booked_scope_type = global`
3. **Kostenartvertrag aus `Stammdaten` bestimmen**
   - `allocation_basis`
   - `nach Berechnungseinheit`
4. **Finalen Verteilungsscope bestimmen**
   - wenn die Kostenart **nicht** `nach Berechnungseinheit` verteilt wird und keine speziellere Fachregel greift:
     - `scope_type/scope_id = metadata.booked_scope_type/metadata.booked_scope_id`
   - wenn die Kostenart `nach Berechnungseinheit = x` traegt:
     - befuelltes `D` bleibt final `unit`
     - sonst befuelltes `C` bleibt final `calculation_unit`
     - sonst greifen die kostenartspezifischen Regeln dieser Iteration
5. **Parteienverteilung erst innerhalb des finalen Scopes**
   - nie direkt aus dem blossen Buchungsscope, wenn der finale Fachvertrag enger ist.

## Kostenartspezifische Fachregeln fuer den finalen Verteilungsscope
### 1) Heizungsnahe Energietraegerfamilien
- Fuer `Brennstoffkosten` und heizungsnahe, BE-gebundene Kostenarten gilt:
  - `metadata.energy_carrier_family = oil_be1`
    - finaler Scope: `calculation_unit`, `scope_id = 1`
  - `metadata.energy_carrier_family = wood_pellet_be2`
    - finaler Scope: `calculation_unit`, `scope_id = 2`

Semantik:
- `oil_be1` umfasst Oel-bezogene Kosten fuer das Gebaeude Ost / Berechnungseinheit 1.
- `wood_pellet_be2` umfasst Holz-, Pellet- sowie zugehoerige Holz-/Saegezubehoer-Belege fuer Gebaeude Nord/West / Berechnungseinheit 2.

Verbindliche Folge:
- Wenn eine objektweit gebuchte, BE-gebundene Heizkostenposition diese Energietraegerfamilie traegt, dann darf der finale Scope **nicht** global bleiben.

### 2) Gebaeudeversicherung 2024
- Gebaeudeversicherung wird 2024 nicht als pauschaler Globaltopf behandelt.
- Verbindliche Vertragsgruppen:
  - `NE3`
  - `NE1_NE2`
  - `NE4_NE5`
- Der finale Scope fuer Gebaeudeversicherung ist damit 2024:
  - `unit` fuer den Einzelvertrag `NE3`,
  - `unit_group` fuer `NE1_NE2`,
  - `unit_group` fuer `NE4_NE5`.

Verbindliche Folge:
- Eine Gebaeudeversicherungsposition darf 2024 nicht als global verteilte Versicherungskostenposition normalisiert werden, wenn sie fachlich zu einer dieser Vertragsgruppen gehoert.

### 3) Mehrdeutige Heizungsbauer-/Kaminfeger-Belege
- Heizungsbauer-, Wartungs-, Brenner-, Schornsteinfeger- und vergleichbare heizungsnahe Servicebelege duerfen **nicht** still anhand einer Vermutung einer Berechnungseinheit zugeordnet werden, wenn aus Beleg und Workbook keine eindeutige Berechnungseinheit folgt.
- Fuer diese Faelle ist ein vorgelagerter Pflichtinput erforderlich.

## Verbindlicher Pflichtinput fuer Nutzerentscheidungen
- Der produktive Jahreslauf erwartet fuer mehrdeutige heizungsnahe Servicebelege eine dedizierte Datei:
  - `_inputs/operator_scope_decisions_{jahr}.yaml`

Verbindlicher YAML-Grundvertrag:
```yaml
operator_scope_decisions:
  - source_fingerprint: "<receipt.source_fingerprint>"
    cost_type_id: "heiznebenkosten"
    final_scope_type: "calculation_unit"
    final_scope_id: "1"
    note: "betrifft Oelanlage Gebaeude Ost"
```

Zulaessige Ziele:
- `final_scope_type = calculation_unit` mit `final_scope_id = 1` oder `2`
- `final_scope_type = unit`
- `final_scope_type = unit_group` plus `scope_unit_ids`

Verbindliche Regeln:
- Die Entscheidung ist **vor dem produktiven Lauf** zu hinterlegen.
- Fehlt sie fuer einen mehrdeutigen heizungsnahen Servicebeleg, muss die Pipeline:
  - einen blocking Review-/Input-Hinweis erzeugen
  - und darf fuer diesen Beleg keine finale Scope-Zuordnung raten.
- Die angewendete Entscheidung wird im normalisierten `cost_entry` referenziert ueber:
  - `metadata.scope_rule_source = operator_scope_decision`
  - `metadata.operator_decision_ref = <source_fingerprint>`

## Superseded / Clarified
- Nach Iteration 17 gilt explizit:
  - `scope_type/scope_id` beschreiben nicht mehr bloss den Legacy-Buchungskontext, sondern den finalen Verteilungsraum.
  - Der Legacy-Buchungskontext bleibt separat in `metadata.booked_scope_*` erhalten.
  - `unit_group` ist ein zulaessiger fachlicher Verteilungsraum fuer Kostenarten wie die 2024er Gebaeudeversicherung.
  - Mehrdeutige Heizungsservice-Belege sind kein Feld fuer implizite Heuristiken, sondern fuer einen expliziten Pflichtinput.

## Acceptance / Verification Test Cases
1) **Objektweit gebuchter Oel-Beleg wird final BE1**
   - Given ein objektweit gebuchter `Brennstoffkosten`-Beleg mit `metadata.energy_carrier_family = oil_be1`,
   - when der `cost_entry` normalisiert wird,
   - then gilt:
     - `metadata.booked_scope_type = global`
     - `scope_type = calculation_unit`
     - `scope_id = 1`
     - `metadata.scope_rule_source = energy_carrier_family`.

2) **Objektweit gebuchter Holz-/Pellet-Beleg wird final BE2**
   - Given ein objektweit gebuchter heizungsnaher Beleg mit `metadata.energy_carrier_family = wood_pellet_be2`,
   - when der `cost_entry` normalisiert wird,
   - then gilt:
     - `metadata.booked_scope_type = global`
     - `scope_type = calculation_unit`
     - `scope_id = 2`.

3) **Gebaeudeversicherung 2024 darf Gruppenscope tragen**
   - Given ein 2024er Gebaeudeversicherungsbeleg fuer den Vertrag `NE1 + NE2`,
   - when die Position normalisiert wird,
   - then gilt:
     - `scope_type = unit_group`
     - `scope_id = NE1_NE2`
     - `metadata.scope_unit_ids = [NE1, NE2]`
     - und die Position ist nicht global verteilt.

4) **Mehrdeutiger Heizungsservicebeleg ohne Pflichtinput blockiert**
   - Given ein Heizungsbauer- oder Kaminfeger-Beleg ohne eindeutige fachliche Berechnungseinheit,
   - when `_inputs/operator_scope_decisions_{jahr}.yaml` keinen passenden Eintrag enthaelt,
   - then erzeugt die Pipeline einen blocking Review-/Input-Hinweis und keine geratene finale Scope-Zuordnung.

5) **Mehrdeutiger Heizungsservicebeleg mit Pflichtinput wird deterministisch**
   - Given derselbe Beleg und ein passender Eintrag in `_inputs/operator_scope_decisions_{jahr}.yaml`,
   - when die Normalisierung laeuft,
   - then folgt `scope_type/scope_id` exakt der Nutzerentscheidung und der `cost_entry` traegt `metadata.operator_decision_ref`.

6) **Tenant-facing Output bleibt auf finalem Scope**
   - Given eine Kostenposition mit `metadata.booked_scope_type = global`, aber `scope_type = calculation_unit`,
   - when die Einzelabrechnung gerendert wird,
   - then zeigt das Dokument die relevante Berechnungseinheit als Bezugsraum und nicht den blossen Legacy-Buchungsscope.

# Iteration 18

## Summary
- Diese Iteration praezisiert die letzten noch zu locker formulierten Fachvertraege aus Iteration 17:
  - exaktes Matching-/Validierungsverhalten fuer `_inputs/operator_scope_decisions_{jahr}.yaml`
  - eindeutige Prioritaetsregeln zwischen Workbook-Scope, Operatorentscheidung und deterministischen Fachregeln
  - Persistenzpflicht fuer `booked_scope`-/`final_scope`-Nachvollziehbarkeit
  - Blockierverhalten fuer gemischte bzw. nicht sauber splitbare Mehrbereichs-Belege
- Ziel ist, dass ein nachgelagerter Plan keine Produktregeln mehr erfinden muss, sondern nur noch konkrete Implementierungsschritte daraus ableitet.

## Praezisierter Vertrag fuer `_inputs/operator_scope_decisions_{jahr}.yaml`
- Jeder Eintrag unter `operator_scope_decisions` muss genau einen mehrdeutigen heizungsnahen Servicebeleg adressieren.
- Pflichtfelder:
  - `source_fingerprint`
  - `cost_type_id`
  - `final_scope_type`
- Pflichtfeld abhaengig vom Ziel:
  - bei `final_scope_type = calculation_unit` -> `final_scope_id`
  - bei `final_scope_type = unit` -> `final_scope_id`
  - bei `final_scope_type = unit_group` -> `final_scope_id` **und** `scope_unit_ids`
- `note` bleibt optional, aber empfohlen.

Matching- und Validierungsregeln:
- Matching erfolgt primaer ueber `source_fingerprint`.
- `cost_type_id` muss zum normalisierten Beleg passen; ein Eintrag mit falscher Kostenart ist ungueltig.
- Mehr als ein passender Decision-Eintrag fuer denselben `source_fingerprint` ist unzulaessig und blockiert den Lauf.
- Ein Decision-Eintrag fuer einen Beleg, dessen finaler Scope bereits eindeutig aus:
  - `Betriebskosten.D`,
  - `Betriebskosten.C`,
  - oder einer deterministischen Fachregel
  folgt, ist **konfliktbehaftet** und darf nicht still ueberstimmen.

Verbindliche Review-Ausgaenge:
- fehlende Entscheidung -> blocking Review `operator_scope_decision_missing`
- mehrere passende Entscheidungen -> blocking Review `operator_scope_decision_ambiguous`
- unpassende/konfliktbehaftete Entscheidung -> blocking Review `operator_scope_decision_conflict`

## Verbindliche Prioritaetsreihenfolge fuer die finale Scope-Herleitung
Die finale fachliche Scope-Herleitung folgt ab jetzt dieser Prioritaet:
1. **Explizite Workbook-Granularitaet**
   - `Betriebskosten.D` gewinnt immer.
   - sonst gewinnt `Betriebskosten.C`.
2. **Pflichtentscheidung fuer mehrdeutige heizungsnahe Servicebelege**
   - greift nur, wenn weder `D` noch `C` den finalen Scope bereits eindeutig festlegen.
3. **Deterministische kostenartspezifische Fachregel**
   - z. B. `energy_carrier_family = oil_be1` -> `calculation_unit 1`
   - z. B. `energy_carrier_family = wood_pellet_be2` -> `calculation_unit 2`
   - z. B. Gebaeudeversicherung 2024 -> `unit` / `unit_group`
4. **Sonstiger Buchungsscope**
   - nur wenn keine engere Fachregel greift.

Nicht zulaessig ist:
- dass eine Operatorentscheidung eine bereits explizite `D`-/`C`-Zuordnung ueberschreibt,
- oder dass eine unsichere Heuristik einen eigentlich pflichtentscheidungsbeduerftigen Servicebeleg doch noch still zuordnet.

## Persistenz- und Nachvollziehbarkeitspflicht fuer Scope-Metadaten
- Die folgenden Informationen muessen den produktiven Lauf ueberdauern und in den normalisierten Artefakten erhalten bleiben:
  - `scope_type`
  - `scope_id`
  - `metadata.booked_scope_type`
  - `metadata.booked_scope_id`
  - `metadata.scope_rule_source`
- Falls `unit_group` verwendet wird, zusaetzlich:
  - `metadata.scope_unit_ids`
- Falls eine Operatorentscheidung verwendet wird, zusaetzlich:
  - `metadata.operator_decision_ref`

Verbindliche Folge:
- Ein normalisierter `cost_entry` ist fachlich unvollstaendig, wenn der finale Scope spaeter nicht mehr auf seinen Buchungsscope und seine Herleitungsquelle zurueckgefuehrt werden kann.
- Es ist zulaessig, diese Felder top-level oder in `metadata` zu persistieren, solange kein Informationsverlust entsteht.

## Gemischte oder nicht sauber trennbare Mehrbereichs-Belege
- Wenn ein einzelner Eingangsbeleg fachlich mehrere verschiedene finale Scopes oder Kostenarten enthaelt, dann gilt:
  - er muss in mehrere normalisierte `cost_entries` gesplittet werden,
  - oder der Lauf blockiert mit einem Review-/Split-Hinweis.

Verbindliche Beispiele:
- eine Rechnung mit getrennten Positionen fuer BE1- und BE2-Leistungen -> Split in mehrere `cost_entries`
- eine Rechnung, bei der aus OCR/Beleg nicht belastbar hervorgeht, welcher Teil zu welcher Berechnungseinheit gehoert -> blocking Review statt Ratescope

## Acceptance / Verification Test Cases
1) **Operator-Decision-Datei validiert eindeutig**
   - Given zwei Eintraege mit demselben `source_fingerprint`,
   - when `_inputs/operator_scope_decisions_{jahr}.yaml` geladen wird,
   - then blockiert der Lauf mit `operator_scope_decision_ambiguous`.

2) **Operatorentscheidung darf explizten Workbook-Scope nicht ueberschreiben**
   - Given ein Beleg mit explizitem `Betriebskosten.C = 2` oder `D = NE3`,
   - when zusaetzlich eine abweichende Operatorentscheidung vorliegt,
   - then entsteht `operator_scope_decision_conflict` statt stiller Uebernahme.

3) **Scope-Nachvollziehbarkeit bleibt persistent**
   - Given ein normalisierter `cost_entry` mit `metadata.booked_scope_type = global` und finalem `scope_type = calculation_unit`,
   - when die Artefakte des produktiven Laufs geschrieben werden,
   - then bleiben Buchungsscope, finaler Scope und `scope_rule_source` rekonstruierbar erhalten.

4) **Gemischter Mehrbereichs-Beleg wird nicht still einem Scope zugewiesen**
   - Given ein Eingangsbeleg mit Positionen fuer mehrere finale Scopes,
   - when die Positionen nicht belastbar getrennt werden koennen,
   - then blockiert der Lauf mit einem Review-/Split-Hinweis statt einer geratenen Einzelscope-Zuordnung.

# Restart Iteration 0

## Summary
- Diese Iteration startet die Spec fachlich neu, nachdem die bisherige Arbeitslinie den Kern der Aufgabe verwischt hat.
- Fuer alle weiteren Spec-, Plan- und Implementierungsschritte gilt ab hier: **Excel ist kein produktiver Laufzeit-Input und kein stiller Fallback mehr.**
- Die frueheren Iterationen bleiben als Historie erhalten, sind fuer den Neustart aber nur noch Kontext und **nicht** mehr autoritativ.

## Problem Statement
- Ziel ist eine lokal laufende Nebenkosten-Pipeline fuer `Hauptstr. 2, 36381 Schluechtern`, die aus echten Quelldokumenten nachvollziehbare Einzelabrechnungen erzeugt.
- Das bisherige manuelle Workbook darf als Altartefakt, Migrationshilfe oder Vergleichsstand existieren, aber die neue Pipeline darf fachlich nicht davon abhaengen, dass dieses Workbook vorhanden ist.
- Jeder sichtbare Wert in der Abrechnung muss auf eine kanonische Quelle und eine explizite Herleitung zurueckfuehrbar sein.

## Neustart-Leitlinien
1. **Kein Workbook im Normalbetrieb**
   - `run-folder` und jeder spaetere produktive Standardlauf duerfen das Legacy-Workbook weder als Input noch als automatische Ergaenzung verwenden.
2. **Kein stiller Fallback**
   - Wenn kanonische Inputs unvollstaendig sind, entsteht ein Review-/Blocker-Zustand.
   - Fehlende Daten duerfen nicht durch Excel, geratene Defaults oder implizite Annahmen ersetzt werden.
3. **Explizite Source-of-Truth-Kette**
   - Zulassige fachliche Kette ist:
     - Quelldokumente / manuelle Operatorentscheidungen
     - Extraktion / OCR-Artefakte
     - kanonische strukturierte Inputs
     - Berechnung
     - Render-Payloads
     - PDF / Pruefbericht
4. **Ehrliche Darstellung fuer Mieter**
   - Wenn periodengenaue Rohmesswerte oder Belegzuordnungen fehlen, muss das Dokument dies offen benennen, statt eine vollstaendige Herleitung vorzutaeuschen.
5. **Lesbare Fachsprache**
   - Abkuerzungen und interne Begriffe wie `BE1`, `BE2`, `VE1`, `scope_type` oder aehnliche Technikbegriffe duerfen im Mieter-PDF nicht unerklaert auftauchen.

## Scope of This Restart
- Im Scope:
  - Definition eines sauberen Zielbilds ohne Excel-Abhaengigkeit im Normalbetrieb
  - Festlegung der autoritativen Eingabekette
  - fachliche und dokumentarische Nachvollziehbarkeit pro Zielwert
  - 2024 als erstes Referenzjahr fuer Migration und Verifikation
- Nicht im Scope dieser Iteration:
  - konkrete Implementierungsschritte
  - Rueckbau oder Bewertung einzelner Alt-Commits
  - Optimierungen an OCR, Layout oder Performance ohne vorher geklaerte Datenvertraege

## Functional Intent
- Ein Jahreslauf startet lokal ueber einen Belegordner und verarbeitet:
  - ista-PDFs,
  - Ableseprotokoll-Bilder,
  - Belege als Bild oder PDF,
  - explizite manuelle Operatorentscheidungen dort, wo Dokumente fachlich nicht eindeutig genug sind.
- Das Ergebnis pro Partei ist mindestens:
  - eine lesbare Einzelabrechnung als PDF,
  - ein Pruef-/Nachweisartefakt mit Quellen und Rechenweg,
  - ein maschinenlesbares Payload-Artefakt.

## Hard Constraints
- Excel darf **nicht** zur produktiven Berechnung, Datenanreicherung oder Render-Vervollstaendigung herangezogen werden.
- Ein Vergleich gegen das Legacy-Workbook ist nur als **expliziter Migrations- oder Verifikationsschritt** zulaessig und darf keine produktiven Inputs mutieren.
- Jeder Zielwert braucht rekonstruierbar:
  - `source_ref` oder gleichwertige Quellenreferenz,
  - verwendete Normalisierung / Regel,
  - Rechenformel,
  - Ergebniswert.
- Die Pipeline darf bei fehlender Sicherheit lieber `needs_review` oder `blocked` liefern als ein scheinbar sauberes, aber fachlich nicht belastbares Ergebnis.

## Acceptance Criteria for the Restart Baseline
1. Ein kuenftiger Normalbetrieb kommt ohne Workbook-Datei aus.
2. Wenn strukturierte Inputs vorhanden sind, wird kein Workbook stillschweigend eingelesen oder zur Ergaenzung verwendet.
3. Wenn strukturierte Inputs fehlen oder unvollstaendig sind, entsteht ein expliziter Review-/Blocker-Fall statt Excel-Nachhilfe.
4. Die Dokumentation fuer Mieter zeigt nur Herleitungen, die aus der kanonischen Eingabekette belastbar ableitbar sind.
5. Fruehere Spec-Iterationen duerfen nur noch als historische Referenz dienen; neue Planung muss diese Restart-Iteration als autoritativ behandeln.

## Open Markers
- [MISSING BLOCKING] Exakte Definition des kanonischen Input-Sets fuer den Normalbetrieb:
  - welche Daten aus Dokumenten extrahiert werden,
  - welche Daten manuell erfasst werden duerfen,
  - in welchen versionierbaren Dateien/Feldern sie abgelegt werden.
- [MISSING BLOCKING] Exakte Review-State-Semantik:
  - wann `needs_review`,
  - wann `blocked`,
  - wann ein Lauf trotz Teilunschaerfe noch tenant-facing Artefakte erzeugen darf.
- [MISSING BLOCKING] Formale Definition, welche Werte im tenant-facing PDF als Pflicht-Herleitung sichtbar sein muessen und welche nur im Pruefbericht auftauchen.
- [DECISION BLOCKING] Ob das Legacy-Workbook einen **separaten** Migrationsbefehl bekommen darf, der einmalig kanonische Inputs erzeugt; falls ja, unter welchen Review-Schranken.
- [DECISION NON-BLOCKING] Ob fuer den Neustart spaeter eine physisch neue Spec-Datei angelegt wird oder diese Datei als historische Sammeldatei bestehen bleibt.

# Restart Iteration 1

## Summary
- Der Neustart wird produktseitig auf drei klar getrennte Teile festgelegt:
  - fachlicher C#-Kern,
  - spaeterer Import/OCR-Pfad,
  - spaeterer PDF-/Dokumentpfad.
- Der erste belastbare Liefergegenstand ist **nicht** sofort das Endprodukt, sondern ein neuer Rechenkern, der gegen das Referenzjahr 2024 verifiziert werden kann.
- Das Legacy-Workbook ist fuer den Neustart **nur Test- und Vergleichsorakel**, nie operativer Input.

## Produktbild
- Das spaetere Produkt soll lokal aus echten Dokumenten nachvollziehbare Nebenkostenabrechnungen erzeugen.
- Es soll weiterhin einen OCR-/Import-Teil und einen PDF-/Dokumentteil geben.
- Der fachliche Kern darf jedoch unabhaengig davon aufgebaut und getestet werden.

## Schichten des Zielprodukts
1. **Fachlicher Kern**
   - neue Implementierung in C#
   - enthaelt Domänenmodell, Berechnungsregeln, Review-Entscheidungen und die fachlich richtigen Ergebnisse
2. **Import / OCR**
   - erschliesst die Eingangsdokumente fuer den spaeteren Produktivlauf
   - darf spaeter iterativ aufgebaut werden
3. **Dokumente / PDF**
   - erzeugt lesbare Einzelabrechnungen und Pruefberichte aus den Ergebnissen des Kerns
   - darf erst aufsetzen, wenn die Kernresultate fachlich stabil sind

## Klare Produktgrenzen
- Der fachliche Kern darf nicht von OCR, PDF-Rendering oder dem Legacy-Workbook abhaengen.
- OCR und PDF bleiben ausdruecklich Produktbestandteile, aber nicht Startpunkt des Neustarts.
- Ein spaeterer Wechsel der OCR- oder PDF-Technologie darf den fachlichen Kern nicht neu definieren.

## Verifikationsstrategie fuer den Neustart
- Das Referenzjahr 2024 bleibt das wichtigste Testjahr.
- Die manuell erstellte 2024-Abrechnung und das zugehoerige Workbook duerfen als **explizites Testorakel** genutzt werden.
- Zweck dieses Orakels:
  - erwartete Zwischen- und Endwerte fuer den neuen Rechenkern ableiten,
  - Abweichungen sichtbar machen,
  - Regressionsschutz fuer den Neustart schaffen.
- Nicht zulaessig:
  - Workbook-Werte in den operativen Lauf nachladen,
  - fehlende Produktivdaten mit Excelwerten auffuellen,
  - tenant-facing Ergebnisse auf versteckte Workbook-Hilfen stuetzen.

## Test-Setup-Grundsatz
- Der neue Rechenkern wird gegen 2024 mit einer festen Testsuite aufgebaut.
- Diese Tests duerfen das Workbook und die alte 2024-Abrechnung als Vergleichsstand benutzen.
- Die Testumgebung ist damit ausdruecklich strenger als der operative Lauf:
  - **im Test** ist Excel als Oracle erlaubt,
  - **im Produktivlauf** ist Excel als Input ausgeschlossen.

## Neustart-Reihenfolge
1. Zuerst fachlichen Kern neu aufbauen und gegen 2024 verifizieren.
2. Danach Import-/OCR-Schicht an den Kern anbinden.
3. Danach PDF-/Dokumentschicht auf die stabilen Kernresultate setzen.

## Acceptance Criteria
1. Es gibt einen neuen C#-Rechenkern, der ohne operative Excel-Abhaengigkeit gegen 2024 getestet werden kann.
2. Die 2024er Excel-/Abrechnungswerte werden nur fuer Tests und Vergleich genutzt.
3. Der spaetere Produktpfad bleibt offen fuer OCR und PDF, ohne den Kern wieder zu vermischen.
4. Die Spec haelt damit das Produktziel fest, nicht die technische Detailausgestaltung einzelner Typen oder Dateiformate.

## Open Markers
- [MISSING BLOCKING] **Verbindlicher Vergleichsstand fuer 2024-Tests**
  - Der Neustart-Teststand fuer 2024 soll mindestens diese fachlichen Vergleichswerte abdecken:
    - Parteien, Zeitraeume und Zuordnung von Nutzeinheiten zu Berechnungseinheiten,
    - Zahlungen / Vorauszahlungen je Partei - hierzu bruache ich einen Input Datei (später exportiere ich die Kontoauszüge im pdf Format)
    - Stromtarifperioden und monatliche Stromkosten je betroffener Partei,
    - abrechnungsrelevante Verbrauchswerte fuer Strom, Warmwasser und Kaltwasser,
    - Heiz- und Warmwasser-Sonderlogik fuer die betroffenen Einheiten,
    - Endergebnisse der Einzelabrechnungen je Partei fuer 2024.
  - Als Referenz duerfen das 2024er Workbook und die manuell erstellten 2024er Abrechnungen ausdruecklich genutzt werden.
  - Diese Referenz dient nur dem Test- und Vergleichsstand des neuen Kerns und ist kein operativer Input.
- [MISSING BLOCKING] **Tenant-facing Mindestinhalte der spaeteren PDF-Abrechnung**
  - Die spaetere PDF-Abrechnung soll mindestens enthalten:
    - Objekt, Partei und Abrechnungszeitraum,
    - Gesamtkosten, bereits gezahlte Vorauszahlungen und Ergebnis (`Nachzahlung`, `Guthaben` oder interne Leerstands-/Vermieterposition),
    - tabellarische Darstellung der relevanten Kostenarten,
    - je Kostenart eine lesbare Angabe der Umlagebasis bzw. Herleitungslogik,
    - bei verbrauchsabhaengigen Positionen die fuer Mieter nachvollziehbare Verbrauchsermittlung, samt Messwerte
    - verstaendliche Begriffe statt unerklaerter interner Kuerzel,
    - nachvollziehbare Sonderhinweise fuer fachliche Spezialfaelle wie Warmwasser in Gebaeude Ost.
  - Der Pruefbericht darf tiefere Herleitungen und Quellverweise enthalten, die nicht zwingend auf der eigentlichen Mieterabrechnung stehen muessen.
- [MISSING BLOCKING] **Review-/Blocker-Situationen fuer den operativen Lauf**
  - Ein operativer Lauf muss mindestens dann stoppen oder als nicht freigabefaehig gelten, wenn:
    - zentrale Pflichtdaten fuer Partei, Zeitraum, Kostenart oder Zahlungen fehlen,
    - die fachlich noetige Verbrauchs- oder Umlagebasis fehlt,
    - heizungsnahe oder vergleichbar kritische Belege keinem belastbaren Umlagebereich zugeordnet werden koennen,
    - Zaehler oder Messwerte widerspruechlich oder nicht eindeutig zuordenbar sind,
    - Tarifdefinitionen fuer den relevanten Zeitraum fachlich nicht belastbar sind,
    - notwendige Operatorentscheidungen fehlen oder sich widersprechen.
  - Nicht jeder Review-Fall ist automatisch blocker:
    - rein pruefbeduerftige, aber fachlich nicht laufkritische Unschaerfen duerfen als Warnung dokumentiert werden,
    - blocker und warnung muessen im Neustart spaeter klar voneinander getrennt werden.
- [DECISION NON-BLOCKING] Ob fuer den Neustart spaeter eine eigene neue Spec-Datei angelegt wird oder diese Datei die Historie weitertraegt.

# Restart Iteration 2

## Summary
- Diese Iteration loest die letzten offenen Produktfragen aus `Restart Iteration 1` auf.
- Sie definiert, was fuer den Neustart als **fachlich stabil** gilt, welche Inhalte der **verbindliche 2024-Vergleichsstand** abdeckt und wie **Mieterabrechnung, Pruefbericht und Review-Freigabe** voneinander abgegrenzt sind.
- Damit ist die Neustart-Spec auf Produkt- und Anforderungsniveau konsistent genug, um daraus einen Implementierungsplan abzuleiten.

## Bedeutung von "fachlich stabil"
- Der neue fachliche Kern gilt fuer einen definierten Scope als **fachlich stabil**, wenn:
  - die vereinbarten 2024-Vergleichswerte fuer diesen Scope reproduzierbar erreicht oder sauber erklaert abweichend dokumentiert werden,
  - keine offenen blockerhaften Review-Faelle mehr bestehen, die die fachliche Aussagekraft des Ergebnisses untergraben,
  - die entstehenden Ergebnisse fuer Mieter und Operatoren nachvollziehbar voneinander herleitbar sind.
- `fachlich stabil` bedeutet ausdruecklich nicht, dass OCR und PDF bereits final ausgebaut sein muessen.
- OCR-/Import- und PDF-Arbeit bauen auf diesem Zustand auf, statt ihn zu definieren.

## Verbindlicher 2024-Vergleichsstand fuer den Neustart
- Der Neustart verifiziert den neuen Rechenkern gegen einen klaren 2024-Referenzstand.
- Dieser Vergleichsstand umfasst mindestens:
  1. Parteien, Rollen, Zeitraeume und Zuordnung von Nutzeinheiten zu Berechnungseinheiten,
  2. Zahlungen und Vorauszahlungen je Partei,
  3. Endergebnisse je Partei (`Gesamtkosten`, `Nachzahlung`, `Guthaben` bzw. interne Leerstands-/Vermieterwirkung),
  4. abrechnungsrelevante Verbrauchs- und Tarifwerte fuer die betroffenen Kostenarten,
  5. die fachlichen Spezialregeln des Objekts, insbesondere: => nur um es klar zu stellen, die Warmwasseraufbereitung in Berechnungseinheit1 erfolgt mittels Wärmepumpe, die an den allgemeinen Stromzähler von BE 1 angeschlossen ist. Die Stromkosten für die Warmwasseraufbereitung ergeben sich aus Kosten für Warmwasser = Allgemeinstromkosten - Stromzähler Nutzeinheit 1 - Stromzähler Nutzeinheit 2, diese ergibt die Stromkosten für die Warmwasseraufbereitung, diese werden nach Verbrauch auf NE1 und NE2 umgelegt. Kaltwasser funktioniert ähnlich hier gibt es den Wasserzähler am Hauptanschlaschluss, dieser zählt die gesamtmenge des verbrauchten Wassers, jede Nutzeinheite hat noch einmal einen seperaten Kaltwasserzähler ausser NU5 hier gilt Kaltwasserverbrauch NU5 (KW) = KW Hauptanschluss - KW NU1 -KW NU2 -KW NU3-KW NU4
     - Warmwasser-Allgemein nur fuer Gebaeude Ost,
     - verbrauchsabhaengige Verteilung der entsprechenden Kosten,
     - Behandlung von Leerstand,
     - belastbare Zuordnung zu den Berechnungseinheiten.
- Das 2024er Workbook und die manuell erstellten 2024er Abrechnungen duerfen dafuer als Test- und Vergleichsorakel verwendet werden.
- Diese Orakel-Nutzung ist streng auf Verifikation beschraenkt und erzeugt keinerlei operative Eingabeberechtigung fuer den Produktivlauf.

## Trennung von Mieterabrechnung und Pruefbericht
- Die spaetere **Mieterabrechnung** ist das lesbare Ergebnisdokument fuer den Mieter.
- Sie soll mindestens enthalten:
  - Objekt, Partei und Abrechnungszeitraum,
  - Gesamtkosten, bereits gezahlte Vorauszahlungen und Ergebnis,
  - tabellarische Darstellung der relevanten Kostenarten,
  - lesbare Umlage- bzw. Herleitungslogik pro relevanter Position,
  - nachvollziehbare Verbrauchsermittlung bei verbrauchsabhaengigen Kosten, samt Messwerte
  - verstaendliche Sprache ohne unerklaerte interne Kuerzel.
- Der **Pruefbericht** ist das vertiefende Nachweis- und Operator-Dokument.
- Er soll insbesondere enthalten:
  - Quellen- und Belegbezug,
  - vertiefte Formeln und Zwischenwerte,
  - dokumentierte Review-Hinweise, Warnungen und erklaerte Abweichungen,
  - tiefere Details, die fuer Nachvollziehbarkeit wichtig sind, aber nicht zwingend in die Mieterabrechnung gehoeren. => sie gehören genau genommen garnihct in die Abrechnung der prüfbericht ist für mich und zeigt mir ob alles in ordnungs ist
- Wenn ein Detail fachlich relevant, aber fuer die Mieterabrechnung zu technisch oder noch nicht belastbar genug ist, gehoert es in den Pruefbericht statt in die Mieterabrechnung.

## Freigabepolitik fuer Review-Ergebnisse
- **Blocker** verhindern ein freigabefaehiges tenant-facing Ergebnis fuer den betroffenen Scope.
- Betrifft ein blocker nur eine einzelne Partei oder einen eng begrenzten fachlichen Bereich, darf dafuer keine freigabefaehige Mieterabrechnung entstehen.
- Betrifft ein blocker eine gemeinsame fachliche Grundlage mehrerer Parteien, duerfen fuer die betroffenen Parteien keine freigabefaehigen Mieterabrechnungen entstehen.
- **Warnungen** duerfen einen Lauf nicht automatisch stoppen, muessen aber fuer Operatoren sichtbar bleiben und im Pruefkontext nachvollziehbar dokumentiert werden.
- Ein Ergebnis darf nur dann als freigabefaehige Mieterabrechnung gelten, wenn fuer den betreffenden Scope keine offenen blockerhaften Sachverhalte mehr bestehen.

## Marker-Status nach dieser Iteration
- Die drei blocking Open Markers aus `Restart Iteration 1` zu
  - 2024-Vergleichsstand,
  - tenant-facing Mindestinhalten,
  - Review-/Blocker-Freigabe
  gelten durch diese Iteration fachlich als aufgeloest.
- Offen bleibt nur noch die nicht-blockierende Strukturfrage, ob der Neustart spaeter in eine eigene neue Spec-Datei ausgelagert wird.

# Restart Iteration 3

## Summary
- Diese Iteration schliesst die letzten verbleibenden Neustart-Luecken auf Spec-Niveau:
  - kanonisches operatives Eingabepaket,
  - konkretes 2024-Testorakel,
  - Mindestinhalt des operatorseitigen Pruefberichts,
  - Entscheidung zur Workbook-Migration.
- Die neuen `=>`-Erlaeuterungen zu Zahlungen, Warmwasser, Kaltwasser und Pruefbericht werden hier fachlich eingeordnet und verbindlich gemacht.
- Damit ist die Neustart-Spec jetzt plan-ready; technische Serialisierung, Dateiformate und Klassenstrukturen gehoeren ab hier in den Implementierungsplan.

## Kanonisches operatives Eingabepaket
- Der spaetere produktive Lauf verwendet **kein Workbook** und keine freien Tabellen als operative Eingabe.
- Stattdessen verwendet er ein **kanonisches, versionierbares Eingabepaket** aus strukturierten Artefakten.
- Dieses Eingabepaket muss mindestens abdecken:
  1. Objektsicht und Zuordnung von Berechnungseinheiten, Nutzeinheiten und relevanten Zaehlern,
  2. Parteien, Rollen und Abrechnungszeiträume,
  3. Zahlungen / Vorauszahlungen je Partei,
  4. Tarife und sonstige preisrelevante Zeitabschnitte,
  5. abrechnungsrelevante Mess- und Verbrauchsdaten,
  6. Kostenpositionen / normalisierte Beleginformationen,
  7. notwendige manuelle Operatorentscheidungen fuer nicht deterministische Zuordnungen.
- Die konkrete technische Serialisierung dieses Pakets ist keine Spec-Frage mehr, sondern Teil des spaeteren Implementierungsplans.

## Zahlungsinput als eigener fachlicher Eingang
- Zahlungen und Vorauszahlungen sind ein eigener verpflichtender Teil des kanonischen Eingabepakets.
- Der neue Kern rechnet mit bestaetigten Zahlungsfakten, nicht mit rohen Kontoauszuegen oder PDF-Kontoexporten.
- Ein spaeterer Import aus Kontoauszuegen oder PDF-Dokumenten darf diese Zahlungsfakten erzeugen, ersetzt aber nicht die Pflicht zu einem belastbaren Zahlungsinput.

## Verbindliches 2024-Testorakel
- Fuer den Neustart wird ein explizites 2024-Testorakel verwendet.
- Dieses Orakel besteht mindestens aus:
  - dem 2024er Legacy-Workbook inklusive der fuer Vergleich und Herleitung relevanten Blaetter,
  - den manuell erstellten 2024er Einzelabrechnungen,
  - den 2024er Quelldokumenten fuer Messwerte, Ablesungen und Belege,
  - den fuer 2024 benoetigten Zahlungsinformationen.
- Als fachlich verbindlich fuer den Neustart gelten mindestens diese Vergleichsdimensionen:
  1. Parteien, Rollen, Zeitraeume und Zuordnung zu Berechnungseinheiten,
  2. Zahlungen und Vorauszahlungen,
  3. relevante Tarif- und Verbrauchswerte,
  4. Endergebnisse je Partei,
  5. objektspezifische Sonderregeln.
- Dieses Testorakel darf nur zur Verifikation, Testableitung und Delta-Erklaerung genutzt werden.
- Es darf keinen verdeckten Rueckkanal in den operativen Lauf erzeugen.

## Objektspezifische Sonderregeln, die im Neustart mit abgedeckt werden muessen
- **Warmwasser in Gebaeude Ost / Berechnungseinheit 1**
  - Die Warmwasseraufbereitung in Berechnungseinheit 1 erfolgt ueber eine Waermepumpe.
  - Diese haengt am allgemeinen Stromzaehler der Berechnungseinheit 1.
  - Die Stromkosten fuer Warmwasser ergeben sich fachlich aus dem Allgemeinstrom der Berechnungseinheit 1 abzueglich der eindeutig zuordenbaren Stromverbraeuche der Nutzeinheiten 1 und 2.
  - Der so ermittelte Warmwasser-Stromanteil wird nach Warmwasserverbrauch auf die betroffenen Einheiten in Berechnungseinheit 1 verteilt.
- **Kaltwasser fuer Nutzeinheit 5**
  - Der Hauptanschluss zaehlt den Gesamtverbrauch des Kaltwassers im Objekt.
  - Die Nutzeinheiten 1 bis 4 verfuegen ueber eigene Kaltwasserzaehler.
  - Der Kaltwasserverbrauch der Nutzeinheit 5 ergibt sich als Restgroesse aus Hauptanschluss minus Nutzeinheiten 1 bis 4.
- Diese beiden Regeln sind fuer dieses Objekt fachlich relevant und gehoeren damit in den verbindlichen 2024-Vergleichsstand.

## Mindestinhalt des Pruefberichts
- Der Pruefbericht ist ein **operatorseitiges Kontroll- und Nachweisdokument**.
- Er ist nicht Teil der eigentlichen Mieterkommunikation und muss nicht auf Mieterlesbarkeit optimiert sein.
- Er soll mindestens enthalten:
  - Quellenbezug auf Dokumente, strukturierte Eingaben und Operatorentscheidungen,
  - die relevanten Formeln und Zwischenwerte,
  - erklaerte Abweichungen gegenueber dem 2024-Testorakel,
  - offene Warnungen und blockerhafte Sachverhalte,
  - die Herleitung vom fachlichen Input zum Endergebnis.

=> die gebäudeversicherung besteht aus 3 einzelnen Verträgen bei der AXA Versicherung. Versicherungsnummer 560036443442 wird unter NE5 und NE4 aufgeteilt, Versicerungsnummer 56003644335 gehört zu NE3, Versicerhungsnummer 56003644333 wird unter NE1 und NE2 aufgeteilt
=> Holz und Pellets wird auf die Brechnungseinhiet 2 verteilt damit wird geheist und warmes wasser erzeugt, Öl und Wäremepumpe auf Berechnungseinhiet 1 siehe oben

## Entscheidung zur Workbook-Migration
- Fuer den Neustart gibt es **keinen** workbook-basierten operativen Lauf und **keinen** stillen Workbook-Migrationspfad.
- Ein allgemeiner Workbook-Migrationsbefehl ist **nicht** Teil des Neustart-MVP.
- Falls spaeter ein einmaliger Migrationshelfer gebaut wird, ist er:
  - explizit separat,
  - nur fuer Migration/Testvorbereitung gedacht,
  - ausserhalb des operativen Laufpfads,
  - und seine Ergebnisse muessen als strukturierte Eingaben pruefbar und reviewbar sein.

## Marker-Status nach dieser Iteration
- Die in `Restart Iteration 0` und `Restart Iteration 1` verbliebenen blocking-Fragen zu
  - kanonischem Eingabepaket,
  - 2024-Testorakel,
  - tenant-facing Abrechnung vs. operatorseitigem Pruefbericht,
  - Review-/Blocker-Freigabe,
  - Workbook-Migration
  gelten durch `Restart Iteration 2` und `Restart Iteration 3` fachlich als aufgeloest.
- Die Neustart-Spec ist damit bereit fuer die Ableitung eines Implementierungsplans.

# Restart Iteration 4

## Summary
- Diese Iteration ueberfuehrt die letzten fachlich relevanten `=>`-Kommentare in eine autoritative Neustart-Fassung.
- Neu verbindlich ergaenzt werden:
  - die Aufteilung der Gebaeudeversicherung,
  - die Zuordnung von Energietraegern zu den Berechnungseinheiten,
  - die Pflicht zur Darstellung der nicht verbrauchsabhaengigen Schluesselwerte und ihrer Herleitung in der Mieterabrechnung.
- Damit sind auch die zuletzt ausserhalb der Iterationsstruktur notierten Kommentare fachlich integriert.

## Weitere objektspezifische Zuordnungsregeln
- **Gebaeudeversicherung**
  - Die Gebaeudeversicherung besteht im relevanten Objekt aus drei getrennten Vertraegen.
  - Ein Vertrag betrifft die Einheiten `NE4` und `NE5`.
  - Ein Vertrag betrifft ausschliesslich `NE3`.
  - Ein Vertrag betrifft die Einheiten `NE1` und `NE2`.
  - Diese Versicherungszuordnung ist fuer das Objekt fachlich verbindlich und gehoert damit in den Vergleichs- und Regelsatz des Neustarts.
- **Energietraeger je Berechnungseinheit**
  - Holz und Pellets gehoeren fachlich zur Berechnungseinheit 2 und decken dort Heizung und Warmwasser ab.
  - Oel und Waermepumpe gehoeren fachlich zur Berechnungseinheit 1.
  - Diese Zuordnung ist fuer Kostenklassifikation, Vergleichsstand und spaetere Regelumsetzung verbindlich.

## Pflicht zur Darstellung von Schluesselwerten in der Mieterabrechnung
- Die allgemeinen Anforderungen aus `Restart Iteration 0` gelten unveraendert weiter.
- Wenn in der Abrechnung nicht verbrauchsabhaengige Schluesselwerte fuer die Umlage relevant sind, muessen diese in der Mieterabrechnung nachvollziehbar auftauchen.
- Dazu gehoeren insbesondere:
  - die verwendeten Verteilungsschluessel,
  - die dazugehoerigen Basiswerte der betroffenen Einheit oder Partei,
  - die Herleitung dieser Basiswerte, soweit sie fuer die konkrete Umlage relevant ist.
- Diese Informationen duerfen nicht ausschliesslich im operatorseitigen Pruefbericht verbleiben, wenn sie fuer das Verstaendnis der eigentlichen Umlage in der Mieterabrechnung notwendig sind.

## Marker-Status nach dieser Iteration
- Die zuletzt ausserhalb der Restart-Iterationsstruktur notierten fachlichen Kommentare zu
  - Gebaeudeversicherung,
  - Energietraeger-Zuordnung,
  - Schluesselwerten in der Mieterabrechnung
  gelten durch `Restart Iteration 4` als formal in die Neustart-Spec uebernommen.
- Die Neustart-Spec ist damit auf Spec-Niveau konsistent und bereit fuer die Ableitung eines Implementierungsplans.

| Date | Iteration | Author | Delta |
| --- | --- | --- | --- |
| 2026-03-14 | 1 | Copilot | Initiales RefinePlan-Iteration-Append mit Struktur, Phasen und expliziten BLOCKING/NON-BLOCKING Open Items |
| 2026-03-14 | 2 | Copilot | Nutzerantworten aus `=>` integriert, BLOCKING-Punkte aufgelöst, implementation-ready inkl. Verifikationstestfälle |
| 2026-03-14 | 3 | Copilot | Implementation-Ready-Review korrigiert: numerischen Input->Output Oracle ergänzt und datenbezogene Testfälle mit konkreten Sollwerten eingeführt |
| 2026-03-14 | 4 | Copilot | OCR-Vorlauf mit realen 2024-Quellen integriert; Testfälle auf OCR->Canonical->Berechnung mit konkreten Input/Output-Werten erweitert |
| 2026-03-14 | 5 | Copilot | Nutzerantworten zu WW-Regel, lernender Belegzuordnung und Tarif-Basisdaten integriert; späterer Umsetzungsstatus und verbleibende Tasks in Iteration 5 konsolidiert |
| 2026-03-14 | 6 | Copilot | Implementierungsplan auf umsetzungsfähigen Zielzustand verfeinert: kanonische Inputs/Persistenz, Parteien- und Leerstandslogik, Meter-Aliase, Beleggruppierung und PDF-Zielartefakte spezifiziert |
| 2026-03-14 | 7 | Copilot | Formale Datenverträge, Review-State-Machine, Replay-Semantik und Umlageregel-Matrix ergänzt; Plan damit implementation-ready gemacht |
| 2026-03-14 | 8 | Copilot | Zahlungsinput und explizite Umlagebasisverträge ergänzt; Vorauszahlungen und personenbasierte Verteilung fachlich reproduzierbar gemacht |
| 2026-03-14 | 9 | Copilot | Nutzerentscheidung zu Leerstand als nicht abrechenbare Phase integriert; Müll ohne Leerstand verteilt und Vermieter-Abschreibung als eigenes Zielartefakt definiert |
| 2026-03-14 | 10 | Copilot | Legacy- und Target-Rule-Orakel sauber getrennt; supersedierte Workbook-Felder und Teststrategie für Leerstand formalisiert |
| 2026-03-14 | 11 | Copilot | Leerstand als interne, renderbare Abrechnung statt separatem Owner-Report präzisiert; Output-Vertrag und Template-Strategie harmonisiert |
| 2026-03-14 | 12 | Copilot | PDF-Rendering auf Typst umgestellt; ReportLab-Festlegungen supersediert und JSON->Typst->PDF-Architektur samt Template-/Payload-Vertrag festgezogen |
| 2026-03-14 | 13 | Copilot | Autoritative Kurzfassung der Iterationen 6-12 ergänzt; maßgebliche Designentscheidungen konsolidiert und supersedierte Altentscheidungen explizit ausgeschlossen |
| 2026-03-14 | 14 | Copilot | Ultrakurze operative Implementierungs-Checkliste ergänzt; klargestellt, dass frühere Iterationen nicht physisch gekürzt, sondern nur autoritativ übersteuert wurden |
| 2026-03-23 | 15 | Copilot | Formalized Excel derivation rules: Betriebskosten scope from columns C/D, allocation key from Stammdaten, readable Berechnungseinheit 1/2 semantics, and superseded the old blanket scope-missing rule for empty C/D |
| 2026-03-23 | 16 | Copilot | Closed the final spec gap for objectwide-but-BE-distributed costs, enumerated the full 2024 cost-type expansion scope, and made the booking-scope vs. final-distribution split explicit |
| 2026-03-23 | 17 | Copilot | Fixed the normalization contract on field level: final scope vs booked scope, allowed unit_group scopes, mandatory operator scope decisions file, and deterministic rules for oil/wood-pellet/insurance cases |
| 2026-03-23 | 18 | Copilot | Tightened the remaining spec contracts: exact operator-decision validation, precedence rules, scope traceability persistence, and blocking behavior for unsplittable mixed-scope receipts |
| 2026-03-23 | Restart 0 | Copilot | Neue Neustart-Baseline: Excel aus produktivem Laufzeitpfad ausgeschlossen, autoritative Source-of-Truth-Kette definiert, offene Blocking-Fragen fuer den sauberen Neuanfang markiert |
| 2026-03-23 | Restart 1 | Copilot | Zielarchitektur fuer den Neustart festgelegt: C#-Domänenkern zuerst, OCR/Import und PDF als getrennte spaetere Schichten mit klaren Input-/Output-Vertraegen |
| 2026-03-24 | Restart 2 | Copilot | Restliche Neustart-Produktfragen aufgelöst: Bedeutung von fachlicher Stabilität, verbindlicher 2024-Vergleichsstand, Trennung Mieterabrechnung/Prüfbericht und Freigabepolitik für Blocker/Warnungen |
| 2026-03-24 | Restart 3 | Copilot | Kanonisches Eingabepaket, 2024-Testorakel, operatorseitiger Prüfbericht und Workbook-Migrationspolitik auf Spec-Niveau verbindlich gemacht; Neustart damit plan-ready |
| 2026-03-24 | Restart 4 | Copilot | Letzte außerhalb der Iterationen notierte Fachkommentare formal integriert: Gebäudeversicherung, Energieträger-Zuordnung und Schlüsselwerte in der Mieterabrechnung |

SessionId: 5ff61b4a-8355-4271-b526-26f6f9832807
