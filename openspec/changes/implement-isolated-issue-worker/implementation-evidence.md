# Implementation Evidence

Verified at `2026-08-22T04:37:54Z` against working-tree changes based on commit `85066a35cd5efdf461af725181d5c418f83b3e41` on branch `codex/implement-isolated-issue-worker` in `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs-issue-02`.

## Acceptance Matrix

| Criterion | Public verification | Observed result | Verdict |
| --- | --- | --- | --- |
| Active OpenSpec change defines goal, scope, write-set, and direct verification before implementation | `openspec validate implement-isolated-issue-worker --strict`, proposal/design/spec/tasks, and Git history of this session | Strict validation passed before runtime code changed and again at closeout; the proposal limits the write-set to the pilot package, docs, change, and Issue 02. | proven |
| Evidence matrix exists before implementation | `acceptance-criteria-matrix.md` in the active change | All ten Issue 02 criteria had a public surface, expected outcome, and planned proof before the first runtime test/code slice. | proven |
| Assignment contains only issue, requirements, repository context, evidence matrix, and findings | `test_claimed_issue_persists_bounded_assignment_and_evidence_before_worker_invocation` through signed `POST /webhooks/github` and public workflow GET | The persisted and invoked schema-validated assignment has exactly the six top-level fields (schema version plus the five allowed context groups), both checkbox requirements, explicit HTTP/pytest evidence plans, and the current finding; no webhook/session/secret context is present. | proven |
| Each run receives an isolated worktree | `test_git_adapter_creates_a_run_owned_branch_without_changing_other_worktrees` | A real temporary Git repository created `codex/run-run-001` under a separate worker root; Daniel's checkout and an uncommitted sibling worktree remained unchanged. | proven |
| Codex implementer is non-interactive Terra/`xhigh` with routed skills and recorded provenance | `test_codex_cli_adapter_runs_non_interactively_with_assignment_policy_skills_and_schema` plus HTTP read-back test | The fake executable observed `codex exec`, Terra, `model_reasoning_effort="xhigh"`, `approval_policy="never"`, `workspace-write`, isolated `--cd`, `$implement`/`$tdd`, JSONL, and output schema. Public state recorded model, reasoning, and 64-character skill hashes. | proven |
| Versioned node policy maps deterministic/Luna/Terra/Sol work exactly | `tests/test_policy_contract.py` | Parametrized contracts proved no model for deterministic work, Luna/`medium` presentation, Terra/`xhigh` regular nodes, read-only reviewers, write-enabled implementer/findings repair, and Sol/`xhigh` only for six defined escalation reasons. | proven |
| Skill routing and fail-closed policy combinations match the issue | `tests/test_policy_contract.py` | Triage routed `triage`, slicing routed `to-tickets`, features routed `implement`+`tdd`, bugs routed `diagnosing-bugs`+`tdd`; mismatched model/reasoning/sandbox and unsupported routes were rejected. | proven |
| Feature/bug work returns validated observable Red-Green results permanently associated with the run | `test_valid_red_green_worker_result_is_persisted_and_observable_after_restart` and worker-result schema rejection contract | A completed result included the independently observed failing and passing commands, result/evidence/diagnostics were durable, and a new application instance returned identical public state. Empty Red-Green evidence was rejected. | proven |
| Only the implementer writes; invalid/failed results are contained | Two `test_failed_worker_is_contained_and_duplicate_delivery_starts_nothing_else` cases plus access-profile rejection contract | Schema-invalid output and simulated process failure recorded `failed`; only the assigned worktree changed, Daniel's and sibling markers stayed unchanged, no PR write occurred, replay created no second worktree/worker, and an out-of-worktree write profile failed before process start. | proven |
| Worker adapter is replaceable and proves the full contract without experimental server APIs | Controlled `WorkerPort` HTTP tests and `CodexCliWorker` fake-process contract | The same immutable invocation/result contract worked through the controlled adapter and subprocess adapter, covering assignment, result, model, skills, rights, schema, and diagnostics without app-server or exec-server use. | proven |

## Verification Commands

```text
uv run pytest -q
uv run pytest -vv <seven named HTTP/Git/Codex acceptance scenarios>
uvx ruff check .
uv lock --check
uvx pip-audit --path .venv/lib/python3.14/site-packages --skip-editable --progress-spinner off
uv build --out-dir <temporary-directory>
git diff --check
openspec validate implement-isolated-issue-worker --strict
```

Observed summary:

- full suite: `46 passed`
- named acceptance set: `7 passed`
- Ruff: `All checks passed!`
- lockfile: resolved `54 packages` without change
- dependency audit: `No known vulnerabilities found` (editable project skipped; installed third-party distributions audited)
- wheel build: succeeded; all four versioned assignment/result/policy/routing JSON contracts were present in the wheel
- strict OpenSpec validation: passed
- diff check: passed

The test runner emits one upstream FastAPI/Starlette deprecation warning recommending the future `httpx2` TestClient path. It does not affect the verified HTTP behavior.
