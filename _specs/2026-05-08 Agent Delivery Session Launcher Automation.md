**Date:** 2026-05-08
**Status:** 🔵 Implemented
**Scope:** Agent Delivery Workflow automation for turning session handoffs into launched or queued fresh agent sessions.

---

## Review Control Surface

- Spec-Variante: Contract-heavy workflow/tooling Spec.
- Goldstandard Status: candidate.
- Ziel: Ein persistiertes Agent-Delivery-Handoff soll nicht mehr nur ein manueller Kopiertext sein, sondern in einen vollstaendigen agent-auswaehlbaren Startauftrag fuer die naechste frische Agent-Session uebersetzt, vorab validiert und entweder direkt ueber einen lokal implementierten Agent-Adapter gestartet oder maschinenlesbar queued werden.
- In Scope: Agent-Delivery-Handoff-Parser, Workflow-Control-/Verdict-Konsistenzpruefung, Startauftrag-/Prompt-Generierung, `--target-id` fuer den Session-Gegenstand, `--agent` Provider-Auswahl mit `codex` als einzig implementiertem v1-Adapter, Codex-App-Projektzuordnung ueber Ziel-Workspace, deterministischer Session-Titel-Vertrag, Secret-Guard, Statusmodell `launched`/`queued`/`manual_start_required`/`blocked`/`failed`, `codex exec` Launch-Pfad, Queue-Fallback, persistierte Run-Evidence, verpflichtende Einbettung in die Agent-Delivery-Workflow-Skills, Beispiel-Startauftrag, positive und negative Verifikationsfaelle inklusive Skill-Integration.
- Out of Scope: Runtime-Implementierung in Produktrepos, Aenderungen an Original-KI-fuer-KMU-Specs, breite DocWorkflow-Umstrukturierung, Implementierung weiterer Agent-Adapter ausser `codex`, agent-spezifische Promptsprache fuer fremde Tools, App-internes Session-Protokoll ohne lokal pruefbare Schnittstelle, unkontrollierter Auto-Launch ohne expliziten Modus, Secrets in Prompt/Manifest/Logs.
- Wichtigste Test-/Harness-Cases: vorhandenes Handoff wie `DWT-S4` oder synthetisches valides Handoff wird gelesen und erzeugt einen vollstaendigen Startauftrag; `--agent codex` erzeugt Codex-Launch-/Queue-Evidence; Codex-Launches verwenden den Target Workspace als `-C`, damit die Session im gleichen Projektkontext landet; Launcher erzeugt einen deterministischen `session_title` und prueft nach Launch die lokal sichtbare Thread-Metadatenlage soweit verfuegbar; ein nicht implementierter Agent wird nicht als gestartet behauptet, sondern mit Adapter-Status `unsupported` als `manual_start_required` oder `blocked` dokumentiert; unvollstaendiges/stales Handoff blockiert; Queue-Fallback persistiert JSON plus Prompt; Launch-Dry-Run belegt `codex exec` Command-Vertrag; Statuswerte unterscheiden Launch, Queue, Manual, Blocked und Failed; Secret-Muster blockieren vor Prompt-/Manifest-Persistenz; Skill-Integrationstests belegen, dass `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout` und `agent-delivery-retro-review` die Launcher-Evidence kennen und nicht nur Handoff-Text erzeugen.
- Wichtigste Verification Commands: `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff <path> --target-id <id> --agent codex --mode queue --out _specs/agent-delivery-session-launches`; `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff <path> --target-id <id> --agent unsupported-demo --mode queue --out /tmp/agent-delivery-session-launcher-unsupported`; `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --handoff <bad-fixture> --target-id <id> --agent codex --mode queue`; `sqlite3 /Users/dh/.codex/state_5.sqlite '.schema threads'`; `rg -n "AgentDeliverySessionLauncher|Agent Delivery Session Launch/Queue Evidence|agent-delivery-session-launches" docs/doc-workflow.md skills-repo/skills/{spec-orchestrator,child-spec-hardening,spec-change-delivery,spec-closeout,agent-delivery-retro-review}/SKILL.md`; `git diff --check`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen fuer die Spec. Der direkte Launch-Pfad ist in v1 lokal auf den Agent-Provider `codex` via `codex exec` begrenzt; andere Agent-Provider sind als manifestierter Adapter-Vertrag vorgesehen, aber nicht implementiert. Desktop-App-/Heartbeat-/App-Server-Mechanismen werden nur als spaetere Erweiterung gefuehrt, weil kein stabiler lokaler Startvertrag nachgewiesen wurde.
- Readiness Status: IMPLEMENTATION READY fuer einen einzelnen Workflow-2-Tooling-Change.

## Session Briefing

- Modus/Skill: `doc-coauthoring` mit anschliessendem `doc-review-autoresolve`.
- Source of Truth: `docs/doc-workflow.md`, die Agent-Delivery-Skills unter `skills-repo/skills/`, vorhandene Handoffs in `_specs/child-session-handoffs/`, vorhandenes Tool `skills-repo/tools/ValidateChildReadiness.cs`, lokale `codex` CLI Help-Ausgabe und lokale Codex-Thread-Metadatenpruefung vom 2026-05-08.
- Ziel: Die Anforderungen fuer eine kleine robuste Agent-Delivery-Workflow-Automatisierung fixieren, die einen Handoff-Uebergang technisch ausfuehrt oder beweisbar queued und in den relevanten Agent-Delivery-Skills verbindlich benutzt wird.
- Nicht-Ziele: keine Produktimplementierung, keine grossflaechige Skill-/Workflow-Rewrite, keine Implementierung weiterer Agent-Adapter ausser `codex`, kein Startmechanismus ohne vorherige lokale Pruefung.
- In Scope: Spec, Normative Contract, Akzeptanzkriterien, Verifikationscommands und Beispielartefakte fuer die folgende Implementierung.
- Erwarteter Output: eine implementation-ready Spec im shared-ai-docs `_specs`-Ordner.
- Verification/Review: Content-Quality-Review gegen den Handoff-Startpunkt, Status-/Evidence-Vertrag und lokale technische Machbarkeit.
- Offene Entscheidungen: Keine blockierenden Entscheidungen.

