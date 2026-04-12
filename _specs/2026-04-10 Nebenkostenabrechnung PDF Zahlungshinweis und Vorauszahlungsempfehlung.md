# Iteration 0

Der PDF-Ausgabe der Nebenkostenabrechnung soll ein klarer Zahlungshinweis fuer Nachzahlungen hinzugefuegt werden.

Zusaetzlich soll aus Nachzahlung oder Guthaben eine Empfehlung fuer die kuenftige monatliche Vorauszahlung abgeleitet werden:

- Saldo durch `12` teilen
- auf die naechste `5 EUR`-Stufe auf- oder abrunden
- bei jedem von `0 EUR` abweichenden Saldo eine Aenderung der Vorauszahlung ableiten

Beispiele:

- Nachzahlung `1200 EUR` -> `1200 / 12 = 100` -> neue Vorauszahlung `X + 100 EUR`
- Nachzahlung `1458.20 EUR` -> `1458.20 / 12 = 121.52` -> neue Vorauszahlung `X + 120 EUR`

Der Zahlungshinweis soll auf das Konto `DE95 5305 1396 0000 6256 74` verweisen und eine Frist von `14 Tagen` nennen.

## Status

Accepted and closed on 2026-04-11.

- Verification replay VC1-VC7: gruen am 2026-04-11
- OpenSpec archived as `2026-04-11-2026-04-10-pdf-vorauszahlungsempfehlung`
- Kanonischer PDF-Output ersetzt durch `data/2025/output/final-pdf-2025-canonical-2026-04-11_0756`

## Zweck

Diese Spec definiert einen bounded Change fuer die Ausgabeartefakte der Nebenkostenabrechnung:

1. einen expliziten Zahlungshinweis fuer Nachzahlungen in der HTML-/PDF-Ausgabe
2. eine testbare, deterministische Empfehlung fuer die neue monatliche Vorauszahlung auf Basis des Abrechnungssaldos

Ziel ist eine fachlich klare Kommunikation an die Mietpartei und eine reproduzierbare Ableitung der neuen Vorauszahlung, ohne dass diese nur informell ausserhalb der Abrechnung berechnet werden muss.

## Bezug

Massgebliche Referenzen:

- Hauptspec: `2026-03-24 Nebenkostenabrechnung Applikation.md`
- 2025 Parent-Spec: `Completed/2026-04-09 Nebenkostenabrechnung 2025 Realdaten und Abrechnungspfad.md`
- Repository: `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung`
- Pattern: `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/docs/input-json-pattern.md`
- Checkliste: `/Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung/docs/input-json-checklist.md`

## Scope

In Scope:

- Statement-/Rendering-Ausgabe fuer `einzelabrechnung.json`, HTML und PDF
- Zahlungshinweis bei Nachzahlung
- strukturierte Vorauszahlungsempfehlung je Mietpartei
- Platzierung der neuen Inhalte direkt unter dem Block `Begriffe kurz erklaert`
- deterministische Rundungsregel auf `5 EUR`
- Verifikation ueber JSON, HTML/PDF-Lauf und Regression

Out of Scope:

- Aenderung der `input.json`
- automatische Fortschreibung von Vorauszahlungen in Stammdaten
- Mahnwesen oder Zahlungseingangsverfolgung
- SEPA-/QR-Code-Generierung
- juristische Sondertexte ausserhalb des hier definierten Zahlungshinweises

## Decision Freeze Pack

### Zielbild und Scope in 1-2 Saetzen

Die Einzelabrechnung ergaenzt fuer Nachzahlungen einen klaren Zahlungshinweis mit Frist und IBAN und liefert zusaetzlich fuer jede Mietpartei eine strukturierte Empfehlung fuer die kuenftige monatliche Vorauszahlung. Die Empfehlung basiert ausschliesslich auf dem finalen Jahressaldo und der hier definierten Rundungslogik.

### Referenz-Baseline

Falls der Change zunaechst fuer 2025 umgesetzt wird, ist die kanonische Baseline:

- `data/2025/input.json`
- letzter kanonischer PDF-Lauf des Zieljahrs

### Layout-Freeze

Die neuen Inhalte werden im HTML-/PDF-Layout direkt unter dem Block

- `Begriffe kurz erklaert`

platziert.

Normative Folge:

- der freie Bereich unter dieser Box wird bewusst fuer Zahlungshinweis und Vorauszahlungsempfehlung genutzt
- die Inhalte erscheinen vor dem Abschnitt `1. Verbrauchs- und Ablesewerte`
- die Platzierung ist Teil der Akzeptanz und der Verifikation

### Go/No-Go

Go:

- strukturierte Empfehlung ist in `einzelabrechnung.json` vorhanden
- HTML/PDF zeigen den passenden Hinweistext
- Rundungsregel ist testseitig fuer Nachzahlung, Guthaben und den exakten Nullsaldo-Fall abgesichert

No-Go:

- Empfehlung existiert nur als Freitext ohne strukturierte Datenbasis
- Zahlungshinweis erscheint falsch auch bei Guthaben
- Rundungsregel ist nicht deterministisch oder nicht testbar

## Fachliche Regeln

### 1. Zahlungshinweis fuer Nachzahlungen

Wenn der Saldo einer Mietpartei positiv ist, also eine Nachzahlung besteht, muss die HTML-/PDF-Ausgabe einen zusaetzlichen Hinweis enthalten:

> Bitte begleichen Sie die Nachzahlung innerhalb von 14 Tagen auf das Konto DE95 5305 1396 0000 6256 74.

Normative Regeln:

- der Hinweis erscheint nur bei Nachzahlung
- bei Guthaben erscheint dieser Hinweis nicht
- der Hinweis muss in HTML und PDF sichtbar sein
- der Hinweis soll aus strukturierten Statement-Daten ableitbar sein und nicht nur als harter Template-String ohne Modellbezug entstehen

### 2. Empfehlung fuer die kuenftige Vorauszahlung

Fuer jede Mietpartei wird eine Empfehlung fuer die kuenftige monatliche Vorauszahlung berechnet.

#### 2.1 Basiswert

Als aktuelle monatliche Vorauszahlung `X` gilt:

- der chronologisch zuletzt gueltige monatliche Vorauszahlungsbetrag der Mietpartei im Abrechnungsjahr

Deterministische Regel:

- verwende das Vorauszahlungssegment mit dem spaetesten `periode_bis`
- bei Gleichstand verwende das Segment mit dem spaetesten `periode_von`
- wenn keine Vorauszahlung vorhanden ist, gilt `X = 0 EUR`

Beispiele:

- `350 EUR/Monat` bei `vz-ne1-hainz`
- `230 EUR/Monat` bei `vz-ne2`
- `0 EUR/Monat`, wenn bewusst keine Vorauszahlung geleistet wird

#### 2.2 Rohdelta

Es wird der absolute Saldo durch `12` geteilt:

- `rohdelta = abs(saldo) / 12`

#### 2.3 Kein Schwellwert

Es gibt keinen Mindestschwellwert fuer die Anpassung.

Normative Folge:

- jeder von `0 EUR` abweichende Saldo fuehrt zu einer Aenderung der monatlichen Vorauszahlung
- nur bei exakt `saldo = 0 EUR` bleibt die empfohlene monatliche Vorauszahlung unveraendert
- der Status der Empfehlung ist nur im exakten Nullsaldo-Fall `unchanged`

#### 2.4 Rundung

Wenn `saldo != 0 EUR`, wird `rohdelta` auf die naechste `5 EUR`-Stufe gerundet.

Normative Rundungsregel:

- kaufmaennische Rundung auf das naechste Vielfache von `5 EUR`
- Zwischenwerte unter `2.50 EUR` Abstand werden abgerundet
- Zwischenwerte ab `2.50 EUR` Abstand werden aufgerundet

Beispiele:

- `100.00 -> 100`
- `121.52 -> 120`
- `122.50 -> 125`
- `63.99 -> 65`

#### 2.5 Richtung der Anpassung

- bei Nachzahlung wird die monatliche Vorauszahlung um den gerundeten Betrag erhoeht
- bei Guthaben wird die monatliche Vorauszahlung um den gerundeten Betrag reduziert

Formeln:

- Nachzahlung: `empfohlen = X + rundungsdelta`
- Guthaben: `empfohlen = X - rundungsdelta`

#### 2.6 Untergrenze

Die empfohlene monatliche Vorauszahlung darf nicht negativ werden.

Normative Regel:

- wenn `X - rundungsdelta < 0`, wird die empfohlene monatliche Vorauszahlung auf `0 EUR` gesetzt

### 3. Strukturierte Statement-Daten

Die Empfehlung darf nicht nur implizit aus Freitext entstehen.

