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


@dataclass(frozen=True)
class ReviewSkillRoute:
    axis: str
    skills: tuple[SkillProvenance, ...]


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

    def select_repair(
        self,
        *,
        round_number: int,
        escalation_reason: str | None = None,
    ) -> NodeSelection:
        if round_number not in {1, 2, 3}:
            raise PolicyViolation("repair round must be between one and three")
        allowed = set(self._contract["allowed_escalations"])
        if escalation_reason is not None and escalation_reason not in allowed:
            raise PolicyViolation(f"{escalation_reason!r} is not an allowed repair escalation")
        if escalation_reason == "final_repair_round" and round_number != 3:
            raise PolicyViolation("final repair escalation is restricted to round three")

        escalated = round_number == 3 or escalation_reason is not None
        return self.select("findings_repair_escalated" if escalated else "findings_repair")


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

        return self._resolve(names)

    def route_review(self, task: str) -> ReviewSkillRoute:
        route = self._contract["review_routes"].get(task)
        if route is None:
            raise PolicyViolation(f"unsupported review skill route: {task}")
        return ReviewSkillRoute(axis=route["axis"], skills=self._resolve(route["skills"]))

    def _resolve(self, names: list[str]) -> tuple[SkillProvenance, ...]:
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
