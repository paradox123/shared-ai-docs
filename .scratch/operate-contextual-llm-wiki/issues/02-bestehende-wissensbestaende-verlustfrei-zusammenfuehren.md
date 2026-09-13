# 02: Bestehende Wissensbestände verlustfrei zusammenführen

**What to build:** Daniel kann vorhandene Wiki-Seiten und gespeicherte Gesprächssynthesen in den gemeinsamen Wissensbestand übernehmen, ohne einzigartige Antworten, Quellenherkunft oder ihre Nachpflegefähigkeit still zu verlieren. Ungültige Altinhalte bleiben überprüfbar erhalten, werden aber nicht als aktuelle Erkenntnisse veröffentlicht.

**Blocked by:** 01 — Gemeinsames Wiki erzeugen und abfragen.

**Status:** ready-for-agent

## Grundlage und Ausgangslage

Maßgeblich sind der OpenSpec-Change [operate-contextual-llm-wiki](../../../openspec/changes/operate-contextual-llm-wiki/proposal.md), sein [Migrationsdesign](../../../openspec/changes/operate-contextual-llm-wiki/design.md), die [kanonischen Wiki-Requirements](../../../openspec/specs/contextual-llm-wiki/spec.md) zu Provenienz, Antwortabhängigkeiten und Wiederherstellung sowie [ADR 0010](../../../docs/adr/0010-shared-wiki-across-personal-and-professional-domains.md).

Vorhanden sind getrennte Konfigurationen und echte Abnahmebestände mit gespeicherten Synthesen. Konfigurierte Produktionsausgaben sind nicht automatisch bereits befüllt. Die tatsächlichen Bestände müssen deshalb inventarisiert werden. Eine reine Neukompilierung kann einzigartige Gesprächsformulierungen nicht zuverlässig rekonstruieren.

## Abnahmekriterien

- [ ] Vor der Übernahme liegt eine Inventur der tatsächlich vorhandenen Bestände, Seiten, gespeicherten Antworten und ihrer Abhängigkeiten vor. Leere Produktionsausgaben und befüllte Abnahmebestände werden unterschieden.
- [ ] Eine überprüfbare Sicherung erhält die bisherigen Texte, Provenienz und erforderlichen Zustände vor jeder Ablösung. Die Quelle dieser Sicherung bleibt bis zum erfolgreichen Übernahmenachweis verfügbar.
- [ ] Gültige gespeicherte Antworten sind nach der Übernahme im gemeinsamen Wiki über die verwaltete Abfrage auffindbar und auf ihre Originalquellen zurückführbar. Sie werden nicht still durch neue Modellformulierungen ersetzt.
- [ ] Abhängigkeiten von Antworten auf Konzeptseiten und weitere gespeicherte Antworten bleiben erhalten beziehungsweise werden überprüfbar auf gültige gemeinsame Seitenstände überführt.
- [ ] Gleichnamige Seiten mit unterschiedlichen Aussagen oder Quellen werden nicht still überschrieben. Der Übernahmebericht erklärt, welche Inhalte zusammengeführt, getrennt erhalten oder zur Prüfung zurückgestellt wurden.
- [ ] Seiten mit veralteter, entfallener oder unvollständig belegter Evidenz erscheinen nicht als aktuelles Wissen. Ihre bisherige Fassung bleibt in der Sicherung überprüfbar; Zurückstellungen und deren Gründe sind sichtbar.
- [ ] Eine Quelländerung nach der Migration erreicht eine davon abhängige gespeicherte Antwort über die gemeinsame Pflege. Eine unabhängige Antwort bleibt nutzbar und wird nicht unnötig verändert.
- [ ] Eine unterbrochene oder fehlgeschlagene Übernahme kann wiederholt oder auf den gesicherten Stand zurückgeführt werden. Wiederholung erzeugt keine doppelten aktiven Antworten und verliert keine bereits gesicherten Inhalte.
- [ ] QMD liefert den übernommenen gültigen Bestand ohne aus dem Tätigkeitsbereich abgeleitete Ausschlüsse. Die Migration repointet oder entfernt keine fremden Collections.

## Umsetzung und Nachweis

Die vollständige Kette sichern → übernehmen → abfragen → Quelle ändern → Antwort nachpflegen über öffentliche Schnittstellen prüfen. Unterschiedliche gleichnamige Seiten, eine abhängige Antwortkette und einen ungültigen Altbeleg als Verhaltenstests verwenden. Für reale Bestände Erwartung, beobachtetes Resultat und Evidence je Übernahmekriterium dokumentieren.

Die gemeinsame Wiki-Funktion aus Ticket 01 ist Voraussetzung. Ticket 03 ist keine Voraussetzung: Migrationsfehler und Wiederholbarkeit gehören zur eigenen Übernahmefunktion. Die abschließende produktive Aktivierung und Ablösung des bisherigen Betriebs erfolgen erst in Ticket 04.

## Comments

- 13.09.2026: Aufteilung und Abhängigkeiten von Daniel bestätigt. Der vollständige Erstimport ersetzt nicht die verifizierte Übernahme gespeicherter Gesprächssynthesen.
