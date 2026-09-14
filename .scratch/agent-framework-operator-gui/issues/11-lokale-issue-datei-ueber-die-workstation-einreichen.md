# 11: Lokale Issue-Datei über die Workstation einreichen und bearbeiten

**What to build:** Ein Mensch übergibt den Pfad einer Issue-Markdown-Datei auf seinem Rechner; die Control Plane speichert genau diesen Auftrag und verarbeitet ihn im selben Hintergrundworkflow wie ein GitHub Issue.

**Blocked by:** 04: Handover im lokalen Agenten öffnen und Diagnose zentral erfassen; 09: Eingereichtes Issue unbeaufsichtigt bis Intervention oder Review bearbeiten.

**Status:** ready-for-agent

- [ ] Die Einreichung benennt Quelle und erreichbaren Quell-Workspace/Host; der tatsächliche Inhalt wird über den autorisierten Workstation-Zugang aufgenommen, statt den Pfad als beliebige Serverdatei zu interpretieren.
- [ ] Zielrepository wird aus eindeutiger Zuordnung ermittelt oder in der Startoberfläche ausgewählt und gegen Repository Authorization geprüft; ein lokaler Dateipfad gewährt keine zusätzlichen Rechte.
- [ ] Eine stabile lokale Issue-/Einreichungsidentität und aufgenommene Fassung funktionieren ohne erfundene GitHub-Issue-Nummer. Die notwendige Generalisierung erweitert bestehende Verträge kompatibel vor der lokalen Aufnahme.
- [ ] Das Issue bleibt eine Datei; die Aufnahme veröffentlicht kein GitHub Issue. Der zentrale Run nutzt denselben autorisierten Implementierungs-/Evidence-/Reviewpfad und bleibt nach Host-/Service-Neustart nachvollziehbar.
- [ ] Nachträgliche Dateiänderungen verändern nicht still das aktive Arbeitsmandat. Wiederholte Aufnahme desselben logischen Auftrags erzeugt keine doppelten Runs.
- [ ] Die GUI zeigt lokale Herkunft, Inhalt, Version, Repository, Aktivitäten und Ergebnis; ein realer Dateiauftrag von einer getrennten Workstation beweist den gesamten Pfad bis zu Intervention oder qualifiziertem Stand.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
