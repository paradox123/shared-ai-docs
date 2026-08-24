from __future__ import annotations

import copy

import pytest

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.implementation import (
    InvalidWorkerResult,
    validate_worker_result,
)
from github_issue_pilot.intervention import (
    InvalidInterventionContract,
    validate_intervention_request,
)
from github_issue_pilot.repair import InvalidRepairContract, validate_repair_result
from github_issue_pilot.review import InvalidReviewContract, validate_review_result

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"


def valid_intervention(role: str = "implementer", phase: str = "implementation") -> dict[str, object]:
    return {
        "schema_version": "1",
        "repository": {"full_name": "daniel/probare-crm", "issue_number": 41},
        "run": {
            "id": "run-001",
            "phase": phase,
            "operation_key": f"run-001:{phase}:worker-001",
        },
        "role": role,
        "context": {
            "worktree_path": "/tmp/pilot-worktrees/run-001",
            "branch": "codex/run-run-001",
            "pull_request_number": 77,
            "head_sha": HEAD_SHA,
        },
        "classification": "product_decision",
        "problem": "The requirements permit two contradictory retention behaviors.",
        "required_action": "Choose which retention behavior is authoritative.",
        "options": [
            {
                "label": "retain-30-days",
                "impact": "Records remain recoverable for thirty days.",
            },
            {
                "label": "delete-immediately",
                "impact": "Records cannot be recovered after deletion.",
            },
        ],
        "recommendation": {
            "option_label": "retain-30-days",
            "rationale": "It matches the existing audit requirement.",
        },
        "preserved": {
            "findings": ["Requirements disagree on retention."],
            "results": ["No source changes were made after detecting the conflict."],
        },
    }


def valid_worker_intervention_result() -> dict[str, object]:
    return {
        "schema_version": "3",
        "outcome": "intervention",
        "summary": "Implementation paused for a product decision.",
        "red_green_slices": [],
        "changed_files": [],
        "verification": [],
        "evidence": [],
        "findings": ["Requirements disagree on retention."],
        "intervention": valid_intervention(),
    }


def valid_review_intervention_result() -> dict[str, object]:
    return {
        "schema_version": "2",
        "invocation_id": "review-requirements-001",
        "axis": "requirements",
        "head_sha": HEAD_SHA,
        "verdict": "intervention",
        "rationale": "The acceptance requirements contradict each other.",
        "findings": [],
        "intervention": valid_intervention("requirements_reviewer", "review"),
    }


def valid_repair_intervention_result() -> dict[str, object]:
    return {
        "schema_version": "2",
        "repair_batch_id": "repair-batch-001",
        "round_number": 1,
        "outcome": "intervention",
        "summary": "Repair paused for a product decision.",
        "implementation_result": None,
        "remaining_findings": [],
        "blockage": None,
        "escalation_reason": None,
        "terminal_disposition": None,
        "intervention": valid_intervention("repairer", "repair"),
    }


def test_every_agent_phase_accepts_the_same_complete_intervention_contract() -> None:
    validate_intervention_request(valid_intervention())
    validate_worker_result(valid_worker_intervention_result())
    validate_review_result(valid_review_intervention_result())
    validate_repair_result(valid_repair_intervention_result())


@pytest.mark.parametrize(
    "field",
    [
        "repository",
        "run",
        "role",
        "context",
        "classification",
        "problem",
        "required_action",
        "options",
        "recommendation",
        "preserved",
    ],
)
def test_intervention_rejects_missing_decision_context(field: str) -> None:
    request = valid_intervention()
    request.pop(field)

    with pytest.raises(InvalidInterventionContract):
        validate_intervention_request(request)


def test_agent_phase_rejects_an_invalid_nested_intervention() -> None:
    for result, validator, expected_error in (
        (valid_worker_intervention_result(), validate_worker_result, InvalidWorkerResult),
        (valid_review_intervention_result(), validate_review_result, InvalidReviewContract),
        (valid_repair_intervention_result(), validate_repair_result, InvalidRepairContract),
    ):
        invalid = copy.deepcopy(result)
        invalid["intervention"]["options"] = []
        with pytest.raises(expected_error):
            validator(invalid)


def test_strict_agent_schemas_embed_the_canonical_intervention_shape() -> None:
    canonical = load_contract("intervention-request-v1.json")
    for name in (
        "worker-result-v3.json",
        "review-verdict-v2.json",
        "repair-result-v2.json",
    ):
        schema = load_contract(name)
        assert schema["$defs"]["intervention_request"] == canonical
