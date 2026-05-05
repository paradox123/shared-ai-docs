# Improve Skills Report

## Run Summary
- Processed window: 2026-04-22T06:31:22.442Z -> 2026-05-01T11:11:57.351Z
- Sessions reviewed:
  - /Users/dh/.codex/sessions/2026/04/25/rollout-2026-04-25T16-41-57-019dc517-1587-7860-a754-7e2ee215f22e.jsonl
  - /Users/dh/.codex/sessions/2026/05/01/rollout-2026-05-01T10-42-01-019de2b3-b4c3-7883-b237-9b4a2078c13e.jsonl
- Existing skills updated: 2 (`spec-change-delivery`, `doc-coauthoring`)
- New candidate counters changed:
  - `runtime-proof-gate`: 3 -> 4
  - `verification-command-determinism`: +1 (new)

## Skill Updates
- [spec-change-delivery] scope=general reason=Spec-16 execution repeatedly produced verification churn caused by non-functional command fragility (`cp -n` platform behavior, branch-history scope guard, compose startup race). change=Added non-negotiables for verification command portability, benign-state handling, scope-guard baseline strategy, and mandatory runtime readiness strategy; added verify-step readiness note. evidence=/Users/dh/.codex/sessions/2026/05/01/rollout-2026-05-01T10-42-01-019de2b3-b4c3-7883-b237-9b4a2078c13e.jsonl (notable lines around 368-394 show repeated `failed` statuses, `copy_secrets_rc:1`, `health/login/oidc` 502, and out-of-scope guard history spill).
- [doc-coauthoring] scope=general reason=Spec authoring currently allows verification blocks that are syntactically complete but operationally brittle, leading to repeated operator rework later. change=Added `Verification Command Authoring Guardrail` section with 5 mandatory rules (platform context, benign-state behavior, scope baseline semantics, runtime readiness, explicit success criteria) plus marker templates for unresolved command quality gaps. evidence=/Users/dh/.codex/sessions/2026/05/01/rollout-2026-05-01T10-42-01-019de2b3-b4c3-7883-b237-9b4a2078c13e.jsonl (verification loop required multiple manual remediations outside strict block).

## New Or Escalated Candidates
- [runtime-proof-gate] scope=general counter=4 signal=The verdict can remain formally correct (`NOT READY`) while command-quality defects in verification blocks still consume significant user/operator time. recommendation=Keep blocker-first runtime gating and combine it with command-quality gating before implementation starts.
- [verification-command-determinism] scope=general counter=1 signal=Verification commands failed due to platform semantics and startup timing rather than product behavior. recommendation=If this repeats in another session, extract a dedicated reusable `verification-command-hardening` playbook or skill.

## Notable Discovery Patterns
- session=019de2b3-b4c3-7883-b237-9b4a2078c13e pattern=Scope guard used `origin/develop...HEAD` and therefore failed because of long-lived branch history unrelated to current working-tree scope. classification=improve-existing-skill note=Addressed by adding scope-baseline strategy rule and long-lived-branch fallback requirement.
- session=019de2b3-b4c3-7883-b237-9b4a2078c13e pattern=Compose startup checks were run before deterministic readiness stabilization, producing transient 502/404 failures that cascaded into downstream token checks. classification=improve-existing-skill note=Addressed by explicit readiness strategy requirement.
- session=019de2b3-b4c3-7883-b237-9b4a2078c13e pattern=`cp -n` in preflight failed on already-existing targets in this operator environment, causing false-negative command status. classification=improve-existing-skill note=Addressed by benign-state handling rule.
- session=019dc517-1587-7860-a754-7e2ee215f22e pattern=Build-optimization investigation used relevant workflow and did not show verification-command fragility. classification=no-action note=Reviewed for window completeness; no counter change for verification issues.

## Deferred Items
- item=Automated static checker for verification blocks in specs (portability/readiness/baseline lint) reason=High leverage but requires tooling beyond SKILL.md/doc updates.
- item=Project-specific runtime readiness helper script for STS compose smoke checks reason=Useful to reduce repeated manual retries, but currently outside this skill-only pass.

## Cursor Update
- newest_session_timestamp: 2026-05-01T11:11:57.351Z
- last-run file updated: /Users/dh/.agents/skills/improve-skills/last-run.json
