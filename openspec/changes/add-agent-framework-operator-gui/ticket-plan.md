# Bestätigte Ticketaufteilung

Der Nutzer hat die Aufteilung mit 16 Tickets bestätigt. Die Tickets sind einzeln mit ihren Akzeptanzkriterien und Blockern im lokalen Tracker veröffentlicht. Ticket 01 ist lokal abgenommen und `resolved`; die übrigen Tickets tragen den Status `ready-for-agent` unter ihren jeweiligen Blockern. Die fachlichen Entscheidungen bleiben im bestehenden Change; Parent-Issue und bestehende Pilot-Tickets wurden nicht geändert.

## Drei kleine benutzbare Einstiegsschritte

1. **Eingeben und wiederfinden:** GitHub-Issue-URL in einer minimalen GUI eingeben, tatsächlichen Inhalt samt Herkunft dauerhaft speichern und die Einreichung wieder öffnen. Noch keine Agentenverarbeitung; die Anzeige nennt das wahrheitsgemäß eine aufgenommene Einreichung.
2. **Starten und Ergebnis sehen:** Den eingegebenen Auftrag in einen Run überführen, die erste echte Hintergrundaktivität automatisch ausführen und Zustand/Ergebnis in einer einfachen Run-Ansicht sehen. Noch kein aufwendiger Graph nötig.
3. **Workflow und Details verfolgen:** Genau den selbst gestarteten Run mit Aktivitäten, vollständigen Sessiondetails und Live-Ereignissen als schmalen Workflow untersuchen, auch von einem anderen berechtigten Client.

Jedes Ticket beginnt an einer realen Benutzerhandlung und liefert einen nutzbaren Fortschritt. Kein Beobachtungsticket setzt einen manuell vorbereiteten Datenbank-Run voraus. Der Server-/Client-Fall bleibt vom ersten Eingabeschritt an Bestandteil der Architektur. Der Nutzer hat Ticket 01 am 2026-09-14 lokal abgenommen und dessen Mehrrechnertest in Ticket 16 zur verteilten Gesamtabnahme verschoben; der verteilte Nachweis bleibt verbindlich und offen. Im fertigen Startweg kann eine neue Quelle weiterhin in einer Aktion eingereicht und gestartet werden, ohne doppelte fachliche Freigabe.

Das bisherige große Einstiegsticket wird durch diese drei Slices ersetzt. Die übrigen Tickets bleiben inhaltlich erhalten und rücken um zwei Nummern nach hinten: Handover ist jetzt 04, vollständige Hintergrundkette 09, PRD-Gesamtgraph 15 und Gesamt-Abnahme 16.

## Ausgangslage aus der Implementierung

- Die bestehende API bietet Run-/Event-/Artifact-/Export- und Steuerungsoberflächen, erzwingt aber bislang Loopback und eine Fixture-Capability. Ticket 01 liefert einen erreichbaren authentifizierten Einreichungsweg; Ticket 03 verwendet diesen Zugang für vollständige Run-Beobachtung.
- Aufnahme verwendet ein synthetisches Issue-Fixture und eine positive Issue-Nummer. Ticket 01 entkoppelt die Quellenaufnahme von manueller Fixture-Vorbereitung; Ticket 11 ergänzt lokale Issueidentitäten kompatibel.
- Worker werden bisher für einen expliziten Run und Ausführungsmodus gestartet. Ticket 02 automatisiert den ersten echten Schritt aus einer Einreichung, Ticket 09 verbindet die vollständige Verarbeitung und überwacht Recovery und Head-Änderungen.
- Zentrale History-/Artifact-, Control-Lease-/Transfer- und Agentensteuerungsverträge existieren bereits und werden weiterverwendet. Ticket 02 erhält die Beobachtungen des gestarteten Schritts; Ticket 03 macht die vollständigen Details grafisch zugänglich.
- Automatisches Öffnen einer lokalen Assistenzsession samt vollständiger Ereigniserfassung wird früh in Ticket 04 an einem über die GUI gestarteten Fehlerfall real geprüft.
- Nötige vorbereitende Entkopplung erfolgt kompatibel vor dem jeweiligen neuen Verhalten. Ein breites eigenständiges Refactoring ist anhand der untersuchten Schnittstellen nicht gerechtfertigt.

## Veröffentlichte Tickets

