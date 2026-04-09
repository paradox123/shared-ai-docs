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
  counter: 1
  signal: Implementation confidence remained low until runtime proof was provided.
  latest_evidence: /Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/improve-skills-report-2026-04-03.md
  suggested_skill_or_playbook: Require runtime and smoke evidence before marking done.

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
