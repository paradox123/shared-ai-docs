from __future__ import annotations

from github_issue_pilot.storage import Delivery, WorkflowStore

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"


def test_review_batch_and_three_axis_results_survive_store_reconstruction(tmp_path) -> None:
    database_path = tmp_path / "pilot.db"
    store = WorkflowStore(database_path)
    delivery = Delivery(
        delivery_id="delivery-001",
        body_digest="digest",
        repository="daniel/probare-crm",
        issue_number=41,
        event="issues",
        action="labeled",
        accepted_at="2026-08-23T10:30:00+00:00",
    )
    assert store.accept(delivery) == "accepted"
    run = store.claim_run(delivery, issue_number=41, created_at=delivery.accepted_at)
    assert run is not None
    run_id = str(run["id"])

    batch_id = store.begin_review_batch(
        run_id=run_id,
        head_sha=HEAD_SHA,
        pull_request_number=77,
        started_at=delivery.accepted_at,
    )
    assert (
        store.begin_review_batch(
            run_id=run_id,
            head_sha=HEAD_SHA,
            pull_request_number=77,
            started_at=delivery.accepted_at,
        )
        == batch_id
    )
    for axis, route_axis, skills in (
        ("requirements", "spec", [{"name": "code-review", "content_sha256": "a" * 64}]),
        ("code", "standards", [{"name": "code-review", "content_sha256": "a" * 64}]),
        (
            "architecture",
            "architecture",
            [
                {"name": "codebase-design", "content_sha256": "b" * 64},
                {"name": "domain-modeling", "content_sha256": "c" * 64},
            ],
        ),
    ):
        store.record_review_result(
            batch_id=batch_id,
            axis=axis,
            assignment={"axis": axis, "head_sha": HEAD_SHA},
            result={
                "schema_version": "1",
                "invocation_id": f"review-{axis}-001",
                "axis": axis,
                "head_sha": HEAD_SHA,
                "verdict": "pass",
                "rationale": "passed",
                "findings": [],
            },
            policy={
                "version": "1",
                "model": "gpt-5.6-terra",
                "reasoning_effort": "xhigh",
                "sandbox": "read-only",
            },
            route_axis=route_axis,
            skills=skills,
            access_profile={"role": "reviewer", "sandbox": "read-only"},
            diagnostic_events=[{"type": "turn.completed"}],
            completed_at=delivery.accepted_at,
        )
    store.complete_review_batch(
        batch_id=batch_id,
        projected_labels=frozenset({"ready-for-agent", "verified", "awaiting-review"}),
        completed_at=delivery.accepted_at,
    )
    before_restart = store.workflow_review(run_id)
    store.close()

    restarted = WorkflowStore(database_path)
    after_restart = restarted.workflow_review(run_id)
    restarted.close()

    assert after_restart == before_restart
    assert after_restart is not None
    assert after_restart["status"] == "verified"
    assert after_restart["head_sha"] == HEAD_SHA
    assert after_restart["pull_request_number"] == 77
    assert after_restart["projected_labels"] == [
        "awaiting-review",
        "ready-for-agent",
        "verified",
    ]
    assert [result["axis"] for result in after_restart["results"]] == [
        "requirements",
        "code",
        "architecture",
    ]
    assert all(result["policy"]["sandbox"] == "read-only" for result in after_restart["results"])
