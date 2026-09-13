## Why

Die bisherige allgemeine/private Quellenpartition verhinderte gewünschte repoübergreifende Erkenntnisse. Daniel hat das gemeinsame Quellenmodell in ADR 0010 bestätigt und die Umsetzung von Ticket 01 am 13.09.2026 ausdrücklich akzeptiert.

## What Changes

- Alle acht ausgewählten Repo-Identitäten einschließlich persönlicher Fachquellen bilden eine gemeinsame Wissensschicht.
- Fachliche Relevanz bestimmt die Query-Evidenz; explizite Repo-/Quellenbegrenzungen werden einschließlich transitiver Abhängigkeiten vor Provideraufrufen geprüft.
- Die gemeinsame QMD-Collection bleibt regulär sichtbar; Originalstände, No-op und Quellenabhängigkeiten bleiben überprüft.

Dieser Change ist der abgeschlossene Ticket-01-Anteil aus `operate-contextual-llm-wiki`. Bestandsmigration, Teilfehlerfortsetzung, Live-Aktivierung und Vollimport verbleiben dort in Tickets 02–04.

## Capabilities

### Modified Capabilities

- `contextual-llm-wiki`: gemeinsamer Quellenbestand, belegte Synthese, transitive Aufgabenbegrenzung und QMD-Routing ohne Privatpartition.

## Impact

CLI und Verhaltenstests unter `contextual-llm-wiki`, gemeinsame Inventur, Retrieval-Dokumentation und kanonische Wiki-Spec. Keine Änderung des Live-Jobs oder bestehender Bestände. [Abnahme](../../../../contextual-llm-wiki/evidence/shared-wiki-01.md).
