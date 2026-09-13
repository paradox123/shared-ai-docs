# Kontextabhängiges LLM-Wiki mit Atomicstrata

Status: closed
Accepted: 2026-09-13
Closed: 2026-09-13

Umsetzungsstand: implementiert; definierte Abnahme einschließlich Obsidian A10 bestanden, alle 24 Tasks abgeschlossen. [Abnahmenachweis](../../contextual-llm-wiki/evidence/acceptance.md).

## Problem Statement

Daniel arbeitet in mehreren eigenständig versionierten Markdown-Repos innerhalb seines Obsidian-Vaults. Diese Fachquellen sollen bestehen bleiben. Gemeinsame Vergleiche und übertragbare Erkenntnisse müssen bisher wiederholt zusammengesucht werden; bei einer Quellenänderung ist nicht durchgängig erkennbar, welche abgeleitete Aussage nachgepflegt werden muss.

Andrej Karpathys LLM-Wiki-Konzept und Atomicstratas LLM-Wiki-Compiler sind gewählt. Es geht um deren konkrete Integration, nicht um eine weitere Konzept- oder Kandidatenauswahl. Der Compiler liefert bereits Quellenstände und Freshness für Konzeptseiten, deckt aber weder mehrere externe Repo-Wurzeln als vollständigen Kontext noch die gewünschte Nachpflege aller gespeicherten Gesprächssynthesen fertig ab.

## Solution

Eine gemeinsame, vom LLM gepflegte Markdown-Schicht über den jeweils eingebundenen Fachrepos wird zum ersten Einstieg für Mensch in Obsidian und Agent. Ein lokaler Integrationsablauf gleicht die Quellen gerichtet ab, verwendet den Atomicstrata-Compiler für die eigentliche Wissensverarbeitung und ergänzt nachvollziehbare Quellen- und Seitenabhängigkeiten. Er führt Ingest, gezielte Nachpflege, Query mit optionalem Speichern und Lint auf ausdrücklichen Aufruf aus.

Die Fachrepos bleiben unverändert an ihren Orten. Das erzeugte Wiki ist kein eigenes Git-Repo. Seine Inhalte bleiben zwischen Fragen und Sessions erhalten, solange ihre benötigten Quellen zum Repo-Kontext gehören. Entfällt ein benötigter Input, verschwindet davon abhängiges Wissen aus dem aktiven Wiki und der Suche; eine spätere Rückkehr ermöglicht einen Neuaufbau. QMD bleibt die einzige persistierte Retrieval-Engine. Die Anbindung ist erst abgenommen, wenn diese Abläufe mit dem echten Compiler und realen Ausgabedateien gezeigt wurden.

## User Stories

