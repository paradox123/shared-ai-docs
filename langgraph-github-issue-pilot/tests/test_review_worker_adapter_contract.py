from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.implementation import Worktree
from github_issue_pilot.policy import (
    NodePolicy,
    NodeSelection,
    ReviewSkillRoute,
    SkillProvenance,
    SkillRouter,
)
from github_issue_pilot.review import (
    CodexCliReviewWorker,
    InvalidReviewContract,
    ReviewExecutionError,
    ReviewInvocation,
)

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"
SKILL_ROOT = (
    Path(__file__).resolve().parents[2] / "skills-repo" / "vendor" / "mattpocock" / ".agents" / "skills"
)
TASKS = {
    "requirements": "requirements_review",
    "code": "code_review",
    "architecture": "architecture_review",
}


def test_review_output_schema_is_accepted_by_codex_strict_mode() -> None:
    schema = load_contract("review-verdict-v1.json")

    def assert_strict_objects(value: object) -> None:
        if isinstance(value, dict):
            assert "allOf" not in value
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


def review_assignment(axis: str) -> dict[str, object]:
    return {
        "schema_version": "1",
        "invocation_id": f"review-{axis}-001",
        "axis": axis,
        "scope": f"Review only the {axis} axis",
        "pull_request": {
            "number": 77,
            "url": "https://github.example/daniel/probare-crm/pull/77",
            "base_ref": "main",
            "head_ref": "codex/run-run-001",
            "head_sha": HEAD_SHA,
        },
        "requirements": ["Customer can export CSV"],
        "implementation": {
            "summary": "Implemented customer export",
            "changed_files": ["src/export.py"],
            "verification": [{"command": "pytest", "observed": "passed"}],
        },
        "evidence": [{"criterion": "Customer can export CSV", "verdict": "pass"}],
        "repository_context": {"instructions": "Follow AGENTS.md."},
    }


