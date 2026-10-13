# 01: NCG-Wiki-Review vollständig robust und effizient machen

Status: ready-for-agent
Execution: completed
Closed: 2026-10-13
Blocked by: None

## Arbeitsmandat

Daniel beauftragt am 12.10.2026 sämtliche sechs Reviewfindings und verlangt ausdrücklich deren Zusammenfassung in einen Fix in derselben Session. Die [Spec](../spec.md) und der [archivierte OpenSpec-Change](../../../openspec/changes/archive/2026-10-13-complete-ncg-wiki-review-hardening/proposal.md) sind die Anforderungsquellen. Es entstehen keine sechs Implementierungssessions oder zusätzlichen Nutzerchats.

Am 13.10.2026 erweitert Daniel das Mandat um einen realen Automationslauf im
bestehenden Chat, unabhängige Ergebnisprüfung und Changeabschluss. Die untere
Delivery boundary beschreibt das ursprüngliche Implementierungsmandat;
guarded Docs-main-Lieferung, offizieller Checkpoint und der etablierte
shared-ai-docs-main-Abschluss mit Archivierung sind jetzt ebenfalls autorisiert.

## What to build

Die vorhandene Automation kann ein beliebig gewachsenes eingefrorenes Review-Fenster in begrenzten Paketen vollständig prüfen, bekannte technische Fehler gezielt wiederaufnehmen und ausschließlich eigene Docs-Lieferungen nach Unterbrechung erkennen. Der vollständige Checkpoint mit separater Docs-Revision wird idempotent abgeschlossen. Themenprüfung und Prompt werden effizienter, ohne Quellen-, Privacy-, Carry- oder main-only-Grenzen abzuschwächen.

## Acceptance criteria

- [x] Mehr als 500 gemischte Sessions werden über einen einzigen Live-Snapshot in Paketen von höchstens 100 aufgelösten Sessions vollständig erfasst. Neustart wiederverwendet erfolgreiche Pakete; fehlende/fremde/duplizierte Pakete, falsche Fensterbindung und unzulässige Missing-Carry-Ausnahmen blockieren. Legacy-Resolver bleibt kompatibel.
- [x] Subprozesse und eigene Nachkommen haben begrenzte Laufzeit/Ausgabe und geschützte Fehlerdiagnosen. Ein expliziter Retry ersetzt nur einen bekannten fehlgeschlagenen Versuch mit unveränderten Inputs; erfolgreiche und korrupte Belege bleiben verschieden behandelt.
- [x] Separater Docs-Prüfstand verwendet ancestry-validierte SHA-Bereiche und erkennt old-dated neu erreichbare Commits. Fehlende Baseline wird ausdrücklich geprüft, ungültige/duplizierte/rewritten Zustände blockieren, vier Code-Pins bleiben exakt vier.
- [x] Gebündelte Themenoperationen verwenden eine aktuelle Vollständigkeitsprüfung je begrenztem Aufruf. Blockweise Hashes erhalten genau die bisherigen Raw-byte-/Zeilengrenzen sowie Mutations-/Truncation-/Append-only-Regeln. Effizienz wird an einem wiederholbaren Fixture tatsächlich gemessen.
- [x] Vorausgehende Lieferabsicht bindet base SHA, eigene Pfade/gewünschte Inhalte und Vergleichsbelege. Local bare Git Fixtures beweisen Wiederaufnahme eigener Edits/Commit/Push, erkennen schon erfolgte Lieferung und blockieren fremde Arbeit ohne destruktive Recovery.
- [x] Vollständige Kandidatendispositionen, erlaubte aktuelle Quellen und notwendige Lieferung werden vor journalisiertem Memoryabschluss geprüft. Offizielle Bundlewerte werden aus Manifest/Belegen abgeleitet, nicht aus Caller-Erfolgsschaltern. Unterbrechungen rund um Memoryersetzung, Receipt und Retirement sind idempotent; fremder Stand blockiert.
- [x] Der kurze eindeutige Prompt nutzt nur vorhandene getestete Verträge, erlaubt die notwendige Bootstrap-README und enthält keine konkurrierenden Mechanikregeln. Zeitplan/Zielchat/unrelated fields sowie sämtliche fachlichen Gates bleiben erhalten; live definition readback belegt die Änderung.
- [x] Bestehende relevante Suiten, isolierter öffentlicher CLI-Gesamtlauf, strikte OpenSpec-Validierung und Diffprüfung bestehen. Echtes Memory bleibt unverändert; bestehende Nutzeränderungen bleiben erhalten. Nachweise unterscheiden Implementierungsreife von neuem Live-Wiki-Erfolg.

## Delivery boundary

Owning repository: shared-ai-docs, vorhandener main-Kontext mit geschützten staged/unstaged Vorarbeiten. Neue Logik bevorzugt C#/.NET File-based Apps, Anwendungsfälle als Vertical Slices; vorhandene Python-Reader bleiben als konkrete Runtimebindung. Keine Infrastrukturänderung, keine Änderung an NCG-Codeworktrees, keine produktive Testausführung. Repository-Push/Archive sind nicht Teil dieses Implementierungsauftrags.

## Comments

- 12.10.2026: Ticketzuschnitt auf Daniels Wunsch zusammengefasst; Umsetzung läuft in der bestehenden Session mit intern delegierbaren Teilaufgaben.

- 12.10.2026: Alle Kriterien öffentlich/isoliert geprüft; DRY, SOLID und KISS einschließlich gezielter Reparatur-Nachprüfungen sauber. Automationprompt installiert, echtes Memory unverändert. [Abschlussnachweis](../../../openspec/changes/archive/2026-10-13-complete-ncg-wiki-review-hardening/completion.md); bereit zur Abnahme, ohne Repository-Push/Archive/Issueabschluss.

- 13.10.2026: Daniels Live-/Abschlussmandat erfüllt. Der reale Lauf liefert neun Wiki-Dateien und einen offiziellen vollständigen Checkpoint. Die unabhängige Originalcodeprüfung findet einen falschen Buchungszeitraum; ein separater guarded Folgelauf korrigiert genau eine Zeile, liefert Commit 2115e5d857992d710cec5a4075c9140965b66cdb auf ncg-docs main und finalisiert. Beide root-seitigen identischen Finalize-Wiederholungen verändern Memory/Receipts nicht. Technisch abgeschlossen; Standardarchiv erstellt, scoped shared-ai-docs-main-Lieferung anhand der Indexidentität vorbereitet mit erhaltener Fremdarbeit. Status bleibt die historische Triageklassifikation; Execution/Closed dokumentieren den tatsächlichen Abschluss.