1. **[GitHub Issue eingeben und gespeicherte Einreichung wiederfinden](../../../.scratch/agent-framework-operator-gui/issues/01-github-issue-eingeben-und-einreichung-wiederfinden.md)**

   **Blocked by:** Keine. **Status:** `resolved` — lokal abgenommen; Mehrrechnertest in Ticket 16.

   **Lieferergebnis:** Ein Mensch gibt in einer minimalen servergestützten GUI eine GitHub-Issue-URL ein und sieht den tatsächlich aufgenommenen Auftrag mit Inhalt, Herkunft und Repository in seiner Einreichungsübersicht.

2. **[Eingereichtes Issue als erste Hintergrundaktivität starten](../../../.scratch/agent-framework-operator-gui/issues/02-eingereichtes-issue-als-hintergrundaktivitaet-starten.md)**

   **Blocked by:** 01.

   **Lieferergebnis:** Der Mensch startet sein eingegebenes Issue über die GUI; der Server erzeugt den zugehörigen Run, führt den ersten realen Agentenschritt aus und zeigt dessen Status und Ergebnis in einer einfachen Run-Ansicht.

3. **[Selbst gestarteten Run als Workflow und Sessionverlauf beobachten](../../../.scratch/agent-framework-operator-gui/issues/03-gestarteten-run-als-workflow-und-sessionverlauf-beobachten.md)**

   **Blocked by:** 02.

   **Lieferergebnis:** Ein Mensch öffnet seinen über die GUI gestarteten Run von einem berechtigten Client und verfolgt die tatsächlichen Aktivitäten sowie die vollständigen gespeicherten Sessiondetails in einer schmalen Workflow-Ansicht.

4. **[Handover im lokalen Agenten öffnen und Diagnose zentral erfassen](../../../.scratch/agent-framework-operator-gui/issues/04-handover-im-lokalen-agenten-oeffnen-und-diagnose-erfassen.md)**

   **Blocked by:** 03.

   **Lieferergebnis:** Ein über die GUI eingereichter und gestarteter Run löst bei einem kontrollierten Fehler auf einer zugeordneten Workstation automatisch eine lokale Agentensession aus, die lesend diagnostiziert und deren vollständige beobachtbare Arbeit als Aktivität desselben Runs in der GUI erscheint.

5. **[Handover und lokale Historie nach Verbindungsabbruch fortsetzen](../../../.scratch/agent-framework-operator-gui/issues/05-handover-und-historie-nach-verbindungsabbruch-fortsetzen.md)**

   **Blocked by:** 04.

   **Lieferergebnis:** Ein zeitweise ausgeschalteter oder getrennter Workstation Client erhält weiterhin offene Handovers und synchronisiert seine bereits entstandene Agentenhistorie nachvollziehbar nach.

6. **[Control Lease zwischen Menschen in der GUI übergeben](../../../.scratch/agent-framework-operator-gui/issues/06-control-lease-in-der-gui-uebergeben.md)**

   **Blocked by:** 02.

   **Lieferergebnis:** Berechtigte Menschen beanspruchen oder wechseln die Steuerung eines bestehenden Runs grafisch, während alle Beobachter denselben nachvollziehbaren Verantwortungsstand sehen.

7. **[Intervention per GUI oder lokalem Agenten beantworten](../../../.scratch/agent-framework-operator-gui/issues/07-intervention-per-gui-oder-lokalem-agenten-beantworten.md)**

   **Blocked by:** 04, 06.

   **Lieferergebnis:** Der steuernde Mensch beantwortet eine konkrete Interventionsanfrage entweder grafisch oder mit Unterstützung seines lokalen Agenten; dieselbe zentrale Session verarbeitet die Antwort und der Run wird fortgesetzt.

8. **[Aktive und fehlgeschlagene Versuche gezielt steuern](../../../.scratch/agent-framework-operator-gui/issues/08-aktive-und-fehlgeschlagene-versuche-gezielt-steuern.md)**

   **Blocked by:** 07.

   **Lieferergebnis:** Ein Mensch greift aus der GUI oder über seinen lokalen Agenten gezielt in einen ausgewählten Aktivitätsversuch ein und nutzt die bestehenden Fortsetzungs- und Codex-Öffnungswege.

9. **[Eingereichtes Issue unbeaufsichtigt bis Intervention oder Review bearbeiten](../../../.scratch/agent-framework-operator-gui/issues/09-eingereichtes-issue-unbeaufsichtigt-bis-intervention-oder-review-bearbeiten.md)**

   **Blocked by:** 02.

   **Lieferergebnis:** Nach einmaligem Start übernimmt der Hintergrundbetrieb den vorhandenen Implementierungs-, Evidence-, Review- und Reparaturpfad und erreicht selbstständig einen konkreten Blocker oder einen qualifizierten Stand.

