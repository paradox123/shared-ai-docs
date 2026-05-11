READY: RADW-C4 wurde im erlaubten Write-Set geliefert.

Geändert:
- [count.txt](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/target/output/count.txt): jetzt exakt `1\n2\n3\n4\n`
- [delivery.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/delivery-evidence/radw-c4/delivery.json): `final_status: ran-target`, `written_value: "4"`
- [radw-c4.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T134151Z-real-regression/closeout/children/radw-c4.json): `final_status: ran-target`, `closeout_status: closed`, `output_status: pass`

Verification:
- `ValidateChildReadiness.cs` für `RADW-C4`: passed
- Count assertion auf `1\n2\n3\n4\n`: passed
- Closeout JSON assertion: passed
- Delivery JSON assertion: passed
- `git diff --check` auf den geänderten Dateien: passed