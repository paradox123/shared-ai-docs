# Nebenkostenabrechnung 2025 - Belege und Messwerte

## Statushinweis

Diese Spec beschreibt weiterhin das fachliche Zielbild fuer die Vorverarbeitung von Belegen und Messwerten 2025.

Stand `2026-04-09` ist sie jedoch **nicht als operativ vollstaendig umgesetzt** zu lesen. Die aktuelle Code- und Realdatenbewertung zeigt, dass wesentliche Teile der hier beschriebenen Ziel-Vorverarbeitung fuer die echten 2025er Unterlagen noch nicht durchgaengig implementiert sind, insbesondere:

- OCR fuer bildbasierte Messwert- und Belegquellen
- Segmentierung und operative Extraktion von Sammelbelegen
- Parser fuer allgemeine Belege, Versicherungen und `ista_period_or_snapshot`
- robuste Tibber-Verarbeitung fuer reale 2025er Rechnungen mit Verbrauchsanpassungen und Zaehlerwechsel

Fuer die konkrete Erstellung der Nebenkostenabrechnung 2025 ist deshalb die operative Ausfuehrungsspec
[`2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad`](./Completed/2026-04-09%20Nebenkostenabrechnung%202025%20Realdaten%20und%20Abrechnungspfad.md)
massgeblich.

Diese Datei bleibt damit:

- **normative Zielbeschreibung** fuer den angestrebten Import-/Vorverarbeitungspfad
- **nicht** der Nachweis, dass dieser Pfad fuer die echten 2025er Unterlagen bereits vollstaendig verfuegbar ist

## Titel und Einordnung

Diese Spec konkretisiert die Vorverarbeitung fuer gescannte **Belege** und **Messwerte** des Abrechnungsjahres 2025.

Sie ergaenzt und referenziert normativ die Hauptspec
[`2026-03-24 Nebenkostenabrechnung Applikation`](./2026-03-24%20Nebenkostenabrechnung%20Applikation.md).

Die Hauptspec bleibt massgeblich fuer:

- fachliches Domänenmodell
- Berechnungslogik
- Validierungslogik des Input-JSON
- Ausgabeformate der Anwendung

Diese Spec ist massgeblich fuer:

- Quellklassifikation der 2025er PDFs
- OCR-/Extraktionsregeln
- Normalisierung in das bestehende `NebenkostenInput`-Format
- Scope-Inferenz fuer Belege
- Zaehler-Matching und OCR-Korrektur
- Ableitung monatlicher Tibber-`stromtarife[]`

## Verbindliche Randbedingung: keine Aenderung an Rechenkern und Rendering ab `input.json`

Diese Spec zielt primaer auf die **Vorverarbeitung bis zur gueltigen `input.json`**.

Ab dem Moment, in dem die `input.json` von der Anwendung unter
`/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung`
eingelesen wird, sollen **Rechenkern, Validierungslogik, Ausgabeaufbereitung und PDF-Rendering fachlich unveraendert bleiben**.

Die Vorverarbeitung hat sich an das bestehende Input-Modell (`InputDto.cs`) und an die bestehende Validierung (`InputValidator.cs`) anzupassen. Das ist hier moeglich, weil die aktuelle Anwendung bereits folgende fuer 2025 relevante Faelle abbildet:

- mehrere `zaehler[]` desselben Typs innerhalb einer NE
- mehrere `ablesungen[]` pro Zaehler
- zwei Ablese-Modelle:
  - Periodenmodell via `quelle` beginnend mit `ista`
  - Stichtagsmodell via `quelle = "manuell"`
- `stromtarife[]` je `be_id`

Anpassungen **vor** diesem Punkt, also in einer separaten Import-/Vorverarbeitungsschicht, sind von dieser Randbedingung nicht ausgeschlossen.

Eine Aenderung am Anwendungscode **nach dem Import der `input.json`** ist nur dann zulaessig, wenn **ein echter Bug** oder **eine fachlich notwendige, mit dem bestehenden JSON nicht ausdrueckbare 2025-Anforderung** nachgewiesen wird. In diesem Fall ist ein separater Bug-/Decision-Nachtrag zur Hauptspec anzulegen.

## Blockierende Voraussetzungen

Vor einer belastbaren Umsetzung der Vorverarbeitung muessen folgende Artefakte vorliegen:

- eine fachlich gepflegte Ziel-`input.json` oder ein gleichwertiger Input-Scaffold, in dem die kanonische `zaehler[]`-Liste fuer 2025 bereits enthalten ist
- eine fachlich gepflegte Zuordnung dieser Zaehler zu `ne_id`, `be_id` oder `objektweit`

Ohne diese Grundlage darf die Vorverarbeitung zwar OCR und Dokumentsegmentierung ausfuehren, aber **keine verbindliche automatische Zaehlerkorrektur** vornehmen.

## Bestehendes Zielmodell der Anwendung

Die Vorverarbeitung muss auf das bereits vorhandene operative JSON-Format zielen, wie es in
`private/Vermietung/nebenkosten-abrechnung/data/2024/input_tariff_from_excel.json`
und in der Hauptspec beschrieben ist.

Die aktuell implementierte Referenz fuer dieses operative Input-Schema ist
`/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/src/Nebenkosten.Core/Input/InputDto.cs`.

Relevant fuer diese Import-Spec sind insbesondere:

- `zaehler[]`
  - `id`, `typ`, `einheit`, `zaehlernummer`
  - optional `zugeordnete_ne`, `zugeordnete_be`, `objektweit`, `beschreibung`
- `ablesungen[]`
  - **ista-Modell**: `quelle`, `periode.von`, `periode.bis`, `messwert_alt`, `messwert_neu`, optional `ne_id`
  - **Stichtagsmodell**: `quelle = "manuell"`, `stichtag`, `messwert`, optional `ne_id`
- `kostenbelege[]`
  - `id`, `kostenart_id`, `betrag`, `datum`, optional `beschreibung`, optional `scope`
- `stromtarife[]`
  - `id`, `grundpreis_eur_jahr`, `arbeitspreis_ct_kwh`, `gueltig_von`, `gueltig_bis`, `be_id`, optional `lieferant`, `tarif`

**Wichtig:** Provenienz-, OCR- und Review-Metadaten gehoeren **nicht** in das operative Anwendungs-JSON, sondern in einen separaten Vorverarbeitungs-/Import-Manifest-Datensatz.

