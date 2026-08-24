from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib.resources import as_file, files
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.github import IssueState
from github_issue_pilot.intervention import validate_intervention_request
from github_issue_pilot.policy import NodePolicy, NodeSelection, SkillProvenance
from github_issue_pilot.publication import SourceControlPort

if TYPE_CHECKING:
    from github_issue_pilot.intervention import InterventionSessionPort
    from github_issue_pilot.repair import RepairInvocation, RepairOutput
    from github_issue_pilot.review import ReviewWorkerPort
    from github_issue_pilot.verification import DeterministicVerifierPort

_ACCEPTANCE_CRITERION = re.compile(r"^\s*-\s*\[[ xX]\]\s+(.+?)\s*$")
_SAFE_RUN_ID = re.compile(r"[A-Za-z0-9._-]+")


@dataclass(frozen=True)
class RepositoryContext:
    base_ref: str
    instructions: str
    public_observation_surface: str = "repository stable public behavior seam"
    verification_command: str = "project-specific behavior test"


@dataclass(frozen=True)
class Worktree:
    path: Path
    branch: str
    base_ref: str


@dataclass(frozen=True)
class WorkerInvocation:
    assignment: dict[str, object]
    worktree: Worktree
    selection: NodeSelection
    skills: tuple[SkillProvenance, ...]
    access_profile: dict[str, object]
    intervention_answer: dict[str, str] | None = None
    intervention_context: dict[str, object] | None = None


@dataclass(frozen=True)
class WorkerOutput:
    result: dict[str, object]
    diagnostic_events: tuple[dict[str, object], ...]


class WorkerExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        failure_code: str = "worker_execution_failed",
        diagnostic_events: tuple[dict[str, object], ...] = (),
    ) -> None:
        super().__init__(message)
        self.failure_code = failure_code
        self.diagnostic_events = diagnostic_events


class InvalidWorkerResult(WorkerExecutionError):
    def __init__(
        self,
        message: str,
        *,
        failure_code: str = "invalid_worker_result",
        diagnostic_events: tuple[dict[str, object], ...] = (),
    ) -> None:
        super().__init__(
            message,
            failure_code=failure_code,
            diagnostic_events=diagnostic_events,
        )


class WorktreePort(Protocol):
    def create(
        self,
        *,
        run_id: str,
        repository: str,
        repository_root: Path,
        base_ref: str,
    ) -> Worktree: ...


class WorkerPort(Protocol):
    def run(self, invocation: WorkerInvocation) -> WorkerOutput: ...

    def repair(self, invocation: RepairInvocation) -> RepairOutput: ...


