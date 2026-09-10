# Lösungsrecherche: Make-or-Buy für die Distributed Codex Work Package Control Plane

**Stand:** 2026-09-05

**Status:** Desk Research; keine der Bewertungen ersetzt den vorgesehenen lokalen Spike oder eine Anbieterzusage.

**Entscheidungsgrundlage:** [Spec](./spec.md), [Make-or-Buy-Entscheidungsvorlage](./make-or-buy-entscheidungsvorlage.md), [ADR 0008](../../docs/adr/0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md) und die [Dokumentation des LangGraph-Piloten](../../docs/langgraph-github-issue-pilot.md).

## Leseschlüssel und Evidenzstandard

- **Fakt** bezeichnet eine Aussage, die durch eine lokale Implementierung oder eine direkt verlinkte offizielle Primärquelle belegt ist.
- **Inferenz** bezeichnet eine aus diesen Fakten abgeleitete Bewertung für die konkrete Spec.
- **Offen** bezeichnet eine Annahme, die erst durch Spike, Lastmessung, Rechts-/Security-Prüfung oder ein belastbares Angebot entschieden werden kann.
- Externe Fakten stammen ausschließlich aus offiziellen Dokumentationen, Produkt-/Pricing-Seiten, Repositories, Releases oder Lizenzdateien. Marketingaussagen werden nicht als Erfüllungsnachweis für ein Gate behandelt.
- „Nativ“ bedeutet nicht „die Spec ist ohne Anwendungscode erfüllt“. Codex-Adapter, Domänenmodell, Repository-Autorisierung, Operator-API/UI und Artefaktverwaltung bleiben bei allen realistischen Kandidaten Anwendungscode.

## Executive Finding

**Inferenz:** Die realistische Shortlist besteht aus drei Pfaden:

1. **Microsoft Agent Framework (MAF) für .NET + Durable Extension + Durable Task Scheduler (DTS), bevorzugt mit BYO-Compute-Workern.** Das ist der passendste Spike-Kandidat, weil die fachliche Graph-/Agent-Abstraktion und Durable-Ausführung in einem .NET-Stack zusammenkommen. Die Durable Extension ist jedoch noch Preview; damit ist die Präferenz ausdrücklich bedingt.
2. **Temporal Cloud + eigene .NET-Domänen-, Codex- und Operator-Schicht.** Das ist aktuell die stärkste risikoarme Buy-Baseline für langlebige Workflow-Ausführung. Temporal liefert aber keine Codex-spezifische Agent-Control-Plane; der fachliche Eigenbau bleibt groß.
3. **Den vorhandenen LangGraph/Python-Piloten zentralisieren.** Das ist die belastbare Rückfalloption mit dem höchsten Wiederverwendungswert und der kürzesten Strecke zur nächsten verifizierbaren Iteration, trägt aber den Python-Stack sowie einen erheblichen Ausbau von Einzelprozess/SQLite zu zentralem Mehrbenutzerbetrieb weiter.

**Inferenz:** MAF + Azure Functions + DTS ist eine prüfenswerte Hosting-Variante, aber nicht automatisch gleichwertig mit BYO Compute: Der Codex-Prozess, Git-Worktrees und lange lokale Tool-Ausführungen passen möglicherweise nicht sauber in den Functions-Lebenszyklus. Ein hybrider Aufbau mit Functions für Orchestrierung und separaten Codex-Workern würde faktisch wieder in Richtung BYO-Compute-Variante gehen.

**Inferenz:** Temporal Core self-hosted bleibt eine valide Souveränitätsoption, verursacht gegenüber Temporal Cloud aber zusätzlichen Cluster-, Datenbank-, Upgrade-, Backup- und Bereitschaftsaufwand. Ein vollständiger Eigenbau des Durable Cores ist technisch möglich, aber ohne einen zwingenden regulatorischen oder strategischen Grund nicht die bevorzugte Erstinvestition.

**Offen:** Keine Variante darf ausgewählt werden, solange die U-Gates G03, G06, G07 und G08 nicht in einem End-to-End-Spike bestanden sind. Die zentrale Frage ist die kontrollierte Codex-Sitzungs- und Seiteneffekt-Semantik – nicht, welches Framework die längste Featureliste besitzt.

## Die bestehende LangGraph-Verhaltensbaseline

**Fakt (lokal):** Der Pilot verwendet Python, FastAPI, LangGraph, einen SQLite-Checkpointer und Codex CLI beziehungsweise Codex app-server. Er beweist bereits Issue-Claim, langlebigen lokalen Workflow, isolierte Git-Worktrees, Evidenzqualifizierung, Draft-PR, drei unabhängige Reviews desselben Head-SHA, begrenzte Reparaturschleifen, Human Intervention, Wiederanlauf/Idempotenz über die HTTP-Grenze und Redaction. Siehe [Pilot-Dokumentation](../../docs/langgraph-github-issue-pilot.md), [README](../../langgraph-github-issue-pilot/README.md) und [Paketdefinition](../../langgraph-github-issue-pilot/pyproject.toml).

