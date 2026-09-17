# Wiederaufnehmbare Pflege: Ticket 05

Isolierte Implementierung der Quellenabweichungs-Prüfung im bestehenden Paketmodell. Kein produktiver Pflegeaufruf, keine Automation, kein Modell- oder Dependencywechsel. Der Compiler bleibt auf `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb` mit den unveränderten fünf vorhandenen Patches.

## Soll und beobachtetes Verhalten

| Vertrag | Beobachtung durch öffentliche Schnittstelle |
| --- | --- |
| Originale vor Wiederverwendung und Publikation prüfen | Wartender Cachekandidat wird bei inzwischen geändertem Original mit Quellenfehler zurückgewiesen, statt als erfolgreicher Treffer zu zählen. Vollständiger Re-Scan vor Publikation liefert abweichende Identitäten; Konfigurations-/Scan-/externe Seitenfehler bleiben gemeinsame Blocker. |
| Drift isolieren, unbekannte Zugehörigkeit nicht erraten | Echter Helper wird am lokalen Provider gehalten; Alpha ändert sich erneut. Globale Freigabesynthese über Alpha und Beta sowie direkte/transitive Antworten bleiben gesperrt. Aktuelle Kontrollquelle veröffentlicht als ausdrücklich quellgebundene Wiki-Seite; WikiQuery verwendet diese ohne Rohquellen-Fallback. |
| Unabhängige Wissensarbeit bewahren | Neue Quelle während Generierung macht globale Zugehörigkeit unbekannt. Bestehende gültige reine Quellenantwort bleibt bytegleich und über WikiQuery auffindbar. Noch sichere Extraktionen bleiben dauerhaft gespeichert. |
| Gezielte Wiederaufnahme | Neuer Helper-Prozess fordert nur eine geänderte Alpha-Extraktion an. Danach ist die tatsächliche gemeinsame Synthese mit Alpha-/Beta-Provenienz wieder vorhanden, ebenso beide Antwortkettenstufen. Folgeprozess ist No-op ohne neue Modellrequests. |
| Isolierter Antwortfehler | Direkte und transitive Antwort bleiben zurückgezogen; unabhängige Kontrollantwort bleibt bytegleich und suchbar. Reparatur fordert keine Extraktionen an und führt zum No-op. |
| Quellenfehler, Entfernung, Scanfehler unterscheiden | Bestehende öffentliche Fälle prüfen source_error, unbekannte Abhängigkeit, bestätigte Entfernung und nicht verfügbaren Repo-Root. Ein fehlender Root ist keine Massenentfernung. Ticket-04-Gegenproben prüfen außerdem Entfernung bereits veröffentlichter Quellseiten/Antworten über echtes QMD. |
| Später Indexfehler | Reale QMD-Datei wird nur im eigenen Fixture nach Generierung unzugänglich gemacht. Ergebnis bleibt unvollständig; kompatible Arbeit bleibt erhalten. Reparatur und anschließender No-op benötigen keinerlei neue Modellrequests. Ein davor erfolgreich gepflegter Originalindex ist separat vom fehlgeschlagenen Wiki-Index ausgewiesen. |
| Bereits beobachtete Drift startet die Tagesfrist | Derselbe vollständige Re-Scan aktualisiert das vorhandene Inventar sofort. Eine geänderte Initialversion wird im laufenden Bericht daily; ein späterer Neustart setzt ihre Beobachtung und Frist nicht zurück. Kontrollierte Uhr: Beobachtung 17.09., Frist 18.09., Wiederaufnahme 20.09. meldet überfällig. |
| Keine falsche Frische oder Gesamtabschluss | Drift markiert die inzwischen überholte Originalindex-Momentaufnahme `ok: false, status: stale`; WikiQuery prüft weiterhin jedes Original. Tagesrest, Erstimportrest und globale Vollständigkeit bleiben getrennt. `lastCompleted` steigt bei offenen Paketen nicht. |

## Grenzen