1. Als Daniel möchte ich meine bestehenden Markdown-Repos an ihren Orten behalten, damit mein Obsidian- und Git-Arbeitsablauf weiter funktioniert.
2. Als Daniel möchte ich die zu einer Wissenssicht gehörenden Repos einmal benennen können, damit ich nicht jede Quelldatei einzeln importieren muss.
3. Als Daniel möchte ich weitere geklonte Repos in diesen Kontext aufnehmen können, damit das gemeinsame Wiki mit meinem Arbeitskontext wächst.
4. Als Daniel möchte ich Quellen rekursiv mit klaren Ein- und Ausschlüssen auswählen können, damit nur beabsichtigte Markdown-Inhalte in das Wiki gelangen.
5. Als Daniel möchte ich private Quellen nur in ausdrücklich dafür gewählten Kontexten verwenden, damit private Synthesen nicht im allgemeinen Einstieg erscheinen.
6. Als Quellenautor möchte ich, dass die Wiki-Pflege meine Fachquellen nicht verändert, damit deren Zuständigkeit erhalten bleibt.
7. Als Agent möchte ich gleichnamige Dateien verschiedener Repos eindeutig unterscheiden können, damit Belege und Erkenntnisse nicht kollidieren.
8. Als Leser möchte ich vom Wiki-Beleg zur ursprünglichen Repo-Datei und ihrem geprüften Stand gelangen, damit ich die Aussage nachvollziehen kann.
9. Als Daniel möchte ich Atomicstratas vorhandene Compilerfunktionen nutzen, damit wir Zusammenfassung und Seitenpflege nicht neu implementieren.
10. Als Leser möchte ich eine gemeinsame Erkenntnis aus mehreren Repos mit ihren Gemeinsamkeiten und Grenzen erhalten, damit sich der zusätzliche Wiki-Nutzen konkret zeigt.
11. Als Leser möchte ich bestehende Fachregeln, ADRs und Specs weiterhin als maßgebliche Quellen erkennen, damit eine Synthese deren Autorität nicht still ersetzt.
12. Als Daniel möchte ich das erzeugte Wiki ohne eigenes Git-Repository verwenden, damit seine Ablage meinem dynamischen Vault-Setup entspricht.
13. Als Leser möchte ich in Obsidian über eine verständliche Startseite und funktionierende Links navigieren, damit ich das Wiki im Alltag nutzen kann.
14. Als Agent möchte ich bei Wissensfragen zuerst passende Wiki-Seiten finden und bei Bedarf Fachquellen lesen, damit vorhandene Synthesen wiederverwendet werden.
15. Als Daniel möchte ich hilfreiche Gesprächsantworten ausdrücklich als Wiki-Seiten speichern lassen, damit Erkenntnisse nicht in einer Session verschwinden.
16. Als Leser möchte ich auch bei gespeicherten Antworten deren Quellenabhängigkeiten erkennen, damit diese nicht ungeprüft dauerhaft als Wissen gelten.
17. Als Quellenautor möchte ich eine fachliche Korrektur beim nächsten Pflegeaufruf im Wiki berücksichtigt sehen, damit weitergepflegte Repos als Eingang taugen.
18. Als Daniel möchte ich die von einer Änderung betroffenen Seiten und belegten Passagen sehen, damit ich den Prüfbedarf gezielt nachvollziehen kann.
19. Als Agent möchte ich indirekt abhängige Gesprächssynthesen ebenfalls zur Nachprüfung erhalten, damit die Kette Quelle–Konzept–Antwort nicht abbricht.
20. Als Leser möchte ich geänderte Belege und widersprüchliche Quellen als Prüfbedarf erkennen, damit offene Widersprüche nicht als gesicherte Einigkeit erscheinen.
21. Als Daniel möchte ich nur betroffene Inhalte neu verarbeiten lassen, damit unveränderte Erkenntnisse bei wiederholter Pflege erhalten bleiben.
22. Als Daniel möchte ich, dass nach Entzug eines Repos davon abhängige Erkenntnisse aus dem aktiven Wiki verschwinden, damit der vorhandene Input den Wissensbestand bestimmt.
23. Als Leser möchte ich auf gemischten Seiten weiterhin unabhängig belegtes Wissen nutzen können, damit eine entfernte Quelle nicht das ganze Wiki unbrauchbar macht.
24. Als Daniel möchte ich nach Rückkehr eines Repos dessen Erkenntnisse neu erzeugen können, damit kein dauerhaftes Archiv ausgeschiedener Kontexte erforderlich ist.
25. Als Agent möchte ich entzogene Inhalte auch nicht mehr über QMD oder den Wiki-Einstieg erhalten, damit entfernte Dateien nicht als Suchtreffer weiterleben.
26. Als Daniel möchte ich QMD für das Wiki weiterverwenden, damit keine konkurrierenden dauerhaften Such- und Embedding-Indizes gepflegt werden müssen.
27. Als Betreiber möchte ich unveränderte Pflegeaufrufe ohne neue Modellkompilierung wiederholen können, damit häufige Nutzung keine unnötige Arbeit erzeugt.
28. Als Betreiber möchte ich einen fehlgeschlagenen Lauf mit erkennbarem Restbedarf fortsetzen können, damit ein Abbruch weder Änderungen verliert noch einen falschen Erfolg meldet.
29. Als Betreiber möchte ich Quellenentzug von einem unvollständigen oder fehlgeschlagenen Scan unterscheiden können, damit ein Lesefehler keine massenhafte Löschung auslöst.
30. Als Daniel möchte ich Versions-, Provider- und Laufvoraussetzungen vor der Verarbeitung prüfen können, damit Einrichtungsprobleme vor Inhaltsänderungen sichtbar werden.
31. Als Daniel möchte ich einen verständlichen Bericht über Änderungen, geprüfte Inhalte und offene Probleme erhalten, damit ich den Wiki-Stand einschätzen kann.
32. Als Daniel möchte ich eine Wiederherstellung des lokalen Wiki-Zustands nachvollziehen können, damit auch gespeicherte Gesprächssynthesen bei einem Defekt erhalten werden können.
33. Als Daniel möchte ich eine Abnahme mit sichtbaren Vorher-/Nachher-Aussagen, Quellen und Obsidian-Navigation erhalten, damit erfolgreiche Tests nicht mit fachlicher Funktionsfähigkeit verwechselt werden.
34. Als Daniel möchte ich die bestehenden Fachautomationen während dieser Integration beibehalten, damit die Quellenpflege nicht ohne Ersatz ausfällt.

