from __future__ import annotations

import hashlib
import hmac
import json
import multiprocessing
import os
import threading
import time
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from github_issue_pilot.app import create_app
from github_issue_pilot.github import (
    BacklogIssue,
    BlockerState,
    DraftPullRequest,
    IssueState,
    PullRequestState,
)
from github_issue_pilot.implementation import (
    ImplementationServices,
    RepositoryContext,
    WorkerExecutionError,
    WorkerInvocation,
    WorkerOutput,
    Worktree,
)
from github_issue_pilot.intervention import InterventionAnswer, InterventionSession
from github_issue_pilot.publication import PublishedHead
from github_issue_pilot.repair import RepairInvocation, RepairOutput
from github_issue_pilot.review import ReviewInvocation, ReviewOutput
from github_issue_pilot.storage import WorkflowStore
from github_issue_pilot.verification import DeterministicVerification

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
    allowed_event_actions = frozenset(
        {
            ("issues", "labeled"),
            ("pull_request_review", "submitted"),
            ("pull_request_review_comment", "created"),
            ("pull_request", "closed"),
        }
    )

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
        self.implementation_pr_merged = False
        self.pull_request_merged = False
        self.issue_states: dict[int, IssueState] = {}

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        if issue_number in self.issue_states:
            return self.issue_states[issue_number]
        return IssueState(
            open=self.open,
            labels=frozenset(self.labels),
            blockers=(BlockerState(40, False, False),) if self.open_blockers else (),
            title=self.title,
            body=self.body,
            issue_type=self.issue_type,
            findings=self.findings,
            implementation_pr_merged=self.implementation_pr_merged,
        )

    @staticmethod
    def is_configured_human(login: str, user_type: str) -> bool:
        return login.casefold() == "daniel" and user_type.casefold() == "user"

    def backlog(self, trigger_issue_number: int) -> tuple[BacklogIssue, ...]:
        if self.issue_states:
            return tuple(
                BacklogIssue(issue_number, state)
                for issue_number, state in sorted(self.issue_states.items())
                if state.open
            )
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

    def pull_request_state(
        self, repository: str, pull_request_number: int
    ) -> PullRequestState:
        del repository
        return PullRequestState(
            number=pull_request_number,
            head_sha=self.reported_head_override or self.pull_request_head,
            merged=self.pull_request_merged,
            actor_login="daniel",
            actor_type="user",
        )

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


class ControlledInterventionWorker(ControlledWorker):
    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        self.invocations.append(invocation)
        if invocation.intervention_answer is not None:
            evidence = [
                _direct_evidence(criterion)
                for criterion in invocation.assignment["requirements"]
            ]
            return WorkerOutput(
                result={
                    "schema_version": "3",
                    "outcome": "completed",
                    "summary": "Implemented the selected retention behavior.",
                    "red_green_slices": [
                        {
                            "requirement": "Customer can export CSV",
                            "red": {
                                "command": "pytest retention",
                                "observed": "failed: decision missing",
                            },
                            "green": {
                                "command": "pytest retention",
                                "observed": "passed",
                            },
                        }
                    ],
                    "changed_files": ["src/retention.py"],
                    "verification": [{"command": "pytest", "observed": "passed"}],
                    "evidence": evidence,
                    "findings": [],
                    "intervention": None,
                },
                diagnostic_events=(
                    {"type": "turn.completed", "thread_id": "thread-continuation-001"},
                ),
            )
        issue = invocation.assignment["issue"]
        repository = issue["repository"]
        run_id = invocation.worktree.branch.removeprefix("codex/run-")
        return WorkerOutput(
            result={
                "schema_version": "3",
                "outcome": "intervention",
                "summary": "Implementation paused for a retention decision.",
                "red_green_slices": [],
                "changed_files": [],
                "verification": [],
                "evidence": [],
                "findings": ["Retention requirements contradict each other."],
                "intervention": {
                    "schema_version": "1",
                    "repository": {
                        "full_name": repository,
                        "issue_number": issue["number"],
                    },
                    "run": {
                        "id": run_id,
                        "phase": "implementation",
                        "operation_key": f"{run_id}:implementation:worker",
                    },
                    "role": "implementer",
                    "context": {
                        "worktree_path": str(invocation.worktree.path),
                        "branch": invocation.worktree.branch,
                        "pull_request_number": None,
                        "head_sha": None,
                    },
                    "classification": "product_decision",
                    "problem": "The issue requires both immediate deletion and 30-day retention.",
                    "required_action": "Choose the authoritative retention behavior.",
                    "options": [
                        {
                            "label": "retain-30-days",
                            "impact": "Deleted records remain recoverable for thirty days.",
                        },
                        {
                            "label": "delete-immediately",
                            "impact": "Deleted records cannot be recovered.",
                        },
                    ],
                    "recommendation": {
                        "option_label": "retain-30-days",
                        "rationale": "It matches the existing audit requirement.",
                    },
                    "preserved": {
                        "findings": ["Retention requirements contradict each other."],
                        "results": ["No source changes followed the detected conflict."],
                    },
                },
            },
            diagnostic_events=({"type": "turn.completed", "thread_id": "thread-001"},),
        )


class TransientContinuationWorker(ControlledInterventionWorker):
    def __init__(self) -> None:
        super().__init__()
        self.failed_once = False

    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        if invocation.intervention_answer is not None and not self.failed_once:
            self.invocations.append(invocation)
            self.failed_once = True
            raise WorkerExecutionError("transient continuation failure")
        return super().run(invocation)


class ControlledInterventionSessions:
    def __init__(self, answer: InterventionAnswer | None = None) -> None:
        self.answer = answer
        self.deliveries: list[dict[str, object]] = []
        self.reads: list[InterventionSession] = []
        self.archives: list[InterventionSession] = []
        self.delivered = threading.Event()

    def deliver(
        self,
        request: dict[str, object],
        *,
        worktree: Path,
    ) -> InterventionSession:
        self.deliveries.append({"request": request, "worktree": worktree})
        self.delivered.set()
        return InterventionSession(thread_id="intervention-thread-001", delivery_turn_id="turn-001")

    def read_answer(self, session: InterventionSession) -> InterventionAnswer | None:
        self.reads.append(session)
        return self.answer

    def archive(self, session: InterventionSession) -> None:
        self.archives.append(session)


class ControlledRepairWorker(ControlledWorker):
    def __init__(self, terminal_disposition: str | None = None) -> None:
        super().__init__()
        self.repair_invocations: list[RepairInvocation] = []
        self.terminal_disposition = terminal_disposition

    def repair(self, invocation: RepairInvocation) -> RepairOutput:
        self.repair_invocations.append(invocation)
        implementation = super().run(
            WorkerInvocation(
                assignment={
                    "requirements": invocation.assignment["requirements"],
                },
                worktree=invocation.worktree,
                selection=invocation.selection,
                skills=invocation.skills,
                access_profile=invocation.access_profile,
            )
        ).result
        implementation["summary"] = "Repaired review findings"
        return RepairOutput(
            result={
                "schema_version": "1",
                "repair_batch_id": invocation.assignment["repair_batch_id"],
                "round_number": invocation.assignment["round"]["number"],
                "outcome": "completed",
                "summary": "Repaired review findings",
                "implementation_result": implementation,
                "remaining_findings": [],
                "blockage": None,
                "escalation_reason": None,
                "terminal_disposition": self.terminal_disposition,
            },
            diagnostic_events=({"type": "turn.completed", "thread_id": "repair-001"},),
        )


class ControlledInterventionRepairWorker(ControlledRepairWorker):
    def repair(self, invocation: RepairInvocation) -> RepairOutput:
        if invocation.intervention_answer is not None:
            output = super().repair(invocation)
            output.result["schema_version"] = "2"
            output.result["intervention"] = None
            return output
        self.repair_invocations.append(invocation)
        context = invocation.intervention_context
        assert context is not None
        return RepairOutput(
            result={
                "schema_version": "2",
                "repair_batch_id": invocation.assignment["repair_batch_id"],
                "round_number": invocation.assignment["round"]["number"],
                "outcome": "intervention",
                "summary": "Repair paused for deletion semantics.",
                "implementation_result": None,
                "remaining_findings": invocation.assignment["findings"],
                "blockage": None,
                "escalation_reason": None,
                "terminal_disposition": None,
                "intervention": {
                    "schema_version": "1",
                    **context,
                    "classification": "product_decision",
                    "problem": "The finding permits two incompatible deletion semantics.",
                    "required_action": "Choose the semantic behavior for this repair.",
                    "options": [
                        {
                            "label": "retain-30-days",
                            "impact": "The repair preserves recoverability.",
                        }
                    ],
                    "recommendation": {
                        "option_label": "retain-30-days",
                        "rationale": "It preserves the existing audit contract.",
                    },
                    "preserved": {
                        "findings": [
                            str(finding["description"])
                            for finding in invocation.assignment["findings"]
                        ],
                        "results": ["No repair changes followed the product conflict."],
                    },
                },
            },
            diagnostic_events=(
                {"type": "turn.completed", "thread_id": "repair-intervention"},
            ),
        )


