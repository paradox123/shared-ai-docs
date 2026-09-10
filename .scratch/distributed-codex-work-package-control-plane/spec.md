# Distributed Codex Work Package Control Plane

Status: ready-for-agent

## Problem Statement

Ein komplexer Implementierungslauf besteht nicht nur aus einer einzelnen Codex-Unterhaltung. Aus einem freigegebenen GitHub Issue entstehen Implementierung, deterministische Tests, Verhaltensnachweise, mehrere unabhängige Reviews, Behebungsrunden, menschliche Rückfragen, Freigabe und Abschluss. In einer einzigen durchgehenden Agentensession wächst der Kontext über diese Tätigkeiten hinweg so stark, dass Context Drift, überholte Annahmen und schwer nachvollziehbare Entscheidungen wahrscheinlich werden. Werden die Tätigkeiten dagegen nur als voneinander getrennte Tasks oder verlustbehaftete Handovers ausgeführt, fehlt dem eingreifenden Menschen die Historie, die er zur Diagnose des Fehlerfalls benötigt.

Der heutige Pilot ist außerdem an einen lokalen Betreiber und dessen Mac gebunden. Für den späteren Einsatz in einem Entwicklungsteam mit ungefähr 20 Personen darf ein Implementierungslauf weder einem bestimmten Rechner noch dauerhaft derselben Person gehören. Ein Entwickler kann das Arbeitsmandat anstoßen, ein anderer kann Stunden später einen Fehler untersuchen und beheben, und ein dritter kann den verifizierten Pull Request freigeben. Alle Beteiligten müssen von ihren Work Machines auf denselben zentralen Implementierungslauf, dessen aktuellen Zustand und dessen vollständig beobachtbare Ausführungshistorie zugreifen können.

Daniel bevorzugt Codex als Agent-Harness, weil die damit erzielten Implementierungs- und Review-Ergebnisse den bisher erprobten Alternativen mit Claude oder GitHub Copilot überlegen sind. Eine neue Orchestrierungsplattform darf deshalb Codex nicht beiläufig durch einen anderen Agent-Harness ersetzen. Sie soll Codex-Sessions zentral koordinieren, beobachten und im Fehlerfall gezielt fortsetzen, forken oder neu starten.

Benötigt wird somit eine verteilte, teamfähige Control Plane: Ein GitHub-Issue-gebundener Implementierungslauf bleibt die einzige sichtbare Arbeitseinheit, unter der viele kontextisolierte Codex-Aktivitätsläufe mit einer gemeinsamen, dauerhaft lesbaren Historie koordiniert werden. Der Mensch muss einen Fehler nicht nur als zusammengefasste Interventionsanfrage sehen, sondern nachvollziehen können, was der betroffene Agent tatsächlich beobachtbar getan hat, wo er scheiterte und welche Artefakte er hinterließ.

## Solution

Die Work Package Control Plane führt pro freigegebenem Issue genau einen langlebigen Implementierungslauf. Dieser Lauf bündelt Implementierung, Tests, Evidence, unabhängige Reviews, begrenzte Behebungsrunden, menschliche Intervention, Freigabe und Abschluss. Er bleibt für das Team erreichbar, auch wenn Personen, Rechner oder ausführende Prozesse wechseln.

Jede agentische Tätigkeit erhält standardmäßig eine eigene, begrenzte Codex-Session. Die gemeinsame, dauerhaft lesbare Run History zeigt die beobachtbare Ausführung aller Tätigkeiten; der aktive Modellkontext bleibt davon getrennt und enthält nur die für die jeweilige Aufgabe benötigten Informationen. Damit bleiben Diagnose und Audit vollständig, ohne alle Tätigkeiten in eine immer länger werdende Unterhaltung zu zwingen.

Berechtigte Teammitglieder können denselben Lauf unabhängig von ihrem Arbeitsplatz beobachten. Genau ein Mensch steuert ihn zu einem Zeitpunkt; Verantwortung kann freiwillig übertragen oder sichtbar erzwungen übernommen werden. Der Steuernde kann eine laufende Aktivität gezielt unterbrechen oder eine Anweisung einreihen und nach einem Fehler bewusst zwischen Fortsetzen, Fork, frischem Versuch, manueller Übernahme oder Abbruch wählen.

Für die Detailarbeit kann der konkrete Aktivitätsversuch aus dem Operator Client in Codex geöffnet werden. Wenn Codex die ursprüngliche Session sicher darstellen und fortsetzen kann, wird genau diese Session geöffnet. Andernfalls entsteht nur nach sichtbarer Bestätigung ein als Handoff gekennzeichneter Fork mit nachvollziehbarer Herkunft. Öffnen und Bearbeiten umgehen weder Control Lease noch Fencing; alle beobachtbaren Folgeereignisse bleiben Teil derselben Run History.

Repositoryberechtigungen bestimmen Beobachtungs- und Steuerungsrechte. Menschliche Entscheidungen und technische Servicewirkungen bleiben klar getrennt und auditierbar. Freigaben erfordern eine explizite interaktive Handlung eines berechtigten Menschen; der Workflow darf nicht selbst freigeben, mergen, deployen oder releasen.

Der zusätzliche Microsoft-Agent-Framework-Pilot prüft diese fachlichen Anforderungen als eigenständige Schwesterimplementierung. Der vorhandene LangGraph-Pilot mit Cloudflare-, macOS- und ProBara-CRM-Anbindung bleibt unverändert und unabhängig ausführbar. Für den neuen Piloten ist ein produktionsfähiger, selbst hostbarer Open-Source-Pfad ohne verpflichtende zusätzliche Framework- oder Managed-Workflow-Service-Lizenzkosten zwingend; Temporal und kostenpflichtige Managed-Workflow-Dienste sind ausgeschlossen.

Konkrete Frameworks, Pakete, Persistenztechniken, Prozessgrenzen, Ports und Fehlereinspritzung gehören nicht in diese PRD. Sie werden im ADR, im technischen Mapping, im Spike-Plan und in den Umsetzungstickets festgelegt und müssen die hier beschriebenen Ergebnisse über öffentliche Oberflächen nachweisen.

## User Stories

