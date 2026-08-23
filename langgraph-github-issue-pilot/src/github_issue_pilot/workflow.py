from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from datetime import datetime
from pathlib import Path
from typing import NotRequired, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from github_issue_pilot.evidence import (
    EvidenceRejected,
    qualify_evidence,
    redact_payload,
    redact_text,
    render_pull_request_body,
)
from github_issue_pilot.github import (
    AUTHORIZED_ORIGINS,
    DraftPullRequestError,
    IssueState,
    RepositoryAdapter,
)
from github_issue_pilot.implementation import (
    ImplementationServices,
    WorkerExecutionError,
    WorkerInvocation,
    Worktree,
    build_assignment,
    validate_worker_result,
)
from github_issue_pilot.policy import (
    NodePolicy,
    NodeSelection,
    SkillProvenance,
    SkillRouter,
)
from github_issue_pilot.publication import SourcePublicationError
from github_issue_pilot.review import ReviewBatchInput, ReviewCoordinator
from github_issue_pilot.storage import Delivery, WorkflowStore


class ClaimState(TypedDict):
    delivery_id: str
    repository: str
    issue_number: int
    status: str
    claim_label: str
    assignment: NotRequired[dict[str, object]]
    worktree: NotRequired[dict[str, str]]
    policy: NotRequired[dict[str, str]]
    skills: NotRequired[list[dict[str, str]]]
    access_profile: NotRequired[dict[str, object]]


