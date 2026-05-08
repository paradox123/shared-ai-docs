**Date:** 2026-05-08
**Status:** 🔵 Implemented
**Scope:** Enforceable Agent Delivery launch evidence and real session-log references for fresh-session handoffs.

---

## Review Control Surface

- Spec-Variante: contract-heavy workflow/tooling Spec.
- Goldstandard Status: implemented.
- Ziel: Future Agent Delivery handoffs must not claim a fresh Codex session transition unless matching launch/queue evidence exists, and handoffs must no longer rely on semantic `SessionId` labels as their only session reference.
- In Scope: launcher-evidence enforcement, stale/missing launcher-evidence detection, real Codex session/log reference contract, historical/pre-launcher transition labeling, deterministic validator or harness fixture, small workflow-skill doc patches, and closeout/reporting expectations for this enforcement change.
- Out of Scope: backfilling fake launch artifacts for completed DWT sessions, changing completed DWT acceptance status, broad redesign of `AgentDeliverySessionLauncher.cs`, implementing non-Codex agent adapters, direct mutation of Codex app databases, runtime/product repository changes, and a new Parent/Child split for this small follow-up.
- Wichtigste Test-/Harness-Cases: missing launcher evidence blocks an automatic fresh-session claim; stale launcher evidence with mismatched target id or handoff path blocks; `manual_start_required` is visible but not automatic success; `blocked` and `failed` stop delivery; matching `queued` or `launched` evidence passes; handoff with only semantic `SessionId` is flagged unless marked `legacy_reconstructed` or paired with real log path/session id.
- Wichtigste Verification Commands: `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help`; targeted launcher-evidence validator or Node fixture command for valid/missing/stale/manual/blocked cases; `rg -n "Agent Delivery Session Launch/Queue Evidence|agent-delivery-session-launches|manual_start_required|legacy_reconstructed|real session" docs/doc-workflow.md skills-repo/skills`; `git diff --check`.
- Offene Entscheidungen: Keine blockierenden Entscheidungen. Historical DWT transitions are documented as pre-launcher/manual reconstruction unless a later explicit backfill spec chooses otherwise.
- Readiness Status: IMPLEMENTED / READY.

## Session Briefing

- Modus/Skill: `doc-coauthoring`, followed by `doc-review-autoresolve`.
- Source of Truth: `docs/agent-delivery-retro-review-2026-05-08.md`, `docs/doc-workflow.md`, `skills-repo/tools/AgentDeliverySessionLauncher.cs`, `skills-repo/tools/ValidateChildReadiness.cs`, and the Agent Delivery workflow skills.
- Ziel: Define the smallest implementation-ready follow-up that turns the retro finding into enforceable workflow behavior.
- Nicht-Ziele: no historical status rewrite, no broad DWT testsuite reopen, no speculative provider abstraction, no direct app database edits.
- Verification/Review: content-quality review against user intent, retro findings, launcher-evidence contract, and deterministic testability.
- Offene Entscheidungen: none.

## 1. Problem

The DocWorkflow Agent Delivery Testsuite was completed before the newly implemented Agent Delivery Session Launcher became effective as an enforced gate. The suite now documents a gap: real Codex sessions and good handoffs existed, but the delivered DWT chain did not have `_specs/agent-delivery-session-launches/**/launch-request.json` and `evidence.json` artifacts for each claimed fresh-session transition.

That is acceptable as historical pre-launcher evidence. It must not remain acceptable for future Agent Delivery work.

Two failure modes need to be closed:

1. A handoff or skill output says "fresh session started", "queued", or equivalent, but no matching launcher evidence exists.
2. A handoff records only a semantic `SessionId` such as `2026-05-08-docworkflow-agent-delivery-testsuite-dwt-s5`, without a real Codex session id, `.jsonl` log path, launcher evidence path, or explicit historical/manual marker.

## 2. Decision Freeze Pack

