

## Implement Spec mit OpenSpec

Implementiere diese Spec-Änderung im OpenSpec-Modus:

1. **Pre-Implementation Analysis**: 
   - Prüfe die Spec auf formale Marker (`[MISSING]`, `[DECISION]`, `[BLOCKED]`)
   - **Inhaltliche Analyse**: Lies die betroffene Codebase, verstehe die aktuellen Implementierungen
   - Validiere ob Spec-Anforderungen realistisch und umsetzbar sind im aktuellen Kontext
   - Prüfe auf logische Inkonsistenzen zwischen Spec-Requirements und existierendem Code
   - Stoppe bei blockierenden Widersprüchen und frage nach

2. **Scope Contract**: Erstelle expliziten Scope Contract basierend auf **Spec-Anforderungen UND Code-Realität** mit in/out scope, acceptance targets, und planned verification bevor du editierst.

3. **Execution Mode**: Nutze `openspec` mode - erstelle/update einen OpenSpec Change für diesen Change mit Proposal, Tasks, und Spec Deltas aligned zum Scope Contract.

4. **Implementation**: Implementiere gemäß Definition of Ready (DoR) aus doc-workflow.md. Nutze TDD wo sinnvoll für testbare Komponenten.

5. **Verification**: Führe ALLE Verification Commands aus der Spec aus. Nutze `check-build-watcher` für NCG-Backend Build-Monitoring. Jedes Command muss `ran`/`failed`/`blocked` Status erhalten.

6. **Definition of Done**: Change ist erst DONE wenn alle DoD-Kriterien erfüllt sind:
   - Alle Spec-Verification-Commands sind grün
   - Runtime-Validierung erfolgreich (z.B. docker compose + health checks)
   - OpenSpec Tasks sind complete (keine `[BLOCKED]` als done markiert)
   - Acceptance criteria mit Evidence belegt

7. **Scope Discipline**: Avoid scope creep - implementiere nur was im aktuellen Change definiert ist. Keine opportunistischen Refactorings außerhalb des Scope.

8. **Final Verdict**: Liefere `READY` oder `NOT READY` Verdict mit vollständiger Evidence (changed files, verification checklist, open risks).

Unterbreche erst wenn komplett fertig implementiert ODER blocker/open items auftreten die vorher nicht sichtbar waren.
Nutze den skill spec-change-delivery.

## Implement Spec (Direct Mode)

Implementiere diese Spec-Änderung im Direct-Modus (ohne OpenSpec):

1. **Pre-Implementation Analysis**: 
   - Prüfe die Spec auf formale Marker (`[MISSING]`, `[DECISION]`, `[BLOCKED]`)
   - **Inhaltliche Analyse**: Lies die betroffene Codebase, verstehe die aktuellen Implementierungen
   - Validiere ob Spec-Anforderungen realistisch und umsetzbar sind im aktuellen Kontext
   - Prüfe auf logische Inkonsistenzen zwischen Spec-Requirements und existierendem Code
   - Stoppe bei blockierenden Widersprüchen und frage nach

2. **Scope Contract**: Erstelle expliziten Scope Contract basierend auf **Spec-Anforderungen UND Code-Realität** mit in/out scope, acceptance targets, und planned verification bevor du editierst.

3. **Execution Mode**: Nutze `direct` mode - implementiere direkt aus dem Scope Contract ohne OpenSpec Change zu erstellen.

4. **Implementation**: Implementiere gemäß Definition of Ready (DoR) aus doc-workflow.md. Nutze TDD wo sinnvoll für testbare Komponenten.

5. **Verification**: Führe ALLE Verification Commands aus der Spec aus. Nutze `check-build-watcher` für NCG-Backend Build-Monitoring. Jedes Command muss `ran`/`failed`/`blocked` Status erhalten.

6. **Definition of Done**: Change ist erst DONE wenn alle DoD-Kriterien erfüllt sind:
   - Alle Spec-Verification-Commands sind grün
   - Runtime-Validierung erfolgreich (z.B. docker compose + health checks)
   - Acceptance criteria mit Evidence belegt

7. **Scope Discipline**: Avoid scope creep - implementiere nur was im aktuellen Change definiert ist. Keine opportunistischen Refactorings außerhalb des Scope.

8. **Final Verdict**: Liefere `READY` oder `NOT READY` Verdict mit vollständiger Evidence (changed files, verification checklist, open risks).

Unterbreche erst wenn komplett fertig implementiert ODER blocker/open items auftreten die vorher nicht sichtbar waren. Nutze den skill spec-change-delivery.

## Close Change

change ist akzeptiert, schließe spec/open-spec


## Start Agent Delivery Workflow Regression Test

Starte einen echten Regressionstest fuer den Agent Delivery Workflow.

Wichtig:
- Diese Session ist nur Kontrollsession.
- Der eigentliche Workflow muss in einer separaten, vom Agent Delivery Session Launcher gestarteten Session laufen.
- Keine Single-Session-Simulation.
- Kein `run-mock-e2e-checks.sh` als Ersatz.
- Keine Abkuerzungen.
- Der Test gilt nur als gruen, wenn echte Launcher-/Session-Evidence fuer Parent und Child-Sessions existiert.

Aufgabe:
1. Bereite einen frischen Test-Parent fuer den Agent Delivery Workflow vor.
2. Starte den Workflow ueber `skills-repo/tools/AgentDeliverySessionLauncher.cs` mit `--mode launch --agent codex`.
3. Die gestartete Parent-Session muss aus dem Parent:
   - ein Orchestration Pack erzeugen,
   - fuenf Child Specs erzeugen,
   - fuenf Child Handoffs erzeugen,
   - fuer die Child-Arbeit wiederum `AgentDeliverySessionLauncher.cs --mode launch --agent codex` verwenden.
4. Jeder Child muss in einer eigenen Launcher-Session laufen.
5. Jeder Child muss sein Readiness-/Handoff-Gate bestehen, bevor er delivered.
6. Jeder Child schreibt genau seinen eigenen Wert in `target/output/count.txt`:
   - Child 1 schreibt `1`
   - Child 2 schreibt `2`
   - Child 3 schreibt `3`
   - Child 4 schreibt `4`
   - Child 5 schreibt `5`
7. Am Ende muss `target/output/count.txt` exakt enthalten:

1
2
3
4
5

8. Pruefe die Evidence:
   - Parent Launcher Evidence existiert.
   - Child Launcher Evidence fuer alle fuenf Childs existiert.
   - Alle Childs haben `final_status: ran-target`.
   - Alle Childs haben `closeout_status: closed`.
   - Finale Closeout Summary hat `overall_status: pass`.

Wenn der Prozess irgendwo fehlschlaegt oder haengt:
- Stoppe den Test.
- Beende keine fremden Prozesse, aber beende von dir gestartete haengende Testprozesse sauber.
- Melde exakt:
  - an welchem Child / Schritt der Workflow gescheitert ist,
  - welche Evidence existiert,
  - welche Evidence fehlt,
  - welchen Inhalt `count.txt` zu diesem Zeitpunkt hat.
- Finaler Verdict muss dann `NOT READY` sein.

Berichte am Ende knapp:
- Run-Verzeichnis
- gestartete Launcher-Sessions
- Status pro Child
- finaler `count.txt` Inhalt
- finale Verdict: `READY` oder `NOT READY`

## ToDo NCG

Login per KFZ Kennzeichen
- Textbox auf Login Bildschirm ziehen
- Textbox erlaubt Email und KFZ 