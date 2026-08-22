from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from github_issue_pilot.contracts import load_contract


class PolicyViolation(ValueError):
    pass


@dataclass(frozen=True)
class NodeSelection:
    policy_version: str
    task: str
    model: str | None
    reasoning_effort: str | None
    sandbox: str


@dataclass(frozen=True)
class SkillProvenance:
    name: str
    content_sha256: str


class NodePolicy:
    def __init__(self, contract: dict[str, Any]) -> None:
        self._contract = contract

    @classmethod
    def packaged(cls) -> NodePolicy:
        return cls(load_contract("node-policy-v1.json"))

    def select(
        self,
        task: str,
        *,
        escalation_reason: str | None = None,
        requested_model: str | None = None,
        requested_reasoning: str | None = None,
        requested_sandbox: str | None = None,
    ) -> NodeSelection:
        tasks = self._contract["tasks"]
        if task not in tasks:
            raise PolicyViolation(f"unsupported node task: {task}")
        if task == "escalation" and escalation_reason not in self._contract["allowed_escalations"]:
            raise PolicyViolation(f"{escalation_reason!r} is not an allowed escalation")

        selected = tasks[task]
        overrides = {
            "model": requested_model,
            "reasoning_effort": requested_reasoning,
            "sandbox": requested_sandbox,
        }
        for field, requested in overrides.items():
            if requested is not None and requested != selected[field]:
                raise PolicyViolation(f"requested {field} does not match node policy")

        return NodeSelection(
            policy_version=self._contract["version"],
            task=task,
            model=selected["model"],
            reasoning_effort=selected["reasoning_effort"],
            sandbox=selected["sandbox"],
        )


class SkillRouter:
    def __init__(self, contract: dict[str, Any], skill_root: Path) -> None:
        self._contract = contract
        self._skill_root = skill_root

    @classmethod
    def packaged(cls, skill_root: Path) -> SkillRouter:
        return cls(load_contract("skill-routing-v1.json"), skill_root)

    def route(self, task: str, *, issue_type: str | None = None) -> tuple[SkillProvenance, ...]:
        key = f"{task}:{issue_type}" if issue_type is not None else task
        names = self._contract["routes"].get(key)
        if names is None:
            raise PolicyViolation(f"unsupported skill route: {key}")

        routed = []
        for name in names:
            skill_path = self._skill_root / name / "SKILL.md"
            if not skill_path.is_file():
                raise PolicyViolation(f"routed skill is missing: {name}")
            routed.append(
                SkillProvenance(
                    name=name,
                    content_sha256=hashlib.sha256(skill_path.read_bytes()).hexdigest(),
                )
            )
        return tuple(routed)