1. Als Entwickler möchte ich ein freigegebenes GitHub Issue als einen zentralen Implementierungslauf starten, damit alle nachfolgenden Tätigkeiten derselben Arbeitseinheit zugeordnet bleiben.
2. Als Entwickler möchte ich nach dem Start nicht technischer Eigentümer des Implementierungslaufs sein, damit andere Teammitglieder ihn später bearbeiten können.
3. Als Teammitglied möchte ich einen Implementierungslauf über eine stabile URL oder Kennung öffnen, damit ich ihn von jeder autorisierten Work Machine erreichen kann.
4. Als Teammitglied möchte ich nur einen sichtbaren Implementierungslauf pro Issue sehen, damit ich nicht für jede Agentenaktivität eine separate Benutzer-Task verwalten muss.
5. Als Teammitglied möchte ich unter dem Implementierungslauf alle Implementierungs-, Test-, Review-, Repair- und Interventionsaktivitäten sehen, damit der Gesamtzusammenhang erhalten bleibt.
6. Als Teammitglied möchte ich den aktuellen Zustand, die aktive Phase, den aktuellen Head und den verantwortlichen Akteur auf einen Blick sehen, damit ich den Lauf schnell einordnen kann.
7. Als Initiator möchte ich den Arbeitsplatz ausschalten können, ohne den zentralen Implementierungslauf zu unterbrechen, damit dessen Lebensdauer nicht von meinem Laptop abhängt.
8. Als Initiator möchte ich nicht online bleiben müssen, während zentrale Worker das Issue bearbeiten, damit der Lauf wirklich unbeaufsichtigt arbeiten kann.
9. Als Betreiber möchte ich Agenten auf zentralen oder verwalteten Worker Machines ausführen, damit Ausführung, Secrets und Ressourcen nicht auf Benutzer-Laptops verteilt werden müssen.
10. Als Betreiber möchte ich Worker horizontal ergänzen oder ersetzen können, damit spätere Teams und zusätzliche Aktivitäten nicht an eine einzelne Maschine gebunden sind.
11. Als Betreiber möchte ich einen aktiven Worktree und mutierenden Writer pro Implementierungslauf kontrollieren, damit parallele Agenten keine konkurrierenden Änderungen erzeugen.
12. Als Betreiber möchte ich die bestehende Implementierungswarteschlange und Repository-Serialisierung zunächst bewahren, damit der neue Prototyp keine zusätzlichen Merge- und Branch-Konflikte einführt.
13. Als Entwickler möchte ich Codex weiterhin als Agent-Harness verwenden, damit die bisher erreichte Implementierungs- und Reviewqualität erhalten bleibt.
14. Als Entwickler möchte ich Codex über einen austauschbaren Adapter anbinden, damit die Control Plane nicht an eine einzelne CLI- oder App-Server-Version gekoppelt ist.
15. Als Betreiber möchte ich die verwendete Codex-Version, das Modell, die Reasoning-Stufe, die Skills und die Zugriffsrichtlinie pro Aktivitätsversuch sehen, damit Ergebnisse reproduzierbar und auditierbar sind.
16. Als Implementierungsagent möchte ich einen isolierten Worktree, ein Arbeitsmandat und einen begrenzten Tätigkeitsscope erhalten, damit fremde Historie meinen aktiven Kontext nicht unnötig belastet.
17. Als Reviewer möchte ich eine frische, nur lesende Codex-Session für genau eine Review-Achse und eine Head-SHA erhalten, damit meine Prüfung unabhängig bleibt.
18. Als Team möchte ich Requirements-, Code- und Architekturreview weiterhin als getrennte Achsen ausführen, damit keine Perspektive durch eine andere kompensiert wird.
19. Als Team möchte ich spätere zusätzliche Tätigkeiten als weitere Aktivitätstypen ergänzen können, damit die Control Plane für den komplexeren Arbeitsprozess auf der Arbeit erweiterbar bleibt.
20. Als Architekt möchte ich Aktivitätstypen über versionierte Ein- und Ausgangsverträge anbinden, damit neue Tätigkeiten nicht den gesamten Implementierungslauf neu entwerfen müssen.
21. Als Entwickler möchte ich, dass jede agentische Tätigkeit standardmäßig in einer eigenen Session startet, damit Implementierung, Review und Freigabe keinen gemeinsamen driftenden Gesprächskontext bilden.
22. Als Entwickler möchte ich, dass ein neuer Aktivitätsversuch nicht automatisch die gesamte vorherige Unterhaltung in sein Context Window lädt, damit sein Auftrag fokussiert bleibt.
23. Als Entwickler möchte ich, dass ein Agent bei Bedarf ausgewählte frühere Aktivitäten und Artefakte nachladen kann, damit Kontextisolation nicht zu Informationsverlust führt.
24. Als Entwickler möchte ich sehen, welche früheren Informationen einem Aktivitätsversuch tatsächlich bereitgestellt wurden, damit sein Verhalten erklärbar bleibt.
25. Als Betreiber möchte ich Context-Budget, Session-Länge und relevante Drift-Signale beobachten, damit problematisch lange Agentensessions früh erkennbar sind.
26. Als Betreiber möchte ich für bestimmte Tätigkeiten einen frischen Versuch erzwingen können, damit eine festgefahrene Session nicht unbegrenzt weitergeführt wird.
27. Als Entwickler möchte ich einen fehlgeschlagenen Agentenlauf in einer vollständigen beobachtbaren Timeline sehen, damit ich die Ursache selbst beurteilen kann.
28. Als Entwickler möchte ich die Benutzer- und Agentennachrichten eines Aktivitätsversuchs sehen, damit ich verstehe, welche Aufgabe bearbeitet und welche Antworten gegeben wurden.
29. Als Entwickler möchte ich Toolaufrufe mit Parametern, Ergebnissen, Dauer und Fehlern sehen, damit ich erkenne, woran die Ausführung technisch scheiterte.
30. Als Entwickler möchte ich betroffene Dateien, Diffs, Commits, Tests, Screenshots und Evidence direkt aus der Aktivität öffnen können, damit Diagnose und Review nicht auf verstreute Logs angewiesen sind.
31. Als Entwickler möchte ich den letzten erfolgreichen Schritt und den ersten fehlerhaften Schritt erkennen, damit ich gezielt ab der richtigen Grenze fortfahren kann.
32. Als Entwickler möchte ich zwischen Agentenfehler, Infrastrukturfehler, fehlendem Zugriff, unklarer Anforderung und ausgeschöpfter Behebungsrunde unterscheiden können, damit ich die passende Reaktion wähle.
33. Als Security-Verantwortlicher möchte ich, dass Secrets und sensible Nutzdaten vor der zentralen Persistierung und Anzeige redigiert werden, damit die Historie nicht zum Datenleck wird.
34. Als Auditor möchte ich nachvollziehen können, welche Historienelemente redigiert oder nicht mehr verfügbar sind, damit eine scheinbar vollständige Timeline ihre Grenzen offenlegt.
35. Als Teammitglied möchte ich wissen, dass private interne Gedankengänge des Modells nicht Teil der Historie sind, damit „vollständige Historie“ korrekt als vollständig beobachtbare Ausführung verstanden wird.
36. Als Entwickler möchte ich bei einer fachlichen Rückfrage dieselbe Codex-Session mit meiner Antwort fortsetzen können, damit der lokal relevante Gesprächskontext erhalten bleibt.
37. Als Entwickler möchte ich eine festgefahrene Codex-Session forken können, damit die bisherige Historie erhalten bleibt, aber ein neuer Lösungsweg beginnen kann.
38. Als Entwickler möchte ich eine Aktivität nach einem Infrastruktur- oder Werkzeugfehler frisch ab einem stabilen Checkpoint wiederholen können, damit fehlerhafter Gesprächskontext nicht unnötig fortgeführt wird.
39. Als Entwickler möchte ich einen Implementierungslauf manuell übernehmen können, damit ein nicht agentisch lösbarer Fall nicht blockiert bleibt.
40. Als Entwickler möchte ich einen Lauf mit dokumentiertem Grund abbrechen können, damit ein ungültiges oder widerrufenes Arbeitsmandat sicher endet.
41. Als Entwickler möchte ich vor Resume, Fork oder Retry die konkrete Zielaktivität, Session und erwartete Head-SHA sehen, damit ich nicht versehentlich einen veralteten Zustand fortsetze.
42. Als Entwickler möchte ich nach einer menschlichen Antwort sehen, welche Session oder welcher Fork sie verarbeitet hat, damit die Wirkung meiner Entscheidung nachvollziehbar bleibt.
43. Als Betreiber möchte ich Resume-, Fork-, Retry-, Takeover- und Cancel-Operationen idempotent ausführen, damit Netzwerk-Retries keine doppelten Agentenläufe erzeugen.
44. Als Betreiber möchte ich, dass ein bereits abgeschlossener externer Effekt nach einem Crash adoptiert statt wiederholt wird, damit Git-, GitHub- und Toolwirkungen sicher bleiben.
45. Als Betreiber möchte ich, dass der zentrale Implementierungslauf Prozess-, Worker- und Serverneustarts überlebt, damit menschliche Intervention auch Stunden oder Tage später möglich ist.
46. Als Betreiber möchte ich eine Interventionsanfrage dauerhaft in einer zentralen Inbox sehen, damit sie nicht von einer offenen Desktop-Session abhängt.
47. Als Teammitglied möchte ich für Interventionsanfragen benachrichtigt werden, ohne technischer Eigentümer des Laufs zu sein, damit verfügbare Kollegen übernehmen können.
48. Als Teammitglied möchte ich sehen, ob ein anderer Mensch eine Intervention bereits beansprucht oder bearbeitet, damit keine doppelte Fehlerbehebung beginnt.
49. Als Betreiber möchte ich eine zeitlich begrenzte Bearbeitungslease für mutierende Interventionen, damit verlassene Claims wieder freigegeben werden können.
50. Als Entwickler möchte ich eine Intervention an einen anderen berechtigten Kollegen übergeben können, damit Spezialwissen gezielt eingebunden wird.
51. Als Entwickler möchte ich Kommentare und Entscheidungen am Implementierungslauf hinterlassen können, damit Schicht- und Personenwechsel ohne private Nebenkommunikation funktionieren.
52. Als Teamleiter möchte ich Rollen und Berechtigungen für Initiieren, Beobachten, Beheben, Freigeben, Übernehmen, Abbrechen und Administrieren getrennt vergeben können, damit Verantwortlichkeiten der Organisation entsprechen.
53. Als Teamleiter möchte ich nicht voraussetzen, dass Initiator, Fehlerbeheber, Freigeber und Merger dieselbe Person sind, damit Vier-Augen-Prinzip und Arbeitsteilung möglich sind.
54. Als Freigeber möchte ich den verifizierten aktuellen Pull-Request-Head prüfen, auch wenn ich weder Initiator noch Fehlerbeheber war, damit Freigabe organisatorisch unabhängig bleibt.
55. Als Freigeber möchte ich die für die Freigabe relevante Historie und Evidence sehen, ohne alle Agententraces vollständig lesen zu müssen, damit menschliches Review effizient bleibt.
56. Als Freigeber möchte ich bei Bedarf von der kompakten Freigabesicht in die vollständige Aktivitätshistorie wechseln können, damit ungewöhnliche Entscheidungen untersuchbar bleiben.
57. Als Betreiber möchte ich jede menschliche Aktion mit authentifizierter Identität, Rolle und Zeitpunkt speichern, damit Verantwortungswechsel auditierbar sind.
58. Als Betreiber möchte ich für mutierende Aktionen Compare-and-Swap gegen Phase, Aktivitätsversuch und Head-SHA verwenden, damit veraltete Browser oder parallele Benutzer keine aktuellen Entscheidungen überschreiben.
59. Als Betreiber möchte ich zentrale Authentifizierung und verschlüsselte Netzwerkverbindungen verwenden, damit Work Machines sicher auf die Control Plane zugreifen.
60. Als Betreiber möchte ich Repository- und Laufzugriff voneinander begrenzen können, damit Teammitglieder nur berechtigte Arbeitsmandate und Quellartefakte sehen.
61. Als Betreiber möchte ich Worker-Secrets von den Work Machines fernhalten, damit ein Benutzer für Diagnose oder Freigabe keine produktiven Agenten-Credentials benötigt.
62. Als Betreiber möchte ich Historie, Artefakte und Workflow-Zustand nach definierten Aufbewahrungsregeln speichern, damit Auditierbarkeit und Datenschutz vereinbar bleiben.
63. Als Betreiber möchte ich große Toolausgaben und Binärartefakte außerhalb des Workflow-Kernzustands speichern und unveränderlich referenzieren, damit der Durable State begrenzt bleibt.
64. Als Team möchte ich GitHub Issue, Pull Request, Commit-SHA und Reviews weiterhin als sichtbare fachliche Projektion verwenden, damit der Prozess in bestehende Entwicklungsgewohnheiten passt.
65. Als Team möchte ich die zentrale Control Plane als technische Quelle für Aktivitäts-, Session-, Interventions- und Recovery-Zustand verwenden, damit GitHub-Kommentare nicht die gesamte Maschinenhistorie tragen müssen.
66. Als Daniel möchte ich, dass der Workflow weiterhin niemals selbst merged oder deployt, damit irreversible Freigaben menschlich bleiben.
67. Als Team möchte ich nach jedem neuen Writer-Head die deterministischen Checks und alle erforderlichen Reviews erneut ausführen, damit alte Qualification keinen neuen Commit freigibt.
68. Als Team möchte ich Behebungsrunden weiterhin begrenzen und ausgeschöpfte Versuche sichtbar erhalten, damit der zentrale Betrieb keine Endlosschleifen erzeugt.
69. Als Team möchte ich das Verhalten zuerst an einem vollständigen Fehlerfall prototypisch beweisen, damit die Wahl der Orchestrierungs- und Session-Technologie auf beobachtbarer Eignung statt Framework-Marketing beruht.
70. Als Entwickler möchte ich eine noch laufende Agentenoperation live beobachten können, damit ich eine erkennbar falsche Richtung früh korrigieren kann.
71. Als Entwickler möchte ich während einer aktiven Agentenoperation einen Control Command senden können, damit ich nicht auf einen Fehler- oder Freigabepunkt warten muss.
72. Als Entwickler möchte ich beim Senden zwischen `interrupt` und `queue` wählen, damit ich Dringlichkeit und Risiko der Korrektur selbst bestimme.
73. Als Entwickler möchte ich, dass `interrupt` die laufende Operation kontrolliert beendet und meinen Command als Nächstes bearbeitet, damit ein falscher Lösungsweg nicht unnötig fortgesetzt wird.
74. Als Entwickler möchte ich, dass `queue` die laufende Operation abschließen lässt und meinen Command danach in stabiler Reihenfolge bearbeitet, damit eine nicht dringende Ergänzung keine laufende Arbeit verwirft.
75. Als Teammitglied möchte ich Zustellungsmodus, Abbruch, Queue-Reihenfolge und Agentenantwort in der Aktivitätshistorie sehen, damit Live-Eingriffe nachvollziehbar bleiben.
76. Als Entwickler möchte ich mich mit einem zustandsarmen Operator Client an einen zentralen Implementierungslauf anhängen, damit meine Work Machine keine eigene Agentensession betreiben muss.
77. Als Entwickler möchte ich eine gemeinsame Run History über alle Agentensessions des Workflows sehen, damit ich Implementierung, Reviews, Repair und Intervention im Zusammenhang nachvollziehen kann.
78. Als Entwickler möchte ich einzelne Agentensessions aus der gemeinsamen Run History filtern und öffnen können, damit Detaildiagnose trotz einheitlicher Sicht möglich bleibt.
79. Als Entwickler möchte ich die Control Lease für einen Implementierungslauf sichtbar beanspruchen können, damit genau ein Mensch mutierende Commands senden darf.
80. Als Beobachter möchte ich mich parallel nur lesend an denselben Implementierungslauf anhängen können, damit ich den Verlauf ohne Kollisionsrisiko verfolgen kann.
81. Als Steuernder möchte ich Kommandos an die aktuelle Workflow-Aktivität statt an eine selbst gewählte Session-ID senden, damit die Control Plane sie sicher zur zuständigen Codex-Session routet.
82. Als Steuernder möchte ich agentenseitige Interventionsanfragen unmittelbar in meinem verbundenen Operator Client sehen, damit ich ohne zusätzliche Codex-Task reagieren kann.
83. Als Beobachter möchte ich sehen, wer die Control Lease besitzt und welche Commands ausgeführt wurden, damit Verantwortlichkeit und aktueller Bearbeitungsstand klar bleiben.
84. Als Steuernder möchte ich die Control Lease einheitlich für den gesamten Implementierungslauf besitzen, damit parallele Agentenaktivitäten nicht widersprüchlich von verschiedenen Menschen gelenkt werden.
85. Als Beobachter möchte ich keine einzelne Parallelaktivität separat übernehmen können, solange ein anderer Mensch den Implementierungslauf steuert, damit die exklusive Verantwortung eindeutig bleibt.
86. Als Beobachter möchte ich einen Control Transfer für einen Implementierungslauf anfragen können, damit die zuständige Person kontrolliert wechseln kann.
87. Als aktueller Steuernder möchte ich einen Transfer Request bewilligen oder ablehnen können, damit die Control Lease nicht ohne mein Wissen wechselt.
88. Als neuer Steuernder möchte ich die Control Lease erst nach einem atomaren Control Transfer erhalten, damit zu keinem Zeitpunkt zwei Menschen mutierende Commands senden dürfen.
89. Als Teammitglied möchte ich Transfer Request, Entscheidung und Inhaberwechsel in der Run History sehen, damit die Verantwortungsübergabe nachvollziehbar bleibt.
90. Als Beobachter möchte ich die Control Lease ohne Zustimmung des bisherigen Inhabers per Forced Takeover übernehmen können, damit ein abwesender oder nicht reagierender Inhaber den Implementierungslauf nicht blockiert.
91. Als Team möchte ich für einen Forced Takeover keine zusätzliche Administratorrolle benötigen, damit der Prototyp kein unnötiges privilegiertes Rollenmodell einführt.
92. Als neuer Steuernder möchte ich nach einem Forced Takeover exklusiv mutierende Rechte erhalten, damit die bisherige Control Lease nicht parallel wirksam bleibt.
93. Als bisheriger Steuernder möchte ich den Forced Takeover in der Run History sehen, damit der Verantwortungswechsel nicht verborgen erfolgt.
94. Als Teammitglied möchte ich bisherigen und neuen Inhaber, Zeitpunkt, Implementierungslauf und erzwungene Übergabeart nachvollziehen können, damit Forced Takeovers auditierbar sind.
95. Als Prozessverantwortlicher möchte ich Forced Takeovers als eigenes Signal in einer Agent Evolution Loop auswerten, damit wiederkehrende Übergabe- oder Blockademuster sichtbar werden.
96. Als Prozessverantwortlicher möchte ich Interventionsanfragen, Control Commands, Forks und Retries gemeinsam mit Forced Takeovers betrachten, damit die Agent Evolution Loop den gesamten menschlichen Eingriffsbedarf bewertet.
97. Als Entwickler möchte ich source-code-relevante Domainbegriffe, Eventnamen und Interfaces durchgehend auf Englisch verwenden, damit keine deutsch-englischen Wortkonstrukte in den Code übergehen.
98. Als Agent Maintainer möchte ich Prompts, Skills, Tools, Agent Policies, Integrationen und Zugriffe gemeinsam in einem versionierten Agent Definition Repository verwalten, damit deren Zusammenspiel als eine Agentendefinition verbessert werden kann.
99. Als Agent Maintainer möchte ich, dass die Agent Evolution Loop Änderungen an jedem Teil eines Agent Definition Repository vorschlagen und ausarbeiten darf, damit ihre Verbesserung nicht künstlich auf Prompts beschränkt bleibt.
100. Als Agent Maintainer möchte ich jede vorgeschlagene Änderung im jeweiligen GitHub-Repository prüfen können, damit Herkunft, Diff und Evaluation nachvollziehbar sind.
101. Als Agent Maintainer möchte ich, dass keine Agent-Definition-Änderung ohne menschliche Freigabe verwendet wird, damit die Agent Evolution Loop ihre eigene Governance nicht umgehen kann.
102. Als Prozessverantwortlicher möchte ich jeden Änderungsvorschlag auf konkrete Run-History-, Evaluations- oder Prozesssignale zurückführen können, damit die Lernschleife evidenzbasiert bleibt.
103. Als Architekt möchte ich Agent Definition Repository und Work Package Control Plane als getrennte Domainkonzepte verwenden, damit „Platform“ nicht für zwei unterschiedliche Verantwortungsbereiche steht.
104. Als Agent Maintainer möchte ich Agent Definition Repositories unabhängig von der Work Package Control Plane versionieren können, damit Agentenfähigkeiten und Orchestrierung getrennt evolvieren.
105. Als Betreiber möchte ich, dass jeder Agentenaufruf seine verwendete Agent-Definition-Revision aufzeichnet, damit historische Ergebnisse reproduzierbar bleiben.
106. Als Betreiber möchte ich eine menschlich freigegebene neue Agent-Definition-Revision auch in einem bereits aktiven Implementierungslauf für nachfolgende Agentenaufrufe verwenden können, damit kein unnötiges Pinnen bis zum Laufabschluss erforderlich ist.
107. Als Betreiber möchte ich eine bereits laufende Agentenoperation nicht rückwirkend auf eine neue Agent-Definition-Revision umstellen, damit ihr konkreter Ausführungskontext konsistent bleibt.
108. Als Agent Maintainer möchte ich jede Agent-Definition-Änderung nach dem Vier-Augen-Prinzip prüfen lassen, damit kein Autor seine eigene Änderung allein aktiviert.
109. Als Agent Maintainer möchte ich dafür die vorhandenen geschützten Branches und Pull oder Merge Requests meines Repository Providers verwenden, damit kein paralleler Freigabeprozess entsteht.
110. Als Betreiber möchte ich GitHub, GitLab und Azure DevOps über denselben fachlichen Agent-Definition-Approval-Vertrag anbinden können, damit die Control Plane nicht an einen Provider gekoppelt ist.
111. Als Betreiber möchte ich, dass die Work Package Control Plane ausschließlich extern qualifizierte Agent-Definition-Revisionen verwendet, damit sie Repository Governance nicht umgehen kann.
112. Als Betreiber möchte ich keine Rollen, Reviewer oder Branch-Protection-Regeln für Agent Definition Approval in der Work Package Control Plane verwalten, damit die Verantwortungsgrenze klar bleibt.
113. Als Teammitglied möchte ich mich am Operator Client mit meiner bestehenden GitHub-, GitLab- oder Azure-DevOps-Identität anmelden, damit keine zweite Benutzeridentität gepflegt werden muss.
114. Als Betreiber möchte ich jeden Implementierungslauf eindeutig einem Repository zuordnen, damit seine Zugriffsautorität eindeutig bestimmt ist.
115. Als Teammitglied möchte ich Zugriff auf einen Implementierungslauf aus meiner aktuell wirksamen Repositoryberechtigung erhalten, damit direkte, geerbte und gruppenbasierte Rechte des Providers berücksichtigt werden.
116. Als Betreiber möchte ich keine eigene Mitglieder- oder Zugriffsliste für Implementierungsläufe verwalten, damit Repositoryzugriff nicht in zwei Systemen auseinanderlaufen kann.
117. Als Betreiber möchte ich Providerberechtigungen über einen einheitlichen Repository-Authorization-Vertrag in beobachtende und mutierende Aktionen übersetzen, damit GitHub, GitLab und Azure DevOps trotz unterschiedlicher Rechtekonzepte austauschbar bleiben.
118. Als Sicherheitsverantwortlicher möchte ich entzogene Repositoryrechte zeitnah bei neuen Verbindungen und mutierenden Aktionen wirksam sehen, damit eine alte Operator-Session keinen dauerhaften Zugriff erhält.
119. Als Teammitglied möchte ich im Operator Client nur die für mich erlaubten Run-History- und Steuerungsaktionen sehen, damit die Oberfläche den tatsächlichen Autorisierungszustand verständlich wiedergibt.
120. Als Steuernder möchte ich über eine Texteingabe einen Control Command an den bestehenden Implementierungslauf senden, damit meine Einflussnahme keine zusätzliche Agentensession und keinen getrennten Verlauf erzeugt.
121. Als Teammitglied mit Repository-Lesezugriff möchte ich die Run History beobachten können, ohne den Implementierungslauf verändern zu dürfen.
122. Als Teammitglied mit Schreib- oder Contributor-Zugriff möchte ich die Control Lease beanspruchen, einen Control Transfer ausführen, einen Forced Takeover auslösen und Control Commands senden können, damit mutierende Steuerung auf beitragsberechtigte Repositorymitglieder begrenzt bleibt.
123. Als Steuernder möchte ich die Control Lease bei einem Verbindungsabbruch des Operator Clients behalten, damit fachliche Verantwortung nicht von einer Browser-, Terminal- oder Netzwerkverbindung abhängt.
124. Als anderer Contributor möchte ich eine verwaiste Control Lease weiterhin per Control Transfer oder Forced Takeover übernehmen können, damit eine getrennte Work Machine den Implementierungslauf nicht blockiert.
125. Als Steuernder möchte ich einen Control Command an einen expliziten Activity Attempt richten, damit bei parallelen Aktivitäten kein falscher Agent beeinflusst wird.
126. Als Entwickler möchte ich, dass ein neuer Implementierungslauf erst auf der autoritativen Repository-Base nach Abschluss seiner Blocker beginnt, damit keine Änderung auf einem veralteten lokalen Branch entsteht.
127. Als Betreiber möchte ich vor Beginn teurer Agentenarbeit sehen, ob Verträge, Werkzeuge, Abhängigkeiten, Zugriffe, Sandbox-Rechte und benötigte Evidence-Oberflächen verfügbar sind, damit fehlende Voraussetzungen früh und handlungsfähig sichtbar werden.
128. Als Entwickler möchte ich unvollständige Evidence nach fertiger Implementierung gezielt nacherfassen oder korrigieren können, damit ein fehlender Screenshot oder Read-back nicht den gesamten Lauf dauerhaft blockiert.
129. Als Betreiber möchte ich schema-, prozess-, transport-, infrastruktur- und fachliche Fehler getrennt sehen und das ursprüngliche redigierte Worker-Ergebnis behalten, damit eine nachgelagerte Ablehnung nicht zur generischen Fehlermeldung wird.
130. Als Betreiber möchte ich Run-, Attempt-, Prozess- und Heartbeat-Zeiten sowie die tatsächlich eingesetzten Runtime-, Vertrags- und Konfigurationsversionen getrennt sehen, damit Alter, Timeout und Deployment-Drift nicht verwechselt werden.
131. Als Freigeber möchte ich, dass ausschließlich meine explizite interaktive und authentifizierte Aktion das menschliche Approval-Gate erfüllt, damit kein Monitor, Scheduler, Worker oder Service-Token meine Freigabe simuliert.
132. Als Betreiber möchte ich den zusätzlichen Agent-Framework-Piloten unabhängig neben dem bestehenden LangGraph-Piloten ausführen können, damit dessen Code, Cloudflare-Anbindung, macOS-Betrieb, Laufzeitdaten und ProBara-CRM-Konfiguration unverändert bleiben.
133. Als Entwickler möchte ich einen konkreten fehlgeschlagenen, wartenden oder aktiven Aktivitätsversuch aus dem Operator Client in Codex öffnen können, damit ich die Session im vertrauten Werkzeug untersuchen und – mit gültiger Control Lease – kontrolliert fortführen kann, ohne einen unverbundenen Nebenverlauf zu erzeugen.

