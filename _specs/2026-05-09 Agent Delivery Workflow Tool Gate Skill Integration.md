**Date:** 2026-05-09
**Status:** 🟡 Spec
**Scope:** Integration der Agent-Delivery-Workflow-Tools als Tool-Gates in bestehende Skills und Workflow-Dokumentation.
**SessionId:** workflow-tool-gate-skill-integration-spec

---

## Review Control Surface

- Spec-Variante: Normale, direkte Integrations-Spec; keine Parent/Child-Orchestrierung.
- Goldstandard Status: Gehärtet fuer spätere `spec-change-delivery`-Umsetzung im OpenSpec-Modus.
- Ziel: Skill-Prosa fuer Agent-Delivery-Workflow-Regeln reduzieren und durch konkrete Tool-Gates mit Stop/Continue-Regeln ersetzen, ohne den in `docs/doc-workflow.md` beschriebenen Workflow zu verändern.
- In Scope: `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`, `docs/doc-workflow.md`; Tool-Gate-Befehle fuer `EvaluateOrchestrationNextStep.cs`, `ValidateOrchestrationPack.cs`, `SyncChildHandoff.cs`, `ValidateChildReadiness.cs`, `WorkflowDoctor.cs`, `ValidateAgentDeliveryLaunchEvidence.cs`, `AgentDeliverySessionLauncher.cs`; Reduktion oder Ersatz alter paralleler Prosa-Regeln; explizite Wahrung der Workflow-Reihenfolge, Status-Ownership und Gate-Semantik aus `docs/doc-workflow.md`.
- Out of Scope: neue Tools entwickeln, bestehende Tool-CLI ändern, MD-E2E-Specs oder Handoffs ändern, breite Skill-Neuschreibung, Parent/Child-Spec-Orchestrierung, Runtime-/Produktimplementierung.
- Wichtigste Test-/Harness-Cases: Post-Orchestration-Gate routet zu Hardening; Pack-Validation blockiert stale/komprimierte Orchestration Packs; Handoff-Sync blockiert Drift; Pre-Delivery blockiert ohne Readiness- und Launch-Evidence; Closeout gibt nächsten Child erst nach Sync frei; Workflow-Preservation-Check bestätigt, dass Reihenfolge und Status-Ownership aus `docs/doc-workflow.md` unverändert bleiben.
- Wichtigste Verification Commands: alle Tool-`--help`/Usage-Commands; ein `EvaluateOrchestrationNextStep.cs` Smoke gegen die vorhandene MD-E2E-Fixture; `rg` checks auf Toolnamen in betroffenen Skills/Docs; `rg` checks auf Workflow-Reihenfolge/Status-Ownership; `git diff --check`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. `WorkflowDoctor.cs` bleibt optionaler Low-token Einstieg fuer `post-orchestration`; da seine aktuelle CLI nur diese Phase unterstützt, darf die Skill-Integration keine `pre-delivery`- oder `closeout`-Doctor-Phase voraussetzen.
- Readiness Status: READY FOR IMPLEMENTATION PLANNING.

## Source Of Truth

Diese Spec ist die Source of Truth fuer die spätere Skill-Integration. `docs/doc-workflow.md` bleibt die kanonische Gate- und Workflow-Quelle. Die Tools bleiben die Source of Truth fuer konkrete Gate-Entscheidungen innerhalb dieses Workflows. Nach Umsetzung sollen Skills keine zweite, parallele Entscheidungspolitik pflegen, die Tool-Ergebnisse neu interpretiert oder widerspricht.

Betroffene Dateien:

- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-orchestrator/SKILL.md`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/child-spec-hardening/SKILL.md`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-change-delivery/SKILL.md`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/spec-closeout/SKILL.md`
- `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/doc-workflow.md`

## Workflow Preservation Contract

Die spätere Umsetzung ist eine workflow-erhaltende Refaktorierung. Sie darf nicht aus der Summe der Skills einen neuen Workflow machen. Die Reihenfolge, Zuständigkeiten und Statusübergänge bleiben die aus `docs/doc-workflow.md`.

Diese Invarianten dürfen nicht verändert werden:

