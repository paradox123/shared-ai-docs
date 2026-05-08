**Date:** 2026-05-08
**Status:** 🟡 Spec
**Scope:** Automation for turning Agent Delivery Child Session Handoffs into launched or queued fresh Child sessions.

---

## Review Control Surface

- Spec-Variante: Contract-heavy workflow/tooling Spec.
- Goldstandard Status: candidate.
- Ziel: Ein persistiertes Child Session Handoff soll nicht mehr nur ein manueller Kopiertext sein, sondern in einen vollstaendigen Startauftrag fuer die naechste frische Child-Session uebersetzt, vorab validiert und entweder direkt ueber einen lokalen Codex-Mechanismus gestartet oder maschinenlesbar queued werden.
- In Scope: Handoff-Parser, Child-Index-/Verdict-Konsistenzpruefung, Startauftrag-/Prompt-Generierung, Secret-Guard, Statusmodell `launched`/`queued`/`manual_start_required`/`blocked`/`failed`, `codex exec` Launch-Pfad, Queue-Fallback, persistierte Run-Evidence, minimale Workflow-/Skill-Doku, Beispiel-Startauftrag, positive und negative Verifikationsfaelle.
- Out of Scope: Runtime-Implementierung in Produktrepos, Aenderungen an Original-KI-fuer-KMU-Specs, breite DocWorkflow-Umstrukturierung, App-internes Session-Protokoll ohne lokal pruefbare Schnittstelle, unkontrollierter Auto-Launch ohne expliziten Modus, Secrets in Prompt/Manifest/Logs.
- Wichtigste Test-/Harness-Cases: vorhandenes Handoff wie `DWT-S4` oder synthetisches valides Handoff wird gelesen und erzeugt einen vollstaendigen Startauftrag; unvollstaendiges/stales Handoff blockiert; Queue-Fallback persistiert JSON plus Prompt; Launch-Dry-Run belegt `codex exec` Command-Vertrag; Statuswerte unterscheiden Launch, Queue, Manual, Blocked und Failed; Secret-Muster blockieren vor Prompt-/Manifest-Persistenz.
- Wichtigste Verification Commands: `dotnet run skills-repo/tools/LaunchChildSession.cs -- --handoff <path> --child <id> --mode queue --out _specs/child-session-launches`; `dotnet run skills-repo/tools/LaunchChildSession.cs -- --handoff <bad-fixture> --child <id> --mode queue`; `bash -n` fuer optionale Wrapper-Skripte; `git diff --check`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen fuer die Spec. Der direkte Launch-Pfad ist lokal auf `codex exec` begrenzt; Desktop-App-/Heartbeat-/App-Server-Mechanismen werden nur als spaetere Erweiterung gefuehrt, weil kein stabiler lokaler Startvertrag nachgewiesen wurde.
- Readiness Status: IMPLEMENTATION READY fuer einen einzelnen Workflow-2-Tooling-Change.

## Session Briefing

- Modus/Skill: `doc-coauthoring` mit anschliessendem `doc-review-autoresolve`.
- Source of Truth: `docs/doc-workflow.md`, die Agent-Delivery-Skills unter `skills-repo/skills/`, vorhandene Handoffs in `_specs/child-session-handoffs/`, vorhandenes Tool `skills-repo/tools/ValidateChildReadiness.cs`, lokale `codex` CLI Help-Ausgabe vom 2026-05-08.
- Ziel: Die Anforderungen fuer eine kleine robuste Automatisierung fixieren, die einen Handoff-Uebergang technisch ausfuehrt oder beweisbar queued.
- Nicht-Ziele: keine Produktimplementierung, keine grossflaechige Skill-/Workflow-Rewrite, kein Startmechanismus ohne vorherige lokale Pruefung.
- In Scope: Spec, Normative Contract, Akzeptanzkriterien, Verifikationscommands und Beispielartefakte fuer die folgende Implementierung.
- Erwarteter Output: eine implementation-ready Spec im shared-ai-docs `_specs`-Ordner.
- Verification/Review: Content-Quality-Review gegen den Handoff-Startpunkt, Status-/Evidence-Vertrag und lokale technische Machbarkeit.
- Offene Entscheidungen: Keine blockierenden Entscheidungen.

## 1. Problem

