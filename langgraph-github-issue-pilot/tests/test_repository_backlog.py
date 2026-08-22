from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from github_issue_pilot.app import create_app
from github_issue_pilot.github import (
    AuthorizationEvidence,
    BacklogIssue,
    BlockerState,
    ConfiguredRepositoryAdapter,
    GitHubHttpAdapter,
    IssueState,
    RepositorySettings,
)

SECRET = b"adapter-contract-secret"


class ControlledRepositoryAdapter:
    contract_version = "1"

    def __init__(self, *, repository: str, ready_label: str, running_label: str) -> None:
        self.repository = repository
        self.ready_label = ready_label
        self.running_label = running_label
        self.allowed_event_actions = frozenset(
            {("issues", "opened"), ("pull_request", "closed")}
        )
        self.labels = {ready_label}
        self.issue_type = "task"
        self.authorization_origin = "unproven"
        self.within_inherited_scope = True
        self.blockers: tuple[BlockerState, ...] = ()
        self.backlog_issue_numbers = (41,)
        self.closed_issues: set[int] = set()
        self.merged_issues: set[int] = set()
        self.issue_labels: dict[int, set[str]] = {41: self.labels}
        self.label_writes: list[tuple[str, int, str]] = []

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        labels = self.issue_labels.setdefault(issue_number, {self.ready_label})
        return IssueState(
            open=issue_number not in self.closed_issues,
            labels=frozenset(labels),
            blockers=self.blockers,
            issue_type=self.issue_type,
            implementation_pr_merged=issue_number in self.merged_issues,
            authorization=AuthorizationEvidence(
                origin=self.authorization_origin,
                within_inherited_scope=self.within_inherited_scope,
            ),
        )

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        labels = self.issue_labels.setdefault(issue_number, {self.ready_label})
        if label not in labels:
            labels.add(label)
            self.label_writes.append((repository, issue_number, label))

    def backlog(self, trigger_issue_number: int) -> tuple[BacklogIssue, ...]:
        del trigger_issue_number
        return tuple(
            BacklogIssue(issue_number, self.issue_state(self.repository, issue_number))
            for issue_number in self.backlog_issue_numbers
        )


def fixed_clock() -> datetime:
    return datetime(2026, 8, 21, 11, 0, tzinfo=UTC)


def signed_delivery(
    repository: str,
    *,
    delivery_id: str,
    issue_number: int = 41,
) -> tuple[bytes, dict[str, str]]:
    body = json.dumps(
        {
            "action": "opened",
            "repository": {"full_name": repository},
            "issue": {"number": issue_number},
        },
        separators=(",", ":"),
    ).encode()
    digest = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return body, {
        "content-type": "application/json",
        "x-github-delivery": delivery_id,
        "x-github-event": "issues",
        "x-hub-signature-256": f"sha256={digest}",
    }


def signed_pull_request_delivery(
    repository: str,
    *,
    delivery_id: str,
    pull_request_number: int,
) -> tuple[bytes, dict[str, str]]:
    body = json.dumps(
        {
            "action": "closed",
            "repository": {"full_name": repository},
            "pull_request": {"number": pull_request_number, "merged": True},
        },
        separators=(",", ":"),
    ).encode()
    digest = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return body, {
        "content-type": "application/json",
        "x-github-delivery": delivery_id,
        "x-github-event": "pull_request",
        "x-hub-signature-256": f"sha256={digest}",
    }


@pytest.mark.parametrize(
    ("repository", "ready_label", "running_label"),
    [
        ("daniel/probare-crm", "ready-for-agent", "agent-running"),
        ("example/second-repository", "queued-for-bot", "bot-running"),
    ],
    ids=["probare-crm", "second-adapter"],
)
def test_repository_adapter_contract_selects_with_adapter_owned_events_and_labels(
    tmp_path,
    repository: str,
    ready_label: str,
    running_label: str,
) -> None:
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label=ready_label,
        running_label=running_label,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    body, headers = signed_delivery(repository, delivery_id=f"delivery-{repository}")
    owner, name = repository.split("/", maxsplit=1)

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=headers)
        observed = client.get(f"/workflows/{owner}/{name}/issues/41")

    assert accepted.status_code == 202
    assert observed.status_code == 200
    assert observed.json()["run"]["status"] == "running"
    assert observed.json()["claim"]["label"] == running_label
    assert adapter.label_writes == [(repository, 41, running_label)]


@pytest.mark.parametrize("issue_type", ["bug", "feature", "task", "security"], ids=str)
def test_ready_issue_types_are_authorized_without_a_second_start_signal(tmp_path, issue_type: str) -> None:
    repository = "daniel/probare-crm"
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label="ready-for-agent",
        running_label="agent-running",
    )
    adapter.issue_type = issue_type
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    body, headers = signed_delivery(repository, delivery_id=f"delivery-{issue_type}")

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=headers)
        observed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert observed["run"]["status"] == "running"
    assert adapter.label_writes == [(repository, 41, "agent-running")]


