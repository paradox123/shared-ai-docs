from __future__ import annotations

import re
from collections.abc import Sequence

from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator

from github_issue_pilot.contracts import load_contract


class EvidenceRejected(ValueError):
    pass


_REQUIRED_PHASES = {
    "rest": frozenset({"request", "response", "read_back"}),
    "ui": frozenset({"interaction", "screenshot"}),
    "recovery": frozenset({"restart", "read_back"}),
    "idempotency": frozenset({"repeat", "read_back"}),
    "negative_gate": frozenset({"rejection", "side_effect_read_back"}),
    "background": frozenset({"eventual_result"}),
}
_ARTIFACT_PHASES = frozenset(
    {"request", "response", "read_back", "screenshot", "side_effect_read_back", "eventual_result", "log"}
)
_SURROGATE_PATTERN = re.compile(
    r"(?i)\b(?:build passed|process started|container (?:is )?running|health ?check|"
    r"http 2\d\d|2xx|queue accepted|enqueued|static (?:initial|starting) screenshot|"
    r"log (?:message|says?)[^;.\n]*)\b"
)
_EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_AUTHORIZATION_PATTERN = re.compile(r"(?i)\bauthorization\s*:\s*(?:bearer|token)\s+\S+")
_GITHUB_TOKEN_PATTERN = re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")
_CREDENTIAL_PATTERN = re.compile(
    r"(?i)\b(?:token|secret|password|api[_-]?key)\s*[=:]\s*[^\s,;]+"
)
_HEAD_SHA_PATTERN = re.compile(r"[0-9a-f]{40}")


def qualify_evidence(
    requirements: Sequence[str],
    result: dict[str, object],
    *,
    sensitive_values: Sequence[str] = (),
) -> list[dict[str, object]]:
    try:
        Draft202012Validator(load_contract("worker-result-v2.json")).validate(result)
    except ValidationError as exc:
        raise EvidenceRejected("schema_invalid") from exc
    if result["outcome"] != "completed":
        raise EvidenceRejected("implementation_not_completed")

    raw_evidence = result["evidence"]
    if not isinstance(raw_evidence, list):
        raise EvidenceRejected("schema_invalid")
    criteria = [item["criterion"] for item in raw_evidence]
    if len(criteria) != len(set(criteria)) or sorted(criteria) != sorted(requirements):
        raise EvidenceRejected("criterion_coverage")

    for item in raw_evidence:
        if item["verdict"] != "pass":
            raise EvidenceRejected("criterion_verdict")
        observations = item["observations"]
        phases = {observation["phase"] for observation in observations}
        required = _REQUIRED_PHASES[str(item["kind"])]
        if not required.issubset(phases):
            raise EvidenceRejected("missing_direct_observation")
        for observation in observations:
            phase = str(observation["phase"])
            if phase in _ARTIFACT_PHASES and not observation.get("artifact"):
                raise EvidenceRejected("missing_embedded_artifact")
            if phase == "log" and not observation.get("correlation_id"):
                raise EvidenceRejected("uncorrelated_log")
        direct_text = " ".join(
            f"{observation['description']} {observation.get('artifact', '')}"
            for observation in observations
            if observation["phase"] in required
        )
        meaningful_remainder = _SURROGATE_PATTERN.sub(" ", direct_text)
        if len(re.sub(r"[^A-Za-z]+", "", meaningful_remainder)) < 4:
            raise EvidenceRejected("infrastructure_surrogate")

    return [_redact_value(item, sensitive_values) for item in raw_evidence]


