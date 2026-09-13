# 12: Unvollständige Evidence korrigieren und den Run konvergieren

**What to build:** Ein implementierter Draft-PR mit schema-valider, aber semantisch unvollständiger Evidence erhält eine begrenzte Nacherfassung und endet anschließend entweder evidence-bereit oder explizit blockiert, ohne weitere Repositoryarbeit festzuhalten.

**Blocked by:** 11: Einen Draft-PR mit ausführbarer Evidence erzeugen

**Status:** resolved

- [x] Ein kontrolliertes Worker-Ergebnis ist strukturell gültig, lässt aber mindestens eine erforderliche Request-, Response-, Repeat-, Read-back- oder Screenshot-Phase aus.
- [x] Die Evidence-Qualification unterscheidet strukturelle Gültigkeit von fachlicher Vollständigkeit und veröffentlicht die exakt fehlenden Phasen.
- [x] Fehlende Evidence startet eine nummerierte, begrenzte Capture-/Correction-Aktivität und nicht still eine neue Codeimplementierung.
- [x] Die Nacherfassung verwendet denselben qualifizierbaren Head und verändert Quellcode oder Branch nicht.
- [x] Erfolgreich nacherfasste Evidence wird redigiert, head-gebunden und über PR sowie Operator-Oberfläche nachlesbar.
- [x] Kann die Evidence nicht innerhalb der Grenze erfasst werden, endet der Run mit konkreter Human Request oder explizitem Blockzustand.
- [x] Der terminale Zustand entfernt aktive Projektionen und gibt die Repository-Serialisierung nach Policy frei; es verbleibt kein dauerhaftes `agent-running`.
- [x] Originalergebnis, Qualification-Ablehnung und Correction-Ergebnis bleiben als getrennte, korrelierte Beobachtungen erhalten.

## Session lesson

Der ProBara-Run blieb nach `missing_direct_observation` aktiv und blockierte Nachfolger. Dieser Slice macht Evidence-Recovery und terminale Zustandskonvergenz zu demselben Abnahmefall.


## Implementation — 2026-09-13

Auf dem ausdrücklich freigegebenen Zielbranch `main` umgesetzt, nachdem Issue 11
integriert war. Der Change
[`recover-agent-framework-evidence`](../../../../openspec/changes/recover-agent-framework-evidence/proposal.md)
trennt Schema-Validität und fehlende fachliche Phasen. Zwei nummerierte,
persistierte Capture-Runden verwenden denselben Head, ohne Codex erneut zur
Implementierung aufzurufen. Abbruch, Drift und ausgeschöpfte Nacherfassung
konvergieren mit konkretem Blocker und Repository-Freigabe; überholte native
Human Requests werden im terminalen Zustand aufgelöst.

Der kontrollierte Worker-/Provider-Durchstich führt echte REST-, Repeat-, Browser-
und Dokumentphasen aus. Ein zusätzlicher Durchstich mit echter Codex-Runtime und
nativer TUI bestätigt Publication und Request-Auflösung. Die GitHub-Grenze ist
kontrolliert; kein Live-PR oder Merge war Teil der Abnahme.

[Abnahmeübersicht mit Ergebnissen, Nachweisen und Grenzen](../../../../openspec/changes/recover-agent-framework-evidence/implementation-evidence.md)

[Standards-/Spec-Review](../../../../openspec/changes/recover-agent-framework-evidence/review.md)

[Operator-Anleitung](../../../../microsoft-agent-framework-work-package-pilot/PUBLICATION.md)

Die abschließende Gesamtsuite umfasst 180 Tests: 163 bestanden, 17 opt-in-Fälle
übersprungen, kein Fehler. Darin sind alle 35 Recovery-/Publication-Fälle enthalten.
Der echte Codex/TUI-Test besteht zusätzlich. Build und strikte OpenSpec-Validierung
bestehen; Standards- und Spec-Review haben keine offenen Befunde.
