# Wiederaufnehmbare Wiki-Pflege: Umsetzungstickets

Die Aufteilung in sechs Tickets wurde von Daniel am 17.09.2026 bestaetigt: „das passt, lets go“. Alle Tickets sind im lokalen Markdown-Tracker als `ready-for-agent` veroeffentlicht. Das bedeutet Implementierungsbereitschaft, nicht erledigte Arbeit. Die [Parent-Spec](spec.md) bleibt unveraendert; keine Implementierung oder Live-Umstellung wurde mit dieser Veroeffentlichung ausgefuehrt.

| Ticket | Liefert | Blockiert durch |
| --- | --- | --- |
| [01: Fachquellen unabhaengig indexieren](issues/01-fachquellen-unabhaengig-indexieren.md) | Aktuelle Originalquellen ueber WikiQuery trotz fehlgeschlagener Wiki-Aufbereitung | Keine |
| [02: Extraktionen wiederaufnehmen](issues/02-extraktionen-wiederaufnehmen.md) | Erfolgreiche kompatible Modellarbeit ueberlebt einen Prozessneustart | Keine |
| [03: Pflegelaeufe begrenzen](issues/03-pflegelaeufe-begrenzen.md) | Endliches Laufende, dauerhafter Fortschritt und Stopp bei gemeinsamem Providerfehler | 02 |
| [04: Tagesaenderungen priorisieren](issues/04-tagesaenderungen-priorisieren.md) | Gepruefte Tagespakete vor dem Erstimport, sichtbare Fristverletzungen | 03 |
| [05: Quellenänderungen isolieren](issues/05-quellenaenderungen-isolieren.md) | Abhaengige Aussagen sperren und unabhaengige Arbeit erhalten | 04 |
| [06: Pflegeautomation aktivieren](issues/06-pflegeautomation-aktivieren.md) | Integrierter Ablauf im bestehenden Job samt getrennter Produktivabnahme | 01, 05 |

Die Startfront besteht aus 01 und 02. Danach gilt 02 → 03 → 04 → 05; 06 verbindet diese Kette mit 01. Die Kanten sind fachliche Voraussetzungen. Moegliche Ueberschneidungen im Wartungshelper oder Berichtscode erfordern bei paralleler Umsetzung Koordination, erzeugen aber keine zusaetzlichen fachlichen Blockaden. Kleine notwendige vorbereitende Refactorings gehoeren an den Anfang des jeweiligen Tickets.

## Abdeckung der Parent-Spec

| User Stories | Primaerer Nachweis |
| --- | --- |
| 1–6 | 01 |
| 7–11 | 04 |
| 12–13 | 02, erneute Pruefung in 05 |
| 14 | 05 |
| 15 | 04 und 05 |
| 16 | 01, 04 und 05 |
| 17–19 | 03 und 06 |
| 20 | 05 |
| 21–22 | 01, 03 und integrierte Abnahme 06 |
| 23 | 04 |
| 24 | 02, 04 und 05 |
| 25 | 02, 05 und 06 |
| 26–27 | 06 |

Jedes Ticket prueft seinen kompletten Pfad ueber oeffentliche Pflege-/Query-Schnittstellen mit isolierten Daten und kontrollierten externen Providerantworten. Die Core-Verarbeitung und der behauptete Suchnachweis werden nicht durch Attrappen ersetzt. Der echte Schedulerlauf und der mehrtaegige Erstimport-Abschluss aus 06 duerfen als zeitlich spaetere Abnahmepunkte offen bleiben, werden aber niemals aus einem manuellen Lauf oder einer Definition abgeleitet. Keine unbegrenzten Warteaufrufe fuer ihre Beobachtung.
