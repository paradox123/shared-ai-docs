from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from github_issue_pilot.app import create_app
from github_issue_pilot.github import BacklogIssue, DraftPullRequest, IssueState

SECRET = b"startup-reconciliation-secret"
REPOSITORY = "daniel/probare-crm"


class ReconciliationGitHub:
    contract_version = "1"
    repository = REPOSITORY
    ready_label = "ready-for-agent"
    running_label = "agent-running"
    allowed_event_actions = frozenset({("issues", "labeled"), ("pull_request", "closed")})

    def __init__(self) -> None:
        self.reconciliation_reads = 0
        self.fail_reconciliation = False
        self.issues: dict[int, IssueState] = {}
        self.label_writes: list[tuple[str, int, str]] = []

    @staticmethod
    def is_configured_human(login: str, user_type: str) -> bool:
        return login.casefold() == "daniel" and user_type.casefold() == "user"

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        del repository
        return self.issues.get(issue_number, IssueState(open=False, labels=frozenset()))

    def backlog(self, trigger_issue_number: int) -> tuple[BacklogIssue, ...]:
        del trigger_issue_number
        self.reconciliation_reads += 1
        if self.fail_reconciliation:
            raise RuntimeError("controlled GitHub snapshot failure")
        return tuple(
            BacklogIssue(issue_number, state)
            for issue_number, state in sorted(self.issues.items())
            if state.open
        )

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        self.label_writes.append((repository, issue_number, label))

    @staticmethod
    def current_pull_request_head(repository: str, pull_request_number: int) -> str:
        del repository, pull_request_number
        return "a" * 40

    @staticmethod
    def project_workflow_labels(
        repository: str,
        issue_number: int,
        *,
        add: frozenset[str],
        remove: frozenset[str],
    ) -> frozenset[str]:
        del repository, issue_number, add, remove
        return frozenset()

    @staticmethod
    def ensure_draft_pull_request(
        repository: str,
        *,
        issue_number: int,
        branch: str,
        title: str,
        body: str,
        head_sha: str,
    ) -> DraftPullRequest:
        del repository, issue_number, branch, title
        return DraftPullRequest(1, "https://example.test/pulls/1", head_sha, True, body)


def _delivery(
    *, issue_number: int = 41, delivery_id: str = "seed-delivery"
) -> tuple[bytes, dict[str, str]]:
    body = json.dumps(
        {
            "action": "labeled",
            "repository": {"full_name": REPOSITORY},
            "issue": {"number": issue_number},
            "label": {"name": "ready-for-agent"},
        },
        separators=(",", ":"),
    ).encode()
    signature = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return body, {
        "X-GitHub-Delivery": delivery_id,
        "X-GitHub-Event": "issues",
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json",
    }


def _app(
    database_path: Path,
    github: ReconciliationGitHub,
    *,
    now: datetime,
    boot_id: str,
):
    return create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        clock=lambda: now,
        boot_session_id=lambda: boot_id,
        repository_adapters={REPOSITORY: github},
    )


@pytest.mark.parametrize(
    ("offline_for", "expected_outcome", "expected_status"),
    [
        (timedelta(hours=23, minutes=59, seconds=59), "below_threshold", "not_required"),
        (timedelta(hours=24), "threshold_reached", "completed"),
    ],
)
def test_new_boot_evaluates_the_24_hour_boundary_once_through_public_read_back(
    tmp_path: Path,
    offline_for: timedelta,
    expected_outcome: str,
    expected_status: str,
) -> None:
    database_path = tmp_path / f"pilot-{int(offline_for.total_seconds())}.db"
    github = ReconciliationGitHub()
    first_seen = datetime(2026, 8, 20, 8, tzinfo=UTC)
    body, headers = _delivery()

    with TestClient(
        _app(database_path, github, now=first_seen, boot_id="boot-a")
    ) as client:
        assert client.post("/webhooks/github", content=body, headers=headers).status_code == 202
        first = client.get("/workflows/daniel/probare-crm/issues/41").json()
        assert first["reconciliation"] == {
            "boot_id": "boot-a",
            "status": "not_required",
            "outcome": "first_start",
            "last_alive_at": first_seen.isoformat(),
            "previous_last_alive_at": None,
            "started_at": first_seen.isoformat(),
            "completed_at": first_seen.isoformat(),
            "offline_seconds": None,
            "discovered_commands": 0,
            "accepted_commands": 0,
            "deduplicated_commands": 0,
        }

    restarted_at = first_seen + offline_for
    with TestClient(
        _app(database_path, github, now=restarted_at, boot_id="boot-b")
    ) as client:
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert state["reconciliation"]["boot_id"] == "boot-b"
    assert state["reconciliation"]["status"] == expected_status
    assert state["reconciliation"]["outcome"] == expected_outcome
    assert state["reconciliation"]["previous_last_alive_at"] == first_seen.isoformat()
    assert state["reconciliation"]["started_at"] == restarted_at.isoformat()
    assert state["reconciliation"]["completed_at"] == restarted_at.isoformat()
    assert state["reconciliation"]["offline_seconds"] == int(offline_for.total_seconds())