1. `docs/doc-workflow.md` bleibt die kanonische Gate-Quelle fuer beide unterstützten Workflows.
2. Workflow 1 bleibt legacy-kompatibel nutzbar; Workflow 2 bleibt der Default fuer neue Deliveries.
3. Der Parent/Child-Pfad bleibt: `spec-orchestrator` schneidet Childs, Coverage, Dependencies, Parallel-Lanes und Hardening Queue; `child-spec-hardening` härtet einzelne Child Specs bis zur Implementierungsreife; `spec-change-delivery` implementiert genau einen implementation-ready Child; `spec-closeout` ist der optionale formale Abschluss und synchronisiert Parent/Index/Backlog/Evidence/Next Handoff.
4. `spec-orchestrator` und `child-spec-hardening` halten Specs normalerweise im Status `🟡 Spec`; `spec-change-delivery` besitzt den Übergang zu `🟠 Plan` und später `🔵 Implemented`; `spec-closeout` setzt erst bei vollständiger Verifikation/Closeout auf `🟢 Accepted`.
5. `IMPLEMENTATION READY` oder bewusst akzeptierte `READY WITH NON-BLOCKING NOTES` bleiben die einzigen implementation-allowing Child-Hardening-Verdicts.
6. Der Child Index bleibt die operative Steuerzentrale fuer Parent/Child-Arbeit; er ersetzt weder OpenSpec noch `spec-change-delivery`-Scope-Contracts noch Closeout Evidence.
7. Ein `IMPLEMENTATION READY`-Hardening-Ergebnis bleibt ein Handoff-Punkt. Delivery startet danach nur bei ausdrücklicher User-Autorisierung oder in einem späteren `spec-change-delivery`-Run.
8. Closeout darf den nächsten führenden Child erst freigeben, wenn der vorige Child synchronisiert ist oder die Blockade/stale State explizit im Child Index und Handoff sichtbar ist.
9. Tools dürfen manuelle Prüfungen konkretisieren und deterministisch machen, aber keine zusätzlichen Workflow-Schritte, Statuswerte, Skill-Zuständigkeiten oder Abkürzungen einführen.
10. Wenn Tool-Ausgaben und `docs/doc-workflow.md` scheinbar kollidieren, ist das kein Anlass fuer lokale Skill-Policy. Die Umsetzung muss stoppen, die Inkonsistenz als Workflow-/Tool-Contract-Finding dokumentieren und eine separate Korrektur-Spec verlangen.

## Workflow Preservation Mapping

| Doc-Workflow-Konzept | Muss nach Tool-Integration gleich bleiben | Tool-Gate-Rolle |
|---|---|---|
| Workflow-Auswahl | Workflow 1/Workflow 2 werden nicht umgedeutet; diese Spec betrifft nur Agent-Delivery-Gates im bestehenden Workflow. | Keine Tool-Auswahl darf Workflow 1 auf Workflow 2 migrieren oder umgekehrt. |
| `spec-orchestrator` | Schneidet, priorisiert und empfiehlt den nächsten Child; meldet keine Implementierungsfreigabe ohne Hardening-Verdict. | `ValidateOrchestrationPack.cs` und `EvaluateOrchestrationNextStep.cs` validieren/benennen den nächsten erlaubten Workflow-Schritt. |
| `child-spec-hardening` | Erzeugt Vertragstiefe und implementation-allowing Verdicts, stoppt danach am Handoff. | `SyncChildHandoff.cs` und `ValidateChildReadiness.cs` prüfen dieselben Readiness-Bedingungen deterministisch. |
| `spec-change-delivery` | Implementiert genau einen implementation-ready Child und setzt Status gemäß Workflow 2. | `ValidateChildReadiness.cs` und `ValidateAgentDeliveryLaunchEvidence.cs` sind Pre-Edit-Gates, keine neuen Delivery-Schritte. |
| `spec-closeout` | Optionaler formaler Abschluss; synchronisiert Child/Parent/Index/OpenSpec/Evidence/Next Handoff vor `🟢 Accepted`. | `SyncChildHandoff.cs`, `AgentDeliverySessionLauncher.cs` und `ValidateAgentDeliveryLaunchEvidence.cs` konkretisieren die Next-Handoff-/Launch-Evidence-Prüfung. |
| Child Index | Operative Steuerzentrale, aber nicht Delivery-Ledger oder feingranulare Taskliste. | Pack-/Readiness-/Handoff-Tools prüfen und synchronisieren bestehende Index-Semantik. |

## Problem

Die Agent-Delivery-Skills enthalten inzwischen viel prose-basierte Workflow-Logik: exakte Child-Index-Spalten, Handoff-Staleness, Launch-Evidence, Readiness-Verdicts, Next-Action-Routing und Closeout-Sync. Diese Regeln waren wichtig, sind aber schwer wartbar und können neben den neuen Tools driften.

