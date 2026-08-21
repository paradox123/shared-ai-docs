# LangGraph GitHub Issue Implementation Pilot

Status: ready-for-agent

## Problem Statement

Daniel verwaltet ausgereifte Anforderungen und PRDs bereits als GitHub Issues mit Parent-/Child-Beziehungen, Abhaengigkeiten und dem Zustand `ready-for-agent`. Die anschliessende Implementierung erfordert heute dennoch wiederholte manuelle Agentenstarts, Kontextuebergaben, Verifikationslaeufe und Review-Koordination. Dadurch bleibt Daniel selbst die Control Plane fuer Arbeit, die nach der fachlichen Freigabe weitgehend deterministisch orchestriert werden kann.

Ein einfacher Code-Agent reicht fuer diese Aufgabe nicht aus. Der Workflow muss das vorhandene Arbeitsmandat respektieren, Abhaengigkeiten und Repository-Grenzen einhalten, Implementierungen nach Unterbrechungen fortsetzen, Anforderungen nachweisbar erfuellen, mehrere unabhaengige Review-Perspektiven zusammenfuehren und nur bei echten Produktentscheidungen oder nicht agentisch loesbaren Blockaden zu Daniel zurueckkehren. Ein gestarteter Container, ein erfolgreicher Build oder ein Healthcheck beweist dabei nicht, dass eine Anforderung fachlich funktioniert.

Daniel benoetigt deshalb einen lokalen, persistenten und GitHub-gesteuerten Implementierungsworkflow, der freigegebene Issues autonom bis zu einem verifizierten Pull Request bearbeitet, ohne selbst zu mergen, zu deployen oder fachliche Produktentscheidungen zu erfinden.

## Solution

Ein lokaler LangGraph-Workflow bildet die persistente Control Plane fuer GitHub-Issue-Implementierungen. `probare-crm` ist das erste Pilotrepository. Im Normalbetrieb startet oder aktualisiert ein signiertes GitHub-Webhook-Ereignis den zugehoerigen Lauf. Eine kostenlose Cloudflare Queue puffert gueltige Ereignisse fuer bis zu 24 Stunden; nach einer laengeren lokalen Inaktivitaet fuehrt der Mac beim naechsten Start genau einen idempotenten GitHub-Reconciliation-Lauf aus.

`ready-for-agent` ist Reifezustand und Implementierungsfreigabe zugleich. Der Workflow darf das Label auch selbst setzen, wenn ein Issue nachweisbar aus einem von Daniel angestossenen Issue, einer verlinkten PRD oder einem vergleichbaren Arbeitsmandat abgeleitet wurde. Pro Repository wird nur ein Issue gleichzeitig implementiert; offene `Blocked by`-Beziehungen verhindern den Start.

LangGraph startet fuer fachliche Arbeit nicht-interaktive Codex-Worker in isolierten Worktrees und weist ihnen die vorhandenen Matt-Pocock-Skills zu. Implementierung, deterministische Verifikation, Requirements Review, Code Review und Architektur Review bilden einen wiederholbaren Lauf. Die drei Reviewer arbeiten unabhaengig und nur lesend. Erst wenn alle anwendbaren Review-Achsen bestanden sind und jedes Akzeptanzkriterium durch belastbare Verhaltensnachweise belegt ist, erhaelt der Pull Request `verified` und `awaiting-review`.

Der Pull-Request-Body ist das kanonische Evidence-Paket. Er bettet entscheidende Screenshots, REST-Aufrufe, Response-Ausschnitte und korrelierte Logs direkt ein. Daniel bleibt fuer die menschliche PR-Pruefung, Merge, Deployment und echte Produktentscheidungen zustaendig. Menschliche Aenderungswuensche starten im selben Lauf eine neue Implementierungs-, Verifikations- und Review-Runde.

## User Stories

