# Hybrid Skill Sync fuer private und Arbeitsgeraete

## Ziel

Dies beschreibt ein Setup, in dem eigene Agent-Skills auf mehreren Geraeten gemeinsam genutzt und bearbeitet werden koennen, waehrend externe Skills weiterhin ueber `vercel-labs/skills` installiert oder getestet werden koennen.

Das Zielbild ist:

1. ein Git-Repository als zentrale Quelle fuer eigene Skills
2. lokale Runtime-Pfade fuer `~/.agents/skills`, `~/.claude/skills` und `~/.copilot/skills`
3. optionaler Import externer Skills ueber `vercel-labs/skills`

## Ausgangslage

Aktuell ist auf dem privaten Mac:

- [`/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills`](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills) ein Symlink auf [`/Users/dh/.claude/skills`](/Users/dh/.claude/skills)
- [`/Users/dh/.agents/skills`](/Users/dh/.agents/skills) enthaelt eigene Skills als lokalen Runtime-Pfad

Dieses Modell ist fuer echte Zwei-Wege-Synchronisation unguenstig, weil der geteilte Pfad nicht die Quelle ist, sondern nur auf einen lokalen Pfad zeigt.

## Empfohlenes Zielbild

Die Quelle wird in ein normales Git-Repository verschoben, zum Beispiel:

```text
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/
  docs/
  skills-repo/
    skills/
      core/
      documentation/
      frontend-design/
      ...
    vendor/
      vercel/
      custom/
    bootstrap/
      setup-macos.sh
      setup-windows.ps1
    README.md
```

Wichtig:

- `skills-repo/skills` enthaelt die eigenen, editierbaren Skills
- `skills-repo/vendor` ist fuer fremde oder testweise importierte Skills
- lokale Tool-Pfade zeigen nur noch auf `skills-repo/skills` oder auf gezielt gemappte Unterordner

## Rolle von `vercel-labs/skills`

`vercel-labs/skills` ist in diesem Setup kein Source-of-Truth und kein Sync-Mechanismus.

Es wird nur fuer diese Aufgaben genutzt:

1. externe Skills installieren oder evaluieren
2. Skills aus anderen Repositories lokal testen
3. Vorlagen oder Drittanbieter-Skills in einen separaten Vendor-Bereich uebernehmen

Der lokale Pfad [`/Users/dh/.agents/skills`](/Users/dh/.agents/skills) ist dabei ein Runtime-Pfad, kein Paketregister.

Praktisch bedeutet das:

- eigene Skills werden direkt im Git-Repo gepflegt
- externe Skills koennen mit `vercel-labs/skills` in `vendor/` geholt werden
- nur die Skills, die wirklich aktiv sein sollen, werden in die Runtime-Pfade eingebunden

## Hybrid-Modell

### Teil A: Eigene Skills

Eigene Skills liegen im Git-Repo:

```text
skills-repo/skills/<skill-name>/SKILL.md
```

Diese Struktur wird zwischen privatem und beruflichem Geraet per Git synchronisiert.

### Teil B: Externe Skills

Externe Skills werden getrennt gehalten, zum Beispiel:

```text
skills-repo/vendor/vercel/<skill-name>/
skills-repo/vendor/custom/<skill-name>/
```

Sie koennen:

1. direkt gelesen werden
2. testweise verlinkt werden
3. bei Bedarf spaeter in `skills/` uebernommen und angepasst werden

## Empfohlene Runtime-Mappings

### Privat-Mac

Empfohlen:

- [`/Users/dh/.claude/skills`](/Users/dh/.claude/skills) -> `skills-repo/skills`
- [`/Users/dh/.agents/skills`](/Users/dh/.agents/skills) -> `skills-repo/skills`
- optional `~/.copilot/skills` -> `skills-repo/skills`

### Arbeitsgeraet mit Windows und GitHub Copilot

Empfohlen:

