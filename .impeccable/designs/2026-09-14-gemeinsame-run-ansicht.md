# Gemeinsame Run-Ansicht — Entwurf vom 14.09.2026

Status: Designreferenz zur Diskussion, keine fachliche Abnahme oder Implementierung im Operator Client.

Der Nutzer wählte als Schwerpunkt die gemeinsame Run-Ansicht mit Status und Ergebnis und beschränkte den Entwurf auf die vorhandenen Funktionen aus Tickets 01–03. Grundlage ist die [UX/UI-Kritik](../critique/2026-09-14T15-15-44Z__index-html.md). Der Entwurf gehört zum aktiven Change `add-agent-framework-operator-gui`; er führt keine neue OpenSpec-Anforderung ein.

## Gestalterische Entscheidung

- **Aufgabe und Zielgruppe:** Ein Operator öffnet eine gespeicherte Anforderung erneut und erkennt unmittelbar den aktuellen Analysezustand und das Ergebnis. Modus: Operate.
- **Hierarchie:** Gemeinsamer Kopf mit Titel und Analysezustand; Einstieg „Ergebnis“. Die Ansichten „Verlauf“, „Dateien“ und „Anforderungen“ halten sämtliche bestehenden Informationen gezielt erreichbar. Die vollständige Quelle bestimmt nicht mehr den Weg zum Verlauf.
- **Inhalt:** Originalergebnis in Kurzansicht und aufklappbarer Abgrenzung, vier unverändert erhaltene offene Produktentscheidungen, eine genannte Abhängigkeit und acht weitere Erkenntnisse. Die Aufteilung stammt aus den aufgezeichneten Findings; sie ersetzt keine fachliche Entscheidung.
- **Bedienung:** Eine kompakte Anforderungsliste ersetzt die bisherige Kombination aus großer globaler Seitenleiste und zusätzlicher Liste. „Neu“ öffnet die Aufnahme inline. In der Verlaufansicht bleibt die Schrittauswahl beim Wechsel bestehen, einschließlich ihres Tastaturfokus. Auf Mobil stehen beide Schritte vertikal und vollständig sichtbar.
- **Visuelle Grundlage:** Vorhandene grüne Produktgestaltung, vertraute Schrift und ruhigere Gruppierung. Der Entwurf folgt der hellen oder dunklen Darstellung des Hosts. Große Ergebnisfläche, größere Beschriftungen und erreichbare Bedienflächen; keine zusätzlichen Workflowfähigkeiten aus Tickets 04–16.

## Quelle und Grenzen

Inline-Entwurf dieser Aufgabe:

`/Users/dh/.codex/visualizations/2026/09/14/01a0a070-1490-75a3-a05d-53444614d6d8/gemeinsame-run-ansicht.html`

Die Daten stammen aus `openspec/changes/add-agent-framework-operator-gui/evidence/issue-03-readable/live-workflow.json` und den beiden Ergebnisartefakten im Worktree `shared-ai-docs-operator-issue-03` (Branch `codex/operator-gui-issue-03`). Verwendet werden der aufgezeichnete Run `c8c55cd0-91bf-40f3-b685-f56b3e174a7e`, alle 22 Runereignisse, beide Artefakte und die gespeicherte Anforderungsfassung. Der vorhandene `session-content.js`-Renderer ist als Kopie eingebettet; Transport, Berechtigungen und Backend werden nicht ausgeführt.

Aufnahme und Start sind ausdrücklich lokale Beispielinteraktionen. Weitere vorhandene Zustände lassen sich über die optionalen Darstellungsoptionen des Hosts auswählen und sind als Beispiele beschriftet. Der Entwurf macht keine Aussagen über Live-Ausführung, Authentifizierung, Wiederaufnahme oder Mehrrechnerbetrieb. Er ist kein neuer Codepfad der produktiven GUI.

## Direkte Kontrolle

Eine gemeinsame Browserrunde auf Desktop (1024 × 1000) und Mobil (390 × 844), danach eine begrenzte Korrektur und Bestätigung:

| Ziel | Beobachtet |
|---|---|
| Ergebnis am Einstieg | Ergebnisbereich beginnt im Desktop-Fragment bei ca. 263 px, mobil bei ca. 368 px. Der mobile Zusammenfassungstext endet bei ca. 645 px. |
| Mobile Auswahl erkennbar | Beide Schritte nehmen die verfügbare Breite von 324 px ein; ausgewählte Analyse vollständig sichtbar. Kein horizontaler Überlauf des Fragments. |
| Tastaturorientierung | Enter wählt die Aufnahme; Fokus bleibt auf dem aktivierten Aufnahmebutton. |
| Vollständigkeit | „Alle Ereignisse“ zeigt 18 Originalereignisse der Agentensession mit 18 zunächst geschlossenen technischen Details. Normalansicht zeigt fünf lesbare Einträge. |
| Dateien | Das Ergebnisartefakt öffnet als lesbarer Inhalt, Originalinhalt bleibt aufklappbar. |
| Anforderungstext | Gespeicherte Quelle zeigt fünf Überschriften und sieben Listeneinträge. Herkunft und Originalfassung bleiben erreichbar. |
| Beispielaufnahme | „Nur aufnehmen“ zeigt „Aufgenommen“ und „Analyse starten“; der Start zeigt „Analyse wartet“. Die Ansicht kennzeichnet beide als Zustandsbeispiel und blendet das aufgezeichnete abgeschlossene Ergebnis aus. |

Die eingebettete Umgebung verhindert Formularübermittlungen. Die Beispielbuttons steuern deshalb ausschließlich lokalen Zustand, ohne Formularübermittlung. JavaScript-Syntaxprüfung bestanden. Der mechanische Detector meldet keine Musterbefunde; dies ist kein vollständiges Accessibility-Audit. Das finale Inline-Fragment benötigt keinen laufenden Vorschauprozess.

## Anschluss

Eine spätere Implementierung überträgt die bestätigte Informationsarchitektur in die vorhandene GUI und bindet ihre Statusanzeigen an die existierenden öffentlichen Antworten. Sie benötigt die üblichen Verhaltenstests und OpenSpec-Pflege im aktiven Change. Für diesen Entwurf wurde der Produktcode nicht geändert.
