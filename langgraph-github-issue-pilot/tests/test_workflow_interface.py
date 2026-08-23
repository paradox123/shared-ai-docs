from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from github_issue_pilot.app import create_app
from github_issue_pilot.github import (
    BacklogIssue,
    BlockerState,
    DraftPullRequest,
    IssueState,
)
from github_issue_pilot.implementation import (
    ImplementationServices,
    RepositoryContext,
    WorkerExecutionError,
    WorkerInvocation,
    WorkerOutput,
    Worktree,
)
from github_issue_pilot.publication import PublishedHead
from github_issue_pilot.review import ReviewInvocation, ReviewOutput

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
        self.pull_request_writes: list[object] = []
        self.workflow_label_projections: list[dict[str, object]] = []
        self.pull_request_head = ControlledSourceControl.head_sha
        self.reported_head_override: str | None = None
        self.head_reads: list[tuple[str, int]] = []
        self.title = "Add customer export"
        self.body = "- [ ] Customer can export CSV\n- [ ] Export includes active filters"
        self.issue_type = "feature"
        self.findings: tuple[str, ...] = ()

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        return IssueState(
            open=self.open,
            labels=frozenset(self.labels),
            blockers=(BlockerState(40, False, False),) if self.open_blockers else (),
            title=self.title,
            body=self.body,
            issue_type=self.issue_type,
            findings=self.findings,
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

    def ensure_draft_pull_request(
        self,
        repository: str,
        *,
        issue_number: int,
        branch: str,
        title: str,
        body: str,
        head_sha: str,
    ) -> DraftPullRequest:
        write = {
            "repository": repository,
            "issue_number": issue_number,
            "branch": branch,
            "title": title,
            "body": body,
            "head_sha": head_sha,
        }
        self.pull_request_writes.append(write)
        self.pull_request_head = head_sha
        return DraftPullRequest(
            number=77,
            url="https://github.example/daniel/probare-crm/pull/77",
            head_sha=head_sha,
            draft=True,
            body=body,
        )

    def current_pull_request_head(self, repository: str, pull_request_number: int) -> str:
        self.head_reads.append((repository, pull_request_number))
        return self.reported_head_override or self.pull_request_head

    def project_workflow_labels(
        self,
        repository: str,
        issue_number: int,
        *,
        add: frozenset[str],
        remove: frozenset[str],
    ) -> frozenset[str]:
        self.workflow_label_projections.append(
            {
                "repository": repository,
                "issue_number": issue_number,
                "add": add,
                "remove": remove,
            }
        )
        self.labels = (self.labels | set(add)) - set(remove)
        return frozenset(self.labels)


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


def _direct_evidence(criterion: str) -> dict[str, object]:
    return {
        "criterion": criterion,
        "verdict": "pass",
        "kind": "rest",
        "observed_interface": "HTTP API",
        "expected_result": criterion,
        "observations": [
            {
                "phase": "request",
                "description": "Submitted export request",
                "artifact": "POST /exports with active filters",
                "correlation_id": "run-41",
            },
            {
                "phase": "response",
                "description": "Export response contained a CSV resource",
                "artifact": "201 {export_id: exp-41}",
                "correlation_id": "run-41",
            },
            {
                "phase": "read_back",
                "description": "Downloaded export contains the expected customer rows",
                "artifact": "GET /exports/exp-41 -> customer_id,status",
                "correlation_id": "run-41",
            },
            {
                "phase": "log",
                "description": "Correlated export completion",
                "artifact": "export_id=exp-41 status=completed",
                "correlation_id": "run-41",
            },
        ],
    }


class ControlledWorker:
    def __init__(self) -> None:
        self.invocations: list[WorkerInvocation] = []

    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        self.invocations.append(invocation)
        evidence = [_direct_evidence(criterion) for criterion in invocation.assignment["requirements"]]
        return WorkerOutput(result={
            "schema_version": "2",
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
            "evidence": evidence,
            "findings": [],
        }, diagnostic_events=({"type": "turn.completed", "thread_id": "thread-001"},))


class ControlledReviewer:
    def __init__(self, verdicts: dict[str, str] | None = None) -> None:
        self.verdicts = verdicts or {}
        self.invocations: list[ReviewInvocation] = []

    def run(self, invocation: ReviewInvocation) -> ReviewOutput:
        self.invocations.append(invocation)
        axis = str(invocation.assignment["axis"])
        verdict = self.verdicts.get(axis, "pass")
        findings = (
            [{"location": "src/export.py:1", "description": "Code quality regression"}]
            if verdict == "fail"
            else []
        )
        return ReviewOutput(
            result={
                "schema_version": "1",
                "invocation_id": invocation.assignment["invocation_id"],
                "axis": axis,
                "head_sha": invocation.assignment["pull_request"]["head_sha"],
                "verdict": verdict,
                "rationale": f"{axis} review returned {verdict}",
                "findings": findings,
            },
            diagnostic_events=(
                {"type": "turn.completed", "thread_id": f"fresh-{axis}"},
            ),
        )


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


class InsufficientEvidenceWorker(ControlledWorker):
    def __init__(self, failure_mode: str) -> None:
        super().__init__()
        self.failure_mode = failure_mode

    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        output = super().run(invocation)
        evidence = output.result["evidence"]
        if self.failure_mode == "missing-criterion":
            evidence.pop()
        elif self.failure_mode == "negative-without-side-effect-read-back":
            evidence[0].update(
                kind="negative_gate",
                observations=[
                    {
                        "phase": "rejection",
                        "description": "Export was blocked by authorization policy",
                    }
                ],
            )
        elif self.failure_mode == "background-surrogate":
            evidence[0].update(
                kind="background",
                observations=[
                    {
                        "phase": "eventual_result",
                        "description": "queue accepted; process started",
                        "artifact": "healthcheck 200",
                    }
                ],
            )
        return output


class SensitiveEvidenceWorker(ControlledWorker):
    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        output = super().run(invocation)
        output.result["evidence"][0]["observations"][1]["description"] = (
            "Authorization: Bearer ghp_12345678901234567890 for daniel@example.com"
        )
        output.result["evidence"][0]["observations"][1]["artifact"] = (
            "secret=super-private-value"
        )
        return WorkerOutput(
            result=output.result,
            diagnostic_events=(
                {"type": "turn.completed", "message": "token=super-private-value"},
            ),
        )


class ControlledSourceControl:
    head_sha = "1234567890abcdef1234567890abcdef12345678"

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def publish(self, worktree, *, issue_number: int, sensitive_values=()) -> PublishedHead:
        self.calls.append(
            {
                "worktree": worktree,
                "issue_number": issue_number,
                "sensitive_values": tuple(sensitive_values),
            }
        )
        return PublishedHead(branch=worktree.branch, head_sha=self.head_sha)


def controlled_implementation_services(
    tmp_path,
    worktrees: ControlledWorktrees,
    worker: ControlledWorker,
    *,
    repository_root=None,
    source_control=None,
    reviewer=None,
    sensitive_values=(),
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
        source_control=source_control,
        reviewer=reviewer,
        sensitive_values=tuple(sensitive_values),
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


def test_claimed_issue_persists_bounded_assignment_and_evidence_before_worker_invocation(tmp_path) -> None:
    github = ControlledGitHub()
    github.findings = ("Keep export authorization unchanged",)
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    services = controlled_implementation_services(tmp_path, worktrees, worker)
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
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
        repository_adapters={REPOSITORY: github},
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
        repository_adapters={REPOSITORY: github},
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


def test_sufficient_evidence_publishes_one_commit_bound_draft_pr_through_http_seam(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    source_control = ControlledSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    draft = state["draft_pull_request"]
    assert accepted.status_code == 202
    assert state["implementation"]["status"] == "completed"
    assert draft["status"] == "published"
    assert draft["head_sha"] == source_control.head_sha
    assert draft["branch"].startswith("codex/run-")
    assert draft["pull_request"] == {
        "number": 77,
        "url": "https://github.example/daniel/probare-crm/pull/77",
        "draft": True,
    }
    assert [item["criterion"] for item in draft["evidence"]] == [
        "Customer can export CSV",
        "Export includes active filters",
    ]
    assert draft["body"].count(f"`{source_control.head_sha}`") >= 3
    assert "POST /exports with active filters" in draft["body"]
    assert "correlation `run-41`" in draft["body"]
    assert "Closes #41" in draft["body"]
    assert len(source_control.calls) == 1
    assert len(github.pull_request_writes) == 1


def test_one_failed_axis_blocks_verification_after_three_independent_reviews_through_http_seam(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = ControlledSourceControl()
    reviewer = ControlledReviewer({"code": "fail"})
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        ControlledWorker(),
        source_control=source_control,
        reviewer=reviewer,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    review = state["review"]
    assert accepted.status_code == 202
    assert review["status"] == "blocked"
    assert review["reason"] == "review_failed"
    assert review["head_sha"] == source_control.head_sha
    assert [result["axis"] for result in review["results"]] == [
        "requirements",
        "code",
        "architecture",
    ]
    assert [result["verdict"]["verdict"] for result in review["results"]] == [
        "pass",
        "fail",
        "pass",
    ]
    assert [result["policy"]["task"] for result in review["results"]] == [
        "requirements_review",
        "code_review",
        "architecture_review",
    ]
    assert {
        (result["policy"]["model"], result["policy"]["reasoning_effort"])
        for result in review["results"]
    } == {("gpt-5.6-terra", "xhigh")}
    assert [result["route_axis"] for result in review["results"]] == [
        "spec",
        "standards",
        "architecture",
    ]
    assert [[skill["name"] for skill in result["skills"]] for result in review["results"]] == [
        ["code-review"],
        ["code-review"],
        ["codebase-design", "domain-modeling"],
    ]
    assert all(
        len(skill["content_sha256"]) == 64
        for result in review["results"]
        for skill in result["skills"]
    )
    assert "requirement" in review["results"][0]["assignment"]["scope"].casefold()
    assert "code smells" in review["results"][1]["assignment"]["scope"].casefold()
    assert "domain language" in review["results"][2]["assignment"]["scope"].casefold()
    assert len(reviewer.invocations) == 3
    assert len({item.assignment["invocation_id"] for item in reviewer.invocations}) == 3
    assert {
        item.assignment["pull_request"]["head_sha"] for item in reviewer.invocations
    } == {source_control.head_sha}
    assert all(item.access_profile["sandbox"] == "read-only" for item in reviewer.invocations)
    assert all("peer_verdicts" not in item.assignment for item in reviewer.invocations)
    assert github.workflow_label_projections == []
    assert github.labels == {"ready-for-agent", "agent-running"}
    assert len(source_control.calls) == 1
    assert len(github.pull_request_writes) == 1


def test_all_applicable_axes_pass_and_project_verified_current_head_through_http_seam(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = ControlledSourceControl()
    reviewer = ControlledReviewer({"architecture": "not_applicable"})
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        ControlledWorker(),
        source_control=source_control,
        reviewer=reviewer,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    review = state["review"]
    assert review["status"] == "verified"
    assert review["head_sha"] == source_control.head_sha
    assert [result["verdict"]["verdict"] for result in review["results"]] == [
        "pass",
        "pass",
        "not_applicable",
    ]
    assert review["projected_labels"] == [
        "awaiting-review",
        "ready-for-agent",
        "verified",
    ]
    assert github.workflow_label_projections == [
        {
            "repository": REPOSITORY,
            "issue_number": 41,
            "add": frozenset({"verified", "awaiting-review"}),
            "remove": frozenset({"agent-running"}),
        }
    ]
    assert github.labels == {"ready-for-agent", "verified", "awaiting-review"}


def test_changed_head_blocks_projection_and_review_batch_survives_restart_without_new_effects(
    tmp_path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    github.reported_head_override = "fedcba0987654321fedcba0987654321fedcba09"
    reviewer = ControlledReviewer()
    source_control = ControlledSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        ControlledWorktrees(tmp_path / "worktrees"),
        ControlledWorker(),
        source_control=source_control,
        reviewer=reviewer,
    )
    body = delivery_body()
    headers = signed_headers(body)
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=body, headers=headers)
        before_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(restarted_app) as client:
        after_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert before_restart["review"]["status"] == "blocked"
    assert before_restart["review"]["reason"] == "head_changed"
    assert before_restart["review"]["head_sha"] == source_control.head_sha
    assert after_restart["review"] == before_restart["review"]
    assert len(reviewer.invocations) == 3
    assert github.head_reads == [(REPOSITORY, 77)]
    assert github.workflow_label_projections == []


@pytest.mark.parametrize(
    ("failure_mode", "expected_reason"),
    [
        ("missing-criterion", "criterion_coverage"),
        ("negative-without-side-effect-read-back", "missing_direct_observation"),
        ("background-surrogate", "infrastructure_surrogate"),
    ],
    ids=["missing-criterion", "negative-gate", "background-surrogate"],
)
def test_insufficient_evidence_is_durably_rejected_without_source_or_pr_effect(
    tmp_path,
    failure_mode: str,
    expected_reason: str,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = ControlledSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        InsufficientEvidenceWorker(failure_mode),
        source_control=source_control,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    rejection = state["draft_pull_request"]
    assert state["implementation"]["status"] == "completed"
    assert rejection == {
        "status": "rejected",
        "evidence": [],
        "branch": None,
        "head_sha": None,
        "body": None,
        "pull_request": None,
        "reason": expected_reason,
        "started_at": "2026-08-21T10:30:00+00:00",
        "completed_at": "2026-08-21T10:30:00+00:00",
    }
    assert source_control.calls == []
    assert github.pull_request_writes == []


def test_duplicate_delivery_keeps_one_published_head_and_draft_pull_request(tmp_path) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    source_control = ControlledSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()
    headers = signed_headers(body)

    with TestClient(app) as client:
        first = client.post("/webhooks/github", content=body, headers=headers)
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()
        repeated = client.post("/webhooks/github", content=body, headers=headers)
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert first.status_code == 202
    assert repeated.json()["status"] == "already_accepted"
    assert after["draft_pull_request"] == before["draft_pull_request"]
    assert len(worker.invocations) == 1
    assert len(source_control.calls) == 1
    assert len(github.pull_request_writes) == 1


def test_published_draft_pr_remains_observable_after_restart_without_another_write(
    tmp_path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    source_control = ControlledSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
    )
    body = delivery_body()
    headers = signed_headers(body)
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=body, headers=headers)
        before_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(restarted_app) as client:
        after_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert after_restart["draft_pull_request"] == before_restart["draft_pull_request"]
    assert after_restart["draft_pull_request"]["status"] == "published"
    assert after_restart["draft_pull_request"]["head_sha"] == source_control.head_sha
    assert len(worker.invocations) == 1
    assert len(source_control.calls) == 1
    assert len(github.pull_request_writes) == 1


def test_sensitive_worker_evidence_and_diagnostics_are_redacted_before_read_back(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = ControlledSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        SensitiveEvidenceWorker(),
        source_control=source_control,
        sensitive_values=("super-private-value",),
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    serialized = json.dumps(state, sort_keys=True)
    assert "super-private-value" not in serialized
    assert "ghp_12345678901234567890" not in serialized
    assert "daniel@example.com" not in serialized
    assert serialized.count("[REDACTED]") >= 4
    assert source_control.calls[0]["sensitive_values"] == ("super-private-value",)


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
        repository_adapters={REPOSITORY: github},
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
