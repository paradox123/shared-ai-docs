# Iteration 0

Ich bin Vermieter der Hauptstr. 2 in 36381 Schlüchtern und möchte den Prozess der Nebenkostenabrechnung automatisieren. Bisher habe ich diese Abrechnung manuell erstellt und in '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung' nach Jahren abgelegt. Basis für die Nebenkostenabrechnung war in den Jahren 2022 und 2023 die Unterlagen der Firma ista und im Jahre 2024 meine eigene Excel Tabelle '/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/Nebenkostenabrechnung_2024.xlsx' (Excel2024).

Für das Jahr 2025 möchte ich nun eine Anwendung zur Abrechnung erstellen. Diese Spezifikation dient der fachlichen Beschreibung dieser Anwendung.

## Gesetzliche Anforderungen an eine Nebenkostenabrechnung

> Rechtsgrundlagen: § 556 ff. BGB, Betriebskostenverordnung (BetrKV), Heizkostenverordnung (HeizkostenV)

Hinweis zur Begrifflichkeit: In den gesetzlichen Anforderungen wird der Rechtsbegriff "Mieter" verwendet. Im Domänenmodell dieser Spezifikation entspricht dies der **Mietpartei**.

Eine gültige Nebenkostenabrechnung muss folgende **vier Pflichtangaben** enthalten (BGH-Rechtsprechung):

1. Aufstellung aller umlagefähigen Gesamtkosten nach Kostenart
2. Verteilerschlüssel mit Erläuterung (z. B. Wohnfläche, Verbrauch)
3. Berechnung des Mieteranteils aus den Gesamtkosten
4. Abzug der geleisteten Vorauszahlungen → Saldo (Nachzahlung oder Guthaben)

**Fristen (§ 556 Abs. 3 BGB):**
- Abrechnung muss dem Mieter innerhalb von **12 Monaten** nach Ende des Abrechnungszeitraums zugehen; sonst keine Nachforderung möglich
- Mieter hat danach weitere **12 Monate** Zeit für Einwände

**Umlagefähige Kosten (§ 2 BetrKV):** Grundsteuer, Wasser/Abwasser, Heizung, Warmwasser, Müll, Hausreinigung, Gartenpflege, Beleuchtung, Schornsteinreinigung, Versicherungen, Hauswart, sonstige vertraglich vereinbarte Kosten. Verwaltungskosten und Instandhaltung sind **nicht** umlagefähig.

**Heizkosten (HeizkostenV):** Bei Zentralheizung müssen 50–70 % der Heizkosten verbrauchsabhängig abgerechnet werden; bei Verstoß darf der Mieter 15 % kürzen.

## Basisdaten Hauptstr. 2
Die Nebenkostenabrechnung für das Objekt Hauptstr. 2 basiert auf zwei verschiedenen Berechnungseinheiten (BE), die insgesamt 5 Nutzeinheiten (NE) zusammenfassen und sich insbesondere durch die unterschiedlichen Energieträger und Verteilerschlüssel unterscheiden.
Die nachfolgende Aufstellung enthält die Berechnungseinheiten und deren zugeordnete Nutzeinheiten samt deren Schlüsselwerten auf Objektebene und innerhalb der Berechnungseinheit in Klammern.

Hinweis: Die abstrakte Modellbeschreibung der Entitäten (Objekt, BE, NE, Mietpartei) ist im Abschnitt *Desired State / Domänenmodell* definiert.

### Berechnungseinheit 1: Gebäude Ost (Energieträger: Öl und Wärmepumpe)
Die Nutzeinheiten (NE1 und NE2) im Gebäude Ost werden mit Öl beheizt, die Warmwasseraufbereitung erfolgt über eine strombetriebene Wärmepumpe.
1. Gebäude Ost - Loftwohnung (Nutzeinheit 1 / NE1): Wohnfläche 180 m², Verteilschlüssel Wohnfläche 28 % (gesamt) bzw. 69 % (innerhalb Gebäude Ost), 2 Personen (20 % Personenanteil), Nutzfläche 180 m² (13 % der Gesamtnutzfläche).
2. Gebäude Ost - Wohnung 2 (Nutzeinheit 2): Wohnfläche 80 m², Verteilschlüssel Wohnfläche 12 % (gesamt) bzw. 31 % (innerhalb Gebäude Ost), 2 Personen (20 % Personenanteil), Nutzfläche 80 m² (6 % der Gesamtnutzfläche).

### Berechnungseinheit 2: Gebäude Nord und Gebäude West (Energieträger: Holz und Pellets)												
Die Nutzeinheiten im Gebäude Nord und Gebäude West werden mit Holz und Pellets beheizt.
1. Gebäude Nord - Gesindehaus (Nutzeinheit 3): Wohnfläche 60 m², Verteilschlüssel Wohnfläche 9 % (gesamt) bzw. 15 % (innerhalb dieser Berechnungseinheit), 1 Person (10 % Personenanteil), Nutzfläche 60 m² (4 % der Gesamtnutzfläche).
2. 1-Zimmer-Apartment (Nutzeinheit 4): Wohnfläche 34 m², Verteilschlüssel Wohnfläche 5 % (gesamt) bzw. 9 % (innerhalb dieser Berechnungseinheit), 1 Person (10 % Personenanteil), Nutzfläche 34 m² (3 % der Gesamtnutzfläche).
3. Gebäude West - Wohnhaus (Nutzeinheit 5): Wohnfläche 300 m², Verteilschlüssel Wohnfläche 46 % (gesamt) bzw. 76 % (innerhalb dieser Berechnungseinheit), 4 Personen (40 % Personenanteil), Nutzfläche 1000 m² (74 % der Gesamtnutzfläche).

Hinweis: siehe Excel2024 Worksheet "Allgemein"

### Begriffsdefinitionen
- **Objekt**: die gesamte Liegenschaft Hauptstr. 2
- **Berechnungseinheit (BE)**: eine Teilmenge von Nutzeinheiten mit gemeinsamer Kosten- oder Verbrauchslogik
- **Nutzeinheit (NE)**: die konkrete abrechenbare Einheit; alltagssprachlich häufig "Wohnung"
- **Mietpartei**: die abrechnungsrelevante Partei; im rechtlichen Sinne entspricht dies dem "Mieter"
- **Scope** (technisch) / **Bezug** (auf der Abrechnung): die Menge der Einheiten, auf die eine Kostenart umgelegt wird. Auf der mietergerichteten Einzelabrechnung wird `Scope` als **Bezug** ausgewiesen. Mögliche Scope-Typen: `Objekt`, `Berechnungseinheit`, `Vertrag`
- **Vertragsgruppe** (Scope-Typ `Vertrag`): die einem Versicherungsvertrag direkt zugeordneten Nutzeinheiten; Vertrag ist einer von drei Scope-Typen neben `Objekt` und `Berechnungseinheit`

### Schlüsselwerte
Folgende Schlüsselwerte sind der Mietpartei zuzordnen:
- Personen

Folgende Schlüsselwerte sind der Nutzeinheit zuzordnen:
- Wohnfläche
- Nutzfläche

### Kostenarten mit Schlüsselumlage
Hinweis: Die verbindliche Quelle für Scope und Umlageart ist die Kostenarten-Matrix (→ Abschnitt unten). Die nachfolgende Liste dient der Erläuterung.
Zur Kostenermittlung werden alle Belege einer Kostenart aufsummiert und anhand der genannten Schlüsselwerte anteilig auf den relevanten Scope umgelegt. Der relevante Scope kann je nach Kostenart das Objekt, eine Berechnungseinheit oder eine Vertragsgruppe (Scope-Typ `Vertrag`) sein.
Folgende Kostenarten werden anhand von Schlüsseln umgelegt:
- Gebäudeversicherung
- Grundsteuer
- Oberflächenwasser
- Müllabfuhr
- Betriebskosten Heizung

#### Ausnahme: Gebäudeversicherung (AXA-Verträge)

