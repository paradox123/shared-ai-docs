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
- `retro-plan`

Hier werden die gemeinsamen Begriffe gepflegt:
- **Definition of Ready (DoR)**
- **Definition of Done (DoD)**
- **Decision Freeze Pack**

Die Skills dürfen diese Begriffe lokal kurz restaten, sollen aber **keine abweichenden Definitionen** einführen. Änderungen an der gemeinsamen Bedeutung werden zuerst hier gepflegt.

## End-to-End Pipeline

```
Prompt (Kernanforderungen)
  | Iteration 0
  v
doc-coauthoring  ->  Spec/Proposal/Decision Doc
  | "refine the plan"
  v
refine-plan      ->  Implementierungsplan + Verification Cases
  | Scope/Impact Check
  |-- direkter Plan-Track
  |-- optional: OpenSpec-Track (wenn vom User gewünscht)
  v
Implementierung + Verifikation (tests + runtime + smoke)
  v
retro-plan + improve-skills (Feedback in Workflow/Skills)
```

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
4. Jede Iteration endet mit:
   - Was wurde entschieden?
   - Was bleibt offen?
   - Welche Evidenz fehlt noch?
5. Keine "Hybrid-Steuerung": entweder OpenSpec bewusst als SSOT oder bewusst ohne OpenSpec.

## Marker System

| Marker | Bedeutung | Verwendung |
|--------|-----------|-----------|
| `[MISSING ...]` | Fehlende Information | Spec/Plan |
| `[DECISION ...]` | Offene Wahl | Spec/Plan |
| `[REVIEW ...]` | Prüfen/Validieren | Spec |
| `[MISSING SPEC ...]` | Spezifikationslücke | Plan |
| `[DECISION SPEC ...]` | Spezifikationsentscheidung offen | Plan |
| `[BLOCKED ...]` | Externer Blocker | Plan/OpenSpec Tasks |

## Iteration, History, SessionId

Weiterhin append-only:

1. `Iteration 0` = Initialanforderung.
2. `Iteration N` = jede Verfeinerung.
3. Keine Überschreibung alter Iterationen.
4. History Table am Dateiende pflegen.
5. SessionId am Dateiende pflegen.

## File Conventions

| Typ | Ort | Muster |
|-----|-----|--------|
| Spezifikation (ohne OpenSpec) | `_specs/` | `YYYY-MM-DD <Titel>.md` |
| Plan | neben Spec oder Projektordner | `<name>-plan.md` |
| OpenSpec Change (optional) | `openspec/changes/<change>/` | Standard-Artefakte |
| Retro | inline im Plan oder eigene Datei | `<name>-retro.md` |

## Übergänge

### Spec -> Plan
"refine the plan" erst, wenn blockierende `[MISSING]`/`[DECISION]` minimiert sind.

### Plan -> Umsetzung
Nur bei erfüllter Definition of Ready.

### Umsetzung -> Retro
"retro the plan" nach jedem signifikanten Meilenstein, "final retro the plan" vor Abschluss.

### Retro -> Improve Skills
Wiederkehrende Probleme als `improve-skills`-Kandidaten erfassen und in Workflow/Skills einarbeiten.

## Lightweight Checkliste vor Umsetzung

1. Ist der Scope klar abgegrenzt?
2. Sind Entscheidungen eingefroren (Decision Freeze Pack)?
3. Sind Test- und Runtime-Gates vorab definiert?
4. Ist eine Referenz-Baseline nötig und benannt (falls relevant)?
5. Sind externe Abhängigkeiten/Owner dokumentiert?
6. Ist klar, was "done" konkret bedeutet?
