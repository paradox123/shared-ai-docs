from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from github_issue_pilot.app import create_app
from github_issue_pilot.github import BacklogIssue, BlockerState, IssueState

SECRET = b"test-webhook-secret"
REPOSITORY = "daniel/probare-crm"


class ControlledGitHub:
    contract_version = "1"
    repository = REPOSITORY
    ready_label = "ready-for-agent"
    running_label = "agent-running"
    allowed_event_actions = frozenset({("issues", "labeled")})

    def __init__(self) -> None:
        self.labels: set[str] = {"ready-for-agent"}
        self.open = True
        self.open_blockers = False
        self.label_writes: list[tuple[str, int, str]] = []

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        return IssueState(
            open=self.open,
            labels=frozenset(self.labels),
            blockers=(BlockerState(40, False, False),) if self.open_blockers else (),
        )

    def backlog(self, trigger_issue_number: int) -> tuple[BacklogIssue, ...]:
        return (
            BacklogIssue(
                trigger_issue_number,
                self.issue_state(REPOSITORY, trigger_issue_number),
            ),
        )

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        if label not in self.labels:
            self.labels.add(label)
            self.label_writes.append((repository, issue_number, label))


def fixed_clock() -> datetime:
    return datetime(2026, 8, 21, 10, 30, tzinfo=UTC)


def delivery_body(
    *,
    issue_number: int = 41,
    action: str = "labeled",
    repository: str = REPOSITORY,
) -> bytes:
    return json.dumps(
        {
            "action": action,
            "repository": {"full_name": repository},
            "issue": {"number": issue_number},
            "label": {"name": "ready-for-agent"},
        },
        separators=(",", ":"),
    ).encode()


def signed_headers(body: bytes, *, delivery_id: str = "delivery-001", event: str = "issues") -> dict[str, str]:
    digest = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return {
        "content-type": "application/json",
        "x-github-delivery": delivery_id,
        "x-github-event": event,
        "x-hub-signature-256": f"sha256={digest}",
    }


def test_signed_allowed_delivery_is_durable_before_acceptance(tmp_path) -> None:
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: ControlledGitHub()},
        clock=fixed_clock,
    )
    body = delivery_body()

    with TestClient(app) as client:
        response = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        observed = client.get("/workflows/daniel/probare-crm/issues/41")

    assert response.status_code == 202
    assert response.json() == {"delivery_id": "delivery-001", "status": "accepted"}
    assert observed.status_code == 200
    assert observed.json()["delivery"] == {
        "id": "delivery-001",
        "status": "accepted",
        "accepted_at": "2026-08-21T10:30:00+00:00",
        "event": "issues",
        "action": "labeled",
    }


def test_eligible_issue_gets_one_persistent_run_and_github_claim(tmp_path) -> None:
    github = ControlledGitHub()
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    body = delivery_body()

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        observed = client.get("/workflows/daniel/probare-crm/issues/41")

    state = observed.json()
    assert accepted.status_code == 202
    assert state["run"]["status"] == "running"
    assert state["run"]["issue_number"] == 41
    assert state["claim"] == {
        "label": "agent-running",
        "projected_at": "2026-08-21T10:30:00+00:00",
    }
    assert state["checkpoint"]["thread_id"] == state["run"]["id"]
    assert state["checkpoint"]["values"] == {
        "delivery_id": "delivery-001",
        "repository": REPOSITORY,
        "issue_number": 41,
        "status": "claimed",
        "claim_label": "agent-running",
    }
    assert github.label_writes == [(REPOSITORY, 41, "agent-running")]


def test_repeated_delivery_keeps_the_same_run_checkpoint_and_claim(tmp_path) -> None:
    github = ControlledGitHub()
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    body = delivery_body()
    headers = signed_headers(body)

    with TestClient(app) as client:
        first = client.post("/webhooks/github", content=body, headers=headers)
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()
        repeated = client.post("/webhooks/github", content=body, headers=headers)
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert first.status_code == 202
    assert repeated.status_code == 200
    assert repeated.json() == {"delivery_id": "delivery-001", "status": "already_accepted"}
    assert after["run"]["id"] == before["run"]["id"]
    assert after["checkpoint"]["id"] == before["checkpoint"]["id"]
    assert github.label_writes == [(REPOSITORY, 41, "agent-running")]


