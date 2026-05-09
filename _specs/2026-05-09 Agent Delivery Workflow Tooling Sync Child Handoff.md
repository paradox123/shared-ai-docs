**Date:** 2026-05-09
**Status:** 🟢 Accepted
**Scope:** .NET 10 tool for generating and synchronizing Child Session Handoff files from Child Index rows.

---

SessionId: sync-child-handoff-tooling

## Review Control Surface

- Spec-Variante: Implementation-ready tool delivery spec.
- Goldstandard Status: accepted with local fixture evidence and archived OpenSpec ledger.
- Ziel: Create `skills-repo/tools/SyncChildHandoff.cs` so Child Session Handoff generation, stale detection and controlled-field synchronization move out of long skill prose.
- In Scope: read one exact operational Child Index row; generate a missing handoff; check or synchronize stale controlled fields; preserve marked manual notes; support `--check`, `--dry-run` and explicit `--write`; emit deterministic text or JSON findings; provide fixtures for generate/check/dry-run/stale-verdict/preserve-notes.
- Out of Scope: starting agent sessions; `spec-orchestrator/SKILL.md` integration; editing real existing handoffs except synthetic fixtures; `WorkflowDoctor`; assigning implementation readiness beyond index/handoff sync.
- Wichtigste Test-/Harness-Cases: `HANDOFF-GENERATE-MISSING`, `HANDOFF-CHECK-CURRENT`, `HANDOFF-SYNC-STALE-VERDICT`, `HANDOFF-DRY-RUN-NO-WRITE`, `HANDOFF-PRESERVE-NOTES`, `HANDOFF-BLOCK-APPROX-WRITESET`.
- Wichtigste Verification Commands: `dotnet run skills-repo/tools/SyncChildHandoff.cs -- --help`; fixture generate/check/dry-run/stale/preserve/approx-write-set commands under `tests/sync-child-handoff/fixtures/`; post-archive `openspec validate docworkflow-agent-delivery-testsuite --strict`; `git diff --check`.
- Offene Entscheidungen: none.
- Readiness Status: ACCEPTED; OpenSpec archived on 2026-05-09.

## Goal

Make Child Session Handoff creation boring and repeatable. Agents should not manually retype template fields from the Child Index, and a stale handoff must produce deterministic findings before any downstream hardening, delivery or closeout session treats it as current.

## Source Of Truth

- Child Session Handoff template and staleness rule: `docs/doc-workflow.md`, section `Child Session Handoff Template (kurz)`.
- Exact operational Child Index columns: `docs/doc-workflow.md`, section `Child Index als operative Steuerzentrale`.
- Existing parser/validator behavior: `skills-repo/tools/ValidateChildReadiness.cs`.
- Downstream launcher field expectations: `skills-repo/tools/AgentDeliverySessionLauncher.cs`.
- Existing handoff examples: `_specs/child-session-handoffs/*.md`, read-only for this change.

## In Scope

- Add `skills-repo/tools/SyncChildHandoff.cs` as a .NET 10 file-based app.
- Add synthetic fixtures under `tests/sync-child-handoff/fixtures/`.
- Add one OpenSpec change for this delivery.
- Update this source spec status/history and evidence after implementation.

## Out Of Scope

- No Agent Delivery session launch or queue creation.
- No `spec-orchestrator` skill integration or prose edits.
- No changes under unrelated Spec 2 / Spec 3 artifacts.
- No mutation of real `_specs/child-session-handoffs/*.md`; only fixture copies may be written.
- No broad Markdown formatter and no `WorkflowDoctor`.

## CLI Contract

```sh
dotnet run skills-repo/tools/SyncChildHandoff.cs -- \
  --index <child-index-or-pack.md> \
  --child <stable-child-id> \
  --out <handoff.md> \
  [--target-repo <absolute-path>] \
  [--parent <parent.md>] \
  [--timestamp <yyyy-MM-dd>] \
  [--check | --dry-run | --write] \
  [--format text|json] \
  [--allow-non-ready] \
  [--allow-approx-write-set]
```

Mode semantics:

| Mode | Exit | Filesystem behavior |
|---|---:|---|
| `--check` | `0` when the expected handoff already matches; `1` on drift or blocking findings; `2` on usage/input errors | never writes |
| `--dry-run` | `0` when a render is possible and no blocking finding exists; `1` on blocking finding; `2` on usage/input errors | never writes; prints the proposed handoff |
| `--write` | `0` after creating/updating the handoff when no blocking finding exists; `1` on blocking finding; `2` on usage/input errors | writes only `--out` |