- `%USERPROFILE%\.copilot\skills` -> `<repo>\skills`
- optional `%USERPROFILE%\.agents\skills` -> `<repo>\skills`

Unter Windows sollten bevorzugt Junctions oder Directory Symlinks verwendet werden, je nach Firmenrichtlinie.

## Migration vom aktuellen Mac-Setup

### Schritt 1: Neues Zielverzeichnis anlegen

Beispiel:

```bash
mkdir -p /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills
mkdir -p /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/vendor/vercel
mkdir -p /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/bootstrap
```

### Schritt 2: Eigene Skills in das Repo verschieben oder kopieren

Als Quelle eignen sich die aktuell gepflegten lokalen Skills, zum Beispiel aus:

- [`/Users/dh/.agents/skills`](/Users/dh/.agents/skills)
- [`/Users/dh/.claude/skills`](/Users/dh/.claude/skills)

Nur die eigenen Skills uebernehmen, nicht blind alle Drittanbieter-Inhalte.

### Schritt 3: Lokale Skill-Pfade auf das Repo umstellen

Vorhandene Pfade sichern und dann neu verlinken.

Beispiel auf macOS:

```bash
mv /Users/dh/.agents/skills /Users/dh/.agents/skills.bak
mv /Users/dh/.claude/skills /Users/dh/.claude/skills.bak

ln -s /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills /Users/dh/.agents/skills
ln -s /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills /Users/dh/.claude/skills
```

Falls `shared-ai-docs/skills` als Kompatibilitaetspfad erhalten bleiben soll:

```bash
rm /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills
ln -s /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills
```

Damit zeigt der geteilte Pfad kuenftig auf das Git-Repo statt auf einen lokalen Home-Verzeichnis-Pfad.

## Windows-Setup

Annahme:

- Repo liegt unter `C:\Users\<user>\Documents\shared-ai-docs\skills-repo`

Beispiel mit PowerShell:

```powershell
$Repo = "$env:USERPROFILE\Documents\shared-ai-docs\skills-repo\skills"
$Copilot = "$env:USERPROFILE\.copilot\skills"

if (Test-Path $Copilot) {
  Rename-Item $Copilot "$Copilot.bak"
}

New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.copilot" | Out-Null
cmd /c mklink /J "$Copilot" "$Repo"
```

