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

Blockierend offen:

- `[MISSING Personenanzahl der Mietpartei Ingeborg Hainz]`

Ohne diese Angabe ist insbesondere die korrekte Muellumlage nicht abschliessend bestimmbar.

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

- `[MISSING korrespondierende Endablesung 2025 fuer z-strom-ne1, falls sie nicht belastbar aus den Messwert-Unterlagen 2025 extrahiert wird]`

Ohne Endablesung kann der direkte Stromverbrauch NE1 fuer 2025 nicht berechnet werden.

### 3. Stromtarife BE1 / Tibber

### 3.1 Grundregel

Die Tibber-Rechnungen erzeugen operative `stromtarife[]` fuer `be1`, nicht `kostenbelege[]` mit `kostenart_id = "strom"`.

### 3.2 Monatsableitung statt Uebersichtssumme

Wenn eine Tibber-Rechnung Verbrauchsanpassungen aus frueheren Perioden enthaelt, gilt:

- die tarifliche Ableitung fuer einen Monat erfolgt ausschliesslich aus der **dedizierten Monatssektion** (z. B. `Juni 2025`, `August 2025`, `September 2025`)
- die Uebersichtssumme `Kosten Stromverbrauch ... enthaelt Verbrauchsanpassungen ...` darf **nicht** direkt als Monatskostenbasis verwendet werden

### 3.3 Zaehlerwechsel / Lieferstellenkontinuitaet

Bis zum Nachweis des Gegenteils gilt fuer 2025 folgende Arbeitsannahme:

- `1ISK0078261075` und `1ISK0094903173` repraesentieren dieselbe fachliche Stromlieferung fuer die BE1-Stromkostenkette, nur mit geaenderter Zaehlernummer
- die operative Tarifzielstruktur bleibt deshalb `stromtarife[]` fuer `be1`

Diese Annahme ist vor Finalisierung gegenzupruefen:

- `[REVIEW Bestaetigen, dass der Zaehlerwechsel 1ISK0078261075 -> 1ISK0094903173 kein Scope-Wechsel, sondern nur ein technischer Zaehlerwechsel innerhalb derselben BE1-Lieferstelle ist]`

### 3.4 Fehlende Stromperioden

Aus dem vorliegenden Ordner sind derzeit erkennbar:

- Teilperiode `2025-03-02` bis `2025-03-31`
- April 2025
- Mai 2025 ist **nicht** als eigener sauberer Monatsbeleg vorhanden
- Juni 2025
- Juli 2025
- August 2025
- September 2025

Blockierend offen bleiben damit aktuell mindestens:

- `[MISSING belastbare Stromkostenquelle fuer BE1 vom 2025-01-01 bis 2025-03-01]`
- `[MISSING belastbare Stromkostenquelle fuer Mai 2025]`
- `[MISSING belastbare Stromkostenquelle fuer Oktober 2025]`
- `[MISSING belastbare Stromkostenquelle fuer November 2025]`
- `[MISSING belastbare Stromkostenquelle fuer Dezember 2025]`

Wenn diese Monate in anderen Belegen oder Konto-/Anbieterunterlagen vorhanden sind, muessen sie vor Finalisierung in die 2025er Tarifkette aufgenommen werden.

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

- fuer die 2025er Bearbeitung ist dieses Dokument fachlich wie eine potentielle Ablese-/Messwertquelle zu behandeln, nicht wie ein normaler Kostenbeleg
- seine inhaltliche Rolle ist vor Finalisierung zu klaeren

Offen:

- `[REVIEW fachliche Bedeutung des Dokuments 026490450 - AQ -2025-NE0000(P621450654).pdf bestaetigen]`

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

Blockierend offen:

- `[MISSING bestaetigtes carryover-output.json oder belastbare Restbasis 2024 -> 2025 fuer Heizoel/Holz/Pellets]`

Ohne diesen Schritt kann zwar ein technischer Scaffold-Lauf erfolgen, aber keine vollstaendige operative 2025er Kostenbasis.

### 7. Vorauszahlungen

Fuer rechtlich brauchbare Einzelabrechnungen muessen die 2025er Vorauszahlungen je Mietpartei vorliegen.

Blockierend offen:

- `[MISSING Vorauszahlungen 2025 je Mietpartei, insbesondere fuer Ingeborg Hainz ab 2025-04-01]`

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
6. Fehlende Daten fuer Stromperioden, Vorauszahlungen, Personenanzahl und Carryover sind als blockierende Punkte sichtbar gemacht.
7. Die bestehende Codebasis wird nicht falscherweise als vollautomatischer 2025er Import dargestellt, sondern korrekt als Rechenkern plus Review-gestuetzte Vorverarbeitung beschrieben.

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

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
