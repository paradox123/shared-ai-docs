# 02: Erfolgreiche Extraktionen nach Neustart wiederverwenden

Status: closed

**Parent:** [Wiederaufnehmbare Wiki-Pflege](../spec.md)

**What to build:** Ein unterbrochener Wiki-Pflegelauf kann in einem neuen Prozess fortgesetzt werden, ohne bereits erfolgreiche, unveraenderte Extraktionen erneut beim Modell anzufordern. Nur fehlende, beschaedigte oder inkompatible Arbeit wird neu verarbeitet. Gesicherte Modellarbeit ist noch kein veroeffentlichtes Wiki-Wissen.

**Blocked by:** None (can start immediately).

**Spec coverage:** User Stories 12–13, 24–25; Implementation Decisions 1, 5, 7, 13.

- [ ] Die vorhandene Extraktionsgrenze wird bei Bedarf als kleiner vorbereitender Schritt fuer Wiederverwendung zugaenglich gemacht; bestehende oeffentliche Pflege- und Query-Aufrufe bleiben der Nachweisweg.
- [ ] Jede erfolgreich validierte Extraktion wird dauerhaft und vollstaendig gesichert, bevor sie als wiederaufnehmbarer Fortschritt gilt. Ein frischer Prozess kann den Zustand ohne Speicher des vorherigen Prozesses verwenden.
- [ ] Ein isolierter Prozessabbruch nach einem gesicherten Ergebnis fuehrt beim Neustart zu keinem zweiten identischen erfolgreichen Providerauftrag fuer diese Quelle; offene Arbeit wird weiterverarbeitet und das Endergebnis bleibt korrekt.
- [ ] Die Wiederverwendbarkeit beruecksichtigt Quellenidentitaet und Inhalt sowie relevante Modell-, Prompt-, Schema- und Compilerstaende und jeden weiteren tatsaechlich verwendeten Modellkontext. Eine Aenderung daran entwertet die betreffenden Ergebnisse.
- [ ] Unvollstaendige, defekte oder inkompatible Eintraege gelten nicht als Erfolg. Unbetroffene kompatible Ergebnisse bleiben weiterhin verwendbar.
- [ ] Ein spaeterer Fehler vor der Veroeffentlichung, einschliesslich Quellenabweichung oder Indexfehler, loescht keine unabhaengig gueltigen gesicherten Extraktionen. Beim Folgeaufruf werden diese erneut auf Gueltigkeit geprueft.
- [ ] Cachetreffer allein machen keine Quelle aktuell veroeffentlicht und ziehen keinen vollstaendigen Pflegezeitpunkt vor. Bestehende Provenienz- und Aktualitaetspruefungen bleiben wirksam.
- [ ] Bestehende Pflegezustaende ohne Wiederaufnahmedaten funktionieren weiter; eine erforderliche lokale Zustandsuebernahme verliert keine gueltigen generierten Seiten oder gespeicherten Antworten.
- [ ] Nach vollstaendig erfolgreicher Verarbeitung verursacht ein unveraenderter Folgeaufruf keine neuen Modellanfragen.

**Verification:** Bestehenden oeffentlichen Pflegeaufruf mit kontrolliertem Provider ausfuehren, nach nachweisbar gesicherter Arbeit den eigenen Testprozess beenden und einen frischen Prozess starten. Wiederverwendung anhand beobachteter Provideranfragen fuer die kontrollierten Quellen und der anschliessenden WikiQuery-Ergebnisse pruefen. Der Test besitzt eine kurze Frist und raeumt ausschliesslich eigene Prozesse auf.

**Boundary:** Kein Scheduling- oder Prioritaetsmodell vorwegnehmen. Noch kein kontrolliertes Produktionsbudget; das liefert Ticket 03. Der Cache ist abgeleitete Modellarbeit, kein zweiter Suchspeicher. Aenderungen am Compiler werden ueber die bestehende lokale Integrationsmechanik geliefert, ohne eigenstaendiges Upstream-/Dependency-Upgrade. Live-Automation bleibt unveraendert.

## Implementierungsnachweis

Ticket 02 wurde nach separater kritischer Verifikation und Koordinator-Abnahme am 17.09.2026 mit [PR #4](https://github.com/paradox123/shared-ai-docs/pull/4) nach `main` geliefert. Verifizierter Merge: [`2c73bb72d22eda046788ae90115caa21d466cb45`](https://github.com/paradox123/shared-ai-docs/commit/2c73bb72d22eda046788ae90115caa21d466cb45). Alle neun akzeptierten Dateihashes des Inhaltsmanifests `81a70b813fe791266a0412f03837af9bcb98100cae81a05ca8a5dc3cd8ae995e` wurden auf Remote-`main` bestätigt. [Gemessene Ergebnisse, konkrete dauerhafte Rohbelege und Grenzen](../../../contextual-llm-wiki/evidence/resumable-maintenance-02.md). Die restlichen vier Tickets und die produktive Aktivierung bleiben offen; der gemeinsame OpenSpec-Change wird nicht archiviert.