## Implementation Decisions

- **Gewählte Basis:** Atomicstrata LLM-Wiki-Compiler am geprüften Commit `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb`, zunächst mit dem Default-Profil. Kein erneuter Auswahlwettbewerb und kein Ersatzcompiler. Updates sind eigenständige, nachzuprüfende Änderungen.
- **Eine Integrationsgrenze:** Ein lokales TypeScript-Modul bietet eine öffentliche CLI für Einrichtung, Kontextabgleich/Pflege, Status, Query mit optionalem Speichern sowie Lint. Intern verwendet es bevorzugt das öffentliche Compiler-SDK. Bereits passende Compilerfunktionen bleiben erhalten; neue Eingriffe werden auf fehlende Adapter oder Erweiterungspunkte begrenzt. Konkrete Befehlsnamen sind Implementierungsdetails, keine Behauptung über vorhandene Upstream-Befehle.
- **Quellenadapter:** Eine lokale Kontextkonfiguration ordnet stabile Repo-IDs den vorhandenen Clone-Wurzeln und expliziten Markdown-Filtern zu. Ein gerichteter, zeilenerhaltender Spiegel führt Quellen unter kollisionsfreien Identitäten in den Compiler. Symlink-Traversal und Verschieben bestehender Repos sind nicht die Integrationsstrategie. Pfadwechsel derselben Quelle und Repo-Wechsel werden anhand ihrer Identität auseinandergehalten.
- **Kontextdefinition:** Die Konfiguration wählt Repos aus, nicht einzelne Seiten. Vorhandene ausgewählte Repos bestimmen den aktiven Kontext. Neu geklonte, noch nicht ausgewählte Repos werden nicht still einbezogen. Private Kontexte benötigen ausdrückliche Auswahl und eine getrennte aktive Ausgabe-/Suchsicht. Dies konkretisiert die bestehende Scope-Regel ohne globales Einsammeln aller Vault-Inhalte.
- **Eigentum:** Wiki-Schreiboperationen beschränken sich auf den verwalteten Arbeitsbereich und dessen registrierte Suchsicht. Quellenstand, Originalpfad und Spiegelzuordnung bleiben nachvollziehbar. Compiler-Betriebszustand und Quellenkopien sind keine zweite kuratierte Wissensquelle und werden nicht nochmals als Wiki-Inhalt indexiert.
- **Abhängigkeiten:** Bestehende Quellenstände und Konzeptbesitz werden wiederverwendet. Gespeicherte Antworten und weitere verwaltete Synthesen erhalten zusätzlich Abhängigkeiten zu tatsächlich verwendeten Wiki-Seiten und deren Quellständen. Bei Unsicherheit darf die gesamte verwendete Evidenzmenge konservativ als Abhängigkeit gelten; ein unvollständiger Beleg darf nicht als unabhängige frische Synthese veröffentlicht werden. Ein allgemeiner semantischer Claim-Graph ist nicht erforderlich.
- **Inkrementelle Pflege:** Der Abgleich ermittelt hinzugefügte, geänderte und entzogene Quellen. Änderungen erzeugen eine begründete Prüfliste der direkt und indirekt betroffenen Seiten; bestehende Zitate grenzen betroffene Passagen ein. Nachpflege bestätigt, korrigiert oder entfernt Aussagen und aktualisiert erst danach den geprüften Stand. Neue Quellen dürfen gemeinsame Konzepte erweitern; unveränderte Quellen lösen keinen unnötigen Neubau aus.
- **Kontextentzug:** Abhängige Seiten werden aus der aktiven Sicht genommen, bevor sie erneut als aktuelle Evidenz dienen können. Gemischte Konzeptseiten werden aus verbleibenden Quellen neu erzeugt; gespeicherte Antworten mit entfallenem benötigtem Input werden entfernt und können später neu erstellt werden. Unabhängige Seiten bleiben erhalten. Ein blosses Orphan-Flag erfüllt diese Regel nicht.
- **QMD:** Die bestehende Single-Engine-Vorgabe bleibt erhalten. Das SDK erlaubt Compile ohne Embeddings; die dabei erzeugte Markdown-Inhaltsübersicht bleibt ausdrücklich erhalten. Sie ist kein zweiter persistierter Retrieval-Index. Der native Query-/Save-Pfad benötigt dagegen eine Anbindung für QMD-Evidenz und das Speichern ohne eigenen Embedding-Bestand. Dafür wird ein schmaler Retrieval-/Save-Erweiterungspunkt vorgezogen; falls der vorhandene Agent die Antwort aus QMD-Evidenz bildet, speichert der Integrationsadapter das Ergebnis über denselben geprüften Abhängigkeitsvertrag. Compiler-Manifeste, Hashes und Provenienz sind zulässige Betriebsmetadaten. Keine native Query-Variante darf die QMD- oder Kontextregeln umgehen.
- **Zugriff und Veröffentlichung:** Mensch und Agent nutzen dieselbe aktive Markdown-Schicht. Der Agent-Ablauf prüft den Kontextzustand und priorisiert Wiki-Treffer, mit Quellen-Fallback bei fehlender oder unzureichender Synthese. Noch nicht nachgepflegte Aussagen werden nicht als aktuell bestätigt ausgegeben. Der Obsidian-Einstieg zeigt letzten Pflegezeitpunkt und offene Prüfungen; Echtzeitaktualität ohne Pflegeaufruf wird nicht zugesagt.
- **Auslöser:** Ein ausdrücklicher Pflegeaufruf übernimmt Abgleich und erforderliche Nachpflege. Ein Dateiwächter und neue Scheduled Tasks sind nicht Bestandteil dieses Changes. Das Modul bleibt später automatisierbar, ohne einen neuen Ablauf zu erfinden.
- **Fehler und Wiederaufnahme:** Unvollständige Scans werden nicht als vollständiger Quellenentzug interpretiert. Nur vollständig vorbereitete Seitenergebnisse werden aktiv veröffentlicht; Fehler bleiben als Restbedarf sichtbar. Ein unterbrochener Entzug darf über die verwaltete Agent-Schnittstelle keine alte Aussage erneut freigeben. Änderungen während der Verarbeitung werden erkannt und erneut eingeplant.
- **Einrichtung und Betrieb:** Die gepinnte Runtime und ein konfigurierbarer, bereits verfügbarer Modellprovider werden zuerst geprüft. Deutsches Wiki-Prosa ist der Standard; Fachbegriffe und Quellzitate behalten ihre passende Sprache. Versionsstand und Provider werden protokolliert, keine Zugangsdaten. Lokale Sicherung und Wiederherstellung umfassen gespeicherte Antworten samt Abhängigkeiten und beachten beim Restore den aktuellen Repo-Kontext.
- **Abgrenzung des Spezifikationsstands:** Nutzerentscheidungen sind Compilerwahl, Karpathy-Modell, Repo-Erhalt, Git-freies Wiki, dauerhafte Synthese und Quellen-/Kontextnachpflege. Spiegel, CLI/SDK-Modul, explizite Kontextkonfiguration, konservative Antwortabhängigkeiten und Veröffentlichungsschritte sind daraus abgeleitete technische Festlegungen. Sie dürfen ohne Änderung des beobachtbaren Vertrags vereinfacht werden.

