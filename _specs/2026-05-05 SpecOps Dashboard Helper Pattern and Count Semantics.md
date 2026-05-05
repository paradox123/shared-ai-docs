**Date:** 2026-05-05
**Status:** 🟢 Accepted
**Scope:** SpecOps Dashboard Follow-up fuer renderstabile Helper, klare Projektzaehlungen und wartbare DataviewJS-Konventionen

---

## Kontext

Die SpecOps-Dashboards sind inzwischen als Cockpit nutzbar: Root, Project Index, Global Spec Board, Backlog, Missing Metadata und Projektboards nutzen DataviewJS-Karten, Links und Lanes.

Das aktuelle UX-Review hat drei Follow-up-Findings identifiziert:

1. `Dashboard.md` nutzt im `Needs Attention`-Block `linkEl(...)`, obwohl dieser Helper in einem anderen DataviewJS-Block definiert ist. DataviewJS-Bloecke muessen als isolierte Ausfuehrungseinheiten behandelt werden.
2. `project-index.md` zaehlt Specs/Backlog anhand von `project.title`. Bei Project Entities, deren `title` nicht dem Taxonomie-Key `project` entspricht, koennen Counts leer oder irrefuehrend werden.
3. `linkEl`, Grid-, Card- und Metric-Patterns werden in mehreren Dashboard-Dateien kopiert. Das ist derzeit funktional, erhoeht aber Drift- und Wartungsrisiko.

Dieses Spec beschreibt einen kleinen Stabilitaets- und Konventions-Slice.

## Ziel

SpecOps-Dashboards sollen stabil rendern und kuenftige UX-Aenderungen besser tragen:

1. Jeder DataviewJS-Block ist in sich renderfaehig und verlaesst sich nicht auf Helper aus anderen Blocks.
2. Projektkarten machen explizit, ob Counts nach Project Entity Title oder Project Taxonomy Key berechnet werden.
3. Es gibt eine dokumentierte, copy-paste-sichere Dashboard-Helper-Konvention fuer Links, Cards, Grids und Metrics.

## In Scope

1. `Dashboard.md` so korrigieren, dass `Needs Attention` einen eigenen lokalen Link-Helper hat oder ohne externen Helper funktioniert.
2. `project-index.md` so anpassen, dass die Count-Semantik explizit ist:
   - Anzeige von Project Entity Title.
   - Anzeige von Project Taxonomy Key.
   - Counts basieren auf einem klar benannten `countKey`.
3. Eine kleine Referenzdatei fuer Dashboard-Helper-Patterns anlegen, z. B. `_shared/SpecOps/Reference/dashboard-helper-patterns.md`.
4. Bestehende Dashboard-Dateien nur dort anpassen, wo es fuer P1-Fix oder Count-Semantik erforderlich ist.
5. Verification-Checks fuer DataviewJS-Block-Isolation, Project-Index-Count-Key und Referenzdokument einfuehren.

## Out of Scope

1. Kein gemeinsames JavaScript-Modul, das Obsidian zur Laufzeit importieren muss.
2. Kein neues Obsidian-Plugin.
3. Kein CSS-/Theme-Slice.
4. Keine vollstaendige Refaktorierung aller Dashboard-DataviewJS-Bloecke.
5. Keine Entity-Schema-Aenderung.
6. Keine Backfill-Arbeit.
7. Keine Aenderung an Skills, Agents, RAG-Runtime oder Fachcode.

## Requirements

### R1 - Isolated Needs Attention Block

`Dashboard.md` darf im `Needs Attention`-DataviewJS-Block keine Helper aus anderen DataviewJS-Bloecken voraussetzen.

Akzeptanzkriterien:

1. Der `Needs Attention`-Block enthaelt eine eigene `linkEl`-Funktion oder nutzt ausschliesslich lokale/plain Dataview-Ausgabe.
2. Der Block parst im Node-Syntaxcheck.
3. Der Block enthaelt weiterhin klickbare Entity-Links fuer Backlog- und Metadata-Attention-Items.