1. Als Daniel moechte ich `probare-crm` als erstes Pilotrepository verwenden, damit der Workflow an einem konkreten agentenfaehigen Backlog validiert wird.
2. Als Daniel moechte ich grundsaetzlich alle Issue-Typen durch den Piloten bearbeiten lassen, damit der Pilot nicht durch pauschale Risikoklassen kuenstlich eingeschraenkt wird.
3. Als Daniel moechte ich mit `ready-for-agent` zugleich Reife und Implementierungsfreigabe ausdruecken, damit kein zweites Startsignal erforderlich ist.
4. Als Daniel moechte ich, dass ein Agent `ready-for-agent` selbst setzen darf, wenn das Issue nachweisbar aus meinem Arbeitsmandat abgeleitet wurde, damit PRD-Slicing ohne zusaetzliche Freigabeschleife weiterlaufen kann.
5. Als Daniel moechte ich keine zusaetzliche Arbeitsmandat-Sektion in jedem Issue pflegen, damit vorhandene PRD-, Parent-/Child- und Issue-Verlinkungen genuegen.
6. Als Daniel moechte ich, dass ein von mir eroeffnetes eigenstaendiges Issue als eigenes Arbeitsmandat gilt, damit kleine Vorhaben nicht unnoetig formalisiert werden.
7. Als Daniel moechte ich, dass abgeleitete Issues den geerbten Scope schneiden und praezisieren duerfen, damit grosse PRDs in umsetzbare Arbeit zerlegt werden koennen.
8. Als Daniel moechte ich, dass Agenten den geerbten Scope nicht eigenmaechtig erweitern, damit fachliche Reichweitenentscheidungen bei mir bleiben.
9. Als Repository-Maintainer moechte ich nur einen aktiven Implementierungslauf pro Repository, damit Worktrees, Pull Requests und Abhaengigkeiten nicht miteinander kollidieren.
10. Als Repository-Maintainer moechte ich, dass offene `Blocked by`-Beziehungen den Start verhindern, damit Issues in fachlich gueltiger Reihenfolge umgesetzt werden.
11. Als Repository-Maintainer moechte ich, dass ein Folge-Issue erst nach Merge und Abschluss seines Blockers startet, damit es nicht auf ungemergten Annahmen aufbaut.
12. Als Daniel moechte ich im Pilot keine gestapelten Pull Requests, damit meine Review-Oberflaeche einfach und eindeutig bleibt.
13. Als Daniel moechte ich den Workflow im Normalbetrieb durch GitHub-Webhooks starten lassen, damit freigegebene Arbeit ohne periodisches Polling zeitnah beginnt.
14. Als Betreiber moechte ich, dass nur korrekt signierte GitHub-Deliveries akzeptiert werden, damit manipulierte oder fremde Requests keine Agentenarbeit ausloesen.
15. Als Betreiber moechte ich, dass Repository, Event und Action vor der Annahme validiert werden, damit der Pilot nur vorgesehene Zustandsuebergaenge verarbeitet.
16. Als Betreiber moechte ich, dass jede akzeptierte Delivery vor der positiven Antwort dauerhaft gepuffert wird, damit ein lokaler Ausfall keine bereits bestaetigte Arbeit verliert.
17. Als Betreiber moechte ich Cloudflare im kostenlosen Tarif nutzen, damit der Pilot ohne zusaetzliche laufende Infrastrukturkosten startet.
18. Als Betreiber moechte ich ein garantiertes Offline-Fenster von 24 Stunden, damit kurze Ausschalt- und Schlafphasen des Macs automatisch ueberbrueckt werden.
19. Als Betreiber moechte ich mindestens einmal zugestellte Queue-Nachrichten idempotent verarbeiten, damit Wiederholungen keine doppelten Laeufe erzeugen.
20. Als Betreiber moechte ich `X-GitHub-Delivery` durchgaengig als fachlichen Idempotenzschluessel verwenden, damit Edge-Ingress, lokale Inbox und LangGraph denselben Auftrag erkennen.
21. Als Betreiber moechte ich temporaer fehlgeschlagene lokale Zustellungen mit Backoff wiederholen, damit kurze Ausfaelle ohne Eingriff heilen.
22. Als Betreiber moechte ich dauerhaft fehlgeschlagene Nachrichten sichtbar in eine Dead-Letter-Behandlung ueberfuehren, damit Fehler nicht still verschwinden.
23. Als Daniel moechte ich nach mindestens 24 Stunden lokaler Inaktivitaet genau einen Startup-Reconciliation-Lauf, damit abgelaufene Webhook-Deliveries durch den aktuellen GitHub-Zustand kompensiert werden.
24. Als Daniel moechte ich kein periodisches GitHub-Polling, damit der Normalbetrieb ereignisgetrieben bleibt.
25. Als Betreiber moechte ich hoechstens einen Reconciliation-Lauf pro Mac-Boot, damit Prozessneustarts keinen wiederholten Vollabgleich ausloesen.
26. Als Betreiber moechte ich, dass Reconciliation und spaet eintreffende Queue-Deliveries dieselben Idempotenzregeln verwenden, damit ihre Reihenfolge keine Doppelverarbeitung verursacht.
27. Als Daniel moechte ich, dass der lokale Stack nach meiner macOS-Anmeldung automatisch startet, damit der Workflow ohne manuellen Prozessstart verfuegbar wird.
28. Als Betreiber moechte ich, dass abgestuerzte lokale Prozesse automatisch neu gestartet werden, damit der Pilot innerhalb seiner Betriebsgrenzen selbststaendig weiterarbeitet.
29. Als Implementierungsagent moechte ich fuer jedes Issue einen isolierten Worktree erhalten, damit Aenderungen anderer Laeufe oder des Benutzer-Worktrees nicht ueberschrieben werden.
30. Als Implementierungsagent moechte ich nur den explizit uebergebenen Issue-, Requirements-, Repository- und Finding-Kontext erhalten, damit der aktive Scope eng bleibt.
31. Als Implementierungsagent moechte ich die vorhandenen Matt-Pocock-Skills passend zur Aufgabe verwenden, damit Triage, Slicing, Diagnose, TDD, Implementierung und Design konsistent ausgefuehrt werden.
32. Als Implementierungsagent moechte ich Features und Fehler in verhaltensbasierten Red-Green-Slices bearbeiten, damit jede Aenderung durch einen beobachtbaren Test abgesichert wird.
33. Als Betreiber moechte ich Codex CLI hinter einem austauschbaren Worker-Adapter betreiben, damit LangGraph nicht an eine experimentelle Codex-Server-Schnittstelle gekoppelt wird.
34. Als Betreiber moechte ich strukturierte Worker-Ergebnisse gegen feste Schemas validieren, damit LangGraph nicht von unstrukturierter Modellprosa abhaengt.
35. Als Betreiber moechte ich Modell, Reasoning-Stufe und Skill-Version pro Agent-Node nachvollziehen koennen, damit Qualitaet, Kosten und Reproduzierbarkeit sichtbar bleiben.
36. Als Daniel moechte ich einfache Darstellung mit Luna und `medium` ausfuehren, damit rein redaktionelle Arbeit kosteneffizient bleibt.
37. Als Daniel moechte ich regulaere fachliche Agenten mit Terra und `xhigh` ausfuehren, damit Implementierung und Reviews hohe Qualitaet ohne generellen Sol-Einsatz erreichen.
38. Als Daniel moechte ich Sol nur fuer definierte schwierige Eskalationen mit `xhigh` einsetzen, damit das teuerste Modell nicht der allgemeine Default ist.
39. Als Daniel moechte ich Requirements Review, Code Review und Architektur Review als drei unabhaengige Perspektiven, damit fachliche Vollstaendigkeit, Codequalitaet und Systemform getrennt beurteilt werden.
40. Als Reviewer moechte ich nur lesend arbeiten und strukturierte Verdicts liefern, damit Reviews den Branch nicht verdeckt veraendern.
41. Als Requirements Reviewer moechte ich Akzeptanzkriterien gegen Implementierung und Evidence pruefen, damit ein gruener Build keine fehlende Anforderung verdeckt.
42. Als Code Reviewer moechte ich Repository-Standards und relevante Code-Smells pruefen, damit die Implementierung wartbar und konsistent bleibt.
43. Als Architektur Reviewer moechte ich Domaenensprache, ADRs, Module, Interfaces, Seams, Adapter und Testoberflaechen pruefen, damit der Code den dokumentierten Systemgrenzen entspricht.
44. Als Daniel moechte ich, dass ein `fail` auf einer Review-Achse die Freigabe blockiert, damit keine Perspektive durch eine andere ueberstimmt wird.
45. Als Implementierungsagent moechte ich aggregierte Findings in einer neuen Runde bearbeiten, damit nur ein schreibender Agent fuer den Branch verantwortlich bleibt.
46. Als Daniel moechte ich pro Review- oder Feedback-Batch hoechstens drei automatische Behebungsrunden, damit Endlosschleifen begrenzt werden.
47. Als Daniel moechte ich nach drei erfolglosen Runden einen Draft-PR mit Versuchen und offenen Findings, damit unfertige Arbeit sichtbar und verwertbar bleibt.
48. Als Daniel moechte ich fehlende oder widerspruechliche Anforderungen als `needs-info` sehen, damit fachliche Klaerung von technischen Problemen getrennt bleibt.
49. Als Daniel moechte ich nicht agentisch loesbare Implementierungs- oder Reviewkonflikte als `ready-for-human` sehen, damit ich gezielt uebernehmen kann.
50. Als Daniel moechte ich nur bei echten Produktentscheidungen, materieller Scope-Erweiterung, fehlenden Zugangsdaten, unvermeidbarer manueller Evidence oder ausgeschoepften Runden unterbrochen werden, damit kleine technische Details autonom geloest werden.
51. Als Daniel moechte ich bei kleinen reversiblen Darstellungsdetails nicht unterbrochen werden, damit der Workflow nicht wegen Buttonfarben oder vergleichbarer Einzelheiten stoppt.
52. Als Daniel moechte ich, dass semantisch relevante Darstellungsentscheidungen weiterhin als Produktentscheidung erkannt werden, damit Warnungen, Einwilligungen und fachliche Aktionen nicht versehentlich veraendert werden.
53. Als Daniel moechte ich vor der Implementierung eine Evidence-Matrix pro Akzeptanzkriterium, damit von Anfang an klar ist, wie Erfuellung bewiesen wird.
54. Als Daniel moechte ich REST-Verhalten durch Request, Response und fachlichen Read-back bewiesen sehen, damit ein einzelner `2xx`-Status nicht als Funktionsnachweis gilt.
55. Als Daniel moechte ich UI-Verhalten durch ausgefuehrte Interaktionen und entscheidende Screenshots bewiesen sehen, damit ein statischer Seitenzustand nicht als Interaktionsnachweis gilt.
56. Als Daniel moechte ich Persistenz und Recovery durch Neustart und erneute Beobachtung ueber die oeffentliche Schnittstelle bewiesen sehen, damit Wiederanlauf nicht nur aus Logs abgeleitet wird.
57. Als Daniel moechte ich Idempotenz durch wiederholte erlaubte Aufrufe und ausbleibende Doppelwirkungen bewiesen sehen, damit Retry-Sicherheit belastbar ist.
58. Als Daniel moechte ich Logs nur als korrelierte Stuetzbelege verwenden, damit behaupteter Erfolg nicht das fachlich beobachtbare Ergebnis ersetzt.
59. Als Daniel moechte ich die entscheidende Evidence direkt im Pull-Request-Body sehen, damit ich nicht fuer Screenshots und Ergebnisse in den GitHub-Datei-Viewer wechseln muss.
60. Als Daniel moechte ich Screenshots, REST-Ausschnitte und relevante Logs kompakt und redigiert eingebettet sehen, damit die Review-Oberflaeche aussagekraeftig und sicher bleibt.
61. Als Daniel moechte ich `verified` nur fuer den aktuell geprueften PR-Head vergeben, damit ein neuer Commit keine veraltete Freigabe behaelt.
62. Als Daniel moechte ich, dass jeder neue Commit die vollstaendige Verifikations- und Review-Runde erneut ausloest, damit Evidence und Verdicts commit-genau bleiben.
63. Als Daniel moechte ich einen verifizierten Pull Request mit `verified` und `awaiting-review` sehen, damit klar ist, wann meine menschliche Pruefung beginnt.
64. Als Daniel moechte ich menschliche Aenderungswuensche im selben Lauf weiterbearbeiten lassen, damit Kontext, Checkpoints und Evidence nicht durch einen neuen Auftrag getrennt werden.
65. Als Daniel moechte ich, dass ein neuer menschlicher Feedback-Batch einen eigenen Rundenzaehler erhaelt, damit spaetes Review nicht durch fruehere Agentenrunden bestraft wird.
66. Als Daniel moechte ich, dass der Workflow niemals selbst merged oder deployt, damit die irreversible Freigabe bei mir bleibt.
67. Als Daniel moechte ich, dass ein menschlich gemergter Pull Request das Issue abschliesst und den Lauf beendet, damit GitHub und LangGraph denselben Abschlusszustand zeigen.
68. Als Betreiber moechte ich Secrets, Tokens, personenbezogene Daten und irrelevante Payload-Inhalte aus Evidence und Logs entfernen, damit Automatisierung keine vertraulichen Daten veroeffentlicht.
69. Als Betreiber moechte ich Checkpoints, Versuche, Events und Korrelationen dauerhaft nachvollziehen koennen, damit unterbrochene oder fehlgeschlagene Laeufe diagnostizierbar sind.
70. Als spaeterer Maintainer moechte ich `ki-fuer-kmu` und weitere Repositories ueber Adapter anbinden koennen, damit der Pilot ohne Neuschreiben der Control Plane erweitert werden kann.

