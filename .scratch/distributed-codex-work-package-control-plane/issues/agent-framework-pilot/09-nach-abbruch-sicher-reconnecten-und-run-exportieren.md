# 09: Nach einem Abbruch sicher reconnecten und den Run exportieren

**What to build:** Ein berechtigter Benutzer kann einen fehlgeschlagenen Run von einem anderen Client ab der letzten bestätigten Eventposition lückenlos weiterlesen und als redigiertes, portables Run-Dossier einschließlich Artefakten exportieren und wiederherstellen.

**Blocked by:** 03: Repositoryzugriff und exklusive Steuerung durchsetzen; 04: Einen Fake-Codex-Versuch transparent scheitern und wiederherstellen

**Status:** resolved

- [x] Reconnect mit bestätigter Eventposition liefert nach Client-, API- und Workerrestart alle späteren autorisierten Ereignisse genau einmal und in stabiler Reihenfolge.
- [x] Der Nachweis umfasst mehr als 10.000 Events, eine große Live-Ausgabe sowie einen fehlgeschlagenen oder abgebrochenen Run.
- [x] Große und binäre Artefakte bleiben unveränderlich, checksum-gebunden und außerhalb des Workflow-Kernzustands referenziert.
- [x] Kontrollierte Secrets, Tokens, Credentials, E-Mail-Adressen und Personen-Canaries erscheinen in keiner Datenbank-, Artefakt-, Log-, Export- oder Clientoberfläche roh.
- [x] Redaction oder Nichtverfügbarkeit bleibt mit Policy-Version sichtbar und auditierbar.
- [x] Der Export enthält Domain-History, Projektionen, Artefaktmanifest, Runtime-/Adapter-Provenance und Framework-Korrelation, aber keine Abhängigkeit von einem proprietären Dashboardformat.
- [x] Restore in frische lokale Komponenten erzeugt dieselben öffentlichen History- und Artefaktchecksummen.
- [x] Fehlende oder korrupte Artefakte werden sichtbar und können keine spätere Qualification passieren.

## Session lesson

Beim LangGraph-Piloten gingen konkrete JSONL-Diagnosen verloren. Das portable Dossier bewahrt redigierte Originalbeobachtungen unabhängig vom ausführenden Prozess.


## Outcome

**Implementiert und verifiziert (2026-09-12).** OpenSpec-Change
`reconnect-and-export-run` ergänzt begrenzte Cursor-Seiten, autorisierten SSE-Replay,
checksum-gebundene redigierte Artefakte sowie ZIP-Export und schreibgeschützten
Restore in frische lokale Komponenten.

Der öffentliche Prozessnachweis umfasst 10.015 Events, rund 12 MB Live-Stream,
zwei hart beendete Worker und einen API-Abbruch. Ab bestätigter Position 250 lesen
andere Clients dieselben 9.765 späteren Events ohne Lücken oder Duplikate. Der
fehlgeschlagene Run wird in einem zweiten PostgreSQL-/API-/Artefakt-Setup mit
identischen öffentlichen Prüfsummen wiederhergestellt. 35 geprüfte Oberflächen
enthalten keinen rohen Canary aus den sechs kontrollierten Kategorien.

101 Regressionstests und anschließend 22 gezielte Tests zum letzten URI-Fix
bestehen; insgesamt sind 102 unterschiedliche Tests nachgewiesen. Locked Restore,
Build ohne Warnungen, strikte OpenSpec-Validierung und der begrenzte Diff-Check
sind erfolgreich. Die Head-Qualification selbst bleibt Ticket 13; dieses Ticket
liefert ihre sperrende Artefakt-Voraussetzung.

- [Akzeptanzübersicht und Grenzen](../../../../openspec/changes/archive/2026-09-12-reconnect-and-export-run/implementation-evidence.md)
- [Öffentliche Checksummen und Reconnect-Nachweis](../../../../openspec/changes/archive/2026-09-12-reconnect-and-export-run/evidence/public-proof.json)
- [Exportiertes Beispieldossier](../../../../openspec/changes/archive/2026-09-12-reconnect-and-export-run/evidence/run-dossier.zip)
- [Betrieb und CLI](../../../../microsoft-agent-framework-work-package-pilot/README.md#reconnect-and-portable-run-dossier-ticket-09)

## Acceptance

**Akzeptiert und abgeschlossen (2026-09-12).** Der Benutzer hat die Implementierung
ausdrücklich abgenommen und Archivierung, Commit und Push beauftragt. Der
OpenSpec-Change wurde über `openspec archive -y reconnect-and-export-run`
archiviert; seine vier Anforderungen sind in der
[kanonischen Spec](../../../../openspec/specs/portable-run-dossier/spec.md)
übernommen. Das Ticket bleibt `resolved`.
