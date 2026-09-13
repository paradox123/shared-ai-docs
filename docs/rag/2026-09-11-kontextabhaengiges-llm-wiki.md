# Kontextabhängiges LLM-Wiki über dem Obsidian-Vault

Konzeptstand: 12.09.2026; Umsetzungsnachtrag: 13.09.2026. Die Integration ist implementiert, abgenommen und akzeptiert. Die folgenden Konzept- und Auswahlabschnitte bewahren den damaligen Gesprächsstand; der aktuelle Abschluss steht unter „Umsetzung mit Atomicstrata“. Laufende Fachautomationen wurden nicht verändert.

## Gewähltes Konzept

Daniel nutzt Andrej Karpathys [LLM-Wiki-Konzept](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Als ausführende Implementierung ist inzwischen Atomicstratas LLM-Wiki-Compiler gewählt. Der [lokale Umsetzungsauftrag](../../.scratch/contextual-llm-wiki/spec.md) und der [OpenSpec-Change](../../openspec/changes/archive/2026-09-13-integrate-contextual-llm-wiki/proposal.md) definieren die Anpassung an den Vault. Die vorherigen Interviewfragen behandelten konzeptionell bereits vorgegebene Abläufe unnötig als freie Produktentscheidungen. Die [Originalquellenprüfung vom 12.09.](2026-09-12-karpathy-llm-wiki-konzeptpruefung.md) hält die geprüften Aussagen und Grenzen fest.

Das Rollenmodell lautet: Der Mensch kuratiert Quellen, fragt und lenkt die Analyse; das LLM erzeugt und pflegt die verknüpften Wiki-Seiten. Auch Gesprächsergebnisse können zu Wiki-Inhalt werden. „Der Mensch liest, das LLM schreibt“ beschreibt den normalen Arbeitsweg, kein technisches Schreibverbot. Nachpflege gehört zu Ingest und Lint; ein bestimmter Automatisierungsgrad oder Auslöser wird im Original nicht verbindlich festgelegt. [Original: Architecture und Operations](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#architecture)

## Daniels Anpassung für den Vault

- Die bestehenden Markdown-Repos und das Arbeiten im Obsidian-Vault bleiben erhalten. Ihre Dokumente liefern die Fachquellen. „Raw“ beschreibt ihre Rolle gegenüber dem Wiki; bereits kuratierte Dokumentation ist ebenfalls Input.
- Der Wiki-Pflegeprozess liest diese Quellen und schreibt seine abgeleitete Wissensschicht. Die vorhandene fachliche Bearbeitung der Repo-Dokumente bleibt möglich. Das ist eine Anpassung des im Original als unveränderlich beschriebenen Quellenbestands an extern weitergepflegte Repos.
- Das Wiki wird als übergeordnete Schicht und erster Einstieg für Mensch und Agent in Obsidian genutzt. Es entsteht passend zum Kontext geklonter Repos und ist kein eigenes Git-Repo. Karpathy erwähnt Git für sein Wiki; der Verzicht darauf ist Daniels bewusste Anpassung.
- Wiederkehrende Vergleiche und übertragbare Erkenntnisse bleiben über Fragen und Sessions hinweg nutzbar. Entfällt ein benötigter Repo-Input aus dem Kontext, verschwindet die davon abhängige Erkenntnis; bei seiner Rückkehr kann sie neu entstehen. Diese Kontextregel stammt von Daniel und ist im Original nicht spezifiziert.
- Bei einer Änderung der Fachquelle muss erkennbar sein, welche gemeinsame Aussage erneut geprüft werden muss. Das ist ein wesentliches Auswahlkriterium für die Implementierung; aus dem Konzept allein folgt noch kein Nachweis vollständiger Quellenabhängigkeiten.
- SpecOps ist nach Daniels früherer Klarstellung ein nicht weiterverfolgter Prototyp. Bestehende Automationen dürfen grundsätzlich ersetzt werden; daraus folgt kein aktueller Auftrag, sie abzuschalten.

Die Architekturentscheidung steht in [ADR-0009](../adr/0009-contextual-llm-wiki-over-existing-source-repositories.md), die Begriffe im [Glossar](../../CONTEXT.md#llm-wiki).

## Annahmen für die Implementierungsauswahl

QMD bleibt entsprechend dem [bestehenden Betriebsmodell](operating-model-rag-qmd.md) der Suchweg. Das Wiki ergänzt gepflegte Inhalte, Orientierung und Quellenbeziehungen. Der Wiki-Einstieg muss bei Bedarf zu den Fachquellen führen; die abgeleitete Darstellung hebt deren fachliche Autorität nicht auf.

Die Auswahl soll Karpathys Arbeitsweise übernehmen und sie an die vorhandenen Repos anpassen. Ein konkreter Ordneraufbau, Auslöser für Ingest/Lint, lokale Speicherung sowie die technische Kontext- und Quellenzuordnung werden anhand des gewählten Ansatzes festgelegt. Dafür wird das Interview nicht mit abstrakten Detailfragen fortgesetzt.

## Nachweisplan vor der Umsetzung

- Atomicstrata ist ausgewählt, aber noch nicht im Vault erprobt. Die in den früheren Tasks besprochene Alternativenrecherche bleibt Recherchehistorie; ihre Präferenz muss an diesem geklärten Zielbild gemessen werden. Ihre damalige Datei `2026-09-10-agent-wiki-alternativen.md` ist beim Check vom 12.09. nicht mehr im aktuellen Dokumentationsbestand vorhanden.
- Die gewünschte Kette von Quellenänderung bis betroffener gemeinsamer Aussage muss am Kandidaten nachgewiesen werden. Karpathys Pflegeanweisungen ersetzen diesen Nachweis nicht.
- Der vorhandene Repo-Kontext muss bei der Umsetzung konkret abgebildet werden. Ein globales Gedächtnis ausgeschiedener Repos ist nicht gewünscht.
- Ohne eigenes Wiki-Git sind Versionierung und Wiederherstellung nicht automatisch gelöst. Insbesondere gespeicherte Gesprächssynthesen sind nicht ohne Weiteres allein aus Quelldateien identisch rekonstruierbar. Die Auswahl muss dies transparent behandeln, ohne die festgelegte Kontextregel still zu verändern.

## Gesprächsgrundlage und Dokumentationsumfang

Grundlage sind die abrufbaren Inhalte der Tasks „Analysiere Agent-Wiki für Vault“ (`01a086d8-cd4c-7083-b338-90884b83d83b`) und „Finde Agent-Wiki-Alternativen“ (`01a08b7d-c661-7682-a082-3f680efe27a9`) sowie Daniels Klarstellungen vom 11.–12.09.2026. Der jüngste abgerufene Turn des Alternativen-Tasks enthielt keine Nachrichten. Das damalige Zielbild vom 10.09. ist hinsichtlich der Rolle des gemeinsamen Pflegeprozesses durch diese Abgrenzung überholt; seine Bestandsprüfung bleibt historischer Gesprächskontext. Die damalige Datei `2026-09-10-agent-wiki-zielbild-nach-automationspruefung.md` ist beim Check vom 12.09. nicht mehr im aktuellen Dokumentationsbestand vorhanden.

Die Exit-Prüfung von `grill-with-docs` ist erfüllt: Konzept und lokale Architekturgrenzen stehen fest; die verbleibenden Fragen gehören zur Kandidatenprüfung und Umsetzung. Das Interview endet hier mit diesem Dokumentationsstand. Kein passender aktiver Wiki-Change wurde gefunden; diese Runde korrigiert die Konzeptdokumentation und legt keinen Implementierungs-Change an.

## Empfohlener nächster Ablauf nach ask-matt

Historische Empfehlung vor der anschliessenden Atomicstrata-Auswahl vom 12.09.2026: Zuerst eine bestehende Implementierung auswählen und ihre Eignung praktisch prüfen, danach den verbleibenden Anpassungsumfang spezifizieren. Das ist eine Empfehlung für den nächsten Arbeitsauftrag; bislang wurde kein Kandidat installiert oder erprobt.

Der [ask-matt-Flow](../../skills-repo/vendor/mattpocock/.agents/skills/ask-matt/SKILL.md) sieht vor einer Build-Spec eine Erprobung vor, wenn offene Fragen eine ausführbare Antwort benötigen. Hier stehen Konzept und Ziele bereits fest. Unbekannt sind die Passung einer vorhandenen Implementierung und der tatsächlich notwendige Integrationsaufwand. Karpathys [Original](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f#note) schreibt kein bestimmtes Werkzeug vor. Daraus folgt weder eine Pflicht zum Eigenbau noch bereits der Nachweis, dass ein beliebiges Repository mit kleinen Änderungen ausreicht.

1. **Kandidaten prüfen:** Wenige Implementierungen anhand der vorhandenen Anforderungen vergleichen: Karpathy-Abläufe, mehrere externe Quellrepos, gemeinsames Markdown-Wiki für Obsidian ohne Git-Zwang, QMD-Anbindung und nachvollziehbare Änderungsnachpflege. Lizenz, Ausführbarkeit im vorhandenen Agent-Setup und Eingriffstiefe in den Upstream mitprüfen.
2. **Favoriten erproben:** In einem begrenzten Testbestand zwei Repo-Quellen zu einer gemeinsamen Erkenntnis verarbeiten, diese bei einer Folgefrage wiederverwenden, eine tragende Quelle korrigieren und die betroffene Aussage erneut prüfen lassen. Dabei zeigen, dass die Quellen unberührt bleiben und die erzeugte Schicht in Obsidian nutzbar ist. Kein Ersatzprototyp, der Fähigkeiten nur simuliert, die eigentlich am Kandidaten geprüft werden müssen.
3. **Anpassungen abgrenzen:** Dokumentieren, was unverändert funktioniert, was Konfiguration oder Agent-Anweisungen benötigen und was echten eigenen Code verlangt. Bevorzugt vorhandene Erweiterungspunkte nutzen; umfangreiche Kernänderungen sind ein Grund, die Kandidatenwahl nochmals zu prüfen.
4. **Passend in die Umsetzung wechseln:** Bei reiner kleiner Einrichtung genügen nachvollziehbare Konfiguration und Betriebsdokumentation. Für dauerhafte Verhaltensänderungen gilt die OpenSpec-Policy des Repos: vor ihrer Implementierung einen passenden Change anlegen und Verhalten nachweisen; bei grösserem Umfang in selbständige Arbeitspakete zerlegen. Die Spec beschreibt dann die Integration und fehlende Fähigkeiten, nicht das gesamte bereits implementierte Wiki neu.

Das vorhandene Zielbild und die ADR dienen bis dahin als Auswahl- und Prüfkriterien. Eine vollständige Build-Spec vor der Kandidatenprüfung würde ungeprüfte Annahmen über die Architektur des Fremdrepos festschreiben. Eine vollständig spezifikationsfreie spätere Eigenentwicklung ist damit ebenfalls nicht empfohlen.

## Umsetzung mit Atomicstrata

Daniel hat Atomicstrata ausdrücklich gewählt und die Spezifikation beauftragt. Die Wahl stützt sich auf vorhandene Quellenstände und Freshness-/Refresh-Funktionen. Externe Repo-Anbindung, transitive Nachpflege gespeicherter Antworten und QMD-basierter Zugriff sind eigene Integrationsaufgaben. Die [Schnittstellenprüfung](2026-09-12-atomicstrata-integrationsschnittstellen.md) unterscheidet vorhandene SDK-Funktionen von nötigen Erweiterungen. Insbesondere ist die Markdown-Inhaltsübersicht beim Compile kein konkurrierender Suchindex; der native Query-/Save-Pfad benötigt dagegen eine QMD- und Abhängigkeitsanbindung.

Die [Spec im lokalen Tracker](../../.scratch/contextual-llm-wiki/spec.md) wurde implementiert und von Daniel am 13.09.2026 akzeptiert. Der [Change integrate-contextual-llm-wiki](../../openspec/changes/archive/2026-09-13-integrate-contextual-llm-wiki/proposal.md) enthält Design, normative Szenarien und die abgeschlossenen Umsetzungsschritte. Die [Abnahme mit echtem Compiler, Provider, QMD und Obsidian](../../contextual-llm-wiki/evidence/acceptance.md) ist dokumentiert; die kanonischen Requirements liegen unter `openspec/specs/contextual-llm-wiki`. Die Pflege erfolgt ausdrücklich über `wiki maintain`; ein automatischer Auslöser gehört nicht zu diesem Change.