## 1. Problem

Der Agent Delivery Workflow verlangt bei groesseren Parent-/Child-, Hardening-, Delivery- und Closeout-Uebergaengen regelmaessig eine frische Session. Die aktuellen Skills erzeugen dafuer persistierte Handoffs und Startkontext, aber sie starten die naechste Session nicht und hinterlassen auch keinen standardisierten maschinenlesbaren Queue-Auftrag. Dadurch kann ein Workflow formal "handoff-ready" wirken, waehrend der eigentliche Uebergang weiterhin manuelles Kopieren bleibt.

Die wichtigste Anforderung ist deshalb nicht ein weiterer Textblock im Skill, sondern ein belastbarer Uebergang:

1. Aus dem Handoff entsteht ein vollstaendiger Startauftrag.
2. Der Startauftrag wird mit dem Handoff-Inhalt initialisiert.
3. Vor Launch oder Queueing wird Konsistenz geprueft.
4. Launch oder Queueing hinterlaesst persistierte Evidence, die spaetere Skills auswerten koennen.

## 2. Lokale technische Optionen und Entscheidung

Am 2026-05-08 wurden diese lokalen Optionen geprueft:

| Option | Lokal gefunden | Bewertung |
|---|---|---|
| `codex exec` | `codex exec [PROMPT]`, stdin-Prompt, `--json`, `-C <dir>`, `--output-last-message <file>`, persistierte Sessions wenn nicht `--ephemeral`. | Geeignet fuer direkten frischen nicht-interaktiven Agent-Delivery-Session-Run. Der Prompt kann exakt aus dem Startauftrag per stdin uebergeben werden. `-C` setzt lokal nachweisbar den Thread-`cwd` und ist damit der Projektzuordnungshebel. |
| `codex` TUI / `codex fork` / `codex resume` | Verfuegbar, aber interaktiv bzw. auf bestehende Sessions bezogen. | Nicht geeignet als Standard-Automation fuer frische Agent-Delivery-Session-Starts. |
| Codex Desktop App / App-Server | `codex app-server` existiert experimentell; keine stabile lokale "create new app session with prompt" Schnittstelle wurde nachgewiesen. | Spaetere Erweiterung, kein Implementierungsfundament fuer diese Spec. |
| Codex Automations | `~/.codex/automations` ist vorhanden, aber leer; Codex-App-Automation-Tool kann Cron/Heartbeat-Jobs anlegen, nicht nachweislich eine neue Agent-Delivery-Session aus einem Handoff starten. | Nicht als direkter Session-Launcher verwenden; nur als spaetere Orchestrierung denkbar. |
| Codex Thread Metadata | Lokale App-DB `~/.codex/state_5.sqlite` enthaelt `threads` mit `id`, `rollout_path`, `source`, `cwd`, `title`, `first_user_message`; `codex exec`-Runs erscheinen dort mit `source='exec'` und dem per `-C` gesetzten `cwd`. Ein offizieller `codex exec --title` Parameter wurde lokal nicht gefunden. | Projektzuordnung kann ueber `-C <target_workspace>` verifiziert werden. Titelsteuerung braucht einen Launcher-Titelvertrag und post-launch Verifikation; direkte DB-Mutation ist nicht v1-Default. |
| Queue-Datei | Im Repo frei implementierbar. | Robuster Fallback und Audit-Vertrag, wenn Launch nicht gewollt oder nicht moeglich ist. |

Entscheidung: Implementiere ein kleines lokales Tool unter `skills-repo/tools/AgentDeliverySessionLauncher.cs`. Der Name bindet das Tool sichtbar an den Agent Delivery Workflow, ohne es auf Child-only Sessions zu begrenzen. Das Tool nutzt den vorhandenen Stil der file-based .NET Tools, nimmt einen Session-Gegenstand ueber `--target-id <id>` und einen Agent-Provider ueber `--agent <id>` an und arbeitet in drei Modi:

1. `--mode queue`: validiert Handoff/Index/Agent-Adapter, erzeugt Startauftrag, Prompt, Manifest und Evidence, startet aber keine Session.
2. `--mode launch`: validiert, erzeugt Startauftrag und startet einen frischen non-interactive Run ueber den gewaehlten Agent-Adapter. In v1 ist nur `--agent codex` launchfaehig und nutzt `codex exec` mit Prompt aus stdin.
3. `--mode auto`: nutzt `launch`, wenn der gewaehlte Agent-Adapter implementiert ist und alle Launch-Preflights gruen sind; sonst `queue` oder bei nicht queuefaehigem Adapter `manual_start_required`.

Ein direkter Launch ist nur dann `launched`, wenn der Prozess wirklich gestartet wurde und die Run-Evidence den verwendeten Prompt, Startzeit, Ziel-Workspace, Handoff-Pfad, Target-ID, Mechanismus, Exitstatus und soweit verfuegbar Session-ID oder Logpfad enthaelt. Andernfalls ist der Ergebnisstatus `queued`, `manual_start_required`, `blocked` oder `failed`.

## 2.1 Agent Provider Contract

Der Launcher ist provider-neutral im Artefaktvertrag, aber nicht provider-beliebig in der Ausfuehrung. `--agent codex` ist der Default und der einzige in dieser Spec zu implementierende Launch-Adapter.

Pflichtregeln:

1. CLI akzeptiert `--agent <provider-id>`; wenn der Parameter fehlt, gilt `codex`.
2. `launch-request.json` und `evidence.json` muessen den angeforderten Provider, den tatsaechlich verwendeten Adapter, dessen Faehigkeit und dessen Version/Command-Vertrag speichern.
3. `codex` Adapter:
   - `launch_capability: "launch"`
   - command contract: `codex exec --json -C <target_workspace> --output-last-message <last-message.md> -`
   - Prompt wird aus `start-prompt.md` per stdin uebergeben.
