# Gemeinsamer technischer Abschluss — Design und Begriffsklärung

Stand: 2026-09-20. Anwendungsbereich, Abnahmeauslöser, Reihenfolge und zentrale Zuständigkeit von code-review sind entschieden; die Vereinheitlichung ist lokal implementiert und initial geprüft. Die vollständige technische Abschlussprüfung dieser Änderung wartet auf Daniels kontextbezogene Abnahme. Die Erweiterung gehört zum laufenden Change, weil sie die Orchestrator-spezifische Review-Ausnahme der ersten Tokenoptimierung durch einen gemeinsamen Abschluss ersetzen soll. Die frühere Implementierung und ihre Nachweise bleiben als Ausgangsstand erhalten.

## Bestätigte Entscheidung

Für NCG-Backend, ki-fuer-kmu und probare-crm gelten beim gemeinsamen Abschluss drei getrennte Prüfungen in der Reihenfolge **DRY → SOLID → KISS**, jeweils mit eigenem Prüfagenten. Sie beginnen erst nach kritischer Verifikation der Anforderungsumsetzung und der Behebung dort gefundener Lücken. Befunde werden vor dem nächsten Durchlauf bearbeitet; Verhalten bleibt erhalten und betroffene Tests werden erneut ausgeführt. Daniel hat die drei getrennten Prüfungen ausdrücklich gewählt, einschließlich der Erweiterung gegenüber der bisherigen probare-crm-Vorgabe. Ihre frühere Platzierung vor der kritischen Verifikation war ein Fehler bei der Zusammenführung der Abläufe. Siehe [ADR 0017](../../../docs/adr/0017-three-sequential-refactoring-checks.md).

Das Ziel aus dem vorherigen Auftrag bleibt: widerspruchsarme Anweisungen und weniger wiederholte Arbeit, auch wenn eine Änderung ohne Orchestrator umgesetzt wird.

## Zentrale Zuständigkeit von code-review

Daniel hat vorgeschlagen, DRY, SOLID und KISS ausdrücklich in code-review aufzunehmen und alle Aufrufer auf diesen Skill verweisen zu lassen. Dieser Vorschlag ersetzt die vorherige Aufteilung, bei der ein neuer Abschluss-Skill die Reviewmethodik besessen hätte.

- **code-review besitzt die Reviewmethodik:** drei getrennte Prüfagenten in der Reihenfolge DRY → SOLID → KISS, zugeordnete Repository-Standards, Bearbeitung der Befunde, gezielte Nachprüfung und Nachweis für den geprüften Stand. Reihenfolge und Kriterien stehen ausschließlich dort und in seinen eigenen Referenzen.
- **Der Accepted-/Abschluss-Einstieg besitzt den Ablauf:** kontextbezogene Abnahme erkennen, kritische Anforderungsverifikation einschließlich Spec-Abgleich abschließen, code-review aufrufen, danach den autorisierten Abschluss fortsetzen. Er kopiert keine Reviewkriterien und startet keine weitere allgemeine Standards-/Spec-Runde.
- **AGENTS.md verankert die Pflicht:** Vor technischem Abschluss muss ein gültiger Nachweis des code-review-Skills vorliegen. Repository-spezifische Standards und Prüfkommandos bleiben lokal; die allgemeine DRY-/SOLID-/KISS-Anleitung wird durch den Verweis ersetzt.
- **Implementierung und Orchestrator verwenden diese Einstiege:** Der Orchestrator koordiniert Arbeit, erteilt im delegierten Auftrag den Abschlussauftrag, beurteilt Nachweise und integriert. Er besitzt keine zweite Reviewmethodik.
- **Archivierung prüft den vorhandenen Abschlussnachweis:** Ein unveränderter bereits geprüfter Stand löst keine erneute Refactoring-Runde aus; Änderungen öffnen betroffene Prüfungen über code-review wieder.
- **write-agents-md erzeugt den Verweis:** Die Vorlage enthält die Abschlussverpflichtung und lokale Ergänzungen, keine Kopie der Reviewmethode.

code-review verlangt als Eingang einen festen Änderungsumfang und aktuelle Anforderungsnachweise. Fehlen diese oder gelten sie nicht für den aktuellen Stand, muss die kritische Verifikation vor dem ersten Strukturreview vervollständigt werden. Ein ausdrücklicher eigenständiger code-review-Auftrag benötigt keinen Accepted-Trigger und erteilt keine Lieferfreigabe. Dadurch bleibt der Skill auch für die Prüfung eines Branches oder PRs verwendbar.

Der Abschluss-Skill bleibt ein schlanker Aufrufer. Nachweisdateiname und mechanische Migration sind Implementierungsdetails. Keine neue Glossardefinition ist erforderlich: DRY, SOLID, KISS und Refactoring sind allgemeine Engineering-Begriffe.

## Begriffsklärung und Überschneidungen