Die Gebäudeversicherung besteht aus drei einzelnen AXA-Verträgen mit direkter Zuordnung auf Teilmengen der NE:
- Versicherungsnummer 56003644342: Zuordnung auf NE4 und NE5
- Versicherungsnummer 56003644335: Zuordnung auf NE3
- Versicherungsnummer 56003644333: Zuordnung auf NE1 und NE2

Regel: Die Umlage erfolgt anhand der Wohnfläche innerhalb der jeweiligen Vertragsgruppe (Scope-Typ `Vertrag`).
Klarstellung: Für Versicherungsnummer 56003644342 wird der Umlageschlüssel nur aus NE4 und NE5 gebildet; NE3 bleibt trotz gleicher Berechnungseinheit unberücksichtigt, da ein eigener Vertrag (56003644335) besteht.
Es wird keine separate Berechnungseinheit für die Gebäudeversicherung gebildet.

Hinweis: Excel2024 verwendet als Nenner für die NE4-Umlage irrtümlich die BE2-Gesamtfläche (NE3+NE4+NE5 = 394 m²) statt der Vertragsgruppen-Fläche (NE4+NE5 = 334 m²). Die Spec-Berechnung gilt; diese Abweichung ist in den bekannten Abweichungen dokumentiert.


### Kostenarten-Matrix (verbindlich)

| Kostenart | Scope | Umlageart | Schlüssel/Verbrauch | Hinweis |
|---|---|---|---|---|
| Gebäudeversicherung | Vertrag (Vertragsgruppe) | Schlüssel | Wohnfläche (innerhalb Vertragsgruppe) | AXA-Verträge: 56003644342 -> NE4/NE5, 56003644335 -> NE3, 56003644333 -> NE1/NE2 |
| Grundsteuer | Objekt | Schlüssel | Wohnfläche | alle NE |
| Oberflächenwasser | Objekt | Schlüssel | Wohnfläche | alle NE |
| Müllabfuhr | Objekt | Schlüssel | Personen | alle NE |
| Betriebskosten Heizung | Berechnungseinheit | Schlüssel | Wohnfläche | nur NE der jeweiligen BE |
| Brennstoffkosten | Berechnungseinheit | Mischumlage | 30% Wohnfläche, 70% Heizverbrauch | je BE |
| Heiznebenkosten | Berechnungseinheit | Verbrauch | Heizverbrauch (HKV) | je BE |
| Verbrauchskosten Heizung | Berechnungseinheit | Verbrauch | Heizverbrauch (HKV) | je BE, falls separat ausgewiesen |
| Kalt- und Abwasser | Objekt | Verbrauch | Kaltwasserverbrauch | NE5 als Restverbrauch |
| Verbrauchskosten Warmwasser | Berechnungseinheit | Verbrauch | Warmwasserverbrauch | je BE |
| Strom | Berechnungseinheit | Verbrauch | Stromverbrauch | BE1 inkl. Warmwasseraufbereitung via Wärmepumpe |

Hinweis zur Vermeidung von Doppelzählung: Wenn "Verbrauchskosten Heizung" bereits in "Brennstoffkosten" oder "Heiznebenkosten" enthalten sind, wird die doppelte Position nicht zusätzlich angesetzt.
Die Kostenarten-Matrix ist die fachlich verbindliche Quelle für Scope und Umlageart; erläuternde Listen im Dokument dürfen ihr nicht widersprechen.


### Kostenarten mit Verbrauchsumlage - Messgeräte
Hinweis: Die verbindliche Quelle für Scope und Umlageart ist die Kostenarten-Matrix (→ Abschnitt oben). Die nachfolgende Liste dient der Erläuterung.
Zur Kostenermittlung werden alle Belege einer Kostenart aufsummiert und anhand der gemessenen Verbräuche anteilig auf die NE umgelegt.
Folgende Kostenarten enthalten ganz oder teilweise eine Verbrauchsumlage:
- Brennstoffkosten (Mischumlage: 70% Verbrauchsumlage, 30% Schlüsselumlage nach Wohnfläche)
- Heiznebenkosten
- Kalt- und Abwasser
- Strom
- Verbrauchskosten Warmwasser
- Verbrauchskosten Heizung
(siehe Excel2024 Worksheet Stammdaten)

Jede Nutzeinheit hat die folgenden Messgeräte zur Erfassung von Verbräuchen installiert:
- Kaltwasserzähler: misst die verbrauchte Menge kaltes Wasser in m³. Die Messwerte werden von der ista zur Verfügung gestellt.
- Warmwasserzähler: misst die verbrauchte Menge warmes Wasser in m³. Die Messwerte werden von der ista zur Verfügung gestellt.
- Heizkostenverteiler: misst die verbrauchte Menge Heizenergie in Verbrauchseinheiten. Ein Zähler ist an jedem Heizkörper installiert. Die Verbrauchseinheiten eines Messgerätes erhält man durch den Messwert * Umrechnungsfaktor, der spezifisch für jedes Messgerät von der ista definiert wurde (siehe Excel2024 Worksheet Messgeräte Spalte G).
- Stromzähler: misst die verbrauchte Menge Strom in kWh. Der Messwert wird einmal im Jahr und bei Aus- und Einzug manuell abgelesen und in einem Ableseprotokoll festgehalten (siehe Excel2024 Worksheet Ableseprotokoll Muster).

- Allgemein Hauptanschluss: Kaltwasserzähler für die gesamte Liegenschaft (alle NE)
- Allgemein Zähler Gebäude Ost: misst den verbrauchten Strom der BE1. Durch Abzug der Stromzählerwerte für NE1 und NE2 erhält man den verbrauchten Strom für die Warmwasseraufbereitung durch die Wärmepumpe, welche dann nach Verbrauch auf NE1 und NE2 umgelegt wird.

Hinweis: Zähler beziehen sich im Regelfall auf genau eine Nutzeinheit. Zähler mit Bezug auf eine Berechnungseinheit oder das gesamte Objekt sind Sonderfälle und müssen in der Berechnung explizit behandelt werden, z. B. der Hauptanschluss oder der Allgemein-Zähler Gebäude Ost für die Wärmepumpe.

Die Zähler geben jeweils einen Messwert zum Stichtag X aus. Beispiele für die Ableseprotokolle sind:
- Manuelles Ableseprotokoll: /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten_pipeline/fixtures/2024/20260314_121317.jpg
enthält die Spalten:
Berechnungseinheit | Nutzeinheit | Zählernummer | Messwert
- jährliches Ableseprotokoll der Firma ista: '/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten_pipeline/fixtures/2024/Ablesequittungen AZ 2024.pdf'
enthält Spalten: (siehe Erkläuterung im pdf)
- monatliches Ableseprotokoll der Firma ista: '/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten_pipeline/fixtures/2024/Monatswerte - 2024 -  - NE0001(P560620521).pdf'
enthält Spalten: (siehe Erkläuterung im pdf)

Der Verbrauch errechnet sich immer aus der Differenz der Messwerte zwischen dem Ende und dem Anfang der Abrechnungsperiode. Eine Abrechnungsperiode besteht im Allgemeinen aus 12 Monaten (Jan-Dez). Bei Ein- und Auszug ist diese kürzer, siehe Beispiel Kraft/Hühne in Excel2024.

Regel für Ein- und Auszug: Die zeitanteilige Abrechnung erfolgt monatsgenau. Der Einzugsmonat zählt ab Einzug voll mit, der Auszugsmonat bis Auszug ebenfalls als voller Monat. Verbrauchsgebundene Positionen werden nach tatsächlicher Messdifferenz der jeweiligen Periode berechnet.

Regel für manuelle Ablesungen: Für die Berechnung und für die Ausgabe werden immer zwei manuelle Ablesungen desselben Zählers herangezogen – und, falls der Zähler NE-bezogen ist, derselben Nutzeinheit –: eine zum Anfang und eine zum Ende des Abrechnungszeitraums bzw. der Teilperiode. Daraus ergeben sich `wert_alt`, `wert_neu` und die Differenz als Verbrauch.

