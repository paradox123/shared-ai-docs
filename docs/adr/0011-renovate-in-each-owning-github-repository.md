---
status: accepted
date: 2026-09-13
---

# Renovate läuft im jeweils zuständigen GitHub-Repository

Daniel hat Renovate in GitHub Actions als Standard für die Abhängigkeitspflege zukünftiger Repositories bestätigt. Jeder Wartungsjob wird im Repository der zu pflegenden Anwendung eingerichtet; Konfiguration, Rechte, Tests, Update-PRs und Merge gehören damit zur gleichen Repository-Verantwortung. Die [gemeinsame Betriebsdokumentation](../renovate-repository-standard.md) hält das wiederverwendbare Muster fest.

Ein zentraler Runner im privaten Obsidian-Repository wurde ausdrücklich ausgeschlossen: **`paradox123/obsidian-private-notes` übernimmt keine Renovate-Jobs für andere Repositories.** Die dortige Einrichtung ist für das Nebenkostenabrechnungstool zuständig, dessen Code dort liegt. Andere Projekte erhalten ihren Job am eigenen Git-Root; auch in Monorepos entscheidet das besitzende Repository, nicht der Speicherort dieser gemeinsamen Dokumentation.

Abhängigkeitsupdates dürfen nach vollständig erfolgreichen Pflichtprüfungen automatisch gemergt werden, einschließlich Major-Paketupdates. Bei nicht erfolgreichen Prüfungen bleibt der PR offen und wird dem Verantwortlichen mit persönlicher GitHub-Erwähnung sowie PR- und Prüflauf-Link vorgelegt. Diese vorab erteilte Merge-Freigabe gilt für Abhängigkeitspflege und erweitert nicht die Freigaben allgemeiner agentischer Implementierung.

## Konsequenzen

- Rechte und Fehlermeldungen bleiben auf das jeweilige Repository begrenzt. Ein zentrales Repository benötigt keine repoübergreifenden Schreibrechte zur Paketpflege.
- Jedes Repository benötigt eine eigene Einrichtung und Betriebsprüfung. Gemeinsame Dokumentation reduziert wiederholte Entscheidungen; Änderungen am Muster ändern bestehende Workflows nicht automatisch.
- Paketmanager, Testumfang, Schutzmechanismen, Empfänger und Laufzeitgrenzen werden passend zum Zielprojekt gewählt. Der Grundsatz bleibt: nur den erfolgreich geprüften Stand übernehmen, Fehler sichtbar vorlegen.
