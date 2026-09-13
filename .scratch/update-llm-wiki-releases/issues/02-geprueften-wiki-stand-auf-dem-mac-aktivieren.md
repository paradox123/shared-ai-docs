# 02: Geprüften Wiki-Stand auf dem Mac aktivieren

**What to build:** Ein erfolgreich geprüfter Release-Kandidat kann automatisch die bisherige lokale LLM-Wiki-Installation ersetzen. Der Betreiber kann die tatsächlich aktive Version erkennen; bei fehlgeschlagener Übernahme bleibt der bisherige funktionsfähige Stand nutzbar.

**Blocked by:** 01 — Upstream-Release reproduzierbar installieren und prüfen.

**Status:** ready-for-agent

- [ ] Der öffentliche Updateaufruf aktiviert ausschließlich den konkreten Kandidaten, dessen Build und sämtliche erforderlichen Tests erfolgreich sind; eine nachträgliche Änderung des Kandidaten erfordert erneute Prüfung.
- [ ] Die Übernahme benötigt keine erneute menschliche Review-, Merge- oder Deployment-Freigabe. Ungeprüfte oder fehlgeschlagene Kandidaten können die aktive Installation nicht ersetzen.
- [ ] Nach der Umschaltung belegen die tatsächlich genutzte Release-/Commit-Identität und ein begrenzter öffentlicher Wiki-Funktionsaufruf die erfolgreiche lokale Aktivierung; ein Merge oder ein Versionsmanifest allein genügt nicht.
- [ ] Bestehende Wissensseiten, gespeicherte Synthesen und ihr Zustand bleiben erhalten. Falls das Release eine Datenmigration benötigt, umfasst die Wiederherstellbarkeit auch die betroffenen Daten.
- [ ] Bei fehlgeschlagener Umschaltung oder Aktivierungsprüfung wird der bisherige funktionsfähige Stand beibehalten beziehungsweise wiederhergestellt; das Ergebnis meldet den Fehler und den weiterhin aktiven Stand eindeutig.
- [ ] Wiederholte Übernahme desselben unveränderten Releases ist ein No-op. Gleichzeitige Updates oder laufende Wiki-Nutzung verursachen keine gemischte Runtime und keine überlappenden Zustandsänderungen.
- [ ] Erfolgreiche Aktivierung, No-op und gezielt ausgelöster Aktivierungsfehler werden auf dem Mac über den öffentlichen Aufruf nachgewiesen. Wissenspflege und deren Scheduler werden dabei nicht verändert.