## Fachliche Regeln und Grenzen

- Ein autorisierter Issue-Auftrag erzeugt höchstens einen dauerhaften Implementierungslauf. Der Lauf bündelt Implementierung, Verifikation, Review, Reparatur, Intervention, Freigabe und Abschluss und überlebt Benutzer-, Rechner-, Worker- und Prozesswechsel.
- Ein Lauf kann mehrere fachlich benannte Aktivitäten und Versuche enthalten. Agentische Aktivitäten verwenden standardmäßig eine neue, begrenzte Codex-Session; regelbasierte Entscheidungen wie Autorisierung, Scheduling, Git-Wirkungen, Tests, Qualification und Freigabepolitik bleiben außerhalb des Modells.
- Codex bleibt der Agent-Harness. Die Workflow-Technologie ist austauschbar und muss die Anforderungen über ihre öffentlichen Produktoberflächen beweisen.
- Der Agent-Framework-Pilot ergänzt den bestehenden LangGraph-Piloten in einem getrennten Repository-Ordner. Beide bleiben unabhängig ausführbar und teilen weder schreibbare Laufzeitdaten noch Worktrees.
- Der Workflow-Stack benötigt einen produktionsfähigen, selbst hostbaren Open-Source-Pfad ohne verpflichtende zusätzliche Framework- oder Managed-Workflow-Service-Lizenzkosten. Temporal und kostenpflichtige Managed-Workflow-Dienste sind weder Kandidaten noch Fallbacks.
- Alle für Betrieb und Diagnose beobachtbaren Aktivitäten, Nachrichten, Toolaufrufe, Ergebnisse, Fehler, Artefakte, Zustandswechsel, menschlichen Entscheidungen und verwendeten Revisionen erscheinen kausal geordnet in einer gemeinsamen Run History. Private interne Gedankengänge des Modells werden nicht vorausgesetzt oder versprochen.
- Geheimnisse und konfigurierte personenbezogene Daten werden vor jeder dauerhaften Speicherung oder Anzeige redigiert. Große Nachweise bleiben unveränderlich referenziert und zusammen mit der fachlichen Historie portabel exportierbar.
- Berechtigte Personen können denselben Lauf von getrennten, zustandsarmen Clients beobachten. Nach einer Unterbrechung setzt ein Client ab seiner zuletzt bestätigten Position ohne Lücken, Duplikate oder Umordnung fort.
- Genau ein berechtigter Mensch besitzt die laufweite Control Lease für mutierende Eingriffe; weitere Berechtigte dürfen gleichzeitig beobachten. Die Lease ist an die Provideridentität gebunden, überlebt Clientabbrüche und wird durch Release, bewilligten Transfer, Forced Takeover oder Rechteentzug beendet.
- Transfer und Forced Takeover wechseln die Control Lease atomar und entwerten veraltete Steuerungsversuche. Anfrage, Entscheidung, Wechsel und abgelehnte veraltete Aktionen bleiben auditierbar; für den Forced Takeover ist im Pilot keine zusätzliche Administratorrolle erforderlich.
- Menschliche Commands adressieren einen expliziten aktiven Versuch. `interrupt` stoppt die laufende Operation kontrolliert und stellt den angenommenen Command nach Wirkungsabgleich als Nächstes zu; `queue` bewahrt die sichtbare Annahmereihenfolge bis zum Abschluss der laufenden Operation.
- `Resume` führt dieselbe Session fort, `Fork` beginnt einen neuen Lösungszweig mit nachvollziehbarer Herkunft und `Fresh Retry` beginnt ohne automatische Übernahme der bisherigen Agentenkonversation. `Cancel`, Human Requests und Antworten bleiben davon unterscheidbar und dauerhaft nachvollziehbar.
- `Open in Codex` adressiert den ausgewählten Aktivitätsversuch. Das System öffnet nach Möglichkeit dieselbe Codex-Session; ist dies nicht sicher unterstützt, weist es die Einschränkung aus und darf nur nach expliziter Bestätigung einen neuen Handoff-Fork mit Herkunft erzeugen. Schreibende Interaktion setzt die Control Lease voraus und wird in die Run History zurückgeführt.
- Ein menschlich ausgelöster Abbruch ist kein Agentenfehler und verbraucht keine fachliche Reparaturrunde. Vor der Fortsetzung werden bereits eingetretene externe Wirkungen abgeglichen und sicher adoptiert oder als Konflikt sichtbar gemacht.
- Initiator, Interventionsbearbeiter, Freigeber und Merger sind unabhängige Rollen. Menschliche Identitäten und technische Service-Identitäten bleiben für Autorisierung und Audit getrennt.
- Der jeweilige Repository-Provider bleibt die Autorität für Mitgliedschaft und wirksame Berechtigungen. Lesezugriff erlaubt Beobachtung; zulässige Mutationen erfordern zusätzlich aktuelle Schreibberechtigung, die Control Lease und alle fachlichen Vorbedingungen.
- Agent Definition Repository und Work Package Control Plane bleiben getrennte fachliche Verantwortungen. Änderungen an Agentendefinitionen dürfen vorgeschlagen und vorbereitet, aber erst nach externer menschlicher Repository-Freigabe verwendet werden; jeder Agentenversuch nennt die verwendete Definition.
- Ein Lauf oder Reparaturversuch beginnt nur auf einer aufgezeichneten, provider-autoritativ bestätigten Base-SHA. Eine veraltete lokale Referenz darf keinen Nachfolger starten oder publizieren.
- Vor teurer Agentenarbeit wird geprüft, ob benötigte Verträge, Werkzeuge, Abhängigkeiten, Zugriffe, Ausführungsrechte und Evidence-Oberflächen tatsächlich verfügbar sind. Fehlende Voraussetzungen werden als konkrete menschliche Anfrage oder expliziter Blocker sichtbar.
- Externe Wirkungen besitzen eine stabile fachliche Identität und können nach einem Abbruch abgeglichen werden. Recovery setzt nur fehlende Arbeit fort und rät bei mehrdeutigen oder widersprüchlichen Wirkungen nicht.
- Qualification gilt immer für genau eine Head-SHA. Sie verlangt deterministische Verifikation und frische, kontextisolierte Requirements-, Code- und Architektur-Reviews; ein neuer Writer-Head entwertet alle bisherigen Verdicts.
- Schema-Validität allein qualifiziert weder ein Worker-Ergebnis noch Evidence. Semantisch unvollständige Evidence erhält einen begrenzten Nacherfassungspfad; andernfalls endet der Lauf explizit blockiert und gibt die Repository-Serialisierung nach Policy frei.
- Das redigierte beobachtbare Originalergebnis eines Workers bleibt vor jeder nachgelagerten Interpretation erhalten. Prozessfehler, Timeout, Transportfehler, Vertragsinkompatibilität, Schemafehler, gültiger Blockzustand, Evidence-Ablehnung und Infrastrukturfehler bleiben unterscheidbar.
- Run-, Attempt-, Prozess- und Heartbeat-Zeit sowie eingesetzte Source-, Paket-, Konfigurations-, Vertrags- und Agent-Definitionsrevisionen werden getrennt ausgewiesen. Inkompatible Kombinationen blockieren vor dem Issue-Start.
- Recovery, Retry, Retire und Reconcile sind über öffentliche Produktoberflächen ausführbar; manuelle Änderungen an Laufzeitdatenbanken sind kein vorgesehener Betriebsweg.
- Approval verlangt eine explizite interaktive Aktion eines authentifizierten und berechtigten Menschen für den qualifizierten Head. Monitor, Scheduler, Worker, Service-Identität und Hintergrundautomation dürfen Bereitschaft melden, aber weder Approval noch Mark-ready, Merge, Deployment oder Release im Namen eines Menschen ausführen.
- Der erste Agent-Framework-Spike beweist den anspruchsvollen fachlichen Schnitt mit drei Menschen: Start und beobachtbarer Fehler, Remote-Übernahme und bewusste Fortsetzung, erneute Qualification sowie interaktive Freigabe – ohne Merge, Deployment oder Release.

