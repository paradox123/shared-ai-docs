from __future__ import annotations

import json
import subprocess
from io import StringIO
from pathlib import Path

import httpx
import pytest

from github_issue_pilot.activation import run_cli

REPOSITORY = "daniel/probare-crm"
SECRET = "never-print-live-token"


def initialized_repository(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init", "-b", "main", str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "remote", "add", "origin", f"git@github.com:{REPOSITORY}.git"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "--local", "user.name", "daniel"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "config",
            "--local",
            "user.email",
            "11044764+daniel@users.noreply.github.com",
        ],
        check=True,
    )
    return path


def live_environment(tmp_path: Path) -> dict[str, str]:
    repository = initialized_repository(tmp_path / "repository")
    worktrees = tmp_path / "worktrees"
    worktrees.mkdir()
    context = tmp_path / "AGENTS.md"
    context.write_text("Repository guidance\n", encoding="utf-8")
    skills = tmp_path / "skills"
    skills.mkdir()
    tunnel = tmp_path / "tunnel.yml"
    tunnel.write_text("ingress: []\n", encoding="utf-8")
    return {
        "PILOT_ALLOWED_REPOSITORIES": REPOSITORY,
        "PILOT_REPOSITORY_ROOT": str(repository),
        "PILOT_WORKTREE_ROOT": str(worktrees),
        "PILOT_REPOSITORY_CONTEXT_PATH": str(context),
        "PILOT_SKILL_ROOT": str(skills),
        "PILOT_BASE_REF": "main",
        "PILOT_GITHUB_WEBHOOK_URL": "https://relay.example.test/webhooks/github",
        "PILOT_PUBLIC_RECEIVER_URL": "https://pilot.example.test/webhooks/github",
        "CLOUDFLARED_CONFIG": str(tunnel),
        "PILOT_VERIFICATION_COMMAND": "pytest -q",
        "GITHUB_TOKEN": SECRET,
        "DANIEL_GITHUB_LOGIN": "daniel",
    }


def ready_github(request: httpx.Request) -> httpx.Response:
    if request.url.path == f"/repos/{REPOSITORY}":
        return httpx.Response(
            200,
            json={
                "default_branch": "main",
                "permissions": {"pull": True, "push": True, "admin": True},
            },
        )
    if request.url.path == f"/repos/{REPOSITORY}/labels":
        return httpx.Response(
            200,
            json=[
                {"name": label}
                for label in (
                    "ready-for-agent",
                    "agent-running",
                    "verified",
                    "awaiting-review",
                    "needs-info",
                    "ready-for-human",
                )
            ],
        )
    if request.url.path == f"/repos/{REPOSITORY}/issues":
        return httpx.Response(
            200,
            json=[
                {
                    "number": 17,
                    "title": "private customer issue title",
                    "state": "open",
                    "labels": [{"name": "ready-for-agent"}],
                    "type": {"name": "Bug"},
                },
                {
                    "number": 18,
                    "title": "private feature title",
                    "state": "open",
                    "labels": [],
                    "type": {"name": "Feature"},
                },
            ],
        )
    if request.url.path == f"/repos/{REPOSITORY}/hooks":
        return httpx.Response(
            200,
            json=[
                {
                    "active": True,
                    "events": [
                        "issue_comment",
                        "issues",
                        "pull_request",
                        "pull_request_review",
                        "pull_request_review_comment",
                    ],
                    "config": {
                        "url": "https://relay.example.test/webhooks/github",
                        "content_type": "json",
                        "insecure_ssl": "0",
                    },
                }
            ],
        )
    raise AssertionError(f"unexpected GitHub request: {request.method} {request.url}")


def test_live_readiness_reports_bounded_profile_and_complete_backlog(tmp_path: Path) -> None:
    output = StringIO()

    exit_code = run_cli(
        ["live-readiness"],
        environment=live_environment(tmp_path),
        transport=httpx.MockTransport(ready_github),
        stdout=output,
    )

    observed = json.loads(output.getvalue())
    assert exit_code == 0
    assert observed == {
        "adapter_version": "1",
        "allowed_event_group_count": 5,
        "base_ref": "main",
        "open_issue_count": 2,
        "profile_hash": observed["profile_hash"],
        "ready_issue_count": 1,
        "repository_hash": observed["repository_hash"],
        "required_label_count": 6,
        "status": "ready",
        "type_counts": {"Bug": 1, "Feature": 1},
        "webhook_count": 1,
    }
    assert len(observed["profile_hash"]) == 64
    assert len(observed["repository_hash"]) == 64
    serialized = output.getvalue()
    assert SECRET not in serialized
    assert "private customer issue title" not in serialized
    assert "private feature title" not in serialized