10. **[Bereitschaft zustellen und den aktuellen Head menschlich freigeben](../../../.scratch/agent-framework-operator-gui/issues/10-bereitschaft-zustellen-und-aktuellen-head-menschlich-freigeben.md)**

   **Blocked by:** 04, 06, 09.

   **Lieferergebnis:** Sobald ein Hintergrundrun einen qualifizierten Head erreicht, wird der zuständige Mensch über seinen lokalen Agenten darauf aufmerksam und kann genau diesen Head interaktiv in der GUI freigeben.

11. **[Lokale Issue-Datei über die Workstation einreichen und bearbeiten](../../../.scratch/agent-framework-operator-gui/issues/11-lokale-issue-datei-ueber-die-workstation-einreichen.md)**

   **Blocked by:** 04, 09.

   **Lieferergebnis:** Ein Mensch übergibt den Pfad einer Issue-Markdown-Datei auf seinem Rechner; die Control Plane speichert genau diesen Auftrag und verarbeitet ihn im selben Hintergrundworkflow wie ein GitHub Issue.

12. **[GitHub-PRD in verknüpfte Issues zerlegen](../../../.scratch/agent-framework-operator-gui/issues/12-github-prd-in-verknuepfte-issues-zerlegen.md)**

   **Blocked by:** 07, 09.

   **Lieferergebnis:** Eine als GitHub Issue eingereichte PRD wird als Arbeitsmandat aufgenommen, im Hintergrund in nachvollziehbare GitHub Issues zerlegt und mit ihren ersten zulässigen Implementierungsläufen in der Übersicht verbunden.

13. **[PRD-Datei in lokale Issue-Dateien zerlegen](../../../.scratch/agent-framework-operator-gui/issues/13-prd-datei-in-lokale-issue-dateien-zerlegen.md)**

   **Blocked by:** 11, 12.

   **Lieferergebnis:** Eine PRD-Datei durchläuft dieselbe beobachtbare Zerlegung und erzeugt ihre abgeleiteten Issues als einzelne Markdown-Dateien im zugeordneten Quell-Workspace.

14. **[Abhängige Issues nach menschlichem Merge selbstständig fortsetzen](../../../.scratch/agent-framework-operator-gui/issues/14-abhaengige-issues-nach-menschlichem-merge-fortsetzen.md)**

   **Blocked by:** 13.

   **Lieferergebnis:** Der Pilot beobachtet abgeschlossene Vorgänger und startet zulässige Folge-Issues aus GitHub- oder Datei-Mandaten selbstständig von der maßgeblichen Repositorybasis.

15. **[Gesamten PRD-Lebenszyklus als Workflow erkunden](../../../.scratch/agent-framework-operator-gui/issues/15-gesamten-prd-lebenszyklus-als-workflow-erkunden.md)**

   **Blocked by:** 05, 13.

   **Lieferergebnis:** Die grafische Workflow-Ansicht macht PRD-Zerlegung, Kindissues, Runs, Reviews und lokale Handovers über alle beteiligten Personen und Rechner hinweg navigierbar und mit der vollständigen zentralen Historie überprüfbar.

16. **[Verteilten Gesamtfall und verbleibende Issue-14-Gates nachweisen](../../../.scratch/agent-framework-operator-gui/issues/16-verteilten-gesamtfall-und-issue-14-gates-nachweisen.md)**

   **Blocked by:** 08, 10, 14, 15.

   **Übernommener Prüfpunkt aus 01:** Echte GitHub-Aufnahme aus leerer Datenbank mit Server und Browser auf unterschiedlichen Rechnern; dieselbe Anforderungs-ID und Fassung nach beiden Neustarts, keine Duplikate, aktuelle Berechtigung, Redaktion und konkrete Fehler. Aufnahme allein startet keinen Run.

   **Lieferergebnis:** Ein reproduzierbarer Abnahmelauf zeigt Einreichung, autonome Bearbeitung, Übergabe zwischen Menschen und Rechnern, vollständige Historie und menschliche Freigabe als zusammenhängendes Verhalten und ordnet die verbleibenden Pilot-Gates ehrlich ein.

## Abhängigkeiten und sinnvolle Bearbeitungsfolge

Der Einstieg ist 01 → 02 → 03. Nach 02 können Steuerungswechsel (06) und die vollständige Hintergrundkette (09) bereits unabhängig von der erweiterten Workflow-Darstellung (03) bearbeitet werden. Der bevorzugte frühe Handover-Nachweis ist 01 → 02 → 03 → 04; offline/reconnect folgt in 05.