## Testing Decisions

- **Höchste gemeinsame Schnittstelle:** Black-Box-Tests rufen die öffentliche Integrations-CLI als separaten Prozess auf und prüfen tatsächliche Markdown-Ausgabe, Beleglinks, Status, Exit-Ergebnis und QMD-Treffer. Sie testen keine privaten SDK-Methoden oder intern gewählten Dateiformate. Der vorgeschlagene Schwerpunkt wurde im Gespräch zum Abgleich vorgelegt; eine andere Rückmeldung wird eingearbeitet.
- **Prüfgegenstand:** Kontext-/Quellenadapter, echter Atomicstrata-Compiler, Nachpflege gespeicherter Antworten und QMD-Anbindung werden gemeinsam durch diese Oberfläche ausgeübt. Für den minimalen Umfang genügt Agent-Aufruf dieser CLI; ein zusätzlicher MCP-Transport ist kein zweiter obligatorischer Implementierungspfad.
- **Deterministische Verifikation:** Zwei temporäre Git-Repos liefern kurze, fachlich eindeutig erwartbare Markdown-Quellen einschließlich gleicher Dateinamen. Nur die Modellprovider-Grenze darf für Fehler- und Wiederholungstests einen kontrollierten Provider verwenden; der Compiler und der Abhängigkeitsablauf werden nicht durch einen Scheincompiler ersetzt. Mindestens ein Lauf mit echtem Provider belegt tatsächliche Synthesequalität und Zitierbarkeit.
- **Vorbild:** Die vorhandenen Control-Plane-Black-Box-Tests dieses Repos nutzen separate Prozessclients und beobachtbare öffentliche Ergebnisse. Dieses Prinzip wird übernommen, ohne deren Dienstarchitektur oder Domänentestfälle zu kopieren. Relevante Upstream-Tests für Freshness, Quellenentzug, Compile und SDK ergänzen die eigenen Verhaltensfälle.
- **Abnahme:** Die folgende Tabelle ist der verpflichtende Nachweisplan. Bei Umsetzung werden Beobachtung und konkrete Evidence-Links ergänzt. Die ausgeführte Abnahme einschließlich ihrer UI-Nachweise sind im [Abnahmenachweis](../../contextual-llm-wiki/evidence/acceptance.md) dokumentiert.