Exactly one mode is required. `--target-repo` defaults to the current working directory and is rendered as an absolute path. `--timestamp` defaults to the current UTC date for `--write` and `--dry-run`, but `--check` accepts an existing handoff timestamp unless a timestamp is explicitly supplied. Fixtures may pass `--timestamp` for deterministic output. `--format` defaults to `text`.

## Controlled Field Contract

The tool reads the exact operational Child Index table with these required columns:

`Child`, `Child Spec`, `Parent Coverage`, `Readiness / Hardening Verdict`, `Session Handoff`, `OpenSpec / Ledger`, `Dependencies`, `Allowed Write-Set`, `Verification`, `Evidence / Closeout`, `Backlog / Re-entry`, `Next Action`.

The generated `## Child Session Handoff` block is fully controlled for these bullets:

- `Parent`
- `Stable Child ID`
- `Child`
- `Child Spec`
- `Child Index / Queue`
- `Handoff File`
- `Target Repository / Working Directory`
- `Codex Session / Log`
- `Session Evidence`
- `Handoff Timestamp`
- `Naechster Modus/Skill`
- `Aktueller Verdict`
- `Scope Summary`
- `Non-Goals`
- `Allowed Write-Set`
- `Shared / Read-only Files`
- `Verification Lifecycle`
- `Evidence / OpenSpec`
- `Retained Evidence`
- `Offene Blocker oder non-blocking Notes`
- `Fresh Session empfohlen`

Mapping rules:

| Handoff field | Source |
|---|---|
| `Parent` | `--parent` when provided, otherwise `unknown` |
| `Stable Child ID`, `Child` | Child Index `Child` |
| `Child Spec` | Child Index `Child Spec` |
| `Child Index / Queue` | `--index` path plus `section Child Index` |
| `Handoff File` | `--out` path |
| `Target Repository / Working Directory` | `--target-repo` or current working directory |
| `Codex Session / Log`, `Session Evidence` | `not created by SyncChildHandoff` |
| `Handoff Timestamp` | `--timestamp`; otherwise current UTC date for write/dry-run, or the existing handoff timestamp during check |
| `Naechster Modus/Skill` | Child Index `Next Action` |
| `Aktueller Verdict` | Child Index `Readiness / Hardening Verdict` |
| `Scope Summary` | `Parent Coverage: <Parent Coverage>. Dependencies: <Dependencies>.` |
| `Non-Goals` | `No agent session launch; no edits outside the allowed write-set.` |
| `Allowed Write-Set` | Child Index `Allowed Write-Set` |
| `Shared / Read-only Files` | `docs/doc-workflow.md`; `skills-repo/tools/ValidateChildReadiness.cs`; `skills-repo/tools/AgentDeliverySessionLauncher.cs` |
| `Verification Lifecycle` | rendered sub-bullets where `Delivery Gate` comes from Child Index `Verification`; other lifecycle slots explicitly say `not recorded by SyncChildHandoff` |
| `Evidence / OpenSpec` | Child Index `OpenSpec / Ledger`; Child Index `Evidence / Closeout` |
| `Retained Evidence` | Child Index `Evidence / Closeout` |
| `Offene Blocker oder non-blocking Notes` | Child Index `Backlog / Re-entry` |
| `Fresh Session empfohlen` | `Yes` when `Next Action` contains `spec-change-delivery`, otherwise `Review next action` |

All controlled fields are overwritten on `--write`. Manual edits inside the controlled block are intentionally not preserved.

## Manual Preservation Contract

Manual content is preserved only inside an explicit section named exactly:

```md
## Notes Preserved By Sync
```

The tool preserves that section and all following text verbatim when rewriting `--out`. If the section is absent, the rewritten file contains only the generated controlled handoff block and a trailing newline. This keeps preservation deterministic and prevents stale manual edits inside controlled bullets from masquerading as current workflow state.

## Findings And Drift Contract

The tool emits deterministic findings with these fields in JSON mode:

```json
{
  "status": "current|would_create|would_update|written|blocked|error",
  "child": "DWT-S3",
  "handoff_path": "...",
  "findings": [
    { "severity": "info|warning|error", "code": "FIELD_DRIFT", "field": "Aktueller Verdict", "message": "..." }
  ]
}
```

Required finding codes:

- `HANDOFF_MISSING`
- `FIELD_DRIFT`
- `INDEX_POINTER_MISMATCH`
- `APPROX_WRITE_SET`
- `COMPRESSED_INDEX`
- `CHILD_NOT_FOUND`
- `USAGE_ERROR`