In `einzelabrechnung.json` muss eine eigene strukturierte Sektion vorhanden sein, z. B.:

- `vorauszahlungsempfehlung`

Die Sektion muss mindestens folgende Informationen enthalten:

- `aktuell_monatlich_eur`
- `saldo_eur`
- `rohdelta_monatlich_eur`
- `rundungsdelta_monatlich_eur`
- `status` mit einem der Werte:
  - `increase`
  - `decrease`
  - `unchanged`
- `empfohlen_monatlich_eur`
- `begruendung`
- `zahlungshinweis_erforderlich`
- `anzeigetitel`

Optional zusaetzlich:
- keine

### 4. Sichtbare Ausgabe in HTML/PDF

Die HTML-/PDF-Ausgabe muss die strukturierte Empfehlung in lesbarer Form ausgeben.

Normatives Zielbild:

- die Ausgabe steht direkt unter `Begriffe kurz erklaert`
- die Ausgabe erscheint vor den Tabellenabschnitten zu Verbrauch und Kosten
- die neue sichtbare Sektion traegt den stabilen Titel `Empfehlung zur kuenftigen Vorauszahlung`
- bei Nachzahlung:
  - Zahlungshinweis mit `14 Tagen` und IBAN
  - Hinweis auf empfohlene neue monatliche Vorauszahlung
- bei Guthaben:
  - kein Zahlungshinweis
  - Hinweis auf reduzierte oder unveraenderte Vorauszahlung
- bei `unchanged`:
  - expliziter Hinweis, dass die monatliche Vorauszahlung bei exakt `saldo = 0 EUR` unveraendert bleiben kann

## Beispiele

### Beispiel A - Nachzahlung mit klarer Erhoehung

- aktuelle Vorauszahlung `X = 350 EUR`
- Saldo `+1200 EUR`
- `rohdelta = 100 EUR`
- `rundungsdelta = 100 EUR`
- Empfehlung `450 EUR/Monat`
- Zahlungshinweis erscheint

### Beispiel B - Nachzahlung mit Rundung auf 5 EUR

- aktuelle Vorauszahlung `X = 350 EUR`
- Saldo `+1458.20 EUR`
- `rohdelta = 121.52 EUR`
- `rundungsdelta = 120 EUR`
- Empfehlung `470 EUR/Monat`
- Zahlungshinweis erscheint

### Beispiel C - Guthaben mit Reduktion

- aktuelle Vorauszahlung `X = 350 EUR`
- Saldo `-735.87 EUR`
- `rohdelta = 61.3225 EUR`
- `rundungsdelta = 60 EUR`
- Empfehlung `290 EUR/Monat`
- Zahlungshinweis erscheint nicht

### Beispiel D - Kleines Delta wird trotzdem angepasst

- aktuelle Vorauszahlung `X = 230 EUR`
- Saldo `+540 EUR`
- `rohdelta = 45 EUR`
- `rundungsdelta = 45 EUR`
- Empfehlung `275 EUR/Monat`
- Status `increase`

### Beispiel E - Exakter Nullsaldo

- aktuelle Vorauszahlung `X = 230 EUR`
- Saldo `0 EUR`
- `rohdelta = 0 EUR`
- `rundungsdelta = 0 EUR`
- Empfehlung `230 EUR/Monat`
- Status `unchanged`

## Akzeptanzkriterien

1. Bei Nachzahlung enthaelt die HTML-/PDF-Ausgabe den Hinweis:
   - `Bitte begleichen Sie die Nachzahlung innerhalb von 14 Tagen auf das Konto DE95 5305 1396 0000 6256 74.`
2. Bei Guthaben enthaelt die HTML-/PDF-Ausgabe diesen Zahlungshinweis nicht.
3. `einzelabrechnung.json` enthaelt eine strukturierte Vorauszahlungsempfehlung je Mietpartei.
4. Die Rundungsregel auf `5 EUR` ist fuer Nachzahlung und Guthaben deterministisch umgesetzt.
5. Jeder von `0 EUR` abweichende Saldo fuehrt zu einer Anpassung der Vorauszahlung; nur exakter Nullsaldo bleibt unveraendert.
6. Die empfohlene monatliche Vorauszahlung wird nie negativ.
7. HTML und PDF verwenden dieselbe strukturierte Datenbasis wie `einzelabrechnung.json`.
8. Die neuen Inhalte stehen sichtbar direkt unter dem Block `Begriffe kurz erklaert`.
9. Der Fall `X = 0 EUR` ist fachlich korrekt verarbeitet und testseitig belegt.
10. `zahlungshinweis_erforderlich` ist in der strukturierten Empfehlung vorhanden und steuert die sichtbare Ausgabe.