4. Nicht implementierte Provider duerfen nicht still auf Codex fallen. Sie muessen als `adapter_status: "unsupported"` dokumentiert werden.
5. Bei `--agent <unsupported>` und `--mode launch` ist das Ergebnis `manual_start_required` oder `blocked`, niemals `launched`.
6. Bei `--agent <unsupported>` und `--mode queue` darf ein vollstaendiger provider-neutraler Startauftrag entstehen, aber nur mit `status: "manual_start_required"` oder einem expliziten `queued`-Status fuer einen spaeteren Runner, wenn ein maschinenlesbarer Queue-Consumer fuer diesen Provider existiert. In v1 existiert kein solcher Consumer; daher ist `manual_start_required` der erwartete Status.
7. Der Startprompt selbst bleibt workflow-neutral und darf keine Codex-spezifischen Anweisungen enthalten, ausser der gewaehlte Adapter benoetigt eine klar markierte, harmlose Adapter-Hinweiszeile. Der Handoff-Kontext bleibt die fuehrende Quelle.
8. Neue Provider-Adapter sind spaetere, separate Changes. Sie muessen eigene Preflight-, Command-, Evidence- und Secret-Gates ergaenzen, bevor sie `launched` oder `queued` als automatischen Uebergang melden duerfen.

## 2.2 Skill Integration Contract

Der Launcher ist Teil des Agent Delivery Workflows, nicht nur ein loses Tool. Die Implementierung muss deshalb die relevanten Skills so patchen, dass sie die Launcher-Evidence erzeugen, verlangen oder auswerten koennen.

Pflichtintegration:

| Skill / Dokument | Pflichtaenderung | Testbarer Nachweis |
|---|---|---|
| `docs/doc-workflow.md` | Definiert "Agent Delivery Session Launch/Queue Evidence" als eigenen Handoff-Nachweis nach Child/Parent/Workflow-Step-Handoffs. Erklaert die Statuswerte `launched`, `queued`, `manual_start_required`, `blocked`, `failed` und den Standardort `_specs/agent-delivery-session-launches/`. | `rg` findet den Evidence-Begriff, Statusliste, Toolname und Standardpfad. |
| `spec-orchestrator` | Wenn ein neuer fuehrender Handoff erzeugt oder aktualisiert wird, muss der Skill entweder `AgentDeliverySessionLauncher.cs --mode queue` empfehlen/ausfuehren oder explizit dokumentieren, warum Launch/Queue blockiert ist. Er darf einen Handoff nicht mehr als vollstaendigen automatisierten Uebergang darstellen, solange keine Launcher-Evidence existiert. | Skilltext nennt Tool, Queue/Launch-Evidence und Blocked-Fallback. |
| `child-spec-hardening` | Bei `IMPLEMENTATION READY` oder `READY WITH NON-BLOCKING NOTES` muss nach dem persistierten Handoff ein Launcher-Queue-/Launch-Schritt entstehen oder als blockiert dokumentiert werden. Der Hardening-Handoff bleibt nicht bei Copy/Paste stehen. | Skilltext koppelt Implementation-ready Handoff an `AgentDeliverySessionLauncher.cs` und `agent-delivery-session-launches`. |
| `spec-change-delivery` | Wenn eine Delivery aus einem Handoff startet, prueft der Skill zusaetzlich zur Handoff-/Index-Readiness, ob es eine aktuelle Launcher-Evidence fuer dieselbe Target-ID und denselben Handoff-Pfad gibt. `manual_start_required` ist kein automatischer Uebergangserfolg; `blocked`/`failed` blockieren Delivery. | Skilltext nennt Statusauswertung und Target-/Handoff-Abgleich. |
| `spec-closeout` | Beim Freigeben des naechsten fuehrenden Handoffs muss Closeout den naechsten Startauftrag erzeugen/queueen oder den Handoff im Control Index als nicht gestartet/blockiert markieren. | Skilltext nennt naechsten Handoff plus Launcher-Evidence als Closeout-Sync-Pflicht. |
| `agent-delivery-retro-review` | Meta-Review prueft, ob der Workflow wirklich `launched`/`queued` Evidence erzeugt hat oder nur Handoff-Dateien/Prompts. Fehlende Launcher-Evidence ist ein Finding. | Skilltext nennt Launch/Queue-Evidence als Reviewfrage/Finding-Kategorie. |

Integrationsregel:
1. Ein Agent-Delivery-Handoff ist weiterhin die fachliche Startquelle.
2. Ein Agent-Delivery-Session-Launch-Request ist der technische Uebergangsnachweis.
3. Skills duerfen "frische Session gestartet/gequeued" nur behaupten, wenn `launch-request.json`/`evidence.json` mit `status` `launched` oder `queued` fuer dieselbe Target-ID und denselben Handoff-Pfad existiert.
4. Wenn ein Skill aus Sicherheits-, Adapter- oder Konsistenzgruenden nur `manual_start_required` erzeugen kann, muss er das als manuellen Rest klar ausweisen.
5. `blocked` und `failed` muessen in den Control-Artefakten sichtbar bleiben und duerfen nicht durch einen neu formulierten Copy/Paste-Prompt ueberdeckt werden.

## 2.3 Codex App Visibility and Title Contract

Fuer den `codex` Adapter ist App-Sichtbarkeit ein eigener Teil des Launch-Vertrags. Ein gestarteter Run soll nicht irgendwo im lokalen Verlauf verschwinden, sondern im gleichen Projektkontext sichtbar sein wie der Handoff-Run.

Lokaler Befund vom 2026-05-08:

1. `codex exec -C <dir>` schreibt persistierte Thread-Metadaten mit `cwd=<dir>` in die lokale Codex-Thread-Datenbank.
2. Die Codex-App/Extension-Datenbank `~/.codex/state_5.sqlite` enthaelt eine Tabelle `threads` mit `cwd`, `title`, `source`, `rollout_path`, `first_user_message`, Git-Metadaten und Zeitstempeln.
3. `codex exec --help` zeigt keinen offiziellen `--title` Parameter.
4. `codex exec` Threads koennen lokal als `source='exec'` auftauchen. Die tatsaechliche Anzeige in der App-Seitenleiste muss nach Launch verifiziert werden, statt nur angenommen zu werden.

Pflichtregeln:

1. Der Launcher muss fuer `--agent codex --mode launch` immer `codex exec -C <target_workspace>` verwenden, nicht den aktuellen Shell-CWD und nicht den Fixture-/Handoff-Dateiordner, ausser der Handoff setzt den Target Workspace explizit anders.
2. `target_workspace` muss dem Projekt entsprechen, in dem die Parent-/Handoff-Session sichtbar sein soll. Fuer shared-ai-docs ist das `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`.
3. `launch-request.json` und `evidence.json` muessen `project_cwd`, `codex_thread_id`, `codex_rollout_path`, `codex_thread_source`, `codex_thread_title_observed`, `codex_thread_cwd_observed` und `codex_app_visibility_status` aufnehmen, soweit lokal verfuegbar.
4. `codex_app_visibility_status` nutzt diese Werte:
   - `verified_same_project`: lokaler Thread-Datensatz wurde gefunden und `cwd` entspricht `target_workspace`.
   - `launched_unverified`: Run wurde gestartet, aber Thread-Metadaten konnten nicht gelesen oder nicht eindeutig zugeordnet werden.
   - `wrong_project`: Thread-Datensatz wurde gefunden, aber `cwd` weicht vom `target_workspace` ab.
   - `not_app_visible`: lokaler Thread-Datensatz fehlt oder App-Index kennt den Run nicht.
   - `not_applicable`: Provider ist nicht `codex` oder Modus ist nicht `launch`.
5. `launched` darf fuer Codex zwar den Prozessstatus beschreiben, aber die Evidence muss zusaetzlich sagen, ob die App-Projektzuordnung `verified_same_project`, `launched_unverified`, `wrong_project` oder `not_app_visible` ist. `wrong_project` ist ein Workflow-Finding und blockiert die Behauptung "im richtigen Projekt gestartet".
6. Der Launcher erzeugt vor dem Start einen deterministischen `session_title` aus Target-ID, Target-Rolle, naechstem Skill und kurzem Scope, z. B. `DWT-S2 spec-change-delivery - L2 parent orchestration`.
7. Solange `codex exec` keinen offiziellen Titelparameter anbietet, muss der Prompt mit einer kurzen Titelzeile beginnen:

```md
Session Title: DWT-S2 spec-change-delivery - L2 parent orchestration
```

8. Nach Launch prueft der Launcher, ob ein lokaler `title` beobachtet werden kann. Wenn der beobachtete Titel nicht dem gewuenschten `session_title` entspricht, bleibt das kein Launch-Fehler, aber die Evidence muss `title_status: "not_applied"` oder `title_status: "observed_different"` enthalten.
9. Direkte Mutation der Codex-App-Datenbank, `session_index.jsonl` oder anderer interner Metadaten ist in v1 kein Default und darf nur als spaeterer expliziter Adapter-Modus mit Backup, Schema-Pruefung und User-Freigabe spezifiziert werden. Die v1-Loesung setzt keinen nicht dokumentierten App-Titel durch direkte DB-Edits.
10. Wenn spaeter ein offizieller Codex-App-/CLI-Mechanismus zum Setzen des Thread-Titels verfuegbar ist, darf der Codex-Adapter ihn nutzen und muss dann `title_status: "applied"` verifizieren.

## 3. Startauftrag-Vertrag

Das Tool erzeugt pro Run einen stabilen Run-Ordner:

```text
_specs/agent-delivery-session-launches/<UTC timestamp>-<target-id>/
  launch-request.json
  start-prompt.md
  evidence.json
  agent-events.jsonl              # nur bei launch, falls der Adapter JSONL-Events ausgibt
  last-message.md                 # nur bei launch, falls erzeugt
```

`launch-request.json` ist maschinenlesbar und muss mindestens diese Felder enthalten:

```json
{
  "schema_version": "agent-delivery.session-launch.v1",
  "status": "queued",
  "created_at": "2026-05-08T00:00:00Z",
  "started_at": null,
  "completed_at": null,
  "parent": "_specs/parent.md",
  "target_id": "DWT-S4",
  "target_role": "child",
  "target_spec": "_specs/child.md",
  "control_index": "_specs/parent.md#Delivery Orchestration Pack",
  "handoff_path": "_specs/child-session-handoffs/dwt-s4-session-handoff.md",
  "target_workspace": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "project_cwd": "/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs",
  "session_title": "DWT-S4 spec-change-delivery - reporting contract",
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
  "agent": {
    "requested_provider": "codex",
    "adapter_id": "codex-cli",
    "adapter_status": "supported",
    "launch_capability": "launch",
    "command_contract": "codex exec --json -C <target_workspace> --output-last-message <last-message.md> -"
  },
  "mechanism": {
    "type": "queue",
    "recommended_command": "codex exec -C ... - < start-prompt.md",
    "actual_command": null,
    "adapter_available": true
  },
  "evidence_paths": {
    "prompt": "_specs/agent-delivery-session-launches/.../start-prompt.md",
    "events": null,
    "last_message": null
  },
  "codex_app": {
    "visibility_status": "not_applicable",
    "thread_id": null,
    "rollout_path": null,
    "thread_source": null,
    "thread_cwd_observed": null,
    "thread_title_observed": null,
    "title_status": "not_applicable"
  },
  "blockers": [],
  "warnings": []
}
```

`start-prompt.md` ist exakt der Prompt, der bei `launch` per stdin an `codex exec` uebergeben wird oder bei `queue`/`manual_start_required` manuell verwendbar ist. Er muss die Handoff-Inhalte direkt enthalten, nicht nur auf das Handoff verweisen.

Pflichtinhalte des Prompts:

1. Parent.
2. Target-ID und Target-Rolle, z. B. `child`, `parent`, `closeout`, `hardening` oder `workflow-step`.
3. Target Spec oder fuehrendes Target-Artefakt.
4. Control Index / Queue, falls fuer diesen Target-Typ vorhanden.
5. Handoff File.
6. Target Repository / Working Directory.
7. Project CWD / Codex-App-Projektkontext.
8. Session Title.
9. Naechster Skill/Modus.
10. Angeforderter Agent-Provider und Adapter-Status.
11. Scope Summary.
12. Non-Goals.
13. Allowed Write-Set.
14. Shared / Read-only Files.
15. Verification Lifecycle oder Verification Commands.
16. Evidence / OpenSpec.
17. Offene Blocker oder non-blocking Notes.
18. Explizite Anweisung, zuerst Handoff, Control Index/Queue soweit vorhanden und das relevante Verdict zu validieren und nur im erlaubten Write-Set zu arbeiten.