**Fakt (extern):** LangGraph stellt Checkpoints/Threads, Human-in-the-loop, Fault Tolerance und Time Travel bereit; beim Fortsetzen können erfolgreiche Knoten desselben Supersteps über „pending writes“ wiederverwendet werden ([Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Time Travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)). Interrupts benötigen einen dauerhaften Checkpointer, und vor einem Interrupt ausgeführte Seiteneffekte müssen idempotent sein ([Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)). Das Projekt ist MIT-lizenziert ([Lizenz](https://github.com/langchain-ai/langgraph/blob/main/LICENSE)); die offizielle Paketdefinition klassifiziert es als „Production/Stable“ ([pyproject.toml](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/pyproject.toml)).

**Nicht durch den Piloten bewiesen:** zentrale Mehrbenutzer-Control-Plane, zentrale Identität und aktuelle Repository-Autorisierung, eine globale gefencete Control Lease samt Transfer/Forced Takeover, verteilte Worker, lückenlos wiederaufnehmbare Remote-Events sowie die exakten Codex-Semantiken für Resume, Fork, Fresh Retry und adressierte Live-Interrupts plus Durable Queue.

Diese Baseline ist der Akzeptanzmaßstab für jeden neuen Spike. Ein MAF- oder Temporal-Prototyp ist nicht besser, wenn er nur einen langlebigen „Hello World“-Workflow zeigt, aber die bereits belegten Pilotverhalten verliert.

## Realistische Shortlist und Abgrenzung

| Variante | Architekturform | Was wird gekauft/übernommen? | Was bleibt Eigenbau? | Vorläufiger Status |
|---|---|---|---|---|
| A. Vollständiger .NET-Core | MAKE | nur Standardbausteine und deren Betriebsplattform | Durable Engine, Scheduling, Replay/Recovery, Domain, Codex, Operator, Security | nicht bevorzugt |
| B. LangGraph/Python zentral | STATUS QUO+ | OSS-Graph-/Checkpoint-Modell plus vorhandener Pilot | Zentralisierung, Worker/Queue, Identität, Lease, Events, UI/API, Produktion | Shortlist/Fallback |
| C. MAF .NET + Durable, BYO + DTS | HYBRID BUY | MAF-Graph/Agent-Abstraktion, Durable Extension, gemanagter Scheduler | Domain, Codex, Operator, Security, Artefakte, anwendungsspezifische Events | bevorzugter Spike |
| D. MAF .NET + Functions + DTS | BUY/HYBRID | zusätzlich gemanagte Functions-Compute-Schicht | wie C; eventuell trotzdem separate Codex-Worker | Hosting-Alternative, Spike nötig |
| E. Temporal Core self-hosted | HYBRID/MAKE-OPS | OSS-Durable Engine und .NET SDK | Betrieb des Temporal-Clusters plus Domain, Codex, Operator, Security | Souveränitätsoption |
| F. Temporal Cloud | BUY/HYBRID | gemanagter Temporal Service | Worker sowie Domain, Codex, Operator, Security, Artefakte | Shortlist/Risikobaseline |

## Kandidatenprofile

### A. Vollständiger eigener .NET-Control-Plane-Core auf Standardbausteinen (MAKE)

**Architekturform – Inferenz:** ASP.NET Core API/Operator-Backend, eigener persistenter Zustandsautomat, Postgres mit Outbox/Inbox und Fencing, Queue/Broker, Object Storage, verteilte .NET-Worker und ein eigener Event-/Projektionspfad.

**Nativer Nutzen – Fakt/Inferenz:** .NET-Team-Fit, freie Daten- und Hostingwahl und kein Workflow-Framework-Lock-in. Standarddatenbank, Broker und OpenTelemetry lösen jedoch nicht von selbst deterministisches Wiederanlaufen, langlebige Timer, sichere Activity-Retries oder Workflow-Versionierung.

**Notwendiger Eigenbau:** praktisch die gesamte Control-Plane-Semantik einschließlich Scheduler, Recovery, Lease/Fencing, Retry/Adoption, Sessiongraph, Eventstream, Security Boundary, Redaction, Operatoroberfläche und Upgrade-Migrationen.

**Reife/Lifecycle – Offen:** Die Einzelbausteine können ausgereift sein; die relevante Gesamtlösung existiert noch nicht und hat daher keinerlei Felderfahrung.

**Hosting und Lock-in – Inferenz:** frei hostbar und niedriger Produkt-Lock-in, dafür hoher Lock-in in eigenen unverwechselbaren Infrastrukturcode und dessen Autorenwissen.

**Kostenmodell:** Lizenzkosten der Standardbausteine plus Compute, Datenbank, Queue, Storage, Observability; dominierend sind initiale Entwicklungszeit, Fehlerkorrektur, Upgrade-/Migrationsarbeit, Last- und Chaos-Tests sowie 24/7-Betriebsfähigkeit. Ohne Mengengerüst und Personalkostensatz ist keine seriöse TCO-Zahl möglich.

### B. Bestehenden LangGraph/Python-Piloten zentralisieren (STATUS QUO+)

**Architekturform – Fakt/Inferenz:** Der lokale FastAPI/LangGraph/Codex-Pilot wird um produktionsfähige persistente Ablage, zentrale API, verteilte Worker, Identitäts-/Autorisierungsadapter, Control Lease, Eventprojektion und Operator-Client erweitert.

**Nativer Nutzen – Fakt:** Checkpointing, Threads, Interrupt/Resume, Time Travel und Graphausführung sind Teil von LangGraph ([Persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [Time Travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)); das lokale Pilotverhalten ist bereits ausführbar und getestet. Die offizielle Durable-Execution-Anleitung verlangt trotzdem, nichtdeterministische und seiteneffektbehaftete Operationen in Tasks zu kapseln und idempotent zu entwerfen ([Functional API](https://docs.langchain.com/oss/python/langgraph/functional-api)).

**Notwendiger Eigenbau:** Multi-Tenant-/Mehrbenutzerbetrieb, produktionsfähige DB- und Worker-Topologie, Codex-Sitzungsgraph, globale Lease/Fencing, externe Effekt-Adoption, lückenloser Eventcursor, Identity/Repository-Auth, Artefakte und UI.

**Reife/Lifecycle – Fakt:** LangGraph ist MIT-lizenziert und offiziell als Production/Stable klassifiziert ([Lizenz](https://github.com/langchain-ai/langgraph/blob/main/LICENSE), [Paketmetadaten](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/pyproject.toml)). **Inferenz:** Die Reife des Frameworks beseitigt nicht die noch fehlende Reife der zentralen Anwendung.

**Hosting und Lock-in:** self-managed Python-Service; optionales LangSmith ist nicht Bestandteil dieser Variante. Der Code ist OSS, die Checkpoint-/State- und Graphsemantik erzeugt dennoch Migrationskosten.

**Kostenmodell:** keine LangGraph-Lizenzgebühr; Python-Compute, Produktionsdatenbank, Queue, Artefakt-Storage, Observability und Betrieb. Optionales LangSmith wäre ein separater Buy-Posten; dessen öffentliche Pläne und nutzungsabhängige LCU/LSU-Abrechnung stehen auf der [offiziellen Pricing-Seite](https://www.langchain.com/pricing). Hauptunsicherheit ist der Ausbauaufwand, nicht die OSS-Lizenz.

### C. Microsoft Agent Framework für .NET + Durable Extension, BYO Compute + DTS

**Architekturform – Fakt:** MAF modelliert Workflows als Graph aus typisierten Executoren und unterstützt Fan-out/Fan-in, Events, Checkpoints und Human-in-the-loop ([Workflow Concepts](https://learn.microsoft.com/en-us/agent-framework/concepts/workflows/)). Die Durable Extension unterstützt neben Azure Functions ausdrücklich selbst gehostete Workerprozesse, Container, Kubernetes oder eigene Anwendungsinfrastruktur; diese Worker verbinden sich mit einem Durable Task Scheduler Backend ([Durable Extension – Hosting](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions)). DTS ist dabei weiterhin ein gemanagter Azure-Dienst, nicht ein selbst gehosteter Scheduler ([offizielle DTS-Provider-Dokumentation](https://github.com/Azure/durabletask/blob/main/docs/providers/durable-task-scheduler.md)).

**Nativer Nutzen – Fakt:** langlebige Agent-/Workflow-Sitzungen, verteilte zustandslose Worker, Failure Recovery, externe Events/HITL und ein Dashboard werden von der Durable Extension adressiert; zuverlässiges Streaming verwendet einen Response-Callback-Mechanismus wie Redis Streams ([Durable Extension – Hosting](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions)).

**Notwendiger Eigenbau – Inferenz:** IssueRun-Domäne, Codex-Adapter und Sitzungsidentitäten, globales Lease/Fencing, External-Effect-Ids und Adoption, Security/Repository-Auth, Redaction, anwendungsfachlicher Eventverlauf, Artefaktablage, Operator-API/UI und Export.

**Reife/Lifecycle – Fakt:** Der MAF-Kern ist MIT-lizenziert ([Repository](https://github.com/microsoft/agent-framework)) und das Workflow-Paket liegt stabil als `1.20.0` vor ([NuGet](https://www.nuget.org/packages/Microsoft.Agents.AI.Workflows/)). Die Durable-Pakete sind dagegen am Stichtag Preview, beispielsweise `Microsoft.Agents.AI.DurableTask 1.16.0-preview.260730.1` ([NuGet](https://www.nuget.org/packages/Microsoft.Agents.AI.DurableTask/)). Das offizielle GA-Milestone der Durable Extension war am 2026-09-01 noch offen und auf 2026-09-15 terminiert ([GitHub Milestone](https://github.com/microsoft/agent-framework-durable-extension/milestone/1)). **Inferenz:** Ein angekündigtes GA-Datum ist kein Produktionsnachweis.

**Technische Grenzen – Fakt:** Der vollständige Durable-Agent-Konversationszustand wird in einer Durable Entity gespeichert; DTS begrenzt Entity State auf 1 MB. Dokumentiert sind außerdem zusätzliche Latenz, manuelle Kompaktierung beziehungsweise neue Sessions bei Größenproblemen, Request/Response-basiertes Streaming mit externem Callback Store sowie vollständige, nicht wiederherstellbare Löschung nach TTL ([MAF Durable Agents](https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-agents-microsoft-agent-framework)). **Inferenz:** Der fachliche Run/Event-/Artefaktverlauf darf deshalb nicht ungeteilt als MAF-Agentzustand modelliert werden.

**Hosting und Lock-in:** Worker und API bleiben in eigener Infrastruktur, Scheduler-State liegt in Azure DTS. MAF und die Durable Extension sind MIT-lizenziert ([MAF](https://github.com/microsoft/agent-framework), [Durable Extension](https://github.com/microsoft/agent-framework-durable-extension)); die DTS-Integration, Betriebssteuerung und gespeicherte Ausführungshistorie schaffen dennoch Azure-/API-Lock-in.

**Kostenmodell – Fakt:** DTS berechnet Scheduler plus Compute. Dedicated ist eine feste CU-Gebühr; Consumption berechnet dispatchte Aktionen. Dokumentiert sind unterschiedliche Durchsatz-, Retention- und HA-Eigenschaften: Dedicated bis 2.000 Aktionen/s je CU, bis 90 Tage Retention und für HA mindestens drei CUs; Consumption bis 500 Aktionen/s und maximal 30 Tage Retention ohne HA ([DTS Billing](https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler-billing)). **Offen:** regionale CU-/Action-Preise, Worker-Compute, Redis, Datenbank, Blob Storage, Observability und Netzwerk. Daher nur die Formel: `DTS-Aktionen oder CUs + BYO-Worker + Redis/Eventpfad + DB/Object Store + Observability + Betrieb`.

### D. Microsoft Agent Framework für .NET + Azure Functions + DTS

**Architekturform – Fakt:** Dieselben MAF-/Durable-Primitiven werden im Azure-Functions-Hostingmodell betrieben; die offizielle Extension unterstützt C# und Python und registriert Durable Workflows/Agents in einer Functions-Anwendung ([Durable Extension – Azure Functions](https://learn.microsoft.com/en-us/agent-framework/hosting/azure-functions)).

**Nativer Nutzen:** zusätzlich gemanagte Skalierung und Compute-Abrechnung. Flex Consumption skaliert auf null und bis zu 1.000 Instanzen ([Flex Consumption](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)).

**Notwendiger Eigenbau:** wie C. **Offen:** Ob der Codex-Prozess selbst innerhalb Functions laufen sollte. Flex Consumption hat zwar für nicht-HTTP-Ausführungen standardmäßig 30 Minuten und konfigurierbar keine feste Maximaldauer, aber Scale-in- und Plattformupdate-Grace-Periods bleiben begrenzt; HTTP-Antworten sind auf 230 Sekunden begrenzt ([Functions Scale and Timeouts](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)). Run-from-package macht das App-Verzeichnis außerdem read-only ([Run from Package](https://learn.microsoft.com/en-us/azure/azure-functions/run-functions-from-deployment-package)). **Inferenz:** langlebige Git-Worktrees und Codex-CLI-Prozesse gehören wahrscheinlich in dedizierte externe Worker; dann ist diese Variante eine hybride Unterform von C.

**Reife/Lifecycle:** MAF Durable bleibt wie in C Preview; Functions und DTS ändern diesen Produktstatus nicht.

**Hosting und Lock-in:** höchste Azure-Integration der MAF-Varianten; geringster eigener Compute-Betrieb, aber größter Azure-Plattform-Lock-in.

**Kostenmodell – Fakt:** Flex Consumption berechnet Ausführungen und GB-Sekunden, ergänzt um Always-Ready-Kosten; die öffentliche Seite nennt monatliche Freikontingente von 250.000 Ausführungen und 100.000 GB-s im Pay-as-you-go-Modell ([Azure Functions Pricing](https://azure.microsoft.com/en-us/pricing/details/functions/)). Hinzu kommen DTS, Storage, Redis/Callback Store, Monitoring und gegebenenfalls separate Codex-Worker. Ohne Profil für Laufzeit, Speicher, Warmhaltung und Aktionen bleibt der Preis offen.

### E. Temporal Core self-hosted + eigene .NET-Schicht

**Architekturform – Fakt:** Eigene .NET-Workflow-/Activity-Worker sprechen mit einem selbst betriebenen Temporal Service. Für Produktion sind Service-Cluster und Persistenz zu betreiben; das offizielle Beispiel umfasst PostgreSQL, Elasticsearch und UI, und Schema-Upgrades sind ein eigener Betriebsprozess ([Self-hosted Deployment](https://docs.temporal.io/self-hosted-guide/deployment)). Anwendungscode/Worker laufen unabhängig davon immer in der eigenen Infrastruktur ([Production Deployment](https://docs.temporal.io/production-deployment)).

**Nativer Nutzen – Fakt:** langlebige Workflow-Historie, Wiederanlauf, Timer, Signals/Updates, Activity-Retries und Visibility. Das offizielle .NET SDK bietet Workflows/Activities und OpenTelemetry-Integration ([SDK Repository](https://github.com/temporalio/sdk-dotnet), [Message Passing](https://docs.temporal.io/develop/dotnet/message-passing)). Visibility ist such- und filterbar, aber eventual consistent; für den autoritativen Stand sind Describe/History zu verwenden ([Visibility](https://docs.temporal.io/visibility)).

**Notwendiger Eigenbau – Inferenz:** vollständige IssueRun-/Agent-Domäne, Codex-Sitzungsgraph und Adapter, Operator/API/UI, Lease/Fencing, anwendungsfachliche Events und Artefakte, Repository-Auth, Redaction und Export. Temporal ist eine Durable-Execution-Plattform, keine fertige Codex-Control-Plane.

**Reife/Lifecycle – Fakt:** Temporal Server und .NET SDK sind MIT-lizenziert ([Server-Lizenz](https://github.com/temporalio/temporal/blob/main/LICENSE), [SDK Repository](https://github.com/temporalio/sdk-dotnet)); das .NET SDK `1.18.0` wurde am 2026-08-13 veröffentlicht ([Release](https://github.com/temporalio/sdk-dotnet/releases/tag/1.18.0)).

**Seiteneffekte – Fakt:** Temporal führt eine abgeschlossene Activity bei Workflow-Replay nicht erneut aus. Stürzt ein Worker jedoch nach dem externen Effekt und vor dem Completion-Acknowledgement ab, kann die Activity erneut ausgeführt werden; die Anwendung muss Idempotency Keys verwenden ([Activity Idempotency](https://docs.temporal.io/activity-definition#idempotency)). **Inferenz:** G08 ist durch Temporal allein nicht erfüllt.

**Hosting und Lock-in:** maximale Daten-/Betriebskontrolle, MIT-Code und selbst kontrollierte Persistenz; Lock-in verbleibt in Workflow-Historien, APIs und deterministischen Workflow-Regeln. Exit ist möglich, aber nicht kostenlos.

**Kostenmodell:** keine Server-Lizenzgebühr; Service-Compute, PostgreSQL, gegebenenfalls Elasticsearch/OpenSearch, Netzwerk, UI/Monitoring, Backups, Upgrades, Disaster Recovery, Sicherheitsbetrieb und On-call plus die eigenen Worker. **Inferenz:** Bei einem kleinen Team kann Betriebs-TCO den vermiedenen SaaS-Preis übersteigen; ohne SRE-Aufwand und RTO/RPO ist das nicht quantifizierbar.

### F. Temporal Cloud + eigene .NET-Schicht

**Architekturform – Fakt:** Temporal Cloud betreibt den Temporal Service; Anwendungscode und Worker verbleiben beim Kunden ([Temporal Cloud](https://temporal.io/cloud), [Production Deployment](https://docs.temporal.io/production-deployment)). Die eigene .NET-Schicht entspricht inhaltlich E, ohne Betrieb des Temporal-Service-Clusters.

**Nativer Nutzen:** Durable Execution, History, Timer, Signals/Updates, Retries und gemanagter Servicebetrieb. Die Codex- und Domänenlücke bleibt identisch zu E.

**Reife/Lifecycle:** derselbe stabile .NET-SDK-Pfad wie E; Service-Lifecycle und SLA sind ein Lieferantenvertrag. Die veröffentlichten Bedingungen nennen 99,9 % Standard-SLA beziehungsweise 99,99 % für replizierte Namespaces ([Terms of Service](https://temporal.io/terms-of-service)). Vertragliche Anwendbarkeit ist zu prüfen.

**Hosting und Lock-in:** Kunden-Worker und Codex-Compute bleiben unter eigener Kontrolle, die Workflow-Historie und Control Plane sind SaaS. Geschlossene Historie ist in Cloud maximal 90 Tage direkt verfügbar; für längere Aufbewahrung ist Export vorgesehen ([Cloud Pricing/Storage](https://docs.temporal.io/cloud/pricing)). **Inferenz:** Der dauerhafte Audit-/Artefaktverlauf der Spec braucht ohnehin eine anwendungseigene Ablage.

**Kostenmodell – Fakt:** Öffentliche Startpreise sind Essentials ab 100 USD/Monat mit 1 Mio. Aktionen, 1 GB Active Storage und 40 GB Retained Storage sowie Business ab 500 USD/Monat mit 2,5 Mio. Aktionen, 2,5 GB Active und 100 GB Retained ([Pricing](https://temporal.io/pricing)). Die dokumentierte Pay-as-you-go-Formel staffelt zusätzliche Aktionen, Active Storage zu 0,042 USD/GB-Stunde und Retained Storage zu 0,00105 USD/GB-Stunde; die Plan Fee ist bei Essentials das Maximum aus 100 USD oder 5 % Usage und bei Business aus 500 USD oder 10 % Usage ([Cloud Pricing](https://docs.temporal.io/cloud/pricing)). Hinzu kommen eigene Worker, App/API/UI, Object Store, Observability, Support/Add-ons, Netzwerk und gegebenenfalls Enterprise-Funktionen. Das ist eine Preisformel, keine TCO-Prognose.

## Longlist: Aufnahme oder Ausschluss

| Kandidat | Primärquellenbefund | Entscheidung für diese Runde |
|---|---|---|
| DBOS | Die offizielle Dokumentation nennt SDKs für Python, TypeScript, Go und Java, aber keinen .NET-SDK-Pfad ([Docs](https://docs.dbos.dev/), [Portable Workflows](https://docs.dbos.dev/explanations/portable-workflows)). DBOS setzt auf eine PostgreSQL-Systemdatenbank und sprachgebundene Anwendungen ([Architecture](https://docs.dbos.dev/architecture)); auch die offizielle GitHub-Organisation weist keinen produktionsreifen .NET-SDK aus ([dbos-inc](https://github.com/dbos-inc/)). | **Ausschluss aus Shortlist. Fakt:** Am Stichtag ist kein produktionsreifer nativer .NET-SDK-Pfad belegt. Ein Brückendienst in einer anderen Sprache wäre zusätzlicher Integrations- und Betriebsaufwand und unterläuft den .NET-Vorteil. |
| Prefect | Prefect ist ein Apache-2.0-lizenziertes Python-Workflow-Orchestrierungsprojekt ([Repository](https://github.com/PrefectHQ/prefect)); Worker und interaktive Pause/Resume-Flows sind dokumentiert ([Workers](https://docs.prefect.io/v3/concepts/workers), [Interactive Workflows](https://docs.prefect.io/v3/advanced/interactive)). Self-hosted HA bringt PostgreSQL-/Redis-Betrieb mit ([Self-hosted](https://docs.prefect.io/v3/advanced/self-hosted)); Cloud-Pläne sind sitz-/nutzungsabhängig ([Pricing](https://www.prefect.io/pricing)). | **Longlist, nicht Shortlist. Inferenz:** Gute generische Python-Orchestrierung, aber kein Vorteil gegenüber der bereits vorhandenen LangGraph-Baseline für Agentgraph, Codex-Sessions, Lease und Ereigniskausalität. |
| Windmill | Windmill bietet Workflows, Worker und Agent-Worker; Self-hosting besteht aus Server, PostgreSQL und Workern ([Platform](https://www.windmill.dev/platform), [Self-host](https://www.windmill.dev/docs/advanced/self_host), [Agent Workers](https://www.windmill.dev/docs/core_concepts/agent_workers)). Preise kombinieren je Edition Nutzer, Compute/Worker und gegebenenfalls Enterprise-Funktionen ([Pricing](https://www.windmill.dev/pricing)). | **Longlist, nicht Shortlist. Inferenz:** Stark als generische Ausführungs-/Internal-Tool-Plattform, aber die spezifizierte langlebige Codex-Sitzungs-, Kontroll- und Historiensemantik bliebe anwendungsspezifisch; kein klarer .NET-/Wiederverwendungsvorteil. |
| GitHub Actions / `gh-aw` | `gh-aw` kompiliert Agentic Workflows zu GitHub Actions, unterstützt unter anderem OpenAI Codex und begrenzt Schreiboperationen über Safe Outputs ([Docs](https://github.github.com/gh-aw/), [Architecture/Security](https://github.github.com/gh-aw/introduction/architecture/)). Die Ausführung bleibt das Job-/Workflow-Modell von GitHub Actions ([How they work](https://github.github.com/gh-aw/introduction/how-they-work/)). | **Als Control-Plane-Core ausgeschlossen; als Integrations-/Security-Referenz behalten. Inferenz:** GitHub-Jobs ersetzen keine langlaufende zentrale Mehrbenutzer-Run-Historie, globale Lease oder adressierte Live-Session-Steuerung. |
| Spezialisierte Agent-Control-Planes | Es wurde kein konkreter Anbieter samt Edition, Deploymentmodell, Lizenz und Exportvertrag benannt. | **RFI-Kategorie, nicht scorable.** Mindestnachweise vor Aufnahme: Codex bleibt Harness; stabile Resume/Fork/Interrupt-API; vollständiger Export; Repository-Auth statt eigener ACL; keine verpflichtende Agent-Runtime; prüfbare Datenresidenz, SLA und 3-Jahres-Angebot. |

## Gate-Einschätzung G01–G18

Legende: **N** = nativ/aktuell belegt, **K** = Konfiguration oder dünnes Glue, **E** = substanzieller Eigenbau, **U** = für diese Variante unbewiesen, **X** = widerspricht Produkt-/Betriebsgrenze. Die Bewertung gilt für die **Gesamtlösung**, nicht nur den Frameworkkern. Ein U ist ein Blocker bis zum Spike-Nachweis.

| Gate | A MAKE | B LangGraph+ | C MAF BYO+DTS | D MAF Functions+DTS | E Temporal Core | F Temporal Cloud |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| G01 Codex bleibt Agent-Harness | E | N | E | **U** | E | E |
| G02 zentraler, langlebiger IssueRun | E | E | K | K | K | K |
| G03 Create/Read/Resume/Fork/Stop stabil | **U** | **U** | **U** | **U** | **U** | **U** |
| G04 viele isolierte Activities, gemeinsame History | E | E | N | N | N | N |
| G05 kausale Messages/Tools/Diffs/Tests/Artefakte | E | E | E | E | E | E |
| G06 adressierter Interrupt + durable geordnete Queue | **U** | **U** | **U** | **U** | **U** | **U** |
| G07 Resume/Fork/Fresh Retry unterscheidbar | **U** | **U** | **U** | **U** | **U** | **U** |
| G08 keine doppelten externen Effekte/Adoption | **U** | **U** | **U** | **U** | **U** | **U** |
| G09 genau eine gefencete Control Lease | E | E | E | E | E | E |
| G10 atomarer Transfer/Forced Takeover | E | E | E | E | E | E |
| G11 Repository-Auth, keine eigene ACL | E | E | E | E | E | E |
| G12 Revocations werden aktuell wirksam | E | E | E | E | E | E |
| G13 Redaction vor Persistenz/UI | E | E | E | E | E | E |
| G14 drei unabhängige Reviews desselben Head-SHA | E | N | E | E | E | E |
| G15 reconnectbarer Eventstream ohne Lücken/Duplikate | E | E | E | E | E | E |
| G16 Human- und Service-Identitäten unterscheidbar | E | E | E | E | E | E |
| G17 kein Auto-Merge/-Release/-Self-Approval | K | N | K | K | K | K |
| G18 Export-/Exit-Pfad | E | K | E | E | K | E |

### Begründung der U- und X-Punkte

- **G03/G06/G07 – alle Varianten U:** Kein untersuchter Frameworknachweis deckt die konkrete, stabile Codex-Control-API und die geforderte Semantik von adressierter Unterbrechung, dauerhafter Queue, Resume, Fork und Fresh Retry ab. Der lokale Pilot deckt Teilstrecken ab, aber nicht die zentrale verteilte Variante. Das ist Adapter- und Integrationsevidenz, keine Feature-Checkliste.
- **G08 – alle Varianten U:** LangGraph verlangt idempotente Seiteneffekte ([Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)); Durable Task Activities können wiederholt werden und müssen idempotent sein ([Durable Task Activities](https://github.com/Azure/durabletask/blob/main/docs/concepts/activities.md)); Temporal dokumentiert denselben Crash-Zwischenraum vor dem Completion-Acknowledgement ([Temporal Idempotency](https://docs.temporal.io/activity-definition#idempotency)). Externe Effekt-IDs, Read-before-write/Adoption und Fault-Injection müssen daher anwendungsseitig bewiesen werden.
- **D/G01 – U:** Functions kann langlebige Orchestrierung hosten, aber die Eignung als Host für Codex-Prozesse, veränderliche Git-Worktrees und deren sichere Wiederaufnahme ist nicht belegt. Ein externer Codex-Worker würde das Gate wahrscheinlich lösen, verändert aber die Variante.
- **X:** Es gibt in der realistischen Sechsergruppe derzeit kein belegtes X. Das ist kein positives Auswahlurteil: Vier gemeinsame U-Gates blockieren alle Kandidaten. Bei der spezialisierten SaaS-Longlist würde eine verpflichtende proprietäre Agent-Runtime oder fehlender Voll-Export G01 beziehungsweise G18 zu X machen.

## Nutzwertvorschlag N01–N11 (0–5)

**Wichtig:** Dies ist eine **Desk-Research-Vorbewertung**, kein Spike-Ergebnis. Die Kriterien und Gewichte entsprechen der Entscheidungsvorlage. Gewichtet wird `Gewicht × Punktzahl / 5`; maximal sind 100 Punkte. Halbe Punkte sind zulässig. Gate-Verletzungen werden durch den Score nicht geheilt.

| Kriterium | Gewicht | A MAKE | B LangGraph+ | C MAF BYO+DTS | D MAF Functions+DTS | E Temporal Core | F Temporal Cloud |
|---|---:|---:|---:|---:|---:|---:|---:|
| N01 fachliche Spec-Abdeckung | 18 | 4 | 4 | 4 | 4 | 3 | 3 |
| N02 Durable Correctness/Recovery | 12 | 2 | 3 | 4 | 4 | 5 | 5 |
| N03 Codex-/Session-Integration | 10 | 3 | 4 | 4 | 3 | 4 | 4 |
| N04 Observability/Run History | 10 | 3 | 4 | 4 | 4 | 4 | 4 |
| N05 menschliche Remote-Steuerung | 8 | 3 | 2 | 3 | 3 | 4 | 4 |
| N06 Security/Datenschutz/Audit | 10 | 3 | 4 | 4 | 4 | 4 | 4 |
| N07 Erweiterbarkeit/Providerneutralität | 7 | 5 | 3 | 4 | 4 | 4 | 4 |
| N08 Betrieb/Reife/Team-Fit/Support | 7 | 2 | 3 | 3,5 | 3 | 3 | 4 |
| N09 Time-to-Value | 5 | 1 | 5 | 4 | 3 | 2 | 3 |
| N10 Drei-Jahres-TCO | 8 | 1 | 3 | 3 | 3 | 2 | 3 |
| N11 Lock-in/Reversibilität | 5 | 5 | 4 | 3 | 2 | 3 | 2 |
| **Gewichtetes Ergebnis / 100** | **100** | **59,4** | **71,0** | **75,1** | **70,4** | **71,2** | **74,2** |

**Inferenz zu den Ergebnissen:** MAF BYO+DTS liegt in der an der Entscheidungsvorlage ausgerichteten Bewertung knapp vor Temporal Cloud. Der Abstand von 0,9 Punkten liegt deutlich unter der Schätzunsicherheit. C wird deshalb nicht aufgrund einer scheinpräzisen Rangzahl, sondern wegen .NET-Team-Fit und erwarteter Time-to-Value zuerst gespikt; F bleibt der stärkere Reife-/Durable-Benchmark. Ein einzelner nicht bestandener kritischer Gate-Test schlägt jeden Nutzwertvorteil.

Kurzbegründung der Profile:

- **A MAKE:** maximale Gestaltungsfreiheit und Portabilität, aber schwächste belastbare Durable-Baseline, längste Zeit bis Produktionsreife und höchste versteckte Engineering-TCO.
- **B LangGraph+:** größter Wiederverwendungs- und Time-to-Value-Vorteil; Abzüge für Python-Teamfit, Zentralisierungsarbeit und den noch lokalen SQLite-Ausgangspunkt.
- **C MAF BYO+DTS:** beste Kombination aus .NET, Agent-/Workflowmodell und kontrollierbarem Worker-Hosting; Abzüge für Preview-Lifecycle, Azure-Scheduler-Abhängigkeit und unbewiesene Codex-/Eventsemantik.
- **D MAF Functions+DTS:** weniger Compute-Betrieb, aber zusätzliche Plattformgrenzen für Codex/Git und höherer Lock-in.
- **E Temporal Core:** sehr starke Durable-Primitiven und volle Datenkontrolle; Abzüge für Servicebetrieb und weil Agent-/Operator-Domäne vollständig selbst entsteht.
- **F Temporal Cloud:** stärkste risikoarme Durable-Service-Baseline und kein Clusterbetrieb; Abzüge für SaaS-/Preismodell, Daten-/Exit-Prüfung und unverändert großen fachlichen Eigenbau.

## TCO-Treiber und fehlende Eingaben

### Gemeinsames Mengengerüst, das noch fehlt

- Runs pro Monat und pro Peak-Stunde; Activities/Versuche, Signale, Events und Timer je Run.
- Durchschnittliche und P95/P99-Laufzeit einer Codex-Activity, Speicher/CPU, Parallelität und Warmhaltebedarf.
- Aktive History- und Retention-Dauer; Event-, Diff-, Log- und Artefaktvolumen; Egress und Regionen.
- Zahl der Umgebungen, Mandanten/Repos und tatsächlichen Operator-Nutzer; 20 Nutzer allein reichen nicht für eine Verbrauchsschätzung.
- Verfügbarkeitsziel, RTO/RPO, Supportklasse, Datenresidenz, Private Networking, SSO/SCIM und Audit-Anforderungen.
- Vollkostensatz und verfügbare Personentage für .NET, Python, Plattform/SRE, Security und 24/7-Bereitschaft.
- Codex-/Modellnutzung ist separat zu kalkulieren und in weiten Teilen kandidatengleich; nur zusätzliche Agent-/Review-Aufrufe zählen als differenzierender TCO-Treiber.

### Formeln statt Scheingenauigkeit

- **A MAKE:** Entwicklungs- und Testtage + DB/Queue/Object Store/Compute/Observability + Backup/DR/On-call + laufende Weiterentwicklung.
- **B LangGraph+:** Zentralisierungs- und Migrationsaufwand + Python-Worker + Produktions-Checkpoint-DB/Queue + API/UI/Event Store + Betrieb; optional LangSmith separat.
- **C MAF BYO+DTS:** DTS Consumption-Aktionen **oder** Dedicated-CUs + BYO-Worker + Redis-Response-Store + App-DB/Object Store + Observability + Preview-/Upgrade-Risiko.
- **D MAF Functions+DTS:** DTS + Functions-Ausführungen/GB-s/Always Ready + Storage/Redis/App Insights + gegebenenfalls separate Codex-Worker.
- **E Temporal Core:** Temporal-Service-Compute + PostgreSQL + Visibility Store + Backups/DR/Upgrades/On-call + App-/Codex-Worker + Object Store/API/UI.
- **F Temporal Cloud:** Plan Fee + Actions + Active/Retained Storage + Support/Add-ons/Netzwerk + App-/Codex-Worker + Object Store/API/UI.

Benötigt werden daher Azure-Regionstarife und gegebenenfalls ein DTS-/Functions-Angebot, ein Temporal-Cloud-Angebot mit den geforderten Enterprise-/Security-Eigenschaften sowie eine intern abgestimmte Vollkostenrechnung. Vorher ist ein Drei-Jahres-TCO nur „offen“, nicht „günstig“ oder „teuer“.

## Risiken, Evidence-Lücken und konkrete Spike-Fragen

### Kandidatenübergreifende Nachweise

1. Kann ein vollständiger Pilot-Run als ein IssueRun mit mehreren isolierten Codex-Activities ausgeführt werden, ohne Codex als Agent-Harness zu ersetzen?
2. Sind `create`, `read`, `resume`, `fork`, `fresh retry` und `stop` mit stabilen IDs und nach Prozess-/Worker-Neustart beobachtbar verschieden?
3. Erreicht ein Interrupt genau die adressierte aktive Sitzung; bleiben nachfolgende Eingaben dauerhaft, geordnet und genau einmal konsumierbar?
4. Was geschieht bei Crash jeweils **vor** externem Effekt, **nach** Effekt aber vor Acknowledgement und **nach** Acknowledgement? Werden vorhandener Branch, Commit, PR, Kommentar und Review sicher adoptiert statt dupliziert?
5. Kann ein zweiter Operator eine Lease per CAS übernehmen; wird der alte Controller durch Fencing sicher abgewiesen? Ist Forced Takeover atomar und auditierbar?
6. Liefert Reconnect ab Cursor unter Parallelität, Failover und Retention eine lückenlose, deduplizierbare Eventfolge?
7. Werden Secrets und sensible Toolausgaben vor jeder dauerhaften Framework-, Log-, Event- und UI-Persistenz redigiert?
8. Werden Repository-Berechtigungsentzug und Rollenänderung ohne veraltete lokale ACL wirksam?
9. Sind drei Reviews nachweislich unabhängige Fresh Sessions auf exakt demselben Head-SHA, und bleibt Auto-Merge/-Release technisch gesperrt?
10. Kann ein Run samt Domain Events, Frameworkhistory, Sessiongraph, Prompts/Antworten, Tooldaten, Diffs, Tests und Artefakten exportiert und in ein neutrales Format rekonstruiert werden?

### MAF/DTS-spezifisch

- Lässt sich Codex als eigener `AIAgent`-/Executor-Adapter betreiben, ohne dass MAFs Conversation State zur kanonischen IssueRun-History wird?
- Bleiben Run-, Event- und Artefaktpayloads außerhalb der 1-MB-Durable-Entity-Grenze; welche IDs statt Payloads werden checkpointed?
- Ist Redis-Callback-Streaming nur Livekomfort oder kann es die G15-Cursorsemantik tragen? Wahrscheinlich braucht G15 einen separaten transaktionalen Event Store.
- Überstehen Checkpoints einen Upgradepfad von der Preview- auf die GA-Version; welche Replay-/Schema-Kompatibilitätszusage gilt tatsächlich?
- Reichen DTS-Retention und Export für Recovery, während langfristiger Auditverlauf separat gehalten wird?
- Können BYO Worker lokale/ephemere Worktrees sicher bereitstellen, aufräumen und nach Crash adoptieren?

### Azure-Functions-spezifisch

- Kann der Codex/Git-Teil unter Scale-in, Deployment und read-only App-Package zuverlässig laufen? Wenn nicht: klare Trennung zwischen Functions-Orchestrierung und dedizierten Codex-Workern testen und neu bepreisen.
- Welche Kosten verursachen Always Ready, lange Ausführungen, Storage Mounts, Redis und Application Insights unter realistischem Lastprofil?

### Temporal-spezifisch

- Wie werden IssueRun und Sessiongraph auf Workflow, Child Workflows, Activities, Signals und Updates abgebildet, ohne unbeherrschbare History-Größe?
- Welche Heartbeat-, Cancellation- und Async-Completion-Semantik ist für lange Codex-Prozesse robust?
- Wie werden Activity-ID/Effect-ID, Adoption und Retry bei GitHub/Git in einem Fault-Injection-Test umgesetzt?
- Welche Worker-Versioning-/Deploymentregeln gelten für monatelang offene Runs?
- Reicht Temporal Visibility nur als Betriebsindex, während eine eigene fachliche Eventprojektion G05/G15/G18 erfüllt?
- Für Cloud: Datenresidenz, Verschlüsselung, Private Connectivity, SLA, Support und vollständiger History-Export vertraglich prüfen.

### LangGraph- und MAKE-spezifisch

- **LangGraph:** produktionsfähigen Checkpointer, verteilte Claim-/Worker-Konkurrenz, Single Writer/Fencing, Multi-Instance-Failover und SSE/WebSocket-Cursor unter Last beweisen; Migrationspfad vom SQLite-Piloten messen.
- **MAKE:** nur als timeboxter Thin-Core-Gegenversuch zulassen. Derselbe Fault-Injection- und Session-Semantik-Test muss eine belastbare Aufwandsschätzung liefern; ein Happy Path rechtfertigt keinen Eigenbau.

## Vorläufige Empfehlung und Entscheidungsregel

1. **MAF BYO Compute + DTS erhält den nächsten lokalen Spike**, wie in [ADR 0008](../../docs/adr/0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md) vorgesehen. Der Spike muss sich am vorhandenen LangGraph-Verhalten messen und insbesondere G03/G06/G07/G08 plus Event-/State-Separation prüfen.
2. **MAF gewinnt die Make-or-Buy-Entscheidung nur dann**, wenn der Spike alle Gates ohne Framework-Fork besteht, Codex Harness bleibt, Durable State klar von Domain Events/Artefakten getrennt wird, Upgrade/GA-Pfad vertretbar ist und der geschätzte Eigenbau für Lease, Security, Operator und Eventpfad nicht annähernd einem eigenen Workflow-Core entspricht. Für Produktion sollte mindestens der tatsächliche GA-Stand und nicht nur ein geplantes Datum bewertet werden.
3. **Temporal Cloud wird bevorzugt**, wenn MAFs Durable Extension nach GA weiterhin kritische Lifecycle-/Replay-/Streaming-Lücken zeigt, Fault Injection nicht sauber besteht oder ein belastbarer Temporal-Vertrag das Betriebs- und Compliance-Risiko deutlich senkt. Temporal ist dann Durable Backbone; Codex-, Domain- und Operator-Schicht bleiben bewusst eigene .NET-Module.
4. **Temporal Core self-hosted wird nur bevorzugt**, wenn Daten-/Souveränitätsvorgaben Temporal Cloud oder Azure DTS ausschließen und der laufende Servicebetrieb personell sowie finanziell belegt ist.
5. **LangGraph+ wird bevorzugt**, wenn kurzfristiger Nutzen und Wiederverwendung wichtiger sind als die .NET-Konsolidierung, der zentrale Produktionsausbau die U-Gates im Spike besteht und die Migration zu MAF/Temporal keinen belegbaren Risiko-/TCO-Vorteil bringt. Es ist die Referenz- und Rückfalloption, kein bloßes Wegwerfartefakt.
6. **Vollständiger MAKE-Core wird nur wieder geöffnet**, wenn sowohl MAF/DTS als auch Temporal an einem harten Gate oder einer nicht akzeptablen Vertrags-/Souveränitätsgrenze scheitern. Dann muss der Eigenbau als Produkt mit eigener Roadmap, Security- und Betriebsbudget bewertet werden.

Damit ist die Annahme „MAF ist für einen .NET-Entwickler zu bevorzugen, wenn es LangGraph fachlich und Temporal durable gleichwertig abdeckt“ als **plausible, aber noch unbewiesene Entscheidungsregel** verankert. Die Primärquellen belegen die Bausteine; erst der fokussierte Spike belegt ihre Gleichwertigkeit für diese Spec.
