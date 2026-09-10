# 12: Unvollständige Evidence korrigieren und den Run konvergieren

**What to build:** Ein implementierter Draft-PR mit schema-valider, aber semantisch unvollständiger Evidence erhält eine begrenzte Nacherfassung und endet anschließend entweder evidence-bereit oder explizit blockiert, ohne weitere Repositoryarbeit festzuhalten.

**Blocked by:** 11: Einen Draft-PR mit ausführbarer Evidence erzeugen

**Status:** ready-for-agent

- [ ] Ein kontrolliertes Worker-Ergebnis ist strukturell gültig, lässt aber mindestens eine erforderliche Request-, Response-, Repeat-, Read-back- oder Screenshot-Phase aus.
- [ ] Die Evidence-Qualification unterscheidet strukturelle Gültigkeit von fachlicher Vollständigkeit und veröffentlicht die exakt fehlenden Phasen.
- [ ] Fehlende Evidence startet eine nummerierte, begrenzte Capture-/Correction-Aktivität und nicht still eine neue Codeimplementierung.
- [ ] Die Nacherfassung verwendet denselben qualifizierbaren Head und verändert Quellcode oder Branch nicht.
- [ ] Erfolgreich nacherfasste Evidence wird redigiert, head-gebunden und über PR sowie Operator-Oberfläche nachlesbar.
- [ ] Kann die Evidence nicht innerhalb der Grenze erfasst werden, endet der Run mit konkreter Human Request oder explizitem Blockzustand.
- [ ] Der terminale Zustand entfernt aktive Projektionen und gibt die Repository-Serialisierung nach Policy frei; es verbleibt kein dauerhaftes `agent-running`.
- [ ] Originalergebnis, Qualification-Ablehnung und Correction-Ergebnis bleiben als getrennte, korrelierte Beobachtungen erhalten.

## Session lesson

Der ProBara-Run blieb nach `missing_direct_observation` aktiv und blockierte Nachfolger. Dieser Slice macht Evidence-Recovery und terminale Zustandskonvergenz zu demselben Abnahmefall.