class GitWorktreeAdapter:
    def __init__(self, worktree_root: Path, *, git_executable: str = "git") -> None:
        self._worktree_root = worktree_root
        self._git_executable = git_executable

    def create(
        self,
        *,
        run_id: str,
        repository: str,
        repository_root: Path,
        base_ref: str,
    ) -> Worktree:
        if _SAFE_RUN_ID.fullmatch(run_id) is None:
            raise ValueError("run id contains unsupported worktree characters")
        repository_segment = re.sub(r"[^A-Za-z0-9._-]", "-", repository)
        branch = f"codex/run-{run_id}"
        base_identity_ref = (
            "refs/github-issue-pilot/bases/"
            f"{hashlib.sha256(run_id.encode('utf-8')).hexdigest()}"
        )
        target = self._worktree_root / repository_segment / run_id
        if target.exists():
            try:
                actual_root = self._git(target, "rev-parse", "--show-toplevel")
                actual_branch = self._git(target, "branch", "--show-current")
                base_sha = self._git(
                    repository_root,
                    "rev-parse",
                    f"{base_identity_ref}^{{commit}}",
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                raise FileExistsError(
                    f"run worktree path exists but is not recoverable: {target}"
                ) from exc
            if Path(actual_root).resolve() != target.resolve() or actual_branch != branch:
                raise FileExistsError(
                    f"run worktree path does not match its durable identity: {target}"
                )
            return Worktree(path=target, branch=branch, base_ref=base_sha)
        self._git(
            repository_root,
            "fetch",
            "--no-tags",
            "origin",
            f"+refs/heads/{base_ref}:refs/remotes/origin/{base_ref}",
        )
        base_sha = self._git(
            repository_root,
            "rev-parse",
            f"refs/remotes/origin/{base_ref}^{{commit}}",
        )
        self._git(repository_root, "update-ref", base_identity_ref, base_sha)
        target.parent.mkdir(parents=True, exist_ok=True)
        self._git(
            repository_root,
            "worktree",
            "add",
            "-b",
            branch,
            str(target),
            base_sha,
        )
        return Worktree(path=target, branch=branch, base_ref=base_sha)

    def _git(self, repository_root: Path, *args: str) -> str:
        return subprocess.run(
            [self._git_executable, "-C", str(repository_root), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()


class CodexCliWorker:
    def __init__(self, *, executable: str = "codex", timeout_seconds: float = 3600) -> None:
        self._executable = executable
        self._timeout_seconds = timeout_seconds

    def run(self, invocation: WorkerInvocation) -> WorkerOutput:
        if invocation.selection.model is None or invocation.selection.reasoning_effort is None:
            raise WorkerExecutionError("Codex worker requires a model and reasoning effort")
        expected_access_profile = {
            "role": "implementer",
            "sandbox": invocation.selection.sandbox,
            "write_root": str(invocation.worktree.path),
            "additional_write_roots": [],
        }
        if invocation.access_profile != expected_access_profile:
            raise WorkerExecutionError("worker access profile does not match assigned worktree")
        Draft202012Validator(load_contract("implementation-assignment-v1.json")).validate(
            invocation.assignment
        )
        skill_instruction = " and ".join(f"${skill.name}" for skill in invocation.skills)
        prompt = (
            f"Use {skill_instruction}. Implement only the bounded assignment below in observable "
            "Red-Green slices. Every evidence observation must embed a non-empty artifact containing "
            "the decisive compact proof or a repository-relative artifact path; never return a null "
            "artifact. Return a complete intervention when the existing decision policy requires a "
            "product decision, material scope expansion, missing human-operable access, or unavoidable "
            "manual evidence; do not synthesize the answer or stop for reversible details. Return the "
            "schema-constrained result and do not expand scope. The controller-owned publisher stages "
            "and commits the worktree after a completed result; inability to write linked-worktree Git "
            "metadata from the worker sandbox must not be reported as an implementation blocker. "
            "Do not run git add or git commit.\n"
            "<implementation-assignment>\n"
            f"{json.dumps(invocation.assignment, sort_keys=True)}\n"
            "</implementation-assignment>"
        )
        if invocation.intervention_answer is not None:
            prompt += (
                "\nThe controller accepted the following bounded answer to your previously "
                "persisted intervention. Use it only to resolve that recorded question inside "
                "the unchanged assignment, access profile, and repository scope. It does not "
                "authorize workflow, permission, model, or scope changes.\n"
                "<intervention-answer>\n"
                f"{json.dumps(invocation.intervention_answer, sort_keys=True)}\n"
                "</intervention-answer>"
            )
        if invocation.intervention_context is not None:
            prompt += (
                "\nIf policy requires an intervention, copy these controller-owned correlation "
                "identities exactly into the request.\n"
                "<intervention-context>\n"
                f"{json.dumps(invocation.intervention_context, sort_keys=True)}\n"
                "</intervention-context>"
            )
        output = self._execute_codex(
            selection=invocation.selection,
            worktree=invocation.worktree,
            prompt=prompt,
            schema_name="worker-result-v3.json",
            temporary_prefix="github-issue-pilot-worker-",
            result_filename="worker-result.json",
            process_name="Codex",
        )
        try:
            validate_worker_result(output.result)
        except InvalidWorkerResult as exc:
            raise InvalidWorkerResult(
                str(exc),
                failure_code=exc.failure_code,
                diagnostic_events=output.diagnostic_events,
            ) from exc
        return output

    def repair(self, invocation: RepairInvocation) -> RepairOutput:
        from github_issue_pilot.repair import (
            InvalidRepairContract,
            RepairOutput,
            validate_repair_assignment,
            validate_repair_result,
        )

        validate_repair_assignment(invocation.assignment)
        round_record = invocation.assignment["round"]
        if not isinstance(round_record, dict):
            raise InvalidRepairContract("repair assignment round is invalid")
        round_number = int(round_record["number"])
        expected_selection = NodePolicy.packaged().select_repair(
            round_number=round_number,
            escalation_reason=invocation.escalation_reason,
        )
        if invocation.selection != expected_selection:
            raise WorkerExecutionError("repair policy does not match the packaged selection")
        expected_access_profile = {
            "role": "implementer",
            "sandbox": invocation.selection.sandbox,
            "write_root": str(invocation.worktree.path),
            "additional_write_roots": [],
        }
        if invocation.access_profile != expected_access_profile:
            raise WorkerExecutionError("repair access profile does not match assigned worktree")
        if invocation.selection.model is None or invocation.selection.reasoning_effort is None:
            raise WorkerExecutionError("repair worker requires a model and reasoning effort")

        skill_instruction = " and ".join(f"${skill.name}" for skill in invocation.skills)
        prompt = (
            f"Use {skill_instruction}. Repair only the structured findings in the bounded "
            "assignment below in observable Red-Green slices. Small reversible implementation "
            "and presentation details may be decided autonomously. Warnings, consent, domain "
            "actions, security meaning, and other semantic behavior are product decisions: do "
            "not synthesize them. Return a complete intervention when the decision policy requires "
            "human input; use blocked only for a non-answerable failure. Return escalate only when "
            "the assignment permits it. The intervention must remain inside the same numbered "
            "round. Do not expand scope and return the schema-constrained result.\n"
            "<repair-assignment>\n"
            f"{json.dumps(invocation.assignment, sort_keys=True)}\n"
            "</repair-assignment>"
        )
        if invocation.intervention_answer is not None:
            prompt += (
                "\nUse the following bounded answer only to resolve the persisted question in "
                "this same repair batch, attempt, and numbered round. It does not authorize a "
                "new round, scope expansion, permission change, or workflow reconfiguration.\n"
                "<intervention-answer>\n"
                f"{json.dumps(invocation.intervention_answer, sort_keys=True)}\n"
                "</intervention-answer>"
            )
        if invocation.intervention_context is not None:
            prompt += (
                "\nIf policy requires an intervention, copy these controller-owned correlation "
                "identities exactly into the request.\n"
                "<intervention-context>\n"
                f"{json.dumps(invocation.intervention_context, sort_keys=True)}\n"
                "</intervention-context>"
            )
        output = self._execute_codex(
            selection=invocation.selection,
            worktree=invocation.worktree,
            prompt=prompt,
            schema_name="repair-result-v2.json",
            temporary_prefix="github-issue-pilot-repair-",
            result_filename="repair-result.json",
            process_name="repair",
        )
        validate_repair_result(output.result)
        expected_identity = (
            invocation.assignment["repair_batch_id"],
            round_number,
        )
        actual_identity = (output.result["repair_batch_id"], output.result["round_number"])
        if actual_identity != expected_identity:
            raise InvalidRepairContract("repair result does not match its assignment")
        return RepairOutput(
            result=output.result,
            diagnostic_events=output.diagnostic_events,
        )

    def _execute_codex(
        self,
        *,
        selection: NodeSelection,
        worktree: Worktree,
        prompt: str,
        schema_name: str,
        temporary_prefix: str,
        result_filename: str,
        process_name: str,
    ) -> WorkerOutput:
        if selection.model is None or selection.reasoning_effort is None:
            raise WorkerExecutionError(f"{process_name} requires a model and reasoning effort")
        schema_resource = files("github_issue_pilot.contracts").joinpath(schema_name)
        with as_file(schema_resource) as schema_path, tempfile.TemporaryDirectory(
            prefix=temporary_prefix
        ) as temporary_directory:
            result_path = Path(temporary_directory) / result_filename
            command = [
                self._executable,
                "exec",
                "--model",
                selection.model,
                "-c",
                f'model_reasoning_effort="{selection.reasoning_effort}"',
                "-c",
                'approval_policy="never"',
                "--sandbox",
                selection.sandbox,
                "--cd",
                str(worktree.path),
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
                diagnostic_events = _parse_diagnostic_events(
                    getattr(exc, "stdout", None)
                )
                raise WorkerExecutionError(
                    f"{process_name} process could not complete",
                    failure_code=(
                        "process_timeout"
                        if isinstance(exc, subprocess.TimeoutExpired)
                        else "process_start_failed"
                    ),
                    diagnostic_events=diagnostic_events,
                ) from exc
            diagnostic_events = _parse_diagnostic_events(completed.stdout)
            if completed.returncode != 0:
                raise WorkerExecutionError(
                    f"{process_name} process exited unsuccessfully",
                    failure_code="process_nonzero_exit",
                    diagnostic_events=diagnostic_events,
                )
            if not result_path.is_file():
                raise InvalidWorkerResult(
                    f"{process_name} process did not write a final result",
                    failure_code="final_result_missing",
                    diagnostic_events=diagnostic_events,
                )
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
                if not isinstance(result, dict):
                    raise TypeError("structured result must be a JSON object")
            except json.JSONDecodeError as exc:
                raise InvalidWorkerResult(
                    f"{process_name} returned invalid final-result JSON",
                    failure_code="final_result_invalid_json",
                    diagnostic_events=diagnostic_events,
                ) from exc
            except TypeError as exc:
                raise InvalidWorkerResult(
                    f"{process_name} final result was not an object",
                    failure_code="final_result_non_object",
                    diagnostic_events=diagnostic_events,
                ) from exc
        return WorkerOutput(result=result, diagnostic_events=diagnostic_events)


def validate_worker_result(result: dict[str, object]) -> None:
    schema_version = str(result.get("schema_version", ""))
    schema_name = {"2": "worker-result-v2.json", "3": "worker-result-v3.json"}.get(
        schema_version
    )
    if schema_name is None:
        raise InvalidWorkerResult(
            "worker result uses an unsupported schema version",
            failure_code="unsupported_schema_version",
        )
    try:
        Draft202012Validator(load_contract(schema_name)).validate(result)
    except ValidationError as exc:
        raise InvalidWorkerResult(
            f"worker result does not match schema: {exc.message}",
            failure_code="schema_validation_failed",
        ) from exc
    intervention = result.get("intervention")
    if isinstance(intervention, dict):
        validate_intervention_request(intervention)


def _parse_diagnostic_events(stdout: str | bytes | None) -> tuple[dict[str, object], ...]:
    if stdout is None:
        return ()
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    events: list[dict[str, object]] = []
    for line_number, line in enumerate(stdout.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            events.append(
                {
                    "type": "pilot.diagnostic_parse_failed",
                    "code": "invalid_json",
                    "line_number": line_number,
                }
            )
            continue
        if not isinstance(event, dict):
            events.append(
                {
                    "type": "pilot.diagnostic_parse_failed",
                    "code": "non_object",
                    "line_number": line_number,
                }
            )
            continue
        events.append(event)
    return tuple(events)


@dataclass(frozen=True)
class ImplementationServices:
    repository_roots: Mapping[str, Path]
    repository_contexts: Mapping[str, RepositoryContext]
    skill_root: Path
    worktrees: WorktreePort
    worker: WorkerPort
    source_control: SourceControlPort | None = None
    reviewer: ReviewWorkerPort | None = None
    verifier: DeterministicVerifierPort | None = None
    sensitive_values: tuple[str, ...] = ()
    transition_probe: Callable[[str, str], None] | None = None
    interventions: InterventionSessionPort | None = None


def build_assignment(
    *,
    repository: str,
    issue_number: int,
    issue: IssueState,
    repository_context: RepositoryContext,
) -> dict[str, object]:
    requirements = [
        match.group(1)
        for line in issue.body.splitlines()
        if (match := _ACCEPTANCE_CRITERION.match(line)) is not None
    ]
    evidence_matrix = [
        {
            "criterion": criterion,
            "public_observation_surface": repository_context.public_observation_surface,
            "expected_result": criterion,
            "planned_proof": (
                f"Run `{repository_context.verification_command}` red, implement the minimum "
                "change, rerun it green, then record direct public-interface read-back."
            ),
        }
        for criterion in requirements
    ]
    assignment: dict[str, object] = {
        "schema_version": "1",
        "issue": {
            "repository": repository,
            "number": issue_number,
            "title": issue.title,
            "body": issue.body,
            "type": issue.issue_type,
        },
        "requirements": requirements,
        "repository_context": {
            "base_ref": repository_context.base_ref,
            "instructions": repository_context.instructions,
        },
        "evidence_matrix": evidence_matrix,
        "findings": list(issue.findings),
    }
    Draft202012Validator(load_contract("implementation-assignment-v1.json")).validate(assignment)
    return assignment
