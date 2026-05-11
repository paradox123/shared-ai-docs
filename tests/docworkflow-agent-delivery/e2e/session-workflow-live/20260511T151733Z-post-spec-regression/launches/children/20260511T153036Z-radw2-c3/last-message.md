READY: `RADW2-C3` wurde im erlaubten Write-Set umgesetzt.

Geändert:
- [count.txt](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/target/output/count.txt): jetzt exakt `1\n2\n3\n`
- [delivery.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/delivery-evidence/radw2-c3/delivery.json)
- [radw2-c3.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T151733Z-post-spec-regression/closeout/children/radw2-c3.json)

Verification: alle drei Handoff-Commands liefen erfolgreich, plus Delivery-JSON-Check und scoped `git diff --check`. `RADW2-C2` war geschlossen, der Prefix war vor dem Schreiben exakt `1\n2\n`, und ich habe keine Dateien außerhalb des erlaubten Write-Sets geändert. Hinweis: Für C3 war nur ein `launches/.../start-prompt.md` vorhanden; ich habe keine automatisierte Launch-Evidence beansprucht oder geschrieben.