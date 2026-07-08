# Hybrid Skill Sync fuer private und Arbeitsgeraete

## Ziel

Dieses Setup nutzt `shared-ai-docs/skills-repo/skills` als einzige aktive Skill-Liste.

Das bedeutet:

1. eigene Skills werden im Git-Repo gepflegt
2. vendorgemanagte Skills sind unter `skills-repo/skills` als Links auf `skills-repo/vendor/...` sichtbar
3. Codex, Claude und Agents lesen dieselbe aktive Skill-Liste
4. es gibt keinen separaten `active-skills/` Aggregationsordner

## Kanonische Struktur

```text
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/
  docs/
  skills-repo/
    skills/
      <active-skill-name>/
      <vendor-managed-skill-name> -> ../vendor/<source>/...
    vendor/
      custom/
      mattpocock/
      vercel/
    tools/
      sync-codex-skill-links.sh
      install-git-hooks.sh
```

`skills-repo/skills` ist die aktive Liste. Wenn ein Skill dort nicht steht, soll er nicht als gemeinsamer aktiver Skill behandelt werden.

## Aktuelle Runtime-Mappings auf dem Mac

Diese Pfade zeigen auf dieselbe aktive Liste:

```text
/Users/dh/.agents/skills -> /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills
/Users/dh/.claude/skills -> /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills
```

Codex nutzt einzelne Links in:

```text
/Users/dh/.codex/skills/<skill-name> -> /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/<skill-name>
```

Die Codex-Links werden mit diesem Tool aktualisiert:

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
```

Das Tool laesst Codex-Systemskills und Plugin-Runtime-Ordner unveraendert und verwaltet nur Links auf die gemeinsame `skills-repo/skills` Liste.

## Vendor-Skills

Vendor-Quellen liegen unter:

```text
skills-repo/vendor/custom/
skills-repo/vendor/mattpocock/
skills-repo/vendor/vercel/
```

Wenn ein vendorgemanagter Skill aktiv sein soll, steht er unter `skills-repo/skills` als Link auf seine Vendor-Quelle. Dadurch wird der aktive Skill automatisch aktualisiert, sobald die Vendor-Quelle durch einen Pull oder Import aktualisiert wird.

Beispiel:

```text
skills-repo/skills/tdd -> ../vendor/mattpocock/.agents/skills/tdd
```

Alle Skills aus `skills-repo/vendor/mattpocock/.agents/skills` sind aktive Skills. Sie werden in `skills-repo/skills` als Links auf die Vendor-Quelle gefuehrt, damit Codex sie verwendet und Vendor-Pulls sofort sichtbar werden.

Der fruehere lokale Skill `diagnose` ist nicht mehr aktiv. Die aktive bug-diagnosis Variante kommt aus dem Matt-Pocock-Vendor-Skill `diagnosing-bugs`.

Der `council` Skill ist ebenfalls aktiv unter `skills-repo/skills/council`. Seine Dateien zeigen auf `vendor/custom/council-of-high-intelligence`; `SKILL.md` zeigt dabei bewusst auf die Codex-spezifische Vendor-Datei `SKILL.codex.md`.

## Keine `active-skills/`

`skills-repo/active-skills` ist nicht Teil dieses Setups.

Gruende:

1. Die aktive Liste waere sonst doppelt modelliert.
2. Codex, Claude und Agents wuerden unterschiedliche Pfade sehen.
3. Vendor-Updates koennten in Kopien oder Aggregationsordnern haengen bleiben.

Die aktive Quelle ist immer:

```text
skills-repo/skills
```

## Tools

### Codex-Links synchronisieren

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
```

Das Tool:

1. liest alle Eintraege unter `skills-repo/skills`
2. entfernt alte Codex-Links auf dieses Repo oder auf das fruehere `active-skills/`
3. legt passende Links in `/Users/dh/.codex/skills` an