## Fachliche Abnahmegrundsätze

- Die primäre Abnahme erfolgt über die öffentliche Work-Package-Oberfläche sowie die fachlich autoritativen Repository- und Artefaktoberflächen. Private Workflow-Reihenfolgen und Datenbanktabellen sind kein Ersatz für beobachtbares Produktverhalten.
- Der höchste vollständige Systemtest startet ein freigegebenes Issue über den produktionsnah authentifizierten Eingang, lässt einen zentralen Codex-Testworker nach mehreren beobachtbaren Schritten kontrolliert scheitern und liest denselben Implementierungslauf anschließend über einen zweiten authentifizierten Client.
- Der Systemtest beweist, dass der zweite Benutzer Nachrichten, Toolaufrufe, Ergebnisse, Artefakte, Head-SHA und Fehlerursache des gescheiterten Versuchs sieht, ohne Zugriff auf den ursprünglichen Worker oder dessen Work Machine zu benötigen.
- Derselbe Systemtest lässt den zweiten Benutzer eine explizite Resume-, Fork- oder Fresh-Retry-Entscheidung treffen, prüft deren Korrelation mit Session, Versuch und Head und beobachtet genau eine Fortsetzung ohne doppelte externe Wirkung.
- Der Systemtest lässt einen dritten berechtigten Benutzer den frisch qualifizierten Head freigeben und beweist, dass Initiator, Fehlerbeheber und Freigeber verschieden sein dürfen.
- Ein konkurrierender zweiter Interventionsversuch muss an Lease oder Compare-and-Swap scheitern, ohne einen weiteren Writer, Commit oder Agentenlauf zu erzeugen.
- Ein veralteter Browserzustand mit alter Head-SHA muss abgelehnt werden und die aktuelle Aktivitätshistorie zur erneuten Entscheidung anbieten.
- Prozess-, Worker- und Control-Plane-Neustarts werden an den Grenzen vor und nach Agentenstart, Toolwirkung, Fehlerpersistierung, menschlicher Entscheidung und Fortsetzung erzwungen. Danach wird der Implementierungslauf über die öffentliche Seam erneut gelesen und nur der fehlende Effekt fortgesetzt.
- Context-Isolation wird extern geprüft: unabhängige Reviewer erhalten dieselbe Head-SHA, aber keine gegenseitigen Verdicts oder fremden aktiven Gesprächskontexte. Gleichzeitig bleiben ihre vollständigen beobachtbaren Traces im gemeinsamen Implementierungslauf lesbar.
- Fork wird als neue Session mit Herkunftsreferenz beobachtet; Resume behält die Session-Identität; Fresh Retry erzeugt eine neue Session ohne automatische Übernahme der alten Unterhaltung. Alle drei Varianten behalten die alte Historie unverändert.
- Ein Open-in-Codex-Test öffnet vom Operator Client aus den ausgewählten Aktivitätsversuch. Er beweist entweder dieselbe Session-Identität oder einen vorab bestätigten, eindeutig gekennzeichneten Handoff-Fork; ein stiller Sessionwechsel, eine Mutation ohne Control Lease oder ein zweiter unkorrelierter Verlauf schlägt fehl.
- Live Control wird über die öffentliche Seam in beiden Modi geprüft: `interrupt` stoppt eine kontrolliert laufende Agentenoperation und verarbeitet genau einen Control Command als Nächstes; `queue` lässt die Operation abschließen und verarbeitet mehrere Commands anschließend in ihrer dauerhaft sichtbaren Reihenfolge.
- Ein Prozessneustart zwischen Persistierung und Zustellung eines gequeueten Control Commands darf den Command weder verlieren noch doppelt zustellen. Ein Neustart nach einem Interrupt muss bereits eingetretene externe Wirkungen übernehmen und den korrigierenden Command genau einmal verarbeiten.
- Sicherheitsprüfungen injizieren erkennbare Tokens, Zugangsdaten und personenbezogene Werte in kontrollierte Toolausgaben und beweisen über Cockpit/API und Artefaktzugriff, dass diese Werte redigiert sind.
- Berechtigungsprüfungen beweisen Repository-Lesezugriff für Beobachtung sowie Schreib- oder Contributor-Zugriff plus Control Lease für mutierende Operator-Aktionen. Ein nur lesender Benutzer darf die Historie sehen, aber keine Session fortsetzen oder einen Head freigeben; ein eigenes Administratorrecht der Control Plane existiert nicht.
- Provider-Vertragstests liefern direkte, geerbte und entzogene Repositoryrechte und beweisen dieselbe normalisierte Repository-Authorization-Entscheidung an der öffentlichen Control-Plane-Oberfläche.
- Ein Repository-Authorization-Systemtest meldet zwei Menschen über den Provider an, lässt den berechtigten Beobachter dieselbe Run History lesen und prüft für jede mutierende Aktion sowohl Providerberechtigung als auch Control Lease.
- Ein Benutzer mit ausschließlich effektivem Repository-Lesezugriff kann die Run History lesen, aber weder eine Control Lease beanspruchen noch Control Transfer, Forced Takeover oder Control Command auslösen. Derselbe Test gewährt Schreib- oder Contributor-Zugriff und beobachtet, dass die Aktionen erst dann grundsätzlich autorisiert werden.
- Nach Entzug der Repositoryberechtigung darf ein neuer Verbindungsversuch nicht mehr lesen. Eine bereits verbundene Session muss spätestens bei der nächsten sicherheitsrelevanten Mutation revalidiert und abgelehnt werden.
- Tests konfigurieren oder spiegeln keine eigene Control-Plane-Mitgliedschaft. Benutzer- und Gruppenverwaltung des Providers wird an der Adaptergrenze kontrolliert und nicht innerhalb der Control Plane nachimplementiert.
- UI-Evidence zeigt den Implementierungslauf, die Aktivitätstimeline, den konkreten Fehler, die verfügbaren Fortsetzungsoptionen, den Benutzerwechsel und den final qualifizierten Head. Logs allein gelten nicht als Verhaltensnachweis.
- Ein Systemtest des Operator Client liest einen zusammenhängenden Stream aus mindestens zwei unterschiedlichen Codex-Sessions und einer deterministischen Aktivität, trennt ihn bei Bedarf nach Session und setzt nach Client-Neustart ohne Lücke oder Duplikat an der bestätigten Eventposition fort.
- Ein Control-Lease-Test beweist, dass genau ein authentifizierter Benutzer die Control Lease beansprucht, ein zweiter Benutzer dieselbe Run History lesen kann, dessen mutierender Command jedoch ohne Lease abgelehnt wird.
- Ein Reconnect-Test trennt sämtliche Operator Clients des Lease-Inhabers, verbindet denselben Menschen erneut und beweist, dass die Control Lease weder freigegeben noch einer Clientinstanz zugeordnet wurde. Ein anderer Contributor kann sie weiterhin nur über Control Transfer oder Forced Takeover erhalten.
- Ein Authorization-Revocation-Test entzieht dem Lease-Inhaber den erforderlichen Schreib- oder Contributor-Zugriff und beweist, dass seine Lease keine weitere Mutation autorisiert, obwohl ein bloßer Clientabbruch sie nicht beendet hätte.
- Derselbe Test startet parallele Review-Aktivitäten und beweist, dass keine davon separat durch einen anderen Menschen beansprucht oder gesteuert werden kann.
- Ein Control-Transfer-Test lässt einen Beobachter die Control Lease anfragen, beweist vor der Bewilligung weiterhin ausschließlich die Rechte des bisherigen Inhabers und beobachtet nach dessen Bewilligung einen atomaren Rollenwechsel ohne überlappende mutierende Rechte.
- Wiederholte Anfrage- oder Bewilligungszustellung darf keine zweite Übergabe erzeugen; eine Bewilligung für eine veraltete Anfrage oder einen inzwischen gewechselten Inhaber wird abgelehnt.
- Ein Forced-Takeover-Test wechselt die Control Lease ohne Zustimmung und ohne Administratoridentität atomar zu einem anderen zugriffsberechtigten Benutzer, lehnt danach alte mutierende Requests des bisherigen Inhabers ab und bewahrt dessen Lesezugriff.
- Workflow-Phase, aktive Agentensession und bereits akzeptierte externe Wirkungen bleiben durch den Forced Takeover unverändert; die Run History zeigt den erzwungenen Wechsel genau einmal.
- Eine Agent-Evolution-Loop-Projektion liefert Forced Takeovers und andere menschliche Eingriffe als getrennte, korrelierte Ereignistypen, ohne ihre Bedeutung aus unstrukturierter Logprosa ableiten zu müssen.
- Ein Agent-Definition-Änderungstest lässt die Agent Evolution Loop einen versionierten Änderungsvorschlag mit Herkunft und Evaluation im betroffenen Agent Definition Repository erzeugen und beweist, dass die ungeprüfte Änderung weder laufende noch neue Agentenaufrufe beeinflusst.
- Erst ein kontrolliertes menschliches Approval-Ereignis darf die neue Agent-Definition-Revision zur Verwendung qualifizieren; die Agent Evolution Loop darf ihr eigenes Approval weder erzeugen noch simulieren.
- Ein providerneutraler Contract-Test liefert eine ungeprüfte und eine nach Vier-Augen-Regeln gemergte Agent-Definition-Revision aus kontrollierten GitHub-, GitLab- und Azure-DevOps-Adaptern. Nur die extern qualifizierten Revisionen werden für neue Agentenaufrufe auswählbar.
- Tests der Work Package Control Plane konfigurieren, verändern oder duplizieren keine Branch-Protection-Regeln und prüfen nicht die internen Reviewregeln des Repository Providers.
- Ein aktiver Implementierungslauf startet nach dieser Freigabe einen späteren Agentenaufruf mit der neuen Revision, während eine zum Freigabezeitpunkt bereits laufende Operation weiterhin ihre zuvor aufgezeichnete Revision verwendet.
- Ein Routing-Test sendet ein Kommando an Implementierungslauf und expliziten Activity Attempt und beobachtet, dass ausschließlich die daraus zentral aufgelöste Codex-Session es genau einmal erhält. Bei mehreren aktiven Versuchen wird ein Kommando ohne Ziel abgelehnt.
- Ein Sequenztest merged einen Blocker, lässt die lokale Referenz absichtlich veraltet und beweist, dass der Nachfolger erst auf der provider-autoritativ bestätigten Base-SHA startet.
- Ein Readiness-Test entzieht jeweils Evidence-Oberfläche, Dependency, Sandbox-Recht und Vertragskompatibilität und beweist einen frühen sichtbaren Blocker ohne teuren Agentenstart.
- Ein Evidence-Recovery-Test liefert ein schema-valides Ergebnis mit fehlender Request-, Response-, Repeat-, Read-back- oder Screenshot-Phase und beweist entweder die begrenzte Nacherfassung oder einen expliziten Blockzustand ohne Repository-Deadlock.
- Ein Failure-Fidelity-Test lässt eine nachgelagerte Verarbeitung ein gültiges `blocked`-Ergebnis ablehnen und beweist, dass Originalergebnis und getrennte Ablehnungsursache in der Run History erhalten bleiben.
- Ein Runtime-Provenance-Test setzt Source-, Package-, Contract- oder Konfigurationsversion absichtlich auseinander und beweist eine Startablehnung mit sichtbarer Versionskorrelation.
- Ein Human-Gate-Test lässt einen Monitor einen qualifizierten Head erkennen und beweist, dass er nur benachrichtigen kann; Approval und Merge bleiben ohne interaktive menschliche Aktion aus.
- Als Prior Art dienen die bestehenden Systemtests und ProBara-CRM-Sessions des LangGraph-Piloten. Der zusätzliche Pilot übernimmt deren öffentliche Verhaltensverträge, nicht ihre konkrete Workflow-, Storage-, Cloudflare- oder macOS-Implementierung.
- Niedrigere Adaptertests dürfen Codex-, Workflow-, Artifact-Store- und Identity-Provider-Verträge absichern, ersetzen aber nicht den vollständigen Rollenwechsel- und Fehlerbehebungsfall.

