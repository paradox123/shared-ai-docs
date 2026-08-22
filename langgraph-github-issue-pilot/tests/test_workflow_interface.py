from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from github_issue_pilot.app import create_app
from github_issue_pilot.github import IssueState
from github_issue_pilot.implementation import (
    ImplementationServices,
    RepositoryContext,
    WorkerExecutionError,
    WorkerInvocation,
    WorkerOutput,
    Worktree,
)

SECRET = b"test-webhook-secret"
REPOSITORY = "daniel/probare-crm"
MATT_POCOCK_SKILL_ROOT = (
    Path(__file__).resolve().parents[2]
    / "skills-repo"
    / "vendor"
    / "mattpocock"
    / ".agents"
    / "skills"
)


class ControlledGitHub:
    def __init__(self) -> None:
        self.labels: set[str] = {"ready-for-agent"}
        self.open = True
        self.open_blockers = False
        self.label_writes: list[tuple[str, int, str]] = []
        self.pull_request_writes: list[object] = []
        self.title = "Add customer export"
        self.body = "- [ ] Customer can export CSV\n- [ ] Export includes active filters"
        self.issue_type = "feature"
        self.findings: tuple[str, ...] = ()

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        return IssueState(
            open=self.open,
            labels=frozenset(self.labels),
            has_open_blockers=self.open_blockers,
            title=self.title,
            body=self.body,
            issue_type=self.issue_type,
            findings=self.findings,
        )

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        if label not in self.labels:
            self.labels.add(label)
            self.label_writes.append((repository, issue_number, label))


class ControlledWorktrees:
    def __init__(self, root) -> None:
        self.root = root
        self.calls: list[dict[str, object]] = []

    def create(self, *, run_id: str, repository: str, repository_root, base_ref: str) -> Worktree:
        self.calls.append(
            {
                "run_id": run_id,
                "repository": repository,
                "repository_root": repository_root,
                "base_ref": base_ref,
            }
        )
        return Worktree(path=self.root / run_id, branch=f"codex/run-{run_id}", base_ref=base_ref)


class ControlledWorker:
    def __init__(self) -> None:
        self.invocations: list[WorkerInvocation] = []

    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        self.invocations.append(invocation)
        return WorkerOutput(result={
            "schema_version": "1",
            "outcome": "completed",
            "summary": "Implemented customer export",
            "red_green_slices": [
                {
                    "requirement": "Customer can export CSV",
                    "red": {"command": "pytest export", "observed": "failed: export missing"},
                    "green": {"command": "pytest export", "observed": "passed"},
                }
            ],
            "changed_files": ["src/export.py"],
            "verification": [{"command": "pytest", "observed": "passed"}],
            "evidence": [{"criterion": "Customer can export CSV", "proof": "HTTP read-back passed"}],
            "findings": [],
        }, diagnostic_events=({"type": "turn.completed", "thread_id": "thread-001"},))


class FailingWorker(ControlledWorker):
    def __init__(self, failure_mode: str) -> None:
        super().__init__()
        self.failure_mode = failure_mode

    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        output = super().run(invocation)
        invocation.worktree.path.mkdir(parents=True)
        (invocation.worktree.path / "worker-change.txt").write_text(
            "assigned worktree only\n", encoding="utf-8"
        )
        if self.failure_mode == "process":
            raise WorkerExecutionError("simulated Codex exit 1")
        output.result["red_green_slices"] = []
        return output


def controlled_implementation_services(
    tmp_path,
    worktrees: ControlledWorktrees,
    worker: ControlledWorker,
    *,
    repository_root=None,
) -> ImplementationServices:
    return ImplementationServices(
        repository_roots={REPOSITORY: repository_root or tmp_path / "daniels-checkout"},
        repository_contexts={
            REPOSITORY: RepositoryContext(
                base_ref="main",
                instructions="Follow repository AGENTS.md and test through the public API.",
                public_observation_surface="HTTP API",
                verification_command="pytest tests/test_export.py",
            )
        },
        skill_root=MATT_POCOCK_SKILL_ROOT,
        worktrees=worktrees,
        worker=worker,
    )


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
        allowed_repositories={REPOSITORY},
        github=ControlledGitHub(),
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
        allowed_repositories={REPOSITORY},
        github=github,
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
        allowed_repositories={REPOSITORY},
        github=github,
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
        allowed_repositories={REPOSITORY},
        github=github,
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
        allowed_repositories={REPOSITORY},
        github=github,
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
        allowed_repositories={REPOSITORY},
        github=github,
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
        allowed_repositories={REPOSITORY},
        github=github,
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
        allowed_repositories={REPOSITORY},
        github=github,
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
        allowed_repositories={REPOSITORY},
        github=github,
        clock=fixed_clock,
    )

    with TestClient(first_app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=headers)
        before_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        allowed_repositories={REPOSITORY},
        github=github,
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


