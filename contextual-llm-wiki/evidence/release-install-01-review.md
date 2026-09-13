# Release-Ticket 01: Code-Review

Feste Basis: `dbb6df2030f26543099eb34d3bb6b7ff38963dbc`. Erster Implementierungscommit `a576a27`, Review-Korrektur `669eb7f`. Zwei unabhängige Subagenten prüften Standards und Spec gemäß dem `code-review`-Skill. Primärquelle ist `.scratch/update-llm-wiki-releases/issues/01-upstream-release-reproduzierbar-installieren-und-pruefen.md` mit Parent-Spec und aktivem OpenSpec-Change.

## Standards

Keine dokumentierten Verstöße und keine hinreichend begründeten Smells im ursprünglichen Diff. Der Nachreview des Fixes bestätigt: Der kleine Reporter hat eine begrenzte Verantwortung; unterschiedliche Vitest-/Node-Ergebnisformate rechtfertigen separate Auswertungen. Regressionstests beobachten weiterhin öffentliche Prozessaufrufe, Berichte und tatsächliche Testausgabe. Das Entfernen von `NODE_OPTIONS` betrifft nur die Integrationsprüfung und ist dokumentiert.

## Spec

Im Erstreview wurden zwei Varianten desselben unvollständigen Pflichtprüfungsnachweises identifiziert:

1. Eine vorhandene Upstream-Pflichtdatei konnte durch Vitest-Konfiguration ausgeschlossen werden; erfolgreiche Gesamtsummen reichten dem Installer trotzdem. Reproduktion: Freshness ausgeschlossen, verbleibende 44/44 Tests erfolgreich.
2. Node meldet testlose oder vollständig weggefilterte Dateien als erfolgreiche synthetische Dateitests; auch diese Summen erfüllten zuvor die Eignungsprüfung.

Die Korrektur verlangt Vitest-Ergebnisse samt erfolgreichen Assertions für jede Pflichtdatei. Ein Node-JSONL-Reporter unterscheidet echte Szenariotests von synthetischen Dateierfolgen. Geerbte `NODE_OPTIONS` können Pflichtszenarien nicht mehr ausfiltern. Drei öffentliche Installer-Regressionstests wurden zunächst fehlgeschlagen und anschließend erfolgreich ausgeführt: ausgeschlossene Freshness-Datei, leere Pflichtdatei und geerbter Filter vor einem absichtlich fehlschlagenden Szenario.

Der unabhängige Nachreview von `669eb7f` bestätigt die Behebung, einschließlich eigener Prüfung des Node-Reporters mit echter, testloser und weggefilterter Testdatei. Keine verbleibenden belastbaren Spec-Befunde; Aktivierung und Erkennung bleiben im vereinbarten Umfang der Folgetickets.

Standards: 0 offene Findings. Spec: 0 offene Findings nach Behebung beider Ausführungslücken. Den abschließenden Verhaltens-/Gesamttestnachweis enthält [die Abnahme](release-install-01.md).
