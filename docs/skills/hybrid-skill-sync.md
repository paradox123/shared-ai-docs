# Hybrid Skill Sync fuer globale Skills

## Ziel

Dieses Setup gilt nur fuer globale beziehungsweise geraeteuebergreifende Skills.

Es nutzt `shared-ai-docs/skills-repo/skills` als einzige aktive globale Skill-Liste.

Das bedeutet:

1. eigene Skills werden im Git-Repo gepflegt
2. vendorgemanagte Skills sind unter `skills-repo/skills` als Links auf `skills-repo/vendor/...` sichtbar
3. Codex, Claude und Agents lesen dieselbe aktive Skill-Liste
4. es gibt keinen separaten `active-skills/` Aggregationsordner

## Scope

Im Scope:

- globale Skills fuer Codex, Claude, Agents und Copilot
- gemeinsame Skills, die auf mehreren Geraeten genutzt werden sollen
- Vendor-Skills, die global aktiv sein sollen
- Runtime-Links unter `/Users/dh/.codex/skills`, `/Users/dh/.agents/skills`, `/Users/dh/.claude/skills` und den entsprechenden globalen Windows-Skillpfaden

Nicht im Scope:

- repo-spezifische Skills in einem einzelnen Projekt
- lokale Skill-Ordner wie `<repo>/.agents/skills` oder `<repo>/.codex/skills`
- Skills, die nur fuer einen bestimmten Workspace, eine bestimmte Codebase oder ein bestimmtes AGENTS.md gelten

Repo-spezifische Skill-Setups sollen der jeweiligen Repo-Dokumentation folgen. Dieses globale Setup darf sie nicht in `shared-ai-docs/skills-repo/skills` verschieben, ausser der User verlangt ausdruecklich eine globale Aktivierung.

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
      sync-windows-skill-links.ps1
      install-git-hooks.sh
```

`skills-repo/skills` ist die aktive globale Liste. Wenn ein Skill dort nicht steht, soll er nicht als gemeinsamer globaler Skill behandelt werden.

## Aktuelle Runtime-Mappings auf dem Mac

Diese Pfade zeigen auf dieselbe aktive Liste:

```text
/Users/dh/.agents/skills -> /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills
/Users/dh/.claude/skills -> /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills
```

Codex nutzt fuer globale Skills einzelne Links in:

```text
/Users/dh/.codex/skills/<skill-name> -> /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/<skill-name>
```

Die Codex-Links werden mit diesem Tool aktualisiert:

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
```

Das Tool laesst Codex-Systemskills, Plugin-Runtime-Ordner und repo-spezifische Skills unveraendert und verwaltet nur Links auf die gemeinsame globale `skills-repo/skills` Liste.

## Vendor-Skills

Vendor-Quellen liegen unter:

```text
skills-repo/vendor/custom/
skills-repo/vendor/mattpocock/
skills-repo/vendor/vercel/
```

Wenn ein vendorgemanagter Skill global aktiv sein soll, steht er unter `skills-repo/skills` als Link auf seine Vendor-Quelle. Dadurch wird der aktive Skill automatisch aktualisiert, sobald die Vendor-Quelle durch einen Pull oder Import aktualisiert wird.

Beispiel:

```text
skills-repo/skills/tdd -> ../vendor/mattpocock/.agents/skills/tdd
```

Alle Skills aus `skills-repo/vendor/mattpocock/.agents/skills` sind aktive globale Skills. Sie werden in `skills-repo/skills` als Links auf die Vendor-Quelle gefuehrt, damit Codex sie global verwendet und Vendor-Pulls sofort sichtbar werden.

Der fruehere lokale Skill `diagnose` ist nicht mehr aktiv. Die aktive bug-diagnosis Variante kommt aus dem Matt-Pocock-Vendor-Skill `diagnosing-bugs`.

Der `council` Skill ist ebenfalls aktiv unter `skills-repo/skills/council`. Seine Dateien zeigen auf `vendor/custom/council-of-high-intelligence`; `SKILL.md` zeigt dabei bewusst auf die Codex-spezifische Vendor-Datei `SKILL.codex.md`.