| Begriff | Prüffrage und Ergebnis |
| --- | --- |
| Kritische Anforderungsverifikation | Sind alle vereinbarten Anforderungen tatsächlich und korrekt umgesetzt? Akzeptanzkriterien werden mit beobachtetem Verhalten, relevanten Gegenbeispielen und Grenzen abgeglichen. Fehlende oder falsche Umsetzung und unzureichende Nachweise werden vor den Strukturprüfungen behoben. |
| Strukturprüfung DRY → SOLID → KISS | Ist die bereits funktional verifizierte Umsetzung ohne unnötige Dopplung, mit klaren Verantwortlichkeiten und angemessen einfach aufgebaut? Die drei Agenten prüfen jeweils eine Perspektive; Refactoring ist die anschließende Bearbeitung ihrer Befunde. |
| Unabhängige Prüfung | Beschreibt die Trennung vom Implementierungsagenten und einen eigenen Prüfauftrag. Es ist keine zusätzliche inhaltliche Prüfkategorie. Auch die drei Strukturprüfungen sind unabhängige Reviews. Ein unabhängiger Agent kann ebenfalls die Anforderungsverifikation übernehmen. |
| Standards-/Spec-Review im vorhandenen code-review-Skill | Ein konkretes Paket aus zwei Prüfaufträgen: Standards prüft dokumentierte Repository-Regeln und Code Smells; Spec gleicht den Diff mit den Anforderungen ab, einschließlich fehlender, falscher oder nicht beauftragter Umsetzung. |

Der Spec-Auftrag stellt dieselbe fachliche Grundfrage wie die kritische Anforderungsverifikation, verwendet aber primär eine unabhängige Diff-Inspektion. Die bisherige kritische Verifikation wird gesondert beim Implementierungsagenten angefordert und verlangt Verhaltensnachweise. Das ist eine Überschneidung mit unterschiedlicher Methode und Perspektive; ein zusätzlicher Spec-Agent wäre eine bewusste zweite Anforderungsprüfung, keine neue Qualitätsdimension.

Standards überschneidet sich bei Duplikaten, Verantwortlichkeiten und unnötiger Komplexität mit DRY/SOLID/KISS. Er enthält zusätzlich verbindliche Repository-Regeln, die nicht automatisch durch diese drei Prinzipien abgedeckt sind. Solche Regeln dürfen bei einer Zusammenlegung nicht verloren gehen.

Die zentrale Zuständigkeit löst diese Überschneidung so auf: Anforderungsabdeckung einschließlich Spec-Abgleich gehört in die kritische Verifikation; Strukturqualität und Repository-Standards gehören in code-review. Dessen drei getrennte Reviews ersetzen den bisherigen allgemeinen Standards-Auftrag. Verbleibende Repository-Regeln werden ausdrücklich einer passenden Prüfung oder vorhandenen automatischen Checks zugeordnet. Eine weitere pauschale Spec-Runde nach bereits abgeschlossener Anforderungsverifikation entfällt. Der aktive Skill und die Delta-Spezifikation setzen diese Zuständigkeit um; die unveränderten Vendor-Fassungen bleiben als Herkunftsnachweis erhalten.

## Bestätigter Anwendungsbereich

Daniel hat Option 1 gewählt: Der vollständige Abschluss gilt für inhaltliche Änderungen an Code, Anforderungen, wirksamer Konfiguration oder verbindlichen Arbeitsregeln; damit gehören auch verhaltensändernde Skill-/AGENTS-Anpassungen dazu. Reine Rechtschreib-, Formatierungs- oder redaktionelle Linkkorrekturen erhalten passende Dokumentprüfungen. Maßgeblich ist die Wirkung der Änderung, nicht die Dateiendung.

Die Anwendungsgrenze wird zentral gepflegt; einzelne Skills erhalten keine eigenen Ausnahmelisten.

## Bestehende Abnahme-Einstiege

Daniel verwendet häufig „Change accepted“ oder „akzeptiert“ und schlägt diese Formulierungen als Trigger für den Abschluss vor.

Die lokale Bestandsprüfung zeigt zwei unterschiedliche Bedeutungen:

- `ki-fuer-kmu/.codex/skills/change-accepted-closeout/SKILL.md` beschreibt „change accepted“ als Einstieg in Archivierung, Commit, standardmäßige Integration nach main, Push und Issue-Abschluss. Fehlende Verifikation muss zuvor erledigt werden.
- Die aktuelle Orchestrator-Vorlage `references/messages.md` verwendet „Akzeptiert für [ticket]“ erst nach technischer Verifikation und Review als Vorbereitung der Integration; eine konkrete Merge-Freigabe folgt später.

Zusammenführung: Ein auf einen konkreten Implementierungsstand bezogener Abschlussauftrag ruft den gemeinsamen Abschluss auf. Der Ablauf übernimmt passende aktuelle Nachweise und führt fehlende oder durch Änderungen betroffene Prüfungen aus. Ein wiederholtes „akzeptiert“ erzeugt keine neue vollständige Prüfrunde für denselben Stand. Die Formulierung bei einer Designentscheidung oder in zitiertem Text ist kein Abschlussauftrag für eine Implementierung. Vorhandene Lieferautorisierung und Zielvorgaben werden aus dem tatsächlichen Auftrag übernommen, nicht aus einem globalen Schlüsselwort mit main als Standard abgeleitet.