Drift is reported when the existing handoff disagrees with the Child Index or controlled CLI inputs for child id, child spec, child index path, handoff file, target repository, current verdict, allowed write-set, verification, evidence/OpenSpec or next action.

Approximate write-sets are blocking by default when they contain `voraussichtlich`, `likely`, `probably`, `expected`, `TBD`, `to be decided`, `as needed`, `related files`, `and related`, `etc.` or lack a concrete path/list shape. `--allow-approx-write-set` downgrades this finding to a warning for non-delivery hardening handoffs.

## Acceptance Criteria

1. Missing handoff can be generated from a valid Child Index row with `--write`.
2. `--check` exits `0` for a current fixture and exits `1` with `FIELD_DRIFT` for a stale verdict fixture.
3. `--dry-run` prints the proposed handoff and leaves the target file unchanged.
4. `--write` synchronizes controlled fields and preserves `## Notes Preserved By Sync` verbatim.
5. Approximate write-sets produce a blocking `APPROX_WRITE_SET` finding unless `--allow-approx-write-set` is passed.
6. The generated handoff includes the fields consumed by `AgentDeliverySessionLauncher.cs` and checked by `ValidateChildReadiness.cs`: child id, Child Index / Queue, target repository, next skill, verdict, allowed write-set, verification and evidence/OpenSpec.

## Verification Commands

Execution context: run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs` on macOS/zsh unless a command explicitly changes directory. Tool verification uses source-controlled synthetic fixtures only.

Risk-based preflight:

```sh
dotnet run skills-repo/tools/SyncChildHandoff.cs -- --help
```

Gate verification:

```sh
rm -f tests/sync-child-handoff/fixtures/generated/missing-session-handoff.md
dotnet run skills-repo/tools/SyncChildHandoff.cs -- \
  --index tests/sync-child-handoff/fixtures/generated/control-index.md \
  --child SYNC-1 \
  --out tests/sync-child-handoff/fixtures/generated/missing-session-handoff.md \
  --target-repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --parent tests/sync-child-handoff/fixtures/generated/parent.md \
  --timestamp 2026-05-09 \
  --write \
  --format json

dotnet run skills-repo/tools/SyncChildHandoff.cs -- \
  --index tests/sync-child-handoff/fixtures/current/control-index.md \
  --child SYNC-1 \
  --out tests/sync-child-handoff/fixtures/current/child-session-handoff.md \
  --target-repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --parent tests/sync-child-handoff/fixtures/current/parent.md \
  --timestamp 2026-05-09 \
  --check \
  --format json

dotnet run skills-repo/tools/SyncChildHandoff.cs -- \
  --index tests/sync-child-handoff/fixtures/stale-verdict/control-index.md \
  --child SYNC-1 \
  --out tests/sync-child-handoff/fixtures/stale-verdict/child-session-handoff.md \
  --target-repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --parent tests/sync-child-handoff/fixtures/stale-verdict/parent.md \
  --timestamp 2026-05-09 \
  --check \
  --format json

before_sha="$(shasum -a 256 tests/sync-child-handoff/fixtures/dry-run/child-session-handoff.md | awk '{print $1}')"
dotnet run skills-repo/tools/SyncChildHandoff.cs -- \
  --index tests/sync-child-handoff/fixtures/dry-run/control-index.md \
  --child SYNC-1 \
  --out tests/sync-child-handoff/fixtures/dry-run/child-session-handoff.md \
  --target-repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --parent tests/sync-child-handoff/fixtures/dry-run/parent.md \
  --timestamp 2026-05-09 \
  --dry-run
after_sha="$(shasum -a 256 tests/sync-child-handoff/fixtures/dry-run/child-session-handoff.md | awk '{print $1}')"
test "$before_sha" = "$after_sha"

dotnet run skills-repo/tools/SyncChildHandoff.cs -- \
  --index tests/sync-child-handoff/fixtures/preserve-notes/control-index.md \
  --child SYNC-1 \
  --out tests/sync-child-handoff/fixtures/preserve-notes/child-session-handoff.md \
  --target-repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --parent tests/sync-child-handoff/fixtures/preserve-notes/parent.md \
  --timestamp 2026-05-09 \
  --write
rg -n "Manual note that must survive sync" tests/sync-child-handoff/fixtures/preserve-notes/child-session-handoff.md

