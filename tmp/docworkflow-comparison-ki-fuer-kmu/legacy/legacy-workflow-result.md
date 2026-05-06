# Legacy Workflow Test: KI fuer KMU Free Entry v2

## Session Briefing

- Modus/Skill: Workflow 1 / `refine-plan` simulation.
- Source of Truth: `_specs/2026-05-04-free-entry-v2-master-spec.md`.
- Ziel: Die Parent/Master Spec als planbares Gesamtvorhaben in einen status-bearing implementation plan uebersetzen.
- Nicht-Ziele: Kein Spec Sizing Gate als fuehrende Automatik, keine Child-Hardening Queue, keine Runtime-Implementierung.
- Erwarteter Output: Iterativer Plan mit `[DONE]`, `[PENDING]`, `[BLOCKED]`, Verification Cases und Open Items.

## Legacy Routing

Der User hat fuer diesen Test explizit Workflow 1 gewaehlt. Deshalb bleibt `refine-plan` der fuehrende Plan-Ledger, obwohl der Scope nach heutigem Sizing Gate oversized waere.

Verdict: **PLAN CREATED, NOT IMPLEMENTATION READY AS ONE UNIT**

Grund: Die Master Spec ist zu breit fuer eine robuste direkte Umsetzung in einem Run. Der Legacy-Workflow kann das sichtbar machen, aber er erzeugt keinen automatisch session-faehigen Child-Schnitt.

## Iteration 1: Gesamtplan Aus Master Spec

### Actions

1. `[DONE]` Repo Freeze / Legacy Quarantine nachvollziehen.
   - Evidence: S0 child spec existiert mit Status `🔵 Implemented`.
   - Gap: Kein formaler Accepted-Status im Child Index.

2. `[DONE]` Vertikalen Architektur-Spike als technische Baseline nutzen.
   - Evidence: S1 child spec existiert mit Status `🟢 Accepted`.
   - Verification Pattern: .NET Build/Test, lokale Harness, Docker-Harness.

3. `[DONE]` Survey Delivery / Answer Handoff als akzeptierte Grundlage nutzen.
   - Evidence: S2 child spec existiert mit Status `🟢 Accepted`.
   - Verification Pattern: Survey service, Handoff, Import, Retention, Redaction.

4. `[PENDING]` S3 Content Bundle / Managed-AI Channel implementieren.
   - Scope: Bundle manifest, content sets, signature/hash, entitlement, managed update metadata, plugin baseline, optional Git path.
   - Verification: Build/Test, local S3 harness, Docker S3 harness, secret leak assertions.
   - Risk: S3 spec ist stark, aber nach neuem Standard fehlen Review Control Surface, Parent Scope Conformance, Dependencies/Write-Set und Closeout Sync Targets.

5. `[PENDING]` S4 Provider Activation Guides implementieren.
   - Scope: Provider matrix, guide freshness, official links, readiness test, credential redaction.
   - Risk: Aktuelle provider-spezifische Details koennen externe Recherche brauchen.

6. `[PENDING]` S5 Survey v2 Content implementieren.
   - Scope: A/B/C variants, common core, KRITIS conditional routing, survey rendering, local fallback.
   - Risk: Final wording and question identity/versioning need hardening before implementation.

7. `[PENDING]` S6 ROI/RAG Runtime implementieren.
   - Scope: RAG status, source status, ROI assumptions, report contract, LLM readiness guard.
   - Dependency: S4 provider readiness, S5 survey content, S3 workbench layout.

8. `[PENDING]` S7 Docker/Safe Harness implementieren.
   - Scope: Cross-slice control-flow cases, exit codes, manifest assertions, secret leak checks, Docker/Compose gate.
   - Dependency: S3-S6 contracts should stabilize first.

9. `[BLOCKED]` Single-run direct implementation.
   - Blocker: Scope spans many domains, multiple verification cycles, and several child-level contracts.
   - Legacy handling: Implement only one tranche at a time despite this monolithic plan.

## Verification Cases

| Case | Legacy Plan Coverage | Status |
|---|---|---|
| S3 build/test/local/docker harness | planned | pending |
| Provider readiness without secret leakage | planned | pending |
| Survey A/B/C rendering and routing | planned | pending |
| ROI/RAG blocked/prepared/report states | planned | pending |
| Cross-flow Docker/Safe Harness replay | planned | pending |
| Parent coverage after each tranche | mentioned | weak, manual |

## Open Items

1. `[MISSING SPEC: S3 parent conformance and write-set]`
2. `[MISSING SPEC: S4 provider-guide freshness and source verification policy]`
3. `[MISSING SPEC: S5 survey fixture and question identity contract]`
4. `[MISSING SPEC: S6 report/RAG state machine and blocked-output contract]`
5. `[MISSING SPEC: S7 cross-slice harness matrix]`
6. `[DECISION SPEC: whether S0 should be formally accepted or treated as implemented prerequisite]`

## Legacy Workflow Outcome

Strengths:

- Fast to produce a single visible plan.
- Easy to see what is done vs pending.
- Good for small or already bounded changes.

Weaknesses in this test:

- The plan becomes a second control surface beside the already existing child index.
- Parent coverage is only manually mentioned, not mechanically guarded.
- No automatic child hardening occurs before implementation.
- A future implementation agent could still pick S3 directly and miss parent conformance/write-set gaps.
- Long context is still concentrated in one thread, so the original context-compression risk remains.

## Final Verdict

`NOT IMPLEMENTATION READY AS ONE LEGACY RUN`

Smallest safe legacy next step: treat S3 as the next explicit tranche and manually harden its missing spec gaps before coding. This is functionally close to the new workflow, but with less automation and weaker handoff control.

## History

| Date | Iteration | Author | Delta |
|---|---:|---|---|
| 2026-05-06 | 1 | Codex | Legacy workflow test plan generated from the copied KI fuer KMU Free Entry v2 Master Spec. |
