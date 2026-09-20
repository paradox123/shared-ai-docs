# Gemeinsamer Abschluss: Implementierung und erste Nachweise

Stand: 2026-09-20. **Akzeptiert und technisch abgeschlossen.** Nach der ausdrücklichen Abnahme wurde die tatsächliche Migration kritisch verifiziert und durch drei getrennte Reviewer in der Reihenfolge DRY → SOLID → KISS geprüft: keine offenen Befunde. Der [Abschlussbeleg](completion.md) ergänzt die unten erhaltenen historischen Initialprüfungen und Beispielnachweise.

## Ergebnis

Der aktive gemeinsame code-review-Skill besitzt die Strukturreview-Methode und Nachprüfung. change-accepted besitzt den Abschlussauslöser, die vorgelagerte Anforderungsverifikation einschließlich Spec-Abgleich und den Übergang zum autorisierten Abschluss. implement und ask-matt verweisen auf diesen Ablauf. Orchestrator und Repository-Anleitungen enthalten keine eigene DRY-/SOLID-/KISS-Anweisung mehr.

| Anforderung | Erste beobachtete Evidenz |
| --- | --- |
| Direkte Umsetzung wartet nach ersten Tests | Unabhängiges Szenario `direct-ready` meldet awaiting-acceptance ohne Abschlussreviews oder Lieferung. |
| Designzustimmung startet keinen Abschluss | `design-accepted` bleibt bei der Designentscheidung. |
| Delegierter Abschluss ohne weitere menschliche Schleife | `delegated-gap` übernimmt den delegierten Auftrag, hält aber die Strukturreviews bis zum fehlenden Verhaltensnachweis zurück. |
| Zentrale Reviewmethode und vollständige Standards-Abdeckung | Aktiver code-review definiert Reihenfolge, separate Reviewer, Regelzuordnung und gezielte Nachprüfung. Quellsuche in den migrierten Aufrufern findet keine wiederholte DRY-/SOLID-/KISS-Methode. Ergänzend wurde der Ablauf inzwischen an einer ausführbaren Beispieländerung mit drei tatsächlichen Reviewern durchlaufen; siehe Prozessnachweis unten. |
| Nachweise wiederverwenden und betroffene Prüfungen öffnen | `reuse-archive` verwendet gültige Nachweise; `late-repair` öffnet betroffene Anforderungs- und Strukturabdeckung, ohne pauschalen Neustart. |
| Redaktionelle Grenze und eigenständige Reviews | `editorial` verlangt Dokumentchecks; `standalone` ergänzt zuerst Anforderungsnachweise ohne zusätzlichen Accepted-Trigger. |
| Aktive Skills und Referenzen erreichbar | Synchronisierte Runtime-Links aller sechs betroffenen globalen Einstiegspunkte zeigen auf vorhandene kanonische Dateien; keine defekten Skill-Links oder geprüften relativen Referenzen. |
| Vendor-Herkunft erhalten | Drei Quelldatei-Hashes stimmen mit den unangetasteten Vendor-Fassungen überein; aktive lokale Fassungen behalten die öffentlichen Namen. |

Details: [Szenarien und unabhängige Ergebnisse](evidence/completion-forward-check.md), [ausgeführte Prüfungen](evidence/completion-initial-checks.json), [Quellstand](evidence/completion-source-manifest.json).

## Geänderter Umfang

- shared-ai-docs: aktive code-review-, implement- und ask-matt-Fassungen, neuer change-accepted-Skill; Orchestrator-Aufrufer; write-agents-md-Vorlage; eigene AGENTS.md und OpenSpec-Archivierungs-Einstieg; Spezifikation, ADR und Integrationsdokumentation.
- NCG: `/Users/dh/Documents/Dev/NCG/ncg-backend/AGENTS.md` und Git-root-Anleitung `backend/AGENTS.md`. Die übergeordnete Datei liegt außerhalb des Backend-Git-Roots und muss bei einer späteren Übertragung separat berücksichtigt werden.
- probare-crm: `AGENTS.md` verweist nun ebenfalls auf die gemeinsame Abschlussverpflichtung.
- ki-fuer-kmu: `AGENTS.md`, lokaler Accepted-Adapter, OpenSpec-Archivierung und Issue-Ablauf. Repository-Prüfkommandos bleiben lokal; ein Schlüsselwort wählt keinen Zielbranch und erteilt keine pauschale Lieferfreigabe.

Die drei Git-Repositories außerhalb von shared-ai-docs waren vor diesen Änderungen sauber. In shared-ai-docs vorhandene fremde Änderungen an hybrid-skill-sync, improve-skills und install-vendor-skills wurden nicht verändert. Es wurden keine Commits, Pushes, Merges, Issues, aktiven Automationen oder Produktivsysteme geändert.

## Prüfgrenzen

OpenSpec strict und Diff-Prüfungen der vier Git-Repositories bestehen. Der Skill-Validator akzeptiert die neuen/angepassten code-review-, change-accepted-, orchestrate-ticket-batch- und write-agents-md-Fassungen. Bei implement und ask-matt beanstandet er das bereits in den unveränderten Vendor-Originalen vorhandene Feld `disable-model-invocation`. Das Feld bleibt erhalten; ein temporärer Prüfeingang ohne ausschließlich dieses Feld besteht die übrige Schema-Prüfung. Die rohen Validatorfehler sind ausdrücklich im Prüfprotokoll enthalten.

Die sieben Szenarien sind isolierte Entscheidungen anhand realer Skilltexte und synthetischer Zustände. Sie sind kein vollständiger Live-Lauf mit Anwendungen, tatsächlichen Reviewer-Reparaturen, Archivierung oder Integration. Die Anwendungssuiten wurden für diese Anleitungsmigration nicht ausgeführt; Anwendungscode blieb unverändert. Gemessene Tokenersparnis aus einem neuen realen Batch liegt nicht vor.

Nach der kontextbezogenen Abnahme wurde der technische Abschluss dieser Migration ausgeführt; siehe [Abschlussbeleg](completion.md). Commit/Push/Integration sind ausdrücklich nach `main` autorisiert; für NCG wurde `develop` bestätigt. Archivierung ist kein Bestandteil dieses Lieferauftrags.

## Ergänzung: tatsächlich ausgeführter Beispielprozess

Der [Prozessnachweis vom 20.09.2026](evidence/live-process/README.md) ergänzt die ursprünglichen Entscheidungsszenarien: echte CLI-Regression rot → Reparatur → grün, danach drei tatsächliche separate Reviewer in der Reihenfolge DRY → SOLID → KISS. Ein DRY-Befund wurde repariert und vom ursprünglichen Reviewer gezielt nachgeprüft. Sechs abschließende CLI-Tests wurden unabhängig erfolgreich nachgespielt. Ein zweiter tatsächlicher Abschlussaufruf verwendete die geprüften Nachweise ohne neue Reviewer oder CLI-Testläufe. Das bestätigt den Ablauf am isolierten Beispiel. Der separate technische Abschluss dieser Migration (Task 7.7) folgte erst nach ausdrücklicher Abnahme und ist jetzt ebenfalls belegt.
