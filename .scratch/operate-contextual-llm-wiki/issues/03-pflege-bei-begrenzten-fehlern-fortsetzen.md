# 03: Pflege bei begrenzten Fehlern fortsetzen

**What to build:** Ein begrenzter Fehler verhindert nicht die Pflege unabhängiger Erkenntnisse im gemeinsamen Wiki. Daniel erhält einen verständlichen Teilfehlerbericht; abhängige oder ungeprüfte Aussagen werden nicht als aktuell ausgegeben. Nach Behebung lässt sich offene Arbeit abschließen.

**Blocked by:** 01 — Gemeinsames Wiki erzeugen und abfragen.

**Status:** resolved

## Grundlage und Ausgangslage

Maßgeblich sind der OpenSpec-Change [operate-contextual-llm-wiki](../../../openspec/changes/operate-contextual-llm-wiki/proposal.md), sein [Design](../../../openspec/changes/operate-contextual-llm-wiki/design.md) und die [Betriebs-Requirements](../../../openspec/changes/operate-contextual-llm-wiki/specs/contextual-wiki-operations/spec.md), insbesondere „Observable serialized maintenance with bounded failures“.

Der bestehende Wartungshelfer stoppt beim ersten Fehler den gesamten Lauf; auch die Kompilierung veröffentlicht bisher keine unabhängig abgeschlossenen Teilbereiche eines fehlgeschlagenen Gesamtlaufs. Daniel hat unabhängige Weiterverarbeitung ausdrücklich grundsätzlich bestätigt. Die fachliche Einheit der Fehlerisolation ist betroffene Evidenz mit ihren Abhängigkeiten, nicht eine allgemeine/private Wiki-Grenze.

## Abnahmekriterien

- [x] Ein reproduzierbarer begrenzter Quellen- oder Kompilierungsfehler verhindert nicht die Aktualisierung einer nachweislich unabhängigen Kontrollquelle samt ihrer abgeleiteten Erkenntnis.
- [x] Der Fehler wirkt auf direkt und transitiv abhängige Konzepte und gespeicherte Antworten. Betroffene Aussagen werden über die verwaltete Abfrage nicht als aktuelle Wiki-Evidenz geliefert.
- [x] Ein unvollständiger Scan oder Lesefehler wird nicht als bestätigte Entfernung der Quelle interpretiert. Es entsteht kein unbegründeter Massenentzug.
- [x] Fehlende oder unklare Abhängigkeiten werden nicht als Unabhängigkeit behandelt. Gemeinsame Runtime-/Indexfehler blockieren alle davon abhängigen Schritte sichtbar.
- [x] Sicher ausführbare QMD-Pflege läuft für gültige unabhängige Ergebnisse weiter. Ungeprüfte Inhalte werden dadurch nicht als geprüft veröffentlicht; der Erfolg von Indexierung oder Embeddings verdeckt keinen Wiki-Teilfehler.
- [x] Der Gesamtbericht unterscheidet abgeschlossene Arbeit, No-op, Fehler und verbleibende Arbeit. Ein Teilerfolg liefert insgesamt einen nicht erfolgreichen Exitstatus und nennt betroffene Arbeit sowie lokale Evidence.
- [x] Rohantworten, Fehlermeldungen und Exitcodes bleiben im eigenen Laufverzeichnis erhalten. Ungültiges JSON, fehlende erforderliche Ergebnisfelder und fehlende Laufberichte werden nicht als Erfolg interpretiert.
- [x] Nach Behebung des Fehlers wird die offene Arbeit erfolgreich abgeschlossen, ohne unabhängige gültige Inhalte unnötig neu zu kompilieren oder Seiten zu duplizieren. Die nächste unveränderte Wiederholung ist ein No-op.
- [x] Gleichzeitige Pflegeaufrufe bleiben serialisiert; die Teilfehlerfortsetzung umgeht keine bestehenden Schreibsperren.

## Umsetzung und Nachweis

Die öffentliche Pflege- und Abfrageschnittstelle mit einem betroffenen Abhängigkeitszweig und einem unabhängigen Kontrollzweig prüfen. Die Fehler müssen tatsächlich ausgelöst werden; reine Erfolgsmeldungen oder simulierte Gesamtberichte reichen nicht. Die Einheiten der internen Verarbeitung sind eine Umsetzungsentscheidung innerhalb dieses Vertrags.

Ticket 02 ist keine Voraussetzung. Vorhandene Migrationsbestände werden für diesen Nachweis nicht benötigt. Der Live-Job bleibt bis Ticket 04 unverändert.

## Comments

- 13.09.2026: Aufteilung und Abhängigkeiten von Daniel bestätigt. Sichere unabhängige Fortsetzung bedeutet keine Freigabe, fehlerhafte oder unbestimmbare Ergebnisse zu verwenden.

- 13.09.2026: Auf Daniels bestätigtem Zielbranch `codex/shared-wiki-03` auf Basis von Ticket 01 umgesetzt und isoliert verifiziert. [Abnahme mit beobachtetem Verhalten, Rohartefakten und Grenzen](../../../contextual-llm-wiki/evidence/bounded-failures-03.md). Keine Live-Umstellung; Ticket 02 wird nicht vorausgesetzt. Standards- und Spec-Review abgeschlossen; ein reproduzierbarer Wiederaufnahmefehler aus dem Review wurde testgeführt behoben und unabhängig erneut geprüft.
