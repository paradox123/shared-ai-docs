# Wiederaufnahme einzelner Seitenantworten

Status: die eng gefasste Tracker-Spec wurde am 27.09.2026 angenommen. Die produktive Seitenantwort-Wiederaufnahme ist geprüft. Der übergeordnete OpenSpec-Change bleibt für separat offene Betriebs- und Importabnahmen aktiv.

## Umsetzung

Der öffentliche `maintain`-Helper übergibt die Seitengenerierung an einen dauerhaften Antwortcache. Eine Antwort wird pro Seite gesichert, sobald sie zurückkommt und die vollständig gerenderte Markdown-Seite Größen- und Schema-Prüfung besteht. Das Schreiben ist atomar und enthält eine Prüfsumme. Beim Folgelauf werden aktuelle Originalbytes erneut gegen die erfassten Quellenhashes geprüft. Der Schlüssel bindet genaue Anfrage und Modell, Quellidentitäten, Originalpfade und Hashes, den Publikationsvertrag, Providerparameter, den gepinnten Compiler und dessen Lockdatei. Ein ungültiger, beschädigter oder inkompatibler Eintrag wird neu erzeugt.

Ein Treffer ersetzt weder Provenienz- und Driftprüfung noch Veröffentlichung oder QMD-Abgleich. Bis die normale Compilerprüfung und Veröffentlichung abgeschlossen sind, bleibt ein Lauf mit offener Arbeit unvollständig und rückt `lastCompleted` nicht vor. `pageResponses.saved/reused/invalid` macht Cachefortschritt im bestehenden Fortschrittsdatensatz sichtbar.

Der neue Upstream-Patch ändert nur die Seitengenerierung. Für den exakten neu gebauten Compiler-Digest bleibt daher genau der unmittelbar vorherige Produktions-Compilervertrag für bereits validierte Extraktionen lesbar. Der neue Compiler-Digest wurde nach zwei sauberen Bootstrap-Aufrufen als `48c07885fa82636b6914059eff6fd22f4547391133fb2dbf8c498e889822fb2b` bestätigt; andere Compilerstände erhalten diese Ausnahme nicht.

Der Bootstrap setzt den generierten Compilercheckout vor Anwendung der versionierten Patchserie auf den bestätigten Pin zurück. Damit lassen sich überlappende Patches auch bei wiederholter Einrichtung anwenden. Zwei aufeinanderfolgende `scripts/bootstrap.sh`-Aufrufe bauten denselben gepatchten Compiler erfolgreich.

## Verhaltensnachweis

Der öffentliche Helper-Test verwendet zwei temporäre Git-Quellrepos, den echten gepinnten Compiler, eine isolierte QMD-Datenbank und einen lokalen deterministischen Provider.

- Vor der Cacheänderung wurde der Verlust reproduziert: Nach kontrolliertem Stopp wiederholte der Folgelauf eine bereits erfolgreich beantwortete Seitengenerierung (`1 !== 0`).
- Danach blieb die erste abgeschlossene Antwort über den Stopp erhalten. Der Teilbericht meldete `budget-exhausted`, offene Arbeit und keinen `lastCompleted`; die unfertige Konzeptseite war weder vorhanden noch über WikiQuery aktuell verfügbar.
- Der frische Lauf fragte die gespeicherte Antwort nicht erneut an, veröffentlichte eine Markdown-Seite mit beiden Originalbelegen und machte sie über QMD auffindbar.
- Ein unveränderter Folgelauf war No-op ohne Providerrequests. Eine Änderung einer Quellversion führte zu einer neuen Seitengenerierungsanfrage und aktuellem Seiteninhalt. Die Quelltexte wurden vom Compiler nicht geändert.

## Prüfungen

- `./wiki-node --test --test-name-pattern='bounded helper resumes a completed page response after generation is interrupted' test/maintenance-budget.test.ts`: bestanden, 1/1; vor der Implementierung rot.
- `./wiki-node --test --test-concurrency=1 test/*.test.ts`: bestanden, 117/117.
- `npm run typecheck`: bestanden.
- `npm run test:upstream`: bestanden, 59/59 Upstream-Integrationstests auf dem sauberen Patchstack.
- `npm run test:operations`: bestanden, 14/14.
- `openspec validate operate-contextual-llm-wiki --strict`: bestanden.
- `git diff --check`: bestanden.
- `scripts/bootstrap.sh`: zweimal nacheinander erfolgreich; der anschließende gezielte Wiederaufnahmetest blieb grün.

Der erste parallele Gesamtlauf meldete 115/117. Er deckte auf, dass die Publikationsversion Teil des Antwortvertrags sein muss; nach ihrer Aufnahme bestand der Provenienz-Migrationstest. Der zweite zeitgebundene Fehler bestand isoliert und im abschließenden seriellen Gesamtlauf.

## Produktive Wiederaufnahme am 27.09.2026

Beide Aufrufe verwendeten den gepatchten Compiler und Helper aus dem Implementierungs-Worktree, aber die unveränderte gemeinsame Produktionskonfiguration und den echten gemeinsamen Wiki-/QMD-Bestand. Die SHA-256 der Produktionskonfiguration blieb `f878d6123252a7474a44d6cf0ba561bec9b21d7f1a14bb2cfaf1d73550d927cf`.

| Lauf | Ergebnis | Seitenantworten | Restarbeit |
|---|---|---:|---|
| [20-Minuten-Lauf](</Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/contextual-llm-wiki/.local/operations-runs/20260927T135350-89197/observation.json>) | Nach 1201,3 s kontrolliert mit `budget-exhausted`, Exit 1 beendet; kein Vollerfolg behauptet. 2209 Extraktionen wiederverwendet; der Quellenabgleich war abgeschlossen. | 322 gespeichert, 0 wiederverwendet, 0 ungültig | `compile`, Wiki-Status/Lint und QMD update/embed/status offen |
| [Wiederaufnahme](</Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/contextual-llm-wiki/.local/operations-runs/20260927T141443-45826/observation.json>) | Nach 121,3 s kontrolliert mit `budget-exhausted`, Exit 1 beendet; Restarbeit blieb sichtbar. | 322 wiederverwendet, 8 gespeichert, 0 ungültig | dieselben Compiler-, Wiki- und QMD-Phasen offen |

Der Produktionscache enthält danach 330 Seitenantwortdateien. Die Wiederverwendung der 322 zuvor gesicherten Antworten in einem frischen Produktionsprozess belegt die Prozessgrenzen hinweg persistierte Speicherung und Kompatibilitätsprüfung. Der unveränderte Quell-/Modellvertrag wurde im Test zusätzlich durch geänderte Quellen gegen falsche Wiederverwendung geprüft.

Diese Läufe prüfen die Cache-Wiederaufnahme am echten Bestand; sie schließen weder den vollständigen Erstimport noch Wiki-Publikation, QMD-Embeddings oder den späteren Schedulerlauf ab. Die Automationsdefinition und die Produktionskonfiguration wurden nicht geändert. Nach beiden Läufen war die gemeinsame Maintenance-Sperre frei.

## Verifikationsgrenzen

Die isolierte Verhaltensprüfung verwendet künstliche Quellen und kontrollierte Providerantworten. Die produktive Wiederaufnahme bestätigt Persistenz, Cachetreffer und ehrlichen Teilstatus, aber nicht die Ausgabe eines vollständigen produktiven Compile-/Publikations-/QMD-Zyklus. Der vollständige Import und spätere Schedulerlauf bleiben separat offen.