## Stichprobenartige Quellanalyse 2025

Die folgende Stichprobe wurde aus echten 2025er Dateien gezogen und dient als normative Grundlage fuer die Importregeln dieser Spec.

| Quelle | Typ | Stichprobe | Relevante Beobachtung |
|---|---|---|---|
| `Belege/Rechnung_1167054194.pdf` | Tibber-Rechnung | native Textlage | Rechnung Juni 2025, Zaehler `1ISK0078261075`, Verbrauch `615,32 kWh`, Gesamt `156,88 EUR`, dadurch monatlicher Stromtarif ableitbar |
| `Belege/Öl_25.pdf` | Oel-/Heizoelbeleg | Vision-OCR | Ommert Mineraloelhandel, Dokumentdatum `27.11.2025`, Produkt `HEL schwefelarm`, OCR zeigt brauchbare Liefer-/Rechnungsdaten, aber Einzelwerte brauchen Review |
| `Belege/Belege_BE1.pdf` | gebuendelter BE1-Beleg | Vision-OCR | ista Miet-/Wartungsrechnung, Rechnungsnummer `055650005`, Rechnungsdatum `06.01.2025`, Abrechnungszeitraum `01.01.2025 - 31.12.2025`, Scope-Hinweis durch Dateiname `BE1` |
| `Belege/Belege_Liegenschaft.pdf` | gebuendelter Liegenschaftsbeleg | Vision-OCR | Seite 1 ist Schornsteinfeger-Rechnung `J-25-02027` vom `01.08.2025`, Betrag `81,93 EUR`; Bundle muss in Einzelbelege zerlegt werden |
| `Messwerte/Ablesungen24_25.pdf` | Ableseprotokoll | Vision-OCR | Stichtagsformat mit `Ablesedatum 30.12.2024`, Wohnungen, Zaehlerarten und Ablesewerten; OCR produziert Zahlendreher/Extraziffern |
| `Messwerte/Monatswerte - 2025 -  - NE0001(P621593463).pdf` | ista Monatswerte | Vision-OCR | Pro Geraet monatliche Zeilen `Datum` + `Monatswert`; Beispielgeraete `120298189`, `120298011`, `120298110`, `120298127`; mehrere HKV innerhalb derselben NE |

## Zielbild der Vorverarbeitung

Die Vorverarbeitung besteht aus drei logisch getrennten Schichten:

1. **Quellextraktion**
   - PDF erkennen
   - nativen Text verwenden, falls vorhanden
   - sonst OCR anwenden
   - Seitenbereiche gebuendelter PDFs in logische Einzeldokumente zerlegen

2. **Normalisierung**
   - Belege und Messwerte in ein importfaehiges, quellnahes internes Modell ueberfuehren
   - Scope, Kostenart, Zaehlerzuordnung und Periodenform vereinheitlichen
   - OCR-Abweichungen gegen bekannte Zaehlernummern validieren und ggf. korrigieren

3. **Kanonisierung**
   - finales `NebenkostenInput`-JSON erzeugen
   - nur Felder verwenden, die die bestehende Anwendung bereits akzeptiert
   - Review-/OCR-/Provenienzinfos ausserhalb des operativen JSON ablegen

## Belege: Extraktions- und Mapping-Regeln

### Dokumentgrenze

Ein PDF ist nicht automatisch ein einzelner `kostenbeleg`.

Folgende Regeln gelten:

- Einzelrechnungen bleiben 1:1 ein `kostenbeleg`
- Sammel-PDFs wie `Belege_BE1.pdf`, `Belege_BE2.pdf`, `Belege_Liegenschaft.pdf` werden in **logische Einzelbelege pro Rechnung/Vertrag** aufgeteilt
- Die Aufteilung erfolgt seitenbasiert oder dokumentstruktur-basiert; ein Bundle darf mehrere operative `kostenbelege[]` erzeugen

Deterministische Mindestregel fuer Bundles:

- die **atomare Grundeinheit** ist zunaechst die einzelne PDF-Seite
- benachbarte Seiten duerfen nur dann zu **einem** logischen Beleg zusammengefuehrt werden, wenn mindestens eines der folgenden Merkmale den Zusammenhang belegt:
  - identische Rechnungs- oder Vertragsnummer
  - expliziter Fortsetzungsvermerk (`Seite x/y`, `Fortsetzung`, identischer Briefkopf plus gleiche Rechnungsreferenz)
  - eindeutig identischer Aussteller, Empfaenger, Rechnungsdatum und keine neue Rechnungskennung auf der Folgeseite
- wenn diese Merkmale fehlen oder widerspruechlich sind, wird **nicht** automatisch zusammengefuehrt
- unklare Seiten bleiben als getrennte vorlaeufige Einheiten erhalten und werden review-pflichtig markiert

### Zu extrahierende Mindestfelder pro Beleg

Jeder operative Beleg muss mindestens liefern:

- `id`
- `kostenart_id`
- `betrag`
- `datum`
- optionale `beschreibung`
- optionalen `scope`
- Verweis auf Quell-PDF und Seitenbereich im Import-Manifest

### Scope-Inferenz fuer Belege

Die Scope-Bestimmung erfolgt in dieser Prioritaet:

1. **Explizit im Dokumenttext**
   - z. B. konkrete Gebaeude-/Einheitsangabe
2. **Explizit im Dateinamen**
   - z. B. `BE1`, `BE2`, `Liegenschaft`
3. **Fachregel aus Kostenart und Objektwissen**
   - z. B. Oel für BE1 gemaess Hauptspec-Energietraeger
4. **Manueller Review**
   - wenn mehrere plausible Scopes verbleiben

Konfliktregel:

- **Dokumenttext gewinnt immer** gegen Dateiname und Domain-Regel
- **Dateiname gewinnt** gegen reine Domain-Regel
- die Domain-Regel darf nur als Tiebreaker verwendet werden, wenn weder Dokumenttext noch Dateiname den Scope eindeutig bestimmen
- ein Dateiname darf **nie** einen expliziten Dokumentscope ueberschreiben

Dateinamen sind damit **Hinweise**, aber nicht blind bindend. Ein Einzelbeleg in `Belege_Liegenschaft.pdf` darf nur dann BE-spezifisch gemappt werden, wenn der Belegtext diesen engeren Scope tatsaechlich hergibt.

