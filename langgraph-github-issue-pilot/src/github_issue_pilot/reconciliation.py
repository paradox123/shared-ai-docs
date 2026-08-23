from __future__ import annotations

import hashlib
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path

from github_issue_pilot.storage import Delivery


@dataclass(frozen=True)
class ReconciliationCommand:
    command_key: str
    repository: str
    issue_number: int
    kind: str
    action: str
    pull_request_number: int | None = None
    actor_login: str | None = None
    head_sha: str | None = None
    merged: bool = False

    def delivery(self, *, boot_id: str, accepted_at: str) -> Delivery:
        identity = hashlib.sha256(f"{boot_id}\n{self.command_key}".encode()).hexdigest()
        return Delivery(
            delivery_id=f"reconcile-{identity}",
            body_digest=hashlib.sha256(self.command_key.encode()).hexdigest(),
            repository=self.repository,
            issue_number=self.issue_number,
            event="reconciliation",
            action=self.action,
            accepted_at=accepted_at,
            kind=self.kind,
            pull_request_number=self.pull_request_number,
            actor_login=self.actor_login,
            head_sha=self.head_sha,
            merged=self.merged,
            command_key=self.command_key,
        )


def ready_issue_command(
    *, repository: str, issue_number: int, ready_label: str
) -> ReconciliationCommand:
    return ReconciliationCommand(
        command_key=f"issue-label:{repository}:{issue_number}:{ready_label.casefold()}",
        repository=repository,
        issue_number=issue_number,
        kind="repository_activity",
        action="ready",
    )


def human_merge_command(
    *,
    repository: str,
    issue_number: int,
    pull_request_number: int,
    head_sha: str,
    actor_login: str,
) -> ReconciliationCommand:
    return ReconciliationCommand(
        command_key=(
            f"pull-merged:{repository}:{pull_request_number}:{head_sha.casefold()}"
        ),
        repository=repository,
        issue_number=issue_number,
        kind="human_merge",
        action="human_merged",
        pull_request_number=pull_request_number,
        actor_login=actor_login,
        head_sha=head_sha,
        merged=True,
    )


def system_boot_session_id() -> str:
    if platform.system() == "Linux":
        value = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="utf-8").strip()
    elif platform.system() == "Darwin":
        result = subprocess.run(
            ["sysctl", "-n", "kern.boottime"],
            check=True,
            capture_output=True,
            text=True,
        )
        value = result.stdout.strip()
    else:
        raise RuntimeError("operating-system boot identity is unavailable")
    if not value:
        raise RuntimeError("operating-system boot identity is empty")
    return hashlib.sha256(value.encode()).hexdigest()
