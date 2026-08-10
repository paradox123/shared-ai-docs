#!/usr/bin/env python3
"""Extract bounded, argument-free routing evidence from a resolver manifest."""

import argparse
from collections import OrderedDict
from itertools import islice
import json
from pathlib import Path
import re
import sys
from typing import Dict, Iterable, List, Optional, Tuple


SUMMARY_CHAR_LIMIT = 240
TOOL_NAME_LIMIT = 12
HEARTBEAT_GROUP_LIMIT = 12
SAFE_LABEL_CHAR_LIMIT = 120
DEFAULT_MAX_TOTAL_CHARS = 20_000
MIN_MAX_TOTAL_CHARS = 2_000
FINAL_PHASES = {"final", "final_answer"}

WRAPPER_PATTERNS = (
    re.compile(
        r"<recommended_plugins\b[^>]*>.*?</recommended_plugins\s*>",
        flags=re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"#\s*AGENTS\.md instructions for[^\n]*\s*"
        r"<INSTRUCTIONS\b[^>]*>.*?</INSTRUCTIONS\s*>",
        flags=re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"<environment_context\b[^>]*>.*?</environment_context\s*>",
        flags=re.IGNORECASE | re.DOTALL,
    ),
)
NESTED_TOOL_RE = re.compile(
    r"\btools\.([A-Za-z_][A-Za-z0-9_.-]*)\s*\("
)
HEARTBEAT_START_RE = re.compile(r"^\s*<heartbeat\b", re.IGNORECASE)
HEARTBEAT_OPEN_RE = re.compile(
    r"^\s*<heartbeat\b(?P<attributes>[^>]*)>",
    re.IGNORECASE | re.DOTALL,
)
HEARTBEAT_FIELDS = ("automation_id", "state", "decision", "status")
SAFE_HEARTBEAT_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")


class EvidenceError(Exception):
    """Raised when the manifest or one advertised evidence range is invalid."""


def bounded_text(value: object, limit: int) -> Optional[str]:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text[:limit] if text else None


def strip_injected_wrappers(text: str) -> str:
    cleaned = text
    for pattern in WRAPPER_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    return cleaned.strip()


def normalized_payload(record: dict) -> dict:
    raw_payload = record.get("payload", {})
    if not isinstance(raw_payload, dict):
        return {}
    nested = raw_payload.get("item")
    return nested if isinstance(nested, dict) else raw_payload


def message_text(payload: dict) -> str:
    content = payload.get("content", [])
    if isinstance(content, str):
        return content
    parts: List[str] = []
    if isinstance(content, list):
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
    if not parts and isinstance(payload.get("text"), str):
        parts.append(payload["text"])
    return " ".join(parts)


def normalized_heartbeat_key(raw: str) -> Optional[str]:
    value = raw.lower().replace("-", "_")
    if value == "automationid":
        value = "automation_id"
    return value if value in HEARTBEAT_FIELDS else None


def safe_heartbeat_label(value: object) -> Optional[str]:
    label = bounded_text(value, SAFE_LABEL_CHAR_LIMIT)
    if label is None:
        return None
    return label if SAFE_HEARTBEAT_LABEL_RE.fullmatch(label) else "[redacted]"


