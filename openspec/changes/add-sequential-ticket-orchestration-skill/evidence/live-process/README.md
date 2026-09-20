# Ausgeführter Prozessnachweis

Am 20.09.2026 lief der aktive `change-accepted` → `code-review`-Ablauf tatsächlich an einem isolierten Python-Ticketexport. Der Abschlussagent erhielt Anforderungen und eine fehlerhafte Umsetzung; die Fehlerstelle wurde ihm nicht vorgegeben. Er führte Programme aus, reparierte Code und beauftragte drei getrennte Reviewer nacheinander.

| Zeit (UTC) | Tatsächlicher Ablauf | Nachweis |
| --- | --- | --- |
| 08:14:22 → 08:16:37 | Kritische Anforderungsprüfung entdeckt den Filterfehler in CSV und JSON. Regression zunächst rot, nach Reparatur grün; anschließend vollständige Anforderungsabdeckung. Noch kein Strukturreview. | [Fehler](fixture/evidence/02-normalized-filter-red.json), [Reparaturtest](fixture/evidence/03-normalized-filter-green.json), [Anforderungsabgleich](fixture/evidence/requirements-pre-review.md) |
| 08:17:10 → 08:21:49 | DRY-Rezensent findet doppelte Datenaufbereitung. Abschlussagent extrahiert gemeinsame Verarbeitung, führt Tests aus; derselbe Reviewer bestätigt gezielt die Reparatur. | [Befund](fixture/evidence/dry-initial-receipt.md), [echter Diff](fixture/evidence/dry-repair.delta.diff), [Nachprüfung](fixture/evidence/dry-delta-receipt.md) |
| 08:22:20 → 08:25:04 | Erst nach geschlossener DRY-Nachprüfung startet ein anderer SOLID-Rezensent. Keine offenen Befunde. | [SOLID-Ergebnis](fixture/evidence/solid-receipt.md) |
| 08:25:43 → 08:28:05 | Erst danach startet ein dritter KISS-Rezensent. Keine offenen Befunde. | [KISS-Ergebnis](fixture/evidence/kiss-receipt.md) |
| 08:29:08 | Abschluss dokumentiert: Anforderungsnachweise und alle drei Reviews gelten für denselben finalen Quellstand. | [Abschlussbeleg](fixture/evidence/completion.md) |
| 08:29:23 | Übergeordneter Agent spielt unabhängig alle sechs CLI-Tests erneut ab: **6/6 grün**, Quellen unverändert. Auch der rote Zwischenstand wurde unabhängig nachgespielt. | [Grüner Replay](parent-final-replay.json), [roter Replay](parent-red-replay.json) |
| 08:30:49 → 08:32:44 | Zweiter echter Auftrag „Change accepted“: Quellen, Anforderungen, Regeln und Nachweise werden geprüft und wiederverwendet. **0 neue Reviewer, 0 neue Strukturreviewrunden, 0 neue CLI-Testläufe.** | [Wiederholungsaufruf](fixture/evidence/repeat-request.md) |

Konkretes Verhalten: Ein Ticket mit Status `" DONE "` verschwand beim Filter `--status done` zunächst aus der Ausgabe (`[]`). Nach der Reparatur erscheint es korrekt mit Status `"done"`. Beide Ausgaben stammen aus [ausgeführten CLI-Aufrufen](parent-behavior-replay.json).

Die tatsächlichen Reviewer waren `/root/live_completion/dry_reviewer`, `/root/live_completion/solid_reviewer` und `/root/live_completion/kiss_reviewer`. Ihre laufenden Zustände wurden auch vom übergeordneten Agenten beobachtet. [Ereignisfolge mit Aufrufen und Zeitstempeln](fixture/evidence/events.jsonl); [unabhängiger Abgleich von Reihenfolge, Dateihashes und Wiederholung](parent-process-audit.json).

## Selbst nachspielen

Aus diesem Verzeichnis, mit Python 3 und ohne zusätzliche Pakete:

```bash
# Erwartet: fehlgeschlagener Test mit zwei Subcase-Fehlern, Exit 1.
(cd fixture/evidence/snapshots/red && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_ticket_export.ExportTests.test_filter_matches_normalized_status_in_both_formats)

# Erwartet: sechs erfolgreiche CLI-Tests, Exit 0.
(cd fixture/evidence/snapshots/final && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v)
```

Die ausführbaren Zwischenstände und Rohprotokolle wurden unverändert aus dem lokalen Testrepository übernommen; dessen `.git` und Python-Caches sind ausgenommen. Historische Rohprotokolle behalten ihre ursprünglichen temporären Pfade. Die damaligen Git-Integritätsprüfungen benötigen dieses ursprüngliche Testrepository; die obigen Verhaltenstests laufen auch aus der erhaltenen Kopie.

## Aussagegrenze

Belegt sind die ausgeführte Reihenfolge, ein gefundener und reparierter Anforderungsfehler, ein echter DRY-Befund mit gezielter Nachprüfung sowie Wiederverwendung beim zweiten Abschlussaufruf. Das ist ein lokaler Beispielprozess; kein Produktionslauf und keine gemessene Tokenersparnis. Die technische Abnahme der gesamten Skill-/AGENTS-Migration erfolgte anschließend separat; siehe [Abschlussbeleg](../../completion.md). Die Protokolle sind aufgezeichnete Agentenbelege, keine signierten Runtime-Attestierungen.