Der Agent Delivery Workflow verlangt bei Child-Hardening und Child-Delivery regelmaessig eine frische Session. Die aktuellen Skills erzeugen dafuer persistierte Child Session Handoffs und Startkontext, aber sie starten die naechste Session nicht und hinterlassen auch keinen standardisierten maschinenlesbaren Queue-Auftrag. Dadurch kann ein Workflow formal "handoff-ready" wirken, waehrend der eigentliche Uebergang weiterhin manuelles Kopieren bleibt.

Die wichtigste Anforderung ist deshalb nicht ein weiterer Textblock im Skill, sondern ein belastbarer Uebergang:

1. Aus dem Handoff entsteht ein vollstaendiger Startauftrag.
2. Der Startauftrag wird mit dem Handoff-Inhalt initialisiert.
3. Vor Launch oder Queueing wird Konsistenz geprueft.
4. Launch oder Queueing hinterlaesst persistierte Evidence, die spaetere Skills auswerten koennen.

## 2. Lokale technische Optionen und Entscheidung

Am 2026-05-08 wurden diese lokalen Optionen geprueft:

| Option | Lokal gefunden | Bewertung |
|---|---|---|
| `codex exec` | `codex exec [PROMPT]`, stdin-Prompt, `--json`, `-C <dir>`, `--output-last-message <file>`, persistierte Sessions wenn nicht `--ephemeral`. | Geeignet fuer direkten frischen nicht-interaktiven Child-Run. Der Prompt kann exakt aus dem Startauftrag per stdin uebergeben werden. |
| `codex` TUI / `codex fork` / `codex resume` | Verfuegbar, aber interaktiv bzw. auf bestehende Sessions bezogen. | Nicht geeignet als Standard-Automation fuer frische Child-Starts. |
| Codex Desktop App / App-Server | `codex app-server` existiert experimentell; keine stabile lokale "create new app session with prompt" Schnittstelle wurde nachgewiesen. | Spaetere Erweiterung, kein Implementierungsfundament fuer diese Spec. |
| Codex Automations | `~/.codex/automations` ist vorhanden, aber leer; Codex-App-Automation-Tool kann Cron/Heartbeat-Jobs anlegen, nicht nachweislich eine neue Child-Session aus einem Handoff starten. | Nicht als direkter Session-Launcher verwenden; nur als spaetere Orchestrierung denkbar. |
| Queue-Datei | Im Repo frei implementierbar. | Robuster Fallback und Audit-Vertrag, wenn Launch nicht gewollt oder nicht moeglich ist. |

Entscheidung: Implementiere ein kleines lokales Tool unter `skills-repo/tools/LaunchChildSession.cs`. Das Tool nutzt den vorhandenen Stil der file-based .NET Tools und arbeitet in drei Modi:

1. `--mode queue`: validiert Handoff/Index, erzeugt Startauftrag, Prompt, Manifest und Evidence, startet aber keine Session.
2. `--mode launch`: validiert, erzeugt Startauftrag und startet einen frischen non-interactive Run per `codex exec` mit Prompt aus stdin.
3. `--mode auto`: nutzt `launch`, wenn `codex exec` vorhanden und alle Launch-Preflights gruen sind; sonst `queue`.

Ein direkter Launch ist nur dann `launched`, wenn der Prozess wirklich gestartet wurde und die Run-Evidence den verwendeten Prompt, Startzeit, Ziel-Workspace, Handoff-Pfad, Child-ID, Mechanismus, Exitstatus und soweit verfuegbar Session-ID oder Logpfad enthaelt. Andernfalls ist der Ergebnisstatus `queued`, `manual_start_required`, `blocked` oder `failed`.

## 3. Startauftrag-Vertrag

Das Tool erzeugt pro Run einen stabilen Run-Ordner:

```text
_specs/child-session-launches/<UTC timestamp>-<child-id>/
  launch-request.json
  start-prompt.md
  evidence.json
  codex-events.jsonl              # nur bei launch, falls --json genutzt wurde
  last-message.md                 # nur bei launch, falls erzeugt
```

`launch-request.json` ist maschinenlesbar und muss mindestens diese Felder enthalten:

