# UX/UI-Skills: Bewertung vom 14.09.2026

## Ergebnis und Umfang

`plugin87/ux-ui-agent-skills` passt als gezielt integrierte Ergänzung. Für Daniels
Anwendungsoberflächen empfehlen sich vor allem UX Writing und Design Review,
ergänzt durch Vercels Web Interface Guidelines. Eine vollständige globale
Aktivierung der 19 Plugin87-Skills ist nicht die Empfehlung.

Dies ist eine Eignungsbewertung, keine Produktanforderung und kein bereits
implementierter Skill-Import. Es wurden keine bestehenden Skills geändert oder
neue Skills aktiviert. Der bestehende GUI-Change bleibt für Produktänderungen
zuständig; für dieses Dokument ist kein neuer OpenSpec-Change erforderlich.

## Evidenz aus heutigen Aufgaben

Gezielt ausgewertet wurden die folgenden Aufgaben und ihre relevanten
Nutzer-/Ergebnisnachrichten, nicht sämtliche heutigen Sessions:

| Aufgabe | Beobachtung | Folgerung |
| --- | --- | --- |
| Issue 1: Implementiere Issue-Eingabe | Daniel ließ „Einreichung“ durch „Anforderungen“ ersetzen. | Fachliche UI-Begriffe müssen am Nutzerwortschatz ausgerichtet sein. |
| Issue 2: Issue als Hintergrundtask starten | Der gespeicherte Desktop-Screenshot zeigt ein lesbares, aber langes Analyseergebnis mit wenig Gliederung. | Ergebnis, Einschränkungen und weitere Schritte brauchen eine schnell erfassbare Hierarchie. |
| Issue 3: Implementiere Run-Verlauf | Der beanstandete Screenshot zeigt UUIDs, Protokollereignisse und große JSON-Blöcke im Vordergrund. Daniel erklärte diese Darstellung ausdrücklich für unverständlich. | Ein technisch vollständiger Verlauf ist noch keine verständliche Arbeitsansicht. |
| GitHub-Tickets als Prototyp prüfen | Daniel bewertete die Darstellung grundsätzlich positiv, nahm Texte und Farben aus und untersagte neue Anforderungen durch den Prototyp. Variante A wurde zusätzlich im Browser angesehen. | Visuelle Referenzen helfen, benötigen aber verständliche Texte und eine zum Arbeitskontext passende Gestaltung. |

Die drei Operator-Aufgaben sind `01a09f10-371c-7733-bf8f-9a8e5bf6087a`,
`01a09f6f-a9aa-7340-8174-4496be780ddc` und
`01a09fe5-d91a-7643-ac88-a483b8257c95`; die Probare-Aufgabe ist
`01a09f11-4fea-7133-aedb-d95b9fd1989f`.

Die Run-Verlauf-Aufgabe war bei der Sichtung aktiv und bearbeitete die
Rohdatenkritik bereits. Die Diagnose bezieht sich auf den beanstandeten
Zwischenstand, nicht auf eine abschließende Bewertung dieser laufenden Korrektur.

Visuell betrachtet: der Ticket-02-Erfolgsscreenshot, der beanstandete
Ticket-03-Desktop-Screenshot und Probare-Variante A. Letztere nutzt große
Serifenschriften, Grün-/Beigetöne und vergleichsweise kleine Hilfs-/Statustexte.
Varianten B/C wurden in dieser Bewertung nicht visuell geprüft.

