**Date:** 2026-05-07  
**Status:** 🟢 Accepted  
**Scope:** Tech-Stack-Entscheidung fuer Agent-/Skill-Testframeworks der DocWorkflow Agent Delivery Testsuite.

---

## Review Control Surface

- Spec-Variante: ADR / Tech Stack Evaluation.
- Goldstandard Status: candidate.
- Ziel: Ein bestehendes Agent-/Eval-Testframework als bevorzugten Rahmen fuer die spaetere Testsuite-Implementierung festlegen und diese Empfehlung durch einen einmaligen Pre-Implementation-Spike validierbar machen, damit kein eigenes Testing Framework from scratch entsteht.
- In Scope: Framework-Vergleich fuer Skill-Unit-, Skill-Chain-/Teil-E2E-, Style-/Usability- und Efficiency-/Telemetry-Gates.
- Out of Scope: Implementierungsplan, konkrete Testdateien, Runner-Kommandos, CI-Integration.
- Wichtigste Test-/Harness-Cases: Codex-/Coding-Agent-Skill-Unit-Tests, Parent/Child-Skill-Chain-Tests, agent-output-basierte Style- und Efficiency-Gates.
- Wichtigste Verification Commands: Werden im `DWT-S0` Promptfoo-first Spike geplant und als Re-Evaluation-Artefakt dokumentiert, bevor wiederholbare Testsuite-Implementierung startet.
- Offene Entscheidungen: Keine blockierende Framework-Entscheidung offen. Promptfoo wird als primaerer Agent-/Coding-Agent-Eval-Rahmen empfohlen und muss vor der Testsuite-Implementierung durch einen einmaligen Spike validiert werden; Inspect AI bleibt strategischer Fallback/Ergaenzungskandidat.
- Readiness Status: Accepted after `DWT-S0` spike evidence; Promptfoo remains primary with documented limitations.

## 1. Kontext

Die DocWorkflow Agent Delivery Testsuite soll nicht als eigenes Testing Framework neu gebaut werden. Sie braucht aber mehr als klassische Shell-Smoke-Checks:

- Skill-Unit-Tests: ein Skill, ein Input-Fixture, erwarteter Output.
- Skill-Chain-/Teil-E2E-Tests: mehrere Skills in definierter Reihenfolge mit Artefaktuebergabe.
- Style-/Usability-Gates: Output muss fuer User und Folgeskill nutzbar sein.
- Efficiency-/Telemetry-Gates: Tool-/Command-/Read-Verhalten darf nicht ausufern.
- Testisolation: keine Originalspecs oder echten Runtime-Repos veraendern.

Die Framework-Recherche wurde am 2026-05-07 anhand offizieller Dokumentation durchgefuehrt.

## 2. Bewertungs-Kriterien

| Kriterium | Gewicht | Bedeutung |
|---|---:|---|
| Codex-/Coding-Agent-Anbindung | hoch | Kann das Framework Codex/Coding-Agent-Laeufe direkt oder mit wenig Adapter testen? |
| Skill-Unit- und Chain-Faehigkeit | hoch | Lassen sich einzelne Skills und Skill-Folgen mit Fixtures und erwarteten Artefakten pruefen? |
| Tool-/Trace-/Telemetry-Sichtbarkeit | hoch | Lassen sich Tool Calls, Datei-/Command-Verhalten, Kosten/Token/Iterationsdaten oder Traces pruefen? |
| Testisolation | hoch | Unterstuetzt es Temp-Workspaces, Sandboxes oder klare Runtime-Grenzen? |
| Deterministische Assertions | hoch | Erlaubt es strukturierte Assertions statt nur LLM-as-Judge? |
| CI-/lokale Reproduzierbarkeit | mittel | Kann es lokal und in CI mit wiederholbaren Reports laufen? |
| Framework-Reife / Wartbarkeit | mittel | Dokumentation, Beispiele, aktive Nutzung, Integrationsmodell. |
| .NET-Kompatibilitaet | niedrig-mittel | Muss nicht .NET-native sein, soll aber mit .NET-Hilfsvalidatoren kombinierbar sein. |

## 3. Kandidaten

### Promptfoo

Offizielle Dokumentation beschreibt Promptfoo explizit fuer Coding-Agent-Evals, inklusive OpenAI Codex SDK, OpenAI Codex app-server, Claude Agent SDK und OpenCode SDK. Die Docs betonen, dass Agent-Evals ein System mit Zwischenschritten testen, nicht nur Input -> Output, und dass Intermediate Steps, Tool-Entscheidungen, File Reads, Command Runs, Side Effects und Runtime Boundary relevant sind. Promptfoo dokumentiert auch Capability-Tiers fuer Coding Agents und nennt Codex app-server/Desktop als Rich-Client-Protokollpfad.

