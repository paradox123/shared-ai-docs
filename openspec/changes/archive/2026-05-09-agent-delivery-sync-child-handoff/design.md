# Design

## Scope Boundary

`SyncChildHandoff.cs` is a local synchronization helper, not a readiness validator and not a launcher. It writes only the requested `--out` handoff path and never edits the Child Index. Existing real handoffs under `_specs/child-session-handoffs/` are read-only for this delivery; synthetic fixtures exercise writes.

## Rendering Model

The tool renders the entire controlled `## Child Session Handoff` block from:

- the exact operational Child Index row selected by `--child`,
- controlled CLI inputs (`--out`, `--target-repo`, `--parent`, `--timestamp`),
- fixed workflow defaults for launcher/session fields that this tool does not create.

Controlled bullets are overwritten wholesale. This keeps synchronization deterministic and avoids field-by-field Markdown surgery. `--check` does not create daily timestamp-only drift: when no `--timestamp` is supplied and an existing handoff has `Handoff Timestamp`, that timestamp is accepted for comparison.

## Preservation Model

The only manual preservation zone is `## Notes Preserved By Sync` and everything after it. On rewrite, the generated block is written first, then the preserved section is appended verbatim. Manual edits inside controlled bullets are treated as stale controlled state and are not preserved.

## Findings Model

The tool compares an existing handoff's controlled bullets to the freshly rendered expected bullets. Differences produce `FIELD_DRIFT` findings. Missing handoffs produce `HANDOFF_MISSING`. Child Index pointer mismatch, compressed/aliased table headers, missing child rows and approximate write-sets produce named findings.

`--check` reports findings without writing. `--dry-run` prints the expected file without writing. `--write` creates or replaces only `--out` when no blocking findings exist other than missing/stale controlled content.

## Compatibility

The generated handoff includes the fields consumed by `AgentDeliverySessionLauncher.cs` and `ValidateChildReadiness.cs`: child id, Child Index / Queue, target repository, next skill, verdict, allowed write-set, verification and evidence/OpenSpec.