```json
{
  "schema_version": "agent-delivery.child-session-launch.v1",
  "status": "queued",
  "created_at": "2026-05-08T00:00:00Z",
  "started_at": null,
  "completed_at": null,
  "parent": "_specs/parent.md",
  "child_id": "DWT-S4",
  "child_spec": "_specs/child.md",
  "child_index": "_specs/parent.md#Delivery Orchestration Pack",
  "handoff_path": "_specs/child-session-handoffs/dwt-s4-session-handoff.md",
  "target_workspace": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "next_skill": "spec-change-delivery",
  "next_mode": "OpenSpec or direct as stated by handoff",
  "current_verdict": "IMPLEMENTATION READY",
  "scope_summary": "Use exact handoff scope summary.",
  "non_goals": ["No out-of-scope work."],
  "allowed_write_set": ["path/or/glob"],
  "read_only_files": ["path/or/glob"],
  "verification": ["command or lifecycle item"],
  "evidence_openspec": ["path or note"],
  "open_notes": ["blocker or non-blocking note"],
  "fresh_session_required": true,
  "mechanism": {
    "type": "queue",
    "recommended_command": "codex exec -C ... - < start-prompt.md",
    "actual_command": null,
    "codex_available": true
  },
  "evidence_paths": {
    "prompt": "_specs/child-session-launches/.../start-prompt.md",
    "events": null,
    "last_message": null
  },
  "blockers": [],
  "warnings": []
}
```

`start-prompt.md` ist exakt der Prompt, der bei `launch` per stdin an `codex exec` uebergeben wird oder bei `queue`/`manual_start_required` manuell verwendbar ist. Er muss die Handoff-Inhalte direkt enthalten, nicht nur auf das Handoff verweisen.

Pflichtinhalte des Prompts:

1. Parent.
2. Child-ID.
3. Child Spec.
4. Child Index / Queue.
5. Handoff File.
6. Target Repository / Working Directory.
7. Naechster Skill/Modus.
8. Scope Summary.
9. Non-Goals.
10. Allowed Write-Set.
11. Shared / Read-only Files.
12. Verification Lifecycle oder Verification Commands.
13. Evidence / OpenSpec.
14. Offene Blocker oder non-blocking Notes.
15. Explizite Anweisung, zuerst Handoff, Child Index und Child Verdict zu validieren und nur im erlaubten Write-Set zu arbeiten.

## 4. Konsistenz- und Sicherheits-Gates

Vor Launch oder Queueing muss das Tool diese Gates pruefen:

| Gate | Blockiert wenn |
|---|---|
| Handoff existiert und ist parsebar | Datei fehlt, Pflichtfelder fehlen oder mehrere Child-IDs widersprechen sich. |
| Child-ID konsistent | CLI-`--child`, Handoff `Child`/`Stable Child ID`, Handoff-Dateiname und Child-Index-Zeile widersprechen sich. |
| Child Index operativ | Index fehlt, Zielzeile fehlt, Handoff-Pointer fehlt oder zeigt auf anderen Pfad. |
| Verdict passend zum naechsten Skill | `spec-change-delivery` ohne `IMPLEMENTATION READY` oder akzeptiertes `READY WITH NON-BLOCKING NOTES`; `child-spec-hardening` ohne hardening-faehigen Status wie `needs_hardening`, `ready_candidate`, `NEEDS HARDENING` oder expliziten Blocker; Closeout ohne akzeptierte Delivery-Evidence. |
| Write-Set enforceable | `Allowed Write-Set` fehlt, ist leer, enthaelt `TBD`, `as needed`, `likely`, `related files`, `etc.` oder keine konkreten Pfade/Globs. |
| Target Workspace | Pfad fehlt, ist nicht absolut oder existiert nicht im lokalen Environment. |
| Secret-Guard | Handoff, Startauftrag oder Prompt enthalten offensichtliche Secret-Muster wie API-Key-/Token-Prefixe, `password=`, `Authorization: Bearer`, private key blocks oder `.env`-Werte. |
| Prompt-Vollstaendigkeit | Einer der Pflichtinhalte aus Abschnitt 3 fehlt. |
| Launch-Preflight | `codex exec` fehlt, Modus ist `launch`/`auto`, Ziel-CWD ist ungueltig oder der command contract kann nicht gebaut werden. |

Wenn ein Gate vor Prompt-Persistenz ein Secret findet, darf das Tool keinen vollstaendigen Prompt und kein unredigiertes Manifest schreiben. Es schreibt nur `evidence.json` mit `status: "blocked"`, redigierter Diagnose und ohne Secret-Wert.

