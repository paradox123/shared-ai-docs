# 02: Geprüften Wiki-Stand auf dem Mac aktivieren

**What to build:** Ein erfolgreich geprüfter Release-Kandidat kann automatisch die bisherige lokale LLM-Wiki-Installation ersetzen. Der Betreiber kann die tatsächlich aktive Version erkennen; bei fehlgeschlagener Übernahme bleibt der bisherige funktionsfähige Stand nutzbar.

**Blocked by:** 01 — Upstream-Release reproduzierbar installieren und prüfen.

**Status:** resolved

- [x] Der öffentliche Updateaufruf aktiviert ausschließlich den konkreten Kandidaten, dessen Build und sämtliche erforderlichen Tests erfolgreich sind; eine nachträgliche Änderung des Kandidaten erfordert erneute Prüfung.
- [x] Die Übernahme benötigt keine erneute menschliche Review-, Merge- oder Deployment-Freigabe. Ungeprüfte oder fehlgeschlagene Kandidaten können die aktive Installation nicht ersetzen.
- [x] Nach der Umschaltung belegen die tatsächlich genutzte Release-/Commit-Identität und ein begrenzter öffentlicher Wiki-Funktionsaufruf die erfolgreiche lokale Aktivierung; ein Merge oder ein Versionsmanifest allein genügt nicht.
- [x] Bestehende Wissensseiten, gespeicherte Synthesen und ihr Zustand bleiben erhalten. Falls das Release eine Datenmigration benötigt, umfasst die Wiederherstellbarkeit auch die betroffenen Daten.
- [x] Bei fehlgeschlagener Umschaltung oder Aktivierungsprüfung wird der bisherige funktionsfähige Stand beibehalten beziehungsweise wiederhergestellt; das Ergebnis meldet den Fehler und den weiterhin aktiven Stand eindeutig.
- [x] Wiederholte Übernahme desselben unveränderten Releases ist ein No-op. Gleichzeitige Updates oder laufende Wiki-Nutzung verursachen keine gemischte Runtime und keine überlappenden Zustandsänderungen.
- [x] Erfolgreiche Aktivierung, No-op und gezielt ausgelöster Aktivierungsfehler werden auf dem Mac über den öffentlichen Aufruf nachgewiesen. Wissenspflege und deren Scheduler werden dabei nicht verändert.

## Umsetzung und Verhaltensnachweis

Implementiert auf `codex/update-llm-wiki-releases` mit `1f68c57`, `c6b69ba` und `2ae80c5`. [Abnahme](../../../contextual-llm-wiki/evidence/release-activation-02.md), [maschinenlesbare Ergebnisse](../../../contextual-llm-wiki/evidence/release-activation-02-results.json), [Review](../../../contextual-llm-wiki/evidence/release-activation-02-review.md).

`wiki update --candidate PATH` aktiviert nur vollständig qualifizierte, unveränderte Kandidaten. Der Feature-Worktree verwendet nach realer Aktivierung v1.3.0 / `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb` aus einer eigenen Runtime-Kopie. No-op, erhaltener und weiterpflegbarer Zustand, gezielter Fehler samt Rückfall, Abbruchwiederherstellung und Serialisierung sind nachgewiesen. Typecheck, 61 CLI-, 59 Upstream-, acht Wartungshelfer- und 21 Release-Tests sind grün; keine offenen Review-Findings.

Produktive Wissensdaten, Konfiguration und Schedulerdefinition sind hashgleich erhalten. Der produktive Scheduler verwendet weiterhin seinen bisherigen Einstieg; aktiviert wurde der öffentliche Einstieg des Feature-Worktrees. Der reale Release benötigt keine Produktivmigration; inkompatible Zustandsverträge werden zurückgewiesen, eine künftig nötige Migration braucht zuvor einen gesicherten, rücksetzbaren Vertrag. Ticket 03 (Release-Erkennung) bleibt offen. Der gemeinsame Betriebs-Change wird nicht archiviert.

## Comments

Daniel hat die Implementierung am 13.09.2026 ausdrücklich akzeptiert und Spec-Abschluss, Commit und Push beauftragt. Ticket 02 bleibt `resolved`; sein erfüllter Vertrag ist unter [activate-qualified-wiki-releases](../../../openspec/changes/archive/2026-09-13-activate-qualified-wiki-releases/proposal.md) separat abgeschlossen und kanonisch übernommen. Ticket 03 und offene Wissenspflege bleiben im Betriebs-Change.
