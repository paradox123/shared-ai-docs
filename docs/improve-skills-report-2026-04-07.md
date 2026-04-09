# Improve Skills Report

## Run Summary
- Processed window: 2026-03-30T00:00:00Z to 2026-04-01T09:14:15.006Z
- Sessions reviewed: 3 (`67b5a7b4-812f-4429-95a1-8ae9804b32ac`, `82d9f987-ab82-448f-962d-253fe1c985c9`, `286a6556-ab40-4fa3-8370-decc76dc53d9`)
- Existing skills updated: 2
- New candidate counters changed: 2

## Skill Updates
- [CORE] scope=general reason=Sensitive values were echoed in tool output and final summaries during Codex LiteLLM setup change=Added a `Secret Hygiene (CRITICAL)` section with explicit redaction and safe-verification rules evidence=session `286a6556-ab40-4fa3-8370-decc76dc53d9` exposed full `LITELLM_MASTER_KEY` and `OPENAI_API_KEY` in command output and response text
- [improve-skills] scope=general reason=Current workflow assumed `/memories` and `.claude` paths that were not consistently available in the active environment change=Added path fallback rules for skill roots, cursor file, and candidate memory storage with explicit report disclosure evidence=This run required manual fallback from missing `/memories` and dual `.agents`/`.claude` skill roots before execution could proceed cleanly

## New Or Escalated Candidates
- [codex-local-config-discovery-playbook] scope=project:ncg-backend counter=1 signal=Repeated path discovery (`which codex`, probing `~/.local/bin`, `/usr/local/bin`, app support folders) recommendation=Create a project playbook with fixed discovery order and a minimal command set
- [litellm-codex-responses-compat-check] scope=general counter=1 signal=Compatibility issue (`/responses` websocket 403/401) surfaced only after config edits and verification retries recommendation=Add preflight compatibility checks before mutating user shell/config files

## Notable Discovery Patterns
- session=286a6556-ab40-4fa3-8370-decc76dc53d9 pattern=Secret values were surfaced directly in stdout and response summaries classification=improve-existing-skill note=Hardened CORE with explicit redaction and safe verification rules
- session=286a6556-ab40-4fa3-8370-decc76dc53d9 pattern=Binary/config location discovery relied on many ad-hoc filesystem probes classification=project-scoped-playbook note=Track as `codex-local-config-discovery-playbook`
- session=286a6556-ab40-4fa3-8370-decc76dc53d9 pattern=Provider compatibility was validated late, causing avoidable retry loops classification=new-skill-candidate note=Track as `litellm-codex-responses-compat-check`

## Deferred Items
- item=Session `82d9f987-ab82-448f-962d-253fe1c985c9` had startup/API failure but no execution sequence reason=Insufficient evidence for skill updates beyond environment-level incident handling
- item=Session `67b5a7b4-812f-4429-95a1-8ae9804b32ac` mostly contained readiness chatter reason=No recurring tool-discovery or retry pattern observed

## Cursor Update
- newest_session_timestamp: 2026-04-01T09:14:15.006Z
- last-run file updated: yes (`/Users/dh/.agents/skills/improve-skills/last-run.json`, `/Users/dh/.claude/skills/improve-skills/last-run.json`)
