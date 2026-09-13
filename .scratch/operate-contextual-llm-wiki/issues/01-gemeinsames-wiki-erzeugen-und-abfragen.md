# 01: Gemeinsames Wiki erzeugen und abfragen

**What to build:** Daniel kann Fachquellen aus allen ausgewählten Tätigkeitsbereichen in einem gemeinsamen Wiki pflegen und daraus passende repoübergreifende Synthesen abrufen. `private` bezeichnet persönliche Themen wie Vermietung oder Portfoliopflege und begründet weder einen separaten Wissensbestand noch eine besondere Abfragefreigabe. Die fachliche Relevanz und ausdrücklich gesetzte Aufgabengrenzen bestimmen die verwendete Evidenz.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

## Grundlage und Ausgangslage

Maßgeblich sind der OpenSpec-Change [operate-contextual-llm-wiki](../../../openspec/changes/operate-contextual-llm-wiki/proposal.md), sein [Design](../../../openspec/changes/operate-contextual-llm-wiki/design.md), die [geänderten Wiki-Requirements](../../../openspec/changes/operate-contextual-llm-wiki/specs/contextual-llm-wiki/spec.md) und [ADR 0010](../../../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md). Bei der Umsetzung zusätzlich die unveränderten kanonischen Wiki-Requirements beachten.

Der vorhandene Scanner partitioniert Quellen nach allgemeinem beziehungsweise privatem Scope. Auch die private Produktionskonfiguration umfasst dadurch nicht alle Quellen gemeinsam. Die bisherige getrennte Abnahme ist kein Nachweis für das gewünschte gemeinsame Wiki. Compiler-Pin, QMD als einzige Retrieval-Engine und Quellen-/Antwortabhängigkeiten sind bereits implementiert und bleiben erhalten.

## Abnahmekriterien

- [ ] Die gemeinsame Inventur registriert die acht vereinbarten Repo-Identitäten `vault-root`, `meeting-assistant`, `shared-ai-docs`, `ki-fuer-kmu`, `ncg-docs`, `private`, `probare-crm` und `sparkle`. Meetings und Projects einschließlich Projects/Private sind rekursiv enthalten.
- [ ] Persönliche und berufliche Fachquellen werden in derselben Wissensschicht verarbeitet. Zusätzliche Worktrees, unselektierte Repos, technische Laufzeitdaten und generierte Ausgaben werden weiterhin ausgeschlossen; Originalquellen bleiben unverändert.
- [ ] Eine öffentlich ausführbare Pflege verarbeitet eine persönliche und eine andere ausgewählte Fachquelle mit einem tatsächlich relevanten Zusammenhang zu einer belegten Synthese. Der Nachweis verwendet den echten gepinnten Compiler und QMD; deterministische Substitution ist auf die Providergrenze begrenzt.
- [ ] Eine passende verwaltete Abfrage verwendet diese Synthese ohne privaten Sondermodus. Ein irrelevanter Kontrollbeleg wird nicht allein wegen gleicher Begriffe oder gleicher Tätigkeitszuordnung als Evidenz einbezogen.
- [ ] Eine ausdrücklich auf bestimmte Repos oder Quellen begrenzte Aufgabe verwendet ausschließlich zulässige Evidenz. Die Beschränkung gilt auch für transitive Quellenabhängigkeiten einer Synthese und für Quellen-Fallbacks; eine bloße Anweisung im Fragetext ersetzt keine Überprüfung.
- [ ] Eine nach der Pflege geänderte Originalquelle führt dazu, dass die abhängige Wiki-Seite nicht ungeprüft als aktuell verwendet wird. Die Abfrage meldet offenen Pflegebedarf oder verwendet passende aktuelle Quellen.
- [ ] Wiederholte Abfragen verwenden gültiges gespeichertes Wissen ohne erneute Kompilierung; ohne Speicherauftrag entstehen keine dauerhaften Antwortseiten. Ein unveränderter Pflegelauf ist ein No-op.
- [ ] QMD bleibt die einzige persistierte Retrieval-Engine. Der Tätigkeitsbereich `private` erzeugt keine ausgeblendete Wiki-Collection; fremde Collections werden nicht verändert.

## Umsetzung und Nachweis

In kleinen Rot→Grün-Schritten über die öffentliche Wiki-Schnittstelle arbeiten. Die Relevanzprüfung muss eine unterstützte Beziehung und einen irrelevanten Kontrollbeleg unterscheiden; bloße Treffer- oder Seitenanzahlen genügen nicht. Den beobachteten Inhalt, seine Originalbelege und die Aktualitätsprüfung verständlich dokumentieren.

Die gemeinsame Ausgabe zunächst isoliert verifizieren. Die Übernahme bestehender Bestände gehört zu Ticket 02, Teilfehlerfortsetzung zu Ticket 03 und die produktive Aktivierung samt vollständigem Erstimport zu Ticket 04. Keine alten Bestände vorzeitig löschen oder den Live-Job umstellen.

## Comments

- 13.09.2026: Aufteilung und Abhängigkeiten von Daniel bestätigt. Dieses Ticket deckt die gemeinsame Quellen-/Abfragefunktion und deren QMD-Anbindung ab.
