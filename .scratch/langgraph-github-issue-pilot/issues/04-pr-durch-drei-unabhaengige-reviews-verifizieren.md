# 04: Den PR durch drei unabhaengige Reviews verifizieren

**What to build:** Ein Draft-PR wird unabhaengig auf Anforderungserfuellung, Codequalitaet und Architektur geprueft und nur bei drei erfolgreichen anwendbaren Verdicts als bereit fuer Daniels Review markiert.

**Blocked by:** 03: Einen Draft-PR mit belastbarer Evidence erzeugen

**Covers:** US 39-44, 61, 63

**Status:** ready-for-agent

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Requirements-, Code- und Architekturreview laufen mit frischem, voneinander unabhaengigem Kontext und ausschliesslich lesendem Zugriff auf denselben PR-Head.
- [x] Jeder Reviewer liefert ein schema-validiertes `pass`, `fail` oder `not_applicable` mit Begruendung und konkreten Findings; Requirements Review ist immer anwendbar.
- [x] Requirements Review gleicht Anforderungen, Implementierung und Evidence ab; Code Review prueft Repository-Standards und relevante Code-Smells; Architekturreview prueft Domaenensprache, ADRs, Module, Interfaces, Seams, Adapter und Testoberflaechen.
- [x] Regulaere Reviews verwenden GPT-5.6 Terra mit `xhigh` und die vorgesehenen Matt-Pocock-Skills; Modell-, Reasoning- und Skill-Metadaten bleiben am Verdict nachvollziehbar.
- [x] Requirements- und Code-Review verwenden die getrennten Achsen von `code-review`; Architekturreview verwendet `codebase-design` und `domain-modeling`. Contract-Tests beweisen dieses Routing fuer jede Review-Achse.
- [x] Ein einziges `fail` blockiert die Freigabe; nur wenn alle anwendbaren Achsen bestehen, erhaelt der aktuelle PR-Head `verified` und `awaiting-review` und verliert `agent-running`.
- [x] Keiner der Reviewer darf den Branch veraendern, Findings selbst beheben, mergen, deployen oder eine Produktentscheidung synthetisieren.
- [x] Ein Systemtest beweist getrennte Reviewergebnisse, Fail-Closed-Aggregation und die erfolgreiche GitHub-Projektion ausschliesslich ueber oeffentliche Beobachtungsflaechen.

## Implementation Evidence

Implemented through archived OpenSpec change `2026-08-23-verify-draft-pr-with-independent-reviews`. Criterion-level evidence is recorded in `openspec/changes/archive/2026-08-23-verify-draft-pr-with-independent-reviews/implementation-evidence.md`.
