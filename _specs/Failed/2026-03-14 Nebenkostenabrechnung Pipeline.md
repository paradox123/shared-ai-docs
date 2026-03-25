# Nebenkostenabrechnung Neustart-Spec

## Status
- Diese Datei ist die **autoritative Neustart-Spec** fuer die weitere Arbeit.
- Die fruehere Langhistorie wurde archiviert unter:
  - `/Users/dh/Documents/DanielsVault/_shared/_specs/Failed/2026-03-14 Nebenkostenabrechnung Pipeline.history.md`

## Problem Statement
- Ziel ist eine lokal laufende Nebenkosten-Pipeline fuer `Hauptstr. 2, 36381 Schluechtern`.
- Das spaetere Produkt soll aus echten Quelldokumenten nachvollziehbare Einzelabrechnungen erzeugen.
- Jeder sichtbare Wert muss auf eine kanonische Quelle und eine explizite Herleitung zurueckfuehrbar sein.

## Harte Leitlinien
1. **Kein Excel im operativen Lauf**
   - Das Legacy-Workbook ist kein produktiver Laufzeit-Input und kein stiller Fallback.
   - Fehlende operative Daten duerfen nicht durch Workbook-Werte, implizite Annahmen oder geratene Defaults ersetzt werden.
2. **Excel nur als Test-Orakel**
   - Das 2024er Workbook und die manuell erstellten 2024er Abrechnungen duerfen nur fuer Test, Vergleich und Delta-Erklaerung genutzt werden.
   - Diese Orakel-Nutzung erzeugt keinen Rueckkanal in den operativen Lauf.
3. **Explizite Source-of-Truth-Kette**
   - Quelldokumente / manuelle Operatorentscheidungen
   - Extraktion / Import
   - kanonisches Eingabepaket
   - Berechnung
   - Render-Payloads
   - Mieterabrechnung / Pruefbericht
4. **Ehrliche Darstellung**
   - Wenn Rohmesswerte, Zuordnungen oder Herleitungen nicht belastbar vorliegen, muss dies offen kenntlich sein.
5. **Lesbare Fachsprache**
   - Interne Kuerzel wie `BE1`, `BE2`, `VE1` oder technische Scope-Begriffe duerfen im tenant-facing Dokument nicht unerklaert auftauchen.

## Produktbild
- Das Zielprodukt besteht aus drei klar getrennten Teilen:
  1. **Fachlicher Kern**
     - neue Implementierung in C#
     - enthaelt Domänenlogik, Berechnungsregeln, Review-Entscheidungen und fachlich richtige Ergebnisse
  2. **Import / OCR**
     - erschliesst spaeter Dokumente fuer den Produktivlauf
  3. **Dokumente / PDF**
     - erzeugt spaeter Einzelabrechnungen und Pruefberichte aus stabilen Kernresultaten
- Der fachliche Kern darf nicht von OCR, PDF-Rendering oder dem Legacy-Workbook abhaengen.

## Neustart-Reihenfolge
1. Zuerst den fachlichen Kern neu aufbauen und gegen 2024 verifizieren.
2. Danach Import-/OCR-Schicht an den Kern anbinden.
3. Danach PDF-/Dokumentschicht auf die stabilen Kernresultate setzen.

## Bedeutung von "fachlich stabil"
- Der neue Kern gilt fuer einen definierten Scope als fachlich stabil, wenn:
  - die vereinbarten 2024-Vergleichswerte fuer diesen Scope reproduzierbar erreicht oder sauber erklaert abweichend dokumentiert werden,
  - keine offenen blockerhaften Review-Faelle mehr bestehen, die die fachliche Aussagekraft des Ergebnisses untergraben,
  - die Ergebnisse fuer Mieter und Operatoren nachvollziehbar voneinander herleitbar sind.
- `fachlich stabil` bedeutet ausdruecklich nicht, dass OCR und PDF bereits final ausgebaut sein muessen.