## Out of Scope

- Ein Wechsel von Codex zu Claude, GitHub Copilot oder einem anderen primären Agent-Harness.
- Die Behauptung, private interne Gedankengänge oder versteckte Chain-of-Thought-Inhalte des Modells speichern oder anzeigen zu können.
- Automatischer Merge, Deployment, Release oder eine autonome Produktfreigabe.
- Temporal und verpflichtende kostenpflichtige Managed-Workflow-Dienste als Kandidat oder Fallback.
- Produktionsreife Hochverfügbarkeit, globale Multi-Region-Verteilung, verbindliche SLOs und Capacity Planning für Organisationen oberhalb des zunächst betrachteten Teams.
- Eine vollständige Unternehmensintegration in einen konkreten Identity Provider; der Prototyp muss Rollen und mehrere Identitäten beweisen, aber nicht jeden späteren SSO- und Provisioning-Prozess implementieren.
- Konfiguration oder Verwaltung von Branch Protection, Reviewergruppen und Merge Policies in GitHub, GitLab oder Azure DevOps; diese Regeln gehören zur bestehenden Repository Governance.
- Eine eigene Mitglieder-, Gruppen- oder Repository-ACL-Verwaltung in der Work Package Control Plane; diese bleibt beim jeweiligen Repository Provider.
- Eine allgemeine Projektmanagement-, Sprintplanung- oder Ticketing-Plattform neben dem GitHub-gebundenen Implementierungslauf.
- Unbegrenzte Parallelisierung schreibender Agenten innerhalb desselben Repositorys oder gestapelte Pull Requests im ersten Prototyp.
- Das automatische Laden der vollständigen Aktivitätshistorie in jeden neuen Agentenkontext.
- Eine endgültige Aufbewahrungs- und Compliance-Policy für produktive Unternehmensdaten; der Prototyp muss Redaction, Zugriffstrennung und konfigurierbare Retention als Architekturgrenzen beweisen.

