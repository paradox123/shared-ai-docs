# Agent Delivery Retro Review - DocWorkflow Testsuite

## Findings

- P1: Missing launch/queue evidence for the delivered DWT chain. Evidence: `_specs/agent-delivery-session-launches/` is absent, while the handoffs for `DWT-S0` through `DWT-S5` recommend fresh sessions and real sessions were reconstructed from `/Users/dh/.codex/...` logs. Impact: future reviewers can prove the handoff text existed, but not that a fresh agent transition was queued or launched through the workflow contract. Recommendation: keep `AgentDeliverySessionLauncher.cs` as a required gate for future ready-child handoffs; historical DWT sessions should be recorded as pre-launcher/manual transitions.
- P1: Semantic `SessionId` labels are not enough for forensic reconstruction. Evidence: Parent and child handoffs use labels such as `2026-05-08-docworkflow-agent-delivery-testsuite-dwt-s5`, while real Codex ids include `019e0721-3feb-7bf1-9c5d-154d2ef3980f`, `019e075a-cf38-7511-ab14-a6f4cc97b411`, and `019e0797-f6ba-7eb1-9fa9-514543678bf8`. Impact: session collection required `rg` over `.codex` logs instead of following durable handoff metadata. Recommendation: handoffs should include real session/log paths when available, or launcher evidence should become the source of truth.
- P2: Active-change verification can go stale immediately after archive. Evidence: Parent closeout records the DWT-S5 L3 active-child harness as a failed stale post-archive command and replaces it with archive-presence plus canonical-spec assertions. Impact: a correct closeout can look failed if a future session replays the pre-archive command blindly. Recommendation: every closeout must leave a current `Post-Archive / Current Replay` command set and mark active-change commands as historical evidence only.
- P2: Temp evidence was useful during delivery but needed explicit retention. Evidence: DWT-S1 initially used `/var/folders/.../l1-summary.json`; DWT-S2, DWT-S3 and DWT-S5 later retained `ran-target` summaries under `tests/docworkflow-agent-delivery/**/evidence/2026-05-08-ran-target/`. Impact: later child specs can safely consume retained summaries only after source-controlled copy plus manifest/hash exists. Recommendation: keep the current stable-retention rule and treat temp-only accepted evidence as a blocker or named limitation.
- P3: The workflow improved while the testsuite was being delivered. Evidence: the 2026-05-08 launcher automation sessions implemented `skills-repo/tools/AgentDeliverySessionLauncher.cs` and patched `docs/doc-workflow.md`, `spec-orchestrator`, `child-spec-hardening`, `spec-change-delivery`, `spec-closeout`, and this retro skill. Impact: some early DWT findings are already addressed in current workflow docs, but should remain documented as regression targets.

## Reconstructed Flow

- Parent/Scope: `_specs/2026-05-07 DocWorkflow Agent Delivery Testsuite.md` remained the control layer, with `DWT-S0` through `DWT-S5` tracked in the Delivery Orchestration Pack and closed as accepted on 2026-05-08.
- Orchestrator: `spec-orchestrator` created/updated child rows and handoffs, but readiness was correctly deferred to `child-spec-hardening` plus `ValidateChildReadiness.cs`.
- Child Hardening: `DWT-S1`, `DWT-S2`, `DWT-S3`, `DWT-S4`, and `DWT-S5` were hardened in separate sessions with child specs, handoffs, OpenSpec changes, write-sets and verification contracts.
- Delivery: `spec-change-delivery` implemented `DWT-S0`, `DWT-S1`, `DWT-S2`, `DWT-S3`, `DWT-S4`, and `DWT-S5` through deterministic, L2 agent, reporting, and L3 temp-repo harnesses.
- Closeout: `spec-closeout` archived OpenSpec changes, updated the canonical spec, synchronized parent/index/handoff/evidence, and eventually closed the parent.
- Handoff / Next Child: next-child release stayed gated; `DWT-S5` was not released by `DWT-S3` until its own hardening produced an implementation-ready handoff.

