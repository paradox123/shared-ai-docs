# 15: Gesamten PRD-Lebenszyklus als Workflow erkunden

**What to build:** Die grafische Workflow-Ansicht macht PRD-Zerlegung, Kindissues, Runs, Reviews und lokale Handovers über alle beteiligten Personen und Rechner hinweg navigierbar und mit der vollständigen zentralen Historie überprüfbar.

**Blocked by:** 05: Handover und lokale Historie nach Verbindungsabbruch fortsetzen; 13: PRD-Datei in lokale Issue-Dateien zerlegen.

**Status:** ready-for-agent

- [ ] Eine PRD-Übersicht zeigt Einreichung, Zerlegungsaktivitäten und Kindissue-Abhängigkeiten; die Navigation führt in eigenständige Runs und deren Aktivitäten, Versuche und Sessions, ohne Identitäten zu vermischen.
- [ ] Der Graph zeigt reale Zustände einschließlich paralleler Reviews, Wiederholungen, Handover, Wartebedingungen und fehlender Synchronisierung; Layout und clientseitige Darstellung steuern keine Backend-Entscheidungen.
- [ ] Anklicken und Filtern nach Issue, Run, Aktivität, Person, Rechner oder Session öffnet die vollständigen zugeordneten Chats, Erkenntnisse, Toolaufrufe/-ergebnisse und Artefakte mit paginiertem Nachladen.
- [ ] Live-Ereignisse aktualisieren den ausgewählten Ablauf, ohne Benutzerfokus und Quellreihenfolge zu verlieren. Große Historien werden vollständig abrufbar gehalten, ohne jeden Toolaufruf als permanent sichtbaren Graphknoten rendern zu müssen.
- [ ] Zentrale und lokale Ereignisse sowie vor den Kind-Runs entstandene PRD-Beobachtungen bleiben nach Neustart sichtbar. Fehlende/redigierte Inhalte und ausstehende Synchronisierung werden nicht als vollständige Evidence dargestellt.
- [ ] Der vorhandene Dossier-/Exportpfad bleibt kompatibel und wird um die benötigten Einreichungs-/Mandatsbezüge und lokale Aktivitäten ergänzt; exportierte Daten und öffentliche Detailansicht lassen sich auf dieselbe Historie zurückführen.
- [ ] Ein repräsentativer Ablauf mit mehreren Kindissues, parallelen Reviews und lokaler Diagnose wird im Browser visuell und funktional geprüft; API-/Quellereignisvergleich belegt Vollständigkeit. React Flow ist der bevorzugte geprüfte Kandidat; seine Verwendung ersetzt diesen Nachweis nicht.

## Comments

### 2026-09-13 — Backstage-/React-Flow-Prototyp

Frage: Welcher Einstieg macht die verteilte Run-Bedienung verständlich — Workflow-Werkbank, persönliche Interventions-Inbox oder Repository mit PRD-Mandaten?

Technisch beobachtet: Ein echtes Backstage-Frontend-Plugin lädt React Flow und drei umschaltbare Ansichten. Graphauswahl, Session-/Tooldetails, Einreichung, Intervention, Stale-Head-Sperre, Lease-Übergabe und Workstation-Reconnect wurden mit ausdrücklich simulierten Zuständen im Browser erkundet; der Vite-Build läuft durch. Das bestätigt die Frontend-Einbettung für die verwendete Paketkombination. Die UI-Auswahl ist noch offen.

Primärquelle: lokaler Wegwerfbranch `codex/prototype-backstage-react-flow`, Commit `f804685`; [Prototyp, Bedienwege und Grenzen](../../../../shared-ai-docs-backstage-prototype/microsoft-agent-framework-work-package-pilot/operator-gui-prototype/README.md). [Laufende lokale Vorschau](http://127.0.0.1:4317/prototype/agent-operations?variant=A), solange der Dev-Server läuft. Code und Varianten bleiben außerhalb von `main`.

Kein Nachweis für echte Persistenz, Provider-Autorisierung, autonome Hintergrundarbeit, vollständige reale Session-Erfassung oder tatsächliches Workstation-Öffnen. Keine Produktvariante übernommen; keine Akzeptanzkriterien abgehakt und kein Ticketstatus geändert.

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