def test_live_readiness_rejects_webhook_that_bypasses_the_edge_relay(
    tmp_path: Path,
) -> None:
    environment = live_environment(tmp_path)
    environment["PILOT_GITHUB_WEBHOOK_URL"] = environment["PILOT_PUBLIC_RECEIVER_URL"]
    errors = StringIO()

    exit_code = run_cli(
        ["live-readiness"],
        environment=environment,
        transport=httpx.MockTransport(ready_github),
        stdout=StringIO(),
        stderr=errors,
    )

    assert exit_code == 69
    assert json.loads(errors.getvalue()) == {
        "category": "relay_route_unavailable",
        "status": "not_ready",
    }


def test_live_readiness_rejects_git_identity_that_github_privacy_will_block(
    tmp_path: Path,
) -> None:
    environment = live_environment(tmp_path)
    subprocess.run(
        [
            "git",
            "-C",
            environment["PILOT_REPOSITORY_ROOT"],
            "config",
            "--local",
            "user.email",
            "daniel@example.test",
        ],
        check=True,
    )
    errors = StringIO()

    exit_code = run_cli(
        ["live-readiness"],
        environment=environment,
        transport=httpx.MockTransport(ready_github),
        stdout=StringIO(),
        stderr=errors,
    )

    assert exit_code == 69
    assert json.loads(errors.getvalue()) == {
        "category": "git_identity_invalid",
        "status": "not_ready",
    }


@pytest.mark.parametrize(
    ("broken_path", "expected_category"),
    [
        ("/repos/daniel/probare-crm", "github_permission_missing"),
        ("/repos/daniel/probare-crm/labels", "workflow_labels_missing"),
        ("/repos/daniel/probare-crm/hooks", "webhook_configuration_mismatch"),
    ],
)
def test_live_readiness_fails_closed_with_stable_secret_safe_categories(
    tmp_path: Path, broken_path: str, expected_category: str
) -> None:
    writes: list[str] = []

    def broken_github(request: httpx.Request) -> httpx.Response:
        if request.method != "GET":
            writes.append(f"{request.method} {request.url.path}")
        response = ready_github(request)
        if request.url.path != broken_path:
            return response
        payload = response.json()
        if broken_path.endswith("/labels"):
            payload = payload[:-1]
        elif broken_path.endswith("/hooks"):
            payload[0]["active"] = False
        else:
            payload["permissions"]["admin"] = False
        return httpx.Response(200, json=payload)

    output = StringIO()
    errors = StringIO()
    exit_code = run_cli(
        ["live-readiness"],
        environment=live_environment(tmp_path),
        transport=httpx.MockTransport(broken_github),
        stdout=output,
        stderr=errors,
    )

    assert exit_code == 69
    assert output.getvalue() == ""
    assert json.loads(errors.getvalue()) == {
        "category": expected_category,
        "status": "not_ready",
    }
    assert writes == []
    assert SECRET not in errors.getvalue()