def heartbeat_values(text: str) -> Tuple[Optional[str], ...]:
    values: Dict[str, object] = {}
    opening = HEARTBEAT_OPEN_RE.match(text)
    attributes = opening.group("attributes") if opening else ""
    attribute_re = re.compile(
        r"\b(automation[_-]?id|automationId|state|decision|status)\s*=\s*"
        r"(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
        re.IGNORECASE,
    )
    for match in attribute_re.finditer(attributes):
        key = normalized_heartbeat_key(match.group(1))
        if key:
            values[key] = next(
                group for group in match.groups()[1:] if group is not None
            )

    for key in HEARTBEAT_FIELDS:
        aliases = [key]
        if key == "automation_id":
            aliases.extend(("automation-id", "automationId"))
        alias_pattern = "|".join(re.escape(alias) for alias in aliases)
        match = re.search(
            rf"<(?P<key>{alias_pattern})\b[^>]*>(?P<value>.*?)"
            rf"</(?P=key)\s*>",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if match:
            values[key] = match.group("value")

    object_start = text.find("{")
    object_end = text.rfind("}")
    if object_start >= 0 and object_end > object_start:
        try:
            parsed = json.loads(text[object_start : object_end + 1])
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            heartbeat_object = parsed.get("heartbeat")
            if isinstance(heartbeat_object, dict):
                parsed = heartbeat_object
            for raw_key, value in parsed.items():
                key = normalized_heartbeat_key(str(raw_key))
                if key and value is not None:
                    values[key] = value

    for key in HEARTBEAT_FIELDS:
        if key in values:
            continue
        aliases = [key]
        if key == "automation_id":
            aliases.extend(("automation-id", "automationId"))
        alias_pattern = "|".join(re.escape(alias) for alias in aliases)
        match = re.search(
            rf"(?:^|[\s,;{{])(?:{alias_pattern})\s*[:=]\s*"
            r"([^\s,;}<>]+)",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            values[key] = match.group(1).strip("\"'")

    return tuple(safe_heartbeat_label(values.get(key)) for key in HEARTBEAT_FIELDS)


def heartbeat_group(
    key: Tuple[Optional[str], ...], line_number: int
) -> dict:
    group = {
        field: value for field, value in zip(HEARTBEAT_FIELDS, key)
    }
    group.update(
        {
            "count": 1,
            "first_line": line_number,
            "last_line": line_number,
        }
    )
    return group


def normalized_tool_names(payload: dict) -> List[str]:
    item_type = payload.get("type")
    if item_type == "function_call":
        name = bounded_text(payload.get("name"), SAFE_LABEL_CHAR_LIMIT)
        return [name] if name else ["unknown"]
    if item_type != "custom_tool_call":
        return []
    recorder_input = payload.get("input")
    nested = (
        NESTED_TOOL_RE.findall(recorder_input)
        if isinstance(recorder_input, str)
        else []
    )
    if nested:
        return [name[:SAFE_LABEL_CHAR_LIMIT] for name in nested]
    recorder = bounded_text(payload.get("name"), SAFE_LABEL_CHAR_LIMIT)
    return [f"recorder:{recorder or 'unknown'}"]


def valid_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def session_range(session: dict, index: int) -> Tuple[int, int, list]:
    rollout_window = session.get("rollout_window")
    if not isinstance(rollout_window, dict):
        raise EvidenceError(
            f"resolved session {index} has no rollout_window object"
        )
    start = rollout_window.get("review_line_start")
    end = rollout_window.get("review_line_end")
    if not valid_integer(start) or not valid_integer(end):
        raise EvidenceError(
            f"resolved session {index} has non-integer review line bounds"
        )
    if start < 1 or end < 0 or end < start - 1:
        raise EvidenceError(
            f"resolved session {index} has invalid review range {start}:{end}"
        )
    embedded = rollout_window.get("embedded_session_metas", [])
    if not isinstance(embedded, list):
        raise EvidenceError(
            f"resolved session {index} has invalid embedded_session_metas"
        )
    return start, end, embedded


def rollout_path(session: dict, index: int, manifest_dir: Path) -> Path:
    raw_path = session.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise EvidenceError(f"resolved session {index} has no valid path")
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = manifest_dir / path
    if not path.is_file():
        raise EvidenceError(
            f"resolved session {index} path is not a readable file: {path}"
        )
    return path


def advertised_lines(
    path: Path, start: int, end: int
) -> Iterable[Tuple[int, str]]:
    expected = max(end - start + 1, 0)
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            if expected == 0:
                physical_line_count = sum(1 for _line in handle)
                if end > physical_line_count or start > physical_line_count + 1:
                    raise EvidenceError(
                        f"advertised empty range {start}:{end} exceeds {path}"
                    )
                return
            selected_count = 0
            for line_number, line in enumerate(
                islice(handle, start - 1, end),
                start=start,
            ):
                selected_count += 1
                yield line_number, line
    except OSError as exc:
        raise EvidenceError(f"could not read rollout path {path}: {exc}") from exc
    if selected_count != expected:
        raise EvidenceError(
            f"advertised range {start}:{end} exceeds rollout path {path}"
        )
    return


def safe_session_identity(session: dict, index: int) -> Tuple[str, Optional[str]]:
    raw_id = session.get("id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise EvidenceError(f"resolved session {index} has no valid id")
    session_id = bounded_text(raw_id, SAFE_LABEL_CHAR_LIMIT)
    thread_name = bounded_text(session.get("thread_name"), SUMMARY_CHAR_LIMIT)
    return session_id or f"session-{index}", thread_name


def manual_projection(
    session: dict,
    index: int,
    start: int,
    end: int,
    embedded: list,
) -> dict:
    session_id, thread_name = safe_session_identity(session, index)
    embedded_ids: List[str] = []
    for meta in embedded:
        if not isinstance(meta, dict):
            continue
        embedded_id = bounded_text(meta.get("id"), SAFE_LABEL_CHAR_LIMIT)
        if embedded_id and embedded_id not in embedded_ids:
            embedded_ids.append(embedded_id)
        if len(embedded_ids) == 8:
            break
    return {
        "id": session_id,
        "thread_name": thread_name,
        "rollout_state": bounded_text(
            session.get("rollout_window", {}).get("state"),
            SAFE_LABEL_CHAR_LIMIT,
        ),
        "review_line_start": start,
        "review_line_end": end,
        "manual_suffix_selection_required": True,
        "embedded_session_meta_count": len(embedded),
        "embedded_session_ids": embedded_ids,
        "counts": {
            "advertised_lines": max(end - start + 1, 0),
            "inspected_lines": 0,
        },
        "user_summary": None,
        "tool_names": [],
        "final_summary": None,
        "heartbeat_groups": [],
    }


def extract_session(
    session: dict,
    index: int,
    path: Path,
    start: int,
    end: int,
) -> dict:
    session_id, thread_name = safe_session_identity(session, index)
    user_summary: Optional[str] = None
    last_final: Optional[str] = None
    tool_names: List[str] = []
    heartbeat_groups: "OrderedDict[Tuple[Optional[str], ...], dict]" = (
        OrderedDict()
    )
    counts = {
        "advertised_lines": max(end - start + 1, 0),
        "inspected_lines": 0,
        "response_items": 0,
        "user_messages": 0,
        "substantive_user_messages": 0,
        "heartbeat_messages": 0,
        "heartbeat_messages_omitted_from_groups": 0,
        "assistant_final_messages": 0,
        "tool_calls": 0,
        "tool_names_omitted": 0,
    }

    for line_number, raw_line in advertised_lines(path, start, end):
        counts["inspected_lines"] += 1
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise EvidenceError(
                f"invalid rollout JSON at {path}:{line_number}: {exc.msg}"
            ) from exc
        if not isinstance(record, dict):
            raise EvidenceError(
                f"rollout record at {path}:{line_number} is not an object"
            )
        if record.get("type") != "response_item":
            continue
        counts["response_items"] += 1
        payload = normalized_payload(record)
        item_type = payload.get("type")

        if item_type == "message" and payload.get("role") == "user":
            counts["user_messages"] += 1
            cleaned = strip_injected_wrappers(message_text(payload))
            if not cleaned:
                continue
            if HEARTBEAT_START_RE.match(cleaned):
                counts["heartbeat_messages"] += 1
                key = heartbeat_values(cleaned)
                if key in heartbeat_groups:
                    group = heartbeat_groups[key]
                    group["count"] += 1
                    group["last_line"] = line_number
                elif len(heartbeat_groups) < HEARTBEAT_GROUP_LIMIT:
                    heartbeat_groups[key] = heartbeat_group(key, line_number)
                else:
                    counts["heartbeat_messages_omitted_from_groups"] += 1
                continue
            counts["substantive_user_messages"] += 1
            if user_summary is None:
                user_summary = bounded_text(cleaned, SUMMARY_CHAR_LIMIT)
            continue

        if (
            item_type == "message"
            and payload.get("role") == "assistant"
            and payload.get("phase") in FINAL_PHASES
        ):
            counts["assistant_final_messages"] += 1
            final_text = bounded_text(
                message_text(payload), SUMMARY_CHAR_LIMIT
            )
            if final_text:
                last_final = final_text
            continue

        names = normalized_tool_names(payload)
        if not names:
            continue
        counts["tool_calls"] += len(names)
        remaining = max(TOOL_NAME_LIMIT - len(tool_names), 0)
        tool_names.extend(names[:remaining])
        counts["tool_names_omitted"] += max(len(names) - remaining, 0)

    return {
        "id": session_id,
        "thread_name": thread_name,
        "rollout_state": bounded_text(
            session.get("rollout_window", {}).get("state"),
            SAFE_LABEL_CHAR_LIMIT,
        ),
        "review_line_start": start,
        "review_line_end": end,
        "manual_suffix_selection_required": False,
        "counts": counts,
        "user_summary": user_summary,
        "tool_names": tool_names,
        "final_summary": last_final,
        "heartbeat_groups": list(heartbeat_groups.values()),
    }


def parse_max_total_chars(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value < MIN_MAX_TOTAL_CHARS:
        raise argparse.ArgumentTypeError(
            f"must be at least {MIN_MAX_TOTAL_CHARS}"
        )
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract bounded summaries, normalized tool names, and heartbeat "
            "counts from a resolve_codex_sessions.py manifest."
        )
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--session-id",
        action="append",
        default=[],
        help=(
            "Exact manifest session id to inspect; may be repeated. "
            "Unknown or unresolved requested ids fail closed."
        ),
    )
    parser.add_argument(
        "--max-total-chars",
        type=parse_max_total_chars,
        default=DEFAULT_MAX_TOTAL_CHARS,
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON; minified JSON is the default.",
    )
    return parser.parse_args()


def serialize(output: dict, pretty: bool) -> str:
    if pretty:
        return json.dumps(output, indent=2, ensure_ascii=False)
    return json.dumps(output, ensure_ascii=False, separators=(",", ":"))


def output_document(
    projections: List[dict],
    emitted: List[dict],
    manifest_session_count: int,
    selected_session_count: int,
    filtered_out_session_count: int,
    skipped_unresolved_count: int,
) -> dict:
    omitted = len(projections) - len(emitted)
    return {
        "schema_version": 1,
        "counts": {
            "manifest_sessions": manifest_session_count,
            "selected_sessions": selected_session_count,
            "filtered_out_sessions": filtered_out_session_count,
            "resolved_sessions": len(projections),
            "skipped_unresolved_sessions": skipped_unresolved_count,
            "emitted_sessions": len(emitted),
            "omitted_sessions": omitted,
        },
        "omitted_sessions": {
            "count": omitted,
            "reason": "max_total_chars" if omitted else None,
        },
        "sessions": emitted,
    }


def fit_output(
    projections: List[dict],
    manifest_session_count: int,
    selected_session_count: int,
    filtered_out_session_count: int,
    skipped_unresolved_count: int,
    max_total_chars: int,
    pretty: bool,
) -> str:
    emitted: List[dict] = []
    for projection in projections:
        candidate = emitted + [projection]
        document = output_document(
            projections,
            candidate,
            manifest_session_count,
            selected_session_count,
            filtered_out_session_count,
            skipped_unresolved_count,
        )
        if len(serialize(document, pretty)) <= max_total_chars:
            emitted = candidate

    document = output_document(
        projections,
        emitted,
        manifest_session_count,
        selected_session_count,
        filtered_out_session_count,
        skipped_unresolved_count,
    )
    rendered = serialize(document, pretty)
    while len(rendered) > max_total_chars and emitted:
        emitted.pop()
        document = output_document(
            projections,
            emitted,
            manifest_session_count,
            selected_session_count,
            filtered_out_session_count,
            skipped_unresolved_count,
        )
        rendered = serialize(document, pretty)
    if len(rendered) > max_total_chars:
        raise EvidenceError(
            "max-total-chars is too small for the bounded output envelope"
        )
    return rendered


def load_manifest(path: Path) -> dict:
    if not path.is_file():
        raise EvidenceError(f"manifest is not a readable file: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise EvidenceError(f"could not read manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError(
            f"manifest is not valid JSON at line {exc.lineno}: {exc.msg}"
        ) from exc
    if not isinstance(manifest, dict):
        raise EvidenceError("manifest root must be an object")
    sessions = manifest.get("sessions")
    if not isinstance(sessions, list):
        raise EvidenceError("manifest sessions must be an array")
    return manifest


def run(args: argparse.Namespace) -> str:
    manifest_path = args.manifest.expanduser()
    manifest = load_manifest(manifest_path)
    sessions = manifest["sessions"]
    for index, session in enumerate(sessions, start=1):
        if not isinstance(session, dict):
            raise EvidenceError(f"manifest session {index} is not an object")

    requested_ids = list(dict.fromkeys(args.session_id))
    if any(not isinstance(value, str) or not value for value in requested_ids):
        raise EvidenceError("requested session ids must be non-empty strings")
    selected_indexes: Optional[set] = None
    if requested_ids:
        indexes_by_id: Dict[str, List[int]] = {}
        for index, session in enumerate(sessions):
            session_id = session.get("id")
            if isinstance(session_id, str):
                indexes_by_id.setdefault(session_id, []).append(index)
        unknown_ids = [
            session_id
            for session_id in requested_ids
            if session_id not in indexes_by_id
        ]
        if unknown_ids:
            rendered_ids = ", ".join(
                value[:SAFE_LABEL_CHAR_LIMIT] for value in unknown_ids[:8]
            )
            if len(unknown_ids) > 8:
                rendered_ids += f", ... ({len(unknown_ids) - 8} more)"
            raise EvidenceError(f"unknown requested session id(s): {rendered_ids}")
        ambiguous_ids = [
            session_id
            for session_id in requested_ids
            if len(indexes_by_id[session_id]) != 1
        ]
        if ambiguous_ids:
            rendered_ids = ", ".join(
                value[:SAFE_LABEL_CHAR_LIMIT] for value in ambiguous_ids[:8]
            )
            if len(ambiguous_ids) > 8:
                rendered_ids += f", ... ({len(ambiguous_ids) - 8} more)"
            raise EvidenceError(
                f"duplicate requested session id(s) in manifest: {rendered_ids}"
            )
        selected_indexes = {
            indexes_by_id[session_id][0] for session_id in requested_ids
        }
        unresolved_ids = [
            session_id
            for session_id in requested_ids
            if sessions[indexes_by_id[session_id][0]].get("status")
            != "resolved"
        ]
        if unresolved_ids:
            rendered_ids = ", ".join(
                value[:SAFE_LABEL_CHAR_LIMIT] for value in unresolved_ids[:8]
            )
            if len(unresolved_ids) > 8:
                rendered_ids += f", ... ({len(unresolved_ids) - 8} more)"
            raise EvidenceError(
                f"requested session id(s) are not resolved: {rendered_ids}"
            )

    projections: List[dict] = []
    skipped_unresolved_count = 0
    for index, session in enumerate(sessions, start=1):
        if selected_indexes is not None and index - 1 not in selected_indexes:
            continue
        if session.get("status") != "resolved":
            skipped_unresolved_count += 1
            continue
        start, end, embedded = session_range(session, index)
        path = rollout_path(session, index, manifest_path.parent)
        if embedded:
            # Validate the path/range, but do not parse or summarize a rollout
            # whose imported-history boundary still needs human selection.
            for _line_number, _line in advertised_lines(path, start, end):
                pass
            projections.append(
                manual_projection(session, index, start, end, embedded)
            )
            continue
        projections.append(
            extract_session(session, index, path, start, end)
        )
    return fit_output(
        projections,
        len(sessions),
        len(selected_indexes) if selected_indexes is not None else len(sessions),
        len(sessions) - (
            len(selected_indexes) if selected_indexes is not None else len(sessions)
        ),
        skipped_unresolved_count,
        args.max_total_chars,
        args.pretty,
    )


def main() -> int:
    args = parse_args()
    try:
        rendered = run(args)
    except EvidenceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
