# 01: Gemeinsame Run-Ansicht mit verlässlichem Status

**What to build:** Ein Mensch öffnet seine gespeicherten Anforderungen und erkennt im gemeinsamen Kopf unmittelbar den tatsächlichen Analysezustand sowie das vorhandene Ergebnis oder den konkreten Fehler. Ergebnis, Verlauf, Dateien und Anforderungen bleiben als zusammengehörige Ansichten desselben Runs direkt erreichbar.

**Blocked by:** Operator-GUI-Ticket [03: Selbst gestarteten Run als Workflow und Sessionverlauf beobachten](../../agent-framework-operator-gui/issues/03-gestarteten-run-als-workflow-und-sessionverlauf-beobachten.md). Dessen geprüfter Stand muss in der gemeinsamen Implementierungsbasis verfügbar sein.

**Status:** ready-for-agent

**Kontext:** UX-01; [Spezifikation und Designreferenz](../spec.md).

- [ ] Das Öffnen eines gespeicherten Runs führt zur Ergebnisansicht mit Titel, Quelle und aktuellem Analysezustand am Einstieg. Vollständiger Anforderungstext und lange Erkenntnislisten stehen nicht mehr vor dem Zugang zu Status, Ergebnis und Verlauf. Die übrigen drei Ansichten sind direkt auswählbar und verwenden dieselbe Run-Zuordnung.
- [ ] Anforderungsliste und gemeinsamer Kopf verwenden die bestätigten öffentlichen Zustände: aufgenommen ohne Run, wartend, laufend, Ergebnisabgleich, Analyse abgeschlossen oder fehlgeschlagen. Ein unbekannter Zustand wird als unbekannt angezeigt. Eine vorhandene Run-ID allein begründet keine Anzeige „Läuft“ oder „Gestartet“; abgeschlossene Analyse behauptet weder Implementierung noch Review oder Gesamtabschluss.
- [ ] Statusänderungen werden während der Beobachtung und nach erneutem Öffnen konsistent sichtbar. Verbindungsverlust wird von Ausführungsfehler und Ergebnisabgleich unterschieden; ein zuletzt bekannter Stand wird nicht als aktuell bestätigt ausgegeben. Änderungen der ausgewählten Anforderung zeigen keine verspäteten Inhalte des vorherigen Runs.
- [ ] Vorhandene Aufnahme-/Startaktionen und sämtliche bereits zugänglichen History-, Session-, Artefakt- und Quelldaten bleiben über die gemeinsame Ansicht erreichbar. UX-02 bis UX-04 können deren Darstellung anschließend unabhängig verfeinern; dieses Ticket liefert bereits eine funktionierende Ansicht über die vorhandenen öffentlichen Schnittstellen.
- [ ] Navigation und Zustandswechsel sind per Tastatur bedienbar und verständlich beschriftet. Aktualisierungen verlieren weder die gewählte Ansicht noch ihren Bedienfokus. Bei 390 und 1024 Pixeln Breite sind Titel, Status und Navigation lesbar; das Seitenlayout benötigt keinen horizontalen Bildlauf.
- [ ] Ein reproduzierbarer Check belegt vor der Korrektur den widersprüchlichen Status beziehungsweise den langen Einstieg. Verhaltenstests vergleichen die neuen Anzeigen mit öffentlichen Antworten für die genannten Zustände. Browsernachweise zeigen Öffnen, Zustandsänderung und Wiederöffnen auf Desktop und Mobil mit tatsächlichen gespeicherten Daten; der simulierte Entwurf genügt nicht als Implementierungsnachweis.
