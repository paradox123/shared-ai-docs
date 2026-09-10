## 1. Canonical product specification

- [x] 1.1 Refactor the distributed Work Package Control Plane scratch spec into technology-independent product requirements and remove Temporal/framework implementation choices.
- [x] 1.2 Append a ProBara CRM session-feedback ledger that maps each verified failure to a requirement or mandatory ticket/test reference.

## 2. Microsoft pilot architecture material

- [x] 2.1 Update ADR 0008 to exclude Temporal and paid managed workflow services and to require a separate sibling pilot.
- [x] 2.2 Update the Microsoft local spike plan with open-source Gate 0, the future `microsoft-agent-framework-work-package-pilot/` topology, non-replacement rules, and non-Temporal stop criteria.
- [x] 2.3 Update the LangGraph mapping and primary-source research so LangGraph remains an unchanged baseline and Temporal is not an actionable fallback.
- [x] 2.4 Update the related Make-or-Buy decision language without overwriting unrelated existing edits.

## 3. Fresh implementation backlog

- [x] 3.1 Create vertical issue files under `.scratch/distributed-codex-work-package-control-plane/issues/agent-framework-pilot/` for the additional Microsoft pilot and keep the LangGraph baseline separately indexed.
- [x] 3.2 Ensure every issue traces to the canonical product requirements and incorporates relevant ProBara session lessons without reopening old LangGraph tickets.
- [x] 3.3 Review the tracer-bullet granularity and blocking edges with the user, then publish the approved 14-ticket dependency graph including targeted `Open in Codex` behavior.

## 4. Remove the duplicate PRD

- [x] 4.1 Verify that every unique functional requirement from `microsoft-agent-framework-prd.md` is represented in the canonical spec.
- [x] 4.2 Delete `microsoft-agent-framework-prd.md` after the extraction check passes.

## 5. Validation

- [x] 5.1 Validate local Markdown links, `git diff --check`, and the absence of actionable Temporal fallback language in canonical decision and spike documents.
- [x] 5.2 Run `openspec validate separate-agent-framework-pilot-spec-and-spike --strict` and record the final documentation-only scope.