Das vorhandene `ValidateChildReadiness.cs` bleibt fuer implementation-ready `spec-change-delivery`-Starts die fuehrende Readiness-Pruefung. `LaunchChildSession.cs` soll es nicht duplizieren, sondern entweder intern aufrufen oder dieselben Pflichtbedingungen mit klarer Begruendung referenzieren. Fuer Hardening-Starts darf die Readiness-Pruefung nicht faelschlich `IMPLEMENTATION READY` verlangen; sie muss den naechsten Skill beruecksichtigen.

## 5. Statusmodell

| Status | Bedeutung | Evidence-Anforderung |
|---|---|---|
| `launched` | Eine neue frische non-interactive Codex-Session wurde ueber `codex exec` mit genau dem persistierten `start-prompt.md` gestartet. | `started_at`, `target_workspace`, `handoff_path`, `child_id`, `actual_command`, Exitstatus, `codex-events.jsonl` oder Logpfad, Prompt-Hash, soweit verfuegbar Session-ID. |
| `queued` | Kein direkter Start wurde versucht oder `auto` fiel bewusst auf Queue zurueck; ein vollstaendiger maschinenlesbarer Auftrag und Prompt liegen vor. | `launch-request.json`, `start-prompt.md`, `recommended_command`, Blocker leer oder nur nicht-blockierende Launch-Warnung. |
| `manual_start_required` | Automatische Queue ist moeglich, aber der nachgewiesene lokale Mechanismus reicht nicht fuer den angeforderten interaktiven/App-Start; manueller Prompt ist exakt persistiert. | Vollstaendiger Prompt, Begruendung warum kein direkter Mechanismus verfuegbar ist, empfohlenes manuelles Kommando oder App-Schritt. |
| `blocked` | Konsistenz-, Verdict-, Workspace- oder Secret-Gate verhindert Start und Queue als gueltigen Auftrag. | Redigierte Blocker-Liste, keine ungueltige Startfreigabe, kein vollstaendiger Prompt bei Secret-Blocker. |
| `failed` | Launch wurde versucht, aber der Prozess schlug fehl oder Evidence konnte nicht geschrieben werden. | Exitcode, stderr/stdout-Auszug ohne Secrets, Prompt-Hash, Run-Pfad, naechster sicherer Schritt. |

Akzeptanzregel: Spaetere Skills duerfen nur `launched` und `queued` als erfolgreiche Automatisierungsuebergabe werten. `manual_start_required` ist besser als Chat-only, aber kein automatischer Start/Queue-Erfolg. `blocked` und `failed` blockieren Folge-Delivery.

## 6. Beispiel-Startprompt aus bestehendem Handoff

Aus `_specs/child-session-handoffs/dwt-s4-session-handoff.md` muss das Tool sinngemaess diesen Prompt erzeugen:

```md
Wir arbeiten in /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs.

Starte eine frische Agent-Delivery-Child-Session aus folgendem persistierten Handoff.

Pflicht: Lies zuerst das Handoff, den Child Index und die Child Spec. Validiere, dass Child-ID, Handoff-Pfad, Child Index, aktueller Verdict, Target Workspace und Allowed Write-Set konsistent sind. Arbeite nur im erlaubten Write-Set. Wenn ein Gate stale, widerspruechlich oder unvollstaendig ist, stoppe mit NOT READY und persistiere Evidence statt zu implementieren.

- Parent: _specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md
- Child: DWT-S4
- Child Spec: _specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S4 Summary Telemetry Style Reporting Contract.md
- Child Index / Queue: _specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md section Delivery Orchestration Pack
- Handoff File: _specs/child-session-handoffs/dwt-s4-session-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Next Mode / Skill: spec-change-delivery
- Current Verdict: ACCEPTED
- Scope Summary: Implement the DWT-S4 reporting contract...
- Non-Goals: No Agent-Ausfuehrung; no Promptfoo/Codex/Auth-Provisionierung; ...
- Allowed Write-Set: ...
- Shared / Read-only Files: ...
- Verification Commands: ...
- Evidence / OpenSpec: ...
- Open Notes: None for DWT-S4 closeout. DWT-S2, DWT-S3 and DWT-S5 remain unreleased.
```

