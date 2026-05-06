# DocWorkflow Dry Run: Child Index and S3 Handoff Operationalization

## Session Briefing

- Modus/Skill: `spec-orchestrator` temp index operationalization, then `child-spec-hardening` readiness simulation.
- Source of Truth: temp-folder copies under `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/`.
- Ziel: Verify that a new session can find Parent, Child Index, S3 Child Spec, and a persisted S3 Child Session Handoff without relying on chat context.
- Nicht-Ziele: No runtime implementation, no edits to original KI-fuer-KMU specs, no legacy backfill, no broad S4-S7 hardening.
- In Scope: Operational Child Index schema, S3 Handoff file, readiness verdict under the stricter handoff rules.
- Verification/Review: file existence check, Child Index/Handoff pointer scan, S3 required-gate section scan, manual consistency review against the updated DocWorkflow.
- Offene Entscheidungen: none for this temp dry run.

## Files Changed In Temp

1. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-child-specs-index.md`
   - Converted from a simple slice/status list into the operational Child Index schema.
   - Added `Session Handoff` column.
   - Linked S3 to `child-session-handoffs/s3-session-handoff.md`.
   - Kept S1/S2 as historical reference evidence without forced migration.

2. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/child-session-handoffs/s3-session-handoff.md`
   - Added persisted S3 Child Session Handoff.
   - Names Parent, Child, Child Index, handoff file, next skill, current verdict, allowed write-set, read-only files, verification limits, and fresh-session guidance.

No original KI-fuer-KMU spec was changed.

## Dry-Run Commands

```sh
rg -n "Session Handoff|NEEDS HARDENING|IMPLEMENTATION READY|READY WITH NON-BLOCKING|Next Action|Operational Child Index" \
  tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-child-specs-index.md \
  tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/child-session-handoffs/s3-session-handoff.md

rg -n "^## (Review Control Surface|Parent Scope Conformance|Decision Freeze Pack|Dependencies and Write-Set|Closeout Sync Targets|Child Session Handoff|Hardening Verdict)|Readiness Status|IMPLEMENTATION READY|READY WITH NON-BLOCKING|NEEDS HARDENING|NEEDS PARENT/ORCHESTRATOR SYNC" \
  tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md

test -f tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/child-session-handoffs/s3-session-handoff.md && printf 'handoff exists\n'
```

Results:

- The Child Index and S3 handoff both expose the S3 `Session Handoff` pointer and `NEEDS HARDENING` verdict.
- The handoff file exists.
- The S3 required-gate section scan returned no matching gate headings or hardening verdict in the S3 child spec.

## S3 Readiness Verdict

Final verdict: **NEEDS HARDENING**.

Why it is no longer `NEEDS PARENT/ORCHESTRATOR SYNC`:

- The temp Child Index now uses the operational schema.
- S3 has a persisted handoff file.
- The Child Index points to that handoff.
- The next action is explicit: run `child-spec-hardening` for S3 and do not implement.

Why it is still not `READY WITH NON-BLOCKING NOTES` or `IMPLEMENTATION READY`:

- S3 has strong domain content, canonical manifest examples, harness cases, and verification commands, but the spec still lacks the required Review Control Surface.
- It lacks a compact Parent Scope Conformance table.
- It lacks a Decision Freeze Pack.
- It lacks an explicit Dependencies and Write-Set section.
- It lacks Closeout Sync Targets.
- It lacks a documented final Hardening Verdict.
- The persisted handoff is a hardening-session start artifact, not implementation permission.

Under the new rules, `spec-change-delivery` must still refuse S3 implementation.

## Fresh-Session Test

A new hardening session can now start from only:

1. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-04-free-entry-v2-master-spec.md`
2. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-child-specs-index.md`
3. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/2026-05-05-free-entry-v2-s3-content-bundle-managed-ai-channel-spec.md`
4. `tmp/docworkflow-dry-run-ki-fuer-kmu/_specs/child-session-handoffs/s3-session-handoff.md`

That is enough to know:

- where the next child stands,
- that implementation is forbidden,
- which skill should run next,
- which files are writable,
- which files are read-only,
- which verification is allowed before hardening,
- what still blocks implementation readiness.

## Closeout Sync Implication

The dry run also confirms the closeout rule: after any future accepted S3 implementation, closeout must sync Parent Coverage, Child Index, Backlog/Re-entry, Evidence/OpenSpec status, and the next child handoff before S4/S5/S6/S7 becomes leading. If that sync cannot happen, the next handoff must be marked stale or blocked instead of silently reused.

## Mini-Retro

- Was wurde entschieden? Persisted handoff plus Child Index pointer is sufficient for a fresh hardening session, but not for implementation permission.
- Was wurde geaendert? Temp Child Index operationalized; S3 persisted handoff created; this dry-run report added.
- Was bleibt offen? A real S3 hardening pass must still add the missing control surfaces and final Hardening Verdict.
- Welche Evidenz/Verification fehlt? No runtime verification was run because S3 is not implementation-ready.
- Welche Skill-/Workflow-Reibung ist aufgefallen? The Handoff concept carries only if the Index points to a file and the file states its own non-permission status clearly.
- Session-/Kontextzustand: Good to start a fresh S3 hardening session from the four listed artifacts.