@pytest.mark.parametrize(
    "origin",
    ["daniel_issue", "linked_prd", "parent_chain"],
    ids=["direct-issue", "linked-prd", "parent-chain"],
)
def test_proven_in_scope_origin_self_authorizes_and_selects_issue(tmp_path, origin: str) -> None:
    repository = "daniel/probare-crm"
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label="ready-for-agent",
        running_label="agent-running",
    )
    adapter.labels.clear()
    adapter.authorization_origin = origin
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    body, headers = signed_delivery(repository, delivery_id=f"delivery-{origin}")

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=headers)
        observed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert observed["run"]["status"] == "running"
    assert adapter.label_writes == [
        (repository, 41, "ready-for-agent"),
        (repository, 41, "agent-running"),
    ]


@pytest.mark.parametrize(
    ("origin", "within_scope", "expected_reason"),
    [
        ("unproven", True, "invalid-provenance"),
        ("parent_chain", False, "product-decision-required"),
    ],
    ids=["invalid-provenance", "material-scope-expansion"],
)
def test_unapproved_origin_is_durably_interrupted_without_github_projection(
    tmp_path,
    origin: str,
    within_scope: bool,
    expected_reason: str,
) -> None:
    repository = "daniel/probare-crm"
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label="ready-for-agent",
        running_label="agent-running",
    )
    adapter.labels.clear()
    adapter.authorization_origin = origin
    adapter.within_inherited_scope = within_scope
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    body, headers = signed_delivery(repository, delivery_id=f"delivery-{expected_reason}")

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=headers)
        observed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert accepted.status_code == 202
    assert observed["disposition"] == {
        "status": "interrupted",
        "reason": expected_reason,
        "issue_type": "task",
        "evaluated_at": "2026-08-21T11:00:00+00:00",
    }
    assert observed["run"] is None
    assert observed["claim"] is None
    assert adapter.label_writes == []


@pytest.mark.parametrize(
    ("issue_closed", "pull_request_merged", "expected_status"),
    [
        (False, False, "queued"),
        (False, True, "queued"),
        (True, False, "queued"),
        (True, True, "selected"),
    ],
    ids=["both-open", "merge-only", "closure-only", "merge-and-closure"],
)
def test_blocker_requires_human_merge_and_issue_closure_before_selection(
    tmp_path,
    issue_closed: bool,
    pull_request_merged: bool,
    expected_status: str,
) -> None:
    repository = "daniel/probare-crm"
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label="ready-for-agent",
        running_label="agent-running",
    )
    adapter.blockers = (
        BlockerState(
            issue_number=40,
            issue_closed=issue_closed,
            pull_request_merged=pull_request_merged,
        ),
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    body, headers = signed_delivery(
        repository,
        delivery_id=f"delivery-blocker-{issue_closed}-{pull_request_merged}",
    )

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=headers)
        observed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert observed["disposition"]["status"] == expected_status
    if expected_status == "queued":
        assert observed["disposition"]["reason"] == "blocked-by-incomplete-issue-40"
        assert observed["run"] is None
        assert adapter.label_writes == []
    else:
        assert observed["disposition"]["reason"] is None
        assert observed["run"]["status"] == "running"
        assert adapter.label_writes == [(repository, 41, "agent-running")]


def test_simultaneous_candidates_are_sorted_selected_once_and_durably_queued(tmp_path) -> None:
    repository = "daniel/probare-crm"
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label="ready-for-agent",
        running_label="agent-running",
    )
    adapter.backlog_issue_numbers = (42, 41)
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    first_body, first_headers = signed_delivery(
        repository,
        issue_number=42,
        delivery_id="simultaneous-42",
    )
    second_body, second_headers = signed_delivery(
        repository,
        issue_number=41,
        delivery_id="simultaneous-41",
    )

    with TestClient(app) as client:
        first = client.post("/webhooks/github", content=first_body, headers=first_headers)
        second = client.post("/webhooks/github", content=second_body, headers=second_headers)
        lower = client.get("/workflows/daniel/probare-crm/issues/41")
        higher = client.get("/workflows/daniel/probare-crm/issues/42")

    assert first.status_code == 202
    assert second.status_code == 202
    assert lower.status_code == 200
    assert higher.status_code == 200
    assert lower.json()["disposition"]["status"] == "selected"
    assert lower.json()["run"]["status"] == "running"
    assert higher.json()["disposition"] == {
        "status": "queued",
        "reason": "repository-busy",
        "issue_type": "task",
        "evaluated_at": "2026-08-21T11:00:00+00:00",
    }
    assert higher.json()["run"] is None
    assert adapter.label_writes == [(repository, 41, "agent-running")]


