# Renovate im jeweiligen GitHub-Repository

Status: akzeptierter Standard für zukünftige Repository-Einrichtungen, bestätigt am 13.09.2026. Architekturentscheidung: [ADR 0011](adr/0011-renovate-in-each-owning-github-repository.md).

## Zuständigkeit

Abhängigkeiten eigener Anwendungen werden mit Renovate in GitHub Actions gepflegt. Workflow, Renovate-Konfiguration, Prüfungen und Update-PRs gehören in das GitHub-Repository, das den Anwendungscode und seine Abhängigkeitsdateien versioniert. Dieses Dokument ist die gemeinsame Vorlage für die Einrichtung.

**Für jedes neue Projekt wird der Job in dessen eigenem Repository eingerichtet. `paradox123/obsidian-private-notes` ist kein zentraler Renovate-Runner für andere Repositories.** Dort läuft die bereits eingerichtete Pflege des Nebenkostenabrechnungstools, weil dessen Code Bestandteil dieses Repositorys ist. Bei einem Monorepo liegt der Workflow am Git-Root unter `.github/workflows/`; die Renovate-Konfiguration grenzt die zu pflegenden Anwendungen bei Bedarf über Pfade ein.

Vor jeder Einrichtung werden der tatsächliche Git-Root, das zugehörige GitHub-Remote und der Standardbranch ermittelt. Repository, Branch, Paketpfade und Empfänger werden aus dem Zielprojekt abgeleitet. Werte aus dem Nebenkosten-Beispiel dürfen nicht ungeprüft übernommen werden. Der Job verarbeitet ausschließlich sein eigenes Repository; eine Suche nach oder Pflege von weiteren Repositories gehört nicht zum Standard.

## Verbindliches Verhalten

- Renovate erkennt neue stabile Versionen und erstellt Update-PRs im jeweiligen Repository. Verwaltet werden dessen eigene Pakete, Lockdateien und geeignete Laufzeit- oder SDK-Referenzen im vereinbarten Umfang.
- Vollständig erfolgreiche Pflichtprüfungen erlauben den automatischen Merge ohne erneute menschliche Freigabe, auch bei Major-Paketupdates. Build und relevante Tests müssen den aktuellen Update-Stand einschließlich seiner Integration mit dem Zielbranch abdecken.
- Fehlende, laufende, abgebrochene, übersprungene oder fehlgeschlagene Pflichtprüfungen erlauben keinen Merge. Ein leerer Testlauf gilt nicht als Erfolg. Ändert sich der relevante Stand, ist eine neue Prüfung erforderlich.
- Bei Fehlern bleibt der PR offen. Daniel beziehungsweise der im Zielrepository festgelegte Verantwortliche erhält eine persönliche GitHub-Erwähnung mit PR- und Prüflauf-Link. Die zusätzliche E-Mail- oder Push-Zustellung folgt den persönlichen GitHub-Einstellungen.
- Ein unveränderter Fehler wird nicht täglich erneut gemeldet. Nach einer Korrektur wird erneut geprüft; eine manuelle Wiederholung bleibt möglich. Scheitert die Wartung schon vor der PR-Prüfung oder bei der Benachrichtigung, muss eine gesonderte, deduplizierte Fehlermeldung den Verantwortlichen erreichen.

Als Ausgangseinstellung werden neue Updates montags zwischen 06:00 und 10:00 Uhr Europe/Berlin aufgenommen. Ein täglicher Wartungslauf bearbeitet offene PRs weiter; im Referenzprojekt startet er um 06:17 UTC. Releases müssen mindestens drei Tage alt sein. Höchstens ein Update-PR wird gleichzeitig bearbeitet; technisch zusammengehörige Pakete werden gemeinsam aktualisiert. Diese Betriebsparameter können begründet an das Zielrepository angepasst werden. Die Repository-Zuständigkeit und die Pflicht erfolgreicher Prüfungen bleiben erhalten.

## Einrichtung und Verifikation

