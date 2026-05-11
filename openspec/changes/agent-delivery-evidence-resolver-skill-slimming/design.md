## Context

Agent Delivery now has three valid session evidence shapes:

- launcher-only handoff evidence under `_specs/agent-delivery-session-launches/**`
- controller-backed visible multi-session evidence with controller summaries, requests, responses, and per-session launcher evidence
- closeout archive or retention summaries for visible Codex-App sessions

The current workflow docs and skills know these shapes, but the skills still repeat many low-level checks. That increases cognitive load and makes future drift likely.

## Goals / Non-Goals

**Goals:**

- Add one deterministic resolver gate that classifies Agent Delivery evidence for a target handoff or retained run.
- Let skills call the resolver and obey its verdict instead of restating detailed Launcher/Controller/archive checks.
- Keep the change small: reuse `WorkflowDoctor.cs` if practical, or add a focused tool with the same contract if that is simpler.
- Cover launcher-only, controller-backed visible multi-session, and closeout archive fixtures with positive and negative cases.

**Non-Goals:**

- Do not change how sessions are launched.
- Do not add new live app-server behavior.
- Do not implement live `thread/archive`.
- Do not replace the existing mock E2E gate or MD-E2E-5 live runner.
- Do not broadly rewrite the Agent Delivery workflow.

## Decisions

### Decision: Resolver Contract First, Tool Name Second

The implementation SHALL provide a stable CLI contract:

```sh
dotnet run skills-repo/tools/WorkflowDoctor.cs -- --phase evidence-resolution ...
```

The canonical command SHALL accept the relevant evidence shape through explicit inputs, for example handoff/launcher evidence paths, a retained controller run directory, or a closeout archive summary path. It SHALL also accept or infer the expected claim level, such as queued handoff, launched session, visible controller run, or closeout archive. If `WorkflowDoctor.cs` becomes awkward, a new focused tool may be introduced, but it MUST expose the same verdict fields and be referenced from `WorkflowDoctor` or the skills through one canonical command.

Rationale: the user-facing simplification is the resolver contract, not the class name.

### Decision: Verdict Semantics

The resolver SHALL use:

- `pass` only when the requested evidence shape is complete and internally consistent.
- `not_ready` when required evidence is missing, incomplete, still manual, queued when the requested claim requires launched/visible proof, or blocked by an expected-but-unresolved prerequisite.
- `fail` when evidence is contradictory, unsafe, proves a forbidden flow such as parent-started child launch, or claims success while a blocking archive/session condition is present.

Rationale: skills need predictable stop behavior without reimplementing the detailed evidence matrix.

### Decision: Machine-Readable Verdict

The resolver SHALL emit JSON with:

- `schema_id`
- `verdict`: `pass`, `not_ready`, or `fail`
- `mode`: `launcher_only`, `controller_visible_multi_session`, or `closeout_archive`
- `target_id` or run id
- `evidence_paths`
- `blockers`
- `warnings`
- `recommended_next_action`

Rationale: skills need one small decision point and enough evidence paths for handoff/closeout reporting.

### Decision: Fixture-First Implementation

The resolver SHALL support fixture replay before any live evidence path is required. Fixtures should reuse existing evidence families where possible and add only the missing resolver-specific manifests.

Rationale: this is a workflow hardening change; deterministic regression coverage is more valuable than a new live run.

## Risks / Trade-offs

- **Risk:** A resolver could hide important nuance from the skills.  
  **Mitigation:** JSON keeps blockers, warnings, evidence paths, and recommended next action.

- **Risk:** Skills may become too terse and lose operational context.  
  **Mitigation:** `doc-workflow.md` remains the canonical conceptual source; skills retain roles and stop conditions.

- **Risk:** Adding a new tool instead of extending `WorkflowDoctor` could create another thing to remember.  
  **Mitigation:** either route through `WorkflowDoctor --phase evidence-resolution` or document one canonical resolver command in `doc-workflow.md`.
