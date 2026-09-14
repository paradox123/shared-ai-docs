# 04: Handover im lokalen Agenten öffnen und Diagnose zentral erfassen

**What to build:** Ein über die GUI eingereichter und gestarteter Run löst bei einem kontrollierten Fehler auf einer zugeordneten Workstation automatisch eine lokale Agentensession aus, die lesend diagnostiziert und deren vollständige beobachtbare Arbeit als Aktivität desselben Runs in der GUI erscheint.

**Blocked by:** 03: Selbst gestarteten Run als Workflow und Sessionverlauf beobachten.

**Status:** ready-for-agent

- [ ] Ein Workstation Client ist einer authentifizierten menschlichen Identität und einem Gerät zugeordnet; die Control Plane adressiert einen dauerhaften Handover-Auftrag an diesen Empfänger.
- [ ] Bei geschlossener GUI öffnet ein Servertrigger den tatsächlich unterstützten lokalen Agenten mit Handover-Inhalt und autorisiertem Zugriff auf weitere gespeicherte Daten. Eine Promptdatei, ein Link oder ein Fake-Launcher allein erfüllt den Nachweis nicht.
- [ ] Handover, Ziel-Run/-Versuch, zentrale Session, lokale Assistenzsession, zuständiger Mensch und Ausführungsrechner sind explizit zugeordnet; zentrale Ausführung und Arbeitsverzeichnis bleiben bestehen.
- [ ] Der lokale Agent lädt relevanten Kontext, untersucht den Fehler lesend und formuliert einen Lösungsvorschlag. Er verändert weder Implementierungsdateien noch Workflow-Entscheidungen und beansprucht nicht automatisch die Control Lease.
- [ ] Alle beobachtbaren Benutzer-/Agentennachrichten, bereitgestellten Aufträge/Kontexte, Erkenntnisse, Toolparameter/-ergebnisse mit Dauer/Fehlern und Artefakte dieser Diagnose werden zentral erfasst und als Workflow-Aktivität lesbar; nur eine Endzusammenfassung reicht nicht.
- [ ] Zugriff, Ereignisannahme und Redaktionsregeln verhindern, dass ein fremder Client Beobachtungen unter einer anderen Session/Identität einspeist oder über Beobachtungsdaten Steuerungsbefugnisse erhält.
- [ ] Wiederholte Zustellung desselben Auftrags wird mit derselben lokalen Session abgeglichen. Nicht unterstütztes Öffnen oder fehlende vollständige Ereigniserfassung ergibt einen sichtbaren Capability-Blocker und keinen behaupteten Erfolg.
- [ ] Der Nachweis erzeugt den Fehler in einem über den GUI-Eingabe-/Startweg aufgenommenen Run und verwendet eine echte lokale Agentenintegration auf einem vom Server getrennten Rechner. Ein manuell vorbereiteter Datenbank-Run ersetzt diesen Benutzerpfad nicht; die spätere vollständige Review-/Reparaturkette ist dafür noch keine Voraussetzung.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
