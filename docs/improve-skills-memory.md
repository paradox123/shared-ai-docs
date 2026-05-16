# Improve Skills Memory

- name: decision-freeze-pack
  scope: general
  counter: 1
  signal: Late architecture and ops decisions increased rework.
  latest_evidence: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/improve-skills-report-2026-04-03.md
  suggested_skill_or_playbook: Add a mandatory pre-apply decision freeze checklist.

- name: openspec-ssot-discipline
  scope: general
  counter: 1
  signal: Hybrid execution between OpenSpec and ad-hoc edits reduced predictability.
  latest_evidence: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/improve-skills-report-2026-04-03.md
  suggested_skill_or_playbook: Enforce explicit OpenSpec mode selection for medium and large changes.

- name: runtime-proof-gate
  scope: general
  counter: 4
  signal: Delivery status remained formally correct (`NOT READY`) but foundational runtime blockers were not escalated early enough, causing user-perceived mismatch between requested implementation and delivered scope.
  latest_evidence: /Users/dh/.codex/sessions/2026/05/01/rollout-2026-05-01T10-42-01-019de2b3-b4c3-7883-b237-9b4a2078c13e.jsonl
  suggested_skill_or_playbook: Enforce an early foundational-runtime reality gate and explicit blocker decision before continuing implementation workflows.

- name: verification-command-determinism
  scope: general
  counter: 1
  signal: Verification command blocks can fail for non-functional reasons (platform-specific command semantics, branch-history scope guards on long-lived branches, startup timing races), creating avoidable rework.
  latest_evidence: /Users/dh/.codex/sessions/2026/05/01/rollout-2026-05-01T10-42-01-019de2b3-b4c3-7883-b237-9b4a2078c13e.jsonl
  suggested_skill_or_playbook: Add explicit verification-command authoring constraints (portability/readiness/baseline semantics) in doc-coauthoring and enforce them in spec-change-delivery.

- name: codex-local-config-discovery-playbook
  scope: project:ncg-backend
  counter: 1
  signal: Multiple filesystem probes were used to rediscover Codex binary and config locations.
  latest_evidence: /Users/dh/.claude/projects/-Users-dh-Documents-Dev-NCG-ncg-backend-backend-sources/286a6556-ab40-4fa3-8370-decc76dc53d9.jsonl
  suggested_skill_or_playbook: Add a deterministic local Codex configuration playbook with fixed path order and checks.

- name: litellm-codex-responses-compat-check
  scope: general
  counter: 1
  signal: Responses API incompatibility was discovered late after broad config mutation.
  latest_evidence: /Users/dh/.claude/projects/-Users-dh-Documents-Dev-NCG-ncg-backend-backend-sources/286a6556-ab40-4fa3-8370-decc76dc53d9.jsonl
  suggested_skill_or_playbook: Add a preflight compatibility check step before writing Codex LiteLLM config.

- name: gate-environment-truth-labeling
  scope: general
  counter: 1
  signal: A local compose rehearsal was temporarily communicated as if it were a gate-valid Hetzner runtime run.
  latest_evidence: /Users/dh/.codex/sessions/2026/04/16/rollout-2026-04-16T08-21-54-019d94f4-0b73-71f2-8640-05bac38b653a.jsonl
  suggested_skill_or_playbook: Add explicit ran-target vs ran-rehearsal labeling to spec-change-delivery and enforce verdict downgrade when mismatched.

- name: watcher-vs-functional-proof-separation
  scope: general
  counter: 1
  signal: Pipeline watcher success created ambiguity about whether the required Store token endpoint test had actually run.
  latest_evidence: /Users/dh/.codex/sessions/2026/04/16/rollout-2026-04-16T08-21-54-019d94f4-0b73-71f2-8640-05bac38b653a.jsonl
  suggested_skill_or_playbook: Add hard watcher boundaries that separate pipeline health evidence from explicit functional endpoint verification.

