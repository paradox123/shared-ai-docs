---
status: accepted
---

# Fachquellenindex unabhaengig von der Wiki-Aufbereitung pflegen

Daniel hat am 17.09.2026 entschieden, aktuelle Fachquellen bereits ueber WikiQuery auffindbar zu machen, auch wenn ihre Wiki-Aufbereitung noch aussteht oder fehlgeschlagen ist. Die Fachquellen-Indexpflege wird deshalb von der erfolgreichen Wiki-Kompilierung entkoppelt; neue und geaenderte Quellen haben bei der Wiki-Nachpflege Vorrang vor dem Erstimport-Rueckstand und sollen spaetestens am naechsten Tag verarbeitet sein, waehrend der Erstimport mehrere Tage dauern darf. Die bisherige starre Reihenfolge „gesamtes Wiki, danach QMD“ haelt bei mehrstuendigen oder abgebrochenen Erstimporten auch die Suche in aktuellen Originalen auf.

Dies ergaenzt [ADR 0010](0010-shared-wiki-across-personal-and-professional-domains.md): WikiQuery bleibt der gemeinsame Zugang, QMD die interne Suchmaschine. Der Rueckgriff auf gepruefte aktuelle Fachquellen bleibt als solcher erkennbar; veraltete oder ungepruefte Wiki-Aussagen werden nicht als aktuell ausgegeben. Ein erfolgreicher Indexlauf und der Abschluss laufender Aenderungen sind getrennt vom vollstaendigen Wiki-Erstimport auszuweisen. Ein gemeinsamer Speicher-, Scan- oder Indexfehler bleibt fuer die jeweils abhaengige Arbeit ein Blocker.

Die Entscheidung ersetzt die bisherige Reihenfolgevorgabe im [aktiven Betriebs-Change](../../openspec/changes/operate-contextual-llm-wiki/specs/contextual-wiki-operations/spec.md). Sie dokumentiert das Zielverhalten; Live-Automation und Implementierung sind damit noch nicht umgestellt.
