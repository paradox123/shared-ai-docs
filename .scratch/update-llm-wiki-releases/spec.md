# Veröffentlichte LLM-Wiki-Releases auf dem Mac übernehmen

## Arbeitsmandat

Daniel hat die drei Umsetzungstickets und den Kanal „veröffentlichte Releases“ ausdrücklich bestätigt. Aktualisierungseinheit ist das Upstream-Projekt `atomicstrata/llm-wiki-compiler` als Ganzes mit seinen festgelegten Abhängigkeiten. Einzelne Bibliotheken werden nicht unabhängig aktualisiert. Erfolgreicher Build und alle erforderlichen Integrationstests erlauben die automatische Übernahme ohne erneute Review-, Merge- oder Deployment-Freigabe.

Reguläre veröffentlichte Releases werden auf einen exakten Commit aufgelöst. Hauptbranch-Commits, bloße Tags ohne veröffentlichtes Release und Entwürfe lösen keine Übernahme aus. Vorabversionen werden standardmäßig nicht verfolgt. Ein notwendiger Build reproduziert den Release-Stand mit seiner Lockdatei und dem vorhandenen Integrationspatch. Falls Renovate eingesetzt wird, verwaltet es ausschließlich unsere Upstream-Referenz; ein Integrations-PR wird nach erfolgreichen Pflichtprüfungen automatisch gemergt. Das Upstream-Repository wird nicht verändert.

## Abgrenzung

Wissenspflege, deren Schedulerwechsel, die gemeinsame Wiki-Migration sowie unabhängige Node-, QMD- oder Wrapper-Updates gehören nicht zu diesen Tickets. Die bestehende Pflegeautomation bleibt unverändert. Die Tests prüfen die vorhandene Wiki-Integration mit begrenzten Testbeständen und setzen die noch offenen Wissenspflege-Tickets nicht voraus. Eine vom Release tatsächlich benötigte Laufzeitanpassung gehört zur Prüfung seiner Installierbarkeit.

## Umsetzung und Verhaltensnachweis

1. Einen Release-Kandidaten reproduzierbar installieren und prüfen.
2. Einen erfolgreichen Kandidaten lokal aktivieren und bei Fehlern den bisherigen funktionsfähigen Stand erhalten.
3. Neue Releases regelmäßig erkennen und die gesamte Übernahme automatisch ausführen.

Jedes Ticket wird über die direkteste öffentliche Schnittstelle nachgewiesen. Ticket 01 ist auf `codex/update-llm-wiki-releases` umgesetzt und geprüft; [Abnahme](../../contextual-llm-wiki/evidence/release-install-01.md). Aktivierung und regelmäßige Erkennung aus Tickets 02/03 sind noch nicht umgesetzt.

## Quellen

- [Aktiver OpenSpec-Change](../../openspec/changes/operate-contextual-llm-wiki/design.md)
- [Anforderung zur Upstream-Übernahme](../../openspec/changes/operate-contextual-llm-wiki/specs/contextual-wiki-operations/spec.md)
- [Korrigierte Betriebsnotiz](../../docs/rag/2026-09-13-llm-wiki-dependency-updates.md)
