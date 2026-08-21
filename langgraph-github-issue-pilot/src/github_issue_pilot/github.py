from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass(frozen=True)
class IssueState:
    open: bool
    labels: frozenset[str]
    has_open_blockers: bool


class GitHubPort(Protocol):
    def issue_state(self, repository: str, issue_number: int) -> IssueState: ...

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None: ...


class GitHubHttpAdapter:
    def __init__(
        self,
        token: str,
        *,
        api_url: str = "https://api.github.com",
        api_version: str = "2026-03-10",
        timeout_seconds: float = 10.0,
    ) -> None:
        self._client = httpx.Client(
            base_url=api_url,
            timeout=timeout_seconds,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": api_version,
            },
        )

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        issue_response = self._client.get(f"/repos/{repository}/issues/{issue_number}")
        issue_response.raise_for_status()
        issue = issue_response.json()

        blockers_response = self._client.get(
            f"/repos/{repository}/issues/{issue_number}/dependencies/blocked_by",
            params={"per_page": 100},
        )
        blockers_response.raise_for_status()
        blockers = blockers_response.json()

        labels = frozenset(
            label if isinstance(label, str) else label["name"]
            for label in issue.get("labels", [])
        )
        return IssueState(
            open=issue.get("state") == "open",
            labels=labels,
            has_open_blockers=any(blocker.get("state") == "open" for blocker in blockers),
        )

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        response = self._client.post(
            f"/repos/{repository}/issues/{issue_number}/labels",
            json={"labels": [label]},
        )
        response.raise_for_status()

    def close(self) -> None:
        self._client.close()