class EscalatingRepairWorker(ControlledRepairWorker):
    def repair(self, invocation: RepairInvocation) -> RepairOutput:
        if not self.repair_invocations:
            self.repair_invocations.append(invocation)
            return RepairOutput(
                result={
                    "schema_version": "1",
                    "repair_batch_id": invocation.assignment["repair_batch_id"],
                    "round_number": invocation.assignment["round"]["number"],
                    "outcome": "escalate",
                    "summary": "Security boundary needs material escalation",
                    "implementation_result": None,
                    "remaining_findings": [],
                    "blockage": None,
                    "escalation_reason": "security_boundary",
                    "terminal_disposition": None,
                },
                diagnostic_events=({"type": "turn.completed", "thread_id": "repair-terra"},),
            )
        return super().repair(invocation)


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


class InitiallyFailingReviewer(ControlledReviewer):
    def __init__(self, failed_axes: frozenset[str]) -> None:
        super().__init__()
        self.failed_axes = failed_axes

    def run(self, invocation: ReviewInvocation) -> ReviewOutput:
        initial_batch = len(self.invocations) < 3
        axis = str(invocation.assignment["axis"])
        self.verdicts = {axis: "fail"} if initial_batch and axis in self.failed_axes else {}
        return super().run(invocation)


class ControlledInterventionReviewer(ControlledReviewer):
    def run(self, invocation: ReviewInvocation) -> ReviewOutput:
        axis = str(invocation.assignment["axis"])
        self.invocations.append(invocation)
        if axis != "code" or invocation.intervention_answer is not None:
            return ReviewOutput(
                result={
                    "schema_version": "2",
                    "invocation_id": invocation.assignment["invocation_id"],
                    "axis": axis,
                    "head_sha": invocation.assignment["pull_request"]["head_sha"],
                    "verdict": "pass",
                    "rationale": f"{axis} review passed",
                    "findings": [],
                    "intervention": None,
                },
                diagnostic_events=(
                    {"type": "turn.completed", "thread_id": f"fresh-{axis}"},
                ),
            )
        assignment = invocation.assignment
        pull_request = assignment["pull_request"]
        run_id = invocation.worktree.branch.removeprefix("codex/run-")
        operation_key = str(assignment["invocation_id"])
        return ReviewOutput(
            result={
                "schema_version": "2",
                "invocation_id": operation_key,
                "axis": axis,
                "head_sha": pull_request["head_sha"],
                "verdict": "intervention",
                "rationale": "The required deletion semantics are contradictory.",
                "findings": [
                    {
                        "location": "src/retention.py:20",
                        "description": "Deletion behavior needs a product decision.",
                    }
                ],
                "intervention": {
                    "schema_version": "1",
                    "repository": {"full_name": REPOSITORY, "issue_number": 41},
                    "run": {
                        "id": run_id,
                        "phase": "review",
                        "operation_key": operation_key,
                    },
                    "role": "code_reviewer",
                    "context": {
                        "worktree_path": str(invocation.worktree.path),
                        "branch": invocation.worktree.branch,
                        "pull_request_number": pull_request["number"],
                        "head_sha": pull_request["head_sha"],
                    },
                    "classification": "product_decision",
                    "problem": "Deletion semantics conflict with retention semantics.",
                    "required_action": "Choose which semantic rule is authoritative.",
                    "options": [
                        {
                            "label": "retain-30-days",
                            "impact": "Deletion keeps a recoverable audit record.",
                        }
                    ],
                    "recommendation": {
                        "option_label": "retain-30-days",
                        "rationale": "It preserves the documented audit behavior.",
                    },
                    "preserved": {
                        "findings": ["Deletion behavior needs a product decision."],
                        "results": ["Requirements review already passed this exact head."],
                    },
                },
            },
            diagnostic_events=(
                {"type": "turn.completed", "thread_id": "code-intervention"},
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
                        "artifact": "403 export blocked by authorization policy",
                        "correlation_id": None,
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
                        "correlation_id": None,
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


class SequencedSourceControl(ControlledSourceControl):
    repair_head_sha = "abcdef1234567890abcdef1234567890abcdef12"

    def publish(self, worktree, *, issue_number: int, sensitive_values=()) -> PublishedHead:
        published = super().publish(
            worktree,
            issue_number=issue_number,
            sensitive_values=sensitive_values,
        )
        head_sha = self.head_sha if len(self.calls) == 1 else self.repair_head_sha
        return PublishedHead(branch=published.branch, head_sha=head_sha)


class RoundHeadSourceControl(ControlledSourceControl):
    heads = (
        ControlledSourceControl.head_sha,
        "1111111111111111111111111111111111111111",
        "2222222222222222222222222222222222222222",
        "3333333333333333333333333333333333333333",
    )

    def publish(self, worktree, *, issue_number: int, sensitive_values=()) -> PublishedHead:
        published = super().publish(
            worktree,
            issue_number=issue_number,
            sensitive_values=sensitive_values,
        )
        return PublishedHead(branch=published.branch, head_sha=self.heads[len(self.calls) - 1])


class GeneratedHeadSourceControl(ControlledSourceControl):
    def publish(self, worktree, *, issue_number: int, sensitive_values=()) -> PublishedHead:
        published = super().publish(
            worktree,
            issue_number=issue_number,
            sensitive_values=sensitive_values,
        )
        return PublishedHead(branch=published.branch, head_sha=f"{len(self.calls):040x}")


class ControlledVerifier:
    def __init__(self, passed: bool = True) -> None:
        self.passed = passed
        self.calls: list[dict[str, object]] = []

    def verify(self, worktree, *, command: str, head_sha: str) -> DeterministicVerification:
        self.calls.append({"worktree": worktree, "command": command, "head_sha": head_sha})
        return DeterministicVerification(
            command=command,
            head_sha=head_sha,
            passed=self.passed,
            exit_code=0 if self.passed else 1,
            observed="passed" if self.passed else "failed",
        )


class SequencedVerifier(ControlledVerifier):
    def __init__(self, outcomes: list[bool]) -> None:
        super().__init__()
        self.outcomes = outcomes

    def verify(self, worktree, *, command: str, head_sha: str) -> DeterministicVerification:
        self.passed = self.outcomes[len(self.calls)]
        return super().verify(worktree, command=command, head_sha=head_sha)


class ProcessControlledGitHub(ControlledGitHub):
    def __init__(self, counts, shared_state) -> None:
        super().__init__()
        self._counts = counts
        self._shared_state = shared_state

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        self._counts["claim"] = self._counts.get("claim", 0) + 1
        super().ensure_label(repository, issue_number, label)

    def ensure_draft_pull_request(self, *args, **kwargs) -> DraftPullRequest:
        self._counts["pull_request"] = self._counts.get("pull_request", 0) + 1
        pull_request = super().ensure_draft_pull_request(*args, **kwargs)
        self._shared_state["head"] = pull_request.head_sha
        return pull_request

    def current_pull_request_head(self, repository: str, pull_request_number: int) -> str:
        return str(self._shared_state.get("head", ControlledSourceControl.head_sha))


class ProcessControlledWorktrees(ControlledWorktrees):
    def __init__(self, root, counts) -> None:
        super().__init__(root)
        self._counts = counts

    def create(self, **kwargs) -> Worktree:
        self._counts["worktree"] = self._counts.get("worktree", 0) + 1
        return super().create(**kwargs)


class ProcessControlledWorker(ControlledRepairWorker):
    def __init__(self, counts) -> None:
        super().__init__()
        self._counts = counts

    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        self._counts["worker"] = self._counts.get("worker", 0) + 1
        return super().run(invocation)

    def repair(self, invocation: RepairInvocation) -> RepairOutput:
        self._counts["repair"] = self._counts.get("repair", 0) + 1
        return super().repair(invocation)


class ProcessControlledSourceControl(ControlledSourceControl):
    def __init__(self, counts) -> None:
        super().__init__()
        self._counts = counts

    def publish(self, worktree, *, issue_number: int, sensitive_values=()) -> PublishedHead:
        self._counts["source"] = self._counts.get("source", 0) + 1
        published = super().publish(
            worktree,
            issue_number=issue_number,
            sensitive_values=sensitive_values,
        )
        sequence = int(self._counts["source"])
        return PublishedHead(branch=published.branch, head_sha=f"{sequence:040x}")


class ProcessControlledReviewer(ControlledReviewer):
    def __init__(self, counts, *, fail_initial: bool = False) -> None:
        super().__init__()
        self._counts = counts
        self._fail_initial = fail_initial

    def run(self, invocation: ReviewInvocation) -> ReviewOutput:
        axis = str(invocation.assignment["axis"])
        key = f"review_{axis}"
        self._counts[key] = self._counts.get(key, 0) + 1
        self.verdicts = (
            {"code": "fail"}
            if self._fail_initial and axis == "code" and int(self._counts[key]) == 1
            else {}
        )
        return super().run(invocation)


class ProcessControlledVerifier(ControlledVerifier):
    def __init__(self, counts) -> None:
        super().__init__()
        self._counts = counts

    def verify(self, worktree, *, command: str, head_sha: str) -> DeterministicVerification:
        self._counts["verification"] = self._counts.get("verification", 0) + 1
        return super().verify(worktree, command=command, head_sha=head_sha)


def run_recovery_process(
    database_path: str,
    worktree_root: str,
    counts,
    shared_state,
    crash_phase: str | None,
    result_path: str | None,
    with_reviewer: bool = False,
    with_repair: bool = False,
    with_verifier: bool = False,
) -> None:
    github = ProcessControlledGitHub(counts, shared_state)

    def transition_probe(phase: str, _operation_key: str) -> None:
        if phase == crash_phase:
            os._exit(86)

    services = controlled_implementation_services(
        Path(worktree_root).parent,
        ProcessControlledWorktrees(Path(worktree_root), counts),
        ProcessControlledWorker(counts),
        source_control=ProcessControlledSourceControl(counts),
        reviewer=(
            ProcessControlledReviewer(counts, fail_initial=with_repair)
            if with_reviewer or with_repair
            else None
        ),
        verifier=(
            ProcessControlledVerifier(counts) if with_repair or with_verifier else None
        ),
    )
    services = replace(services, transition_probe=transition_probe)
    app = create_app(
        database_path=Path(database_path),
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(app) as client:
        if crash_phase is not None:
            if crash_phase == "waiting_process":
                client.get("/workflows/daniel/probare-crm/issues/41")
                os._exit(86)
            elif crash_phase == "feedback_attempt_completed":
                body = feedback_body(head_sha=str(shared_state["head"]))
                client.post(
                    "/webhooks/github",
                    content=body,
                    headers=signed_headers(
                        body,
                        delivery_id="feedback-delivery-001",
                        event="pull_request_review",
                    ),
                )
            else:
                body = delivery_body()
                client.post("/webhooks/github", content=body, headers=signed_headers(body))
        else:
            observed = client.get("/workflows/daniel/probare-crm/issues/41")
            if result_path is not None:
                Path(result_path).write_text(
                    json.dumps(observed.json(), sort_keys=True), encoding="utf-8"
                )


def controlled_implementation_services(
    tmp_path,
    worktrees: ControlledWorktrees,
    worker: ControlledWorker,
    *,
    repository_root=None,
    source_control=None,
    reviewer=None,
    verifier=None,
    sensitive_values=(),
    intervention_sessions=None,
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
        verifier=verifier,
        sensitive_values=tuple(sensitive_values),
        interventions=intervention_sessions,
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


def feedback_body(
    *,
    pull_request_number: int = 77,
    feedback: str = "Keep the CSV column order stable.",
    login: str = "daniel",
    user_type: str = "User",
    review_state: str = "changes_requested",
    head_sha: str = ControlledSourceControl.head_sha,
) -> bytes:
    return json.dumps(
        {
            "action": "submitted",
            "repository": {"full_name": REPOSITORY},
            "pull_request": {
                "number": pull_request_number,
                "head": {"sha": head_sha},
            },
            "review": {
                "id": 901,
                "state": review_state,
                "body": feedback,
                "user": {"login": login, "type": user_type},
            },
        },
        separators=(",", ":"),
    ).encode()


def merge_body(
    *,
    pull_request_number: int = 77,
    head_sha: str = ControlledSourceControl.head_sha,
    merged: bool = True,
    login: str = "daniel",
    user_type: str = "User",
) -> bytes:
    return json.dumps(
        {
            "action": "closed",
            "repository": {"full_name": REPOSITORY},
            "pull_request": {
                "number": pull_request_number,
                "head": {"sha": head_sha},
                "merged": merged,
                "merged_by": {"login": login, "type": user_type},
            },
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


def test_implementation_intervention_is_persisted_before_delivery_and_survives_restart(
    tmp_path,
) -> None:
    database_path = tmp_path / "pilot.db"
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    first_worker = ControlledInterventionWorker()
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: ControlledGitHub()},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            first_worker,
        ),
    )
    body = delivery_body()

    with TestClient(first_app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()

    second_worker = ControlledInterventionWorker()
    second_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: ControlledGitHub()},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            second_worker,
        ),
    )
    with TestClient(second_app) as client:
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert accepted.status_code == 202
    request = before["intervention"]["requests"][0]
    assert request["status"] == "pending_delivery"
    assert request["request"]["classification"] == "product_decision"
    assert request["request"]["required_action"] == (
        "Choose the authoritative retention behavior."
    )
    assert request["request"]["preserved"]["findings"] == [
        "Retention requirements contradict each other."
    ]
    assert before["run"]["status"] == "running"
    assert after["run"]["id"] == before["run"]["id"]
    assert after["implementation"]["worktree"] == before["implementation"]["worktree"]
    assert after["intervention"] == before["intervention"]
    assert len(first_worker.invocations) == 1
    assert second_worker.invocations == []


def test_heartbeat_delivers_one_intervention_session_and_restart_only_reads_it(
    tmp_path,
) -> None:
    database_path = tmp_path / "pilot.db"
    sessions = ControlledInterventionSessions()
    services = controlled_implementation_services(
        tmp_path,
        ControlledWorktrees(tmp_path / "worktrees"),
        ControlledInterventionWorker(),
        intervention_sessions=sessions,
    )
    app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: ControlledGitHub()},
        clock=fixed_clock,
        implementation=services,
        heartbeat_interval_seconds=0.01,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        assert sessions.delivered.wait(timeout=2)
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(100):
            if state["intervention"]["requests"][0]["status"] == "open":
                break
            time.sleep(0.01)
            state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert len(sessions.deliveries) == 1
    assert state["intervention"]["requests"][0]["session"] == {
        "thread_id": "intervention-thread-001",
        "delivery_turn_id": "turn-001",
    }

    restarted = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: ControlledGitHub()},
        clock=fixed_clock,
        implementation=services,
        heartbeat_interval_seconds=0.01,
    )
    with TestClient(restarted) as client:
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert len(sessions.deliveries) == 1
    assert sessions.reads
    assert after["intervention"] == state["intervention"]


