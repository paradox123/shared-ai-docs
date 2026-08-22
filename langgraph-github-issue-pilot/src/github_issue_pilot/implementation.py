from __future__ import annotations

import json
import re
import subprocess
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.resources import as_file, files
from pathlib import Path
from typing import Protocol

from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.github import IssueState
from github_issue_pilot.policy import NodeSelection, SkillProvenance

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


@dataclass(frozen=True)
class WorkerOutput:
    result: dict[str, object]
    diagnostic_events: tuple[dict[str, object], ...]


class WorkerExecutionError(RuntimeError):
    pass


class InvalidWorkerResult(WorkerExecutionError):
    pass


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
        target = self._worktree_root / repository_segment / run_id
        if target.exists():
            raise FileExistsError(f"worktree path already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                self._git_executable,
                "-C",
                str(repository_root),
                "worktree",
                "add",
                "-b",
                branch,
                str(target),
                base_ref,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return Worktree(path=target, branch=branch, base_ref=base_ref)


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
            "Red-Green slices. Return the schema-constrained result and do not expand scope.\n"
            "<implementation-assignment>\n"
            f"{json.dumps(invocation.assignment, sort_keys=True)}\n"
            "</implementation-assignment>"
        )
        schema_resource = files("github_issue_pilot.contracts").joinpath("worker-result-v1.json")
        with as_file(schema_resource) as schema_path, tempfile.TemporaryDirectory(
            prefix="github-issue-pilot-worker-"
        ) as temporary_directory:
            result_path = Path(temporary_directory) / "worker-result.json"
            command = [
                self._executable,
                "exec",
                "--model",
                invocation.selection.model,
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
                raise WorkerExecutionError(f"Codex process could not complete: {exc}") from exc
            if completed.returncode != 0:
                detail = completed.stderr.strip()[-2000:] or "no diagnostic stderr"
                raise WorkerExecutionError(
                    f"Codex process exited with {completed.returncode}: {detail}"
                )
            if not result_path.is_file():
                raise InvalidWorkerResult("Codex process did not write a final result")
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
                if not isinstance(result, dict):
                    raise TypeError("worker result must be a JSON object")
                diagnostic_events = tuple(
                    json.loads(line) for line in completed.stdout.splitlines() if line.strip()
                )
                if not all(isinstance(event, dict) for event in diagnostic_events):
                    raise TypeError("JSONL diagnostics must contain objects")
            except (json.JSONDecodeError, TypeError) as exc:
                raise InvalidWorkerResult(f"Codex returned invalid structured output: {exc}") from exc
            validate_worker_result(result)
            return WorkerOutput(result=result, diagnostic_events=diagnostic_events)


def validate_worker_result(result: dict[str, object]) -> None:
    try:
        Draft202012Validator(load_contract("worker-result-v1.json")).validate(result)
    except ValidationError as exc:
        raise InvalidWorkerResult(f"worker result does not match schema: {exc.message}") from exc


@dataclass(frozen=True)
class ImplementationServices:
    repository_roots: Mapping[str, Path]
    repository_contexts: Mapping[str, RepositoryContext]
    skill_root: Path
    worktrees: WorktreePort
    worker: WorkerPort


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