## Implementation Decisions

- `shared-ai-docs` besitzt den zentralen Orchestrator; `probare-crm` ist das erste konfigurierte Pilotrepository.
- LangGraph ist die persistente Control Plane. Git, GitHub und LangGraph-Checkpoints sind dauerhafte Quellen; eine einzelne Codex-Session ist keine Workflow-Persistenz.
- Die Loesung wird als tiefer Workflow-`Module` mit einem kleinen externen `Interface` entworfen. Aufrufer liefern ein authentifiziertes Ereignis oder einen Startup-Reconciliation-Impuls; das Modul verantwortet Claiming, Scheduling, Statuswechsel, Worker-Aufrufe, Reviews, Evidence und Abschlussprojektion.
- Der Cloudflare-Ingress ist ein getrennt deploybares `Module`. Sein `Interface` nimmt den rohen GitHub-Request an und liefert nur Annahme oder Ablehnung. Signaturpruefung, Repository-Allowlist, Eventfilterung und Queue-Schreiboperation bleiben in seiner Implementation verborgen.
- Der lokale Ingress ist ein getrenntes `Module`, weil Cloudflare und lokale Control Plane in verschiedenen Laufzeiten liegen. Sein `Interface` nimmt eine signierte Delivery idempotent an und bestaetigt erst nach atomarer Persistierung.
- `X-GitHub-Delivery` ist der durchgaengige Idempotenzschluessel fuer Edge Queue, lokale Inbox und LangGraph-Transitionen.
- Cloudflare Workers und Cloudflare Queues bilden die dauerhafte Edge-Inbox. Der kostenlose Tarif mit 24 Stunden Retention ist eine bewusst akzeptierte Betriebsgrenze.
- Ein Queue-Consumer liefert Ereignisse ueber einen benannten, ausgehend aufgebauten Cloudflare Tunnel an genau den lokalen Webhook-Pfad. Es werden keine eingehenden Router-Ports geoeffnet.
- Cloudflare Access liegt nicht vor dem maschinellen Webhook-Pfad. GitHub- und interne Request-Signaturen sowie getrennt gespeicherte Secrets sichern die beiden Hops.
- Der lokale Receiver akzeptiert nur vorgesehene Requests, begrenzt die Groesse, validiert Signaturen vor dem Parsen und erlaubt nur konfigurierte Repositories und Event-/Action-Kombinationen.
- Der Edge-Consumer bestaetigt eine Queue-Nachricht erst nach dauerhafter lokaler Annahme. Retry, Backoff und Dead-Letter-Behandlung muessen sichtbar und idempotent sein.
- Die lokale Control Plane fuehrt einen internen `last_alive_at`-Zeitpunkt und eine Mac-Boot-Session-ID. Nach mindestens 24 Stunden Inaktivitaet laeuft pro Boot hoechstens ein Startup-Reconciliation-Abgleich.
- Startup-Reconciliation liest den aktuellen Zustand freigegebener und laufender Issues sowie zugehoeriger Pull Requests und speist fehlende Transitionen als synthetische idempotente Kommandos in dieselbe Inbox ein.
- Der lokale Stack startet nach Daniels macOS-Anmeldung als `launchd`-LaunchAgent und wird bei Prozessfehlern neu gestartet.
- `ready-for-agent` ist Reifezustand und Arbeitsfreigabe. Ein zweites Startlabel wird nicht eingefuehrt.
- Agentisches Selbstsetzen von `ready-for-agent` ist nur innerhalb einer nachweisbaren Herkunftskette aus Daniels Issue, PRD oder vergleichbarem Arbeitsmandat erlaubt.
- Parent-/Child-, PRD- und native Blocking-Beziehungen bilden Herkunft und Ausfuehrungsreihenfolge ab; ein zusaetzlicher Pflichtabschnitt wird nicht eingefuehrt.
- Pro Repository ist hoechstens ein Implementierungslauf aktiv. Offene Blocker verhindern den Start; gestapelte Pull Requests sind im Pilot nicht erlaubt.
- Der GitHub-Zustand ist eine sichtbare Projektion. Persistierte LangGraph-Zustaende bleiben die technische Quelle fuer Checkpoints, Versuche und Wiederaufnahme.
- Die Workflow-Qualifier sind `agent-running`, `verified` und `awaiting-review`; fachliche Klaerung und menschliche Uebernahme verwenden `needs-info` und `ready-for-human`.
- Codex CLI wird ueber einen austauschbaren Worker-`Adapter` mit nicht-interaktivem `codex exec` angesprochen. Experimentelle Codex-App- oder Exec-Server sind nicht Teil des Piloten.
- Der Implementierungsworker besitzt Schreibzugriff auf einen isolierten Worktree. Requirements-, Code- und Architekturreview arbeiten mit frischem Kontext und nur lesend.
- Worker-Eingaben und -Ergebnisse folgen versionierten strukturierten Schemas. Diagnoseevents duerfen als JSONL erfasst werden, sind aber nicht selbst der fachliche Erfolgsnachweis.
- Matt-Pocock-Skills liefern den Arbeitsvertrag der Agent-Nodes. Triage verwendet `triage`, grosse Anforderungen `to-tickets`, Feature-Arbeit `implement` und `tdd`, Bugarbeit `diagnosing-bugs` und `tdd`, Code- und Requirements Review die getrennten Achsen von `code-review`, Architekturreview `codebase-design` und `domain-modeling`.
- Die verwendeten Skill-Versionen oder Content-Hashes werden pro Lauf aufgezeichnet.
- Deterministische Control-Plane-Arbeit verwendet kein Sprachmodell. Rein darstellende Arbeit verwendet GPT-5.6 Luna mit `medium`. Triage, Slicing, Implementierung, Findings-Bearbeitung und regulaere Reviews verwenden GPT-5.6 Terra mit `xhigh`. Definierte schwierige Eskalationen verwenden GPT-5.6 Sol mit `xhigh`.
- Sol-Eskalationen sind auf materielle Architektur-, Persistenz-, Sicherheits- oder Datenmigrationsfragen, ein strukturiertes `escalate`-Verdict oder die dritte und letzte Behebungsrunde begrenzt.
- Requirements, Code und Architektur sind drei feste unabhaengige Review-Nodes. Jeder liefert `pass`, `fail` oder `not_applicable` mit Begruendung und Findings; Requirements Review ist immer anwendbar.
- Ein `fail` auf einer Achse blockiert die Reviewfreigabe. Nur der Implementierungsworker behebt Findings; danach laufen deterministische Verifikation und alle drei Reviews erneut.
- Pro initialem Review-Batch oder neuem menschlichem Feedback-Batch sind hoechstens drei automatische Behebungsrunden erlaubt.
- Nach drei erfolglosen Runden bleibt ein Draft-PR mit Versuchen und Findings bestehen. Fehlende Anforderungen fuehren zu `needs-info`; nicht agentisch loesbare Konflikte zu `ready-for-human`.
- Die Interrupt-Policy unterscheidet echte Produktentscheidungen von reversiblen Implementierungs- und Darstellungsdetails. Nur Produktverhalten, materielle Scope-Erweiterung, fehlende menschliche Zugaenge, unvermeidbare manuelle Evidence oder ausgeschoepfte Runden pausieren den Lauf.
- Vor Implementierung entsteht eine Evidence-Matrix, die jedes Akzeptanzkriterium einer direkten beobachtbaren Schnittstelle, erwartetem Ergebnis und konkretem Beweis zuordnet.
- `verified` setzt fuer jedes Akzeptanzkriterium belastbare Verhaltensnachweise voraus. Build, Prozessstart, Containerstatus, Healthcheck, nackter `2xx`-Status, unkorrelierte Logs oder statische Ausgangsscreenshots reichen nicht aus.
- Der Pull-Request-Body ist das kanonische Delivery-Evidence-Paket. Kriteriumsverdicts, entscheidende Screenshots, REST-Requests und -Responses sowie kurze korrelierte Logs werden soweit technisch moeglich direkt eingebettet.
- Kuratierte Screenshots duerfen commit-genau im PR-Branch liegen. Umfangreiche Rohdaten und Secrets gehoeren nicht in Branch oder PR-Body.
- `verified` gilt ausschliesslich fuer einen konkreten PR-Head. Jeder neue Commit entfernt `verified` und `awaiting-review`, setzt `agent-running` und startet eine vollstaendige neue Verifikations- und Review-Runde.
- Ein erfolgreicher automatischer Lauf endet mit einem verifizierten Pull Request in `awaiting-review`. Menschliche Aenderungswuensche setzen denselben Lauf fort. Merge, Deployment, Release und Produktionsaenderungen bleiben ausserhalb der Automatisierung.