## Test Cases

### TC1 - Unit-Test Rundungslogik

Ziel:

- die `5 EUR`-Rundung ohne Mindestschwelle ist isoliert testbar

Sollfaelle mindestens:

- `+1200.00 EUR` bei `X=350` -> `450`
- `+1458.20 EUR` bei `X=350` -> `470`
- `-735.87 EUR` bei `X=350` -> `290`
- `+540.00 EUR` bei `X=230` -> `275`
- `0.00 EUR` bei `X=230` -> `230`
- `+6624.97 EUR` bei `X=0` -> `550`
- starkes Guthaben mit Untergrenze -> nicht negativ

### TC2 - Statement-JSON enthaelt strukturierte Empfehlung

Ziel:

- `einzelabrechnung.json` enthaelt `vorauszahlungsempfehlung`
- alle Pflichtfelder sind vorhanden
- Werte stimmen fuer mindestens eine Nachzahlung und ein Guthaben

### TC3 - Zahlungshinweis nur bei Nachzahlung

Ziel:

- HTML- und PDF-Ausgabe fuer Nachzahlung enthaelt den Hinweistext
- HTML- und PDF-Ausgabe fuer Guthaben enthaelt ihn nicht

### TC4 - Platzierung direkt unter `Begriffe kurz erklaert`

Ziel:

- HTML zeigt die Sektion `Empfehlung zur kuenftigen Vorauszahlung` direkt unter dem Block `Begriffe kurz erklaert`
- die neuen Inhalte erscheinen vor dem Abschnitt `1. Verbrauchs- und Ablesewerte`

### TC5 - End-to-End auf realem Jahresinput

Ziel:

- der CLI-Lauf auf `data/2025/input.json` erzeugt JSON/HTML/PDF mit den neuen Inhalten

### TC6 - Realfall `X = 0 EUR`

Ziel:

- mindestens ein Realfall ohne Vorauszahlungen erzeugt eine strukturierte Empfehlung
- die Empfehlung ist sichtbar in JSON und HTML/PDF

### TC7 - Regression

Ziel:

- `dotnet test Nebenkosten.sln` bleibt gruen

## Verification Commands

### VC1 - Unit-/Regressionstests

```bash
dotnet test Nebenkosten.sln
```

### VC2 - Finaler CLI-/PDF-Lauf auf realem 2025er Input

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
dotnet run --project src/Nebenkosten.Cli -- \
  --input-json data/2025/input.json \
  --output-dir data/2025/output/final-pdf-vorauszahlungsempfehlung
```

### VC3 - Strukturpruefung in `einzelabrechnung.json`

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
python3 - <<'PY'
import json
from pathlib import Path
base = Path("data/2025/output")
candidates = sorted(base.glob("final-pdf-vorauszahlungsempfehlung-*/mp-ne1-hainz/einzelabrechnung.json"))
assert candidates, "no output found"
path = candidates[-1]
data = json.loads(path.read_text())
print(path)
print(sorted(data["vorauszahlungsempfehlung"].keys()))
assert "zahlungshinweis_erforderlich" in data["vorauszahlungsempfehlung"]
assert "anzeigetitel" in data["vorauszahlungsempfehlung"]
PY
```

### VC4 - HTML-Platzierung und Hinweistext pruefen

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
python3 - <<'PY'
from pathlib import Path
base = Path("data/2025/output")
nachzahlung = sorted(base.glob("final-pdf-vorauszahlungsempfehlung-*/mp-ne2/einzelabrechnung.html"))
guthaben = sorted(base.glob("final-pdf-vorauszahlungsempfehlung-*/mp-ne1-hainz/einzelabrechnung.html"))
assert nachzahlung and guthaben, "html outputs missing"
html_n = nachzahlung[-1].read_text()
html_g = guthaben[-1].read_text()
needle = "Bitte begleichen Sie die Nachzahlung innerhalb von 14 Tagen auf das Konto DE95 5305 1396 0000 6256 74."
assert needle in html_n
assert needle not in html_g
anchor = "Begriffe kurz erklaert"
title = "Empfehlung zur kuenftigen Vorauszahlung"
section = "1. Verbrauchs- und Ablesewerte"
assert title in html_n
assert html_n.index(anchor) < html_n.index(title) < html_n.index(section)
PY
```

### VC5 - Realfall `X = 0 EUR` pruefen

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
python3 - <<'PY'
import json
from pathlib import Path
base = Path("data/2025/output")
candidates = sorted(base.glob("final-pdf-vorauszahlungsempfehlung-*/mp-ne5/einzelabrechnung.json"))
assert candidates, "no output found"
data = json.loads(candidates[-1].read_text())
empf = data["vorauszahlungsempfehlung"]
print(empf)
assert empf["aktuell_monatlich_eur"] == 0
assert empf["status"] == "increase"
assert empf["empfohlen_monatlich_eur"] == 550
PY
```

