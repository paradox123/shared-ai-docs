# MD-E2E-5 Visible Codex App Sessions

`MD-E2E-5` is the live visible Codex-App session workflow test. It is separate from the mock-only standard gate and must not reuse mock-runner evidence as live proof.

## Runner Contract

The S3 runner command is:

```sh
tests/docworkflow-agent-delivery/scripts/run-visible-app-session-workflow-checks.sh --run-id <id> --keep
```

The command passes only when the runner retains a live run directory under:

```text
tests/docworkflow-agent-delivery/e2e/session-workflow-live/<run-id>/
```

The live run must include:

- parent visible-session evidence,
- five child visible-session evidence records for `RSW-C1` through `RSW-C5`,
- S4 control-boundary summary,
- S5 closeout archive summary,
- final `target/output/count.txt`,
- `visible-session-summary.json`.

## Required Final Summary

The live runner must write `visible-session-summary.json` with `schema_id: "docworkflow-agent-delivery-visible-app-e2e-summary.v1"`.

Pass requires:

- `overall_workflow_status: "pass"`,
- `visible_session_status: "pass"`,
- `control_session_status: "observed_only"`,
- `archive_status: "READY"`,
- `final_output_status: "pass"`,
- `mock_gate_status: "not_applicable_live_md_e2e_5"`.

The final output file must be exactly `1\n2\n3\n4\n5\n` with SHA-256 `f6b49467f595b1a44e442c198b3df4d221e88efcaabc26254f8e0ad4f79b6242`.

## Consumed Gates

Before a live `MD-E2E-5` result can pass, the runner must consume the accepted predecessor gates:

```sh
dotnet run skills-repo/tools/ValidateVisibleCodexAppSessionEvidence.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-evidence
node tests/docworkflow-agent-delivery/e2e/validators/control-boundary-summary.js tests/docworkflow-agent-delivery/e2e/fixtures/control-session-boundary
dotnet run skills-repo/tools/ArchiveVisibleCodexAppSession.cs -- --fixture tests/docworkflow-agent-delivery/e2e/fixtures/visible-app-session-closeout --mode validate
```

For the live run, parent plus five child evidence records must pass the S2 visible evidence rules; the S4 summary must prove observed-only control behavior; the S5 archive summary must prove visible sessions were archived, already archived, or explicitly retained with user acceptance.

## Negative Cases

`MD-E2E-5` must fail when any of these are true:

- final output is correct but visible evidence is missing, headless, queued, source-exec, wrong-title, wrong-cwd, missing-thread, empty-turn, or prompt-hash invalid,
- visible evidence exists but final output is wrong or incomplete,
- the control session writes orchestration, child specs, handoffs, child delivery evidence, closeout evidence, or `target/output/count.txt`,
- visible sessions remain unarchived without explicit retained-session acceptance,
- mock-runner output is relabelled as live visible-session proof,
- setup/usage is invalid, including missing or unsafe `--run-id`,
- summaries or retained evidence leak secrets, prompt bodies, auth tokens, raw environment, or unnecessary transcript payloads.

## Current Delivery Status

S3 now has an executable `--run-id <id> --keep` gate. It writes `visible-session-summary.json` for both pass and retained `not_ready` runs. A pass must not be claimed until real parent plus five child visible Codex-App session evidence, S4 control-boundary status, S5 archive evidence, and exact final output are retained under the live run directory.