Die alte Konzeptzuordnung einer inzwischen geänderten Quelle beweist nicht die Zugehörigkeit ihrer neuesten Fassung. Deshalb wird während unbekannter Zugehörigkeit keine unabhängige **globale** Konzeptseite behauptet. Die unabhängige Veröffentlichung nutzt die in Ticket 04 eingeführte quellgebundene Einheit im selben Wiki. Ein späterer Prozess stellt die gemeinsame Synthese nach vollständiger Abhängigkeitsprüfung wieder her. Modell-Semantik wird nicht formal garantiert; die kontrollierten Providerantworten und tatsächlich übergebene Evidenz dienen als überprüfbare Fixture-Fakten.

Die integrierten Helper-Proben führen Wiki-CLI, Compiler und eigene QMD-Datenbank tatsächlich aus; nur der vaultweite Reconciler und zusätzliche globale QMD-Schritte sind isolierte Peers (`/usr/bin/true`), damit kein Produktivindex berührt wird. Kein Anspruch auf erfolgreiche produktive globale Indexpflege. Die endlichen Testbudgets sind Fehlerexperiment-Grenzen, keine produktive Durchsatzmessung; diese gehört zu Ticket 06.

## Nachweise und Prüfung

Dauerhafte Rohartefakte und lesbare Abnahmematrix liegen unter `/Users/dh/.codex/batches/01a0af21-127f-7833-b0c1-136e653dc476/ticket05/`. `acceptance.json` benennt die tatsächlichen Messdateien, `acceptance.md` die Prüfungsergebnisse und Grenzen. Tests: `maintenance-drift.test.ts` (Helper-Drift, neue Zugehörigkeit, wartende Cache-Version, Antwortketten), erweiterter realer QMD-Fehlerfall in `extraction-resume.test.ts` und vorhandene Prioritäts-/Lebensdauer-/Fehlerregressionen.

Die separate kritische Batch-Abnahme und das exakte Merge-Gate folgen vor Integration. Live-Aktivierung, nächster tatsächlicher Schedulerlauf und vollständiger produktiver Erstimport bleiben außerhalb dieser isolierten Abnahme. Der aktive OpenSpec-Change bleibt offen.

## Separate kritische Verifikation

Nach initial-ready wurden fünf zusätzliche öffentliche Gegenfälle geprüft: kombinierte bestätigte Entfernung und Versionsdrift, erst nach Startscan unerreichbarer Root, realer QMD-Dateifehler nach bereits beobachteter Drift einschließlich erhaltener Tagesfrist, geänderte Evidenz während gehaltener Queryantwort mit Save sowie der Wechsel einer Driftquelle in das zuvor unabhängige Kontrollkonzept. Alle fünf sind grün; kein zusätzlicher Produktfix war erforderlich. Alte Konzeptbesitzer begründen keine falsche Unabhängigkeit: während unbekannter neuer Zuordnung bleibt die globale Seite gesperrt, anschließend belegt die gemeinsame Seite tatsächlich beide aktuellen Besitzer. `critical-acceptance.md/json` im dauerhaften Batchverzeichnis enthält Soll/Ist, tatsächliche Rohmessungen, Hashes und Grenzen.

Prüfstand: vollständige Baseline107Fälle mit106grünen Ergebnissen und einer versehentlich ergänzten Testassertion, anschließend korrigiert. Finaler betroffener Stand26/26 plus5/5kritischeFälle, Compiler59/59, Helper8/8, Typecheck/OpenSpec/Diffcheck. Ein erneuter vollständiger107/107-Lauf wird nicht behauptet. Der unabhängige SpecReview-P2 zur Fristbeobachtung wurde repariert und nachgeprüft; keine offenen Pflichtbefunde beider Reviewachsen. Noch kein Integrations-/Mergeabschluss.

Die endgültige kritische Messung korrigiert außerdem den generischen Testprovider: Er gibt nur im tatsächlichen Request enthaltene Fakten und Beleg-IDs aus. Removal- und Ownershipqueries prüfen nun Antwortinhalt **und** gespeicherte Queryrequests positiv/negativ. Entfernte Beta-Evidenz, Alpha-Inhalt in der Beta-begrenzten Anfrage und erfundene „Beide Repos“-Aussagen sind ausgeschlossen. Alle fünf Gegenfälle wurden auf dieser finalen Testdatei gemeinsam erneut grün gemessen (28,28s), Produktbytes unverändert. Die frühere generische Providerantwort ist kein finaler Inhaltsnachweis; ihre Vorstufe bleibt im Batchverzeichnis nachvollziehbar.
