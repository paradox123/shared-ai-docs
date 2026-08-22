from __future__ import annotations

import re
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from typing import Protocol

import httpx

REPOSITORY_ADAPTER_VERSION = "1"
AUTHORIZED_ORIGINS = frozenset({"daniel_issue", "linked_prd", "parent_chain"})


@dataclass(frozen=True)
class AuthorizationEvidence:
    origin: str = "unproven"
    within_inherited_scope: bool = False


@dataclass(frozen=True)
class BlockerState:
    issue_number: int
    issue_closed: bool
    pull_request_merged: bool


@dataclass(frozen=True)
class IssueState:
    open: bool
    labels: frozenset[str]
    issue_type: str = "issue"
    authorization: AuthorizationEvidence = AuthorizationEvidence()
    blockers: tuple[BlockerState, ...] = ()
    implementation_pr_merged: bool = False
    title: str = ""
    body: str = ""
    findings: tuple[str, ...] = ()


@dataclass(frozen=True)
class BacklogIssue:
    issue_number: int
    state: IssueState


class GitHubPort(Protocol):
    def issue_state(self, repository: str, issue_number: int) -> IssueState: ...

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None: ...


class RepositoryDataPort(GitHubPort, Protocol):
    def backlog(self, repository: str, trigger_issue_number: int) -> tuple[BacklogIssue, ...]: ...


class RepositoryAdapter(Protocol):
    contract_version: str
    repository: str
    ready_label: str
    running_label: str
    allowed_event_actions: AbstractSet[tuple[str, str]]

    def issue_state(self, repository: str, issue_number: int) -> IssueState: ...

    def backlog(self, trigger_issue_number: int) -> tuple[BacklogIssue, ...]: ...

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None: ...


@dataclass(frozen=True)
class RepositorySettings:
    repository: str
    ready_label: str = "ready-for-agent"
    running_label: str = "agent-running"
    allowed_event_actions: AbstractSet[tuple[str, str]] = frozenset({("issues", "labeled")})


class ConfiguredRepositoryAdapter:
    contract_version = REPOSITORY_ADAPTER_VERSION

    def __init__(self, github: RepositoryDataPort, settings: RepositorySettings) -> None:
        self._github = github
        self.repository = settings.repository
        self.ready_label = settings.ready_label
        self.running_label = settings.running_label
        self.allowed_event_actions = settings.allowed_event_actions

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        return self._github.issue_state(repository, issue_number)

    def backlog(self, trigger_issue_number: int) -> tuple[BacklogIssue, ...]:
        return tuple(self._github.backlog(self.repository, trigger_issue_number))

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        self._github.ensure_label(repository, issue_number, label)