def test_claimed_issue_persists_bounded_assignment_and_evidence_before_worker_invocation(tmp_path) -> None:
    github = ControlledGitHub()
    github.findings = ("Keep export authorization unchanged",)
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    services = controlled_implementation_services(tmp_path, worktrees, worker)
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        allowed_repositories={REPOSITORY},
        github=github,
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assignment = state["implementation"]["assignment"]
    assert accepted.status_code == 202
    assert set(assignment) == {
        "schema_version",
        "issue",
        "requirements",
        "repository_context",
        "evidence_matrix",
        "findings",
    }
    assert assignment["issue"] == {
        "repository": REPOSITORY,
        "number": 41,
        "title": "Add customer export",
        "body": "- [ ] Customer can export CSV\n- [ ] Export includes active filters",
        "type": "feature",
    }
    assert assignment["requirements"] == [
        "Customer can export CSV",
        "Export includes active filters",
    ]
    assert assignment["repository_context"] == {
        "base_ref": "main",
        "instructions": "Follow repository AGENTS.md and test through the public API.",
    }
    assert [entry["criterion"] for entry in assignment["evidence_matrix"]] == assignment[
        "requirements"
    ]
    assert all(
        set(entry)
        == {"criterion", "public_observation_surface", "expected_result", "planned_proof"}
        for entry in assignment["evidence_matrix"]
    )
    assert all(
        entry["public_observation_surface"] == "HTTP API"
        and "pytest tests/test_export.py" in entry["planned_proof"]
        for entry in assignment["evidence_matrix"]
    )
    assert assignment["findings"] == ["Keep export authorization unchanged"]
    assert state["implementation"]["policy"] == {
        "version": "1",
        "model": "gpt-5.6-terra",
        "reasoning_effort": "xhigh",
    }
    assert [skill["name"] for skill in state["implementation"]["skills"]] == [
        "implement",
        "tdd",
    ]
    assert all(len(skill["content_sha256"]) == 64 for skill in state["implementation"]["skills"])
    assert state["implementation"]["access_profile"]["sandbox"] == "workspace-write"
    assert len(worker.invocations) == 1
    assert worker.invocations[0].assignment == assignment


def test_valid_red_green_worker_result_is_persisted_and_observable_after_restart(tmp_path) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    services = controlled_implementation_services(tmp_path, worktrees, worker)
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        allowed_repositories={REPOSITORY},
        github=github,
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        before_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        allowed_repositories={REPOSITORY},
        github=github,
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(restarted_app) as client:
        after_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    implementation = before_restart["implementation"]
    assert implementation["status"] == "completed"
    assert implementation["result"]["outcome"] == "completed"
    assert implementation["result"]["red_green_slices"] == [
        {
            "requirement": "Customer can export CSV",
            "red": {"command": "pytest export", "observed": "failed: export missing"},
            "green": {"command": "pytest export", "observed": "passed"},
        }
    ]
    assert implementation["diagnostic_events"] == [
        {"type": "turn.completed", "thread_id": "thread-001"}
    ]
    assert implementation["completed_at"] == "2026-08-21T10:30:00+00:00"
    assert after_restart == before_restart
    assert len(worker.invocations) == 1


@pytest.mark.parametrize("failure_mode", ["invalid-result", "process"])
def test_failed_worker_is_contained_and_duplicate_delivery_starts_nothing_else(
    tmp_path, failure_mode: str
) -> None:
    daniels_checkout = tmp_path / "daniels-checkout"
    sibling_worktree = tmp_path / "sibling-worktree"
    daniels_checkout.mkdir()
    sibling_worktree.mkdir()
    (daniels_checkout / "marker.txt").write_text("Daniel's checkout\n", encoding="utf-8")
    (sibling_worktree / "marker.txt").write_text("sibling run\n", encoding="utf-8")
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worker-worktrees")
    worker = FailingWorker(failure_mode)
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        repository_root=daniels_checkout,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        allowed_repositories={REPOSITORY},
        github=github,
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()
    headers = signed_headers(body)

    with TestClient(app) as client:
        first = client.post("/webhooks/github", content=body, headers=headers)
        repeated = client.post("/webhooks/github", content=body, headers=headers)
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    implementation = state["implementation"]
    assert first.status_code == 202
    assert repeated.json()["status"] == "already_accepted"
    assert implementation["status"] == "failed"
    assert implementation["result"] is None
    assert implementation["error"].startswith(
        "InvalidWorkerResult:" if failure_mode == "invalid-result" else "WorkerExecutionError:"
    )
    assert implementation["access_profile"] == {
        "role": "implementer",
        "sandbox": "workspace-write",
        "write_root": implementation["worktree"]["path"],
        "additional_write_roots": [],
    }
    assert Path(implementation["worktree"]["path"], "worker-change.txt").read_text(
        encoding="utf-8"
    ) == "assigned worktree only\n"
    assert (daniels_checkout / "marker.txt").read_text(encoding="utf-8") == "Daniel's checkout\n"
    assert (sibling_worktree / "marker.txt").read_text(encoding="utf-8") == "sibling run\n"
    assert len(worktrees.calls) == 1
    assert len(worker.invocations) == 1
    assert github.pull_request_writes == []
