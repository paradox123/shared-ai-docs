**Date:** 2026-05-05
**Status:** 🟡 Spec
**Scope:** SpecOps Environment Tracking Model Klaerung fuer projekt-/release-spezifische Environment-Signale, ohne freischwebende Stage-Taxonomie

---

## Kontext

Die SpecOps Parent-Spec trennt bewusst mehrere Statusachsen. Spec-Status, Artefakt-Status, Verification-Status und Environment-Status duerfen nicht ineinanderfallen.

Aktuell existieren bereits reale Environment-Signale in Spec-Entities:

1. `environment_local: verified`
2. `environment_local: partially_validated`

Gleichzeitig ist `_shared/SpecOps/Entities/environments/` noch leer und es gibt noch kein Environment-Dashboard. Das bestehende Backlog-Item `environment-tracking-model` ist dafuer triaged und hat als Trigger:

1. Eine Spec hat separate lokale, Dev-, Staging- oder Prod-Zustaende.
2. Release Evidence braucht environment-level distinction.

Dieser Slice promoted ausschliesslich das bestehende Backlog-Item `environment-tracking-model` mit `candidate_slice: SpecOps Environment Board`.

Wichtige Modellgrenze:

1. Nicht alle Projekte haben dieselben Stages.
2. Diese Child-Spec darf keine freischwebende globale Stage-Taxonomie wie `local/dev/staging/prod` als verbindliches Modell einfuehren.
3. Die Hauptspec muss zuerst klaeren, ob Environments als globale Entities, projektbezogene Labels, releasebezogene Felder oder workflow-/skill-getriebene Registrierungen modelliert werden.
4. Bis diese Parent-Entscheidung steht, darf diese Child-Spec nur bestehende Environment-Signale sichtbar machen und offene Modellfragen festhalten.

## Ziel

SpecOps soll Environment-Zustaende sichtbar machen, ohne sie mit Spec-Lifecycle oder Release-Status zu vermischen und ohne projektuebergreifend identische Stages vorauszusetzen.

Nach diesem Slice soll beantwortbar sein:

1. Welche Specs haben lokale Environment-Signale?
2. Welche Environment-/Stage-Begriffe tauchen bereits als Signale auf?
3. Welche Specs sind lokal verified, partially validated, missing oder blocked?
4. Welche Evidence stuetzt den Environment-Zustand?
5. Welche Environment-Felder fehlen noch und sollen in Missing Metadata sichtbar bleiben?

## In Scope

1. Analyse und Sichtbarmachung bestehender Spec-Felder `environment_local`, `evidence`, `project`, `status`, `metadata_quality`.
2. Environment-Dashboard unter `_shared/SpecOps/Dashboards/environments.md`, das vorhandene Signale projektbezogen zeigt.
3. Root-Dashboard-Verweis auf die Environment-Sicht.
4. Backlog-Item `environment-tracking-model` mit dieser Child-Spec verknuepfen.
5. Explizite Parent-Spec-Frage fuer spaetere Environment-/Release-/Skill-Integration festhalten.

## Out of Scope

1. Keine echten Deployments oder Runtime-Aenderungen.
2. Keine Docker-/Health-Checks als neue Umgebungsmessung.
3. Keine Release-Entity-Implementierung.
4. Keine globale Stage-Taxonomie.
5. Keine Pflichtannahme, dass alle Projekte `dev`, `staging` oder `prod` haben.
6. Keine Aenderung an Spec-Lifecycle-Status.
7. Keine automatische Environment-Erkennung.
8. Keine Skill-/Agent-/Learning-Integration.
9. Keine historische Vollmigration.

## Requirements

### R1 - Environment Signal View

Vorhandene Environment-Signale muessen sichtbar werden, ohne daraus bereits ein verbindliches Entity-Modell abzuleiten.

Akzeptanzkriterien:

1. Die View verwendet bestehende `environment_*` Felder aus Spec-Entities.
2. Die View gruppiert oder sortiert nach Projekt, damit unterschiedliche Stage-Landschaften sichtbar bleiben.
3. Fehlende Environment-Felder werden nicht als verified, dev, staging oder prod interpretiert.
4. Die Spec dokumentiert, dass ein spaeteres Entity-Modell von der Hauptspec entschieden werden muss.

