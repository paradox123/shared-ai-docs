# Storyboard: Wie ein Ticket den Entwicklungsprozess durchläuft

Status: Entwurf zur fachlichen und visuellen Freigabe

## Ziel

Das Video vermittelt einer Projektleitung, wie ein Ticket durch den agentischen Entwicklungsprozess geführt wird:

- was der Mensch entscheidet und freigibt,
- welche begrenzten Aufgaben Agenten übernehmen,
- welche Aufgaben die Work Package Control Plane deterministisch ausführt,
- wie Fehler nach ihrer Ursache behandelt werden,
- und warum das Ergebnis erst nach menschlicher Freigabe abgeschlossen wird.

Die erwartete Laufzeit beträgt ungefähr drei Minuten. Das Ticket ist die Hauptfigur; einzelne Entwicklerpersonen stehen nicht im Mittelpunkt.

## Visuelles Grundmodell

Während des gesamten Videos bleiben drei horizontale Spuren sichtbar:

```text
┌──────────────────────────────────────────────────────────────┐
│ MENSCH          Anforderungen · Freigaben · Entscheidungen  │
├──────────────────────────────────────────────────────────────┤
│ AGENT           Implementierung · Reviews · Reparaturen     │
├──────────────────────────────────────────────────────────────┤
│ CONTROL PLANE   Koordination · Gates · Historie · Recovery  │
└──────────────────────────────────────────────────────────────┘
```

Ein Ticket mit der Kennung `ISSUE #247` wandert von links nach rechts durch diese Spuren. Jede Aktion erscheint in der fachlich verantwortlichen Spur. Wechsel zwischen den Spuren werden als Übergabe dargestellt, nicht als autonomes Verschwimmen der Verantwortlichkeiten.

Die drei regulären Human-in-the-Loop-Gates erhalten ein wiederkehrendes Symbol und eine eindeutige Nummer:

1. Anforderungen freigeben
2. Agentische Implementierung freigeben
3. Verifiziertes Artefakt freigeben

## Szenen

### Szene 1 — Ein Ticket beginnt seine Reise

**Dauer:** etwa 12 Sekunden

**Kernaussage:** Ein Ticket durchläuft einen kontrollierten Entwicklungsprozess und nicht nur eine einzelne Agentensitzung.

**Bild:** Eine einzelne Ticketkarte `ISSUE #247` erscheint links. Rechts liegen noch unscharf die Stationen Anforderungen, Implementierung, Nachweise, Reviews und Freigabe. Beim Einsetzen des Sprechertexts werden die drei Spuren Mensch, Agent und Control Plane eingeblendet.

**Text im Bild:**

- „Ein Ticket. Ein kontrollierter Entwicklungsprozess.“
- klein: „Vom Arbeitsauftrag zum verifizierten Artefakt“

**Übergang:** Die Ticketkarte bewegt sich in die Spur Mensch.

### Szene 2 — Drei Akteure, klare Verantwortung

**Dauer:** etwa 18 Sekunden

**Kernaussage:** Mensch, Agent und Control Plane besitzen unterschiedliche Verantwortlichkeiten.

**Bild:** In jeder Spur erscheint genau eine Rollenkarte:

- Mensch: entscheidet und gibt frei
- Agent: bearbeitet begrenzte Aufgaben
- Control Plane: koordiniert und prüft deterministisch

Darüber erscheint ein durchgehender Rahmen mit dem Label „Human in the Loop“. Er verbindet die drei späteren Freigabe-Gates, ohne den Menschen als permanenten Mikromanager darzustellen.

**Text im Bild:** „Human in the Loop ist das Governance-Prinzip.“

**Übergang:** Der Rahmen fokussiert auf Gate 1.

### Szene 3 — Gate 1: Anforderungen freigeben

**Dauer:** etwa 24 Sekunden

**Kernaussage:** Ohne bestätigte Anforderungen und eindeutige Akzeptanzkriterien beginnt keine agentische Bearbeitung.

**Bild:** In der Mensch-Spur öffnet sich das Ticket mit drei Akzeptanzkriterien. Der Mensch bestätigt die fachlichen Anforderungen. Die Ticketkarte erhält das Siegel „Anforderungen freigegeben“.

Danach wechselt die Ticketkarte in die Control-Plane-Spur. Dort laufen nacheinander drei sichtbare Prüfungen:

- Mandat vorhanden
- Kriterien eindeutig
- Repository und Berechtigung gültig