| Decision | Frozen Value |
|---|---|
| Enforcement target | Future Agent Delivery handoffs and delivery kickoffs. |
| Historical DWT handling | Completed DWT sessions remain accepted but are labeled as pre-launcher/manual reconstruction where discussed. No fake backfill is allowed in this change. |
| Passing automatic transition statuses | Only `queued` and `launched` with matching Target-ID and handoff path. |
| Non-automatic transition status | `manual_start_required`; visible but not an automatic transition success. |
| Blocking statuses | `blocked` and `failed`; downstream delivery must stop until resolved. |
| Session reference rule | Semantic `SessionId` alone is insufficient for future forensic evidence. Use launcher evidence, real Codex session id/log path, or explicit `legacy_reconstructed` / `manual_start_required`. |
| Implementation shape | Small workflow/tooling patch plus deterministic validator or fixture tests. |
| No-go | Do not reopen the DWT Parent/Child acceptance chain and do not synthesize historical launcher artifacts as if they existed during delivery. |

## 3. Normative Requirements

### Requirement: Automatic Fresh-Session Claims Require Launcher Evidence

Any future Agent Delivery artifact that claims a fresh session was automatically queued or launched must point to matching Agent Delivery Session Launch/Queue Evidence.

Matching evidence means:

- `launch-request.json` exists.
- `evidence.json` exists.
- The evidence target id equals the handoff target id.
- The evidence handoff path resolves to the same handoff file.
- The evidence status is `queued` or `launched`.
- The requested provider and adapter status are recorded.
- The start prompt path exists or is intentionally omitted only for a blocked secret-guard case.

If any matching condition fails, the transition must not be described as automatically queued or launched.

### Requirement: Manual, Blocked and Failed Transitions Stay Visible

`manual_start_required` is a valid state, but it is not proof of an automated transition.

`blocked` and `failed` are stop states for downstream delivery. A delivery skill may continue only after fresh matching evidence supersedes the blocked or failed evidence, or after the user explicitly changes the scope to a manual/reconstructed path.

### Requirement: Handoffs Need Real Session Evidence or an Explicit Legacy Marker

Future handoffs must not rely on semantic `SessionId` labels alone.

A handoff session reference is acceptable when at least one of these is present:

- matching launcher evidence path,
- real Codex session id plus `.codex/...jsonl` log path,
- `manual_start_required` with the manual start evidence path,
- `legacy_reconstructed` with the reconstruction source and date.

Semantic labels may remain as human-readable aliases, but not as the only forensic session reference.

### Requirement: Skills Must Consume the Gate Consistently

The workflow skills must align on the same interpretation:

| Skill / Document | Required behavior |
|---|---|
| `docs/doc-workflow.md` | Define launcher evidence as required for automatic fresh-session claims and define semantic-only `SessionId` as insufficient for future proof. |
| `spec-orchestrator` | When reporting the next leading handoff, create/require launcher evidence or label the transition manual/blocked. |
| `child-spec-hardening` | When a child becomes implementation-ready and a fresh session is recommended, produce or require queue evidence before claiming a queued transition. |
| `spec-change-delivery` | Before delivery from a handoff, check any available launcher evidence; missing evidence means manual handoff, `manual_start_required` remains visible, and `blocked`/`failed` stops the run. |
| `spec-closeout` | When closeout releases a next handoff, create/require launcher evidence or record why the next transition is manual/blocked. |
| `agent-delivery-retro-review` | Continue to treat missing or stale launcher evidence as a workflow finding. |

## 4. Expected Implementation Targets

The implementation should stay small and local.

Expected files:

- `docs/doc-workflow.md`
- `skills-repo/skills/spec-orchestrator/SKILL.md`
- `skills-repo/skills/child-spec-hardening/SKILL.md`
- `skills-repo/skills/spec-change-delivery/SKILL.md`
- `skills-repo/skills/spec-closeout/SKILL.md`
- optional `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs` or an extension to `AgentDeliverySessionLauncher.cs` / `ValidateChildReadiness.cs`
- deterministic fixtures under `tests/agent-delivery-session-launcher/` or `tests/docworkflow-agent-delivery/`