def render_pull_request_body(
    *,
    issue_number: int,
    head_sha: str,
    evidence: Sequence[dict[str, object]],
    repair_attempts: Sequence[dict[str, object]] = (),
    open_findings: Sequence[dict[str, object]] = (),
) -> str:
    if _HEAD_SHA_PATTERN.fullmatch(head_sha) is None:
        raise ValueError("head SHA must be a 40-character lowercase hexadecimal commit id")
    lines = [
        f"## Behavioral Evidence — head `{head_sha}`",
        "",
        "| Criterion | Verdict | Observed interface | Expected result | Head |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in evidence:
        lines.append(
            "| "
            + " | ".join(
                (
                    _table_text(str(item["criterion"])),
                    str(item["verdict"]),
                    _table_text(str(item["observed_interface"])),
                    _table_text(str(item["expected_result"])),
                    f"`{head_sha}`",
                )
            )
            + " |"
        )

    for index, item in enumerate(evidence, start=1):
        criterion = str(item["criterion"])
        lines.extend(
            (
                "",
                f"### {index}. {criterion}",
                "",
                f"- Verdict: `{item['verdict']}`",
                f"- Observed interface: {item['observed_interface']}",
                f"- Expected result: {item['expected_result']}",
                f"- Published head: `{head_sha}`",
            )
        )
        for observation in item["observations"]:
            correlation = (
                f" (correlation `{observation['correlation_id']}`)"
                if observation.get("correlation_id")
                else ""
            )
            lines.extend(
                (
                    "",
                    f"- **{observation['phase']}** — {observation['description']}{correlation}",
                )
            )
            artifact = observation.get("artifact")
            if artifact and observation["phase"] == "screenshot":
                lines.extend(("", f"![Evidence: {criterion}]({artifact})"))
            elif artifact:
                lines.extend(("", "```text", str(artifact), "```"))

    if repair_attempts:
        lines.extend(
            (
                "",
                "## Repair Attempts",
                "",
                "| Round | Status | Head | Summary |",
                "| --- | --- | --- | --- |",
            )
        )
        for attempt in repair_attempts:
            attempt_head = attempt.get("head_sha") or "not published"
            head_cell = (
                f"`{attempt_head}`"
                if _HEAD_SHA_PATTERN.fullmatch(str(attempt_head))
                else _table_text(str(attempt_head))
            )
            lines.append(
                "| "
                + " | ".join(
                    (
                        str(attempt.get("round", "?")),
                        _table_text(str(attempt.get("status", "unknown"))),
                        head_cell,
                        _table_text(str(attempt.get("summary", "Repair attempt"))),
                    )
                )
                + " |"
            )
    if open_findings:
        lines.extend(("", "## Open Findings", ""))
        for finding in open_findings:
            lines.append(
                "- "
                f"**{finding.get('axis', 'repair')}** at "
                f"`{finding.get('location', 'unspecified')}`: "
                f"{finding.get('description', 'Unresolved finding')}"
            )

    lines.extend(("", f"Closes #{issue_number}"))
    body = "\n".join(lines) + "\n"
    if len(body.encode("utf-8")) > 60_000:
        raise EvidenceRejected("pull_request_body_too_large")
    return body


def redact_text(value: str, sensitive_values: Sequence[str] = ()) -> str:
    redacted = value
    for sensitive in sorted((item for item in sensitive_values if item), key=len, reverse=True):
        redacted = redacted.replace(sensitive, "[REDACTED]")
    for pattern in (
        _AUTHORIZATION_PATTERN,
        _GITHUB_TOKEN_PATTERN,
        _EMAIL_PATTERN,
        _CREDENTIAL_PATTERN,
    ):
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def contains_sensitive_text(value: str, sensitive_values: Sequence[str] = ()) -> bool:
    if any(sensitive and sensitive in value for sensitive in sensitive_values):
        return True
    return any(
        pattern.search(value)
        for pattern in (
            _AUTHORIZATION_PATTERN,
            _GITHUB_TOKEN_PATTERN,
            _EMAIL_PATTERN,
            _CREDENTIAL_PATTERN,
        )
    )


def redact_payload(value: object, sensitive_values: Sequence[str] = ()) -> object:
    return _redact_value(value, sensitive_values)


def _redact_value(value: object, sensitive_values: Sequence[str]) -> object:
    if isinstance(value, str):
        return redact_text(value, sensitive_values)
    if isinstance(value, list):
        return [_redact_value(item, sensitive_values) for item in value]
    if isinstance(value, dict):
        return {key: _redact_value(item, sensitive_values) for key, item in value.items()}
    return value


def _table_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