1. Paketmanager, Updateumfang und aussagekräftige Build-/Testprüfungen des Zielprojekts bestimmen. Doppelte Dependabot- und Renovate-Pflege desselben Umfangs auflösen.
2. Renovate-Konfiguration und geplanten GitHub-Actions-Workflow im Zielrepository versionieren. Action-Versionen pinnen; Zugangsdaten auf dieses Repository begrenzen. Kurzlebige Zugangsdaten und die jeweils nötigen Jobrechte bevorzugen. Keine Tokens aus einem anderen Projekt übernehmen.
3. Automatischen Merge mit den verfügbaren Repository-Schutzmechanismen und verbindlichen Prüfungen absichern. Bei abweichenden Plattformmöglichkeiten muss eine alternative Steuerung nachweislich nur den erfolgreich geprüften Stand übernehmen. Der besondere Abschlussjob des Nebenkostenprojekts ist eine dort geprüfte Umsetzung, keine zwingende Kopiervorlage für jedes Repository.
4. Sicherstellen, dass Bot-PRs tatsächlich sämtliche Pflichtprüfungen auslösen. Die Einrichtung darf nicht auf einer ungeprüften Annahme über Folgeereignisse des verwendeten Tokens beruhen. Tests von Update-Code erhalten keine Schreibrechte; eine gegebenenfalls separate Merge-Steuerung verwendet vertrauenswürdigen Code.
5. Fehlerbenachrichtigung und erfolgreichen automatischen Merge über GitHub verifizieren. Dabei nachweisen, dass ein Fehler den PR offen hält und dass genau der erfolgreich geprüfte Stand übernommen wird. Lauf- und PR-Links in der Betriebsdokumentation des Zielrepositorys festhalten.
6. Zeitplan, Updateumfang, Empfänger, manuelle Wiederholung und Pausieren des Jobs im Zielrepository dokumentieren. Erst nach dieser Verifikation gilt die Einrichtung als aktiv.

Bei SDKs und Laufzeiten werden die unterstützte Version und notwendige Zielplattformänderungen projektspezifisch berücksichtigt. Ein Paketmanager-Pin allein ersetzt keine Migration. Änderungen an Workflow-Dateien benötigen eine dafür geeignete Berechtigung; sind sie nicht automatisiert verwaltbar, wird diese Grenze ausdrücklich dokumentiert.

## Geltungsgrenzen

Ein gemeinsames Muster erteilt keinen Auftrag, alle bestehenden Repositories sofort umzustellen. Es wird bei deren Einrichtung oder bei einem entsprechenden Wartungsauftrag angewendet. Dieses Dokument registriert selbst keinen zusätzlichen Job.

Renovate pflegt versionierte Abhängigkeitsreferenzen. Ein erfolgreicher Merge beweist kein Deployment und keine Aktualisierung einer lokalen Installation. Bei eingebundenen Fremdprojekten wird die eigene Upstream-Referenz gepflegt; deren interne Bibliotheken werden nicht eigenständig vorgezogen. Ein engerer, ausdrücklich vereinbarter Updateumfang bleibt maßgeblich, beispielsweise bei den [LLM-Wiki-Release-Updates](rag/2026-09-13-llm-wiki-dependency-updates.md).

Die automatische Merge-Freigabe gilt für die hier beschriebenen Abhängigkeitsupdates. Sie ändert keine Freigaberegeln für allgemeine agentische Implementierungsaufträge.

## Erprobte Referenz

Beim Nebenkostenabrechnungstool wurden Fehlerbenachrichtigung und automatischer Merge mit einem echten Renovate-PR nachgewiesen: [Update-PR #5](https://github.com/paradox123/obsidian-private-notes/pull/5), [Fehlermeldung am offenen PR](https://github.com/paradox123/obsidian-private-notes/pull/5#issuecomment-5652804773), [erfolgreicher Prüflauf und Merge](https://github.com/paradox123/obsidian-private-notes/actions/runs/34752982396). Diese Links belegen das Muster; sie bestimmen nicht den Ausführungsort zukünftiger Jobs.
