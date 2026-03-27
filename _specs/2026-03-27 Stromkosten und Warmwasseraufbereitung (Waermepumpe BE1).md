# Stromkosten und Warmwasseraufbereitung (Waermepumpe BE1)

## Zweck

Diese Spec trennt die bisher vermischten Themen

- direkter NE-Strom,
- strombasierte Warmwasseraufbereitung ueber die Waermepumpe in BE1,
- Excel2024-Oracle,
- und technische Input-/Output-Regeln

in ein eigenstaendiges, fachlich eindeutiges Dokument.

Sie dient als Referenz fuer die weitere Bereinigung von Rechenkern, Tests, Fixtures und Oracle-Werten.

## Bezug

- Haupt-Spec: `./2026-03-24 Nebenkostenabrechnung Applikation.md`
- Analyse-Notiz: `./2026-03-26 Stromkosten-Datenkorrektur und Test-Oracle Alignment.md`

## Problemstellung

In der bisherigen Entwicklung wurden zwei fachlich unterschiedliche Sachverhalte vermischt:

1. **Direkter Wohnungsstrom** einzelner Nutzeinheiten
2. **Waermepumpenstrom als Kostenbasis der Warmwasseraufbereitung** in BE1

Diese Vermischung fuehrte zu:

- widerspruechlichen Oracle-Werten,
- unklaren Kostenarten,
- fehlerhaften Tarif-Fixtures,
- und Doppelzaehlung im Tarifmodus.

## Geltungsbereich

Diese Spec beschreibt:

1. die allgemeine fachliche Trennung von direktem Wohnungsstrom und Waermepumpenstrom in BE1,
2. die Zuordnung des Waermepumpenstroms zur Kostenart Warmwasser,
3. die Abbildung aus Excel als Datenquelle,
4. und die daraus folgenden Test- und Output-Anforderungen.

Die zeitraumbezogene Umlage je Mietpartei (Einzug/Auszug) ist in der Haupt-Spec bereits verbindlich geregelt und wird hier nicht erneut vollstaendig definiert.

## Zeitlogik (Verweis auf Haupt-Spec)

- Diese Spec uebernimmt die Zeitlogik aus der Haupt-Spec unveraendert.
- Fuer 2024 bedeutet das im aktuellen Fall: NE1 Teiljahr (01/2024-10/2024), uebrige relevante NEs Volljahr (01/2024-12/2024).
- Diese Angaben dienen hier nur der Einordnung der Oracle-Werte, nicht der Neudefinition der Zeitregeln.

## Nicht Gegenstand

Diese Spec regelt nicht erneut:

- Grundsteuer,
- Versicherung,
- Brennstoffkosten,
- Kalt-/Abwasser ausser soweit fuer Abgrenzung noetig,
- oder allgemeine Render-/PDF-Anforderungen.

## Begriffe

### Direkter Strom

Direkter Strom ist Strom, der einer Nutzeinheit unmittelbar als eigener Wohnungsstrom zugerechnet wird.

### Waermepumpenstrom

Waermepumpenstrom ist keine eigene verbraucherseitige Kostenart fuer Mieter, sondern die aus Stromzaehlern hergeleitete Kostenbasis fuer die Warmwasseraufbereitung in BE1.

### Warmwasserkosten

Warmwasserkosten im hier gemeinten Sinn sind die an Mieter verteilten Kosten der Warmwasseraufbereitung. Dazu gehoeren die ueber die Waermepumpe verursachten Stromkosten, sofern diese Kostenbasis fachlich ueber Warmwasserverbrauch verteilt wird.

## Fachregeln

### 1. Direkter NE-Strom bleibt eigene Kostenposition nur bei echtem Wohnungsstrom

- Eine NE darf eine eigene Kostenposition `strom` haben, wenn es sich um direkt zurechenbaren Wohnungsstrom handelt.
- Diese Kostenposition ist von der Warmwasseraufbereitung fachlich getrennt zu behandeln.

### 2. Waermepumpenstrom in BE1 gehoert nicht zur Kostenart `strom`

