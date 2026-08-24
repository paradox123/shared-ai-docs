from __future__ import annotations

import json
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from importlib.resources import as_file, files
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator
from langgraph.types import interrupt

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.evidence import redact_payload
from github_issue_pilot.github import VerificationProjectionError
from github_issue_pilot.intervention import (
    InterventionContinuationError,
    bounded_intervention_answer,
    validate_intervention_request,
)
from github_issue_pilot.policy import (
    NodePolicy,
    NodeSelection,
    PolicyViolation,
    ReviewSkillRoute,
    SkillRouter,
)

if TYPE_CHECKING:
    from github_issue_pilot.github import RepositoryAdapter
    from github_issue_pilot.implementation import Worktree
    from github_issue_pilot.storage import WorkflowStore


class InvalidReviewContract(ValueError):
    pass


class ReviewExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ReviewInvocation:
    assignment: dict[str, object]
    worktree: Worktree
    selection: NodeSelection
    route: ReviewSkillRoute
    access_profile: dict[str, object]
    intervention_answer: dict[str, str] | None = None
    intervention_context: dict[str, object] | None = None


@dataclass(frozen=True)
class ReviewOutput:
    result: dict[str, object]
    diagnostic_events: tuple[dict[str, object], ...]


class ReviewWorkerPort(Protocol):
    def run(self, invocation: ReviewInvocation) -> ReviewOutput: ...


