# 02: Eingereichtes Issue als erste Hintergrundaktivität starten

**What to build:** Der Mensch startet sein eingegebenes Issue über die GUI; der Server erzeugt den zugehörigen Run, führt den ersten realen Agentenschritt aus und zeigt dessen Status und Ergebnis in einer einfachen Run-Ansicht.

**Blocked by:** 01: GitHub Issue eingeben und gespeicherte Einreichung wiederfinden.

**Status:** ready-for-agent

- [ ] Der Startweg verbindet die vorhandene Aufnahme mit Run-Erzeugung und persistierter Disposition; eine eingegebene neue Quelle lässt sich in einer Startaktion aufnehmen und ausführen. Eine bereits gespeicherte Einreichung kann ebenfalls gestartet werden, ohne einen manuellen Run oder Worker-Auftrag anzulegen.
- [ ] Die vorhandene zentrale Worker-/Agentenintegration führt automatisch mindestens einen realen agentischen Verarbeitungsschritt aus. Run, Einreichung, Aktivität, Versuch und tatsächliche Session sind dauerhaft korreliert; beobachtbare Nachrichten, Toolaufrufe/-ergebnisse und Artefakte werden über die bestehende zentrale History-Grenze erhalten.
- [ ] Eine einfache Run-Statusansicht zeigt den durch die Eingabe erzeugten Run als wartend, tatsächlich laufend, abgeschlossen oder konkret fehlgeschlagen und macht das Ergebnis beziehungsweise den Fehler des ersten Schritts lesbar. Ein HTTP-Erfolg oder animierter Status ohne echte Ausführung genügt nicht.
- [ ] Der Schritt läuft unabhängig von Browser, startendem Terminal oder Codex-Haupttask. Erneutes Öffnen zeigt denselben Run; doppelte Startzustellung erzeugt keinen zweiten Run oder zweiten logischen Agentenschritt.
- [ ] Berechtigung, Arbeitsmandat und vorhandene Ausführungsvoraussetzungen werden vor Start geprüft. Die minimale Startanbindung erhält die bestehenden CLI-/Run-/Dossier-Verträge; sie setzt noch keinen neuen Graph-Renderer voraus.
- [ ] Der direkte Nachweis reicht eine Quelle über die GUI ein, startet sie, schließt den Browser und liest später das reale Ergebnis sowie einen kontrolliert erzeugten Fehler zurück. Die vollständige automatische Evidence-/Review-/Reparaturkette ist eine spätere Erweiterung dieses funktionierenden Starts.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
