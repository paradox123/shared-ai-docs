## Why

Die gemeinsame Wiki-Pflege brach bisher beim ersten Fehler ab. Daniel hat Ticket 03 am 13.09.2026 ausdrücklich akzeptiert und den Abschluss samt Commit und Push beauftragt.

## What Changes

- Begrenzte Fehler sperren betroffene Quellen-/Seitenzweige einschließlich transitiver Konzepte und gespeicherter Antworten, während nachweislich unabhängige Ergebnisse weiter gepflegt werden.
- Strukturierte Teilfehlerberichte und lokale Rohartefakte bewahren abgeschlossene, unveränderte, fehlgeschlagene und offene Arbeit; unvollständige Verträge erlauben keine Folgepflege.
- Sichere QMD-Pflege bleibt möglich, ohne den Gesamtfehler zu verdecken. Reparatur arbeitet offene Quellen nach und erhält gültige unabhängige Inhalte; die nächste Wiederholung ist No-op.

Dieser Change schließt ausschließlich den akzeptierten Ticket-03-Anteil aus `operate-contextual-llm-wiki` ab. Bestandsmigration, Live-Aktivierung und Vollimport verbleiben im aktiven Betriebs-Change.

## Capabilities

### New Capabilities

- `contextual-wiki-operations`: überprüfbare serialisierte Pflege mit begrenzten Fehlern, konservativer Abhängigkeitsprüfung und sicherer Wiederaufnahme. Weitere Betriebs-Requirements verbleiben im übergeordneten Change.

## Impact

Pflege-CLI, optionaler Callback im gepinnten Compiler, Quellenprüfung, Wartungshelper, Verhaltenstests und lokale Evidence. Keine Änderung am Live-Job oder an produktiven Beständen. [Abnahme](../../../../contextual-llm-wiki/evidence/bounded-failures-03.md).