def test_live_readiness_rejects_checkout_for_another_repository_before_github(
    tmp_path: Path,
) -> None:
    environment = live_environment(tmp_path)
    subprocess.run(
        [
            "git",
            "-C",
            environment["PILOT_REPOSITORY_ROOT"],
            "remote",
            "set-url",
            "origin",
            "git@github.com:daniel/another-repository.git",
        ],
        check=True,
    )
    requests: list[str] = []

    def unexpected_github(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        return httpx.Response(500)

    errors = StringIO()
    exit_code = run_cli(
        ["live-readiness"],
        environment=environment,
        transport=httpx.MockTransport(unexpected_github),
        stdout=StringIO(),
        stderr=errors,
    )

    assert exit_code == 69
    assert json.loads(errors.getvalue()) == {
        "category": "repository_origin_mismatch",
        "status": "not_ready",
    }
    assert requests == []


def test_ensure_live_labels_creates_only_missing_definitions_and_converges(
    tmp_path: Path,
) -> None:
    labels = {
        "ready-for-agent",
        "agent-running",
        "verified",
        "awaiting-review",
    }
    created: list[dict[str, object]] = []

    def github(request: httpx.Request) -> httpx.Response:
        if request.url.path == f"/repos/{REPOSITORY}":
            return ready_github(request)
        if request.url.path == f"/repos/{REPOSITORY}/labels" and request.method == "GET":
            return httpx.Response(200, json=[{"name": label} for label in sorted(labels)])
        if request.url.path == f"/repos/{REPOSITORY}/labels" and request.method == "POST":
            payload = json.loads(request.content)
            created.append(payload)
            labels.add(payload["name"])
            return httpx.Response(201, json=payload)
        raise AssertionError(f"unexpected GitHub request: {request.method} {request.url}")

    environment = live_environment(tmp_path)
    first_output = StringIO()
    first = run_cli(
        ["ensure-live-labels"],
        environment=environment,
        transport=httpx.MockTransport(github),
        stdout=first_output,
    )
    second_output = StringIO()
    second = run_cli(
        ["ensure-live-labels"],
        environment=environment,
        transport=httpx.MockTransport(github),
        stdout=second_output,
    )

    assert first == second == 0
    assert json.loads(first_output.getvalue()) == {
        "created_count": 2,
        "existing_count": 4,
        "repository_hash": json.loads(first_output.getvalue())["repository_hash"],
        "required_label_count": 6,
        "status": "labels_ready",
    }
    assert json.loads(second_output.getvalue()) == {
        "created_count": 0,
        "existing_count": 6,
        "repository_hash": json.loads(second_output.getvalue())["repository_hash"],
        "required_label_count": 6,
        "status": "labels_ready",
    }
    assert [payload["name"] for payload in created] == ["needs-info", "ready-for-human"]
    assert all(set(payload) == {"color", "description", "name"} for payload in created)
    assert all("issues" not in path for path in [f"/repos/{REPOSITORY}/labels"])
    assert SECRET not in first_output.getvalue() + second_output.getvalue()


def verified_workflow(head_sha: str) -> dict[str, object]:
    body = f"""## Behavioral Evidence — head `{head_sha}`

| Criterion | Verdict | Observed interface | Expected result | Head |
| --- | --- | --- | --- | --- |
| Live behavior | pass | browser and REST | visible result | `{head_sha}` |

![Evidence: Live behavior](https://example.test/redacted.png)

```text
POST /api/items -> 201; GET /api/items/17 -> expected result
```

- **log** — transition completed (correlation `run-17`)

Closes #17
"""
    results = []
    for axis, skill_names in (
        ("requirements", ["code-review"]),
        ("code", ["code-review"]),
        ("architecture", ["codebase-design", "domain-modeling"]),
    ):
        results.append(
            {
                "axis": axis,
                "assignment": {"invocation_id": f"review-17:{axis}"},
                "verdict": {
                    "invocation_id": f"review-17:{axis}",
                    "axis": axis,
                    "head_sha": head_sha,
                    "verdict": "pass",
                    "rationale": "Current head satisfies this axis.",
                    "findings": [],
                },
                "policy": {
                    "model": "gpt-5.6-terra",
                    "reasoning_effort": "xhigh",
                    "sandbox": "read-only",
                },
                "skills": [
                    {"name": name, "content_sha256": str(index + 1) * 64}
                    for index, name in enumerate(skill_names)
                ],
            }
        )
    return {
        "delivery": {"id": "delivery-17", "status": "processed"},
        "run": {"id": "run-17", "status": "running"},
        "checkpoint": {
            "id": "checkpoint-17",
            "thread_id": "run-17",
            "values": {"status": "verified"},
        },
        "implementation": {
            "status": "completed",
            "policy": {
                "model": "gpt-5.6-terra",
                "reasoning_effort": "xhigh",
                "sandbox": "workspace-write",
            },
            "skills": [{"name": "tdd", "content_sha256": "a" * 64}],
            "result": {
                "verification": [
                    {"command": "pytest -q", "observed": "passed on published changes"}
                ]
            },
        },
        "draft_pull_request": {
            "status": "published",
            "head_sha": head_sha,
            "body": body,
            "evidence": [
                {
                    "criterion": "Live behavior",
                    "observations": [
                        {"phase": "interaction", "artifact": "clicked save"},
                        {
                            "phase": "screenshot",
                            "artifact": "https://example.test/redacted.png",
                        },
                        {"phase": "request", "artifact": "POST /api/items"},
                        {"phase": "response", "artifact": "201 created"},
                        {"phase": "read_back", "artifact": "GET /api/items/17"},
                        {
                            "phase": "log",
                            "artifact": "transition completed",
                            "correlation_id": "run-17",
                        },
                    ],
                }
            ],
            "pull_request": {"number": 77, "draft": True},
        },
        "review": {
            "id": "review-17",
            "status": "verified",
            "head_sha": head_sha,
            "projected_labels": ["awaiting-review", "ready-for-agent", "verified"],
            "results": results,
        },
        "repair": None,
    }


def test_capture_live_evidence_requires_one_exact_head_and_writes_bounded_manifest(
    tmp_path: Path,
) -> None:
    head_sha = "a1" * 20
    workflow = verified_workflow(head_sha)

    def live_boundaries(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/workflows/daniel/probare-crm/issues/17":
            return httpx.Response(200, json=workflow)
        if request.url.path == f"/repos/{REPOSITORY}/pulls/77":
            return httpx.Response(
                200,
                json={
                    "number": 77,
                    "draft": True,
                    "head": {"sha": head_sha},
                    "body": workflow["draft_pull_request"]["body"],
                    "merged": False,
                    "merged_at": None,
                },
            )
        if request.url.path == f"/repos/{REPOSITORY}/issues/17/labels":
            return httpx.Response(
                200,
                json=[
                    {"name": "ready-for-agent"},
                    {"name": "verified"},
                    {"name": "awaiting-review"},
                ],
            )
        raise AssertionError(f"unexpected boundary request: {request.method} {request.url}")

    environment = live_environment(tmp_path)
    environment["PILOT_PORT"] = "18788"
    manifest_path = tmp_path / "private" / "live-evidence.json"
    output = StringIO()
    exit_code = run_cli(
        ["capture-live-evidence", "17", str(manifest_path)],
        environment=environment,
        transport=httpx.MockTransport(live_boundaries),
        stdout=output,
    )

    assert exit_code == 0
    assert json.loads(output.getvalue()) == {
        "head_sha": head_sha,
        "manifest_sha256": json.loads(output.getvalue())["manifest_sha256"],
        "status": "evidence_captured",
    }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest == {
        "adapter_version": "1",
        "checkpoint_id": "checkpoint-17",
        "checkpoint_status": "verified",
        "delivery_id": "delivery-17",
        "evidence": {
            "body_sha256": manifest["evidence"]["body_sha256"],
            "correlated_log_count": 1,
            "criterion_count": 1,
            "rest_artifact_count": 3,
            "screenshot_count": 1,
        },
        "head_sha": head_sha,
        "issue_number": 17,
        "labels": ["awaiting-review", "ready-for-agent", "verified"],
        "pull_request_number": 77,
        "repository_hash": manifest["repository_hash"],
        "reviews": [
            {
                "axis": axis,
                "invocation_id": f"review-17:{axis}",
                "model": "gpt-5.6-terra",
                "reasoning_effort": "xhigh",
                "skill_hashes": review["skill_hashes"],
                "verdict": "pass",
            }
            for axis, review in zip(
                ("requirements", "code", "architecture"),
                manifest["reviews"],
                strict=True,
            )
        ],
        "run_id": "run-17",
        "schema_version": "1",
        "status": "verified",
        "verification": {
            "checks": 1,
            "source": "implementation",
        },
        "worker": {
            "model": "gpt-5.6-terra",
            "reasoning_effort": "xhigh",
            "skill_hashes": {"tdd": "a" * 64},
        },
    }
    assert manifest_path.stat().st_mode & 0o777 == 0o600
    assert len(json.loads(output.getvalue())["manifest_sha256"]) == 64
    assert SECRET not in manifest_path.read_text(encoding="utf-8") + output.getvalue()


def test_capture_live_evidence_accepts_direct_document_readback_without_ui_artifacts(
    tmp_path: Path,
) -> None:
    head_sha = "b2" * 20
    workflow = verified_workflow(head_sha)
    workflow["draft_pull_request"]["body"] = f"""## Behavioral Evidence — head `{head_sha}`

| Criterion | Verdict | Observed interface | Expected result | Head |
| --- | --- | --- | --- | --- |
| Manual send | pass | rendered Markdown | explicit human confirmation | `{head_sha}` |

### 1. Manual send

- **read_back** — The rendered PRD requires explicit human confirmation.

```text
docs/probare-crm-mvp-prd.md
```

Closes #17
"""
    workflow["draft_pull_request"]["evidence"] = [
        {
            "criterion": "Manual send",
            "kind": "document",
            "observations": [
                {
                    "phase": "read_back",
                    "artifact": "docs/probare-crm-mvp-prd.md",
                }
            ],
        }
    ]
    workflow["implementation"]["result"]["verification"].append(
        {"command": "find test harness", "observed": "No executable harness exists."}
    )

    def live_boundaries(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/workflows/daniel/probare-crm/issues/17":
            return httpx.Response(200, json=workflow)
        if request.url.path == f"/repos/{REPOSITORY}/pulls/77":
            return httpx.Response(
                200,
                json={
                    "number": 77,
                    "draft": True,
                    "head": {"sha": head_sha},
                    "body": workflow["draft_pull_request"]["body"],
                    "merged": False,
                    "merged_at": None,
                },
            )
        if request.url.path == f"/repos/{REPOSITORY}/issues/17/labels":
            return httpx.Response(
                200,
                json=[
                    {"name": "ready-for-agent"},
                    {"name": "verified"},
                    {"name": "awaiting-review"},
                ],
            )
        raise AssertionError(f"unexpected boundary request: {request.method} {request.url}")

    environment = live_environment(tmp_path)
    manifest_path = tmp_path / "private" / "document-evidence.json"
    assert run_cli(
        ["capture-live-evidence", "17", str(manifest_path)],
        environment=environment,
        transport=httpx.MockTransport(live_boundaries),
        stdout=StringIO(),
    ) == 0

    evidence = json.loads(manifest_path.read_text(encoding="utf-8"))["evidence"]
    assert evidence["criterion_count"] == 1
    assert evidence["rest_artifact_count"] == 1
    assert evidence["screenshot_count"] == 0
    assert evidence["correlated_log_count"] == 0


def test_capture_live_evidence_rejects_a_stale_current_pull_request_head(
    tmp_path: Path,
) -> None:
    verified_head = "a1" * 20
    current_head = "b2" * 20
    workflow = verified_workflow(verified_head)

    def stale_boundaries(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/workflows/daniel/probare-crm/issues/17":
            return httpx.Response(200, json=workflow)
        if request.url.path == f"/repos/{REPOSITORY}/pulls/77":
            return httpx.Response(
                200,
                json={
                    "number": 77,
                    "draft": True,
                    "head": {"sha": current_head},
                    "body": workflow["draft_pull_request"]["body"],
                    "merged": False,
                    "merged_at": None,
                },
            )
        if request.url.path == f"/repos/{REPOSITORY}/issues/17/labels":
            return httpx.Response(200, json=[{"name": "verified"}])
        raise AssertionError(f"unexpected boundary request: {request.method} {request.url}")

    environment = live_environment(tmp_path)
    output_path = tmp_path / "stale-evidence.json"
    errors = StringIO()
    exit_code = run_cli(
        ["capture-live-evidence", "17", str(output_path)],
        environment=environment,
        transport=httpx.MockTransport(stale_boundaries),
        stdout=StringIO(),
        stderr=errors,
    )

    assert exit_code == 69
    assert json.loads(errors.getvalue()) == {
        "category": "pull_request_head_mismatch",
        "status": "not_ready",
    }
    assert not output_path.exists()
