# Upstream-Stand von LLM Wiki auf dem Mac aktuell halten

Stand: 13.09.2026. Korrigierter Auftrag nach Nutzerklärung. Es wurden keine Bot-Konfiguration, Installation oder Versionsänderung vorgenommen.

## Bestätigter Umfang

Der Mac soll den aktuellen übernommenen Stand des Upstream-Repositories `atomicstrata/llm-wiki-compiler` erhalten. Aktualisierungseinheit ist LLM Wiki als Ganzes, einschließlich der von diesem Stand festgelegten Abhängigkeiten. Dessen Manifest und Lockdatei bestimmen die Installation. Wenn Library X eine neue Version veröffentlicht, entsteht daraus kein lokaler Updateauftrag. Erst wenn LLM Wiki diese Version upstream übernimmt, kommt sie mit dem entsprechenden Wiki-Stand auf den Mac.

Eigenständige Renovate-Updates von Compiler-Bibliotheken, Lockfile-Neuauflösungen sowie unabhängig veranlasste Node-, QMD- oder Wrapper-Updates gehören nicht zu diesem Auftrag. Eine vom neuen Upstream-Stand benötigte Laufzeitanpassung ist Teil seiner Kompatibilitätsprüfung. Ein gegebenenfalls erforderlicher lokaler Build reproduziert den übernommenen Stand; er entwickelt dessen Abhängigkeiten nicht vorweg.

Erfolgreicher Build und alle erforderlichen Tests erlauben die automatische Übernahme ohne erneute menschliche Review-/Merge-Freigabe. Fehlende, ausstehende oder fehlgeschlagene Pflichtprüfungen blockieren die Übernahme. Ein gegebenenfalls verwendeter PR betrifft ausschließlich unsere Referenz auf den Upstream-Stand und wird nach erfolgreichen Prüfungen automatisch gemergt. Es werden keine Änderungen oder PRs im Upstream-Repository vorgenommen.

## Verifizierter Ausgangspunkt

Der Compiler-Commit ist in Bootstrap und Runtime-Prüfung doppelt hinterlegt. Bootstrap richtet einen fehlenden Clone ein, aktualisiert einen bestehenden älteren Clone aber nicht. Der ignorierte Runtime-Clone enthält einen lokalen Integrationspatch. Deshalb muss ein Update auch die bestehende Integration prüfen und darf nicht bloß den Commit austauschen. Lokale Referenzen: [Bootstrap](../../contextual-llm-wiki/scripts/bootstrap.sh), [Runtime-Prüfung](../../contextual-llm-wiki/src/runtime.ts), [Betriebsanleitung](../../contextual-llm-wiki/OPERATIONS.md).

Beim read-only-Abgleich am 13.09.2026 entsprach der Pin `34ca1df97b3e60a6700048c48c7cf70c92a9bfdb` dem Release v1.3.0 und dem damaligen `main`-Stand. [Offizielles Release v1.3.0](https://github.com/atomicstrata/llm-wiki-compiler/releases/tag/v1.3.0)

## Technischer Umsetzungsvorschlag

1. Bestätigter Kanal sind veröffentlichte Releases. Reguläre Releases werden auf einen exakten Commit aufgelöst; Hauptbranch-Commits, bloße Tags und Entwürfe lösen kein Update aus. Vorabversionen werden standardmäßig nicht verfolgt.
2. Änderungen dieses Upstream-Stands erkennen. Falls Renovate verwendet wird, verfolgt es ausschließlich diese Integration als Abhängigkeit. Es verwaltet nicht die Bibliotheken innerhalb des Compilers. Renovate kann Tags oder Git-Refs verfolgen und Referenz-Updates automatisch mergen. [Custom Manager](https://docs.renovatebot.com/modules/manager/regex/), [Git-Refs](https://docs.renovatebot.com/modules/datasource/git-refs/), [Automerge](https://docs.renovatebot.com/key-concepts/automerge/)
3. Einen Kandidaten aus genau diesem Commit mit den dort festgelegten Abhängigkeiten installieren, den bestehenden Integrationspatch prüfen und gegebenenfalls bauen. Build und Integrationstests müssen erfolgreich sein.
4. Den geprüften Stand automatisch lokal aktivieren, die Aktivierung verifizieren und bei Fehlern den bisherigen funktionsfähigen Stand beibehalten beziehungsweise wiederherstellen. Ein Repository-Merge allein beweist keine lokale Aktualisierung.

Die zuvor vorgeschlagene breite Dependency-Pflege ist durch diese Eingrenzung ersetzt. Renovate ist ein möglicher Baustein für die Upstream-Referenz, kein eigenständiges Deployment-Werkzeug. Der Updateablauf ist noch nicht implementiert.

## Aus dieser Session ausgeklammert

Daniel bearbeitet Wissenspflege und deren möglichen Wechsel von Codex zu einem direkten lokalen Scheduler in einer anderen Session. Die bestehende Pflegeautomation wird hier weder geändert noch deaktiviert. Frühere Wissenspflege-Anforderungen bleiben als Bestand dokumentiert; ihre weitere Umsetzung wird in dieser Session nicht fortgesetzt.

## Freigegebene Umsetzungstickets

Die drei Tickets sind freigegeben und separat von der Wissenspflege unter [LLM-Wiki-Release-Updates](../../.scratch/update-llm-wiki-releases/spec.md) veröffentlicht. Reihenfolge: Kandidat installieren und prüfen → lokal aktivieren → Releases automatisch erkennen und übernehmen.