Die spätere Umsetzung soll die langen Regelblöcke auf kurze Gate-Anweisungen reduzieren: Tool ausführen, relevante Felder lesen, Stop/Continue-Regel anwenden, Ergebnis berichten. Wo Details weiterhin nötig sind, sollen sie als Tool-Input/Output-Contract oder als kurze Fallback-Erklärung stehen, nicht als zweite manuelle Policy.

## Goals

1. `spec-orchestrator` führt nach Erstellung/Aktualisierung von Child Index, Hardening Queue und Handoff zuerst strukturelle Pack-Validierung und danach Next-Step-Evaluation aus.
2. `child-spec-hardening` erzeugt/synchronisiert implementation-ready Handoffs mit `SyncChildHandoff.cs` und verankert `ValidateChildReadiness.cs` als finales Readiness-Gate.
3. `spec-change-delivery` nutzt `ValidateChildReadiness.cs` und `ValidateAgentDeliveryLaunchEvidence.cs` als Pre-Delivery-Stop-Gates, bevor Implementierungsdateien editiert werden.
4. `spec-closeout` synchronisiert den nächsten Handoff mit `SyncChildHandoff.cs`, erzeugt Queue-/Launch-Evidence mit `AgentDeliverySessionLauncher.cs` und validiert diese Evidence, bevor ein nächster Child als freigegeben gilt.
5. `docs/doc-workflow.md` beschreibt die Tool-Gates kompakt und entfernt oder kürzt wiederholte manuelle Regeln, ohne die Kontrollflächen zu verlieren.
6. Alle Skill-Änderungen bleiben mit Workflow-Auswahl, Status Ownership, Parent/Child-Reihenfolge, Handoff-Punkten und Closeout-Regeln aus `docs/doc-workflow.md` äquivalent.

## Non-Goals

- Keine Änderung an den Tool-Implementierungen oder ihren CLI-Contracts.
- Keine neue `WorkflowDoctor`-Policy. Der Doctor darf nur bekannte spezialisierte Tools bündeln und aktuell nur `post-orchestration` voraussetzen.
- Keine automatische Parent/Child-Orchestrierung fuer diese Spec.
- Keine Änderung an MD-E2E-Specs, Child-Handoffs, Fixtures oder laufenden Delivery-Artefakten, außer Verification-Smokes lesen vorhandene Fixture-Dateien.
- Keine neuen Launch-/Queue-Mechaniken in den Skills.
- Keine Änderung der Workflow-Reihenfolge, Skill-Zuständigkeiten, Status-Ownership, Statuswerte oder Implementierungsfreigabe-Semantik aus `docs/doc-workflow.md`.

## Verified CLI Contracts

Die folgenden Contracts wurden am 2026-05-09 per `dotnet run <tool> -- --help` bzw. aktueller Usage-Ausgabe geprüft.

### EvaluateOrchestrationNextStep.cs

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- \
  --pack <orchestration-pack.md> \
  --repo <repo> \
  --child-index-section "Child Index" \
  --intent <expects-hardening|expects-implementation-ready|hardening-queue-only|orchestration-only|stop-before-hardening|unknown> \
  --no-implementation \
  --format <json|markdown|both>
```

Supported additionally: `--fail-on-required-next-step`, `--help`.

Relevant outputs: `required_next_skill`, `first_unblocked_child`, `delivery_allowed`, `trigger_result`, `final_status_token`, `lane_classification`, `warnings`, `errors`.

Exit codes: `0` evaluation succeeded; `1` only when `--fail-on-required-next-step` finds a required next step; `2` invalid args/unreadable/malformed input.

### ValidateOrchestrationPack.cs

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack <orchestration-pack.md> \
  --repo <repo> \
  --child-index-section "Child Index" \
  --hardening-queue-section "Hardening Queue" \
  --format <json|markdown|both>
```

Supported additionally: `--allow-extra-columns`, `--help`.

Important verified absence: no `--require-handoffs` flag exists in the current CLI. Handoff expectations must be enforced by the validator's current findings and by `SyncChildHandoff.cs` / downstream gates, not by inventing this flag.

Exit codes: `0` no error findings; `1` validation found error findings; `2` invalid args/unreadable/missing required Child Index.

### SyncChildHandoff.cs

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/SyncChildHandoff.cs -- \
  --index <child-index-or-pack.md> \
  --child <child-id> \
  --out <handoff.md> \
  --target-repo <repo> \
  --parent <parent.md> \
  --timestamp <yyyy-MM-dd> \
  --check \
  --format json
