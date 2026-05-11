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
- `spec-orchestrator`
- `child-spec-hardening`
- `refine-plan`
- `spec-change-delivery`
- `spec-closeout`
- `doc-review-autoresolve`
- `retro-plan`

Hier werden die gemeinsamen Begriffe gepflegt:
- **Definition of Ready (DoR)**
- **Definition of Done (DoD)**
- **Decision Freeze Pack**
- **Session Briefing**
- **Child Index**
- **Child Session Handoff**
- **Review Control Surface**
- **Parallel Work Control Surface**
- **Mini-Retro**
- **Spec Goldstandard**
- **Agent Delivery Session Launch/Queue Evidence**

Die Skills dürfen diese Begriffe lokal kurz restaten, sollen aber **keine abweichenden Definitionen** einführen. Änderungen an der gemeinsamen Bedeutung werden zuerst hier gepflegt.

Die ausfuehrliche Goldstandard-Definition fuer Specs lebt in
[`docs/spec-goldstandard.md`](spec-goldstandard.md). Dieses Workflow-Dokument bleibt die kanonische Gate-Quelle; die Goldstandard-Datei definiert Varianten, Mindestbestandteile, Anti-Patterns, Kandidatenbewertung und den Prozess, mit dem eine Spec zur Goldstandard-Referenz erhoben wird.

## Session Briefing Template (kurz)

Bei groesseren Arbeiten, neuen Sessions, Kontextkomprimierung oder Skill-Wechsel zuerst ein kurzes Briefing herstellen. Es darf aus dem vorhandenen Kontext abgeleitet werden; nur blockierende Luecken werden zurueckgefragt.

```md
## Session Briefing

- Modus/Skill:
- Source of Truth:
- Ziel:
- Nicht-Ziele:
- In Scope:
- Erwarteter Output:
- Verification/Review:
- Offene Entscheidungen:
```

Regeln:
1. `Modus/Skill` benennt den aktiven Workflow-Schritt, z. B. `doc-coauthoring`, `spec-orchestrator`, `child-spec-hardening`, `doc-review-autoresolve` oder `spec-change-delivery`.
2. `Source of Truth` nennt die fuehrenden Dateien/Specs/Artefakte; keine Hybrid-Steuerung ohne explizite Entscheidung.
3. `Ziel`, `Nicht-Ziele`, `In Scope` und `Erwarteter Output` muessen vor groesseren Edits oder Implementierung klar sein.
4. Ausgeschlossene Themen werden als Nicht-Ziele sichtbar gehalten, damit sie nicht nebenbei in den Scope rutschen.
5. Bei Review-/Spec-Arbeit wird zusaetzlich die `Review Control Surface` der betroffenen Spec geprueft oder angelegt.

## Child Session Handoff Template (kurz)

Ein Child Session Handoff ist der kompakte Startpunkt fuer die naechste Child-Hardening-, Delivery- oder Closeout-Session. Es ersetzt nicht Parent Spec, Child Spec, OpenSpec oder Evidence; es verweist nur auf die fuehrenden Artefakte und die naechste erlaubte Aktion.

Persistenzregel:
1. Bei Parent/Child-Vorhaben muss jedes fuehrende Child Session Handoff als auffindbares Artefakt persistiert werden, nicht nur im Chat oder in einem Orchestration-Pack.
2. Standardort ist ein `child-session-handoffs/`-Ordner neben dem Child Index, z. B. `_specs/child-session-handoffs/s3-session-handoff.md`.
3. Wenn kein eigener Child-Index-Dateipfad existiert, liegt das Handoff neben dem Parent-, Slice-Plan- oder Delivery-Orchestration-Pack-Artefakt, das den Child Index enthaelt.
4. Der Child Index muss pro Child auf das persistierte Handoff zeigen. Ein reines Inline-Handoff ist nur als Fallback erlaubt, wenn der Index einen stabilen Abschnittsanker oder Patch-Zielpfad benennt.
5. Ein Handoff ist stale, wenn Target Repository / Working Directory, Child Spec, Hardening Verdict, Child Index, Evidence/OpenSpec-Status oder Next Action voneinander abweichen. Stale Handoffs duerfen nicht als Implementierungsfreigabe gelten.

```md
## Child Session Handoff

- Parent:
- Child:
- Child Spec:
- Child Index / Queue:
- Handoff File:
- Target Repository / Working Directory:
- Codex Session / Log:
- Session Evidence:
- Handoff Timestamp:
- Naechster Modus/Skill:
- Aktueller Verdict:
- Scope Summary:
- Non-Goals:
- Allowed Write-Set:
- Shared / Read-only Files:
- Verification Lifecycle:
  - Rehearsal / Preflight:
  - Delivery Gate:
  - Pre-Archive Closeout:
  - Post-Archive / Current Replay:
- Evidence / OpenSpec:
- Retained Evidence:
- Offene Blocker oder non-blocking Notes:
- Fresh Session empfohlen:
```

Regeln:
1. `spec-orchestrator` erzeugt oder aktualisiert ein persistiertes Handoff fuer den naechsten empfohlenen Child und verlinkt es im Child Index.
2. `child-spec-hardening` liefert bei `IMPLEMENTATION READY` oder `READY WITH NON-BLOCKING NOTES` immer ein persistiertes Handoff fuer die Implementierung und synchronisiert den Child-Index-Pointer.
3. `spec-change-delivery` darf ein Child-Handoff als Kickoff-Quelle nutzen, muss aber trotzdem Target Repository / Working Directory, Child Spec, Parent Conformance, Child Index und Hardening Verdict pruefen.
4. `spec-closeout` aktualisiert das naechste Handoff oder markiert es im Child Index als stale/blockiert, damit der naechste fuehrende Child nicht aus veralteten Status-/Evidence-Links startet.
5. Bei grossen Parent/Child-Vorhaben wird pro Child-Implementation normalerweise eine frische Session empfohlen.
6. Wenn ein Hardening-Run einen Child auf `IMPLEMENTATION READY` setzt, ist das ein Handoff-Punkt. Der Run liefert ein frisches Handoff und stoppt dort, ausser der User hat ausdruecklich denselben Run auch fuer Delivery freigegeben.
7. `Verification Lifecycle` trennt Command-Rehearsal, Delivery-Gate, Pre-Archive-Closeout und aktuellen Post-Archive-Replay. Ein nach OpenSpec-Archive ungueltiger Active-Change-Command darf nicht als aktueller Replay-Command im Handoff stehen bleiben.
8. Temp-Evidence darf als Laufnachweis dienen, aber accepted Baseline-Evidence muss entweder an einem stabilen Workspace-Pfad persistiert oder mit Retention-/Hash-/Wiederherstellungsanweisung im Handoff referenziert werden.

## Agent Delivery Session Launch/Queue Evidence

Ein Agent-Delivery-Handoff ist die fachliche Startquelle; die technische Uebergabe in eine frische Agent-Session wird durch Agent Delivery Session Launch/Queue Evidence belegt. Standardort ist `_specs/agent-delivery-session-launches/`. Das lokale Tool `skills-repo/tools/AgentDeliverySessionLauncher.cs` erzeugt pro Run mindestens `launch-request.json`, `start-prompt.md` und `evidence.json`; bei Launch koennen `agent-events.jsonl` und `last-message.md` dazukommen.

Rollen:
1. `AgentDeliverySessionLauncher.cs` ist das Basiswerkzeug fuer genau eine Session. Er erzeugt Queue-/Launch-Evidence und kann mit `--adapter codex-app-server` eine sichtbare Codex-App-Session starten.
2. `AgentDeliveryVisibleSessionController.cs` ist der externe Orchestrator fuer sichtbare Parent/Child-Session-Ketten. Er startet Parent und Children ausserhalb des Parent-Turns, konsumiert Child-Requests und ruft den Launcher pro Session auf.
3. Wenn ein Workflow eine controller-backed sichtbare Multi-Session-Kette verlangt, z. B. `MD-E2E-5`, darf die Parent-Session keine Child-Launcher-, `codex app-server`- oder sonstige Child-Start-Kommandos ausfuehren. Die Child-Starts muessen ueber den externen Controller laufen.
4. Skills duerfen fuer normale Handoff-/Queue-Arbeit direkt den Launcher verlangen. Fuer controller-backed sichtbare Multi-Session-Arbeit muessen sie Controller-Evidence, Controller-Requests/Responses und die darunterliegenden Launcher-Evidence zusammen pruefen.

Canonical Evidence Resolver:

```sh
dotnet run skills-repo/tools/WorkflowDoctor.cs -- --phase evidence-resolution --mode <launcher_only|controller_visible_multi_session|closeout_archive> ...
```

Der Resolver ist der kanonische Gate-Check fuer konkrete Launcher-/Controller-/Archive-Artefakte. Er gibt maschinenlesbares JSON aus:

- `schema_id: agent-delivery.evidence-resolution.v1`
- `verdict: pass | not_ready | fail`
- `mode: launcher_only | controller_visible_multi_session | closeout_archive`
- `target_id` oder `run_id`
- `evidence_paths`
- `blockers`
- `warnings`
- `recommended_next_action`

Claim-Level:

