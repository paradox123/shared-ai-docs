# Nebenkostenabrechnung 2025 - Realdaten und Abrechnungspfad

## Zweck

Diese Spec beschreibt den operativen Pfad, um aus der bestehenden Codebasis und den real vorliegenden 2025er Unterlagen eine belastbare Nebenkostenabrechnung 2025 fuer Hauptstr. 2 zu erstellen.

Sie ist bewusst keine Wiederholung der Hauptspec, sondern eine operative 2025er Ausfuehrungsspec mit drei Schwerpunkten:

1. Statusklaerung der bestehenden Vorarbeiten und der Spec `2026-03-28 Nebenkostenabrechnung Blege und Messwerte`
2. Abgleich zwischen implementierter Import-/Abrechnungslogik und den echten 2025er Dateien
3. normative Festlegungen fuer den 2025er Datenstand, insbesondere Mietparteienwechsel, Strom-/Messwertbehandlung und manuelle Review-Strecke

## Bezug

Massgebliche Referenzen:

- Hauptspec: `2026-03-24 Nebenkostenabrechnung Applikation.md`
- Strom-/Warmwasser-Spec: `2026-03-27 Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1).md`
- Import-Spec Altstand: `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`
- Codebasis: `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung`
- Realdaten 2025: `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2025`

## Ergebnis der Statuspruefung der bestehenden Import-Spec vom 2026-03-28

### Befund

Die Spec `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md` ist **textlich weitgehend fertig**, aber **operativ nicht als abgeschlossen zu bewerten**.

### Begruendung

1. Die Datei enthaelt keine offenen `[MISSING ...]`- oder `[DECISION ...]`-Marker mehr.
2. Die Datei liegt jedoch weiterhin im regulären `_specs`-Ordner und nicht in `Completed`.
3. Wichtiger als der Ablageort: zentrale Teile der dort beschriebenen Vorverarbeitung sind in der aktuellen Codebasis fuer die echten 2025er Dateien noch nicht umgesetzt.

### Operative Bewertung

Die Alt-Spec ist damit in folgendem Sinn zu lesen:

- **fachlich weitgehend ausgearbeitet**
- **als Beschreibung des Zielbilds nuetzlich**
- **nicht als Nachweis eines fertig erreichten Importstands verwendbar**

Normative Folgerung dieser Spec:

- Die Alt-Spec bleibt Referenz fuer das gewollte Zielbild.
- Fuer die konkrete 2025er Erstellung gilt jedoch der tatsaechliche Code- und Realdatenstand dieser Spec.

## Analysierter Ist-Stand der Codebasis

### Bereits implementiert und testseitig abgesichert

Die Codebasis enthaelt bereits eine lauffaehige Jahreswechsel- und Importstruktur:

- `Nebenkosten.Import` mit den CLI-Schritten
  - `generate-scaffold-template`
  - `build-year-input`
  - `finalize-year-input`
- `Nebenkosten.Carryover` fuer Anfangsbestaende / `Rest aus Vorjahr`
- Rechenkern, Validierung, Rendering und PDF-Ausgabe
- Import-Tests fuer Scaffold, Tibber, ista-Monatswerte, Meter-Matching und Finalisierung
- Rechenkern-Tests fuer Leerstand, Unterjaehrigkeit, Strom-/Warmwasserlogik und Rendering

Verifizierter Teststand zum Zeitpunkt dieser Spec:

- `dotnet test Nebenkosten.sln` erfolgreich
- `Nebenkosten.Import.Tests`: 10/10 gruen
- `Nebenkosten.Tests`: 53/53 gruen

### Fachlich relevante, bereits tragende Eigenschaften des Rechenkerns

Der bestehende Rechenkern deckt fuer 2025 bereits wichtige Anforderungen ab:

1. **Leerstand wird getragen**
   - leerstehende Nutzeinheiten erzeugen keine Mieterabrechnung
   - Personen-Umlagen rechnen fuer Leerstand mit 0 Personen

2. **unterjaehriger Einzug/Auszug wird getragen**
   - schluesselbasierte Kosten werden zeitanteilig proratiert
   - verbrauchsbasierte Kosten werden nicht zeitanteilig geraten, sondern aus den Messwerten gebildet

3. **manuelle Stromablesungen werden als Stichtagspaare verarbeitet**
   - fuer direkte Wohnungsstromzaehler ist genau diese Logik fuer NE1 in 2025 relevant

