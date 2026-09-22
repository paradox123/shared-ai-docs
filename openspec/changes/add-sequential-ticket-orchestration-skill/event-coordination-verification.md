# Worker-driven coordination: initial verification

Date: 2026-09-21. Scope: the shared `orchestrate-ticket-batch` skill, its existing standard-library helper and this active OpenSpec change. Basis: the user's approved improvements following the analysis of Codex task `01a0bfe9-b8b0-7ad3-8e4c-6ac52195daa7` (NCG audit tickets 11–14). This records implementation readiness, not acceptance-triggered technical closeout.

## Requirement coverage

| Expected behavior | Observed evidence | Result / limit |
| --- | --- | --- |
| Worker phase reports replace the default repeated model status loop when usable background continuation exists | SKILL, worker-events and all message templates specify callback-driven continuation; independent cases A/D end the turn after actionable work | Pass at instruction/scenario level; live idle wake is not verified |
| Missing callbacks and interruptions preserve autonomous continuation without inventing scheduling authority | Modes explicitly separate verified callback wake, authorized heartbeat and bounded active wait; cases B/C/D retain pending actions and honor automation restrictions | Pass at instruction/scenario level |
| Duplicate, stale, foreign, conflicting and missing-sequence events cannot mechanically authorize a repeated action | Six new public-CLI tests cover classification, malformed input, no writes and no payload disclosure; cases A/B/G also invoke the helper on synthetic JSON | Pass; phase legality, sender identity and evidence remain coordinator checks |
| Receipt and pending action survive interruption | Existing revision-checked checkpoint helper is retained; instructions store an immutable event path plus SHA-256 together with pending action, then reconcile uncertain dispatch | Existing helper regression tests pass; no real transport or crash-injection test of a complete batch |
| Readiness does not replace acceptance or integration checks | Case A requests missing expected/actual evidence; case E requires revalidation against moved target T2 and keeps a single integration reservation | Pass at scenario level |
| Early complete examples and scoped repairs prevent uncontrolled broad rework | Packets require representative cases for large repetitive work; repair template binds finding, affected scope, revision and evidence delta; case F reassesses method before another equivalent repair | Pass at instruction/scenario level; runtime savings not measured |
| Nested delegation is bounded separately from ticket slots | Default total active subagent allowance is three; per-worker reservations count nested agents; case F rejects additional parallel reviewers and preserves required sequential reviews | Pass at scenario level |
| Compact results and milestone-only usage avoid new monitoring overhead | Event/result templates link detailed evidence; usage records use available counter deltas, declare missing counters and prohibit discovery/polling solely for usage; case F does not invent counters | Pass at instruction/scenario level |
| Actual role/model selection is visible | Start-of-batch instructions record requested and actual settings and disclose mismatch once, preserving explicit model authorization | Source coherence verified; no live batch exercised the role profile |

## Executed checks

From the shared-ai-docs repository root:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills-repo/skills/orchestrate-ticket-batch/scripts/tests -v`: all **27 tests passed** (21 existing tests plus 6 event-classification tests). New behavior was developed in failing/passing public-CLI slices.
- `openspec validate add-sequential-ticket-orchestration-skill --strict`: passed.
- `git diff --check`: passed.
- System `skill-creator/scripts/quick_validate.py`: unavailable because its Python environment lacks PyYAML. Manual fallback checked required name/description metadata, all 20 local Markdown links, and the active skill symlink. Two intentional resolved-path placeholders in message templates are not file links and must be replaced on dispatch.
- Coherent reread: edited SKILL, agent metadata, local references, helper and tests. Existing acceptance, explicit-target, authority, integration and cleanup boundaries remain in place.
- Independent forward evaluation: seven isolated planning cases, with no live task, messaging, automation, Git or network mutations. See [full scenario results](evidence/worker-events-2026-09-21/forward-scenarios.md); synthetic JSON inputs and classifier outputs are retained alongside that report. This is instruction evaluation, not the separate code-review completion workflow.

The active `/Users/dh/.codex/skills/orchestrate-ticket-batch` link resolves to this edited skill directory. No installation or restart was necessary for future skill reads.

## Runtime limits and closeout

No live batch was started or migrated, no existing automation was changed, and callback delivery to an idle coordinator was not experimentally established. A callable messaging tool alone does not prove that behavior. The skill therefore requires an evidenced usable continuation mode, including an explicit active-wait fallback if no background continuation is available. It does not promise exactly-once transport or a measured token reduction.

Approval of the proposed changes authorized this implementation. Acceptance of the implemented extension and the subsequent `change-accepted` / `code-review` workflow remain separate (task 8.6). Earlier completion records cover prior revisions only. Changes are local and uncommitted.