- `launcher_only --claim-level queued`: `queued` oder `launched` ist erlaubt, solange Target-ID, Handoff-Pfad, `launch-request.json`, `start-prompt.md` und `evidence.json` konsistent sind.
- `launcher_only --claim-level launched`: erfordert `status: launched`.
- `controller_visible_multi_session`: erfordert Controller-Summary, Requests, Responses, retained visible-session summary und passende per-session Launcher-Evidence. Parent-started Child-Launches blockieren den Gate.
- `closeout_archive`: erfordert eine gueltige visible-session archive summary. `retained_session_accepted`, explizite no-thread Status und echte Archive-Proofs koennen passieren; unarchivierte sichtbare Sessions, `manual_visible_missing_thread`, `archive_failed` und `proof_failed` blockieren.

Skills sollen fuer Evidence-Konsistenz diesen Resolver aufrufen oder verlangen und bei `not_ready` oder `fail` stoppen. `docs/doc-workflow.md` bleibt die kanonische Rollenbeschreibung; Skills sollen keine alternativen Launcher-/Controller-/Archive-Rollen definieren.

Statuswerte:
1. `launched`: ein implementierter Adapter hat eine frische Session wirklich gestartet.
2. `queued`: ein vollstaendiger maschinenlesbarer Startauftrag und Prompt liegen fuer einen implementierten Queue-/Launch-Adapter vor.
3. `manual_start_required`: der Prompt ist vollstaendig, aber der angeforderte Agent-Provider hat keinen implementierten automatischen v1-Adapter.
4. `blocked`: Konsistenz-, Verdict-, Workspace- oder Secret-Gate verhindert eine gueltige Startfreigabe.
5. `failed`: ein Launch wurde versucht, schlug aber fehl oder Evidence konnte nicht vollstaendig geschrieben werden.

Regeln:
1. Skills duerfen "frische Session gestartet/gequeued" nur behaupten, wenn `launch-request.json` und `evidence.json` fuer dieselbe Target-ID und denselben Handoff-Pfad existieren und `status` `launched` oder `queued` ist.
2. `manual_start_required` ist ein sichtbarer manueller Rest, aber kein automatisierter Uebergangserfolg.
3. `blocked` und `failed` blockieren Folge-Delivery und muessen in Control-Artefakten sichtbar bleiben.
4. Fuer `codex`-Launches muss Evidence `project_cwd` und `codex_app.visibility_status` enthalten; `verified_same_project` ist nur erlaubt, wenn der beobachtete Thread-`cwd` dem Target Workspace entspricht.
5. Ein semantischer `SessionId` wie `2026-05-08-...` ist nur ein menschlicher Alias. Fuer zukuenftige forensische Session-Evidence braucht ein Handoff entweder passende Launch/Queue-Evidence, eine echte Codex Session-ID plus `.codex/...jsonl` Logpfad, `manual_start_required` mit Startauftrag-Evidence oder den expliziten historischen Marker `legacy_reconstructed` mit Rekonstruktionsquelle und Datum.
6. `legacy_reconstructed` darf historische/pre-launcher Uebergaenge erklaeren, zaehlt aber nicht als automatischer Launch-/Queue-Erfolg.
7. Headless `codex exec`-Erfolg ist keine sichtbare Codex-App-Session. `status: launched` und `codex_app.visibility_status: verified_same_project` belegen bei `thread_source/source='exec'` nur eine nachvollziehbare CLI-Session im richtigen Workspace. Sie duerfen nicht als Beweis gelten, dass ein neuer Chat in der Codex-App-Seitenleiste sichtbar ist.
8. Wenn ein Workflow ausdruecklich eine sichtbare Codex-App-Session verlangt, muss Evidence eine eigene Sichtbarkeitsklasse oder gleichwertige Felder enthalten, die `headless_cli_session`, `queued_manual_start` und `visible_codex_app_session` unterscheiden. Sichtbarer Erfolg braucht eine echte App-/App-Server-/UI- oder manuell bestaetigte Thread-Referenz; Queue- und Headless-Erfolg bleiben nur traceable, nicht sichtbar.
9. Der lokal nachgewiesene technische Pfad fuer maschinell erzeugte sichtbare/interactive-source Codex-Sessions ist `codex app-server`: `thread/start`, `thread/name/set`, `turn/start`, danach `thread/list` mit derselben Thread-ID, `source: "vscode"`, passendem `cwd`, Titel und Rollout-Pfad. Ein leerer `thread/start` ohne Turn reicht nicht als sichtbarer Session-Erfolg.
10. Sichtbare Agent-Delivery-Sessions muessen im initiierenden Codex-Projekt geoeffnet werden: `thread/start.cwd` und beobachtetes `cwd` entsprechen dem `cwd` der Parent-/aktuellen Codex-Session, sofern kein expliziter anderer Projektkontext gewaehlt wurde. Der Titel folgt `{ParentSpecAbbrevAndNumber}: {Hardening|Implementation} - {ChildSpecDesignation}`, z. B. `DWT-1: Implementation - S3 Content Bundle`. Der Prefix stammt aus der Parent-Spec; eine Child-ID wie `DWT-S3` darf die Parent-Spec-Nummer nicht ersetzen.
11. `spec-closeout` archiviert alle sichtbaren Codex-App-Sessions, die fuer die jeweilige Child-Spec-Bearbeitung geoeffnet wurden, bevor Child-Closeout `READY` melden darf. Der closeout-nahe Nachweis laeuft ueber `ArchiveVisibleCodexAppSession.cs`: fixture/summary validation bleibt der Standard, live `thread/archive` ist explizit opt-in. Headless- und Queue-Evidence erhalten stattdessen explizite Archivstatus wie `not_app_visible_not_archived` oder `no_thread_created`; `manual_visible_missing_thread`, `archive_failed`, `proof_failed` und unarchivierte sichtbare Threads blockieren `READY`, sofern keine explizite `retained_session_accepted`-Notiz mit Akzeptanzperson und Grund vorliegt.

## Mini-Retro Template (kurz)

Eine Mini-Retro ist ein leichtgewichtiges Kontrollritual gegen Kontextverlust und Rework. Sie ersetzt keine vollstaendige `retro-plan`-Analyse, sondern haelt den aktuellen Stand fest, bevor ein groesserer Arbeitsblock endet oder der naechste Schritt startet.

```md
## Mini-Retro

- Was wurde entschieden?
- Was wurde geaendert?
- Was bleibt offen?
- Welche Evidenz/Verification fehlt?
- Welche Skill-/Workflow-Reibung ist aufgefallen?
- Session-/Kontextzustand: weiterarbeiten oder neue Session starten?
```

Regeln:
1. Eine Mini-Retro entsteht nach groesseren Spec-, Review-, Hardening-, Delivery- oder Closeout-Schritten, wenn sonst relevanter Kontext verloren gehen koennte.
2. Eine Mini-Retro entsteht vor Session-Ende, Kontextkomprimierung, laengerem Pausieren, Handoff an einen anderen Skill oder Start des naechsten groesseren Workflow-Schritts.
3. Sie bleibt kurz: Stichpunkte reichen, keine Ursachenanalyse erzwingen, keine neue Methodik starten.
4. Offene Entscheidungen, fehlende Evidenz, Workflow-Reibung und Kontextqualitaet muessen sichtbar bleiben, damit sie im naechsten Schritt nicht neu entdeckt werden.
5. Wenn die Mini-Retro echte Planungsfehler, wiederkehrende Rework-Muster oder Skill-Luecken zeigt, kann daraus eine vollstaendige `retro-plan`-Retro oder ein `improve-skills`-Kandidat werden.

## Agent Delivery Meta-Review

Ein Agent Delivery Meta-Review ist das lernende Kontrollritual fuer Parent/Child-Arbeit. Es rekonstruiert nicht die Produktimplementierung, sondern bewertet, ob der Workflow selbst waehrend Orchestration, Hardening, Delivery, Closeout und Handoff funktioniert hat.

Trigger:
1. Nach Abschluss oder Abbruch eines Parent/Child-Arbeitsblocks, wenn mehrere Child-Sessions beteiligt waren.
2. Nach einem Child-Closeout, wenn Rework, stale Handoffs, command-contract repairs, Kontextverlust oder unklare Next Actions sichtbar wurden.
3. Vor dem Start eines groesseren Folge-Childs, wenn der bisherige Parent/Child-Ablauf als Lernsignal genutzt werden soll.
4. Wenn der User nach Workflow-Selbstoptimierung, Prozessreview, "was lernen wir daraus" oder aehnlichen Meta-Fragen fragt.

Vorgehen:
1. Fuehrende Parent Spec, Child Index, Child Specs, Handoffs, OpenSpec-Artefakte, Evidence und Session-Logs identifizieren.
2. Den tatsaechlichen Ablauf rekonstruieren: Parent/Scope -> Orchestrator -> Hardening -> Delivery -> Closeout -> naechstes Handoff.
3. Findings-first bewerten, mit Prioritaet `P0` bis `P3` und konkreten Artefakt-/Dateireferenzen.
4. Verbesserungsvorschlaege trennen in `sofort patchbar`, `braucht Entscheidung`, `spaeterer Testsuite-Ausbau` und `Automatisierung/Validator`.
5. Kleine, evidence-backed Workflow-/Skill-/Template-Haertungen duerfen direkt umgesetzt werden, wenn der User das Review als Optimierungsauftrag formuliert hat. Breite Refactors, Runtime-Implementierung und Original-Produkt-Spec-Aenderungen bleiben ausserhalb des Meta-Reviews.

Persistierter Skill:
- Nutze `agent-delivery-retro-review`, wenn ein Parent/Child-Prozess selbst reviewed und in Workflow-Verbesserungen rueckgekoppelt werden soll.

