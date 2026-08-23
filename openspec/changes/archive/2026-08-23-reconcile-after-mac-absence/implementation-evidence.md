# Implementation Evidence

## Outcome

Issue 10 is implemented as a once-per-operating-system-boot startup gate backed by real SQLite liveness and reconciliation records. A qualifying gap is exactly 24 hours or more. Startup reconciles an active human-merged pull request before ready backlog work, feeds deterministic synthetic deliveries through the ordinary inbox and dispatcher, and deduplicates them against delayed Queue deliveries by semantic command identity. A local heartbeat updates SQLite only; GitHub remains event-driven after startup.

## Criterion Evidence

| Behavior | Verification | Observation | Status |
|---|---|---|---|
| Active OpenSpec change bounded before production edits | `openspec validate reconcile-after-mac-absence --strict` before implementation | Proposal, new capability spec, design, write-set, tasks, and productive verification plan were complete and strictly valid | proven |
| First start and exact 24-hour boundary | `test_new_boot_evaluates_the_24_hour_boundary_once_through_public_read_back` | Separate real SQLite files showed first start `not_required`, 23:59:59 `below_threshold`, and exactly 24:00:00 `completed` with the measured gap in workflow GET | proven |
| Same-boot restart does not allocate another run | `test_interrupted_reconciliation_resumes_the_same_run_on_same_boot` | A controlled GitHub snapshot failure left the original boot row running; a restart five minutes later retained its original `started_at` and completed that same row | proven |
| Production boot identity | `uv run python -c '...system_boot_session_id...'` on macOS | The `kern.boottime` resolver returned a bounded 64-character opaque identity; controlled tests supplied stable/changeable boot IDs | proven |
| Missed ready work returns to normal workflow | `test_qualifying_boot_feeds_a_missed_ready_issue_through_the_normal_workflow` | A GitHub-only ready issue became a synthetic `reconciliation/ready` inbox delivery and ordinary selected run visible through GET | proven |
| Missed active PR merge completes the same run | `test_qualifying_boot_reconciles_the_active_human_merged_pull_request` | Current PR/issue state generated a synthetic human-merge command; the existing run ID and checkpoint became terminal with its persisted PR/head correlation | proven |
| Merge completion precedes ready successor | `test_startup_reconciliation_completes_active_merge_before_ready_successor` | One startup snapshot accepted two commands, completed issue 41, then selected issue 52 as the sole running successor | proven |
| Reconciliation then Queue delivery | `test_reconciliation_first_deduplicates_a_late_queue_delivery` | The delayed real receipt returned `200 already_accepted`; repetition remained accepted and run/claim/checkpoint did not change | proven |
| Queue delivery then reconciliation | `test_queue_first_is_deduplicated_by_reconciliation_on_the_next_boot` | The later boot discovered one command, accepted zero, deduplicated one, and preserved the original run/claim/checkpoint | proven |
| Heartbeat without periodic GitHub polling | `test_idle_heartbeat_advances_liveness_without_polling_github` | `last_alive_at` advanced ten controlled minutes during an idle lifespan and survived restart while the controlled GitHub read count remained unchanged | proven |
| Bounded data-minimized observability | `test_reconciliation_read_back_excludes_sensitive_github_material` | Read-back exposed only boot/status/outcome/liveness/time/gap/count fields; recognizable token, email, and authorization material present at the adapter were absent | proven |
| Bounded live PR adapter state | `test_github_adapter_reads_bounded_human_merge_state_for_reconciliation` | Production adapter read only PR number, head, merged fact, and normalized actor identity from the controlled GitHub HTTP boundary | proven |
| Existing workflow behavior remains intact | Full pilot suite | Delivery, backlog, recovery, evidence, publication, review, repair, feedback, merge, adapter, policy, and new reconciliation contracts all passed | proven |

## Verification Commands

- `uv run pytest -o addopts='' -q` in `langgraph-github-issue-pilot` → 210 passed; one upstream FastAPI/Starlette TestClient deprecation warning.
- `uvx ruff check .` in `langgraph-github-issue-pilot` → all checks passed.
- `uv lock --check` in `langgraph-github-issue-pilot` → 54 locked packages resolved and the lockfile is valid.
- `openspec validate reconcile-after-mac-absence --strict` → change valid.
- `git diff --check` → no whitespace errors.
- Production macOS boot-ID smoke check → 64-character opaque ID.

## Refactoring Review

- **DRY:** startup reconciliation column selection, liveness upsert, and threshold classification are centralized in `WorkflowStore`; semantic command builders share one bounded delivery renderer.
- **SOLID:** OS boot resolution, command representation, GitHub current-state reads, durable storage, and workflow dispatch remain separate boundaries. `WorkflowRuntime` composes active-merge and ready-backlog discovery without repository-name branches.
- **KISS:** one local heartbeat, one boot row, and one semantic command ledger extend the existing SQLite/inbox model. No scheduler, historical event replay, second dispatcher, or periodic GitHub polling was introduced.

## Known Warning

The suite emits the existing upstream FastAPI/Starlette warning that the current `httpx` TestClient integration is deprecated in favor of `httpx2`. It does not affect lifespan execution, signed HTTP behavior, SQLite persistence, controlled restart, or reconciliation results.
