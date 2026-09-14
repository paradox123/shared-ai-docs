# 16: Verteilten Gesamtfall und verbleibende Issue-14-Gates nachweisen

**What to build:** Ein reproduzierbarer Abnahmelauf zeigt Einreichung, autonome Bearbeitung, Übergabe zwischen Menschen und Rechnern, vollständige Historie und menschliche Freigabe als zusammenhängendes Verhalten und ordnet die verbleibenden Pilot-Gates ehrlich ein.

**Blocked by:** 08: Aktive und fehlgeschlagene Versuche gezielt steuern; 10: Bereitschaft zustellen und den aktuellen Head menschlich freigeben; 14: Abhängige Issues nach menschlichem Merge selbstständig fortsetzen; 15: Gesamten PRD-Lebenszyklus als Workflow erkunden.

**Status:** ready-for-agent

- [ ] Der aus Ticket 01 übernommene Mehrrechnertest beginnt mit leerer Anwendungsdatenbank: Eine berechtigte Person nimmt eine echte GitHub-Issue-URL über die GUI auf einer vom Server getrennten Maschine auf. Nach Server- und Browserneustart zeigen GUI und öffentliches Readback dieselbe Anforderungs-ID, Fassung, Herkunft und Repositorybindung; erneute Übermittlung erzeugt kein Duplikat. Aktuelle menschliche Repository-Berechtigung, konkrete Zugriffs-/Quellfehler und Redaktion vor Speicherung und Anzeige gelten auch über diese Verbindung. Die Aufnahme allein startet keinen Run. Der Browser benötigt weder Serverdateisystem- noch Datenbankzugriff; ein Nachweis mit beiden Prozessen auf demselben Rechner genügt nicht.
- [ ] GitHub- und Datei-Einreichung sowie beide PRD-Zerlegungswege werden durch bereits erstellte Belege und einen zusammenhängenden verteilten Lauf abgedeckt; die Startclients sind während zentraler Arbeit geschlossen.
- [ ] Ein kontrollierter Fehler öffnet auf einer vom Server getrennten Workstation den lokalen Agenten; vollständige Diagnose-/Chat-/Toolereignisse erscheinen als Workflow-Schritt zentral, und eine menschlich angewiesene Intervention setzt denselben Run fort.
- [ ] Eine weitere berechtigte Person kann den gesamten Zusammenhang lesen und die Steuerung nach geltenden Regeln übernehmen; eine echte interaktive Freigabe betrifft exakt den qualifizierten Head.
- [ ] Reconnect, verlorene Bestätigung, stale Control Lease, Head-Wechsel sowie unvollständige oder redigierte Artefakte werden durch direkte öffentliche Nachweise aus den jeweiligen Tickets abgedeckt.
- [ ] Für jede Anforderung benennt die Abnahme erwartetes Verhalten, beobachtetes Ergebnis und zugehörige Evidence; Logs/Healthchecks allein werden nicht als fachlicher Erfolg gezählt.
- [ ] Der ursprüngliche Drei-Identitäten-Nachweis, extern freigegebene Agent-Definition-Revisionen und unveränderte LangGraph-Koexistenz werden separat geprüft. Nicht vorhandene Nachweise ergeben ein offenes Gate beziehungsweise Stop und werden nicht durch Rollenwechsel einer Person oder GUI-Fertigstellung ersetzt.
- [ ] Vorhandene Pilot-/CRM-Hauptcheckouts, Laufzeitdaten und Dienste werden nicht unautorisiert verändert; der bestehende Issue-14-Change und das Parent-Issue werden durch dieses Ticket nicht geschlossen oder umgeschrieben.
- [ ] Nach einer DRY-/SOLID-/KISS-Prüfung sind relevante Verhaltenstests, Browsernachweise und OpenSpec-Validierung erneut grün; reale Integrationslücken und fehlende menschliche Voraussetzungen bleiben ausdrücklich dokumentiert.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.

### 2026-09-14 — Mehrrechnernachweis aus Ticket 01 übernommen

Der Nutzer hat [Ticket 01](01-github-issue-eingeben-und-einreichung-wiederfinden.md)
lokal abgenommen und dessen Mehrrechnertest diesem Ticket zugeordnet. Die
[lokalen Nachweise](../../../openspec/changes/add-agent-framework-operator-gui/issue-01-evidence.md)
sind die Ausgangsbasis; der verteilte Nachweis ist weiterhin offen. Dafür werden
ein erreichbarer Testserver und ein Browser auf einer anderen Maschine benötigt.
Die oben eingetragenen Blocker dieses Tickets bleiben bestehen.
