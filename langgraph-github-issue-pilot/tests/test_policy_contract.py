from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from github_issue_pilot.policy import NodePolicy, PolicyViolation, SkillRouter

SKILL_ROOT = (
    Path(__file__).resolve().parents[2] / "skills-repo" / "vendor" / "mattpocock" / ".agents" / "skills"
)


@pytest.mark.parametrize(
    ("task", "model", "reasoning", "sandbox"),
    [
        ("deterministic", None, None, "read-only"),
        ("presentation", "gpt-5.6-luna", "medium", "read-only"),
        ("triage", "gpt-5.6-terra", "xhigh", "read-only"),
        ("slicing", "gpt-5.6-terra", "xhigh", "read-only"),
        ("implementation", "gpt-5.6-terra", "xhigh", "workspace-write"),
        ("findings_repair", "gpt-5.6-terra", "xhigh", "workspace-write"),
        ("requirements_review", "gpt-5.6-terra", "xhigh", "read-only"),
        ("code_review", "gpt-5.6-terra", "xhigh", "read-only"),
        ("architecture_review", "gpt-5.6-terra", "xhigh", "read-only"),
    ],
)
def test_versioned_node_policy_selects_exact_model_reasoning_and_rights(
    task: str,
    model: str | None,
    reasoning: str | None,
    sandbox: str,
) -> None:
    selection = NodePolicy.packaged().select(task)

    assert selection.policy_version == "1"
    assert (selection.model, selection.reasoning_effort, selection.sandbox) == (
        model,
        reasoning,
        sandbox,
    )


@pytest.mark.parametrize(
    "reason",
    [
        "architecture_boundary",
        "persistence_boundary",
        "security_boundary",
        "data_migration",
        "worker_escalate",
        "final_repair_round",
    ],
)
def test_sol_is_limited_to_defined_escalations(reason: str) -> None:
    selection = NodePolicy.packaged().select("escalation", escalation_reason=reason)

    assert (selection.model, selection.reasoning_effort, selection.sandbox) == (
        "gpt-5.6-sol",
        "xhigh",
        "read-only",
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"requested_model": "gpt-5.6-sol"},
        {"requested_reasoning": "medium"},
        {"requested_sandbox": "danger-full-access"},
    ],
)
def test_policy_rejects_an_override_that_differs_from_the_versioned_selection(
    overrides: dict[str, str],
) -> None:
    with pytest.raises(PolicyViolation, match="does not match node policy"):
        NodePolicy.packaged().select("implementation", **overrides)


def test_policy_rejects_an_undefined_sol_escalation() -> None:
    with pytest.raises(PolicyViolation, match="not an allowed escalation"):
        NodePolicy.packaged().select("escalation", escalation_reason="expensive_task")


@pytest.mark.parametrize(
    ("task", "issue_type", "expected_names"),
    [
        ("triage", None, ["triage"]),
        ("slicing", None, ["to-tickets"]),
        ("implementation", "feature", ["implement", "tdd"]),
        ("implementation", "bug", ["diagnosing-bugs", "tdd"]),
    ],
)
def test_skill_routing_records_task_specific_matt_pocock_content_hashes(
    task: str,
    issue_type: str | None,
    expected_names: list[str],
) -> None:
    routed = SkillRouter.packaged(SKILL_ROOT).route(task, issue_type=issue_type)

    assert [skill.name for skill in routed] == expected_names
    assert [skill.content_sha256 for skill in routed] == [
        hashlib.sha256((SKILL_ROOT / name / "SKILL.md").read_bytes()).hexdigest()
        for name in expected_names
    ]


def test_skill_routing_fails_closed_for_an_unsupported_issue_type() -> None:
    with pytest.raises(PolicyViolation, match="unsupported skill route"):
        SkillRouter.packaged(SKILL_ROOT).route("implementation", issue_type="research")


@pytest.mark.parametrize(
    ("task", "axis", "expected_names"),
    [
        ("requirements_review", "spec", ["code-review"]),
        ("code_review", "standards", ["code-review"]),
        ("architecture_review", "architecture", ["codebase-design", "domain-modeling"]),
    ],
)
def test_review_skill_routing_preserves_each_independent_axis_with_content_hashes(
    task: str,
    axis: str,
    expected_names: list[str],
) -> None:
    route = SkillRouter.packaged(SKILL_ROOT).route_review(task)

    assert route.axis == axis
    assert [skill.name for skill in route.skills] == expected_names
    assert [skill.content_sha256 for skill in route.skills] == [
        hashlib.sha256((SKILL_ROOT / name / "SKILL.md").read_bytes()).hexdigest()
        for name in expected_names
    ]
