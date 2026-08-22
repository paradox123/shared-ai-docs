# Implementation Evidence

Verified at `2026-08-22T04:38:38Z` against working-tree changes based on commit `85066a35cd5efdf461af725181d5c418f83b3e41`.

## Acceptance Matrix

| Criterion | Public verification | Observed result | Verdict |
| --- | --- | --- | --- |
| Active OpenSpec change exists and was strictly valid before implementation | `openspec validate dispose-authorized-repository-backlog --strict` | Proposal, design, specs, write-set, tasks, and direct verification were valid before the first runtime test and at closeout. | proven |
| Repository-independent control plane uses a versioned adapter | `test_repository_adapter_contract_selects_with_adapter_owned_events_and_labels` drives signed HTTP deliveries through two adapters | Both adapters use contract version `1` and independently supply repository identity, events, ready/running labels, backlog state, and projections; the core contains no repository-name branch. | proven |
| `probare-crm` is the only live production binding | `test_probare_http_adapter_reads_the_complete_open_issue_backlog` plus entry-point configuration inspection | The production entry point requires exactly one repository named `probare-crm`; the second adapter exists only in the parameterized behavior test. | proven |
| Every issue type can enter the pilot | Four `test_ready_issue_types_are_authorized_without_a_second_start_signal` cases | Bug, Feature, Task, and Security examples all create the same selected running outcome; the core has no type or risk filter. | proven |
| `ready-for-agent` is the sole start authorization | The ready issue-type cases submit only the adapter's ready label | Every unblocked ready case starts without another label or mandate-body section. | proven |
| Proven inherited work can self-authorize | Three `test_proven_in_scope_origin_self_authorizes_and_selects_issue` cases | Direct Daniel issue, linked PRD, and parent chain each project `ready-for-agent` followed by `agent-running`. | proven |
| Invalid provenance and scope expansion interrupt safely | Two `test_unapproved_origin_is_durably_interrupted_without_github_projection` cases | Readback returns `invalid-provenance` or `product-decision-required`; neither case has a run, checkpoint, claim, or adapter write. | proven |
| Blockers require both merge and closure | Four `test_blocker_requires_human_merge_and_issue_closure_before_selection` cases | Neither fact, merge only, and closure only remain queued; only merge plus closure produces `selected`. | proven |
| One implementation is active per repository and no stacked work starts | `test_simultaneous_candidates_are_sorted_selected_once_and_durably_queued` | Out-of-order candidates `(42, 41)` are evaluated by issue number; 41 alone owns the running LangGraph thread and 42 remains `repository-busy`. | proven |
| A completed active issue advances the frontier | `test_merged_and_closed_active_issue_completes_and_advances_frontier` uses an `issues` wakeup followed by a `pull_request/closed` wakeup | After controlled GitHub state reports human merge plus issue closure, run 41 becomes completed and issue 42 is selected in the same scheduling pass. | proven |
| Simultaneous events and unselected state remain durable | The simultaneous case sends two accepted deliveries; two `test_unselected_disposition_and_delivery_correlation_survive_restart` cases reconstruct the app | Both wakeups reevaluate the full frontier; queued and interrupted disposition, reason, and delivery correlation survive restart without duplicate writes. | proven |
| Productive surfaces and real workflow persistence are tested | `tests/test_repository_backlog.py` and retained `tests/test_workflow_interface.py` | Assertions use signed `POST /webhooks/github`, productive GET readback, and controlled adapter effects with real SQLite and LangGraph `SqliteSaver`; no raw-table or private-node assertions exist. | proven |

## Production Adapter Basis

The live adapter uses GitHub's documented REST surfaces for [repository issue listing](https://docs.github.com/en/rest/issues/issues?apiVersion=2026-03-10), [issue dependencies](https://docs.github.com/en/rest/issues/issue-dependencies?apiVersion=2026-03-10), [parent issues](https://docs.github.com/en/rest/issues/sub-issues?apiVersion=2026-03-10), and [timeline cross-references](https://docs.github.com/en/rest/issues/timeline?apiVersion=2026-03-10). No live GitHub writes were executed during verification because repository credentials and an external test issue were not part of this local implementation request; the GitHub system boundary was controlled while the productive HTTP, SQLite, and LangGraph surfaces remained real.

## Verification Commands

```text
uv lock --check
uvx ruff check .
uv run pytest -vv tests/test_repository_backlog.py
uv run pytest -q
uvx pip-audit --path .venv/lib/python3.14/site-packages --skip-editable --progress-spinner off
python -m compileall -q src tests
git diff --check
openspec validate dispose-authorized-repository-backlog --strict
```

Observed summary:

- focused signed-HTTP and adapter suite: `20 passed`
- complete package suite: `34 passed`
- Ruff: `All checks passed!`
- dependency audit: `No known vulnerabilities found` (the editable project itself was skipped; all installed third-party distributions were audited)
- lock check, bytecode compilation, diff check, and strict OpenSpec validation: passed

The test runner emits one upstream FastAPI/Starlette deprecation warning recommending the future `httpx2` TestClient path. It does not affect the verified HTTP behavior or dependency-audit result.