Normalisierungsregel:
- Bestehende Child Session Handoffs bleiben gueltige Eingaben. Das Tool liest daraus `Child` oder `Stable Child ID` als `target_id`, `Child Spec` als `target_spec` und `Child Index / Queue` als `control_index`.
- Spaetere Parent- oder Workflow-Step-Handoffs duerfen dieselben generischen Felder direkt setzen (`Target ID`, `Target Role`, `Target Spec`, `Control Index / Queue`). Sie sind keine v1-Pflicht, aber der Name und Vertrag des Tools duerfen sie nicht ausschliessen.
- Child-spezifische Validierung wie `ValidateChildReadiness.cs` laeuft nur, wenn `target_role` `child` ist oder wenn ein Child-Handoff erkannt wird.

## 4. Konsistenz- und Sicherheits-Gates

Vor Launch oder Queueing muss das Tool diese Gates pruefen:

| Gate | Blockiert wenn |
|---|---|
| Handoff existiert und ist parsebar | Datei fehlt, Pflichtfelder fehlen oder mehrere Target-IDs widersprechen sich. |
| Target-ID konsistent | CLI-`--target-id`, Handoff `Target ID`/`Child`/`Stable Child ID`, Handoff-Dateiname und Control-Index-Zeile widersprechen sich. |
| Control Index operativ | Fuer Child-Handoffs fehlt der Child Index, die Zielzeile fehlt, der Handoff-Pointer fehlt oder zeigt auf einen anderen Pfad. Fuer Parent-/Workflow-Step-Handoffs gilt dieses Gate nur, wenn ein Control Index im Handoff benannt ist. |
| Verdict passend zum naechsten Skill | `spec-change-delivery` ohne `IMPLEMENTATION READY` oder akzeptiertes `READY WITH NON-BLOCKING NOTES`; `child-spec-hardening` ohne hardening-faehigen Status wie `needs_hardening`, `ready_candidate`, `NEEDS HARDENING` oder expliziten Blocker; Closeout ohne akzeptierte Delivery-Evidence. |
| Write-Set enforceable | `Allowed Write-Set` fehlt, ist leer, enthaelt `TBD`, `as needed`, `likely`, `related files`, `etc.` oder keine konkreten Pfade/Globs. |
| Target Workspace | Pfad fehlt, ist nicht absolut oder existiert nicht im lokalen Environment. |
| Codex App Project | `--agent codex --mode launch` wuerde ohne `-C <target_workspace>` laufen; `target_workspace` ist nicht der erwartete Projekt-CWD; nach Launch wird `wrong_project` beobachtet. |
| Session Title | `session_title` fehlt, ist laenger als 80 Zeichen, enthaelt Zeilenumbrueche oder kann nicht als erste Prompt-Zeile persistiert werden. |
| Agent Provider | `--agent` fehlt nicht und defaultet nicht sauber auf `codex`; angeforderter Provider ist nicht implementiert und der Modus behauptet trotzdem `launched` oder automatisches `queued`; Adapter-Command-Vertrag fehlt. |
| Secret-Guard | Handoff, Startauftrag oder Prompt enthalten offensichtliche Secret-Muster wie API-Key-/Token-Prefixe, `password=`, `Authorization: Bearer`, private key blocks oder `.env`-Werte. |
| Prompt-Vollstaendigkeit | Einer der Pflichtinhalte aus Abschnitt 3 fehlt. |
| Launch-Preflight | Der gewaehlte Adapter ist `codex` und `codex exec` fehlt; Modus ist `launch`/`auto`, Ziel-CWD ist ungueltig oder der command contract kann nicht gebaut werden. |

Wenn ein Gate vor Prompt-Persistenz ein Secret findet, darf das Tool keinen vollstaendigen Prompt und kein unredigiertes Manifest schreiben. Es schreibt nur `evidence.json` mit `status: "blocked"`, redigierter Diagnose und ohne Secret-Wert.

Das vorhandene `ValidateChildReadiness.cs` bleibt fuer implementation-ready Child-`spec-change-delivery`-Starts die fuehrende Readiness-Pruefung. `AgentDeliverySessionLauncher.cs` soll es nicht duplizieren, sondern entweder intern aufrufen oder dieselben Pflichtbedingungen mit klarer Begruendung referenzieren, wenn der Target-Typ ein Child ist. Fuer Parent-/Workflow-Step-Handoffs darf das Tool keine Child-Readiness erzwingen; es muss dann nur die im Handoff benannten Control-Artefakte und Verdicts pruefen. Fuer Hardening-Starts darf die Readiness-Pruefung nicht faelschlich `IMPLEMENTATION READY` verlangen; sie muss den naechsten Skill beruecksichtigen.

## 5. Statusmodell