def test_merged_and_closed_active_issue_completes_and_advances_frontier(tmp_path) -> None:
    repository = "daniel/probare-crm"
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label="ready-for-agent",
        running_label="agent-running",
    )
    adapter.backlog_issue_numbers = (41, 42)
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    initial_body, initial_headers = signed_delivery(
        repository,
        issue_number=41,
        delivery_id="active-41",
    )
    completion_body, completion_headers = signed_pull_request_delivery(
        repository,
        delivery_id="completed-41",
        pull_request_number=88,
    )

    with TestClient(app) as client:
        client.post("/webhooks/github", content=initial_body, headers=initial_headers)
        adapter.merged_issues.add(41)
        adapter.closed_issues.add(41)
        completion = client.post(
            "/webhooks/github",
            content=completion_body,
            headers=completion_headers,
        )
        completed = client.get("/workflows/daniel/probare-crm/issues/41").json()
        successor = client.get("/workflows/daniel/probare-crm/issues/42").json()

    assert completion.status_code == 202
    assert completed["run"]["status"] == "completed"
    assert completed["disposition"]["status"] == "completed"
    assert completed["disposition"]["reason"] == "implementation-finished"
    assert successor["run"]["status"] == "running"
    assert successor["disposition"]["status"] == "selected"
    assert adapter.label_writes == [
        (repository, 41, "agent-running"),
        (repository, 42, "agent-running"),
    ]


@pytest.mark.parametrize("outcome", ["queued", "interrupted"])
def test_unselected_disposition_and_delivery_correlation_survive_restart(tmp_path, outcome: str) -> None:
    repository = "daniel/probare-crm"
    database_path = tmp_path / "pilot.db"
    adapter = ControlledRepositoryAdapter(
        repository=repository,
        ready_label="ready-for-agent",
        running_label="agent-running",
    )
    observed_issue = 41
    if outcome == "queued":
        adapter.backlog_issue_numbers = (41, 42)
        observed_issue = 42
    else:
        adapter.labels.clear()
    body, headers = signed_delivery(
        repository,
        issue_number=41,
        delivery_id=f"restart-{outcome}",
    )
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=body, headers=headers)
        before = client.get(
            f"/workflows/daniel/probare-crm/issues/{observed_issue}"
        ).json()

    writes_before_restart = list(adapter.label_writes)
    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={repository: adapter},
        clock=fixed_clock,
    )
    with TestClient(restarted_app) as client:
        after_response = client.get(
            f"/workflows/daniel/probare-crm/issues/{observed_issue}"
        )

    assert after_response.status_code == 200
    assert after_response.json() == before
    assert after_response.json()["delivery"]["id"] == f"restart-{outcome}"
    assert after_response.json()["disposition"]["status"] == outcome
    assert after_response.json()["run"] is None
    assert after_response.json()["claim"] is None
    assert after_response.json()["checkpoint"] is None
    assert adapter.label_writes == writes_before_restart


def test_probare_http_adapter_reads_the_complete_open_issue_backlog() -> None:
    repository = "daniel/probare-crm"

    def github_api(request: httpx.Request) -> httpx.Response:
        if request.url.path == f"/repos/{repository}/issues":
            return httpx.Response(
                200,
                json=[
                    {
                        "number": 42,
                        "state": "open",
                        "labels": [{"name": "ready-for-agent"}],
                        "user": {"login": "daniel"},
                        "type": {"name": "Feature"},
                    },
                    {
                        "number": 41,
                        "state": "open",
                        "labels": [{"name": "ready-for-agent"}],
                        "user": {"login": "daniel"},
                        "type": {"name": "Bug"},
                    },
                ],
            )
        if request.url.path.endswith("/dependencies/blocked_by"):
            return httpx.Response(200, json=[])
        if request.url.path.endswith("/timeline"):
            return httpx.Response(200, json=[])
        raise AssertionError(f"unexpected GitHub request: {request.method} {request.url}")

    github = GitHubHttpAdapter(
        "token",
        human_login="daniel",
        transport=httpx.MockTransport(github_api),
    )
    adapter = ConfiguredRepositoryAdapter(
        github,
        RepositorySettings(
            repository=repository,
            allowed_event_actions=frozenset(
                {
                    ("issues", "labeled"),
                    ("issues", "closed"),
                    ("pull_request", "closed"),
                }
            ),
        ),
    )

    try:
        backlog = adapter.backlog(trigger_issue_number=42)
    finally:
        github.close()

    assert [(item.issue_number, item.state.issue_type) for item in backlog] == [
        (42, "Feature"),
        (41, "Bug"),
    ]
    assert all(item.state.authorization.origin == "daniel_issue" for item in backlog)
    assert all(item.state.blockers == () for item in backlog)
