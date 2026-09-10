# Session prompt: Microsoft Agent Framework control-plane PRD

> **Superseded input — do not execute.** This file preserves the original session request only as provenance. The later product decision excludes Temporal and paid managed workflow services, keeps the LangGraph pilot unchanged, and uses `.scratch/distributed-codex-work-package-control-plane/spec.md` as the sole PRD. Current implementation guidance lives in `microsoft-agent-framework-local-spike-plan.md` and `issues/`.

Work in the repository `shared-ai-docs` and develop a reviewable PRD plus a local architecture-spike plan for implementing the Distributed Codex Work Package Control Plane with Microsoft Agent Framework for .NET and its Durable Extension.

This session is for product/architecture elaboration and spike design. Do not implement or migrate the production control plane yet. Preserve unrelated worktree changes.

## Starting position

The architecture preference is already recorded: Microsoft Agent Framework for .NET plus Durable Extension/Durable Task is the preferred candidate for the first local spike because:

1. its graph-based .NET workflows are a plausible peer to the LangGraph workflow layer in the existing pilot;
2. the Durable Extension addresses the same durable-execution problem class as Temporal;
3. existing .NET expertise should reduce implementation, diagnosis, and operating cost when the technical fit is otherwise comparable.

This is not permission to assume feature parity. The spike must prove the hard semantics. Codex remains the agent harness and must be integrated behind a versioned adapter. LangGraph is the behavioral baseline; Temporal is the durable-execution benchmark and fallback.

## Read first

Follow `AGENTS.md`, inspect `git status --short`, and then read these sources in order:

1. `README.md`
2. `.scratch/distributed-codex-work-package-control-plane/spec.md`
3. `docs/adr/0001-live-control-commands-for-active-agent-runs.md`
4. `docs/adr/0002-operator-clients-instead-of-human-agent-sessions.md`
5. `docs/adr/0003-forced-takeover-without-admin-role.md`
6. `docs/adr/0004-human-approved-agent-definition-evolution.md`
7. `docs/adr/0005-separate-agent-definitions-from-work-package-orchestration.md`
8. `docs/adr/0006-externalize-agent-definition-approval-to-repository-governance.md`
9. `docs/adr/0007-derive-operator-access-from-repository-permissions.md`
10. `docs/adr/0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md`
11. `.scratch/distributed-codex-work-package-control-plane/make-or-buy-entscheidungsvorlage.md`
12. `langgraph-github-issue-pilot/README.md`
13. `docs/langgraph-github-issue-pilot.md`
14. `docs/langgraph-github-issue-pilot/open-source-orchestration-options.md`
15. `langgraph-github-issue-pilot/pyproject.toml`
16. the relevant implementation seams under `langgraph-github-issue-pilot/src/github_issue_pilot/`, especially `workflow.py`, `storage.py`, `implementation.py`, `intervention.py`, `review.py`, `repair.py`, `github.py`, and `app.py`
17. the corresponding behavioral and recovery tests under `langgraph-github-issue-pilot/tests/`

Use QMD first for additional DanielsVault documentation discovery. For current Microsoft Agent Framework, Durable Task, Temporal, and Codex facts, verify against current primary documentation rather than relying on memory. Clearly separate documented capability, inference, and spike result.

## Goal

Produce a PRD that describes the smallest useful distributed Work Package Control Plane built around Microsoft Agent Framework for .NET, with a local spike that can falsify the architecture preference early.

The PRD must preserve these product boundaries:

- one durable `ImplementationRun` per authorized issue;
- multiple typed activities and attempts under the same run;
- fresh, context-isolated Codex sessions by default;
- deterministic tests, Git/GitHub effects, qualification, and status projection outside the model;
- complete observable execution history, but no claim to private model reasoning;
- a stateless Operator Client with remote inspection and control;
- exactly one human Control Lease per run;
- repository-derived authorization instead of a second member/ACL system;
- explicit Resume, Fork, Fresh Retry, Takeover, Cancel, Approval, `interrupt`, and `queue` semantics;
- no automatic merge, deployment, release, or self-approval of Agent Definition changes.

## Required analysis

### 1. Map the existing pilot instead of starting from a blank slate

Create a source-to-target mapping for at least:

- LangGraph `StateGraph`, checkpoints, `Command`, and `interrupt`;
- SQLite inbox, workflow state, operation identities, and startup reconciliation;
- FastAPI webhook and workflow read-back seams;
- `RepositoryAdapter`, GitHub transport, worktree and publication adapters;
- `CodexCliWorker`, review workers, intervention session adapter, and JSON contracts;
- evidence qualification, deterministic verification, three review axes, repair rounds, and human feedback;
- current tests that can become language-neutral contract or black-box tests.

For every element classify it as:

- `reuse unchanged`;
- `reuse contract/behavior only`;
- `replace with Agent Framework`;
- `replace with Durable Task`;
- `new WorkPackageControlPlane responsibility`;
- `defer/out of scope`.

Do not assume every LangGraph node should become an Agent Framework agent. Prefer deterministic executors/activities for deterministic work.

### 2. Separate the architecture layers

Define clear responsibilities and interfaces for:

