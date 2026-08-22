from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from github_issue_pilot.app import create_app
from github_issue_pilot.github import BacklogIssue, IssueState

INTERNAL_SECRET = b"internal-relay-test-secret"
REPOSITORY = "daniel/probare-crm"
BODY = json.dumps(
    {
        "action": "labeled",
        "repository": {"full_name": REPOSITORY},
        "issue": {"number": 41},
        "label": {"name": "ready-for-agent"},
    },
    separators=(",", ":"),
).encode()
FIXED_RELAY_SIGNATURE = "sha256=ba8bc97e411592a16dc39e0677ca0ebb8e4348d8d33096f22e2c0c1210396dff"


class ControlledGitHub:
    contract_version = "1"
    repository = REPOSITORY
    ready_label = "ready-for-agent"
    running_label = "agent-running"
    allowed_event_actions = frozenset({("issues", "labeled")})

    def __init__(self) -> None:
        self.labels = {"ready-for-agent"}
        self.label_writes: list[tuple[str, int, str]] = []

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        return IssueState(open=True, labels=frozenset(self.labels))

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


def relay_headers(
    body: bytes,
    *,
    delivery_id: str = "delivery-001",
    event: str = "issues",
) -> dict[str, str]:
    canonical = b"\n".join((delivery_id.encode(), event.encode(), body))
    signature = hmac.new(INTERNAL_SECRET, canonical, hashlib.sha256).hexdigest()
    return {
        "content-type": "application/json",
        "x-github-delivery": delivery_id,
        "x-github-event": event,
        "x-pilot-signature-256": f"sha256={signature}",
    }


def relay_app(tmp_path, github: ControlledGitHub):
    return create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=None,
        internal_webhook_secret=INTERNAL_SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )


def test_fixed_relay_signature_is_accepted_by_the_productive_http_interface(tmp_path) -> None:
    github = ControlledGitHub()
    app = relay_app(tmp_path, github)
    headers = relay_headers(BODY)

    assert headers["x-pilot-signature-256"] == FIXED_RELAY_SIGNATURE
    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=BODY, headers=headers)
        observed = client.get("/workflows/daniel/probare-crm/issues/41")

    assert accepted.status_code == 202
    assert accepted.json() == {"delivery_id": "delivery-001", "status": "accepted"}
    assert observed.status_code == 200
    assert observed.json()["delivery"]["id"] == "delivery-001"
    assert github.label_writes == [(REPOSITORY, 41, "agent-running")]


def test_duplicate_relay_delivery_converges_on_one_local_run_checkpoint_and_claim(tmp_path) -> None:
    github = ControlledGitHub()
    app = relay_app(tmp_path, github)
    headers = relay_headers(BODY)

    with TestClient(app) as client:
        first = client.post("/webhooks/github", content=BODY, headers=headers)
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()
        duplicate = client.post("/webhooks/github", content=BODY, headers=headers)
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert first.status_code == 202
    assert duplicate.status_code == 200
    assert duplicate.json() == {"delivery_id": "delivery-001", "status": "already_accepted"}
    assert after["delivery"] == before["delivery"]
    assert after["run"]["id"] == before["run"]["id"]
    assert after["checkpoint"]["id"] == before["checkpoint"]["id"]
    assert github.label_writes == [(REPOSITORY, 41, "agent-running")]


@pytest.mark.parametrize(
    ("signed_body", "header_overrides", "sent_body"),
    [
        (BODY, {"x-github-delivery": "delivery-tampered"}, BODY),
        (BODY, {"x-github-event": "pull_request"}, BODY),
        (BODY, {}, BODY.replace(b"41", b"42")),
    ],
    ids=["delivery-id", "event", "body"],
)
def test_relay_signature_binds_delivery_event_and_body_before_parsing(
    tmp_path,
    signed_body: bytes,
    header_overrides: dict[str, str],
    sent_body: bytes,
) -> None:
    github = ControlledGitHub()
    app = relay_app(tmp_path, github)
    headers = relay_headers(signed_body)
    headers.update(header_overrides)

    with TestClient(app) as client:
        rejected = client.post("/webhooks/github", content=sent_body, headers=headers)
        absent = client.get("/workflows/daniel/probare-crm/issues/41")

    assert rejected.status_code == 401
    assert absent.status_code == 404
    assert github.label_writes == []


@pytest.mark.parametrize(
    ("webhook_secret", "internal_secret"),
    [(b"github", b"internal"), (None, None)],
    ids=["both", "neither"],
)
def test_application_requires_exactly_one_authentication_mode(
    tmp_path,
    webhook_secret: bytes | None,
    internal_secret: bytes | None,
) -> None:
    with pytest.raises(ValueError, match="exactly one webhook authentication mode"):
        create_app(
            database_path=tmp_path / "pilot.db",
            webhook_secret=webhook_secret,
            internal_webhook_secret=internal_secret,
            repository_adapters={REPOSITORY: ControlledGitHub()},
            clock=fixed_clock,
        )
