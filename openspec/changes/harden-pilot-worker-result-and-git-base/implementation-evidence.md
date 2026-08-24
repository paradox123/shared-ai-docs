## Implementation Evidence

Verified locally on 2026-08-24 in `shared-ai-docs`. No `probare-crm` Issue #2 implementation, retry, publication, label, mailbox, frontend dependency, or worktree mutation was performed.

| Behavior | Direct verification | Result |
| --- | --- | --- |
| A valid v2 `blocked` final result survives one malformed JSONL line | `test_codex_cli_adapter_retains_a_valid_blocked_result_when_one_jsonl_line_is_malformed` first failed with `InvalidWorkerResult` at the combined JSONL parse; after the fix it retains the complete result, valid events, and one bounded `pilot.diagnostic_parse_failed` event | Proven red → green |
| The productive workflow persists that same result across restart | `test_blocked_final_result_survives_malformed_jsonl_and_is_observable_after_restart` drives signed POST plus GET read-back with the production `CodexCliWorker`, a fake Codex executable, real SQLite/LangGraph persistence, and restart | Proven |
| Missing result files retain useful diagnostics and a concrete cause | `test_codex_cli_adapter_retains_diagnostics_when_the_final_result_file_is_missing` first failed because `InvalidWorkerResult` had no failure code/events; it now exposes `final_result_missing` and both parsed completion events | Proven red → green |
| Workflow failure storage retains bounded cause/events | `test_failed_worker_is_contained_and_duplicate_delivery_starts_nothing_else` proves `schema_validation_failed` versus `process_nonzero_exit`, diagnostic retention, isolation, and duplicate convergence through HTTP read-back | Proven red → green |
| A stale local `main` cannot seed a new run | `test_git_adapter_fetches_and_pins_the_remote_base_when_local_main_is_stale` first created the worktree at local commit A; it now fetches and starts at remote commit B while leaving local `main` unchanged | Proven red → green |
| Recovery keeps the original immutable base | `test_git_adapter_adopts_the_same_run_owned_worktree_after_restart` advances the remote after creation and verifies adoption returns the same worktree/base identity | Proven |
| Worker does not treat sandboxed Git metadata as a product blocker | `test_codex_cli_adapter_runs_non_interactively_with_assignment_policy_skills_and_schema` verifies the prompt assigns staging/commit to the controller publisher and forbids reporting linked-worktree metadata access as an implementation blocker | Proven red → green |

## Verification Commands

- `uv run pytest tests/test_worker_adapter_contract.py tests/test_worktree_adapter_contract.py tests/test_workflow_interface.py::test_failed_worker_is_contained_and_duplicate_delivery_starts_nothing_else -q` — 12 passed.
- `uv run pytest tests/test_workflow_interface.py::test_blocked_final_result_survives_malformed_jsonl_and_is_observable_after_restart -q` — passed.
- `uv run pytest -q` — 281 passed on the final full rerun. An earlier full run exposed one unrelated heartbeat timing race in an existing recovery test; its isolated rerun passed and the unchanged full-suite rerun then passed.
- `uvx ruff check .` — passed.
- `uv lock --check` — passed (54 packages resolved from the lock).
- `openspec validate harden-pilot-worker-result-and-git-base --strict` — passed.
- `git diff --check` — passed.

The required refactoring pass consolidated Git subprocess execution in `GitWorktreeAdapter`; no further nearby DRY, SOLID, or KISS issue justified expanding this focused change.