#### Ausnahmen
- NE5 hat keinen eigenen Kaltwasserzähler. Der Verbrauch der NE5 errechnet sich durch NE5 = Allgemein Hauptanschluss - NE1 - NE2 - NE3 - NE4
- Brennstoffkosten werden im Verhältnis 70:30 auf die Nutzeinheiten umgelegt, wobei 
    - 30% anhand der Wohnfläche nach Schlüssel umgelegt werden
   - 70% anhand des Verbrauchs umgelegt werden

#### Fail-fast-Regeln
- Es werden keine stillen Annahmen, Schätzwerte oder Defaultwerte verwendet.
- Fehlende Pflichtwerte in Eingabedaten, Schlüsselwerten, Ablesungen oder Kostenbelegen führen zum sofortigen Abbruch mit einer eindeutigen Fehlermeldung.
- Ist eine Kostenart mehreren fachlich überlappenden Kategorien zuordenbar, muss die Zuordnung vor der Berechnung eindeutig aufgelöst werden; sonst Abbruch mit Fehlermeldung.
- Ergibt sich für einen abgeleiteten Verbrauch (z. B. Restverbrauch NE5) ein unplausibler oder negativer Wert, wird die Berechnung abgebrochen.
- Fehlen für verbrauchsabhängige Kostenarten die erforderlichen Messwerte für die betroffene Periode, wird die Berechnung abgebrochen.
 
#### Kostenberechnung
- Kosten sind in der Regel durch entsprechende Belege ausgewiesen, die der entsprechenden Kostenart zugeordnet werden, siehe Excel2024 Worksheet Betriebskosten. Hier sind die Belege nicht nur der Kostenart, sondern auch Berechnungseinheiten bzw. Nutzeinheiten zugeordnet. Ist die Scope-Zuordnung am Beleg leer, wird der Scope strikt aus der verbindlichen Kostenarten-Matrix abgeleitet (Objekt, Berechnungseinheit oder Vertrag je Kostenart).
- Die Kosten für die Warmwasseraufbereitung der BE1 werden aus dem Stromverbrauch für die Wärmepumpe hergeleitet (siehe oben) und nach Verbrauch (siehe Warmwasserzähler der NE) umgelegt.

Zur Kostenberechnung werden alle Belege einer Kostenart aufsummiert und gemäß der verbindlichen Kostenarten-Matrix (Scope + Umlageart + Schlüssel/Verbrauch) auf die NE umgelegt.

#### Berechnungslogik: Systematische Regeln zu Zeitanteiligkeit und Scope-Grenzen

**Was bedeutet „Zeitanteilig"?**

Zeitanteiligkeit gilt für **Schlüssel-umgelagerte Kostenarten** (nicht Verbrauch!) bei Mietparteien mit Einzug/Auszug im Abrechnungsjahr:
- Beispiele: Grundsteuer (Wohnfläche), Oberflächenwasser (Wohnfläche), Müllabfuhr (Personen), Brennstoffkosten Grundkosten-Anteil (30 %)
- Formel: `betrag_roh × (tage_anteilig / 365)` vor Rundung auf NE-Ebene
- **Nicht zeitanteilig:** Verbrauchskosten (incl. Heiznebenkosten, Strom, Warmwasser) — nur der gemessene Verbrauch ist unterschiedlich, nicht der Umlagezeitraum

**Scope-Grenzen: Drei knifflige Fälle**

1. **Gebäudeversicherung (Vertragsgruppe)**
   - Nenner = nur die NE in dieser Vertragsgruppe, NICHT die ganze Berechnungseinheit
   - Beispiel: Versicherung für NE4+NE5 hat Nenner = 34 m² (NE4) + 300 m² (NE5) = 334 m², nicht BE2-Gesamtfläche 394 m² (die NE3 mit 60 m² einschließt)
   - Excel2024-Fehler: nutzt irrtümlich BE2-Gesamtfläche 394 m² → Spec-Berechnung gilt

2. **Brennstoffkosten: 30 % Pauschalanteil + 70 % Verbrauchs­anteil**
   - Der 30%-Anteil ist eine Schlüsselumlage (Wohnfläche nach BE) und wird zeitanteilig berechnet
   - Der 70%-Anteil ist Verbrauchsumlage (HKV) und wird NICHT zeitanteilig berechnet
   - Fehlerfall: Ist die Summe (30 % + 70 %) > Gesamtbeleg, Abbruch mit Fehlermeldung

3. **Kalt- und Abwasser: NE5-Restverbrauch**
   - Formel: `NE5_Verbrauch = Hauptanschluss_Verbrauch − NE1_Verbrauch − NE2_Verbrauch − NE3_Verbrauch − NE4_Verbrauch`
   - Fehlerfall: Wenn Restverbrauch ≤ 0 (z. B. weil Summe NE1–NE4 > Hauptanschluss), Abbruch mit Fehlermeldung

**Wärmepumpen-Stromkosten (BE1 spezial)**
- Kostenbasis wird aus Stromzählern abgeleitet: `WP_Strom = Zähler_BE1_Gesamtanlage − Zähler_NE1_individual − Zähler_NE2_individual`
- Diese Kostenbasis wird dann nach Warmwasserzähler (WW-Verbrauch) auf NE1 und NE2 umgelegt
- Dies ist eine abgeleitete Größe, keine Messung — muss in Zwischenergebnis als Formel ausgewiesen werden, nicht als Alt/Neu/Differenz

#### Rundung und Summenkonsistenz
- Geldbeträge werden kaufmännisch auf 2 Nachkommastellen gerundet.
- Rundung erfolgt auf Ebene "Kostenanteil je Kostenart und NE".
- Die Summe aller gerundeten Einzelanteile wird je Kostenart auf den Kostenart-Gesamtbetrag abgeglichen.
- Etwaige Rundungsdifferenzen (Restcent) werden innerhalb der Kostenart der NE mit dem größten ungerundeten Anteil zugeordnet.
- Bei Gleichstand erhält die NE mit der lexikographisch kleinsten NE-ID den Restcent (deterministische Tie-Breaker-Regel).

## Desired State

### Input - Domänenmodell

Die Nebenkostenabrechnung basiert auf folgenden Domänenobjekten und ihren Relationen:

**Kernentitäten und Beziehungen:**

1. **Objekt** (Liegenschaft Hauptstr. 2)
   - enthält N **Berechnungseinheiten** (BE)
   - enthält N **Nutzeinheiten** (NE)

2. **Berechnungseinheit (BE)** (z. B. Gebäude Ost, Gebäude Nord/West)
   - gruppiert 1..N **Nutzeinheiten**
   - hat gemeinsame Energie-/Verbrauchslogik
   - trägt 1..N **Kostenbelege** (Brennstoff, Heizung, Warmwasser etc., BE-spezifisch)

3. **Nutzeinheit (NE)** (z. B. NE1, NE2, ... NE5; einzelne Nutzeinheiten)
   - wird von 0..1 **Mietpartei** bewohnt (0 = Leerstand; 1 = bewohnt)
   - hat **Schlüsselwerte** direkt im NE-Objekt: `wohnflaeche_m2`, `nutzflaeche_m2`
   - ordnet 1..N **Messgeräte (Zähler)** zu
   - hat 1..N **Ablesungen** (für jeden Zähler in der Periode)
   - kann 1..N **Versicherungsverträgen** angehören (via Vertragsgruppe)
   - trägt 0..N **Kostenbelege** (optional NE-spezifische Zuordnung)

