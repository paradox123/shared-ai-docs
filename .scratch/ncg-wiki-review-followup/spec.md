# NCG-Wiki-Automation: alle Robustheits- und Effizienzfindings

Status: ready-for-agent
Execution: completed
Closed: 2026-10-13

Arbeitsmandat: Daniel hat am 12.10.2026 die Umsetzung aller sechs Findings beauftragt, ask-matt aufgerufen und die Zusammenfassung in einen Fix in derselben Session verlangt. Ein einziges Umsetzungsticket ist veröffentlicht; es braucht keine sechs Implementierungssessions.

Mandatserweiterung 13.10.2026: Daniel beauftragt einen realen Lauf im bestehenden
Automationschat, die Prüfung seines Ergebnisses und den Abschluss dieses Changes.
Die ursprünglichen Implementierungsgrenzen unten beschreiben den Stand vom
12.10.; jetzt sind zusätzlich guarded ncg-docs-main-Lieferung, offizieller
Checkpointabschluss und die etablierte main-Lieferung/Archivierung im
Owning-Repository autorisiert. NCG-Infrastruktur und Implementierungsrepos
bleiben unverändert und read-only.

## Problem Statement

Die NCG-Wiki-Automation besitzt belastbare Quellen- und Checkpointgrenzen, kann aber nach Fehlern dauerhaft blockieren. Das globale Sessionlimit wird vor der NCG-Auswahl angewandt, fehlgeschlagene Seitenversuche können die Wiederaufnahme blockieren und Prozesse besitzen keinen Ablauf. Eigene nicht vollständig gelieferte Dokumentationsänderungen kollidieren mit dem Clean-main-Guard. Der Docs-Prüfstand ist keine gespeicherte Revision. Themenprüfungen wiederholen die vollständige Belegprüfung, während der lange Prompt Regeln mehrfach enthält und sich beim README-Einstieg widerspricht.

## Solution

Ein Wiki-Review-Fenster wird einmal eingefroren und verlustfrei in begrenzten Paketen geprüft. Prozesse und Wiederholungen sind begrenzt und anhand erhaltener Belege nachvollziehbar. Ein Wiki-Lieferbeleg macht ausschließlich eigene Arbeit wiederaufnehmbar. Der vollständige Prüfstand einschließlich separater Docs-Revision wird nach belegter Prüfung/Lieferung wiederaufnehmbar fortgeschrieben. Themen werden mit gleicher Integrität gebündelt geprüft; der Prompt beschreibt einen eindeutigen Ablauf und verweist auf dessen zentrale Verträge.

## User Stories

1. Als Daniel möchte ich auch mehr als 500 Sessions vollständig prüfen lassen, damit ein gewachsenes Fenster die Automation nicht dauerhaft blockiert.
2. Als Daniel möchte ich abgeschlossene Pakete nach Unterbrechung wiederverwenden, damit die Automation keine bereits geprüfte Arbeit wiederholt.
3. Als Daniel möchte ich neue Sessions erst im nächsten eingefrorenen Fenster berücksichtigen, damit Fortschritt und Abdeckung eindeutig bleiben.
4. Als Daniel möchte ich ein bekannt fehlgeschlagenes Paket gezielt erneut versuchen können, ohne seine Fehlerevidenz zu verlieren.
5. Als Daniel möchte ich hängende Prozesse samt ihren eigenen Kindern beenden lassen, damit eine Sperre nicht unbegrenzt liegen bleibt.
6. Als Daniel möchte ich neu auf main gelieferte Docs-Commits trotz alter Commitdaten erkennen, damit die Dokumentationsprüfung nichts durch Datumsfilter übersieht.
7. Als Daniel möchte ich einen fehlenden Docs-Prüfstand ausdrücklich migrieren, damit ein neuer Tip nicht als bereits geprüft ausgegeben wird.
8. Als Daniel möchte ich nach einem fehlgeschlagenen Push ausschließlich die gespeicherte eigene Lieferung wiederaufnehmen können.
9. Als Daniel möchte ich fremde Bearbeitungen und Commits unverändert erhalten und als Blocker erkennen.
10. Als Daniel möchte ich einen bereits erfolgreichen Push nach einem Modellabbruch feststellen, ohne ihn erneut auszulösen.
11. Als Daniel möchte ich den Abschluss nach einem Abbruch während der Checkpointfortschreibung eindeutig fortsetzen können.
12. Als Daniel möchte ich bei fehlenden Kandidatendispositionen, ungelösten Themen oder fehlender Lieferung keinen erfolgreichen Checkpoint erhalten.
13. Als Daniel möchte ich mehrere unveränderte Themen mit einer vollständigen Belegprüfung wiederaufnehmen, damit der Aufwand nicht pro Thema wächst.
14. Als Daniel möchte ich einen kurzen, widerspruchsfreien Automationsvertrag, damit der Agent Regeln zuverlässig befolgen kann.
15. Als Daniel möchte ich nachvollziehbare Verhaltensnachweise mit lokalen Fixtures, damit die Verbesserung ohne Änderungen an NCG-Systemen geprüft wird.

## Implementation Decisions