## Kanonisches operatives Eingabepaket
- Der spaetere produktive Lauf verwendet ein **kanonisches, versionierbares Eingabepaket** aus strukturierten Artefakten.
- Dieses Eingabepaket muss mindestens abdecken:
  1. Objektsicht und Zuordnung von Berechnungseinheiten, Nutzeinheiten und relevanten Zaehlern,
  2. Parteien, Rollen und Abrechnungszeiträume,
  3. Zahlungen / Vorauszahlungen je Partei,
  4. Tarife und sonstige preisrelevante Zeitabschnitte,
  5. abrechnungsrelevante Mess- und Verbrauchsdaten,
  6. Kostenpositionen / normalisierte Beleginformationen,
  7. notwendige manuelle Operatorentscheidungen fuer nicht deterministische Zuordnungen.
- Die konkrete technische Serialisierung dieses Pakets ist Teil des Implementierungsplans, nicht dieser Spec.

## Zahlungsinput
- Zahlungen und Vorauszahlungen sind ein eigener verpflichtender Teil des kanonischen Eingabepakets.
- Der Kern rechnet mit bestaetigten Zahlungsfakten, nicht mit rohen Kontoauszuegen oder PDF-Kontoexporten.
- Ein spaeterer Import aus Kontoauszuegen oder PDF-Dokumenten darf solche Zahlungsfakten erzeugen, ersetzt aber nicht die Pflicht zu einem belastbaren Zahlungsinput.

## Verbindliches 2024-Testorakel
- Der Neustart verifiziert den neuen Kern gegen einen klaren 2024-Referenzstand.
- Dieses Testorakel besteht mindestens aus:
  - dem 2024er Legacy-Workbook inklusive der relevanten Blaetter,
  - den manuell erstellten 2024er Einzelabrechnungen,
  - den 2024er Quelldokumenten fuer Messwerte, Ablesungen und Belege,
  - den fuer 2024 benoetigten Zahlungsinformationen.
- Als fachlich verbindliche Vergleichsdimensionen gelten mindestens:
  1. Parteien, Rollen, Zeitraeume und Zuordnung zu Berechnungseinheiten,
  2. Zahlungen und Vorauszahlungen,
  3. relevante Tarif- und Verbrauchswerte,
  4. Endergebnisse je Partei,
  5. objektspezifische Sonderregeln.

## Objektspezifische Sonderregeln
- **Berechnungseinheit 1**
  - Oel und Waermepumpe gehoeren fachlich zu Berechnungseinheit 1.
  - Die Warmwasseraufbereitung in Berechnungseinheit 1 erfolgt ueber eine Waermepumpe am allgemeinen Stromzaehler von Berechnungseinheit 1.
  - Die Stromkosten fuer Warmwasser ergeben sich fachlich aus dem Allgemeinstrom der Berechnungseinheit 1 abzueglich der eindeutig zuordenbaren Stromverbraeuche der Nutzeinheiten 1 und 2.
  - Der so ermittelte Warmwasser-Stromanteil wird nach Warmwasserverbrauch auf die betroffenen Einheiten in Berechnungseinheit 1 verteilt.
- **Berechnungseinheit 2**
  - Holz und Pellets gehoeren fachlich zu Berechnungseinheit 2 und decken dort Heizung und Warmwasser ab.
- **Kaltwasser fuer Nutzeinheit 5**
  - Der Hauptanschluss zaehlt den Gesamtverbrauch des Kaltwassers im Objekt.
  - Die Nutzeinheiten 1 bis 4 verfuegen ueber eigene Kaltwasserzaehler.
  - Der Kaltwasserverbrauch der Nutzeinheit 5 ergibt sich als Restgroesse aus Hauptanschluss minus Nutzeinheiten 1 bis 4.
- **Gebaeudeversicherung**
  - Die Gebaeudeversicherung besteht fuer das relevante Objekt aus drei getrennten Vertraegen.
  - Ein Vertrag betrifft `NE4` und `NE5`.
  - Ein Vertrag betrifft ausschliesslich `NE3`.
  - Ein Vertrag betrifft `NE1` und `NE2`.