- name: blocker-first-runtime-prereq-gate
  scope: general
  counter: 1
  signal: The run discovered missing core prerequisites (`rag` CLI/runtime) after execution had already advanced deeply into verification paperwork, leading to avoidable frustration.
  latest_evidence: /Users/dh/.codex/sessions/2026/04/21/rollout-2026-04-21T07-49-37-019dae96-456d-76e2-b1e5-562f1534a6cd.jsonl
  suggested_skill_or_playbook: Add a mandatory early stop-and-choose gate for missing foundational runtime prerequisites in spec-change-delivery.

- name: parent-child-spec-orchestration
  scope: general
  counter: 1
  signal: Scope splitting helped delivery, but child specs, parent coverage, backlog re-entry, and parallel execution ownership were not consistently enforced by the workflow skills.
  latest_evidence: /Users/dh/.codex/sessions/2026/05/05/rollout-2026-05-05T17-48-36-019df8d3-b142-7c22-9c48-0d755090556b.jsonl
  suggested_skill_or_playbook: Add parent/child orchestration rules to doc-workflow and delivery skills: coverage matrix, child readiness envelope, backlog trigger/done signal, disjoint write-set lane matrix, and shared-file integration owner.

- name: agent-delivery-launch-evidence
  scope: general
  counter: 1
  signal: The DocWorkflow Agent Delivery Testsuite used strong persisted handoffs and real Codex sessions, but historical DWT fresh-session transitions had no `_specs/agent-delivery-session-launches/**/launch-request.json` or `evidence.json` artifacts.
  latest_evidence: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/agent-delivery-retro-review-2026-05-08.md
  suggested_skill_or_playbook: Treat Agent Delivery Session Launch/Queue Evidence as the default proof for future fresh-session transitions; missing historical evidence should be labeled as reconstructed/manual instead of automated.

- name: session-id-crosswalk
  scope: general
  counter: 1
  signal: Semantic handoff `SessionId` labels were useful for humans but not enough to directly locate real Codex `.jsonl` session logs during the DWT retro.
  latest_evidence: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/agent-delivery-retro-review-2026-05-08.md
  suggested_skill_or_playbook: Handoffs and launcher evidence should store real session/log paths when available, or explicitly state that the transition is pre-launcher/manual.

- name: post-archive-replay-contract
  scope: general
  counter: 1
  signal: The DWT-S5 active-child runtime command became stale after OpenSpec archive, and parent closeout had to replace it with archive-presence plus canonical spec validation.
  latest_evidence: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/agent-delivery-retro-review-2026-05-08.md
  suggested_skill_or_playbook: Closeout must preserve pre-archive commands as historical evidence and publish a separate post-archive/current replay command set.

- name: codex-automation-bootstrap-paths
  scope: general
  counter: 4
  signal: Multiple automation runs rediscovered how to resolve `~/.codex`, `memory.md`, and session-log anchors when `$CODEX_HOME` was unset, causing blank-path probes and fallback churn.
  latest_evidence: /Users/dh/.codex/sessions/2026/05/16/rollout-2026-05-16T09-02-06-019e2f97-9ffb-7d33-9649-0526b6d6a9a3.jsonl
  suggested_skill_or_playbook: Strengthen `improve-skills` and `build-codex-automations` with deterministic `$CODEX_HOME` fallback, explicit `memory.md` semantics, and a no-`/automations` probe rule.

- name: ncg-backend-wrapper-git-root
  scope: project:ncg-backend
  counter: 2
  signal: Agents start in the wrapper folder and hit `fatal: not a git repository` before switching to `backend/`, which repeats avoidable structure discovery.
  latest_evidence: /Users/dh/.codex/sessions/2026/05/16/rollout-2026-05-16T09-02-01-019e2f97-8be2-73c1-96c9-11e63fc73f6a.jsonl
  suggested_skill_or_playbook: Add an `ncg-backend` playbook note that git-root commands run in `backend/` while solution/runtime commands still anchor in `backend/sources`.