| Status | Bedeutung | Evidence-Anforderung |
|---|---|---|
| `launched` | Eine neue frische non-interactive Agent-Session wurde ueber einen implementierten Adapter mit genau dem persistierten `start-prompt.md` gestartet. In v1 ist das nur `codex` via `codex exec`. | `agent.requested_provider`, `adapter_id`, `started_at`, `target_workspace`, `handoff_path`, `target_id`, `target_role`, `actual_command`, Exitstatus, `agent-events.jsonl` oder adapter-spezifischer Logpfad, Prompt-Hash, soweit verfuegbar Session-ID. |
| `queued` | Kein direkter Start wurde versucht oder `auto` fiel bewusst auf Queue zurueck; ein vollstaendiger maschinenlesbarer Auftrag und Prompt liegen fuer einen implementierten Queue-/Launch-Adapter vor. In v1 gilt das fuer `codex`. | `launch-request.json`, `start-prompt.md`, `agent.requested_provider`, `adapter_status`, `recommended_command`, Blocker leer oder nur nicht-blockierende Launch-Warnung. |
| `manual_start_required` | Der Startprompt ist vollstaendig persistiert, aber der angeforderte Agent-Provider hat keinen implementierten Launch-/Queue-Adapter oder der nachgewiesene lokale Mechanismus reicht nicht fuer den angeforderten interaktiven/App-Start. | Vollstaendiger Prompt, `adapter_status: "unsupported"` oder Begruendung warum kein direkter Mechanismus verfuegbar ist, empfohlenes manuelles Kommando oder App-Schritt. |
| `blocked` | Konsistenz-, Verdict-, Workspace- oder Secret-Gate verhindert Start und Queue als gueltigen Auftrag. | Redigierte Blocker-Liste, keine ungueltige Startfreigabe, kein vollstaendiger Prompt bei Secret-Blocker. |
| `failed` | Launch wurde versucht, aber der Prozess schlug fehl oder Evidence konnte nicht geschrieben werden. | Exitcode, stderr/stdout-Auszug ohne Secrets, Prompt-Hash, Run-Pfad, naechster sicherer Schritt. |

Akzeptanzregel: Spaetere Skills duerfen nur `launched` und `queued` als erfolgreiche Automatisierungsuebergabe werten. `manual_start_required` ist besser als Chat-only, aber kein automatischer Start/Queue-Erfolg. `blocked` und `failed` blockieren Folge-Delivery.

## 6. Beispiel-Startprompt aus bestehendem Child-Handoff

Aus `_specs/child-session-handoffs/dwt-s4-session-handoff.md` muss das Tool sinngemaess diesen generischen Agent-Delivery-Session-Prompt erzeugen. Dass die Quelle ein Child-Handoff ist, erscheint als `Target Role: child`, nicht im Toolnamen.

```md
Session Title: DWT-S4 spec-change-delivery - reporting contract

Wir arbeiten in /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs.

Starte eine frische Agent-Delivery-Session aus folgendem persistierten Handoff.

Pflicht: Lies zuerst das Handoff, den Control Index / die Queue und das Target-Artefakt. Validiere, dass Target-ID, Target-Rolle, Handoff-Pfad, Control Index, aktueller Verdict, Target Workspace und Allowed Write-Set konsistent sind. Arbeite nur im erlaubten Write-Set. Wenn ein Gate stale, widerspruechlich oder unvollstaendig ist, stoppe mit NOT READY und persistiere Evidence statt zu implementieren.

- Parent: _specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md
- Target ID: DWT-S4
- Target Role: child
- Target Spec: _specs/2026-05-07 DocWorkflow Agent Delivery Testsuite DWT-S4 Summary Telemetry Style Reporting Contract.md
- Control Index / Queue: _specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md section Delivery Orchestration Pack
- Handoff File: _specs/child-session-handoffs/dwt-s4-session-handoff.md
- Target Repository / Working Directory: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Project CWD / App-Kontext: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
- Next Mode / Skill: spec-change-delivery
- Requested Agent Provider: codex
- Agent Adapter Status: supported; codex-cli via codex exec
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

1. Given ein gueltiges implementation-ready Delivery-Handoff mit operativem Control Index, when `AgentDeliverySessionLauncher.cs --target-id DWT-LAUNCH-1 --agent codex --mode queue` laeuft, then entstehen `launch-request.json`, `start-prompt.md` und `evidence.json` mit `status: "queued"`, `target_id: "DWT-LAUNCH-1"`, `agent.requested_provider: "codex"` und allen Pflichtfeldern.
2. Given dasselbe Handoff und lokal verfuegbares `codex exec`, when `--agent codex --mode launch --dry-run` laeuft, then wird der exakt empfohlene `codex exec`-Befehl inklusive stdin-Promptvertrag persistiert, aber nicht ausgefuehrt.
3. Given dasselbe Handoff und `--agent codex --mode launch` ohne Dry-Run, when der Codex-Prozess erfolgreich startet und beendet, then ist der Status `launched`, der verwendete Prompt entspricht bytegleich `start-prompt.md`, und Run-Evidence enthaelt Target-ID, Target-Rolle, Agent-Provider, Adapter-ID, Startzeit, Ziel-Workspace, Project-CWD, Handoff, Mechanismus, Exitstatus und Log-/Eventpfad soweit verfuegbar.
4. Given ein Handoff mit fehlendem Pflichtfeld, widerspruechlicher Target-ID, falschem Control-Index-Pointer oder nicht passendem Verdict, when das Tool laeuft, then ist der Status `blocked`, und es entsteht keine erfolgreiche Queue-/Launch-Freigabe.
5. Given ein valides Handoff, aber fehlendes `codex exec` im PATH, when `--agent codex --mode auto` laeuft, then entsteht `queued` mit `recommended_command` oder `manual_start_required`, je nachdem ob ein nicht-interaktiver CLI-Fallback sauber formulierbar ist.
6. Given ein valides Handoff und `--agent unsupported-demo`, when das Tool mit `--mode queue` oder `--mode launch --dry-run` laeuft, then entsteht kein `launched`; Evidence enthaelt `adapter_status: "unsupported"` und Status `manual_start_required` oder `blocked`.
7. Given ein Handoff mit offensichtlichem Secret-Muster, when das Tool laeuft, then blockiert es vor Persistenz eines vollstaendigen Prompts und schreibt nur redigierte Evidence.
8. Given ein Launch-Prozess mit non-zero Exitcode, when das Tool die Evidence schreiben kann, then ist der Status `failed`, nicht `queued` und nicht `launched`.
9. Given spaetere Skills lesen `launch-request.json`, when `status` `queued` oder `launched` ist, then koennen sie eindeutig erkennen, welcher Agent-Provider, welche Target-ID, welche Target-Rolle, welches Handoff, welcher Prompt und welche Evidence fuer den Uebergang fuehrend sind.
10. Given ein Implementierungsdiff fuer diese Spec, when die Skill-Integration geprueft wird, then nennen `docs/doc-workflow.md`, `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout` und `agent-delivery-retro-review` den Launcher oder die Agent-Delivery-Session-Launch/Queue-Evidence an der jeweils passenden Workflow-Stelle.
11. Given ein Skill erzeugt oder bewertet einen Handoff, when keine passende Launcher-Evidence mit derselben Target-ID und demselben Handoff-Pfad existiert, then darf der Skill keinen automatisierten Session-Uebergang behaupten; er muss `manual_start_required`, `blocked` oder fehlende Queue-Evidence sichtbar machen.
12. Given ein Codex-Launch laeuft, when der Launcher den Prozess startet, then nutzt der empfohlene und tatsaechliche Command `codex exec -C <target_workspace>` und Evidence speichert `project_cwd`.
13. Given ein Codex-Launch erfolgreich beendet ist, when lokale Codex-Thread-Metadaten lesbar sind, then speichert Evidence `codex_app.visibility_status`; `verified_same_project` ist nur erlaubt, wenn der beobachtete Thread-`cwd` exakt dem `target_workspace` entspricht.
14. Given ein Startauftrag erzeugt wird, when `session_title` berechnet wird, then ist er deterministisch, kurz, einzeilig, in `launch-request.json` gespeichert und die erste Zeile von `start-prompt.md`.

## 8. Verification Commands

Ausfuehrungskontext: macOS oder Linux, Shell `zsh`/`bash`, Arbeitsverzeichnis `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`. Commands duerfen keine echten Produkt- oder Delivery-Arbeiten starten, ausser der Operator waehlt explizit `--mode launch` ohne `--dry-run`.

Risk-based Preflight:

```sh
command -v codex
codex exec --help
dotnet --info
```

Syntax/Build:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help
git diff --check
```

