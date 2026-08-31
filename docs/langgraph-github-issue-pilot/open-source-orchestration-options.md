# Open-Source-Optionen für den GitHub-Issue-Piloten

Stand: 26. August 2026

## Ergebnis in Kürze

Es gibt noch keinen reifen Open-Source-Drop-in-Ersatz, der genau den heutigen Vertrag des Piloten abdeckt: isolierte Implementierung, deterministische Tests, drei unabhängige Reviews auf derselben Head-SHA, begrenzte Repair-Runden, persistente Recovery und menschliche Entscheidungen über GitHub.

Die sinnvollste Vereinfachung ist deshalb nicht der Austausch von LangGraph gegen ein anderes Agenten-Framework. Sie ist die Zerlegung in **frische, ereignisgetriebene Läufe**, die über GitHub-Artefakte kommunizieren:

1. [`github/gh-aw`](https://github.com/github/gh-aw) übernimmt Trigger, isolierte Agentenläufe, Berechtigungsgrenzen und kontrollierte GitHub-Schreiboperationen.
2. Normale GitHub Actions führen Tests und den Review-Aggregator deterministisch aus.
3. Issue, Pull Request, Commit-SHA, Checks, Review-Findings und menschliche Kommentare bilden den dauerhaften Arbeitsstand.
4. Bei `needs_human` endet der Agentenlauf. Die Antwort erzeugt ein neues GitHub-Ereignis und damit einen neuen Lauf; es wird keine alte Agentenkonversation fortgesetzt.

Als lokaler Gegenentwurf ist [`apokamo/kaji`](https://github.com/apokamo/kaji) der fachlich engste Treffer. Sein Workflow ist bereits als Design → Implementierung → Review → Fix → Verify → PR mit strukturierten Verdict-Artefakten und begrenzten Schleifen modelliert. Das Projekt ist aber jung und kaum verbreitet. Es eignet sich für einen Spike, noch nicht für eine ungeprüfte Ablösung des Piloten.

Wenn nach einem `gh-aw`-Spike tatsächlich eine eigene lokale Durable-Control-Plane nötig bleibt, ist [`dbos-inc/dbos-transact-py`](https://github.com/dbos-inc/dbos-transact-py) die kleinste ernsthafte technische Alternative. Temporal wäre robuster, aber kaum eine Vereinfachung.

## Bewertungsmaßstab

Ein Kandidat passt umso besser, je mehr der folgenden Eigenschaften er bereitstellt, ohne wieder eine langlebige Multi-Agent-Konversation zum eigentlichen Zustand zu machen:

- ein frischer, begrenzter Kontext pro Tätigkeit;
- genau ein schreibender Implementer und nur lesende Reviewer;
- deterministische Tests außerhalb des LLM-Loops;
- Übergaben als versionierte JSON/YAML-Dateien, Commits, Checks und Findings;
- Bindung jeder Prüfung an eine konkrete Head-SHA;
- persistenter Zustand und idempotente Wiederaufnahme nach Prozessausfall;
- menschliche Fragen als dauerhafte Inbox-Einträge und neue Ereignisse;
- GitHub-Issue-, PR-, Review- und Kommentar-Integration;
- lokale oder selbst gehostete Ausführung mit nachvollziehbarer Lizenz.

Aktivität und Releases wurden über die offiziellen GitHub-Repositories und Release-Seiten geprüft. Sterne werden nur als grober Adoptionshinweis verwendet, nicht als Qualitätsbeweis.

## Engere Auswahl

| Kandidat | Lizenz und Aktivität | Was bereits passt | Wesentliche Lücke | Urteil |
| --- | --- | --- | --- | --- |
| [`github/gh-aw`](https://github.com/github/gh-aw) | MIT; sehr aktiv; [`v0.86.2`, 11.08.2026](https://github.com/github/gh-aw/releases/tag/v0.86.2) | GitHub-Trigger, Codex/Claude/Copilot/Gemini, isolierte Actions-Runs, Safe Outputs, Workflow-Komposition, Repo-/Kommentar-Memory, menschliche Gates | Kein fertiger dreiachsiger Review-/Repair-Zustandsautomat; lokale Worktrees und Head-SHA-Aggregation müssen explizit gebaut werden | **Beste Basis für den Pilot-Spike** |
| [`apokamo/kaji`](https://github.com/apokamo/kaji) | Apache-2.0; 12 Sterne; erstellt 12/2025; [`v0.20.0`, 25.08.2026](https://github.com/apokamo/kaji/releases/tag/v0.20.0) | Issue-to-PR-Workflow, Codex/Claude, deterministische `exec`-Steps, `PASS/RETRY/BACK/ABORT`, Artefakte, Iterationsgrenzen, GitHub-Lifecycle, Headless/tmux, Resume ab benanntem Step | Sehr geringe Adoption; automatische Crash-Recovery, Idempotenz und exakte Head-Bindung müssen produktiv geprüft werden; Standardworkflow hat nicht die drei geforderten unabhängigen Review-Achsen | **Höchste fachliche Passung, hohes Reiferisiko** |
| [`dbos-inc/dbos-transact-py`](https://github.com/dbos-inc/dbos-transact-py) | MIT; als Production/Stable klassifiziert; [`2.31.0`, 25.08.2026](https://github.com/dbos-inc/dbos-transact-py/releases/tag/2.31.0) | Postgres-gestützte Durable Steps, automatische Recovery, Queues, dauerhafte Nachrichten und HITL-Inbox | GitHub, Worktrees, Worker-Policies und Review-Verträge bleiben Eigenbau | **Beste eigene lokale Control Plane, falls nötig** |
| [`PrefectHQ/prefect`](https://github.com/PrefectHQ/prefect) | Apache-2.0; reif und aktiv; [`3.8.4`, 25.08.2026](https://github.com/PrefectHQ/prefect/releases/tag/3.8.4) | Self-hosted Server und UI, lokal SQLite oder Postgres, Retries, Abhängigkeiten, typisiertes Pause/Suspend/Resume für menschliche Eingaben | Daten-/Workflow-Plattform statt Coding-Agent-System; GitHub- und Worktree-Verträge bleiben Eigenbau | **Guter Operator-UI-Prototyp, aber mehr Plattform als nötig** |
| [`temporalio/temporal`](https://github.com/temporalio/temporal) | MIT; sehr reif; [`v1.31.2`, 08.07.2026](https://github.com/temporalio/temporal/releases/tag/v1.31.2) | stärkste Durable-Execution-, Retry-, Signal- und Recovery-Semantik; Activities können frische Worker sein | eigener Server/Cluster, SDK- und Determinismusregeln; keinerlei fertige GitHub-/Agentenlogik | **Technisch stark, für diesen linearen Pilot überdimensioniert** |
| [`OpenHands/OpenHands`](https://github.com/OpenHands/OpenHands) | MIT-Kern, Enterprise-Verzeichnis separat lizenziert; sehr aktiv; [`v1.15.0`, 21.08.2026](https://github.com/OpenHands/OpenHands/releases/tag/v1.15.0) | sandboxed Coding-Worker, [Issue Resolver](https://github.com/OpenHands/OpenHands/blob/main/openhands/resolver/README.md), [iterative GitHub-Action](https://docs.openhands.dev/openhands/usage/run-openhands/github-action), PR-Review und persistierbare Konversationen | keine fertige dauerhafte Implementieren–Testen–Dreifach-Review–Repair-Control-Plane | **Starker Worker, kein Orchestrator-Ersatz** |
| [`SWE-agent/mini-swe-agent`](https://github.com/SWE-agent/mini-swe-agent) | MIT; aktiv; [`v2.4.6`, 23.07.2026](https://github.com/SWE-agent/mini-swe-agent/releases/tag/v2.4.6); Paketstatus Alpha | sehr kleiner Issue-to-Patch-Worker, Shell-Aktionen sind pro Aufruf unabhängig, Trajectory-Artefakte | keine Durable-Orchestrierung, keine echte GitHub-HITL- oder Review-Control-Plane | **Einfacher Worker, nicht der Workflow** |

## 1. GitHub Agentic Workflows (`gh-aw`)

[`gh-aw`](https://github.com/github/gh-aw) kompiliert Markdown mit YAML-Frontmatter in normale GitHub-Actions-Workflows. GitHub Actions liefert Trigger, Runner, Logs und Job-Orchestrierung; `gh-aw` ergänzt Agenten-Engines, Sandbox, Berechtigungen und sichere Ausgaben. Codex ist eine offiziell unterstützte Engine und wird mit `engine: codex` sowie `CODEX_API_KEY` oder `OPENAI_API_KEY` konfiguriert ([Codex-Engine](https://github.github.com/gh-aw/engines/codex/), [Funktionsweise](https://github.github.com/gh-aw/introduction/how-they-work/)).

### Warum es Context Drift reduziert

Ein Issue-, PR-, Kommentar- oder Review-Ereignis startet einen neuen Actions-Run und damit einen neuen Agentenkontext. Zwischen den Läufen können explizite Artefakte verwendet werden:

- [Safe Outputs](https://github.github.com/gh-aw/reference/safe-outputs/) trennen den standardmäßig nur lesenden Agentenjob von privilegierten Jobs, die Issues, Kommentare, Pull Requests oder Labels schreiben.
- [PR Safe Outputs](https://github.github.com/gh-aw/reference/safe-outputs-pull-requests/) können Pull Requests erstellen oder aktualisieren, auf den PR-Branch pushen, Reviews und Review-Kommentare abgeben und Reviewer hinzufügen.
- [Repo Memory](https://github.github.com/gh-aw/reference/repo-memory/) speichert begrenzte Dateien versioniert auf eigenen Git-Branches; [MemoryOps](https://github.github.com/gh-aw/patterns/memory-ops/) beschreibt Repo-, Cache- und Kommentar-Memory für schrittweise Aufgaben.
- [Artifacts](https://github.github.com/gh-aw/reference/artifacts/) und der `upload-artifact`-Output transportieren runbezogene Dateien.
- [`workflow_call` und `dispatch-workflow`](https://github.github.com/gh-aw/patterns/orchestration/) starten getrennte Worker synchron oder asynchron und können eine explizite Korrelations-ID weitergeben.
- Kritische Schreibjobs können über GitHub Environments eine [externe menschliche Freigabe](https://github.github.com/gh-aw/reference/faq/) verlangen.

Damit kann der Workflow bewusst **keinen** pausierten Gedankengang fortsetzen. Nach einem Fehler oder einer menschlichen Antwort startet ein neuer Worker und liest nur Auftrag, Head-SHA, relevante Evidence, Findings und Entscheidung.

### Konkreter Zuschnitt für den Pilot

```text
Issue + ready-for-agent
        │
        ▼
frischer Implementierungs-Workflow ──► Draft-PR + Head-SHA
        │
        ▼
normale deterministische CI
        │
        ├──► frischer Requirements-Review
        ├──► frischer Code-Review
        └──► frischer Architektur-Review
                    │
                    ▼
         deterministischer Aggregator
          │ pass              │ fail
          ▼                   ▼
 verified/awaiting       Findings-JSON +
 human review            frischer Repair-Run
                              │
                              └──► neue Head-SHA, alles erneut
```

Die drei festen Reviews sollten **nicht** einem Agenten überlassen werden, der dynamisch einen von mehreren `call-workflow`-Workern auswählt. Sie sollten als drei fest verdrahtete Jobs oder getrennte Workflows laufen. Jeder erhält dieselbe `head_sha`, checkt genau diesen Commit aus und liefert ein schema-validiertes Verdict. Der Aggregator verwirft Resultate, wenn GitHub inzwischen einen anderen PR-Head meldet.

`needs_human` sollte einen strukturierten Kommentar oder ein kleines JSON-Artefakt mit Frage, Optionen, Empfehlung, Head-SHA und Findings erzeugen und den Lauf beenden. Ein autorisierter Kommentar oder ein Label startet anschließend einen neuen Repair-/Continuation-Run. Damit entfallen LangGraph-Interrupt, Checkpoint-Zuordnung und Wiederaufnahme einer verborgenen Codex-Session.

### Grenzen

- `gh-aw` liefert keinen fertigen dreiachsigen Review-Aggregator, keinen Runden-Zähler und keine fachliche `needs-info`/`ready-for-human`-Policy. Das bleibt kleine deterministische Workflow-Logik.
- GitHub-hosted Runner besitzen nur ephemere Checkouts. Selbst gehostete Runner werden unterstützt, aber `gh-aw` verwaltet nicht automatisch die heutigen lokalen, laufgebundenen Worktrees und deren Cleanup.
- Repo Memory ist eine Dateiablage, keine transaktionale Workflow-Datenbank. Der kanonische Zustand sollte deshalb möglichst in Issue, PR, Head-SHA, Check Runs und versionierten Ergebnisartefakten liegen.
- Das Projekt ist aktiv und breit angenommen, aber noch `0.x` und entwickelt sich schnell. Workflow-Quellen und kompilierte Lock-Dateien müssen versionsgepinnt und im Review gehalten werden.

[`githubnext/agentics`](https://github.com/githubnext/agentics) ist dazu kein zweiter Orchestrator, sondern eine MIT-lizenzierte Sammlung installierbarer `gh-aw`-Workflows. Sie ist eine gute Quelle für GitHub-native Muster, ersetzt aber nicht die pilotspezifische Head-SHA-, Evidence- und Repair-Policy.

Als noch kleinerer Baustein kann [`openai/codex-action`](https://github.com/openai/codex-action) Codex direkt in normalen Actions-Jobs ausführen. Das Apache-2.0-Projekt liefert einen frischen Codex-Lauf und strukturierbare Ergebnisse, aber keinerlei übergeordnete Orchestrierung. Es ist die Kontrollvariante für den Spike: gewöhnliches Actions-YAML plus Codex-Action statt `gh-aw`.

## 2. Kaji

[`kaji`](https://github.com/apokamo/kaji) beschreibt sich ausdrücklich als „closed-loop agentic development“ für Claude Code, Codex und weitere CLIs. Der [mitgelieferte GitHub-Workflow](https://github.com/apokamo/kaji/blob/main/.kaji/wf/official/dev.yaml) definiert benannte Schritte, Übergänge und begrenzte Zyklen. Agentensteps schreiben `verdict.yaml`; der Harness entscheidet deterministisch anhand von `PASS`, `RETRY`, `BACK` oder `ABORT`. Nicht-agentische Prüfungen können direkte `exec`-Steps sein.

Das trifft den fachlichen Bedarf ungewöhnlich gut:

- GitHub Issue, Branch, PR, Review-Polling und Issue-Abschluss gehören zum Standardablauf.
- Design-, Code- und PR-Fix-Schleifen haben `max_iterations` und ein explizites `on_exhaust`.
- Headless-Ausführung eignet sich für Automation; der tmux-Runner macht Agentenarbeit sichtbar.
- `--from <step>` und `--step <step>` erlauben eine artefaktbasierte Wiederaufnahme ohne alten Chat.
- Pro Step können verschiedene Agenten und Modelle ausgewählt werden; die Übergabe erfolgt über Artefakte.

Vor einer Übernahme müssten vier Dinge in einem Spike bewiesen werden:

1. Jeder Review- und Repair-Step startet tatsächlich mit dem gewünschten frischen Kontext; `resume:` darf nur gezielt eingesetzt werden.
2. Drei unabhängige Review-Achsen lassen sich fest verdrahten und ihre Ergebnisse gegen exakt dieselbe Head-SHA aggregieren.
3. Ein Prozessabbruch zwischen Git-/GitHub-Schreiboperation und Verdict wird idempotent rekonstruiert; `--from` allein ist noch keine automatische Crash-Recovery.
4. Eine menschliche Antwort wird korreliert persistiert und startet einen neuen Step, ohne einen weiteren Repair-Versuch zu verbrauchen.

Das Projekt hat bei sehr schneller Release-Frequenz derzeit nur rund zwölf Sterne und einen Fork. Seine Architektur ist fast ein fertiges Abbild des gewünschten Systems, seine Betriebserfahrung aber nicht mit `gh-aw`, Prefect oder Temporal vergleichbar. Deshalb ist Kaji ein sehr guter **Code- und Spike-Kandidat**, aber noch kein belastbarer Produktionsentscheid.

## 3. Durable Workflow Engines

### DBOS

DBOS ist die beste Option, falls GitHub nicht allein das Workflow-Gedächtnis sein soll. Die Python-Bibliothek annotiert normale Funktionen als Workflows und Steps, speichert Inputs und Step-Ergebnisse in Postgres und nimmt unterbrochene Workflows ab dem letzten abgeschlossenen Step wieder auf ([Repository](https://github.com/dbos-inc/dbos-transact-py), [Architektur und Recovery](https://docs.dbos.dev/architecture)). Ein separater Orchestrierungsserver ist für die lokale Grundform nicht nötig.

Für menschliche Entscheidungen bietet DBOS mit `send`/`recv` eine dauerhafte Inbox: Deadline und Nachricht bleiben in der Datenbank, während der Prozess Stunden oder Tage beendet sein kann ([Reliable Human-in-the-Loop](https://docs.dbos.dev/ai/hitl)). Jeder Workflow-Step kann trotzdem einen neuen Codex-Prozess mit einem kleinen Übergabepaket starten. Das löst Durable Execution, aber nicht GitHub-, Worktree-, Sicherheits- oder Review-Semantik; diese Teile des heutigen Piloten blieben erhalten.

### Prefect

Prefect lässt sich lokal mit UI und SQLite starten oder mit Postgres betreiben ([Self-hosted Server](https://github.com/PrefectHQ/prefect/blob/main/docs/v3/how-to-guides/self-hosted/server-cli.mdx)). Flows können pausieren oder suspendieren, typisierte menschliche Eingaben in der UI anfordern und danach weiterlaufen ([Interactive Workflows](https://docs.prefect.io/v3/advanced/interactive)). Das ist operatorfreundlicher als eine eigene Interventions-Inbox, trägt aber eine komplette Workflow-Plattform in den Pilot. Agentenisolierung und GitHub-Artefaktverträge müssen auch hier selbst entworfen werden.

[`windmill-labs/windmill`](https://github.com/windmill-labs/windmill) ist eine weitere reife, selbst hostbare Script-/Flow-Plattform mit UI, Jobs und Approval-Schritten. Für diesen Fall gilt derselbe Einwand noch stärker: Sie kann den Ablauf hosten, liefert aber weder Coding-Agent-Isolation noch die Issue-/PR-/Head-SHA-Verträge. Sie ist sinnvoll, wenn Windmill ohnehin als interne Automationsplattform betrieben wird, nicht als gezielte LangGraph-Ablösung.

### Temporal

Temporal bietet die stärkste Recovery-Semantik: Workflow-History, langlebige Ausführung, Retries und Messages/Signals überleben Prozess- und Infrastrukturausfälle ([Dokumentation](https://docs.temporal.io/), [Server-Repository](https://github.com/temporalio/temporal)). Implementierung, Tests und Reviews könnten getrennte Activities mit typisierten Resultaten sein. Für einen einzelnen linearen lokalen Pilot wären Server, Worker, Persistence, SDK-Regeln und Betriebsaufwand jedoch voraussichtlich schwerer als LangGraph. Temporal ist nur dann die richtige Wahl, wenn es bereits Plattformstandard ist oder viele verteilte, jahrelang langlebige Prozesse getragen werden sollen.

## 4. Coding-Agenten und Reviewer als Bausteine

### OpenHands

OpenHands bringt einen produktnahen Sandbox- und Coding-Worker mit. Der Issue Resolver kann durch Label oder `@openhands-agent` gestartet werden, erstellt einen Draft-PR oder Branch, kommentiert das Ergebnis und verarbeitet spätere PR-Kommentare ([Resolver README](https://github.com/OpenHands/OpenHands/blob/main/openhands/resolver/README.md), [GitHub Action](https://docs.openhands.dev/openhands/usage/run-openhands/github-action)). Es gibt außerdem eine gesonderte [PR-Review-Action](https://github.com/OpenHands/docs/blob/main/openhands/usage/use-cases/code-review.mdx) und Conversation-Persistence.

Das macht OpenHands zu einem möglichen Ersatz für einzelne Codex-Worker. Die dauerhafte Phasenlogik fehlt aber. Werden persistierte Konversationen als Übergabe benutzt, entsteht erneut genau das Context-Drift-Risiko. Für den Pilot sollte OpenHands daher höchstens frisch pro Phase gestartet werden und nur strukturierte Artefakte zurückgeben.

### mini-SWE-agent und SWE-agent

[`mini-swe-agent`](https://github.com/SWE-agent/mini-swe-agent) ist bewusst minimal: ein kleiner Issue-to-Patch-Agent, dessen Shell-Aktionen jeweils als unabhängige Subprozesse laufen. Das ist attraktiv für austauschbare Implementierungsworker. [`SWE-agent`](https://github.com/SWE-agent/SWE-agent) besitzt umfangreichere Konfiguration, Docker-/SWE-ReX-Ausführung, Trajectories und Replay, ist laut eigener Dokumentation aber inzwischen maintenance-only zugunsten von mini-SWE-agent ([CLI-Dokumentation](https://swe-agent.com/latest/usage/cli/)). Beide liefern keinen dauerhaften menschlichen Issue-to-PR-Prozess.

### PR-Agent

[`The-PR-Agent/pr-agent`](https://github.com/The-PR-Agent/pr-agent) ist MIT-lizenziert, aktiv und mit [`v0.43.0` vom 22.08.2026](https://github.com/The-PR-Agent/pr-agent/releases/tag/v0.43.0) deutlich verbreiteter als die jungen End-to-End-Orchestratoren. Es automatisiert PR-Beschreibung, Review, Verbesserungsvorschläge und ähnliche PR-Aufgaben über GitHub. Es eignet sich als zusätzliche Review-Achse oder Vergleichsbaseline, implementiert aber weder Issue-Claim, schreibenden Implementer, deterministische Tests noch einen dauerhaften Repair-/HITL-Zustandsautomaten.

### Pydantic AI

[`pydantic/pydantic-ai`](https://github.com/pydantic/pydantic-ai) ist eine sinnvolle Agentenschicht, wenn DBOS, Prefect oder Temporal gewählt wird. Es unterstützt typisierte Resultate, Tool-Approvals und offizielle Durable-Execution-Integrationen ([Durable Execution](https://github.com/pydantic/pydantic-ai/blob/main/docs/durable_execution/overview.md), [Deferred Tools/Approvals](https://github.com/pydantic/pydantic-ai/blob/main/docs/deferred-tools.md)). GitHub-, Worktree- und Review-Policy bleiben aber Anwendungscode; allein vereinfacht Pydantic AI den Piloten nicht.

## 5. Frühe vollständige Control Planes und Inspirationsquellen

- [`Untrivial-ai/agent-orchestrator`](https://github.com/Untrivial-ai/agent-orchestrator), Apache-2.0, [`v0.12.7`](https://github.com/Untrivial-ai/agent-orchestrator/releases/tag/v0.12.7), bietet Worktrees, mehrere Coding-CLIs, PR-/CI-Beobachtung und eine menschliche Desktop-Inbox. Es setzt aber stärker auf persistente Agentensessions und verschiebt damit das Drift-Problem teilweise.
- [`openai/symphony`](https://github.com/openai/symphony), Apache-2.0, [`v0.0.2`](https://github.com/openai/symphony/releases/tag/v0.0.2), ist ein wichtiges Architekturvorbild: Tracker-Arbeit, isolierter Workspace pro Issue, Reconciliation und `Human Review` statt Sessionsteuerung. Die Implementierung ist ausdrücklich Engineering Preview; die [Spezifikation](https://github.com/openai/symphony/blob/main/SPEC.md) ist derzeit kein fertiger GitHub-Pilotersatz.
- [`KjellKod/quest`](https://github.com/KjellKod/quest) nutzt frische Agentenkontexte, `state.json`, Handoff-, Plan- und Review-Artefakte sowie Human Gates. Das ist ein passendes manuell geführtes Muster, aber keine GitHub-native, unbeaufsichtigte Control Plane.
- [`nutthouse/tutti`](https://github.com/nutthouse/tutti) besitzt Worktree-Isolation, typisierte Artefaktübergaben, SQLite-Eventlog, Issue-Leases und einen SDLC-Zustandsautomaten. Es ist ein interessantes frühes lokales Produkt, arbeitet aber auch mit persistenten tmux-Agententeams und hat Teile des Replay-/Adapter-Umfangs noch auf der Roadmap.
- [`apify/shepherd`](https://github.com/apify/shepherd) beschreibt nahezu ideal „files are the only handoff“ mit engen Lesemengen, blind unabhängigen Reviewern, Testartefakten, Human Gates und `_state.json`. Das öffentliche Repository enthält aktuell jedoch keine Lizenzdatei. Ohne explizite Lizenz ist es trotz technischer Passung kein übernehmbarer Open-Source-Kandidat.

CrewAI und AutoGen wurden nicht in die engere Auswahl aufgenommen. Sie können Multi-Agent-Abläufe, State und menschliche Eingaben modellieren, machen aber wieder Agentenkonversation und Framework-State zum Mittelpunkt. Das würde LangGraph eher durch eine ähnliche Abstraktion ersetzen als den Pilot vereinfachen. Restate wurde ebenfalls ausgeschlossen: Der Server steht unter Business Source License 1.1 und bezeichnet diese in der eigenen [Lizenzdatei](https://github.com/restatedev/restate/blob/main/LICENSE) ausdrücklich nicht als Open-Source-Lizenz.

## Empfehlung für Daniel

### Spike A: `gh-aw` plus normale Actions

Das ist die bevorzugte Richtung. Der Spike sollte nur einen kleinen vollständigen Vertikalschnitt beweisen:

1. Ein autorisiertes Issue-Label startet einen frischen Codex-Implementierungsrun.
2. Der Run eröffnet einen Draft-PR und veröffentlicht ein schema-validiertes `implementation-result.json` mit Base- und Head-SHA.
3. Normale CI prüft den Head deterministisch.
4. Drei getrennte, nur lesende Review-Runs liefern jeweils ein `review-result.json` für exakt diese SHA.
5. Ein deterministischer Aggregator akzeptiert nur drei aktuelle schema-valide Resultate.
6. Bei Findings startet ein frischer Repair-Run mit Findings, Tests und Head-SHA; alte Review-Ergebnisse werden nie wiederverwendet.
7. Bei `needs_human` endet der Run mit einer strukturierten GitHub-Frage. Eine autorisierte Antwort startet einen neuen Run.
8. Kein Schritt resumiert eine Agentenkonversation; die Wiederaufnahme wird ausschließlich aus GitHub und Ergebnisartefakten rekonstruiert.

Parallel sollte derselbe Schnitt einmal mit gewöhnlichem Actions-YAML und `openai/codex-action` gebaut oder zumindest skizziert werden. So wird sichtbar, welchen realen Wert `gh-aw` gegenüber wenigen eigenen Jobs liefert.

### Spike B: Kaji lokal

Nur falls der lokale Mac, sichtbare tmux-Sessions und persistente Worktrees zwingend bleiben, sollte derselbe Vertikalschnitt mit Kaji ausprobiert werden. Der Spike ist erfolgreich, wenn er Prozessabbruch, doppelte Zustellung, einen veralteten PR-Head, drei unabhängige Reviews und eine menschliche Antwort ohne Wiederaufnahme des alten Agentenkontexts korrekt behandelt.

### Eskalationspfad

DBOS sollte erst ergänzt werden, wenn Spike A zeigt, dass GitHub-Artefakte und Actions-Runs für Recovery oder lokale Offline-Zustellung nicht ausreichen. Temporal, Prefect, Windmill oder eine neue Agenten-Control-Plane sind erst gerechtfertigt, wenn der Pilot zu einer allgemeinen Plattform für viele langlebige Workflows wird.

Die wahrscheinlich richtige Zielarchitektur lautet daher:

> **GitHub ist das dauerhafte Arbeitspaket; Actions/`gh-aw` starten frische Spezialisten; deterministische Checks entscheiden Übergänge; Menschen antworten durch neue Ereignisse.**

Damit interagieren Implementierung, Tests, Reviews und Reparaturen eng miteinander, ohne dass sie dafür denselben Gesprächskontext teilen müssen.
