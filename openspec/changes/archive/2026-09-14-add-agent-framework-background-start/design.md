## Context

Ticket 02 was implemented on `codex/operator-gui-issue-02` from the accepted Ticket 01 baseline `a77418a`. The user accepted the real GUI/background/failure proofs on 2026-09-14 and requested archive, commit, push and merge to `main`.

## Goals / Non-Goals

**Goals:** Archive the completed first-step contract and its direct evidence, preserving the accepted intake baseline and all unfinished work in the parent change.

**Non-Goals:** Full unattended implementation/evidence/review/repair (Ticket 09), file intake (Ticket 11), detailed graph/history rendering (Ticket 03), Azure deployment of the new runtime, and separate-machine overall acceptance (Ticket 16).

## Decisions

- Analyze the immutable admitted GitHub requirements in a service-owned read-only workspace. The result describes scope, acceptance criteria and blockers; completed analysis does not qualify an implementation head.
- Reuse the Agent Framework worker and central `AgentSessionAdapter/v1` history boundary with the additive analysis result contract. Retain the existing `worker-result-v3` implementation contract and public CLI/run/dossier paths.
- Link the submission, ImplementationRun and dispatch atomically in PostgreSQL. A separate service claims work; neither browser nor launcher lifetime owns execution.
- Persist preparation before dispatch and reconcile uncertain responses using the original operation/assignment. A timeout or worker crash must not create a replacement logical step or discard an eventual session/result.
- Use the same accepted-slice extraction as Ticket 01. Archiving the entire parent would falsely close unfinished requirements; keeping duplicated Ticket 02 scenarios in both deltas would risk divergent contracts.

## Risks / Trade-offs

- Local process independence is not distributed acceptance → retain Ticket 16 and its server/workstation scenarios unchanged.
- Adapter outage after possible delivery leaves uncertainty → retain the reconciling disposition and diagnostic until the original receipt can be read.
- Archive moves can break evidence links → update references and verify all moved documents against their final archive location.

## Closeout refactoring and verification

The pre-archive DRY/SOLID/KISS pass inspected the shared session workflow, dispatch/storage boundary and surrounding mode/result logic. The earlier review corrections already consolidated mode metadata, restored the legacy fixture and preserved uncertain deliveries; no further runtime change is warranted. Extract only the accepted requirement and evidence, replacing duplicate parent detail with links. Rerun the focused public HTTP/browser checks; retain the full 218-test regression and the fresh five-case live/recovery proof.