4. **Mietpartei** (z. B. "Kraft / Hühne" – Lebensgemeinschaft, Familie, Einzelperson)
   - bewohnt 1..N **Nutzeinheiten**
   - hat eine Personenzahl (Schlüsselwert für Müllabfuhr etc.)
   - hat `einzug`-Datum (Pflicht) und `auszug`-Datum (optional, null = aktiv)
   - Bei unterjährigem Ein- oder Auszug wird die Abrechnung monatsgenau zeitanteilig berechnet
   - leistet 1..N **Vorauszahlungen** pro Periode (monatlicher Betrag × Anzahl Monate)
   - erhält 1 **Einzelabrechnung** mit ihren Kostenanteilen

Regel Leerstand: Für nicht bewohnte Nutzeinheiten wird keine Einzelabrechnung erstellt. Für die Umlage nach Personen zählen nur die der Nutzeinheit tatsächlich zugeordneten Mietparteien; ein Leerstand trägt damit faktisch 0 Personen zum Scope bei.

5. **Messgerät / Zähler** (z. B. Kaltwasserzähler, Stromzähler)
   - ist im Regelfall genau 1 **Nutzeinheit** zugeordnet; Sonderfälle können sich auf 1 **Berechnungseinheit** oder das gesamte **Objekt** beziehen
   - produziert 1..N **Ablesungen** (je nach Quelle als Stichtags- oder Periodenablesung)
   - hat Typ, Einheit, optional Umrechnungsfaktor
   - keine Belege, nur Messwertdaten

6. **Ablesung** (Messwertdaten je Quelle)
   - referenziert 1 **Zähler**
   - referenziert bei NE-bezogenen Zählern genau 1 **Nutzeinheit**; bei Zählern mit Bezug auf Berechnungseinheit oder Objekt ist keine direkte NE-Referenz erforderlich
   - enthält je nach `quelle` entweder ein Stichtagsmodell oder ein Periodenmodell
   - **Zwei Ablese-Modelle** je nach Quelle:
     - `ista_ablese` / `ista_monatsmittel`: ein Datensatz mit `messwert_alt`, `messwert_neu`, `periode` (von/bis) – Verbrauch direkt als Differenz im Datensatz
      - `manuell`: ein Datensatz pro Stichtag mit `stichtag` + `messwert` (Zählerstand per Ableseprotokoll) – Verbrauch = Differenz zweier manueller Ablesungen für denselben Zähler und, falls NE-bezogen, dieselbe Nutzeinheit am Anfang und Ende des Abrechnungszeitraums bzw. der Teilperiode

7. **Kostenbeleg** (Rechnung, Vertrag, Abschlag)
   - wird zugeordnet 1 **Kostenart** (muss in Kostenarten-Matrix sein)
   - hat Betrag, Datum, Beschreibung
   - optionale Scope-Einschränkung: **Berechnungseinheit** ODER **Nutzeinheit** ODER **Versicherungsvertrag**
   - keine Scope → gilt für alle relevanten Einheiten dieser Kostenart

8. **Kostenart** (z. B. Grundsteuer, Müllabfuhr, Brennstoffkosten, Strom)
   - definiert via **Kostenarten-Matrix** (Scope, Umlageart, Schlüssel/Verbrauch)
   - trägt 1..N **Kostenbelege**
   - wird umgelegt auf relevante NE nach Kostenarten-Matrix

9. **Versicherungsvertrag** (AXA-Verträge)
   - ist eine spezielle **Kostenart** (Gebäudeversicherung)
   - ist direkt zugeordnet 1..N **Nutzeinheiten** (Vertragsgruppe)
   - trägt 1 **Kostenbeleg** pro Versicherung
   - Umlage nur auf die zugeordneten NE, nach Wohnfläche (innerhalb der Vertragsgruppe)

10. **Vorauszahlung** (geleistete Zahlungen der Mietpartei)
    - wird gezahlt von 1 **Mietpartei**
    - gilt für eine **Periode** (von/bis)
    - hat `betrag_monatlich`, `anzahl_monate`, `gesamtbetrag` (Konsistenz wird validiert)
    - Bei unterjährigem Ein-/Auszug entsprechend kürzere Periode und angepasste Monatsanzahl

11. **Stromtarif** (zeitlich begrenzte Tarifkonfiguration)
    - gilt für den Stromverbrauch einer BE
    - hat Grundpreis (EUR/Jahr, taggenau anteilig) und Arbeitspreis (ct/kWh)
    - hat `gueltig_von` / `gueltig_bis`: Verbrauchsanteile werden je Tarifperiode tagesgenau berechnet
    - Lieferant und Tarifname zur Nachvollziehbarkeit

**Derivierte Größen (nicht in Input-JSON, aber konzeptionell wichtig):**
- **Schlüsselwert-Summe pro Scope**: z. B. Summe Wohnfläche aller NE in BE1
- **Verbrauch pro NE**: Messwert_neu - Messwert_alt (ggf. berechnet, z. B. NE5-Restverbrauch)
- **Kostenteil je Kostenart und NE**: Gesamtbeleg × (Schlüssel_NE / Schlüssel_Summe) oder (Verbrauch_NE / Verbrauch_Summe)
- **Gesamtkosten je Mietpartei**: Summe Kostenteile über alle ihre NE und alle Kostenarten
- **Saldo je Mietpartei**: Gesamtkosten - Vorauszahlungen

### Eingabe: Struktur und Validierung

Ich möchte die zur Berechnung erforderlichen Daten aus der Excel in ein strukturiertes JSON-Eingabeformat überführen, das die Domänenobjekte und ihre Relationen explizit abbildet.

**Festlegung:** Das Eingabeformat ist **JSON (UTF-8)** als einziges Quellformat für die Anwendung. Das JSON-Schema ist unter [nebenkosten_input_schema.json](nebenkosten_input_schema.json) definiert. Ein Beispiel-Input ist unter [nebenkosten_input_example.json](nebenkosten_input_example.json) zu finden.

**Pflichtstruktur:**
- `abrechnungsjahr` — integer
- `abrechnungszeitraum` — Objekt mit `von` und `bis` (ISO-Datum)
- `objekt` — hierarchische Struktur (BE → NE); NE enthält direkt `wohnflaeche_m2` und `nutzflaeche_m2`
- `mietparteien` — Array mit ID, Name, zugeordnete NE, `personen`, `einzug`, `auszug` (null = aktiv); Leerstand wird über nicht zugeordnete NE modelliert
- `versicherungsvertraege` — Array mit AXA-Kontrakten: Nummer, zugeordnete NE
- `zaehler` — Messgeräte mit Typ, Einheit und Zuordnung zu Nutzeinheit, Berechnungseinheit oder Objekt
- `ablesungen` — zwei Modelle je nach `quelle`: ista (`ista_ablese`/`ista_monatsmittel`) → `periode` + `messwert_alt` + `messwert_neu`; manuell (`manuell`) → `stichtag` + `messwert` (Verbrauch = Differenz zweier Stichtag-Einträge); bei NE-bezogenen Zählern mit NE-Referenz, bei BE-/Objekt-Zählern ohne direkte NE-Referenz
- `kostenbelege` — Rechnungen mit Kostenart-ID, Betrag, optionale Scope-Einschränkung
- `vorauszahlungen` — `betrag_monatlich`, `anzahl_monate`, `gesamtbetrag` (wird validiert), `periode`
- `stromtarife` — Zeitlich begrenzte Tarife: `grundpreis_eur_jahr`, `arbeitspreis_ct_kwh`, `gueltig_von`, `gueltig_bis`

#### Excel2024-Abbildung fuer Stromkosten (Iteration 1 Ergaenzung)

Die Laufzeitanwendung verarbeitet weiterhin ausschliesslich JSON. Fuer Datenmigration/Fixture-Erstellung und Oracle-Abgleich gilt fuer Excel2024 zusaetzlich diese normative Abbildung:

1. Worksheet `Stromkosten`, Spalten B-H sind die Quellbasis fuer `stromtarife` im Input-JSON.
2. Worksheet `Stromkosten`, Spalten L-Q sind die verteilten Ergebniswerte je Mietpartei und dienen als Oracle-/Plausibilitaetsbereich fuer Regression, nicht als operative Eingabequelle.

