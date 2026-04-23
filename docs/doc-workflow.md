# Documentation & Planning Workflow

Dieser Workflow erweitert die bestehende Skill-Pipeline um klare Planungs- und Verifikations-Gates, um Nacharbeiten zu reduzieren.

## Ziel

1. Anforderungen sauber erfassen.
2. Entscheidungen vor Umsetzung einfrieren.
3. Umsetzung nur mit überprüfbaren Gates starten.
4. Abweichungen und Learnings systematisch in Skills/Workflow zurückführen.

## Shared Gate Source of Truth

Dieses Dokument ist die **kanonische Quelle** für die gemeinsamen Delivery-Gates in:
- `doc-coauthoring`
- `refine-plan`
- `spec-change-delivery`
- `spec-closeout`
- `doc-review-autoresolve`
- `retro-plan`

Hier werden die gemeinsamen Begriffe gepflegt:
- **Definition of Ready (DoR)**
- **Definition of Done (DoD)**
- **Decision Freeze Pack**

Die Skills dürfen diese Begriffe lokal kurz restaten, sollen aber **keine abweichenden Definitionen** einführen. Änderungen an der gemeinsamen Bedeutung werden zuerst hier gepflegt.

## Unterstützte Workflows

Beide Workflows sind offiziell unterstützt. Workflow 2 ist der aktuelle Default, Workflow 1 bleibt kompatibel nutzbar.

### Workflow 1 (Legacy-kompatibel)

```
Spec (`🟡 Spec`)
  v
refine-plan (iterativ, plan history)
  v
direct-mode implementation
  v
retro-plan (optional)
```

### Workflow 2 (Current)

```
Spec (`🟡 Spec`)
  v
spec-change-delivery (direct oder OpenSpec) -> Scope Contract (`🟠 Plan`)
  v
Implementierung + Verifikation (`🔵 Implemented`)
  v
retro-plan (optional)
  v
spec-closeout (optional, für formalen Abschluss) (`🟢 Accepted`)
```

## Workflow Selection (ohne Zwangsumstellung)

1. Wenn der User explizit Workflow 1 oder Workflow 2 nennt, diesem Pfad folgen.
2. Wenn ein bestehendes Artefakt bereits klar einen Pfad nutzt, auf demselben Pfad bleiben.
3. Ohne klare Vorgabe:
   - für neue Deliveries Workflow 2 bevorzugen,
   - für laufende ältere Threads Workflow 1 beibehalten.
4. Ein Wechsel ist nur bei expliziter User-Entscheidung sinnvoll.

## Spec Header Contract (verpflichtend)

Jede Spec muss mit diesem Header starten:

```md
**Date:** 2026-03-03  
**Status:** 🟡 Spec
**Scope:** Automated deployment validation and self-healing for NCG backend on Hetzner infrastructure

---
```

Regeln:
1. `Date` im Format `YYYY-MM-DD` (Erstellungsdatum der Spec).
2. `Scope` als prägnanter Einzeiler.
3. `Status` nur aus dieser Liste:
   - `🟡 Spec` - Spec wird erstellt/verfeinert (`doc-coauthoring`)
   - `🟠 Plan` - umsetzbarer Plan existiert (aus `refine-plan` oder `spec-change-delivery`)
   - `🔵 Implemented` - Umsetzung plus Artefakte/Evidenz liegt vor
   - `🟢 Accepted` - formaler Abschluss erfolgt (typisch via `spec-closeout`)

## Status Ownership by Workflow

1. In beiden Workflows:
   - `doc-coauthoring` erstellt Header (falls fehlend) und setzt `🟡 Spec`.
2. Workflow 1:
   - `refine-plan` kann auf `🟠 Plan` setzen, sobald ein umsetzbarer Plan vorliegt.
   - der ausführende Implementierungs-Run (direct mode) setzt auf `🔵 Implemented`, sobald Evidenz vorliegt.
   - `spec-closeout` ist optional; bei erfolgreichem formalem Abschluss wird `🟢 Accepted` gesetzt.
