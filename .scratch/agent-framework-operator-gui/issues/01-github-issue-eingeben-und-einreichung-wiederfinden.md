# 01: GitHub Issue eingeben und gespeicherte Einreichung wiederfinden

**What to build:** Ein Mensch gibt in einer minimalen servergestützten GUI eine GitHub-Issue-URL ein und sieht den tatsächlich aufgenommenen Auftrag mit Inhalt, Herkunft und Repository in seiner Einreichungsübersicht.

**Blocked by:** None (can start immediately).

**Status:** resolved

- [x] Die GUI nimmt eine echte GitHub-Issue-URL entgegen und zeigt den aufgenommenen Titel, Inhalt beziehungsweise dessen Fassung, Quelle, Zielrepository und eindeutige Einreichungsidentität. Ein vorgefertigter Run ist nicht nötig.
- [x] Der Server liest den tatsächlichen Providerinhalt und prüft die bestehende Repository-Identität und Implementierungsfreigabe; synthetische Fixtures oder Auftragspläne werden nicht von Benutzern vorbereitet. Nötige Entkopplung der bisherigen Quellenaufnahme erfolgt kompatibel vor der neuen Aufnahme.
- [x] Die Einreichung wird mit ihrem Inhalt und ihrer Herkunft in der Datenbank gespeichert und ist nach Client-/Service-Neustart über die GUI wieder lesbar. Spätere Quelländerungen ersetzen nicht still die aufgenommene Fassung; wiederholte Übermittlung desselben logischen Auftrags erzeugt kein Duplikat.
- [x] Der Zugriff funktioniert zwischen Server- und Browserprozess auf demselben Rechner mit der menschlichen Repository-Identität. Nur Anforderungen aus berechtigten Repositories sind sichtbar; fehlender Zugriff und ungültige Quelle werden konkret gemeldet, und bestehende Redaktionsregeln gelten vor Speicherung und Anzeige. Der Mehrrechnertest gehört zur Abnahme in [Ticket 16](16-verteilten-gesamtfall-und-issue-14-gates-nachweisen.md).
- [x] Die Abnahme beginnt mit leerer Anwendungsdatenbank und prüft über echte GUI-Eingabe plus öffentliches Readback die gespeicherten fachlichen Inhalte. Die Einreichung wird ausdrücklich als aufgenommen angezeigt und noch nicht als laufender Run ausgegeben; dieses Ticket startet keine Agentenverarbeitung.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.

### 2026-09-14 — Implementierung und direkte lokale Abnahme

Implementiert im isolierten Branch `codex/operator-gui-issue-01`: serverseitige
GitHub-Aufnahme, unveränderliche redigierte Einreichung in PostgreSQL, GUI mit
Repository-/Quellfassung/Identität, aktuelle menschliche GitHub-Berechtigung und
idempotente Wiederholung. Die GUI zeigt ausdrücklich „Aufgenommen“ ohne Run oder
Agentenstart. Der bisherige synthetische API-/CLI-Aufnahmepfad bleibt separat.

Die reale Aufnahme von `paradox123/probare-crm#4` begann mit leerer Testdatenbank
und wurde über GUI sowie öffentliches Readback einschließlich API-Neustart und
neuem Browserprozess geprüft. Die Tests zu Quelländerungen, parallelen
Übermittlungen, Redaktion, sicheren Textinhalten und Zugriffsfehlern bestehen.
Die vollständige Pilot-Regression ist grün: 204 Tests, davon 183 bestanden und
21 optionale Integrationstests übersprungen. Standards-Review ohne offene
Findings; Spec-Review mit dem unten genannten offenen Mehrrechnernachweis.

### 2026-09-14 — Lokale Abnahme durch den Nutzer

Der Nutzer nimmt Ticket 01 auf Basis der vorhandenen lokalen Nachweise ab.
Status: `resolved`. Die Tests liefen auf einem Mac mit getrennten Prozessen;
der Mehrrechnernachweis bleibt offen und ist verbindlich nach
[Ticket 16](16-verteilten-gesamtfall-und-issue-14-gates-nachweisen.md) verschoben.
Er blockiert Ticket 01 und dessen Nachfolger nicht mehr. Die verteilte
Gesamtabnahme und der OpenSpec-Change bleiben offen.
Details und Reviewstand: [OpenSpec-Nachweise](../../../openspec/changes/add-agent-framework-operator-gui/issue-01-evidence.md).