class CodexCliReviewWorker:
    def __init__(
        self,
        *,
        skill_root: Path,
        executable: str = "codex",
        timeout_seconds: float = 3600,
    ) -> None:
        self._skill_root = skill_root
        self._executable = executable
        self._timeout_seconds = timeout_seconds

    def run(self, invocation: ReviewInvocation) -> ReviewOutput:
        validate_review_assignment(invocation.assignment)
        axis = str(invocation.assignment["axis"])
        task = {
            "requirements": "requirements_review",
            "code": "code_review",
            "architecture": "architecture_review",
        }[axis]
        expected_selection = NodePolicy.packaged().select(task)
        if invocation.selection != expected_selection:
            raise ReviewExecutionError("review policy does not match the packaged selection")
        expected_route = SkillRouter.packaged(self._skill_root).route_review(task)
        if invocation.route != expected_route:
            raise ReviewExecutionError("review skills do not match the assigned axis")
        expected_access_profile = {
            "role": "reviewer",
            "sandbox": "read-only",
            "source_root": str(invocation.worktree.path),
            "write_roots": [],
        }
        if invocation.access_profile != expected_access_profile:
            raise ReviewExecutionError("review access profile must be read-only")
        pull_request = invocation.assignment["pull_request"]
        if not isinstance(pull_request, dict):
            raise InvalidReviewContract("review assignment pull request is invalid")

        skill_instruction = " and ".join(f"${skill.name}" for skill in invocation.route.skills)
        prompt = (
            f"Use {skill_instruction} for the {invocation.route.axis} axis only. "
            "Do not start sub-agents or evaluate another review axis. "
            "Do not modify source, repair findings, merge, deploy, or synthesize a product "
            f"decision. Treat {pull_request['base_ref']} as the fixed point and verify that HEAD "
            f"is {pull_request['head_sha']} before inspecting its three-dot diff. Review only the "
            "immutable assignment below and return the schema-constrained verdict.\n"
            "<review-assignment>\n"
            f"{json.dumps(invocation.assignment, sort_keys=True)}\n"
            "</review-assignment>"
        )
        if invocation.intervention_answer is not None:
            prompt += (
                "\nUse the following bounded answer only for the previously persisted question "
                "on this axis and immutable head. It does not expose peer verdicts or authorize "
                "writes, scope changes, or workflow reconfiguration.\n"
                "<intervention-answer>\n"
                f"{json.dumps(invocation.intervention_answer, sort_keys=True)}\n"
                "</intervention-answer>"
            )
        if invocation.intervention_context is not None:
            prompt += (
                "\nIf policy requires an intervention, copy these controller-owned correlation "
                "identities exactly into the intervention request.\n"
                "<intervention-context>\n"
                f"{json.dumps(invocation.intervention_context, sort_keys=True)}\n"
                "</intervention-context>"
            )
        schema_resource = files("github_issue_pilot.contracts").joinpath(
            "review-verdict-v2.json"
        )
        with as_file(schema_resource) as schema_path, tempfile.TemporaryDirectory(
            prefix="github-issue-pilot-review-"
        ) as temporary_directory:
            result_path = Path(temporary_directory) / "review-verdict.json"
            command = [
                self._executable,
                "exec",
                "--model",
                str(invocation.selection.model),
                "-c",
                f'model_reasoning_effort="{invocation.selection.reasoning_effort}"',
                "-c",
                'approval_policy="never"',
                "--sandbox",
                invocation.selection.sandbox,
                "--cd",
                str(invocation.worktree.path),
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(result_path),
                "--json",
                "-",
            ]
            try:
                completed = subprocess.run(
                    command,
                    input=prompt,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=self._timeout_seconds,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise ReviewExecutionError(f"review process could not complete: {exc}") from exc
            if completed.returncode != 0:
                raise ReviewExecutionError(
                    f"review process exited with {completed.returncode}"
                )
            if not result_path.is_file():
                raise InvalidReviewContract("review process did not write a final verdict")
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
                if not isinstance(result, dict):
                    raise TypeError("review verdict must be a JSON object")
                diagnostic_events = tuple(
                    json.loads(line) for line in completed.stdout.splitlines() if line.strip()
                )
                if not all(isinstance(event, dict) for event in diagnostic_events):
                    raise TypeError("review JSONL diagnostics must contain objects")
            except (json.JSONDecodeError, TypeError) as exc:
                raise InvalidReviewContract(f"review returned invalid structured output: {exc}") from exc

        validate_review_result(result)
        expected_identity = (
            invocation.assignment["invocation_id"],
            axis,
            pull_request["head_sha"],
        )
        actual_identity = (result["invocation_id"], result["axis"], result["head_sha"])
        if actual_identity != expected_identity:
            raise InvalidReviewContract("review verdict does not match its assignment")
        return ReviewOutput(result=result, diagnostic_events=diagnostic_events)


def validate_review_assignment(assignment: dict[str, object]) -> None:
    try:
        Draft202012Validator(load_contract("review-assignment-v1.json")).validate(assignment)
    except ValidationError as exc:
        raise InvalidReviewContract(
            f"review assignment does not match schema: {exc.message}"
        ) from exc


def validate_review_result(result: dict[str, object]) -> None:
    schema_version = str(result.get("schema_version", ""))
    schema_name = {"1": "review-verdict-v1.json", "2": "review-verdict-v2.json"}.get(
        schema_version
    )
    if schema_name is None:
        raise InvalidReviewContract("review result uses an unsupported schema version")
    try:
        Draft202012Validator(load_contract(schema_name)).validate(result)
    except ValidationError as exc:
        raise InvalidReviewContract(f"review result does not match schema: {exc.message}") from exc
    if result["verdict"] == "fail" and not result["findings"]:
        raise InvalidReviewContract("failed review must include a finding")
    if result["axis"] == "requirements" and result["verdict"] == "not_applicable":
        raise InvalidReviewContract("requirements review must be applicable")
    intervention = result.get("intervention")
    if isinstance(intervention, dict):
        validate_intervention_request(intervention)


def build_review_assignment(
    *,
    axis: str,
    invocation_id: str,
    implementation_assignment: dict[str, object],
    implementation_result: dict[str, object],
    publication: dict[str, object],
) -> dict[str, object]:
    scope = {
        "requirements": (
            "Compare every requirement with the implementation and qualified behavioral evidence; "
            "missing or insufficient evidence is a failure."
        ),
        "code": (
            "Check repository standards and relevant code smells on the published change."
        ),
        "architecture": (
            "Check domain language, ADRs, modules, interfaces, seams, adapters, depth, and test "
            "surfaces on the published change."
        ),
    }[axis]
    pull_request = publication["pull_request"]
    if not isinstance(pull_request, dict):
        raise InvalidReviewContract("published pull request identity is missing")
    issue = implementation_assignment["issue"]
    repository_context = implementation_assignment["repository_context"]
    if not isinstance(issue, dict) or not isinstance(repository_context, dict):
        raise InvalidReviewContract("implementation assignment is incomplete")
    assignment: dict[str, object] = {
        "schema_version": "1",
        "invocation_id": invocation_id,
        "axis": axis,
        "scope": scope,
        "pull_request": {
            "number": pull_request["number"],
            "url": pull_request["url"],
            "base_ref": repository_context["base_ref"],
            "head_ref": publication["branch"],
            "head_sha": publication["head_sha"],
        },
        "requirements": implementation_assignment["requirements"],
        "implementation": {
            "summary": implementation_result["summary"],
            "changed_files": implementation_result["changed_files"],
            "verification": implementation_result["verification"],
        },
        "evidence": publication["evidence"],
        "repository_context": {"instructions": repository_context["instructions"]},
    }
    validate_review_assignment(assignment)
    return assignment


@dataclass(frozen=True)
class ReviewBatchInput:
    run_id: str
    repository: str
    issue_number: int
    implementation: dict[str, object]
    publication: dict[str, object]
    allow_verification_projection: bool = True


class ReviewCoordinator:
    """Execute and persist one independent, fail-closed review batch."""

    _AXES = (
        ("requirements", "requirements_review"),
        ("code", "code_review"),
        ("architecture", "architecture_review"),
    )

    def __init__(
        self,
        *,
        store: WorkflowStore,
        adapter: RepositoryAdapter,
        reviewer: ReviewWorkerPort,
        skill_root: Path,
        sensitive_values: tuple[str, ...],
        clock: Callable[[], datetime],
        transition_probe: Callable[[str, str], None] | None = None,
    ) -> None:
        self._store = store
        self._adapter = adapter
        self._reviewer = reviewer
        self._skill_root = skill_root
        self._sensitive_values = sensitive_values
        self._clock = clock
        self._transition_probe = transition_probe

    def execute(self, review_input: ReviewBatchInput) -> str:
        publication = review_input.publication
        pull_request = publication["pull_request"]
        if not isinstance(pull_request, dict):
            return "review_blocked"
        head_sha = str(publication["head_sha"])
        batch_id = self._store.begin_review_batch(
            run_id=review_input.run_id,
            head_sha=head_sha,
            pull_request_number=int(pull_request["number"]),
            started_at=self._clock().isoformat(),
        )
        persisted = next(
            batch
            for batch in self._store.workflow_review_history(review_input.run_id)
            if batch["id"] == batch_id
        )
        if persisted["status"] == "verified":
            return "verified"
        if persisted["status"] == "blocked":
            return "review_blocked"
        persisted_results = {
            str(record["axis"]): record["verdict"] for record in persisted["results"]
        }
        for axis in persisted_results:
            application = self._store.intervention_application_for_operation(
                f"{batch_id}:{axis}"
            )
            if application is not None and application["status"] == "applying":
                self._store.complete_intervention_application(
                    intervention_id=str(application["id"]),
                    applied_at=self._clock().isoformat(),
                )
        results: list[dict[str, object]] = list(persisted_results.values())
        failures: list[str] = []
        for axis, task in self._AXES:
            if axis in persisted_results:
                continue
            try:
                result = self._execute_axis(
                    review_input=review_input,
                    batch_id=batch_id,
                    axis=axis,
                    task=task,
                )
            except (
                InvalidReviewContract,
                KeyError,
                PolicyViolation,
                ReviewExecutionError,
                TypeError,
                ValueError,
            ):
                failures.append(axis)
                continue
            results.append(result)

        if failures:
            return self._block(batch_id, "review_execution_failed:" + ",".join(failures))
        if any(result["verdict"] == "fail" for result in results):
            return self._block(batch_id, "review_failed")
        if not review_input.allow_verification_projection:
            return self._block(batch_id, "deterministic_verification_failed")
        return self._project(review_input, batch_id, head_sha, int(pull_request["number"]))

    def _execute_axis(
        self,
        *,
        review_input: ReviewBatchInput,
        batch_id: str,
        axis: str,
        task: str,
    ) -> dict[str, object]:
        from github_issue_pilot.implementation import Worktree

        implementation = review_input.implementation
        selection = NodePolicy.packaged().select(task)
        route = SkillRouter.packaged(self._skill_root).route_review(task)
        invocation_id = f"{batch_id}:{axis}"
        assignment = build_review_assignment(
            axis=axis,
            invocation_id=invocation_id,
            implementation_assignment=implementation["assignment"],
            implementation_result=implementation["result"],
            publication=review_input.publication,
        )
        worktree_record = implementation["worktree"]
        access_profile: dict[str, object] = {
            "role": "reviewer",
            "sandbox": "read-only",
            "source_root": worktree_record["path"],
            "write_roots": [],
        }
        application = self._store.intervention_application_for_operation(invocation_id)
        intervention_answer: dict[str, str] | None = None
        if application is not None and application["status"] != "applied":
            resumed = interrupt(
                {
                    "intervention_id": application["id"],
                    "phase": "review",
                    "operation_key": invocation_id,
                }
            )
            intervention_answer = bounded_intervention_answer(
                application, resumed, phase="review"
            )
            if application["status"] == "answered" and not self._store.claim_intervention_application(
                str(application["id"])
            ):
                raise ReviewExecutionError("review intervention answer could not be claimed")
        try:
            output = self._reviewer.run(
                ReviewInvocation(
                assignment=assignment,
                worktree=Worktree(
                    path=Path(worktree_record["path"]),
                    branch=worktree_record["branch"],
                    base_ref=worktree_record["base_ref"],
                ),
                selection=selection,
                route=route,
                access_profile=access_profile,
                intervention_answer=intervention_answer,
                intervention_context={
                    "repository": {
                        "full_name": review_input.repository,
                        "issue_number": review_input.issue_number,
                    },
                    "run": {
                        "id": review_input.run_id,
                        "phase": "review",
                        "operation_key": invocation_id,
                    },
                    "role": f"{axis}_reviewer",
                    "context": {
                        "worktree_path": worktree_record["path"],
                        "branch": worktree_record["branch"],
                        "pull_request_number": review_input.publication["pull_request"]["number"],
                        "head_sha": review_input.publication["head_sha"],
                    },
                },
                )
            )
        except (ReviewExecutionError, TypeError, ValueError) as exc:
            if intervention_answer is not None:
                raise InterventionContinuationError(
                    "review continuation worker did not complete"
                ) from exc
            raise
        result = redact_payload(output.result, self._sensitive_values)
        diagnostics = redact_payload(list(output.diagnostic_events), self._sensitive_values)
        if not isinstance(result, dict) or not isinstance(diagnostics, list):
            raise InvalidReviewContract("review redaction changed the output shape")
        validate_review_result(result)
        expected_identity = (
            invocation_id,
            axis,
            review_input.publication["head_sha"],
        )
        actual_identity = (result["invocation_id"], result["axis"], result["head_sha"])
        if actual_identity != expected_identity:
            raise InvalidReviewContract("review verdict does not match its assignment")
        intervention_request = result.get("intervention")
        if isinstance(intervention_request, dict):
            if intervention_answer is not None:
                raise InvalidReviewContract("review continuation requested another intervention")
            self._validate_intervention_identity(
                review_input=review_input,
                invocation_id=invocation_id,
                axis=axis,
                request=intervention_request,
            )
            intervention_id = self._store.begin_intervention(
                run_id=review_input.run_id,
                phase="review",
                role=f"{axis}_reviewer",
                operation_key=invocation_id,
                request=intervention_request,
                source_result=result,
                created_at=self._clock().isoformat(),
            )
            interrupt(
                {
                    "intervention_id": intervention_id,
                    "phase": "review",
                    "operation_key": invocation_id,
                }
            )
        self._store.record_review_result(
            batch_id=batch_id,
            axis=axis,
            assignment=assignment,
            result=result,
            policy={
                "version": selection.policy_version,
                "task": selection.task,
                "model": selection.model,
                "reasoning_effort": selection.reasoning_effort,
                "sandbox": selection.sandbox,
            },
            route_axis=route.axis,
            skills=[
                {"name": skill.name, "content_sha256": skill.content_sha256}
                for skill in route.skills
            ],
            access_profile=access_profile,
            diagnostic_events=diagnostics,
            completed_at=self._clock().isoformat(),
        )
        if intervention_answer is not None:
            self._store.complete_intervention_application(
                intervention_id=intervention_answer["intervention_id"],
                applied_at=self._clock().isoformat(),
            )
        if self._transition_probe is not None:
            self._transition_probe(f"review_{axis}_completed", invocation_id)
        return result

    @staticmethod
    def _validate_intervention_identity(
        *,
        review_input: ReviewBatchInput,
        invocation_id: str,
        axis: str,
        request: dict[str, object],
    ) -> None:
        run = request.get("run")
        repository = request.get("repository")
        context = request.get("context")
        pull_request = review_input.publication.get("pull_request")
        worktree = review_input.implementation.get("worktree")
        if not all(
            isinstance(value, dict)
            for value in (run, repository, context, pull_request, worktree)
        ):
            raise InvalidReviewContract("review intervention identity is malformed")
        expected = (
            review_input.run_id,
            "review",
            invocation_id,
            review_input.repository,
            review_input.issue_number,
            f"{axis}_reviewer",
            worktree["path"],
            worktree["branch"],
            pull_request["number"],
            review_input.publication["head_sha"],
        )
        actual = (
            run.get("id"),
            run.get("phase"),
            run.get("operation_key"),
            repository.get("full_name"),
            repository.get("issue_number"),
            request.get("role"),
            context.get("worktree_path"),
            context.get("branch"),
            context.get("pull_request_number"),
            context.get("head_sha"),
        )
        if actual != expected:
            raise InvalidReviewContract("review intervention does not match its operation")

    def _project(
        self,
        review_input: ReviewBatchInput,
        batch_id: str,
        head_sha: str,
        pull_request_number: int,
    ) -> str:
        try:
            current_head = self._adapter.current_pull_request_head(
                review_input.repository, pull_request_number
            )
            if current_head != head_sha:
                return self._block(batch_id, "head_changed")
            projected = self._adapter.project_workflow_labels(
                review_input.repository,
                review_input.issue_number,
                add=frozenset({"verified", "awaiting-review"}),
                remove=frozenset({self._adapter.running_label}),
            )
        except (OSError, RuntimeError, TypeError, ValueError, VerificationProjectionError):
            return self._block(batch_id, "verification_projection_failed")
        self._store.complete_review_batch(
            batch_id=batch_id,
            projected_labels=projected,
            completed_at=self._clock().isoformat(),
        )
        return "verified"

    def _block(self, batch_id: str, reason: str) -> str:
        self._store.block_review_batch(
            batch_id=batch_id,
            reason=reason,
            completed_at=self._clock().isoformat(),
        )
        return "review_blocked"