3. Workflow 2:
   - `spec-change-delivery` setzt auf `🟠 Plan` (Scope Contract fixiert) und später auf `🔵 Implemented` (Umsetzung + Evidenz).
   - `spec-closeout` setzt auf `🟢 Accepted`, wenn Verifikation/Closeout vollständig erfolgreich sind.

## Skills und Verantwortung

### `doc-coauthoring`

Purpose: Anforderungen, Scope, Constraints, Akzeptanzkriterien.

Lieferobjekt:
- belastbare Spec mit `[MISSING ...]`, `[DECISION ...]`, `[REVIEW ...]`
- klare Non-Goals

### `refine-plan`

Purpose: Aus Spec einen ausführbaren Plan machen.

Lieferobjekt:
- status-bearing actions (`[DONE]`, `[PENDING]`, `[BLOCKED]`)
- konkrete Verification Cases pro Teilbereich
- offene Spec-Lücken explizit als `[MISSING SPEC ...]`/`[DECISION SPEC ...]`
- primärer Plan-Track für Workflow 1 (iterativ)

### `spec-change-delivery`

Purpose: Einen klar abgegrenzten Change aus der Spec implementieren und verifizieren.

Lieferobjekt:
- Scope Contract (direct oder OpenSpec)
- umgesetzte Artefakte + Verifikationsnachweise
- primärer Delivery-Track für Workflow 2 inkl. Spec-Statusupdate auf `🟠 Plan` und später `🔵 Implemented`

### `spec-closeout`

Purpose: Akzeptierten Change formal abschließen und dokumentarisch synchronisieren.

Lieferobjekt:
- vollständiger Verifikations-Checklist-Report
- OpenSpec Close/Archivierung (falls genutzt)
- Spec-Statusupdate auf `🟢 Accepted`

### `doc-review-autoresolve`

Purpose: Review-Findings in Specs/Dokus autonom auflösen und direkt gegenprüfen, um Rework-Schleifen zu verkürzen.

Lieferobjekt:
- Findings-first Review mit file/line Referenzen
- automatische Behebung aller sicher entscheidbaren Inkonsistenzen im selben Run
- unmittelbarer Re-Review nach Edits (Loop bis stabil)
- Eskalation nur für echte Entscheidungs-/Informationslücken (`[MISSING ...]`, `[DECISION ...]`, blockierende `[REVIEW ...]`)

### `retro-plan`

Purpose: Ergebnis gegen Plan prüfen und Deltas erfassen.

Lieferobjekt:
- Root-Cause-Analyse
- Follow-up-Deltas für Spec/Plan/Umsetzung

### `improve-skills`

Purpose: wiederkehrende Reibungsmuster identifizieren und dauerhaft reduzieren.

Im Kontext dieses Workflows:
- wiederholte Nacharbeiten klassifizieren
- fehlende/unklare Entscheidungspunkte dokumentieren
- Workflow-/Skill-Anpassungen ableiten

## OpenSpec Nutzung (optional)

OpenSpec ist **optional** und wird **vom User entschieden**.

OpenSpec ist typischerweise hilfreich bei:

1. größeren oder mehrstufigen Vorhaben,
2. mehreren beteiligten Teams/Repos,
3. Bedarf nach formalen Artefakten und Audit-Trace,
4. länger laufenden Changes mit Blockern und Teilfortschritt.

Für kleinere oder klar abgegrenzte Änderungen reicht oft der direkte Plan-Track ohne OpenSpec.

## Definition of Ready (vor Implementierung)

Implementierung startet erst, wenn alle Punkte erfüllt sind:

1. Scope in 1-2 Sätzen fixiert.
2. Non-Goals explizit dokumentiert.
3. Decision Freeze Pack ausgefüllt (siehe unten).
4. Referenz-Baseline benannt (**falls relevant**).
5. Testfälle/Abnahmeszenarien vorab definiert, die den späteren DoD nachweisbar machen.
6. Verifikationskommandos vorab definiert:
   - Unit/Integration Tests
   - Runtime/Compose Start
   - Health/Smoke Checks
7. Offene Risiken, Abhängigkeiten und Blocker sind dokumentiert.

## Decision Freeze Pack (kontextabhängige Checkliste)

Vor der Implementierung die **relevanten** Punkte fixieren:

1. Zielbild und Scope in 1-2 Sätzen.
2. betroffene Umgebungen/Branches (**falls relevant**).
3. Secret-/Config-Contract (**falls relevant**).
4. Datenmigration/Fallback (**falls relevant**).
5. externe Integrationsverträge zu anderen Systemen/Repos (**falls relevant**).
6. Sicherheits-/Exposure-Entscheidungen (**falls relevant**).
7. Abnahmekriterien (Go/No-Go).
8. Owner für offene Abhängigkeiten/Risiken.
9. Nachweisformat (welche Evidenzdatei, welche Kommandos).

## OpenSpec Artifact Contract (nur wenn OpenSpec aktiv)

Mindestens diese Artefakte müssen konsistent sein:

1. `proposal.md` - Why/What/Impact
2. `design.md` - Entscheidungen und Trade-offs
3. `tasks.md` - nur echte, überprüfbare Tasks; Blocker explizit offen lassen
4. `specs/*/spec.md` - Requirements + Scenarios
5. `acceptance-criteria-matrix.md` - `pass/fail/blocked`
6. `implementation-evidence.md` - konkrete Kommandos + Resultate

Regel:
- **`[BLOCKED]` ist nicht `done`**
- Teilweise Umsetzung nicht als abgeschlossen markieren

## Definition of Done (Release Gate)

Ein Change ist erst "done", wenn:

1. relevante Findings und Risiken geklärt, mitigiert oder explizit akzeptiert sind.
2. die in DoR definierten Testfälle ausgeführt und dokumentiert sind.
3. definierte Tests erfolgreich sind.
4. Runtime-Validierung erfolgreich ist (z. B. `docker compose up` + Health).
5. offene Blocker klar dokumentiert sind (inkl. Impact/Nächster Schritt).
6. Akzeptanzkriterien mit Evidenz belegt sind.
7. Specs/Plan/OpenSpec-Artefakte synchron sind (kein Drift).

## Anti-Rework Guardrails

1. Keine Umsetzung starten, solange zentrale Entscheidungen noch "im Fluss" sind.
2. Größere Vorhaben in mehrere Changes/Arbeitspakete splitten (z. B. nach Themenclustern oder Risiko).
3. Referenz-Implementierung/Baseline früh festlegen und diffen (**falls relevant**).
4. Jede Arbeitsphase endet mit:
   - Was wurde entschieden?
   - Was bleibt offen?
   - Welche Evidenz fehlt noch?
5. Keine "Hybrid-Steuerung": entweder OpenSpec bewusst als SSOT oder bewusst ohne OpenSpec.
6. Review-Findings werden standardmäßig per `doc-review-autoresolve` erst **autonom behoben**, dann **erneut reviewed**; Rückfrage nur bei echten Entscheidungs-/Missing-Blockern.

## Marker System

| Marker | Bedeutung | Verwendung |
|--------|-----------|-----------|
| `[MISSING ...]` | Fehlende Information | Spec/Plan |
| `[DECISION ...]` | Offene Wahl | Spec/Plan |
| `[REVIEW ...]` | Prüfen/Validieren | Spec |
| `[MISSING SPEC ...]` | Spezifikationslücke | Plan |
| `[DECISION SPEC ...]` | Spezifikationsentscheidung offen | Plan |
| `[BLOCKED ...]` | Externer Blocker | Plan/OpenSpec Tasks |

