# Issue 12 review

Fixed point: `76f4c51c690aafbb7041f923603e30dccdd7ccfd`, the clean `main`
checkout at implementation start. The user explicitly authorized delivery on
`main`. Review covered the scoped working/index diff:

```bash
git diff 76f4c51 -- microsoft-agent-framework-work-package-pilot openspec/changes/recover-agent-framework-evidence
```

Two independent agents reviewed Standards and Spec in parallel. Concurrent wiki
changes and commit `44f9dbe` are unrelated and excluded from this review.

## Standards

Final Standards check: **0 remaining findings**.

Terminal cleanup uses the existing receipt helpers within the publication
transaction, resolves only the source attempt's open request, and records
correlated history. Replays cannot emit another resolution once the request is
resolved. No new standards breaches or actionable DRY/SOLID/KISS concerns.

## Spec

Final Spec check: **0 remaining findings**.

The cleanup targets the qualified source attempt, resolves only its open Human
Request, preserves the original result and request fields, and records
`HumanRequestResolved` within the terminal publication transaction. Replays cannot
duplicate resolution because the request is already resolved. The added scenario
matches this behavior. The earlier drift P1 is closed.

## Findings closed during review

| Finding | Correction | Direct verification |
| --- | --- | --- |
| Abandoned capture command outlived adapter/worker | Independent process-group supervision checks parent/owner liveness and command deadline | Adapter-kill test first failed; executing-worker kill and replacement now pass |
| P1: crash between drift observation and terminal save could allow another capture and draft | Persist capture result and terminal disposition in one transaction | Restored-repository restart test first published an unauthorized draft; now remains blocked at round 1 |
| Native preparation request remained open after completed work and draft | Resolve source request in the terminal transaction, retaining history | Real Codex/TUI test failed on open request, then passed; see native-red.txt and native-tests.txt |

## Refactoring pass

Inspected current diff and nearby worker/storage code for DRY, SOLID and KISS.
Extracted bounded capture orchestration into `CaptureEvidenceAsync`, shared fault
boundary reporting and terminal-report construction, and centralized the capture
limit. Reused existing receipt persistence helpers for request convergence.
Kept the pilot's JSON publication contract and PostgreSQL activity/history
mechanisms; no new service or generic workflow abstraction was introduced.

Total remaining findings: Standards **0**; Spec **0**.