## Unterstützte Workflows

Beide Workflows sind offiziell unterstützt. Workflow 2 ist der aktuelle Default, Workflow 1 bleibt kompatibel nutzbar.

Status in den Diagrammen meint den Spec-Header-Status (`🟡 Spec`, `🟠 Plan`, `🔵 Implemented`, `🟢 Accepted`). Readiness-Verdicts wie `needs_hardening`, `ready_candidate`, `IMPLEMENTATION READY` oder `READY WITH NON-BLOCKING NOTES` sind Gate-/Kontrollflaechenwerte und ersetzen den Header-Status nicht.

## Spec Sizing Gate (vor Workflow-Auswahl)

Vor groesseren Spec-, Plan- oder Delivery-Schritten wird geprueft, ob die Arbeit in einer robusten Session als normaler Scope bearbeitbar ist oder wegen Kontextdruck in Parent/Child Specs geschnitten werden muss.

Eine Spec gilt als "zu gross", wenn mehrere dieser Signale zusammenkommen:

1. Mehrere Capability-Domains muessen in einem Change verstanden und umgesetzt werden.
2. Mehrere Repos, Systeme, Runtime-Umgebungen oder externe Abhaengigkeiten sind beteiligt.
3. Mehrere getrennte Verification-Zyklen waeren noetig, bevor ein belastbares Done-Signal entsteht.
4. Der Scope zerfaellt natuerlich in mehrere Delivery Slices mit eigenen Done-Signalen.
5. Es sind mehrere offene Produkt-, Architektur-, Security-, Daten- oder Betriebsentscheidungen zu erwarten.
6. Die Arbeit ist so langlaufend, dass Kontextkomprimierung oder Session-Wechsel die Ergebnisqualitaet sichtbar gefaehrden wuerden.

Routing-Regel:

1. Wenn das Sizing Gate nicht feuert, bleibt die Spec eine normale Spec. Es wird keine Parent-/Child-Struktur erzeugt.
2. Wenn das Sizing Gate feuert, wird Parent/Child automatisch angelegt: Parent Spec als Kontrollschicht, Child Specs oder Child-Skeletons als Delivery-Slices, Child-Index/Coverage/Hardening Queue als Steuerflaeche.
3. Nach automatischem Parent/Child-Schnitt startet der Workflow mit `spec-orchestrator` und anschliessendem `child-spec-hardening` fuer die naechsten umsetzbaren Child Specs.
4. Zielbild fuer grosse Vorhaben: Jeder implementation-ready Child ist so vollstaendig, dass eine neue Session nur mit Parent-Verweis, Child Spec, Handoff/Mini-Retro und relevanter Evidence starten kann.

```mermaid
stateDiagram-v2
    [*] --> SizingGate: neuer oder groesserer Scope

    state "Spec Sizing Gate" as SizingGate
    state "Normale Spec" as NormalSpec
    state "Parent/Child-Schnitt" as ParentChild
    state "Workflow 2 Default" as Workflow2Default
    state "Workflow 1 Legacy" as Workflow1Legacy
    state "spec-orchestrator" as Orchestrator
    state "Parallel Work Gate" as ParallelGate
    state "child-spec-hardening" as Hardening

    SizingGate --> NormalSpec: Gate feuert nicht
    SizingGate --> ParentChild: Gate feuert
    NormalSpec --> Workflow2Default: neue Delivery
    NormalSpec --> Workflow1Legacy: laufender Legacy-Thread
    ParentChild --> Orchestrator: Child-Schnitt und Queue
    Orchestrator --> ParallelGate: Dependencies und Write-Sets pruefen
    ParallelGate --> Hardening: parallel oder serialisiert haerten
```

### Workflow 1 (Legacy-kompatibel)

```mermaid
stateDiagram-v2
    [*] --> Spec

    state "Spec (🟡 Spec)" as Spec
    state "refine-plan" as RefinePlan
    state "Plan (🟠 Plan)" as Plan
    state "Direct-mode Implementation" as DirectImplementation
    state "Implemented (🔵 Implemented)" as Implemented
    state "retro-plan optional" as Retro
    state "spec-closeout optional" as Closeout
    state "Accepted (🟢 Accepted)" as Accepted

    Spec --> RefinePlan: Plan iterativ schaerfen
    RefinePlan --> Plan: umsetzbarer Plan liegt vor
    Plan --> DirectImplementation: DoR erfuellt
    DirectImplementation --> Implemented: Umsetzung + Evidenz
    Implemented --> Retro: optionales Lernen
    Implemented --> Closeout: formaler Abschluss
    Retro --> Closeout: falls Abschluss noetig
    Closeout --> Accepted: Verification synchron
```

### Workflow 2 (Current)

```mermaid
stateDiagram-v2
    [*] --> Spec

    state "Spec (🟡 Spec)" as Spec
    state "spec-change-delivery" as Delivery
    state "Scope Contract (🟠 Plan)" as Plan
    state "Implementierung + Verifikation" as Implementation
    state "Implemented (🔵 Implemented)" as Implemented
    state "retro-plan optional" as Retro
    state "spec-closeout optional" as Closeout
    state "Accepted (🟢 Accepted)" as Accepted

    Spec --> Delivery: direct oder OpenSpec
    Delivery --> Plan: Scope Contract fixiert
    Plan --> Implementation: DoR erfuellt
    Implementation --> Implemented: Tests + Evidence gruen
    Implemented --> Retro: optionales Lernen
    Implemented --> Closeout: formaler Abschluss
    Retro --> Closeout: falls Abschluss noetig
    Closeout --> Accepted: Verification/Archive synchron
```

### Large Spec / Child Spec Pipeline

For Parent-/Master-Specs that trigger the Spec Sizing Gate:

```mermaid
stateDiagram-v2
    [*] --> ParentSpec

    state "Parent Spec (🟡 Spec)" as ParentSpec
    state "spec-orchestrator" as Orchestrator
    state "Child-Schnitt + Coverage" as ChildCut
    state "Hardening Queue (needs_hardening / ready_candidate / blocked)" as Queue
    state "Parallel Work Gate" as ParallelGate
    state "child-spec-hardening (Batch/Lanes)" as ParallelHardening
    state "child-spec-hardening (einzelner Child)" as Hardening
    state "doc-review-autoresolve" as Review
    state "Child Spec (🟡 Spec, IMPLEMENTATION READY)" as ReadyChild
    state "Child Spec (🟡 Spec, READY WITH NON-BLOCKING NOTES)" as ReadyWithNotes
    state "User Decision / Blocker" as Blocked
    state "spec-change-delivery" as Delivery
    state "Child Plan (🟠 Plan)" as ChildPlan
    state "Child Implemented (🔵 Implemented)" as ChildImplemented
    state "Child Closeout / Sync" as ChildCloseout
    state "Child Accepted (🟢 Accepted)" as ChildAccepted
    state "Naechster Child oder Parent-Closeout" as NextStep

    ParentSpec --> Orchestrator: Sizing Gate feuert
    Orchestrator --> ChildCut: Slices, Coverage, Ledger
    ChildCut --> Queue: nicht implementation-ready
    Queue --> ParallelGate: Dependencies und Write-Sets pruefen
    ParallelGate --> ParallelHardening: getrennte Spec/Doc-Write-Sets + klare Dependencies
    ParallelGate --> Hardening: Konflikt, Unklarheit oder zyklische Dependencies
    ParallelHardening --> Review: Lane-Ergebnisse integrieren
    Hardening --> Review: autonome Konsistenzpruefung
    Review --> ReadyChild: Verdict gruen
    Review --> ReadyWithNotes: non-blocking Notes akzeptiert
    Review --> Hardening: NEEDS HARDENING
    Review --> Blocked: NEEDS USER DECISION / blocked
    Blocked --> Queue: Entscheidung oder Blocker geloest
    ReadyChild --> Delivery: Handoff + DoR erfuellt
    ReadyWithNotes --> Delivery: bewusst akzeptierte Notes + Handoff
    Delivery --> ChildPlan: Scope Contract fixiert
    ChildPlan --> ChildImplemented: Umsetzung + Verification
    ChildImplemented --> ChildCloseout: Evidence und Index synchronisieren
    ChildCloseout --> ChildAccepted: formaler Closeout erfolgreich
    ChildCloseout --> NextStep: Sync-only oder weiteres Slice
    ChildAccepted --> NextStep: weiteres Slice oder Parent-Closeout
```

`spec-orchestrator` and `child-spec-hardening` normally keep specs in `🟡 Spec`; `spec-change-delivery` owns the transition to `🟠 Plan` once the implementation scope contract is locked.

## Workflow Selection (ohne Zwangsumstellung)

1. Wenn der User explizit Workflow 1 oder Workflow 2 nennt, diesem Pfad folgen.
2. Wenn ein bestehendes Artefakt bereits klar einen Pfad nutzt, auf demselben Pfad bleiben.
3. Ohne klare Vorgabe:
   - zuerst das Spec Sizing Gate anwenden,
   - bei zu grossem Scope automatisch Parent/Child nutzen,
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

## Review Control Surface (verpflichtend fuer Specs)

Jede Spec, Parent Spec und Child Spec muss direkt nach Header/Einleitung eine kurze Kontrollflaeche haben, die ein schnelles Review ermoeglicht. Sie ersetzt keine Detailsektionen, sondern spiegelt deren wichtigste Aussagen.

