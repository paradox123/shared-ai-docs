# Agent Delivery Session Launcher Fixtures

`valid-ready` is a synthetic implementation-ready child handoff used for queue, dry-run and unsupported-provider verification.

`invalid-stale` intentionally disagrees across target id, verdict, handoff pointer and write-set so the launcher must produce `blocked` evidence instead of a successful queue or launch.

`launch-evidence` exercises the enforcement contract for already-produced launcher artifacts. It covers matching `queued`/`launched` evidence, missing or stale evidence, `manual_start_required`, `blocked`, `failed`, semantic-only `SessionId`, and explicit `legacy_reconstructed` historical evidence.

Run:

```sh
dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture tests/agent-delivery-session-launcher/fixtures/launch-evidence
```