**Fehlervorschau:** Ein unklar formuliertes Kriterium wird kurz markiert. Das Ticket bewegt sich zurück zur Mensch-Spur und erst nach der Korrektur wieder nach vorne. Es wird ausdrücklich kein Agent gestartet.

**Text im Bild:** „Unklar? Zurück zum Menschen – noch kein Agentenlauf.“

**Übergang:** Aus den bestätigten Anforderungen entsteht ein begrenzter Arbeitsauftrag.

### Szene 4 — Gate 2: Implementierung freigeben

**Dauer:** etwa 22 Sekunden

**Kernaussage:** Bestätigte Anforderungen sind nicht automatisch eine Freigabe zur agentischen Umsetzung.

**Bild:** Die Control Plane materialisiert eine kompakte Auftragskarte:

- Umsetzungsscope
- Akzeptanzkriterien
- geplanter Verhaltensnachweis
- erwarteter Ausgangszustand

Die Karte geht zurück in die Mensch-Spur. Der Mensch prüft den abgegrenzten Auftrag und aktiviert Gate 2: „Agentische Implementierung freigeben“.

Erst danach erscheinen in der Control-Plane-Spur Repository-Reservierung, isolierter Arbeitsbereich und eine neue Agentensitzung.

**Text im Bild:** „Der Mensch autorisiert den konkreten Implementierungsauftrag.“

**Übergang:** Die Auftragskarte wird an die Agent-Spur übergeben.

### Szene 5 — Implementieren und deterministisch kontrollieren

**Dauer:** etwa 28 Sekunden

**Kernaussage:** Der Agent implementiert; die Control Plane übernimmt deterministische Prüfungen und Zustandsübergänge.

**Bild:** Zwei Spuren arbeiten sichtbar zusammen:

- In der Agent-Spur: Test zuerst rot, Codeänderung, Test grün, Nachweis pro Kriterium.
- In der Control-Plane-Spur: Git-Status, Testausführung, Sicherheitsprüfung, Redaction und eindeutige Commit-Korrelation.

Die Ticketkarte bleibt zwischen beiden Spuren sichtbar. Keine der deterministischen Prüfungen wird innerhalb der Agentenkarte dargestellt.

**Text im Bild:**

- Agent: „Implementieren und Nachweise liefern“
- Control Plane: „Prüfen, korrelieren und sicher publizieren“

**Übergang:** Der geprüfte Commit-Stand wird als Draft Pull Request eingefroren.

### Szene 6 — Drei unabhängige Reviews und Repair-Runden

**Dauer:** etwa 28 Sekunden

**Kernaussage:** Anforderungen, Code und Architektur werden unabhängig am selben Commit-Stand geprüft.

**Bild:** Die Control Plane dupliziert nicht das Ticket, sondern erzeugt drei schmale, nur lesende Reviewaufträge für denselben Commit-Stand:

- Anforderungsprüfung
- Codeprüfung
- Architekturprüfung

Die drei Reviewkarten liegen nebeneinander in der Agent-Spur. Sie besitzen keine Verbindung untereinander und sehen keine gegenseitigen Urteile.

Ein Finding geht in eine nummerierte Repair-Runde. Der Implementierungsagent erzeugt einen neuen Commit-Stand. Sofort erlöschen die bisherigen Nachweis- und Review-Siegel. Neue Gates und drei neue Reviewkarten werden sichtbar.

**Text im Bild:** „Neuer Commit-Stand bedeutet neue vollständige Qualifikation.“

**Übergang:** Die normale Prozesslinie verzweigt sich in mehrere Fehlerszenarien.

### Szene 7 — Fehler werden nach ihrer Ursache behandelt

**Dauer:** etwa 36 Sekunden

**Kernaussage:** Es gibt keinen universellen Retry. Die Reaktion hängt von der Fehlerklasse ab.

**Bild:** Die Ticketkarte bleibt in der Mitte. Nacheinander öffnen sich vier kompakte Fehlerpfade; jeweils nur einer ist aktiv:

1. **Unklare Anforderung**
   - zurück zum Menschen
   - Kriterium präzisieren und erneut freigeben

2. **Review-Finding**
   - begrenzter Repair-Auftrag an den Agenten
   - neuer Commit-Stand und vollständige Requalifikation

3. **Tool- oder Infrastrukturfehler**
   - Control Plane prüft bereits eingetretene Wirkungen
   - nur der fehlende Effekt wird erneut ausgeführt

