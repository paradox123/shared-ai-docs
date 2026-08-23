from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.evidence import (
    EvidenceRejected,
    qualify_evidence,
    redact_payload,
    redact_text,
    render_pull_request_body,
)
from github_issue_pilot.implementation import (
    ImplementationServices,
    InvalidWorkerResult,
    WorkerExecutionError,
    Worktree,
    validate_worker_result,
)
from github_issue_pilot.policy import (
    NodePolicy,
    NodeSelection,
    PolicyViolation,
    SkillProvenance,
)
from github_issue_pilot.publication import SourcePublicationError
from github_issue_pilot.review import ReviewBatchInput, ReviewCoordinator

if TYPE_CHECKING:
    from github_issue_pilot.github import RepositoryAdapter
    from github_issue_pilot.storage import WorkflowStore


class InvalidRepairContract(ValueError):
    pass


@dataclass(frozen=True)
class RepairInvocation:
    assignment: dict[str, object]
    worktree: Worktree
    selection: NodeSelection
    skills: tuple[SkillProvenance, ...]
    access_profile: dict[str, object]
    escalation_reason: str | None = None


@dataclass(frozen=True)
class RepairOutput:
    result: dict[str, object]
    diagnostic_events: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class RepairBatchInput:
    run_id: str
    repository: str
    issue_number: int
    initial_review: dict[str, object]
    implementation: dict[str, object]


def validate_repair_assignment(assignment: dict[str, object]) -> None:
    try:
        Draft202012Validator(load_contract("repair-assignment-v1.json")).validate(assignment)
    except ValidationError as exc:
        raise InvalidRepairContract(
            f"repair assignment does not match schema: {exc.message}"
        ) from exc


def validate_repair_result(result: dict[str, object]) -> None:
    try:
        Draft202012Validator(load_contract("repair-result-v1.json")).validate(result)
        implementation_result = result.get("implementation_result")
        if isinstance(implementation_result, dict):
            validate_worker_result(implementation_result)
    except (InvalidWorkerResult, ValidationError) as exc:
        message = exc.message if isinstance(exc, ValidationError) else str(exc)
        raise InvalidRepairContract(f"repair result does not match schema: {message}") from exc
    if result["outcome"] == "blocked":
        blockage = result["blockage"]
        if not isinstance(blockage, dict):
            raise InvalidRepairContract("blocked repair result has no structured reason")
        needs_info_reasons = {
            "product_decision",
            "scope_expansion",
            "requirements_missing_or_contradictory",
        }
        expected = (
            "needs-info" if blockage["reason"] in needs_info_reasons else "ready-for-human"
        )
        if result["terminal_disposition"] != expected:
            raise InvalidRepairContract(
                "missing requirements require needs-info"
                if blockage["reason"] == "requirements_missing_or_contradictory"
                else f"{blockage['reason']} requires {expected}"
            )