def test_codex_review_adapter_starts_three_fresh_read_only_axis_specific_invocations(
    tmp_path,
) -> None:
    executable = tmp_path / "fake-codex"
    executable.write_text(
        """#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
prompt = sys.stdin.read()
assignment = json.loads(prompt.split("<review-assignment>\\n", 1)[1].split("\\n</review-assignment>", 1)[0])
capture = pathlib.Path(__file__).with_suffix(".calls.jsonl")
with capture.open("a", encoding="utf-8") as stream:
    stream.write(json.dumps({"args": args, "prompt": prompt}) + "\\n")
result = {
    "schema_version": "1",
    "invocation_id": assignment["invocation_id"],
    "axis": assignment["axis"],
    "head_sha": assignment["pull_request"]["head_sha"],
    "verdict": "pass",
    "rationale": "The assigned axis passed.",
    "findings": [],
}
output = pathlib.Path(args[args.index("--output-last-message") + 1])
output.write_text(json.dumps(result), encoding="utf-8")
print(json.dumps({"type": "thread.started", "thread_id": "fresh-" + assignment["axis"]}))
print(json.dumps({"type": "turn.completed"}))
""",
        encoding="utf-8",
    )
    os.chmod(executable, 0o755)
    worktree_path = tmp_path / "review-worktree"
    worktree_path.mkdir()
    worker = CodexCliReviewWorker(executable=str(executable), skill_root=SKILL_ROOT)

    outputs = []
    for axis, task in TASKS.items():
        selection = NodePolicy.packaged().select(task)
        outputs.append(
            worker.run(
                ReviewInvocation(
                    assignment=review_assignment(axis),
                    worktree=Worktree(
                        path=worktree_path,
                        branch="codex/run-run-001",
                        base_ref="main",
                    ),
                    selection=selection,
                    route=SkillRouter.packaged(SKILL_ROOT).route_review(task),
                    access_profile={
                        "role": "reviewer",
                        "sandbox": "read-only",
                        "source_root": str(worktree_path),
                        "write_roots": [],
                    },
                )
            )
        )

    calls = [
        json.loads(line)
        for line in executable.with_suffix(".calls.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(calls) == 3
    assert [output.result["axis"] for output in outputs] == list(TASKS)
    assert {output.result["head_sha"] for output in outputs} == {HEAD_SHA}
    assert [event[0]["thread_id"] for event in [output.diagnostic_events for output in outputs]] == [
        "fresh-requirements",
        "fresh-code",
        "fresh-architecture",
    ]
    for axis, call in zip(TASKS, calls, strict=True):
        args = call["args"]
        prompt = call["prompt"]
        assert args[0] == "exec"
        assert args[args.index("--model") + 1] == "gpt-5.6-terra"
        assert 'model_reasoning_effort="xhigh"' in args
        assert 'approval_policy="never"' in args
        assert args[args.index("--sandbox") + 1] == "read-only"
        assert args[args.index("--cd") + 1] == str(worktree_path)
        assert Path(args[args.index("--output-schema") + 1]).name == "review-verdict-v1.json"
        assert f'"axis": "{axis}"' in prompt
        assert "peer_verdicts" not in prompt
        assert "Do not start sub-agents or evaluate another review axis" in prompt
        assert "Do not modify source, repair findings, merge, deploy" in prompt
    assert "$code-review" in calls[0]["prompt"]
    assert "spec axis" in calls[0]["prompt"]
    assert "$code-review" in calls[1]["prompt"]
    assert "standards axis" in calls[1]["prompt"]
    assert "$codebase-design" in calls[2]["prompt"]
    assert "$domain-modeling" in calls[2]["prompt"]


def test_codex_review_adapter_rejects_tampered_skill_provenance_before_launch(tmp_path) -> None:
    worktree_path = tmp_path / "review-worktree"
    worktree_path.mkdir()
    marker = tmp_path / "must-not-launch"
    executable = tmp_path / "fake-codex"
    executable.write_text(
        f"#!/bin/sh\ntouch {marker}\n",
        encoding="utf-8",
    )
    os.chmod(executable, 0o755)
    route = SkillRouter.packaged(SKILL_ROOT).route_review("requirements_review")
    tampered = ReviewSkillRoute(
        axis=route.axis,
        skills=(SkillProvenance(name="code-review", content_sha256="0" * 64),),
    )

    with pytest.raises(ReviewExecutionError, match="skills do not match"):
        CodexCliReviewWorker(executable=str(executable), skill_root=SKILL_ROOT).run(
            ReviewInvocation(
                assignment=review_assignment("requirements"),
                worktree=Worktree(
                    path=worktree_path,
                    branch="codex/run-run-001",
                    base_ref="main",
                ),
                selection=NodePolicy.packaged().select("requirements_review"),
                route=tampered,
                access_profile={
                    "role": "reviewer",
                    "sandbox": "read-only",
                    "source_root": str(worktree_path),
                    "write_roots": [],
                },
            )
        )

    assert not marker.exists()


def _requirements_invocation(worktree_path: Path) -> ReviewInvocation:
    return ReviewInvocation(
        assignment=review_assignment("requirements"),
        worktree=Worktree(
            path=worktree_path,
            branch="codex/run-run-001",
            base_ref="main",
        ),
        selection=NodePolicy.packaged().select("requirements_review"),
        route=SkillRouter.packaged(SKILL_ROOT).route_review("requirements_review"),
        access_profile={
            "role": "reviewer",
            "sandbox": "read-only",
            "source_root": str(worktree_path),
            "write_roots": [],
        },
    )


@pytest.mark.parametrize(
    ("result_updates", "expected_message"),
    [
        ({"axis": "code"}, "does not match its assignment"),
        ({"head_sha": "0" * 40}, "does not match its assignment"),
        ({"verdict": "not_applicable"}, "requirements review must be applicable"),
        ({"rationale": ""}, "review result does not match schema"),
    ],
    ids=["wrong-axis", "wrong-head", "requirements-not-applicable", "invalid-schema"],
)
def test_codex_review_adapter_fails_closed_for_invalid_worker_output(
    tmp_path,
    result_updates: dict[str, object],
    expected_message: str,
) -> None:
    worktree_path = tmp_path / "review-worktree"
    worktree_path.mkdir()
    result = {
        "schema_version": "1",
        "invocation_id": "review-requirements-001",
        "axis": "requirements",
        "head_sha": HEAD_SHA,
        "verdict": "pass",
        "rationale": "Requirements and evidence agree.",
        "findings": [],
    }
    result.update(result_updates)
    executable = tmp_path / "fake-codex"
    executable.write_text(
        """#!/usr/bin/env python3
import pathlib
import sys

args = sys.argv[1:]
pathlib.Path(args[args.index("--output-last-message") + 1]).write_text('''RESULT''', encoding="utf-8")
""".replace("RESULT", json.dumps(result)),
        encoding="utf-8",
    )
    os.chmod(executable, 0o755)

    with pytest.raises(InvalidReviewContract, match=expected_message):
        CodexCliReviewWorker(executable=str(executable), skill_root=SKILL_ROOT).run(
            _requirements_invocation(worktree_path)
        )


def test_codex_review_adapter_rejects_wrong_policy_and_process_failure(tmp_path) -> None:
    worktree_path = tmp_path / "review-worktree"
    worktree_path.mkdir()
    executable = tmp_path / "fake-codex"
    executable.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
    os.chmod(executable, 0o755)
    invocation = _requirements_invocation(worktree_path)
    worker = CodexCliReviewWorker(executable=str(executable), skill_root=SKILL_ROOT)

    with pytest.raises(ReviewExecutionError, match="policy does not match"):
        worker.run(
            ReviewInvocation(
                assignment=invocation.assignment,
                worktree=invocation.worktree,
                selection=NodeSelection(
                    policy_version="1",
                    task="requirements_review",
                    model="gpt-5.6-sol",
                    reasoning_effort="xhigh",
                    sandbox="read-only",
                ),
                route=invocation.route,
                access_profile=invocation.access_profile,
            )
        )
    with pytest.raises(ReviewExecutionError, match="process exited with 7"):
        worker.run(invocation)
