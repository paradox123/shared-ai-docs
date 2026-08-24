from __future__ import annotations

from pathlib import Path

import pytest

from github_issue_pilot.storage import Delivery, WorkflowStore


def _request(run_id: str) -> dict[str, object]:
    return {
        "schema_version": "1",
        "repository": {"full_name": "daniel/probare-crm", "issue_number": 41},
        "run": {
            "id": run_id,
            "phase": "implementation",
            "operation_key": f"{run_id}:implementation:worker",
        },
        "role": "implementer",
        "context": {
            "worktree_path": f"/tmp/worktrees/{run_id}",
            "branch": f"codex/run-{run_id}",
            "pull_request_number": None,
            "head_sha": None,
        },
        "classification": "product_decision",
        "problem": "Retention requirements contradict each other.",
        "required_action": "Choose the authoritative retention behavior.",
        "options": [{"label": "retain", "impact": "Records remain recoverable."}],
        "recommendation": {
            "option_label": "retain",
            "rationale": "It matches the audit requirement.",
        },
        "preserved": {"findings": ["Retention conflict."], "results": []},
    }


def _store_with_intervention(database_path: Path) -> tuple[WorkflowStore, str, str]:
    store = WorkflowStore(database_path)
    delivery = Delivery(
        delivery_id="delivery-001",
        body_digest="digest-001",
        repository="daniel/probare-crm",
        issue_number=41,
        event="issues",
        action="labeled",
        accepted_at="2026-08-24T10:00:00+00:00",
    )
    store.accept(delivery)
    run = store.claim_run(
        delivery,
        issue_number=41,
        created_at="2026-08-24T10:00:00+00:00",
    )
    assert run is not None
    run_id = str(run["id"])
    request = _request(run_id)
    intervention_id = store.begin_intervention(
        run_id=run_id,
        phase="implementation",
        role="implementer",
        operation_key=str(request["run"]["operation_key"]),
        request=request,
        source_result={"schema_version": "3", "outcome": "intervention"},
        created_at="2026-08-24T10:01:00+00:00",
    )
    return store, run_id, intervention_id


def test_duplicate_delivery_reuses_one_intervention_and_one_codex_session(tmp_path) -> None:
    store, run_id, intervention_id = _store_with_intervention(tmp_path / "pilot.db")
    request = _request(run_id)

    duplicate_id = store.begin_intervention(
        run_id=run_id,
        phase="implementation",
        role="implementer",
        operation_key=str(request["run"]["operation_key"]),
        request=request,
        source_result={"schema_version": "3", "outcome": "intervention"},
        created_at="2026-08-24T10:01:00+00:00",
    )
    store.complete_intervention_delivery(
        intervention_id=intervention_id,
        thread_id="thread-001",
        delivery_turn_id="turn-001",
        delivered_at="2026-08-24T10:02:00+00:00",
    )
    store.complete_intervention_delivery(
        intervention_id=intervention_id,
        thread_id="thread-001",
        delivery_turn_id="turn-001",
        delivered_at="2026-08-24T10:02:00+00:00",
    )

    assert duplicate_id == intervention_id
    assert store.workflow_interventions(run_id)["requests"] == [
        {
            **store.workflow_interventions(run_id)["requests"][0],
            "status": "open",
            "session": {"thread_id": "thread-001", "delivery_turn_id": "turn-001"},
        }
    ]
    with pytest.raises(RuntimeError, match="different session"):
        store.complete_intervention_delivery(
            intervention_id=intervention_id,
            thread_id="thread-002",
            delivery_turn_id="turn-002",
            delivered_at="2026-08-24T10:03:00+00:00",
        )
    store.close()


def test_first_answer_is_applied_once_and_recovery_finishes_the_same_operation(tmp_path) -> None:
    database_path = tmp_path / "pilot.db"
    store, run_id, intervention_id = _store_with_intervention(database_path)
    store.complete_intervention_delivery(
        intervention_id=intervention_id,
        thread_id="thread-001",
        delivery_turn_id="turn-001",
        delivered_at="2026-08-24T10:02:00+00:00",
    )

    assert store.capture_intervention_answer(
        intervention_id=intervention_id,
        answer_turn_id="turn-002",
        answer_text="Retain records for thirty days.",
        answered_at="2026-08-24T10:03:00+00:00",
    )
    assert not store.capture_intervention_answer(
        intervention_id=intervention_id,
        answer_turn_id="turn-003",
        answer_text="Delete immediately instead.",
        answered_at="2026-08-24T10:04:00+00:00",
    )
    assert store.claim_intervention_application(intervention_id)
    assert not store.claim_intervention_application(intervention_id)
    store.close()

    recovered = WorkflowStore(database_path)
    request = recovered.workflow_interventions(run_id)["requests"][0]
    assert request["status"] == "applying"
    assert request["answer"] == {
        "turn_id": "turn-002",
        "text": "Retain records for thirty days.",
    }
    recovered.complete_intervention_application(
        intervention_id=intervention_id,
        applied_at="2026-08-24T10:05:00+00:00",
    )
    recovered.complete_intervention_application(
        intervention_id=intervention_id,
        applied_at="2026-08-24T10:06:00+00:00",
    )
    applied = recovered.workflow_interventions(run_id)["requests"][0]
    assert applied["status"] == "applied"
    assert applied["applied_at"] == "2026-08-24T10:05:00+00:00"
    assert not recovered.capture_intervention_answer(
        intervention_id=intervention_id,
        answer_turn_id="turn-late",
        answer_text="A late conflicting answer.",
        answered_at="2026-08-24T10:07:00+00:00",
    )
    recovered.close()


def test_stable_surface_failure_is_a_public_delivery_blocker(tmp_path) -> None:
    store, run_id, intervention_id = _store_with_intervention(tmp_path / "pilot.db")

    store.block_intervention_delivery(
        intervention_id=intervention_id,
        reason="stable_surface_unavailable",
    )

    state = store.workflow_interventions(run_id)
    assert state["status"] == "delivery_blocked"
    assert state["requests"][0]["status"] == "delivery_blocked"
    assert state["requests"][0]["delivery_error"] == "stable_surface_unavailable"
    store.close()
