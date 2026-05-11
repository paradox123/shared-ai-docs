# VADW-C1 Child Spec

## Goal

Run in a fresh visible Codex-App child session and create the first line of `target/output/count.txt` as exactly `1`.

## Review Control Surface

| Field | Value |
|---|---|
| Spec Variant | visible regression child delivery |
| Goldstandard Status | implementation-ready child spec |
| Goal | Write cumulative output `1\n` and persist child closeout evidence. |
| In Scope | `VADW-PR5`, visible launcher evidence, readiness gate, child closeout JSON. |
| Out of Scope | Parent orchestration, controller request publication, direct child launch from shell, mock runner usage. |
| Key Harness Cases | Missing count file is allowed for C1; final file must equal `1\n`. |
| Verification Commands | `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md --child VADW-C1 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/vadw-c1-handoff.md`; assert `target/output/count.txt` equals `1\n`. |
| Open Decisions | no open decisions |
| Readiness Status | IMPLEMENTATION READY |

## Parent Coverage

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| VADW-PR5 | C1 owns the first output line and cumulative text `1\n`. | preserves | Write exactly the first line. |
| VADW-PR10 | C1 must be launched by the visible controller. | preserves | Do not self-launch. |
| VADW-PR11 | C1 readiness is validated before request publication and again by launcher. | preserves | Keep handoff and Child Index aligned. |
| VADW-PR12 | C1 contributes closeout and output evidence. | preserves | Write child closeout JSON after target output is correct. |

## In Scope

- Create `target/output/count.txt` with exact UTF-8 text `1\n`.
- Create `delivery-evidence/vadw-c1/` evidence if useful to document the action.
- Write `closeout/vadw-c1-closeout.json` with `final_status: ran-target` and `closeout_status: closed`.

## Out of Scope

- Do not edit orchestration pack, parent handoff, child specs, child handoffs, controller requests, or controller responses.
- Do not use `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
- Do not launch other children or simulate their work.

## Decision Freeze Pack

- Output file: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/target/output/count.txt`.
- Required output after C1: `1\n`.
- Closeout file: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/closeout/vadw-c1-closeout.json`.

## Acceptance Criteria

- `target/output/count.txt` exists and equals `1\n`.
- C1 closeout JSON exists with `target_id: VADW-C1`, `final_status: ran-target`, and `closeout_status: closed`.
- No parent-owned or controller-owned file is changed by C1.

## Verification Commands

```sh
dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md --child VADW-C1 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/vadw-c1-handoff.md
python3 - <<'PY'
from pathlib import Path
p = Path('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/target/output/count.txt')
assert p.read_text() == '1\n'
PY
git diff --check
```

## Dependencies and Write-Set

Dependency: parent request publication.
Allowed write-set: `target/output/count.txt`; `delivery-evidence/vadw-c1/**`; `closeout/vadw-c1-closeout.json`.

## Closeout Sync Targets

Child closeout JSON and controller response for `VADW-C1`.
