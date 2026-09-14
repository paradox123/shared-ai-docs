# 12: GitHub-PRD in verknüpfte Issues zerlegen

**What to build:** Eine als GitHub Issue eingereichte PRD wird als Arbeitsmandat aufgenommen, im Hintergrund in nachvollziehbare GitHub Issues zerlegt und mit ihren ersten zulässigen Implementierungsläufen in der Übersicht verbunden.

**Blocked by:** 07: Intervention per GUI oder lokalem Agenten beantworten; 09: Eingereichtes Issue unbeaufsichtigt bis Intervention oder Review bearbeiten.

**Status:** ready-for-agent

- [ ] Der Aufnahmeweg unterscheidet ein PRD-Arbeitsmandat von einem direkt zu implementierenden Issue und speichert dessen zugelassene Fassung und Autorisierungsherkunft.
- [ ] Die beobachtbare PRD-Zerlegung wird schon vor Existenz der Kind-Runs als zugeordnete Aktivität gespeichert, einschließlich Gesprächen, Erkenntnissen, Tools und Artefakten.
- [ ] Abgeleitete Issues werden tatsächlich in GitHub mit PRD-Herkunft und Abhängigkeiten angelegt; jedes Issue erhält höchstens einen eigenen Run und erbt Autorisierung nur innerhalb des Mandats.
- [ ] Unterbrechung nach dem Anlegen eines Kindes wird mit dem existierenden GitHub Issue reconciliiert, statt ein Duplikat anzulegen. Die GUI zeigt auch einen teilweise abgeschlossenen Zerlegungsschritt korrekt.
- [ ] Offene Produktentscheidungen führen zu gezielten Interventionen am Mandat, die über den vorhandenen Antwortweg gelöst werden können; neue Fachentscheidungen werden nicht aus einer pauschalen Freigabe erfunden.
- [ ] Unabhängige zulässige Anfangsarbeit startet unter bestehender Repository-Serialisierung ohne weitere Startfreigabe. Abhängige Folgearbeit bleibt bis zum nachgewiesenen Merge-/Abschlussübergang wartend.
- [ ] Eine kleine echte PRD zeigt gespeicherte Zerlegung, GitHub-Kindissues, Abhängigkeiten und mindestens einen beobachtbaren Kind-Run über öffentliche Quellen und GUI.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