### R2 - Environment Dashboard

SpecOps muss lokale Environment-Signale in einer eigenen View sichtbar machen.

Akzeptanzkriterien:

1. `_shared/SpecOps/Dashboards/environments.md` existiert.
2. Die View zeigt Specs mit `environment_local`.
3. Die View zeigt mindestens `project`, `status`, `environment_local`, `evidence`, `metadata_quality` und `source`.
4. Die View trennt Environment-Signale von Spec-Lifecycle-Boards.
5. Die View behauptet keine nicht vorhandenen Projekt-Stages.

### R3 - Local Environment Coverage

Der Slice muss reale vorhandene `environment_local`-Felder auswerten.

Akzeptanzkriterien:

1. Specs mit `environment_local: verified` sind in der Environment-Sicht auffindbar.
2. Specs mit `environment_local: partially_validated` sind in der Environment-Sicht auffindbar.
3. Specs ohne `environment_local` werden nicht als verified dargestellt.
4. Missing oder inferred Metadaten bleiben in bestehenden Missing-Metadata-Sichten sichtbar.

### R4 - Parent Model Discipline

Das langfristige Environment-/Release-/Workflow-Modell gehoert in die Hauptspec oder eine dedizierte Parent-Entscheidung, nicht in diese Child-Spec.

Akzeptanzkriterien:

1. Die Child-Spec enthaelt einen offenen Parent-Decision-Marker fuer das Environment-/Release-/Workflow-Modell.
2. Die Child-Spec ist nicht implementation-ready, solange diese Parent-Entscheidung offen ist.
3. Spaetere Release- oder Skill-Registrierungsablaeufe werden nicht in diesem Slice festgelegt.

### R5 - Backlog Discipline

Der Slice bleibt an das bestehende Backlog-Item gebunden.

Akzeptanzkriterien:

1. `environment-tracking-model` ist mit dieser Spec verlinkt.
2. Release-Traceability bleibt im Backlog-Item `release-entity-records`.
3. Neue Environment-Ideen, die ueber den lokalen Pilot hinausgehen, werden nicht direkt umgesetzt.

## Decision Freeze Pack

### Zielbild und Scope

Dieser Slice klaert die Grenze fuer Environment Tracking. Er darf vorhandene Environment-Signale sichtbar machen, aber kein verbindliches projektuebergreifendes Stage-Modell einfuehren. Die Entscheidung, ob Environments spaeter globale Entities, projektbezogene Labels, Release-Felder oder Workflow-/Skill-Registrierungen sind, gehoert zur Parent-Spec.

### Betroffene Vault-Bereiche

1. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboards/`
2. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Dashboard.md`
3. `/Users/dh/Documents/DanielsVault/_shared/SpecOps/Entities/backlog/environment-tracking-model.md`
4. Diese Child-Spec unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/`

### Secret-/Config-Contract

Keine Secrets. Alle Daten bleiben lokal im DanielsVault.

### Datenmigration/Fallback

Keine Migration. Bestehende `environment_local` Felder werden nur gelesen. Fehlende Environment-Felder bleiben fehlend und werden nicht kuenstlich inferred. Keine Environment Entity Notes werden verbindlich eingefuehrt, solange die Parent-Entscheidung offen ist.

### Externe Integrationen

Keine externen Integrationen.

### Sicherheits-/Exposure-Entscheidungen

Keine Exposure-Aenderung. Es werden keine Environment-Daten an externe Systeme synchronisiert.

### Abnahmekriterien Go/No-Go

Go:

1. Environment Dashboard existiert und nutzt Dataview.
2. Root-Dashboard referenziert die Environment View.
3. Vorhandene `environment_local` Werte sind sichtbar.
4. Backlog-Item `environment-tracking-model` ist mit dieser Spec verlinkt.
5. Release-Entities oder echte Deployment-Status werden nicht nebenbei eingefuehrt.
6. Parent-Entscheidung zur Environment-/Release-/Workflow-Modellierung bleibt sichtbar offen.

No-Go:

1. Environment-Status wird mit Spec-Lifecycle-Status gleichgesetzt.
2. Fehlende Environment-Felder werden als verified dargestellt.
3. Der Slice erzeugt globale Stage-Entities ohne Parent-Entscheidung.
4. Der Slice erzeugt Release-Entities oder eine produktive Deployment-Matrix.
5. Der Slice veraendert Fachcode oder Runtime-Umgebungen.

### Owner fuer offene Risiken

1. User: Parent-Entscheidung, wie Environments spaeter im Release-/Skill-/Workflow-Kontext modelliert werden sollen.
2. Codex: Child-Spec konsistent halten und keine freischwebende Stage-Taxonomie einfuehren.

## Verifikationskommandos

Ausfuehrungskontext:

```bash
cd /Users/dh/Documents/DanielsVault
```

Shell-/Plattformvertrag:

1. Zielplattform ist macOS.
2. Shell ist `zsh`.
3. `rg` ist installiert und wird fuer Textchecks verwendet.

Pflichtchecks fuer einen spaeteren Implementation-Slice:

1. `test -f _shared/SpecOps/Dashboards/environments.md`
2. `rg -n 'FROM "_shared/SpecOps/Entities/specs"|environment_local|evidence|metadata_quality|source' _shared/SpecOps/Dashboards/environments.md`
3. `rg -n 'environment_local: verified|environment_local: partially_validated' _shared/SpecOps/Entities/specs`
4. `rg -n 'Dashboards/environments|Environments|Environment' _shared/SpecOps/Dashboard.md`
5. `rg -n 'status: promoted|promoted_to: .+2026-05-05 SpecOps Environment Tracking Model.md' _shared/SpecOps/Entities/backlog/environment-tracking-model.md`
6. `find _shared/SpecOps/Entities/releases -type f -name '*.md' | wc -l | tr -d ' '`
7. `find _shared/SpecOps/Entities/environments -type f -name '*.md' | wc -l | tr -d ' '`

Success Criteria:

1. Checks 1-5 geben Exit-Code `0` zurueck.
2. Check 6 muss `0` ausgeben, weil Release-Entities ausserhalb dieses Slices bleiben.
3. Check 7 muss `0` ausgeben, solange die Parent-Entscheidung zu Environment-Entities offen ist.
4. Manuelles Obsidian-/Dataview-Review bestaetigt, dass die Environment View sichtbar ist.

## Backlog Handling

1. Vor Erstellung dieser Child-Spec stand `environment-tracking-model` auf `triaged`.
2. Nach Erstellung dieser Child-Spec steht `environment-tracking-model` auf `promoted`.
3. Nach Umsetzung und erfolgreicher Verifikation darf das Backlog-Item auf `done` gesetzt werden.

## Implementation Readiness

Diese Spec ist bereit fuer einen anschliessenden Scope-Contract-/Delivery-Run, wenn:

1. die Parent-Entscheidung zur Environment-/Release-/Workflow-Modellierung getroffen ist,
2. keine blockierenden `[MISSING ...]` oder `[DECISION ...]` Marker offen sind,
3. die Verification Commands als DoD-Basis akzeptiert werden,
4. der Scope auf Environment-Sichtbarkeit ohne globale Stage-Taxonomie begrenzt bleibt.

Aktueller Stand: nicht implementation-ready.

[DECISION SPEC parent environment model] In der Hauptspec klaeren, ob Environments spaeter als globale Entities, projektbezogene Labels, Release-Felder oder Workflow-/Skill-Registrierungen modelliert werden. Diese Child-Spec darf bis dahin keine freischwebende Stage-Taxonomie definieren.

## Implementation Evidence

Noch nicht umgesetzt.

## History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-05 | User | Naechste MVP-Scope-Taetigkeit nach Backlog-/Hauptspec-Pruefung angefragt. |
| 2026-05-05 | Codex | Child-Spec fuer `environment-tracking-model` / `SpecOps Environment Board` erstellt. |
| 2026-05-05 | User | Klarstellung gegeben, dass Projekte unterschiedliche Stages haben und die Child-Spec kein freischwebendes Environment-Modell definieren soll. |
| 2026-05-05 | Codex | Spec auf Parent-Entscheidung fuer Environment-/Release-/Workflow-Modell zurueckgeschnitten und Implementation-Readiness entfernt. |

SessionId: codex-desktop-current-thread
