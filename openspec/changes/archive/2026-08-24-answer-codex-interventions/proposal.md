## Why

The pilot already knows when implementation or repair cannot safely continue, but the resulting human handoff is only a terminal projection and cannot be answered from Codex. A durable, app-visible intervention channel is needed so Daniel can supply the missing decision once and the same LangGraph run can resume without duplicated work.

## What Changes

- Add one schema-validated, redacted intervention request shared by initial implementation, independent review, and findings repair.
- Persist the request before handoff, expose it in workflow read-back, and pause only its existing run while preserving all run, worktree, branch, pull-request, head, evidence, review, repair, feedback, and recovery identities.
- Publish only intervention requests as clearly named Codex App threads through the documented stable app-server protocol surface, with experimental capabilities and transports disabled; keep `exec-server` excluded.
- Correlate one later user answer to the open request, reject re-answer/re-delivery effects idempotently, and resume the same workflow phase and writing context.
- Invalidate head-bound verification after an answer-driven source change and rerun deterministic checks plus all required fresh independent reviews for the new head.
- Add public-seam behavior coverage and a controlled real-pilot acceptance procedure using a dedicated test issue; do not use or alter ProBara CRM issue #2.

## Capabilities

### New Capabilities
- `codex-intervention-continuation`: Durable intervention requests, stable Codex App handoff, exactly-once answer correlation, same-run continuation, and public read-back evidence.

### Modified Capabilities
- `isolated-issue-worker`: Initial implementation can return a structured intervention instead of synthesizing a product decision or continuing indefinitely.
- `independent-pr-review-verification`: Any independent review axis can return a structured intervention while remaining read-only and head-bound.
- `bounded-review-repair`: A policy-authorized interruption becomes an answerable durable request rather than only a terminal label projection.
- `workflow-crash-recovery`: Recovery preserves intervention delivery, waiting, answer, and continuation operations without duplicate external effects.

## Impact

- **Write set:** `langgraph-github-issue-pilot/src/github_issue_pilot/`, its versioned JSON contracts, public-seam and adapter contract tests, pilot documentation, and this OpenSpec change.
- **Runtime boundaries:** SQLite/LangGraph persistence, the existing HTTP workflow read-back, Codex CLI app-server stdio using only its stable non-experimental protocol subset, and the existing Git/GitHub adapters.
- **Operations:** Production configuration gains an explicit Codex intervention adapter setting and bounded polling/reconciliation behavior. Normal implementation and review workers remain non-interactive `codex exec` processes.
- **Direct verification:** Strict OpenSpec validation and local tests precede one separately identified test issue through the productive GitHub/Cloudflare/pilot path, a decisive Codex App screenshot, one answer, same-run public read-back, and controlled issue closure without merge or deployment.
