# 03: Einen Draft-PR mit belastbarer Evidence erzeugen

**What to build:** Nach einer erfolgreichen Implementierung entsteht ein Draft-Pull-Request, dessen Body jedes Akzeptanzkriterium mit direkter, commit-genauer und redigierter Verhaltens-Evidence belegt.

**Blocked by:** 02: Ein Issue mit Codex im isolierten Worktree implementieren

**Covers:** US 53-60

**Status:** ready-for-agent

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Die Implementierung wird committed und gepusht und erzeugt genau einen Draft-PR fuer das geclaimte Issue.
- [x] Der PR-Body enthaelt eine Matrix aller Akzeptanzkriterien mit Verdict, beobachteter Schnittstelle, erwartetem Ergebnis und konkretem Beweis.
- [x] REST-Evidence umfasst Request, relevante Response und fachlichen Read-back; UI-Evidence umfasst ausgefuehrte Interaktionen und entscheidende Screenshots; Recovery- und Idempotenz-Evidence umfasst Neustart beziehungsweise Wiederholung und die danach beobachtete Wirkung.
- [x] Evidence fuer ein negatives Gate beweist sowohl die begruendete Ablehnung oder Blockierung als auch das Ausbleiben der verbotenen fachlichen Nebenwirkung ueber die oeffentliche Schnittstelle.
- [x] Evidence fuer Hintergrundarbeit beweist das schliesslich beobachtbare fachliche Ergebnis ueber die oeffentliche Schnittstelle; Enqueue-Erfolg, Prozessstart oder Logmeldung allein reichen nicht aus.
- [x] Build, Prozessstart, Containerstatus, Healthcheck, nackter `2xx`-Status, unkorrelierte Logbehauptung und statischer Ausgangsscreenshot werden als alleinige Evidence abgelehnt.
- [x] Entscheidende Screenshots, kompakte REST-Ausschnitte und korrelierte Logs werden soweit technisch moeglich direkt in den PR-Body eingebettet, statt nur auf Rohartefakte zu verlinken.
- [x] Evidence und Verdicts sind an den aktuellen PR-Head gebunden; Secrets, Tokens, personenbezogene Daten und irrelevante Payload-Inhalte werden vor Branch-, Log- und PR-Ausgabe entfernt.
- [x] Ein Verhaltenstest erzeugt den PR ueber den primaeren System-Seam und prueft sowohl ausreichende als auch bewusst unzureichende Evidence-Pakete.

## Implementation Evidence

Implemented through archived OpenSpec change `2026-08-23-create-evidence-backed-draft-pr`. Criterion-level evidence is recorded in `openspec/changes/archive/2026-08-23-create-evidence-backed-draft-pr/implementation-evidence.md`.