## Sessions

- Parent/workflow expansion: `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T08-42-32-019e012c-7b4c-7630-bd35-24add877cd1a.jsonl`
- Testsuite proposal/build start: `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T10-00-23-019e0173-be3b-7283-8d7c-0d589e8aa16d.jsonl`
- DWT-S0 hardening/review: `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T11-36-32-019e01cb-c8b2-7c02-8842-4c9a470144bc.jsonl`
- DWT-S0 delivery: `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T12-24-37-019e01f7-cafe-79b2-9647-76fcab3f807c.jsonl`
- DWT-S1 hardening/delivery/closeout: `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T14-08-24-019e0256-ceba-76b0-b3d7-e11724b5e978.jsonl`, `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T15-28-10-019e029f-d9e0-7372-b32b-7bc310e0880b.jsonl`, `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T17-48-04-019e031f-ebe8-7432-87e9-9c33c216d44b.jsonl`
- DWT-S4 hardening/delivery: `/Users/dh/.codex/archived_sessions/rollout-2026-05-07T17-55-49-019e0327-058b-7bc3-9129-ddf1ff03a58d.jsonl`, `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T07-54-07-019e0626-8278-75e0-b586-4530b268f2ef.jsonl`
- DWT-S2 hardening, auth fix and closeout: `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T08-18-08-019e063c-7e8c-7942-978a-c7fe3d866088.jsonl`, `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T08-31-02-019e0648-5015-7922-a56a-45028e4c16bc.jsonl`, `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T11-01-59-019e06d2-80d5-7b71-8df9-5ef6be374d90.jsonl`
- DWT-S3 hardening/delivery/closeout: `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T11-28-48-019e06eb-0e0e-7fb3-9aeb-d9098c7456b4.jsonl`, `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T11-38-47-019e06f4-30ed-7620-bc41-19b941cbf445.jsonl`
- DWT-S5 hardening/delivery/closeout: `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T12-28-00-019e0721-3feb-7bf1-9c5d-154d2ef3980f.jsonl`, `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T13-30-52-019e075a-cf38-7511-ab14-a6f4cc97b411.jsonl`
- Parent closeout: `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T14-37-40-019e0797-f6ba-7eb1-9fa9-514543678bf8.jsonl`
- Session-launcher learning follow-up: `/Users/dh/.codex/archived_sessions/rollout-2026-05-08T13-31-17-019e075b-3227-7da1-8f59-4480a0ee4d75.jsonl`

## What Worked

- Parent/Child control stayed visible through the full chain.
- `ValidateChildReadiness.cs` caught stale next-action and index/handoff issues before delivery could proceed.
- Accepted `ran-target` evidence was retained for DWT-S2, DWT-S3 and DWT-S5 in source-controlled evidence folders.
- Reporting/style/efficiency fixtures made stale handoff and forbidden command classes machine-readable.
- Parent closeout correctly treated the stale DWT-S5 active-child command as a command-contract finding, not as failed runtime proof.

## Improvements

- Sofort patchbar: maintain this report and skill-memory entries as the durable retro record.
- Braucht Entscheidung: whether to backfill `_specs/agent-delivery-session-launches/` entries for historical DWT sessions as `manual_start_required`/`legacy_reconstructed`, or leave them as pre-launcher history.
- Spaeterer Testsuite-Ausbau: add a fixture that fails when a handoff claims fresh-session transition but no launcher evidence exists.
- Automatisierung / Validator: extend `ValidateChildReadiness.cs` or a companion validator to optionally require matching launcher evidence for ready children.

## Applied Changes

- Added this retro report.
- Added skill-memory entries for launch evidence, session-id crosswalks and post-archive replay discipline.

## Next Best Patch

Add a deterministic testsuite case for missing/stale Agent Delivery Session Launch/Queue Evidence, because that is the one remaining workflow gap that the completed DWT suite exposed but did not itself enforce.