| ID | Erwartetes Verhalten | Beobachtbarer Nachweis | Stand |
|---|---|---|---|
| A0 | Alle acht realen Repo-Wurzeln sowie Meetings und Projects sind initial registriert und korrekt abgegrenzt. | Inventur zeigt Clone-Pfade, Quellenzahlen und Filter; je eine Quelle aus Meetings, Projects und Projects/Private wird im passenden Kontext verarbeitet. Private separat; kein doppelter Checkout, Test-Repo oder doppelte Vault-Root-Erfassung. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A1 | Ausgewählte Repos bleiben unangetastet; gleiche Dateinamen kollidieren nicht. | Vorher-/Nachher-Quellenhashes und Git-Status gleich; getrennte Originalbelege im Ergebnis. | Originalhashes unverändert; parallele sachfremde Git-Änderungen ausgewiesen — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A2 | Zwei Repos ergeben eine gemeinsame Erkenntnis, die bei Folgefragen wiederverwendet wird. | Fachlich prüfbare Synthese mit beiden Belegen; Folgeantwort nutzt dieselbe aktive Wiki-Seite. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A3 | Quellenkorrektur erreicht Konzept und daraus gespeicherte Antwort. | Query vor Sync erkennt geändertes Original; Prüfliste nennt direkte und indirekte Abhängigkeiten; korrigierte Aussage ersetzt alte Aussage, unabhängige Seite unverändert. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A4 | Kontextentzug entfernt abhängiges Wissen aus allen aktiven Zugriffswegen. | Konzeptanteil/Antwort nicht mehr aktiv; weder QMD noch Agent-Kontext oder Obsidian-Index enthalten die entzogene Aussage. | Dateien, Einstieg und echte QMD-Entzugsprüfung bestanden; Obsidian-Navigation zusätzlich unter A10 belegt — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A5 | Rückkehr eines Repos ermöglicht Neuaufbau. | Neu erzeugte, korrekt belegte Erkenntnis ohne Wiederbelebung eines ungeprüften alten Stands. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A6 | Ein unveränderter Abgleich ist ein inhaltlicher No-op. | Keine Modellkompilierung oder neuen Seitenrevisionen; Status meldet keinen neuen Prüfbedarf. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A7 | Fehler und Änderungen während eines Laufs sind wiederaufnehmbar. | Simulierter Provider-/Scan-/Indexfehler und erneuter Aufruf verlieren keine Änderung, melden keinen falschen Erfolg und verhindern veraltete Agent-Antworten. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A8 | QMD bleibt alleinige persistierte Retrieval-Engine. | Echte QMD-Suche/Entzugsprüfung plus Inspektion auf fehlende zusätzliche Such-/Embedding-Indizes nach Compile und Query. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A9 | Private und allgemeine Kontexte bleiben getrennt. | Synthetischer privater Beleg und abgeleitete Antwort fehlen im allgemeinen Einstieg und dessen Suche. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A10 | Wiki ist in Obsidian ohne eigenes Git-Repo nutzbar. | Screenshot von Einstieg, gemeinsamer Seite und Originalverweis; keine neu angelegte Wiki-Git-Wurzel. | Bestanden: Einstieg, gemeinsame Synthese und Originalquelle in Obsidian geöffnet; drei Screenshots vorhanden — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A11 | Gespeicherte Antworten sind abhängigkeitsgeprüft und wiederherstellbar. | Save-/Restore-Test mit Quellenständen; Restore bei kleinerem Kontext veröffentlicht keine entzogene Antwort. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |
| A12 | Einrichtung, Lint und Betriebsbericht sind nachvollziehbar. | Runtime-/Provider-Prüfung, sichtbarer Widerspruch oder Prüfbedarf und verständlicher Laufbericht mit passendem Fehlerstatus. | Bestanden; Beobachtung und Evidence im Abnahmenachweis — [Evidence](../../contextual-llm-wiki/evidence/acceptance.md) |

