READY: RSW-C3 wurde geliefert.

Ich habe nur das erlaubte Write-Set geändert:
- [count.txt](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt): jetzt exakt `1\n2\n3\n`
- [delivery.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/rsw-c3/delivery.json)
- [rsw-c3.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c3.json)

Verifikation erfolgreich:
- `ValidateChildReadiness.cs` passed für `RSW-C3`
- Count-Assertion auf `1\n2\n3\n` passed
- Closeout-JSON-Assertion passed
- Delivery-Evidence-Assertion passed