## Bestätigter Auslöser und Ablauf

Daniel hat am 2026-09-20 Option 2 gewählt: Bei direkter Implementierungsarbeit beginnt der vollständige technische Abschluss erst nach fachlicher Abnahme durch „akzeptiert“, „Change accepted“ oder einen gleichwertigen, auf die konkrete Umsetzung bezogenen Abschlussauftrag. Ein gewöhnlicher Implementierungsauftrag löst die vollständige Abschlussrunde noch nicht aus.

Bei vollständig delegierten Aufträgen übernimmt der autorisierte Koordinator diese Abnahme und erteilt denselben Abschlussauftrag. Dadurch entsteht keine zusätzliche menschliche Freigabeschleife. Der gemeinsame Ablauf hat einen Auslöser; wer ihn erteilen darf, ergibt sich aus der bestehenden Delegation.

1. Umsetzung und erforderliche erste Verhaltensnachweise durchführen. Laufende Tests und Refactoring im Entwicklungszyklus bleiben Teil der Implementierung.
2. Bei direkter Arbeit die Umsetzung als bereit zur fachlichen Abnahme melden und den technischen Abschluss ausdrücklich als offen kennzeichnen. Bei delegierter Arbeit beurteilt der autorisierte Koordinator die Bereitschaft.
3. Nach dem Abschlussauftrag zuerst kritisch verifizieren, ob die Anforderungen tatsächlich umgesetzt sind. Lücken beheben und betroffene Verhaltensnachweise erneuern, bevor die Strukturreviews beginnen.
4. code-review für den festen Änderungsumfang und mit den aktuellen Anforderungsnachweisen aufrufen. Seine Methodik ist dort zentral definiert.
5. Nach den letzten Reparaturen die abschließenden relevanten Tests ausführen und den Reviewnachweis aus code-review übernehmen. Änderungen durch Refactoring können Anforderungsnachweise entwerten; dann die betroffenen Anforderungen erneut verifizieren. Unveränderte gültige Prüfabdeckung bleibt erhalten.
6. Den technischen Abschluss mit Nachweisen für den geprüften Stand dokumentieren. Integration, Push, Archivierung und Issue-Abschluss folgen der bereits erteilten Lieferautorisierung und den Zielvorgaben.

Fachliche Abnahme startet die technische Abschlussprüfung; sie bescheinigt deren Ergebnis nicht vorab. Die jetzige Auswahl des Ablaufmodells ist eine Designentscheidung und kein Abschlussauftrag für die bisherige Implementierung.

## Übergabe an die Umsetzung

Die zentrale Zuständigkeit von code-review klärt die verbliebene Aufteilung. Ablage und Format des Abschlussnachweises sowie die konkreten Verweise bleiben Implementierungsentscheidungen. Der Nachweis muss den geprüften Inhalt und die abgedeckten Anforderungen erkennen lassen; bloße Dateigleichheit ersetzt keine fehlende Prüfabdeckung.

Die Umsetzung erweitert die Spezifikation im bestehenden Change, passt code-review als zentrale Reviewdefinition an, führt den schlanken Abschluss-Einstieg ein und ersetzt widersprechende Ablauftexte an ihren bisherigen Stellen: NCG-Backend einschließlich übergeordneter Anleitung, ki-fuer-kmu, probare-crm, implement, orchestrate-ticket-batch, change-accepted-closeout, betroffene Archivierungs-Einstiege und die Vorlage in write-agents-md. Beschreibungen des alten Zwei-Achsen-Ablaufs, etwa in ask-matt, müssen ebenfalls dem neuen Vertrag entsprechen. Repository-spezifische Prüfkommandos bleiben lokal. Die gepflegte Anpassung des Vendor-Skills muss den bestehenden Skill-Sync-Vertrag beachten und den kanonischen Einstieg code-review erhalten.

Die aktiven Aufrufer und die vereinbarten Repository-Anleitungen wurden auf den gemeinsamen Vertrag umgestellt; Details und Grenzen stehen in [completion-implementation.md](completion-implementation.md). Die zusätzlichen drei Prüfungen erhöhen bei probare-crm den Aufwand pro vollständigem Abschluss; die erwartete Tokenersparnis stammt aus vermiedenen Wiederholungen und kompakterer Koordination und ist noch nicht an einem neuen Live-Lauf gemessen.

Die Abnahme der Umsetzung muss mindestens zeigen: direkte Umsetzung wartet nach ersten Tests; eine kontextbezogene Abnahme startet den Abschluss; autorisierte Delegation benötigt keine weitere Benutzerfreigabe; kritische Anforderungsverifikation und erforderliche Reparaturen liegen vor allen drei getrennten Strukturprüfungen DRY → SOLID → KISS; Anforderungs- und Repository-Regelabdeckung sind ausdrücklich zugeordnet; wiederholte Abnahme und Archivierung nutzen gültige Nachweise; spätere Änderungen öffnen betroffene Prüfungen wieder; Designzustimmung und zitierte Trigger lösen keinen Abschluss aus; reine redaktionelle Korrekturen erhalten passende Dokumentprüfungen.