## Out of Scope

- Erneute Auswahl des Wiki-Konzepts oder eines anderen Compilers; vollständiger Eigenbau von Compile, LLM-Provider-System oder Wissensplattform.
- Verschieben, Umstrukturieren oder fachliches Bearbeiten der bestehenden Quellrepos durch die Wiki-Pflege.
- Eigene Git-Versionierung des generierten Wikis, öffentliche Veröffentlichung, Cloud-Sync oder Team-Berechtigungsverwaltung.
- Neues Obsidian-Plugin, neue Weboberfläche, zusätzliche persistierte Suchplattform oder breitere Migration der QMD-Architektur.
- Neue Fachautomationen, Abschalten heutiger Jobs, Mailaktionen, Code-/Session-Rohdatensammlung und Wiedereinführung von SpecOps.
- Beliebige PDF-, Web- oder Bild-Ingest-Erweiterungen; der Integrationsumfang beginnt mit vorhandenen Markdown-Fachquellen.
- Zusätzliche Lifecycle-Profile, allgemeine Ontologie, vollständige automatische Wahrheitsprüfung oder garantiert identische LLM-Neugenerierung.
- Automatischer Start der Implementierung durch das Veröffentlichen dieser Spec. Die Veröffentlichung allein war keine Implementierungsfreigabe; Umsetzung, Abnahme und ausdrückliche Annahme sind oben separat ausgewiesen.

## Further Notes

