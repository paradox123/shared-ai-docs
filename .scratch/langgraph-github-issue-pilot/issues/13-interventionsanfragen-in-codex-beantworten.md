# 13: Interventionsanfragen in Codex beantworten und denselben Lauf fortsetzen

**What to build:** Der ansonsten autonome GitHub-Issue-Pilot setzt seine bestehende Interrupt-Policy in Implementierung, Review und Findings-Behebung einheitlich durch, macht eine erforderliche menschliche Entscheidung als beantwortbare Codex-Session sichtbar und setzt nach Daniels Antwort denselben dauerhaften LangGraph-Lauf ohne doppelte Wirkungen fort.

**Builds on:** 02: Ein Issue mit Codex im isolierten Worktree implementieren; 04: Den PR durch drei unabhaengige Reviews verifizieren; 05: Review-Fehler automatisch beheben und begrenzen; 06: Human-Feedback im bestehenden Run weiterbearbeiten; 08: Workflows nach Prozessabbruch fortsetzen; 11: Lokalen Piloten unter macOS automatisch betreiben

**Status:** ready-for-agent

- [ ] Vor der Implementierung beschreibt ein neuer kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] Die bestehende Interrupt-Policy bleibt autoritativ und wird nicht erweitert oder neu interpretiert: Eine widerspruechliche oder unvollstaendige Produktentscheidung, materielle Scope-Erweiterung, fehlender Zugang zu einer menschlich bedienbaren Oberflaeche, unvermeidbare manuelle Evidence oder die bereits definierte Erschoepfung automatischer Behebungsrunden unterbricht den Lauf; kleine reversible Implementierungs- und Darstellungsdetails bleiben autonom.
- [ ] Initiale Implementierung, unabhaengige Reviews und Findings-Behebung koennen eine schema-validierte `Interventionsanfrage` erzeugen. Der Worker synthetisiert die fehlende Produktentscheidung nicht und laeuft nach erkanntem Interventionsbedarf nicht unbegrenzt weiter.
- [ ] Eine Interventionsanfrage enthaelt in redigierter Form mindestens Repository und Issue, dauerhafte Run- und Phasenidentitaet, betroffene Rolle, Worktree beziehungsweise aktuellen PR-Head, Klassifikation, konkretes Problem, die benoetigte Entscheidung oder menschliche Handlung, vorhandene Optionen mit Auswirkungen, eine begruendete Agentenempfehlung und die bis dahin erhaltenen Findings beziehungsweise Ergebnisse.
- [ ] Der Pilot persistiert die Interventionsanfrage vor dem menschlichen Handoff, pausiert nur den betroffenen LangGraph-Lauf und bewahrt Assignment, Worktree, Branch, Pull Request, Head, Evidence, Review-, Repair- und Recovery-Korrelationen. Er erzeugt weder einen zweiten Run noch einen zweiten Worktree oder Pull Request.
- [ ] Die Interventionsanfrage wird in der Codex-App als eindeutig benannte, sichtbare und beantwortbare Session dargestellt. Daniel muss das Problem nicht aus SQLite, Rollout-Dateien, Prozesslisten oder Hintergrundlogs rekonstruieren.
- [ ] Daniels Antwort wird dauerhaft genau der offenen Interventionsanfrage zugeordnet. Der Pilot setzt danach denselben Run im vorhandenen Worktree und in der betroffenen Workflow-Phase fort; die Antwort konfiguriert den Workflow nicht neu und autorisiert keine Arbeit ausserhalb des bestehenden Arbeitsmandats.
- [ ] Wenn die Antwort einen neuen Implementierungs- oder PR-Head erzeugt, werden deterministische Verifikation und alle erforderlichen unabhaengigen Reviews fuer genau diesen Head frisch ausgefuehrt. Eine beeinflusste oder veraltete Review-Session qualifiziert den Head nicht.
- [ ] Wiederholte App-Zustellung, erneutes Antworten, Prozessneustart oder eine verspaetete korrelierte Delivery fuehren weder zu einer zweiten Anwendung derselben Antwort noch zu doppelten externen Wirkungen. Eine bereits beantwortete Interventionsanfrage bleibt als Historie sichtbar und ist nicht erneut beantwortbar.
- [ ] Die Codex-Anbindung verwendet eine unterstuetzte stabile Oberflaeche. Der bestehende Ausschluss des experimentellen Codex `app-server` und `exec-server` wird nicht stillschweigend aufgehoben; fehlt eine geeignete stabile Oberflaeche, meldet die Umsetzung diesen technischen Blocker, statt die Sicherheits- oder Persistenzgrenzen zu schwaechen.
- [ ] Die direkte End-to-End-Verifikation legt ein neues, eindeutig als Test markiertes Dummy-Issue im echten `probare-crm`-Backlog an, startet es ueber den normalen produktiven GitHub-, Cloudflare- und Pilot-Pfad und loest darin deterministisch eine Interventionsanfrage aus.
- [ ] Der Verhaltensnachweis zeigt durch die Codex-App, dass die zum Dummy-Issue gehoerende Session sichtbar ist und den entscheidungsrelevanten Kontext enthaelt. Daniel beantwortet die Anfrage dort; anschliessend beweisen Workflow-Read-back und produktive Korrelationen, dass genau derselbe Run ohne zweiten Worktree oder doppelte Wirkung fortgesetzt wurde.
- [ ] Der UI-Nachweis enthaelt eine entscheidende Screenshot-Referenz der sichtbaren Codex-Session. Der Workflow-Nachweis enthaelt den Run, die Interventionsanfrage, die einmalig zugeordnete Antwort und den fortgesetzten Zustand ueber die oeffentliche Read-back-Oberflaeche; reine Logs, Prozessstatus oder Datenbankzeilen genuegen nicht.
- [ ] Das Dummy-Issue wird nach dem Nachweis kontrolliert geschlossen. Die Verifikation merged oder deployt nichts und hinterlaesst keine laufende Testarbeit.
- [ ] ProBara CRM Issue #2, sein bestehender Pilot-Run, seine Codex-Sessions und sein Worktree werden weder als Reproduktionsfall noch als Fixture oder Evidence verwendet oder veraendert. Der dort separat bearbeitete Pilot-Bug ist nicht Teil dieses Issues.

