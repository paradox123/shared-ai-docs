#!/usr/bin/env python3
"""Resolve one bounded Codex session-review window from one index snapshot."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Dict, Iterable, List, Optional, Tuple


STRUCTURED_MEMORY_FIELDS = ("Processed window end", "Last review")
CARRY_FORWARD_SESSIONS_FIELD = "Carry-forward sessions"
FINAL_PHASES = {"final", "final_answer"}


def parse_timestamp(raw: str) -> datetime:
    value = str(raw).strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    match = re.match(r"^(.*\.)(\d+)([+-]\d\d:\d\d)$", value)
    if match:
        fraction = match.group(2)[:6].ljust(6, "0")
        value = match.group(1) + fraction + match.group(3)
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    rendered = value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    rendered = rendered.replace("+00:00", "Z")
    return rendered.replace(".000000Z", "Z")


def cutoff_sources(
    memory_path: Optional[Path], prompt_last_run: str
) -> Tuple[List[dict], List[dict]]:
    sources: List[dict] = []
    diagnostics: List[dict] = []
    if memory_path is not None:
        if memory_path.exists():
            memory_text = memory_path.read_text(errors="replace")
            for field in STRUCTURED_MEMORY_FIELDS:
                match = re.search(
                    rf"^{re.escape(field)}:\s*(\S+)",
                    memory_text,
                    flags=re.MULTILINE,
                )
                if not match:
                    continue
                raw = match.group(1)
                try:
                    normalized = format_timestamp(parse_timestamp(raw))
                except ValueError as exc:
                    diagnostics.append(
                        {
                            "code": "invalid_memory_timestamp",
                            "field": field,
                            "value": raw,
                            "message": str(exc),
                        }
                    )
                    continue
                sources.append(
                    {
                        "name": f"memory.{field}",
                        "value": raw,
                        "normalized": normalized,
                    }
                )
        else:
            diagnostics.append(
                {
                    "code": "missing_memory",
                    "path": str(memory_path),
                }
            )
    if prompt_last_run:
        try:
            normalized = format_timestamp(parse_timestamp(prompt_last_run))
        except ValueError as exc:
            diagnostics.append(
                {
                    "code": "invalid_prompt_last_run",
                    "value": prompt_last_run,
                    "message": str(exc),
                }
            )
        else:
            sources.append(
                {
                    "name": "prompt.Last run",
                    "value": prompt_last_run,
                    "normalized": normalized,
                }
            )
    return sources, diagnostics


def carry_forward_sessions(
    memory_path: Optional[Path],
) -> Tuple[List[dict], List[dict]]:
    if memory_path is None or not memory_path.exists():
        return [], []
    memory_text = memory_path.read_text(errors="replace")
    memory_header = memory_text.split("\n## ", 1)[0]
    match = re.search(
        rf"^{re.escape(CARRY_FORWARD_SESSIONS_FIELD)}:\s*(.*)$",
        memory_header,
        flags=re.MULTILINE,
    )
    if not match:
        return [], []
    raw = match.group(1).strip()
    if not raw:
        return [], []
    diagnostics: List[dict] = []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [], [
            {
                "code": "invalid_carry_forward_json",
                "message": str(exc),
            }
        ]
    if not isinstance(parsed, list):
        return [], [{"code": "invalid_carry_forward_shape"}]
    entries: List[dict] = []
    seen_ids = set()
    for entry_index, value in enumerate(parsed):
        if not isinstance(value, dict):
            diagnostics.append(
                {
                    "code": "invalid_carry_forward_entry",
                    "entry_index": entry_index,
                }
            )
            continue
        session_id = value.get("id")
        line_count = value.get("line_count")
        last_activity_at = value.get("last_activity_at")
        if (
            not isinstance(session_id, str)
            or len(session_id) > 128
            or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._:-]*", session_id
            )
            or not isinstance(line_count, int)
            or isinstance(line_count, bool)
            or line_count < 0
        ):
            diagnostics.append(
                {
                    "code": "invalid_carry_forward_entry",
                    "entry_index": entry_index,
                }
            )
            continue
        if last_activity_at is not None:
            try:
                last_activity_at = format_timestamp(
                    parse_timestamp(last_activity_at)
                )
            except (TypeError, ValueError):
                diagnostics.append(
                    {
                        "code": "invalid_carry_forward_activity_timestamp",
                        "entry_index": entry_index,
                        "session_id": session_id,
                    }
                )
                continue
        if session_id in seen_ids:
            diagnostics.append(
                {
                    "code": "duplicate_carry_forward_session",
                    "session_id": session_id,
                }
            )
            continue
        seen_ids.add(session_id)
        entries.append(
            {
                "id": session_id,
                "line_count": line_count,
                "last_activity_at": last_activity_at,
            }
        )
    return entries, diagnostics


def normalized_payload(record: dict) -> dict:
    raw_payload = record.get("payload", {})
    nested = raw_payload.get("item")
    return nested if isinstance(nested, dict) else raw_payload


def inspect_rollout_window(
    path: Path,
    window_end: datetime,
    previous_line_count: int,
    expected_session_id: str,
) -> dict:
    physical_line_count = 0
    line_count_at_window = 0
    non_meta_record_count = 0
    response_item_count = 0
    assistant_final_count = 0
    last_user_message_line = 0
    last_assistant_final_line = 0
    records_after_window = 0
    invalid_json_records = 0
    missing_timestamp_records = 0
    embedded_session_metas: List[dict] = []
    max_record_timestamp: Optional[datetime] = None
    try:
        with path.open(errors="replace") as handle:
            for line_number, line in enumerate(handle, start=1):
                physical_line_count = line_number
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    invalid_json_records += 1
                    continue
                raw_timestamp = record.get("timestamp")
                if not raw_timestamp and record.get("type") == "session_meta":
                    raw_timestamp = record.get("payload", {}).get("timestamp")
                if not raw_timestamp:
                    missing_timestamp_records += 1
                    continue
                try:
                    record_timestamp = parse_timestamp(raw_timestamp)
                except ValueError:
                    invalid_json_records += 1
                    continue
                if record_timestamp > window_end:
                    records_after_window += 1
                    continue
                line_count_at_window = line_number
                if (
                    max_record_timestamp is None
                    or record_timestamp > max_record_timestamp
                ):
                    max_record_timestamp = record_timestamp
                if record.get("type") == "session_meta":
                    payload = record.get("payload", {})
                    embedded_session_id = payload.get("id") or payload.get(
                        "session_id"
                    )
                    if (
                        embedded_session_id
                        and embedded_session_id != expected_session_id
                    ):
                        embedded_session_metas.append(
                            {
                                "line_number": line_number,
                                "id": embedded_session_id,
                                "timestamp": payload.get("timestamp"),
                            }
                        )
                else:
                    non_meta_record_count += 1
                if record.get("type") != "response_item":
                    continue
                response_item_count += 1
                payload = normalized_payload(record)
                if (
                    payload.get("type") == "message"
                    and payload.get("role") == "user"
                ):
                    last_user_message_line = line_number
                if (
                    payload.get("type") == "message"
                    and payload.get("role") == "assistant"
                    and payload.get("phase") in FINAL_PHASES
                ):
                    assistant_final_count += 1
                    last_assistant_final_line = line_number
    except OSError:
        return {
            "state": "unreadable",
            "previous_line_count": previous_line_count,
            "physical_line_count": 0,
            "line_count_at_window": 0,
            "review_line_start": previous_line_count + 1,
            "review_line_end": previous_line_count,
            "new_lines_at_window": 0,
            "non_meta_record_count": 0,
            "response_item_count": 0,
            "assistant_final_count": 0,
            "max_record_timestamp": None,
            "records_after_window": 0,
            "invalid_json_records": 0,
            "missing_timestamp_records": 0,
            "embedded_session_metas": [],
            "checkpoint_line_count": previous_line_count,
            "carry_forward_required": True,
        }

    truncated = physical_line_count < previous_line_count
    new_lines_at_window = max(line_count_at_window - previous_line_count, 0)
    if truncated or invalid_json_records or missing_timestamp_records:
        state = "unknown"
    elif (
        assistant_final_count
        and last_assistant_final_line > last_user_message_line
    ):
        state = "complete"
    elif non_meta_record_count:
        state = "open"
    else:
        state = "metadata_only"
    is_carried = previous_line_count > 0
    carry_forward_required = (
        state in {"unknown", "unreadable"}
        or records_after_window > 0
        or (
            state == "open"
            and (not is_carried or new_lines_at_window > 0)
        )
    )
    checkpoint_line_count = (
        previous_line_count
        if truncated or invalid_json_records or missing_timestamp_records
        else line_count_at_window
    )
    return {
        "state": state,
        "previous_line_count": previous_line_count,
        "physical_line_count": physical_line_count,
        "line_count_at_window": line_count_at_window,
        "review_line_start": previous_line_count + 1,
        "review_line_end": line_count_at_window,
        "new_lines_at_window": new_lines_at_window,
        "non_meta_record_count": non_meta_record_count,
        "response_item_count": response_item_count,
        "assistant_final_count": assistant_final_count,
        "max_record_timestamp": (
            format_timestamp(max_record_timestamp)
            if max_record_timestamp is not None
            else None
        ),
        "records_after_window": records_after_window,
        "invalid_json_records": invalid_json_records,
        "missing_timestamp_records": missing_timestamp_records,
        "embedded_session_metas": embedded_session_metas,
        "truncated_since_checkpoint": truncated,
        "checkpoint_line_count": checkpoint_line_count,
        "carry_forward_required": carry_forward_required,
    }


def read_session_meta(path: Path) -> Optional[dict]:
    try:
        with path.open(errors="replace") as handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") != "session_meta":
                    continue
                payload = record.get("payload", {})
                session_id = payload.get("id") or payload.get("session_id")
                if not session_id:
                    return None
                return {
                    "id": session_id,
                    "timestamp": payload.get("timestamp"),
                    "cwd": payload.get("cwd"),
                }
    except OSError:
        return None
    return None


def add_verified_candidate(
    candidates: Dict[str, Dict[Path, str]],
    selected_ids: Iterable[str],
    path: Path,
    source: str,
) -> None:
    meta = read_session_meta(path)
    if not meta:
        return
    session_id = meta["id"]
    if session_id not in selected_ids:
        return
    candidates.setdefault(session_id, {})[path] = source


def resolve_rollouts(
    codex_home: Path,
    rows: List[dict],
    window_end: datetime,
    carry_by_id: Dict[str, dict],
) -> Tuple[List[dict], List[dict], bool]:
    sessions_root = codex_home / "sessions"
    selected_ids = {row["id"] for row in rows}
    candidates: Dict[str, Dict[Path, str]] = {}

    days = sorted(
        {
            parse_timestamp(row["updated_at"]).strftime("%Y/%m/%d")
            for row in rows
        }
    )
    for day in days:
        for path in sorted((sessions_root / day).glob("*.jsonl")):
            add_verified_candidate(candidates, selected_ids, path, "updated-day")

    for session_id in sorted(selected_ids - candidates.keys()):
        for path in sorted(sessions_root.glob(f"*/*/*/*{session_id}*.jsonl")):
            add_verified_candidate(
                candidates, {session_id}, path, "targeted-filename"
            )

    archived_root = codex_home / "archived_sessions"
    for session_id in sorted(selected_ids - candidates.keys()):
        for path in sorted(archived_root.glob(f"*{session_id}*.jsonl")):
            add_verified_candidate(candidates, {session_id}, path, "archive")

    diagnostics: List[dict] = []
    resolved: List[dict] = []
    safe = True
    for row in rows:
        session_id = row["id"]
        matches = candidates.get(session_id, {})
        item = {
            "id": session_id,
            "thread_name": row.get("thread_name"),
            "updated_at": row["updated_at"],
            "selection_reasons": row.get("_selection_reasons", ["window"]),
        }
        if len(matches) == 1:
            path, source = next(iter(matches.items()))
            previous_checkpoint = carry_by_id.get(
                session_id,
                {"line_count": 0, "last_activity_at": None},
            )
            rollout_window = inspect_rollout_window(
                path,
                window_end,
                previous_checkpoint["line_count"],
                session_id,
            )
            if rollout_window.get("state") in {"unknown", "unreadable"}:
                rollout_window["max_record_timestamp"] = previous_checkpoint.get(
                    "last_activity_at"
                )
                safe = False
                diagnostics.append(
                    {
                        "code": "unsafe_rollout_window",
                        "session_id": session_id,
                        "state": rollout_window.get("state"),
                    }
                )
            item.update(
                {
                    "status": "resolved",
                    "path": str(path),
                    "source": source,
                    "meta": read_session_meta(path),
                    "rollout_window": rollout_window,
                }
            )
            embedded_session_metas = rollout_window.get(
                "embedded_session_metas", []
            )
            if embedded_session_metas:
                diagnostics.append(
                    {
                        "code": "embedded_session_history_detected",
                        "session_id": session_id,
                        "embedded_session_ids": list(
                            dict.fromkeys(
                                meta["id"]
                                for meta in embedded_session_metas
                            )
                        ),
                    }
                )
        elif not matches:
            safe = False
            item.update({"status": "missing", "path": None, "source": None})
            diagnostics.append(
                {
                    "code": "missing_rollout",
                    "session_id": session_id,
                }
            )
        else:
            safe = False
            item.update(
                {
                    "status": "ambiguous",
                    "path": None,
                    "source": None,
                    "candidates": [str(path) for path in sorted(matches)],
                }
            )
            diagnostics.append(
                {
                    "code": "ambiguous_rollout",
                    "session_id": session_id,
                    "paths": [str(path) for path in sorted(matches)],
                }
            )
        resolved.append(item)
    return resolved, diagnostics, safe


def load_index_snapshot(index_path: Path) -> Tuple[bytes, List[dict], List[dict]]:
    snapshot = index_path.read_bytes()
    rows: List[dict] = []
    diagnostics: List[dict] = []
    for line_number, raw_line in enumerate(snapshot.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            row = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            diagnostics.append(
                {
                    "code": "invalid_index_json",
                    "line": line_number,
                    "message": str(exc),
                }
            )
            continue
        session_id = row.get("id")
        updated_at = row.get("updated_at")
        if not session_id or not updated_at:
            diagnostics.append(
                {
                    "code": "invalid_index_row",
                    "line": line_number,
                }
            )
            continue
        try:
            parsed = parse_timestamp(updated_at)
        except ValueError as exc:
            diagnostics.append(
                {
                    "code": "invalid_index_timestamp",
                    "line": line_number,
                    "value": updated_at,
                    "message": str(exc),
                }
            )
            continue
        normalized = {
            "id": session_id,
            "thread_name": row.get("thread_name"),
            "updated_at": format_timestamp(parsed),
            "_updated": parsed,
        }
        rows.append(normalized)
    return snapshot, rows, diagnostics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Capture session_index.jsonl once, choose the newest structured "
            "cutoff, resolve the bounded review window, and emit compact JSON."
        )
    )
    parser.add_argument("--codex-home", required=True, type=Path)
    parser.add_argument("--memory", type=Path)
    parser.add_argument("--prompt-last-run", default="")
    parser.add_argument("--recent", type=int, default=120)
    parser.add_argument("--max-sessions", type=int, default=100)
    parser.add_argument(
        "--compact",
        action="store_true",
        help=(
            "Emit a minified review manifest with only persistence and "
            "evidence-routing fields."
        ),
    )
    parser.add_argument(
        "--exclude-session-id",
        action="append",
        default=[],
        help=(
            "Exact current maintenance session id to exclude before "
            "resolution, normally the exported CODEX_THREAD_ID; may be repeated."
        ),
    )
    return parser.parse_args()


def compact_session(session: dict) -> dict:
    fields = (
        "id",
        "thread_name",
        "updated_at",
        "selection_reasons",
        "status",
        "path",
        "source",
        "meta",
        "candidates",
    )
    compact = {key: session[key] for key in fields if key in session}
    rollout_window = session.get("rollout_window")
    if rollout_window is not None:
        review_fields = (
            "state",
            "review_line_start",
            "review_line_end",
            "new_lines_at_window",
            "records_after_window",
            "checkpoint_line_count",
            "carry_forward_required",
            "embedded_session_metas",
        )
        compact["rollout_window"] = {
            key: rollout_window[key]
            for key in review_fields
            if key in rollout_window
        }
    return compact


def compact_output(output: dict) -> dict:
    compact = dict(output)
    compact["sessions"] = [
        compact_session(session) for session in output.get("sessions", [])
    ]
    return compact


def main() -> int:
    args = parse_args()
    diagnostics: List[dict] = []
    sources, cutoff_diagnostics = cutoff_sources(
        args.memory, args.prompt_last_run
    )
    diagnostics.extend(cutoff_diagnostics)
    carry_entries, carry_diagnostics = carry_forward_sessions(args.memory)
    diagnostics.extend(carry_diagnostics)
    carry_by_id = {entry["id"]: entry for entry in carry_entries}
    excluded_session_ids = list(dict.fromkeys(args.exclude_session_id))
    if not sources:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "diagnostics": diagnostics
                    + [{"code": "missing_cutoff"}],
                },
                indent=2,
            )
        )
        return 1
    cutoff = max(
        (parse_timestamp(source["normalized"]) for source in sources)
    )

    index_path = args.codex_home / "session_index.jsonl"
    try:
        snapshot, rows, index_diagnostics = load_index_snapshot(index_path)
    except OSError as exc:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "diagnostics": diagnostics
                    + [
                        {
                            "code": "index_read_failed",
                            "path": str(index_path),
                            "message": str(exc),
                        }
                    ],
                },
                indent=2,
            )
        )
        return 1
    diagnostics.extend(index_diagnostics)
    if not rows:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "diagnostics": diagnostics
                    + [{"code": "empty_index"}],
                },
                indent=2,
            )
        )
        return 1

    latest_by_id: Dict[str, dict] = {}
    duplicate_counts: Dict[str, int] = {}
    for row in rows:
        previous = latest_by_id.get(row["id"])
        if previous is not None:
            duplicate_counts[row["id"]] = duplicate_counts.get(row["id"], 1) + 1
        if previous is None or row["_updated"] >= previous["_updated"]:
            latest_by_id[row["id"]] = row
    snapshot_end = max(row["_updated"] for row in rows)
    window_end = max(cutoff, snapshot_end)
    selected_by_id: Dict[str, dict] = {}
    for row in latest_by_id.values():
        if cutoff < row["_updated"] <= window_end:
            selected = dict(row)
            selected["_selection_reasons"] = ["window"]
            selected_by_id[row["id"]] = selected
    missing_carry_ids: List[str] = []
    for session_id in carry_by_id:
        if session_id in excluded_session_ids:
            continue
        row = latest_by_id.get(session_id)
        if row is None:
            missing_carry_ids.append(session_id)
            continue
        if session_id in selected_by_id:
            selected_by_id[session_id]["_selection_reasons"].append(
                "carry_forward"
            )
        else:
            selected = dict(row)
            selected["_selection_reasons"] = ["carry_forward"]
            selected_by_id[session_id] = selected
    if missing_carry_ids:
        diagnostics.append(
            {
                "code": "carry_forward_sessions_missing_from_index",
                "session_ids": missing_carry_ids,
            }
        )
    excluded_sessions = []
    for session_id in excluded_session_ids:
        row = selected_by_id.pop(session_id, None)
        if row is not None:
            excluded_sessions.append(
                {
                    "id": session_id,
                    "thread_name": row.get("thread_name"),
                    "updated_at": row["updated_at"],
                }
            )
    selected_rows = list(selected_by_id.values())
    selected_rows.sort(key=lambda row: (row["_updated"], row["id"]))
    selected_duplicates = [
        {"id": row["id"], "row_count": duplicate_counts[row["id"]]}
        for row in selected_rows
        if row["id"] in duplicate_counts
    ]
    if selected_duplicates:
        diagnostics.append(
            {
                "code": "duplicate_index_rows_collapsed",
                "sessions": selected_duplicates,
            }
        )
    if len(selected_rows) > args.max_sessions:
        diagnostics.append(
            {
                "code": "too_many_sessions",
                "count": len(selected_rows),
                "max_sessions": args.max_sessions,
            }
        )

    safe_to_persist = (
        not index_diagnostics
        and not carry_diagnostics
        and not missing_carry_ids
        and len(selected_rows) <= args.max_sessions
    )
    resolved: List[dict] = []
    if len(selected_rows) <= args.max_sessions:
        resolved, rollout_diagnostics, rollout_safe = resolve_rollouts(
            args.codex_home,
            selected_rows,
            window_end,
            carry_by_id,
        )
        diagnostics.extend(rollout_diagnostics)
        safe_to_persist = safe_to_persist and rollout_safe

    carry_forward_to_persist = []
    for session in resolved:
        rollout_window = session.get("rollout_window", {})
        if not rollout_window.get("carry_forward_required", False):
            continue
        carry_forward_to_persist.append(
            {
                "id": session["id"],
                "line_count": rollout_window.get(
                    "checkpoint_line_count", 0
                ),
                "last_activity_at": rollout_window.get(
                    "max_record_timestamp"
                ),
            }
        )

    def public_row(row: dict) -> dict:
        return {
            "id": row["id"],
            "thread_name": row.get("thread_name"),
            "updated_at": row["updated_at"],
        }

    recent_count = min(max(args.recent, 0), 500)
    recent_rows = rows[-recent_count:] if recent_count else []
    output = {
        "schema_version": 1,
        "snapshot": {
            "sha256": hashlib.sha256(snapshot).hexdigest(),
            "record_count": len(rows),
            "max_updated_at": format_timestamp(snapshot_end),
            "recent_index": [
                public_row(row) for row in recent_rows
            ],
        },
        "cutoff": {
            "chosen": format_timestamp(cutoff),
            "sources": sources,
        },
        "window": {
            "start_exclusive": format_timestamp(cutoff),
            "end_inclusive": format_timestamp(window_end),
            "cursor_to_persist": format_timestamp(window_end),
            "safe_to_persist": safe_to_persist,
            "carry_forward_from_memory": carry_entries,
            "carry_forward_to_persist": carry_forward_to_persist,
            "carry_forward_memory_field": CARRY_FORWARD_SESSIONS_FIELD,
        },
        "excluded_sessions": excluded_sessions,
        "sessions": resolved,
        "diagnostics": diagnostics,
    }
    if args.compact:
        print(
            json.dumps(
                compact_output(output),
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if safe_to_persist else 2


if __name__ == "__main__":
    sys.exit(main())
