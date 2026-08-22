# Pre-Implementation Evidence Matrix

Created before runtime code changes on 2026-08-21. Each row maps an Issue 02 acceptance criterion to the narrowest planned public observation surface.

| Criterion | Public observation surface | Expected result | Planned proof |
| --- | --- | --- | --- |
| Active OpenSpec target, scope, write-set, direct verification, strict validation | OpenSpec CLI and change artifacts | Change describes the isolated-worker slice and validates strictly before code edits | `openspec validate implement-isolated-issue-worker --strict` plus proposal/design/spec/task inspection |
| Evidence matrix exists before code changes | Versioned change artifact | Every Issue 02 criterion has a surface, expected result, and proof plan | Commit/diff ordering and this matrix, followed by completed implementation evidence |
| Assignment contains only issue, requirements, repository context, evidence matrix, findings | `GET /workflows/{owner}/{repo}/issues/{number}` and controlled worker invocation | Persisted/invoked assignment has exactly the five allowed context groups and no extra properties | HTTP behavior test inspects read-back and worker-observed assignment |
| One isolated worktree per assignment | Git CLI adapter and workflow read model | Run gets a distinct branch/path; original and sibling worktree contents do not change | Real temporary Git repository contract test plus HTTP behavior test |
| Codex implementer uses Terra/`xhigh`, issue skills, recorded provenance | Worker adapter process contract and workflow read model | Invocation selects Terra/`xhigh`, required skills and hashes, and persists them | Fake Codex executable contract test plus read-back assertion |
| Versioned node policy maps deterministic/Luna/Terra/Sol tasks | Policy public API loaded from packaged JSON | Every documented task maps exactly; Sol is limited to enumerated escalations | Parametrized policy contract tests |
| Skill routing and policy reject invalid combinations | Routing/policy public API | Triage, slicing, feature, and bug maps match the issue; overrides fail before effects | Parametrized contract tests and effect counters |
| Red-Green result is schema-valid and permanently associated | HTTP workflow read model across application restart | Valid result exposes red/green observations after restart | Signed-delivery HTTP behavior test, close/recreate application, HTTP read-back |
| Only implementer writes; invalid/failed result is contained | Real Git worktrees, controlled worker, GitHub effect recorder | Only assigned worktree can change; run records failure; no PR write surface is called | Failure behavior test compares original/sibling trees and public run state |
| Adapter is replaceable and proves full contract without experimental server | `WorkerPort` controlled implementation and `CodexCliWorker` fake process | Both controlled and CLI adapters consume the same invocation/result contract | Worker port workflow test and CLI boundary contract test; no app-server/exec-server dependency |
