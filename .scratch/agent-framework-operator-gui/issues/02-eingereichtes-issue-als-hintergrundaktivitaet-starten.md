# 02: Eingereichtes Issue als erste Hintergrundaktivität starten

**What to build:** Der Mensch startet sein eingegebenes Issue über die GUI; der Server erzeugt den zugehörigen Run, führt den ersten realen Agentenschritt aus und zeigt dessen Status und Ergebnis in einer einfachen Run-Ansicht.

**Blocked by:** 01: GitHub Issue eingeben und gespeicherte Einreichung wiederfinden.

**Status:** resolved

- [x] Der Startweg verbindet die vorhandene Aufnahme mit Run-Erzeugung und persistierter Disposition; eine eingegebene neue Quelle lässt sich in einer Startaktion aufnehmen und ausführen. Eine bereits gespeicherte Einreichung kann ebenfalls gestartet werden, ohne einen manuellen Run oder Worker-Auftrag anzulegen.
- [x] Die vorhandene zentrale Worker-/Agentenintegration führt automatisch mindestens einen realen agentischen Verarbeitungsschritt aus. Run, Einreichung, Aktivität, Versuch und tatsächliche Session sind dauerhaft korreliert; beobachtbare Nachrichten, Toolaufrufe/-ergebnisse und Artefakte werden über die bestehende zentrale History-Grenze erhalten.
- [x] Eine einfache Run-Statusansicht zeigt den durch die Eingabe erzeugten Run als wartend, tatsächlich laufend, abgeschlossen oder konkret fehlgeschlagen und macht das Ergebnis beziehungsweise den Fehler des ersten Schritts lesbar. Ein HTTP-Erfolg oder animierter Status ohne echte Ausführung genügt nicht.
- [x] Der Schritt läuft unabhängig von Browser, startendem Terminal oder Codex-Haupttask. Erneutes Öffnen zeigt denselben Run; doppelte Startzustellung erzeugt keinen zweiten Run oder zweiten logischen Agentenschritt.
- [x] Berechtigung, Arbeitsmandat und vorhandene Ausführungsvoraussetzungen werden vor Start geprüft. Die minimale Startanbindung erhält die bestehenden CLI-/Run-/Dossier-Verträge; sie setzt noch keinen neuen Graph-Renderer voraus.
- [x] Der direkte Nachweis reicht eine Quelle über die GUI ein, startet sie, schließt den Browser und liest später das reale Ergebnis sowie einen kontrolliert erzeugten Fehler zurück. Die vollständige automatische Evidence-/Review-/Reparaturkette ist eine spätere Erweiterung dieses funktionierenden Starts.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.

### 2026-09-14 — Implementierung und direkte lokale Verifikation

Implementiert auf `codex/operator-gui-issue-02` aus dem abgenommenen Stand
`a77418a`, innerhalb des aktiven OpenSpec-Changes `add-agent-framework-operator-gui`.
Neue und gespeicherte GitHub-Einreichungen starten atomar einen Run mit dauerhafter
Disposition. Ein unabhängiger Worker führt die echte Anforderungsanalyse aus;
GUI und zentrale History erhalten Ergebnis, tatsächliche Session, Nachrichten,
Tools und Artefakte. Ein abgeschlossener erster Schritt bedeutet abgeschlossene
Analyse. Die vollständige Implementierungskette gehört zu Ticket 09.

Der reale Nachweis verwendet `paradox123/probare-crm#4`, Chrome und den gepinnten
Codex-Runtime: Browser und API wurden vor Ausführung geschlossen, der Worker
überlebte seinen beendeten Startprozess (PPID 1), und ein neuer Browser las später
denselben Run samt Ergebnis. Ein kontrollierter Adapterausfall wird ebenfalls
nach Neustart lesbar angezeigt. Zusätzliche Tests beweisen die Wiederaufnahme
verspäteter Antworten nach Timeout und Worker-Ausfall ohne zweite logische Arbeit.

Finale Gesamtregression: **218 Tests, 194 bestanden, 24 optionale Tests
übersprungen**. Die relevanten realen GitHub-/Codex-Nachweise wurden separat
aktiviert und bestanden. Standards-Review: **0 offene Findings**; Spec-Review:
**0 offene Findings**. Strikte OpenSpec-Validierung und Build sind grün.

Die [Abnahmeübersicht mit Belegen](../../../openspec/changes/archive/2026-09-14-add-agent-framework-background-start/issue-02-evidence.md)
ordnet jedem Kriterium erwartetes Verhalten, beobachtetes Ergebnis und Nachweis zu;
das [Review](../../../openspec/changes/archive/2026-09-14-add-agent-framework-background-start/issue-02-review.md)
dokumentiert auch die behobenen Befunde. Status `resolved` bezeichnet die
implementierte und lokal verifizierte Ticketscheibe. Azure bleibt auf Ticket 01;
die verteilte Gesamtabnahme bleibt in Ticket 16 offen.

### 2026-09-14 — Nutzerabnahme und Abschluss

Der Nutzer akzeptiert Ticket 02 nach dem erneut ausgeführten direkten Nachweis:
5/5 Tests bestanden, einschließlich echter GitHub-/Codex-Hintergrundanalyse,
lesbarem kontrolliertem Ausfall, parallelen Starts und Wiederaufnahme nach Timeout
beziehungsweise Worker-Abbruch. Er beauftragt Archivierung, Commit, Push und Merge
nach `main` sowie Bereinigung des erledigten Arbeitszweigs.

Der akzeptierte Umfang wird als
[add-agent-framework-background-start](../../../openspec/changes/archive/2026-09-14-add-agent-framework-background-start/proposal.md)
archiviert. Der GUI-Sammelchange bleibt für die offenen Tickets 03–16 aktiv.