Fuer BE1 gilt verbindlich:

`WP_Strom = Zaehler_BE1_Gesamtanlage − Zaehler_NE1_individual − Zaehler_NE2_individual`

Diese Groesse ist:

- eine **abgeleitete Kostenbasis**,
- **keine** direkte Mieter-Stromposition,
- und kostenartenmaessig der Warmwasseraufbereitung zuzuordnen.

Diese Regel ist objektspezifisch fuer BE1 (getrennte Waermepumpe und Oelheizkessel) und gilt nicht nur fuer ein einzelnes Abrechnungsjahr.

### 3. Verteilung der Waermepumpenkosten erfolgt ueber Warmwasserverbrauch

Die aus `WP_Strom` entstehenden Kosten werden nicht nach Stromverbrauch verteilt, sondern nach Warmwasserverbrauch der betroffenen NEs.

Fuer BE1 bedeutet das:

- Verteilung nur auf die NEs mit relevantem WW-Verbrauch,
- Schluessel = Warmwasserverbrauch,
- Kostenart im Ergebnis = `verbrauchskosten_warmwasser`, nicht `strom`.

### 4. Darstellungsregel fuer Herleitung

Die Herleitung des Waermepumpenstroms muss im Zwischenergebnis sichtbar sein als Formelableitung.

Sie darf nicht dargestellt werden als:

- normaler Einzelzaehler mit Alt/Neu/Differenz,
- oder eigenstaendige `strom`-Kostenzeile fuer die Mietpartei.

## Excel2024-Abbildung

### Datenquellen

### A. Worksheet `Stromkosten`

- Spalten B-H: Tarif- und Stammdaten fuer `stromtarife`
- L-Q: Ergebnis-/Plausibilitaetsbereich, nicht operative Eingabequelle

### B. Worksheet `Messwerte`

- Quelle fuer relevante Strom-Messwerte der Zaehler
- dient der Nachvollziehbarkeit der Strombasis und der WP-Herleitung

### C. Worksheet `Verbraeuche`

- Quelle fuer den Warmwasserverbrauch je NE
- fuer die 2024-Oracles relevant insbesondere die Werte aus Spalten M-O

## Verbindliche Abgrenzung der Excel-Nutzung

- Excel-Ergebniszellen duerfen nicht blind als operative Kostenpositionen in das Input-JSON kopiert werden.
- Tarifdaten duerfen fuer `stromtarife` extrahiert werden.
- Direkter Strom und Warmwasseraufbereitung muessen im Rechenkern fachlich getrennt behandelt werden.
- Wenn Excel2024 Stromkosten fuer Warmwasseraufbereitung falsch unter `strom` fuehrt, gilt diese neue Spec und nicht die fehlerhafte Excel-Kostenart-Zuordnung.

Operationales Prinzip:

- Excel ist Quelle fuer Tarife, Messwerte und Plausibilisierung.
- Die fachliche Kostenarten-Zuordnung erfolgt im Rechenkern gemaess dieser Spec.

## Input-Regeln

### Tarifmodus

Wenn `stromtarife` vorhanden sind, gilt:

- Es duerfen keine `kostenbelege` mit `kostenart_id = "strom"` vorhanden sein.
- Ein solcher Beleg ist ein Vorverarbeitungs- bzw. Fixture-Fehler.
- Stromkosten im Tarifmodus entstehen ausschliesslich im Rechenkern.

### Direkter Modus

Wenn keine `stromtarife` vorhanden sind, duerfen direkte Strom-Kostenbelege verwendet werden, soweit dies dem historischen 2024-Oracle entspricht.

## Output-Regeln

### `cost_items`

- Direkter Wohnungsstrom wird nur dort als `strom` ausgewiesen, wo er fachlich direkter Wohnungsstrom ist.
- Waermepumpenbasierte Warmwasseraufbereitung wird als `verbrauchskosten_warmwasser` ausgewiesen.

### `consumption_items`

- Abgeleiteter Waermepumpenstrom muss als Herleitung/Formel sichtbar sein.
- Er darf nicht als normaler Alt/Neu-Zaehlerstand erscheinen.
- Die Darstellung darf technisch variieren, muss aber maschinell pruefbar bleiben.

Normativer Mindestvertrag fuer maschinelle Pruefbarkeit:

- Es gibt mindestens ein Element in `consumption_items` mit `item_type = "derived_formula_wp_strom"`.
- Dieses Element enthaelt `formula = "Zaehler_BE1_Gesamtanlage - Zaehler_NE1_individual - Zaehler_NE2_individual"`.
- Dieses Element enthaelt `meter_refs = ["Zaehler_BE1_Gesamtanlage", "Zaehler_NE1_individual", "Zaehler_NE2_individual"]`.
- Dieses Element enthaelt `derived_value` als numerischen Wert fuer die abgeleitete Groesse.

## Glossar und Mapping

- Fachbegriff `Direkter Strom` -> Kostenart `strom` (nur direkt zurechenbarer Wohnungsstrom)
- Fachbegriff `Waermepumpenstrom` -> abgeleitete Basis fuer Warmwasser (kein eigener Mieter-Stromposten)
- Fachbegriff `Warmwasserkosten` -> Kostenart `verbrauchskosten_warmwasser`
- Ausgabe `cost_items` -> enthaelt abrechnungsrelevante Kostenarten je NE
- Ausgabe `consumption_items` -> enthaelt Verbrauchs- und Herleitungsinformationen

## Implementierungshinweis (nicht normativ)

Die konkrete technische Darstellung der WP-Herleitung ist ein Implementierungsdetail. Fuer spaetere Umsetzung ist jedoch sicherzustellen, dass die Herleitung in den Ausgaben eindeutig nachvollziehbar ist und maschinell validiert werden kann.

Beispielhafte Minimalanforderung fuer die Umsetzung:

- Die konkrete Feldbenennung kann intern variieren, solange sie in eine stabile API-Ausgabe mit den oben genannten Mindestinformationen gemappt wird.

## Oracle 2024

## Festgelegte Werte fuer NE1

### A. Direkter Strom NE1

- Zeitraum: 01/2024-10/2024
- Erwarteter Wert: **497,15 EUR**

### B. Verbrauchskosten Warmwasser NE1

- Excel2024 verwendet faelschlich 01/2024-12/2024 Gesamtkosten: **858,82 EUR**
- Fachlich korrekter Gesamtkostenwert fuer den NE1-Zeitraum 01/2024-10/2024: **717,46 EUR**
- Gesamtverbrauch Warmwasser: **57,95 m3**
- Verbrauch NE1: **32,56 m3**
- Anteil NE1: **0,561863676**
- Erwarteter Kostenanteil NE1: **403,21 EUR**

## Festgelegte Oracle-Werte fuer weitere NEs (2024)

### C. Direkter Strom NE2

- Zeitraum: 01/2024-12/2024
- Erwarteter Wert: **541.90 EUR**

### D. Verbrauchskosten Warmwasser NE2

- Zeitraum: 01/2024-12/2024
- Erwarteter Wert: **376.28 EUR**

### E. Direkter Strom NE4

- Zeitraum: 01/2024-12/2024
- Erwarteter Wert: **83.70 EUR**

### F. Warmwasserzuordnung fuer BE2 (NE3/NE4/NE5)

- In BE2 werden keine separaten Verbrauchskosten Warmwasser als eigene Kostenposition ausgewiesen.
- Heizung und warmes Brauchwasser werden ueber den Kessel bereitgestellt und ueber Heizkosten umgelegt.
- Fuer NE3/NE4/NE5 wird daher in der Strom-/Warmwasser-Sicht der Status `Warmwasser separat: nein (in Heizkosten enthalten)` explizit gefuehrt.

## Oracle-Vergleichsregel (normativ)

- Fuer die in dieser Spec festgelegten 2024-Oracles gilt eine feste absolute Toleranz von 0.01 EUR.
- Klassifikation ist ausschliesslich `gleich` oder `Implementierungsfehler`.
- Eine Ausnahme- oder Bugwert-Kategorie fuer alte Excel-Werte ist nicht zulaessig.

