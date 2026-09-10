## Why

The distributed Work Package Control Plane needs one technology-independent product contract and a separate Microsoft Agent Framework architecture spike. The current drafts mix product requirements, LangGraph-specific pilot behavior, Microsoft package choices, and a Temporal fallback that has now been explicitly excluded, making future ticket slicing ambiguous.

## What Changes

- Establish the distributed Work Package Control Plane as the single technology-independent product capability.
- Preserve the implemented LangGraph GitHub Issue Pilot, including its Cloudflare and macOS integration, as an unchanged behavioral baseline.
- Define the Microsoft Agent Framework pilot as an additional sibling implementation under `microsoft-agent-framework-work-package-pilot/`, never as an in-place migration or replacement.
- Require an open-source, self-hostable production path without additional framework or workflow-service licence fees; exclude Temporal and paid managed workflow services from the candidate set.
- Feed verified ProBara CRM pilot-session failures back into requirements or, where they are implementation concerns, into mandatory ticket and verification guidance.
- Remove the duplicate Microsoft-specific PRD after extracting its unique product requirements; retain Microsoft-specific decisions only in the ADR, mapping, and spike plan.
- Create a fresh vertical implementation-ticket set for the additional .NET pilot rather than reopening the completed LangGraph tickets.
- Require the Operator Client to open a targeted background attempt in Codex using the same session where safely supported or an explicitly confirmed, correlated handoff fork otherwise.

## Capabilities

### New Capabilities

- `distributed-work-package-control-plane`: Technology-independent run, history, control, authorization, recovery, qualification, and human-approval behavior shared by alternative pilot implementations.

### Modified Capabilities

None. Existing LangGraph pilot capabilities remain accepted and unchanged.

## Impact

- Product source: `.scratch/distributed-codex-work-package-control-plane/spec.md`.
- Architecture records and spike material under `.scratch/distributed-codex-work-package-control-plane/` and `docs/adr/0008-prefer-microsoft-agent-framework-for-dotnet-control-plane-spike.md`.
- New implementation backlog under `.scratch/distributed-codex-work-package-control-plane/issues/agent-framework-pilot/` targeting a future top-level `microsoft-agent-framework-work-package-pilot/` directory. The adjacent LangGraph index and restored previous draft keep the two histories visibly separated.
- No production code, current LangGraph pilot code, Cloudflare configuration, macOS services, GitHub configuration, or ProBara CRM application code changes.
