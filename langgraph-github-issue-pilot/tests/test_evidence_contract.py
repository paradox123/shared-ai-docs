from __future__ import annotations

import pytest
from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator

from github_issue_pilot.contracts import load_contract
from github_issue_pilot.evidence import (
    EvidenceRejected,
    qualify_evidence,
    render_pull_request_body,
)


def evidence_item(kind: str, phases: list[str]) -> dict[str, object]:
    return {
        "criterion": f"Criterion for {kind}",
        "verdict": "pass",
        "kind": kind,
        "observed_interface": "public test interface",
        "expected_result": "business result is observable",
        "observations": [
            {
                "phase": phase,
                "description": f"Observed {phase}",
                "artifact": f"inline {phase} excerpt",
                "correlation_id": "run-41",
            }
            for phase in phases
        ],
    }


def complete_result() -> dict[str, object]:
    return {
        "schema_version": "2",
        "outcome": "completed",
        "summary": "Implemented customer export",
        "red_green_slices": [
            {
                "requirement": "Customer can export CSV",
                "red": {"command": "pytest export", "observed": "failed"},
                "green": {"command": "pytest export", "observed": "passed"},
            }
        ],
        "changed_files": ["src/export.py"],
        "verification": [{"command": "pytest", "observed": "passed"}],
        "evidence": [
            evidence_item("rest", ["request", "response", "read_back"]),
            evidence_item("ui", ["interaction", "screenshot"]),
            evidence_item("recovery", ["restart", "read_back"]),
            evidence_item("idempotency", ["repeat", "read_back"]),
            evidence_item("negative_gate", ["rejection", "side_effect_read_back"]),
            evidence_item("background", ["eventual_result", "log"]),
            evidence_item("document", ["read_back", "log"]),
        ],
        "findings": [],
    }


def test_packaged_worker_result_v2_accepts_every_supported_evidence_kind() -> None:
    validator = Draft202012Validator(load_contract("worker-result-v2.json"))

    validator.validate(complete_result())


def test_worker_result_v2_rejects_unknown_observation_phases() -> None:
    result = complete_result()
    result["evidence"][0]["observations"][0]["phase"] = "healthcheck"

    with pytest.raises(ValidationError):
        Draft202012Validator(load_contract("worker-result-v2.json")).validate(result)


def test_complete_direct_evidence_is_qualified_for_every_criterion() -> None:
    result = complete_result()
    requirements = [item["criterion"] for item in result["evidence"]]

    qualified = qualify_evidence(requirements, result)

    assert [item["criterion"] for item in qualified] == requirements
    assert all(item["verdict"] == "pass" for item in qualified)


@pytest.mark.parametrize(
    ("kind", "missing_phase"),
    [
        ("rest", "request"),
        ("ui", "interaction"),
        ("recovery", "restart"),
        ("idempotency", "repeat"),
        ("negative_gate", "side_effect_read_back"),
        ("background", "eventual_result"),
        ("document", "read_back"),
    ],
    ids=["rest", "ui", "recovery", "idempotency", "negative-gate", "background", "document"],
)
def test_each_evidence_kind_requires_its_direct_observations(
    kind: str,
    missing_phase: str,
) -> None:
    result = complete_result()
    requirements = [item["criterion"] for item in result["evidence"]]
    item = next(item for item in result["evidence"] if item["kind"] == kind)
    item["observations"] = [
        observation
        for observation in item["observations"]
        if observation["phase"] != missing_phase
    ]

    with pytest.raises(EvidenceRejected, match="missing_direct_observation"):
        qualify_evidence(requirements, result)


@pytest.mark.parametrize(
    "surrogate",
    [
        "build passed",
        "process started",
        "container running",
        "healthcheck 200",
        "HTTP 200",
        "2xx",
        "queue accepted",
        "enqueued",
        "log says export completed",
        "static initial screenshot",
    ],
    ids=[
        "build",
        "process",
        "container",
        "healthcheck",
        "http-status",
        "status-family",
        "queue",
        "enqueue",
        "log-claim",
        "static-screenshot",
    ],
)
def test_operational_surrogate_alone_never_qualifies_as_background_result(
    surrogate: str,
) -> None:
    result = complete_result()
    requirements = [item["criterion"] for item in result["evidence"]]
    background = next(item for item in result["evidence"] if item["kind"] == "background")
    background["observations"] = [
        {
            "phase": "eventual_result",
            "description": surrogate,
            "artifact": surrogate,
            "correlation_id": None,
        }
    ]

    with pytest.raises(EvidenceRejected, match="infrastructure_surrogate"):
        qualify_evidence(requirements, result)


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        (lambda evidence: evidence.pop(), "criterion_coverage"),
        (lambda evidence: evidence.append(evidence[0]), "criterion_coverage"),
        (
            lambda evidence: evidence[0]["observations"].pop(),
            "missing_direct_observation",
        ),
        (
            lambda evidence: next(
                item for item in evidence if item["kind"] == "background"
            ).update(
                observations=[
                    {
                        "phase": "eventual_result",
                        "description": "queue accepted; process started",
                        "artifact": "healthcheck 200",
                        "correlation_id": None,
                    }
                ]
            ),
            "infrastructure_surrogate",
        ),
    ],
    ids=["missing", "duplicate", "missing-kind-phase", "surrogate-only"],
)
def test_incomplete_or_surrogate_evidence_is_rejected(mutation, expected_code: str) -> None:
    result = complete_result()
    requirements = [item["criterion"] for item in result["evidence"]]
    mutation(result["evidence"])

    with pytest.raises(EvidenceRejected, match=expected_code):
        qualify_evidence(requirements, result)


def test_qualified_evidence_is_redacted_and_rendered_with_embedded_artifacts() -> None:
    result = complete_result()
    requirements = [item["criterion"] for item in result["evidence"]]
    result["evidence"][0]["observations"][1].update(
        description="Response for daniel@example.com used Authorization: Bearer ghp_12345678901234567890",
        artifact="customer_secret=super-private-value",
    )
    result["evidence"][1]["observations"][1]["artifact"] = (
        "https://example.invalid/evidence/ui-export.png"
    )

    qualified = qualify_evidence(
        requirements,
        result,
        sensitive_values=("super-private-value",),
    )
    body = render_pull_request_body(
        issue_number=41,
        head_sha="1234567890abcdef1234567890abcdef12345678",
        evidence=qualified,
    )

    assert "daniel@example.com" not in body
    assert "ghp_12345678901234567890" not in body
    assert "super-private-value" not in body
    assert body.count("[REDACTED]") >= 3
    assert "`1234567890abcdef1234567890abcdef12345678`" in body
    assert "| Criterion for rest | pass | public test interface |" in body
    assert "```text\ninline request excerpt\n```" in body
    assert "![Evidence: Criterion for ui]" in body
    assert "correlation `run-41`" in body
    assert "Closes #41" in body
