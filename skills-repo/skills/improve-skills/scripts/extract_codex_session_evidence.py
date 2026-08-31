#!/usr/bin/env python3
"""Extract bounded session evidence from a resolver manifest."""

import argparse
import ast
from collections import OrderedDict
from itertools import islice
import json
import os
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
BOUNDARY_LINE_LIMIT = 64
TOOL_COMMAND_CHAR_LIMIT = 600
TOOL_CWD_CHAR_LIMIT = 240
TOOL_RESULT_PARSE_CHAR_LIMIT = 4_000
FINAL_PHASES = {"final", "final_answer"}
SAFE_TOOL_STATUSES = {
    "cancelled",
    "completed",
    "error",
    "failed",
    "interrupted",
    "running",
    "success",
    "timed_out",
    "timeout",
}

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
    r"(?<![A-Za-z0-9_$?.])tools\.([A-Za-z_][A-Za-z0-9_.-]*)\s*\("
)
TOOLS_IDENTIFIER_RE = re.compile(
    r"(?<![A-Za-z0-9_$])tools(?![A-Za-z0-9_$])"
)
HEARTBEAT_START_RE = re.compile(r"^\s*<heartbeat\b", re.IGNORECASE)
HEARTBEAT_OPEN_RE = re.compile(
    r"^\s*<heartbeat\b(?P<attributes>[^>]*)>",
    re.IGNORECASE | re.DOTALL,
)
HEARTBEAT_FIELDS = ("automation_id", "state", "decision", "status")
SAFE_HEARTBEAT_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
WORKTREE_TAIL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
STRUCTURAL_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]*$")
SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"\b(?P<key>[A-Za-z_][A-Za-z0-9_]*(?:token|secret|password|pass|"
    r"api[_-]?key|authorization|auth|credential)[A-Za-z0-9_]*)"
    r"\s*=\s*(?:\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*'|[^\s;&|]+)",
    re.IGNORECASE,
)
SENSITIVE_FLAG_RE = re.compile(
    r"(?P<flag>--(?:token|secret|password|pass|api[_-]?key|"
    r"authorization|auth|credential))(?:\s*=\s*|\s+)"
    r"(?:\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*'|[^\s;&|]+)",
    re.IGNORECASE,
)
AUTHORIZATION_VALUE_RE = re.compile(
    r"(?P<prefix>authorization\s*:\s*(?:bearer|basic)\s+)"
    r"[^\s'\"]+",
    re.IGNORECASE,
)


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


def nested_tool_scan(
    value: object,
) -> Tuple[List[Tuple[str, int]], bool]:
    """Return canonical calls and flag any indirect `tools` reference."""
    if not isinstance(value, str):
        return [], False
    occurrences: List[Tuple[str, int]] = []
    ambiguous = False
    index = 0
    while index < len(value):
        if value[index] == "`":
            expression_ranges, next_index = js_template_expression_ranges(
                value, index
            )
            for expression_start, expression_end in expression_ranges:
                nested, nested_ambiguous = nested_tool_scan(
                    value[expression_start:expression_end]
                )
                ambiguous = ambiguous or nested_ambiguous
                for name, call_end in nested:
                    occurrences.append(
                        (name, expression_start + call_end)
                    )
            index = max(index + 1, next_index)
            continue
        if value[index] in {'"', "'"}:
            _string_value, next_index = js_string_literal(value, index)
            index = max(index + 1, next_index)
            continue
        if value.startswith("//", index):
            newline = value.find("\n", index + 2)
            index = len(value) if newline < 0 else newline + 1
            continue
        if value.startswith("/*", index):
            comment_end = value.find("*/", index + 2)
            index = len(value) if comment_end < 0 else comment_end + 2
            continue
        if value[index] == "/" and js_regex_can_start(value, index):
            regex_end = js_regex_literal_end(value, index)
            if regex_end is not None:
                index = regex_end
                continue
        match = NESTED_TOOL_RE.match(value, index)
        if match:
            occurrences.append(
                (match.group(1)[:SAFE_LABEL_CHAR_LIMIT], match.end())
            )
            index = match.end()
            continue
        reference = TOOLS_IDENTIFIER_RE.match(value, index)
        if reference:
            ambiguous = True
            index = reference.end()
            continue
        index += 1
    return occurrences, ambiguous


def nested_tool_occurrences(value: object) -> List[Tuple[str, int]]:
    occurrences, _ambiguous = nested_tool_scan(value)
    return occurrences


def normalized_tool_names(payload: dict) -> List[str]:
    item_type = payload.get("type")
    if item_type == "function_call":
        name = bounded_text(payload.get("name"), SAFE_LABEL_CHAR_LIMIT)
        return [name] if name else ["unknown"]
    if item_type != "custom_tool_call":
        return []
    nested = nested_tool_occurrences(payload.get("input"))
    if nested:
        return [name for name, _call_end in nested]
    recorder = bounded_text(payload.get("name"), SAFE_LABEL_CHAR_LIMIT)
    return [f"recorder:{recorder or 'unknown'}"]


