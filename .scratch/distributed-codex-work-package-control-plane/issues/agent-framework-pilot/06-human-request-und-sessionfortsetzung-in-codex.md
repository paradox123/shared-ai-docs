# 06: Eine Human Request beantworten und die Session in Codex fortsetzen

**What to build:** Ein zweiter berechtigter Mensch öffnet einen fehlgeschlagenen oder wartenden Activity Attempt im Operator Client, kann ihn gezielt in Codex öffnen und entscheidet nachvollziehbar zwischen derselben Session, einem Fork oder einem frischen Versuch.

**Blocked by:** 03: Repositoryzugriff und exklusive Steuerung durchsetzen; 05: Repository-Base und externe Wirkungen sicher reconciliieren

**Status:** ready-for-agent

- [ ] Eine dauerhafte Human Request bleibt nach API-/Workerneustart mit Run, Attempt, Session, Head, Problem, Evidence und zulässigen Aktionen auffindbar.
- [ ] Der Operator zeigt vor jeder Fortsetzung Zielattempt, Sessionidentität, Phase, erwartete Head-SHA, Lease-Inhaber und bereits eingetretene Wirkungen.
- [ ] `Resume` verwendet dieselbe Session-ID; `Fork` erzeugt eine neue Session mit expliziter Herkunft; `Fresh Retry` erzeugt eine neue Session ohne automatische Übernahme der bisherigen Unterhaltung.
- [ ] `Open in Codex` öffnet genau die zugeordnete Session, wenn der Adapter dies sicher unterstützt.
- [ ] Kann die ursprüngliche Background-Session nicht direkt in Codex dargestellt werden, benennt der Operator die Einschränkung und erzeugt erst nach ausdrücklicher Bestätigung einen als Handoff gekennzeichneten Fork mit Herkunft.
- [ ] Eine schreibende Interaktion in der geöffneten Codex-Session setzt die aktuelle Control Lease voraus; ihre beobachtbaren Nachrichten, Tools, Ergebnisse und Entscheidungen fließen in dieselbe Run History zurück.
- [ ] Das Öffnen allein verändert weder Workflowphase, Head, externe Effekte noch Sessionidentität und erzeugt keinen unkorrelierten Nebenlauf.
- [ ] Doppelte, veraltete oder falsch adressierte Antworten und Fortsetzungsentscheidungen werden ohne Nebenwirkung abgelehnt; eine gültige Entscheidung wirkt logisch genau einmal.

## Session lesson

Die LangGraph-Intervention eröffnete eine separate Zusammenfassungs-Task, während die eigentliche Background-Session schwer auffindbar blieb. Dieses Ticket macht die konkrete Session erreichbar, ohne die zentrale Run History aufzugeben.
