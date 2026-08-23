from __future__ import annotations

import pytest

from github_issue_pilot.review import (
    InvalidReviewContract,
    validate_review_assignment,
    validate_review_result,
)

HEAD_SHA = "1234567890abcdef1234567890abcdef12345678"


def valid_review_assignment(axis: str = "requirements") -> dict[str, object]:
    return {
        "schema_version": "1",
        "invocation_id": f"review-{axis}-001",
        "axis": axis,
        "scope": {
            "requirements": "Compare requirements, implementation, and evidence",
            "code": "Check repository standards and relevant code smells",
            "architecture": (
                "Check domain language, ADRs, modules, interfaces, seams, adapters, "
                "depth, and test surfaces"
            ),
        }[axis],
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
        "evidence": [
            {
                "criterion": "Customer can export CSV",
                "verdict": "pass",
                "kind": "rest",
                "observed_interface": "HTTP API",
                "expected_result": "CSV is returned",
                "observations": [
                    {"phase": "request", "description": "POST /exports"},
                    {"phase": "response", "description": "201 export_id=41"},
                    {"phase": "read_back", "description": "CSV contains customer row"},
                ],
            }
        ],
        "repository_context": {"instructions": "Follow AGENTS.md."},
    }


def valid_review_result(axis: str = "requirements", verdict: str = "pass") -> dict[str, object]:
    return {
        "schema_version": "1",
        "invocation_id": f"review-{axis}-001",
        "axis": axis,
        "head_sha": HEAD_SHA,
        "verdict": verdict,
        "rationale": "The reviewed axis satisfies its contract.",
        "findings": [],
    }


@pytest.mark.parametrize("axis", ["requirements", "code", "architecture"])
def test_review_assignment_and_result_contracts_accept_every_axis(axis: str) -> None:
    validate_review_assignment(valid_review_assignment(axis))
    validate_review_result(valid_review_result(axis))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda result: result.update(verdict="maybe"),
        lambda result: result.update(rationale=""),
        lambda result: result.update(head_sha="main"),
        lambda result: result.update(findings=[{"description": "Missing location"}]),
        lambda result: result.update(unexpected="field"),
    ],
    ids=["verdict", "rationale", "head", "finding", "extra-field"],
)
def test_review_result_contract_rejects_malformed_verdicts(mutation) -> None:
    result = valid_review_result("code", "fail")
    mutation(result)

    with pytest.raises(InvalidReviewContract, match="review result does not match schema"):
        validate_review_result(result)


def test_requirements_review_can_never_be_not_applicable() -> None:
    result = valid_review_result("requirements", "not_applicable")

    with pytest.raises(InvalidReviewContract, match="requirements review must be applicable"):
        validate_review_result(result)


def test_review_assignment_rejects_unbounded_or_peer_review_context() -> None:
    assignment = valid_review_assignment()
    assignment["peer_verdicts"] = [{"axis": "code", "verdict": "pass"}]

    with pytest.raises(InvalidReviewContract, match="review assignment does not match schema"):
        validate_review_assignment(assignment)
