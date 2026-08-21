# 03: Einen Draft-PR mit belastbarer Evidence erzeugen

**What to build:** Nach einer erfolgreichen Implementierung entsteht ein Draft-Pull-Request, dessen Body jedes Akzeptanzkriterium mit direkter, commit-genauer und redigierter Verhaltens-Evidence belegt.

**Blocked by:** 02: Ein Issue mit Codex im isolierten Worktree implementieren

**Covers:** US 53-60

**Status:** ready-for-agent

- [ ] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] Die Implementierung wird committed und gepusht und erzeugt genau einen Draft-PR fuer das geclaimte Issue.
- [ ] Der PR-Body enthaelt eine Matrix aller Akzeptanzkriterien mit Verdict, beobachteter Schnittstelle, erwartetem Ergebnis und konkretem Beweis.
- [ ] REST-Evidence umfasst Request, relevante Response und fachlichen Read-back; UI-Evidence umfasst ausgefuehrte Interaktionen und entscheidende Screenshots; Recovery- und Idempotenz-Evidence umfasst Neustart beziehungsweise Wiederholung und die danach beobachtete Wirkung.
- [ ] Evidence fuer ein negatives Gate beweist sowohl die begruendete Ablehnung oder Blockierung als auch das Ausbleiben der verbotenen fachlichen Nebenwirkung ueber die oeffentliche Schnittstelle.
- [ ] Evidence fuer Hintergrundarbeit beweist das schliesslich beobachtbare fachliche Ergebnis ueber die oeffentliche Schnittstelle; Enqueue-Erfolg, Prozessstart oder Logmeldung allein reichen nicht aus.
- [ ] Build, Prozessstart, Containerstatus, Healthcheck, nackter `2xx`-Status, unkorrelierte Logbehauptung und statischer Ausgangsscreenshot werden als alleinige Evidence abgelehnt.
- [ ] Entscheidende Screenshots, kompakte REST-Ausschnitte und korrelierte Logs werden soweit technisch moeglich direkt in den PR-Body eingebettet, statt nur auf Rohartefakte zu verlinken.
- [ ] Evidence und Verdicts sind an den aktuellen PR-Head gebunden; Secrets, Tokens, personenbezogene Daten und irrelevante Payload-Inhalte werden vor Branch-, Log- und PR-Ausgabe entfernt.
- [ ] Ein Verhaltenstest erzeugt den PR ueber den primaeren System-Seam und prueft sowohl ausreichende als auch bewusst unzureichende Evidence-Pakete.
