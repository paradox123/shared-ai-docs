## Context

Akzeptierter Installations-/Prüfanteil von Release-Ticket 01. Dieser Abschluss übernimmt die bereits implementierten und verifizierten Entscheidungen aus dem aktiven Betriebs-Change.

## Goals / Non-Goals

Ein exaktes veröffentlichtes Release mit unveränderten Abhängigkeitseingängen separat installieren und seine tatsächliche Wiki-Kompatibilität nachweisen. Aktivierung, Rollback, Release-Scheduler und Wissenspflege gehören zu den offenen Folgetickets.

## Decisions

Owning Git root: `_shared/shared-ai-docs`, Ausgang `main` bei `dbb6df2030f26543099eb34d3bb6b7ff38963dbc`; Ziel `codex/update-llm-wiki-releases` im separaten Worktree `../shared-ai-docs-update-llm-wiki-releases`. Derselbe Ausgangscommit ist die Review-Basis. Fremde Änderungen im ursprünglichen Checkout werden nicht übernommen. Die Implementierung erfolgte im bestehenden Abschnitt 5. Der akzeptierte Anteil wird zum Abschluss separat archiviert.

`scripts/install-release.py --release TAG` erzeugt einen neuen Kandidaten unter `.runtime/candidates/` oder einem ausdrücklich angegebenen neuen Ziel. GitHub Release-Metadaten über `gh api --hostname github.com` belegen die Veröffentlichung; ein frischer Git-Fetch des Release-Tags liefert den exakten Commit. Ein isolierter Wrapper-Snapshot erhält eine eigene Release-Definition und einen eigenen Compiler, sodass die bestehenden statischen SDK-Imports tatsächlich den Kandidaten prüfen. Der vorhandene Node wird nur lesend verwendet, bei fehlender oder inkompatibler Runtime scheitert der Kandidat. Manifest/Lock bleiben bytegleich; `npm ci` installiert die festgelegten Versionen einschließlich Build-Abhängigkeiten. Bestehende Integrationspatches werden in Dateireihenfolge angewandt.

Die stabile Testgrenze ist der öffentliche Installationsprozess samt JSON-Bericht und Exitcode. GitHub-/Git-Transport werden für Fehlerfälle an der externen Prozessgrenze kontrolliert; der echte Release-Nachweis verwendet GitHub, Git, npm, Compiler und QMD. Nur der Modellprovider bleibt in den begrenzten Integrationstests deterministisch. Jeder erforderliche Schritt beginnt mit einem dauerhaft gespeicherten nicht erfolgreichen Status. Aktivierung, Rollback und periodische Erkennung bleiben Tickets 02/03.

Der Review ergänzte einen Ausführungsnachweis je Pflichtdatei: Vitest-JSON muss jede kanonische Datei mit erfolgreichen Assertions enthalten; ein Node-JSONL-Reporter unterscheidet tatsächliche Tests von synthetischen Erfolgen leerer Dateien. Die Summenprüfung bleibt zusätzlich bestehen. Der Node-Integrationslauf entfernt geerbte `NODE_OPTIONS`, damit ein äußerer Testfilter keine Pflichtszenarien auslassen kann.

## Risks / Trade-offs

Release-Tags können upstream verändert werden; jeder Kandidat dokumentiert den beim Aufruf aufgelösten exakten Commit. Die Eignung beschreibt die geprüften Bytes zum Prüfzeitpunkt. Ein späterer Aktivierer muss deren Identität erneut prüfen. Die lokale Node-/QMD-Runtime muss verfügbar und kompatibel sein. Die Modellgrenze ist in den begrenzten Tests deterministisch, Compiler und QMD sind echt.

## Migration Plan

Keine Produktmigration in diesem Abschluss. Das akzeptierte Requirement wird durch `openspec archive` kanonisch übernommen; das verbleibende Betriebs-Delta referenziert diesen Vertrag. [Verhaltensnachweis und Grenzen](../../../../contextual-llm-wiki/evidence/release-install-01.md).