def structural_label(value: object) -> Optional[str]:
    """Return one bounded machine label without rendering arbitrary content."""
    if not isinstance(value, str):
        return None
    label = value.strip()[:SAFE_LABEL_CHAR_LIMIT]
    if not label:
        return None
    return label if STRUCTURAL_LABEL_RE.fullmatch(label) else "[redacted]"


def structural_record(record: dict, line_number: int) -> dict:
    """Project one rollout record without reading content-bearing fields."""
    raw_payload = record.get("payload")
    payload = normalized_payload(record)
    payload_type = payload.get("type")
    tool_name = None
    if payload_type in {"function_call", "custom_tool_call"}:
        tool_name = structural_label(payload.get("name"))

    record_session_id = None
    if record.get("type") == "session_meta" and isinstance(raw_payload, dict):
        record_session_id = structural_label(
            raw_payload.get("id") or raw_payload.get("session_id")
        )

    return {
        "line_number": line_number,
        "record_type": structural_label(record.get("type")),
        "payload_type": structural_label(payload_type),
        "role": structural_label(payload.get("role")),
        "phase": structural_label(payload.get("phase")),
        "tool_name": tool_name,
        "session_id": record_session_id,
    }


def normalize_home_path(text: str) -> str:
    home = str(Path.home())
    return re.sub(rf"{re.escape(home)}(?=/|$)", "~", text)


def sanitized_command(value: object) -> Optional[str]:
    if not isinstance(value, str):
        return None
    text = normalize_home_path(strip_injected_wrappers(value))
    text = SENSITIVE_ASSIGNMENT_RE.sub(
        lambda match: f"{match.group('key')}=[redacted]", text
    )
    text = SENSITIVE_FLAG_RE.sub(
        lambda match: f"{match.group('flag')} [redacted]", text
    )
    text = AUTHORIZATION_VALUE_RE.sub(
        lambda match: f"{match.group('prefix')}[redacted]", text
    )
    return bounded_text(text, TOOL_COMMAND_CHAR_LIMIT)


def sanitized_cwd(value: object) -> Optional[str]:
    if not isinstance(value, str):
        return None
    return bounded_text(
        normalize_home_path(strip_injected_wrappers(value)),
        TOOL_CWD_CHAR_LIMIT,
    )


def json_object(value: object) -> Optional[dict]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or len(value) > TOOL_RESULT_PARSE_CHAR_LIMIT:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def js_string_literal(source: str, start: int) -> Tuple[Optional[str], int]:
    if start >= len(source) or source[start] not in {'"', "'", "`"}:
        return None, start
    quote = source[start]
    escaped = False
    for index in range(start + 1, len(source)):
        character = source[index]
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character != quote:
            continue
        raw = source[start : index + 1]
        try:
            if quote == '"':
                value = json.loads(raw)
            elif quote == "'":
                value = ast.literal_eval(raw)
            elif "${" not in raw:
                value = raw[1:-1].replace("\\`", "`").replace("\\\\", "\\")
            else:
                value = None
        except (ValueError, SyntaxError, json.JSONDecodeError):
            value = None
        return value if isinstance(value, str) else None, index + 1
    return None, len(source)


def js_regex_can_start(source: str, start: int) -> bool:
    index = start - 1
    while index >= 0 and source[index].isspace():
        index -= 1
    if index < 0:
        return True
    if source[index] in "([{:;,=!?&|+-*%^~<>":
        return True
    prefix = source[: index + 1]
    match = re.search(r"([A-Za-z_$][A-Za-z0-9_$]*)$", prefix)
    if not match or match.group(1) not in {
        "await",
        "case",
        "delete",
        "do",
        "else",
        "in",
        "instanceof",
        "new",
        "of",
        "return",
        "throw",
        "typeof",
        "void",
        "yield",
    }:
        return False
    before_word = match.start(1) - 1
    while before_word >= 0 and source[before_word].isspace():
        before_word -= 1
    return before_word < 0 or source[before_word] not in ".$?"


def js_regex_literal_end(source: str, start: int) -> Optional[int]:
    if start >= len(source) or source[start] != "/":
        return None
    escaped = False
    in_character_class = False
    for index in range(start + 1, len(source)):
        character = source[index]
        if character in "\r\n":
            return None
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == "[":
            in_character_class = True
            continue
        if character == "]" and in_character_class:
            in_character_class = False
            continue
        if character == "/" and not in_character_class:
            next_index = index + 1
            while next_index < len(source) and source[next_index].isalpha():
                next_index += 1
            return next_index
    return None