## Tenant-Facing Mieterabrechnung
- Die spaetere Mieterabrechnung ist das lesbare Ergebnisdokument fuer den Mieter.
- Sie soll mindestens enthalten:
  - Objekt, Partei und Abrechnungszeitraum,
  - Gesamtkosten, bereits gezahlte Vorauszahlungen und Ergebnis,
  - tabellarische Darstellung der relevanten Kostenarten,
  - lesbare Umlage- bzw. Herleitungslogik pro relevanter Position,
  - nachvollziehbare Verbrauchsermittlung bei verbrauchsabhaengigen Kosten, samt relevanter Messwerte,
  - verstaendliche Sprache ohne unerklaerte interne Kuerzel,
  - nachvollziehbare Sonderhinweise fuer fachliche Spezialfaelle,
  - nicht verbrauchsabhaengige **Schluesselwerte** und deren Herleitung, soweit sie fuer die konkrete Umlage relevant sind.
- Dazu gehoeren insbesondere:
  - verwendete Verteilungsschluessel,
  - die dazugehoerigen Basiswerte der betroffenen Einheit oder Partei,
  - die Herleitung dieser Basiswerte, soweit sie fuer die konkrete Umlage relevant ist.

## Operatorseitiger Pruefbericht
- Der Pruefbericht ist ein operatorseitiges Kontroll- und Nachweisdokument.
- Er ist nicht Teil der eigentlichen Mieterkommunikation und muss nicht auf Mieterlesbarkeit optimiert sein.
- Er soll mindestens enthalten:
  - Quellenbezug auf Dokumente, strukturierte Eingaben und Operatorentscheidungen,
  - relevante Formeln und Zwischenwerte,
  - erklaerte Abweichungen gegenueber dem 2024-Testorakel,
  - offene Warnungen und blockerhafte Sachverhalte,
  - die Herleitung vom fachlichen Input zum Endergebnis.

## Review- und Freigabepolitik
- **Blocker** verhindern ein freigabefaehiges tenant-facing Ergebnis fuer den betroffenen Scope.
- Ein operativer Lauf muss mindestens dann stoppen oder als nicht freigabefaehig gelten, wenn:
  - zentrale Pflichtdaten fuer Partei, Zeitraum, Kostenart oder Zahlungen fehlen,
  - die fachlich noetige Verbrauchs- oder Umlagebasis fehlt,
  - heizungsnahe oder vergleichbar kritische Belege keinem belastbaren Umlagebereich zugeordnet werden koennen,
  - Zaehler oder Messwerte widerspruechlich oder nicht eindeutig zuordenbar sind,
  - Tarifdefinitionen fuer den relevanten Zeitraum fachlich nicht belastbar sind,
  - notwendige Operatorentscheidungen fehlen oder sich widersprechen.
- **Warnungen** duerfen einen Lauf nicht automatisch stoppen, muessen aber fuer Operatoren sichtbar und im Pruefkontext nachvollziehbar dokumentiert werden.
- Ein Ergebnis darf nur dann als freigabefaehige Mieterabrechnung gelten, wenn fuer den betreffenden Scope keine offenen blockerhaften Sachverhalte mehr bestehen.

## Workbook-Migrationspolitik
- Es gibt keinen workbook-basierten operativen Lauf und keinen stillen Workbook-Migrationspfad.
- Ein allgemeiner Workbook-Migrationsbefehl ist nicht Teil des Neustart-MVP.
- Falls spaeter ein einmaliger Migrationshelfer gebaut wird, ist er:
  - explizit separat,
  - nur fuer Migration/Testvorbereitung gedacht,
  - ausserhalb des operativen Laufpfads,
  - und seine Ergebnisse muessen als strukturierte Eingaben pruefbar und reviewbar sein.

## Acceptance Criteria
1. Es gibt einen neuen C#-Rechenkern, der ohne operative Excel-Abhaengigkeit gegen 2024 getestet werden kann.
2. Die 2024er Excel-/Abrechnungswerte werden nur fuer Tests und Vergleich genutzt.
3. Der spaetere Produktpfad bleibt offen fuer OCR und PDF, ohne den Kern wieder zu vermischen.
4. Die spaetere Mieterabrechnung zeigt die fuer die Umlage relevanten Schluesselwerte und Herleitungen nachvollziehbar an.
5. Die Spec ist damit auf Produktniveau konsistent und bereit fuer die Ableitung eines Implementierungsplans.