def test_signed_implementation_intervention_answer_resumes_same_checkpoint(
    tmp_path,
) -> None:
    database_path = tmp_path / "pilot.db"
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledInterventionWorker()
    sessions = ControlledInterventionSessions(
        InterventionAnswer(turn_id="answer-turn-001", text="Retain records for 30 days.")
    )
    app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: ControlledGitHub()},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            worker,
            intervention_sessions=sessions,
        ),
        heartbeat_interval_seconds=0.01,
    )
    body = delivery_body()

    with TestClient(app) as client:
        accepted = client.post(
            "/webhooks/github", content=body, headers=signed_headers(body)
        )
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(200):
            requests = state["intervention"]["requests"]
            if requests and requests[0]["status"] == "applied":
                break
            time.sleep(0.01)
            state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert accepted.status_code == 202
    assert len(worktrees.calls) == 1
    assert len(worker.invocations) == 2
    first, continuation = worker.invocations
    assert continuation.worktree == first.worktree
    assert continuation.intervention_answer == {
        "intervention_id": state["intervention"]["requests"][0]["id"],
        "answer_turn_id": "answer-turn-001",
        "answer_text": "Retain records for 30 days.",
    }
    assert state["implementation"]["result"]["outcome"] == "completed"
    assert state["checkpoint"]["thread_id"] == state["run"]["id"]
    assert state["checkpoint"]["values"]["status"] == "implemented"
    assert state["intervention"]["requests"][0]["status"] == "applied"