The implementation should not touch completed DWT child specs except if a documentation-only note is explicitly required by the user.

## 5. Harness Cases

| Case | Input | Expected Result |
|---|---|---|
| `launch-evidence-valid-queued` | Handoff plus launcher evidence with same target id, same handoff path and status `queued`. | Pass. Automatic queue claim allowed. |
| `launch-evidence-valid-launched` | Handoff plus launcher evidence with same target id, same handoff path and status `launched`. | Pass. Automatic launch claim allowed. |
| `launch-evidence-missing` | Handoff recommends fresh session but no launch evidence path exists. | Fail for automatic claim; allowed only as manual handoff if the output says so. |
| `launch-evidence-stale-target` | Evidence target id differs from handoff target id. | Fail. |
| `launch-evidence-stale-handoff` | Evidence handoff path differs from current handoff path. | Fail. |
| `launch-evidence-manual-required` | Evidence status is `manual_start_required`. | Warn or manual result; not automatic success. |
| `launch-evidence-blocked` | Evidence status is `blocked`. | Fail/block delivery. |
| `launch-evidence-failed` | Evidence status is `failed`. | Fail/block delivery. |
| `semantic-session-only` | Handoff has only semantic `SessionId`. | Fail for future proof unless marked `legacy_reconstructed` with source/date. |
| `legacy-reconstructed-dwt` | Handoff/report explicitly labels historical DWT transition as `legacy_reconstructed` and points to reconstruction sources. | Pass as historical/manual evidence, not as automated launch proof. |

## 6. Verification Commands

Run from `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs` unless a command states otherwise.

Preflight:

```sh
dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help
```

Gate verification after implementation:

```sh
rg -n "Agent Delivery Session Launch/Queue Evidence|agent-delivery-session-launches|manual_start_required|legacy_reconstructed|real Codex session|semantic.*SessionId" docs/doc-workflow.md skills-repo/skills
```

The implementation must add one deterministic command that exercises the harness cases in section 5. The exact command may be a `.NET` file-based validator or a Node validator following the existing testsuite style, but it must run without Codex credentials and without starting a real agent.

Expected command shape:

```sh
dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture tests/agent-delivery-session-launcher/fixtures/launch-evidence
```

or:

```sh
node tests/agent-delivery-session-launcher/validators/launch-evidence-validator.js tests/agent-delivery-session-launcher/fixtures/launch-evidence
```

Final hygiene:

```sh
git diff --check
```

## 7. Acceptance Criteria

1. Future automatic fresh-session claims require matching launcher evidence with status `queued` or `launched`.
2. Missing launcher evidence no longer silently passes as automatic transition proof.
3. `manual_start_required` remains visible and is not reported as automated success.
4. `blocked` and `failed` launch evidence block downstream delivery.
5. Semantic-only `SessionId` is rejected for future forensic proof unless explicitly marked as historical/manual reconstruction.
6. Historical DWT transitions are not rewritten as if launcher evidence existed during delivery.
7. At least one deterministic harness or validator proves valid, missing, stale, manual, blocked, failed and semantic-only cases.
8. Workflow skill docs are synchronized so orchestration, hardening, delivery, closeout and retro all use the same gate.
9. Verification commands are runnable from the declared CWD and do not require Codex credentials or launching a real fresh session.
10. The final implementation reports a clear readiness verdict and any historical/manual residue without hiding it.

## 8. Content Quality Review

Review result after hardening: no content blockers.

- Correctness/domain fit: Pass. The spec targets the exact retro gap: launcher evidence and real session/log references.
- Scope discipline: Pass. The spec excludes DWT status rewrites, fake backfills and broad launcher redesign.
- Completeness: Pass. Normal, stale, missing, manual, blocked, failed and legacy-reconstructed paths are covered.
- Consistency: Pass. Status meanings match the existing Agent Delivery launcher contract.
- Verifiability: Pass with one implementation-time choice: the validator may be .NET or Node, but must be deterministic and credential-free.
- Traceability: Pass. Requirements trace to the 2026-05-08 retro report and current workflow docs.
- Readiness: IMPLEMENTATION READY for one bounded workflow/tooling change.