4. **Stromtarife werden be_id-bezogen verarbeitet**
   - operative `stromtarife[]` benoetigen keine Zaehlerspur im End-JSON
   - fuer die Importphase existiert aktuell aber noch eine technische Zaehlermatch-Annahme

### Aktuelle Grenzen der Implementierung

Die operative Grenze liegt nicht im Rechenkern, sondern fast vollstaendig in der Vorverarbeitung der echten 2025er Unterlagen.

Aktuell implementiert die Importstrecke real nur:

- native Textgewinnung ueber `pdftotext`
- Dokumentklassifikation ueber einfache Namens-/Textheuristiken
- Parser fuer
  - `tibber_invoice`
  - `ista_monthly_export`
- Review-Ausgabe fuer alles, was nicht automatisch verarbeitet werden kann

Nicht implementiert oder fuer 2025 real nicht ausreichend sind aktuell:

1. OCR fuer bildbasierte PDFs
2. Segmentierung von Sammelbelegen (`Belege_BE1`, `Belege_BE2`, `Belege_Liegenschaft`)
3. Parser fuer allgemeine Belege / Versicherungen / Oelbeleg
4. Parser fuer `ista_period_or_snapshot`
5. robuste Tibber-Extraktion fuer reale 2025er Rechnungen mit Monatssektionen, Verbrauchsanpassungen und Zaehlerwechsel
6. Klassifikation des Dokuments `026490450 - AQ -2025-NE0000(P621450654).pdf`

## Realdatenanalyse 2025

Im Quellordner wurden 16 PDFs gefunden.

### Gruppe A: Tibber-Rechnungen

Gefundene Dateien:

- `Belege/Rechnung_1167054681.pdf`
- `Belege/Rechnung_1167054673.pdf`
- `Belege/Rechnung_1167054194.pdf`
- `Belege/Rechnung_1167054608.pdf`
- `Belege/Rechnung_1167054756.pdf`

Beobachtungen aus den realen Dokumenten:

1. Es existieren mindestens zwei unterschiedliche Tibber-Zaehlernummern in 2025:
   - `1ISK0078261075`
   - `1ISK0094903173`

2. Die Rechnungen liegen nicht durchgaengig im vom aktuellen Parser erwarteten Format `dd.MM.yyyy - dd.MM.yyyy` als globalem Rechnungszeitraum vor.

3. Reale Rechnungen enthalten teils **Verbrauchsanpassungen aus frueheren Perioden**.
   - Beispiel `Rechnung_1167054194.pdf`:
     - Uebersicht: `Kosten Stromverbrauch fuer Juni 2025, enthaelt Verbrauchsanpassungen aus frueheren Perioden`
     - Detailteil: separate Untersektion `Juni 2025` mit `615,32 kWh` und `Durchschnittspreis 19,70 ct/kWh`
   - Beispiel `Rechnung_1167054756.pdf`:
     - Sammelrechnung fuer `1. Aug. 2025 - 30. Sept. 2025`
     - enthaelt negative Anpassungen fuer Juni und Juli
     - enthaelt getrennte Monatssektionen fuer August und September

4. Daraus folgt fachlich zwingend:
   - Die Tarifableitung darf **nicht** aus der Uebersichtssumme des Stromverbrauchsblocks erfolgen, wenn dieser Anpassungen aus anderen Perioden enthaelt.
   - Stattdessen ist die **monatsbezogene Detailsektion** der Rechnung massgeblich.

### Gruppe B: Messwerte / ista-Dokumente

Gefundene Dateien:

- `Messwerte/Ablesungen24_25.pdf`
- `Messwerte/Monatswerte - 2025 -  - NE0001(P621593463).pdf`
- `Messwerte/026490450 - AQ -2025-NE0000(P621450654).pdf`

Beobachtungen:

1. `pdftotext` liefert fuer `Ablesungen24_25.pdf` und fuer die `Monatswerte`-Datei im aktuellen Lauf keine auswertbaren Textdaten.
2. Der aktuelle Importcode verfuegt ueber **keine OCR-Stufe**, obwohl die Alt-Spec dies als Zielbild vorsieht.
3. Das Dokument mit `AQ` im Dateinamen wird aktuell als `generic_invoice` behandelt, obwohl es sehr wahrscheinlich fachlich eine Ablese-/Ablesequittungsquelle ist.

