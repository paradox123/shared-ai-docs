from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.implementation import (
    CodexCliWorker,
    InvalidWorkerResult,
    WorkerExecutionError,
    WorkerInvocation,
    Worktree,
    validate_worker_result,
)
from github_issue_pilot.policy import NodePolicy, SkillRouter

SKILL_ROOT = (
    Path(__file__).resolve().parents[2] / "skills-repo" / "vendor" / "mattpocock" / ".agents" / "skills"
)


def valid_assignment() -> dict[str, object]:
    return {
        "schema_version": "1",
        "issue": {
            "repository": "daniel/probare-crm",
            "number": 41,
            "title": "Add customer export",
            "body": "- [ ] Customer can export CSV",
            "type": "feature",
        },
        "requirements": ["Customer can export CSV"],
        "repository_context": {"base_ref": "main", "instructions": "Follow AGENTS.md."},
        "evidence_matrix": [
            {
                "criterion": "Customer can export CSV",
                "public_observation_surface": "HTTP API",
                "expected_result": "CSV is returned",
                "planned_proof": "Failing then passing HTTP behavior test",
            }
        ],
        "findings": [],
    }


def valid_result() -> dict[str, object]:
    return {
        "schema_version": "2",
        "outcome": "completed",
        "summary": "Implemented export",
        "red_green_slices": [
            {
                "requirement": "Customer can export CSV",
                "red": {"command": "pytest export", "observed": "failed: missing"},
                "green": {"command": "pytest export", "observed": "passed"},
            }
        ],
        "changed_files": ["src/export.py"],
        "verification": [{"command": "pytest", "observed": "passed"}],
        "evidence": [
            {
                "criterion": "Customer can export CSV",
                "verdict": "pass",
                "kind": "rest",
                "observed_interface": "HTTP API",
                "expected_result": "CSV is returned",
                "observations": [
                    {
                        "phase": "request",
                        "description": "Requested export",
                        "artifact": "POST /exports",
                        "correlation_id": None,
                    },
                    {
                        "phase": "response",
                        "description": "Export resource created",
                        "artifact": "201 export_id=41",
                        "correlation_id": None,
                    },
                    {
                        "phase": "read_back",
                        "description": "CSV contains customer row",
                        "artifact": "GET /exports/41 -> customer_id",
                        "correlation_id": None,
                    },
                ],
            }
        ],
        "findings": [],
    }


def test_codex_cli_adapter_runs_non_interactively_with_assignment_policy_skills_and_schema(tmp_path) -> None:
    executable = tmp_path / "fake-codex"
    args_capture = tmp_path / "fake-codex.args.json"
    stdin_capture = tmp_path / "fake-codex.stdin.txt"
    executable.write_text(
        """#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
base = pathlib.Path(__file__).with_name("fake-codex")
base.with_suffix(".args.json").write_text(json.dumps(args), encoding="utf-8")
base.with_suffix(".stdin.txt").write_text(sys.stdin.read(), encoding="utf-8")
output = pathlib.Path(args[args.index("--output-last-message") + 1])
output.write_text('''RESULT_JSON''', encoding="utf-8")
print(json.dumps({"type": "thread.started", "thread_id": "thread-001"}))
print(json.dumps({"type": "turn.completed"}))
""".replace("RESULT_JSON", json.dumps(valid_result())),
        encoding="utf-8",
    )
    os.chmod(executable, 0o755)
    worktree = tmp_path / "worker-worktree"
    worktree.mkdir()
    selection = NodePolicy.packaged().select("implementation")
    skills = SkillRouter.packaged(SKILL_ROOT).route("implementation", issue_type="feature")
    access_profile = {
        "role": "implementer",
        "sandbox": "workspace-write",
        "write_root": str(worktree),
        "additional_write_roots": [],
    }

    output = CodexCliWorker(executable=str(executable)).run(
        WorkerInvocation(
            assignment=valid_assignment(),
            worktree=Worktree(path=worktree, branch="codex/run-001", base_ref="main"),
            selection=selection,
            skills=skills,
            access_profile=access_profile,
        )
    )

    args = json.loads(args_capture.read_text(encoding="utf-8"))
    prompt = stdin_capture.read_text(encoding="utf-8")
    assert args[0] == "exec"
    assert args[args.index("--model") + 1] == "gpt-5.6-terra"
    assert 'model_reasoning_effort="xhigh"' in args
    assert 'approval_policy="never"' in args
    assert args[args.index("--sandbox") + 1] == "workspace-write"
    assert args[args.index("--cd") + 1] == str(worktree)
    assert Path(args[args.index("--output-schema") + 1]).name == "worker-result-v3.json"
    assert "--json" in args
    assert args[-1] == "-"
    assert "$implement" in prompt and "$tdd" in prompt
    assert "Every evidence observation must embed a non-empty artifact" in prompt
    assert json.dumps(valid_assignment(), sort_keys=True) in prompt
    assert "app-server" not in prompt and "exec-server" not in prompt
    assert output.result == valid_result()
    assert output.diagnostic_events == (
        {"type": "thread.started", "thread_id": "thread-001"},
        {"type": "turn.completed"},
    )


def test_worker_result_schema_rejects_a_completed_result_without_red_green_evidence() -> None:
    result = valid_result()
    result["red_green_slices"] = []

    with pytest.raises(InvalidWorkerResult, match="worker result does not match schema"):
        validate_worker_result(result)


def test_worker_output_schema_requires_every_object_property_for_codex_strict_mode() -> None:
    schema = load_contract("worker-result-v2.json")

    def assert_strict_objects(value: object) -> None:
        if isinstance(value, dict):
            if value.get("type") == "object":
                assert set(value.get("properties", {})) == set(value.get("required", []))
                assert value.get("additionalProperties") is False
            if "enum" in value or "const" in value:
                assert "type" in value
            for nested in value.values():
                assert_strict_objects(nested)
        elif isinstance(value, list):
            for nested in value:
                assert_strict_objects(nested)

    assert_strict_objects(schema)


def test_worker_output_schema_requires_an_embedded_artifact_for_every_observation() -> None:
    schema = load_contract("worker-result-v2.json")
    artifact = schema["$defs"]["evidence_observation"]["properties"]["artifact"]

    assert artifact == {"type": "string", "minLength": 1}


def test_codex_cli_adapter_rejects_a_write_profile_outside_the_assigned_worktree(tmp_path) -> None:
    worktree = tmp_path / "worker-worktree"
    worktree.mkdir()
    selection = NodePolicy.packaged().select("implementation")

    with pytest.raises(WorkerExecutionError, match="access profile does not match"):
        CodexCliWorker(executable="unused-because-policy-must-fail-first").run(
            WorkerInvocation(
                assignment=valid_assignment(),
                worktree=Worktree(path=worktree, branch="codex/run-001", base_ref="main"),
                selection=selection,
                skills=SkillRouter.packaged(SKILL_ROOT).route(
                    "implementation", issue_type="feature"
                ),
                access_profile={
                    "role": "implementer",
                    "sandbox": "workspace-write",
                    "write_root": str(tmp_path / "other-worktree"),
                    "additional_write_roots": [],
                },
            )
        )