Wenn der Handoff bereits `ACCEPTED` statt `IMPLEMENTATION READY` ist und `Next Mode / Skill` trotzdem `spec-change-delivery` fordert, muss die Konsistenzpruefung blockieren oder den Status als Closeout-/historisches Handoff klassifizieren. Dieser Fall ist ein wichtiger negativer Test, weil akzeptierte alte Handoffs nicht versehentlich als neue Delivery-Freigabe dienen duerfen.

## 7. Acceptance Criteria

1. Given ein gueltiges implementation-ready Delivery-Handoff mit operativem Child Index, when `LaunchChildSession.cs --mode queue` laeuft, then entstehen `launch-request.json`, `start-prompt.md` und `evidence.json` mit `status: "queued"` und allen Pflichtfeldern.
2. Given dasselbe Handoff und lokal verfuegbares `codex exec`, when `--mode launch --dry-run` laeuft, then wird der exakt empfohlene `codex exec`-Befehl inklusive stdin-Promptvertrag persistiert, aber nicht ausgefuehrt.
3. Given dasselbe Handoff und `--mode launch` ohne Dry-Run, when der Codex-Prozess erfolgreich startet und beendet, then ist der Status `launched`, der verwendete Prompt entspricht bytegleich `start-prompt.md`, und Run-Evidence enthaelt Startzeit, Ziel-Workspace, Handoff, Child-ID, Mechanismus, Exitstatus und Log-/Eventpfad soweit verfuegbar.
4. Given ein Handoff mit fehlendem Pflichtfeld, widerspruechlicher Child-ID, falschem Child-Index-Pointer oder nicht passendem Verdict, when das Tool laeuft, then ist der Status `blocked`, und es entsteht keine erfolgreiche Queue-/Launch-Freigabe.
5. Given ein valides Handoff, aber fehlendes `codex exec` im PATH, when `--mode auto` laeuft, then entsteht `queued` mit `recommended_command` oder `manual_start_required`, je nachdem ob ein nicht-interaktiver CLI-Fallback sauber formulierbar ist.
6. Given ein Handoff mit offensichtlichem Secret-Muster, when das Tool laeuft, then blockiert es vor Persistenz eines vollstaendigen Prompts und schreibt nur redigierte Evidence.
7. Given ein Launch-Prozess mit non-zero Exitcode, when das Tool die Evidence schreiben kann, then ist der Status `failed`, nicht `queued` und nicht `launched`.
8. Given spaetere Skills lesen `launch-request.json`, when `status` `queued` oder `launched` ist, then koennen sie eindeutig erkennen, welcher Child, welches Handoff, welcher Prompt und welche Evidence fuer den Uebergang fuehrend sind.

## 8. Verification Commands

Ausfuehrungskontext: macOS oder Linux, Shell `zsh`/`bash`, Arbeitsverzeichnis `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`. Commands duerfen keine echten Child-Deliveries starten, ausser der Operator waehlt explizit `--mode launch` ohne `--dry-run`.

Risk-based Preflight:

```sh
command -v codex
codex exec --help
dotnet --info
```

Syntax/Build:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/LaunchChildSession.cs -- --help
git diff --check
```

Positive Queue-Fixture:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/LaunchChildSession.cs -- \
  --handoff tests/agent-delivery-launch/fixtures/valid-ready/child-session-handoff.md \
  --child DWT-LAUNCH-1 \
  --index tests/agent-delivery-launch/fixtures/valid-ready/child-index.md \
  --mode queue \
  --out /tmp/agent-delivery-launch-positive
```

Success criteria: exit code `0`; `/tmp/agent-delivery-launch-positive/**/launch-request.json` exists; JSON status is `queued`; `start-prompt.md` contains Parent, Child, Child Spec, Child Index, Handoff, Target Workspace, Next Skill, Scope, Non-Goals, Allowed Write-Set, Read-only Files, Verification, Evidence/OpenSpec and Notes.

Negative Consistency Fixture:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/LaunchChildSession.cs -- \
  --handoff tests/agent-delivery-launch/fixtures/invalid-stale/child-session-handoff.md \
  --child DWT-LAUNCH-1 \
  --index tests/agent-delivery-launch/fixtures/invalid-stale/child-index.md \
  --mode queue \
  --out /tmp/agent-delivery-launch-negative