class WorkflowRuntime:
    def __init__(
        self,
        *,
        database_path: Path,
        store: WorkflowStore,
        repository_adapters: Mapping[str, RepositoryAdapter],
        clock: Callable[[], datetime],
        implementation: ImplementationServices | None = None,
    ) -> None:
        self._store = store
        self._repository_adapters = repository_adapters
        self._clock = clock
        self._implementation = implementation
        self._checkpoint_connection = sqlite3.connect(database_path, check_same_thread=False)
        self._checkpointer = SqliteSaver(self._checkpoint_connection)

        builder = StateGraph(ClaimState)
        builder.add_node("project_claim", self._project_claim)
        builder.add_edge(START, "project_claim")
        if implementation is None:
            builder.add_edge("project_claim", END)
        else:
            builder.add_node("prepare_implementation", self._prepare_implementation)
            builder.add_node("execute_worker", self._execute_worker)
            builder.add_edge("project_claim", "prepare_implementation")
            builder.add_edge("prepare_implementation", "execute_worker")
            if implementation.source_control is None:
                builder.add_edge("execute_worker", END)
            else:
                builder.add_node("publish_draft_pr", self._publish_draft_pr)
                builder.add_edge("execute_worker", "publish_draft_pr")
                if implementation.reviewer is None:
                    builder.add_edge("publish_draft_pr", END)
                else:
                    builder.add_node("review_draft_pr", self._review_draft_pr)
                    builder.add_edge("publish_draft_pr", "review_draft_pr")
                    builder.add_edge("review_draft_pr", END)
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

    def _prepare_implementation(self, state: ClaimState) -> dict[str, object]:
        services = self._require_implementation()
        repository = state["repository"]
        context = services.repository_contexts[repository]
        run_id = self._store.run_id_for_issue(repository, state["issue_number"])
        current_issue = self._repository_adapters[repository].issue_state(
            repository, state["issue_number"]
        )
        assignment = build_assignment(
            repository=repository,
            issue_number=state["issue_number"],
            issue=current_issue,
            repository_context=context,
        )
        selection = NodePolicy.packaged().select("implementation")
        issue_type = (
            "bug"
            if current_issue.issue_type.casefold() == "bug"
            or any(label.casefold() in {"bug", "type: bug"} for label in current_issue.labels)
            else "feature"
        )
        skills = SkillRouter.packaged(services.skill_root).route(
            "implementation", issue_type=issue_type
        )
        worktree = services.worktrees.create(
            run_id=run_id,
            repository=repository,
            repository_root=services.repository_roots[repository],
            base_ref=context.base_ref,
        )
        skill_records = [
            {"name": skill.name, "content_sha256": skill.content_sha256} for skill in skills
        ]
        access_profile: dict[str, object] = {
            "role": "implementer",
            "sandbox": selection.sandbox,
            "write_root": str(worktree.path),
            "additional_write_roots": [],
        }
        if selection.model is None or selection.reasoning_effort is None:
            raise RuntimeError("implementation policy must select a model and reasoning effort")
        self._store.prepare_implementation(
            run_id=run_id,
            assignment=assignment,
            worktree_path=str(worktree.path),
            branch=worktree.branch,
            base_ref=worktree.base_ref,
            policy_version=selection.policy_version,
            model=selection.model,
            reasoning_effort=selection.reasoning_effort,
            skills=skill_records,
            access_profile=access_profile,
            started_at=self._clock().isoformat(),
        )
        return {
            "assignment": assignment,
            "worktree": {
                "path": str(worktree.path),
                "branch": worktree.branch,
                "base_ref": worktree.base_ref,
            },
            "policy": {
                "version": selection.policy_version,
                "task": selection.task,
                "model": selection.model,
                "reasoning_effort": selection.reasoning_effort,
                "sandbox": selection.sandbox,
            },
            "skills": skill_records,
            "access_profile": access_profile,
        }

    def _execute_worker(self, state: ClaimState) -> dict[str, str]:
        services = self._require_implementation()
        policy = state["policy"]
        run_id = self._store.run_id_for_issue(state["repository"], state["issue_number"])
        diagnostic_events: list[dict[str, object]] = []
        try:
            output = services.worker.run(
                WorkerInvocation(
                    assignment=state["assignment"],
                    worktree=Worktree(
                        path=Path(state["worktree"]["path"]),
                        branch=state["worktree"]["branch"],
                        base_ref=state["worktree"]["base_ref"],
                    ),
                    selection=NodeSelection(
                        policy_version=policy["version"],
                        task=policy["task"],
                        model=policy["model"],
                        reasoning_effort=policy["reasoning_effort"],
                        sandbox=policy["sandbox"],
                    ),
                    skills=tuple(
                        SkillProvenance(
                            name=skill["name"], content_sha256=skill["content_sha256"]
                        )
                        for skill in state["skills"]
                    ),
                    access_profile=state["access_profile"],
                )
            )
            redacted_diagnostics = redact_payload(
                list(output.diagnostic_events),
                services.sensitive_values,
            )
            redacted_result = redact_payload(output.result, services.sensitive_values)
            if not isinstance(redacted_diagnostics, list) or not isinstance(
                redacted_result, dict
            ):
                raise TypeError("redaction changed structured worker output shape")
            diagnostic_events = redacted_diagnostics
            validate_worker_result(redacted_result)
        except (WorkerExecutionError, TypeError) as exc:
            self._store.fail_implementation(
                run_id=run_id,
                error=f"{type(exc).__name__}: worker execution failed",
                diagnostic_events=diagnostic_events,
                completed_at=self._clock().isoformat(),
            )
            return {"status": "worker_failed"}
        self._store.complete_implementation(
            run_id=run_id,
            result=redacted_result,
            diagnostic_events=diagnostic_events,
            completed_at=self._clock().isoformat(),
        )
        return {"status": "implemented"}

    def _publish_draft_pr(self, state: ClaimState) -> dict[str, str]:
        services = self._require_implementation()
        source_control = services.source_control
        if source_control is None:
            raise RuntimeError("source control is not configured")
        run_id = self._store.run_id_for_issue(state["repository"], state["issue_number"])
        implementation = self._store.workflow_implementation(run_id)
        if implementation is None or implementation["result"] is None:
            return {"status": "worker_failed"}
        assignment = implementation["assignment"]
        result = implementation["result"]
        now = self._clock().isoformat()
        try:
            qualified = qualify_evidence(
                assignment["requirements"],
                result,
                sensitive_values=services.sensitive_values,
            )
            render_pull_request_body(
                issue_number=state["issue_number"],
                head_sha="0" * 40,
                evidence=qualified,
            )
        except EvidenceRejected as exc:
            self._store.reject_publication(
                run_id=run_id,
                reason=str(exc),
                rejected_at=now,
            )
            return {"status": "evidence_rejected"}

        worktree = Worktree(
            path=Path(implementation["worktree"]["path"]),
            branch=implementation["worktree"]["branch"],
            base_ref=implementation["worktree"]["base_ref"],
        )
        self._store.begin_publication(
            run_id=run_id,
            evidence=qualified,
            branch=worktree.branch,
            started_at=now,
        )
        try:
            published = source_control.publish(
                worktree,
                issue_number=state["issue_number"],
                sensitive_values=services.sensitive_values,
            )
            body = render_pull_request_body(
                issue_number=state["issue_number"],
                head_sha=published.head_sha,
                evidence=qualified,
            )
            issue = assignment["issue"]
            pull_request = self._repository_adapters[state["repository"]].ensure_draft_pull_request(
                state["repository"],
                issue_number=state["issue_number"],
                branch=published.branch,
                title=redact_text(
                    f"Implement #{state['issue_number']}: {issue['title']}",
                    services.sensitive_values,
                ),
                body=body,
                head_sha=published.head_sha,
            )
            if pull_request.body != body:
                raise RuntimeError("pull request body does not match qualified evidence")
        except (
            DraftPullRequestError,
            EvidenceRejected,
            OSError,
            RuntimeError,
            SourcePublicationError,
            TypeError,
            ValueError,
        ):
            self._store.reject_publication(
                run_id=run_id,
                reason="publication_failed",
                rejected_at=self._clock().isoformat(),
            )
            return {"status": "publication_failed"}
        self._store.complete_publication(
            run_id=run_id,
            branch=published.branch,
            head_sha=published.head_sha,
            body=body,
            pull_request_number=pull_request.number,
            pull_request_url=pull_request.url,
            completed_at=self._clock().isoformat(),
        )
        return {"status": "draft_pr_published"}

    def _review_draft_pr(self, state: ClaimState) -> dict[str, str]:
        services = self._require_implementation()
        reviewer = services.reviewer
        if reviewer is None:
            return {"status": state["status"]}
        run_id = self._store.run_id_for_issue(state["repository"], state["issue_number"])
        implementation = self._store.workflow_implementation(run_id)
        publication = self._store.workflow_publication(run_id)
        if (
            implementation is None
            or implementation["result"] is None
            or publication is None
            or publication["status"] != "published"
            or publication["pull_request"] is None
            or publication["head_sha"] is None
        ):
            return {"status": state["status"]}
        coordinator = ReviewCoordinator(
            store=self._store,
            adapter=self._repository_adapters[state["repository"]],
            reviewer=reviewer,
            skill_root=services.skill_root,
            sensitive_values=services.sensitive_values,
            clock=self._clock,
        )
        status = coordinator.execute(
            ReviewBatchInput(
                run_id=run_id,
                repository=state["repository"],
                issue_number=state["issue_number"],
                implementation=implementation,
                publication=publication,
            )
        )
        return {"status": status}

    def _require_implementation(self) -> ImplementationServices:
        if self._implementation is None:
            raise RuntimeError("implementation services are not configured")
        return self._implementation

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
        implementation = (
            self._store.workflow_implementation(str(run["id"])) if run is not None else None
        )
        draft_pull_request = (
            self._store.workflow_publication(str(run["id"])) if run is not None else None
        )
        review = self._store.workflow_review(str(run["id"])) if run is not None else None
        return {
            "delivery": delivery,
            "disposition": disposition,
            "run": run,
            "claim": claim,
            "checkpoint": checkpoint,
            "implementation": implementation,
            "draft_pull_request": draft_pull_request,
            "review": review,
        }

    def close(self) -> None:
        self._checkpoint_connection.close()
