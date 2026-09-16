# Acceptance evidence — sequential ticket orchestration skill

Verified 2026-09-16. Scope: new shared `orchestrate-ticket-batch` skill, its metadata recovery helper, prompt/state references, catalog entry and targeted Codex discovery link. Product code, vendor implement skill and active orchestration automations were not changed. Existing unrelated shared-ai-docs changes were preserved.

## Requirement outcomes

| Requirement | Expected | Observed evidence |
| --- | --- | --- |
| Short invocation and finite scope | Skill plus repository/tickets selects sequential lifecycle | Independent fixture-only invocation for acme/widget #8–#10 preserved the exact queue and dependencies, dispatched no extra tickets and applied the default acceptance/delivery gates |
| Lost creation response / omitted listing | Recover existing worker, never duplicate | Forward exercise rejected wrong-repository candidate A and adopted directly verified B; pending creation reconciled rather than retried |
| Candidate metadata behavior | Bounded results, ambiguity and errors remain explicit | Eight subprocess CLI tests pass under macOS `/usr/bin/python3` 3.9.6; no writes to input index; at most ten emitted candidates |
| Real metadata recovery | Find the known missing #4 task without user copying a link | Read-only helper returned `01a0a948-3b72-7612-b191-fd789bc582f7` for the exact recorded title; identity had already been verified through read_thread in this diagnosis |
| Critical verification | Test counts alone cannot grant acceptance | Forward exercise requested separate critical verification for “45 tests green” with no artifact paths |
| Acceptance identity | Later behavior change invalidates old evidence | Forward exercise refused H1 evidence for changed PR head H2 and required fresh verification |
| Approval rejection | Preserve PR and report exact blocked action | Forward exercise retained approval-required state and did not route merge through the coordinator or start the next ticket |
| Sequential delivery | Advance only after remote confirmation | Forward exercise kept #9/#10 queued until remote merge, included accepted contents and issue closure were verified; next action starts #9 in the same run |
| Discovery and metadata | Canonical shared source available to Codex | `~/.codex/skills/orchestrate-ticket-batch` resolves to canonical shared directory; frontmatter, name, reference targets, UI text and default prompt checked |

## Helper red-green evidence

Public seam: subprocess CLI with temporary metadata index and JSON/exit output. Observed failures before fixes:

- Exact-title recent candidate returned not-found; implemented candidate selection.
- Two distinct candidates returned candidate; implemented ID deduplication and explicit ambiguity.
- Malformed matching timestamp returned an unstructured failure; implemented bounded error output.
- Review regression: missing/null/integer title fields returned not-found; implemented pre-filter title validation.

Final eight tests also cover nanosecond timestamps, activity after the dispatch date, explicit timezone offsets, repeated rows, no exact recent match, output capping and rejection of client IDs. Every fixture asserts unchanged input bytes.

Reproduce:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s skills-repo/skills/orchestrate-ticket-batch/scripts/tests -v
OPENSPEC_TELEMETRY=0 openspec validate add-sequential-ticket-orchestration-skill --strict
```

## Standards

One finding: worker template unconditionally selected an isolated worktree/codex branch despite an explicit user checkout/branch override. Corrected template to use resolved user-respecting values. Independent narrow re-review confirmed resolution. No remaining actionable standards/smell findings.

## Spec

One finding: invalid title metadata was skipped as a nonmatch. Added a behavior regression, observed failure and corrected validation. Independent narrow re-review confirmed resolution. No remaining actionable spec findings.

Totals: Standards 0 unresolved (1 fixed); Spec 0 unresolved (1 fixed).

## Coherence and limits

Read SKILL.md, both directly linked references, script, CLI tests and agents/openai.yaml fully after changes. Checked scope, templates, state transitions and recovery/approval rules for consistency. No duplicate lifecycle embedded in new runtime configuration. Refactoring review kept the helper narrowly read-only and reused implement, automation and deeper session-forensics owners rather than duplicating their workflows.

OpenSpec strict validation and scoped whitespace checks pass. The bundled quick_validate.py could not run because the default Python lacks PyYAML. Required frontmatter, supported keys, folder/name agreement, referenced files, absence of unfinished SKILL scaffold markers and UI metadata were checked separately; no unrelated Python environment was modified.

The forward exercise used hypothetical artifacts and produced decisions only; it does not establish live scheduler timing, end-to-end GitHub delivery or future approval outcomes. No extra production batch was launched. The active OpenSpec change records this delivered skill and these limits; it has not been archived.

## Evidence ownership

New general-purpose skill, not an expansion of implement or build-codex-automations. The user's initial orchestration request and task `01a0a8fd-8d65-74b1-aae1-95bcd191fab3`, plus verified workers #3 and #4, established the repeated failures. Current recovery history was already present in the conversation; a bounded latest-task read additionally confirmed progression to #6. No broad retrospective cursor or automation memory was advanced.