Skill Integration Static Check:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
rg -n "AgentDeliverySessionLauncher|Agent Delivery Session Launch/Queue Evidence|agent-delivery-session-launches|launch-request.json|manual_start_required|blocked|failed" \
  docs/doc-workflow.md \
  skills-repo/skills/spec-orchestrator/SKILL.md \
  skills-repo/skills/child-spec-hardening/SKILL.md \
  skills-repo/skills/spec-change-delivery/SKILL.md \
  skills-repo/skills/spec-closeout/SKILL.md \
  skills-repo/skills/agent-delivery-retro-review/SKILL.md
```

Success criteria: every listed file has a relevant hit; `spec-change-delivery` and `spec-closeout` mention status handling for `manual_start_required`, `blocked` or `failed`; `spec-orchestrator` and `child-spec-hardening` mention queue/launch creation after handoff generation; `agent-delivery-retro-review` can detect missing launch/queue evidence as a workflow finding.

Codex App Metadata Preflight:

```sh
sqlite3 /Users/dh/.codex/state_5.sqlite '.schema threads'
sqlite3 -line /Users/dh/.codex/state_5.sqlite \
  "select id, source, cwd, title, rollout_path from threads order by updated_at desc limit 3;"
```

Success criteria: command is optional and local-Codex-specific; when available, schema contains `cwd`, `title`, `source` and `rollout_path`; launcher implementation may use this read-only to verify `codex_app.visibility_status`. If unavailable, launch evidence must use `launched_unverified` instead of claiming app visibility.

Positive Queue-Fixture:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff tests/agent-delivery-session-launcher/fixtures/valid-ready/child-session-handoff.md \
  --target-id DWT-LAUNCH-1 \
  --agent codex \
  --control-index tests/agent-delivery-session-launcher/fixtures/valid-ready/control-index.md \
  --mode queue \
  --out /tmp/agent-delivery-session-launcher-positive
```

Success criteria: exit code `0`; `/tmp/agent-delivery-session-launcher-positive/**/launch-request.json` exists; JSON status is `queued`; JSON contains `target_id: "DWT-LAUNCH-1"`, `target_role: "child"`, `agent.requested_provider: "codex"` and `adapter_status: "supported"`; `start-prompt.md` contains Parent, Target ID, Target Role, Target Spec, Control Index, Handoff, Target Workspace, Next Skill, Agent Provider, Scope, Non-Goals, Allowed Write-Set, Read-only Files, Verification, Evidence/OpenSpec and Notes.

Negative Consistency Fixture:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff tests/agent-delivery-session-launcher/fixtures/invalid-stale/child-session-handoff.md \
  --target-id DWT-LAUNCH-1 \
  --agent codex \
  --control-index tests/agent-delivery-session-launcher/fixtures/invalid-stale/control-index.md \
  --mode queue \
  --out /tmp/agent-delivery-session-launcher-negative
```

Success criteria: non-zero exit code or documented blocked exit code; evidence status is `blocked`; no successful `queued` or `launched` status exists.

Launch Dry-Run:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff tests/agent-delivery-session-launcher/fixtures/valid-ready/child-session-handoff.md \
  --target-id DWT-LAUNCH-1 \
  --agent codex \
  --control-index tests/agent-delivery-session-launcher/fixtures/valid-ready/control-index.md \
  --mode launch \
  --dry-run \
  --out /tmp/agent-delivery-session-launcher-dry-run
```

Success criteria: status is `queued` or `manual_start_required` with `dry_run: true`; `recommended_command` contains `codex exec` and `-C /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`; `session_title` is present; no Codex run is executed.

Unsupported Agent Provider:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff tests/agent-delivery-session-launcher/fixtures/valid-ready/child-session-handoff.md \
  --target-id DWT-LAUNCH-1 \
  --agent unsupported-demo \
  --control-index tests/agent-delivery-session-launcher/fixtures/valid-ready/control-index.md \
  --mode queue \
  --out /tmp/agent-delivery-session-launcher-unsupported
```

Success criteria: no `launched` status; evidence records `requested_provider: "unsupported-demo"` and `adapter_status: "unsupported"`; status is `manual_start_required` or `blocked`; the prompt remains provider-neutral and fully usable manually unless a separate consistency or secret gate blocks prompt persistence.

Optional Real Launch Gate:

```sh
cd /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- \
  --handoff tests/agent-delivery-session-launcher/fixtures/valid-ready/child-session-handoff.md \
  --target-id DWT-LAUNCH-1 \
  --agent codex \
  --control-index tests/agent-delivery-session-launcher/fixtures/valid-ready/control-index.md \
  --mode launch \
  --out /tmp/agent-delivery-session-launcher-real
