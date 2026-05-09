**Date:** 2026-05-09
**Status:** 🟡 Spec
**Scope:** .NET 10 validator for Agent Delivery orchestration packs.

---

## Review Control Surface

- Spec-Variante: Tool delivery spec.
- Goldstandard Status: first draft.
- Ziel: Create `skills-repo/tools/ValidateOrchestrationPack.cs` to validate Child Index, Hardening Queue, handoff pointers, status consistency, and honest orchestration claims.
- In Scope: structural validation, consistency validation, handoff existence checks, status/next-action mismatch findings, optional JSON report.
- Out of Scope: deciding the next workflow step, generating handoffs, validating implementation readiness, launching agents.
- Wichtigste Test-/Harness-Cases: `ORCH-PACK-VALID`, `ORCH-PACK-MISSING-HANDOFF`, `ORCH-PACK-STALE-NEXT-ACTION`, `ORCH-PACK-COMPRESSED-INDEX`, `ORCH-PACK-FALSE-ADVANCEMENT-CLAIM`.
- Wichtigste Verification Commands: future `dotnet run ...ValidateOrchestrationPack.cs -- --pack <fixture> --repo <repo>`; `git diff --check`.
- Offene Entscheidungen: Exact false-advancement wording heuristics should be hardened later.
- Readiness Status: DRAFT; needs hardening before implementation.

## Goal

Provide a deterministic validator for orchestration artifacts so the agent does not have to manually inspect every table and handoff relationship.

## In Scope

- Validate the exact operational Child Index columns.
- Validate every row has a stable child id, child spec path, verdict, handoff pointer, dependencies, write-set, verification, evidence/closeout and next action.
- Validate referenced handoff files exist and mention the same child id.
- Detect obvious stale or contradictory verdict/next-action pairs.
- Detect claims that hardening, delivery, closeout, launch or queue happened without matching evidence.

## Out of Scope

- No mutation of packs or handoffs.
- No replacement for `ValidateChildReadiness.cs`.
- No natural language proof of all final answer wording.

## Acceptance Criteria

1. Valid orchestration fixture exits `0`.
2. Missing handoff exits `1` with a precise finding.
3. Compressed or aliased Child Index exits `1` unless explicitly allowed.
4. A pack that says all children are ready while rows say `NEEDS HARDENING` exits `1`.
5. Output can be plain text or JSON via `--format`.

## Verification Commands

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/ValidateOrchestrationPack.cs -- --help
git diff --check
```

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |

