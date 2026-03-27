# Stromkosten-Datenkorrektur und Test-Oracle Alignment (Neubewertung 2026-03-27)

## Zweck

Diese Notiz ersetzt die vorherige Bewertung vom 2026-03-26 inhaltlich. Die damalige These war in zentralen Punkten falsch oder unvollstaendig. Grundlage dieser Neubewertung sind:

- die fachliche Regel in der Haupt-Spec (/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-03-24 Nebenkostenabrechnung Applikation.md) zu Waermepumpen-Stromkosten,
- der aktuelle Stand der JSON-Fixtures,
- die reproduzierte Tariflauf-Analyse,
- und die vom Benutzer konkretisierten 2024-Werte fuer NE1.

## Korrigierte Kernaussagen

### 1. Der Strom-Beleg in `input_tariff_from_excel.json` ist falsch und muss entfernt werden

Die Datei
`/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/data/2024/input_tariff_from_excel.json`
enthaelt aktuell einen BE-bezogenen Strom-Kostenbeleg:

```json
{
  "id": "kb-strom-be1",
  "kostenart_id": "strom",
  "betrag": 2344.79,
  "datum": "2024-03-01",
  "scope": {
    "berechnungseinheit": "be1"
  }
}
```

Dieser Beleg ist fachlich falsch, weil der Tarif-Input gerade nicht mit einem operativen Strom-Beleg kombiniert werden darf. Er fuehrt in der aktuellen Implementierung dazu, dass im Tarifmodus einerseits Strom aus dem Beleg verteilt und andererseits zusaetzlich individueller Tarifstrom erzeugt wird.

**Folge:** Doppelzaehlung im Tarifmodus.

**Bewertung:** Diese Beobachtung bestaetigt Punkt 1 der vorherigen Analyse. Der Fehler sitzt hier nicht in der Haupt-Spec, sondern im Fixture `input_tariff_from_excel.json`.

### 2. Die fachlich richtige Ableitung lautet: WP-Stromkosten gehoeren zur Kostenart Warmwasser, nicht zur Kostenart Strom

Die Haupt-Spec ist in der Berechnungslogik an dieser Stelle korrekt:

> **Waermepumpen-Stromkosten (BE1 spezial)**
> - Kostenbasis wird aus Stromzaehlern abgeleitet: `WP_Strom = Zähler_BE1_Gesamtanlage − Zähler_NE1_individual − Zähler_NE2_individual`
> - Diese Kostenbasis wird dann nach Warmwasserzaehler (WW-Verbrauch) auf NE1 und NE2 umgelegt
> - Dies ist eine abgeleitete Groesse, keine Messung — muss in Zwischenergebnis als Formel ausgewiesen werden, nicht als Alt/Neu/Differenz

Der fachliche Fehler in der Entwicklung liegt damit nicht in der Formel, sondern in der Vermischung zweier Ebenen:

- **Mess- und Herleitungsebene:** Stromzaehler liefern die Kostenbasis der Waermepumpe.
- **Kostenartenebene:** Die daraus entstehenden Kosten sind der Warmwasseraufbereitung zuzuordnen.

Die bisherige Umsetzung hat Stromkosten teilweise als eigene Kostenart `strom` behandelt, obwohl die abgeleiteten Waermepumpen-Kosten fachlich zur Kostenart `verbrauchskosten_warmwasser` gehoeren.

**Korrigierte Fachregel:**

- Individuelle NE-Stromkosten bleiben nur dort eigenstaendig, wo es sich um echten, direkt zurechenbaren Wohnungsstrom handelt.
- Der aus `BE1-Gesamt - NE1 - NE2` hergeleitete Waermepumpenstrom ist keine eigenstaendige Kostenart `strom`, sondern Kostenbasis fuer Warmwasser.
- Diese Kostenbasis wird ueber Warmwasserverbrauch auf NE1 und NE2 verteilt.

### 3. Die Umstellung auf 528,24 EUR fuer NE1 war in dieser Form nicht belastbar

Die vorherige Notiz behauptete, 528,24 EUR fuer NE1 seien der neue korrekte Stromwert. Diese Aussage ist nach dem aktuellen fachlichen Stand nicht haltbar.

Der Benutzer hat fuer die 2024er Abrechnung NE1 folgende Werte vorgegeben:

- Stromkosten NE1 fuer Zeitraum 01/2024-10/2024: **497,15 EUR sind korrekt**
- Verbrauchskosten Warmwasser wurden in Excel2024 falsch berechnet
- Excel2024 hat faelschlich Gesamtkosten fuer 01/2024-12/2024 verwendet: **858,82 EUR**
- Korrekt fuer NE1 ist jedoch der Zeitraum 01/2024-10/2024 mit Warmwasser-Gesamtkosten: **717,46 EUR**
- Gesamtverbrauch Warmwasser: **57,95 m3**
- Verbrauch NE1: **32,56 m3**
- Anteil: **0,561863676**
- Daraus resultierender NE1-Anteil Warmwasser: **403,21 EUR**

Damit war die damalige Schlussfolgerung sachlich falsch, weil sie:

- Stromkosten und Warmwasserkosten nicht sauber getrennt hat,
- aus Strommesswerten direkt eine neue Strom-Orakelzahl abgeleitet hat,
- statt die Warmwasser-Kostenart und deren Zeitanteil fuer NE1 neu zu bewerten.

## Neubewertung der vorherigen Punkte

### Punkt 1 aus der vorherigen Analyse: Tarifmodus zaehlt Strom doppelt

**Status:** bleibt richtig.

Der konkrete Ausloeser ist der falsche Strombeleg in `input_tariff_from_excel.json`. Dieser Beleg muss entfernt werden. Solange er existiert, ist jeder Tariflauf fachlich kontaminiert.

### Punkt 2 aus der vorherigen Analyse: WP-Strom ist nicht Ende-zu-Ende korrekt umgesetzt

**Status:** bleibt richtig, aber praeziser gefasst.

Nicht die Formel ist das Problem, sondern die Zuordnung im Kostenartenmodell und in den Tests:

- WP-Strom wird korrekt als Herleitung benoetigt,
- darf aber nicht als eigenstaendige `strom`-Kostenposition enden,
- sondern muss in `verbrauchskosten_warmwasser` einfliessen.

### Punkt 3 aus der vorherigen Analyse: Spec-Widerspruch

**Status:** weiterhin richtig.

Die Haupt-Spec ist in der WP-Logik korrekt, aber der dokumentierte Umgang mit Strom- und Warmwasserkosten ist in den nachgelagerten Entwicklungsartefakten nicht sauber getrennt worden. Genau daraus entstanden die inkonsistenten Orakelwerte und Testanpassungen.

### Punkt 4 aus der vorherigen Analyse: Tests validieren nicht sauber den gewuenschten Excel-/Tariffluss

**Status:** bleibt richtig.

Nach deiner Klarstellung ist jetzt noch deutlicher:

- Tests duerfen nicht nur auf einer allgemeinen Strom-Orakelzahl beruhen,
- sondern muessen zwischen direktem Wohnungsstrom und in Warmwasser aufgehenden Waermepumpenkosten unterscheiden,
- und fuer 2024 explizit die korrigierten NE1-Werte verwenden.

## Konkrete 2024-Werte fuer NE1, die kuenftig fuer Tests gelten sollen

### A. Direkter Strom NE1

- Zeitraum: 01/2024-10/2024
- Erwarteter Wert: **497,15 EUR**

### B. Verbrauchskosten Warmwasser NE1

- Excel2024 verwendet faelschlich den Jahreswert 01/2024-12/2024: **858,82 EUR**
- Fachlich korrekter Gesamtkostenwert fuer NE1-Zeitraum 01/2024-10/2024: **717,46 EUR**
- Gesamtverbrauch Warmwasser: **57,95 m3**
- Verbrauch NE1: **32,56 m3**
- Anteil NE1: **0,561863676**
- Erwarteter Kostenanteil NE1 Warmwasser: **403,21 EUR**

### C. Konsequenz fuer das Oracle

Die vorherige Umstellung auf hoehere Stromwerte wie 528,24 EUR war keine saubere Korrektur des Oracle, sondern eine Vermischung von:

- direktem Strom,
- Tarifherleitung,
- und Warmwasseraufbereitung per Waermepumpe.

Fuer die 2024-Regression muss diese Trennung im Oracle kuenftig explizit gemacht werden.

## Empfehlung zum Rollback der letzten Aenderungen

### Empfehlung: Ja, die letzten Strom-/Oracle-Aenderungen sollten inhaltlich zurueckgerollt werden

Diese Empfehlung bezieht sich auf die inhaltliche Richtung der letzten Aenderungen, insbesondere:

- die Erhoehung der direkten Strom-Orakelwerte auf 528,24 / 587,35 / 134,84,
- die daraus abgeleiteten Testanpassungen,
- und die zu starke Deutung der Stromzaehlerkorrektur als direkte Stromkostenkorrektur.

### Was dabei nicht zurueckgerollt werden sollte

Nicht jede einzelne Beobachtung war falsch. Beibehalten werden sollten die Erkenntnisse, dass:

- der Tarif-Input nicht mit einem Strombeleg kombiniert werden darf,
- die WP-Herleitung als Formel sichtbar sein muss,
- und die Entwicklung aktuell Strom und Warmwasser fachlich vermischt.

### Was fachlich zurueck auf den Stand vor der Fehlumstellung sollte

- Direkter Strom NE1 2024 wieder auf **497,15 EUR**
- Keine automatische Umdeutung des WP-Stroms zu eigenstaendigen `strom`-Orakelwerten
- Warmwasserkosten separat mit korrektem Zeitraum und WW-Verbrauch neu aufsetzen

## Korrigierte Problemformulierung

Die eigentliche Ursache war nicht primaer: "Messwerte waren falsch, deshalb musste Strom neu berechnet werden".

Die eigentliche Ursache lautet jetzt:

1. Im Tarif-Fixture existiert ein fachlich unzulaessiger Strombeleg.
2. In der Umsetzung wurden Kostenart `strom` und `verbrauchskosten_warmwasser` nicht sauber getrennt.
3. Die Waermepumpen-Herleitung wurde teilweise wie eine Strom-Kostenart behandelt, obwohl sie fachlich Warmwasser betrifft.
4. Dadurch wurden Tests und Oracle in eine falsche Richtung korrigiert.

## Offene Punkte fuer die naechste Session

Diese Punkte sind fuer die neue Strom-/Warmwasser-Spec relevant:

1. Eindeutige Trennung zwischen direktem Wohnungsstrom und WP-basierten Warmwasserkosten
2. Endgueltige Definition, ob die Kostenart `strom` in 2024 nur NE-individuellen Wohnungsstrom enthaelt
3. Definition des korrekten 2024-Oracle fuer NE2 und NE4 unter derselben Trennlogik
4. Technische Abbildung im Rechenkern: WP-Herleitung sichtbar, aber kostenartenmaessig unter Warmwasser verbucht
5. Teststrategie: direkte Stromtests getrennt von Warmwasser-/WP-Tests

## History

| Date | Iteration | Author | Delta |
|---|---|---|---|
| 2026-03-26 | 0 | Copilot | Erste Analyse erstellt, spaeter als fachlich fehlerhaft erkannt |
| 2026-03-27 | 1 | Copilot | Analyse nach Benutzerkorrektur neu bewertet: falschen Tarif-Strombeleg, korrekte WP->Warmwasser-Zuordnung, NE1-Werte 497,15 EUR und 403,21 EUR festgehalten, Rollback der letzten Strom-Orakel-Aenderungen empfohlen |
