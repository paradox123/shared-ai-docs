from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from github_issue_pilot.implementation import (
    CodexCliWorker,
    WorkerExecutionError,
    Worktree,
)
from github_issue_pilot.policy import NodePolicy, SkillRouter
from github_issue_pilot.repair import InvalidRepairContract, RepairInvocation

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"
SKILL_ROOT = (
    Path(__file__).resolve().parents[2] / "skills-repo" / "vendor" / "mattpocock" / ".agents" / "skills"
)


def repair_assignment(round_number: int) -> dict[str, object]:
    return {
        "schema_version": "1",
        "repair_batch_id": "repair-batch-001",
        "initial_review": {"batch_id": "review-batch-001", "head_sha": HEAD_SHA},
        "round": {"number": round_number, "limit": 3},
        "issue": {
            "repository": "daniel/probare-crm",
            "number": 41,
            "title": "Add customer export",
            "body": "- [ ] Customer can export CSV",
            "type": "feature",
        },
        "requirements": ["Customer can export CSV"],
        "repository_context": {
            "base_ref": "main",
            "instructions": "Follow AGENTS.md.",
            "verification_command": "pytest tests/test_export.py",
        },
        "findings": [
            {
                "source": "review",
                "axis": "code",
                "location": "src/export.py:10",
                "description": "Validate the filter before export",
            }
        ],
        "prior_attempts": [],
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


def repair_result(round_number: int) -> dict[str, object]:
    criterion = "Customer can export CSV"
    return {
        "schema_version": "1",
        "repair_batch_id": "repair-batch-001",
        "round_number": round_number,
        "outcome": "completed",
        "summary": "Repaired export filter validation",
        "implementation_result": {
            "schema_version": "2",
            "outcome": "completed",
            "summary": "Repaired export filter validation",
            "red_green_slices": [
                {
                    "requirement": criterion,
                    "red": {"command": "pytest export", "observed": "failed"},
                    "green": {"command": "pytest export", "observed": "passed"},
                }
            ],
            "changed_files": ["src/export.py"],
            "verification": [{"command": "pytest", "observed": "passed"}],
            "evidence": [
                {
                    "criterion": criterion,
                    "verdict": "pass",
                    "kind": "rest",
                    "observed_interface": "HTTP API",
                    "expected_result": criterion,
                    "observations": [
                        {
                            "phase": "request",
                            "description": "POST /exports",
                            "artifact": "POST /exports",
                            "correlation_id": None,
                        },
                        {
                            "phase": "response",
                            "description": "201 export_id=41",
                            "artifact": "201 export_id=41",
                            "correlation_id": None,
                        },
                        {
                            "phase": "read_back",
                            "description": "CSV contains customer row",
                            "artifact": "GET /exports/41 -> customer row",
                            "correlation_id": None,
                        },
                    ],
                }
            ],
            "findings": [],
        },
        "remaining_findings": [],
        "blockage": None,
        "escalation_reason": None,
        "terminal_disposition": None,
    }


def _fake_codex(tmp_path: Path, result: dict[str, object]) -> Path:
    executable = tmp_path / "fake-codex"
    executable.write_text(
        """#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]
prompt = sys.stdin.read()
pathlib.Path(__file__).with_suffix(".args.json").write_text(json.dumps(args), encoding="utf-8")
pathlib.Path(__file__).with_suffix(".stdin.txt").write_text(prompt, encoding="utf-8")
output = pathlib.Path(args[args.index("--output-last-message") + 1])
output.write_text('''RESULT_JSON''', encoding="utf-8")
print(json.dumps({"type": "thread.started", "thread_id": "repair-thread-001"}))
print(json.dumps({"type": "turn.completed"}))
""".replace("RESULT_JSON", json.dumps(result)),
        encoding="utf-8",
    )
    os.chmod(executable, 0o755)
    return executable


@pytest.mark.parametrize(
    ("round_number", "model"),
    [(1, "gpt-5.6-terra"), (3, "gpt-5.6-sol")],
)
def test_same_codex_writer_repairs_in_existing_worktree_with_bounded_policy_and_prompt(
    tmp_path,
    round_number: int,
    model: str,
) -> None:
    executable = _fake_codex(tmp_path, repair_result(round_number))
    worktree_path = tmp_path / "run-worktree"
    worktree_path.mkdir()
    assignment = repair_assignment(round_number)
    selection = NodePolicy.packaged().select_repair(round_number=round_number)
    skills = SkillRouter.packaged(SKILL_ROOT).route("implementation", issue_type="feature")

    output = CodexCliWorker(executable=str(executable)).repair(
        RepairInvocation(
            assignment=assignment,
            worktree=Worktree(worktree_path, "codex/run-001", "main"),
            selection=selection,
            skills=skills,
            access_profile={
                "role": "implementer",
                "sandbox": "workspace-write",
                "write_root": str(worktree_path),
                "additional_write_roots": [],
            },
        )
    )

    args = json.loads(executable.with_suffix(".args.json").read_text(encoding="utf-8"))
    prompt = executable.with_suffix(".stdin.txt").read_text(encoding="utf-8")
    assert args[args.index("--model") + 1] == model
    assert 'model_reasoning_effort="xhigh"' in args
    assert args[args.index("--sandbox") + 1] == "workspace-write"
    assert args[args.index("--cd") + 1] == str(worktree_path)
    assert Path(args[args.index("--output-schema") + 1]).name == "repair-result-v1.json"
    assert "$implement" in prompt and "$tdd" in prompt
    assert "Small reversible" in prompt
    assert "Warnings, consent, domain actions, security meaning" in prompt
    assert "do not synthesize" in prompt.casefold()
    assert "peer_verdicts" not in prompt
    assert output.result == repair_result(round_number)
    assert output.diagnostic_events[0]["thread_id"] == "repair-thread-001"


def test_repair_adapter_rejects_wrong_policy_write_root_and_result_identity_before_acceptance(
    tmp_path,
) -> None:
    worktree_path = tmp_path / "run-worktree"
    worktree_path.mkdir()
    assignment = repair_assignment(1)
    skills = SkillRouter.packaged(SKILL_ROOT).route("implementation", issue_type="feature")
    wrong_result = repair_result(1)
    wrong_result["repair_batch_id"] = "other-batch"
    executable = _fake_codex(tmp_path, wrong_result)
    worker = CodexCliWorker(executable=str(executable))

    with pytest.raises(WorkerExecutionError, match="repair policy"):
        worker.repair(
            RepairInvocation(
                assignment=assignment,
                worktree=Worktree(worktree_path, "codex/run-001", "main"),
                selection=NodePolicy.packaged().select_repair(round_number=3),
                skills=skills,
                access_profile={
                    "role": "implementer",
                    "sandbox": "workspace-write",
                    "write_root": str(worktree_path),
                    "additional_write_roots": [],
                },
            )
        )

    with pytest.raises(WorkerExecutionError, match="access profile"):
        worker.repair(
            RepairInvocation(
                assignment=assignment,
                worktree=Worktree(worktree_path, "codex/run-001", "main"),
                selection=NodePolicy.packaged().select_repair(round_number=1),
                skills=skills,
                access_profile={
                    "role": "implementer",
                    "sandbox": "workspace-write",
                    "write_root": str(tmp_path / "other"),
                    "additional_write_roots": [],
                },
            )
        )

    with pytest.raises(InvalidRepairContract, match="does not match its assignment"):
        worker.repair(
            RepairInvocation(
                assignment=assignment,
                worktree=Worktree(worktree_path, "codex/run-001", "main"),
                selection=NodePolicy.packaged().select_repair(round_number=1),
                skills=skills,
                access_profile={
                    "role": "implementer",
                    "sandbox": "workspace-write",
                    "write_root": str(worktree_path),
                    "additional_write_roots": [],
                },
            )
        )