def js_template_expression_end(source: str, start: int) -> Optional[int]:
    depth = 1
    index = start
    while index < len(source):
        if source[index] in {'"', "'"}:
            _value, index = js_string_literal(source, index)
            continue
        if source[index] == "`":
            _ranges, next_index = js_template_expression_ranges(source, index)
            if next_index <= index or next_index > len(source):
                return None
            index = next_index
            continue
        if source.startswith("//", index):
            newline = source.find("\n", index + 2)
            index = len(source) if newline < 0 else newline + 1
            continue
        if source.startswith("/*", index):
            comment_end = source.find("*/", index + 2)
            if comment_end < 0:
                return None
            index = comment_end + 2
            continue
        if source[index] == "/" and js_regex_can_start(source, index):
            regex_end = js_regex_literal_end(source, index)
            if regex_end is None:
                return None
            index = regex_end
            continue
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def js_template_expression_ranges(
    source: str, start: int
) -> Tuple[List[Tuple[int, int]], int]:
    if start >= len(source) or source[start] != "`":
        return [], start
    ranges: List[Tuple[int, int]] = []
    index = start + 1
    while index < len(source):
        if source[index] == "\\":
            index += 2
            continue
        if source[index] == "`":
            return ranges, index + 1
        if source.startswith("${", index):
            expression_start = index + 2
            expression_end = js_template_expression_end(
                source, expression_start
            )
            if expression_end is None:
                return [], len(source)
            ranges.append((expression_start, expression_end))
            index = expression_end + 1
            continue
        index += 1
    return [], len(source)


def skip_js_value(source: str, start: int) -> int:
    pairs = {"{": "}", "[": "]", "(": ")"}
    closing: List[str] = []
    index = start
    while index < len(source):
        character = source[index]
        if character in {'"', "'", "`"}:
            _value, index = js_string_literal(source, index)
            continue
        if character in pairs:
            closing.append(pairs[character])
        elif closing and character == closing[-1]:
            closing.pop()
        elif not closing and character in {",", "}"}:
            return index
        index += 1
    return index


def js_object_string_fields(source: str, start: int) -> dict:
    if start >= len(source) or source[start] != "{":
        return {}
    fields: Dict[str, str] = {}
    index = start + 1
    while index < len(source):
        while index < len(source) and (
            source[index].isspace() or source[index] == ","
        ):
            index += 1
        if index >= len(source) or source[index] == "}":
            break
        if source[index] in {'"', "'"}:
            key, index = js_string_literal(source, index)
        else:
            match = re.match(r"[A-Za-z_$][A-Za-z0-9_$]*", source[index:])
            if not match:
                return {}
            key = match.group(0)
            index += len(key)
        while index < len(source) and source[index].isspace():
            index += 1
        if index >= len(source) or source[index] != ":":
            return {}
        index += 1
        while index < len(source) and source[index].isspace():
            index += 1
        value = None
        if index < len(source) and source[index] in {'"', "'", "`"}:
            value, index = js_string_literal(source, index)
        else:
            index = skip_js_value(source, index)
        if key in {"cmd", "cwd", "workdir"} and isinstance(value, str):
            fields[key] = value
    return fields


def nested_exec_command_arguments(
    value: object, call_end: Optional[int]
) -> Optional[dict]:
    if not isinstance(value, str) or call_end is None:
        return None
    if call_end < 0 or call_end > len(value):
        return None
    index = call_end
    while index < len(value) and value[index].isspace():
        index += 1
    if index >= len(value) or value[index] != "{":
        return None
    return js_object_string_fields(value, index)


def call_identity(payload: dict) -> Optional[str]:
    for key in ("call_id", "tool_call_id", "id"):
        value = payload.get(key)
        if isinstance(value, str) and 0 < len(value) <= 512:
            return value
    return None


def safe_paired_result(payload: dict) -> Tuple[Optional[str], Optional[int]]:
    candidates = [payload, json_object(payload.get("output"))]
    status = None
    exit_code = None
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        raw_status = candidate.get("status")
        if isinstance(raw_status, str):
            normalized_status = raw_status.strip().lower()
            if normalized_status in SAFE_TOOL_STATUSES:
                status = normalized_status
        for key in ("exit_code", "exitCode"):
            raw_exit_code = candidate.get(key)
            if valid_integer(raw_exit_code):
                exit_code = raw_exit_code
                break
    return status, exit_code


