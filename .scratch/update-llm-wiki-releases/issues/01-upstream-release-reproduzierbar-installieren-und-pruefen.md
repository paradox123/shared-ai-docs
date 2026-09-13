# 01: Upstream-Release reproduzierbar installieren und prüfen

**What to build:** Ein ausgewähltes veröffentlichtes LLM-Wiki-Release lässt sich als separater Kandidat mit genau seinen upstream festgelegten Abhängigkeiten installieren und auf Kompatibilität mit der vorhandenen Wiki-Integration prüfen. Das Ergebnis weist eindeutig aus, welcher Release-Commit geprüft wurde und ob er zur Aktivierung geeignet ist.

**Blocked by:** None (can start immediately).

**Status:** resolved

- [x] Vor der Erweiterung werden die mehrfach hinterlegten Compiler-Versionsangaben unter Beibehaltung des bisherigen Verhaltens auf eine gemeinsame nachvollziehbare Release-/Commit-Definition zurückgeführt; Installation und Runtime-Prüfung stimmen überein.
- [x] Der öffentliche Installationsaufruf löst ein reguläres veröffentlichtes Release des bestätigten Upstream-Projekts auf einen exakten Commit auf und erstellt den Kandidaten getrennt von der aktiven Installation. Hauptbranch-Commits, Entwürfe und bloße Tags reichen nicht als Release-Nachweis; Vorabversionen werden standardmäßig ausgeschlossen.
- [x] Manifest und Lockdatei des Releases bestimmen die Abhängigkeiten ohne eigenständige Versionsupdates oder Lockfile-Neuauflösung. Eine neu veröffentlichte Library-Version allein verändert den Kandidaten nicht.
- [x] Der bestehende Integrationspatch lässt sich reproduzierbar anwenden; bei Konflikt, fehlender benötigter Laufzeit oder Installationsfehler entsteht ein eindeutiges nicht erfolgreiches Ergebnis, während die aktive Installation erhalten bleibt.
- [x] Build und erforderliche Integrationstests prüfen die vorhandenen öffentlichen Wiki-Abläufe einschließlich Query, Quellenherkunft und Aktualitätsprüfung an begrenzten Testbeständen. Erfolgreiche Installation allein gilt nicht als Kompatibilitätsnachweis.
- [x] Release, Commit, Patchstand sowie Ergebnisse der erforderlichen Prüfungen sind dem konkreten Kandidaten zugeordnet. Fehlende, ausstehende oder fehlgeschlagene Prüfungen ergeben keine Aktivierungseignung.
- [x] Ein echter Release-Kandidat sowie ein gezielt fehlschlagender Kandidat werden über den öffentlichen Aufruf nachgewiesen; bestehende Wiki-Daten, Fachquellen und Pflegeautomation bleiben unverändert.

## Comments

13.09.2026: Implementiert und reviewed auf `codex/update-llm-wiki-releases` im isolierten Worktree `../shared-ai-docs-update-llm-wiki-releases`, Basis `dbb6df2030f26543099eb34d3bb6b7ff38963dbc`. [Abnahme und Grenzen](../../../contextual-llm-wiki/evidence/release-install-01.md), [Kandidatenberichte](../../../contextual-llm-wiki/evidence/release-install-01-results.json) und [Standards-/Spec-Review](../../../contextual-llm-wiki/evidence/release-install-01-review.md). Kein Merge und keine produktive Aktivierung; Tickets 02/03 bleiben separat.
