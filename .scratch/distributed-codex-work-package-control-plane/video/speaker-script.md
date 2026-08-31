# Sprechertext: Wie ein Ticket den Entwicklungsprozess durchläuft

Status: fachlich freigegebener Entwurf

## 1. Ein Ticket beginnt seine Reise

Ein Softwareticket durchläuft mehr als nur eine Implementierung. Anforderungen müssen geprüft, Änderungen umgesetzt, Nachweise erbracht, Reviews durchgeführt und Fehler sicher behandelt werden. Die Work Package Control Plane führt das Ticket kontrolliert durch diesen gesamten Entwicklungsprozess.

## 2. Drei Akteure mit klaren Verantwortlichkeiten

Dabei arbeiten drei Akteure zusammen. Der Mensch formuliert Anforderungen, erteilt Freigaben und trifft Entscheidungen. Agenten übernehmen klar begrenzte Entwicklungs- und Reviewaufgaben. Die zentrale Steuerungsebene koordiniert den Ablauf, verwaltet Zustände und führt deterministische Prüfungen aus.

Der Mensch bleibt dabei jederzeit Teil des Prozesses. Die menschliche Einbindung ist kein Ausnahmefall, sondern ein durchgängiges Governance-Prinzip.

## 3. Erstes menschliches Gate: Anforderungen freigeben

Am Anfang beschreibt der Mensch das gewünschte Ergebnis und die Akzeptanzkriterien. Bevor eine Umsetzung beginnen darf, prüft und bestätigt er diese Anforderungen.

Die Steuerungsebene kontrolliert anschließend, ob das Ticket eindeutig, vollständig und tatsächlich zur Bearbeitung freigegeben ist. Unklare, widersprüchliche oder unvollständige Anforderungen gehen zurück an den Menschen. Es wird noch kein Agent gestartet und kein Arbeitsbereich angelegt.

## 4. Zweites menschliches Gate: Implementierung freigeben

Auf Basis der bestätigten Anforderungen entsteht ein begrenzter Arbeitsauftrag mit Umsetzungsscope, Akzeptanzkriterien und geplantem Verhaltensnachweis.

Der Mensch gibt nun ausdrücklich die agentische Implementierung dieses Auftrags frei. Erst danach reserviert die Steuerungsebene das Repository, erzeugt einen isolierten Arbeitsbereich und startet den Implementierungsagenten.

## 5. Der Agent implementiert – das System kontrolliert

Der Implementierungsagent arbeitet testgetrieben und nur innerhalb seines freigegebenen Auftrags. Er verändert den Code und liefert für jedes Akzeptanzkriterium einen überprüfbaren Nachweis.

Tests, Sicherheitsprüfungen, Git-Operationen und Statusübergänge werden nicht dem Sprachmodell überlassen. Diese Aufgaben führt die Steuerungsebene deterministisch aus. Nur ein eindeutig identifizierter Commit-Stand darf als Pull Request veröffentlicht werden.

## 6. Unabhängige Prüfung und Repair-Runden

Danach prüfen drei voneinander unabhängige Agenten denselben Commit-Stand: eine Anforderungsprüfung, eine Codeprüfung und eine Architekturprüfung.

Erkannte Probleme werden gebündelt an den Implementierungsagenten zurückgegeben. Nach jeder Korrektur entsteht ein neuer Commit-Stand. Frühere Prüfergebnisse verlieren ihre Gültigkeit, und Nachweise, Sicherheitsprüfungen und Reviews werden vollständig wiederholt.

## 7. Fehler werden nach ihrer Ursache behandelt

Nicht jeder Fehler bedeutet dasselbe. Unklare Anforderungen gehen zurück an den Menschen. Eine fachliche Rückfrage erzeugt eine sichtbare Intervention. Prüfbefunde führen in eine begrenzte Reparaturrunde.

Bei einem Werkzeug- oder Infrastrukturfehler gleicht die Steuerungsebene zuerst ab, welche Wirkungen bereits eingetreten sind. Danach wird nur der fehlende Schritt wiederholt.

Steckt eine Agentensitzung fest, kann der Mensch sie gezielt fortsetzen, einen neuen Lösungszweig beginnen oder einen frischen Versuch ab einem stabilen Kontrollpunkt starten.

Sind die erlaubten Reparaturrunden ausgeschöpft, entscheidet ebenfalls der Mensch: Auftrag eingrenzen, manuell übernehmen, erneut freigeben oder kontrolliert abbrechen.

## 8. Drittes menschliches Gate: Artefakt freigeben

Erst wenn der aktuelle Commit-Stand alle Nachweise, Sicherheitsprüfungen und unabhängigen Reviews bestanden hat, wird das resultierende Artefakt dem Menschen zur Freigabe vorgelegt.

Der Mensch prüft exakt diesen verifizierten Stand. Er kann Änderungen verlangen oder ihn freigeben und zusammenführen. Ein später veränderter Stand müsste erneut vollständig verifiziert werden.

## 9. Abschluss

So bleibt der Mensch an den entscheidenden Stellen verantwortlich: für die Anforderungen, für das Mandat zur Implementierung und für das finale Artefakt.

Agenten bearbeiten die Entwicklungsaufgaben. Die Control Plane sorgt für einen nachvollziehbaren, wiederholbaren und fehlertoleranten Prozess.

## Sprachregeln für die Produktion

- „Human in the Loop“ wird im Bild gezeigt, aber als „menschliche Einbindung“ oder „menschliche Freigabe“ gesprochen.
- „Head“ wird als „Commit-Stand“ gesprochen.
- „Fresh Retry“ wird als „frischer Versuch ab einem stabilen Kontrollpunkt“ gesprochen.
- „Requirements Review“ und „Architecture Review“ werden als „Anforderungsprüfung“ und „Architekturprüfung“ gesprochen.
- „Work Package Control Plane“ wird nur in Einleitung und Schluss genannt.
- Der finale Sprechertext wird als eine zusammenhängende Aufnahme produziert; Szenenpausen werden in derselben Tonspur angelegt.
