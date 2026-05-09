**Date:** 2026-05-09
**Status:** 🟢 Accepted
**Scope:** Integrate post-orchestration next-step tooling into the `spec-orchestrator` skill with minimal prose.

---

## Review Control Surface

- Spec-Variante: Workflow/skill integration spec.
- Goldstandard Status: implementation-ready workflow/skill integration spec.
- Ziel: Reduce `spec-orchestrator/SKILL.md` prose by delegating the post-orchestration transition decision to `EvaluateOrchestrationNextStep.cs`.
- In Scope: skill instructions for when to run the tool, how to interpret JSON verdicts, how to report final status tokens, and how to stop before delivery.
- Out of Scope: building the evaluator tool, changing child specs, broad skill rewrite, changing `child-spec-hardening`, launching agents.
- Wichtigste Test-/Harness-Cases: `ORCH-SKILL-RUNS-EVALUATOR`, `ORCH-SKILL-FOLLOWS-HARDENING-VERDICT`, `ORCH-SKILL-NO-IMPLEMENTATION-STILL-HARDENS`, `ORCH-SKILL-FINAL-WORDING`.
- Wichtigste Verification Commands: `rg` for evaluator invocation and status tokens in `skills-repo/skills/spec-orchestrator/SKILL.md`; focused `dotnet run` evaluator smoke against a temporary Child Index pack; `git diff --check`.
- Offene Entscheidungen: none.
- Readiness Status: IMPLEMENTATION READY.

## Goal

Make the orchestrator skill smaller and less interpretive. The skill should create/update orchestration artifacts, run the evaluator tool, and follow the tool verdict instead of restating every transition rule in prose.

## In Scope

- Add a short "Tool Gate" section to `spec-orchestrator/SKILL.md`.
- Replace detailed hardening trigger prose with a command invocation and terse verdict-following rules.
- Require final answers to include the evaluator's `final_status_token`.
- State that `--no-implementation` must be passed when the user forbids implementation.

## Out of Scope

- No runtime code implementation.
- No changes to the evaluator tool contract unless a later hardening pass finds a blocker.
- No large rewrite of unrelated orchestrator sections.
- No changes to MD-E2E child specs or downstream delivery tools.

## Tool Contract

After `spec-orchestrator` creates or updates a Child Index and Hardening Queue, it must run the existing evaluator:

```sh
dotnet run /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/tools/EvaluateOrchestrationNextStep.cs -- \
  --pack <orchestration-pack-or-index.md> \
  --repo <target-repo-or-workspace> \
  --child-index-section "Child Index" \
  --intent <expects-hardening|expects-implementation-ready|hardening-queue-only|orchestration-only|stop-before-hardening|unknown> \
  --format json
```

Add `--no-implementation` when the user forbids runtime/product implementation. This flag must not suppress `child-spec-hardening`; it only prevents routing to `spec-change-delivery`.

The skill must follow the JSON verdict:

| Tool field | Required skill behavior |
|---|---|
| `errors` non-empty or exit `2` | Stop, report `final_status_token`, and keep orchestration blocked until the Child Index/tool input is fixed. |
| `required_next_skill = child-spec-hardening` | Start or hand off to `child-spec-hardening` for `first_unblocked_child`, unless the user explicitly requested `orchestration-only` or `stop-before-hardening`. |
| `required_next_skill = spec-change-delivery` | Stop at the implementation handoff unless the user explicitly requested implementation and all readiness gates remain valid. |
| `required_next_skill = spec-orchestrator` | Fix or synchronize the orchestration artifacts before any hardening/delivery step. |
| `required_next_skill = none` | Report no required next workflow step and include the tool's status token. |

Final answers from `spec-orchestrator` must include the evaluator's `final_status_token` and avoid implying workflow advancement when only a queue was created.

## Acceptance Criteria

1. `spec-orchestrator/SKILL.md` instructs agents to run `EvaluateOrchestrationNextStep.cs` after creating/updating a Child Index and Hardening Queue.
2. The skill maps `required_next_skill = child-spec-hardening` to actually starting child hardening unless the user explicitly stopped before hardening.
3. The skill maps `required_next_skill = spec-change-delivery` to a stop unless the user requested implementation and readiness gates are valid.
4. The final response must distinguish queue creation from workflow advancement using the tool's status token.
5. The patch removes or shortens duplicated prose when the tool covers the rule.
6. The skill keeps existing Child Index, handoff, launch-evidence, and readiness guardrails intact except for prose shortened by the tool gate.

## Verification Commands

```sh
rg -n "EvaluateOrchestrationNextStep|final_status_token|required_next_skill|--no-implementation" skills-repo/skills/spec-orchestrator/SKILL.md
tmp_pack="$(mktemp)"; cat > "$tmp_pack" <<'EOF'
## Child Index
| Child | Child Spec | Parent Coverage | Readiness / Hardening Verdict | Session Handoff | OpenSpec / Ledger | Dependencies | Allowed Write-Set | Verification | Evidence / Closeout | Backlog / Re-entry | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | child.md | P1 | NEEDS HARDENING | handoff.md | change | none | child.md | rg gate | none | none | harden |
EOF
dotnet run skills-repo/tools/EvaluateOrchestrationNextStep.cs -- --pack "$tmp_pack" --repo . --intent expects-hardening --format json
rm "$tmp_pack"
git diff --check
```

## Closeout Evidence

- OpenSpec Change: `agent-delivery-spec-orchestrator-gate-integration`
- OpenSpec Archive: `openspec/changes/archive/2026-05-09-agent-delivery-spec-orchestrator-gate-integration/`
- Canonical Spec: `openspec/specs/docworkflow-agent-delivery-testsuite/spec.md`
- Closeout Verification:
  - `rg -n "EvaluateOrchestrationNextStep|final_status_token|required_next_skill|--no-implementation" skills-repo/skills/spec-orchestrator/SKILL.md`: passed.
  - Temporary Child Index evaluator smoke: passed with `required_next_skill = child-spec-hardening`, `first_unblocked_child = S1`, and `final_status_token = hardening_started_required`.
  - `openspec validate agent-delivery-spec-orchestrator-gate-integration --strict`: passed before archive.
  - `openspec archive -y agent-delivery-spec-orchestrator-gate-integration`: passed; canonical spec updated.
  - `git diff --check`: passed after whitespace cleanup.

## History

| Date | SessionId | Change |
|---|---|---|
| 2026-05-09 | workflow-tooling-specs-initial | Initial draft spec. |
| 2026-05-09 | spec-orchestrator-gate-integration | Hardened against the accepted evaluator CLI and marked implementation-ready. |
| 2026-05-09 | spec-orchestrator-gate-integration | Implemented minimal Tool Gate integration and recorded OpenSpec evidence. |
| 2026-05-09 | spec-orchestrator-gate-integration-closeout | Accepted change, archived OpenSpec, and synchronized canonical testsuite spec. |