class GitHubHttpAdapter:
    def __init__(
        self,
        token: str,
        *,
        human_login: str,
        api_url: str = "https://api.github.com",
        api_version: str = "2026-03-10",
        timeout_seconds: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._human_login = human_login.casefold()
        self._client = httpx.Client(
            base_url=api_url,
            timeout=timeout_seconds,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": api_version,
            },
            transport=transport,
        )

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        issue_response = self._client.get(f"/repos/{repository}/issues/{issue_number}")
        issue_response.raise_for_status()
        return self._issue_state_from_payload(repository, issue_response.json())

    def backlog(self, repository: str, trigger_issue_number: int) -> tuple[BacklogIssue, ...]:
        del trigger_issue_number
        issues = self._paginate(
            f"/repos/{repository}/issues",
            params={"state": "open"},
        )
        return tuple(
            BacklogIssue(int(issue["number"]), self._issue_state_from_payload(repository, issue))
            for issue in issues
            if "pull_request" not in issue
        )

    def _issue_state_from_payload(self, repository: str, issue: dict[str, object]) -> IssueState:
        issue_number = int(issue["number"])
        blocker_payloads = self._paginate(
            f"/repos/{repository}/issues/{issue_number}/dependencies/blocked_by"
        )
        blockers = tuple(
            BlockerState(
                issue_number=int(blocker["number"]),
                issue_closed=blocker.get("state") != "open",
                pull_request_merged=self._implementation_pr_human_merged(
                    repository,
                    int(blocker["number"]),
                ),
            )
            for blocker in blocker_payloads
        )

        labels = self._labels(issue)
        return IssueState(
            open=issue.get("state") == "open",
            labels=labels,
            issue_type=self._issue_type(issue),
            authorization=self._authorization(repository, issue),
            blockers=blockers,
            implementation_pr_merged=self._implementation_pr_human_merged(
                repository,
                issue_number,
            ),
            title=str(issue.get("title", "")),
            body=str(issue.get("body") or ""),
        )

    @staticmethod
    def _labels(issue: dict[str, object]) -> frozenset[str]:
        raw_labels = issue.get("labels", [])
        if not isinstance(raw_labels, list):
            return frozenset()
        return frozenset(
            label if isinstance(label, str) else str(label.get("name", ""))
            for label in raw_labels
            if isinstance(label, (str, dict))
        )

    @staticmethod
    def _issue_type(issue: dict[str, object]) -> str:
        issue_type = issue.get("type")
        if isinstance(issue_type, dict) and issue_type.get("name"):
            return str(issue_type["name"])
        if isinstance(issue_type, str) and issue_type:
            return issue_type
        return "issue"

    def _authorization(
        self,
        repository: str,
        issue: dict[str, object],
    ) -> AuthorizationEvidence:
        if self._login(issue.get("user")) == self._human_login and self._human_login:
            return AuthorizationEvidence(origin="daniel_issue", within_inherited_scope=True)
        if self._has_human_rooted_parent(repository, int(issue["number"])):
            return AuthorizationEvidence(origin="parent_chain", within_inherited_scope=True)
        if self._has_human_authored_prd_link(repository, str(issue.get("body") or "")):
            return AuthorizationEvidence(origin="linked_prd", within_inherited_scope=True)
        return AuthorizationEvidence()

    def _has_human_rooted_parent(self, repository: str, issue_number: int) -> bool:
        seen = {issue_number}
        current = issue_number
        while True:
            response = self._client.get(f"/repos/{repository}/issues/{current}/parent")
            if response.status_code == 404:
                return False
            response.raise_for_status()
            parent = response.json()
            parent_number = int(parent["number"])
            if parent_number in seen:
                return False
            seen.add(parent_number)
            if self._login(parent.get("user")) == self._human_login and self._human_login:
                return True
            current = parent_number

    def _has_human_authored_prd_link(self, repository: str, body: str) -> bool:
        owner, name = map(re.escape, repository.split("/", maxsplit=1))
        pattern = re.compile(
            rf"https://github\.com/{owner}/{name}/issues/(?P<number>\d+)",
            re.IGNORECASE,
        )
        for match in pattern.finditer(body):
            response = self._client.get(
                f"/repos/{repository}/issues/{int(match.group('number'))}"
            )
            response.raise_for_status()
            linked = response.json()
            is_prd = self._issue_type(linked).casefold() == "prd" or "prd" in {
                label.casefold() for label in self._labels(linked)
            }
            if is_prd and self._login(linked.get("user")) == self._human_login:
                return True
        return False

    def _implementation_pr_human_merged(self, repository: str, issue_number: int) -> bool:
        timeline = self._paginate(f"/repos/{repository}/issues/{issue_number}/timeline")
        for event in timeline:
            if event.get("event") != "cross-referenced":
                continue
            source = event.get("source")
            source_issue = source.get("issue") if isinstance(source, dict) else None
            if not isinstance(source_issue, dict) or "pull_request" not in source_issue:
                continue
            if not self._closes_issue(str(source_issue.get("body") or ""), issue_number):
                continue
            pull_number = int(source_issue["number"])
            response = self._client.get(f"/repos/{repository}/pulls/{pull_number}")
            response.raise_for_status()
            pull = response.json()
            merged_by = pull.get("merged_by")
            if pull.get("merged_at") and self._login_type(merged_by) == "user":
                return True
        return False

    @staticmethod
    def _closes_issue(body: str, issue_number: int) -> bool:
        return bool(
            re.search(
                rf"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#?{issue_number}\b",
                body,
            )
        )

    @staticmethod
    def _login(user: object) -> str:
        return str(user.get("login", "")).casefold() if isinstance(user, dict) else ""

    @staticmethod
    def _login_type(user: object) -> str:
        return str(user.get("type", "")).casefold() if isinstance(user, dict) else ""

    def _paginate(
        self,
        path: str,
        *,
        params: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        items: list[dict[str, object]] = []
        page = 1
        while True:
            page_params = dict(params or {})
            page_params.update({"per_page": 100, "page": page})
            response = self._client.get(path, params=page_params)
            response.raise_for_status()
            batch = response.json()
            if not isinstance(batch, list):
                raise TypeError(f"GitHub list endpoint returned non-list payload: {path}")
            items.extend(item for item in batch if isinstance(item, dict))
            if len(batch) < 100:
                return items
            page += 1

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        response = self._client.post(
            f"/repos/{repository}/issues/{issue_number}/labels",
            json={"labels": [label]},
        )
        response.raise_for_status()

    def close(self) -> None:
        self._client.close()
