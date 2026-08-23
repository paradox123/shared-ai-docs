# Implementation Evidence

## Outcome

Issue 08 is implemented through automatic FastAPI-startup recovery backed by the existing SQLite records and LangGraph run/thread identity. Claim, implementation, publication, review, repair, and human-feedback execution are re-entrant. Completed durable transitions are reused; uncertain opaque work stays under the same run/batch/round and deterministic worktree/branch/PR ownership. Human-merge completion remains terminal.

## Criterion Evidence

| Behavior | Verification | Observation | Status |
|---|---|---|---|
| Active OpenSpec change bounded scope before implementation | `openspec validate resume-interrupted-workflows --strict` before production edits | Proposal, design, new capability spec, write-set, tasks, and direct process verification plan validated strictly | proven |
| Startup continues one claimed run | `test_startup_recovery_continues_claimed_run_once_through_http_read_back` | New app instance on the same database retained run/thread and produced one implementation and draft PR; a third instance added no external effect | proven |
| Real process abort during claim, implementation, and publication | `test_real_process_exit_recovers_completed_effects_without_duplicates[claim]`, `[implementation]`, and `[publication]` | Spawned serving processes exited with the controlled non-zero code, replacement processes converged through workflow GET, and shared counters remained one claim/worktree/worker/source/PR | proven |
| Existing deterministic worktree is adopted | `test_git_adapter_adopts_the_same_run_owned_worktree_after_restart` | Repeated creation for the same run returned the same path/branch and Git listed that worktree once | proven |
| Partial independent review resumes only missing axes | `test_real_process_exit_resumes_only_missing_review_axes` | Process exited after the durable requirements verdict; restart retained it and ran code/architecture only, leaving exactly one result and invocation per axis | proven |
| Repair resumes one persisted invocation and round | `test_real_process_exit_reuses_persisted_repair_invocation` | Restart exposed one repair round with one invocation, one new repaired head, fresh deterministic verification/review, and no second repair-worker call | proven |
| Human waiting and feedback continuation are restart-safe | `test_real_process_exit_preserves_completed_feedback_attempt_and_batch_counter` | Process was killed while waiting and again after durable feedback-attempt completion; restart completed the same batch at count one without another worker/publication/review | proven |
| Terminal merge cannot reactivate | `test_authorized_human_merge_completes_the_same_run_and_checkpoint_after_restart` | A second post-completion application reconstruction returned an identical completed run/checkpoint/history and unchanged worktree/writer/source/reviewer counts | proven |
| Recovery/checkpoint diagnostics are data-minimized | `test_sensitive_worker_evidence_and_diagnostics_are_redacted_before_read_back` | Recovery events contain exactly ID/phase/operation-key/outcome/time; checkpoint values contain only delivery/repository/issue/status/claim correlation; configured secret, recognizable token, and email were absent | proven |
| Existing bounded round and idempotency behavior remains intact | Full pilot suite | All delivery, backlog, evidence, review, three-round repair, feedback, merge, publication, policy, and adapter contracts remained green | proven |

## Verification Commands

- `uv run pytest -o addopts=''` in `langgraph-github-issue-pilot` → 199 passed; only the upstream FastAPI/Starlette TestClient deprecation warning was emitted.
- `uvx ruff check .` in `langgraph-github-issue-pilot` → all checks passed.
- `uv lock --check` in `langgraph-github-issue-pilot` → lockfile valid and unchanged.
- `openspec validate resume-interrupted-workflows --strict` → change valid.
- `git diff --check` → no whitespace errors.

## Refactoring Review

- **DRY:** recovery calls the existing workflow nodes and review/repair/feedback coordinators, and reconstructs node inputs from the canonical domain records instead of introducing parallel execution paths or duplicated payload stores.
- **SOLID:** persistence remains in `WorkflowStore`; Git/worktree/GitHub/worker/reviewer/verifier boundaries remain ports; the optional transition probe is injected only for process-boundary observation.
- **KISS:** stable identities come from existing run/head/batch/round keys, the schema change is one additive recovery-event table, and checkpoints were reduced to five bounded correlation/status fields instead of gaining another recovery payload.

## Known Warning

The suite emits one upstream FastAPI/Starlette warning that the current `httpx` TestClient integration is deprecated in favor of `httpx2`. It does not affect signed HTTP behavior, spawned-process termination, SQLite persistence, or recovery results.
