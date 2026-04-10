

## Implement Spec mit OpenSpec

Implementiere diese Spec-Änderung im OpenSpec-Modus:

1. **Pre-Implementation Analysis**: 
   - Prüfe die Spec auf formale Marker (`[MISSING]`, `[DECISION]`, `[BLOCKED]`)
   - **Inhaltliche Analyse**: Lies die betroffene Codebase, verstehe die aktuellen Implementierungen
   - Validiere ob Spec-Anforderungen realistisch und umsetzbar sind im aktuellen Kontext
   - Prüfe auf logische Inkonsistenzen zwischen Spec-Requirements und existierendem Code
   - Stoppe bei blockierenden Widersprüchen und frage nach

2. **Scope Contract**: Erstelle expliziten Scope Contract basierend auf **Spec-Anforderungen UND Code-Realität** mit in/out scope, acceptance targets, und planned verification bevor du editierst.

3. **Execution Mode**: Nutze `openspec` mode - erstelle/update einen OpenSpec Change für diesen Slice mit Proposal, Tasks, und Spec Deltas aligned zum Scope Contract.

4. **Implementation**: Implementiere gemäß Definition of Ready (DoR) aus doc-workflow.md. Nutze TDD wo sinnvoll für testbare Komponenten.

5. **Verification**: Führe ALLE Verification Commands aus der Spec aus. Nutze `check-build-watcher` für NCG-Backend Build-Monitoring. Jedes Command muss `ran`/`failed`/`blocked` Status erhalten.

6. **Definition of Done**: Change ist erst DONE wenn alle DoD-Kriterien erfüllt sind:
   - Alle Spec-Verification-Commands sind grün
   - Runtime-Validierung erfolgreich (z.B. docker compose + health checks)
   - OpenSpec Tasks sind complete (keine `[BLOCKED]` als done markiert)
   - Acceptance criteria mit Evidence belegt

7. **Scope Discipline**: Avoid scope creep - implementiere nur was im aktuellen Slice definiert ist. Keine opportunistischen Refactorings außerhalb des Scope.

8. **Final Verdict**: Liefere `READY` oder `NOT READY` Verdict mit vollständiger Evidence (changed files, verification checklist, open risks).

Unterbreche erst wenn komplett fertig implementiert ODER blocker/open items auftreten die vorher nicht sichtbar waren.

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

7. **Scope Discipline**: Avoid scope creep - implementiere nur was im aktuellen Slice definiert ist. Keine opportunistischen Refactorings außerhalb des Scope.

8. **Final Verdict**: Liefere `READY` oder `NOT READY` Verdict mit vollständiger Evidence (changed files, verification checklist, open risks).

Unterbreche erst wenn komplett fertig implementiert ODER blocker/open items auftreten die vorher nicht sichtbar waren.