- Den bestehenden offenen OpenSpec-Change erweitern. Frühere Vorarbeiten, staged/unstaged Inhalte und unabhängige Änderungen erhalten; Zielkontext bleibt shared-ai-docs main. Kein Push/Archive als Teil dieses Implementierungsmandats.
- Bestehende JSONL-Reader bleiben in Python; nur der erforderliche Opt-in-Batchvertrag wird dort ergänzt. Neue Zustand-/Orchestrierungslogik nutzt C#/.NET, bevorzugt File-based Apps, mit vollständigen Anwendungsfällen statt neuen Frameworkschichten.
- Einen Live-Indexsnapshot festhalten. Weitere Resolveraufrufe arbeiten ausschließlich auf verifizierten Originalbytes, gleicher Memorybasis, Exclusion und Fenstergrenze; höchstens 100 Sessions werden pro Aufruf aufgelöst.
- Zusammenhängende vollständige Batchidentität einschließlich Carry beweisen, bevor das Gesamtmanifest für Session-/Themenprüfung freigegeben wird. Den bisherigen Resolververtrag für andere Aufrufer erhalten.
- Prozessdeadline und Ausgabegrenzen ergänzen, eigene Nachkommen kontrolliert beenden und private Diagnosebelege behalten. Bekannte fehlgeschlagene Versuche ausdrücklich supersedieren; erfolgreiche, korrupte oder geänderte Belege unterscheiden.
- Einen separaten Docs-Prüfstand mit Repository, exakt erlaubter main-Referenz und SHA zum offiziellen Bundle hinzufügen. Die vier Backend-/STS-Tips bleiben unverändert. Keine automatische Baseline oder Datumsersatzprüfung.
- Vor Docs-Bearbeitung gewünschte Inhalte, eigenen Ausgangscommit, Pfade/Hashes und Vergleichsbelege privat festhalten. Wiederaufnahme verlangt exakte Übereinstimmung mit dieser vorausgehenden Absicht.
- Vollständige Dispositionen und tatsächlichen Lieferzustand prüfen. Eigene Änderungen über die Verbindung zwischen Originalvergleich und beabsichtigtem Commit verifizieren; fremde Dateien/Commits nie übernehmen oder zurücksetzen.
- Abschlussabsicht vor Memoryersetzung speichern. Mit gemeinsamer Schreibsperre nur erwartetes altes oder exakt beabsichtigtes neues Bundle zulassen, übrige Memory erhalten, Abschlussbeleg und Retirement idempotent beenden.
- Generische Review-Belege und NCG-spezifische Git-/Liefermechanik haben klare Verantwortungsgrenzen. Keine frei übergebenen Git-Befehle oder Erfolgsschalter als Liefernachweis.
- Gebündelte Themenoperationen prüfen einmal pro begrenztem Aufruf vollständig. Blockweise Hashes erhalten exakt die bisherigen Byte-/Zeilengrenzen. Laufzeitversprechen erst nach Messung.
- Den Prompt nach Installation getesteter Verträge verkürzen und die temporäre Totalgrenze durch die Paketgrenze ersetzen. Zeitplan, Zielchat, Modell/Benachrichtigung und konkrete Quellen-/Liefergrenzen bleiben erhalten.

## Testing Decisions

- Die bestehende öffentliche Resolver-CLI und .NET-Request/Response-CLI sind die Verhaltensgrenzen. Kein zusätzlicher Produktinterface-Testseam ist erforderlich; interne Parameter entscheidet die Implementierung.
- Ein Test ist aussagekräftig, wenn er ein unabhängiges beobachtbares Akzeptanzkriterium aus diesem Mandat belegt und vor dem Fix wegen genau dieses Verhaltens scheitert. Keine bloßen Startnachweise oder nachgebauten internen Algorithmen.
- Private synthetische Index-/Rollout-/Memorydateien und lokale Bare-Git-Repositories als Remote nutzen. Restart-Fälle in verschiedenen Prozessen prüfen; keine aktuellen NCG-Systeme als Testumgebung.
- 386 und mehr als 500 gemischte Sessions, gleiche Zeitstempel, Carry vor Cursor, leeres Fenster, Live-Indexwachstum, fehlender Mittelbatch und falsche Bindung prüfen.
- Timeout mit lebendem eigenen Kind, bekannte Extractorfehler, expliziter Retry, beschädigte Quellbelege und wiederverwendete erfolgreiche Seiten prüfen.
- Old-dated neu erreichbare Docs-Commits, fehlende Baseline, ungültige/duplizierte Felder und nicht mehr bestehende Abstammung prüfen.
- Eigene uncommittete/committete Arbeit, gescheiterter/erfolgreicher Push, fremde lokale/Remote-Arbeit, fehlende Disposition und Unterbrechungen vor/nach Memoryersetzung sowie Retirement prüfen.
- Geänderte erlaubte Quellen-Tips, unzulässige Commitprovenienz, veraltete Themen, geänderte Wiki-Blobs und exakte Hashgrenzen bleiben negative Tests.
- Effizienz an einem wiederholbaren Fixture messen; tatsächliche Arbeit und Laufzeit getrennt berichten. Abschließend bestehende relevante Suiten, strikte OpenSpec-Validierung und Diffprüfung durchführen.

## Out of Scope

- NCG-Implementierungsänderungen, Infrastrukturänderungen und produktive Testausführung.
- Ein frischer vollständiger Live-Wiki-Lauf als Teil der Implementierungsprüfung.
- Änderung der erlaubten Backend-/STS-Referenzen, der genehmigten Deleted-carry-Ausnahme oder der main-only Docs-Lieferung.
- Veränderung des echten Reviewspeichers/Checkpoints während der Implementierung; Indexwartung, neue externe Integrationen, Remote-Nachrichten.
- Push/Merge/Archive dieses Changes vor seiner technischen Abnahme.

## Further Notes

Die normative Weiterführung liegt in der [kanonischen Spezifikation](../../openspec/specs/recoverable-wiki-review/spec.md); der [archivierte OpenSpec-Change](../../openspec/changes/archive/2026-10-13-complete-ncg-wiki-review-hardening/proposal.md) bewahrt das konkrete Mandat. Das [einzige Ticket](issues/01-harden-wiki-review.md) umfasst sämtliche Findings. Isolierte End-to-end-Verifikation, realer Lauf und beauftragter Abschluss sind abgeschlossen.