Normative Folgerung:

- Die reale 2025er Messwertstrecke ist mit dem aktuellen Code **nicht automatisch extrahierbar**.
- Fuer 2025 ist daher eine manuelle oder extern per OCR vorbereitete Ueberfuehrung dieser Dokumente in `ablesungen[]` erforderlich.

### Gruppe C: Kostenbelege / Versicherungen / Sammelbelege

Gefundene Dateien:

- `Belege/Belege_BE1.pdf`
- `Belege/Belege_BE2.pdf`
- `Belege/Belege_BE2_II.pdf`
- `Belege/Belege_Liegenschaft.pdf`
- `Belege/GebaeudeversicherungI.pdf`
- `Belege/GebaeudeversicherungII.pdf`
- `Belege/GebaeudeversicherungIII.pdf`
- `Belege/Oel_25.pdf`

Beobachtungen:

1. Diese Dokumente werden aktuell zwar klassifiziert, aber nicht operativ geparst.
2. Sammelbelege werden derzeit nicht in logische Einzelbelege segmentiert.
3. Die Versicherungsdokumente werden aktuell nur als `generic_invoice` in den Review-Pfad gegeben.
4. Der Oelbeleg ist fuer die Brennstoffkosten 2025 relevant, aber ebenfalls nur Review-Material.

## Experimenteller Reallauf gegen die 2025er Quellen

Ein Probelauf von `build-year-input` gegen den echten 2025er Ordner wurde in einem Temp-Verzeichnis ausgefuehrt.

### Ergebnis

- Der Lauf endet technisch erfolgreich.
- Operativ entsteht jedoch fuer **alle 16 von 16 Dokumenten** ein Review-Eintrag.
- Es wurde im Reallauf **kein einziges 2025er Dokument automatisch bis zur final verwendbaren operativen Struktur uebernommen**.

### Bedeutung

Der Importpfad ist damit fuer 2025 aktuell nicht "fertig", sondern nur als:

- Scaffold-/Manifest-Erzeuger
- und als Review-Backbone

verwendbar.

## Normative Festlegungen fuer den 2025er Datenstand

### 1. Mietparteien 2025

### 1.1 Unveraenderte Fortfuehrung als Default

Mangels gegenteiliger Information werden die Mietparteien von NE2, NE3, NE4 und NE5 gegenueber 2024 unveraendert fortgefuehrt.

### 1.2 NE1: Leerstand und Neueinzug

Fuer NE1 gilt verbindlich fuer 2025:

- vom `2025-01-01` bis einschliesslich `2025-03-31`: **Leerstand / keine Mietpartei**
- ab `2025-04-01`: neue Mietpartei **Ingeborg Hainz**

Normative Abbildung im 2025er Input:

- die 2024er Mietpartei `Kraft / Huehne` darf **nicht** als 2025 aktive Mietpartei in `mietparteien[]` fortgeschrieben werden
- fuer Ingeborg Hainz wird eine neue 2025er Mietpartei angelegt, empfohlen mit einer personbezogenen ID wie `mp-ne1-hainz`
- `zugeordnete_nu = ["NE1"]`
- `einzug = 2025-04-01`
- `auszug = null`

Normative Festlegung:

- die Mietpartei Ingeborg Hainz ist fuer 2025 mit `1 Person` anzulegen

### 2. Direkter Strom NE1

Vom Nutzer vorgegebene 2025er Tatsache:

- Mietpartei Ingeborg Hainz zieht am `2025-04-01` in NE1 ein
- am `2025-03-29` hatte Stromzaehler `34877025` den Messwert `34684 kWh`

Normative Abbildung:

- der bestehende NE1-Stromzaehler `z-strom-ne1` mit `zaehlernummer = "34877025"` bleibt der operative Wohnungsstromzaehler fuer NE1
- es ist eine manuelle Ablesung mit
  - `zaehler_id = "z-strom-ne1"`
  - `quelle = "manuell"`
  - `ne_id = "NE1"`
  - `stichtag = 2025-03-29`
  - `messwert = 34684`
  anzulegen

Diese Ablesung ist die fachlich massgebliche Anfangsablesung fuer die 2025er Teilperiode von Ingeborg Hainz.

Weitere zwingende Voraussetzung:

- die korrespondierende Endablesung fuer `z-strom-ne1` ist aus dem manuellen Ableseprotokoll zum `2025-12-31` zu uebernehmen:
  - `zaehler_id = "z-strom-ne1"`
  - `quelle = "manuell"`
  - `ne_id = "NE1"`
  - `stichtag = 2025-12-31`
  - `messwert = 35005.6`

Damit ergibt sich fuer die Mietperiode von Ingeborg Hainz 2025 ein direkter Stromverbrauch NE1 von:

- `35005.6 - 34684.0 = 321.6 kWh`

### 3. Stromtarife BE1 / Tibber

### 3.1 Grundregel

Fuer 2025 werden operative `stromtarife[]` fuer `be1` aus belastbaren Tarifquellen erzeugt, nicht aus `kostenbelege[]` mit `kostenart_id = "strom"`.

Mit dem nun vorliegenden Vertragsdatensatz gilt fuer BE1 zusaetzlich:

- CHECK24 Vertragsnummer `28632852`
- Vertragskontonummer `12004642899`
- Lieferbeginn `2025-03-03`
- Rueckmeldung des Lieferanten: `Grüüün`
- jaehrlicher Grundpreis brutto `216.26 EUR`
- Arbeitspreis brutto `22.66 ct/kWh`

Dieser Vertragstarif ist fuer BE1 ab `2025-03-03` als kanonische Tarifquelle zu behandeln.

### 3.2 Tibber nur als Plausibilisierung

Die Tibber-Rechnungen 2025 enthalten weiterhin fachlich nuetzliche Monatsdetails, sind fuer die operative 2025er Tarifkette von `be1` aber **nicht** die primaere Tarifquelle, sobald der vertragliche Vattenfall-/Grüüün-Pfad feststeht.

Wenn Tibber-Rechnungen fuer 2025 als Zusatz- oder Plausibilisierungsquelle herangezogen werden, gilt:

- die tarifliche Ableitung fuer einen Monat erfolgt ausschliesslich aus der **dedizierten Monatssektion** (z. B. `Juni 2025`, `August 2025`, `September 2025`)
- die Uebersichtssumme `Kosten Stromverbrauch ... enthaelt Verbrauchsanpassungen ...` darf **nicht** direkt als Monatskostenbasis verwendet werden
- Tibber-PDFs duerfen fuer `be1` nicht zusaetzlich als operative `stromtarife[]` fuer Zeitraeume importiert werden, die bereits durch Vattenfall bzw. Grüüün normativ abgedeckt sind
- die automatische Tibber-Tariferzeugung des aktuellen `build-year-input` ist fuer den 2025er Operativlauf daher nur fuer explizit freigegebene Restzeiträume zulaessig

### 3.3 Abweichende Tibber-Zaehlernummern

Die Quellenlage ist derzeit widerspruechlich:

- in vier Tibber-Rechnungen 2025 wird `1ISK0078261075` genannt
- in `Rechnung_1167054756.pdf` wird dagegen `1ISK0094903173` genannt
- fachliche Vorgabe des Nutzers ist, dass `1ISK0078261075` der korrekte Zaehler fuer die BE1-Stromkette ist und kein echter Zaehlerwechsel stattgefunden hat

Normative Festlegung:

- `1ISK0078261075` ist als kanonische Zaehlernummer zu behandeln
- die in `Rechnung_1167054756.pdf` genannte Nummer `1ISK0094903173` ist als Dokumentfehler zu behandeln
- fuer Import, Review und finale Tarifanlage ist durchgaengig `1ISK0078261075` zu verwenden

### 3.4 Fehlende Stromperioden

Aus dem vorliegenden Ordner und den Nutzerhinweisen ergibt sich:

- fuer Stromperioden ist nicht zwingend eine Monatsrechnung erforderlich; als Quelle kommen auch Vertrags-/Tarifdaten in Betracht
- fuer BE1 liegt in `data/2024/input_tariff_from_excel.json` ein bestehender Tarifdatensatz vor
- dieser Datensatz deckt fuer BE1 jedoch nur den Zeitraum bis einschliesslich `2025-02-14` ab (`gueltig_bis = 2025-02-14`)
- zusaetzlich liegt fuer BE1 ein CHECK24-/Grüüün-Vertragstarif mit Lieferbeginn `2025-03-03` vor
- aus den 2025er Tibber-Unterlagen sind belastbare Monats- bzw. Teilperiodeninformationen fuer `2025-03-02` bis `2025-09-30` erkennbar

