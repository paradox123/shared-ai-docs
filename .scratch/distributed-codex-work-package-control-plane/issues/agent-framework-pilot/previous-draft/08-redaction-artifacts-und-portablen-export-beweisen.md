# 08: Redaction, Artefakte und portablen Export beweisen

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Run History und große Artefakte bleiben vollständig beobachtbar, vor jeder dauerhaften Verwendung redigiert, checksum-gebunden und unabhängig von Framework-History exportier- und wiederherstellbar.

**Blocked by:** 02: Kanonischen Run, History und Operator-Read-back bauen; 07: Evidence, Qualification und bounded Repair umsetzen

**Covers:** US 27-35, 55-63, 77-78, 102, 105, 129-130

**LangGraph baseline:** Issue 03 und 08; Evidence-/Redaction-Contracts und öffentliche Read-back-Tests.

**Status:** needs-triage

- [ ] Kontrollierte Secret-, Token-, Credential-, E-Mail- und Personen-Canaries erscheinen in keiner Datenbank-, Artefakt-, Log-, Export- oder Clientoberfläche roh.
- [ ] Redaction oder Nichtverfügbarkeit bleibt mit Policy-Version sichtbar und auditierbar.
- [ ] Große Outputs liegen unveränderlich und checksum-gebunden außerhalb des Workflow-Kernzustands.
- [ ] Ein Export enthält Domain-Events, Projektionen, Artefaktmanifest, Adapter-/Runtime-Provenance und Framework-Korrelation, aber keine Abhängigkeit von proprietärem Dashboardformat.
- [ ] Restore in frische lokale Komponenten erzeugt identische öffentliche Event-/Projektionschecksummen.
- [ ] Fehlende oder korrupte Artefakte blockieren Qualification sichtbar.
- [ ] Cursor-Reconnect wird mit mehr als 10.000 Events, mehr als 16 KiB Live-Ausgabe und einem fehlgeschlagenen Run bewiesen.

## Session lesson

Der LangGraph-Adapter verwarf bei Fehlern JSONL und konkrete Ergebnisursache. Im neuen Pilot wird redigierte Rohbeobachtung zuerst als Artefakt gesichert und erst danach interpretiert.
