from __future__ import annotations

import pytest

from github_issue_pilot.repair import (
    InvalidRepairContract,
    validate_repair_assignment,
    validate_repair_result,
)

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"


def valid_worker_result() -> dict[str, object]:
    criterion = "Customer can export CSV"
    return {
        "schema_version": "2",
        "outcome": "completed",
        "summary": "Repaired customer export",
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
                    {"phase": "request", "description": "POST /exports"},
                    {"phase": "response", "description": "201 export_id=41"},
                    {"phase": "read_back", "description": "CSV contains customer row"},
                ],
            }
        ],
        "findings": [],
    }


def valid_repair_assignment() -> dict[str, object]:
    return {
        "schema_version": "1",
        "repair_batch_id": "repair-batch-001",
        "initial_review": {"batch_id": "review-batch-001", "head_sha": HEAD_SHA},
        "round": {"number": 1, "limit": 3},
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


def valid_repair_result(outcome: str = "completed") -> dict[str, object]:
    result: dict[str, object] = {
        "schema_version": "1",
        "repair_batch_id": "repair-batch-001",
        "round_number": 1,
        "outcome": outcome,
        "summary": "Repair attempt completed",
        "implementation_result": valid_worker_result() if outcome == "completed" else None,
        "remaining_findings": [],
        "blockage": None,
        "escalation_reason": None,
        "terminal_disposition": None,
    }
    if outcome == "blocked":
        result["blockage"] = {
            "reason": "requirements_missing_or_contradictory",
            "rationale": "The export retention requirement is contradictory.",
        }
        result["terminal_disposition"] = "needs-info"
    if outcome == "escalate":
        result["escalation_reason"] = "security_boundary"
    return result


def test_repair_contracts_accept_bounded_completed_blocked_and_escalated_results() -> None:
    validate_repair_assignment(valid_repair_assignment())
    for outcome in ("completed", "blocked", "escalate"):
        validate_repair_result(valid_repair_result(outcome))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["round"].update(number=4),
        lambda value: value.update(findings=[]),
        lambda value: value["findings"][0].update(axis="security"),
        lambda value: value.update(peer_verdicts=[]),
    ],
    ids=["fourth-round", "empty-findings", "unknown-axis", "peer-context"],
)
def test_repair_assignment_rejects_unbounded_or_unstructured_context(mutation) -> None:
    assignment = valid_repair_assignment()
    mutation(assignment)

    with pytest.raises(InvalidRepairContract, match="repair assignment does not match schema"):
        validate_repair_assignment(assignment)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update(outcome="maybe"),
        lambda value: value.update(implementation_result=None),
        lambda value: value["implementation_result"].update(red_green_slices=[]),
        lambda value: value.update(unexpected=True),
    ],
    ids=["outcome", "completed-without-result", "invalid-worker-result", "extra-field"],
)
def test_completed_repair_result_rejects_malformed_output(mutation) -> None:
    result = valid_repair_result()
    mutation(result)

    with pytest.raises(InvalidRepairContract):
        validate_repair_result(result)


def test_blocked_and_escalated_results_require_structured_allowed_reasons() -> None:
    blocked = valid_repair_result("blocked")
    blocked["blockage"] = None
    escalated = valid_repair_result("escalate")
    escalated["escalation_reason"] = "expensive_task"

    with pytest.raises(InvalidRepairContract):
        validate_repair_result(blocked)
    with pytest.raises(InvalidRepairContract):
        validate_repair_result(escalated)


def test_missing_or_contradictory_requirements_can_only_handoff_as_needs_info() -> None:
    result = valid_repair_result("blocked")
    result["terminal_disposition"] = "ready-for-human"

    with pytest.raises(InvalidRepairContract, match="missing requirements require needs-info"):
        validate_repair_result(result)
