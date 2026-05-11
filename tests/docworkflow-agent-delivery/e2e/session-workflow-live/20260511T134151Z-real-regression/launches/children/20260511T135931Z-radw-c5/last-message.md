READY. RADW-C5 ist im erlaubten Write-Set umgesetzt.

Geändert/geschrieben:
- `target/output/count.txt` enthält exakt `1\n2\n3\n4\n5\n`
- `delivery-evidence/radw-c5/delivery.json`
- `closeout/children/radw-c5.json`

Verifikation:
- `ValidateChildReadiness.cs` für `RADW-C5`: passed
- `count.txt` Exact-Output-Assertion: passed
- `radw-c5.json` Closeout-Assertion: passed
- zusätzliche `delivery.json` Contract-Assertion: passed
- gezielter `git diff --check`: clean

Hinweis: Für RADW-C5 war die passende `start-prompt.md` vorhanden; `launch-request.json`/`evidence.json` für die Launcher-Spur lagen nicht im Child-Write-Set und wurden nicht verändert.