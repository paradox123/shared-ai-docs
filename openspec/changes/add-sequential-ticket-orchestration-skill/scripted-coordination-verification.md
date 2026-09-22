# Scripted coordination: implementation evidence

Date: 2026-09-21. Owning repository: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs`. Branch: `codex/scripted-ticket-coordination`; intended target `main`, explicitly confirmed by Daniel. Changes are local/uncommitted. This extends the current change and preserves the earlier event-protocol work. No push, merge, active batch migration or automation update was performed.

## Result

Routine coordination now uses executable local operations: prepare a correlated command, record its external outcome, create immutable sequenced worker results, consume a result with a next decision atomically, advance verified phases, manage capacity, and return compact decision context. Generated phase messages replace manual prompt headers. No external tool adapter or background daemon was added.

The instruction entrypoint fell from **1,929 to 821 words** (57.4% less). SKILL plus six references plus the new generated phase-message asset total **4,616 words**, versus **9,594** before this refactor (51.9% less). The new asset is included in this comparison; only its relevant phase is generated for a command. Counts use whitespace-separated words, not billed tokens. See [counts](evidence/scripted-coordination-2026-09-21/instruction-size.json). Actual runtime token savings are not measured.

## Expected and observed behavior

| Requirement | Expected | Actually observed |
| --- | --- | --- |
| Command preparation/recovery | Stable request and pending action before external execution; unknown send must not cause replacement | Public CLI blocks replacement, retains the same request and reconciles confirmed delivery; independent case B reproduces it |
| Worker report | Identity/sequence/hash bookkeeping occurs in code and preserves previous report | CLI copies result bytes, increments sequence and returns callback; editing original working result does not change the retained report |
| Event plus decision | Consume receipt and follow-up in one state revision, or neither | Wrong content decision leaves ledger unchanged; valid decision prepares a new request; old redelivery leaves that pending request unchanged |
| Capacity/isolation | Bound ticket/subagent grants, unique worker/branch/checkout, dependencies/conflicts | Over-capacity/conflicting dispatch produces no new packet/state; duplicate ownership rejected; parked work retains conflicts |
| Evidence decisions | Readiness alone never accepts work | Ready result remains implementing/inspect-evidence; matching content and explicit coordinator proof are required to proceed |
| Integration | Single holder and a grant bound to tested/current target | Second holder blocked; T1/T2 mismatch rejected; independent case C successfully prepares revalidation for T2 while retaining the holder |
| Delivery/cleanup | Report alone does not release capacity; verified delivery can unlock prerequisites before cleanup ends | Confirmation keeps reservations; verified mapping/closure/quiescence releases them; dependent ticket becomes eligible; done blocked until all cleanup steps recorded |
| Repair/cancellation | Scoped follow-up and release only with reconciled quiescence/cancellation | Repair commands count rounds and retain workflow gates; silent allowance reduction rejected; integration parking requires revoked grant and absent mutation |
| Managed-state integrity | Generic patches cannot bypass lifecycle; malformed/changed files do not silently advance | Legacy checkpoint rejects managed schema; stale writes preserve bytes; modified packet/result detected; malformed operations return bounded errors |
| Compact usable context | Caller need not read full history or invent IDs/sequences | Status contains current evidence/worker/action fields without history or full instruction; queued dependency blockers now appear directly |
| Compatibility | Existing mechanical/evidence and identity helpers retain behavior | All 27 pre-refactor tests remain green alongside 17 new public-CLI tests |

## Executed verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills-repo/skills/orchestrate-ticket-batch/scripts/tests -v`: **44 tests passed**, final run 15.195 seconds. New slices were observed failing for the missing behavior before implementation, then passing. Real subprocesses and temporary files are used; no mocked internal methods.
- `openspec validate add-sequential-ticket-orchestration-skill --strict`: passed.
- `git diff --check`: passed.
- Python AST parsing, phase-message JSON parsing, frontmatter name/description, 14 local Markdown links and the active Codex skill symlink: passed. The system skill validator's Python environment lacks PyYAML (established in the preceding stage); these explicit checks are the manual fallback, not a claim that quick_validate ran successfully.
- Full coherent reread of the shortened SKILL, all local references, metadata and generated phase texts; helper source inspected through EOF. Dynamic implementation/change-accepted references resolve to the active shared skill tree.
- Independent forward evaluation using the skill/docs and public CLI: [result](evidence/scripted-coordination-2026-09-21/forward/result.md), [exact calls and outputs](evidence/scripted-coordination-2026-09-21/forward/transcript.md). It completed the supplied dependency, uncertain-send/replay and moved-target scenarios without reading implementation or manually patching the ledger. External facts were explicit fixtures. Its sole usability observation—status suggested dispatch before showing a dependency blocker—was corrected and locked down by `test_status_identifies_blocked_dependencies_before_a_dispatch_attempt` before the final 44-test run. This was a forward application test, not formal code-review.

## Current content identity

The [source manifest](evidence/scripted-coordination-2026-09-21/source-manifest.json) hashes all current skill instructions, metadata, assets, helpers and tests listed in [source-files.json](evidence/scripted-coordination-2026-09-21/source-files.json). Manifest-file SHA-256:

`cf55358504873eee0c8853c39c613445d1888389a18b3291d8c2cfdb0076e578`

Verify listed contents with `batch_state.py verify --root skills-repo/skills/orchestrate-ticket-batch --manifest openspec/changes/add-sequential-ticket-orchestration-skill/evidence/scripted-coordination-2026-09-21/source-manifest.json` from the owning repository. The manifest is the content identity; current branch HEAD alone does not identify this uncommitted implementation.

## Limits and next phase

The directly executed surface is the local Python CLI and synthetic instruction workflow. No actual task messaging/idle wake, remote merge, external race or real cleanup was exercised. Evidence files record coordinator assertions; existence and hashes do not establish semantic correctness or external authority. Existing batches are not auto-migrated and require a separately verified adoption path. Participating workers need access to the packet/report filesystem.

Implementation and initial behavioral verification are complete. Technical completion is **awaiting contextual acceptance**, followed by change-accepted and its code-review workflow (task 8.6); no formal technical-completion claim or archival is made. Earlier completion reports cover their earlier revisions only.
