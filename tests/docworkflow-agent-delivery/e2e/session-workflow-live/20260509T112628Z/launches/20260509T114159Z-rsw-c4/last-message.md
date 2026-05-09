READY: RSW-C4 delivered inside the allowed write-set.

Updated:
- [count.txt](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/target/output/count.txt): now exactly `1\n2\n3\n4\n`
- [delivery.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/delivery-evidence/rsw-c4/delivery.json)
- [rsw-c4.json](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260509T112628Z/closeout/children/rsw-c4.json)

Verification passed:
- `ValidateChildReadiness.cs` for `RSW-C4`
- required count assertion
- required closeout JSON assertion
- delivery JSON assertion
- `git diff --check` on touched files

Note: current C4 launch directory has `start-prompt.md`; `launch-request.json`/`evidence.json` were not present yet while this child session is still running.