### Kostenart-Mapping

Das Kostenart-Mapping bleibt an die Hauptspec und die bestehende Kostenarten-Matrix gebunden.

Wichtig fuer die Reihenfolge:

- zuerst wird pro logisch getrenntem Beleg der **Scope** nach den obigen Scope-Regeln bestimmt
- erst **danach** wird die `kostenart_id` auf diesen bereits gescopten Beleg angewendet
- die Kostenart selbst ueberschreibt keinen zuvor eindeutig bestimmten Scope

Beispiele aus der Stichprobe:

- Tibber-Rechnungen fuehren **nicht** zu `kostenbelege[]` fuer Strom, sondern zu `stromtarife[]`
- ista Miet-/Wartungsrechnungen aus `Belege_BE1.pdf` sind typischerweise `heiznebenkosten`
- Schornsteinfeger-, Versicherungs-, Steuer- und vergleichbare Objektkosten werden als normale `kostenbelege[]` erfasst

In grossen Teilen soll sich die `kostenart_id` bereits automatisch aus dem Belegtyp ergeben, z. B.:

- Strombeleg -> `strom` (ausser Tibber-Sonderfall `stromtarife[]`)
- Gebaeudeversicherung -> `gebaeude_versicherung`
- klar bezeichnete Steuer-, Schornsteinfeger- oder vergleichbare Objektbelege -> entsprechende Kostenart gemaess Kostenarten-Matrix

Wenn eine automatische Kostenart-Zuordnung nicht eindeutig moeglich ist, erfolgt **keine** stille Ratevergabe. Stattdessen gilt:

- der Beleg bzw. das Belegsegment wird im Import-Manifest mit `review_required = true` markiert
- die Ausgabe muss filterbar zeigen, welche Belege nicht zugeordnet werden konnten
- die finale Zuordnung von `kostenart_id` und ggf. `scope` erfolgt dann manuell auf Belegebene in der `input.json`

Eine spaetere V2 mit zusaetzlicher LLM-/Agent-Unterstuetzung fuer solche Grenzfaelle ist moeglich, aber **nicht** Teil dieser Spec.

## Messwerte: Quellformate und kanonische Abbildung

### Quellformat A: Zeitraum mit Anfangs- und Endwert

Wenn die Quelle bereits einen Verbrauch fuer einen Zeitraum liefert, wird sie direkt als `ista`-Periodenablesung abgebildet:

- `quelle`: `ista_ablese` oder `ista_monatsmittel`
- `periode.von`
- `periode.bis`
- `messwert_alt`
- `messwert_neu`
- optional `ne_id`

Verwendung der beiden `ista`-Varianten:

- `ista_ablese` fuer Quellen mit explizitem Anfangs- und Endwert einer Periode
- `ista_monatsmittel` nur fuer Quellen, deren Format **bereits fachlich bestaetigt** echte periodische Monatsintervalle repraesentiert
- aus OCR allein wird **nicht** automatisch zwischen `ista_ablese` und `ista_monatsmittel` geraten

Beispiel:

- Tibber-Rechnung Juni 2025: Startwert `25.787,00`, Endwert `26.402,32`, Verbrauch `615,32 kWh`

### Quellformat B: Messwert zu einem Stichtag

Wenn die Quelle nur echte Stichtagswerte ohne ableitbare Periodeninformation liefert, bleibt das Stichtagsmodell im operativen JSON erhalten:

- `quelle = "manuell"`
- `stichtag`
- `messwert`
- optional `ne_id`

Das betrifft insbesondere manuelle Ableseprotokolle oder vergleichbare Quellen, die gerade **keine** vollstaendige ista-Periodenableitung zulassen.

Beispiel:

- `Ablesungen24_25.pdf` mit `Ablesedatum 30.12.2024`

### Interpretation der `Monatswerte`-PDFs

Die OCR-Stichprobe zu `Monatswerte - 2025 -  - NE0001(P621593463).pdf` zeigt:

- Geraetebezogene Monatszeilen
- pro Zeile ein Datum (z. B. `31.01.2025`, `28.02.2025`, ...)
- pro Zeile einen `Monatswert`
- fuer Geraet `120298189` ansteigende Werte Richtung Jahresende (`63`, `486`, `1067`, `1745`)

Normative Interpretation:

- `Monatswerte` und vergleichbare ista-Exports werden **nicht** als `manuell` in das operative JSON uebernommen.
- Stattdessen werden sie anhand der Dokumentstruktur und der ista-Legende in **kanonische periodische ista-Ablesungen** ueberfuehrt.
- Monatliche Einzelzeilen sind dabei nur Quellmaterial zur Herleitung; sie werden nicht 1:1 als operative Einzelablesungen persistiert.
- Bei monatlichen ista-Quellen wird je Zaehler genau **eine** kanonische Periode fuer den fachlich relevanten Miet- bzw. Abrechnungszeitraum gebildet.

Fuer die Interpretation der ista-Messwerte ist die Legende der Dokumente massgeblich:

- Geraet `HKE` kennzeichnet den Messwert eines Heizkostenverteilers
- Geraet `WZK` kennzeichnet den Messwert eines Kaltwasserzaehlers
- Geraet `WZW` kennzeichnet den Messwert eines Warmwasserzaehlers
- Typ `AN` kennzeichnet den Anfangsmesswert der Periode
- Typ `ST` kennzeichnet den Stichtagswert der Periode; bei `HKE` wird nach der Lesung auf `0` zurueckgesetzt
- Typ `VJ` kennzeichnet den Vorjahreswert bzw. Anfangswert der Periode; dies ist insbesondere bei `WZK` und `WZW` relevant

Operative Ableitungsregel:

- wenn ein ista-Dokument anhand seiner Werte und Legende Anfangs- und Endwert einer fachlich zusammenhaengenden Periode hergibt, wird daraus ein kanonischer Datensatz mit `quelle = "ista_ablese"` oder `quelle = "ista_monatsmittel"` erzeugt
- fuer monatliche ista-Quellen wird **nicht** jeder Monat als eigener operativer Messwert erfasst
- stattdessen wird aus den Monatszeilen genau die eine Periode fuer den relevanten Miet- oder Abrechnungszeitraum der betroffenen NE/Mietpartei abgeleitet
- eine Umwandlung solcher ista-Dokumente auf `manuell` ist damit nicht erforderlich