## Review-Findings Auto-Resolution Policy

Default bei Review-Arbeit:
1. Findings erfassen.
2. Alle sicher entscheidbaren Findings ohne Zusatzfreigabe direkt beheben.
3. Im gleichen Run re-reviewen.
4. Wiederholen, bis keine autonomen Findings mehr offen sind.

Eskalation an den User nur wenn:
- mehrere fachlich unterschiedliche Lösungen möglich sind,
- Sicherheits-/Policy-Entscheidungen betroffen sind,
- oder Marker-basierte Entscheidungslücken bestehen (`[MISSING ...]`, `[DECISION ...]`, blockierende `[REVIEW ...]`).

## History und SessionId (verpflichtend)

History und SessionId bleiben verpflichtend, aber ohne Iterationssystem.

1. Jede Spec hat am Dateiende eine append-only History-Tabelle im Format:
   - `| Date | Author | Change |`
2. Jede History-Zeile beschreibt die jeweilige Anpassung in genau einem kurzen Satz.
3. Keine Iterationsspalte und keine Iterationsnummern verwenden.
4. Vorhandene Iterations-History bei Berührung auf das 3-Spalten-Format migrieren.
5. `SessionId` am Dateiende beibehalten; falls fehlend, ergänzen als `SessionId: <session-id>`.
6. Statuswechsel (`🟡 Spec` / `🟠 Plan` / `🔵 Implemented` / `🟢 Accepted`) müssen jeweils mit einer passenden neuen History-Zeile dokumentiert werden.

Hinweis:
- Diese History-Regel gilt für **Spec-Dateien**.
- Iterative History in **Plan-Dateien** (z. B. `refine-plan`) bleibt davon unberührt.

## File Conventions

| Typ | Ort | Muster |
|-----|-----|--------|
| Spezifikation (ohne OpenSpec) | `_specs/` | `YYYY-MM-DD <Titel>.md` |
| Plan | neben Spec oder Projektordner | `<name>-plan.md` |
| OpenSpec Change (optional) | `openspec/changes/<change>/` | Standard-Artefakte |
| Retro | inline im Plan oder eigene Datei | `<name>-retro.md` |

## Übergänge

### Spec -> Plan
Workflow 1: `refine-plan` iterativ; bei implementierungsreifem Plan Status `🟠 Plan`.
Workflow 2: `spec-change-delivery` setzt Status `🟠 Plan`, sobald der Scope Contract fixiert ist.

### Plan -> Umsetzung
Nur bei erfüllter Definition of Ready. Nach ausgeführter Umsetzung mit Artefakten: Status `🔵 Implemented`.

### Umsetzung -> Accepted
In beiden Workflows optional über `spec-closeout`: Status `🟢 Accepted`, wenn Verifikation vollständig grün ist und (falls aktiv) OpenSpec archiviert wurde.

### Umsetzung -> Retro
"retro the plan" nach jedem signifikanten Meilenstein, "final retro the plan" vor Abschluss.

### Review Findings -> Auto-Resolve
Bei Findings aus Review-Runden zuerst `doc-review-autoresolve` ausführen (fix + re-review loop). Erst verbleibende Entscheidungs- oder Missing-Blocker an den User eskalieren.

### Retro -> Improve Skills
Wiederkehrende Probleme als `improve-skills`-Kandidaten erfassen und in Workflow/Skills einarbeiten.

## Lightweight Checkliste vor Umsetzung

1. Ist der Scope klar abgegrenzt?
2. Sind Entscheidungen eingefroren (Decision Freeze Pack)?
3. Sind Test- und Runtime-Gates vorab definiert?
4. Ist eine Referenz-Baseline nötig und benannt (falls relevant)?
5. Sind externe Abhängigkeiten/Owner dokumentiert?
6. Ist klar, was "done" konkret bedeutet?
