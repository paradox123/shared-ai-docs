from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TextIO
from urllib.parse import urlparse

import httpx

from github_issue_pilot.evidence import contains_sensitive_text
from github_issue_pilot.github import REPOSITORY_ADAPTER_VERSION
from github_issue_pilot.profiles import PROBARE_CRM_PROFILE


class LiveActivationError(RuntimeError):
    def __init__(self, category: str) -> None:
        super().__init__(category)
        self.category = category


def _required(environment: Mapping[str, str], name: str) -> str:
    value = environment.get(name, "").strip()
    if not value:
        raise LiveActivationError("missing_configuration")
    return value


def _one_repository(environment: Mapping[str, str]) -> str:
    repositories = {
        repository.strip()
        for repository in _required(environment, "PILOT_ALLOWED_REPOSITORIES").split(",")
        if repository.strip()
    }
    if len(repositories) != 1:
        raise LiveActivationError("repository_profile_mismatch")
    repository = next(iter(repositories))
    if repository.rsplit("/", maxsplit=1)[-1] != PROBARE_CRM_PROFILE.repository_name:
        raise LiveActivationError("repository_profile_mismatch")
    return repository


def _repository_from_origin(origin: str) -> str | None:
    scp_match = re.fullmatch(r"git@github\.com:(?P<repository>[^/]+/[^/]+?)(?:\.git)?", origin)
    if scp_match:
        return scp_match.group("repository")
    parsed = urlparse(origin)
    if parsed.hostname != "github.com":
        return None
    return parsed.path.strip("/").removesuffix(".git") or None


