# Independent DRY review — initial receipt

- Reviewer canonical agent ID: `/root/live_completion/dry_reviewer`.
- Recorded UTC: `2026-09-20T08:18:42.402595+00:00`.
- Repository: `/private/var/folders/wb/rpvbdznn4g3f4s2k4nwbn24c0000gn/T/completion-live-proof-sxwalzix`.
- Fixed base commit: `53f6d11f1a1c9fc1b7fd48b6250ff80aa2f5e26b` (resolved with git).
- Supplied candidate/content identity: `c9657ec045a79c7ad1dfe90bc17c363d79a7ac1084385caa54ea70e2845d4ad3`.
- Write set: `ticket_export.py`, `test_ticket_export.py`, both untracked additions.
- Directly calculated SHA-256 hashes match every manifest entry and the corresponding pre-review snapshot byte for byte.
- Scope: DRY only; no source/shared-repository edits, no other reviewers launched and no delivery.

## Verified content identity

| Path | SHA-256 |
| --- | --- |
| `ticket_export.py` | `1882b09dc5832eebdab623b6c011bd9fdf2e5bf26f1a0200b5d627fdd7628f99` |
| `test_ticket_export.py` | `bc23ad577ab7c5ce3d032a2e1f311d1e7b145233e56d9037f597715ae834ce6a` |
| `REQUIREMENTS.md` | `123aa6dbdb976557bd4d6970b27e0b04672a63b516b4cf2822987c6b5e86fc67` |
| `AGENTS.md` | `41a6c98e5bf1b9ea44299771456d6ccd27f3febf552f97a31f5ed5f618dacda2` |
| `README.md` | `61b5dc2cd5e567defe82cbeae6d2b876fedad81d2ae76ede990d6f0e6a84cdee` |

## Inspected paths and evidence

Read actual current `README.md`, `AGENTS.md`, `REQUIREMENTS.md`, both complete Python files with line numbers, `evidence/candidate-pre-review.json`, `evidence/candidate-pre-review.diff`, `evidence/requirements-pre-review.md`, `evidence/06-requirements-suite.json`, and `evidence/07-safe-import.json`. Compared all five manifest files with `evidence/snapshots/pre-review/`. Read the shared `skills-repo/skills/code-review/SKILL.md` and `references/review-criteria.md` at their absolute shared-repo paths. The actual captured command output, stderr, exit codes and UTC times are in [dry-commands.json](dry-commands.json).

I inspected the CLI test assertions, including normalized `done`/`todo` matching, numeric ordering, quoted multiline titles, empty output and unchanged input bytes. The existing six-test CLI run and safe-import process evidence match the current source hashes; I reused those results without rerunning their commands. No newly discovered behavior defect reopens requirements coverage.

## Coverage

- Repeated production domain decisions: compared both serializer paths for normalization, selection, field projection and ordering; finding DRY-001 below.
- Repeated test knowledge: the shared CLI subprocess harness already owns process execution and input-file immutability checking. Literal expected values and the JSON/CSV representations are independent behavioral assertions; no consolidation finding.
- Format-specific output rules: CSV header/quoting and JSON encoding have distinct reasons to change; no consolidation finding.
- Assigned standard covered: repeated domain decisions, consolidated only where meaning and change reasons agree. SOLID dependency/entrypoint concerns and KISS naming/structure remain assigned to their later reviewers.

## Binding rule violations

None. Current R1–R4 evidence passes. The structural observation below is a design heuristic with concrete maintenance benefit, not a claim that the current formats disagree.

## Heuristic finding

### DRY-001 — Share the format-independent export row preparation

- Priority: P2 maintenance finding.
- File/lines: `ticket_export.py:9–13` and `ticket_export.py:22–26`.
- Criterion: shared DRY review criterion, repeated domain decisions with the same reason to change.
- Observation: `export_csv` and `export_json` repeat the identical loop, normalized status predicate, title/status normalization, three-field projection and numeric sorting. These are the same domain policy, explicitly shared by both formats in R1/R2. They are independent of the serializer.
- Suggested repair: prepare the normalized, selected, sorted rows once in a small shared preparation function or in the CLI before dispatch, then keep CSV and JSON serialization separate. Normalize each ticket's status once within that shared preparation path so matching and emitted status use the same value. Preserve the public CLI and existing serializer behavior; no generic exporter framework is needed.
- Expected benefit: a change to status handling, selected fields or ordering has one implementation point, preserving the required format parity. The recorded pre-review normalization repair already required the same edit in both existing paths.
- Material risk if left: a future fix applied to only one serializer silently creates different selected values/order across formats and can violate R2. This is a maintenance risk, not an observed current behavioral failure.
- Repair risk and verification: moving selection/sorting must preserve empty results, numeric ordering, title/status normalization and CSV CRLF handling. The existing CLI tests exercise those seams; rerun affected tests after the repair.

## Outcome

One actionable DRY heuristic finding (DRY-001); no binding violations and no additional findings. Return the old-to-new source delta, current hashes and affected CLI evidence to this same reviewer after repair so the affected coverage can be closed without repeating unrelated checks.
