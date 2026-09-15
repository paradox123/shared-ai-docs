# UX-01 — gemeinsame Run-Ansicht

## Arbeitsbasis und Umfang

Git-Eigentümer: `shared-ai-docs`; ursprünglicher Checkout `main` bei `dded7d4`.
Uncommittete UX-Planung und andere lokale Änderungen bleiben im ursprünglichen Checkout erhalten.
Implementierungsziel: `codex/operator-gui-ux-01` im isolierten Worktree
`../shared-ai-docs-operator-gui-ux-01`, aus dem lokal abgeschlossenen GUI-03-Stand `a46a133`.
Dieser Stand enthält die vollständigen GUI-03-Code- und Abnahmenachweise; er wird hier als gemeinsame Codebasis verwendet.
Integration in `main` und menschliche Abnahme von GUI-03 werden dadurch nicht vorweggenommen.
Reviewbasis für UX-01 ist `a46a133`; GUI-03 wird nicht erneut als UX-01-Änderung bewertet.
Der beim Worktree-Anlegen ausgeführte Skill-Sync-Hook wurde auf den ursprünglichen
gemeinsamen Checkout zurückgesetzt; globale Skill-Links zeigen nicht auf diesen Feature-Worktree.

Das passende OpenSpec-Gate ist `add-agent-framework-operator-gui` (spec-driven), Task 4.1.
Die freigegebene UX-Planung wird in den Worktree übernommen, GUI-03-Szenarien und Tasks bleiben erhalten.
Die Implementierung konkretisierte die aktive Anforderung „Workflow and persisted run inspection“.
Nach der Abnahme wurde nur dieser fertige Umfang als `add-agent-framework-shared-run-view`
extrahiert und archiviert; es entsteht kein neues Produktverhalten.
UX-02 bis UX-04 und die ursprünglichen späteren GUI-Tickets bleiben offen.

## Reproduzierter Fehler

[Öffentlicher Browsercheck vor der Korrektur](evidence/ux-01/red-status.log):
Die gespeicherte Execution antwortet mit `completed`, die sichtbare Liste zeigt `● Gestartet`.
Die Prüfung scheitert am fachlichen Vergleich, nach erfolgreichem Build und realer Speicherung durch HTTP/Worker.

## Abnahme

Technische Verifikation am 14.09.2026 über die produktive GUI, öffentlich autorisierte
HTTP-Endpunkte, PostgreSQL und unabhängige API-/Worker-/Browserprozesse.
Der Nutzer hat diesen Umfang am **15.09.2026 ausdrücklich akzeptiert** und den
Abschluss von Spec/OpenSpec sowie Commit und Push beauftragt. Die folgenden
Beobachtungen tragen die Abnahme; die dokumentierten Grenzen bleiben bestehen.

| Anforderung | Erwartetes Verhalten | Beobachtetes Ergebnis und Beleg |
| --- | --- | --- |
| Gemeinsamer Einstieg | Öffnen zeigt Titel, Quelle, Status und Ergebnis vor vollständigen Anforderungen; alle vier Ansichten gehören zum ausgewählten Run. | Bei 1024 und 390 px öffnet **Ergebnis**. Öffentliche Titel, Quell-URL, Zusammenfassung, sämtliche 12 Findings und vollständige gespeicherte Anforderungen stimmen überein. Lange Anforderungen bleiben im eigenen Tab, Findings aufklappbar. [Live-Daten](evidence/ux-01/live-shared-run.json), [Desktop](evidence/ux-01/result-1024.png), [Mobil](evidence/ux-01/result-390.png). |
| Verlässliche Zustände | Liste und Kopf zeigen den bestätigten Zustand; Run-ID allein bedeutet nicht „Läuft“. | `admitted`, `queued`, `running`, `reconciling`, `completed`, `failed` und unbekannter Wert werden gegen öffentlich geformte Antworten geprüft. Tatsächliche Speicherung und Worker belegen Aufnahme, Warteschlange und erfolgreichen Verlauf zusätzlich ohne Ersetzung der Execution-Antwort. Analyseabschluss behauptet keine Implementierung oder Review. [Browsertests](evidence/ux-01/shared-browser.log). |
| Beobachtung und Wiederöffnen | Änderungen werden ohne Neuauswahl sichtbar; Verbindungsfehler bleiben vom Ausführungsfehler getrennt. | Echter GitHub/Codex-Run wird als wartend, laufend und abgeschlossen beobachtet. Nach API-Neustart öffnet ein neuer Browserkontext dieselben Identitäten. Unterbrochene Reads markieren „zuletzt bestätigt“, erhalten Inhalte und erholen sich; unbekannte Antworten bleiben unbekannt. [Live-Test](evidence/ux-01/live.log), [Fehler-/Erholungstests](evidence/ux-01/shared-browser.log). |
| Auswahl und Berechtigungen | Verspätete alte Reads überschreiben keine neue Auswahl; Entzug löscht die Ansicht. | Verzögerte Antworten eines vorherigen Runs, hängende Reads einer anderen Listenzeile und 403 während initialer Hydrierung werden über den Browser reproduziert. Die neue Auswahl bleibt bestehen; der 403-Fall bleibt abgemeldet. Abgelehnte Aufnahme unterbricht nicht die Beobachtung des gewählten Runs. [Regressionen](evidence/ux-01/shared-browser.log), [RED Zugriffsentzug](evidence/ux-01/red-revoked-hydration.log). |
| Bestehende Funktionen | Aufnahme/Start, Verlauf, Sessions, Dateien und Herkunft bleiben erreichbar. | Die bisherigen 12 Aufnahme-/Execution-/Workflow-Browsertests bestehen mit der neuen Navigation. Der Live-Run enthält 22 Ereignisse und zwei verfügbare Artefakte. Tests öffnen Sessiondaten und Artefakte über die vorhandenen Endpunkte; UX-02 bis UX-04 werden dadurch nicht vorweggenommen. [Bestehende Browserchecks](evidence/ux-01/existing-browser.log). |
| Tastatur und schmale Ansicht | Beschriftete Tabs, stabiler Fokus und gewählte Ansicht; kein horizontaler Seitenüberlauf bei 390/1024 px. | Pfeile/Home/End bedienen die vier Tabs. Echte Workerupdates erhalten den fokussierten Schritt und **Verlauf**. Gezielte SSE-Änderungen erhalten aufgeklappte Sessionmetadaten und Artefaktbutton-Fokus auch bei geänderter Verfügbarkeit. Beide Live-Viewports melden keinen Seitenüberlauf; finale Bilder zeigen den sichtbaren Zeilenfokus. [Browsertests](evidence/ux-01/shared-browser.log), [Review](ux-01-review.md). |