4. **Agent steckt fest oder Repair-Limit ist erreicht**
   - sichtbare Intervention für den Menschen
   - Session fortsetzen, Lösungszweig beginnen, frischen Versuch starten, übernehmen oder abbrechen

Alle Pfade kehren entweder an einen eindeutig markierten stabilen Zustand zurück oder enden in einer menschlichen Entscheidung. Die Historie bleibt dabei sichtbar und unverändert.

**Text im Bild:** „Fehlerklasse bestimmt Recovery.“

**Übergang:** Nach erfolgreicher Requalifikation kehrt das Ticket auf den Hauptpfad zurück.

### Szene 8 — Gate 3: Verifiziertes Artefakt freigeben

**Dauer:** etwa 24 Sekunden

**Kernaussage:** Der Agent und die Control Plane qualifizieren das Ergebnis; nur der Mensch gibt das Artefakt frei.

**Bild:** Die Ticketkarte steht in einem ruhigen Freigabezustand. Daneben erscheint das Artefakt mit:

- exaktem Commit-Stand
- bestandenen Akzeptanznachweisen
- bestandener Sicherheitsprüfung
- drei bestandenen Reviews

Das verifizierte Artefakt wechselt in die Mensch-Spur. Der Mensch kann in die Nachweise und Historie hineinzoomen, Änderungen anfordern oder Gate 3 aktivieren: „Verifiziertes Artefakt freigeben“.

Erst nach dieser Aktion wird „Freigeben und zusammenführen“ aktiv. Eine Veränderung des Commit-Stands setzt die Qualifikation sichtbar zurück.

**Text im Bild:** „Kein Agent gibt seine eigene Arbeit frei.“

**Übergang:** Das freigegebene Artefakt wird mit Pull Request, Commit und Ticketabschluss korreliert.

### Szene 9 — Kontrollierter Abschluss

**Dauer:** etwa 16 Sekunden

**Kernaussage:** Der Prozess endet erst, wenn der menschlich freigegebene, verifizierte Stand tatsächlich zusammengeführt wurde.

**Bild:** Die Ticketkarte durchläuft drei letzte Kontrollpunkte:

- verifizierter Commit-Stand stimmt überein
- menschliche Freigabe liegt vor
- Pull Request wurde zusammengeführt

Danach wechselt die Ticketkarte auf „Abgeschlossen“. Die drei Human-in-the-Loop-Gates leuchten noch einmal entlang der vollständigen Reise auf.

**Schlussbild:**

```text
Mensch entscheidet.
Agenten bearbeiten.
Die Control Plane macht den Prozess verlässlich.
```

## Visuelle und sprachliche Leitplanken

- Das Ticket ist die Hauptfigur; keine einzelne Entwicklerpersona dominiert die Erzählung.
- Die drei Spuren bleiben räumlich stabil und werden niemals vertauscht oder gedreht.
- Menschliche Aktionen verwenden ein Hand-/Freigabesymbol, Agentenaktivitäten ein klar getrenntes Agentensymbol und deterministische Systemschritte ein Workflow-/Gate-Symbol.
- Farbe unterstützt die Semantik, ist aber nie der einzige Bedeutungsträger.
- Pro Zeitpunkt ist nur eine Hauptaktion hervorgehoben.
- UI-Texte sind primär deutsch. Kanonische englische Begriffe dürfen klein als technische Sekundärlabels erscheinen.
- Im Voice-over werden unter anderem „Commit-Stand“, „neuer Versuch ab Kontrollpunkt“, „Anforderungsprüfung“ und „Verhaltensnachweis“ gesprochen.
- Der Produktname „Work Package Control Plane“ wird nur in Einleitung und Schluss gesprochen.
- Untertitel werden aus dem final freigegebenen Sprechertext erzeugt und nicht als lange Absatzblöcke eingebrannt.
- Die Sprecherstimme muss vor der Gesamtproduktion anhand einer kurzen Probe freigegeben werden.

## Nächster Freigabepunkt

Vor Voice-over-Probe oder Videoproduktion werden bestätigt:

1. die neun Szenen und ihre Reihenfolge,
2. die drei stabilen Verantwortungsspuren,
3. die Darstellung der drei Human-in-the-Loop-Gates,
4. die Auswahl und Gewichtung der vier Fehlerszenarien.

## Fachliche Quellen

- `../spec.md`
- `../../../docs/langgraph-github-issue-pilot/Agent_Dev-Process.drawio`
