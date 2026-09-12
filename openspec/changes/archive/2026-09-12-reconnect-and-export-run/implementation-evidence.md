# Ticket 09 — Reconnect und portables Run-Dossier

Stand: 2026-09-12. Die Implementierung wurde vom Benutzer akzeptiert und der
OpenSpec-Change über den Standardpfad archiviert. Die vier Anforderungen stehen
in der [kanonischen Spec](../../../specs/portable-run-dossier/spec.md).
Es wurde kein laufender Datenbestand migriert.

Der öffentliche Prozessnachweis enthält einen fehlgeschlagenen Run mit **10.015
Events**. Nach bestätigter Position **250** liest ein anderer Client **9.765
Events** über SSE und dieselbe Folge über HTTP-Seiten: null Lücken, Duplikate und
Umordnungen. Dabei werden ein Worker nach rohem Antwortempfang vor dem Commit,
ein weiterer Worker nach Source-Event 5000 und die API mit SIGKILL beendet.
Ein Ersatz-Worker führt dieselbe Session bis `process-failure` fort. Der Stream
umfasst **12.027.444 Bytes**; die große Originalausgabe bleibt zusätzlich als
checksum-geprüftes Artefakt abrufbar.

Die zweite PostgreSQL-/API-Umgebung und ihre separate Artefaktablage liefern nach
Restore dieselben öffentlichen History-, Projektions- und Artefaktprüfsummen.
Der Vergleich und die konkreten ersten/letzten Reconnect-Events stehen im
[öffentlichen Nachweis](evidence/public-proof.json). Das tatsächlich exportierte,
redigierte [Run-Dossier](evidence/run-dossier.zip) ist 865.665 Bytes groß; seine
deklarierten Dateiprüfsummen wurden nach dem Speichern nochmals überprüft.

## Akzeptanzübersicht

| Anforderung | Erwartetes Verhalten | Beobachtetes Ergebnis und Beleg |
| --- | --- | --- |
| Reconnect nach Client-/API-/Workerrestart | Alle Events nach bestätigtem Cursor genau einmal und geordnet; frische Repositoryberechtigung | 250 → 10.015 mit 9.765 identischen Events über SSE/Seiten. Separater SSE-Test entzieht Leserechte und beobachtet `access-revoked` sowie anschließendes HTTP 403. [Prozessnachweis](evidence/public-proof.json), Cursor-/SSE-Tests. |
| Mehr als 10.000 Events, große Ausgabe, fehlgeschlagener Run | Der Nachweis benötigt keinen erfolgreichen Abschluss | 10.015 Events, rund 12 MB Stream, große Ausgabe von über 200 KB, Endzustand `process-failure`. [Prozessnachweis](evidence/public-proof.json). |
| Große und binäre Artefakte außerhalb des Workflow-Kernzustands | Unveränderliche Bytes, SHA-256-Bindung und kleine Projektionen | Text, JSON/JSONL, eine 256-KiB-Binärdatei und große Original-/Endergebnisse sind öffentlich checksum-geprüft abrufbar. Große Projektionen bleiben unter 20 KB; Recovery liest dieselben Originalbytes. Tests für Artefakte, große Originale/Endergebnisse und aktive Operationen. |
| Keine rohen kontrollierten sensiblen Werte | Redaction vor Datenbank, Artefakten, Logs, Export und Clients | 35 Oberflächen aus beiden Datenbanken, beiden Artefaktablagen, Workerlogs, Clientpayloads und entpacktem Dossier: null Treffer für Secret, Token, Authorization, Credential, E-Mail und Person. Zusätzliche Tests prüfen Base64, Unicode-Escapes in JSONL und UTF-16 in Binärdaten. [Scanergebnis](evidence/public-proof.json). |
| Redaction/Nichtverfügbarkeit auditierbar | Marker, Policy-Version und konkreter Verfügbarkeitsgrund | `controlled-dossier-canary-v1` bleibt in Events/Manifesten erhalten. Sensible Binärdaten werden als `binary-controlled-canary` zurückgehalten; URI-only-Quellereignisse erhalten `external-artifact-unavailable`. HTTP 410 liefert das jeweilige Manifest. |
| Portabler vollständiger Export | Domain-History, Projektion, Artefakte, Provenance und Framework-Korrelation | ZIP/JSON enthält `history.json`, `projection.json`, Manifest und verfügbare Blobdateien. Exporttest prüft Admission-Provenance, Adaptervertrag, Runtime und eine kontrolliert übermittelte DTS-Korrelation; die CLI lädt das Dossier herunter. [Beispieldossier](evidence/run-dossier.zip). |
| Restore in frische lokale Komponenten | Identische öffentliche History-/Projektions-/Artefaktchecksummen | Zwei getrennte PostgreSQL-Container, APIs und Artefaktwurzeln liefern identische Checksummen. History-Seiten und Blobdownloads bleiben gleich, Leserechte werden neu geprüft, Control Claim wird mit `restored-dossier-read-only` abgewiesen. [Vergleich](evidence/public-proof.json), Restore-Test. |
| Fehlende oder korrupte Artefakte verhindern spätere Qualification | Fehlende Evidence bleibt sichtbar und sperrt die Artefakt-Voraussetzung | Entfernte/manipulierte Dateien und ZIP-Einträge werden als `missing`/`corrupt` angezeigt; `qualificationEligible` ist false und Downloads liefern 410. Restore/Reexport bewahren diese Zustände. Entferntes Manifestinventar oder beschädigte History verhindern die Veröffentlichung des Imports. |