def test_review_axis_intervention_preserves_peer_result_and_exact_head(tmp_path) -> None:
    github = ControlledGitHub()
    reviewer = ControlledInterventionReviewer()
    source_control = ControlledSourceControl()
    sessions = ControlledInterventionSessions(
        InterventionAnswer(turn_id="review-answer-001", text="Retain records for 30 days.")
    )
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            ControlledWorker(),
            source_control=source_control,
            reviewer=reviewer,
            intervention_sessions=sessions,
        ),
        heartbeat_interval_seconds=0.01,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(200):
            if (
                state["intervention"]["requests"]
                and state["intervention"]["requests"][0]["status"] == "applied"
                and state["review"]["status"] == "verified"
            ):
                break
            time.sleep(0.01)
            state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    axes = [str(call.assignment["axis"]) for call in reviewer.invocations]
    assert axes == ["requirements", "code", "code", "architecture"]
    code_calls = [call for call in reviewer.invocations if call.assignment["axis"] == "code"]
    assert code_calls[0].intervention_answer is None
    assert code_calls[1].intervention_answer == {
        "intervention_id": state["intervention"]["requests"][0]["id"],
        "answer_turn_id": "review-answer-001",
        "answer_text": "Retain records for 30 days.",
    }
    assert {
        call.assignment["pull_request"]["head_sha"] for call in reviewer.invocations
    } == {ControlledSourceControl.head_sha}
    assert len(source_control.calls) == 1
    assert len(worktrees.calls) == 1
    assert state["review"]["status"] == "verified"
    assert state["intervention"]["requests"][0]["status"] == "applied"


def test_repair_intervention_resumes_inside_same_numbered_attempt_and_requalifies_head(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    reviewer = InitiallyFailingReviewer(frozenset({"code"}))
    worker = ControlledInterventionRepairWorker()
    source_control = SequencedSourceControl()
    verifier = ControlledVerifier()
    sessions = ControlledInterventionSessions(
        InterventionAnswer(turn_id="repair-answer-001", text="Retain records for 30 days.")
    )
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            worker,
            source_control=source_control,
            reviewer=reviewer,
            verifier=verifier,
            intervention_sessions=sessions,
        ),
        heartbeat_interval_seconds=0.01,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(300):
            if (
                state["intervention"]["requests"]
                and state["intervention"]["requests"][0]["status"] == "applied"
                and state["repair"]["status"] == "verified"
            ):
                break
            time.sleep(0.01)
            state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    repair = state["repair"]
    assert len(worktrees.calls) == 1
    assert len(worker.repair_invocations) == 2
    first, continuation = worker.repair_invocations
    assert first.assignment["repair_batch_id"] == continuation.assignment["repair_batch_id"]
    assert first.assignment["round"] == continuation.assignment["round"] == {
        "number": 1,
        "limit": 3,
    }
    assert continuation.worktree == first.worktree
    assert continuation.intervention_answer == {
        "intervention_id": state["intervention"]["requests"][0]["id"],
        "answer_turn_id": "repair-answer-001",
        "answer_text": "Retain records for 30 days.",
    }
    assert repair["round_count"] == 1
    assert repair["attempts"][0]["round"] == 1
    assert len(repair["attempts"][0]["invocations"]) == 1
    assert repair["status"] == "verified"
    assert [call["head_sha"] for call in verifier.calls] == [
        SequencedSourceControl.repair_head_sha
    ]
    assert len(reviewer.invocations) == 6
    assert {
        call.assignment["pull_request"]["head_sha"]
        for call in reviewer.invocations[3:]
    } == {SequencedSourceControl.repair_head_sha}
    assert len(source_control.calls) == 2


def test_restart_reuses_applying_answer_run_worktree_branch_and_publication(tmp_path) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = ControlledSourceControl()
    sessions = ControlledInterventionSessions()
    first_worker = ControlledInterventionWorker()
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            first_worker,
            source_control=source_control,
            intervention_sessions=sessions,
        ),
        heartbeat_interval_seconds=0.01,
    )
    body = delivery_body()

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(200):
            if before["intervention"]["requests"][0]["status"] == "open":
                break
            time.sleep(0.01)
            before = client.get("/workflows/daniel/probare-crm/issues/41").json()

    request = before["intervention"]["requests"][0]
    store = WorkflowStore(database_path)
    assert store.capture_intervention_answer(
        intervention_id=request["id"],
        answer_turn_id="restart-answer-001",
        answer_text="Retain records for 30 days.",
        answered_at=fixed_clock().isoformat(),
    )
    assert store.claim_intervention_application(request["id"])

    continuation_worker = ControlledInterventionWorker()
    restarted = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            continuation_worker,
            source_control=source_control,
            intervention_sessions=sessions,
        ),
        heartbeat_interval_seconds=0.01,
    )
    with TestClient(restarted) as client:
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert after["run"]["id"] == before["run"]["id"]
    assert after["implementation"]["worktree"] == before["implementation"]["worktree"]
    assert after["implementation"]["worktree"]["branch"] == before["implementation"][
        "worktree"
    ]["branch"]
    assert after["intervention"]["requests"][0]["status"] == "applied"
    assert len(worktrees.calls) == 1
    assert len(first_worker.invocations) == 1
    assert len(continuation_worker.invocations) == 1
    assert len(source_control.calls) == 1
    assert len(github.pull_request_writes) == 1


def test_transient_continuation_failure_retries_same_applying_operation(tmp_path) -> None:
    worker = TransientContinuationWorker()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = ControlledSourceControl()
    sessions = ControlledInterventionSessions(
        InterventionAnswer(turn_id="retry-answer-001", text="Retain records for 30 days.")
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: ControlledGitHub()},
        clock=fixed_clock,
        implementation=controlled_implementation_services(
            tmp_path,
            worktrees,
            worker,
            source_control=source_control,
            intervention_sessions=sessions,
        ),
        heartbeat_interval_seconds=0.01,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(300):
            if (
                state["intervention"]["requests"]
                and state["intervention"]["requests"][0]["status"] == "applied"
                and state["draft_pull_request"] is not None
            ):
                break
            time.sleep(0.01)
            state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert len(worker.invocations) == 3
    assert worker.invocations[1].intervention_answer == worker.invocations[
        2
    ].intervention_answer
    assert len(worktrees.calls) == 1
    assert len(source_control.calls) == 1
    assert state["intervention"]["requests"][0]["status"] == "applied"


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


def test_startup_recovery_continues_claimed_run_once_through_http_read_back(tmp_path) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    body = delivery_body()
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        claimed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    source_control = ControlledSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
    )
    recovered_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(recovered_app) as client:
        recovered = client.get("/workflows/daniel/probare-crm/issues/41").json()

    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(restarted_app) as client:
        repeated = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert recovered["run"]["id"] == claimed["run"]["id"]
    assert recovered["checkpoint"]["thread_id"] == claimed["checkpoint"]["thread_id"]
    assert recovered["implementation"]["status"] == "completed"
    assert recovered["draft_pull_request"]["status"] == "published"
    assert recovered["recovery"]["status"] == "completed"
    assert {event["phase"] for event in recovered["recovery"]["events"]} >= {
        "implementation",
        "publication",
    }
    assert repeated["recovery"] == recovered["recovery"]
    assert len(worktrees.calls) == 1
    assert len(worker.invocations) == 1
    assert len(source_control.calls) == 1
    assert len(github.pull_request_writes) == 1