def projected_tool_call(
    record: dict,
    line_number: int,
    session_id: str,
    nested_call_index: Optional[int],
) -> Tuple[dict, Optional[str]]:
    payload = normalized_payload(record)
    if record.get("type") != "response_item" or payload.get("type") not in {
        "function_call",
        "custom_tool_call",
    }:
        raise EvidenceError(
            f"requested line {line_number} for "
            f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} is not a tool call"
        )
    payload_type = payload.get("type")
    recorder_input = payload.get("input")
    occurrences, ambiguous_nested_syntax = (
        nested_tool_scan(recorder_input)
        if payload_type == "custom_tool_call"
        else ([], False)
    )
    if ambiguous_nested_syntax:
        raise EvidenceError(
            f"requested line {line_number} for "
            f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} contains ambiguous nested "
            "tool syntax"
        )
    selected_call_end = None
    selected_nested_index = None
    if nested_call_index is not None:
        if payload_type != "custom_tool_call":
            raise EvidenceError(
                f"requested line {line_number} for "
                f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} uses a nested index, "
                "but nested indices apply only to custom tool calls"
            )
        if not occurrences:
            raise EvidenceError(
                f"requested line {line_number} for "
                f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} contains no nested "
                "tool calls"
            )
        if nested_call_index > len(occurrences):
            raise EvidenceError(
                f"requested line {line_number} for "
                f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} nested index "
                f"{nested_call_index} is out of range 1..{len(occurrences)}"
            )
        selected_nested_index = nested_call_index
        raw_tool_name, selected_call_end = occurrences[nested_call_index - 1]
    elif payload_type == "custom_tool_call" and len(occurrences) > 1:
        raise EvidenceError(
            f"requested line {line_number} for "
            f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} contains multiple nested "
            "tool calls and requires an explicit nested index"
        )
    elif payload_type == "custom_tool_call" and occurrences:
        selected_nested_index = 1
        raw_tool_name, selected_call_end = occurrences[0]
    else:
        names = normalized_tool_names(payload)
        if len(names) != 1:
            raise EvidenceError(
                f"requested line {line_number} for "
                f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} does not identify "
                "exactly one tool call"
            )
        raw_tool_name = names[0]

    tool_name = structural_label(raw_tool_name) or "[redacted]"
    arguments = None
    if tool_name == "exec_command":
        if payload_type == "function_call":
            arguments = json_object(payload.get("arguments"))
        else:
            arguments = nested_exec_command_arguments(
                recorder_input, selected_call_end
            )
    command = sanitized_command(arguments.get("cmd")) if arguments else None
    cwd = None
    if arguments:
        cwd = sanitized_cwd(arguments.get("workdir") or arguments.get("cwd"))
    paired_call_id = call_identity(payload)
    if payload_type == "custom_tool_call" and len(occurrences) > 1:
        paired_call_id = None
    return (
        {
            "session_id": structural_label(session_id),
            "line_number": line_number,
            "nested_call_index": selected_nested_index,
            "tool_name": tool_name,
            "command": command,
            "cwd": cwd,
            "paired_status": None,
            "paired_exit_code": None,
        },
        paired_call_id,
    )


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


def rollout_record(path: Path, line_number: int, raw_line: str) -> dict:
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
    return record


def bounded_line_numbers(values: List[int]) -> dict:
    return {
        "lines": values[:BOUNDARY_LINE_LIMIT],
        "omitted": max(len(values) - BOUNDARY_LINE_LIMIT, 0),
    }


