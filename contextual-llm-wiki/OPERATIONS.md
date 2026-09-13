# LLM-Wiki auf Daniels Mac betreiben

> Sollzustand nach Betriebsklärung am 13.09.2026: ein gemeinsames Wiki über alle ausgewählten Fachquellen, einschließlich `private` und `Projects/Private`; „privat“ ist ein Tätigkeitsbereich. [ADR 0010](../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md). Die folgenden Kommandos beschreiben bis zur ausstehenden Umstellung den bisherigen Live-Betrieb.

Die bestehende Codex-Automation `update-qmd-index-daily` übernimmt täglich um 07:00 Uhr (lokale Europe/Berlin-Zeit) die allgemeine Wiki-Pflege und anschließend QMD. Sie läuft lokal im gespeicherten Projekt `codex-global` mit den bisherigen Modell- und Zeitplaneinstellungen. Ein Merge löst keinen eigenen Lauf aus. Der Mac und die lokale Codex-Ausführung müssen verfügbar sein; der Termin garantiert keine Echtzeitaktualität.

## Implementierter gemeinsamer Helper (Ticket 03)

Der neue Helper wurde isoliert mit der gemeinsamen Wiki-CLI geprüft und ist noch nicht im Live-Job aktiviert. Er akzeptiert einen Teilfehler nur bei ausdrücklich bestätigter QMD-Eignung, vorhandenem übereinstimmendem Laufbericht und passenden Status-/Lint-Audits: Betroffene Seiten müssen zurückgezogen sein, verbleibende Änderungen müssen zum gemeldeten Fehlerzweig gehören. Danach darf QMD weiterlaufen; der Gesamt-Exit bleibt ungleich null. Fehlerhafte oder fehlende Verträge stoppen abhängige Schritte. [Abnahme und reproduzierbare Prüfungen](evidence/bounded-failures-03.md).

Die folgenden Abschnitte dokumentieren weiterhin den vor Ticket 04 aktivierten Live-Ablauf und seine bisherigen Konfigurationen.

## Ablauf und Zuständigkeit

`python3 scripts/maintain-index.py` führt aus:

1. Bestehende Quell-Collections über `sync-qmd-collections.py --apply` abgleichen.
2. Vorhandenen Wiki-Provider und gepinnte Runtime prüfen.
3. Für jede ausdrücklich übergebene Konfiguration `wiki maintain`, `wiki status` und `wiki lint` ausführen. Maintain aktualisiert Konzepte, gespeicherte Antworten und die eigene QMD-Collection.
4. Erst nach vollständigem Erfolg globales `qmd update`, `qmd embed` und `qmd status` aus `/` ausführen.

Der Helper prüft strukturierte Erfolgsmeldungen und offene Arbeit. Ein Fehler stoppt Folgeschritte. Die Betriebssystemsperre serialisiert den gesamten Lauf; zusätzlich schützt die bestehende Wiki-Sperre jeden Kontext. Ein unveränderter Wiki-Lauf benötigt keine neue Kompilierung, führt aber die globale Retrieval-Pflege aus.

## Konfiguration

Produktiv wird `.local/general.json` verwendet: der vollständige allgemeine Eingang einschließlich Meetings und Projects. `.local/acceptance-general.json` enthält nur den begrenzten Abnahmebestand und ist kein Ersatz dafür. Die private Konfiguration wird nicht automatisch ergänzt; private Pflege erfordert eine ausdrücklich gewählte zusätzliche `--config`-Option und getrennte Ausgabe/Collection.

Die Konfiguration lässt sich nach einem Umzug mit `wiki init-config` aus der [Einrichtungsanleitung](README.md) neu erzeugen. Bestehende Konfigurationen nicht überschreiben. Providerstandard ist `codex-agent`; optional wirken die vorhandenen `LLMWIKI_PROVIDER`-/`LLMWIKI_MODEL`-Variablen. Die Automation verwendet `LLMWIKI_PROVIDER=codex-agent` und die vorhandene Anmeldung. Ist `codex` nicht auf PATH, ergänzt sie das auf diesem Mac verifizierte gebündelte CLI-Verzeichnis `/Applications/ChatGPT.app/Contents/Resources`; sie installiert keinen neuen Provider. Provider- und Compilerinstallation gehören zur Einrichtung, nicht zu Reparaturaktionen des Tagesjobs.

## Manueller Lauf

Aus `contextual-llm-wiki/`, mit bereits eingerichtetem QMD auf PATH:

```bash
RUN_DIR="$PWD/.local/operations-runs/$(date '+%Y%m%dT%H%M%S')-$$"
python3 scripts/maintain-index.py \
  --config "$PWD/.local/general.json" \
  --artifacts "$RUN_DIR" \
  --lock-file "$PWD/.local/operations-runs/maintenance.lock" \
  --qmd "$(command -v qmd)" \
  --reconcile "$PWD/../../danielsvault-rag/scripts/sync-qmd-collections.py"
```

Für mehrere autorisierte Kontexte `--config` wiederholen; alle laufen seriell. Alle manuellen und automatischen Aufrufe verwenden dieselbe `--lock-file`. Der erste JSON-Datensatz nennt das neu angelegte Artefaktverzeichnis. Bei einem laufenden Tool-Prozess denselben Session-Handle pollen; nicht erneut starten. Pro Schritt werden `.stdout`, `.stderr` und `.exitcode` gespeichert, der Abschluss steht in `report.json`. Das Verzeichnis muss neu sein. Rohartefakte bleiben lokal/ignoriert und können Quelleninhalte enthalten.

Bei Fehlern `report.json` und die Dateien des dort genannten `failedStep` lesen. Nach Behebung einen neuen Lauf mit neuem Artefaktverzeichnis starten. Bei lebender Sperre den bestehenden Lauf abwarten; keine pauschalen Prozessabbrüche. Anmeldung, TCC- oder Collection-Konflikte werden als Blocker gemeldet. Fehlgeschlagene Wiki-Pflege blockiert auch die anschließende globale QMD-Pflege.

## Agenten und Aktualität

Für wiederverwendbare Synthesen die verwaltete Schnittstelle verwenden:

```bash
./wiki query --config .local/general.json --question 'Welche Rolle hat QMD im Wiki?'
```

Sie prüft Originalstände und verwendet bei Lücken aktuelle Quellen. Ohne `--save` entsteht keine dauerhafte Antwort. Direkte QMD-Treffer oder Obsidian-Seiten allein beweisen keine Aktualität. README, AGENTS, CONTEXT, OpenSpec und ADRs bleiben für ihre jeweiligen Regeln maßgeblich. Der [Einführungskatalog](../docs/rag/llm-wiki-context-adoption-catalog.md) benennt die vorgesehenen Verweise; er behauptet keine bereits erfolgte flächendeckende Einführung.

## Abnahme und Vollimport

[Abnahme dieser Betriebserweiterung](../openspec/changes/operate-contextual-llm-wiki/acceptance.md). Die Erstkompilierung des vollständigen allgemeinen Bestands ist vom begrenzten echten Abnahmelauf getrennt zu beurteilen. Maßgeblich sind produktives `wiki status` (`lastCompleted`, `pending`, `changes`, `review`) und der konkrete Laufbericht, nicht die Aktivierung des Zeitplans allein.