Damit ist normativ festgelegt:

- `data/2024/input_tariff_from_excel.json` darf als Tarifquelle fuer BE1 nur fuer den dort tatsaechlich abgedeckten Zeitraum verwendet werden
- der CHECK24-/Grüüün-Tarif ist fuer BE1 ab `2025-03-03` als operative Tarifquelle zu verwenden
- fehlende 2025er Tarifzeiträume duerfen nicht mit pauschalen Annahmen aus 2024 ueberschrieben werden

- der Vattenfall-Vertrag ist die belastbare Tarifquelle fuer BE1 im Zeitraum `2025-02-15` bis `2025-03-01`
- der Uebergangstag `2025-03-02` wird aus den 2025er Tibber-Unterlagen abgedeckt
- die Nutzerangabe `2024-01-18` bis `2025-03-31` ist als Kontext zur Lieferantenkette zu dokumentieren, nicht als operative Datumslogik fuer die finale 2025er Tarifkette
- die abweichende Datierung im Fixture `data/2024/input_tariff_from_excel.json` ist als Fixture-/Datumsfehler zu behandeln und fuer die 2025er operative Tarifkette entsprechend zu korrigieren
- fuer die finale `input.reviewed.json` ist genau **eine** operative Tarifkette fuer `be1` zu hinterlegen; parallele, sich zeitlich ueberlappende Tibber-Monatstarife neben dem Vattenfall-/Grüüün-Vertragspfad sind unzulaessig
- daraus folgt fuer den Operativlauf 2025: Tibber-Rechnungen bleiben Review-/Plausibilisierungsquellen und muessen entweder vor dem automatischen Tarifimport ausgeschlossen oder die daraus erzeugten Monats-Tarife vor Finalisierung wieder entfernt werden

Die bisherigen Marker fuer `Oktober`, `November` und `Dezember 2025` entfallen durch den nun dokumentierten Vertragstarif ab `2025-03-03`.

### 4. Messwerte 2025 ausser Tibber

### 4.1 ista-Monatswerte NE1

Die Datei `Monatswerte - 2025 -  - NE0001(P621593463).pdf` ist fuer Heizkosten-/Warmwasser-/ggf. Kaltwasserablesungen relevant, kann mit dem aktuellen Import aber nicht automatisch gelesen werden.

Normative Festlegung:

- 2025 wird fuer dieses Dokument keine blinde automatische Ableitung verwendet
- entweder
  - das Dokument wird per OCR in auswertbaren Text ueberfuehrt und anschliessend fachlich verifiziert
  - oder die Messwerte werden manuell in die operative `input.reviewed.json` uebernommen

### 4.2 Ablesungen24_25.pdf

Diese Datei ist voraussichtlich fuer manuelle Zaehlerablesungen und Jahresgrenzen relevant.

Normative Festlegung:

- die Datei ist fuer 2025 als primaere Quelle fuer Jahresanfangs-/Jahresendwerte der manuellen Stromzaehler zu pruefen
- solange keine belastbare Extraktion vorliegt, bleiben die betreffenden Stichtage blockierend offen

### 4.3 AQ-Dokument

Das Dokument `026490450 - AQ -2025-NE0000(P621450654).pdf` ist fuer die aktuelle Implementierung falsch bzw. zu generisch eingeordnet.

Normative Festlegung:

- `026490450 - AQ -2025-NE0000(P621450654).pdf` ist die Hauptquelle der Ablesewerte fuer das komplette Jahr 2025
- Ausnahme ist NE1: wegen des unterjaehrigen Einzugs von Ingeborg Hainz muessen die Verbrauchswerte fuer NE1 periodisch bzw. monatlich betrachtet werden
- fuer NE1 ist dafuer die Datei `Monatswerte - 2025 -  - NE0001(P621593463).pdf` die spezialisierte Zusatzquelle

### 5. Belege 2025 ausser Strom

Fuer 2025 muessen die folgenden Kostenbereiche weiterhin manuell bzw. review-gestuetzt in die operative `input.reviewed.json` eingepflegt werden:

- Liegenschaftsbelege
- BE1-Sammelbelege
- BE2-Sammelbelege
- Gebaeudeversicherungen
- Oelbeleg / Brennstoffkosten