### R2 - Explicit Project Count Semantics

`project-index.md` muss transparent machen, welcher Wert fuer Counts verwendet wird.

Akzeptanzkriterien:

1. Der DataviewJS-Block definiert einen klar benannten `countKey`.
2. Projektkarten zeigen `Project Entity` und `Project Key` oder gleichwertige Labels.
3. Counts fuer Specs, Active Specs, Backlog und Metadata Attention verwenden den `countKey`.
4. Wenn `title` und `project` voneinander abweichen, bleibt dieser Unterschied sichtbar statt stillschweigend in Null-Counts zu verschwinden.

### R3 - Dashboard Helper Pattern Reference

Es muss eine kleine Referenz fuer DataviewJS-Dashboard-Konventionen geben.

Akzeptanzkriterien:

1. `_shared/SpecOps/Reference/dashboard-helper-patterns.md` existiert.
2. Die Referenz beschreibt:
   - DataviewJS-Bloecke sind isoliert.
   - Link-Helper-Konvention.
   - Card/Grid/Metric-Konvention.
   - Count-Key-Konvention fuer Projekte.
   - Wann Copy/Paste erlaubt ist und wann ein eigener Slice fuer Refactoring noetig wird.
3. Root-Dashboard oder Reference-Bereich verlinkt die neue Referenz.

## UX Model

Dieser Slice ist kein neuer sichtbarer Dashboard-Ausbau. Er macht die vorhandene UX robuster:

1. Root-Dashboard rendert stabil.
2. Project Index erklaert seine Counts besser.
3. Zukuenftige Dashboard-Slices koennen die Helper-Konvention nachlesen, statt Muster aus alten Blocks zu erraten.

## Data and Implementation Constraints

1. Quelle der Wahrheit bleiben Entity Notes unter `_shared/SpecOps/Entities/`.
2. DataviewJS bleibt erlaubt.
3. Helper werden fuer diesen Slice als copy-paste-sichere lokale Blockfunktionen dokumentiert, nicht als geteiltes Runtime-Modul umgesetzt.
4. Keine neuen Pflichtfelder in Entity Notes.
5. Fehlende Felder werden defensiv angezeigt.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice behebt ein renderkritisches Helper-Problem, macht Project-Index-Counts expliziter und dokumentiert eine wartbare DataviewJS-Konvention. Er veraendert nur Markdown-/DataviewJS-Dashboard-Dateien, eine SpecOps-Reference-Datei und die zugehoerige Spec-Evidence.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/project-index.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Reference/dashboard-helper-patterns.md`
4. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/specops-dashboard-helper-pattern-count-semantics.md`
5. Diese Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Obsidian Dataview und DataviewJS bleiben lokale Anzeigevoraussetzungen.

### Datenmigration/Fallback

Keine Datenmigration. Bestehende Detailtabellen bleiben erhalten.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Alle Daten bleiben lokal im DanielsVault.

### Abnahmekriterien Go/No-Go

Go:

1. `Dashboard.md` `Needs Attention` rendert ohne blockuebergreifende Helper-Annahme.
2. `project-index.md` zeigt Project Entity und Project Key / Count Key explizit.
3. Dashboard Helper Pattern Reference existiert und ist verlinkt.
4. DataviewJS-Syntaxcheck laeuft gruen.
5. Verification Commands laufen mit Exit-Code `0`, ausser explizit negative Guards.

No-Go:

1. Ein neues Runtime-Modul oder Plugin wird eingefuehrt.
2. Alle Dashboards werden opportunistisch refaktoriert.
3. Count-Semantik bleibt implizit.
4. Der renderkritische `Needs Attention`-Block bleibt abhaengig von einem anderen DataviewJS-Block.

### Owner fuer offene Risiken

1. User: Obsidian-Review, ob Project-Index-Count-Labels verstaendlich sind.
2. Codex: Markdown-/DataviewJS-Struktur, Reference-Dokument und Shell-Verifikation.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `rg` ist installiert und wird fuer Textchecks verwendet.
4. `node` ist installiert und wird fuer DataviewJS-Syntaxchecks verwendet.
5. Obsidian-Rendering bleibt ein manuelles Review-Signal.