## 8.1 Implementation Evidence

Implementation mode: direct, without OpenSpec change.

Changed artifact groups:

- Workflow rule sync: `docs/doc-workflow.md`.
- Skill rule sync: `skills-repo/skills/spec-orchestrator/SKILL.md`, `skills-repo/skills/child-spec-hardening/SKILL.md`, `skills-repo/skills/spec-change-delivery/SKILL.md`, `skills-repo/skills/spec-closeout/SKILL.md`, `skills-repo/skills/agent-delivery-retro-review/SKILL.md`.
- Deterministic validator: `skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs`.
- Harness fixtures: `tests/agent-delivery-session-launcher/fixtures/launch-evidence/**`.
- Harness documentation: `tests/agent-delivery-session-launcher/README.md`.

Verification checklist:

| Command | Status | Evidence |
|---|---|---|
| `dotnet run skills-repo/tools/AgentDeliverySessionLauncher.cs -- --help` | ran/pass | Help output lists `--handoff`, `--target-id`, `--agent`, `--mode`, `--control-index`, `--out`, `--dry-run`, and `--help`. |
| `dotnet run skills-repo/tools/ValidateAgentDeliveryLaunchEvidence.cs -- --fixture tests/agent-delivery-session-launcher/fixtures/launch-evidence` | ran/pass | 10 cases passed: valid queued/launched, missing, stale target, stale handoff, manual required, blocked, failed, semantic-only session id, and legacy reconstructed. |
| `rg -n "Agent Delivery Session Launch/Queue Evidence\|agent-delivery-session-launches\|manual_start_required\|legacy_reconstructed\|real Codex session\|semantic.*SessionId" docs/doc-workflow.md skills-repo/skills` | ran/pass | Matches found in workflow docs and all relevant Agent Delivery skills. |
| `git diff --check` | ran/pass | No whitespace errors. |

Runtime validation: not applicable. This change is docs/tooling/validator-only and does not define Docker, service runtime, or NCG backend build gates.

Acceptance evidence:

1. Matching `queued` and `launched` evidence passes in `launch-evidence-valid-queued` and `launch-evidence-valid-launched`.
2. Missing launcher evidence fails in `launch-evidence-missing`.
3. `manual_start_required` returns manual residue, not automatic success, in `launch-evidence-manual-required`.
4. `blocked` and `failed` block in `launch-evidence-blocked` and `launch-evidence-failed`.
5. Semantic-only `SessionId` fails in `semantic-session-only`.
6. Explicit historical `legacy_reconstructed` passes only as historical/manual evidence in `legacy-reconstructed-dwt`.
7. Workflow and skill docs now state the shared gate.
8. No completed DWT child spec or archive was rewritten.

## 9. Mini-Retro

- Was wurde entschieden? The follow-up should be a small enforcement spec, not a new Parent/Child scope.
- Was wurde geaendert? This spec turns the retro findings into normative requirements, harness cases and acceptance criteria.
- Was bleibt offen? No blocking decisions.
- Welche Evidenz/Verification fehlt? None for this direct tooling change.
- Session-/Kontextzustand: Implementation complete; future Agent Delivery handoffs can use the new validator/gate.

## History

| Date | Actor | Change |
|---|---|---|
| 2026-05-08 | Codex | Created, reviewed and hardened the Agent Delivery Launch Evidence Enforcement spec from the DWT retro findings. |
| 2026-05-08 | Codex | Implemented the direct-mode launch evidence enforcement validator, fixtures, workflow docs and skill synchronization; verification passed. |

SessionId: 2026-05-08-agent-delivery-launch-evidence-enforcement