Normative Abbildung:

- Sammelbelege werden fachlich in logische Einzelbelege zerlegt
- jeder operative `kostenbeleg` behaelt eine nachvollziehbare Herkunft aus Datei und Seitenbereich ausserhalb des End-JSON
- Versicherungen bleiben vertragsbezogen gemaess Hauptspec
- Oelkosten bleiben BE1-Brennstoffkosten mit gesonderter Carryover-/Restlogik

### 6. Carryover und Restbestaende

Die 2025er Verarbeitung setzt weiterhin einen gueltigen Anfangsbestandspfad voraus.

Normative Festlegung:

- die Restmengen 2024 -> 2025 sind aus dem manuellen Ableseprotokoll zu uebernehmen:
  - Heizoel Rest `3500 l`
  - Holz Rest `40 m3`
  - Pellets Rest `1500 kg`

Mit `Bewertungsbasis` bzw. `Restwert-Herleitung` ist hierbei der **Geldwert** dieser Restmengen gemeint, also entweder:

- ein bereits belastbar vorliegender Restwert je Energietraeger
- oder eine Herleitung ueber den Durchschnittspreis aus Anfangsbestand und Zugaengen des Vorjahres

Normative Festlegung:

- die Bewertungsbasis fuer die Carryover-Uebernahme 2024 -> 2025 ist aus den Vorjahreskosten und Vorjahresmengen zu berechnen
- primaere operative Referenz dafuer ist die Arbeitsmappe `Nebenkostenabrechnung_2024.xlsx`, Tabellenblatt `Betriebskosten`
- `data/2024/input_tariff_from_excel.json` ist dafuer **nicht** ausreichend als Alleinquelle, weil dort zwar aggregierte Brennstoffkostenbelege, aber keine belastbaren Restmengen-/Restwertzeilen je Energietraeger enthalten sind
- die fachliche Behandlungsregel folgt der Import-Spec `2026-03-28 Nebenkostenabrechnung Blege und Messwerte.md`, insbesondere der dort beschriebenen Restwert-/Durchschnittspreislogik

Die 2024er Arbeitsmappe enthaelt die fuer 2025 erforderlichen Opening-Carryover-Werte bereits explizit:

- Tabellenblatt `Betriebskosten`, Zeile 32: `Öl Rest aus Vorjahr`, Menge `3500`, Betrag `3395.37 EUR`
- Tabellenblatt `Betriebskosten`, Zeile 33: `Holz aus Vorjahr`, Menge `40`, Betrag `2242.40 EUR`
- Tabellenblatt `Betriebskosten`, Zeile 34: `Pellets aus Vorjahr`, Menge `1.5` t entsprechend `1500 kg`, Betrag `425.86 EUR`

Diese drei Zeilen sind fuer die 2025er Carryover-Uebernahme als kanonische Ausgangswerte zu behandeln. Die spiegelbildlichen Endbestandszeilen `25` bis `27` bestaetigen dieselben Werte zum `2024-12-31`.

Beispielhaft gilt fuer das Verstaendnis:

- wenn 2024 fuer einen Energietraeger `10.000 EUR` Kosten angefallen sind und davon wertmaessig `4.000 EUR` als Restbestand ins Folgejahr uebergehen, dann werden `6.000 EUR` in 2024 verbraucht und `4.000 EUR` als `Rest aus Vorjahr` nach 2025 uebernommen

Ohne diesen Schritt kann zwar ein technischer Scaffold-Lauf erfolgen, aber keine vollstaendige operative 2025er Kostenbasis.

### 7. Vorauszahlungen

Fuer rechtlich brauchbare Einzelabrechnungen muessen die 2025er Vorauszahlungen je Mietpartei vorliegen.

Normative Festlegung:

- fuer Ingeborg Hainz gilt ab `2025-04-01` eine monatliche Vorauszahlung von `350 EUR`
- fuer die bestehenden Mietparteien werden die monatlichen Vorauszahlungswerte aus `data/2024/input_tariff_from_excel.json` unveraendert fortgefuehrt:
  - NE2 / `mp-ne2`: `230 EUR` monatlich
  - NE3 / `mp-ne3`: `125 EUR` monatlich
  - NE4 / `mp-ne4`: `107.50 EUR` monatlich
  - NE5 / `mp-ne5`: `0 EUR` monatlich