Falls Directory Symlinks erlaubt sind:

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.copilot\skills" -Target $Repo
```

## Arbeitsweise im Alltag

### Eigene Skills aendern

1. im Repo unter `skills-repo/skills` bearbeiten
2. `git pull` vor Arbeitsbeginn
3. `git commit` und `git push` nach Aenderungen
4. auf dem anderen Geraet `git pull`

### Externe Skills testen

1. Skill mit `vercel-labs/skills` oder aus einem fremden Repo holen
2. unter `skills-repo/vendor/...` ablegen
3. optional testweise in einem separaten Runtime-Pfad verlinken
4. nur bei echtem Bedarf in `skills-repo/skills` uebernehmen

## Empfehlung fuer Runtime-Trennung

Wenn sauber zwischen eigenen und externen Skills getrennt werden soll, sind zwei Muster sinnvoll.

### Variante 1: Nur eigene Skills aktiv

Runtime-Pfade zeigen ausschliesslich auf:

```text
skills-repo/skills
```

Das ist die stabilste und am leichtesten wartbare Variante.

### Variante 2: Aggregierter Aktiv-Pfad

Es gibt zusaetzlich einen Build- oder Aggregationsordner:

```text
skills-repo/active-skills
```

Dort werden Symlinks auf ausgewaehlte Skills aus `skills/` und `vendor/` gesammelt. Die Runtime zeigt dann auf `active-skills`.

Das lohnt sich, wenn:

- nur ein Teil externer Skills aktiv sein soll
- Namen kollidieren koennen
- eigene und fremde Skills getrennt versioniert bleiben sollen

## Namens- und Portabilitaetsregeln

Damit dieselben Skills auf Mac und Windows funktionieren:

1. keine hart kodierten absoluten Mac-Pfade in `SKILL.md`
2. Hilfsskripte moeglichst in `python` oder `node`
3. falls Shell noetig ist, macOS- und Windows-Varianten trennen
4. ASCII-Dateinamen bevorzugen
5. `.gitattributes` fuer konsistente Zeilenenden pflegen

Empfohlene `.gitattributes`:

```text
* text=auto
*.sh text eol=lf
*.ps1 text eol=crlf
```

## Klare Empfehlung

Fuer den Alltag ist dieses Modell empfohlen:

1. `shared-ai-docs/skills-repo` als Git-Quelle einfuehren
2. `skills-repo/skills` fuer eigene Skills verwenden
3. `skills-repo/vendor` fuer externe Skills verwenden
4. `~/.agents/skills`, `~/.claude/skills` und `%USERPROFILE%\.copilot\skills` nur noch auf Repo-Pfade zeigen lassen
5. `vercel-labs/skills` nur als Installations- und Importwerkzeug verwenden

So bleiben Bearbeitung, Synchronisation und produktive Nutzung getrennt und nachvollziehbar.

## Spec

### Ziel

Ein gemeinsames, Git-basiertes Skill-Repository soll als Source of Truth fuer eigene Agent-Skills dienen. Die produktiven Skill-Pfade auf dem privaten Mac und auf dem Windows-Arbeitsgeraet sollen auf diese gemeinsame Quelle zeigen. Externe Skills bleiben optional und werden getrennt im Vendor-Bereich verwaltet.

### Scope

Im Scope dieser Aenderung:

1. Definition der Zielstruktur fuer `skills-repo`
2. Umstellung des Mac-Setups auf repo-basierte Runtime-Links
3. Definition des Windows-Zielsetups fuer GitHub Copilot
4. Dokumentation von Akzeptanzkriterien und Testfaellen fuer beide Geraete

Nicht im Scope dieser Aenderung:

1. Migration aller bestehenden Fremd-Skills in den Vendor-Bereich
2. automatische Aggregation ueber `active-skills/`
3. Vereinheitlichung aller plattformspezifischen Hilfsskripte

### Rollen

- Mac-Umsetzung: Codex setzt die Repo-Struktur und die lokalen Runtime-Links um
- Windows-Umsetzung: GitHub Copilot setzt das lokale Copilot-Setup anhand dieser Doku um

### Decision Freeze

Fuer diese Iteration ist das Abnahmeziel eindeutig:

1. produktive Runtime-Pfade zeigen direkt auf `shared-ai-docs/skills-repo/skills`
2. `active-skills/` bleibt eine optionale Anschlussarbeit und ist nicht Teil der Abnahme
3. Vendor-Skills bleiben getrennt und werden nicht in den produktiven Pfad aufgenommen, solange kein separater Folgeentscheid getroffen wurde

### Akzeptanzkriterien

#### Gemeinsam

1. Es gibt genau eine Git-basierte Quelle fuer eigene Skills unter `shared-ai-docs/skills-repo/skills`.
2. Die Doku beschreibt klar die Trennung zwischen eigenen Skills (`skills/`) und externen Skills (`vendor/`).
3. `vercel-labs/skills` ist als Installations- und Importwerkzeug beschrieben, nicht als Sync-Mechanismus.
4. Die produktiven Runtime-Pfade zeigen auf das gemeinsame Repo und nicht mehr auf voneinander abweichende lokale Skill-Bestaende.

#### Mac

1. [`/Users/dh/.agents/skills`](/Users/dh/.agents/skills) zeigt auf `shared-ai-docs/skills-repo/skills`.
2. [`/Users/dh/.claude/skills`](/Users/dh/.claude/skills) zeigt auf denselben gemeinsamen Pfad.
3. Der bisherige Kompatibilitaetspfad [`/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills`](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills) zeigt, falls beibehalten, ebenfalls auf das Repo und nicht auf ein Home-Verzeichnis.
4. Eine Aenderung an einem Skill im Repo ist ohne weitere Kopier- oder Installationsschritte sofort in den Mac-Runtime-Pfaden sichtbar.

#### Windows

1. `%USERPROFILE%\.copilot\skills` zeigt auf `<repo>\skills`.
2. GitHub Copilot kann Skills aus diesem Pfad lesen; dies wird ueber einen Pfadcheck und einen manuellen Smoke-Test mit einem bekannten lokalen Skill nachgewiesen.
3. Eine Aenderung an einem Skill nach `git pull` ist ohne manuelle Nachsynchronisation im Copilot-Skill-Pfad sichtbar.
4. Das Setup verwendet einen stabilen Link-Mechanismus, bevorzugt Junction oder Directory Symlink gemaess Firmenrichtlinie.

### Testfaelle

#### Mac-Testfaelle

##### TC-MAC-01 Repo ist Source of Truth

Voraussetzung:

- `skills-repo/skills` existiert
- Mac-Runtime-Pfade sind auf das Repo umgestellt

Schritte:

1. `readlink /Users/dh/.agents/skills`
2. `readlink /Users/dh/.claude/skills`
3. optional `readlink /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills`

Erwartung:

- alle aktiven Pfade zeigen auf `shared-ai-docs/skills-repo/skills`

Verifikationskommandos:

```bash
readlink /Users/dh/.agents/skills
readlink /Users/dh/.claude/skills
readlink /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills

realpath /Users/dh/.agents/skills
realpath /Users/dh/.claude/skills
realpath /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills
```

##### TC-MAC-02 Skill-Aenderung ist sofort sichtbar

Voraussetzung:

- mindestens ein Skill liegt in `skills-repo/skills/<name>/SKILL.md`

Schritte:

1. einen kleinen, reversiblen Testkommentar in `SKILL.md` im Repo ergaenzen
2. denselben Skill ueber den Pfad [`/Users/dh/.agents/skills`](/Users/dh/.agents/skills) lesen
3. denselben Skill ueber den Pfad [`/Users/dh/.claude/skills`](/Users/dh/.claude/skills) lesen

Erwartung:

- die Aenderung ist ueber beide Runtime-Pfade sichtbar, ohne Kopier- oder Installationsschritt

Verifikationskommandos:

```bash
export SKILL_NAME="<skill-name>"
export REPO_ROOT="/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills"
export REPO_SKILL="$REPO_ROOT/$SKILL_NAME/SKILL.md"
export AGENTS_SKILL="/Users/dh/.agents/skills/$SKILL_NAME/SKILL.md"
export CLAUDE_SKILL="/Users/dh/.claude/skills/$SKILL_NAME/SKILL.md"
export MARKER="SYNC_TEST_$(date +%Y%m%d%H%M%S)"

