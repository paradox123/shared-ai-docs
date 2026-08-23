from __future__ import annotations

from dataclasses import dataclass

from github_issue_pilot.github import RepositorySettings


@dataclass(frozen=True)
class WorkflowLabelDefinition:
    name: str
    color: str
    description: str


@dataclass(frozen=True)
class RepositoryActivationProfile:
    repository_name: str
    workflow_label_definitions: tuple[WorkflowLabelDefinition, ...]
    allowed_event_actions: frozenset[tuple[str, str]]

    @property
    def workflow_labels(self) -> tuple[str, ...]:
        return tuple(definition.name for definition in self.workflow_label_definitions)

    @property
    def allowed_event_groups(self) -> frozenset[str]:
        return frozenset(event for event, _ in self.allowed_event_actions)

    def settings(self, repository: str, *, base_ref: str) -> RepositorySettings:
        if repository.rsplit("/", maxsplit=1)[-1] != self.repository_name:
            raise ValueError(f"repository must be named {self.repository_name}")
        return RepositorySettings(
            repository=repository,
            base_ref=base_ref,
            allowed_event_actions=self.allowed_event_actions,
        )


PROBARE_CRM_PROFILE = RepositoryActivationProfile(
    repository_name="probare-crm",
    workflow_label_definitions=(
        WorkflowLabelDefinition("ready-for-agent", "1D76DB", "Authorized for agent implementation"),
        WorkflowLabelDefinition("agent-running", "FBCA04", "Agent implementation is active"),
        WorkflowLabelDefinition("verified", "0E8A16", "Current pull request head is verified"),
        WorkflowLabelDefinition("awaiting-review", "5319E7", "Awaiting Daniel's human review"),
        WorkflowLabelDefinition("needs-info", "D93F0B", "Missing or contradictory product information"),
        WorkflowLabelDefinition("ready-for-human", "B60205", "Agent stopped at a human decision boundary"),
    ),
    allowed_event_actions=frozenset(
        {
            ("issues", "opened"),
            ("issues", "edited"),
            ("issues", "labeled"),
            ("issues", "unlabeled"),
            ("issues", "reopened"),
            ("issues", "closed"),
            ("pull_request", "opened"),
            ("pull_request", "synchronize"),
            ("pull_request", "closed"),
            ("pull_request_review", "submitted"),
            ("pull_request_review", "dismissed"),
            ("pull_request_review_comment", "created"),
            ("pull_request_review_comment", "edited"),
            ("issue_comment", "created"),
            ("issue_comment", "edited"),
        }
    ),
)