Der finale echte Run `64074832-80e1-4d57-aaf5-38ba551c5c8a` gehört zur Submission
`91655d7f-1014-46f1-b286-688a704cf3db` und zur bestehenden Quelle
`https://github.com/paradox123/probare-crm/issues/4`. Aufnahme, Worker und Wiederöffnung
verwenden diese Identitäten. Die Abnahme liest reale Providerdaten und führt eine
Anforderungsanalyse durch; sie schreibt nicht in das GitHub-Repository oder das Issue.
Die Browser melden keine JavaScript-Fehler. Testdatenbanken und Prozesse werden entfernt.

## Verifikation und Reproduktion

Aus `microsoft-agent-framework-work-package-pilot`:

```bash
uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_shared_run_browser -v

uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_submission_browser \
  tests.test_submission_execution_browser tests.test_workflow_browser -v

WPCP_CODEX_ENDPOINT_PROBE=1 \
WPCP_LIVE_GITHUB_SUBMISSION_URL=https://github.com/paradox123/probare-crm/issues/4 \
WPCP_SUBMISSION_PROOF_DIR=/tmp/wpcp-shared-run-proof \
  uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest tests.test_shared_run_live -v

uv run --python 3.14 --with-requirements codex-requirements.txt \
  python -m unittest discover -s tests -v
```

- Neue gezielte UX-01-Browserchecks: **10 bestanden**, 60,549 s.
- Bestehende GUI-Browserchecks: **12 bestanden**, 134,996 s.
- Finaler echter GitHub/Codex-Durchlauf mit sichtbarem Fokus: **1 bestanden**, 74,815 s.
- Timeout-Erklärung und Wiederaufnahme: **1 bestanden**, 16,214 s; anschließend die
  vollständige betroffene Ausführungsklasse: **9 bestanden**, 23,457 s
  ([Diagnosecheck](evidence/ux-01/reconciliation-diagnostic.log), [Ausführungsklasse](evidence/ux-01/execution-regression.log)).
- Ergebnis-/Zustandsregression nach der Diagnosekorrektur: **3 bestanden**, 27,095 s
  ([Protokoll](evidence/ux-01/result-regression.log)).
- Finaler vollständiger Pilot-Lauf: **213 bestanden, 26 übersprungen, 0 Fehler**
  (239 Tests insgesamt, 1.074,965 s; [Protokoll](evidence/ux-01/full-regression.log)).
  Die übersprungenen Tests benötigen ausdrücklich aktivierte Provider-/Deployment-
  Probes; der oben genannte echte UX-01-GitHub/Codex-Lauf wurde separat ausgeführt.