**Verbindliche Abgrenzung (Quelle vs. Berechnung):**

- Aus Excel werden fuer Strom ausschliesslich Tarifstammdaten nach `stromtarife` uebernommen (B-H).
- Stromkosten je Mietpartei werden nicht aus Excel und nicht als vorab berechneter Wert aus JSON uebernommen.
- Die Stromkostenberechnung (inkl. Zeitraeume je Tarif, Grundpreis-/Arbeitspreisanteile) erfolgt ausschliesslich im Rechenkern der Anwendung auf Basis von Verbrauchsdaten und `stromtarife`.

**Mapping B-H -> JSON `stromtarife[]`**

| Excel2024 Worksheet `Stromkosten` | JSON-Feld | Bedeutung |
|---|---|---|
| Spalte B | `id` | Tarif-ID |
| Spalte C | `grundpreis_eur_jahr` | Grundpreis in EUR/Jahr |
| Spalte D | `arbeitspreis_ct_kwh` | Arbeitspreis in ct/kWh |
| Spalte E | `gueltig_von` | Tarifbeginn (ISO-Datum) |
| Spalte F | `gueltig_bis` | Tarifende (ISO-Datum) |
| Spalte G | `be_id` | Zuordnung zur Berechnungseinheit |
| Spalte H | `lieferant` und/oder `tarif` | Transparenzfelder fuer Ausweis und Nachvollziehbarkeit |

**Bedeutung L-Q (Verteilung je Mietpartei)**

- L-Q bilden die strombezogene Kostenaufstellung je Mietpartei als Rechenergebnisbereich ab.
- Dieser Bereich wird fuer Regression und Delta-Dokumentation verwendet, jedoch nicht als operative Quelle fuer den Rechenkern.
- Abweichungen zwischen berechnetem Ergebnis und L-Q sind zu dokumentieren als:
   - bekannte Excel-Formelabweichung,
   - bewusstes Spec-Delta,
   - oder Implementierungsfehler.

**Validierungsregel fuer Migration/Fixture-Erstellung**

- Wenn in `Stromkosten` B-H tarifrelevante Datensaetze vorhanden sind, darf `stromtarife` im erzeugten Input-JSON nicht leer sein.
- Wenn `stromtarife` leer bleibt, ist dies ein Mapping-Fehler der Datenaufbereitung (nicht der fachlichen Berechnung) und muss fail-fast als Vorverarbeitungsfehler markiert werden.
- Die Datenaufbereitung darf keine fertigen Stromkosten aus L-Q in JSON-Felder fuer Kostenanteile uebernehmen.

**Validierungsregeln (Fail-Fast):**

*Strukturelle Integrität:*
- Jede NE-Referenz muss eine existierende NE im Objekt sein.
- Jede Mietpartei muss 1..N NE bewohnen; eine NE darf keiner Mietpartei zugeordnet sein (Leerstand).
- Jede Ablesung muss einen existierenden Zähler referenzieren. Falls die Ablesung eine NE referenziert, muss diese existieren und zum Zähler passen.
- Jeder Kostenbeleg muss eine Kostenart-ID referenzieren, die in der Kostenarten-Matrix definiert ist.
- Jeder Versicherungsvertrag muss 1..N NE abdecken; diese NE müssen existieren.

*Datenlogik:*
- Jede Kostenart muss nach Kostenarten-Matrix umsetzbar sein (Scope + Umlageart + Schlüssel/Verbrauch müssen in Input vorhanden sein).
- Für Schlüssel-Umlage: alle NE des Scopes müssen Schlüsselwerte (Wohnfläche / Personen) haben.
- Für die Umlage nach Personen: Schlüsselwert je NE = Summe Personen der ihr zugeordneten Mietpartei(en); bei Leerstand ist dieser Wert 0 (→ Leerstand-Regel im Domänenmodell, Abschnitt Mietpartei).
- Für Verbrauchs-Umlage: alle NE des Scopes müssen Ablesungen für den erforderlichen Zählertyp haben.
- Versicherungsverträge: Für alle zugeordneten NE muss Wohnfläche vorliegen.
- Vorauszahlungen: dürfen nicht null/negativ sein; Summe per Periode muss prüfbar sein.

*Fail-Fast Abbruch bei:*
- Fehlendes Pflichtfeld (z. B. `mietparteien` komplett leer)
- Ungültiger Referenz (z. B. Kostenbeleg referenziert NE, die nicht existiert)
- Mehrdeutige Zuordnung (z. B. Kostenart in mehreren Versicherungsverträgen, aber Kostenbeleg hat keinen eindeutigen Vers.-Scope)
- Unplausibler Verbrauch (z. B. Differenz negativ, oder Restverbrauch NE5 negativ)
- Fehlende kritische Ablesungen (z. B. Heizverbrauch-Umlage gefordert, aber kein Messwert für diese BE vorhanden)

#### Einheitliches Fehlermeldungsformat (v1)

Für jeden **blocking** Fehler verwendet die Anwendung ein einheitliches, maschinenlesbares Fehlermodell. Die konkrete Darstellung in CLI, Logdatei oder JSON-Ausgabe kann variieren, die fachliche Struktur des Fehlers bleibt jedoch identisch.

**Ziele:**
- Fehlermeldungen müssen für den Operator sofort verständlich sein.
- Fehlermeldungen müssen für Tests und spätere Automatisierung stabil auswertbar sein.
- Jeder Abbruch muss genau auf die betroffene Entität, Periode oder Eingabestelle zurückführbar sein.

**Fail-fast-Regel für das Format:**
- Bei einem blocking Fehler wird die Berechnung sofort abgebrochen.
- Die Anwendung gibt genau **einen primären Fehler** zurück.
- Optional darf das Feld `related_errors` zusätzliche, direkt zusammenhängende Detailfehler enthalten, z. B. mehrere fehlende Pflichtfelder innerhalb derselben Schema-Prüfung.
- Nach einem blocking Fehler dürfen keine fachlichen Folgefehler aus späteren Berechnungsschritten mehr erzeugt werden.

**Kanonisches Fehlerobjekt:**

```json
{
   "error_code": "NK-REF-001",
   "category": "reference",
   "severity": "error",
   "blocking": true,
   "phase": "validation",
   "message": "Kostenbeleg verweist auf unbekannte Nutzeinheit.",
   "detail": "Der Kostenbeleg kb-017 referenziert die Nutzeinheit NE9, diese existiert im Objekt jedoch nicht.",
   "entity_type": "kostenbeleg",
   "entity_id": "kb-017",
   "field_path": "$.kostenbelege[16].scope.ne_id",
   "cost_type_id": "gebaeudeversicherung",
   "meter_id": null,
   "mietpartei_id": null,
   "period": {
      "von": "2024-01-01",
      "bis": "2024-12-31"
   },
   "source_ref": "input_json",
   "hint": "Prüfe die NE-ID im Kostenbeleg oder ergänze die fehlende Nutzeinheit im Objektmodell.",
   "related_errors": []
}
```

**Pflichtfelder des Fehlerobjekts:**
- `error_code`: stabiler, testbarer Fehlercode
- `category`: Fehlerkategorie
- `severity`: in v1 für Abbrüche immer `error`
- `blocking`: `true` bei sofortigem Abbruch
- `phase`: Verarbeitungsphase, z. B. `input`, `validation`, `calculation`, `rendering`
- `message`: kurze, operatorlesbare Fehlermeldung
- `detail`: konkrete Beschreibung mit fachlichem Kontext
- `entity_type`: Typ der betroffenen Entität, z. B. `kostenbeleg`, `ablesung`, `zaehler`, `mietpartei`
- `entity_id`: ID der betroffenen Entität, falls vorhanden
- `field_path`: JSON-Pfad oder semantischer Feldpfad zur Ursache
- `period`: betroffene Periode oder Teilperiode, falls relevant
- `hint`: konkrete nächste Prüf- oder Korrekturmaßnahme