Pflichtchecks fuer einen spaeteren Implementation-Slice:

1. `test -f _shared/SpecOps/Dashboard.md`
2. `test -f _shared/SpecOps/Dashboards/project-index.md`
3. `test -f _shared/SpecOps/Reference/dashboard-helper-patterns.md`
4. `rg -n 'function linkEl' _shared/SpecOps/Dashboard.md`
5. `rg -n 'const countKey|Project Key|Project Entity' _shared/SpecOps/Dashboards/project-index.md`
6. `rg -n 'DataviewJS blocks are isolated|linkEl|Card|Grid|Metric|countKey' _shared/SpecOps/Reference/dashboard-helper-patterns.md`
7. `rg -n 'dashboard-helper-patterns' _shared/SpecOps/Dashboard.md`
8. DataviewJS syntax check:

```bash
node - <<'NODE'
const fs = require('fs');
const files = [
  '_shared/SpecOps/Dashboard.md',
  '_shared/SpecOps/Dashboards/project-index.md',
];
let count = 0;
for (const file of files) {
  const text = fs.readFileSync(file, 'utf8');
  const blocks = [...text.matchAll(/```dataviewjs\n([\s\S]*?)\n```/g)];
  for (const [idx, block] of blocks.entries()) {
    count++;
    try {
      new Function('dv', block[1]);
    } catch (err) {
      console.error(`${file} block ${idx + 1}: ${err.message}`);
      process.exitCode = 1;
    }
  }
}
if (!process.exitCode) console.log(`Parsed ${count} dataviewjs blocks`);
NODE
```

9. Needs Attention local-helper check:

```bash
node - <<'NODE'
const fs = require('fs');
const text = fs.readFileSync('_shared/SpecOps/Dashboard.md', 'utf8');
const match = text.match(/## Needs Attention[\s\S]*?```dataviewjs\n([\s\S]*?)\n```/);
if (!match) {
  console.error('Needs Attention dataviewjs block not found');
  process.exit(1);
}
if (!/function linkEl\s*\(/.test(match[1])) {
  console.error('Needs Attention block lacks local linkEl helper');
  process.exit(1);
}
console.log('Needs Attention block has local linkEl helper');
NODE
```

Success Criteria:

1. Positive checks 1-9 geben Exit-Code `0` zurueck.
2. Manuelles Obsidian-Review bestaetigt, dass Root-Dashboard und Project Index rendern.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run, wenn:

1. keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen sind,
2. der Slice als Dashboard-only/Reference-doc Change behandelt wird,
3. die Verification Commands als DoD-Basis akzeptiert werden.

Aktueller Stand: bereit fuer Umsetzung.

## Review

Autorenreview am 2026-05-05:

1. Scope deckt die drei Review-Findings ab: P1 renderkritischer Helper, P2 Count-Semantik, P3 Helper-Pattern-Dokumentation.
2. Scope bleibt klein: keine Runtime-Module, keine Plugins, keine vollstaendige Dashboard-Refaktorierung.
3. Keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen.
4. Verification Commands enthalten Existenzchecks, Strukturchecks, DataviewJS-Syntaxcheck und einen Node-Check fuer lokale Helper-Isolation im `Needs Attention`-Block.
5. Ergebnis: keine offenen Review-Findings.

## Implementation Evidence

Direct-Mode-Umsetzung am 2026-05-05:

1. `Dashboard.md` `Needs Attention` enthaelt einen lokalen `linkEl`-Helper.
2. `project-index.md` nutzt `countKey = project.project ?? project.title ?? project.file.name` fuer Specs, Active Specs, Backlog und Metadata Attention.
3. Project Index zeigt `Project Entity` und `Project Key` sichtbar auf den Karten.
4. `_shared/SpecOps/Reference/dashboard-helper-patterns.md` dokumentiert isolierte DataviewJS-Bloecke, `linkEl`, Card/Grid/Metric und `countKey`.
5. Root-Dashboard verlinkt `[[Reference/dashboard-helper-patterns]]`.