Eignung:

- sehr starke Passung fuer Codex-/Coding-Agent-Evals,
- geeignet fuer Skill-Unit- und Chain-Tests, sofern Skills ueber Codex SDK/app-server oder Provider-Adapter ausgefuehrt werden koennen,
- unterstuetzt strukturierte Outputs, Assertions, Provider-Vergleiche und Coding-Agent-Sicherheits-/Red-Team-Szenarien,
- passt zu Testisolation, weil Coding-Agent-Provider explizite Working Directories, Sandboxes oder Read-only-Default-Postures beschreiben.

Risiken:

- Codex app-server/Desktop-Protokoll wird in der Promptfoo-Doku als experimenteller bzw. Rich-Client-Pfad beschrieben; ein erster Spike muss pruefen, ob unsere Codex Desktop/Skill-Konstellation stabil erreichbar ist.
- Node/JS-Oekosystem, nicht .NET-native. .NET 10 bleibt deshalb eher fuer deterministic validators und Fixture-Hilfen relevant.

Quellen:

- [Promptfoo: Evaluate Coding Agents](https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/)
- [Promptfoo: OpenAI Codex SDK provider](https://www.promptfoo.dev/docs/providers/openai-codex-sdk/)

### Inspect AI

Inspect AI ist ein open-source Framework fuer LLM-Evaluations vom UK AI Security Institute. Die Doku nennt Coding, agentic tasks, tool calling, MCP/custom tools, built-in bash/python/text-editing/web tools, sandboxing und Agent-Evaluations. Relevant ist besonders, dass Inspect laut Doku externe Agents wie Claude Code, Codex CLI und Gemini CLI unterstuetzt.

Eignung:

- stark fuer allgemeine Agent-Evals, Sandbox-/Tool-Use und reproduzierbare Logs,
- gute Architekturbegriffe: Datasets, Solvers, Scorers, Logs, Sandboxing,
- kann fuer breitere Agent-/Skill-Evals relevant werden, wenn Promptfoo/Codex-app-server nicht stabil genug ist oder wenn wir externe Codex-CLI-Laeufe testen wollen.

Risiken:

- weniger direkt auf Codex Desktop Skills/App-Server ausgerichtet als Promptfoo,
- Python-first, nicht .NET-native,
- konkrete Skill-Anbindung muss im Plan/Spike geklaert werden.

Quelle:

- [Inspect AI documentation](https://inspect.aisi.org.uk/)

### mcp-eval

mcp-eval ist ein Eval-Framework fuer MCP-Server und MCP-Agenten. Die Doku beschreibt decorator tasks, pytest suites, datasets, structured expectations, Tool-Call-Assertions, Performance-Checks, Telemetry und JSON/Markdown/HTML-Reports.

Eignung:

- sehr stark, wenn unsere Skills oder Workflow-Komponenten als MCP-Server/Agenten modelliert werden,
- gute Passung fuer Tool-Reihenfolge, Tool-Payloads, Performance und Reports,
- pytest-Anschluss passt gut zu klassischer Testdenke.

Risiken:

- Hauptziel ist MCP. Unsere aktuelle Testsuite testet Codex Skills und lokale Spec-Artefakte, nicht primaer MCP-Server.
- Als Primaerframework wuerde es vermutlich erfordern, dass wir den Workflow erst als MCP-App/Agent-Spec modellieren.

Quelle:

- [mcp-eval documentation](https://docs.mcp-agent.com/test-evaluate/mcp-eval)

### OpenAI Agent Evals / OpenAI Evals

OpenAI Agent Evals bieten traces, graders, datasets und eval runs fuer Agent Workflows. Die Doku beschreibt Trace-Grading als Weg, workflow-level model calls, tool calls, guardrails und handoffs zu bewerten.

Eignung:

- relevant fuer OpenAI-native Agent Workflows und Trace-/Grader-basierte Evaluation,
- guter konzeptioneller Rahmen fuer Trace-Grading, Datasets und Regressionen,
- kann spaeter fuer OpenAI Agents SDK Workflows oder Plattform-Evals wichtig werden.

Risiken:

- Nicht offensichtlich der direkteste lokale Harness fuer Codex Desktop Skills und lokale Spec-Fixtures.
- Plattformgebundener als ein rein lokaler Framework-Runner.

Quelle:

- [OpenAI: Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)

### DeepEval

DeepEval ist ein open-source LLM-Evaluation-Framework mit Test Cases, Datasets, Metrics, Traces und Agent-/Component-Level-Evals. Die Doku beschreibt End-to-End- und Component-Level-Evals und ist gut geeignet fuer LLM-App-Qualitaet.

Eignung:

- gut fuer pytest-artige LLM-/Agent-Komponententests,
- gut fuer Qualitaetsmetriken und LLM-as-Judge,
- potenziell hilfreich fuer Style-/Usability-Gates.

Risiken:

- Weniger spezifisch fuer Codex/Coding-Agent-Harnesses als Promptfoo,
- weniger klarer Fit fuer File-System-/Command-/Skill-Trajectory-Pruefung.

Quelle:

- [DeepEval documentation](https://deepeval.com/docs/introduction)

### LangSmith

LangSmith fokussiert Evaluations, Datasets, Experiments, Traces, Offline-/Online-Evaluation und Vergleiche ueber Experiments. Die Doku nennt fuer Agents Beispiele wie korrekte Tool-Auswahl, Argumentformatierung und Trajectory. Offline-Evals koennen Unit-/Regression-/Benchmarking leisten; Online-Evals nutzen Produktions-Runs/Threads.

Eignung:

- stark fuer Observability, Trace Review, Datasets und langfristige Qualitaetsentwicklung,
- gut fuer Teams, die LangChain/LangGraph-nah arbeiten.

Risiken:

- Plattform-/SDK-/Tracing-Integration statt unmittelbarer lokaler Codex-Skill-Harness,
- wahrscheinlich eher Observability-/Reporting-Ergaenzung als Primaerframework fuer diese lokale Testsuite.

Quelle:

- [LangSmith Evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts)

### Braintrust

Braintrust unterstuetzt systematische AI-Evaluation, Experiments, CI/CD, Scorers, Online Scoring und kann Tasks als LLM call, multi-step agent, retrieval pipeline oder custom workflow behandeln.

Eignung:

- stark fuer systematische Experiments, Regressionen und CI/CD,
- gut fuer Plattform- und Team-Workflow.

Risiken:

- Plattformlastiger als unser lokaler Spec-/Fixture-Harness,
- weniger direkt auf Codex Desktop Skills und lokale Parent/Child-Spec-Artefakte zugeschnitten.

Quelle:

- [Braintrust: Evaluate systematically](https://www.braintrust.dev/docs/evaluate)

### Langfuse

Langfuse bietet Evaluation ueber Observations, Traces und Experiments sowie LLM-as-Judge. Die Doku unterscheidet Produktionsbeobachtung, Trace-/Observation-Level-Evals und kontrollierte Experimente.

Eignung:

- stark fuer Observability, Live-/Trace-Evaluation und LLM-as-Judge,
- gut als spaetere Telemetry-/Monitoring-Ergaenzung.

Risiken:

- Nicht primaer ein lokaler Coding-Agent-Test-Harness,
- eher Ergaenzung fuer Trace-/Observation-Auswertung als Rahmen fuer Skill-Unit-Tests.

Quelle:

- [Langfuse: LLM-as-a-Judge](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge)

## 4. Entscheidung

**Entscheidung:** Promptfoo wird als primaeres Framework fuer die spaetere L2-Agent-/Coding-Agent-Eval-Implementierung der DocWorkflow Agent Delivery Testsuite empfohlen und als erster Implementierungspfad festgelegt.

Diese Entscheidung ist bewusst **spike-validiert**: Sie gilt als fuehrende Empfehlung, bis ein einmaliger Promptfoo-first Pre-Implementation-Spike belegt, dass die Codex-Skill-/Desktop-Anbindung stabil, isoliert und reproduzierbar genug ist. Der Spike darf die Empfehlung bestaetigen, einschraenken oder ersetzen.

**Begruendung:**

1. Es ist der einzige evaluierte Kandidat mit expliziter, aktueller Dokumentation fuer OpenAI Codex SDK und Codex app-server/Desktop als Coding-Agent-Eval-Targets.
2. Es adressiert genau die fuer uns wichtigen Unterschiede zwischen normaler LLM-Evaluation und Agent-Evaluation: Zwischenschritte, File Reads, Command Runs, Side Effects, Runtime Boundary und Tool-/Trace-Verhalten.
3. Es passt zu Skill-Unit- und Skill-Chain-Evals, sofern wir die Skills ueber Codex SDK/app-server oder einen Provider-Adapter stabil ausfuehren koennen.
4. Es verhindert, dass wir ein eigenes Agent-Testframework from scratch bauen.

**Sekundaere Entscheidung:** Inspect AI wird als strategischer Fallback und Ergaenzungskandidat festgehalten, besonders fuer Sandbox-/Tool-Use-/External-Agent-Evals, falls Promptfoo die Codex-Skill-/Desktop-Anbindung nicht stabil genug abdeckt.

**Spezialisierte Entscheidung:** mcp-eval wird nicht als Primaerframework gewaehlt, bleibt aber die bevorzugte Option fuer zukuenftige MCP-spezifische Tests, falls DocWorkflow-Komponenten als MCP-Server oder MCP-Agenten modelliert werden.

**Nicht primaer gewaehlt:** OpenAI Agent Evals, DeepEval, LangSmith, Braintrust und Langfuse werden nicht als primaerer lokaler Harness festgelegt. Sie bleiben relevant als konzeptionelle oder spaetere Plattform-/Observability-/LLM-Judge-Ergaenzungen.

## 5. Pre-Implementation Spike und Re-Evaluation Gate

Vor der eigentlichen Testsuite-Implementierung muss ein einmaliger Promptfoo-first Validierungs-Spike durchgefuehrt werden. Dieser Spike ist **kein Testsuite-Testcase** und darf spaeter nicht Teil des regulaeren Regression-Laufs werden. Er prueft als Vorbedingung, ob die Framework-Entscheidung tragfaehig ist oder ob Plan und ADR angepasst werden muessen.

Der Spike muss mindestens beantworten:

1. Kann Promptfoo in dieser Umgebung einen Codex-/Coding-Agent-Lauf starten, ohne Originalspecs oder Runtime-Repos zu veraendern?
2. Kann der Lauf einen Skill-Unit- oder Skill-aehnlichen Prompt gegen ein isoliertes Fixture ausfuehren?
3. Lassen sich Agent-Output, Tool-/Command-/Trace- oder Provider-Metadaten als Evidence speichern?
4. Lassen sich deterministische Assertions gegen Output und Artefakte auswerten?
5. Laeuft der Spike wiederholbar genug, um als lokaler oder CI-naher Harness-Kandidat zu gelten?
6. Sind Isolation, Kosten-/Token-/Command-Sichtbarkeit und Fehlerdiagnose ausreichend fuer die Testsuite-Ziele?

Der Spike muss ein Re-Evaluation-Artefakt erzeugen, das die ADR nach Auswertung in einen der folgenden Zustaende bringt:

| Ergebnis | Bedeutung |
|---|---|
| `ADOPT_PROMPTFOO` | Promptfoo bleibt primaerer Rahmen; Planung kann auf Promptfoo aufbauen. |
| `ADOPT_WITH_LIMITATIONS` | Promptfoo bleibt primaer, aber nur fuer klar benannte Testlevel/Testarten; Luecken brauchen Validatoren oder Fallbacks. |
| `FALLBACK_TO_INSPECT` | Promptfoo blockiert wesentliche Ziele; Inspect AI wird als naechster Spike-/Implementierungspfad aktiviert. |
| `REOPEN_EVALUATION` | Weder Promptfoo noch Inspect AI passen ohne unvertretbare Workarounds; Framework-Auswahl wird neu bewertet. |

Workarounds muessen im Spike sichtbar bewertet werden. Ein gruener Spike ist nicht ausreichend, wenn er Codex-Skill-Ausfuehrung, Isolation, Tracebarkeit oder deterministische Assertions durch manuelle Schritte, statische Fake-Outputs oder nicht reproduzierbare Umgehungen ersetzt.

## 6. DWT-S0 Re-Evaluation Result

**Result:** `ADOPT_WITH_LIMITATIONS`

**Evidence:** `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/spike-summary.json`
**Closeout Evidence:** `tests/docworkflow-agent-delivery/spikes/dwt-s0/evidence/closeout-verification.txt`
**OpenSpec Archive:** `openspec/changes/archive/2026-05-07-docworkflow-agent-testsuite-dwt-s0-framework-spike/`

Der DWT-S0 Spike hat Promptfoo `0.121.9` mit gebuendeltem Node `v24.14.0`, isoliertem `HOME` und isoliertem `npm_config_cache` ausgefuehrt. `promptfoo debug` und `promptfoo validate config` liefen erfolgreich. Der Codex-SDK-Provider `openai:codex-sdk:gpt-5.5` konnte gegen die isolierte Fixture `tests/docworkflow-agent-delivery/spikes/dwt-s0/fixtures/workspace` laufen und lieferte einen gespeicherten Runner-Output mit bestandenem Promptfoo-Assertion-Set.

Promptfoo bleibt damit der primaere Rahmen fuer die naechsten Agent-/Coding-Agent-Evals. Die Adoption ist eingeschraenkt durch drei betriebliche Grenzen:

- Codex SDK braucht ein explizit provisioniertes `CODEX_HOME` oder gleichwertige Credentials; ein leeres isoliertes `CODEX_HOME` erzeugte reproduzierbar `401 Unauthorized`.
- Isolierte `npx`-/npm-Paketaufloesung haengt an stabiler Registry-/Internetverbindung; ein Closeout-Replay erzeugte bei intermittierender Verbindung `ETIMEDOUT`, die Wiederholung lief danach durch.
- Validiert wurde der Codex-SDK-Pfad, nicht der Codex Desktop/app-server-Pfad.

Der Spike nutzte keine manuellen Ersatzschritte, keine statischen Fake-Outputs und keine versteckten Normalisierungen. Promptfoo stellt fuer den erfolgreichen Lauf Command-Ausfuehrung, Command-Output, Session-ID, Token-Usage, Kosten und Assertion-Ergebnisse als Evidence bereit.

## 7. Anforderungen an die Testsuite-Spec

Die Testsuite-Spec muss nach dieser ADR festschreiben:

1. Die spaetere Implementierungsplanung muss mit Promptfoo als primaerem Agent-/Coding-Agent-Eval-Framework starten.
2. Ein einmaliger Pre-Implementation-Spike muss pruefen, ob Promptfoo unsere Codex-Skill-Ausfuehrung ueber OpenAI Codex SDK, Codex app-server/Desktop oder einen Adapter stabil, isoliert und reproduzierbar treiben kann.
3. Wenn dieser Spike blockiert, ist Inspect AI der erste Fallback fuer Agent-/Sandbox-/External-Agent-Evals.
4. Deterministische Artefaktpruefungen, Fixture-Checks und bestehende Validatoren duerfen ausserhalb von Promptfoo bleiben, muessen aber in das Reporting/Evidence-Modell der Testsuite integrierbar sein.
5. Kein eigenes generisches Agent-Testframework darf gebaut werden, bevor Promptfoo und Inspect AI als ungeeignet dokumentiert sind.
6. Nach dem Spike muss diese ADR explizit re-evaluiert und mit einem der Re-Evaluation-Ergebnisse aus Abschnitt 5 fortgeschrieben werden.

## 8. Konsequenzen

- Die Planungsphase muss keine offene Framework-Recherche mehr starten, sondern einen Promptfoo-first Pre-Implementation-Spike als Vorbedingung planen und durchfuehren.
- Promptfoo ist nicht als unwiderrufliche Tool-Wahl gesetzt; der Spike ist das Evidence-Gate fuer die endgueltige Uebernahme.
- .NET 10 file-based Apps bleiben als kleine deterministische Hilfsvalidatoren erlaubt, aber nicht als Primaer-Agent-Eval-Framework festgelegt.
- Style- und Efficiency-Gates muessen so formuliert werden, dass sie entweder in Promptfoo-Assertions/Provider-Telemetry oder in nachgelagerten deterministischen Validators laufen koennen.
- Testisolation bleibt zwingend: Temp-Fixtures, read-only Source-Fixtures, gespeicherte Agent-Outputs, maschinenlesbare Evidence.

## 9. History

| Date | Author | Change |
|------|--------|--------|
| 2026-05-07 | Codex | Initiale Framework-Evaluation erstellt und Promptfoo als primaeres Agent-/Coding-Agent-Eval-Framework festgelegt. |
| 2026-05-07 | Codex | Promptfoo-Entscheidung als spike-validierte Empfehlung geschaerft und Re-Evaluation-Gate fuer die Testsuite ergaenzt. |
| 2026-05-07 | Codex | Spike als einmalige Pre-Implementation-Vorbedingung statt regulaerem Testsuite-Testcase klargestellt. |
| 2026-05-07 | Codex | ADR-Bezug mit Testsuite-Child-Slice `DWT-S0` synchronisiert und final adoption explizit an Spike-Evidence gebunden. |
| 2026-05-07 | Codex | DWT-S0 Spike mit `ADOPT_WITH_LIMITATIONS` re-evaluiert und Promptfoo als primaeren Rahmen mit Auth-/Cache-Limitierungen bestaetigt. |
| 2026-05-07 | Codex | DWT-S0 akzeptiert, Closeout-Verifikation replayed und OpenSpec-Change archiviert. |

SessionId: 2026-05-07-docworkflow-agent-test-framework-evaluation
