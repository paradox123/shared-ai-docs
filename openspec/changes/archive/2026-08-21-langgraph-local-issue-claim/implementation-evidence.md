# Implementation Evidence

Verified at `2026-08-21T18:47:15Z` against working-tree changes based on commit `1059098d51cefeeb3cd9e9176b249024751ec6c5`.

## Acceptance Matrix

| Criterion | Public verification | Observed result | Verdict |
| --- | --- | --- | --- |
| Active OpenSpec change exists and is strictly valid before implementation | `openspec validate langgraph-local-issue-claim --strict` | Validation passed before runtime files were implemented and again at closeout. | proven |
| Valid allowed delivery is atomically persisted before a positive response | `test_signed_allowed_delivery_is_durable_before_acceptance` drives `POST /webhooks/github`, then reads `GET /workflows/daniel/probare-crm/issues/41` | HTTP `202` returned `accepted`; the read model exposed delivery ID, acceptance time, event, and action. | proven |
| Eligible unblocked issue creates one persistent run and `agent-running` claim | `test_eligible_issue_gets_one_persistent_run_and_github_claim` | Read model exposed one `running` run whose ID equals the checkpoint thread ID; the controlled GitHub adapter observed one `agent-running` write. | proven |
| Repeated delivery creates no second run, checkpoint, or claim | `test_repeated_delivery_keeps_the_same_run_checkpoint_and_claim` | Repeated request returned `already_accepted`; run ID and checkpoint ID stayed unchanged; GitHub write count stayed one. | proven |
| Invalid signature, oversized request, and disallowed repository/event/action have no effect | `test_invalid_signature_is_rejected_before_invalid_json_is_parsed` and four `test_unauthorized_deliveries_have_no_workflow_or_github_effect` cases | Requests returned `401`, `413`, or `403`; workflow lookup returned `404`; no GitHub write occurred. | proven |
| Ineligible and repository-conflicting issues do not claim | Three `test_ineligible_issue_is_accepted_without_a_run_or_claim` cases plus `test_repository_with_a_running_issue_does_not_claim_a_second_issue` | Accepted inbox entries had no run, claim, or checkpoint; the existing repository run remained the only active run. | proven |
| Delivery, run, claim, and checkpoint survive restart | `test_delivery_run_claim_and_checkpoint_remain_observable_after_restart` closes and recreates the application over the same database | Complete public read model was byte-for-byte equivalent after restart; replay remained effect-free. | proven |
| Tests use the productive interface and real workflow persistence | `tests/test_workflow_interface.py` | All assertions use HTTP responses/readback and controlled GitHub effects; SQLite inbox storage and LangGraph `SqliteSaver` are real; no raw-table or node-order assertions exist. | proven |

## Verification Commands

```text
uv lock --check
uvx ruff check .
uv run pytest
uv run pytest -vv tests/test_workflow_interface.py::test_delivery_run_claim_and_checkpoint_remain_observable_after_restart
uvx pip-audit --path .venv/lib/python3.14/site-packages --skip-editable --progress-spinner off
git diff --check
openspec validate langgraph-local-issue-claim --strict
```

Observed summary:

- `14 passed`
- named restart scenario: `1 passed`
- Ruff: `All checks passed!`
- dependency audit: `No known vulnerabilities found` (the editable project itself was skipped; all installed third-party distributions were audited)
- strict OpenSpec validation: passed
- diff check: passed

The test runner emits one upstream FastAPI/Starlette deprecation warning recommending the future `httpx2` TestClient path. It does not change the verified HTTP behavior and no runtime vulnerability was reported by the dependency audit.