### Git-Hooks installieren

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/install-git-hooks.sh
```

Das Tool installiert lokale `post-merge` und `post-checkout` Hooks im Git-Repo `shared-ai-docs`. Nach Pulls oder Branch-Wechseln werden die Codex-Skill-Links dadurch automatisch aktualisiert.

## Windows-Zielsetup

Auf Windows soll der Copilot-Skillpfad auf dieselbe aktive Liste zeigen:

```text
%USERPROFILE%\.copilot\skills -> <repo>\skills-repo\skills
```

Je nach Firmenrichtlinie sollte dafuer eine Junction oder ein Directory Symlink verwendet werden.

Beispiel:

```powershell
$RepoSkills = "<repo>\skills-repo\skills"
$Copilot = "$env:USERPROFILE\.copilot\skills"

if (Test-Path $Copilot) {
  Rename-Item $Copilot "$Copilot.bak"
}

New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.copilot" | Out-Null
cmd /c mklink /J "$Copilot" "$RepoSkills"
```

## Arbeitsweise

### Eigene Skills bearbeiten

1. Skill unter `skills-repo/skills/<skill-name>` bearbeiten.
2. Vor Arbeitsbeginn `git pull` im Repo ausfuehren.
3. Nach Aenderungen committen und pushen.
4. Auf anderen Geraeten pullen.

### Vendor-Skills aktualisieren

1. Vendor-Quelle unter `skills-repo/vendor/<source>` aktualisieren.
2. Weil aktive Vendor-Skills in `skills-repo/skills` als Links auf Vendor-Quellen liegen, sieht der aktive Skill die neue Vendor-Version sofort.
3. Nach einem Pull oder Branch-Wechsel aktualisieren die installierten Hooks die Codex-Links.
4. Wenn neue aktive Skills hinzukommen, `sync-codex-skill-links.sh` ausfuehren oder die Hooks installieren.

### Vendor-Skills lokal anpassen

Vendor-Skills, die direkt als Link aus `skills-repo/skills` auf `vendor/...` zeigen, sollen nicht direkt im aktiven Pfad angepasst werden. Fuer lokale Aenderungen gibt es zwei saubere Optionen:

1. den Skill aus Vendor in einen eigenen Skill unter `skills-repo/skills/<new-name>` forken
2. die Anpassung upstream im Vendor-Repo vornehmen

## Verifikation

### Mac-Runtime-Pfade

```bash
readlink /Users/dh/.agents/skills
readlink /Users/dh/.claude/skills
realpath /Users/dh/.agents/skills
realpath /Users/dh/.claude/skills
```

Erwartung:

```text
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills
```

### Codex sieht die aktive Liste

```bash
find -L /Users/dh/.codex/skills -mindepth 1 -maxdepth 2 -name SKILL.md -print
```

Erwartung: fuer jeden aktiven Skill in `skills-repo/skills` gibt es einen passenden Codex-Link, ausgenommen Codex-Systemskills und Plugin-Runtime-Skills.

### Kein Aggregationsordner

```bash
test ! -e /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/active-skills
```

Erwartung: der Befehl ist erfolgreich.

### Vendor-Link pruefen

```bash
readlink /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/tdd
readlink /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/diagnosing-bugs
```

Erwartung:

```text
../vendor/mattpocock/.agents/skills/tdd
../vendor/mattpocock/.agents/skills/diagnosing-bugs
```

## Akzeptanzkriterien

1. `skills-repo/skills` ist die einzige aktive gemeinsame Skill-Liste.
2. `/Users/dh/.agents/skills` und `/Users/dh/.claude/skills` zeigen auf `skills-repo/skills`.
3. `/Users/dh/.codex/skills` enthaelt Links fuer die aktiven Skills aus `skills-repo/skills`.
4. Alle Matt-Pocock-Vendor-Skills sind unter `skills-repo/skills` aktiv und zeigen per Link auf `skills-repo/vendor/mattpocock/.agents/skills/...`.
5. `skills-repo/active-skills` existiert nicht.
6. Die Dokumentation beschreibt denselben Zustand, den die lokalen Pfade tatsaechlich verwenden.
