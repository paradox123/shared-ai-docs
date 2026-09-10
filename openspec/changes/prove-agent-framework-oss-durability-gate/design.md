## Context

The approved spike plan makes open-source durability Gate 0 a prerequisite for the sibling Microsoft Agent Framework pilot. The current repository contains the accepted LangGraph pilot and planning evidence, but no executable Microsoft gate. The critical unknown is whether the exact Agent Framework Durable Extension client/worker protocol can use a production-capable self-managed open-source Durable backend; the development emulator is explicitly insufficient.

The gate must remain useful when the answer is no. It therefore separates deterministic eligibility checks from the destructive worker-replacement probe and records a signed-off no-go when eligibility cannot be established. All work is isolated from existing pilot state.

## Goals / Non-Goals

**Goals:**

- Produce a reproducible manifest for every direct and transitive component, immutable version/revision, licence, configuration, contract version, and unavoidable service cost.
- Reject drift or an unsupported backend tuple before workflow startup.
- When eligible, run one durable orchestration across two worker processes and prove exactly-once observable effects across controlled worker termination.
- Produce correlated JSON and Markdown evidence, including before/after isolation fingerprints.
- Produce an explicit no-go and stop if the production OSS path cannot be proved.

**Non-Goals:**

- Building the later Work Package Control Plane product API or semantic tickets.
- Treating the local DTS emulator as production evidence.
- Adding Temporal, a paid managed workflow service, or a latent fallback configuration.
- Mutating the LangGraph pilot, Cloudflare relay, macOS services, their runtime data/worktrees, GitHub configuration, or ProBara CRM.

## Decisions

### A small gate workspace precedes the sibling pilot

Gate tooling lives under `microsoft-agent-framework-oss-gate/`, not the future `microsoft-agent-framework-work-package-pilot/`. This makes the rule "no pilot before Gate 0" mechanically observable. The gate owns its temporary resources, evidence, and cleanup boundaries.

Alternative considered: bootstrap the sibling pilot and add a gate project inside it. Rejected because its existence would falsely imply that Gate 0 had passed and would make isolation evidence ambiguous.

### A versioned manifest is the source of eligibility truth

The gate reads a committed machine-readable manifest containing source revision, SDK/runtime, package tuple and lock hash, protocol/contract, backend repository/revision/image digest, licences, storage dependencies, service costs, and forbidden dependencies. JSON Schema plus semantic validation fail closed on missing, floating, inconsistent, or forbidden values. Generated evidence cites the manifest digest.

Alternative considered: infer versions at runtime from installed packages. Rejected because runtime discovery alone cannot reproduce the intended graph or distinguish supported compatibility from accidental resolution.

### Backend qualification is independent of the emulator

The production backend entry must name an open-source repository and immutable revision, document production support and storage dependencies, and expose the protocol required by the pinned Durable client/worker. The checker rejects the development emulator and paid/managed-only endpoints as production backends. A real worker-replacement probe is enabled only after these checks pass.

Alternative considered: demonstrate worker replacement while the in-memory emulator remains alive. Retained only as optional development evidence; it cannot change the Gate 0 outcome.

### Public gate CLI is the TDD seam

Tests invoke a CLI using fixture manifests and process adapters. They assert exit status, structured decision output, prohibited startup calls, run identity, effect counts, and evidence correlation. Production source scanning and a real local backend probe complement, but do not replace, public-seam tests.

### Evidence is immutable and outcome-oriented

Each run writes into a new run-ID directory. `decision.json` and `report.md` correlate repository revision, dirty-state digest, lock hash, runtime, manifest digest, configuration, contract, backend, worker PIDs, checkpoints, and effect ledger. A no-go is a successful execution of the gate command but a nonzero qualification decision; the CLI exit code remains nonzero for automation.

## Risks / Trade-offs

- **No compatible production OSS backend exists for the portable Durable protocol** → Record a verified no-go, leave later tickets blocked, and do not substitute the emulator.
- **Licence metadata from package feeds is incomplete** → Correlate package metadata with repository licence files and fail closed when direct or transitive terms remain unknown.
- **A fake-process test overstates durability** → Label it contract evidence only; Gate 0 passes solely with a real supported backend and OS-level worker replacement.
- **Evidence accidentally captures private state** → Store only whitelisted metadata and hashes; never copy runtime databases, secrets, or private payloads.
- **Existing dirty worktree complicates fingerprints** → Record scoped paths and Git object/tree metadata without resetting or normalizing user changes.

## Migration Plan

1. Add the gate contract, fixtures, and failing public-seam tests.
2. Implement manifest/schema validation and fail-closed decision output.
3. Resolve and audit the exact package/backend graph, then record immutable provenance.
4. Run the real probe only if production OSS compatibility is established.
5. Record pass/no-go and isolation evidence; update the issue status and leave all dependent tickets untouched on no-go.

Rollback removes only the new gate workspace, its OpenSpec change, and generated evidence. Existing pilot assets are never migration targets.

## Open Questions

- Whether the current Microsoft portable Durable Task protocol has any production-supported open-source self-hosted scheduler compatible with the Agent Framework Durable Extension.
- Whether the aligned preview tuple restores and compiles unchanged on all target architectures; the first execution records macOS arm64 and container architecture explicitly.