```md
## Review Control Surface

- Spec-Variante:
- Goldstandard Status:
- Ziel:
- In Scope:
- Out of Scope:
- Wichtigste Test-/Harness-Cases:
- Wichtigste Verification Commands:
- Offene Entscheidungen:
- Readiness Status:
```

Regeln:
1. `Spec-Variante` verwendet eine der Varianten aus `docs/spec-goldstandard.md`, z. B. `Parent/Master Spec`, `implementation-ready Child Spec`, `contract-heavy Spec`, `vertical spike Spec` oder `output/report/data-artifact Spec`.
2. `Goldstandard Status` beschreibt die Referenzklassifizierung der Spec und ist getrennt vom Workflow-`Status` im Header. Erlaubte Werte sind `none`, `candidate` und `reference`. Fuer normale Specs ist `none` ausreichend; Referenz-Specs muessen `candidate` oder `reference` sichtbar tragen.
3. `Ziel` beschreibt die konkrete Verhaltens- oder Dokumentationsaenderung, nicht nur den Projektnamen.
4. `In Scope` und `Out of Scope` muessen die Delivery-Grenze ohne Detaillekture verstaendlich machen.
5. Test-/Harness-Cases und Verification Commands listen die wichtigsten Proof Points, inklusive Negativ-, Fehler- oder Secret-/Redaction-Cases, wenn relevant.
6. `Offene Entscheidungen` nennt blockierende `[MISSING ...]`, `[DECISION ...]` oder blockierende `[REVIEW ...]` Marker; wenn keine offen sind, explizit `Keine blockierenden Entscheidungen`.
7. `Readiness Status` verwendet das passende Skill-Verdict, z. B. `NOT READY`, `READY FOR ORCHESTRATION`, `READY FOR PLANNING`, `IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, `NEEDS USER DECISION`, `NEEDS PARENT/ORCHESTRATOR SYNC` oder `NEEDS HARDENING`.
8. Wenn Detailsektionen geaendert werden, muss die Kontrollflaeche mitgezogen werden. Widerspruch zwischen Kontrollflaeche und Detailvertrag ist ein blockierendes Review-Finding.

Legacy-Regel:
- Bereits akzeptierte Legacy-Specs werden nicht nachtraeglich an der Review Control Surface oder am Goldstandard gemessen. Sie bleiben als umgesetzte Historie unveraendert. Goldstandard-Regeln gelten fuer neue Specs, aktive Kandidaten und Specs, die explizit fuer eine Referenz-Erhebung geoeffnet werden.

## Parallel Work Control Surface (bei paralleler Arbeit verpflichtend)

Parallel Work hat zwei unterschiedliche Modi:

1. **Parallel Spec/Doc Hardening**: mehrere Child Specs oder Plan-/Doc-Arbeitsbloecke werden parallel bis zur Umsetzungsreife geschaerft.
2. **Parallel Implementation**: mehrere umsetzungsreife Specs werden parallel in Runtime-/Produktcode umgesetzt.

Parallel Spec/Doc Hardening ist normalerweise unproblematisch parallelisierbar, sobald Dependencies und Schreibdateien klar sind. Parallel Implementation ist strenger und darf nur starten, wenn zusaetzlich die Runtime-/Code-Write-Sets disjunkt sind, Contracts stabil sind und die Integration seriell gesteuert wird.

In beiden Modi darf Parallel Work erst starten, wenn ein Parent-/Child-Schnitt oder Arbeitsblock-Schnitt existiert und die betroffenen Lanes explizit getrennte Write-Sets, Shared-File-Regeln, Verification Commands und eine Merge-/Sync-Reihenfolge haben.

Praktisch heisst das: Nach `spec-orchestrator` wird Parallel Work aktiv als naheliegender Modus geprueft. Wenn die Lane-Gates erfuellt sind, laeuft Child-Spec-/Doc-Hardening parallel als Batch oder mehrere Lanes; wenn nicht, wird serialisiert.

```mermaid
stateDiagram-v2
    [*] --> CandidateLanes

    state "Child-Schnitt / Hardening Queue" as CandidateLanes
    state "Parallel Work Gate" as ParallelGate
    state "Parallel Spec/Doc Hardening" as ParallelSpecHardening
    state "Implementation-ready Lanes" as ImplementationReadyLanes
    state "Parallel Implementation" as ParallelImplementation
    state "Serialisierter Modus" as SerialMode
    state "Integrations-Owner Sync" as IntegrationSync
    state "Mini-Retro / Handoff" as MiniRetro

    CandidateLanes --> ParallelGate: Dependencies, Write-Sets, Shared Files pruefen
    ParallelGate --> ParallelSpecHardening: Spec/Doc-Write-Sets getrennt
    ParallelGate --> ImplementationReadyLanes: implementation-ready + Runtime-Write-Sets disjunkt
    ParallelGate --> SerialMode: Konflikt, Unklarheit oder fehlender Integrations-Owner
    ImplementationReadyLanes --> ParallelImplementation: stabile Contracts + Gate Verification
    ParallelSpecHardening --> IntegrationSync: Cross-Lane-Review
    ParallelImplementation --> IntegrationSync: Merge + Verification-Replay
    SerialMode --> IntegrationSync: serieller Fortschritt
    IntegrationSync --> MiniRetro: offene Konflikte und Evidence sichtbar halten
    MiniRetro --> [*]
