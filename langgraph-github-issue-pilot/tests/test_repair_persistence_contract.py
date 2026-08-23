from __future__ import annotations

import pytest

from github_issue_pilot.storage import Delivery, WorkflowStore

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"
REPAIR_HEAD = "abcdef1234567890abcdef1234567890abcdef12"
NOW = "2026-08-23T10:30:00+00:00"


def _seed_failed_review(store: WorkflowStore) -> tuple[str, str]:
    delivery = Delivery(
        delivery_id="delivery-001",
        body_digest="digest",
        repository="daniel/probare-crm",
        issue_number=41,
        event="issues",
        action="labeled",
        accepted_at=NOW,
    )
    assert store.accept(delivery) == "accepted"
    run = store.claim_run(delivery, issue_number=41, created_at=NOW)
    assert run is not None
    run_id = str(run["id"])
    review_batch_id = store.begin_review_batch(
        run_id=run_id,
        head_sha=HEAD_SHA,
        pull_request_number=77,
        started_at=NOW,
    )
    store.block_review_batch(
        batch_id=review_batch_id,
        reason="review_failed",
        completed_at=NOW,
    )
    return run_id, review_batch_id


def test_repair_attempt_invocations_and_terminal_state_survive_reconstruction(tmp_path) -> None:
    database_path = tmp_path / "pilot.db"
    store = WorkflowStore(database_path)
    run_id, initial_review_batch_id = _seed_failed_review(store)

    repair_batch_id = store.begin_repair_batch(
        run_id=run_id,
        initial_review_batch_id=initial_review_batch_id,
        started_at=NOW,
    )
    assert store.begin_repair_batch(
        run_id=run_id,
        initial_review_batch_id=initial_review_batch_id,
        started_at=NOW,
    ) == repair_batch_id
    assignment = {
        "schema_version": "1",
        "round": {"number": 1, "limit": 3},
        "findings": [{"axis": "code", "description": "Validate export filter"}],
    }
    attempt_id = store.begin_repair_attempt(
        repair_batch_id=repair_batch_id,
        round_number=1,
        assignment=assignment,
        started_at=NOW,
    )
    assert store.begin_repair_attempt(
        repair_batch_id=repair_batch_id,
        round_number=1,
        assignment=assignment,
        started_at=NOW,
    ) == attempt_id
    for invocation_number, model, outcome in (
        (1, "gpt-5.6-terra", "escalate"),
        (2, "gpt-5.6-sol", "completed"),
    ):
        store.record_repair_invocation(
            attempt_id=attempt_id,
            invocation_number=invocation_number,
            policy={
                "version": "1",
                "task": "findings_repair",
                "model": model,
                "reasoning_effort": "xhigh",
                "sandbox": "workspace-write",
            },
            skills=[{"name": "tdd", "content_sha256": "a" * 64}],
            access_profile={
                "role": "implementer",
                "sandbox": "workspace-write",
                "write_root": "/tmp/run-41",
                "additional_write_roots": [],
            },
            result={"schema_version": "1", "outcome": outcome},
            diagnostic_events=[{"type": "turn.completed"}],
            started_at=NOW,
            completed_at=NOW,
        )
    fresh_review_batch_id = store.begin_review_batch(
        run_id=run_id,
        head_sha=REPAIR_HEAD,
        pull_request_number=77,
        started_at=NOW,
    )
    store.block_review_batch(
        batch_id=fresh_review_batch_id,
        reason="review_failed",
        completed_at=NOW,
    )
    open_findings = [
        {
            "source": "review",
            "axis": "code",
            "location": "src/export.py:10",
            "description": "Validate export filter",
        }
    ]
    store.complete_repair_attempt(
        attempt_id=attempt_id,
        status="unsuccessful",
        head_sha=REPAIR_HEAD,
        deterministic_verification={
            "command": "pytest tests/test_export.py",
            "passed": True,
            "exit_code": 0,
            "observed": "passed",
        },
        review_batch_id=fresh_review_batch_id,
        remaining_findings=open_findings,
        completed_at=NOW,
    )
    store.complete_repair_batch(
        repair_batch_id=repair_batch_id,
        status="ready-for-human",
        open_findings=open_findings,
        projected_labels=frozenset({"ready-for-agent", "ready-for-human"}),
        completed_at=NOW,
    )
    before_restart = store.workflow_repair(run_id)
    store.close()

    restarted = WorkflowStore(database_path)
    after_restart = restarted.workflow_repair(run_id)
    restarted.close()

    assert after_restart == before_restart
    assert after_restart is not None
    assert after_restart["initial_review_batch_id"] == initial_review_batch_id
    assert after_restart["round_limit"] == 3
    assert after_restart["round_count"] == 1
    assert after_restart["status"] == "ready-for-human"
    assert after_restart["open_findings"] == open_findings
    assert after_restart["projected_labels"] == ["ready-for-agent", "ready-for-human"]
    attempt = after_restart["attempts"][0]
    assert attempt["assignment"] == assignment
    assert attempt["head_sha"] == REPAIR_HEAD
    assert attempt["review_batch_id"] == fresh_review_batch_id
    assert attempt["deterministic_verification"]["passed"] is True
    assert [item["policy"]["model"] for item in attempt["invocations"]] == [
        "gpt-5.6-terra",
        "gpt-5.6-sol",
    ]


def test_store_rejects_a_fourth_numbered_repair_round(tmp_path) -> None:
    store = WorkflowStore(tmp_path / "pilot.db")
    run_id, initial_review_batch_id = _seed_failed_review(store)
    repair_batch_id = store.begin_repair_batch(
        run_id=run_id,
        initial_review_batch_id=initial_review_batch_id,
        started_at=NOW,
    )

    with pytest.raises(ValueError, match="between one and three"):
        store.begin_repair_attempt(
            repair_batch_id=repair_batch_id,
            round_number=4,
            assignment={"round": {"number": 4}},
            started_at=NOW,
        )

    assert store.workflow_repair(run_id)["attempts"] == []
    store.close()
