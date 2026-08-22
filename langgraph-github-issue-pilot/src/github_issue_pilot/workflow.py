from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from github_issue_pilot.github import AUTHORIZED_ORIGINS, IssueState, RepositoryAdapter
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
        repository_adapters: Mapping[str, RepositoryAdapter],
        clock: Callable[[], datetime],
    ) -> None:
        self._store = store
        self._repository_adapters = repository_adapters
        self._clock = clock
        self._checkpoint_connection = sqlite3.connect(database_path, check_same_thread=False)
        self._checkpointer = SqliteSaver(self._checkpoint_connection)

        builder = StateGraph(ClaimState)
        builder.add_node("project_claim", self._project_claim)
        builder.add_edge(START, "project_claim")
        builder.add_edge("project_claim", END)
        self._graph = builder.compile(checkpointer=self._checkpointer)

    def _project_claim(self, state: ClaimState) -> dict[str, str]:
        adapter = self._repository_adapters[state["repository"]]
        label = adapter.running_label
        adapter.ensure_label(state["repository"], state["issue_number"], label)
        self._store.record_claim(
            run_id=self._store.run_id_for_issue(state["repository"], state["issue_number"]),
            label=label,
            projected_at=self._clock().isoformat(),
        )
        return {"status": "claimed", "claim_label": label}

    def dispatch(self, delivery: Delivery) -> None:
        adapter = self._repository_adapters[delivery.repository]
        self._complete_finished_run(delivery, adapter)
        candidates = sorted(adapter.backlog(delivery.issue_number), key=lambda item: item.issue_number)
        for candidate in candidates:
            self._dispatch_candidate(delivery, adapter, candidate.issue_number, candidate.state)

    def _complete_finished_run(
        self,
        delivery: Delivery,
        adapter: RepositoryAdapter,
    ) -> None:
        active = self._store.active_run(delivery.repository)
        if active is None:
            return
        issue_number = int(active["issue_number"])
        state = adapter.issue_state(delivery.repository, issue_number)
        if state.open or not state.implementation_pr_merged:
            return
        self._store.complete_run(str(active["id"]))
        self._record_disposition(
            delivery,
            issue_number=issue_number,
            status="completed",
            reason="implementation-finished",
            state=state,
        )

    def _dispatch_candidate(
        self,
        delivery: Delivery,
        adapter: RepositoryAdapter,
        issue_number: int,
        current: IssueState,
    ) -> None:
        if not current.open:
            return
        interruption = self._authorization_interruption(current, adapter, delivery, issue_number)
        if interruption is not None:
            self._record_disposition(
                delivery,
                issue_number=issue_number,
                status="interrupted",
                reason=interruption,
                state=current,
            )
            return
        blocker_reason = self._blocker_reason(current)
        if blocker_reason is not None:
            self._record_disposition(
                delivery,
                issue_number=issue_number,
                status="queued",
                reason=blocker_reason,
                state=current,
            )
            return

        run = self._store.claim_run(
            delivery,
            issue_number=issue_number,
            created_at=self._clock().isoformat(),
        )
        if run is None:
            self._record_disposition(
                delivery,
                issue_number=issue_number,
                status="queued",
                reason="repository-busy",
                state=current,
            )
            return

        self._record_disposition(
            delivery,
            issue_number=issue_number,
            status="selected",
            reason=None,
            state=current,
        )

        if not run["created"]:
            return

        config = {"configurable": {"thread_id": run["id"]}}
        self._graph.invoke(
            {
                "delivery_id": delivery.delivery_id,
                "repository": delivery.repository,
                "issue_number": issue_number,
                "status": "accepted",
                "claim_label": "",
            },
            config,
        )

    def _record_disposition(
        self,
        delivery: Delivery,
        *,
        issue_number: int,
        status: str,
        reason: str | None,
        state: IssueState,
    ) -> None:
        self._store.record_disposition(
            delivery,
            issue_number=issue_number,
            status=status,
            reason=reason,
            issue_type=state.issue_type,
            evaluated_at=self._clock().isoformat(),
        )

    @staticmethod
    def _authorization_interruption(
        state: IssueState,
        adapter: RepositoryAdapter,
        delivery: Delivery,
        issue_number: int,
    ) -> str | None:
        if adapter.ready_label in state.labels:
            return None
        evidence = state.authorization
        if evidence.origin in AUTHORIZED_ORIGINS and evidence.within_inherited_scope:
            adapter.ensure_label(delivery.repository, issue_number, adapter.ready_label)
            return None
        if evidence.origin in AUTHORIZED_ORIGINS:
            return "product-decision-required"
        return "invalid-provenance"

    @staticmethod
    def _blocker_reason(state: IssueState) -> str | None:
        for blocker in state.blockers:
            if not (blocker.issue_closed and blocker.pull_request_merged):
                return f"blocked-by-incomplete-issue-{blocker.issue_number}"
        return None

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
        disposition = self._store.workflow_disposition(repository, issue_number)
        return {
            "delivery": delivery,
            "disposition": disposition,
            "run": run,
            "claim": claim,
            "checkpoint": checkpoint,
        }

    def close(self) -> None:
        self._checkpoint_connection.close()
