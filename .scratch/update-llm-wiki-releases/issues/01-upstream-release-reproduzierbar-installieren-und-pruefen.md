# 01: Upstream-Release reproduzierbar installieren und prüfen

**What to build:** Ein ausgewähltes veröffentlichtes LLM-Wiki-Release lässt sich als separater Kandidat mit genau seinen upstream festgelegten Abhängigkeiten installieren und auf Kompatibilität mit der vorhandenen Wiki-Integration prüfen. Das Ergebnis weist eindeutig aus, welcher Release-Commit geprüft wurde und ob er zur Aktivierung geeignet ist.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Vor der Erweiterung werden die mehrfach hinterlegten Compiler-Versionsangaben unter Beibehaltung des bisherigen Verhaltens auf eine gemeinsame nachvollziehbare Release-/Commit-Definition zurückgeführt; Installation und Runtime-Prüfung stimmen überein.
- [ ] Der öffentliche Installationsaufruf löst ein reguläres veröffentlichtes Release des bestätigten Upstream-Projekts auf einen exakten Commit auf und erstellt den Kandidaten getrennt von der aktiven Installation. Hauptbranch-Commits, Entwürfe und bloße Tags reichen nicht als Release-Nachweis; Vorabversionen werden standardmäßig ausgeschlossen.
- [ ] Manifest und Lockdatei des Releases bestimmen die Abhängigkeiten ohne eigenständige Versionsupdates oder Lockfile-Neuauflösung. Eine neu veröffentlichte Library-Version allein verändert den Kandidaten nicht.
- [ ] Der bestehende Integrationspatch lässt sich reproduzierbar anwenden; bei Konflikt, fehlender benötigter Laufzeit oder Installationsfehler entsteht ein eindeutiges nicht erfolgreiches Ergebnis, während die aktive Installation erhalten bleibt.
- [ ] Build und erforderliche Integrationstests prüfen die vorhandenen öffentlichen Wiki-Abläufe einschließlich Query, Quellenherkunft und Aktualitätsprüfung an begrenzten Testbeständen. Erfolgreiche Installation allein gilt nicht als Kompatibilitätsnachweis.
- [ ] Release, Commit, Patchstand sowie Ergebnisse der erforderlichen Prüfungen sind dem konkreten Kandidaten zugeordnet. Fehlende, ausstehende oder fehlgeschlagene Prüfungen ergeben keine Aktivierungseignung.
- [ ] Ein echter Release-Kandidat sowie ein gezielt fehlschlagender Kandidat werden über den öffentlichen Aufruf nachgewiesen; bestehende Wiki-Daten, Fachquellen und Pflegeautomation bleiben unverändert.