@pytest.mark.parametrize(
    ("crash_phase", "expected_outcomes"),
    [
        (
            "claim",
            {
                "claim": ["reused"],
                "implementation": ["retried", "retried"],
                "publication": ["retried"],
                "waiting": ["waiting"],
            },
        ),
        (
            "implementation_completed",
            {
                "claim": ["reused"],
                "implementation": ["reused"],
                "publication": ["retried"],
                "waiting": ["waiting"],
            },
        ),
        (
            "publication_completed",
            {
                "claim": ["reused"],
                "implementation": ["reused"],
                "publication": ["reused"],
                "waiting": ["waiting"],
            },
        ),
    ],
    ids=["claim", "implementation", "publication"],
)
def test_real_process_exit_recovers_completed_effects_without_duplicates(
    tmp_path, crash_phase: str, expected_outcomes: dict[str, list[str]]
) -> None:
    context = multiprocessing.get_context("spawn")
    with context.Manager() as manager:
        counts = manager.dict()
        shared_state = manager.dict()
        database_path = str(tmp_path / "pilot.db")
        worktree_root = str(tmp_path / "worktrees")
        recovered_path = str(tmp_path / "recovered.json")
        repeated_path = str(tmp_path / "repeated.json")

        crashed = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                crash_phase,
                None,
            ),
        )
        crashed.start()
        crashed.join(20)
        assert crashed.exitcode == 86

        recovered = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                None,
                recovered_path,
            ),
        )
        recovered.start()
        recovered.join(20)
        assert recovered.exitcode == 0

        repeated = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                None,
                repeated_path,
            ),
        )
        repeated.start()
        repeated.join(20)
        assert repeated.exitcode == 0

        first_state = json.loads(Path(recovered_path).read_text(encoding="utf-8"))
        second_state = json.loads(Path(repeated_path).read_text(encoding="utf-8"))
        assert first_state["implementation"]["status"] == "completed"
        assert first_state["draft_pull_request"]["status"] == "published"
        assert first_state["recovery"] == second_state["recovery"]
        observed_outcomes: dict[str, list[str]] = {}
        for event in first_state["recovery"]["events"]:
            observed_outcomes.setdefault(event["phase"], []).append(event["outcome"])
        assert observed_outcomes == expected_outcomes
        assert dict(counts) == {
            "claim": 1,
            "worktree": 1,
            "worker": 1,
            "source": 1,
            "pull_request": 1,
        }


def test_real_process_exit_resumes_only_missing_review_axes(tmp_path) -> None:
    context = multiprocessing.get_context("spawn")
    with context.Manager() as manager:
        counts = manager.dict()
        shared_state = manager.dict()
        database_path = str(tmp_path / "pilot.db")
        worktree_root = str(tmp_path / "worktrees")
        recovered_path = str(tmp_path / "recovered.json")

        crashed = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                "review_requirements_completed",
                None,
                True,
            ),
        )
        crashed.start()
        crashed.join(20)
        assert crashed.exitcode == 86

        recovered = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                None,
                recovered_path,
                True,
            ),
        )
        recovered.start()
        recovered.join(20)
        assert recovered.exitcode == 0

        state = json.loads(Path(recovered_path).read_text(encoding="utf-8"))
        assert state["review"]["status"] == "verified"
        assert [result["axis"] for result in state["review"]["results"]] == [
            "requirements",
            "code",
            "architecture",
        ]
        assert dict(counts) == {
            "claim": 1,
            "worktree": 1,
            "worker": 1,
            "source": 1,
            "pull_request": 1,
            "review_requirements": 1,
            "review_code": 1,
            "review_architecture": 1,
        }


def test_real_process_exit_reuses_persisted_repair_invocation(tmp_path) -> None:
    context = multiprocessing.get_context("spawn")
    with context.Manager() as manager:
        counts = manager.dict()
        shared_state = manager.dict()
        database_path = str(tmp_path / "pilot.db")
        worktree_root = str(tmp_path / "worktrees")
        recovered_path = str(tmp_path / "recovered.json")

        crashed = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                "repair_invocation_completed",
                None,
                False,
                True,
            ),
        )
        crashed.start()
        crashed.join(20)
        assert crashed.exitcode == 86

        recovered = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                None,
                recovered_path,
                False,
                True,
            ),
        )
        recovered.start()
        recovered.join(20)
        assert recovered.exitcode == 0

        state = json.loads(Path(recovered_path).read_text(encoding="utf-8"))
        assert state["repair"]["status"] == "verified"
        assert state["repair"]["round_count"] == 1
        assert len(state["repair"]["attempts"][0]["invocations"]) == 1
        assert state["draft_pull_request"]["head_sha"] == f"{2:040x}"
        assert dict(counts) == {
            "claim": 1,
            "worktree": 1,
            "worker": 1,
            "source": 2,
            "pull_request": 3,
            "review_requirements": 2,
            "review_code": 2,
            "review_architecture": 2,
            "repair": 1,
            "verification": 1,
        }


def test_real_process_exit_preserves_completed_feedback_attempt_and_batch_counter(
    tmp_path,
) -> None:
    context = multiprocessing.get_context("spawn")
    with context.Manager() as manager:
        counts = manager.dict()
        shared_state = manager.dict()
        database_path = str(tmp_path / "pilot.db")
        worktree_root = str(tmp_path / "worktrees")
        recovered_path = str(tmp_path / "recovered.json")

        seeded = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                "seed",
                None,
                True,
                False,
                True,
            ),
        )
        seeded.start()
        seeded.join(20)
        assert seeded.exitcode == 0

        waiting_crash = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                "waiting_process",
                None,
                True,
                False,
                True,
            ),
        )
        waiting_crash.start()
        waiting_crash.join(20)
        assert waiting_crash.exitcode == 86

        crashed = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                "feedback_attempt_completed",
                None,
                True,
                False,
                True,
            ),
        )
        crashed.start()
        crashed.join(20)
        assert crashed.exitcode == 86

        recovered = context.Process(
            target=run_recovery_process,
            args=(
                database_path,
                worktree_root,
                counts,
                shared_state,
                None,
                recovered_path,
                True,
                False,
                True,
            ),
        )
        recovered.start()
        recovered.join(20)
        assert recovered.exitcode == 0

        state = json.loads(Path(recovered_path).read_text(encoding="utf-8"))
        batch = state["human_feedback"]["batches"][0]
        assert batch["status"] == "verified"
        assert batch["round_count"] == 1
        assert batch["attempts"][0]["status"] == "verified"
        assert any(
            event["phase"] == "human_feedback"
            and event["operation_key"].endswith(batch["id"])
            for event in state["recovery"]["events"]
        )
        assert dict(counts) == {
            "claim": 1,
            "worktree": 1,
            "worker": 1,
            "source": 2,
            "pull_request": 2,
            "review_requirements": 2,
            "review_code": 2,
            "review_architecture": 2,
            "repair": 1,
            "verification": 1,
        }


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


def test_generic_github_issue_type_is_normalized_to_feature_before_assignment(tmp_path) -> None:
    github = ControlledGitHub()
    github.issue_type = "issue"
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=controlled_implementation_services(tmp_path, worktrees, worker),
    )
    body = delivery_body()

    with TestClient(app) as client:
        accepted = client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert accepted.status_code == 202
    assert state["implementation"]["assignment"]["issue"]["type"] == "feature"
    assert len(worker.invocations) == 1


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
    assert {key: value for key, value in after_restart.items() if key != "recovery"} == {
        key: value for key, value in before_restart.items() if key != "recovery"
    }
    assert after_restart["recovery"]["status"] == "completed"
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


