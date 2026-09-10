## Context

The repository has two useful but differently scoped sources: the implemented LangGraph pilot specification and tickets, and the newer distributed Work Package Control Plane draft. The LangGraph material proves behavior but also contains deliberate local-pilot choices such as Python, LangGraph, SQLite, Cloudflare, macOS, model routing, and a Codex App intervention handoff. The distributed draft contains the broader team product but mixes those requirements with architecture and testing decisions.

Three archived ProBara CRM tasks provide direct operational feedback:

- `Implement backlog tickets sequential` (`01a02ed5-bc43-7702-bc36-b326f6859839`)
- `Diagnose fehlgeschlagener Issue-2-Um…` (`01a0326d-f61e-7e00-b76d-3dee0e9295ad`)
- `Diagnose LangGraph workflow pause` (`01a03a64-b1c8-7ba1-9493-f27b41beb7c2`)

They exposed stale installed runtime, stale repository base, incomplete execution prerequisites, schema/endpoint incompatibility, loss of a valid worker outcome, semantically insufficient evidence despite schema validity, no evidence-repair transition, stuck active projection/serialization, hidden headless worker sessions, unreliable monitoring duration inference, and an oversight automation that could perform the nominally human PR gate.

The user has fixed three constraints: Temporal is excluded; the solution must have a self-hostable open-source path without additional workflow-engine or managed-service licence fees; and the Microsoft pilot supplements rather than replaces the existing LangGraph pilot.

## Goals / Non-Goals

**Goals:**

- Make one product specification canonical and technology independent.
- Preserve proven LangGraph behavior and operations unchanged.
- Separate Microsoft-specific architecture and executable spike material from product requirements.
- Turn every verified ProBara lesson into either a requirement or a durable ticket/test warning.
- Create a fresh vertical ticket set for a sibling .NET pilot.
- Remove the duplicate Microsoft-specific PRD after extraction.

**Non-Goals:**

- Implementing the .NET pilot in this documentation change.
- Migrating, replacing, or modifying the LangGraph pilot, Cloudflare relay, launchd services, or ProBara CRM.
- Selecting or provisioning a paid Azure service.
- Reopening completed LangGraph tickets.
- Treating the local in-memory DTS emulator as evidence of a production-capable open-source backend.

## Decisions

### One product source, separate implementation tracks

`.scratch/distributed-codex-work-package-control-plane/spec.md` is the product source. It contains outcomes, domain behavior, externally observable scenarios, safety boundaries, and session-derived lessons. Framework types, package versions, local topology, and fault hooks remain in the MAF mapping and spike plan.

The implemented `langgraph-github-issue-pilot/` remains a complete sibling baseline. A later implementation creates `microsoft-agent-framework-work-package-pilot/` as a new top-level directory with independent package metadata, configuration, processes, state, worktrees, and ports. It must not write into LangGraph's runtime database or managed worktrees.

### Open-source suitability is Gate 0

Before building the semantic vertical slices, the spike must prove that the chosen Agent Framework plus Durable Task integration has a production-capable, self-hostable open-source backend path without mandatory managed workflow-service or framework licence fees. The local DTS emulator is allowed for development but cannot pass this gate. Temporal is not an alternative or fallback.

If Gate 0 fails, the MAF/Durable candidate stops. The existing LangGraph pilot continues while another explicitly approved open-source architecture is evaluated separately.

### Reuse behavior, not old implementation tickets

The old tickets remain the audit trail of the LangGraph implementation. Their public acceptance behavior and fixtures are inputs to the new tickets, but LangGraph, SQLite, Cloudflare, macOS, ProBara-specific rollout, and model/version routing are not copied into the new product contract. The old separate summary-task handoff is replaced by a targeted `Open in Codex` action tied to the actual activity attempt and canonical Run History.

### Session feedback classification

Product-level gaps become normative requirements:

- exact provider-authoritative base before work begins;
- executable readiness/evidence plan before expensive agent work;
- visible evidence-repair or explicit blocked convergence;
- lossless redacted worker outcome/failure visibility;
- no automation may impersonate the interactive human approval gate.

Implementation-level gaps become mandatory ticket guidance and tests:

- deployed source/package/config provenance and compatibility checks;
- Codex-supported JSON Schema subset negotiation;
- sandbox ownership and process-boundary preflight;
- distinct run, attempt, process, and heartbeat timestamps;
- headless session observations copied into the public Run History;
- no recovery through manual database edits.

### Document disposition

