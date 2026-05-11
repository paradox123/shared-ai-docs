# VADW-C3 Child Spec

## Goal

Run in a fresh visible Codex-App child session and create the third cumulative output state: `1\n2\n3\n`.

## Review Control Surface

| Field | Value |
|---|---|
| Spec Variant | visible regression child delivery |
| Goldstandard Status | implementation-ready child spec |
| Goal | Preserve C2 output and add line `3`. |
| In Scope | `VADW-PR7`, visible launcher evidence, readiness gate, child closeout JSON. |
| Out of Scope | Parent orchestration, controller request publication, direct child launch from shell, mock runner usage. |
| Key Harness Cases | Predecessor text must be `1\n2\n`; final file must equal `1\n2\n3\n`. |
| Verification Commands | `dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md --child VADW-C3 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/vadw-c3-handoff.md`; assert `target/output/count.txt` equals `1\n2\n3\n`. |
| Open Decisions | no open decisions |
| Readiness Status | IMPLEMENTATION READY |

## Parent Coverage

| Parent Requirement | Child Claim | Conformance | Action |
|---|---|---|---|
| VADW-PR7 | C3 owns the third output line and cumulative text `1\n2\n3\n`. | preserves | Validate predecessor and add the third line. |
| VADW-PR10 | C3 must be launched by the visible controller. | preserves | Do not self-launch. |
| VADW-PR11 | C3 readiness is validated before request publication and again by launcher. | preserves | Keep handoff and Child Index aligned. |
| VADW-PR12 | C3 contributes closeout and output evidence. | preserves | Write child closeout JSON after target output is correct. |

## In Scope

- Verify `target/output/count.txt` currently equals `1\n2\n`.
- Update it to exact UTF-8 text `1\n2\n3\n`.
- Write `closeout/vadw-c3-closeout.json` with `final_status: ran-target` and `closeout_status: closed`.

## Out of Scope

- Do not edit orchestration pack, parent handoff, child specs, child handoffs, controller requests, or controller responses.
- Do not use `tests/docworkflow-agent-delivery/scripts/run-mock-e2e-checks.sh`.
- Do not launch other children or simulate their work.

## Decision Freeze Pack

- Output file: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/target/output/count.txt`.
- Required predecessor output: `1\n2\n`.
- Required output after C3: `1\n2\n3\n`.
- Closeout file: `tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/closeout/vadw-c3-closeout.json`.

## Acceptance Criteria

- `target/output/count.txt` exists and equals `1\n2\n3\n`.
- C3 closeout JSON exists with `target_id: VADW-C3`, `final_status: ran-target`, and `closeout_status: closed`.
- No parent-owned or controller-owned file is changed by C3.

## Verification Commands

```sh
dotnet run skills-repo/tools/ValidateChildReadiness.cs -- --index tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/orchestration-pack.md --child VADW-C3 --handoff tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/handoffs/vadw-c3-handoff.md
python3 - <<'PY'
from pathlib import Path
p = Path('tests/docworkflow-agent-delivery/e2e/session-workflow-live/20260511T140421Z-visible-regression/target/output/count.txt')
assert p.read_text() == '1\n2\n3\n'
PY
git diff --check
```

## Dependencies and Write-Set

Dependency: `VADW-C2` output and closeout.
Allowed write-set: `target/output/count.txt`; `delivery-evidence/vadw-c3/**`; `closeout/vadw-c3-closeout.json`.

## Closeout Sync Targets

Child closeout JSON and controller response for `VADW-C3`.
