# 04: Anforderungen aufnehmen und direkt zur Analyse gelangen

**What to build:** Ein Mensch öffnet über „Neu“ eine kompakte Aufnahme, gibt eine GitHub-Issue-URL ein und entscheidet zwischen „Nur aufnehmen“ und „Aufnehmen und analysieren“. Die bestätigte Aufnahme beziehungsweise der zugehörige Run erscheint unmittelbar in der gemeinsamen Ansicht und bleibt später unter derselben Identität wieder auffindbar.

**Blocked by:** UX-[01: Gemeinsame Run-Ansicht mit verlässlichem Status](01-gemeinsame-run-ansicht-mit-verlaesslichem-status.md).

**Status:** ready-for-agent

**Kontext:** UX-04; [Spezifikation und Designreferenz](../spec.md). UX-02 und UX-03 sind keine Blocker.

- [ ] „Neu“ öffnet die kompakte Aufnahme innerhalb des Operator Clients. Die Oberfläche verwendet konsistent „Anforderungen“. Beide Aufnahmeaktionen sind mit einer eingegebenen GitHub-Issue-URL über die bestehenden öffentlichen Schnittstellen nutzbar; es gibt keine Beschränkung auf die Beispieldaten des Entwurfs.
- [ ] „Nur aufnehmen“ zeigt nach bestätigter Speicherung „Aufgenommen“ ohne Run und bietet den bestehenden expliziten Start an. „Aufnehmen und analysieren“ sowie der Start gespeicherter Anforderungen führen zu dem vom Server bestätigten Run und seinem tatsächlichen Analysezustand. Die Oberfläche meldet keinen erfolgreichen Start allein aufgrund eines Klicks oder einer noch ausstehenden Antwort.
- [ ] Ungültige Quelle, fehlende Berechtigung und nicht verfügbare Startvoraussetzungen erscheinen mit konkreter verständlicher Meldung im Zusammenhang mit der betroffenen Aktion. Während einer Anfrage ist deren laufender Zustand erkennbar. Wenn Aufnahme gelingt und Start scheitert, bleiben die gespeicherten Anforderungen zugänglich und werden korrekt als aufgenommen angezeigt.
- [ ] Wiederholte oder parallele Übermittlung und späteres Wiederöffnen verwenden die bestehende unveränderliche Aufnahme und denselben zugeordneten Run. Es entsteht kein zweiter logischer Agentenschritt. Eine inzwischen geänderte Quelle ersetzt nicht die aufgenommene Fassung.
- [ ] Nach bestätigter Aufnahme oder Start führt die Ansicht zur richtigen Auswahl in der Anforderungsliste. Browser-Schließen und späteres Öffnen beeinflussen die Hintergrundausführung nicht; der aktuelle Zustand und das spätere Ergebnis sind über dieselbe Identität erreichbar.
- [ ] Formular, Aktionen und Fehlerhinweise sind per Tastatur verständlich bedienbar und bei 390 sowie 1024 Pixeln nutzbar. Verhaltenstests prüfen beide Wege, abgewiesenen Start nach erfolgreicher Aufnahme und doppelte Übermittlung. Der direkte Nachweis nimmt ein echtes kontrolliertes Issue auf, startet die Analyse, schließt den Browser und liest später denselben Run mit Ergebnis oder konkretem Fehler über die GUI zurück.
