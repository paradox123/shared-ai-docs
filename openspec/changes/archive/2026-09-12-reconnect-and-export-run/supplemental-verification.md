# Ergänzende Verifikation nach dem URI-only-Fix

Ausgeführt am 2026-09-12 im Pilotverzeichnis nach der letzten fachlichen Änderung:

```bash
python3 -m unittest \
  tests.test_run_dossier.RunDossierTests.test_legacy_artifact_uri_without_bytes_is_visible_and_blocks_qualification \
  tests.test_fake_codex_attempt -v
```

Beobachtetes Ergebnis: **22 Tests in 65,401 Sekunden, OK**. Dies ist eine
Zusammenfassung des ausgeführten Toolergebnisses, kein nachträglich erzeugtes
vollständiges Konsolenprotokoll.

Der neue Test war zuvor rot: ein reiner `fake://report`-Verweis lieferte
`qualificationEligible: true`. Nach der Änderung erscheint genau ein
`external-artifact-unavailable`-Eintrag; die Qualification-Voraussetzung ist false,
sein Download liefert 410 und die History bewahrt den ursprünglichen URI zusammen
mit der neuen Manifestreferenz. Die 21 vorhandenen Fake-Codex-Tests bestätigen
weiterhin Session-Recovery, Reihenfolge, Redaction, Human Requests,
Fortsetzungsentscheidungen und deren Zugriffsschranken.

## Abschlussverifikation

Nach Benutzerabnahme, Abschlussreview und Archivierung am 2026-09-12 wurde das
gesamte Dossier-Modul erneut ausgeführt:

```bash
python3 -m unittest tests.test_run_dossier -v
```

Beobachtetes Ergebnis: **15 Tests in 169,314 Sekunden, OK**. Diese Zusammenfassung
stammt aus dem ausgeführten Toolergebnis; das ursprüngliche Beispieldossier und
sein öffentlicher Nachweis wurden nicht überschrieben.

Der neue synthetische Prozessnachweis lieferte 10.015 Events, 9.765 identische
Reconnect-Events über SSE und Cursor-Seiten, 12.027.369 Stream-Bytes, fünf
Artefakte und null rohe Canary-Treffer auf 35 geprüften Oberflächen. Restore in
frische Komponenten ergab dieselben öffentlichen Checksummen wie dieser Quellrun:

- History: `9d4a5e5159213deb1645ea50ebcf1f885afcc7dfee74c3f5246f6bb61e43104b`
- Projektion: `2ab1007b99424bf4f437ff184785f878d08fda198a538a873ecb697ad487ae81`