## Testing Decisions

- Gute Tests pruefen beobachtbares Verhalten durch dasselbe `Interface`, das auch ein produktiver Aufrufer verwendet. Sie duerfen nicht an interne LangGraph-Node-Reihenfolge, Prompttexte, Helper-Aufrufe, konkrete Datenbankabfragen oder private Klassen gekoppelt sein.
- Der primaere System-`Seam` nimmt eine authentifizierte GitHub-Delivery oder einen Startup-Reconciliation-Impuls entgegen, fuehrt Inbox und LangGraph mit realer Persistenz bis zu einem stabilen Zustand aus und beobachtet ausschliesslich GitHub-Projektionen, Pull-Request-Evidence, Checkpoints und Worker-Ergebnisse.
- Der primaere Seam verwendet kontrollierbare `Adapter` fuer GitHub, Codex, Uhr und externe Zustellung. Die eigentliche Workflow-Implementation und der persistente Zustand bleiben real, damit Restart, Idempotenz, Review-Schleifen und Statusprojektionen gemeinsam bewiesen werden.
- Der Cloudflare-Ingress benoetigt einen schmalen Contract-Seam, weil er in einer getrennten Laufzeit ausgefuehrt wird. Ein roher signierter HTTP-Request fuehrt entweder zu genau einer Queue-Nachricht und einer positiven Antwort oder zu einer begruendeten Ablehnung ohne Queue-Wirkung.
- Der Codex-Worker benoetigt einen schmalen Contract-Seam. Ein strukturierter Agentenauftrag fuehrt zu einer validierten strukturierten Antwort und beweist Modellwahl, Reasoning-Stufe, Skill-Routing sowie Schreib- oder Read-only-Rechte.
- Weitere oeffentliche Test-Seams fuer einzelne LangGraph-Nodes werden nicht eingefuehrt. Deterministische interne Funktionen koennen eng getestet werden, tragen aber nicht die Akzeptanzfreigabe.
- Ein signiertes `ready-for-agent`-Labelereignis fuer ein unblocked Issue muss genau einen Lauf claimen, `agent-running` projizieren und einen isolierten Implementierungsauftrag starten.
- Ein doppeltes oder erneut zugestelltes Webhook-Ereignis darf keinen zweiten Lauf, Worktree oder Pull Request erzeugen.
- Ein offener Blocker muss den Start verhindern; Merge und Abschluss des Blockers muessen das Folge-Issue spaeter freigeben.
- Zwei gleichzeitig freigegebene Issues desselben Repositories duerfen nicht gleichzeitig implementiert werden.
- Ein mindestens 24-stuendiger Ausfall muss beim naechsten Boot genau einen Reconciliation-Lauf ausloesen; ein kuerzerer Ausfall und ein zweiter Prozessstart im selben Boot duerfen keinen solchen Lauf erzeugen.
- Reconciliation und spaete Queue-Delivery fuer denselben Zustand muessen zu genau einer fachlichen Transition fuehren.
- Temporare Zustellfehler muessen wiederholt werden; dauerhafte Fehler muessen nach dem Versuchslimit sichtbar in der Dead-Letter-Behandlung landen.
- Ein Implementierungsdurchlauf muss die fuer den Issue-Typ vorgesehenen Skills, das konfigurierte Modell und die konfigurierte Reasoning-Stufe nachweisbar verwenden.
- Requirements-, Code- und Architekturreview muessen unabhaengig ausgefuehrt und getrennt aggregiert werden. Ein einzelnes `fail` muss die Freigabe blockieren.
- Ein neuer PR-Commit muss vorherige Verification invalidieren und alle anwendbaren Reviews erneut ausfuehren.
- Drei erfolglose automatische Runden muessen einen Draft-PR und den passenden menschlichen Folgezustand erzeugen; eine vierte automatische Runde darf nicht beginnen.
- Neues menschliches Feedback muss im bestehenden Lauf eine neue Runde mit eigenem Batch-Zaehler starten.
- Evidence-Tests muessen fuer REST, UI, Persistenz, Recovery, Idempotenz, negative Gates und Hintergrundarbeit jeweils fachliche Beobachtungen statt Infrastruktur-Surrogate verlangen.
- Ein Healthcheck, Containerstart oder erfolgreicher Testprozess ohne Kriteriumszuordnung muss als unzureichende Evidence abgelehnt werden.
- Der erzeugte Pull-Request-Body muss die Kriteriumsmatrix und die entscheidenden redigierten Evidence-Ausschnitte direkt enthalten.
- Secrets und personenbezogene Daten muessen in Queue-Payloads, Logs, Checkpoints und PR-Evidence redigiert oder ausgeschlossen sein.
- Der Workflow darf in keinem Test selbst mergen, deployen oder eine fachliche Produktentscheidung synthetisieren.
- Als Prior Art dient die in `probare-crm` dokumentierte Strategie, den vollstaendigen beobachtbaren Workflow als hoechsten Seam zu testen. Im Shared-AI-Repository existieren ausserdem deterministische CLI-Validatoren und verhaltensorientierte Python-Tests als Muster fuer kleine Control-Plane-Regeln; eine bestehende LangGraph-Testinfrastruktur gibt es noch nicht.