## Abnahmekriterien

### Pflicht

1. Tarifmodus mit `stromtarife` und gleichzeitigem Strom-Beleg bricht fail-fast ab.
2. Direkter Strom NE1 wird im 2024-Oracle mit **497,15 EUR** validiert.
3. Warmwasserkosten NE1 werden im 2024-Oracle mit **403,21 EUR** validiert.
4. Waermepumpenstrom erscheint als Herleitung, nicht als eigenstaendige `strom`-Kostenposition.
5. Kosten aus der Waermepumpen-Herleitung laufen kostenartenmaessig unter `verbrauchskosten_warmwasser`.
6. Die WP-Herleitung ist ueber `item_type`, `formula`, `meter_refs` und `derived_value` maschinell pruefbar referenzierbar.
7. Direkter Strom NE2 wird im 2024-Oracle mit **541.90 EUR** validiert.
8. Direkter Strom NE4 wird im 2024-Oracle mit **83.70 EUR** validiert.
9. Fuer BE2 (NE3/NE4/NE5) wird kein separater Warmwasser-Verbrauchskostenposten ausgewiesen.
10. Oracle-Vergleiche verwenden feste Toleranz 0.01 EUR und erlauben keine Ausnahmekategorie fuer alte Excel-Bugwerte.

### Nicht akzeptabel

- Doppelzaehlung von Strom im Tarifmodus
- Zuordnung von WP-Kosten zu `strom` statt `verbrauchskosten_warmwasser`
- Verwendung von Excel-Ergebniszellen als operative Input-Kosten

## Migrationshinweise fuer die Umsetzung

1. Bestehende Strom-Oracles, die auf der Vermischung von direktem Strom und WP-Kosten beruhen, muessen bereinigt werden.
2. Fixtures muessen in direkten Modus und Tarifmodus sauber getrennt werden.
3. Bestehende Tests fuer `strom` und `verbrauchskosten_warmwasser` sind entlang dieser Fachgrenze neu zu schneiden.

## History

| Date | Iteration | Author | Delta |
|---|---|---|---|
| 2026-03-27 | 0 | Copilot | Neue dedizierte Spec erstellt: direkte Stromkosten und Warmwasseraufbereitung durch Waermepumpe fachlich getrennt, NE1-Oracle festgelegt, offene Oracle-Punkte fuer NE2/NE4 markiert |
| 2026-03-27 | 1 | User + Copilot | Zeitlogik auf Haupt-Spec referenziert (NE1 Teiljahr, andere Volljahr), BE1-Regel als allgemeine objektspezifische Fachregel klargestellt, Glossar/Mapping und nicht-normativer Implementierungshinweis ergaenzt, Sprachkonsistenz verbessert |
| 2026-03-27 | 2 | Copilot | Redaktionelle Verfeinerung: Bezuege vereinfacht, Zeitlogik-Verweis explizit gemacht, Excel-Abgrenzung und Output-Pruefbarkeit geschaerft, Abnahmekriterien um maschinelle Pruefbarkeit ergaenzt |
| 2026-03-27 | 3 | Copilot | Offene MISSING-Direktiven aufgeloest: NE2/NE4 Oracle-Werte festgelegt, BE2-Regel fuer NE3/NE4/NE5 als explizite finale Vorgabe eingearbeitet, Abnahmekriterien erweitert |
| 2026-03-27 | 4 | Copilot | Vorschlaege fuer Punkt 1 und 2 eingearbeitet: konkreter normativer Output-Mindestvertrag fuer maschinelle Pruefbarkeit definiert und Bezuege als explizite relative Pfade im _specs-Ordner praezisiert |
| 2026-03-27 | 5 | Copilot (GPT-5.3-Codex) | Oracle-Vergleichsregel normiert: feste 0.01 EUR Toleranz, nur `gleich`/`Implementierungsfehler`, keine Ausnahme fuer alte Excel-Bugwerte. |