Council ist ein kopierter Snapshot aus [0xNyk/council-of-high-intelligence](https://github.com/0xNyk/council-of-high-intelligence), kein eigener Git-Checkout. `skills-repo/vendor/custom/council-of-high-intelligence/skills-lock.json` haelt den importierten Commit (`sourceRef`), dessen kanonischen Git-Tree (`sourceTree`) und den SHA-256 der unveraenderten Upstream-Datei `SKILL.codex.md` (`computedHash`) fest. `localOverlays` inventarisiert die lokal angepassten Dateien samt SHA-256 ihres zusammengefuehrten Inhalts. Die Lockdatei selbst gehoert nicht zu Upstream. `reconstructedPreviousRef` dokumentiert den aus Dateivergleichen rekonstruierten Stand vor Einfuehrung der Lockdatei.

Die Council-Overlays erhalten den simulierten Codex-Standardmodus, explizit angeforderte Live-Subagents, sichere CLI-Promptuebergabe und Codex-passende Provider-Erkennung und Beispielkonfigurationen. Beim Update den Drei-Wege-Ablauf unten verwenden. Die Vercel-Skills-CLI kann die Quelle ohne Installation pruefen:

```bash
npx skills@latest add 0xNyk/council-of-high-intelligence --list
```

Den aktualisierten Snapshot unter `vendor/custom/council-of-high-intelligence` uebernehmen und danach bei freigegebener Runtime-Aktualisierung den zum Betriebssystem passenden Skill-Sync ausfuehren. Eine direkte globale CLI-Installation wuerde die bestehende Linkstruktur und den bewusst ausgewaehlten Codex-Einstiegspunkt umgehen.

## Keine `active-skills/`

`skills-repo/active-skills` ist nicht Teil dieses Setups.

Gruende:

1. Die aktive Liste waere sonst doppelt modelliert.
2. Codex, Claude und Agents wuerden unterschiedliche Pfade sehen.
3. Vendor-Updates koennten in Kopien oder Aggregationsordnern haengen bleiben.

Die aktive globale Quelle ist immer:

```text
skills-repo/skills
```

## Tools

### Codex-Links synchronisieren (macOS/POSIX)

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/sync-codex-skill-links.sh
```

Das Tool:

1. liest alle globalen Eintraege unter `skills-repo/skills`
2. entfernt alte Codex-Links auf dieses Repo oder auf das fruehere `active-skills/`
3. legt passende Links in `/Users/dh/.codex/skills` an

### Git-Hooks installieren (macOS/POSIX)

```bash
/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/install-git-hooks.sh
```

Das Tool installiert lokale `post-merge` und `post-checkout` Hooks im Git-Repo `shared-ai-docs`. Nur in einem freigegebenen normalen Checkout mit `.git`-Verzeichnis ausfuehren, nicht in Worktrees oder auf Windows. Nach Pulls oder Branch-Wechseln werden die Codex-Skill-Links dadurch automatisch aktualisiert.

## Windows-Zielsetup

Auf Windows mit `git config core.symlinks=false` sind Git-Symlinks im Checkout
nur Textdateien. Eine einzelne Junction von `%USERPROFILE%\.copilot\skills`
auf `skills-repo\skills` wuerde deshalb Vendor-Skills und den `council`-Einstieg
nicht lauffaehig machen. Wenn native Symlinks Administratorrechte erfordern,
verwendet der Windows-Sync stattdessen Junctions ohne Administratorrechte und
loest die Git-Linktexte gegen die Vendor-Quellen auf:

```text
%USERPROFILE%\.copilot\skills\<skill-name> -> <repo>\skills-repo\skills\<skill-name>
                                                  oder <repo>\skills-repo\vendor\...
%USERPROFILE%\.agents\skills -> %USERPROFILE%\.copilot\skills
%USERPROFILE%\.claude\skills -> %USERPROFILE%\.copilot\skills
%USERPROFILE%\.codex\skills\<skill-name> -> dieselbe Skill-Quelle
```

`council` braucht bei einem Checkout ohne native Symlinks eine kleine
Runtime-Projektion: `SKILL.md` wird aus der kanonischen Vendor-Datei kopiert;
`agents`, `configs` und `scripts` bleiben Junctions auf die Vendor-Quellen.
`skills-repo\skills` bleibt die **einzige aktive Quellliste**; die Runtime-Pfade
sind nur daraus abgeleitete Links und werden nicht im Git-Repo gepflegt.

Bei freigegebener Runtime-Aktualisierung aus dem Repository-Root installieren
oder nach einem Pull/Branch-Wechsel aktualisieren. Ein reiner Quellcode-PR im
Worktree autorisiert keine Aenderung globaler Runtime-Links:

```powershell
powershell.exe -NoProfile -File .\skills-repo\tools\sync-windows-skill-links.ps1
```

Das Script behaelt fremde Skills und Codex-Systemskills bei, ersetzt keine
bestehenden echten Skill-Ordner und entfernt nur veraltete Junctions auf
dieses Repo. Ein unbekannter Namenskonflikt oder ein defektes Vendor-Ziel
fuehrt zu einem Fehler statt zum Ueberschreiben. Ein Link in die abgeleitete
Copilot-Runtime gilt nur mit dem vorhandenen Sync-Marker und exakt passendem
kanonischen Quellpfad als verwaltet, nicht allein durch seinen Runtime-Ort.
Anders als die Mac-Hooks
laeuft der Windows-Sync nicht automatisch nach einem Pull; bei neuen oder
entfernten Skills sowie Council-Updates das Script erneut ausfuehren.

## Arbeitsweise

### Eigene globale Skills bearbeiten

1. Skill unter `skills-repo/skills/<skill-name>` bearbeiten.
2. Vor Arbeitsbeginn `git pull` im Repo ausfuehren.
3. Nach Aenderungen committen und pushen.
4. Auf anderen Geraeten pullen.

### Globale Vendor-Skills aktualisieren

1. Zuerst unterscheiden, ob `skills-repo/vendor/<source>` ein eigener Git-Checkout, ein ueber eine Lockdatei gepinnter Snapshot oder eine Legacy-Kopie ohne Lockdatei ist.
2. Einen Git-Checkout innerhalb seiner eigenen Repo-Grenze aktualisieren. Einen gepinnten Snapshot nicht wie einen Checkout behandeln und nicht blind mit dem neuen Upstream-Stand ueberschreiben. Bei einer Legacy-Kopie zuerst den nachfolgenden Provenienz-Bootstrap abschliessen.
3. Weil aktive globale Vendor-Skills in `skills-repo/skills` als Links auf Vendor-Quellen liegen, sieht der aktive Skill die neue Vendor-Version sofort.
4. Auf dem Mac aktualisieren die installierten Hooks nach einem Pull oder Branch-Wechsel die Codex-Links. Auf Windows den Windows-Sync erneut ausfuehren.
5. Wenn neue aktive Skills hinzukommen, den zum Betriebssystem passenden Sync ausfuehren oder auf dem Mac die Hooks installieren.

### Legacy-Kopie ohne Lockdatei bootstrapen

Wenn kopierte Vendor-Dateien bereits existieren, aber keine Lockdatei ihren bisherigen Upstream-Stand belegt, gilt vor dem ersten Update:

1. Upstream in einen aufgabeneigenen temporaeren Checkout klonen oder fetchen und alle Historienbefehle mit `git -C "$upstream_repo"` daran binden.
2. Aus mehreren stabilen Dateien des kopierten Baums genau einen vorherigen Upstream-Ref rekonstruieren. Bekannte lokale Dateien und wahrscheinliche Overlays nicht als Anker verwenden; Zeitstempel oder ein einzelner lokal editierbarer Einstiegspunkt reichen nicht als Provenienz.
3. Wenn kein Ref passt oder mehrere materiell verschiedene Refs plausibel bleiben, ohne Aenderung am Snapshot anhalten und die Unklarheit melden.
4. Den aktuellen kopierten Baum gegen den rekonstruierten Ref vergleichen und alle lokalen Abweichungen als moegliche Overlays inventarisieren. Der rekonstruierte Ref ist die Merge-Basis; der lokal angepasste Snapshot darf nicht selbst zur Basis erklaert werden.
5. Die erste Lockdatei im Staging erzeugen: `reconstructedPreviousRef` haelt die alte rekonstruierte Basis fest, `sourceRef` den ausgewaehlten neuen Upstream-Commit. Kanonische Upstream-Hashes und zusammengefuehrte lokale Overlays getrennt nach der dokumentierten Lock-Semantik erfassen.
6. Erst danach mit dem Drei-Wege-Ablauf fuer gepinnte Snapshots fortfahren und den validierten Staging-Baum anwenden.

### Gepinnte Vendor-Snapshots sicher aktualisieren

Ein gepinnter Snapshot enthaelt kopierte Vendor-Dateien und eine Lockdatei, die mindestens Quelle, alten `sourceRef`, Vendor-Zielpfad und gegebenenfalls Hashes pro Skill beschreibt. Lokale Anpassungen im kopierten Baum koennen absichtlich vom gepinnten Upstream abweichen.

Der sichere Update-Ablauf ist:

1. Lockdatei lesen und die Bedeutung ihrer Hashes aus bestehender Historie oder Dokumentation klaeren. Bei `skills-repo/vendor/mattpocock/skills-lock.json` beschreiben `computedHash`-Werte den kanonischen Upstream-Inhalt, nicht den lokal zusammengefuehrten Overlay-Stand.
2. Upstream in einen aufgabeneigenen temporaeren Ordner klonen oder fetchen. Historische Git-Befehle immer explizit an diesen Checkout binden:

```bash
git -C "$upstream_repo" show "$old_ref:<source-path>"
git -C "$upstream_repo" diff "$old_ref..$new_ref" -- <source-root>
git -C "$upstream_repo" rev-parse "$new_ref"
```

Ein ungebundenes `git show` oder `git diff` kann stattdessen das uebergeordnete `shared-ai-docs` Repo verwenden und scheinbar fehlende Upstream-Pfade melden.

3. Vor dem Schreiben den aktuellen Vendor-Baum gegen den alten gepinnten Upstream-Stand vergleichen und alle lokalen Abweichungen inventarisieren. Diese Abweichungen sind moegliche Overlays und duerfen nicht durch `rsync --delete` verloren gehen.
4. Den neuen kanonischen Upstream-Baum separat stagen. Fuer jede lokale Abweichung einen Drei-Wege-Vergleich verwenden:

```text
base  = Datei aus altem gepinntem Upstream-Ref
local = aktuelle Datei im Vendor-Snapshot
other = Datei aus neuem Upstream-Ref
```

Nur konfliktfreie Ergebnisse in den Staging-Baum uebernehmen. Bei Konflikten, Upstream-Loeschungen lokal veraenderter Dateien oder uneindeutigen Renames anhalten und die beabsichtigte Anpassung klaeren.

5. Die neue Lockdatei nach ihrer bestehenden Semantik erzeugen. Wenn ihre Hashes kanonischen Upstream abbilden, aus dem unmodifizierten neuen Upstream-Baum hashen; lokale Overlays separat durch einen erwarteten Vendor/Upstream-Diff pruefen.
6. Neue, entfernte und umbenannte Skills sowie direkte Skill-Abhaengigkeiten ermitteln. Fuer jeden neuen oder aktualisierten Einstiegspunkt dessen direkte Skill-Aufrufe und verlinkte Referenzen pruefen. Formulierungen wie "always call", "requires" oder ein namentlich verwendetes Primitiv gelten als notwendige Abhaengigkeit; rein beschreibende Beispiele nicht. Jede notwendige Abhaengigkeit muss im gestagten Vendor-Snapshot vorhanden und bei Aufruf ueber den Skillnamen unter `skills-repo/skills` aktiv sein, oder der Einstiegspunkt muss einen dokumentierten eigenstaendigen Ersatz enthalten. Bei fehlender notwendiger Abhaengigkeit vor der Aktivierung anhalten und Vendor-Version, fehlenden Link oder eine ausdruecklich Daniel-eigene Adaption klaeren. Unter `skills-repo/skills` nur Links aendern, deren bestehendes Ziel nachweislich zu diesem Vendor gehoert. Vor dem Entfernen das exakte erwartete Linkziel pruefen; Daniel-eigene Ordner und Links anderer Vendoren erhalten.
7. Erst nach erfolgreichen Merge-, Lock- und Link-Pruefungen den Staging-Baum auf den exakt validierten Vendor-Zielpfad anwenden. Destruktive Synchronisierung wie `rsync --delete` nie direkt aus einer ungeprueften Quelle oder gegen einen breiten beziehungsweise unaufgeloesten Zielpfad ausfuehren.
8. Danach den zum Betriebssystem passenden Skill-Sync ausfuehren und mindestens Folgendes verifizieren:

- gepinnter `sourceRef` entspricht dem ausgewaehlten neuen Upstream-Ref
- Lock-Hashes entsprechen dem kanonischen Upstream nach der dokumentierten Semantik
- Vendor/Upstream-Differenzen bestehen nur aus den inventarisierten lokalen Overlays
- aktive Vendor-Skillnamen entsprechen dem erwarteten neuen Set
- notwendige direkte Skill-Abhaengigkeiten aktiver Vendor-Einstiegspunkte sind geschlossen oder der eigenstaendige Ersatz ist dokumentiert
- entfernte Runtime-Links fehlen, neue Links zeigen auf vorhandene `SKILL.md` Dateien
- Broken-Link-Pruefungen bleiben leer und `git diff --check` ist erfolgreich

### Globale Vendor-Skills lokal anpassen

Vendor-Skills, die direkt als Link aus `skills-repo/skills` auf `vendor/...` zeigen, sollen nicht direkt im aktiven Pfad angepasst werden. Fuer lokale Aenderungen gibt es folgende Optionen:

1. den Skill aus Vendor in einen eigenen Skill unter `skills-repo/skills/<new-name>` forken
2. die Anpassung upstream im Vendor-Repo vornehmen
3. bei ausdruecklicher Freigabe ein lokales Overlay direkt im verifizierten Vendor-Quellpfad pflegen, ohne den aktiven Link zu veraendern; `sourceRef` und kanonische Upstream-Hashes unveraendert lassen und die Overlay-Differenz separat pruefen

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

### Codex sieht die aktive globale Liste

```bash
find -L /Users/dh/.codex/skills -mindepth 1 -maxdepth 2 -name SKILL.md -print
```

Erwartung: fuer jeden aktiven globalen Skill in `skills-repo/skills` gibt es einen passenden Codex-Link, ausgenommen Codex-Systemskills, Plugin-Runtime-Skills und repo-spezifische Skills.

### Windows-Runtime-Pfade

Aus dem Repository-Root fuer jeden aktiven Skill den lesbaren Einstiegspunkt
in allen vier globalen Runtimes pruefen:

```powershell
$names = (Get-ChildItem .\skills-repo\skills -Force).Name
foreach ($client in @('.copilot', '.agents', '.claude', '.codex')) {
  foreach ($name in $names) {
    $manifest = Join-Path $env:USERPROFILE "$client\skills\$name\SKILL.md"
    if (-not (Test-Path -LiteralPath $manifest -PathType Leaf) -or
        (Get-Content -LiteralPath $manifest -TotalCount 1) -ne '---') {
      throw "Nicht nutzbar: $manifest"
    }
  }
}
```

Die Junctions fuer `.agents\skills` und `.claude\skills` zeigen auf
`.copilot\skills`; alle `SKILL.md` Dateien enthalten echte Frontmatter statt
Git-Linktext. `git status --short` im Repository bleibt unveraendert.

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

1. `skills-repo/skills` ist die einzige aktive gemeinsame globale Skill-Liste.
2. Auf dem Mac zeigen `/Users/dh/.agents/skills` und `/Users/dh/.claude/skills` auf `skills-repo/skills`; auf Windows zeigen die entsprechenden Pfade auf die daraus abgeleitete Copilot-Runtime-Liste.
3. Die globalen Codex-Skillpfade enthalten Links fuer alle aktiven globalen Skills aus `skills-repo/skills`, auch bei Git-Checkouts ohne native Symlinks.
4. Alle global aktivierten Matt-Pocock-Vendor-Skills sind unter `skills-repo/skills` aktiv und zeigen per Link auf `skills-repo/vendor/mattpocock/.agents/skills/...`.
5. `skills-repo/active-skills` existiert nicht.
6. Die Dokumentation beschreibt denselben Zustand, den die lokalen Pfade tatsaechlich verwenden.
7. Aktive Vendor-Einstiegspunkte verweisen nicht auf fehlende notwendige Skill-Primitive; jede Ausnahme ist als eigenstaendige lokale Adaption dokumentiert.