### VC6 - PDF-Hinweistext pruefen

```bash
cd /Users/dh/Documents/DanielsVault/private/Vermietung/nebenkosten-abrechnung
python3 - <<'PY'
import subprocess
from pathlib import Path
base = Path("data/2025/output")
pdf_n = sorted(base.glob("final-pdf-vorauszahlungsempfehlung-*/mp-ne2/einzelabrechnung.pdf"))
pdf_g = sorted(base.glob("final-pdf-vorauszahlungsempfehlung-*/mp-ne1-hainz/einzelabrechnung.pdf"))
assert pdf_n and pdf_g, "pdf outputs missing"
txt_n = subprocess.check_output(["pdftotext", str(pdf_n[-1]), "-"]).decode("utf-8", errors="ignore")
txt_g = subprocess.check_output(["pdftotext", str(pdf_g[-1]), "-"]).decode("utf-8", errors="ignore")
needle = "Bitte begleichen Sie die Nachzahlung innerhalb von 14 Tagen auf das Konto DE95 5305 1396 0000 6256 74."
assert needle in txt_n
assert needle not in txt_g
assert "Empfehlung zur kuenftigen Vorauszahlung" in txt_n
PY
```

### VC7 - Regression

```bash
dotnet test Nebenkosten.sln
```

## Risiken und Guardrails

- Die Empfehlung darf nicht als rechtsverbindliche Vertragsaenderung formuliert werden, sondern als klare Empfehlung fuer die kuenftige monatliche Vorauszahlung.
- Die Zahlungsaufforderung darf nur fuer Nachzahlungen erscheinen.
- Die strukturierte Empfehlungslogik muss aus dem Statement-Modell kommen; reine Template-Magie ohne testbare Datenbasis ist nicht zulaessig.
- Falls ein Jahr keine Vorauszahlungen fuer eine Mietpartei enthaelt, muss `X = 0` sauber verarbeitet werden.

## Reader-Test-Fragen

1. Ist klar, dass der Zahlungshinweis nur fuer Nachzahlungen gilt?
2. Ist klar, wie `X` als aktuelle monatliche Vorauszahlung bestimmt wird?
3. Ist klar, dass es keine `60 EUR`-Schwelle mehr gibt und nur exakter Nullsaldo unveraendert bleibt?
4. Ist klar, wie Guthaben die Vorauszahlung reduzieren?
5. Ist klar, dass die Empfehlung strukturiert testbar sein muss und nicht nur als Freitext erscheint?

## Ready-Status

Bewertung gegen `doc-workflow.md`:

- DoR: erfuellt
- plan-ready: ja
- implementation-ready: ja
- closeout-ready: abgeschlossen

## History

| Date | Iteration | Author | Delta |
|------|-----------|--------|-------|
| 2026-04-10 | 0 | User | Zahlungshinweis fuer Nachzahlungen und Regel zur Anpassung der monatlichen Vorauszahlung angefordert |
| 2026-04-10 | 1 | Codex | Bounded Output-Spec mit strukturierter Vorauszahlungsempfehlung, Rundungsregel, Akzeptanzkriterien, Test Cases und Verification Commands erstellt |
| 2026-04-10 | 2 | Codex | 60-EUR-Schwelle entfernt; Anpassung jetzt fuer jeden von 0 abweichenden Saldo, Nullsaldo bleibt unveraendert |
| 2026-04-11 | 3 | Codex | Verification replay gruen, OpenSpec archiviert, kanonischer 2025er PDF-Output auf verifizierten Stand gehoben |

Session: Codex desktop thread, konkrete Session-ID in dieser Laufumgebung nicht exponiert.