class ReviewRepairCoordinator:
    ROUND_LIMIT = 3

    def __init__(
        self,
        *,
        store: WorkflowStore,
        adapter: RepositoryAdapter,
        services: ImplementationServices,
        clock: Callable[[], datetime],
    ) -> None:
        self._store = store
        self._adapter = adapter
        self._services = services
        self._clock = clock

    def execute(self, repair_input: RepairBatchInput) -> str:
        initial_review = repair_input.initial_review
        findings = self._review_findings(initial_review)
        if initial_review.get("reason") != "review_failed" or not findings:
            return "review_blocked"
        repair_batch_id = self._store.begin_repair_batch(
            run_id=repair_input.run_id,
            initial_review_batch_id=str(initial_review["id"]),
            started_at=self._now(),
        )
        previous_head = str(initial_review["head_sha"])
        terminal_disposition: str | None = None

        for round_number in range(1, self.ROUND_LIMIT + 1):
            repair_state = self._store.workflow_repair(repair_input.run_id)
            assignment = self._build_assignment(
                repair_input=repair_input,
                repair_batch_id=repair_batch_id,
                round_number=round_number,
                findings=findings,
                repair_state=repair_state,
            )
            attempt_id = self._store.begin_repair_attempt(
                repair_batch_id=repair_batch_id,
                round_number=round_number,
                assignment=assignment,
                started_at=self._now(),
            )
            result = self._run_repair_invocation(
                repair_input=repair_input,
                attempt_id=attempt_id,
                invocation_number=1,
                assignment=assignment,
                round_number=round_number,
                escalation_reason=(
                    "final_repair_round" if round_number == self.ROUND_LIMIT else None
                ),
            )
            if result is not None and result["outcome"] == "escalate":
                result = self._run_repair_invocation(
                    repair_input=repair_input,
                    attempt_id=attempt_id,
                    invocation_number=2,
                    assignment=assignment,
                    round_number=round_number,
                    escalation_reason=str(result["escalation_reason"]),
                )
            if result is None or result.get("outcome") == "escalate":
                findings = [self._repair_failure("repair worker did not complete the assignment")]
                self._store.complete_repair_attempt(
                    attempt_id=attempt_id,
                    status="failed",
                    head_sha=None,
                    deterministic_verification=None,
                    review_batch_id=None,
                    remaining_findings=findings,
                    completed_at=self._now(),
                )
                continue
            if result["outcome"] == "blocked":
                blockage = result["blockage"]
                if not isinstance(blockage, dict):
                    raise InvalidRepairContract("blocked repair has no blockage")
                findings = [self._repair_failure(str(blockage["rationale"]))]
                terminal_disposition = str(result["terminal_disposition"])
                self._store.complete_repair_attempt(
                    attempt_id=attempt_id,
                    status="blocked",
                    head_sha=None,
                    deterministic_verification=None,
                    review_batch_id=None,
                    remaining_findings=findings,
                    completed_at=self._now(),
                )
                return self._handoff(
                    repair_input,
                    repair_batch_id,
                    terminal_disposition,
                    findings,
                )

            terminal_disposition = (
                str(result["terminal_disposition"])
                if result.get("terminal_disposition") is not None
                else terminal_disposition
            )
            implementation_result = result["implementation_result"]
            if not isinstance(implementation_result, dict):
                raise InvalidRepairContract("completed repair has no implementation result")
            publication = self._publish_repair(
                repair_input=repair_input,
                round_number=round_number,
                result=result,
                implementation_result=implementation_result,
                previous_head=previous_head,
            )
            if publication is None:
                findings = [self._repair_failure("repair did not produce a safe new head")]
                self._store.complete_repair_attempt(
                    attempt_id=attempt_id,
                    status="failed",
                    head_sha=None,
                    deterministic_verification=None,
                    review_batch_id=None,
                    remaining_findings=findings,
                    completed_at=self._now(),
                )
                continue

            head_sha = str(publication["head_sha"])
            verifier = self._services.verifier
            reviewer = self._services.reviewer
            if verifier is None or reviewer is None:
                raise RuntimeError("repair verification services are not configured")
            worktree = self._worktree(repair_input.implementation)
            context = self._services.repository_contexts[repair_input.repository]
            verification = verifier.verify(
                worktree,
                command=context.verification_command,
                head_sha=head_sha,
            )
            current_implementation = dict(repair_input.implementation)
            current_implementation["result"] = implementation_result
            review_status = ReviewCoordinator(
                store=self._store,
                adapter=self._adapter,
                reviewer=reviewer,
                skill_root=self._services.skill_root,
                sensitive_values=self._services.sensitive_values,
                clock=self._clock,
            ).execute(
                ReviewBatchInput(
                    run_id=repair_input.run_id,
                    repository=repair_input.repository,
                    issue_number=repair_input.issue_number,
                    implementation=current_implementation,
                    publication=publication,
                    allow_verification_projection=verification.passed,
                )
            )
            fresh_review = self._store.workflow_review(repair_input.run_id)
            if fresh_review is None:
                raise RuntimeError("repair review batch was not persisted")
            findings = self._review_findings(fresh_review)
            if not verification.passed:
                findings.insert(
                    0,
                    {
                        "source": "deterministic_verification",
                        "axis": "deterministic_verification",
                        "location": context.verification_command,
                        "description": verification.observed,
                    },
                )
            verified = review_status == "verified" and verification.passed
            self._store.complete_repair_attempt(
                attempt_id=attempt_id,
                status="verified" if verified else "unsuccessful",
                head_sha=head_sha,
                deterministic_verification=verification.as_dict(),
                review_batch_id=str(fresh_review["id"]),
                remaining_findings=findings,
                completed_at=self._now(),
            )
            if verified:
                self._store.complete_repair_batch(
                    repair_batch_id=repair_batch_id,
                    status="verified",
                    open_findings=[],
                    projected_labels=frozenset(fresh_review["projected_labels"]),
                    completed_at=self._now(),
                )
                self._refresh_pull_request(repair_input, open_findings=[])
                return "verified"
            previous_head = head_sha

        return self._handoff(
            repair_input,
            repair_batch_id,
            terminal_disposition or "ready-for-human",
            findings,
        )

    def _build_assignment(
        self,
        *,
        repair_input: RepairBatchInput,
        repair_batch_id: str,
        round_number: int,
        findings: list[dict[str, object]],
        repair_state: dict[str, object] | None,
    ) -> dict[str, object]:
        implementation_assignment = repair_input.implementation["assignment"]
        if not isinstance(implementation_assignment, dict):
            raise InvalidRepairContract("implementation assignment is unavailable")
        context = self._services.repository_contexts[repair_input.repository]
        prior_attempts = []
        if repair_state is not None:
            for attempt in repair_state["attempts"]:
                invocations = attempt["invocations"]
                last_result = invocations[-1]["result"] if invocations else {}
                prior_attempts.append(
                    {
                        "round": attempt["round"],
                        "head_sha": attempt["head_sha"],
                        "summary": last_result.get("summary", "Repair attempt failed"),
                        "remaining_findings": attempt["remaining_findings"],
                    }
                )
        assignment: dict[str, object] = {
            "schema_version": "1",
            "repair_batch_id": repair_batch_id,
            "initial_review": {
                "batch_id": repair_input.initial_review["id"],
                "head_sha": repair_input.initial_review["head_sha"],
            },
            "round": {"number": round_number, "limit": self.ROUND_LIMIT},
            "issue": implementation_assignment["issue"],
            "requirements": implementation_assignment["requirements"],
            "repository_context": {
                "base_ref": context.base_ref,
                "instructions": context.instructions,
                "verification_command": context.verification_command,
            },
            "findings": findings,
            "prior_attempts": prior_attempts,
            "decision_policy": {
                "autonomous": "Small reversible implementation and presentation details.",
                "product_decisions": (
                    "Warnings, consent, domain actions, security meaning, and semantic behavior."
                ),
                "interruptions": [
                    "product_decision",
                    "scope_expansion",
                    "missing_access",
                    "manual_evidence",
                    "requirements_missing_or_contradictory",
                    "unresolvable_conflict",
                ],
            },
        }
        validate_repair_assignment(assignment)
        return assignment

    def _run_repair_invocation(
        self,
        *,
        repair_input: RepairBatchInput,
        attempt_id: str,
        invocation_number: int,
        assignment: dict[str, object],
        round_number: int,
        escalation_reason: str | None,
    ) -> dict[str, object] | None:
        selection = NodePolicy.packaged().select_repair(
            round_number=round_number,
            escalation_reason=escalation_reason,
        )
        worktree = self._worktree(repair_input.implementation)
        skills = tuple(
            SkillProvenance(
                name=str(skill["name"]),
                content_sha256=str(skill["content_sha256"]),
            )
            for skill in repair_input.implementation["skills"]
        )
        access_profile: dict[str, object] = {
            "role": "implementer",
            "sandbox": selection.sandbox,
            "write_root": str(worktree.path),
            "additional_write_roots": [],
        }
        started_at = self._now()
        diagnostics: list[dict[str, object]] = []
        try:
            output = self._services.worker.repair(
                RepairInvocation(
                    assignment=assignment,
                    worktree=worktree,
                    selection=selection,
                    skills=skills,
                    access_profile=access_profile,
                    escalation_reason=escalation_reason,
                )
            )
            redacted_result = redact_payload(output.result, self._services.sensitive_values)
            redacted_diagnostics = redact_payload(
                list(output.diagnostic_events), self._services.sensitive_values
            )
            if not isinstance(redacted_result, dict) or not isinstance(
                redacted_diagnostics, list
            ):
                raise InvalidRepairContract("repair redaction changed output shape")
            validate_repair_result(redacted_result)
            if (
                redacted_result["repair_batch_id"] != assignment["repair_batch_id"]
                or redacted_result["round_number"] != round_number
            ):
                raise InvalidRepairContract("repair result does not match its assignment")
            result = redacted_result
            diagnostics = redacted_diagnostics
        except (InvalidRepairContract, PolicyViolation, TypeError, WorkerExecutionError):
            result = {
                "schema_version": "1",
                "repair_batch_id": assignment["repair_batch_id"],
                "round_number": round_number,
                "outcome": "failed",
                "summary": "repair_execution_failed",
            }
        self._store.record_repair_invocation(
            attempt_id=attempt_id,
            invocation_number=invocation_number,
            policy={
                "version": selection.policy_version,
                "task": selection.task,
                "model": selection.model,
                "reasoning_effort": selection.reasoning_effort,
                "sandbox": selection.sandbox,
                "escalation_reason": escalation_reason,
            },
            skills=[
                {"name": skill.name, "content_sha256": skill.content_sha256}
                for skill in skills
            ],
            access_profile=access_profile,
            result=result,
            diagnostic_events=diagnostics,
            started_at=started_at,
            completed_at=self._now(),
        )
        return result if result.get("outcome") != "failed" else None

    def _publish_repair(
        self,
        *,
        repair_input: RepairBatchInput,
        round_number: int,
        result: dict[str, object],
        implementation_result: dict[str, object],
        previous_head: str,
    ) -> dict[str, object] | None:
        source_control = self._services.source_control
        if source_control is None:
            return None
        implementation_assignment = repair_input.implementation["assignment"]
        if not isinstance(implementation_assignment, dict):
            return None
        try:
            evidence = qualify_evidence(
                implementation_assignment["requirements"],
                implementation_result,
                sensitive_values=self._services.sensitive_values,
            )
            published = source_control.publish(
                self._worktree(repair_input.implementation),
                issue_number=repair_input.issue_number,
                sensitive_values=self._services.sensitive_values,
            )
            if published.head_sha == previous_head:
                return None
            prior_state = self._store.workflow_repair(repair_input.run_id)
            attempts = self._render_attempts(prior_state)
            attempts.append(
                {
                    "round": round_number,
                    "status": "reviewing",
                    "head_sha": published.head_sha,
                    "summary": result["summary"],
                }
            )
            body = render_pull_request_body(
                issue_number=repair_input.issue_number,
                head_sha=published.head_sha,
                evidence=evidence,
                repair_attempts=attempts,
            )
            issue = implementation_assignment["issue"]
            if not isinstance(issue, dict):
                return None
            pull_request = self._adapter.ensure_draft_pull_request(
                repair_input.repository,
                issue_number=repair_input.issue_number,
                branch=published.branch,
                title=redact_text(
                    f"Implement #{repair_input.issue_number}: {issue['title']}",
                    self._services.sensitive_values,
                ),
                body=body,
                head_sha=published.head_sha,
            )
            if pull_request.body != body:
                return None
            self._store.update_publication(
                run_id=repair_input.run_id,
                evidence=evidence,
                head_sha=published.head_sha,
                body=body,
                completed_at=self._now(),
            )
        except (
            EvidenceRejected,
            OSError,
            RuntimeError,
            SourcePublicationError,
            TypeError,
            ValueError,
        ):
            return None
        return self._store.workflow_publication(repair_input.run_id)

    def _handoff(
        self,
        repair_input: RepairBatchInput,
        repair_batch_id: str,
        disposition: str,
        findings: list[dict[str, object]],
    ) -> str:
        status = "needs-info" if disposition == "needs-info" else "ready-for-human"
        projected = self._adapter.project_workflow_labels(
            repair_input.repository,
            repair_input.issue_number,
            add=frozenset({status}),
            remove=frozenset({"agent-running", "verified", "awaiting-review"}),
        )
        self._store.complete_repair_batch(
            repair_batch_id=repair_batch_id,
            status=status,
            open_findings=findings,
            projected_labels=projected,
            completed_at=self._now(),
        )
        self._refresh_pull_request(repair_input, open_findings=findings)
        return status

    def _refresh_pull_request(
        self,
        repair_input: RepairBatchInput,
        *,
        open_findings: list[dict[str, object]],
    ) -> None:
        publication = self._store.workflow_publication(repair_input.run_id)
        repair_state = self._store.workflow_repair(repair_input.run_id)
        implementation_assignment = repair_input.implementation["assignment"]
        if (
            publication is None
            or repair_state is None
            or not isinstance(implementation_assignment, dict)
            or publication["head_sha"] is None
        ):
            return
        issue = implementation_assignment["issue"]
        if not isinstance(issue, dict):
            return
        body = render_pull_request_body(
            issue_number=repair_input.issue_number,
            head_sha=str(publication["head_sha"]),
            evidence=publication["evidence"],
            repair_attempts=self._render_attempts(repair_state),
            open_findings=open_findings,
        )
        pull_request = self._adapter.ensure_draft_pull_request(
            repair_input.repository,
            issue_number=repair_input.issue_number,
            branch=str(publication["branch"]),
            title=redact_text(
                f"Implement #{repair_input.issue_number}: {issue['title']}",
                self._services.sensitive_values,
            ),
            body=body,
            head_sha=str(publication["head_sha"]),
        )
        if pull_request.body == body:
            self._store.update_publication(
                run_id=repair_input.run_id,
                evidence=publication["evidence"],
                head_sha=str(publication["head_sha"]),
                body=body,
                completed_at=self._now(),
            )

    @staticmethod
    def _review_findings(review: dict[str, object]) -> list[dict[str, object]]:
        findings: list[dict[str, object]] = []
        for axis_result in review.get("results", []):
            verdict = axis_result.get("verdict", {})
            if verdict.get("verdict") != "fail":
                continue
            for finding in verdict.get("findings", []):
                findings.append(
                    {
                        "source": "review",
                        "axis": axis_result["axis"],
                        "location": finding["location"],
                        "description": finding["description"],
                    }
                )
        return findings

    @staticmethod
    def _repair_failure(description: str) -> dict[str, object]:
        return {
            "source": "repair",
            "axis": "repair",
            "location": "repair worker",
            "description": description,
        }

    @staticmethod
    def _render_attempts(repair_state: dict[str, object] | None) -> list[dict[str, object]]:
        if repair_state is None:
            return []
        rendered = []
        for attempt in repair_state["attempts"]:
            invocations = attempt["invocations"]
            last_result = invocations[-1]["result"] if invocations else {}
            rendered.append(
                {
                    "round": attempt["round"],
                    "status": attempt["status"],
                    "head_sha": attempt["head_sha"],
                    "summary": last_result.get("summary", "Repair attempt"),
                }
            )
        return rendered

    @staticmethod
    def _worktree(implementation: dict[str, object]) -> Worktree:
        worktree = implementation["worktree"]
        return Worktree(
            path=Path(str(worktree["path"])),
            branch=str(worktree["branch"]),
            base_ref=str(worktree["base_ref"]),
        )

    def _now(self) -> str:
        return self._clock().isoformat()