```

Modes: exactly one of `--check`, `--dry-run`, `--write`.

Supported options: `--target-repo` (not `--repo`), `--parent`, `--timestamp`, `--format text|json`, `--allow-non-ready`, `--allow-approx-write-set`.

Important verified absence: no `--preserve-notes` flag and no `--format markdown|both`. Preservation behavior must rely on the tool's current controlled section / notes contract, not on a nonexistent flag.

### ValidateChildReadiness.cs

Current Usage contract:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index <child-index.md> \
  --child <child-id> \
  --handoff <handoff.md>
```

Supported options: `--allow-non-ready`, `--allow-extra-columns`.

Important verified behavior: passing `--help` currently prints usage but exits `2` because the tool does not expose a normal help flag. Later integration verification must either accept "usage printed with exit 2" for this existing tool or explicitly keep this as a known pre-existing CLI quirk. This Spec does not authorize changing the tool.

### WorkflowDoctor.cs

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/WorkflowDoctor.cs -- \
  --phase post-orchestration \
  --pack <orchestration-pack.md> \
  --repo <repo> \
  --child-index-section "Child Index" \
  --intent <intent> \
  --no-implementation \
  --format <json|markdown|both>
```

Supported additionally: `--fail-on-required-next-step`, `--help`.

Critical current scope: only `--phase post-orchestration` is supported. It runs `EvaluateOrchestrationNextStep.cs` only. It does not run pack validation, handoff sync, pre-delivery checks, closeout checks, skill integration, or agent launches.

### ValidateAgentDeliveryLaunchEvidence.cs

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- \
  --handoff <handoff.md> \
  --evidence <evidence.json> \
  --launch-request <launch-request.json> \
  --require-automatic
```

Also supports fixture mode:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- \
  --fixture <fixture-dir>
```

Relevant rules from Usage: automatic claims require matching target id, handoff path, prompt path and status `queued`/`launched`; `manual_start_required` is manual residue, not automatic success; `blocked`/`failed` stop downstream delivery; semantic-only SessionId is rejected unless backed by legacy or real log evidence.

### AgentDeliverySessionLauncher.cs

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff <handoff.md> \
  --target-id <child-id> \
  --agent codex \
  --mode <queue|launch|auto> \
  --control-index <control-index.md> \
  --out <dir> \
  --dry-run
```

Current v1 supports `codex`; `queue` writes launch artifacts, `launch` executes supported adapter, and `auto` launches when possible.

## Skill Integration Requirements

### spec-orchestrator

Workflow position: after the operational Child Index, Hardening Queue, and leading Child Session Handoff are created or updated, before final next-step wording.

Required gates:

1. Run `ValidateOrchestrationPack.cs` on the orchestration pack or file containing the Child Index.
2. If the leading handoff is created or updated in this run, run `SyncChildHandoff.cs --check` after write/sync, or `--write` when the skill owns the handoff file.
3. Run `EvaluateOrchestrationNextStep.cs` directly, or optionally `WorkflowDoctor.cs --phase post-orchestration` only when the skill wants a low-token wrapper.

Command form:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- \
  --pack <orchestration-pack-or-index.md> \
  --repo <target-repo> \
  --child-index-section "Child Index" \
  --hardening-queue-section "Hardening Queue" \
  --format json

dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- \
  --pack <orchestration-pack-or-index.md> \
  --repo <target-repo> \
  --child-index-section "Child Index" \
  --intent <inferred-or-user-intent> \
  --no-implementation \
  --format json
```

Stop/Continue:

- `ValidateOrchestrationPack.cs` exit `1` or `2`: stop downstream hardening/delivery claims; fix/sync orchestration artifacts or report blocker.
- `EvaluateOrchestrationNextStep.cs` `errors` non-empty or exit `2`: stop and repair orchestration state.
- `required_next_skill=child-spec-hardening`: report or hand off `first_unblocked_child`; do not claim implementation readiness.
- `required_next_skill=spec-change-delivery`: stop at implementation handoff unless the user explicitly requested implementation and downstream readiness gates pass.
- `required_next_skill=spec-orchestrator`: continue orchestration sync before any handoff.
- `required_next_skill=none`: report no required next workflow step with `final_status_token`.

Prosa to replace/shorten:

- Long Child Index column and stale-handoff rule blocks should become a compact "the validator enforces this" summary plus exact operational table reference.
- Existing post-orchestration decision table should defer to `EvaluateOrchestrationNextStep.cs` outputs.
- Manual handoff template prose should be replaced by `SyncChildHandoff.cs` command guidance and a short note that controlled fields are tool-owned.

### child-spec-hardening

Workflow position: before reporting `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`; after child spec hardening edits and Child Index row updates are in place.

Required gates:

1. Use `SyncChildHandoff.cs --write` when this skill owns the handoff file; use `--check` when verifying an existing generated handoff.
2. Run `ValidateChildReadiness.cs` from neutral CWD (`/tmp`) with absolute paths.
3. Keep `git diff --check` and parse/lint checks for normative machine-readable examples as separate verification commands.

Command form:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/SyncChildHandoff.cs -- \
  --index <child-index-or-pack.md> \
  --child <child-id> \
  --out <child-session-handoff.md> \
  --target-repo <target-repo> \
  --parent <parent-or-pack.md> \
  --write \
  --format json

cd /tmp
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index <child-index-or-pack.md> \
  --child <child-id> \
  --handoff <child-session-handoff.md>
```