## Out of Scope

- Automatisches Mergen von Pull Requests.
- Deployment, Releases oder Produktionsaenderungen.
- Mehr als ein paralleler Implementierungslauf pro Repository im ersten Pilot.
- Gestapelte Pull Requests.
- Ein generelles periodisches GitHub-Polling; erlaubt ist nur der definierte einmalige Startup-Reconciliation-Lauf nach mindestens 24 Stunden Inaktivitaet.
- Eine Verfuegbarkeitsgarantie von mehr als 24 Stunden im kostenlosen Cloudflare-Tarif.
- Migration auf einen kostenpflichtigen Cloudflare-Tarif.
- Eine GitHub App als Voraussetzung fuer den ersten Pilot; die Ingress-Schnittstelle soll eine spaetere Migration lediglich ermoeglichen.
- Aktivierung weiterer Pilotrepositories wie `ki-fuer-kmu`, bevor der `probare-crm`-Pilot belastbar ist.
- Risikoklassen, die bestimmte Issue-Typen pauschal vom Pilot ausschliessen.
- Ein zusaetzlicher Arbeitsmandat-Pflichtabschnitt in Issues.
- Ein zweites Start- oder Freigabelabel neben `ready-for-agent`.
- Experimentelle Codex `app-server`- oder `exec-server`-Integrationen.
- Ein generisches Multi-User- oder SaaS-Orchestrierungsprodukt.
- Vollautomatische Loesung echter Produktentscheidungen, Zugangsdatenprobleme oder ausschliesslich menschlicher externer Schritte.
- Rohartefakt-Viewer als primaere Review-Oberflaeche.
- Evidence-Freigabe allein durch Build, Start, Healthcheck, Statuscode, Logbehauptung oder statischen Screenshot.
- Festlegung reversibler Details wie konkrete Ports, interne Paketnamen, Persistenztabellen, Backoff-Intervalle, Logrotation oder Observability-Feldnamen in dieser Parent-Spec.

## Further Notes

- Diese Parent-Spec ist strategische Referenz und Abdeckungsquelle. Sie ist nicht der aktive Implementierungsvertrag fuer einen einzigen grossen Lauf.
- Der naechste Schritt ist die Zerlegung mit `to-tickets` in vertikale tracer-bullet Slices mit expliziten Blocking-Kanten.
- Vor Implementierung eines Slices wird im Shared-AI-Repository jeweils ein kleiner aktiver OpenSpec-Change mit Ziel, In-Scope, Out-of-Scope, Write-Set und Verifikation erstellt.
- `probare-crm` besitzt derzeit 13 offene, voneinander abhaengige und mit `ready-for-agent` markierte MVP-Issues. Sie bilden den realen Pilotbacklog, nicht die Implementierungstickets fuer den Orchestrator selbst.
- Die Pilotnotiz und das Domain-Glossar bleiben Begruendungs- und Vokabelquellen fuer die spaeteren Slices.
- Die bestaetigten Test-Seams wurden vor Erstellung dieser Spec mit Daniel abgeglichen.