## Weitere Hinweise

- Der bestehende LangGraph-Pilot einschließlich Cloudflare-Relay und macOS-Betrieb bleibt als implementierte Verhaltensbaseline bestehen. Der zusätzliche Pilot verändert oder ersetzt ihn nicht.
- Der heute verwendete Ansatz, für eine Interventionsanfrage eine neue zusammenfassende Codex-Task zu öffnen, erfüllt die neue Anforderung nicht. Die Interventionsoberfläche muss den tatsächlichen fehlgeschlagenen Aktivitätsversuch und seine beobachtbare Historie zeigen.
- Der Operator Client ersetzt die zusätzliche zusammenfassende Codex-Task als Quelle der Wahrheit. Er stellt die zentral persistierte Run History dar, leitet Commands an die Control Plane weiter und bietet für einen konkreten Aktivitätsversuch `Open in Codex`; die geöffnete Ansicht bleibt mit Lauf, Versuch, Session und Control Lease korreliert.
- Die aktuelle Codex CLI bietet in der lokal geprüften Version persistente Session-Identitäten, JSONL-Ereignisse sowie Resume- und Fork-Befehle. Diese Fähigkeiten sind ein guter Spike-Ausgangspunkt, müssen aber über einen versionierten Adapter und gegen die am Arbeitsplatz zulässige Codex-Distribution verifiziert werden.
- Der Begriff „Implementierungslauf“ bleibt die fachliche Klammer aus dem bestehenden Domain-Glossar. „Work Package“ bezeichnet in der Diskussion dieselbe zentrale, issuegebundene Benutzeransicht und sollte bei einer späteren Domain-Modellierung entweder als offizieller Begriff aufgenommen oder ausdrücklich als UI-Bezeichnung dem Implementierungslauf zugeordnet werden.
- Vor einer breiten Einführung soll der zusätzliche Pilot absichtlich den Fehlerpfad vor dem Happy Path perfektionieren: Ein anderer Mensch muss den gescheiterten zentralen Agenten verstehen und korrekt fortsetzen können, ohne dessen Rechner, private Nebenkommunikation oder einen vollständigen Kontextdump zu benötigen.

