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
  counter: 2
  signal: Green status was reported before target-runtime verification was truly complete.
  latest_evidence: /Users/dh/.codex/sessions/2026/04/16/rollout-2026-04-16T08-21-54-019d94f4-0b73-71f2-8640-05bac38b653a.jsonl
  suggested_skill_or_playbook: Require strict verification status labels and target-runtime evidence before marking done.

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