```

Success criteria: non-zero exit code or documented blocked exit code; evidence status is `blocked`; no successful `queued` or `launched` status exists.

Launch Dry-Run:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/LaunchChildSession.cs -- \
  --handoff tests/agent-delivery-launch/fixtures/valid-ready/child-session-handoff.md \
  --child DWT-LAUNCH-1 \
  --index tests/agent-delivery-launch/fixtures/valid-ready/child-index.md \
  --mode launch \
  --dry-run \
  --out /tmp/agent-delivery-launch-dry-run
```

Success criteria: status is `queued` or `manual_start_required` with `dry_run: true`; `recommended_command` contains `codex exec`; no Codex run is executed.

Optional Real Launch Gate:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/LaunchChildSession.cs -- \
  --handoff tests/agent-delivery-launch/fixtures/valid-ready/child-session-handoff.md \
  --child DWT-LAUNCH-1 \
  --index tests/agent-delivery-launch/fixtures/valid-ready/child-index.md \
  --mode launch \
  --out /tmp/agent-delivery-launch-real
```

Success criteria: only run with explicit operator intent; status `launched` on zero exit, `failed` on non-zero exit; evidence includes prompt hash, command, start time, exit status and event/log path if emitted by Codex.

Anti-loop rule: These commands verify the launcher contract and one optional real launch. They must not spawn recursive verification of newly launched child work.

## 9. Files Expected In Implementation

Minimal write-set:

1. `skills-repo/tools/LaunchChildSession.cs`.
2. `tests/agent-delivery-launch/fixtures/valid-ready/**`.
3. `tests/agent-delivery-launch/fixtures/invalid-stale/**`.
4. Optional `tests/agent-delivery-launch/README.md` if fixture intent is not obvious.
5. Minimal doc/skill patches:
   - `docs/doc-workflow.md`: add "Child Session Launch/Queue Evidence" rule.
   - `skills-repo/skills/child-spec-hardening/SKILL.md`: after implementation-ready handoff, run or recommend launcher queue/launch.
   - `skills-repo/skills/spec-change-delivery/SKILL.md`: if starting from Handoff, prefer launcher evidence when available.
   - `skills-repo/skills/spec-closeout/SKILL.md`: next child handoff must be launched/queued or explicitly blocked/manual.

No product repo paths or original KI-fuer-KMU specs are in the write-set.

## 10. Definition of Done / Closeout Evidence

Implementation is done when:

1. The launcher reads at least one valid handoff fixture and emits a complete startauftrag.
2. The startauftrag includes the full Handoff context, not just references.
3. Invalid/stale handoffs are blocked before launch/queue success.
4. Queue mode persists machine-readable manifest, exact prompt and evidence.
5. Launch dry-run proves the `codex exec` command contract without starting real work.
6. Optional real launch, if run, persists `launched` or `failed` evidence truthfully.
7. Status values are exclusive and documented.
8. Secret guard prevents obvious secret persistence.
9. Minimal workflow/skill docs tell future skills where to look for launch/queue evidence.
10. `git diff --check` passes.

## 11. Content Quality Review Result

Autonomous review pass after authoring:

| Check | Result |
|---|---|
| Correctness / domain fit | Pass. The Spec addresses the actual missing transition from Handoff to fresh Child session or queued startauftrag. |
| Scope discipline | Pass. The Scope is limited to shared-ai-docs tooling, fixtures and minimal workflow/skill docs. |
| Completeness | Pass. Normal path, queue fallback, manual fallback, blocked path, failed launch and secret path are covered. |
| Consistency | Pass. Statuses and evidence fields are synchronized between Review Control Surface, contract and acceptance criteria. |
| Feasibility | Pass. `codex exec` and file-based .NET tooling are locally available; app-server/automations are not assumed. |
| Testability | Pass. Positive, negative, dry-run, optional launch and diff checks are specified with observable success criteria. |
| Traceability | Pass. Requirements trace to Child Session Handoff, Child Index, existing readiness validator and user-stated status/evidence requirements. |
| Operational fit | Pass with one intentional constraint: direct launch is non-interactive `codex exec`; interactive Desktop-App starts remain future extension until a stable local API exists. |
| Secret handling | Pass. Secret-like input blocks prompt persistence instead of redacting after the fact. |

Readiness verdict: `IMPLEMENTATION READY` for one bounded `spec-change-delivery` tooling change.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-08 | Codex | Initial implementation-ready Spec authored and hardened for Child Session Launch/Queue Automation. |

SessionId: 2026-05-08-agent-delivery-child-session-launch-automation-spec