def clone_boundary_map(
    path: Path,
    start: int,
    end: int,
    session_id: str,
    embedded: list,
) -> dict:
    embedded_ids = {
        meta.get("id")
        for meta in embedded
        if isinstance(meta, dict) and isinstance(meta.get("id"), str)
    }
    lines: Dict[str, List[int]] = {
        "outer_session_meta": [],
        "embedded_session_meta": [],
        "task_started": [],
        "task_complete": [],
        "substantive_user": [],
        "assistant_final": [],
    }
    for line_number, raw_line in advertised_lines(path, start, end):
        record = rollout_record(path, line_number, raw_line)
        record_type = record.get("type")
        raw_payload = record.get("payload", {})
        if record_type == "session_meta" and isinstance(raw_payload, dict):
            meta_id = raw_payload.get("id") or raw_payload.get("session_id")
            if meta_id == session_id:
                lines["outer_session_meta"].append(line_number)
            elif meta_id in embedded_ids:
                lines["embedded_session_meta"].append(line_number)
            continue
        if record_type == "event_msg" and isinstance(raw_payload, dict):
            event_type = raw_payload.get("type")
            if event_type == "task_started":
                lines["task_started"].append(line_number)
            elif event_type == "task_complete":
                lines["task_complete"].append(line_number)
            continue
        if record_type != "response_item":
            continue
        payload = normalized_payload(record)
        if payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role == "user":
            cleaned = strip_injected_wrappers(message_text(payload))
            if cleaned and not HEARTBEAT_START_RE.match(cleaned):
                lines["substantive_user"].append(line_number)
        elif role == "assistant" and payload.get("phase") in FINAL_PHASES:
            lines["assistant_final"].append(line_number)
    return {key: bounded_line_numbers(value) for key, value in lines.items()}


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
    *,
    embedded_history_excluded: bool = False,
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
        record = rollout_record(path, line_number, raw_line)
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

    projection = {
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
    if embedded_history_excluded:
        projection["embedded_history_excluded"] = True
        projection["selected_suffix_start"] = start
    return projection


def extract_structural_session(
    session: dict,
    index: int,
    path: Path,
    start: int,
    end: int,
) -> dict:
    session_id, _thread_name = safe_session_identity(session, index)
    records = [
        structural_record(
            rollout_record(path, line_number, raw_line), line_number
        )
        for line_number, raw_line in advertised_lines(path, start, end)
    ]
    return {
        "id": structural_label(session_id),
        "review_line_start": start,
        "review_line_end": end,
        "records": records,
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


def parse_clone_suffix_starts(raw_values: List[str]) -> Dict[str, int]:
    starts: Dict[str, int] = {}
    for raw in raw_values:
        session_id, separator, raw_line = raw.rpartition("=")
        if not separator or not session_id or not raw_line:
            raise EvidenceError(
                "clone suffix starts must use <session-id>=<line>"
            )
        if session_id in starts:
            raise EvidenceError(
                f"duplicate clone suffix start for {session_id[:SAFE_LABEL_CHAR_LIMIT]}"
            )
        try:
            line_number = int(raw_line)
        except ValueError as exc:
            raise EvidenceError(
                f"clone suffix line for {session_id[:SAFE_LABEL_CHAR_LIMIT]} "
                "must be an integer"
            ) from exc
        if line_number < 1:
            raise EvidenceError(
                f"clone suffix line for {session_id[:SAFE_LABEL_CHAR_LIMIT]} "
                "must be positive"
            )
        starts[session_id] = line_number
    return starts


def parse_tool_call_targets(
    raw_values: List[str],
) -> List[Tuple[str, int, Optional[int]]]:
    targets: List[Tuple[str, int, Optional[int]]] = []
    seen = set()
    for raw in raw_values:
        session_id, separator, raw_selector = raw.rpartition("=")
        if not separator or not session_id or not raw_selector:
            raise EvidenceError(
                "tool call projections must use <session-id>=<line>"
            )
        nested_call_index = None
        if "#" in raw_selector:
            if raw_selector.count("#") != 1:
                raise EvidenceError(
                    "indexed tool call projections must use "
                    "<session-id>=<line>#<nested-index>"
                )
            raw_line, raw_nested_index = raw_selector.split("#", 1)
            if not raw_line or not raw_nested_index:
                raise EvidenceError(
                    "indexed tool call projections must use "
                    "<session-id>=<line>#<nested-index>"
                )
            try:
                nested_call_index = int(raw_nested_index)
            except ValueError as exc:
                raise EvidenceError(
                    "tool call projection nested index must be an integer for "
                    f"{session_id[:SAFE_LABEL_CHAR_LIMIT]}"
                ) from exc
            if nested_call_index < 1:
                raise EvidenceError(
                    "tool call projection nested index must be positive for "
                    f"{session_id[:SAFE_LABEL_CHAR_LIMIT]}"
                )
        else:
            raw_line = raw_selector
        try:
            line_number = int(raw_line)
        except ValueError as exc:
            raise EvidenceError(
                f"tool call projection line for "
                f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} must be an integer"
            ) from exc
        if line_number < 1:
            raise EvidenceError(
                f"tool call projection line for "
                f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} must be positive"
            )
        target = (session_id, line_number, nested_call_index)
        if target in seen:
            rendered_target = f"{session_id[:SAFE_LABEL_CHAR_LIMIT]}={line_number}"
            if nested_call_index is not None:
                rendered_target += f"#{nested_call_index}"
            raise EvidenceError(
                f"duplicate tool call projection for {rendered_target}"
            )
        seen.add(target)
        targets.append(target)
    return targets


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def parse_cwd_roots(raw_values: List[str]) -> List[Path]:
    roots: List[Path] = []
    home = Path.home()
    for raw in raw_values:
        candidate = Path(raw)
        if not candidate.is_absolute():
            raise EvidenceError("--cwd-root values must be absolute paths")
        if ".." in candidate.parts:
            raise EvidenceError("--cwd-root values must not contain '..'")
        normalized = Path(os.path.normpath(raw))
        filesystem_root = Path(normalized.anchor)
        if (
            normalized == filesystem_root
            or len(normalized.parts) < 3
            or path_is_within(home, normalized)
        ):
            raise EvidenceError(
                "--cwd-root is too broad; use a concrete repository root"
            )
        git_marker = normalized / ".git"
        if not git_marker.is_dir() and not git_marker.is_file():
            raise EvidenceError(
                "--cwd-root must name an existing repository root with .git"
            )
        if normalized not in roots:
            roots.append(normalized)
    return roots


def parse_worktree_tails(raw_values: List[str]) -> List[str]:
    tails: List[str] = []
    for raw in raw_values:
        if raw in {".", ".."} or not WORKTREE_TAIL_RE.fullmatch(raw):
            raise EvidenceError(
                "--worktree-tail values must be single repository names"
            )
        if raw not in tails:
            tails.append(raw)
    return tails


def normalized_session_cwd(session: dict) -> Optional[Path]:
    meta = session.get("meta")
    if not isinstance(meta, dict):
        return None
    raw_cwd = meta.get("cwd")
    if not isinstance(raw_cwd, str) or not raw_cwd:
        return None
    cwd = Path(raw_cwd)
    if not cwd.is_absolute() or ".." in cwd.parts:
        return None
    return Path(os.path.normpath(raw_cwd))


