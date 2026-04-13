

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

## Close Change

change ist akzeptiert, schließe spec/open-spec


## Bootstrap Windows Skills

Klar, hier ist ein Copy-Paste-Prompt für Copilot auf dem Windows-Laptop:

```text
Implementiere den Windows-Slice der Skill-Sync-Spec im Direct-Modus (ohne OpenSpec).

Kontext:
- Source of truth ist jetzt das Git-Repo unter `<REPO_ROOT>\skills-repo\skills`
- Der Mac-Slice ist bereits umgesetzt
- Der alte Kompatibilitätspfad `shared-ai-docs/skills` wurde auf dem Mac bewusst entfernt
- Ziel auf Windows: `%USERPROFILE%\.copilot\skills` soll auf `<REPO_ROOT>\skills-repo\skills` zeigen
- Optionaler Alias oder zweite Kopien sind nicht gewünscht
- Nutze einen stabilen Link-Mechanismus: bevorzugt Junction, sonst Directory Symlink
- Verwende als Test-Skill `doc-coauthoring`, falls vorhanden

Arbeite in diesen Schritten:

1. Pre-Implementation Analysis
- Lies die Spec in:
  `<REPO_ROOT>\docs\skills\hybrid-skill-sync.md`
- Prüfe auf formale Marker: `[MISSING]`, `[DECISION]`, `[BLOCKED]`
- Analysiere den aktuellen Ist-Zustand auf Windows:
  - existiert `%USERPROFILE%\.copilot\skills`?
  - ist es ein echtes Verzeichnis, Junction oder Symlink?
  - existiert `<REPO_ROOT>\skills-repo\skills`?
  - ist `doc-coauthoring\SKILL.md` dort vorhanden?
- Stoppe bei blockierenden Widersprüchen und nenne sie explizit

2. Scope Contract
Erstelle vor Änderungen einen kurzen Scope Contract mit:
- In scope
- Out of scope
- Acceptance targets
- Planned verification
- Open risks / assumptions

3. Implementation
- Wenn `%USERPROFILE%\.copilot\skills` bereits existiert, sichere es als Backup
- Richte `%USERPROFILE%\.copilot\skills` als Junction oder Directory Symlink auf:
  `<REPO_ROOT>\skills-repo\skills`
- Keine zweite Kopie der Skills anlegen
- Keine Änderungen außerhalb dieses Windows-Slices

4. Verification
Führe ALLE Windows-Verifikationsschritte aus der Spec aus und gib für jedes Kommando einen Status aus:
- `ran`
- `failed`
- `blocked`

Nutze diese Kommandos bzw. äquivalente PowerShell-Kommandos:

TC-WIN-01
```powershell
$Copilot = "$env:USERPROFILE\.copilot\skills"
$Expected = "<REPO_ROOT>\skills-repo\skills"
Get-ChildItem "$env:USERPROFILE\.copilot" -Force | Format-Table Name,LinkType,Target
Resolve-Path $Copilot
cmd /c dir "$env:USERPROFILE\.copilot"
Write-Host "Expected target: $Expected"
```

TC-WIN-02
```powershell
$SkillName = "doc-coauthoring"
$RepoRoot = "<REPO_ROOT>\skills-repo\skills"
$RepoSkill = Join-Path $RepoRoot "$SkillName\SKILL.md"
$CopilotSkill = Join-Path "$env:USERPROFILE\.copilot\skills" "$SkillName\SKILL.md"
$Marker = "SYNC_TEST_{0}" -f (Get-Date -Format "yyyyMMddHHmmss")

Add-Content -Path $RepoSkill -Value "`n$Marker"
Select-String -Path $RepoSkill,$CopilotSkill -Pattern $Marker
```

Rueckbau:
```powershell
$content = Get-Content $RepoSkill | Where-Object { $_ -ne $Marker }
Set-Content -Path $RepoSkill -Value $content
git -C "<REPO_ROOT>" diff -- $RepoSkill
```

TC-WIN-03
```powershell
$SkillName = "doc-coauthoring"
Get-ChildItem "$env:USERPROFILE\.copilot\skills" -Directory | Select-Object Name
Test-Path "$env:USERPROFILE\.copilot\skills\$SkillName\SKILL.md"
Get-Content "$env:USERPROFILE\.copilot\skills\$SkillName\SKILL.md" -TotalCount 20
```

Zusätzlich:
- führe einen manuellen Smoke-Test mit Copilot Chat durch
- dokumentiere kurz, ob Copilot den lokalen Skill-Bestand sichtbar/nutzbar macht
- wenn der Smoke-Test nicht deterministisch belegbar ist, markiere das sauber als manuellen Nachweis statt als fehlgeschlagen

5. Final Report
Berichte am Ende in diesem Format:
- Scope implemented
- Evidence
- Verification checklist mit `ran`/`failed`/`blocked`
- Changed artifacts
- Open risks / blockers
- Final verdict: `READY` oder `NOT READY`

Wichtig:
- kein OpenSpec
- kein Scope Creep
- keine Refactorings außerhalb des Windows-Setups
- keine zweite Skill-Kopie erzeugen
```

Ersetze nur noch `<REPO_ROOT>` mit dem echten Windows-Pfad zum `shared-ai-docs`-Repo. Ein guter Default wäre z. B. `C:\Users\<DEIN_USER>\Documents\shared-ai-docs`.