def _check_local_configuration(
    environment: Mapping[str, str], repository: str
) -> tuple[str, str, str]:
    repository_root = Path(_required(environment, "PILOT_REPOSITORY_ROOT")).expanduser().resolve()
    worktree_root = Path(_required(environment, "PILOT_WORKTREE_ROOT")).expanduser().resolve()
    context_path = Path(
        _required(environment, "PILOT_REPOSITORY_CONTEXT_PATH")
    ).expanduser().resolve()
    skill_root = Path(_required(environment, "PILOT_SKILL_ROOT")).expanduser().resolve()
    tunnel_config = Path(_required(environment, "CLOUDFLARED_CONFIG")).expanduser().resolve()
    if repository_root.is_relative_to(worktree_root) or worktree_root.is_relative_to(repository_root):
        raise LiveActivationError("repository_worktree_overlap")
    if not repository_root.is_dir() or not worktree_root.is_dir():
        raise LiveActivationError("repository_path_unavailable")
    if not context_path.is_file() or not context_path.read_text(encoding="utf-8").strip():
        raise LiveActivationError("repository_context_unavailable")
    if not skill_root.is_dir():
        raise LiveActivationError("skill_root_unavailable")
    if not tunnel_config.is_file():
        raise LiveActivationError("relay_route_unavailable")
    public_url = _required(environment, "PILOT_PUBLIC_RECEIVER_URL")
    parsed_public_url = urlparse(public_url)
    if parsed_public_url.scheme != "https" or parsed_public_url.path != "/webhooks/github":
        raise LiveActivationError("relay_route_unavailable")
    webhook_url = _required(environment, "PILOT_GITHUB_WEBHOOK_URL")
    parsed_webhook_url = urlparse(webhook_url)
    if (
        parsed_webhook_url.scheme != "https"
        or parsed_webhook_url.path != "/webhooks/github"
        or webhook_url == public_url
    ):
        raise LiveActivationError("relay_route_unavailable")
    try:
        inside = subprocess.run(
            ["git", "-C", str(repository_root), "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        origin = subprocess.run(
            ["git", "-C", str(repository_root), "remote", "get-url", "origin"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LiveActivationError("repository_checkout_invalid") from exc
    if inside != "true" or _repository_from_origin(origin) != repository:
        raise LiveActivationError("repository_origin_mismatch")
    try:
        author_name = subprocess.run(
            ["git", "-C", str(repository_root), "config", "--local", "--get", "user.name"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        author_email = subprocess.run(
            ["git", "-C", str(repository_root), "config", "--local", "--get", "user.email"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LiveActivationError("git_identity_invalid") from exc
    github_login = _required(environment, "DANIEL_GITHUB_LOGIN")
    if not author_name or re.fullmatch(
        rf"[0-9]+\+{re.escape(github_login)}@users\.noreply\.github\.com",
        author_email,
        flags=re.IGNORECASE,
    ) is None:
        raise LiveActivationError("git_identity_invalid")
    base_ref = environment.get("PILOT_BASE_REF", "main").strip() or "main"
    if subprocess.run(
        ["git", "check-ref-format", f"refs/heads/{base_ref}"],
        check=False,
        capture_output=True,
    ).returncode != 0:
        raise LiveActivationError("base_ref_invalid")
    return base_ref, public_url, webhook_url


def _list(client: httpx.Client, path: str) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    page = 1
    while True:
        response = client.get(path, params={"per_page": 100, "page": page})
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise LiveActivationError("github_response_invalid")
        batch = [item for item in payload if isinstance(item, dict)]
        items.extend(batch)
        if len(payload) < 100:
            return items
        page += 1


def _repository_access(
    client: httpx.Client, repository: str, base_ref: str
) -> dict[str, object]:
    repository_response = client.get(f"/repos/{repository}")
    repository_response.raise_for_status()
    repository_payload = repository_response.json()
    if not isinstance(repository_payload, dict):
        raise LiveActivationError("github_response_invalid")
    permissions = repository_payload.get("permissions")
    if not isinstance(permissions, dict) or not all(
        permissions.get(permission) is True for permission in ("pull", "push", "admin")
    ):
        raise LiveActivationError("github_permission_missing")
    if repository_payload.get("default_branch") != base_ref:
        raise LiveActivationError("base_ref_mismatch")
    return repository_payload


def _github_client(
    environment: Mapping[str, str], transport: httpx.BaseTransport | None
) -> httpx.Client:
    return httpx.Client(
        base_url="https://api.github.com",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {_required(environment, 'GITHUB_TOKEN')}",
            "X-GitHub-Api-Version": "2026-03-10",
        },
        timeout=10,
        transport=transport,
    )


def _live_readiness(
    environment: Mapping[str, str], transport: httpx.BaseTransport | None
) -> dict[str, object]:
    repository = _one_repository(environment)
    base_ref, _, webhook_url = _check_local_configuration(environment, repository)
    profile = PROBARE_CRM_PROFILE
    with _github_client(environment, transport) as client:
        _repository_access(client, repository, base_ref)

        label_payloads = _list(client, f"/repos/{repository}/labels")
        existing_labels = {
            str(label.get("name", "")) for label in label_payloads if label.get("name")
        }
        if not set(profile.workflow_labels).issubset(existing_labels):
            raise LiveActivationError("workflow_labels_missing")

        issues = [
            issue
            for issue in _list(client, f"/repos/{repository}/issues")
            if "pull_request" not in issue
        ]
        ready_count = 0
        type_counts: Counter[str] = Counter()
        for issue in issues:
            labels = issue.get("labels")
            label_names = {
                label if isinstance(label, str) else str(label.get("name", ""))
                for label in labels if isinstance(label, (str, dict))
            } if isinstance(labels, list) else set()
            ready_count += profile.workflow_labels[0] in label_names
            issue_type = issue.get("type")
            if isinstance(issue_type, dict):
                type_name = str(issue_type.get("name") or "issue")
            elif isinstance(issue_type, str) and issue_type:
                type_name = issue_type
            else:
                type_name = "issue"
            type_counts[type_name] += 1

        hooks = _list(client, f"/repos/{repository}/hooks")
        matching_hooks = []
        for hook in hooks:
            config = hook.get("config")
            events = hook.get("events")
            if (
                hook.get("active") is True
                and isinstance(config, dict)
                and config.get("url") == webhook_url
                and config.get("content_type") == "json"
                and str(config.get("insecure_ssl", "0")) == "0"
                and isinstance(events, list)
                and profile.allowed_event_groups.issubset(
                    {str(event) for event in events}
                )
            ):
                matching_hooks.append(hook)
        if len(matching_hooks) != 1:
            raise LiveActivationError("webhook_configuration_mismatch")

    profile_material = json.dumps(
        {
            "actions": sorted([list(pair) for pair in profile.allowed_event_actions]),
            "labels": profile.workflow_labels,
            "name": profile.repository_name,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return {
        "adapter_version": REPOSITORY_ADAPTER_VERSION,
        "allowed_event_group_count": len(profile.allowed_event_groups),
        "base_ref": base_ref,
        "open_issue_count": len(issues),
        "profile_hash": hashlib.sha256(profile_material).hexdigest(),
        "ready_issue_count": ready_count,
        "repository_hash": hashlib.sha256(repository.encode()).hexdigest(),
        "required_label_count": len(profile.workflow_labels),
        "status": "ready",
        "type_counts": dict(sorted(type_counts.items())),
        "webhook_count": len(matching_hooks),
    }


def _ensure_live_labels(
    environment: Mapping[str, str], transport: httpx.BaseTransport | None
) -> dict[str, object]:
    repository = _one_repository(environment)
    base_ref, _, _ = _check_local_configuration(environment, repository)
    with _github_client(environment, transport) as client:
        _repository_access(client, repository, base_ref)
        existing_payloads = _list(client, f"/repos/{repository}/labels")
        existing = {
            str(label.get("name", ""))
            for label in existing_payloads
            if label.get("name")
        }
        missing = [
            definition
            for definition in PROBARE_CRM_PROFILE.workflow_label_definitions
            if definition.name not in existing
        ]
        for definition in missing:
            response = client.post(
                f"/repos/{repository}/labels",
                json={
                    "name": definition.name,
                    "color": definition.color,
                    "description": definition.description,
                },
            )
            response.raise_for_status()
        observed_payloads = _list(client, f"/repos/{repository}/labels")
        observed = {
            str(label.get("name", ""))
            for label in observed_payloads
            if label.get("name")
        }
        if not set(PROBARE_CRM_PROFILE.workflow_labels).issubset(observed):
            raise LiveActivationError("workflow_label_bootstrap_failed")
    return {
        "created_count": len(missing),
        "existing_count": len(existing & set(PROBARE_CRM_PROFILE.workflow_labels)),
        "repository_hash": hashlib.sha256(repository.encode()).hexdigest(),
        "required_label_count": len(PROBARE_CRM_PROFILE.workflow_labels),
        "status": "labels_ready",
    }


def _object(value: object, category: str = "workflow_state_invalid") -> dict[str, object]:
    if not isinstance(value, dict):
        raise LiveActivationError(category)
    return value


def _items(value: object, category: str = "workflow_state_invalid") -> list[object]:
    if not isinstance(value, list):
        raise LiveActivationError(category)
    return value


def _skill_hashes(value: object) -> dict[str, str]:
    skills: dict[str, str] = {}
    for raw_skill in _items(value):
        skill = _object(raw_skill)
        name = str(skill.get("name", ""))
        content_hash = str(skill.get("content_sha256", ""))
        if not name or re.fullmatch(r"[0-9a-f]{64}", content_hash) is None:
            raise LiveActivationError("skill_provenance_invalid")
        skills[name] = content_hash
    if not skills:
        raise LiveActivationError("skill_provenance_invalid")
    return dict(sorted(skills.items()))


def _verification_summary(
    workflow: dict[str, object], head_sha: str, verification_command: str
) -> dict[str, object]:
    repair = workflow.get("repair")
    if isinstance(repair, dict) and repair.get("status") == "verified":
        attempts = _items(repair.get("attempts"))
        if not attempts:
            raise LiveActivationError("deterministic_verification_missing")
        attempt = _object(attempts[-1])
        verification = _object(attempt.get("deterministic_verification"))
        if attempt.get("head_sha") != head_sha or verification.get("passed") is not True:
            raise LiveActivationError("deterministic_verification_missing")
        return {"checks": 1, "source": "repair"}

    implementation = _object(workflow.get("implementation"))
    result = _object(implementation.get("result"))
    checks = [
        _object(check)
        for check in _items(result.get("verification"))
        if _object(check).get("command") == verification_command
    ]
    if len(checks) != 1 or re.search(
        r"\b(?:pass(?:ed|es)?|exited\s+0|exit_code=0)\b",
        str(checks[0].get("observed", "")),
        flags=re.IGNORECASE,
    ) is None:
        raise LiveActivationError("deterministic_verification_missing")
    return {"checks": len(checks), "source": "implementation"}


def _review_summary(review: dict[str, object], head_sha: str) -> list[dict[str, object]]:
    if review.get("status") != "verified" or review.get("head_sha") != head_sha:
        raise LiveActivationError("review_not_verified")
    observed: dict[str, dict[str, object]] = {}
    for raw_result in _items(review.get("results")):
        result = _object(raw_result)
        axis = str(result.get("axis", ""))
        verdict = _object(result.get("verdict"))
        policy = _object(result.get("policy"))
        verdict_value = str(verdict.get("verdict", ""))
        if (
            axis not in {"requirements", "code", "architecture"}
            or verdict.get("axis") != axis
            or verdict.get("head_sha") != head_sha
            or verdict_value not in {"pass", "not_applicable"}
            or (axis == "requirements" and verdict_value != "pass")
            or policy.get("sandbox") != "read-only"
        ):
            raise LiveActivationError("review_not_verified")
        invocation_id = str(verdict.get("invocation_id", ""))
        if not invocation_id:
            raise LiveActivationError("review_not_verified")
        observed[axis] = {
            "axis": axis,
            "invocation_id": invocation_id,
            "model": str(policy.get("model", "")),
            "reasoning_effort": str(policy.get("reasoning_effort", "")),
            "skill_hashes": _skill_hashes(result.get("skills")),
            "verdict": verdict_value,
        }
    expected_axes = ("requirements", "code", "architecture")
    if set(observed) != set(expected_axes):
        raise LiveActivationError("review_not_verified")
    return [observed[axis] for axis in expected_axes]


def _evidence_summary(publication: dict[str, object], head_sha: str) -> dict[str, object]:
    body = str(publication.get("body", ""))
    if (
        f"## Behavioral Evidence — head `{head_sha}`" not in body
        or "| Criterion | Verdict | Observed interface | Expected result | Head |" not in body
    ):
        raise LiveActivationError("pull_request_evidence_incomplete")
    evidence = _items(publication.get("evidence"))
    screenshot_count = 0
    rest_artifact_count = 0
    correlated_log_count = 0
    for raw_item in evidence:
        item = _object(raw_item)
        observations = [_object(raw) for raw in _items(item.get("observations"))]
        if not observations or not any(
            observation.get("artifact") for observation in observations
        ):
            raise LiveActivationError("pull_request_evidence_incomplete")
        kind = str(item.get("kind", ""))
        phases = {
            str(observation.get("phase"))
            for observation in observations
            if observation.get("artifact")
        }
        if (
            (kind == "document" and "read_back" not in phases)
            or (kind == "ui" and "screenshot" not in phases)
            or (kind == "rest" and not {"request", "response", "read_back"}.issubset(phases))
        ):
            raise LiveActivationError("pull_request_evidence_incomplete")
        for observation in observations:
            phase = observation.get("phase")
            if phase == "screenshot" and observation.get("artifact"):
                screenshot_count += 1
            if phase in {"request", "response", "read_back"} and observation.get("artifact"):
                rest_artifact_count += 1
            if phase == "log" and observation.get("artifact") and observation.get("correlation_id"):
                correlated_log_count += 1
    if not evidence:
        raise LiveActivationError("pull_request_evidence_incomplete")
    return {
        "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
        "correlated_log_count": correlated_log_count,
        "criterion_count": len(evidence),
        "rest_artifact_count": rest_artifact_count,
        "screenshot_count": screenshot_count,
    }


def _capture_live_evidence(
    argv: Sequence[str],
    environment: Mapping[str, str],
    transport: httpx.BaseTransport | None,
) -> tuple[dict[str, object], dict[str, object]]:
    if len(argv) != 3 or not argv[1].isdigit() or int(argv[1]) <= 0:
        raise LiveActivationError("invalid_evidence_target")
    issue_number = int(argv[1])
    output_path = Path(argv[2]).expanduser().resolve()
    repository = _one_repository(environment)
    repository_root = Path(_required(environment, "PILOT_REPOSITORY_ROOT")).expanduser().resolve()
    if output_path.is_relative_to(repository_root):
        raise LiveActivationError("unsafe_evidence_path")
    port = environment.get("PILOT_PORT", "8788").strip() or "8788"
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        raise LiveActivationError("invalid_evidence_target")
    owner, name = repository.split("/", maxsplit=1)
    with httpx.Client(
        base_url=f"http://127.0.0.1:{port}",
        timeout=10,
        transport=transport,
    ) as local:
        response = local.get(f"/workflows/{owner}/{name}/issues/{issue_number}")
        response.raise_for_status()
        workflow = _object(response.json())

    delivery = _object(workflow.get("delivery"))
    run = _object(workflow.get("run"))
    checkpoint = _object(workflow.get("checkpoint"))
    checkpoint_values = _object(checkpoint.get("values"))
    implementation = _object(workflow.get("implementation"))
    publication = _object(workflow.get("draft_pull_request"))
    review = _object(workflow.get("review"))
    pull_request_identity = _object(publication.get("pull_request"))
    head_sha = str(publication.get("head_sha", ""))
    pull_request_number = pull_request_identity.get("number")
    if (
        publication.get("status") != "published"
        or implementation.get("status") != "completed"
        or re.fullmatch(r"[0-9a-f]{40}", head_sha) is None
        or not isinstance(pull_request_number, int)
        or pull_request_identity.get("draft") is not True
    ):
        raise LiveActivationError("workflow_not_published")

    with _github_client(environment, transport) as github:
        pull_response = github.get(f"/repos/{repository}/pulls/{pull_request_number}")
        pull_response.raise_for_status()
        pull_request = _object(pull_response.json(), "github_response_invalid")
        labels_response = github.get(f"/repos/{repository}/issues/{issue_number}/labels")
        labels_response.raise_for_status()
        label_payloads = _items(labels_response.json(), "github_response_invalid")
    pull_head = _object(pull_request.get("head"), "github_response_invalid").get("sha")
    if (
        pull_request.get("draft") is not True
        or pull_request.get("merged") is True
        or pull_request.get("merged_at") is not None
        or pull_head != head_sha
        or pull_request.get("body") != publication.get("body")
    ):
        raise LiveActivationError("pull_request_head_mismatch")
    labels = sorted(
        str(_object(label, "github_response_invalid").get("name", ""))
        for label in label_payloads
        if _object(label, "github_response_invalid").get("name")
    )
    projected_labels = {str(label) for label in _items(review.get("projected_labels"))}
    if (
        not {"verified", "awaiting-review"}.issubset(labels)
        or "agent-running" in labels
        or not {"verified", "awaiting-review"}.issubset(projected_labels)
        or "agent-running" in projected_labels
    ):
        raise LiveActivationError("workflow_labels_not_verified")

    policy = _object(implementation.get("policy"))
    manifest = {
        "adapter_version": REPOSITORY_ADAPTER_VERSION,
        "checkpoint_id": str(checkpoint.get("id", "")),
        "checkpoint_status": str(checkpoint_values.get("status", "")),
        "delivery_id": str(delivery.get("id", "")),
        "evidence": _evidence_summary(publication, head_sha),
        "head_sha": head_sha,
        "issue_number": issue_number,
        "labels": labels,
        "pull_request_number": pull_request_number,
        "repository_hash": hashlib.sha256(repository.encode()).hexdigest(),
        "reviews": _review_summary(review, head_sha),
        "run_id": str(run.get("id", "")),
        "schema_version": "1",
        "status": "verified",
        "verification": _verification_summary(
            workflow,
            head_sha,
            _required(environment, "PILOT_VERIFICATION_COMMAND"),
        ),
        "worker": {
            "model": str(policy.get("model", "")),
            "reasoning_effort": str(policy.get("reasoning_effort", "")),
            "skill_hashes": _skill_hashes(implementation.get("skills")),
        },
    }
    if not all(
        str(manifest[key]) for key in ("checkpoint_id", "delivery_id", "run_id")
    ):
        raise LiveActivationError("workflow_correlation_missing")
    serialized = json.dumps(manifest, separators=(",", ":"), sort_keys=True) + "\n"
    sensitive_values = tuple(
        value
        for name in ("GITHUB_TOKEN", "PILOT_INTERNAL_WEBHOOK_SECRET", "GITHUB_WEBHOOK_SECRET")
        if (value := environment.get(name, "").strip())
    )
    if contains_sensitive_text(serialized, sensitive_values):
        raise LiveActivationError("sensitive_evidence_rejected")
    output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(serialized)
    finally:
        os.chmod(output_path, 0o600)
    return manifest, {
        "head_sha": head_sha,
        "manifest_sha256": hashlib.sha256(serialized.encode()).hexdigest(),
        "status": "evidence_captured",
    }


def run_cli(
    argv: Sequence[str],
    *,
    environment: Mapping[str, str] | None = None,
    transport: httpx.BaseTransport | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    output = stdout or sys.stdout
    error_output = stderr or sys.stderr
    command = argv[0] if argv else ""
    if command not in {"capture-live-evidence", "ensure-live-labels", "live-readiness"}:
        print(json.dumps({"status": "invalid", "category": "invalid_command"}), file=error_output)
        return 64
    try:
        if command == "capture-live-evidence":
            _, result = _capture_live_evidence(argv, environment or {}, transport)
        elif len(argv) != 1:
            raise LiveActivationError("invalid_command")
        elif command == "live-readiness":
            result = _live_readiness(environment or {}, transport)
        else:
            result = _ensure_live_labels(environment or {}, transport)
    except LiveActivationError as exc:
        print(json.dumps({"status": "not_ready", "category": exc.category}), file=error_output)
        return 69
    except (httpx.HTTPError, OSError, UnicodeError, ValueError, TypeError):
        print(json.dumps({"status": "not_ready", "category": "external_check_failed"}), file=error_output)
        return 69
    print(json.dumps(result, separators=(",", ":"), sort_keys=True), file=output)
    return 0