printf '\n%s\n' "$MARKER" >> "$REPO_SKILL"
rg -n "$MARKER" "$REPO_SKILL" "$AGENTS_SKILL" "$CLAUDE_SKILL"
```

Rueckbau:

```bash
sed -i '' "\|$MARKER|d" "$REPO_SKILL"
git -C /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs diff -- "$REPO_SKILL"
```

##### TC-MAC-03 Gemeinsamer Skill-Bestand fuer mehrere Agenten

Voraussetzung:

- `~/.agents/skills` und `~/.claude/skills` zeigen auf dasselbe Repo

Schritte:

1. in beiden Pfaden die Liste der Skill-Ordner vergleichen
2. stichprobenartig dieselben `SKILL.md`-Dateien pruefen

Erwartung:

- beide Agenten sehen denselben Skill-Bestand derselben Quelle

Verifikationskommandos:

```bash
diff \
  <(find /Users/dh/.agents/skills -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort) \
  <(find /Users/dh/.claude/skills -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
```

#### Windows-Testfaelle

##### TC-WIN-01 Copilot-Pfad zeigt auf Repo

Voraussetzung:

- Repo ist lokal auf dem Windows-Arbeitsgeraet ausgecheckt
- `%USERPROFILE%\.copilot\skills` wurde eingerichtet

Schritte:

1. Link-Ziel von `%USERPROFILE%\.copilot\skills` pruefen
2. pruefen, dass das Ziel auf `<repo>\skills` zeigt

Erwartung:

- der Copilot-Skill-Pfad ist ein Link auf das gemeinsame Repo, keine getrennte Kopie

Verifikationskommandos:

```powershell
$Copilot = "$env:USERPROFILE\.copilot\skills"
$Expected = "<repo-root>\\skills"
Get-ChildItem "$env:USERPROFILE\.copilot" -Force | Format-Table Name,LinkType,Target
Resolve-Path $Copilot
cmd /c dir "$env:USERPROFILE\.copilot"
Write-Host "Expected target: $Expected"
```

##### TC-WIN-02 Repo-Aenderung erscheint in Copilot-Pfad

Voraussetzung:

- mindestens ein Skill liegt im Repo

Schritte:

1. eine kleine Testaenderung im Skill-Repo vornehmen oder per `git pull` beziehen
2. dieselbe Datei ueber `%USERPROFILE%\.copilot\skills` lesen

Erwartung:

- die Aenderung ist ohne Kopier- oder Reinstallationsschritt sichtbar

Verifikationskommandos:

```powershell
$SkillName = "<skill-name>"
$RepoRoot = "<repo-root>\\skills"
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
git -C "<repo-root>" diff -- $RepoSkill
```

##### TC-WIN-03 Copilot kann den Skill-Bestand lesen

Voraussetzung:

- GitHub Copilot ist lokal aktiv
- Skill-Pfad ist eingerichtet

Schritte:

1. pruefen, dass der erwartete Skill im verlinkten Pfad vorhanden ist
2. Copilot mit einem Prompt ansprechen, der einen bekannten lokalen Skill nutzen sollte
3. das Ergebnis als manuellen Smoke-Test dokumentieren

Erwartung:

- der Skill ist im verlinkten Pfad vorhanden
- der manuelle Smoke-Test bestaetigt, dass Copilot den aus dem Repo verlinkten Skill-Bestand lesen und nutzen kann

Verifikationskommandos:

```powershell
$SkillName = "<skill-name>"
Get-ChildItem "$env:USERPROFILE\.copilot\skills" -Directory | Select-Object Name
Test-Path "$env:USERPROFILE\.copilot\skills\$SkillName\SKILL.md"
Get-Content "$env:USERPROFILE\.copilot\skills\$SkillName\SKILL.md" -TotalCount 20
```

Manueller Smoke-Test:

1. einen lokal vorhandenen Skill mit eindeutigem Namen waehlen
2. Copilot Chat neu oeffnen
3. einen Prompt verwenden, der genau diesen Skill triggern sollte
4. das Verhalten oder die sichtbare Referenz auf den Skill kurz dokumentieren

Hinweis:

- dieser Test bleibt clientabhaengig und ist weniger deterministisch als die Pfad- und Dateipruefungen

### Abnahme

Die Aenderung ist abgenommen, wenn:

1. die Mac-Testfaelle erfolgreich durchlaufen wurden
2. die Windows-Testfaelle durch den Copilot auf dem Arbeitsgeraet erfolgreich bestaetigt wurden
3. keine zweite manuell gepflegte Kopie der eigenen Skills mehr als produktiver Pfad benoetigt wird
4. die Doku fuer einen spaeteren Neuaufbau des Setups ausreicht

## Offene Anschlussarbeit

Die folgenden Punkte koennen nach der Umstellung ergaenzt werden:

1. `bootstrap/setup-macos.sh`
2. `bootstrap/setup-windows.ps1`
3. `README.md` im `skills-repo`
4. optional `active-skills/` als Aggregationspfad
5. Migrationscheckliste fuer bestehende Skill-Namen und Abhaengigkeiten
