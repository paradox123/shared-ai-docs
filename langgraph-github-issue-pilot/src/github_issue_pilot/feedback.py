from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from github_issue_pilot.evidence import (
    EvidenceRejected,
    qualify_evidence,
    redact_payload,
    redact_text,
    render_pull_request_body,
)
from github_issue_pilot.implementation import (
    ImplementationServices,
    WorkerExecutionError,
    Worktree,
)
from github_issue_pilot.policy import NodePolicy, PolicyViolation, SkillProvenance
from github_issue_pilot.publication import SourcePublicationError
from github_issue_pilot.repair import (
    InvalidRepairContract,
    RepairInvocation,
    validate_repair_assignment,
    validate_repair_result,
)
from github_issue_pilot.review import ReviewBatchInput, ReviewCoordinator


@dataclass(frozen=True)
class HumanFeedbackInput:
    run_id: str
    repository: str
    issue_number: int
    feedback_batch_id: str
    pull_request_number: int
    starting_head_sha: str
    source_id: str
    feedback: tuple[str, ...]
    implementation: dict[str, object]


class HumanFeedbackCoordinator:
    """Apply one human feedback batch in the existing run-owned worktree."""

    ROUND_LIMIT = 3

    def __init__(
        self,
        *,
        store,
        adapter,
        services: ImplementationServices,
        clock: Callable[[], datetime],
    ) -> None:
        self._store = store
        self._adapter = adapter
        self._services = services
        self._clock = clock

    def execute(self, feedback_input: HumanFeedbackInput) -> str:
        if self._adapter.current_pull_request_head(
            feedback_input.repository, feedback_input.pull_request_number
        ) != feedback_input.starting_head_sha:
            return "feedback_head_mismatch"
        initial_review = self._store.workflow_review(feedback_input.run_id)
        initial_review_id = str(initial_review["id"]) if initial_review else "unreviewed-head"
        findings = self._human_findings(feedback_input)
        previous_head = feedback_input.starting_head_sha

        for round_number in range(1, self.ROUND_LIMIT + 1):
            assignment = self._build_assignment(
                feedback_input=feedback_input,
                initial_review_id=initial_review_id,
                round_number=round_number,
                findings=findings,
            )
            attempt_id = self._store.begin_feedback_attempt(
                feedback_batch_id=feedback_input.feedback_batch_id,
                round_number=round_number,
                assignment=assignment,
                started_at=self._now(),
            )
            invocation = self._invoke(
                feedback_input=feedback_input,
                assignment=assignment,
                round_number=round_number,
            )
            result = invocation["result"]
            if result.get("outcome") == "blocked":
                disposition = str(result.get("terminal_disposition") or "ready-for-human")
                status = "needs-info" if disposition == "needs-info" else "ready-for-human"
                projected = self._handoff(feedback_input, status)
                self._complete_attempt(
                    attempt_id=attempt_id,
                    status="blocked",
                    invocation=invocation,
                    result=result,
                    projected_labels=projected,
                )
                self._store.complete_feedback_batch(
                    feedback_batch_id=feedback_input.feedback_batch_id,
                    status=status,
                    projected_labels=projected,
                    completed_at=self._now(),
                )
                return status

            implementation_result = result.get("implementation_result")
            publication = (
                self._publish(
                    feedback_input=feedback_input,
                    round_number=round_number,
                    result=result,
                    implementation_result=implementation_result,
                    previous_head=previous_head,
                )
                if isinstance(implementation_result, dict)
                else None
            )
            if publication is None:
                self._complete_attempt(
                    attempt_id=attempt_id,
                    status="failed",
                    invocation=invocation,
                    result=result,
                )
                findings = self._failure_findings("Feedback attempt produced no new head")
                continue

            head_sha = str(publication["head_sha"])
            invalidated = self._adapter.project_workflow_labels(
                feedback_input.repository,
                feedback_input.issue_number,
                add=frozenset({"agent-running"}),
                remove=frozenset(
                    {"verified", "awaiting-review", "needs-info", "ready-for-human"}
                ),
            )
            verifier = self._services.verifier
            reviewer = self._services.reviewer
            if verifier is None or reviewer is None:
                self._complete_attempt(
                    attempt_id=attempt_id,
                    status="failed",
                    invocation=invocation,
                    result=result,
                    head_sha=head_sha,
                    evidence=list(publication["evidence"]),
                    projected_labels=invalidated,
                    invalidation_labels=invalidated,
                )
                findings = self._failure_findings("Verification services are unavailable")
                previous_head = head_sha
                continue

            context = self._services.repository_contexts[feedback_input.repository]
            verification = verifier.verify(
                self._worktree(feedback_input.implementation),
                command=context.verification_command,
                head_sha=head_sha,
            )
            reviewed_implementation = dict(feedback_input.implementation)
            reviewed_implementation["result"] = implementation_result
            review_status = ReviewCoordinator(
                store=self._store,
                adapter=self._adapter,
                reviewer=reviewer,
                skill_root=self._services.skill_root,
                sensitive_values=self._services.sensitive_values,
                clock=self._clock,
            ).execute(
                ReviewBatchInput(
                    run_id=feedback_input.run_id,
                    repository=feedback_input.repository,
                    issue_number=feedback_input.issue_number,
                    implementation=reviewed_implementation,
                    publication=publication,
                    allow_verification_projection=verification.passed,
                )
            )
            review = self._store.workflow_review(feedback_input.run_id)
            verified = review_status == "verified" and verification.passed
            projected = (
                frozenset(review["projected_labels"])
                if review is not None and verified
                else invalidated
            )
            self._complete_attempt(
                attempt_id=attempt_id,
                status="verified" if verified else "unsuccessful",
                invocation=invocation,
                result=result,
                head_sha=head_sha,
                evidence=list(publication["evidence"]),
                deterministic_verification=verification.as_dict(),
                review_batch_id=str(review["id"]) if review else None,
                projected_labels=projected,
                invalidation_labels=invalidated,
            )
            if verified:
                self._store.complete_feedback_batch(
                    feedback_batch_id=feedback_input.feedback_batch_id,
                    status="verified",
                    projected_labels=projected,
                    completed_at=self._now(),
                )
                return "verified"
            findings = self._fresh_findings(review, verification.passed)
            previous_head = head_sha

        projected = self._handoff(feedback_input, "ready-for-human")
        self._store.complete_feedback_batch(
            feedback_batch_id=feedback_input.feedback_batch_id,
            status="ready-for-human",
            projected_labels=projected,
            completed_at=self._now(),
        )
        return "ready-for-human"

    def _build_assignment(
        self,
        *,
        feedback_input: HumanFeedbackInput,
        initial_review_id: str,
        round_number: int,
        findings: list[dict[str, object]],
    ) -> dict[str, object]:
        implementation_assignment = feedback_input.implementation["assignment"]
        context = self._services.repository_contexts[feedback_input.repository]
        feedback_state = self._store.workflow_feedback(feedback_input.run_id)
        current = next(
            batch
            for batch in feedback_state["batches"]
            if batch["id"] == feedback_input.feedback_batch_id
        )
        prior_attempts = [
            {
                "round": attempt["round"],
                "head_sha": attempt["head_sha"],
                "summary": (attempt["result"] or {}).get("summary", "Feedback attempt failed"),
                "remaining_findings": self._failure_findings("Fresh verification did not pass"),
            }
            for attempt in current["attempts"][-2:]
        ]
        assignment: dict[str, object] = {
            "schema_version": "1",
            "repair_batch_id": feedback_input.feedback_batch_id,
            "initial_review": {
                "batch_id": initial_review_id,
                "head_sha": feedback_input.starting_head_sha,
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

    def _invoke(
        self,
        *,
        feedback_input: HumanFeedbackInput,
        assignment: dict[str, object],
        round_number: int,
    ) -> dict[str, object]:
        selection = NodePolicy.packaged().select_repair(round_number=round_number)
        skills = tuple(
            SkillProvenance(
                name=str(skill["name"]),
                content_sha256=str(skill["content_sha256"]),
            )
            for skill in feedback_input.implementation["skills"]
        )
        worktree = self._worktree(feedback_input.implementation)
        access_profile: dict[str, object] = {
            "role": "implementer",
            "sandbox": selection.sandbox,
            "write_root": str(worktree.path),
            "additional_write_roots": [],
        }
        diagnostics: list[dict[str, object]] = []
        try:
            output = self._services.worker.repair(
                RepairInvocation(
                    assignment=assignment,
                    worktree=worktree,
                    selection=selection,
                    skills=skills,
                    access_profile=access_profile,
                )
            )
            result = redact_payload(output.result, self._services.sensitive_values)
            redacted_diagnostics = redact_payload(
                list(output.diagnostic_events), self._services.sensitive_values
            )
            if not isinstance(result, dict) or not isinstance(redacted_diagnostics, list):
                raise InvalidRepairContract("feedback redaction changed output shape")
            validate_repair_result(result)
            if result["repair_batch_id"] != feedback_input.feedback_batch_id:
                raise InvalidRepairContract("feedback result does not match its assignment")
            diagnostics = redacted_diagnostics
        except (InvalidRepairContract, PolicyViolation, TypeError, WorkerExecutionError):
            result = {
                "schema_version": "1",
                "repair_batch_id": feedback_input.feedback_batch_id,
                "round_number": round_number,
                "outcome": "failed",
                "summary": "feedback_execution_failed",
            }
        return {
            "result": result,
            "diagnostic_events": diagnostics,
            "policy": {
                "version": selection.policy_version,
                "task": selection.task,
                "model": selection.model,
                "reasoning_effort": selection.reasoning_effort,
                "sandbox": selection.sandbox,
            },
            "skills": [
                {"name": skill.name, "content_sha256": skill.content_sha256}
                for skill in skills
            ],
            "access_profile": access_profile,
        }

    def _publish(
        self,
        *,
        feedback_input: HumanFeedbackInput,
        round_number: int,
        result: dict[str, object],
        implementation_result: dict[str, object],
        previous_head: str,
    ) -> dict[str, object] | None:
        source_control = self._services.source_control
        if source_control is None:
            return None
        implementation_assignment = feedback_input.implementation["assignment"]
        try:
            evidence = qualify_evidence(
                implementation_assignment["requirements"],
                implementation_result,
                sensitive_values=self._services.sensitive_values,
            )
            published = source_control.publish(
                self._worktree(feedback_input.implementation),
                issue_number=feedback_input.issue_number,
                sensitive_values=self._services.sensitive_values,
            )
            if published.head_sha == previous_head:
                return None
            body = render_pull_request_body(
                issue_number=feedback_input.issue_number,
                head_sha=published.head_sha,
                evidence=evidence,
                repair_attempts=[
                    {
                        "round": round_number,
                        "status": "reviewing",
                        "head_sha": published.head_sha,
                        "summary": result["summary"],
                    }
                ],
            )
            issue = implementation_assignment["issue"]
            pull_request = self._adapter.ensure_draft_pull_request(
                feedback_input.repository,
                issue_number=feedback_input.issue_number,
                branch=published.branch,
                title=redact_text(
                    f"Implement #{feedback_input.issue_number}: {issue['title']}",
                    self._services.sensitive_values,
                ),
                body=body,
                head_sha=published.head_sha,
            )
            if pull_request.number != feedback_input.pull_request_number or pull_request.body != body:
                return None
            self._store.update_publication(
                run_id=feedback_input.run_id,
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
        return self._store.workflow_publication(feedback_input.run_id)

    def _complete_attempt(
        self,
        *,
        attempt_id: str,
        status: str,
        invocation: dict[str, object],
        result: dict[str, object],
        head_sha: str | None = None,
        evidence: list[dict[str, object]] | None = None,
        deterministic_verification: dict[str, object] | None = None,
        review_batch_id: str | None = None,
        projected_labels: frozenset[str] = frozenset(),
        invalidation_labels: frozenset[str] = frozenset(),
    ) -> None:
        self._store.complete_feedback_attempt(
            attempt_id=attempt_id,
            status=status,
            result=result,
            head_sha=head_sha,
            evidence=evidence or [],
            deterministic_verification=deterministic_verification,
            review_batch_id=review_batch_id,
            projected_labels=projected_labels,
            invalidation_labels=invalidation_labels,
            policy=invocation["policy"],
            skills=invocation["skills"],
            access_profile=invocation["access_profile"],
            diagnostic_events=invocation["diagnostic_events"],
            completed_at=self._now(),
        )

    def _handoff(
        self, feedback_input: HumanFeedbackInput, status: str
    ) -> frozenset[str]:
        return self._adapter.project_workflow_labels(
            feedback_input.repository,
            feedback_input.issue_number,
            add=frozenset({status}),
            remove=frozenset({"agent-running", "verified", "awaiting-review"}),
        )

    @staticmethod
    def _human_findings(feedback_input: HumanFeedbackInput) -> list[dict[str, object]]:
        return [
            {
                "source": "repair",
                "axis": "repair",
                "location": f"pull-request-review:{feedback_input.source_id}",
                "description": f"Human feedback: {feedback}",
            }
            for feedback in feedback_input.feedback
        ]

    @staticmethod
    def _failure_findings(description: str) -> list[dict[str, object]]:
        return [
            {
                "source": "repair",
                "axis": "repair",
                "location": "feedback-batch",
                "description": description,
            }
        ]

    def _fresh_findings(
        self, review: dict[str, object] | None, deterministic_passed: bool
    ) -> list[dict[str, object]]:
        findings: list[dict[str, object]] = []
        if not deterministic_passed:
            findings.extend(self._failure_findings("Deterministic verification failed"))
        if review is not None:
            for result in review["results"]:
                verdict = result["verdict"]
                if verdict.get("verdict") != "fail":
                    continue
                for finding in verdict.get("findings", []):
                    findings.append(
                        {
                            "source": "review",
                            "axis": result["axis"],
                            "location": finding["location"],
                            "description": finding["description"],
                        }
                    )
        return findings or self._failure_findings("Fresh review did not pass")

    @staticmethod
    def _worktree(implementation: dict[str, object]) -> Worktree:
        record = implementation["worktree"]
        return Worktree(
            path=Path(str(record["path"])),
            branch=str(record["branch"]),
            base_ref=str(record["base_ref"]),
        )

    def _now(self) -> str:
        return self._clock().isoformat()