- **Meetings und Projects sind verpflichtender Input:** Beide Ordner werden mit ihren fachlichen Markdown-Unterordnern initial aufgenommen. Dies umfasst Meeting-Transkripte, Notizen, Zusammenfassungen und Assistant Context. `Projects/Private` wird im privaten Kontext aufgenommen; es wird nicht ausgeschlossen. Eine zusätzliche Auswahl einzelner Meetings ist keine Voraussetzung.
- **Initiale Quellen sind konkret definiert:** Die [Repo-Liste mit Clone-Wurzeln, Vault-Zonen und Filtern](input-repositories.md) ist verbindlicher Einrichtungsumfang. Sie registriert `vault-root`, `meeting-assistant`, `shared-ai-docs`, `ki-fuer-kmu`, `ncg-docs`, `private`, `probare-crm` und `sparkle`. `private` und die private Vault-Projektzone bleiben im privaten Kontext. Zusätzliche Worktrees und Test-Repos sind ausgeschlossen. Vor der ersten Kompilierung weist eine Inventur alle acht Einträge mit ihrem Scope aus; die zwei Test-Repos sind kein Ersatz für diese vollständige Startkonfiguration.
- Verbindliche Szenarien und Umsetzungsschritte: [OpenSpec-Change](../../openspec/changes/archive/2026-09-13-integrate-contextual-llm-wiki/proposal.md), [Requirements](../../openspec/changes/archive/2026-09-13-integrate-contextual-llm-wiki/specs/contextual-llm-wiki/spec.md), [Design](../../openspec/changes/archive/2026-09-13-integrate-contextual-llm-wiki/design.md), [Tasks](../../openspec/changes/archive/2026-09-13-integrate-contextual-llm-wiki/tasks.md). Die User Stories sind der lesbare Auftrag; OpenSpec präzisiert denselben Vertrag. Widersprüche müssen vor Umsetzung synchron korrigiert werden.
- Ausgangslage: [Konzeptstand](../../docs/rag/2026-09-11-kontextabhaengiges-llm-wiki.md), [ADR-0009](../../docs/adr/0009-contextual-llm-wiki-over-existing-source-repositories.md), [QMD-Betriebsmodell](../../docs/rag/operating-model-rag-qmd.md).
- Geprüfte Schnittstellen: [Integrationsprüfung](../../docs/rag/2026-09-12-atomicstrata-integrationsschnittstellen.md). [Gewählter Upstream-Stand](https://github.com/atomicstrata/llm-wiki-compiler/tree/34ca1df97b3e60a6700048c48c7cf70c92a9bfdb).
- Quellenprüfung, Spezifikationsvalidierung und Runtime-Abnahme sind verschiedene Nachweise. Die ausführbare Abnahme einschließlich Obsidian A10 liegt nun vor. Daniel hat den Change am 13.09.2026 akzeptiert und seinen Abschluss beauftragt; die OpenSpec-Archivierung ist ausgeführt.

## Comments

- 12.09.2026: Daniels ausdrücklichen Auftrag umgesetzt, Meetings und Projects in jedem Fall als initialen Wiki-Input zu definieren; den zuvor vom Agenten gewählten Meetings-Ausschluss entfernt.
- 12.09.2026: Auf Daniels Auftrag die konkrete initiale DanielsVault-Repo-Liste ergänzt; Pfade und Git-Grenzen gelesen und bestätigt, noch keine Inputs synchronisiert.
- 12.09.2026: Aus der bisherigen Konzeptklärung und Daniels ausdrücklicher Atomicstrata-Auswahl mit `to-spec` erstellt. Keine neue Interviewrunde und keine Installation ausgeführt.
- 12.09.2026: Im separaten Worktree implementiert. 28 öffentliche Verhaltenstests, 59 Upstream-Tests und echter Codex-/QMD-Lauf bestanden. A10 bleibt wegen gesperrtem Mac offen; keine Archivierung. [Abnahme](../../contextual-llm-wiki/evidence/acceptance.md).
- 12.09.2026: Nach manuellem Entsperren A10 ausgeführt und bestanden: Obsidian-Einstieg → gespeicherte Synthese → unveränderte Originalquelle. [Screenshots](../../contextual-llm-wiki/evidence/obsidian/README.md). Alle 24 Tasks abgeschlossen; nicht gemergt, gepusht oder archiviert.
- 13.09.2026: Von Daniel ausdrücklich akzeptiert und zur lokalen Integration in `main` freigegeben. Tracker-Spec geschlossen; OpenSpec-CLI hat 14 Requirements in die [kanonische Spec](../../openspec/specs/contextual-llm-wiki/spec.md) übernommen und den Change archiviert. Automatische Wiki-Pflege bleibt außerhalb dieses angenommenen Umfangs.