def test_reused_delivery_id_with_different_body_is_rejected_without_effect(tmp_path) -> None:
    github = ControlledGitHub()
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    original = delivery_body()
    conflicting = delivery_body(issue_number=42)

    with TestClient(app) as client:
        first = client.post("/webhooks/github", content=original, headers=signed_headers(original))
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()
        conflict = client.post("/webhooks/github", content=conflicting, headers=signed_headers(conflicting))
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()
        absent = client.get("/workflows/daniel/probare-crm/issues/42")

    assert first.status_code == 202
    assert conflict.status_code == 409
    assert after["run"]["id"] == before["run"]["id"]
    assert absent.status_code == 404
    assert github.label_writes == [(REPOSITORY, 41, "agent-running")]


def test_invalid_signature_is_rejected_before_invalid_json_is_parsed(tmp_path) -> None:
    github = ControlledGitHub()
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    body = b"not-json"
    headers = signed_headers(body)
    headers["x-hub-signature-256"] = "sha256=invalid"

    with TestClient(app) as client:
        response = client.post("/webhooks/github", content=body, headers=headers)

    assert response.status_code == 401
    assert github.label_writes == []


@pytest.mark.parametrize(
    ("body", "header_overrides", "app_overrides", "expected_status"),
    [
        (delivery_body(), {}, {"max_request_bytes": 32}, 413),
        (delivery_body(repository="daniel/other"), {}, {}, 403),
        (delivery_body(), {"x-github-event": "pull_request"}, {}, 403),
        (delivery_body(action="edited"), {}, {}, 403),
    ],
    ids=["too-large", "repository", "event", "action"],
)
def test_unauthorized_deliveries_have_no_workflow_or_github_effect(
    tmp_path,
    body: bytes,
    header_overrides: dict[str, str],
    app_overrides: dict[str, int],
    expected_status: int,
) -> None:
    github = ControlledGitHub()
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        **app_overrides,
    )
    headers = signed_headers(body)
    headers.update(header_overrides)

    with TestClient(app) as client:
        response = client.post("/webhooks/github", content=body, headers=headers)
        absent = client.get("/workflows/daniel/probare-crm/issues/41")

    assert response.status_code == expected_status
    assert absent.status_code == 404
    assert github.label_writes == []


@pytest.mark.parametrize(
    ("attribute", "value"),
    [("open", False), ("labels", set()), ("open_blockers", True)],
    ids=["closed", "not-ready", "blocked"],
)
def test_ineligible_issue_is_accepted_without_a_run_or_claim(tmp_path, attribute: str, value: object) -> None:
    github = ControlledGitHub()
    setattr(github, attribute, value)
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    body = delivery_body()

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        observed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert accepted.status_code == 202
    assert observed["run"] is None
    assert observed["claim"] is None
    assert observed["checkpoint"] is None
    assert github.label_writes == []


def test_repository_with_a_running_issue_does_not_claim_a_second_issue(tmp_path) -> None:
    github = ControlledGitHub()
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    first_body = delivery_body(issue_number=41)
    second_body = delivery_body(issue_number=42)

    with TestClient(app) as client:
        client.post("/webhooks/github", content=first_body, headers=signed_headers(first_body))
        second = client.post(
            "/webhooks/github",
            content=second_body,
            headers=signed_headers(second_body, delivery_id="delivery-002"),
        )
        first_state = client.get("/workflows/daniel/probare-crm/issues/41").json()
        second_state = client.get("/workflows/daniel/probare-crm/issues/42").json()

    assert second.status_code == 202
    assert first_state["run"]["status"] == "running"
    assert second_state["run"] is None
    assert github.label_writes == [(REPOSITORY, 41, "agent-running")]


def test_delivery_run_claim_and_checkpoint_remain_observable_after_restart(tmp_path) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    body = delivery_body()
    headers = signed_headers(body)
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )

    with TestClient(first_app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=headers)
        before_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    with TestClient(restarted_app) as client:
        after_restart = client.get("/workflows/daniel/probare-crm/issues/41")
        repeated = client.post("/webhooks/github", content=body, headers=headers)
        after_repeat = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert accepted.status_code == 202
    assert after_restart.status_code == 200
    assert after_restart.json() == before_restart
    assert repeated.json()["status"] == "already_accepted"
    assert after_repeat == before_restart
    assert github.label_writes == [(REPOSITORY, 41, "agent-running")]
