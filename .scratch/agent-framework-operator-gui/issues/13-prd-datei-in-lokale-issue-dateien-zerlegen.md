# 13: PRD-Datei in lokale Issue-Dateien zerlegen

**What to build:** Eine PRD-Datei durchläuft dieselbe beobachtbare Zerlegung und erzeugt ihre abgeleiteten Issues als einzelne Markdown-Dateien im zugeordneten Quell-Workspace.

**Blocked by:** 11: Lokale Issue-Datei über die Workstation einreichen und bearbeiten; 12: GitHub-PRD in verknüpfte Issues zerlegen.

**Status:** ready-for-agent

- [ ] Die tatsächliche PRD-Fassung vom bezeichneten Quellrechner wird mit Mandat, Zielrepository und Herkunft in der Datenbank gespeichert; die Zerlegungsaktivität bleibt mit den Kindissues verknüpft.
- [ ] Ein Kindissue pro Datei folgt den geltenden Issue-Konventionen des Quellrepositories und enthält Mandatsherkunft, Abhängigkeiten und bearbeitbaren Status.
- [ ] Es werden keine GitHub Issues als Ersatz oder Spiegel erzeugt; gleichwohl nutzen die Kindissues den gemeinsamen Implementierungsworkflow und die Run-Ansicht.
- [ ] Lokale Dateierzeugung ist als externer Effekt nachweisbar: vorhandene Ergebnisse werden nach Abbruch adoptiert, fremde Dateien nicht überschrieben und Namens-/Inhaltskonflikte konkret gemeldet.
- [ ] Ein nicht erreichbarer Quell-Workspace führt zu einem dauerhaften sichtbaren Wartezustand oder Blocker statt zum Schreiben auf einem beliebigen Serverpfad.
- [ ] Die Abnahme liest tatsächlich erzeugte Dateien auf der zugeordneten Workstation beziehungsweise ihrem ausdrücklich freigegebenen Workspace und vergleicht Herkunft/Abhängigkeiten mit der zentralen Übersicht; ein Kind-Run läuft durch den vorhandenen Hintergrundpfad.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