Unique product content from `microsoft-agent-framework-prd.md` is incorporated into the canonical spec. The file is then deleted. `langgraph-to-agent-framework-mapping.md` remains a technical reuse map. `microsoft-agent-framework-local-spike-plan.md` remains the executable architecture plan after removing Temporal and adding Gate 0 plus the sibling-directory boundary. The primary-source research remains evidence, but its recommendation is updated so Temporal is an excluded historical comparison rather than a fallback.

### Deleted-draft extraction check

The final extraction check maps all 18 functional requirements from the deleted draft to the canonical product source and the fresh implementation backlog:

| Deleted draft | Canonical coverage | Implementation slice |
| --- | --- | --- |
| FR-01 authorized unique start; FR-02 typed activities | US 1-8, 19-20 and fachliche Regeln | Issues 01, 02, and 04 |
| FR-03 fresh context; FR-09 continuation modes | US 16-26, 36-38 and fachliche Regeln | Issues 04, 06, and 10 |
| FR-04 observable history; FR-05 remote observation; FR-16 cursor reconnect | US 27-35, 45-48, 76-83 and fachliche Regeln | Issues 02, 04, and 09 |
| FR-06 run-wide lease; FR-07 transfer/takeover; FR-08 targeted commands; FR-10 takeover/cancel/approval | US 39-43, 49-58, 70-96, 120-125 and fachliche Regeln | Issues 03, 06-08, and 14 |
| FR-11 durable human request | US 46-51 and fachliche Regeln | Issue 06 |
| FR-12 external-effect adoption | US 43-45 and fachliche Regeln | Issue 05 |
| FR-13 head qualification; FR-14 bounded repair | US 53-56, 64-69, 128, 131 and fachliche Regeln | Issues 11-14 |
| FR-15 repository-derived authorization | US 57-61, 113-124 and fachliche Regeln | Issues 03 and 08 |
| FR-17 redaction | US 27-35, 55-63 and fachliche Regeln | Issues 02, 04, 09, and 11 |
| FR-18 Agent Definition governance | US 95-112 and fachliche Regeln | Revision provenance begins in Issues 01-02; externally approved use and self-approval prohibition are verified in Issue 14; proposal generation remains beyond this pilot |

The draft's security, reliability, recovery, operability, and measurable-success material is retained as user stories, fachliche rules, acceptance principles, or explicit ticket checks. Framework packages, topology, storage choices, endpoint schema mechanics, and fault hooks remain only in the technical artifacts and tickets.

The later product decision adds one requirement beyond the deleted draft: US 133 and the OpenSpec requirement `A targeted activity session can be opened in Codex`. It is delivered across tickets 04, 06, and 10 and verified again in ticket 14.

## Risks / Trade-offs

- **Product spec becomes too large** → Keep detailed package, topology, and fault mechanics in the design/spike documents and retain only externally observable requirements in the product source.
- **Shared acceptance behavior diverges between pilots** → Use the same language-neutral fixtures and public scenarios while allowing independent implementations.
- **MAF appears free locally but requires paid DTS in production** → Fail Gate 0 before the expensive semantic slices.
- **Session lessons become anecdotal** → Record task IDs, observed facts, classification, and the requirement or ticket that addresses each lesson.
- **Completed LangGraph history is accidentally rewritten** → Do not modify old tickets, runtime code, Cloudflare assets, or ProBara CRM.
- **Deleting the duplicate PRD loses content** → Map every FR section to the canonical spec before deletion and verify required concepts afterward.

## Migration Plan

1. Add the canonical OpenSpec capability and refactor the scratch product spec.
2. Append the ProBara session feedback ledger to the product spec.
3. Update ADR 0008 and the MAF spike/mapping/research documents for the fixed constraints.
4. Create new vertical tickets targeting the future sibling pilot directory.
5. Verify unique MAF-PRD requirements are present, then delete the duplicate PRD.
6. Validate Markdown links, OpenSpec, and repository diff; leave application implementations untouched.

Rollback is documentation-only: restore the deleted draft from the current task diff and revert the new OpenSpec/ticket/spec edits. Neither pilot runtime is changed.

## Open Questions

- Which open-source Durable Task-compatible production backend is actually supported by the pinned MAF Durable Extension tuple? This is an executable Gate 0 question, not a product decision.
- Should the future implementation promote shared JSON contracts into a neutral package after parity, or keep copied versioned fixtures during the spike? Default: copied fixtures until parity avoids destabilizing the working LangGraph pilot.