- Ticket 04 benötigt die tatsächlichen gestarteten Runs und die Sessiondetailansicht aus 03. Es wartet nicht auf die vollständige Review-/Reparaturkette.
- Ticket 06 braucht einen durch 02 nutzbar erzeugten Run, aber keinen Graph-Renderer; seine eigene grafische Steuerungsansicht wird im Slice geliefert.
- Ticket 09 erweitert den funktionierenden Hintergrundstart aus 02; vollständige Graphdetails sind kein notwendiger Blocker.
- Ticket 10 braucht Workstation-Zustellung (04), menschliche Steuerungsrechte (06) und tatsächliche Qualifikation (09).
- Ticket 12 braucht beantwortbare Mandatsinterventionen (07) und den selbstständigen Kind-Run-Pfad (09).
- Ticket 13 ergänzt den lokalen Speicherweg (11) auf der vollständigen GitHub-PRD-Zerlegung (12).
- Ticket 14 folgt 13, das bereits den GitHub-PRD-Pfad einschließt. Ticket 15 ergänzt den Gesamtgraph unabhängig von erweiterten Steuerungsaktionen (08), Freigabe (10) und automatischem Nachfolgerstart (14).
- Ticket 16 integriert die letzten unabhängigen Zweige 08, 10, 14 und 15; transitive Vorgänger werden nicht redundant aufgezählt.

Jedes Funktionsticket enthält die für sein Benutzerergebnis nötige Persistenz, autorisierte Schnittstelle, angemessene GUI und Verhaltenstests. Die frühen Slices verlangen fünf bis sechs gezielte Akzeptanzkriterien statt der bisherigen gebündelten neun. Das letzte Ticket nimmt zuvor geprüfte Features gemeinsam ab.

React Flow bleibt ein geprüfter bevorzugter Kandidat für die Workflow-Darstellung. Ticket 03 beginnt mit einem schmalen Run-Graph; Ticket 15 ergänzt die vollständige verschachtelte PRD-Lebenszyklusansicht.

## Anforderungsabdeckung

| OpenSpec-Anforderung | Tickets |
| --- | --- |
| Graphical background admission | 01, 02, 11, 12, 13 |
| PRD decomposition within the work mandate | 12, 13, 14 |
| Preserve the submitted issue source | 11, 12, 13, 14 |
| Execution is independent of the observing client | 02, 09, 14 |
| Submissions and run relationships are database-backed | 01, 02, 11, 12, 13, 15 |
| The pilot exercises the server and separate human clients | 01 (Implementierung/lokale Abnahme), 03, 04, 05, 16 (einschließlich Mehrrechnertest aus 01) |
| Workflow and persisted run inspection | 02, 03, 15 |
| Complete graphical human operation | 06, 07, 08, 10 |
| Interactive human approval in the GUI | 10 |
| Local-agent Handover remains an independent access path | 04, 07, 08 |
| Automatically open the local agent through a Workstation Client | 04, 05, 10 |
| Automatic local diagnosis precedes human-directed intervention | 04, 07 |
| All participating agent work joins the central lifecycle history | 03, 04, 12, 13, 15 |
| Distributed history synchronization exposes completeness | 03, 05, 15 |

Quellen der allgemeinen Pilotverträge und der aktuellen Erweiterung bleiben die bestehende Pilot-PRD, Domain-Begriffe, ADRs und die vollständige Spezifikation dieses Changes. Die Akzeptanzkriterien der Entwürfe formulieren diese eigenständig und verwenden keine instabilen Implementierungsdateipfade.

## Veröffentlichung

Veröffentlicht gemäß lokaler Tracker-Konvention unter: `.scratch/agent-framework-operator-gui/issues/`, eine Datei je Ticket, `Status: ready-for-agent`, mit Nummern/Titeln der tatsächlichen Blocker. Der Feature-Einstieg verweist auf die bestehende maßgebliche Spezifikation, statt eine konkurrierende Anforderungskopie einzuführen. Bestehendes Pilot-Issue 14 und dessen offener Abnahme-Change bleiben unverändert.

Die Prüfung von Ticketgröße und Abhängigkeiten ist abgeschlossen. [Tracker-Einstieg](../../../.scratch/agent-framework-operator-gui/README.md) und [Spezifikationseinstieg](../../../.scratch/agent-framework-operator-gui/spec.md) führen zu den veröffentlichten Tickets und den maßgeblichen Quellen. Die Implementierung und die direkte Abnahme stehen aus.