Fuer diese Spec wird der **relevante Zeitraum** fuer solche `Monatswerte`-Dokumente praezisiert als:

- primaer der objektweite Abrechnungszeitraum des Zieljahres (z. B. `2025-01-01` bis `2025-12-31`)
- geschnitten mit der fachlich belastbar im Dokument belegten Periode des jeweiligen Zaehlerblocks

Kanonische Ableitung innerhalb dieses relevanten Zeitraums:

- `AN` ist der bevorzugte Startwert
- wenn `AN` fehlt, darf ersatzweise `VJ` als Startwert verwendet werden
- `ST` ist der Endwert
- daraus werden gesetzt:
  - `periode.von = Datum(Startwert)`
  - `periode.bis = Datum(Endwert)`
  - `messwert_alt = Wert(Startwert)`
  - `messwert_neu = Wert(Endwert)`

Mehrdeutige Mehrfach-Starts oder Mehrfach-Enden innerhalb desselben relevanten Zeitraums duerfen nicht geraten werden; sie sind entweder review-pflichtig oder fuehren zum Abbruch.

Damit ist der fruehere Review-Punkt beantwortet: Die Formatentscheidung erfolgt ueber Dokumenttyp und ista-Legende, nicht ueber eine unsichere OCR-Heuristik und auch nicht ueber einen pauschalen Snapshot-Default.

## Mehrere Geraete derselben Art in einer NE

Die 2025er Stichprobe zeigt fuer `NE0001` mehrere HKV-Geraete innerhalb derselben Nutzeinheit.

Das ist **kein** Grund fuer eine App-Aenderung.

Die bestehende Anwendung kann mehrere `zaehler[]` desselben Typs innerhalb einer NE bereits verarbeiten, weil sie Verbraeuche bei der Umlage je NE summiert. Deshalb gilt:

- jedes physische Geraet bekommt einen eigenen Eintrag in `zaehler[]`
- jede erkannte Ablesung referenziert genau diesen Zaehler
- die Aggregation auf NE-Ebene bleibt Aufgabe des bestehenden Rechenkerns

## Zaehler-Matching und OCR-Korrektur

### Ziel

Messwerte muessen gegen die erwarteten Zaehlernummern validiert werden. OCR-Abweichungen wie Extraziffern, fehlende Ziffern oder Zahlendreher sollen korrigiert werden, **aber nur bei eindeutiger Lage**.

Diese Regel ist erst operativ umsetzbar, wenn das 2025er Zaehlerregister als konkretes Artefakt vorliegt. Bis dahin sind erkannte Zaehlernummern hoechstens vorlaeufige OCR-Ergebnisse und im Import-Manifest als `review_required = true` zu kennzeichnen.

### Kanonische Matching-Strategie

Pro erkannter Quell-Zaehlerkennung werden folgende Varianten gebildet:

- Rohtext
- normalisiert alphanumerisch
- normalisiert nur Ziffern
- OCR-normalisiert mit typischen Ersetzungen (`O->0`, `I/l->1`, `S->5`, entfernte Leerzeichen und Satzzeichen)

Dann erfolgt der Abgleich gegen das fuer 2025 gepflegte Zaehlerregister fuer die Liegenschaft.

### Zulässige automatische Korrekturen

Automatische Korrektur ist nur erlaubt, wenn **genau ein** Kandidat uebrig bleibt und dieser fachlich zum Dokument passt:

- exakter Match nach Normalisierung
- eine einzelne Extraziffer am Rand
- eine einzelne fehlende Ziffer am Rand
- eine einzelne Transposition benachbarter Ziffern
- eine einzelne OCR-typische Zeichenverwechslung

Zusatzbedingungen:

- derselbe Kandidat muss auch zu Typ und Scope passen
- bei mehreren gleich guten Kandidaten gibt es **keine** Auto-Korrektur
- jede Korrektur wird im Import-Manifest protokolliert

### Beispiele aus der Stichprobe

Aus `Ablesungen24_25.pdf` ergeben sich OCR-Drifts wie:

- `2108757522` statt plausibel `210875752`
- `2008222190` statt plausibel `200822219`

Diese Faelle duerfen automatisch korrigiert werden, **wenn** die 2025er Zaehlerliste genau einen passenden Kalt-/Warmwasserzaehler im richtigen Scope kennt.

Das kanonische 2025er Zaehlerregister ist **kein separates Nebenartefakt**, sondern die bereits gepflegte `zaehler[]`-Liste der Ziel-`input.json`.

Fuer das Mapping gilt verbindlich:

- gegen Messwerte und Belege wird ausschliesslich auf bereits vorhandene Eintraege in `zaehler[]` gematcht
- aus Messwerten oder Belegen werden **keine neuen Zaehler** erzeugt
- OCR-Korrekturen duerfen nur auf einen bereits existierenden `zaehler[]`-Eintrag zeigen
- kann ein erkannter Zaehler nicht eindeutig auf einen vorhandenen Eintrag in `zaehler[]` gemappt werden, ist dies ein Fehler mit Abbruch der Vorverarbeitung

Die Mindeststruktur dieses kanonischen Registers ergibt sich direkt aus dem operativen Input-Schema, insbesondere aus `ZaehlerDto` in `InputDto.cs`.

## Tibber 2025 -> monatliche `stromtarife[]`

### Grundsatz

Die Tibber-Rechnungen aus `Belege/` werden **nicht** als `kostenbelege[]` fuer Strom importiert.

Stattdessen wird pro Rechnungsmonat ein eigener `stromtarif` erzeugt. Das ist zwingend, weil die bestehende Anwendung im Tarifmodus Stromkosten ausschliesslich aus:

- Stromverbrauchsmesswerten und
- `stromtarife[]`

berechnet und direkte Strom-Kostenbelege in diesem Modus verbietet.

### Monatliche Tarifbildung

Pro Tibber-Rechnung wird genau **ein** Tarif fuer den Rechnungsmonat und den zur Rechnung gehoerigen `be_id` erzeugt.

Pflichtfelder:

