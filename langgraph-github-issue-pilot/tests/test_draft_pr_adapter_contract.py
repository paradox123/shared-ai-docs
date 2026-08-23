from __future__ import annotations

import httpx

from github_issue_pilot.github import GitHubHttpAdapter

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"


def pull_payload() -> dict[str, object]:
    return {
        "number": 77,
        "html_url": "https://github.example/daniel/probare-crm/pull/77",
        "draft": True,
        "body": "Evidence body",
        "head": {"sha": HEAD_SHA},
    }


def test_github_adapter_creates_one_draft_pull_request_for_the_run_branch() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET":
            assert request.url.path == "/repos/daniel/probare-crm/pulls"
            assert request.url.params["state"] == "open"
            assert request.url.params["head"] == "daniel:codex/run-run-001"
            return httpx.Response(200, json=[])
        assert request.method == "POST"
        assert request.url.path == "/repos/daniel/probare-crm/pulls"
        assert request.read().decode() == (
            '{"title":"Implement #41: Add export","head":"codex/run-run-001",'
            '"base":"main","body":"Evidence body","draft":true}'
        )
        return httpx.Response(201, json=pull_payload())

    adapter = GitHubHttpAdapter(
        "test-token",
        human_login="daniel",
        transport=httpx.MockTransport(handler),
    )

    pull_request = adapter.ensure_draft_pull_request(
        "daniel/probare-crm",
        issue_number=41,
        branch="codex/run-run-001",
        base_ref="main",
        title="Implement #41: Add export",
        body="Evidence body",
        head_sha=HEAD_SHA,
    )

    assert pull_request.number == 77
    assert pull_request.url.endswith("/pull/77")
    assert pull_request.head_sha == HEAD_SHA
    assert pull_request.draft is True
    assert pull_request.body == "Evidence body"
    assert [request.method for request in requests] == ["GET", "POST"]


def test_github_adapter_reuses_existing_draft_for_the_same_branch_and_head() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[pull_payload()])

    adapter = GitHubHttpAdapter(
        "test-token",
        human_login="daniel",
        transport=httpx.MockTransport(handler),
    )

    pull_request = adapter.ensure_draft_pull_request(
        "daniel/probare-crm",
        issue_number=41,
        branch="codex/run-run-001",
        base_ref="main",
        title="Implement #41: Add export",
        body="Evidence body",
        head_sha=HEAD_SHA,
    )

    assert pull_request.number == 77
    assert pull_request.head_sha == HEAD_SHA
    assert [request.method for request in requests] == ["GET"]


def test_github_adapter_updates_stale_evidence_body_on_the_existing_draft() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET":
            stale = pull_payload()
            stale["body"] = "Evidence for an older head"
            return httpx.Response(200, json=[stale])
        assert request.method == "PATCH"
        assert request.url.path == "/repos/daniel/probare-crm/pulls/77"
        assert request.read().decode() == (
            '{"title":"Implement #41: Add export","body":"Evidence body"}'
        )
        return httpx.Response(200, json=pull_payload())

    adapter = GitHubHttpAdapter(
        "test-token",
        human_login="daniel",
        transport=httpx.MockTransport(handler),
    )

    pull_request = adapter.ensure_draft_pull_request(
        "daniel/probare-crm",
        issue_number=41,
        branch="codex/run-run-001",
        base_ref="main",
        title="Implement #41: Add export",
        body="Evidence body",
        head_sha=HEAD_SHA,
    )

    assert pull_request.body == "Evidence body"
    assert [request.method for request in requests] == ["GET", "PATCH"]


def test_github_adapter_reads_current_pr_head_and_converges_verified_workflow_labels() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/repos/daniel/probare-crm/pulls/77":
            assert request.method == "GET"
            return httpx.Response(200, json=pull_payload())
        if request.method == "GET":
            assert request.url.path == "/repos/daniel/probare-crm/issues/41/labels"
            return httpx.Response(
                200,
                json=[
                    {"name": "ready-for-agent"},
                    {"name": "agent-running"},
                    {"name": "customer-export"},
                ],
            )
        assert request.method == "PUT"
        assert request.url.path == "/repos/daniel/probare-crm/issues/41/labels"
        assert request.read().decode() == (
            '{"labels":["awaiting-review","customer-export","ready-for-agent","verified"]}'
        )
        return httpx.Response(
            200,
            json=[
                {"name": "awaiting-review"},
                {"name": "customer-export"},
                {"name": "ready-for-agent"},
                {"name": "verified"},
            ],
        )

    adapter = GitHubHttpAdapter(
        "test-token",
        human_login="daniel",
        transport=httpx.MockTransport(handler),
    )

    assert adapter.current_pull_request_head("daniel/probare-crm", 77) == HEAD_SHA
    projected = adapter.project_workflow_labels(
        "daniel/probare-crm",
        41,
        add=frozenset({"verified", "awaiting-review"}),
        remove=frozenset({"agent-running"}),
    )

    assert projected == frozenset(
        {"ready-for-agent", "customer-export", "verified", "awaiting-review"}
    )
    assert [(request.method, request.url.path) for request in requests] == [
        ("GET", "/repos/daniel/probare-crm/pulls/77"),
        ("GET", "/repos/daniel/probare-crm/issues/41/labels"),
        ("PUT", "/repos/daniel/probare-crm/issues/41/labels"),
    ]