Stop/Continue:

- `SyncChildHandoff.cs` exit `1` or `2`: do not report implementation-allowing verdict; return `NEEDS PARENT/ORCHESTRATOR SYNC` for index/handoff drift or `NEEDS HARDENING` for content/write-set blockers.
- `ValidateChildReadiness.cs` non-zero: do not report `IMPLEMENTATION READY` or `READY WITH NON-BLOCKING NOTES`.
- Both tools pass and content-quality gates are clean: implementation handoff may be reported, then stop unless user explicitly authorized delivery in the same run.

Prosa to replace/shorten:

- The long 13-point implementation-ready checklist should stay as a compact readiness concept, but exact Child Index/handoff/write-set enforcement should point to `SyncChildHandoff.cs` and `ValidateChildReadiness.cs`.
- Repeated handoff template field lists should be replaced by "generated/synchronized by `SyncChildHandoff.cs`" plus only fields the skill must supply.

### spec-change-delivery

Workflow position: pre-edit gate for Parent/Child child implementation, before any implementation file modification.

Required gates:

1. Run `ValidateChildReadiness.cs` from `/tmp` with absolute paths.
2. If Agent Delivery Launch/Queue Evidence is present or the handoff claims queued/launched automatic fresh session, run `ValidateAgentDeliveryLaunchEvidence.cs`.
3. Treat missing launch evidence as manual handoff, not as blocker by itself, unless the handoff claims automatic queue/launch or the evidence status is `blocked`/`failed`.

Command form:

```sh
cd /tmp
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- \
  --index <child-index-or-pack.md> \
  --child <child-id> \
  --handoff <child-session-handoff.md>

dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- \
  --handoff <child-session-handoff.md> \
  --evidence <agent-delivery-session-launches/.../evidence.json> \
  --launch-request <agent-delivery-session-launches/.../launch-request.json> \
  --require-automatic
```

Stop/Continue:

- Readiness validator fails or cannot run: final verdict `NOT READY`; no implementation edits.
- Launch evidence validator fails for an automatic claim: final verdict `NOT READY`; do not claim the fresh-session transition.
- Evidence status `blocked` or `failed`: final verdict `NOT READY`.
- Evidence status `manual_start_required`: continue only as manual handoff if all other gates pass, and keep manual residue visible.

Prosa to replace/shorten:

- Manual bullet lists for exact Child Index columns, stable Child id, handoff pointer, approximate write-set, and hardening verdict should be collapsed behind the readiness validator command.
- Launch evidence status prose should become a compact mapping to `ValidateAgentDeliveryLaunchEvidence.cs` results.

### spec-closeout

Workflow position: child closeout sync before advancing the next leading child or claiming closeout `READY`.

Required gates:

1. Run all spec verification commands as today.
2. When closeout creates or updates the next leading Child Session Handoff, use `SyncChildHandoff.cs --write` or `--check`.
3. When closeout releases a next leading handoff, run `AgentDeliverySessionLauncher.cs --mode queue` unless explicitly blocked/manual.
4. Validate created launch evidence with `ValidateAgentDeliveryLaunchEvidence.cs` before saying the next session is queued/launched.

Command form:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/SyncChildHandoff.cs -- \
  --index <child-index-or-pack.md> \
  --child <next-child-id> \
  --out <next-child-session-handoff.md> \
  --target-repo <target-repo> \
  --parent <parent-or-pack.md> \
  --write \
  --format json

dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff <next-child-session-handoff.md> \
  --target-id <next-child-id> \
  --agent codex \
  --mode queue \
  --out <repo>/_specs/agent-delivery-session-launches

dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- \
  --handoff <next-child-session-handoff.md> \
  --evidence <launch-dir>/evidence.json \
  --launch-request <launch-dir>/launch-request.json
```

Stop/Continue:

- Handoff sync fails: closeout remains `NOT READY` for advancing the next child.
- Launcher emits `blocked` or `failed`: next child is not advanced; record blocker.
- Launcher emits `manual_start_required`: closeout may remain ready for completed child only if manual residue is explicit; do not claim automatic queue/launch.
- Launch evidence validation fails: do not claim the fresh session is queued/launched.

Prosa to replace/shorten:

- Child closeout sync details for handoff and launch evidence should point to the three commands above.
- Keep the lifecycle distinction between completed child closeout and next-child release, but remove duplicate low-level evidence matching prose.

### docs/doc-workflow.md

Workflow position: canonical overview and shared rules.

Required documentation change:

- Add a compact "Agent Delivery Tool Gates" section naming each tool, phase, primary command shape, and authoritative outputs.
- Replace repeated detailed prose in Child Index, Child Handoff, Launch Evidence, and Readiness sections with references to the tool gates.
- Preserve the minimum Child Index table and the conceptual status meanings because humans still need review context.

Stop/Continue:

- Docs must not describe unsupported `WorkflowDoctor` phases.
- Docs must not mention nonexistent flags such as `SyncChildHandoff.cs --preserve-notes`, `SyncChildHandoff.cs --format markdown|both`, or `ValidateOrchestrationPack.cs --require-handoffs`.

## Tool-Gate Output Rules

The later implementation must use these output fields as authoritative:

| Tool | Authoritative outputs | Stop tokens / blockers | Continue tokens |
|---|---|---|---|
| `EvaluateOrchestrationNextStep.cs` | `required_next_skill`, `first_unblocked_child`, `delivery_allowed`, `trigger_result`, `final_status_token`, `lane_classification`, `errors` | exit `2`, `errors` non-empty, `required_next_skill=spec-orchestrator` until sync done | `child-spec-hardening`, `spec-change-delivery`, `none` according to user authorization and downstream gates |
| `ValidateOrchestrationPack.cs` | JSON/Markdown findings, exit code | exit `1` or `2` | exit `0` |
| `SyncChildHandoff.cs` | `status`, `findings`, controlled handoff path | exit `1` or `2`, blocking finding such as drift/approx write-set | exit `0` with current/written/would-update as appropriate for selected mode |
| `ValidateChildReadiness.cs` | exit code plus Usage/findings text | non-zero exit for gate run | exit `0` |
| `WorkflowDoctor.cs` | aggregate result for supported phase | exit `2`, or exit `1` when used with `--fail-on-required-next-step` in CI-like mode | exit `0` and underlying parsed result |
| `ValidateAgentDeliveryLaunchEvidence.cs` | validation result text/exit | automatic mismatch, `manual_start_required` under `--require-automatic`, `blocked`, `failed`, semantic-only SessionId | matching queued/launched evidence, or manual residue explicitly treated as manual without automatic claim |
| `AgentDeliverySessionLauncher.cs` | launch artifacts, `evidence.json` status | `blocked`, `failed` | `queued`, `launched`; `manual_start_required` only as visible manual residue |

## Acceptance Criteria

1. `spec-orchestrator/SKILL.md` contains compact gates for `ValidateOrchestrationPack.cs`, `EvaluateOrchestrationNextStep.cs`, optional `WorkflowDoctor.cs --phase post-orchestration`, and `SyncChildHandoff.cs`.
2. `child-spec-hardening/SKILL.md` uses `SyncChildHandoff.cs` and `ValidateChildReadiness.cs` as implementation-readiness gates and removes duplicate hand-maintained field lists where the tools enforce them.
3. `spec-change-delivery/SKILL.md` runs `ValidateChildReadiness.cs` before child implementation edits and uses `ValidateAgentDeliveryLaunchEvidence.cs` for automatic launch/queue claims.
4. `spec-closeout/SKILL.md` uses `SyncChildHandoff.cs`, `AgentDeliverySessionLauncher.cs`, and `ValidateAgentDeliveryLaunchEvidence.cs` when releasing a next leading child.
5. `docs/doc-workflow.md` has one compact Agent Delivery Tool Gates reference and no longer keeps full duplicate manual policy for every tool-enforced field.
6. No skill or doc claims unsupported CLI flags or phases.
7. No skill treats `WorkflowDoctor.cs` as policy owner or assumes unsupported `pre-delivery`/`closeout` phases.
8. The later diff preserves Workflow 1/Workflow 2 selection semantics, Workflow 2 status ownership, Parent/Child step order, Child Index role, implementation-ready verdict semantics, and Closeout release rules from `docs/doc-workflow.md`.
9. The later implementation report includes a "Workflow Preservation" paragraph naming the exact `docs/doc-workflow.md` sections checked and stating whether the Skill changes are behavior-equivalent.
10. No changes are made to MD-E2E specs, MD-E2E handoffs, or tool implementations.
11. The final implementation report includes before/after summary of shortened prose blocks and the exact verification evidence.

## Verification Commands

Execution context: run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs` on macOS/zsh unless a command explicitly uses `/tmp`. These commands verify CLI contracts and the later skill/doc integration. Do not create recursive verification loops; run the preflight/help commands once, then run the gate checks.

