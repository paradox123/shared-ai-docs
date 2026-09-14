# 02: Analyseergebnis verständlich und vollständig lesen

**What to build:** Ein Mensch erfasst das gespeicherte Analyseergebnis in einer lesbaren Zusammenfassung, vertieft einzelne Erkenntnisse nach Bedarf und kann jede Aussage bis zu den verfügbaren Ergebnisartefakten und der aufgenommenen Anforderungsfassung nachvollziehen.

**Blocked by:** UX-[01: Gemeinsame Run-Ansicht mit verlässlichem Status](01-gemeinsame-run-ansicht-mit-verlaesslichem-status.md).

**Status:** ready-for-agent

**Kontext:** UX-02; [Spezifikation und Designreferenz](../spec.md).

- [ ] Die Ergebnisansicht zeigt die gespeicherte Zusammenfassung als lesbaren Inhalt. Lange Erkenntnisse und ergänzende Abgrenzungen lassen sich gezielt aufklappen, ohne Aussagen zu verändern, abzuschneiden oder den Zugang zu anderen Ansichten nach unten zu verdrängen.
- [ ] Gruppierungen, etwa offene Produktentscheidungen oder Abhängigkeiten, werden nur verwendet, wenn die gespeicherten Daten die Zuordnung eindeutig tragen. Unklassifizierte Erkenntnisse bleiben vollständig zugänglich. Die Anzeige setzt weder die Beispielzahlen noch feste Textpositionen oder Formulierungen aus dem Entwurf voraus und trifft keine Produktentscheidung aus einer bloßen Darstellung heraus.
- [ ] „Dateien“ zeigt die tatsächlich vorhandenen Artefakte des ausgewählten Runs. Bekannte Inhalte öffnen lesbar; die gespeicherte redigierte Originalfassung bleibt gezielt erreichbar. Fehlende, nicht verfügbare oder nicht lesbar interpretierbare Inhalte werden korrekt bezeichnet und nicht durch erfundene Zusammenfassungen ersetzt.
- [ ] „Anforderungen“ zeigt die unveränderte aufgenommene Fassung mit Titel, Inhalt, Herkunft und Quellrevision. Die Ansicht lädt nicht stillschweigend den inzwischen geänderten GitHub-Text als Arbeitsmandat nach. Quell- und Artefaktinhalte werden weiterhin als nicht vertrauenswürdige Inhalte sicher dargestellt; vorhandene Redaktion bleibt wirksam.
- [ ] Leere Ergebnisse, fehlende Artefakte und Ergebnisse mit vielen oder unbekannten Erkenntnissen sind unterscheidbar. Alle zugänglichen Inhalte bleiben auch beim Ansichtswechsel dem richtigen Run zugeordnet.
- [ ] Aufklappbereiche und Dateiauswahl sind per Tastatur bedienbar; Beschriftungen und Inhalte bleiben bei 390 und 1024 Pixeln lesbar. Verhaltenstests prüfen unterschiedliche Ergebnisformen und fehlende Inhalte. Ein Browsernachweis vergleicht Zusammenfassung, sämtliche Erkenntnisse, Artefakte und Anforderungsfassung mit den öffentlichen Antworten eines gespeicherten Runs.