dotnet run skills-repo/tools/SyncChildHandoff.cs -- \
  --index tests/sync-child-handoff/fixtures/approx-write-set/control-index.md \
  --child SYNC-1 \
  --out tests/sync-child-handoff/fixtures/approx-write-set/child-session-handoff.md \
  --target-repo /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs \
  --parent tests/sync-child-handoff/fixtures/approx-write-set/parent.md \
  --timestamp 2026-05-09 \
  --check \
  --format json

openspec validate agent-delivery-sync-child-handoff --strict
git diff --check
```

Expected outcomes:

- The stale-verdict command exits `1` and prints `FIELD_DRIFT`.
- The approximate-write-set command exits `1` and prints `APPROX_WRITE_SET`.
- All other commands exit `0`.
- No command edits real handoffs under `_specs/child-session-handoffs/`.
- After OpenSpec archive, replay the canonical spec with `openspec validate docworkflow-agent-delivery-testsuite --strict`; the active-change validation above remains historical delivery evidence.

## DoR / DoD

Definition of Ready:

- This spec has no open blocking `[MISSING]` or `[DECISION]` markers.
- The tool behavior, controlled fields, manual preservation policy, exit codes, fixture set and verification commands are concrete.
- Write-set is limited to this spec, one OpenSpec change, `skills-repo/tools/SyncChildHandoff.cs`, and `tests/sync-child-handoff/fixtures/**`.

Definition of Done:

- OpenSpec change validates strictly.
- `SyncChildHandoff.cs` implements the CLI contract and findings contract.
- All gate verification commands are run and recorded as evidence.
- Source spec status/history and OpenSpec task state are synchronized.

## Closeout Evidence

| Check | Status | Evidence |
|---|---|---|
| `dotnet run skills-repo/tools/SyncChildHandoff.cs -- --help` | ran/pass | Exit `0`; usage text printed. |
| Missing handoff generation fixture | ran/pass | Exit `0`; status `written`; `HANDOFF_MISSING` warning; fixture handoff created. |
| Current handoff check fixture | ran/pass | Exit `0`; status `current`; no findings. |
| Stale verdict fixture | ran/pass expected negative | Exit `1`; `FIELD_DRIFT` for `Aktueller Verdict`. |
| Dry-run no-write fixture | ran/pass | SHA before/after matched; proposed `IMPLEMENTATION READY` handoff printed. |
| Preserve-notes fixture | ran/pass | Exit `0`; `Manual note that must survive sync` remained present. |
| Approximate write-set fixture | ran/pass expected negative | Exit `1`; `APPROX_WRITE_SET` findings. |
| `openspec validate agent-delivery-sync-child-handoff --strict` | ran/pass before archive | Active change valid. |
| `openspec archive -y agent-delivery-sync-child-handoff` | ran/pass | Archived as `openspec/changes/archive/2026-05-09-agent-delivery-sync-child-handoff/`; canonical spec updated. |
| `openspec validate docworkflow-agent-delivery-testsuite --strict` | ran/pass after archive | Canonical spec valid. |
| `git diff --check` | ran/pass | No whitespace errors. |

Documentation sync result:

- `rg` found no public docs under `docs/` or `README.md` that require a SyncChildHandoff update.
- Hits outside the target spec/OpenSpec are other active/draft workflow-tooling specs that intentionally remain out of this closeout scope.
- No real Child Session Handoff or `spec-orchestrator/SKILL.md` integration was changed.

## Mini-Retro

- Was wurde entschieden? Manual prose is preserved only after `## Notes Preserved By Sync`; controlled handoff bullets are always regenerated.
- Was wurde geaendert? The draft is hardened into an implementation-ready tool spec with CLI, field mapping, findings, fixture and verification contracts.
- Was bleibt offen? Later skill integration may call this tool, but that is intentionally out of scope for this change.
- Welche Evidenz/Verification fehlt? No missing evidence for this tool slice; later skill integration remains out of scope.
- Session-/Kontextzustand: Change accepted and closed; future skill integration should be a separate accepted change.

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |
| 2026-05-09 | sync-child-handoff-tooling | Hardened to implementation-ready tool spec with controlled-field, preservation, fixture and verification contracts. |
| 2026-05-09 | sync-child-handoff-tooling | Implemented `SyncChildHandoff.cs`, fixtures, OpenSpec ledger and local verification evidence. |
| 2026-05-09 | sync-child-handoff-tooling | Hardened default timestamp handling so `--check` does not create daily timestamp-only drift. |
| 2026-05-09 | sync-child-handoff-tooling | Accepted change, archived OpenSpec as `2026-05-09-agent-delivery-sync-child-handoff`, replayed canonical validation and closed the spec. |
