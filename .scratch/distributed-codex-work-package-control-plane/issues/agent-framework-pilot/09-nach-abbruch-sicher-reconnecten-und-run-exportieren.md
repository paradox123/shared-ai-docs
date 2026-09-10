# 09: Nach einem Abbruch sicher reconnecten und den Run exportieren

**What to build:** Ein berechtigter Benutzer kann einen fehlgeschlagenen Run von einem anderen Client ab der letzten bestätigten Eventposition lückenlos weiterlesen und als redigiertes, portables Run-Dossier einschließlich Artefakten exportieren und wiederherstellen.

**Blocked by:** 03: Repositoryzugriff und exklusive Steuerung durchsetzen; 04: Einen Fake-Codex-Versuch transparent scheitern und wiederherstellen

**Status:** ready-for-agent

- [ ] Reconnect mit bestätigter Eventposition liefert nach Client-, API- und Workerrestart alle späteren autorisierten Ereignisse genau einmal und in stabiler Reihenfolge.
- [ ] Der Nachweis umfasst mehr als 10.000 Events, eine große Live-Ausgabe sowie einen fehlgeschlagenen oder abgebrochenen Run.
- [ ] Große und binäre Artefakte bleiben unveränderlich, checksum-gebunden und außerhalb des Workflow-Kernzustands referenziert.
- [ ] Kontrollierte Secrets, Tokens, Credentials, E-Mail-Adressen und Personen-Canaries erscheinen in keiner Datenbank-, Artefakt-, Log-, Export- oder Clientoberfläche roh.
- [ ] Redaction oder Nichtverfügbarkeit bleibt mit Policy-Version sichtbar und auditierbar.
- [ ] Der Export enthält Domain-History, Projektionen, Artefaktmanifest, Runtime-/Adapter-Provenance und Framework-Korrelation, aber keine Abhängigkeit von einem proprietären Dashboardformat.
- [ ] Restore in frische lokale Komponenten erzeugt dieselben öffentlichen History- und Artefaktchecksummen.
- [ ] Fehlende oder korrupte Artefakte werden sichtbar und können keine spätere Qualification passieren.

## Session lesson

Beim LangGraph-Piloten gingen konkrete JSONL-Diagnosen verloren. Das portable Dossier bewahrt redigierte Originalbeobachtungen unabhängig vom ausführenden Prozess.
