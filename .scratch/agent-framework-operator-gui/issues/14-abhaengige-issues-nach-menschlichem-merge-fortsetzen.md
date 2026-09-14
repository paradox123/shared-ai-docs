# 14: Abhängige Issues nach menschlichem Merge selbstständig fortsetzen

**What to build:** Der Pilot beobachtet abgeschlossene Vorgänger und startet zulässige Folge-Issues aus GitHub- oder Datei-Mandaten selbstständig von der maßgeblichen Repositorybasis.

**Blocked by:** 13: PRD-Datei in lokale Issue-Dateien zerlegen.

**Status:** ready-for-agent

- [ ] Qualifikation oder menschliches Approval allein macht einen Nachfolger nicht startfähig: Vorgänger-PR muss menschlich gemerged und das blockierende Issue in seiner ursprünglichen Quelle geschlossen sein.
- [ ] GitHub-Abschluss und lokaler Dateistatus werden quellengerecht gelesen beziehungsweise nachvollziehbar aktualisiert; lokale Issues benötigen kein GitHub-Spiegelissue.
- [ ] Die GUI zeigt den konkreten Blocker und den beobachteten Übergang zur Startfähigkeit; der Hintergrundmonitor benötigt keinen geöffneten Benutzerclient.
- [ ] Vor Start gilt der maßgebliche gemergte Provider-Head als Basis; eine veraltete lokale Referenz startet keinen Nachfolger. Die Repository-Serialisierung verhindert konkurrierende Writer.
- [ ] Wiederholte Merge-/Statusbeobachtung, Service-Neustart oder Abbruch während der Disposition erzeugen keinen zweiten Kind-Run und keine doppelte externe Wirkung.
- [ ] Zwei kleine Mandate, eines je Quelle, beweisen Wartezustand vor Merge/Abschluss und genau einen anschließenden Start vom korrekten Head. Der Pilot führt den menschlichen Merge nicht selbst aus.

## Comments

### 2026-09-14 — Unverbindliche Designreferenz

Der [Backstage-/React-Flow-Prototyp mit Codeverweis und Session-Einstieg](../prototype.md) dient als visuelle Orientierung. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben dieses Ticket und die zugehörige OpenSpec-Spezifikation. Abweichungen vom Prototyp sind zulässig; erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten.