Die genannten Verhaltenstests stehen in
[test_run_dossier.py](../../../../microsoft-agent-framework-work-package-pilot/tests/test_run_dossier.py).
Sie prüfen HTTP-/CLI-Verträge und separate Prozesse; die Datenbank-Dumps dienen
ausschließlich dem ergänzenden negativen Canary-Nachweis.

## Verifikation und Review

- Locked Restore und Build: erfolgreich, null Warnungen und Fehler.
- Vollständige Regression: **101 Tests erfolgreich**, 305,455 Sekunden;
  [unverändertes Testprotokoll](verification.log).
- Nach Ergänzung der URI-only-Erfassung: **22 Tests erfolgreich** (neuer URI-Test
  und sämtliche 21 Fake-Codex-Tests), 65,401 Sekunden. Zusammen sind damit
  **102 unterschiedliche Tests** nachgewiesen. [Ergänzende Verifikation](supplemental-verification.md).
- `openspec validate reconnect-and-export-run --strict`: erfolgreich.
- `git diff --check` für Pilot/Change und eine zusätzliche Whitespace-Prüfung
  der neu angelegten Quelldateien: erfolgreich.

Der lokale Review hat History-/Projektions-Snapshot, Cursorgrenzen, Artefaktidentität,
Redaction vor Speicherung, Importvalidierung und Schreibsperre geprüft. Gemeinsame
Snapshot-Reads speisen Export und Checksummen; Adapterpfade teilen die
Artefakterfassung und Event-Envelopes; kanonisches JSON liegt in einem reinen
Domain-Helfer. Beim Review gefundene Lücken für große Endergebnisse und reine
URI-Verweise wurden jeweils durch einen zunächst fehlschlagenden Verhaltenstest
geschlossen. ZIP-Restore speichert öffentliche historische Ansichten und kopiert
keine internen Workflowtabellen oder ausführbaren Workerzustände.

Der globale Diff-Check meldet weiterhin vorbestehenden Whitespace in `AGENTS.md`,
Zeile 46. Die fremden Änderungen an AGENTS/CONTEXT und den LLM-Wiki-Dokumenten
wurden unverändert gelassen.

## Abschluss nach Abnahme

Vor dem Archivieren wurden Diff und angrenzender Code erneut auf DRY, SOLID und
KISS geprüft. Die gemeinsamen Snapshot-Reads, Artefakt-Speichergrenzen und
kanonische JSON-Darstellung benötigen keine weitere Verhaltensänderung.

`openspec archive -y reconnect-and-export-run` hat den vollständigen Change mit
Schema `spec-driven` über den Standardpfad archiviert und alle vier Anforderungen
in die kanonische Spec übernommen. Es gab keine offenen Aufgaben oder akzeptierten
Vollständigkeitswarnungen. Nach dem Archivieren bestehen die repositoryweite
strikte OpenSpec-Validierung mit **43/43 Einträgen**, die Prüfung aller verschobenen
Evidence-Links, die erneute Prüfung der ZIP-Dateiprüfsummen und der Diff-Check des
Commit-Umfangs. Der oben dokumentierte fremde Whitespace-Befund bleibt unverändert.

Nach dem Abschlussreview besteht außerdem das gesamte Dossier-Modul erneut:
**15 Tests in 169,314 Sekunden, OK**, einschließlich des Prozessnachweises mit
10.015 Events und Restore in frische Komponenten. Der erneute synthetische Run
ist in der [ergänzenden Verifikation](supplemental-verification.md#abschlussverifikation)
zusammengefasst; das ursprüngliche Beispieldossier wurde unverändert bewahrt.

## Grenzen des Nachweises

Der Nachweis verwendet neu aufgenommene synthetische Runs, kontrollierte externe
HTTP-Provider und den lokalen Agent-Framework-Graphen. Live-Codex, echte
GitHub-Identitäten und neue automatische Azure-DTS-Dispatches wurden nicht
ausgeführt; dafür bleiben die vorgesehenen weiteren Pilottickets zuständig.
Die DTS-Korrelation im Exporttest ist ausdrücklich ein kontrollierter Eingabewert.

Restore liefert schreibgeschützte historische Ansichten. Die spätere
Head-Qualification muss die hier implementierte Artefakt-Voraussetzung zusammen
mit ihren übrigen Evidence-/Review-Gates auswerten. Die Policy erkennt die
konfigurierten Canaries; allgemeine produktive PII-Erkennung und Retention sind
kein Bestandteil dieses Tickets. Betriebsgrenzen und Aufrufbeispiele stehen im
[Pilot-README](../../../../microsoft-agent-framework-work-package-pilot/README.md#reconnect-and-portable-run-dossier-ticket-09).
