## Why

Daniel hat Release-Ticket 02 am 13.09.2026 ausdrücklich akzeptiert und Abschluss, Commit und Push beauftragt. Ein qualifizierter Release-Kandidat muss lokal nachweisbar aktiv werden und bei Fehlern den bisherigen funktionsfähigen Stand erhalten.

## What Changes

- Ausschließlich unveränderte, vollständig qualifizierte Kandidaten werden als getrennte Runtime atomar ausgewählt.
- Tatsächliche Identität, erhaltene gespeicherte Erkenntnisse und weiterverwendbarer Zustand werden durch öffentliche Wiki-Aufrufe geprüft.
- Prozesssperre, No-op, Rückfall und Abbruchwiederherstellung verhindern überlappende Änderungen und melden den aktiven Stand eindeutig.

Dieser Change schließt ausschließlich den akzeptierten Aktivierungsanteil aus `operate-contextual-llm-wiki` ab. Automatische Release-Erkennung (Ticket 03) und offene Wissenspflege verbleiben dort.

## Capabilities

### Modified Capabilities

- `contextual-wiki-operations`: transaktionale lokale Aktivierung qualifizierter Releases.

## Impact

Stabiler Wiki-Einstieg, Aktivierungssteuerung, gemeinsame Runtime-Inhaltsbindung, öffentlicher Funktionsnachweis und Verhaltenstests. Aktiviert ist der Feature-Worktree; produktiver Einstieg, Wissensdaten und Scheduler bleiben unverändert. [Abnahme](../../../../contextual-llm-wiki/evidence/release-activation-02.md).