- Erster vollständiger Pilot-Lauf: 238 Tests, 2 Fehler, 26 bewusst übersprungene
  Opt-in-Prüfungen ([Originalprotokoll](evidence/ux-01/full-regression-first.log)).
  Der bereits gestartete Lauf erwartete noch die alte Abgleichbeschriftung; der
  korrigierte gezielte Test deckte zusätzlich den fehlenden Diagnoseinhalt auf.
  Der darauffolgende Starttest blieb in diesem Lauf wartend. Beide bestehen in der
  vollständigen Ausführungsklasse nach der Korrektur und im finalen Gesamtlauf.
- OpenSpec strikt gültig; Syntaxprüfung von 14 JS-/Browserdateien und abschließender
  Syntaxcheck des korrigierten Ergebnisrenderers bestanden.

Die ursprünglichen RED-Nachweise betreffen den falschen Status, fehlenden Ergebniszugang,
abgebrochene Beobachtung, verlorenen Schritt-/Disclosure-Fokus, einen fremden alten
Status, blockierende andere Listenzeilen und initialen Zugriffsentzug. Sie liegen in
`evidence/ux-01/red-*.log`; die finalen zehn Tests prüfen die zugehörigen beobachtbaren
Verhaltensweisen gemeinsam. Der zuletzt ergänzte Zugriffsentzugstest besteht separat
und im finalen gezielten Lauf; die schon laufende vollständige Suite hatte ihn bei
Testentdeckung noch nicht aufgenommen. Der finale Gesamtlauf enthält auch diesen Test.

## Review, Gestaltung und Grenzen

Die getrennten Standards- und Spec-Reviews sind in [UX-01 Review](ux-01-review.md)
aufgeführt. Ihre fünf Befunde wurden durch reproduzierbare Checks korrigiert und
vom jeweiligen Reviewer als behoben bestätigt. Der Impeccable-Reviewer bewertete
alle vier gezielten Korrekturen als `resolved`, Disposition `ship`; diese Aussage
gilt für seine Fixliste, nicht als pauschale Konformitätszertifizierung.

Der einmalige [Detectorlauf](evidence/ux-01/detector.json) wurde vor den mechanischen
Schrift-/Kickerkorrekturen aufgezeichnet. Er wurde gemäß Skill nicht erneut ausgeführt.
Die verbleibende gestalterische Bewertung stützt sich auf die finalen Bilder und den
unabhängigen Reviewer. Es entstanden keine generierten Rasterassets oder ein neues Designsystem.

Der echte Lauf verifiziert den erfolgreichen Pfad. `reconciling`, unbekannte Werte,
Netzausfälle und zeitlich gezielte Rennen sind zusätzlich kontrollierte Antworten an
der öffentlichen HTTP-/SSE-Grenze, keine Behauptung über einen realen Providerausfall.
Die vollständige Backend-Suite prüft daneben ihre vorhandenen Fehler- und Recoveryfälle.

Nicht verifiziert: Azure-Deployment, physisch getrennte Rechner (weiter GUI-Ticket 16 /
Task 3.2a), reale Mobilgeräte, weitere Browserengines oder ein vollständiger
Screenreader-/Zoom-/WCAG-Audit. Die Statusbeobachtung fragt pro sichtbarer Anforderung
weiter periodisch ab; die Skalierung sehr großer Listen ist nicht Gegenstand von UX-01.
Der übergeordnete Change bleibt mit seinen 15 offenen Tasks aktiv. Der akzeptierte
UX-01-Umfang wird separat archiviert und auf `codex/operator-gui-ux-01` gepusht;
ein `main`-Merge ist nicht Teil dieses Abschlusses.

## Abschluss am 15.09.2026

Die Refaktorierungsprüfung aus [design.md](design.md) ergab keinen weiteren
Laufzeitänderungsbedarf. Die zehn gezielten Browserfälle und der öffentliche
Timeout-/Wiederaufnahmefall bestehen nach dieser Prüfung erneut: **11 Tests,
83,926 s, keine Fehler** ([Abschlussprotokoll](evidence/ux-01/closeout-browser-2026-09-15.log)).
Der OpenSpec-Standardpfad veröffentlicht genau eine eng abgegrenzte Anforderung
und archiviert diesen `spec-driven`-Change. Die bisherige Live-Evidence bleibt
bytegleich und wird mit ihren SHA-256-Werten geprüft.

Der Standardpfad `openspec archive -y add-agent-framework-shared-run-view` hat
den Change nach `2026-09-15-add-agent-framework-shared-run-view` archiviert und
eine Anforderung in der kanonischen Spec ergänzt. Die strikte Prüfung aller
aktiven Changes und Specs besteht mit **51 geprüften Einträgen, 0 Fehlern**.
Alle 17 betroffenen Markdown-Dokumente haben gültige lokale Links; die ursprünglichen
Live-Dateihashes, die 15 offenen Parent-Tasks und der Laufzeit-/Testcode sind unverändert.
