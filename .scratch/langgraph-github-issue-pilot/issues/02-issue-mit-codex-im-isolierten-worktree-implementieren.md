# 02: Ein Issue mit Codex im isolierten Worktree implementieren

**What to build:** Ein geclaimtes Issue wird als eng begrenzter, strukturierter Auftrag an Codex uebergeben und in einem isolierten Worktree verhaltensbasiert implementiert, ohne Daniels Arbeitsverzeichnis oder andere Laeufe zu veraendern.

**Blocked by:** 01: Ein autorisiertes Issue lokal annehmen und claimen

**Covers:** US 29-38, 53

**Status:** ready-for-agent

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Vor Beginn der Codeaenderung wird fuer jedes Akzeptanzkriterium eine Evidence-Matrix mit oeffentlicher Beobachtungsflaeche, erwartetem Ergebnis und vorgesehenem Beweis erzeugt.
- [x] Der Implementierungsauftrag enthaelt nur das betreffende Issue, seine Anforderungen, den Repository-Kontext, die Evidence-Matrix und gegebenenfalls aktuelle Findings.
- [x] Fuer den Auftrag wird ein eigener Worktree angelegt; Aenderungen bleiben von Daniels Worktree und von anderen Laeufen isoliert.
- [x] Der Codex-Adapter fuehrt den Implementer nicht-interaktiv mit GPT-5.6 Terra und `xhigh` aus, routet die zum Issue-Typ passenden Matt-Pocock-Skills und zeichnet Modell, Reasoning-Stufe sowie Skill-Versionen oder Content-Hashes auf.
- [x] Eine versionierte Node-Policy weist deterministischer Control-Plane-Arbeit kein Sprachmodell, rein darstellender Arbeit GPT-5.6 Luna mit `medium`, Triage, Slicing, Implementierung, Findings-Bearbeitung und regulaeren Reviews GPT-5.6 Terra mit `xhigh` sowie ausschliesslich den definierten Eskalationen GPT-5.6 Sol mit `xhigh` zu.
- [x] Das Skill-Routing verwendet fuer Triage `triage`, fuer grosse Anforderungen `to-tickets`, fuer Features `implement` und `tdd` sowie fuer Bugs `diagnosing-bugs` und `tdd`; Contract-Tests pruefen sowohl diese Zuordnung als auch die Ablehnung einer nicht erlaubten Modell- oder Reasoning-Kombination.
- [x] Feature- und Fehlerarbeit erfolgt in beobachtbaren Red-Green-Slices; das strukturierte Worker-Ergebnis wird gegen ein versioniertes Schema validiert und dauerhaft dem Lauf zugeordnet.
- [x] Nur der Implementer erhaelt Schreibzugriff; ein ungueltiges oder fehlgeschlagenes Worker-Ergebnis veraendert weder einen anderen Worktree noch einen bestehenden Pull Request.
- [x] Der Worker-Adapter ist austauschbar und sein Contract-Test beweist Auftrag, Ergebnis, Modellwahl, Skill-Routing und Rechteprofil ohne Abhaengigkeit von einer experimentellen Codex-Server-Schnittstelle.

## Implementation Evidence

Implemented through archived OpenSpec change `implement-isolated-issue-worker`. Criterion-level evidence is recorded in `openspec/changes/archive/2026-08-22-implement-isolated-issue-worker/implementation-evidence.md`.
