## Why

Veröffentlichte LLM-Wiki-Releases benötigen vor ihrer lokalen Übernahme einen reproduzierbaren Installations- und Kompatibilitätsnachweis. Daniel hat Release-Ticket 01 am 13.09.2026 ausdrücklich akzeptiert und Abschluss, Commit und Push beauftragt.

## What Changes

- Ein bestätigtes reguläres Upstream-Release wird auf einen exakten Commit aufgelöst und separat mit seinen unveränderten Manifest-/Lock-Eingängen installiert.
- Die vorhandenen Integrationspatches, Build und tatsächlich ausgeführte Pflichtprüfungen qualifizieren den konkreten Kandidaten; unvollständige oder fehlgeschlagene Prüfungen sperren die Eignung.
- Bootstrap und Runtime lesen dieselbe Release-/Commit-Definition. Die aktive Installation und produktive Wissenspflege bleiben erhalten.

Dieser Change schließt ausschließlich den akzeptierten Release-Ticket-01-Anteil aus `operate-contextual-llm-wiki` ab. Aktivierung/Rollback (Ticket 02), automatische Release-Erkennung (Ticket 03) und offene Wissenspflege bleiben im aktiven Betriebs-Change.

## Capabilities

### Modified Capabilities

- `contextual-wiki-operations`: reproduzierbare, isolierte Release-Qualifikation mit kandidatengebundenen Prüfnachweisen.

## Impact

Lokaler Installer, gemeinsame Release-Definition, Runtime-Prüfung, Test-Reporter und öffentliche Installer-/Wiki-Tests. Keine neue Library-Version und keine Änderung an produktiven Wiki-Daten oder Pflegeautomation. [Abnahme](../../../../contextual-llm-wiki/evidence/release-install-01.md).