Verification Status:

| Check | Status | Evidence |
|---|---|---|
| `test -f _shared/SpecOps/Dashboard.md` | ran-target | Exit-Code `0` |
| `test -f _shared/SpecOps/Dashboards/project-index.md` | ran-target | Exit-Code `0` |
| `test -f _shared/SpecOps/Reference/dashboard-helper-patterns.md` | ran-target | Exit-Code `0` |
| `rg -n 'function linkEl' _shared/SpecOps/Dashboard.md` | ran-target | Vier lokale Helper gefunden, inklusive `Needs Attention` |
| `rg -n 'const countKey\|Project Key\|Project Entity' _shared/SpecOps/Dashboards/project-index.md` | ran-target | `countKey`, `Project Entity`, `Project Key` gefunden |
| `rg -n 'DataviewJS blocks are isolated\|linkEl\|Card\|Grid\|Metric\|countKey' _shared/SpecOps/Reference/dashboard-helper-patterns.md` | ran-target | Alle Pattern-Begriffe gefunden |
| `rg -n 'dashboard-helper-patterns' _shared/SpecOps/Dashboard.md` | ran-target | Root-Reference-Link gefunden |
| DataviewJS syntax check | ran-target | `Parsed 5 dataviewjs blocks` |
| Needs Attention local-helper check | ran-target | `Needs Attention block has local linkEl helper` |

Runtime Validation:

1. Obsidian-Dataview-Rendering ist fuer diesen Markdown-only Slice das relevante Runtime-Signal.
2. Shell-seitig wurden DataviewJS-Syntax und blocklokale Helper-Isolation gruen geprueft.
3. Docker/Health Checks und `check-build-watcher` sind nicht anwendbar, weil kein NCG-Backend, kein Service und kein Build-Pipeline-Pfad im Scope beruehrt wurde.
4. Visuelle Obsidian-Sichtpruefung bleibt das Review-Signal fuer Acceptance/Closeout.

## Closeout Evidence

Closeout am 2026-05-05:

1. User hat den Change akzeptiert.
2. Alle neun Verification Commands wurden im Closeout erneut mit Exit-Code `0` ausgefuehrt.
3. `openspec list --json` zeigte keinen zugehoerigen aktiven OpenSpec-Change fuer diesen Direct-Mode-Slice; kein OpenSpec-Archiv war erforderlich.
4. Der lokale SpecOps-Dokumentationsstand wurde synchronisiert:
   - Backlog-Entity `specops-dashboard-helper-pattern-count-semantics` auf `done` gesetzt.
   - Spec-Entity `specops-dashboard-helper-pattern-count-semantics-2026-05-05` angelegt.
   - Source Inventory um die akzeptierte narrative Spec ergaenzt.
5. RAG-Closeout-Recherche (`rag workflow spec-closeout --scope all`) lieferte nur unspezifische NCG-Treffer; exakte `rg`-Recherche fand relevante Referenzen nur in SpecOps/Shared-AI-Docs.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Review-Findings fuer Needs-Attention-Helper, Project-Count-Semantik und Helper-Duplikation als neue Spec freigegeben. |
| 2026-05-05 | Codex | Erste Spec fuer Dashboard Helper Pattern and Count Semantics erstellt und reviewt. |
| 2026-05-05 | Codex | Scope Contract im Direct Mode fixiert und Status auf Plan gesetzt. |
| 2026-05-05 | Codex | Direct-Mode-Implementierung abgeschlossen, alle Spec-Verification-Commands gruen ausgefuehrt und Status auf Implemented gesetzt. |
| 2026-05-05 | User + Codex | Change akzeptiert, Closeout-Verifikation erneut gruen replayt und Status auf Accepted gesetzt. |

SessionId: codex-desktop-current-thread