def matches_path_selectors(
    session: dict,
    cwd_roots: List[Path],
    worktree_tails: List[str],
) -> bool:
    cwd = normalized_session_cwd(session)
    if cwd is None:
        return False
    if any(path_is_within(cwd, root) for root in cwd_roots):
        return True
    if not worktree_tails:
        return False
    worktrees_root = Path.home() / ".codex" / "worktrees"
    try:
        relative = cwd.relative_to(worktrees_root)
    except ValueError:
        return False
    return len(relative.parts) >= 2 and relative.parts[1] in worktree_tails


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
        "--cwd-root",
        action="append",
        default=[],
        metavar="ABS_PATH",
        help=(
            "Select sessions whose manifest meta.cwd equals this existing "
            "absolute repository root (with .git) or is its descendant; "
            "may be repeated."
        ),
    )
    parser.add_argument(
        "--worktree-tail",
        action="append",
        default=[],
        metavar="REPO_TAIL",
        help=(
            "Select sessions under ~/.codex/worktrees/<slot>/REPO_TAIL or "
            "its descendants; may be repeated."
        ),
    )
    parser.add_argument(
        "--max-total-chars",
        type=parse_max_total_chars,
        default=DEFAULT_MAX_TOTAL_CHARS,
    )
    parser.add_argument(
        "--list-clone-boundaries",
        action="store_true",
        help=(
            "For embedded-history sessions, emit only bounded line-number "
            "maps for manual suffix selection; no message text is summarized."
        ),
    )
    parser.add_argument(
        "--structural-projection",
        action="store_true",
        help=(
            "For exact --session-id selections, emit only content-free "
            "record structure from resolver-advertised ranges."
        ),
    )
    parser.add_argument(
        "--tool-call-projection",
        action="append",
        default=[],
        metavar="SESSION_ID=LINE[#NESTED_INDEX]",
        help=(
            "Emit one bounded sanitized tool call from an exact advertised "
            "line; append a one-based #NESTED_INDEX for a batched custom "
            "exec wrapper. May be repeated and requires matching "
            "--session-id filters."
        ),
    )
    parser.add_argument(
        "--clone-suffix-start",
        action="append",
        default=[],
        metavar="SESSION_ID=LINE",
        help=(
            "Extract an already-reviewed embedded-history suffix starting at "
            "the exact inclusive line; may be repeated."
        ),
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


def structural_output_document(
    projections: List[dict],
    emitted_counts: List[int],
    manifest_session_count: int,
    selected_session_count: int,
    filtered_out_session_count: int,
) -> dict:
    sessions = []
    inspected_records = 0
    emitted_records = 0
    for projection, emitted_count in zip(projections, emitted_counts):
        records = projection["records"]
        inspected_count = len(records)
        inspected_records += inspected_count
        emitted_records += emitted_count
        sessions.append(
            {
                "id": projection["id"],
                "review_line_start": projection["review_line_start"],
                "review_line_end": projection["review_line_end"],
                "counts": {
                    "advertised_lines": max(
                        projection["review_line_end"]
                        - projection["review_line_start"]
                        + 1,
                        0,
                    ),
                    "inspected_lines": inspected_count,
                    "emitted_records": emitted_count,
                    "omitted_records": inspected_count - emitted_count,
                },
                "records": records[:emitted_count],
            }
        )
    return {
        "schema_version": 1,
        "mode": "structural_projection",
        "counts": {
            "manifest_sessions": manifest_session_count,
            "selected_sessions": selected_session_count,
            "filtered_out_sessions": filtered_out_session_count,
            "resolved_sessions": len(projections),
            "inspected_records": inspected_records,
            "emitted_records": emitted_records,
            "omitted_records": inspected_records - emitted_records,
        },
        "sessions": sessions,
    }


def fit_structural_output(
    projections: List[dict],
    manifest_session_count: int,
    selected_session_count: int,
    filtered_out_session_count: int,
    max_total_chars: int,
    pretty: bool,
) -> str:
    emitted_counts = [0] * len(projections)

    def rendered_document() -> str:
        return serialize(
            structural_output_document(
                projections,
                emitted_counts,
                manifest_session_count,
                selected_session_count,
                filtered_out_session_count,
            ),
            pretty,
        )

    rendered = rendered_document()
    if len(rendered) > max_total_chars:
        raise EvidenceError(
            "max-total-chars is too small for the structural output envelope"
        )

    output_full = False
    for projection_index, projection in enumerate(projections):
        for _record in projection["records"]:
            emitted_counts[projection_index] += 1
            candidate = rendered_document()
            if len(candidate) > max_total_chars:
                emitted_counts[projection_index] -= 1
                output_full = True
                break
            rendered = candidate
        if output_full:
            break
    return rendered_document()


def extract_tool_calls_for_session(
    path: Path,
    start: int,
    end: int,
    session_id: str,
    target_selectors: List[Tuple[int, Optional[int]]],
) -> Dict[Tuple[int, Optional[int]], dict]:
    selectors_by_line: Dict[int, List[Optional[int]]] = {}
    for line_number, nested_call_index in target_selectors:
        selectors_by_line.setdefault(line_number, []).append(
            nested_call_index
        )
    calls: Dict[
        Tuple[int, Optional[int]], Tuple[dict, Optional[str]]
    ] = {}
    paired_results: Dict[
        str, List[Tuple[Optional[str], Optional[int]]]
    ] = {}
    for line_number, raw_line in advertised_lines(path, start, end):
        record = rollout_record(path, line_number, raw_line)
        for nested_call_index in selectors_by_line.get(line_number, []):
            selector = (line_number, nested_call_index)
            calls[selector] = projected_tool_call(
                record, line_number, session_id, nested_call_index
            )
        payload = normalized_payload(record)
        if payload.get("type") not in {
            "function_call_output",
            "custom_tool_call_output",
        }:
            continue
        output_call_id = call_identity(payload)
        if output_call_id is None:
            continue
        paired_results.setdefault(output_call_id, []).append(
            safe_paired_result(payload)
        )

    missing_selectors = [
        selector for selector in target_selectors if selector not in calls
    ]
    if missing_selectors:
        rendered_selectors = []
        for line_number, nested_call_index in missing_selectors[:8]:
            rendered = str(line_number)
            if nested_call_index is not None:
                rendered += f"#{nested_call_index}"
            rendered_selectors.append(rendered)
        raise EvidenceError(
            f"tool call projection could not read requested selector(s) for "
            f"{session_id[:SAFE_LABEL_CHAR_LIMIT]}: "
            + ", ".join(rendered_selectors)
        )

    projected: Dict[Tuple[int, Optional[int]], dict] = {}
    for selector in target_selectors:
        call, call_id = calls[selector]
        results = paired_results.get(call_id, []) if call_id else []
        if len(results) == 1:
            call["paired_status"], call["paired_exit_code"] = results[0]
        projected[selector] = call
    return projected


def fit_tool_call_output(
    tool_calls: List[dict],
    manifest_session_count: int,
    selected_session_count: int,
    filtered_out_session_count: int,
    max_total_chars: int,
    pretty: bool,
) -> str:
    document = {
        "schema_version": 1,
        "mode": "tool_call_projection",
        "counts": {
            "manifest_sessions": manifest_session_count,
            "selected_sessions": selected_session_count,
            "filtered_out_sessions": filtered_out_session_count,
            "projected_tool_calls": len(tool_calls),
        },
        "tool_calls": tool_calls,
    }
    rendered = serialize(document, pretty)
    if len(rendered) > max_total_chars:
        raise EvidenceError(
            "max-total-chars is too small for the bounded tool call projection"
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
    cwd_roots = parse_cwd_roots(args.cwd_root)
    worktree_tails = parse_worktree_tails(args.worktree_tail)
    has_path_selectors = bool(cwd_roots or worktree_tails)
    clone_suffix_starts = parse_clone_suffix_starts(args.clone_suffix_start)
    tool_call_targets = parse_tool_call_targets(args.tool_call_projection)
    if tool_call_targets and not requested_ids:
        raise EvidenceError(
            "--tool-call-projection requires exact --session-id filters"
        )
    if tool_call_targets and (
        has_path_selectors
        or args.structural_projection
        or args.list_clone_boundaries
        or clone_suffix_starts
    ):
        raise EvidenceError(
            "--tool-call-projection cannot be combined with path, "
            "structural, or clone modes"
        )
    tool_target_ids_not_selected = [
        session_id
        for session_id, _line_number, _nested_call_index in tool_call_targets
        if session_id not in requested_ids
    ]
    if tool_target_ids_not_selected:
        rendered_ids = ", ".join(
            value[:SAFE_LABEL_CHAR_LIMIT]
            for value in dict.fromkeys(tool_target_ids_not_selected)
        )
        raise EvidenceError(
            "tool call projection session id(s) missing matching "
            f"--session-id: {rendered_ids}"
        )
    if args.structural_projection and not requested_ids:
        raise EvidenceError(
            "--structural-projection requires exact --session-id filters"
        )
    if args.structural_projection and has_path_selectors:
        raise EvidenceError(
            "--structural-projection cannot be combined with path selectors"
        )
    if args.structural_projection and (
        args.list_clone_boundaries or clone_suffix_starts
    ):
        raise EvidenceError(
            "--structural-projection cannot be combined with clone modes"
        )
    if has_path_selectors and (
        requested_ids or args.list_clone_boundaries or clone_suffix_starts
    ):
        raise EvidenceError(
            "path selectors cannot be combined with exact --session-id or "
            "clone modes"
        )
    if args.list_clone_boundaries and clone_suffix_starts:
        raise EvidenceError(
            "--list-clone-boundaries and --clone-suffix-start are separate steps"
        )
    if (args.list_clone_boundaries or clone_suffix_starts) and not requested_ids:
        raise EvidenceError(
            "clone boundary/suffix modes require exact --session-id filters"
        )
    suffix_ids_not_selected = [
        session_id
        for session_id in clone_suffix_starts
        if session_id not in requested_ids
    ]
    if suffix_ids_not_selected:
        rendered_ids = ", ".join(
            value[:SAFE_LABEL_CHAR_LIMIT]
            for value in suffix_ids_not_selected[:8]
        )
        raise EvidenceError(
            f"clone suffix session id(s) missing matching --session-id: {rendered_ids}"
        )

    indexes_by_id: Dict[str, List[int]] = {}
    for index, session in enumerate(sessions):
        session_id = session.get("id")
        if isinstance(session_id, str):
            indexes_by_id.setdefault(session_id, []).append(index)
    selected_indexes: Optional[set] = None
    if requested_ids:
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
    elif has_path_selectors:
        selected_indexes = {
            index
            for index, session in enumerate(sessions)
            if matches_path_selectors(session, cwd_roots, worktree_tails)
        }

    if tool_call_targets:
        target_selectors_by_session: Dict[
            str, List[Tuple[int, Optional[int]]]
        ] = {}
        for session_id, line_number, nested_call_index in tool_call_targets:
            target_selectors_by_session.setdefault(session_id, []).append(
                (line_number, nested_call_index)
            )
        calls_by_target: Dict[
            Tuple[str, int, Optional[int]], dict
        ] = {}
        for index, session in enumerate(sessions, start=1):
            raw_session_id = session.get("id")
            if not isinstance(raw_session_id, str):
                continue
            if raw_session_id not in target_selectors_by_session:
                continue
            start, end, _embedded = session_range(session, index)
            target_selectors = target_selectors_by_session[raw_session_id]
            outside_lines = [
                line_number
                for line_number, _nested_call_index in target_selectors
                if line_number < start or line_number > end
            ]
            if outside_lines:
                rendered_lines = ", ".join(
                    str(line_number) for line_number in outside_lines[:8]
                )
                raise EvidenceError(
                    f"tool call projection line(s) {rendered_lines} for "
                    f"{raw_session_id[:SAFE_LABEL_CHAR_LIMIT]} are outside "
                    f"advertised range {start}:{end}"
                )
            path = rollout_path(session, index, manifest_path.parent)
            projected = extract_tool_calls_for_session(
                path,
                start,
                end,
                raw_session_id,
                target_selectors,
            )
            for selector, call in projected.items():
                line_number, nested_call_index = selector
                calls_by_target[
                    (raw_session_id, line_number, nested_call_index)
                ] = call
        ordered_calls = [
            calls_by_target[target] for target in tool_call_targets
        ]
        selected_count = len(selected_indexes)
        return fit_tool_call_output(
            ordered_calls,
            len(sessions),
            selected_count,
            len(sessions) - selected_count,
            args.max_total_chars,
            args.pretty,
        )

    if args.structural_projection:
        structural_projections: List[dict] = []
        for index, session in enumerate(sessions, start=1):
            if index - 1 not in selected_indexes:
                continue
            start, end, _embedded = session_range(session, index)
            path = rollout_path(session, index, manifest_path.parent)
            structural_projections.append(
                extract_structural_session(session, index, path, start, end)
            )
        return fit_structural_output(
            structural_projections,
            len(sessions),
            len(selected_indexes),
            len(sessions) - len(selected_indexes),
            args.max_total_chars,
            args.pretty,
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
        session_id, _thread_name = safe_session_identity(session, index)
        if embedded:
            if args.list_clone_boundaries:
                projection = manual_projection(
                    session, index, start, end, embedded
                )
                projection["clone_boundary_map"] = clone_boundary_map(
                    path, start, end, session_id, embedded
                )
                projections.append(projection)
                continue
            if session_id in clone_suffix_starts:
                suffix_start = clone_suffix_starts[session_id]
                if suffix_start < start or suffix_start > end:
                    raise EvidenceError(
                        f"clone suffix start {suffix_start} for "
                        f"{session_id[:SAFE_LABEL_CHAR_LIMIT]} is outside "
                        f"advertised range {start}:{end}"
                    )
                projection = extract_session(
                    session,
                    index,
                    path,
                    suffix_start,
                    end,
                    embedded_history_excluded=True,
                )
                if projection["counts"]["substantive_user_messages"] == 0:
                    raise EvidenceError(
                        f"clone suffix for {session_id[:SAFE_LABEL_CHAR_LIMIT]} "
                        "contains no substantive user message"
                    )
                projection["embedded_session_ids"] = [
                    meta_id
                    for meta_id in (
                        bounded_text(meta.get("id"), SAFE_LABEL_CHAR_LIMIT)
                        for meta in embedded
                        if isinstance(meta, dict)
                    )
                    if meta_id
                ][:8]
                projections.append(projection)
                continue
            # Validate the path/range, but do not parse or summarize a rollout
            # whose imported-history boundary still needs human selection.
            for _line_number, _line in advertised_lines(path, start, end):
                pass
            projections.append(
                manual_projection(session, index, start, end, embedded)
            )
            continue
        if args.list_clone_boundaries:
            raise EvidenceError(
                f"selected session {session_id[:SAFE_LABEL_CHAR_LIMIT]} "
                "has no embedded history"
            )
        if session_id in clone_suffix_starts:
            raise EvidenceError(
                f"selected session {session_id[:SAFE_LABEL_CHAR_LIMIT]} "
                "has no embedded history for a clone suffix"
            )
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