**Optionale Kontextfelder:**
- `cost_type_id`
- `meter_id`
- `mietpartei_id`
- `source_ref` (z. B. `input_json`, `ista_pdf`, `manuelle_ablesung`)
- `related_errors`

**Fehlercode-Schema:**
- Format: `NK-<BEREICH>-<NUMMER>`
- Beispiele für Bereiche:
   - `SCHEMA` = JSON-Struktur / Pflichtfelder
   - `REF` = ungültige Referenzen
   - `VALID` = fachliche Eingabekonsistenz
   - `METER` = Ablesungen / Zähler / Verbrauchsdaten
   - `ALLOC` = Umlage- oder Scope-Fehler
   - `CALC` = Berechnungsfehler
   - `RENDER` = Fehler bei Ausgabeerzeugung

**Mindest-Fehlerkatalog für v1:**
- `NK-SCHEMA-001`: Pflichtfeld fehlt
- `NK-SCHEMA-002`: Feldwert hat ungültigen Typ oder ungültiges Format
- `NK-REF-001`: Referenz auf unbekannte Entität
- `NK-VALID-001`: Mehrdeutige fachliche Zuordnung
- `NK-METER-001`: Kritische Ablesung fehlt für erforderliche Periode
- `NK-METER-002`: Verbrauch ist negativ oder unplausibel
- `NK-ALLOC-001`: Kostenart kann nicht eindeutig gemäß Kostenarten-Matrix umgelegt werden
- `NK-CALC-001`: Abgeleitete Berechnung verletzt fachliche Konsistenzregel
- `NK-RENDER-001`: Pflichtdaten für die Ausgabe fehlen trotz erfolgreicher Berechnung

**Darstellungsregeln:**
- In der CLI muss zusätzlich zur strukturierten Fehlermeldung mindestens eine kurze Ein-Zeilen-Zusammenfassung erscheinen: `FEHLER <error_code>: <message>`.
- In JSON-basierten Tests und Schnittstellen gilt das kanonische Fehlerobjekt als maßgebliche Wahrheit.
- Fehlermeldungen müssen fachlich konkret formuliert sein; generische Meldungen wie `Validation failed` oder `Unexpected error` sind für bekannte Fehlerfälle unzulässig.
- Wenn kein fachlicher Fehlercode greift, ist ein technischer Fallback-Code aus dem Bereich `NK-SYSTEM-*` zu verwenden; auch dann müssen `message`, `detail` und `hint` gesetzt sein.

### Beispiel-Input und Schema

/Users/dh/Documents/DanielsVault/_shared/_specs/nebenkosten_input_example.json

/Users/dh/Documents/DanielsVault/_shared/_specs/nebenkosten_input_schema.json

### Ausgabe

#### Ausgabeformat und Ablage

**Format (zweistufig):**
1. **Zwischenergebnis (JSON):** Die Anwendung erzeugt zunächst ein strukturiertes Berechnungsergebnis als JSON mit allen Zwischenwerten (Schlüsselwert-Summen, Kostenteile je NE, Herleitung abgeleiteter Verbräuche). Dieses dient der Nachvollziehbarkeit und als Basis für das Rendering.
2. **Einzelabrechnung (PDF):** Das finale Dokument für den Mieter wird als PDF ausgegeben. Entwicklungsstufe: zuerst HTML-Mock (direkt renderbar, kein weiteres Tool), dann PDF-Konvertierung.

**Mock-Artefakt:**
- Verbindlicher Layout-Mock für die Einzelabrechnung: `_shared/_specs/mock_einzelabrechnung.html`
- Der Mock dient als visuelle und strukturelle Vorlage für die spätere PDF-Erzeugung.
- Druckbares PDF-Template-Rendering (aus JSON): `_shared/_specs/render_einzelabrechnung_example.py`
- Erstes gerendertes Beispiel (Mietpartei `mp-kraft-huehne`):
   - HTML: `_shared/_specs/rendered_example/mp-kraft-huehne/einzelabrechnung.html`
   - PDF: `_shared/_specs/rendered_example/mp-kraft-huehne/einzelabrechnung.pdf`

**Dateiablage:**
- Der Ausgabepfad ist frei konfigurierbar (Pflichtparameter der Anwendung).
- Beispielpfad: `/Users/dh/Library/CloudStorage/OneDrive-Personal/Documents/Me/Real Estate/Schlüchtern Hauptstr 2/Vermietung/Nebenkostenabrechnung/2024`
- Innerhalb dieses Pfades wird je Mietpartei ein Unterordner angelegt.
- Namenschema Unterordner: `{mietpartei_id}` (aus dem Input-JSON)
- Erzeugte Dateien je Mietpartei: `einzelabrechnung.json` (Zwischenergebnis) + `einzelabrechnung.pdf` (finales Dokument)

**Out of scope für v1:** Objekt-Gesamtübersicht (alle NE + Kosten als Vermieter-Summary).

#### Inhalt der Einzelabrechnung

Die Anwendung soll daraus Einzelabrechnungen für jede Mietpartei erstellen. Jede Einzelabrechnung soll folgende Informationen beinhalten:
1. **Kopf / Identifikation**
   - Objekt
   - Mietpartei / Nutzeinheit / Berechnungseinheit
   - Abrechnungsdatum
   - Abrechnungszeitraum

2. **Ergebnisübersicht**
   - Ihre Gesamtkosten
   - Ihre Vorauszahlungen
   - Ihre Nachzahlung oder Ihr Guthaben

3. **Verbrauchs- und Ablesewerte (nur soweit für diese Mietpartei relevant)**
   - Relevante Werte: Strom / Warmwasser / Kaltwasser / Heizverbrauch / HKV
   - Herkunft je Wert: Gerät / Zähler / Einheit
   - Ablesewerte je Wert: Alt / Neu / Differenz
   - ggf. Umrechnungsfaktor
   - Bei abgeleiteten Verbrauchswerten (z. B. Wärmepumpenanteil Strom BE1, Restverbrauch NE5 Kaltwasser): Herleitung als Formel ausweisen (z. B. BE-Gesamt − NE1 − NE2) statt Alt/Neu/Differenz eines einzelnen Zählers

4. **Gesamtkosten des relevanten Scopes je Kostenart**
   - z. B. Grundsteuer, Müllabfuhr, Gebäudeversicherung, Oberflächenwasser, Kalt- und Abwasser, Heiznebenkosten, Brennstoffkosten, Strom
   - ggf. mit Teilsummen für Heizung, Warmwasser und Hausnebenkosten

5. **Verteilerschlüssel je Kostenart**
   - Schlüsseltyp in lesbarer Form: Wohnfläche / Personen / Heizverbrauch / Warmwasserverbrauch / Kaltwasserverbrauch
   - Gesamteinheiten der Liegenschaft / des Scopes
   - Ihre Einheiten
   - Herleitung der Schlüsselwerte mit Fokus auf Verständlichkeit
   - Betrag pro Einheit oder rechnerische Quote

6. **Ihr Kostenanteil je Kostenart**
   - tabellarisch und rechnerisch nachvollziehbar
   - mit klarer Trennung von: Kostenart gesamt / Verteilerschlüssel / Ihr Anteil / Ihr Betrag

7. **Abzug der Vorauszahlungen**
   - bereits gezahlt gesamt
   - idealerweise zusätzlich: Monatsabschlag x Anzahl Monate
   - nur als Erläuterung, nicht als Ersatz für den echten Zahlungswert

8. **Hinweisblock**
   - Belegeinsicht-Hinweis
   - ggf. kurzer Hinweis zur Prüfbarkeit / Quellen
   - keine unnötige Marketing-/Boilerplate

## Gestaltungsprinzipien
es gelten diese Regeln:

- knapp und klar.
- Nur die für die Mietpartei nötigen Werte im Hauptdokument.
- Fremde Nutzergruppen und unnötige Objekt-Details nicht im Zentrum. Fokus auf relevantem Scope je Kostenart, nicht auf unnötigen Globaldaten.
- Visuell hochwertiges, gut lesbares Dokument mit klarer Typografie, konsistentem Abstandssystem und sauberem Drucklayout.
- Zielgerichtete Visualelemente/Bilder sind erlaubt (z. B. Objektbild, Marken-/Ident-Elemente), sofern sie der Verständlichkeit dienen und das Dokument nicht überladen.
- Tabellen vor Freitext.
- Freitext vor Stichwortwüsten.
- Für Beträge, Schlüsselwerte und Herleitungen sind strukturierte Tabellen Pflicht.
- PDF-Ausgabe muss drucktauglich sein (A4, sinnvolle Seitenumbrüche, keine abgeschnittenen Tabellenzeilen).
- Mieterverständliche Sprache ist Pflicht: keine unnötigen Fachbegriffe; Abkürzungen (z. B. BE, NE, HKV) müssen vor erster Verwendung kurz erklärt werden.
- Verteilerschlüssel dürfen nicht nur genannt werden, sondern müssen je Kostenart nachvollziehbar hergeleitet werden (Gesamtwert, Ihr Wert, Rechenschritt, Ergebnis).

## Tests und Akzeptanzkriterien

### Test-Oracle: Excel2024

Als primärer Referenzwert dient die manuell erstellte Nebenkostenabrechnung 2024 (`Nebenkostenabrechnung_2024.xlsx`). Der Ansatz: Die Anwendung erhält die Eingabedaten des Jahres 2024 und soll dieselben Ergebnisse liefern wie Excel2024.

**Toleranzregel:** Abweichungen sind akzeptabel, wenn sie plausibel erklärt werden können (z. B. korrektere Rundungslogik, bewusste Richtigstellung eines manuellen Fehlers in Excel2024). Jede Abweichung muss dokumentiert werden.

**Bekannte Abweichungen Spec vs. Excel2024** (dokumentiert in dieser Spec):

| Abweichung | Spec | Excel2024 | Entscheidung |
|---|---|---|---|
| Versicherungsgesellschaft | AXA-Verträge (3 Einzelverträge) | Allianz (3 Kostenbelege nach BE/NE) | Geklärt: 2024 = Allianz (Historie/Test-Oracle), ab 2025 = AXA (fachlicher Zielzustand) |
| Kostenart-Name Heizung | `Betriebskosten Heizung` | `Grundkosten Heizung` | Spec-Name gilt; Excel2024 enthält Tippfehler (`Oberfächenwasser`) |
| Kostenart-Name Wasser | `Oberflächenwasser` | `Oberfächenwasser` (Tippfehler) | Spec-Name gilt |
| NE4 Gebäudeversicherung Anteil | 34/(34+300) = 10,18 % (Vertragsgruppe NE4+NE5 = 334 m²) | 34/(60+34+300) = 8,63 % (BE2-Gesamtfläche 394 m²) | Excel2024-Fehler: NE3-Fläche fälschlicherweise in Nenner; Spec-Berechnung gilt |
| NE2 Strom (Schäfer) | individuelle NE2-Stromkosten, 12 Monate ≈ 541,90 EUR | 497,15 EUR (identischer Wert wie NE1 / Kraft-Hühne, 10 Monate) | Excel2024-Formel-Bug: Einzelabrechnung_2 referenziert NE1-Stromzelle statt NE2; Spec-Berechnung gilt |
| NE5 Einzelabrechnung | Einzelabrechnung wird erstellt (NE5 als reguläre Mietpartei Hecht, 365 Tage, 4 Personen, Vollabrechnung) | Keine Einzelabrechnung in Excel2024 (NE5 = Eigentümernutzung) | Entschieden: NE5 wird ab 2025 als reguläre Mietpartei abgerechnet. Excel2024-Oracle (T10) validiert nur NE1–NE4; NE5 wird in Anwendung berechnet, aber nicht gegen Excel2024 getestet |
| Einzelabrechnung_1.2 Leerstand NE1 | Keine Einzelabrechnung für Leerstand-NE | Excel2024 enthält Berechnung für Leerstand-Periode NE1 (61 Tage, Nov–Dez 2024, Kosten 902,23 EUR) als eigenes Worksheet | Vermieter-interne Hilfskalkulation; keine mietergerichtete Ausgabe; Spec-Regel bleibt korrekt |

### Testfälle

| ID | Szenario | Art | Erwartetes Ergebnis |
|---|---|---|---|
| T1 | Happy Path: alle 5 NE besetzt (Vollabrechnung), Volljahr, alle Belege vorhanden | Pflicht | 5 Einzelabrechnungen (NE1–NE5); Summe aller Kostenanteile je Kostenart = Gesamtbeleg (Rundungskonsistenz); NE5 wird erstmals abgerechnet |
| T2 | Leerstand: eine NE ohne zugeordnete Mietpartei | Pflicht | Kein Dokument für diese NE; Personenanteil dieser NE = 0 in allen Personen-Schlüsseln |
| T3 | Unterjähriger Ein-/Auszug (Kraft/Hühne-Szenario aus Excel2024) | Pflicht | Zeitanteilige Abrechnung monatsgenau; Vorauszahlungen entsprechend gekürzt |
| T4 | Abgeleiteter Verbrauch NE5 (Restverbrauch Kaltwasser) | Pflicht | NE5 = Hauptanschluss − NE1 − NE2 − NE3 − NE4; negativer Wert → Abbruch mit Fehlermeldung |
| T5 | Wärmepumpenstrom BE1 | Pflicht | Wärmepumpenanteil = BE1-Gesamt − NE1-Strom − NE2-Strom; Ausweis als Formel in Ausgabe |
| T6 | Fail-fast: fehlende Pflichtablesung | Pflicht | Abbruch mit eindeutiger Meldung (Zähler-ID + fehlende Periode) |
| T7 | Fail-fast: ungültige NE-Referenz in Kostenbeleg | Pflicht | Abbruch mit eindeutiger Meldung |
| T8 | Rundungskonsistenz: Restcent-Zuweisung | Pflicht | Summe gerundeter Anteile = Gesamtbeleg nach Restcent-Zuweisung an größten Anteil |
| T9 | Versicherungs-Vertragsgruppe: NE3 zahlt nur eigenen Vertrag | Pflicht | NE3 erhält keinen Anteil am NE4/NE5-Vertrag und umgekehrt |
| T10 | Excel2024-Regressiontest: gleiche 2024-Eingaben → gleiche Ergebnisse für NE1–NE4 | Pflicht | Abweichungen nur mit Dokumentation akzeptiert (→ bekannte Abweichungen oben). NE5 wird von dieser Validierung ausgenommen, da Excel2024 keine Einzelabrechnung für NE5 enthält. NE5 wird inhaltlich berechnet (T1), aber nicht gegen Oracle validiert |

### Test-Oracle: Erwartete Ergebnisse je NE (aus Excel2024)

Die folgende Tabelle enthält die konkreten Sollwerte für den Regressionstest T10 (und T1/T3) aus den Excel2024-Einzelabrechnungen. Spaltenbezeichnungen entsprechen den Excel-Spalten: Gesamtkosten (Scope-Summe), Anteil (Umlageschlüssel), Tage anteilig, Mieterkosten.

**NE1 – Kraft/Hühne** (304/365 Tage, Einzug 01.02.2024 → Auszug 31.10.2024)