Die [Probare-Projektreferenz](https://github.com/paradox123/probare-crm/blob/main/docs/prototypes/decision-workflow-reference.md)
hält die Grenze zwischen Inspiration und Anforderungen fest.

## Bestehende Skills und die eigentliche Lücke

`frontend-design` und `webapp-testing` sind bereits aktiv. In der Probare-Session
wurden beide ausdrücklich gelesen. Der aktuelle
[Frontend-Skill](../../skills-repo/skills/frontend-design/SKILL.md) betont markante
Ästhetik, ungewöhnliche Typografie und überraschende Gestaltung. Das kann
visuelle Eigenständigkeit unterstützen, sichert aber allein keine effiziente
Arbeitsoberfläche.

Meine Schlussfolgerung: Es fehlt vor allem eine konsequente Verbindung von
Nutzeraufgabe, Informationshierarchie, verständlichen Texten und visueller
Abnahme. Für den Run-Verlauf wäre die konkrete Prüffrage: Erkennt Daniel schnell,
was geschehen ist, was dabei herauskam und ob er handeln muss? Originaldaten
bleiben erreichbar, dominieren aber nicht die erste Ansicht. Das ist ein
Bewertungsvorschlag; dieses Dokument ergänzt keine fachlichen Freigaben,
Pflichtschritte oder Zustandsregeln.

## Quellenbewertung

Plugin87 wurde als temporärer Checkout bei Commit
`f9478157db18a7ac0d88fcd61d43f1650ab25f31` geprüft; `package.json` nennt Version
2.9.0 und MIT. Geprüft wurden insbesondere Skill-Einstiege, referenzierte
Review-Inhalte, Pluginmanifest und der zentrale Prüfbericht.

| Baustein | Empfehlung | Nutzen und Grenze |
| --- | --- | --- |
| Plugin87 `ux-writing` | Gezielt übernehmen | Handlungsbezogene Beschriftungen, verständliche Fehler und Leerzustände; deutsche Fachsprache bleibt projektspezifisch. |
| Plugin87 `design-review` | Gezielt übernehmen | Bewertet Hierarchie und Bedienbarkeit; Bewertungen sind Urteil, kein objektiver Beweis durch eine Punktzahl. |
| Plugin87 `redesign` | Optional bei einer konkreten Überarbeitung | Hilft bei systematischer Bestandsaufnahme; bestehendes Verhalten und Anforderungen bleiben maßgeblich. |
| Vercel `web-design-guidelines` | Als technische UI-Prüfung ergänzen | Prüft unter anderem Semantik, Fokus, Formulare und Bedienung; ersetzt keine visuelle Abnahme. |
| Vercel React-/Composition-Skills | Bei passendem React-Projekt ergänzen | Unterstützen technische Qualität und Komponentenstruktur; beheben keine unverständliche Informationsdarstellung von selbst. |

Quellen: [UX Writing](https://github.com/plugin87/ux-ui-agent-skills/blob/f9478157db18a7ac0d88fcd61d43f1650ab25f31/.claude/skills/ux-writing/SKILL.md),
[Design Review](https://github.com/plugin87/ux-ui-agent-skills/blob/f9478157db18a7ac0d88fcd61d43f1650ab25f31/.claude/skills/design-review/SKILL.md),
[Redesign](https://github.com/plugin87/ux-ui-agent-skills/blob/f9478157db18a7ac0d88fcd61d43f1650ab25f31/.claude/skills/redesign/SKILL.md),
[Vercel Skill-Katalog](https://github.com/vercel-labs/agent-skills),
[Vercel Web Design Guidelines](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md).

## Grenzen einer Installation über Vercels Skills-CLI

Vercels `skills`-CLI und Vercels eigene Skill-Sammlung sind getrennte Projekte.
Der CLI-Installer unterstützt Codex, macht fremde Inhalte aber nicht automatisch
zu einer vollständigen Codex-Integration. [CLI-Dokumentation](https://github.com/vercel-labs/skills)

1. **Externe Referenzen:** `ux-writing/SKILL.md` benötigt beispielsweise
   `content/voice-tone.md` außerhalb seines Skill-Ordners. Der geprüfte
   [CLI-Installer](https://github.com/vercel-labs/skills/blob/d667282815248da03a08a18272b5d2eef9caf77c/src/installer.ts#L365)
   kopiert den jeweiligen Skill-Ordner. Aus dem Quellcodevergleich folgt:
   Ein gewöhnlicher Einzel-Skill-Import nimmt diese Repository-Abhängigkeiten
   nicht mit. Das ist eine statische Prüfung, kein ausgeführter Installationstest.
2. **Claude-spezifische Bestandteile:** Die Integration verwendet zusätzlich
   `.claude/rules`, Commands und einen Design-Critic-Agenten. Deren Funktionsweise
   ist durch das Kopieren der SKILL-Dateien nicht hergestellt.
3. **Falsches Prüfziel vermeiden:**
   [accuracy_report.mjs](https://github.com/plugin87/ux-ui-agent-skills/blob/f9478157db18a7ac0d88fcd61d43f1650ab25f31/scripts/accuracy_report.mjs)
   enthält feste Prüfziele unter `examples/` sowie kit-eigene Token-/Spec-Prüfungen.
   Ein erfolgreicher Lauf belegt deshalb keine Qualität der Operator-Anwendung.
4. **Pauschale Stilregeln:**
   [design-doctrine](https://github.com/plugin87/ux-ui-agent-skills/blob/f9478157db18a7ac0d88fcd61d43f1650ab25f31/.claude/skills/design-doctrine/SKILL.md)
   setzt unter anderem feste Größenverhältnisse für Überschriften voraus.
   Solche Vorgaben sind keine universelle UX-Regel für dichte Arbeitsoberflächen.
5. **Namenskollision:** Plugin87 enthält `prototype`; die aktive gemeinsame Liste
   verwendet bereits Matt Pococks Skill dieses Namens.
6. **Tatsächlich geprüfte CLI-Erkennung:** `skills@1.5.26 add <checkout> --list`
   erkannte 18 Skills. `data-dashboard` wurde mit einem YAML-Parsefehler in der
   unquotierten Beschreibung übersprungen. Der Aufruf installierte keine Skills.
   Laufzeitgrenze: Node 22.12.0 liegt unter der vom CLI-Paket deklarierten
   Mindestversion 22.20.0; npm meldete dazu eine Engine-Warnung.
   Ein zweiter Parseversuch mit Python/PyYAML bestätigte unabhängig den Fehler
   am Doppelpunkt nach `tokens` in dieser Beschreibung.

## Empfohlener Integrationsweg

Für die gewünschte projektübergreifende Verbesserung passt das bestehende
[Hybrid-Sync-Modell](hybrid-skill-sync.md): versionierte Quellen unter
`skills-repo/vendor/plugin87/` und `skills-repo/vendor/vercel/`, gezielte aktive
Einträge unter `skills-repo/skills`, anschließend der vorhandene Codex-Link-Sync.
Plugin87 braucht einen klaren Codex-Einstieg mit auflösbaren Referenzen zum
vollständigen Vendor-Baum; lokale Anpassungen werden getrennt von Upstream
gepflegt. Keine pauschale globale CLI-Installation in die Runtime-Verzeichnisse.

Eine spätere Integration sollte sich an einem realen Bildschirm beweisen:
Nutzeraufgabe und vorhandene Anforderungen erfassen, konkrete Gestaltung
anwenden, gerenderte Desktop-/Mobilansicht prüfen, Hauptaufgabe und relevante
Zustände durchspielen, größere UX-Mängel korrigieren. Alle Prüfungen müssen auf
die echte Anwendung zeigen. Eine Verbesserung durch die neuen Skills ist bislang
nicht experimentell nachgewiesen.

## Review-Status

- Klassifikation: `project-scoped-playbook` für Operator-Terminologie und
  Informationsaufbereitung; gezielte Vendor-Integration als Empfehlung für
  wiederverwendbare Review-/Textkompetenz.
- Bestehende Skills: keine Änderung; keine Ausweitung ihres Scopes.
- Bestehende unversionierte Arbeiten in `docs/research/` und
  `openspec/changes/prove-three-identity-coexistence/` wurden erhalten.
- Kein Session-Cursor und kein Automationsspeicher wurden fortgeschrieben.
- Keine vollständige Accessibility-, Funktions- oder Gate-Abnahme durchgeführt.