Risk-based preflight:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- --help
```

Success: exits `0`, prints `--pack`, `--intent`, `--no-implementation`, `--fail-on-required-next-step`, `--format`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- --help
```

Success: exits `0`, prints `--child-index-section`, `--hardening-queue-section`, `--allow-extra-columns`, `--format json|markdown|both`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/SyncChildHandoff.cs -- --help
```

Success: exits `0`, prints `--target-repo`, `--check`, `--dry-run`, `--write`, `--format text|json`, `--allow-approx-write-set`.

```sh
cd /tmp
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateChildReadiness.cs -- --help
```

Current success contract for this existing tool: prints `Usage:` plus `--allow-non-ready` and `--allow-extra-columns`. Current observed exit is `2`; later implementation must record this as an existing Usage quirk, not as a skill-integration failure.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/WorkflowDoctor.cs -- --help
```

Success: exits `0`, states Slice A supports only `--phase post-orchestration`, and prints `--format json|markdown|both`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --help
```

Success: exits `0`, prints `--fixture`, `--handoff`, `--evidence`, `--launch-request`, `--require-automatic`.

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help
```

Success: exits `0`, prints `--handoff`, `--target-id`, `--agent`, `--mode <queue|launch|auto>`, `--control-index`, `--out`, `--dry-run`.

Gate smoke:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- \
  --pack /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tests/agent-delivery-workflow-tooling/evaluate-orchestration-next-step/md-e2e-like/orchestration-pack.md \
  --repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --intent expects-hardening \
  --no-implementation \
  --format json
```

Success: exits `0`; JSON contains `"required_next_skill": "child-spec-hardening"`, `"first_unblocked_child": "MD-E2E-1"`, `"delivery_allowed": false`, `"final_status_token": "hardening_started_required"`.

Integration checks after skill/doc edits:

```sh
rg -n "ValidateOrchestrationPack|EvaluateOrchestrationNextStep|WorkflowDoctor|SyncChildHandoff" \
  skills-repo/skills/spec-orchestrator/SKILL.md
```

Success: finds the post-orchestration gate tools and no unsupported `WorkflowDoctor` phase.

```sh
rg -n "SyncChildHandoff|ValidateChildReadiness" \
  skills-repo/skills/child-spec-hardening/SKILL.md
```

Success: finds both tools in gate sections.

```sh
rg -n "ValidateChildReadiness|ValidateAgentDeliveryLaunchEvidence" \
  skills-repo/skills/spec-change-delivery/SKILL.md
```

Success: finds both pre-delivery gates.

```sh
rg -n "SyncChildHandoff|AgentDeliverySessionLauncher|ValidateAgentDeliveryLaunchEvidence" \
  skills-repo/skills/spec-closeout/SKILL.md
```

Success: finds closeout next-child release gates.

```sh
rg -n "Agent Delivery Tool Gates|EvaluateOrchestrationNextStep|ValidateOrchestrationPack|SyncChildHandoff|WorkflowDoctor" \
  docs/doc-workflow.md
```

Success: finds the compact shared tool-gate reference.

Workflow-preservation checks after skill/doc edits:

```sh
rg -n "Workflow 1 \\(Legacy-kompatibel\\)|Workflow 2 \\(Current\\)|Workflow Selection|Status Ownership by Workflow|spec-orchestrator -> Child Schnitt|child-spec-hardening -> implementation-ready Child Spec|spec-change-delivery -> one child implementation|spec-closeout \\(optional" \
  docs/doc-workflow.md