## Decision Boundary for the Prototype

- Der Requirements-Audit hat keine weitere offene Produktentscheidung ergeben, die den ersten vertikalen Prototyp blockiert. Die Grill-with-Docs-Befragung ist damit fachlich abgeschlossen.
- Reversible Entscheidungen zu Web- oder Terminaldarstellung, konkretem Event- und Storage-Schema, Cache- und Token-Laufzeiten, Heartbeats, Retry-Intervallen, Frameworkstruktur und Deploymenttopologie trifft das Umsetzungsteam innerhalb der beschriebenen Verhaltens- und Sicherheitsgrenzen.
- Die genaue Open-Source-Workflow- und Codex-Adapteroberfläche sowie die Reihenfolge realer Provideradapter sind Architektur-Spikes. Sie werden anhand des vollständigen Fehler-, Remote-Interventions- und Rollenwechselfalls entschieden und nicht als weitere Geschmacksfragen an den Product Owner delegiert.
- Der erste reale Provider darf der bestehende GitHub-Pilot sein, solange Repository Authorization und Agent Definition Approval providerneutral geschnitten und GitLab sowie Azure DevOps durch Contract-Seams anschliessbar bleiben.
- Eine neue menschliche Produktentscheidung wird erst erforderlich, wenn ein Spike zeigt, dass eine gesetzte Semantik nicht erfüllbar ist oder eine Alternative Sichtbarkeit, Steuerungsrechte, Autonomiegrenzen, Datenschutz oder irreversible externe Wirkungen verändert.