- `id`: z. B. `strom-beX-2025-06-tibber`
- `gueltig_von`: erster Tag des Rechnungsmonats
- `gueltig_bis`: letzter Tag des Rechnungsmonats
- `be_id`: aus validierter Zaehler-/NE-/BE-Zuordnung
- `lieferant = "Tibber"`
- `tarif`: frei lesbare Monatsbezeichnung

Preis-Prioritaet fuer die Tarifbildung:

1. **Direkt ausgewiesene Brutto-Einheitspreise pro `kWh`** haben Vorrang fuer `arbeitspreis_ct_kwh`.
2. **Direkt ausgewiesene periodengebundene Brutto-Fixkosten ohne Verbrauchsbezug** haben Vorrang fuer `grundpreis_brutto_monat`.
3. Nur wenn diese Direktangaben fehlen, werden die Fallback-Formeln dieser Spec verwendet.
4. Wenn weder direkte Angaben noch belastbare Fallback-Werte vorliegen, ist der Beleg review-pflichtig und es darf kein Tarif stillschweigend geraten werden.

### Ableitung von `arbeitspreis_ct_kwh`

Massgeblich ist der in der Tibber-Rechnung ausgewiesene **durchschnittliche Brutto-Arbeitspreis** des Rechnungsmonats.

Die Hauptregel ist:

- wenn die Rechnung einen **direkt ausgewiesenen Brutto-Einheitspreis pro kWh** enthaelt, wird dieser fuer `arbeitspreis_ct_kwh` verwendet
- wenn der direkt ausgewiesene Einheitspreis in `EUR/kWh` statt `ct/kWh` vorliegt, wird nur dieser Wert mit `* 100` nach `ct/kWh` umgerechnet
- wenn die Rechnung **keinen** direkt ausgewiesenen Brutto-Einheitspreis pro kWh enthaelt, wird ersatzweise aus Brutto-Arbeitskosten und Verbrauch auf `ct/kWh` umgerechnet
- massgeblich sind die **Brutto-Preise** der Rechnung

Als **direkt ausgewiesen** gilt dabei jeder Rechnungswert, der selbst bereits eine Preisangabe **pro kWh** enthaelt, unabhaengig von der genauen Benennung, z. B.:

- `... mit einem Durchschnittspreis von 13,77 ct/kWh`
- ein eigenstaendiges Preisfeld wie `Durchschnittspreis`, `Arbeitspreis` oder gleichwertig benannt
- eine direkt ausgewiesene Preisangabe in `EUR/kWh` oder `ct/kWh`

Nicht als direkte Preisangabe gelten bloss Summenwerte oder Kostenpositionen ohne Einheitsangabe pro `kWh`; dafuer ist der Fallback zu verwenden.

Fallback-Formel nur wenn kein direkter Durchschnittspreis in `ct/kWh` vorliegt:

`arbeitspreis_ct_kwh = (arbeitskosten_brutto_monat / verbrauch_kwh_monat) * 100`

Zusaetzlich gilt:

- nur die zum Rechnungsmonat gehoerigen Verbrauchskosten verwenden
- keine SEPA-/Zahlungsflussinformationen verwenden
- keine rein informativen Vorperiodenhinweise als separate Tarife importieren

### Ableitung von `grundpreis_eur_jahr`

Die Anwendung erwartet `grundpreis_eur_jahr`, verteilt aber tagesgenau je Tarifintervall.

Massgeblich ist die in der Tibber-Rechnung ausgewiesene **Brutto-Grundgebuehr** bzw. die Summe aller explizit periodengebundenen, nicht verbrauchsabhaengigen Brutto-Fixkosten des Rechnungsmonats oder Teilmonatszeitraums.

Wenn die Rechnung eine oder mehrere solche Fixkostenpositionen direkt ausweist, werden diese zum `grundpreis_brutto_monat` aufsummiert.

Als **direkt ausgewiesen** gelten hier periodengebundene Brutto-Positionen ohne Verbrauchsbezug, z. B.:

- `Kosten Grundgebühr ... 15,66 EUR`
- gleichwertig bezeichnete Fixkosten-, Monatspreis- oder Grundpreispositionen

Nicht dazu gehoeren verbrauchsabhaengige Kostenpositionen oder reine Zahlungs-/SEPA-Informationen.

Da die Anwendung `grundpreis_eur_jahr` erwartet, muss dieser Brutto-Monatswert fuer das Zielfeld auf einen Jahreswert hochgerechnet werden, so dass der Monatsanteil im Rechenkern wieder genau den Rechnungswert ergibt:

`grundpreis_eur_jahr = grundpreis_brutto_monat * jahrtage / tage_im_tarif`

Beispiel Juni 2025 bei 30 Tagen:

`grundpreis_eur_jahr = grundpreis_brutto_juni * 365 / 30`

Nur so ergibt die bestehende Rechenlogik:

`grundpreis_eur_jahr * (30 / 365) = grundpreis_brutto_juni`

Beispiel fuer eine explizit ausgewiesene Teilmonats-Grundgebuehr:

- Rechnung weist aus: `Kosten Grundgebühr 2. März 2025 - 31. März 2025 ... 15,66 EUR` brutto
- dann gilt fuer diesen Tarifabschnitt: `grundpreis_brutto_monat = 15,66`
- und fuer das Zielfeld: `grundpreis_eur_jahr = 15,66 * 365 / 30`

### Stichprobe Tibber Juni 2025

Aus `Rechnung_1167054194.pdf` wurden u. a. erkannt:

- Rechnungsmonat: `2025-06-01` bis `2025-06-30`
- Zaehler: `1ISK0078261075`
- Verbrauch: `615,32 kWh`
- Rechnungsbetrag gesamt: `156,88 EUR`
- Verbrauchskosten brutto: `141,03 EUR`
- Fixkosten brutto: `15,85 EUR`

Fuer die Tarifbildung gilt dabei zusaetzlich:

- wenn die Rechnung einen durchschnittlichen Brutto-Arbeitspreis direkt nennt, hat diese Direktangabe Vorrang vor einer Rueckrechnung aus Summenwerten
- wenn die Rechnung die Brutto-Grundgebuehr direkt nennt, hat auch diese Direktangabe Vorrang vor einer indirekten Herleitung
- nur wenn diese Direktangaben fehlen, werden die Fallback-Formeln dieser Spec verwendet