def test_multi_axis_review_failure_is_repaired_once_and_new_head_verifies_through_http_seam(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = SequencedSourceControl()
    worker = ControlledRepairWorker()
    reviewer = InitiallyFailingReviewer(frozenset({"requirements", "code"}))
    verifier = ControlledVerifier()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
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

    assert accepted.status_code == 202
    assert state["review"]["status"] == "verified"
    assert state["review"]["head_sha"] == source_control.repair_head_sha
    repair = state["repair"]
    assert repair["status"] == "verified"
    assert repair["round_count"] == 1
    assert repair["open_findings"] == []
    attempt = repair["attempts"][0]
    assert attempt["round"] == 1
    assert attempt["status"] == "verified"
    assert attempt["head_sha"] == source_control.repair_head_sha
    assert attempt["deterministic_verification"] == {
        "command": "pytest tests/test_export.py",
        "head_sha": source_control.repair_head_sha,
        "passed": True,
        "exit_code": 0,
        "observed": "passed",
    }
    assert {
        finding["axis"] for finding in attempt["assignment"]["findings"]
    } == {"requirements", "code"}
    assert attempt["invocations"][0]["policy"]["model"] == "gpt-5.6-terra"
    assert attempt["invocations"][0]["access_profile"]["write_root"] == str(
        worktrees.root / state["run"]["id"]
    )
    assert len(worker.repair_invocations) == 1
    assert worker.repair_invocations[0].worktree.path == worktrees.root / state["run"]["id"]
    assert len(reviewer.invocations) == 6
    assert {
        invocation.assignment["pull_request"]["head_sha"]
        for invocation in reviewer.invocations[:3]
    } == {source_control.head_sha}
    assert {
        invocation.assignment["pull_request"]["head_sha"]
        for invocation in reviewer.invocations[3:]
    } == {source_control.repair_head_sha}
    assert verifier.calls == [
        {
            "worktree": worker.repair_invocations[0].worktree,
            "command": "pytest tests/test_export.py",
            "head_sha": source_control.repair_head_sha,
        }
    ]
    assert len(source_control.calls) == 2
    assert len(github.pull_request_writes) >= 2
    assert github.pull_request_writes[-1]["head_sha"] == source_control.repair_head_sha
    assert "Repair Attempts" in github.pull_request_writes[-1]["body"]
    assert github.labels == {"ready-for-agent", "verified", "awaiting-review"}


def test_review_failures_stop_after_exactly_three_repair_rounds_without_a_fourth_invocation(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    source_control = RoundHeadSourceControl()
    worker = ControlledRepairWorker()
    reviewer = ControlledReviewer({"code": "fail"})
    verifier = ControlledVerifier()
    sessions = ControlledInterventionSessions(
        InterventionAnswer(
            turn_id="exhaustion-answer-001",
            text="Acknowledge the bounded handoff; do not start another round.",
        )
    )
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
        intervention_sessions=sessions,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
        heartbeat_interval_seconds=0.01,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(300):
            requests = state["intervention"]["requests"]
            if (
                requests
                and requests[0]["status"] == "applied"
                and state["repair"]["status"] == "ready-for-human"
            ):
                break
            time.sleep(0.01)
            state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    repair = state["repair"]
    assert repair["status"] == "ready-for-human"
    assert repair["round_limit"] == 3
    assert repair["round_count"] == 3
    assert [attempt["round"] for attempt in repair["attempts"]] == [1, 2, 3]
    assert [attempt["status"] for attempt in repair["attempts"]] == [
        "unsuccessful",
        "unsuccessful",
        "unsuccessful",
    ]
    assert [
        attempt["invocations"][0]["policy"]["model"] for attempt in repair["attempts"]
    ] == ["gpt-5.6-terra", "gpt-5.6-terra", "gpt-5.6-sol"]
    assert repair["attempts"][2]["invocations"][0]["policy"][
        "escalation_reason"
    ] == "final_repair_round"
    assert len(worker.repair_invocations) == 3
    assert len(source_control.calls) == 4
    assert len(verifier.calls) == 3
    assert len(reviewer.invocations) == 12
    assert state["intervention"]["requests"][0]["request"]["classification"] == (
        "repair_rounds_exhausted"
    )
    assert state["intervention"]["requests"][0]["status"] == "applied"
    assert {finding["axis"] for finding in repair["open_findings"]} == {"code"}
    assert state["draft_pull_request"]["head_sha"] == source_control.heads[-1]
    assert "Open Findings" in state["draft_pull_request"]["body"]
    assert github.labels == {"ready-for-agent", "ready-for-human"}


def test_failed_deterministic_check_still_runs_all_reviews_and_enters_next_round(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    source_control = RoundHeadSourceControl()
    worker = ControlledRepairWorker()
    reviewer = InitiallyFailingReviewer(frozenset({"code"}))
    verifier = SequencedVerifier([False, True])
    services = controlled_implementation_services(
        tmp_path,
        ControlledWorktrees(tmp_path / "worktrees"),
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
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

    attempts = state["repair"]["attempts"]
    assert state["repair"]["status"] == "verified"
    assert [attempt["status"] for attempt in attempts] == ["unsuccessful", "verified"]
    assert attempts[0]["deterministic_verification"]["passed"] is False
    assert attempts[0]["remaining_findings"] == [
        {
            "source": "deterministic_verification",
            "axis": "deterministic_verification",
            "location": "pytest tests/test_export.py",
            "description": "failed",
        }
    ]
    assert attempts[1]["assignment"]["findings"] == attempts[0]["remaining_findings"]
    assert len(reviewer.invocations) == 9
    assert {
        invocation.assignment["pull_request"]["head_sha"]
        for invocation in reviewer.invocations[3:6]
    } == {source_control.heads[1]}
    assert {
        invocation.assignment["pull_request"]["head_sha"]
        for invocation in reviewer.invocations[6:9]
    } == {source_control.heads[2]}
    assert len(worker.repair_invocations) == 2


def test_structured_escalation_uses_sol_inside_same_numbered_round(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    source_control = SequencedSourceControl()
    worker = EscalatingRepairWorker()
    reviewer = InitiallyFailingReviewer(frozenset({"code"}))
    services = controlled_implementation_services(
        tmp_path,
        ControlledWorktrees(tmp_path / "worktrees"),
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=ControlledVerifier(),
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

    repair = state["repair"]
    assert repair["status"] == "verified"
    assert repair["round_count"] == 1
    invocations = repair["attempts"][0]["invocations"]
    assert [item["result"]["outcome"] for item in invocations] == [
        "escalate",
        "completed",
    ]
    assert [item["policy"]["model"] for item in invocations] == [
        "gpt-5.6-terra",
        "gpt-5.6-sol",
    ]
    assert invocations[1]["policy"]["escalation_reason"] == "security_boundary"
    assert len(worker.repair_invocations) == 2


@pytest.mark.parametrize(
    ("terminal_disposition", "expected_status"),
    [
        ("needs-info", "needs-info"),
        (None, "ready-for-human"),
    ],
    ids=["missing-requirements", "unresolvable-conflict"],
)
def test_exhausted_human_handoff_survives_restart_without_duplicate_effects(
    tmp_path,
    terminal_disposition: str | None,
    expected_status: str,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    source_control = RoundHeadSourceControl()
    worker = ControlledRepairWorker(terminal_disposition=terminal_disposition)
    reviewer = ControlledReviewer({"code": "fail"})
    verifier = ControlledVerifier()
    sessions = ControlledInterventionSessions(
        InterventionAnswer(
            turn_id=f"exhaustion-{expected_status}",
            text="Acknowledge the bounded handoff without another automatic round.",
        )
    )
    services = controlled_implementation_services(
        tmp_path,
        ControlledWorktrees(tmp_path / "worktrees"),
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
        intervention_sessions=sessions,
    )
    body = delivery_body()
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
        heartbeat_interval_seconds=0.01,
    )

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
        before_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(300):
            if (
                before_restart["intervention"]["requests"]
                and before_restart["intervention"]["requests"][0]["status"] == "applied"
                and before_restart["repair"]["status"] == expected_status
            ):
                break
            time.sleep(0.01)
            before_restart = client.get(
                "/workflows/daniel/probare-crm/issues/41"
            ).json()

    effect_counts = (
        len(worker.repair_invocations),
        len(reviewer.invocations),
        len(source_control.calls),
        len(verifier.calls),
        len(github.pull_request_writes),
        len(github.workflow_label_projections),
    )
    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(restarted_app) as client:
        after_restart = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert after_restart["repair"] == before_restart["repair"]
    assert after_restart["draft_pull_request"] == before_restart["draft_pull_request"]
    assert after_restart["repair"]["status"] == expected_status
    assert after_restart["repair"]["round_count"] == 3
    assert after_restart["repair"]["open_findings"]
    assert set(after_restart["repair"]["projected_labels"]) == {
        expected_status,
        "ready-for-agent",
    }
    assert github.labels == {"ready-for-agent", expected_status}
    assert (
        len(worker.repair_invocations),
        len(reviewer.invocations),
        len(source_control.calls),
        len(verifier.calls),
        len(github.pull_request_writes),
        len(github.workflow_label_projections),
    ) == effect_counts


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
    database_path = tmp_path / "pilot.db"
    app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    body = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=body, headers=signed_headers(body))
    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(restarted_app) as client:
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    serialized = json.dumps(state, sort_keys=True)
    assert "super-private-value" not in serialized
    assert "ghp_12345678901234567890" not in serialized
    assert "daniel@example.com" not in serialized
    assert serialized.count("[REDACTED]") >= 4
    assert state["recovery"]["status"] == "completed"
    assert all(
        set(event) == {"id", "phase", "operation_key", "outcome", "recorded_at"}
        for event in state["recovery"]["events"]
    )
    assert set(state["checkpoint"]["values"]) == {
        "delivery_id",
        "repository",
        "issue_number",
        "status",
        "claim_label",
    }
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


def test_configured_human_feedback_is_correlated_and_persisted_on_the_existing_run(
    tmp_path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    source_control = SequencedSourceControl()
    reviewer = ControlledReviewer()
    verifier = ControlledVerifier()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
    )
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()

    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
    )
    feedback = feedback_body()
    with TestClient(restarted_app) as client:
        response = client.post(
            "/webhooks/github",
            content=feedback,
            headers=signed_headers(
                feedback,
                delivery_id="feedback-001",
                event="pull_request_review",
            ),
        )
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert response.status_code == 202
    assert response.json() == {"delivery_id": "feedback-001", "status": "accepted"}
    assert after["run"]["id"] == before["run"]["id"]
    assert after["implementation"]["worktree"] == before["implementation"]["worktree"]
    assert len(worktrees.calls) == 1
    batch = after["human_feedback"]["batches"][0]
    assert batch == {
        "id": batch["id"],
        "delivery_id": "feedback-001",
        "pull_request_number": 77,
        "starting_head_sha": ControlledSourceControl.head_sha,
        "author": "daniel",
        "feedback": ["Keep the CSV column order stable."],
        "superseded": {
            "head_sha": ControlledSourceControl.head_sha,
            "evidence": before["draft_pull_request"]["evidence"],
            "review_batch_id": before["review"]["id"],
        },
        "round_limit": 3,
        "round_count": 0,
        "status": "pending",
        "projected_labels": [],
        "attempts": [],
        "created_at": "2026-08-21T10:30:00+00:00",
        "completed_at": None,
    }


@pytest.mark.parametrize(
    ("feedback_overrides", "expected_status"),
    [
        ({"review_state": "approved"}, 403),
        ({"login": "dependabot", "user_type": "Bot"}, 403),
        ({"login": "other-user"}, 403),
        ({"feedback": "   "}, 403),
        ({"pull_request_number": 78}, 202),
    ],
    ids=["approval", "bot", "other-user", "empty", "unrelated-pr"],
)
def test_non_feedback_pr_activity_has_no_continuation_effect(
    tmp_path, feedback_overrides: dict[str, object], expected_status: int
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=ControlledSourceControl(),
        reviewer=ControlledReviewer(),
        verifier=ControlledVerifier(),
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()
    feedback = feedback_body(**feedback_overrides)

    with TestClient(app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        response = client.post(
            "/webhooks/github",
            content=feedback,
            headers=signed_headers(
                feedback,
                delivery_id="feedback-rejected",
                event="pull_request_review",
            ),
        )
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert response.status_code == expected_status
    assert state["human_feedback"]["batches"] == []
    assert len(worktrees.calls) == 1
    assert worker.repair_invocations == []


def test_human_feedback_reuses_run_ownership_and_fully_verifies_a_new_head(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    source_control = SequencedSourceControl()
    reviewer = ControlledReviewer()
    verifier = ControlledVerifier()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()
    feedback = feedback_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()
        response = client.post(
            "/webhooks/github",
            content=feedback,
            headers=signed_headers(
                feedback,
                delivery_id="feedback-verified",
                event="pull_request_review",
            ),
        )
        after = client.get("/workflows/daniel/probare-crm/issues/41").json()

    batch = after["human_feedback"]["batches"][0]
    attempt = batch["attempts"][0]
    assignment = worker.repair_invocations[0].assignment
    assert response.status_code == 202
    assert after["run"]["id"] == before["run"]["id"]
    assert after["implementation"]["worktree"] == before["implementation"]["worktree"]
    assert len(worktrees.calls) == 1
    assert source_control.calls[0]["worktree"] == source_control.calls[1]["worktree"]
    assert github.pull_request_writes[0]["branch"] == github.pull_request_writes[1]["branch"]
    assert assignment["issue"] == before["implementation"]["assignment"]["issue"]
    assert assignment["requirements"] == before["implementation"]["assignment"]["requirements"]
    assert assignment["findings"] == [
        {
            "source": "repair",
            "axis": "repair",
            "location": "pull-request-review:901",
            "description": "Human feedback: Keep the CSV column order stable.",
        }
    ]
    assert batch["status"] == "verified"
    assert batch["round_count"] == 1
    assert attempt["head_sha"] == SequencedSourceControl.repair_head_sha
    assert {entry["criterion"] for entry in attempt["evidence"]} == {
        "Customer can export CSV",
        "Export includes active filters",
    }
    assert attempt["deterministic_verification"] == {
        "command": "pytest tests/test_export.py",
        "head_sha": SequencedSourceControl.repair_head_sha,
        "passed": True,
        "exit_code": 0,
        "observed": "passed",
    }
    assert attempt["review_batch_id"] == after["review"]["id"]
    assert attempt["invalidation_labels"] == ["agent-running", "ready-for-agent"]
    assert batch["superseded"]["head_sha"] == ControlledSourceControl.head_sha
    assert batch["superseded"]["review_batch_id"] == before["review"]["id"]
    assert batch["superseded"]["evidence"] == before["draft_pull_request"]["evidence"]
    assert after["review"]["head_sha"] == SequencedSourceControl.repair_head_sha
    assert len(after["review"]["results"]) == 3
    assert len(reviewer.invocations) == 6
    assert github.workflow_label_projections[-2]["add"] == frozenset({"agent-running"})
    assert github.workflow_label_projections[-2]["remove"] == frozenset(
        {"verified", "awaiting-review", "needs-info", "ready-for-human"}
    )
    assert {"verified", "awaiting-review"}.issubset(github.labels)
    assert "agent-running" not in github.labels
    assert [entry["superseded"] for entry in after["review_history"]] == [True, False]


def test_feedback_head_cannot_reuse_old_verification_and_runs_all_reviews_each_round(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    source_control = GeneratedHeadSourceControl()
    reviewer = ControlledReviewer()
    verifier = SequencedVerifier([False, True])
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        feedback = feedback_body(head_sha=f"{1:040x}")
        client.post(
            "/webhooks/github",
            content=feedback,
            headers=signed_headers(
                feedback,
                delivery_id="feedback-two-rounds",
                event="pull_request_review",
            ),
        )
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    batch = state["human_feedback"]["batches"][0]
    first, second = batch["attempts"]
    assert batch["status"] == "verified"
    assert first["status"] == "unsuccessful"
    assert first["deterministic_verification"]["passed"] is False
    assert first["review_batch_id"] == state["review_history"][1]["id"]
    assert state["review_history"][1]["status"] == "blocked"
    assert len(state["review_history"][1]["results"]) == 3
    assert second["status"] == "verified"
    assert second["deterministic_verification"]["passed"] is True
    assert second["review_batch_id"] == state["review_history"][2]["id"]
    assert state["review_history"][2]["status"] == "verified"
    assert len(reviewer.invocations) == 9
    assert [entry["superseded"] for entry in state["review_history"]] == [True, True, False]


def test_feedback_gets_round_one_after_the_initial_repair_batch_exhausted_three_rounds(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    source_control = GeneratedHeadSourceControl()
    reviewer = ControlledReviewer({"code": "fail"})
    sessions = ControlledInterventionSessions(
        InterventionAnswer(
            turn_id="feedback-exhaustion-answer",
            text="Acknowledge the handoff without a fourth repair round.",
        )
    )
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=ControlledVerifier(),
        intervention_sessions=sessions,
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
        heartbeat_interval_seconds=0.01,
    )
    issue = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        exhausted = client.get("/workflows/daniel/probare-crm/issues/41").json()
        for _ in range(300):
            if exhausted["repair"]["status"] == "ready-for-human":
                break
            time.sleep(0.01)
            exhausted = client.get(
                "/workflows/daniel/probare-crm/issues/41"
            ).json()
        reviewer.verdicts = {}
        feedback = feedback_body(
            feedback="Add an explicit CSV encoding assertion.",
            head_sha=exhausted["draft_pull_request"]["head_sha"],
        )
        client.post(
            "/webhooks/github",
            content=feedback,
            headers=signed_headers(
                feedback,
                delivery_id="feedback-after-exhaustion",
                event="pull_request_review",
            ),
        )
        continued = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert exhausted["repair"]["round_count"] == 3
    assert exhausted["repair"]["status"] == "ready-for-human"
    batch = continued["human_feedback"]["batches"][0]
    assert batch["round_count"] == 1
    assert batch["attempts"][0]["round"] == 1
    assert batch["status"] == "verified"
    assert len(worker.repair_invocations) == 4
    assert "ready-for-human" not in github.labels


def test_each_later_human_feedback_batch_starts_with_its_own_counter_and_context(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    source_control = GeneratedHeadSourceControl()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=ControlledReviewer(),
        verifier=ControlledVerifier(),
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        first = feedback_body(
            feedback="Keep the first feedback isolated.",
            head_sha=f"{1:040x}",
        )
        client.post(
            "/webhooks/github",
            content=first,
            headers=signed_headers(first, delivery_id="feedback-one", event="pull_request_review"),
        )
        second = feedback_body(
            feedback="Only apply the second feedback now.",
            head_sha=f"{2:040x}",
        )
        client.post(
            "/webhooks/github",
            content=second,
            headers=signed_headers(second, delivery_id="feedback-two", event="pull_request_review"),
        )
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    batches = state["human_feedback"]["batches"]
    assert [(batch["round_count"], batch["status"]) for batch in batches] == [
        (1, "verified"),
        (1, "verified"),
    ]
    first_assignment, second_assignment = [
        invocation.assignment for invocation in worker.repair_invocations
    ]
    assert first_assignment["findings"][0]["description"] == (
        "Human feedback: Keep the first feedback isolated."
    )
    assert second_assignment["findings"][0]["description"] == (
        "Human feedback: Only apply the second feedback now."
    )
    assert "first feedback" not in json.dumps(second_assignment)


def test_one_human_feedback_batch_stops_after_exactly_three_attempts(
    tmp_path,
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    source_control = GeneratedHeadSourceControl()
    reviewer = ControlledReviewer()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=ControlledVerifier(),
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        reviewer.verdicts = {"code": "fail"}
        feedback = feedback_body(head_sha=f"{1:040x}")
        client.post(
            "/webhooks/github",
            content=feedback,
            headers=signed_headers(
                feedback,
                delivery_id="feedback-exhausted",
                event="pull_request_review",
            ),
        )
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    batch = state["human_feedback"]["batches"][0]
    assert batch["status"] == "ready-for-human"
    assert batch["round_count"] == 3
    assert "ready-for-human" in batch["projected_labels"]
    assert [attempt["round"] for attempt in batch["attempts"]] == [1, 2, 3]
    assert len(worker.repair_invocations) == 3
    assert len(source_control.calls) == 4
    assert "ready-for-human" in github.labels
    assert not {"agent-running", "verified", "awaiting-review"}.intersection(github.labels)


def test_authorized_human_merge_completes_the_same_run_and_checkpoint_after_restart(
    tmp_path,
) -> None:
    database_path = tmp_path / "pilot.db"
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledRepairWorker()
    source_control = SequencedSourceControl()
    reviewer = ControlledReviewer()
    verifier = ControlledVerifier()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=source_control,
        reviewer=reviewer,
        verifier=verifier,
    )
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()
    feedback = feedback_body()

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        client.post(
            "/webhooks/github",
            content=feedback,
            headers=signed_headers(
                feedback,
                delivery_id="feedback-before-merge",
                event="pull_request_review",
            ),
        )
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()

    effect_counts = (
        len(worktrees.calls),
        len(worker.repair_invocations),
        len(source_control.calls),
        len(reviewer.invocations),
    )
    github.open = False
    github.implementation_pr_merged = True
    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    merge = merge_body(head_sha=SequencedSourceControl.repair_head_sha)

    with TestClient(restarted_app) as client:
        response = client.post(
            "/webhooks/github",
            content=merge,
            headers=signed_headers(merge, delivery_id="merge-001", event="pull_request"),
        )
        completed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    terminal_restart = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    with TestClient(terminal_restart) as client:
        after_terminal_restart = client.get(
            "/workflows/daniel/probare-crm/issues/41"
        ).json()

    assert response.status_code == 202
    assert completed["run"]["id"] == before["run"]["id"]
    assert completed["run"]["status"] == "completed"
    assert completed["checkpoint"]["values"]["status"] == "completed"
    assert completed["completion"] == {
        "reason": "human-merged",
        "delivery_id": "merge-001",
        "pull_request_number": 77,
        "head_sha": SequencedSourceControl.repair_head_sha,
        "actor": "daniel",
        "completed_at": "2026-08-21T10:30:00+00:00",
    }
    assert completed["human_feedback"] == before["human_feedback"]
    assert completed["review_history"] == before["review_history"]
    assert after_terminal_restart == completed
    assert (
        len(worktrees.calls),
        len(worker.repair_invocations),
        len(source_control.calls),
        len(reviewer.invocations),
    ) == effect_counts


def test_qualifying_boot_reconciles_the_active_human_merged_pull_request(
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
    first_seen = fixed_clock()
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=lambda: first_seen,
        boot_session_id=lambda: "boot-a",
        implementation=services,
    )
    issue = delivery_body()

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        before = client.get("/workflows/daniel/probare-crm/issues/41").json()

    github.open = False
    github.implementation_pr_merged = True
    github.pull_request_merged = True
    restarted_at = first_seen + timedelta(hours=25)
    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=lambda: restarted_at,
        boot_session_id=lambda: "boot-b",
        implementation=services,
    )

    with TestClient(restarted_app) as client:
        completed = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert completed["run"]["id"] == before["run"]["id"]
    assert completed["run"]["status"] == "completed"
    assert completed["checkpoint"]["values"]["status"] == "completed"
    assert completed["completion"]["reason"] == "human-merged"
    assert completed["completion"]["pull_request_number"] == 77
    assert completed["completion"]["head_sha"] == source_control.head_sha
    assert completed["completion"]["delivery_id"].startswith("reconcile-")
    assert completed["reconciliation"]["discovered_commands"] == 1
    assert completed["reconciliation"]["accepted_commands"] == 1


def test_startup_reconciliation_completes_active_merge_before_ready_successor(
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
    first_seen = fixed_clock()
    first_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=lambda: first_seen,
        boot_session_id=lambda: "boot-a",
        implementation=services,
    )
    issue = delivery_body()

    with TestClient(first_app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))

    github.issue_states = {
        41: IssueState(
            open=False,
            labels=frozenset(),
            implementation_pr_merged=True,
        ),
        52: IssueState(
            open=True,
            labels=frozenset({"ready-for-agent"}),
            title="Add a ready successor",
            body="- [ ] Successor runs after merged active work",
            issue_type="feature",
        ),
    }
    github.pull_request_merged = True
    restarted_at = first_seen + timedelta(hours=25)
    restarted_app = create_app(
        database_path=database_path,
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=lambda: restarted_at,
        boot_session_id=lambda: "boot-b",
        implementation=services,
    )

    with TestClient(restarted_app) as client:
        completed = client.get("/workflows/daniel/probare-crm/issues/41").json()
        successor = client.get("/workflows/daniel/probare-crm/issues/52").json()

    assert completed["run"]["status"] == "completed"
    assert completed["completion"]["reason"] == "human-merged"
    assert successor["run"]["status"] == "running"
    assert successor["disposition"]["status"] == "selected"
    assert successor["reconciliation"]["discovered_commands"] == 2
    assert successor["reconciliation"]["accepted_commands"] == 2


@pytest.mark.parametrize(
    "merge_overrides",
    [
        {"merged": False},
        {"login": "other-user"},
        {"user_type": "Bot"},
        {"pull_request_number": 78},
        {"head_sha": "ffffffffffffffffffffffffffffffffffffffff"},
    ],
    ids=["not-merged", "other-user", "bot", "unrelated-pr", "wrong-head"],
)
def test_pr_close_without_the_correlated_human_merge_does_not_complete_the_run(
    tmp_path, merge_overrides: dict[str, object]
) -> None:
    github = ControlledGitHub()
    worktrees = ControlledWorktrees(tmp_path / "worktrees")
    worker = ControlledWorker()
    services = controlled_implementation_services(
        tmp_path,
        worktrees,
        worker,
        source_control=ControlledSourceControl(),
        reviewer=ControlledReviewer(),
        verifier=ControlledVerifier(),
    )
    app = create_app(
        database_path=tmp_path / "pilot.db",
        webhook_secret=SECRET,
        repository_adapters={REPOSITORY: github},
        clock=fixed_clock,
        implementation=services,
    )
    issue = delivery_body()

    with TestClient(app) as client:
        client.post("/webhooks/github", content=issue, headers=signed_headers(issue))
        github.open = False
        github.implementation_pr_merged = True
        merge = merge_body(**merge_overrides)
        response = client.post(
            "/webhooks/github",
            content=merge,
            headers=signed_headers(merge, delivery_id="merge-ignored", event="pull_request"),
        )
        state = client.get("/workflows/daniel/probare-crm/issues/41").json()

    assert response.status_code == 202
    assert state["run"]["status"] == "running"
    assert state["completion"] is None
    assert len(worktrees.calls) == 1
    assert len(worker.invocations) == 1
