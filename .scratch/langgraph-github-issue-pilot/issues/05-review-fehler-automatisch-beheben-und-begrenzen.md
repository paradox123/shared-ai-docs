# 05: Review-Fehler automatisch beheben und begrenzen

**What to build:** Fehlgeschlagene Reviews fuehren zu begrenzten, nachvollziehbaren Reparaturrunden durch denselben schreibenden Implementer und enden entweder in einem verifizierten PR oder einer klaren menschlichen Uebergabe.

**Blocked by:** 04: Den PR durch drei unabhaengige Reviews verifizieren

**Covers:** US 38, 45-52, 62

**Status:** ready-for-agent

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Findings aller fehlgeschlagenen Review-Achsen werden strukturiert aggregiert und ausschliesslich dem Implementer als neuer Reparaturauftrag uebergeben.
- [x] Nach jedem Reparaturcommit laufen deterministische Verifikation sowie Requirements-, Code- und Architekturreview fuer den neuen PR-Head vollstaendig erneut.
- [x] Pro initialem Review-Batch beginnen hoechstens drei automatische Behebungsrunden; eine vierte Runde wird auch nach einem weiteren `fail` nicht gestartet.
- [x] GPT-5.6 Sol mit `xhigh` wird nur fuer definierte materielle Architektur-, Persistenz-, Sicherheits- oder Datenmigrationseskalationen, ein strukturiertes `escalate` oder die dritte und letzte Reparaturrunde eingesetzt.
- [x] Nach drei erfolglosen Runden bleibt der Draft-PR mit Versuchen und offenen Findings erhalten und wechselt bei fehlenden oder widerspruechlichen Anforderungen zu `needs-info`, andernfalls bei nicht agentisch loesbaren Konflikten zu `ready-for-human`.
- [x] Nur echte Produktfunktion, materielle Scope-Erweiterung, fehlende Zugaenge, unvermeidbare manuelle Evidence oder ausgeschoepfte Runden unterbrechen den Lauf; kleine reversible Darstellungsdetails werden autonom entschieden.
- [x] Semantisch relevante Darstellungsfragen wie Warnungen, Einwilligungen oder fachliche Aktionen werden weiterhin als Produktentscheidung behandelt.
- [x] Systemtests beweisen erfolgreichen Repair, den Drei-Runden-Stopp und beide menschlichen Folgezustaende ueber persistierten Lauf, PR und GitHub-Projektion.

## Implementation Evidence

Implemented through archived OpenSpec change `2026-08-23-add-bounded-review-repair-rounds`. Criterion-level evidence is recorded in `openspec/changes/archive/2026-08-23-add-bounded-review-repair-rounds/implementation-evidence.md`.