def test_interrupted_reconciliation_resumes_the_same_run_on_same_boot(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ReconciliationGitHub()
    first_seen = datetime(2026, 8, 20, 8, tzinfo=UTC)
    body, headers = _delivery()

    with TestClient(
        _app(database_path, github, now=first_seen, boot_id="boot-a")
    ) as client:
        assert client.post("/webhooks/github", content=body, headers=headers).status_code == 202

    qualifying_start = first_seen + timedelta(hours=25)
    github.reconciliation_reads = 0
    github.fail_reconciliation = True
    with (
        pytest.raises(RuntimeError, match="controlled GitHub snapshot failure"),
        TestClient(_app(database_path, github, now=qualifying_start, boot_id="boot-b")),
    ):
        pass

    github.fail_reconciliation = False
    same_boot_restart = qualifying_start + timedelta(minutes=5)
    with TestClient(
        _app(database_path, github, now=same_boot_restart, boot_id="boot-b")
    ) as client:
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert state["reconciliation"]["boot_id"] == "boot-b"
    assert state["reconciliation"]["status"] == "completed"
    assert state["reconciliation"]["started_at"] == qualifying_start.isoformat()
    assert state["reconciliation"]["completed_at"] == same_boot_restart.isoformat()
    assert github.reconciliation_reads == 2


def test_qualifying_boot_feeds_a_missed_ready_issue_through_the_normal_workflow(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ReconciliationGitHub()
    first_seen = datetime(2026, 8, 20, 8, tzinfo=UTC)
    body, headers = _delivery()

    with TestClient(
        _app(database_path, github, now=first_seen, boot_id="boot-a")
    ) as client:
        assert client.post("/webhooks/github", content=body, headers=headers).status_code == 202

    github.issues[52] = IssueState(open=True, labels=frozenset({"ready-for-agent"}))
    restarted_at = first_seen + timedelta(hours=25)
    with TestClient(
        _app(database_path, github, now=restarted_at, boot_id="boot-b")
    ) as client:
        state = client.get("/workflows/daniel/probare-crm/issues/52")
        assert state.status_code == 200
        payload = state.json()

    assert payload["delivery"]["event"] == "reconciliation"
    assert payload["delivery"]["action"] == "ready"
    assert payload["disposition"]["status"] == "selected"
    assert payload["run"]["issue_number"] == 52
    assert payload["reconciliation"]["discovered_commands"] == 1
    assert payload["reconciliation"]["accepted_commands"] == 1


def test_reconciliation_first_deduplicates_a_late_queue_delivery(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ReconciliationGitHub()
    first_seen = datetime(2026, 8, 20, 8, tzinfo=UTC)
    seed_body, seed_headers = _delivery()

    with TestClient(
        _app(database_path, github, now=first_seen, boot_id="boot-a")
    ) as client:
        assert (
            client.post(
                "/webhooks/github", content=seed_body, headers=seed_headers
            ).status_code
            == 202
        )

    github.issues[52] = IssueState(open=True, labels=frozenset({"ready-for-agent"}))
    restarted_at = first_seen + timedelta(hours=25)
    late_body, late_headers = _delivery(issue_number=52, delivery_id="queue-late-52")
    with TestClient(
        _app(database_path, github, now=restarted_at, boot_id="boot-b")
    ) as client:
        before = client.get("/workflows/daniel/probare-crm/issues/52").json()
        late = client.post(
            "/webhooks/github", content=late_body, headers=late_headers
        )
        repeated = client.post(
            "/webhooks/github", content=late_body, headers=late_headers
        )
        after = client.get("/workflows/daniel/probare-crm/issues/52").json()

    assert late.status_code == 200
    assert late.json() == {
        "delivery_id": "queue-late-52",
        "status": "already_accepted",
    }
    assert repeated.status_code == 200
    assert before["run"] == after["run"]
    assert before["claim"] == after["claim"]
    assert before["checkpoint"] == after["checkpoint"]


def test_queue_first_is_deduplicated_by_reconciliation_on_the_next_boot(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ReconciliationGitHub()
    github.issues[52] = IssueState(open=True, labels=frozenset({"ready-for-agent"}))
    first_seen = datetime(2026, 8, 20, 8, tzinfo=UTC)
    body, headers = _delivery(issue_number=52, delivery_id="queue-first-52")

    with TestClient(
        _app(database_path, github, now=first_seen, boot_id="boot-a")
    ) as client:
        accepted = client.post("/webhooks/github", content=body, headers=headers)
        before = client.get("/workflows/daniel/probare-crm/issues/52").json()

    restarted_at = first_seen + timedelta(hours=25)
    with TestClient(
        _app(database_path, github, now=restarted_at, boot_id="boot-b")
    ) as client:
        after = client.get("/workflows/daniel/probare-crm/issues/52").json()

    assert accepted.status_code == 202
    assert before["run"] == after["run"]
    assert before["claim"] == after["claim"]
    assert before["checkpoint"] == after["checkpoint"]
    assert after["reconciliation"]["discovered_commands"] == 1
    assert after["reconciliation"]["accepted_commands"] == 0
    assert after["reconciliation"]["deduplicated_commands"] == 1


def test_idle_heartbeat_advances_liveness_without_polling_github(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ReconciliationGitHub()
    observed_time = [datetime(2026, 8, 20, 8, tzinfo=UTC)]
    body, headers = _delivery()
    app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        clock=lambda: observed_time[0],
        boot_session_id=lambda: "boot-a",
        heartbeat_interval_seconds=0.01,
        repository_adapters={REPOSITORY: github},
    )

    with TestClient(app) as client:
        assert client.post("/webhooks/github", content=body, headers=headers).status_code == 202
        reads_after_delivery = github.reconciliation_reads
        observed_time[0] += timedelta(minutes=10)
        time.sleep(0.05)
        idle = client.get("/workflows/daniel/probare-crm/issues/41").json()

    same_boot_restart = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        clock=lambda: observed_time[0],
        boot_session_id=lambda: "boot-a",
        heartbeat_interval_seconds=0.01,
        repository_adapters={REPOSITORY: github},
    )
    with TestClient(same_boot_restart) as client:
        restarted = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert idle["reconciliation"]["last_alive_at"] == observed_time[0].isoformat()
    assert restarted["reconciliation"]["boot_id"] == "boot-a"
    assert restarted["reconciliation"]["started_at"] == datetime(
        2026, 8, 20, 8, tzinfo=UTC
    ).isoformat()
    assert restarted["reconciliation"]["last_alive_at"] == observed_time[0].isoformat()
    assert github.reconciliation_reads == reads_after_delivery


def test_reconciliation_read_back_excludes_sensitive_github_material(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ReconciliationGitHub()
    first_seen = datetime(2026, 8, 20, 8, tzinfo=UTC)
    body, headers = _delivery()

    with TestClient(
        _app(database_path, github, now=first_seen, boot_id="boot-a")
    ) as client:
        client.post("/webhooks/github", content=body, headers=headers)

    github.issues[52] = IssueState(
        open=True,
        labels=frozenset({"ready-for-agent"}),
        title="Use ghp_12345678901234567890",
        body="Contact daniel@example.com with authorization: Bearer private-value",
    )
    with TestClient(
        _app(
            database_path,
            github,
            now=first_seen + timedelta(hours=25),
            boot_id="boot-b",
        )
    ) as client:
        state = client.get("/workflows/daniel/probare-crm/issues/52").json()

    serialized = json.dumps(state["reconciliation"], sort_keys=True)
    assert set(state["reconciliation"]) == {
        "boot_id",
        "status",
        "outcome",
        "last_alive_at",
        "previous_last_alive_at",
        "started_at",
        "completed_at",
        "offline_seconds",
        "discovered_commands",
        "accepted_commands",
        "deduplicated_commands",
    }
    assert "ghp_12345678901234567890" not in serialized
    assert "daniel@example.com" not in serialized
    assert "Bearer private-value" not in serialized