| Kostenart | Gesamtkosten | Anteil | Tage | Mieterkosten |
|---|---|---|---|---|
| Brennstoffkosten (Grundkosten 30 %) | 883,45 | 69,23 % | 304 | 509,40 |
| Brennstoffkosten (Verbrauch 70 %) | 2.061,38 | 43,49 % | — | 896,50 |
| Heiznebenkosten | 437,34 | 43,49 % | — | 190,20 |
| Gebäudeversicherung | 1.260,34 | 69,23 % | 304 | 726,72 |
| Grundsteuer | 1.342,12 | 27,52 % | 304 | 307,66 |
| Müllabfuhr | 401,28 | 22,22 % | 304 | 74,27 |
| Oberflächenwasser | 790,02 | 27,52 % | 304 | 181,10 |
| Verbrauchskosten Warmwasser | 858,82 | 56,19 % | — | 482,54 |
| Strom (individuell, 10 Monate) | 497,15 | — | — | 497,15 |
| Kalt- und Abwasser | 5.941,14 | 6,47 % | — | 384,48 |
| **Summe** | | | | **4.250,01** |
| Vorauszahlung | | | | 2.500,00 |
| **Nachzahlung** | | | | **1.750,01** |

**NE2 – Schäfer** (365 Tage)

| Kostenart | Gesamtkosten | Anteil | Tage | Mieterkosten |
|---|---|---|---|---|
| Brennstoffkosten (Grundkosten 30 %) | 883,45 | 30,77 % | 365 | 271,83 |
| Brennstoffkosten (Verbrauch 70 %) | 2.061,38 | 54,75 % | — | 1.128,52 |
| Heiznebenkosten | 437,34 | 54,75 % | — | 239,43 |
| Gebäudeversicherung | 1.260,34 | 30,77 % | 365 | 387,80 |
| Grundsteuer | 1.342,12 | 12,23 % | 365 | 164,17 |
| Müllabfuhr | 401,28 | 11,11 % | 365 | 44,59 |
| Oberflächenwasser | 790,02 | 12,23 % | 365 | 96,64 |
| Verbrauchskosten Warmwasser | 858,82 | 43,81 % | — | 376,28 |
| Strom (individuell, 12 Monate) | ⚠ 497,15 (Excel-Bug, korrekt ≈ 541,90) | — | — | ⚠ 497,15 |
| Kalt- und Abwasser | 5.941,14 | 5,92 % | — | 351,81 |
| **Summe** | | | | **3.558,20** |
| Vorauszahlung | | | | 2.760,00 |
| **Nachzahlung** | | | | **798,20** |

**NE3 – König** (365 Tage)

| Kostenart | Gesamtkosten | Anteil | Tage | Mieterkosten |
|---|---|---|---|---|
| Brennstoffkosten (Grundkosten 30 %) | 261,88 | 15,23 % | 365 | 39,88 |
| Brennstoffkosten (Verbrauch 70 %) | 611,06 | 31,36 % | — | 191,65 |
| Heiznebenkosten | 192,73 | 31,36 % | — | 60,45 |
| Gebäudeversicherung | 538,69 | 100,00 % | 365 | 538,69 |
| Grundsteuer | 1.342,12 | 9,17 % | 365 | 123,13 |
| Müllabfuhr | 401,28 | 11,11 % | 365 | 44,59 |
| Oberflächenwasser | 790,02 | 9,17 % | 365 | 72,48 |
| Verbrauchskosten Warmwasser | — | — | — | 0,00 |
| Strom | 0,00 | — | — | 0,00 |
| Kalt- und Abwasser | 5.941,14 | 10,40 % | — | 617,88 |
| **Summe** | | | | **1.688,75** |
| Vorauszahlung | | | | 1.500,00 |
| **Nachzahlung** | | | | **188,75** |

**NE4 – Waldheim** (365 Tage)

| Kostenart | Gesamtkosten | Anteil | Tage | Mieterkosten |
|---|---|---|---|---|
| Brennstoffkosten (Grundkosten 30 %) | 261,88 | 8,63 % | 365 | 22,60 |
| Brennstoffkosten (Verbrauch 70 %) | 611,06 | 68,64 % | — | 419,40 |
| Heiznebenkosten | 192,73 | 68,64 % | — | 132,28 |
| Gebäudeversicherung | 1.967,90 | ⚠ 8,63 % (korrekt laut Spec: 10,18 %) | 365 | ⚠ 169,82 |
| Grundsteuer | 1.342,12 | 5,20 % | 365 | 69,77 |
| Müllabfuhr | 401,28 | 11,11 % | 365 | 44,59 |
| Oberflächenwasser | 790,02 | 5,20 % | 365 | 41,07 |
| Verbrauchskosten Warmwasser | — | — | — | 0,00 |
| Strom | 83,70 | — | — | 83,70 |
| Kalt- und Abwasser | 5.941,14 | 4,75 % | — | 282,46 |
| **Summe** | | | | **1.265,70** |
| Vorauszahlung | | | | 1.290,00 |
| **Guthaben** | | | | **24,30** |

**NE5 – Hecht** (Eigentümernutzung umgeschrieben als reguläre Mietpartei ab 2025)

NE5 wird ab 2025 als reguläre Mietpartei mit Einzelabrechnung behandelt. In Excel2024 gab es keine Einzelabrechnung für NE5 (Eigentümernutzung), daher fehlen konkrete Sollwerte vom Excel-Oracle. Die Anwendung berechnet NE5 nach denselben Regeln wie NE1–NE4, wird aber nicht gegen Excel2024-Werte validiert (T10 umfasst nur NE1–NE4).

Hinweis zur Leerstand-Periode NE1 (Nov–Dez 2024, Einzelabrechnung_1.2): Excel2024 enthält eine interne Berechnung für die 61-tägige Leerstandsperiode (Kosten: 902,23 EUR, Vorauszahlung: 0, Differenz: −902,23). Dies ist keine mietergerichtete Abrechnung, sondern eine vermieterseitige Hilfskalkulation. Die Anwendung erzeugt für Leerstandsperioden kein Ausgabedokument.

### Zwischenergebnis-Schema (JSON)

Das `einzelabrechnung.json` je Mietpartei soll mindestens enthalten:
- `mietpartei_id`, `abrechnungsjahr`, `abrechnungszeitraum`
- `schluessewerte`: Wohnfläche, Personen, Nutzfläche je NE und Scope-Summen
- `verbraeuche`: je Zählertyp und NE — Wert_alt, Wert_neu, Differenz; bei abgeleiteten Werten zusätzlich `herleitung`-Feld mit Formel und Einzelwerten
- `kostenpositionen`: je Kostenart — Gesamtbetrag, Scope, Schlüssel/Verbrauch, Anteil_NE, Betrag_NE
- `vorauszahlungen`: geleisteter Gesamtbetrag, Aufschlüsselung
- `saldo`: Gesamtkosten − Vorauszahlungen (positiv = Nachzahlung, negativ = Guthaben)

### Ergaenzende Testfaelle (Iteration 1)

| ID | Szenario | Art | Erwartetes Ergebnis |
|---|---|---|---|
| T11 | Excel2024 Worksheet `Stromkosten` B-H enthaelt Tarifdaten | Pflicht | Mapping erzeugt nicht-leeres `stromtarife[]` im Input-JSON; leeres `stromtarife[]` gilt als Vorverarbeitungsfehler |
| T12 | Vergleich berechneter Stromkosten gegen Worksheet `Stromkosten` L-Q | Pflicht | Delta je Mietpartei wird als `gleich` oder `Implementierungsfehler` klassifiziert und reportet; alte Excel-Ausnahmen sind nicht zulaessig |
| T13 | Abgrenzung Eingabe/Berechnung fuer Strom | Pflicht | JSON enthaelt keine aus Excel uebernommenen, vorab berechneten Stromkosten; Stromkosten entstehen erst im Rechenkern aus Verbrauchsdaten + `stromtarife` |

## History
| Date | Iteration | Author | Delta |
|---|---|---|---|
| 2026-03-24 | 0 | User | Initiale fachliche Spezifikation erstellt |
| 2026-03-25 | 1 | Copilot (GPT-5.3-Codex) | Excel2024-Stromkostenabbildung praezisiert: Mapping B-H -> `stromtarife`, L-Q als Oracle-Verteilungsbereich, zusaetzliche Testfaelle T11/T12 |