Wenn eine Tibber-Rechnung weder einen eindeutig ausgewiesenen Brutto-Durchschnittspreis noch eine eindeutig ausweisbare Brutto-Grundgebuehr enthaelt, ist der Beleg review-pflichtig; eine automatische Tarifbildung darf dann nicht stillschweigend raten.

## Edgecases: Restbestand, Rest aus Vorjahr, Festmeter und Raummeter

### Fachlicher Grundsatz

Energietraeger wie Oel, Holz und Pellets werden zum Ende einer Abrechnungsperiode in der Regel nicht vollstaendig verbraucht.

Deshalb gilt fachlich:

- der zum Periodenende vorhandene Restbestand gehoert **wirtschaftlich nicht mehr** in die laufende Periode
- dieser Restbestand ist wertmaessig aus der laufenden Periode abzugrenzen
- derselbe Wert wird als **Rest aus Vorjahr** in die Folgeperiode uebernommen

Die Vorverarbeitung muss damit nicht nur die operative `input.json` fuer das Zieljahr erzeugen, sondern fachlich auch in der Lage sein, den Uebergang zum Folgejahr vorzubereiten.

### Kanonische Mengen- und Bewertungseinheiten

Fuer die Bestandsabgrenzung werden Mengen je Energietraeger auf eine kanonische Einheit normalisiert:

- Oel -> Liter (`l`)
- Pellets -> Kilogramm (`kg`)
- Holz -> Raummeter (`Rm`)

Besonderheit Holz:

- Holz wird auf Belegen haeufig in **Festmetern (`Fm`)** gekauft
- im Ablese- bzw. Restprotokoll wird Holz als **Raummeter (`Rm`)** ausgewiesen
- fuer diese Spec gilt normativ: `1 Fm = 1,5 Rm`

Vor jeder Bewertung muessen Belegmengen und Restmengen auf dieselbe kanonische Einheit umgerechnet werden.

### Bewertungslogik fuer Restbestand und Rest aus Vorjahr

Die Bewertung erfolgt je Energietraeger und je Berechnungseinheit.

Verfuegbarer Jahresbestand:

- `verfuegbare_menge = anfangsbestand_menge + einkaufsmengen_im_jahr`
- `verfuegbarer_wert = anfangsbestand_wert + einkaufswerte_im_jahr`

Normativer Einheitspreis fuer die Periodenabgrenzung:

- `durchschnittspreis = verfuegbarer_wert / verfuegbare_menge`

Restbestand zum Periodenende:

- `restwert_jahresende = restmenge_jahresende * durchschnittspreis`

Operativer Brennstoffkostenwert der laufenden Periode:

- `brennstoffkosten_laufendes_jahr = verfuegbarer_wert - restwert_jahresende`

Rest aus Vorjahr der Folgeperiode:

- `rest_aus_vorjahr_folgejahr = restwert_jahresende`

### Operative Abbildung im bestehenden JSON

Diese Spec unterscheidet zwischen:

1. **fachlicher Ledger-Sicht**
2. **operativer `input.json`-Sicht**

Fachlich kann die Jahresabgrenzung als negativer Abschluss im alten Jahr und positiver Anfangsbestand im Folgejahr verstanden werden.

Die operative Anwendung verarbeitet aktuell jedoch nur nicht-negative `kostenbelege[].betrag`. Deshalb gilt fuer die operative `input.json` verbindlich:

- der Restbestand zum Jahresende wird **nicht** als negativer `kostenbeleg` in die operative `input.json` des laufenden Jahres geschrieben
- stattdessen werden die Brennstoffkosten des laufenden Jahres bereits in der Vorverarbeitung auf den **netto verbrauchten** Wert reduziert
- fuer das Folgejahr wird ein positiver `kostenbeleg` `Rest aus Vorjahr` bzw. Anfangsbestand erzeugt

Damit bleibt die wirtschaftliche Logik erhalten, ohne das bestehende Validierungs- und Rechenkernmodell hinter der `input.json` zu veraendern.

### Beispiel

Zum Ende der Abrechnungsperiode 2024 am `31.12.2024` steht im Ablesungsprotokoll:

- BE1, Oel: `3500 l`
- BE2, Holz: `40 Rm`
- BE2, Pellets: `1500 kg`

Annahmen:

1. In 2024 wurden fuer BE1 `4000 l` Oel zu `0,50 EUR/l` gekauft -> `2000 EUR`
2. In 2024 wurden fuer BE2 `80 Fm` Holz zu `20 EUR/Fm` gekauft -> `1600 EUR`
3. In 2024 wurden fuer BE2 `2000 kg` Pellets zu `100 EUR/t` gekauft -> `200 EUR`

Holz-Umrechnung:

- `80 Fm = 120 Rm`
- Preis je `Rm` = `1600 / 120 = 13,33 EUR/Rm`

Bewertung Restbestand:

- Oel: `3500 l * 0,50 EUR/l = 1750 EUR`
- Holz: `40 Rm * 13,33 EUR/Rm ~= 533,33 EUR`
- Pellets: `1500 kg * 0,10 EUR/kg = 150 EUR`

Operative Wirkung:

- die operative `input_2024.json` enthaelt fuer Brennstoffkosten nur noch die **netto verbrauchten** Jahreskosten
- die operative `input_2025.json` enthaelt zusaetzlich positive Anfangsbestands-Belege fuer diese Restwerte

Beispielhafte Folgejahr-Belege:

```json
{
  "id": "kb-brennstoff-rest-vorjahr-be1-oel",
  "kostenart_id": "brennstoffkosten",
  "betrag": 1750.00,
  "datum": "2025-01-01",
  "beschreibung": "Rest aus Vorjahr Oel",
  "scope": { "berechnungseinheit": "be1" }
}
```

```json
{
  "id": "kb-brennstoff-rest-vorjahr-be2-holz",
  "kostenart_id": "brennstoffkosten",
  "betrag": 533.33,
  "datum": "2025-01-01",
  "beschreibung": "Rest aus Vorjahr Holz",
  "scope": { "berechnungseinheit": "be2" }
}
```

```json
{
  "id": "kb-brennstoff-rest-vorjahr-be2-pellets",
  "kostenart_id": "brennstoffkosten",
  "betrag": 150.00,
  "datum": "2025-01-01",
  "beschreibung": "Rest aus Vorjahr Pellets",
  "scope": { "berechnungseinheit": "be2" }
}
```