```

Success: finds the canonical workflow-selection, status-ownership, and step-order anchors.

```sh
rg -n "spec-orchestrator.*schneidet|child-spec-hardening.*Implementierungsreife|spec-change-delivery.*genau einen Child|spec-closeout.*formale?r Abschluss|IMPLEMENTATION READY|READY WITH NON-BLOCKING NOTES|Child Index.*operative Steuerzentrale" \
  docs/doc-workflow.md \
  skills-repo/skills/spec-orchestrator/SKILL.md \
  skills-repo/skills/child-spec-hardening/SKILL.md \
  skills-repo/skills/spec-change-delivery/SKILL.md \
  skills-repo/skills/spec-closeout/SKILL.md
```

Success: confirms that the implementation keeps the same workflow roles and implementation-ready semantics visible after prose reduction.

```sh
git diff -- docs/doc-workflow.md skills-repo/skills/spec-orchestrator/SKILL.md skills-repo/skills/child-spec-hardening/SKILL.md skills-repo/skills/spec-change-delivery/SKILL.md skills-repo/skills/spec-closeout/SKILL.md
```

Success: human review shows only gate-expression/prose-reduction changes, no reordered workflow, no changed status ownership, no new implementation bypass, and no changed Workflow 1/Workflow 2 selection rule.

```sh
rg -n -- "--preserve-notes|--require-handoffs|--format markdown|--phase pre-delivery|--phase closeout" \
  skills-repo/skills/spec-orchestrator/SKILL.md \
  skills-repo/skills/child-spec-hardening/SKILL.md \
  skills-repo/skills/spec-change-delivery/SKILL.md \
  skills-repo/skills/spec-closeout/SKILL.md \
  docs/doc-workflow.md
```

Success: no matches, unless the text explicitly says the flag/phase is unsupported.

```sh
git diff --check
```

Success: exits `0`.

## Command Contract Rehearsal Evidence

Authoring rehearsal on 2026-05-09:

- `EvaluateOrchestrationNextStep.cs --help`: exit `0`; required options present.
- `ValidateOrchestrationPack.cs --help`: exit `0`; no `--require-handoffs`; `--hardening-queue-section` present.
- `SyncChildHandoff.cs --help`: exit `0`; uses `--target-repo`; formats are `text|json`; no `--preserve-notes`.
- `ValidateChildReadiness.cs --help`: printed Usage and options but exited `2`; this is documented as a current tool quirk.
- `WorkflowDoctor.cs --help`: exit `0`; only `post-orchestration` phase supported.
- `ValidateAgentDeliveryLaunchEvidence.cs --help`: exit `0`; required evidence modes present.
- `AgentDeliverySessionLauncher.cs --help`: exit `0`; queue/launch/auto modes present.
- `EvaluateOrchestrationNextStep.cs` MD-E2E-like smoke: exit `0`; returned `required_next_skill=child-spec-hardening`, `first_unblocked_child=MD-E2E-1`, `delivery_allowed=false`, `final_status_token=hardening_started_required`.

## Content Quality Review

- Correctness/domain fit: The spec routes existing skill decisions to the tools that were built for those gates.
- Scope discipline: It forbids tool changes, MD-E2E artifact changes, broad rewrites, and Parent/Child orchestration for this spec.
- Completeness: Each affected skill has workflow position, command form, expected outputs, and Stop/Continue rules.
- Consistency: Verified CLI deviations are documented so implementation will not use nonexistent flags or phases.
- Workflow preservation: The spec now explicitly treats the Skill changes as behavior-equivalent to `docs/doc-workflow.md`; tools concretize existing gates and may not introduce new sequence, status, or ownership semantics.
- Testability: Verification commands cover help contracts, one real next-step smoke, integration `rg` checks, unsupported-token checks, and whitespace diff checks.
- Traceability: Each planned prose reduction maps to a specific tool gate.
- Lifecycle fit: Later implementation can create one OpenSpec change, edit the five target files, run the listed commands, and stop with a concrete readiness verdict.

## Implementation Readiness Verdict

READY FOR IMPLEMENTATION PLANNING.

The spec has no blocking `[MISSING ...]` or `[DECISION ...]` markers. The later implementation should use `spec-change-delivery` in OpenSpec mode, create one bounded change for the five listed files, and avoid any tool or MD-E2E artifact edits.

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tool-gate-skill-integration-spec | Initial hardened normal spec for integrating Agent Delivery Workflow Tool Gates into existing skills and workflow docs. |
| 2026-05-09 | workflow-tool-gate-skill-integration-spec | Added explicit Workflow Preservation Contract so tool adoption cannot change `docs/doc-workflow.md` semantics, step order, or status ownership. |