## Out of scope

- Den separaten Pilot-Bug des bestehenden ProBara CRM Issue-#2-Laufs diagnostizieren oder beheben.
- Die fachlichen Trigger der bestehenden Interrupt-Policy erweitern.
- Normale autonome Worker- oder Review-Sessions dauerhaft in der Codex-App spiegeln.
- Merge, Deployment, Release oder Produktionsaenderungen ausserhalb des kontrollierten Dummy-Issue-Nachweises.

## Direct verification

1. Einen neuen, eindeutig markierten Dummy-Issue im `probare-crm`-Backlog anlegen und ueber den normalen produktiven Pfad autorisieren.
2. Den Dummy-Auftrag so begrenzen, dass er deterministisch eine bereits von der Interrupt-Policy erfasste Produktentscheidung benoetigt, ohne eine reale Produktfunktion oder den Issue-#2-Lauf zu veraendern.
3. In der Codex-App die sichtbare Interventions-Session mit korrektem Issue-, Run-, Phasen- und Entscheidungskontext oeffnen und per Screenshot belegen.
4. Die Entscheidung in dieser Session beantworten.
5. Ueber den oeffentlichen Workflow-Read-back und die produktiven Korrelationen nachweisen, dass dieselbe Antwort genau einmal uebernommen und derselbe LangGraph-Lauf im vorhandenen Worktree fortgesetzt wurde.
6. Das Dummy-Issue ohne Merge oder Deployment kontrolliert schliessen und bestaetigen, dass keine Testarbeit aktiv bleibt.

## Comments

- Der Issue entstand aus der Analyse eines unsichtbaren Interventionsbedarfs. Der bestehende Issue-#2-Lauf ist ausdruecklich kein Akzeptanz- oder Reproduktionsfall, weil sein separater Pilot-Bug in einer anderen Session bearbeitet wird.