Die fachliche Abzugslogik im alten Jahr ist im Review-Output bzw. Import-Manifest zu dokumentieren, wird aber nicht als negativer operativer `kostenbeleg` persistiert.

### Fail-fast fuer Bestandsabgrenzung

Die Vorverarbeitung muss abbrechen, wenn:

- fuer einen Energietraeger Restmengen vorliegen, aber keine belastbare Einkaufs- oder Anfangsbestandsbasis vorhanden ist
- fuer einen Energietraeger `anfangsbestand = 0`, `zugaenge = 0` und zugleich ein positiver Restbestand ausgewiesen wird; dies ist ein Datenwiderspruch
- die Restmenge groesser ist als die verfuegbare Gesamtmenge des Jahres
- Holzmengen nicht eindeutig zwischen `Fm` und `Rm` umgerechnet werden koennen
- fuer denselben Energietraeger und dieselbe BE die Bewertungsbasis widerspruechlich ist

### Jahresuebergangs-Artefakte ausserhalb des operativen JSON

Fuer die Vorverarbeitung werden zusaetzlich zum Import-Manifest zwei eigenstaendige Artefaktklassen normiert:

1. `restbasis.<jahr>.json`
2. `carryover-output.json`

Beide sind **Vorverarbeitungsartefakte** und **kein** Teil des operativen Anwendungsschemas hinter `input.json`.

#### `restbasis.<jahr>.json`

Dieses Artefakt beschreibt die zum Jahresende physisch und bewertungsseitig bekannte Restbasis, wenn noch kein bestaetigtes `carryover-output.json` aus dem Vorjahr vorliegt.

Mindeststruktur:

- `source_year`
- `entries[]`

Je `entries[]`-Position mindestens:

- `energietraeger`
- `be_id`
- `restmenge`
- `restmenge_einheit`
- `bewertungsbasis`

`bewertungsbasis` muss die Bewertung fachlich belastbar machen, also insbesondere die fuer die Durchschnittspreislogik noetigen Angaben zu Anfangsbestand und/oder Zugaengen enthalten.

Ohne belastbare `bewertungsbasis` darf kein Carryover fuer das Folgejahr erzeugt werden.

#### `carryover-output.json`

Dieses Artefakt ist das **Standard-Ausgabeformat** fuer Jahresuebergaenge und wird sowohl fuer:

- Vorjahr -> Zieljahr (`Rest aus Vorjahr`)
- Zieljahr -> Folgejahr

verwendet.

Mindeststruktur:

- `source_year`
- `target_year`
- `generated_at`
- `entries[]`

Je `entries[]`-Position mindestens:

- `energietraeger`
- `be_id`
- `restmenge`
- `restmenge_einheit`
- `restwert_eur`
- `bewertungsbasis`
- `opening_kostenbeleg`

`opening_kostenbeleg` ist dabei **kein neues fachliches Schema**, sondern ein Vorverarbeitungsobjekt mit derselben Struktur, die spaeter operativ als `KostenbelegDto` in `kostenbelege[]` der Ziel-`input.json` geschrieben wird:

- `id`
- `kostenart_id = "brennstoffkosten"`
- `betrag`
- `datum`
- `beschreibung`
- `scope`

Nur `opening_kostenbeleg` wird bei der Uebernahme in die operative `input.generated.json` bzw. `input.json` in `kostenbelege[]` geschrieben. Die restlichen Felder des `carryover-output.json` bleiben Vorverarbeitungs- und Nachweis-Metadaten.

Damit ist normativ festgelegt:

- `carryover-output.json` ist **separat** vom operativen App-Schema
- die operative Anwendung sieht weiterhin nur regulaere `kostenbelege[]`
- `Rest aus Vorjahr` wird operativ als positiver normaler Brennstoff-`kostenbeleg` der Zielperiode modelliert

#### Scaffold-Statusdatei

Fuer den operatorischen Freigabestatus eines vorbereiteten Zieljahres-Scaffolds wird zusaetzlich eine separate Datei `scaffold.state.json` empfohlen und normiert.

Auch diese Datei ist **kein** Teil des operativen Runtime-Schemas.

Mindestfelder:

- `generated_from_year`
- `zaehler_review_completed`
- `mietparteien_review_completed`
- `opening_carryover_attached`

Die fachlichen Scaffold-Daten selbst bleiben in `scaffold.json`; Freigabe- und Workflow-Status gehoeren ausschliesslich in `scaffold.state.json`, damit spaeter nichts aus dem operativen JSON herausgestrippt werden muss.

## Import-Manifest ausserhalb des operativen JSON

Da das operative Anwendungsmodell keine OCR-/Review-Felder kennt, wird ein separates Import-Manifest empfohlen. Es ist **kein** Teil der Laufzeitanwendung, aber Teil der Vorverarbeitung.

Mindestens je Quellartefakt bzw. je erzeugtem operativen Datensatz:

- `source_path`
- `source_pages`
- `document_type`
- `extraction_method` (`native_text`, `ocr_vision`, ...)
- `confidence`
- `raw_identifiers`
- `canonical_identifiers`
- `scope_inference`
- `auto_corrections`
- `review_required`
- `review_reason`
- `output_entity_type`
- `output_entity_id`

Fuer Belege ohne automatische `kostenart_id`-Zuordnung muss das Manifest bzw. ein daraus erzeugter Review-Output gezielt auswertbar machen, welche Belege oder Belegsegmente manuell in der `input.json` nachzupflegen sind.

### Review-Output fuer manuelle Belegzuordnung

Fuer nicht eindeutig zuordenbare Belege ist aus dem Import-Manifest ein gezielter Review-Output abzuleiten.

Dieser Review-Output muss pro offenem Beleg oder Belegsegment mindestens enthalten:

- `source_path`
- `source_pages`
- `document_type`
- `review_reason`
- `beschreibung` bzw. extrahierte Kurzbeschreibung
- optional `proposed_kostenart_id`
- optional `proposed_scope`

Workflow:

1. Vorverarbeitung extrahiert und segmentiert die Quellen.
2. Nicht eindeutig zuordenbare Belege werden im Manifest mit `review_required = true` und `review_reason` markiert.
3. Aus diesen Manifest-Eintraegen wird ein Review-Output gefiltert erzeugt.
4. Die offene `kostenart_id`- bzw. `scope`-Zuordnung wird anschliessend manuell auf Belegebene in der `input.json` nachgepflegt.
5. Solange solche offenen Review-Faelle bestehen, gilt die `input.json` nicht als final vervollstaendigt und darf nicht als operative Eingabe an den Rechenkern uebergeben werden.

Der Review-Output ist damit kein zusaetzliches operatives Eingabeformat der Anwendung, sondern eine gezielte Arbeitsliste fuer die manuelle Vervollstaendigung der `input.json`.

## Operative Mapping-Regeln in das bestehende JSON

### `zaehler[]`

- alle 2025 real existierenden Zaehler und ista-Geraete werden explizit angelegt
- `zaehlernummer` enthaelt den **kanonischen** korrigierten Wert
- mehrere HKV/Wasserzaehler in derselben NE sind zulaessig

### `ablesungen[]`

- Periodenquellen -> `ista_*` mit `periode` + `messwert_alt` + `messwert_neu`
- echte manuelle oder sonstige nicht-periodische Stichtagsquellen -> `quelle = "manuell"` mit `stichtag` + `messwert`
- ista-Monatswerte und vergleichbare ista-Dokumente werden vor der operativen Ablage auf **eine kanonische Periodenablesung** je relevantem Zeitraum verdichtet
- `ne_id` wird gesetzt, wenn der Zaehler einer NE zugeordnet ist
- objektweite bzw. BE-weite Zaehler kommen ohne `ne_id` aus

### `kostenbelege[]`

- jeder logisch getrennte Rechnungsvorgang wird ein eigener Eintrag
- `beschreibung` soll den Lieferanten/Belegtyp knapp enthalten
- `scope` wird nur gesetzt, wenn der Beleg nicht liegenschaftsweit gilt

### `stromtarife[]`

- ein Eintrag je Tibber-Monat und `be_id`
- keine zusaetzlichen Strom-`kostenbelege[]` im Tarifmodus

## Fail-fast- und Review-Regeln

### Fail-fast

Die Vorverarbeitung muss abbrechen bei:

- fehlendem 2025er Zaehlerregister
- Zaehlernummern, fuer die nach Normalisierung **kein plausibler Kandidat** im Zaehlerregister verbleibt
- negativem oder unplausiblem Verbrauch nach Normalisierung
- Tibber-Rechnung ohne ableitbaren Verbrauch oder ohne ableitbaren Monatszeitraum
- Bundle-PDF, dessen Seiten sich nicht in operative Einzelbelege zerlegen lassen
- unplausibler Brennstoff-Bestandsabgrenzung (z. B. Restbestand > verfuegbarer Bestand oder fehlende Bewertungsbasis)

### Review-pflichtig, aber nicht zwingend Abbruch

- OCR unsicher, aber fachlich trotzdem eindeutig
- genau ein plausibler Zaehlerkandidat vorhanden, die OCR-Extraktion selbst ist jedoch fragmentarisch oder schwach
- Scope nur ueber Dateiname, nicht ueber Dokumenttext erkennbar
- Belegwerte mit einzelnen unsicheren OCR-Zeichen, aber plausibler Gesamtsumme

## Akzeptanzkriterien

Die Spec gilt als fachlich ausreichend, wenn eine Umsetzung folgende Ergebnisse liefern kann:

1. Die 2025er PDFs lassen sich in operative Datensaetze fuer `kostenbelege[]`, `zaehler[]`, `ablesungen[]` und `stromtarife[]` ueberfuehren, ohne das Anwendungsmodell zu aendern.
2. `Monatswerte`-, `Ableseprotokoll`- und direkte Rechnungsquellen koennen unterschieden und dem richtigen Ablese-Modell zugeordnet werden.
3. OCR-Fehler in Zaehlernummern werden nur bei eindeutigem Match automatisch korrigiert; sonst wird Review erzwungen.
4. Die Stichprobe `Monatswerte ... NE0001` kann mindestens die erkannten HKV-Geraete `120298189`, `120298011`, `120298110`, `120298127` als separate Zaehler bzw. Messwertquellen abbilden.
5. Die Stichprobe `Ablesungen24_25.pdf` kann mindestens OCR-Varianten wie `2108757522` -> `210875752` und `2008222190` -> `200822219` gegen ein 2025er Zaehlerregister validieren.
6. Die Stichprobe `Rechnung_1167054194.pdf` erzeugt genau einen Monats-Tarif fuer Juni 2025 mit abgeleitetem `arbeitspreis_ct_kwh` und `grundpreis_eur_jahr`.
7. Belege ohne automatische Kostenart-Zuordnung werden in einem Review-Output bzw. Import-Manifest eindeutig ausgewiesen, sodass die Zuordnung manuell in der `input.json` nachgepflegt werden kann.
8. Gebuendelte Beleg-PDFs koennen in logische Einzelbelege aufgeteilt werden, ohne dass deren Seitenherkunft verloren geht.
9. Restbestaende fuer Oel, Holz und Pellets werden zum Jahresende wertmaessig abgegrenzt; die laufende Periode enthaelt nur netto verbrauchte Brennstoffkosten und das Folgejahr positive Anfangsbestands-Belege `Rest aus Vorjahr`.
10. Holzeinkaeufe in `Fm` und Restmengen in `Rm` werden ueber `1 Fm = 1,5 Rm` konsistent normalisiert und bewertet.
11. Die operative JSON-Struktur bleibt kompatibel zur bestehenden Anwendung und zur Hauptspec vom `2026-03-24`.

## Abgrenzung zur Hauptspec

Diese Spec ersetzt die Hauptspec nicht.

Bei Konflikten gilt:

- **Hauptspec gewinnt** fuer JSON-Zielstruktur, Domänenmodell, Kostenlogik und Output
- **diese Spec gewinnt** fuer Quellanalyse, OCR, Scope-Inferenz und Vorverarbeitungsregeln der 2025er Rohdokumente

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-03-28 | 0 | Claude | Fachliche Import-Spec fuer Belege und Messwerte 2025 erstellt |
| 2026-04-09 | 1 | Codex | Statushinweis ergaenzt: Zielbild bleibt gueltig, operative 2025-Ausfuehrung jedoch in der Spec vom 2026-04-09 verankert |