```

Success criteria: only run with explicit operator intent; status `launched` on zero exit, `failed` on non-zero exit; evidence includes prompt hash, command, start time, exit status, event/log path if emitted by Codex, `session_title`, `project_cwd`, and `codex_app.visibility_status`. If local metadata reports a different `cwd`, evidence must be `wrong_project`, not `verified_same_project`.

Anti-loop rule: These commands verify the launcher contract and one optional real launch. They must not spawn recursive verification of newly launched child work.

## 9. Files Expected In Implementation

Minimal write-set:

1. `skills-repo/tools/AgentDeliverySessionLauncher.cs`.
2. `tests/agent-delivery-session-launcher/fixtures/valid-ready/**`.
3. `tests/agent-delivery-session-launcher/fixtures/invalid-stale/**`.
4. Optional `tests/agent-delivery-session-launcher/README.md` if fixture intent is not obvious.
5. Optional `tests/agent-delivery-session-launcher/fixtures/unsupported-agent/**` only if the unsupported-provider case is clearer as its own fixture than as a CLI-variant of `valid-ready`.
6. Minimal doc/skill patches:
   - `docs/doc-workflow.md`: add "Agent Delivery Session Launch/Queue Evidence" rule.
   - `skills-repo/skills/spec-orchestrator/SKILL.md`: when producing a leading handoff, require Launcher queue/launch evidence or explicit blocked/manual state.
   - `skills-repo/skills/child-spec-hardening/SKILL.md`: after implementation-ready handoff, run or recommend launcher queue/launch.
   - `skills-repo/skills/spec-change-delivery/SKILL.md`: if starting from Handoff, prefer launcher evidence when available.
   - `skills-repo/skills/spec-closeout/SKILL.md`: next child handoff must be launched/queued or explicitly blocked/manual.
   - `skills-repo/skills/agent-delivery-retro-review/SKILL.md`: meta-review checks whether launch/queue evidence exists or only handoff text was produced.

No product repo paths or original KI-fuer-KMU specs are in the write-set.

## 10. Definition of Done / Closeout Evidence

Implementation is done when:

1. The Agent Delivery Session Launcher reads at least one valid handoff fixture and emits a complete startauftrag.
2. The startauftrag includes the full Handoff context, not just references.
3. Invalid/stale handoffs are blocked before launch/queue success.
4. Queue mode persists machine-readable manifest, exact prompt, requested agent provider, adapter status and evidence.
5. Launch dry-run proves the `codex` adapter command contract without starting real work.
6. Unsupported Agent Provider path proves that non-Codex agents are represented as extension points without false launch/queue success.
7. Optional real launch, if run, persists `launched` or `failed` evidence truthfully.
8. Status values are exclusive and documented.
9. Secret guard prevents obvious secret persistence.
10. Minimal workflow/skill docs tell future skills where to look for launch/queue evidence.
11. Skill integration static check proves every relevant Agent Delivery Workflow skill knows how to create or consume Agent Delivery Session Launcher evidence.
12. Codex adapter uses `-C <target_workspace>` and records app visibility metadata when locally available.
13. The launcher computes and persists a deterministic `session_title`; without an official Codex title API it uses the title as the first prompt line and records observed title status after launch when available.
14. `git diff --check` passes.

## 11. Content Quality Review Result

Autonomous review pass after authoring:

| Check | Result |
|---|---|
| Correctness / domain fit | Pass. The Spec addresses the actual missing transition from Agent Delivery Handoff to fresh agent session or queued startauftrag. |
| Scope discipline | Pass. The Scope remains limited to shared-ai-docs tooling, fixtures and minimal workflow/skill docs; non-Codex agents are an adapter contract only, not additional implementations. |
| Completeness | Pass. Normal path, queue fallback, unsupported-provider/manual path, blocked path, failed launch, secret path, app visibility, deterministic title and skill-integration path are covered. |
| Consistency | Pass. Statuses, agent-provider fields, Codex app visibility fields, title fields, evidence fields and skill responsibilities are synchronized between Review Control Surface, contract and acceptance criteria. |
| Feasibility | Pass. `codex exec` and file-based .NET tooling are locally available; non-Codex adapters, app-server and automations are not assumed. |
| Testability | Pass. Positive, negative, unsupported-provider, dry-run, skill-integration, Codex metadata preflight, optional launch and diff checks are specified with observable success criteria. |
| Traceability | Pass. Requirements trace to Agent Delivery Handoffs, Child Session Handoff as the first supported source shape, Child Index where applicable, existing readiness validator, user-stated status/evidence requirements and the provider-extensibility requirement. |
| Operational fit | Pass with one intentional constraint: direct launch is non-interactive `codex exec` through the `codex` adapter; other providers remain future extension until a stable local adapter contract exists. |
| Secret handling | Pass. Secret-like input blocks prompt persistence instead of redacting after the fact. |

Readiness verdict: `IMPLEMENTATION READY` for one bounded `spec-change-delivery` tooling change.

## History

| Date | Author | Change |
|---|---|---|
| 2026-05-08 | Codex | Initial implementation-ready Spec authored and hardened for Agent Delivery Session Launcher Automation. |
| 2026-05-08 | Codex | Added provider-neutral `--agent` contract with `codex` as the only v1 launch adapter and hardened unsupported-provider status/evidence rules. |
| 2026-05-08 | Codex | Renamed the tool contract to `AgentDeliverySessionLauncher.cs` and generalized Child-only IDs to Agent Delivery session targets. |
| 2026-05-08 | Codex | Added mandatory Agent Delivery Workflow skill integration scope and static verification for launcher evidence usage. |
| 2026-05-08 | Codex | Added Codex app project visibility and deterministic session title requirements with local metadata verification. |
| 2026-05-08 | Codex | Implemented AgentDeliverySessionLauncher tool, fixtures, queue/dry-run/manual/blocked evidence paths and workflow skill integration. |

SessionId: 2026-05-08-agent-delivery-session-launcher-automation-spec