```

Minimale Kontrollflaeche:

| Child/Arbeitsblock | Modus | Owner/Agent | Erlaubte Write-Sets | Shared Files / Read-only Files | Abhaengigkeiten | Verification Commands | Integrations-Owner | Merge-/Sync-Reihenfolge |
|---|---|---|---|---|---|---|---|---|

Regeln:
1. Parallel Spec/Doc Hardening ist erlaubt, wenn jede Lane ihr eigenes Child-/Doc-/Plan-Artefakt schreibt, Dependencies sichtbar sind und Parent Spec, Child-Spec-Index, Slice-Plan, Backlog und gemeinsame Contracts fuer die Lane read-only bleiben.
2. Parallel Implementation ist nur erlaubt, wenn die betroffenen Specs implementation-ready sind, die erlaubten Runtime-/Code-Write-Sets disjunkt sind und jede editierende Lane in einem isolierten Branch/Worktree/OpenSpec Change oder in eindeutig getrennten Dateien arbeitet.
3. Shared Files sind fuer einzelne Lanes read-only, ausser die Lane ist ausdruecklich als Integrations-Owner fuer genau diese Datei benannt.
4. Parent Spec, Child-Spec-Index, Slice-Plan, Backlog, gemeinsame Contracts, gemeinsame Helpers und gemeinsame Verification-Skripte brauchen genau einen Integrations-Owner.
5. Contract-, Schema-, Harness- oder Shared-Helper-Aenderungen, die mehrere Lanes betreffen, duerfen in einzelnen Child Specs vorbereitet werden; ihre Uebernahme in Shared Files oder Runtime-Code ist ein serialer Integrations-/Prerequisite-Schritt.
6. Jede Lane braucht eigene Verification Commands. Bei Hardening koennen das Review-/Section-/Consistency-Checks sein; bei Implementation muessen es die gate-relevanten Runtime-/Test-Commands der Spec sein.
7. Der Integrations-Owner verantwortet Cross-Lane-Review, Parent-/Index-Sync, Merge-/Sync-Reihenfolge und gemeinsame Verification-Replay.
8. Parallel Work ist nicht erlaubt, wenn Write-Sets ueberlappen, Shared Files unklar sind, Abhaengigkeiten zyklisch/ungeklaert sind oder kein Integrations-Owner benannt ist. Fuer Parallel Implementation blockieren zusaetzlich instabile Contracts oder Verification, die erst nach Gesamtmerge sinnvoll pruefbar ist.
9. Mini-Retro/Handoff muss offene Lane-Konflikte, fehlende Verification und den Session-/Kontextzustand sichtbar halten, bevor weitere Lanes oder Integration starten.

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
- Review Control Surface mit Ziel, Scope, Non-Goals, wichtigsten Cases/Commands, offenen Entscheidungen und Readiness

### `rag-documentation-research`

Purpose: Quellenorientierte Dokumentationssuche vor Plan/Umsetzung mit `rag` als Standard und optionalem `qmd`-Discovery-Zusatz.

Lieferobjekt:
- priorisierte Quellenpfade fuer die aktuelle Frage
- nachvollziehbare Trefferbegruendung pro Quelle
- explizite Kennzeichnung, ob Treffer aus `rag`, `qmd` oder kombiniert stammen

Trigger (beispielhaft):
- "durchsuche die dokumentation"
- "durchsuche docs"
- "research the documentation"
- "search the documentation"
- "find relevant docs"
- "welche dokumente sind relevant"

Routing-Regel:
- Bei solchen Suchanfragen zuerst `rag-documentation-research`, danach mit den Quellen im jeweiligen Workflow (`doc-coauthoring`, `refine-plan`, `spec-change-delivery`, `spec-closeout`) fortfahren.

### `refine-plan`

Purpose: Aus Spec einen ausführbaren Plan machen.

Lieferobjekt:
- status-bearing actions (`[DONE]`, `[PENDING]`, `[BLOCKED]`)
- konkrete Verification Cases pro Teilbereich
- offene Spec-Lücken explizit als `[MISSING SPEC ...]`/`[DECISION SPEC ...]`
- primärer Plan-Track für Workflow 1 (iterativ)

### `spec-orchestrator`

Purpose: Große Parent-/Master-Specs schneller in Child-Delivery-Packs, Coverage-Kontrolle und Hardening Queue übersetzen.

Lieferobjekt:
- Parent-/Child-Inventar und Coverage-Matrix
- Review Control Surface fuer Parent/Child-Set oder fehlende Control-Surface-Patches
- Child-Readiness-Matrix mit fehlenden Delivery-Pack-/Hardening-Bestandteilen
- Parallel Work Control Surface mit Write-Sets, Shared-File-Regeln, Integrations-Owner und Merge-/Sync-Reihenfolge
- empfohlene nächste Slices plus Closeout-Sync-Checkliste
- Hardening Queue fuer Child Specs, die noch nicht implementation-ready sind

Routing-Regel:
- Nach `doc-coauthoring` nutzen, sobald ein Parent-Draft, eine Master-Spec, ein Slice-Plan oder Child Specs existieren und mehrere Slices orchestriert werden muessen.
- Vor `child-spec-hardening` nutzen, wenn mehrere Child Specs, ein großer Parent-Scope oder die Frage nach Parallelisierung/Nächstem Slice im Raum steht.
- Nicht als ersten Schritt fuer einen leeren Initialprompt nutzen; dafuer bleibt `doc-coauthoring` der Startpunkt.
- Nicht versuchen, alle Child Specs selbst bis zur vollen Vertragstiefe auszuarbeiten; dafuer `child-spec-hardening` nutzen.

### `child-spec-hardening`

Purpose: Aus Child-Spec-Drafts oder Orchestrator-Hardening-Queue-Eintraegen implementierungsreife Delivery Specs herstellen.

Lieferobjekt:
- aktualisierte Review Control Surface im Child
- Parent-/Master-Coverage und Parent-Scope-Conformance je Child
- Normative Contract mit Feldern, Statuswerten, Artefakten, Fehlerfaellen, Security-/Redaction-Regeln und Beispielen/Fixtures, soweit fuer den Child-Scope relevant
- konkrete Harness-/Verification-Cases mit Inputs, erwarteten Exit-/Statuswerten, Artefakten und Negativ-/Secret-Assertions
- Verification Commands im Stil akzeptierter Vorgaenger-Slices inklusive Execution Context, Preflight, Gate Verification, Runtime-Readiness und Anti-Loop-Regel
- Definition of Ready fuer Umsetzung und Definition of Done/Closeout Evidence
- Auto-Resolve-/Content-Quality-Review-Loop mit finalem Readiness Verdict

Routing-Regel:
- Nach `spec-orchestrator` nutzen, wenn ein Child `needs_hardening`, `ready_candidate` oder eine Hardening Queue hat.
- Direkt nutzen, wenn ein einzelner Child-Spec-Draft existiert und implementation-ready gemacht werden soll.
- Intern die Schreibprinzipien von `doc-coauthoring` und den Review-/Fix-Zyklus von `doc-review-autoresolve` anwenden.
- Stoppen, wenn echte Produkt-, Scope-, Architektur-, Security-, Legal- oder Data-Contract-Entscheidungen fehlen.
- Erst nach `IMPLEMENTATION READY` an `spec-change-delivery` uebergeben.

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
- RAG-basierte Quellensuche fuer relevante Doku-Updates (RAG-first, `qmd` optional)

### `doc-review-autoresolve`

Purpose: Review-Findings in Specs/Dokus autonom auflösen und direkt gegenprüfen, um Rework-Schleifen zu verkürzen.

Lieferobjekt:
- Findings-first Review mit file/line Referenzen
- automatische Behebung aller sicher entscheidbaren Inkonsistenzen im selben Run
- unmittelbarer Re-Review nach Edits (Loop bis stabil)
- Kontrolle, dass die Review Control Surface mit Detailsektionen, Findings und Readiness-Verdict konsistent ist
- strenger inhaltlicher Review des gesamten Vorhabens: Korrektheit, Scope, Vollstaendigkeit, Konsistenz, Eindeutigkeit, Machbarkeit, Testbarkeit, Traceability, Abstraktionsniveau, operative/lifecycle-relevante Punkte sowie Daten-/Artefaktvertraege
- automatischer Readiness-Status nach Spec-Änderungen (`IMPLEMENTATION READY`, `READY WITH NON-BLOCKING NOTES`, `NOT IMPLEMENTATION READY`)
- Eskalation nur für echte Entscheidungs-/Informationslücken (`[MISSING ...]`, `[DECISION ...]`, blockierende `[REVIEW ...]`)

Zusammenspiel mit `doc-coauthoring`:
- `doc-coauthoring` erstellt und ergänzt Inhalte, Anforderungen, Testfälle und Verification Commands.
- `doc-review-autoresolve` darf direkt danach laufen, um Inkonsistenzen, Drift, Dopplungen, fehlende Querverweise und sicher inferierbare Vertragslücken zu bereinigen.
- `doc-review-autoresolve` trifft keine neuen Produkt-/Scope-/Architektur-/Security-/Legal-/Data-Contract-Entscheidungen. Bei solchen Lücken stoppt der Loop mit Entscheidungsmarker.

### `retro-plan`

Purpose: Ergebnis gegen Plan prüfen und Deltas erfassen.

Lieferobjekt:
- Mini-Retro nach groesseren Arbeitsbloecken oder vor Kontextwechseln
- Root-Cause-Analyse
- Follow-up-Deltas für Spec/Plan/Umsetzung

### `improve-skills`

Purpose: wiederkehrende Reibungsmuster identifizieren und dauerhaft reduzieren.

Im Kontext dieses Workflows:
- wiederholte Nacharbeiten klassifizieren
- fehlende/unklare Entscheidungspunkte dokumentieren
- Workflow-/Skill-Anpassungen ableiten

## OpenSpec Nutzung

OpenSpec ist nach Scope-Modus geregelt:

1. **Normale Specs / kleine Changes**: OpenSpec ist optional und wird vom User entschieden. Ohne explizite OpenSpec-Vorgabe reicht direct Workflow 2.
2. **Parent-/Child-Vorhaben nach Spec Sizing Gate**: OpenSpec ist der Default-Ledger. Es wird nicht erneut beim User nachgefragt, ausser der User fordert direct mode explizit oder das Zielrepo hat keinen sinnvollen OpenSpec-Kontext.

OpenSpec ist besonders hilfreich bei:

1. größeren oder mehrstufigen Vorhaben,
2. mehreren beteiligten Teams/Repos,
3. Bedarf nach formalen Artefakten und Audit-Trace,
4. länger laufenden Changes mit Blockern und Teilfortschritt.

Für kleinere oder klar abgegrenzte Änderungen reicht oft der direkte Plan-Track ohne OpenSpec. Bei Parent-/Child-Vorhaben ersetzt OpenSpec nicht Parent/Child: OpenSpec haelt formale Change-/Audit-Artefakte, Parent/Child haelt Scope-Schnitt, Coverage, Hardening Queue und Session-Handoffs.

## One Delivery Ledger

Ein Delivery-Vorhaben braucht genau eine fuehrende Fortschritts- und Evidenzflaeche:

1. **Direct Workflow 2**: Spec + `spec-change-delivery` Scope Contract + Evidence sind fuehrend.
2. **OpenSpec Workflow 2**: OpenSpec Change-Artefakte sind der formale Delivery-Ledger; Spec/Parent/Child bleiben Scope- und Readiness-Quelle.
3. **Workflow 1**: `refine-plan`-Plan ist der fuehrende Plan-Ledger.

Kein Change soll denselben Fortschritt parallel in `refine-plan`, OpenSpec `tasks.md`, Child Index und Hardening Queue pflegen. Child Index und Hardening Queue duerfen Slices steuern, aber nicht die fein granularen OpenSpec-/Plan-Tasks duplizieren.

## Parent-/Child-Spec Orchestrierung

Wenn eine Spec wegen Scope-Druck in Child Specs aufgeteilt wird, muss die Parent Spec als Kontrollschicht erhalten bleiben. Child Specs duerfen den Scope nur schneiden, nicht verschwinden lassen.

### Child Index als operative Steuerzentrale

Der Child Index ist die operative Steuerzentrale eines Parent/Child-Vorhabens. Er ist nicht der Delivery-Ledger und nicht die fein granulare Taskliste. Er beantwortet: welche Child Specs existieren, welche Parent-Anforderungen sie abdecken, welcher Child als naechstes fuehrt, welche Hardening-/Delivery-/Closeout-Gates blockieren und wo Evidence oder Re-entry liegen.

Minimale Child-Index-Flaeche:

| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|

Regeln:
1. `spec-orchestrator` erzeugt oder aktualisiert den Child Index, sobald Parent/Child genutzt wird. Wenn kein eigener Index existiert, wird die Kontrollflaeche im Parent, Slice-Plan oder Delivery Orchestration Pack angelegt.
2. Die Spalte `Child` enthaelt einen stabilen maschinenlesbaren Child-ID wie `S3`, nicht einen gemischten Anzeigenamen wie `S3 Content Bundle`. Menschliche Titel stehen in `Child Spec`, `Parent Coverage` oder einer separaten Zusatzspalte.
3. Child-ID, Handoff-Dateiname, Handoff-Feld `Child`, Validator-/Delivery-Aufruf und OpenSpec-/Ledger-Verweise muessen dieselbe Child-ID verwenden; der konkrete Pfad steht im Handoff-Feld `Child Spec`. Abweichungen blockieren Implementierungsfreigabe, weil eine frische Session sonst den Ziel-Child nicht eindeutig findet.
4. Der Child Index haelt Slice-Status, Coverage, Abhaengigkeiten, Hardening Queue, Handoff-Pointer, Next Action, Evidence-/Closeout-Links und Backlog-/Re-entry-Verweise. Er dupliziert keine OpenSpec-Tasks und keine detaillierten Implementierungspläne.
5. Die Hardening Queue ist ein Ausschnitt des Child Index fuer nicht implementation-ready Children. Sie nennt Required Hardening, Sources To Read und Blockers, aber keine fein granularen Delivery-Tasks.
6. Ein Child darf nur als `IMPLEMENTATION READY` gelten, wenn die Child-Index-Tabelle die exakten Spaltennamen aus der Mindestflaeche oben enthaelt und die Ziel-Child-Zeile fuer jede Spalte vollstaendig ausgefuellt ist.
7. Zusammengelegte oder umbenannte Ersatzspalten wie `Dependencies / Evidence`, `Allowed Next Mode`, `Implementation Gate`, `Closeout Sync`, `Status`, `Verdict`, `Ledger`, `Gate` oder aehnliche Kurzformen gelten nicht als operational. Sie koennen zusaetzlich existieren, ersetzen aber keine Pflichtspalte.
8. Eine alte Kurzform wie `Slice | Spec | Status | Hardening Verdict | Session Handoff` ist nur ein Migrationszwischenstand und blockiert Implementierung.
9. `Allowed Write-Set` muss fuer `IMPLEMENTATION READY` als verbindliche, durch `spec-change-delivery` durchsetzbare Liste oder Musterliste formuliert sein. Unverbindliche Formulierungen wie `voraussichtlich`, `likely`, `probably`, `expected`, `TBD`, `to be decided`, `etc.`, `and related files` oder `as needed` blockieren Implementierungsfreigabe.
10. Ein Child darf nur als `IMPLEMENTATION READY` gelten, wenn ein dokumentiertes Hardening Verdict mit Parent Conformance, Content-Quality-Ergebnis, Verification Depth und DoR/DoD vorliegt und der Child Index auf ein aktuelles persistiertes Handoff zeigt.
11. `ready_candidate` bedeutet nur: der Schnitt wirkt plausibel. Es ist kein Implementierungsfreigabe-Status.
12. Nach Hardening, Delivery und Closeout muessen Child Spec, Parent Coverage, Child Index, Child Session Handoff, Backlog/Re-entry, Evidence Links und OpenSpec Status synchron sein.
13. Der Child Index benennt den naechsten fuehrenden Child erst, nachdem die vorherige Child-Synchronisation abgeschlossen oder explizit als blockiert dokumentiert ist.

Pflichtbestandteile:

1. Parent Spec oder Slice-Plan mit Coverage-Matrix: jede Parent-Anforderung ist `done`, `partial`, `pending`, `blocked` oder bewusst `out_of_scope`.
2. Child-Spec-Index mit Status, Parent Coverage, Hardening Verdict, Handoff-Pointer, Abhaengigkeiten, naechstem empfohlenem Slice und Links auf Evidence/Closeout/Re-entry.
3. Jede Child Spec enthaelt vor Umsetzung mindestens eine Review Control Surface, Scope, Non-Goals, Master-/Parent-Abdeckung, Parent-Scope-Conformance, Decision Freeze Pack, konkrete Acceptance Criteria und Verification Commands.
4. Restscope wird nicht nur als "Next Step" in einer abgeschlossenen Spec abgelegt, sondern als Backlog-/Child-Spec-Eintrag mit Trigger, Done-Signal und Abhaengigkeit.
5. Closeout einer Child Spec synchronisiert Parent Spec, Slice-Plan/Index, Backlog und OpenSpec-Artefakte, bevor der naechste Slice als fuehrend gilt.
6. Breiter Projekt-Dokumentations-Sync laeuft normalerweise beim Parent-Closeout. Child-Closeout triggert breiten Docs-Sync nur, wenn der Child selbst user-facing/project docs veraendert oder oeffentliche Contract-Dokumentation stale machen wuerde.

Parent-Scope-Conformance ist ein blockierendes Gate nach jeder Child-Spec-Nacharbeit:

1. Jede Parent-Anforderung, die der Child beruehrt, wird als `preserves`, `extends`, `narrows_with_rationale`, `defers_to_child`, `missing_from_child` oder `contradicts_parent` markiert.
2. `contradicts_parent` blockiert Implementierung.
3. `missing_from_child` blockiert Implementierung, wenn kein benannter Child-/Backlog-Reentry existiert.
4. Bewusste Scope-Verengung ist erlaubt, aber nur mit Rationale und Ziel fuer den Restscope.

Parallelisierung ist je nach Modus unterschiedlich zu bewerten: Child-Spec-/Doc-Hardening kann parallel laufen, sobald die jeweiligen Spec-/Doc-Write-Sets getrennt sind und Dependencies eingehalten werden; Runtime-Implementierung braucht zusaetzlich implementation-ready Specs, stabile Contracts und disjunkte Code-/Artefakt-Write-Sets.

Parallel-Lane-Regeln:

1. Vor Start eine Parallel Work Control Surface erstellen: Child/Arbeitsblock, Modus (`spec/doc hardening` oder `implementation`), Owner/Agent, erlaubte Write-Sets, Shared Files / Read-only Files, Abhaengigkeiten, Verification Commands, Integrations-Owner, Merge-/Sync-Reihenfolge.
2. Shared Control Files wie Parent Spec, Slice-Plan, Index, Backlog, gemeinsame Contracts, gemeinsame Helpers oder gemeinsame Verification-Skripte haben genau einen Integrations-Owner.
3. Parallel arbeitende Implementation-Lanes laufen in getrennten Branches/Worktrees oder klar getrennten OpenSpec Changes, wenn sie mehr als reine Read-only-Analyse leisten.
4. Kein paralleler Implementation-Change darf denselben zentralen Contract still veraendern; Contract-, Schema-, Harness- oder Shared-Helper-Aenderungen laufen zuerst als serialer Integrations-/Prerequisite-Schritt.
5. Nach Rueckkehr aller Lanes fuehrt der Integrations-Owner Merge, Cross-Slice-Review, Parent-Coverage-/Index-Update und die gemeinsame Verification-Replay in der festgelegten Reihenfolge aus.
6. Wenn Write-Sets, Shared Files, Dependencies, Verification Commands, Integrations-Owner oder Merge-/Sync-Reihenfolge nicht klar sind, wird serialisiert.

## Child-Spec-Hardening Pipeline

Die Zerlegung und die Tiefe sind getrennte Verantwortungen:

1. `doc-coauthoring` erstellt oder schaerft die Parent-Spec.
2. `spec-orchestrator` erzeugt Child-Schnitt, Coverage, Conformance, Dependencies, Parallel-Lanes und Hardening Queue.
3. `child-spec-hardening` arbeitet einzelne Child Specs oder Batches aus der Hardening Queue bis zur Implementierungsreife aus.
4. `doc-review-autoresolve` laeuft direkt im Anschluss oder innerhalb des Hardening-Schritts, um autonome Inkonsistenzen zu beheben und ein Readiness Verdict zu liefern.
5. `spec-change-delivery` implementiert genau einen Child, nachdem ein dokumentiertes Hardening Verdict `IMPLEMENTATION READY` oder bewusst akzeptierte `READY WITH NON-BLOCKING NOTES` meldet.

Hardening Queue Beispiel:

| Child | Status | Required Hardening | Inputs |
|---|---|---|---|
| S3 | needs_hardening | Normative Contract, Canonical Examples/Fixtures, Pflicht-Cases, Verification nach S1/S2-Muster | Parent V2-FR-031/031a/031b, accepted S1/S2 |
| S4 | ready_candidate | Content-Freshness-Vertrag, Guide-Cases, Rendering ohne LLM | Parent Provider-Guide-Anforderungen |
| S6 | blocked | Dependency-Blocker erhalten, keine Fake-Inputs akzeptieren | S2/S3/S5 Evidence |

`spec-orchestrator` darf einen Child als `ready_candidate` markieren, wenn der Schnitt plausibel ist. `IMPLEMENTATION READY` ist erst erlaubt, wenn `child-spec-hardening` ein dokumentiertes Hardening Verdict erzeugt oder eine bestehende Child Spec dieses Verdict mit derselben Gate-Tiefe bereits sichtbar enthaelt.

Child-Spec-Hardening-Pflichtgates:

1. Review Control Surface: Ziel, In/Out of Scope, wichtigste Cases/Commands, offene Entscheidungen und Readiness sind aktuell und widerspruchsfrei.
2. Status-Provenance: `done`, `accepted` oder `reference_done` nur mit Evidence/Closeout/Verification-Replay; sonst `parent_claims_done`.
3. Normative Contract: Felder, Statuswerte, Fehler-/Blockerpfade, Artefakte, Security/Redaction, Fallbacks und Beispiele/Fixtures soweit relevant.
4. Canonical Examples/Fixtures: contract-heavy Specs entscheiden explizit zwischen eingebetteten Beispielen, referenzierten Fixture-Dateien oder Hybrid; Pflichtpfade, normative Felder und Harness-Nachweis sind dokumentiert.
5. Harness-/Verification-Cases: positive, negative, fallback, blocked und secret/redaction cases mit erwarteten Exit-/Statuswerten und Artefakten.
6. Verification Commands: konkreter Execution Context, risk-based Preflight, Gate Verification, Runtime-Readiness, Success Criteria und Anti-Loop-Regel.
7. Content Quality Review: Korrektheit, Scope, Vollstaendigkeit, Konsistenz, Eindeutigkeit, Machbarkeit, Testbarkeit, Traceability, Abstraktionsniveau und Lifecycle-Fit.
8. DoR/DoD: Definition of Ready fuer Umsetzung und Definition of Done/Closeout Evidence sind vorhanden oder bewusst irrelevant.
9. Handoff: Bei `IMPLEMENTATION READY` oder `READY WITH NON-BLOCKING NOTES` existiert ein persistiertes Child Session Handoff mit Target Repository / Working Directory, naechstem Modus, Write-Set, Verification Commands, Evidence/OpenSpec und offenen Notes; der Child Index verlinkt genau dieses Handoff.
10. Hardening Verification: Vor `IMPLEMENTATION READY` oder `READY WITH NON-BLOCKING NOTES` muss `git diff --check` gruen sein. Wenn die Child Spec eingebettete maschinenlesbare Beispiele enthaelt, muessen die relevanten Beispiele geparst oder bewusst als nicht-parsebare Pseudobeispiele gekennzeichnet werden; parsefehlerhafte normative Beispiele blockieren Readiness.

Contract-heavy Beispielregel:
1. Eingebettete YAML-/JSON-/TOML-/Schema-/Manifest-Beispiele, die als kanonisch oder kopierbar beschrieben werden, muessen syntaktisch parsebar sein.
2. Wenn ein Beispiel bewusst gekuerzt oder nicht parsebar ist, muss es als `pseudo-*`, `sketch` oder `excerpt` markiert werden und darf nicht als kanonische Implementierungsquelle gelten.
3. Parse- oder Lint-Kommandos fuer die eingebetteten Beispiele gehoeren zur Hardening Verification, wenn Standardtools im Repo oder in der lokalen Umgebung verfuegbar sind.
4. Ein parsefehlerhaftes kanonisches Beispiel ist kein non-blocking Note; es ist mindestens `NEEDS HARDENING`.

Child-Hardening-Scope-Regel:
1. `child-spec-hardening` darf den Ziel-Child, den Child Index und das zugehoerige Child Session Handoff synchronisieren.
2. Parent Spec, Slice-Plan, akzeptierte Vorgaenger-Childs und OpenSpec-Archive sind im Child-Hardening read-only, ausser der User beauftragt explizit einen Integrations-/Closeout-Sync.
3. Wenn Hardening entdeckt, dass Vorgaengerstatus, Parent Coverage oder Slice-Plan stale sind, wird ein klarer Sync-Patch oder Folgeauftrag dokumentiert. Der Ziel-Child darf trotzdem nur dann `IMPLEMENTATION READY` werden, wenn der Child Index fuer diesen Child vollstaendig und widerspruchsfrei ist.
4. Akzeptierte Vorgaenger wie S1/S2 duerfen als Evidence-/Verification-Rezept genutzt werden; sie werden nicht pauschal migriert, archiviert oder in ihrem Status geaendert.

## Definition of Ready (vor Implementierung)

Implementierung startet erst, wenn alle Punkte erfüllt sind:

1. Scope in 1-2 Sätzen fixiert.
2. Non-Goals explizit dokumentiert.
3. Review Control Surface aktuell und konsistent mit Detailsektionen.
4. Decision Freeze Pack ausgefüllt (siehe unten).
5. Referenz-Baseline benannt (**falls relevant**).
6. Testfälle/Abnahmeszenarien vorab definiert, die den späteren DoD nachweisbar machen.
7. Verifikationskommandos vorab definiert:
   - Unit/Integration Tests
   - Runtime/Compose Start
   - Health/Smoke Checks
   - Plattform-/Shell-Contract der Kommandos (z. B. macOS vs Linux) ist explizit.
   - Readiness-Strategie für timing-sensitive Runtime-Checks ist explizit (Poll/Retry/Wait).
   - Scope-Guard-Baseline ist explizit (Branch-History vs Working-Tree) inklusive Verhalten auf long-lived branches.
   - Risk-based Verification Preflight ist definiert (nur High-Risk-Kommandos; getrennte Statuslogik).
   - High-Risk-Kommandos wurden als Command-Vertrag rehearsed, soweit das ohne Implementierung oder externe Seiteneffekte moeglich ist. Dazu gehoeren besonders SDK-/Runtime-Auswahl, absolute Pfade, Container-/Compose-Kommandos, Testhost-Flags wie `--no-build`/`--no-restore`, Branch-/Diff-Guards, Health-Polls, Credentials-/Secret-Guards und Befehle, die durch Parent-`global.json`, CWD oder Shell-Unterschiede beeinflusst werden koennen.
   - Anti-Loop-Regel ist definiert: kein rekursives "Verifikation der Verifikation".
   - Vereinfachungen/Anpassungen von Verification Commands sind als Vorschlagspfad mit User-Freigabe geregelt.
8. Offene Risiken, Abhängigkeiten und Blocker sind dokumentiert.
9. Bei Child Specs liegt ein dokumentiertes Hardening Verdict vor (`IMPLEMENTATION READY` oder bewusst akzeptierte `READY WITH NON-BLOCKING NOTES`). Implizite Reife ohne Verdict blockiert Implementierung.
10. Wenn parallele Implementation geplant ist, liegt die Parallel Work Control Surface mit expliziten Runtime-/Code-Write-Sets, Shared-File-Regeln, Integrations-Owner und Merge-/Sync-Reihenfolge vor.

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

### Verification Command Contract Repair

Wenn ein definierter Verification Command waehrend Delivery oder Closeout nicht wegen Produkt-/Implementierungsfehlern scheitert, sondern weil der Command-Vertrag selbst in der Zielumgebung fragil, stale oder falsch formuliert ist, darf der Fehler nicht still als bestanden ersetzt werden.

Regeln:
1. Der fehlgeschlagene Originalcommand wird als Command-Contract-Finding dokumentiert, inklusive Exit/Fehlerbild und Ursache, soweit erkennbar.
2. Ein Ersatzcommand darf nur als gate-relevant gelten, wenn Spec, Child Spec, Child Index/Handoff und OpenSpec/Evidence vorher auf den neuen Command synchronisiert wurden oder ein explizit dokumentierter Sync-Patch Teil desselben Integrations-/Closeout-Runs ist.
3. Nach der Sync-Aenderung muss der korrigierte Command frisch ausgefuehrt werden. Ein frueherer Rehearsal-Lauf ersetzt das nicht.
4. Wenn die Sync-Aenderung nicht im aktuellen Scope erlaubt ist oder eine echte Entscheidung braucht, bleibt das Ergebnis `NOT READY` und wird an `child-spec-hardening`, `spec-change-delivery` oder den Integrations-Owner zurueckgegeben.
5. Evidence muss Originalfehler und korrigierten Lauf unterscheiden. Der Originalfehler darf nicht als `ran/pass` umetikettiert werden.
6. Commands, die nur vor einem OpenSpec-Archive sinnvoll sind, werden als `Pre-Archive Closeout` markiert. Nach Archive ersetzt ein `Post-Archive / Current Replay` die aktive Change-Validierung durch Archive-Presence plus canonical spec validation.
7. Gemeinsame `.NET` file-based Validatoren werden aus einem neutralen CWD gestartet, damit kein Zielrepo-`global.json` oder Projekt-CWD den Lauf verfälscht, z. B. `(cd /tmp && dotnet run /absolute/path/to/ValidateChildReadiness.cs -- --index /absolute/index.md --child <id> --handoff /absolute/handoff.md)`.

### Risk-Based Command Contract Rehearsal

Vor `READY FOR PLANNING`, `IMPLEMENTATION READY` oder `READY WITH NON-BLOCKING NOTES` muessen riskante Verification Commands nicht nur beschrieben, sondern als Command-Vertrag geprueft werden, soweit das in der aktuellen Umgebung ohne Umsetzung oder externe Seiteneffekte sicher moeglich ist.

Regeln:
1. High-Risk-Kommandos sind alle Commands, deren Erfolg stark von SDK-/Runtime-Auswahl, absolutem Pfad, CWD, Shell, Container-Daemon, Compose/Service-Readiness, Testhost-Flags, Vorbuild-Artefakten, Branch-Historie, Credentials oder Netzwerk-/Infrastrukturverfuegbarkeit abhaengt.
2. Die Rehearsal prueft nur den Command-Vertrag: richtige Runtime/SDK-Auswahl, erreichbare Tools, gueltige Pfade, plausible Flags, erwartete Vorbedingungen und fehlende Seiteneffekte. Sie ist keine Ersatz-Verifikation fuer die spaetere Implementierung.
3. Wenn eine Rehearsal sicher nicht moeglich ist, muss die Spec das explizit markieren, inklusive Grund und wer/was den Command-Vertrag spaeter validiert.
4. Ein High-Risk-Command mit fehlender, fehlgeschlagener oder nicht erklaerter Rehearsal blockiert Implementation-Ready. Verwende `NEEDS HARDENING`, `[MISSING command contract rehearsal]` oder `[REVIEW command contract not rehearsed: <reason>]`.
5. Bei Parent/Child-Arbeit muss das Rehearsal-Ergebnis in Child Spec, Child Index/Handoff oder Evidence sichtbar sein, damit eine frische Session den Command nicht erneut blind vertraut.

## Anti-Rework Guardrails

1. Keine Umsetzung starten, solange zentrale Entscheidungen noch "im Fluss" sind.
2. Größere Vorhaben in mehrere Changes/Arbeitspakete splitten (z. B. nach Themenclustern oder Risiko).
3. Referenz-Implementierung/Baseline früh festlegen und diffen (**falls relevant**).
4. Jede Arbeitsphase endet mit:
   - Was wurde entschieden?
   - Was wurde geaendert?
   - Was bleibt offen?
   - Welche Evidenz fehlt noch?
   - Welche Skill-/Workflow-Reibung ist aufgefallen?
   - Session-/Kontextzustand: weiterarbeiten oder neue Session starten?
5. Keine "Hybrid-Steuerung": entweder OpenSpec ist als Ledger aktiv (Default bei Parent/Child) oder der Change laeuft bewusst ohne OpenSpec.
6. Review-Findings werden standardmäßig per `doc-review-autoresolve` erst **autonom behoben**, dann **erneut reviewed**; Rückfrage nur bei echten Entscheidungs-/Missing-Blockern.
7. Orchestrierung und Hardening nicht vermischen: `spec-orchestrator` schneidet und priorisiert; `child-spec-hardening` erzeugt die Vertragstiefe.
8. Keine parallele Umsetzung starten, solange Write-Sets, Shared Files, Integrations-Owner und Merge-/Verification-Reihenfolge nur implizit sind.

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
4. Inhaltlichen Review ausführen: nicht nur Abschnitts-/DoR-Check, sondern strenge fachliche Prüfung des gesamten Vorhabens.
5. Nach jeder Spec-Änderung automatisch Readiness-Status melden; der User soll nicht separat fragen müssen, ob die Spec implementation-ready ist.
6. Wiederholen, bis keine autonomen Findings mehr offen sind.

Findings muessen fuer den tatsaechlichen Review-Stil des Users formuliert sein. Der User liest typischerweise zuerst Ziel, In Scope, Out of Scope, Verification Commands und Test-/Harness-Cases; er hat den mittleren Vertrags-/Detailteil oft nur ueberflogen. Deshalb muss jedes nicht-triviale Finding auch ohne vollstaendige Detaillekture verstaendlich sein.

Finding-Format fuer nicht-triviale Punkte:

1. Kurzbefund in Alltagssprache.
2. Warum das wichtig ist: welcher Implementierungs-/Review-Fehler sonst passieren kann.
3. Wo der User es pruefen soll: Ziel/Scope/Verification/Test-Cases nennen, nicht nur die tiefe Vertragsstelle.
4. Konkretes Beispiel: fehlendes Artefakt, Statuswert, Fixture, Kommando, Testfall oder Verhalten.
5. Noetige Aktion: autonomer Fix oder konkrete User-Entscheidung.

Terse technische Labels reichen nicht. Statt "Canonical Examples/Fixtures decision missing" erklaeren: "Diese Spec definiert ein Manifest. Damit der Implementierer nicht raet, braucht es entweder ein kleines Beispiel in der Spec oder benannte Fixture-Dateien, die die Harness spaeter ausfuehrt."

Inhaltliche Review-Fragen orientieren sich an etablierten Requirements-Qualitaetskriterien:

- Ist das beschriebene Verhalten fachlich korrekt fuer Problem, Nutzer und Kontext?
- Ist jede Anforderung notwendig und im Scope, oder versteckt sie Scope Creep bzw. ein Non-Goal?
- Sind Normalpfad, Edge Cases, Fehlerpfade, Abhaengigkeiten, Constraints und Annahmen ausreichend vollstaendig?
- Sind Anforderungen, Beispiele, Begriffe, Statuswerte, Parent-/Child-Scope, Akzeptanzkriterien und Verification Commands konsistent?
- Ist die Aussage eindeutig genug, dass keine materiell unterschiedlichen Implementierungen plausibel sind?
- Ist die Anforderung in der Zielumgebung machbar?
- Ist sie testbar/verifizierbar durch Test, Inspection, Analyse, Demonstration oder konkrete Abnahme-Evidenz?
- Ist sie traceable zu Intent, Parent Scope, Akzeptanzkriterien, Verification Commands und nachgelagerten Artefakten?
- Ist sie atomar und auf dem richtigen Abstraktionsniveau?
- Sind operative/lifecycle-relevante Themen wie Migration, Fallback, Rollback, Observability, Kompatibilitaet, Ownership und Closeout-Evidenz abgedeckt, falls relevant?

Inhaltliche P1-Beispiele:

- Datenartefakte ohne die fuer den eigenen nachgelagerten Flow notwendige Identitaet, Provenance oder Kontextbindung.
- Hash-/Signaturvertrag ohne kanonische Serialisierung.
- Manifest oder Run-Status ohne erlaubte Werte, Fehlerstatus oder Provenance.
- Akzeptanzkriterium kann formal grün werden, obwohl der intendierte Kontrollfluss übersprungen wurde.
- Anforderung ist mehrdeutig, fachlich widerspruechlich, technisch unmachbar oder nicht testbar.
- Wichtiger Fehler-/Edge-Case fehlt, obwohl die Implementierung ohne ihn nicht sicher oder sinnvoll abgeschlossen werden kann.

Use-Case-spezifische Beispiele sind keine globalen Pflichtfelder. Ein Survey braucht z. B. nur dann Frage-IDs im Antwortvertrag, wenn die Spec spaetere Interpretation nach Frage vorsieht.

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

Bei Parent/Child-Handoffs zusaetzlich erfassen, wenn verfuegbar:
- echte Codex-Session-ID oder semantische Session-ID,
- Session-Log-Pfad (`.codex/sessions/**` oder `.codex/archived_sessions/**`),
- fuehrender Skill des Runs,
- Input-Handoff und Output-/Evidence-Pfade.

Wenn die echte Session-ID noch nicht bekannt oder nicht persistiert ist, wird die Luecke explizit als `Session log not yet persisted` markiert statt durch eine scheinbar echte ID ersetzt.

Hinweis:
- Diese History-Regel gilt für **Spec-Dateien**.
- Iterative History in **Plan-Dateien** (z. B. `refine-plan`) bleibt davon unberührt.

## File Conventions

| Typ | Ort | Muster |
|-----|-----|--------|
| Spezifikation (ohne OpenSpec) | `_specs/` | `YYYY-MM-DD <Titel>.md` |
| Plan | neben Spec oder Projektordner | `<name>-plan.md` |
| OpenSpec Change (optional) | `openspec/changes/<change>/` | Standard-Artefakte |
| Child Session Handoff | `child-session-handoffs/` neben Child Index | `<child-id>-session-handoff.md` |
| Retro/Mini-Retro | inline im Plan/Spec/Handoff oder eigene Datei | `<name>-retro.md` |

## Übergänge

### Spec -> Plan
Workflow 1: `refine-plan` iterativ; bei implementierungsreifem Plan Status `🟠 Plan`.
Workflow 2: `spec-change-delivery` setzt Status `🟠 Plan`, sobald der Scope Contract fixiert ist.

### Plan -> Umsetzung
Nur bei erfüllter Definition of Ready. Nach ausgeführter Umsetzung mit Artefakten: Status `🔵 Implemented`.

### Umsetzung -> Accepted
In beiden Workflows optional über `spec-closeout`: Status `🟢 Accepted`, wenn Verifikation vollständig grün ist und (falls aktiv) OpenSpec archiviert wurde. Bei Parent/Child-Vorhaben unterscheidet Closeout zwischen Child-Sync (Parent Coverage, Index, Backlog, OpenSpec/Evidence) und Parent-Closeout (breiter Projekt-Dokumentations-Sync).

### Arbeitsblock -> Mini-Retro / Retro
Mini-Retro nach signifikanten Spec-, Review-, Delivery- oder Closeout-Bloecken sowie vor Session-Ende, Kontextwechsel oder Skill-Handoff. "retro the plan" nach signifikanten Meilensteinen, wenn Ursachenanalyse oder Planverbesserung noetig ist; "final retro the plan" vor Abschluss.

### Review Findings -> Auto-Resolve
Bei Findings aus Review-Runden zuerst `doc-review-autoresolve` ausführen (fix + re-review loop). Erst verbleibende Entscheidungs- oder Missing-Blocker an den User eskalieren.

### Retro -> Improve Skills
Wiederkehrende Probleme als `improve-skills`-Kandidaten erfassen und in Workflow/Skills einarbeiten.

## Lightweight Checkliste vor Umsetzung

1. Sind Modus/Skill und Source of Truth klar?
2. Sind Ziel, Nicht-Ziele, In Scope und erwarteter Output klar?
3. Ist die Review Control Surface aktuell?
4. Ist der Scope klar abgegrenzt?
5. Sind Entscheidungen eingefroren (Decision Freeze Pack)?
6. Sind Test- und Runtime-Gates vorab definiert?
7. Ist eine Referenz-Baseline nötig und benannt (falls relevant)?
8. Sind externe Abhängigkeiten/Owner dokumentiert?
9. Falls parallel gearbeitet wird: sind Write-Sets, Shared Files, Integrations-Owner und Merge-/Sync-Reihenfolge explizit?
10. Ist klar, was "done" konkret bedeutet?
