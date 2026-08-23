from __future__ import annotations

from github_issue_pilot.storage import Delivery, WorkflowStore

INITIAL_HEAD = "1234567890abcdef1234567890abcdef12345678"
REPAIR_HEAD = "abcdef1234567890abcdef1234567890abcdef12"
NOW = "2026-08-23T10:30:00+00:00"


def test_restarted_publication_rehydrates_qualified_evidence_before_review(tmp_path) -> None:
    store = WorkflowStore(tmp_path / "pilot.db")
    delivery = Delivery(
        delivery_id="delivery-001",
        body_digest="digest",
        repository="daniel/probare-crm",
        issue_number=41,
        event="issues",
        action="labeled",
        accepted_at=NOW,
    )
    store.accept(delivery)
    run = store.claim_run(delivery, issue_number=41, created_at=NOW)
    assert run is not None
    run_id = str(run["id"])
    branch = f"codex/run-{run_id}"
    store.begin_publication(
        run_id=run_id,
        evidence=[],
        branch=branch,
        started_at=NOW,
    )

    qualified = [{"criterion": "Customer can export CSV", "verdict": "pass"}]
    store.begin_publication(
        run_id=run_id,
        evidence=qualified,
        branch=branch,
        started_at=NOW,
    )

    publication = store.workflow_publication(run_id)
    store.close()

    assert publication is not None
    assert publication["status"] == "publishing"
    assert publication["evidence"] == qualified
    assert publication["branch"] == branch


def test_published_run_updates_same_draft_identity_to_repair_head_idempotently(tmp_path) -> None:
    store = WorkflowStore(tmp_path / "pilot.db")
    delivery = Delivery(
        delivery_id="delivery-001",
        body_digest="digest",
        repository="daniel/probare-crm",
        issue_number=41,
        event="issues",
        action="labeled",
        accepted_at=NOW,
    )
    store.accept(delivery)
    run = store.claim_run(delivery, issue_number=41, created_at=NOW)
    assert run is not None
    run_id = str(run["id"])
    store.begin_publication(
        run_id=run_id,
        evidence=[{"criterion": "Customer can export CSV", "head": INITIAL_HEAD}],
        branch=f"codex/run-{run_id}",
        started_at=NOW,
    )
    store.complete_publication(
        run_id=run_id,
        branch=f"codex/run-{run_id}",
        head_sha=INITIAL_HEAD,
        body="Initial evidence",
        pull_request_number=77,
        pull_request_url="https://github.example/pull/77",
        completed_at=NOW,
    )
    repair_evidence = [{"criterion": "Customer can export CSV", "head": REPAIR_HEAD}]

    for _ in range(2):
        store.update_publication(
            run_id=run_id,
            evidence=repair_evidence,
            head_sha=REPAIR_HEAD,
            body="Repair evidence and attempt history",
            completed_at=NOW,
        )

    publication = store.workflow_publication(run_id)
    store.close()

    assert publication is not None
    assert publication["status"] == "published"
    assert publication["head_sha"] == REPAIR_HEAD
    assert publication["body"] == "Repair evidence and attempt history"
    assert publication["evidence"] == repair_evidence
    assert publication["pull_request"] == {
        "number": 77,
        "url": "https://github.example/pull/77",
        "draft": True,
    }
    assert publication["branch"] == f"codex/run-{run_id}"