## Operativer Zielprozess fuer 2025

### Phase 1: Scaffold und Stammdatenpflege

1. 2024er Input als Basis in ein 2025er Scaffold uebernehmen
2. Mietparteien 2025 fachlich korrigieren
3. Zaehlerliste 2025 fachlich pruefen
4. Carryover fuer 2025 anhaengen bzw. bestaetigen

### Phase 2: Rohimport und Review-Artefakte

1. `build-year-input` gegen den 2025er Quellordner laufen lassen
2. `import-manifest.json` und `review-output.json` als Arbeitsliste verwenden
3. reale Belege und Messwerte manuell bzw. OCR-gestuetzt in `input.reviewed.json` nachpflegen

### Phase 3: Finalisierung

1. alle Review-Punkte schliessen
2. alle blockierenden `[MISSING ...]`-Punkte aufloesen
3. `finalize-year-input` ausfuehren
4. mit dem finalen `input.json` die Einzelabrechnungen erzeugen

## Akzeptanzkriterien dieser Spec

Diese Spec ist fuer 2025 fachlich ausreichend, wenn sie als Arbeitsgrundlage zu folgendem Ergebnis fuehrt:

1. Der Stand der Alt-Spec vom `2026-03-28` ist klar eingeordnet: fachlich weit, operativ nicht erledigt.
2. Die 2025er Mietparteienliste bildet NE1 korrekt als Leerstand bis `2025-03-31` und Ingeborg Hainz ab `2025-04-01` ab.
3. Die manuelle Anfangsablesung fuer NE1-Strom `34877025 = 34684 kWh` zum `2025-03-29` ist explizit als operative Pflichtquelle festgelegt.
4. Die reale Importgrenze ist explizit dokumentiert: 16/16 Dokumente sind im aktuellen Reallauf review-pflichtig.
5. Tibber-Rechnungen mit Verbrauchsanpassungen werden nicht ueber die Uebersichtssumme fehlinterpretiert, sondern monatsweise aus den Detailsektionen behandelt.
6. Die operative Tarifkette fuer `be1` ist ohne Ueberlappung definiert, und Tibber-Rechnungen werden nicht versehentlich parallel als konkurrierende Monatstarife importiert.
7. Die Carryover-Uebernahme 2024 -> 2025 ist nicht nur logisch beschrieben, sondern mit konkreten Restmengen und Restwerten aus der 2024er Arbeitsmappe belegt.
8. Die bestehende Codebasis wird nicht falscherweise als vollautomatischer 2025er Import dargestellt, sondern korrekt als Rechenkern plus Review-gestuetzte Vorverarbeitung beschrieben.

## Abgrenzung

Diese Spec definiert nicht erneut:

- die allgemeine Kostenarten-Matrix
- die Grundlogik der Heiz-/Warmwasser-/Versicherungsumlage
- das PDF-Layout der Einzelabrechnung
- oder eine neue Zielarchitektur fuer den Import jenseits des fuer 2025 noetigen operativen Vorgehens

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-09 | 0 | User | Anfrage zur Erstellung der Nebenkostenabrechnung 2025, Hinweis auf Mieterwechsel NE1 und bestehende Vorarbeiten |
| 2026-04-09 | 1 | Codex | Code-, Test- und Realdatenanalyse; operative 2025er Spec mit Datenstand, Importgrenzen und Blockern erstellt |
| 2026-04-09 | 2 | Codex | Nutzerantworten aus `=>`-Kommentaren eingearbeitet; belastbare Aussagen normativ uebernommen und unvollstaendige Antworten in praezise Rest-Blocker umformuliert |
| 2026-04-09 | 3 | Codex | CHECK24-/Grüüün-Tarif fuer BE1, Fortgeltung der Vorauszahlungen der Bestandsmieter und Erlaeuterung der Carryover-Bewertungsbasis eingearbeitet |
| 2026-04-09 | 4 | Codex | Neue Nutzerantworten zu Tibber-Dokumentfehler, Vattenfall-Zwischenzeitraum und Herleitung der Carryover-Bewertung normativ eingearbeitet |
| 2026-04-09 | 5 | Codex | Quellenabgleich gegen Code und 2024er Arbeitsmappe: Carryover-Quelle auf Excel-Betriebskostenblatt verengt und operative Tarifregel gegen ueberlappende Tibber-Monatstarife geschaerft |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
