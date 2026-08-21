from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from github_issue_pilot.github import GitHubPort, IssueState
from github_issue_pilot.storage import Delivery, WorkflowStore


class ClaimState(TypedDict):
    delivery_id: str
    repository: str
    issue_number: int
    status: str
    claim_label: str


class WorkflowRuntime:
    def __init__(
        self,
        *,
        database_path: Path,
        store: WorkflowStore,
        github: GitHubPort,
        clock: Callable[[], datetime],
    ) -> None:
        self._store = store
        self._github = github
        self._clock = clock
        self._checkpoint_connection = sqlite3.connect(database_path, check_same_thread=False)
        self._checkpointer = SqliteSaver(self._checkpoint_connection)

        builder = StateGraph(ClaimState)
        builder.add_node("project_claim", self._project_claim)
        builder.add_edge(START, "project_claim")
        builder.add_edge("project_claim", END)
        self._graph = builder.compile(checkpointer=self._checkpointer)

    def _project_claim(self, state: ClaimState) -> dict[str, str]:
        label = "agent-running"
        self._github.ensure_label(state["repository"], state["issue_number"], label)
        self._store.record_claim(
            run_id=self._store.run_id_for_issue(state["repository"], state["issue_number"]),
            label=label,
            projected_at=self._clock().isoformat(),
        )
        return {"status": "claimed", "claim_label": label}

    def dispatch(self, delivery: Delivery) -> None:
        current = self._github.issue_state(delivery.repository, delivery.issue_number)
        if not self._eligible(current):
            return

        run = self._store.claim_run(delivery, created_at=self._clock().isoformat())
        if run is None or not run["created"]:
            return

        config = {"configurable": {"thread_id": run["id"]}}
        self._graph.invoke(
            {
                "delivery_id": delivery.delivery_id,
                "repository": delivery.repository,
                "issue_number": delivery.issue_number,
                "status": "accepted",
                "claim_label": "",
            },
            config,
        )

    @staticmethod
    def _eligible(state: IssueState) -> bool:
        return state.open and "ready-for-agent" in state.labels and not state.has_open_blockers

    def checkpoint(self, run_id: str) -> dict[str, object] | None:
        snapshot = self._graph.get_state({"configurable": {"thread_id": run_id}})
        if not snapshot.values:
            return None
        checkpoint_id = snapshot.config["configurable"]["checkpoint_id"]
        return {"id": checkpoint_id, "thread_id": run_id, "values": dict(snapshot.values)}

    def workflow_state(self, repository: str, issue_number: int) -> dict[str, object] | None:
        delivery = self._store.workflow_delivery(repository, issue_number)
        if delivery is None:
            return None
        run = self._store.workflow_run(repository, issue_number)
        claim = self._store.workflow_claim(str(run["id"])) if run is not None else None
        checkpoint = self.checkpoint(str(run["id"])) if run is not None else None
        return {"delivery": delivery, "run": run, "claim": claim, "checkpoint": checkpoint}

    def close(self) -> None:
        self._checkpoint_connection.close()