## Erfahrungsrückfluss aus den ProBara-CRM-Pilotsessions

Diese Hinweise sind verbindlicher Input für die spätere Ticketzerlegung. Eine Beobachtung wird entweder durch eine fachliche Regel geschlossen oder ausdrücklich als Architektur-/Testpflicht referenziert, damit der zusätzliche Pilot bekannte Fehler nicht wiederholt.

| Verifizierte Beobachtung | Einordnung | Konsequenz für PRD oder Tickets |
| --- | --- | --- |
| Der sequenzielle Nachfolger startete vom veralteten lokalen `main`, obwohl der Blocker bereits auf dem Provider gemergt war. | Fachliche Zuverlässigkeitslücke | US 126 und die Regel zur provider-autoritativen Base-SHA; Ticket muss den Stale-Base-Test enthalten. |
| Worker scheiterten spät an fehlender Mailbox-Anbindung, nicht verfügbarem Frontend-Cache, Browser-/Loopback-Beschränkung und Git-Metadaten außerhalb der Sandbox. | Teilweise fachliche Readiness-Lücke, teilweise Ausführungsdesign | US 127; jedes Ausführungsticket benötigt einen Prerequisite-/Sandbox-/Evidence-Preflight und klare Effektverantwortung. |
| Die installierte Runtime verwendete ältere Worker-Verträge als der getestete Source-Stand. | Operability-/Deployment-Lücke | US 130; Bootstrap-Ticket muss Source-, Package-, Config- und Contract-Provenance prüfen und inkompatible Starts ablehnen. |
| Ein an Codex übergebenes JSON Schema enthielt eine dort nicht unterstützte Konstruktion, obwohl das kanonische Schema lokal gültig war. | Adapter- und Contract-Testlücke | Agent-Session-Ticket muss den tatsächlich unterstützten Schema-Subset verhandeln und gegen den echten Prozess-Endpunkt testen. |
| Ein schema-valides Worker-Ergebnis enthielt nicht die semantisch erforderlichen REST-, Idempotenz- und UI-Evidence-Phasen. | Fachliche Evidence-Lücke plus Assignment-Vertragslücke | US 128; Evidence-Ticket muss geforderte Phasen im Auftrag explizit machen und schema-valide, aber unzureichende Evidence nacherfassen oder blockieren. |
| Nach Evidence-Rejection blieb der Run `running`, `agent-running` blieb gesetzt und die Repository-Serialisierung blockierte alle Nachfolger. | Fachliche Zustands-/Recovery-Lücke | Evidence- und Recovery-Tickets müssen vollständige Zustandskonvergenz und Freigabe der Serialisierung über die öffentliche Oberfläche beweisen. |
| Eine gültige `outcome: blocked`-Antwort wurde als generisches `InvalidWorkerResult` gespeichert; JSONL und konkrete Ursache gingen verloren. | Fachliche Diagnose-/Audit-Lücke | US 129; Adapter-Ticket persistiert das redigierte Original vor Parsing und trennt Adapter-, Contract- und Fachfehler. |
| Monitoring verwechselte Alter des Runs, Laufzeit des Recovery-Versuchs und Schlafzeit des Hosts. | Observability-/Testlücke | US 130; Event-/Operator-Ticket modelliert getrennte Zeitachsen und darf Timeout nicht aus einem fremden Alterswert ableiten. |
| Normale headless `codex exec`-Sessions waren nicht als sichtbare Codex-App-Tasks gelistet, obwohl sie per ID lesbar waren. | Fachliche Übergabe- und Integrationslücke | US 133; Run-History und Adapter dürfen App-Task-Sichtbarkeit nicht voraussetzen, müssen aber für den konkreten Versuch eine verlässliche `Open in Codex`-Aktion mit Same-Session- oder expliziter Handoff-Fork-Semantik anbieten. |
| Recovery erforderte Backups und gezielte manuelle Änderungen an SQLite-Zustand, um einen rejected Run zu retiren und neu zuzustellen. | Fachliche Operability-Lücke | Recovery-/Operator-Ticket stellt unterstützte Retry-, Retire-, Reconcile- und Adopt-Commands bereit; Datenbankmanipulation ist kein Akzeptanzweg. |
| Eine Überwachungsautomation war beauftragt, qualifizierte PRs selbst „ready“ zu schalten und zu mergen. | Fachliche Autonomie-/Governance-Lücke | US 131 und ausdrückliches Verbot der Human-Gate-Imitation; Monitor darf ausschließlich informieren und Bereitschaft projizieren. |

Sessionquellen:

- `Implement backlog tickets sequential` — `01a02ed5-bc43-7702-bc36-b326f6859839`
- `Diagnose fehlgeschlagener Issue-2-Um…` — `01a0326d-f61e-7e00-b76d-3dee0e9295ad`
- `Diagnose LangGraph workflow pause` — `01a03a64-b1c8-7ba1-9493-f27b41beb7c2`

Die ältere LangGraph-PRD und ihre 13 Tickets bleiben historische und ausführbare Baseline. Sie werden nicht wieder geöffnet; nur ihre technologieunabhängigen Verhaltensverträge und die obigen Lernerfahrungen fließen in die neuen Tickets ein.