- `WorkPackageControlPlane` domain/application layer;
- Microsoft Agent Framework workflow layer;
- Durable Extension/Durable Task execution layer;
- versioned `AgentSessionAdapter` for Codex;
- Run History/Event Store and read projections;
- Artifact Store;
- Repository Provider adapters;
- Operator API and Operator Client;
- worker/worktree execution boundary;
- Agent Evolution Loop.

Explicitly decide which state is canonical. Agent Framework session history and Durable Task orchestration history must not silently replace the domain-level `ImplementationRun` history.

### 3. Define the local falsification spike

Design one executable local vertical slice using .NET and bring-your-own-compute/self-hosted workers. Prefer the officially supported local Durable Task development backend or emulator; do not provision paid cloud resources in this planning session.

The spike must demonstrate:

1. an authorized synthetic or local GitHub issue command starts one durable implementation run;
2. a Codex adapter boundary is exercised first with a deterministic fake and then, if locally safe, with a real bounded Codex invocation;
3. the agent performs several observable steps and fails after a controlled external effect;
4. the host and worker are terminated at deliberately chosen boundaries and the run recovers without duplicating the external effect;
5. a second authenticated test identity reads the same run from another client process;
6. Resume preserves the Codex session identity, Fork creates a new session with ancestry, and Fresh Retry creates a new session without automatic conversation carry-over;
7. `interrupt` and `queue` target one explicit activity attempt and remain visible in stable order;
8. Control Lease, transfer, Forced Takeover, stale-head rejection, and fencing are proven under concurrency;
9. deterministic verification and three context-isolated reviewers qualify the same new Head-SHA;
10. a third identity approves the qualified head without triggering merge;
11. the Operator Client reconnects from an acknowledged event cursor without gaps or duplicates;
12. secrets and recognizable personal data injected into controlled tool output are redacted before persistence and display.

For each spike step specify setup, action, crash boundary, expected observable result, public read-back seam, required evidence, and pass/fail condition.

### 4. Test the Agent Framework assumption directly

Answer with evidence:

- Which existing LangGraph responsibilities are covered by Agent Framework Workflows?
- Which durability responsibilities are covered only when the Durable Extension/Durable Task is added?
- What is the exact local hosting topology?
- Can an external Codex process/session be modeled cleanly without replacing Codex with a model-native Agent Framework agent?
- What events are emitted, persisted, replayed, and exportable?
- How are pending human requests restored after restart?
- What are the failure semantics when an external effect succeeds immediately before an activity result is durably recorded?
- Can running work be cancelled or interrupted and then receive exactly one next command?
- Which functions require custom application code despite framework support?
- Which packages or capabilities are prerelease, and what version-pinning/upgrade risk follows?
- At which concrete result would Temporal become the preferred fallback?

Treat „Agent Framework is equivalent to LangGraph plus Temporal“ as the hypothesis to falsify, not as the conclusion to defend.

## Required artifacts

Create these files next to the existing scratch spec:

1. `.scratch/distributed-codex-work-package-control-plane/microsoft-agent-framework-prd.md`
2. `.scratch/distributed-codex-work-package-control-plane/microsoft-agent-framework-local-spike-plan.md`
3. `.scratch/distributed-codex-work-package-control-plane/langgraph-to-agent-framework-mapping.md`

The PRD should contain:

- problem, intended outcomes, personas, scope, non-goals, assumptions, and constraints;
- canonical domain concepts and actor boundaries;
- functional requirements and externally observable acceptance scenarios;
- security, privacy, audit, reliability, recovery, performance, and operability requirements;
- MVP and later phases;
- dependency and hosting choices that remain open;
- measurable success criteria;
- risks and explicit product questions that genuinely require Daniel's decision.

The spike plan should contain:

- local topology and component diagram;
- package/version assumptions with source dates;
- vertical slices in dependency order;
- fault-injection matrix;
- evidence matrix against the relevant Make-or-Buy gates;
- effort estimate by slice, not a false single-number estimate;
- stop/go criteria and Temporal fallback triggers;
- cleanup and rollback steps for local resources.

The mapping should identify existing source files, tests, contracts, public seams, retained behavior, and the proposed .NET destination. It must highlight what can be reused conceptually versus what would need reimplementation.

## Working rules

- Keep the work in `.scratch/distributed-codex-work-package-control-plane/`; do not change production code in this session.
- Do not create Azure resources, purchase services, change GitHub configuration, or start a production migration.
- Do not modify the accepted behavioral semantics merely to match an easier framework abstraction.
- Do not equate Agent Framework's model/provider support with support for the Codex CLI/session harness without a demonstrated adapter.
- Do not treat a dashboard screenshot, successful startup, health check, or framework checkpoint alone as sufficient evidence.
- Preserve the existing direct public-interface evidence standard from the LangGraph pilot.
- Record unresolved framework behavior as a spike question with an executable verification, not as an assumption.
- If no new product decision is required, make reasonable technical choices and document them. Ask Daniel only when an alternative changes visibility, control rights, autonomy, privacy, or irreversible external effects.

Finish with a concise recommendation: proceed with the local Microsoft Agent Framework spike, revise its scope, or stop and prefer Temporal/LangGraph. Base that recommendation on the completed PRD and explicit evidence gaps; do not implement the spike unless Daniel asks in a later turn.
