from __future__ import annotations

import json
from pathlib import Path

import pytest

from github_issue_pilot.intervention import (
    CodexAppServerInterventionSessions,
    InterventionAnswer,
    InterventionSession,
    InterventionSessionError,
)


def _request(worktree: Path) -> dict[str, object]:
    return {
        "schema_version": "1",
        "repository": {"full_name": "daniel/probare-crm", "issue_number": 41},
        "run": {
            "id": "run-001",
            "phase": "implementation",
            "operation_key": "run-001:implementation:worker",
        },
        "role": "implementer",
        "context": {
            "worktree_path": str(worktree),
            "branch": "codex/run-run-001",
            "pull_request_number": None,
            "head_sha": None,
        },
        "classification": "product_decision",
        "problem": "Immediate deletion contradicts thirty-day retention.",
        "required_action": "Choose the authoritative retention behavior.",
        "options": [
            {"label": "retain", "impact": "Records remain recoverable."},
            {"label": "delete", "impact": "Records are irrecoverable."},
        ],
        "recommendation": {
            "option_label": "retain",
            "rationale": "It matches the audit requirement.",
        },
        "preserved": {
            "findings": ["Retention requirements conflict."],
            "results": ["No source changes followed the conflict."],
        },
    }


def _fake_server(tmp_path: Path, *, fail_initialize: bool = False) -> tuple[Path, Path, Path]:
    executable = tmp_path / "fake-codex"
    messages = tmp_path / "messages.jsonl"
    arguments = tmp_path / "arguments.json"
    initialize_response = (
        '{"id":1,"error":{"code":-32601,"message":"stable method unavailable"}}'
        if fail_initialize
        else '{"id":1,"result":{"userAgent":"fake-app-server"}}'
    )
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        f"messages = pathlib.Path({str(messages)!r})\n"
        f"pathlib.Path({str(arguments)!r}).write_text(json.dumps(sys.argv[1:]))\n"
        "for line in sys.stdin:\n"
        "    value = json.loads(line)\n"
        "    with messages.open('a') as stream:\n"
        "        stream.write(json.dumps(value, sort_keys=True) + '\\n')\n"
        "    method = value.get('method')\n"
        "    if method == 'initialize':\n"
        f"        print({initialize_response!r}, flush=True)\n"
        "    elif method == 'thread/start':\n"
        "        print(json.dumps({'id': value['id'], 'result': {'thread': {'id': 'thread-001'}}}), flush=True)\n"
        "    elif method == 'thread/name/set':\n"
        "        print(json.dumps({'id': value['id'], 'result': {}}), flush=True)\n"
        "    elif method == 'turn/start':\n"
        "        print(json.dumps({'id': value['id'], 'result': {'turn': {'id': 'turn-001'}}}), flush=True)\n"
        "        print(json.dumps({'method': 'turn/completed', 'params': {'turn': {'id': 'turn-001', 'status': 'completed', 'items': []}}}), flush=True)\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return executable, messages, arguments


def _fake_answer_server(tmp_path: Path) -> tuple[Path, Path]:
    executable = tmp_path / "fake-codex-reader"
    messages = tmp_path / "reader-messages.jsonl"
    thread = {
        "id": "thread-001",
        "turns": [
            {
                "id": "turn-001",
                "status": "completed",
                "items": [
                    {
                        "type": "userMessage",
                        "id": "message-delivery",
                        "content": [{"type": "text", "text": "Intervention request"}],
                    }
                ],
            },
            {
                "id": "turn-002",
                "status": "completed",
                "items": [
                    {
                        "type": "userMessage",
                        "id": "message-answer",
                        "content": [
                            {"type": "text", "text": "Retain records for thirty days."}
                        ],
                    }
                ],
            },
            {
                "id": "turn-003",
                "status": "completed",
                "items": [
                    {
                        "type": "userMessage",
                        "id": "message-repeat",
                        "content": [{"type": "text", "text": "A later conflicting reply."}],
                    }
                ],
            },
        ],
    }
    executable.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        f"messages = pathlib.Path({str(messages)!r})\n"
        f"thread = json.loads({json.dumps(thread)!r})\n"
        "for line in sys.stdin:\n"
        "    value = json.loads(line)\n"
        "    with messages.open('a') as stream:\n"
        "        stream.write(json.dumps(value, sort_keys=True) + '\\n')\n"
        "    method = value.get('method')\n"
        "    if method == 'initialize':\n"
        "        print(json.dumps({'id': value['id'], 'result': {'userAgent': 'fake'}}), flush=True)\n"
        "    elif method == 'thread/read':\n"
        "        print(json.dumps({'id': value['id'], 'result': {'thread': thread}}), flush=True)\n"
        "    elif method == 'thread/archive':\n"
        "        print(json.dumps({'id': value['id'], 'result': {}}), flush=True)\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return executable, messages


def test_named_read_only_intervention_uses_only_stable_stdio_methods(tmp_path) -> None:
    executable, messages_path, arguments_path = _fake_server(tmp_path)
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    request = _request(worktree)

    session = CodexAppServerInterventionSessions(
        executable=str(executable),
        timeout_seconds=5,
    ).deliver(request, worktree=worktree)

    assert session == InterventionSession(thread_id="thread-001", delivery_turn_id="turn-001")
    assert json.loads(arguments_path.read_text()) == ["app-server", "--listen", "stdio://"]
    messages = [json.loads(line) for line in messages_path.read_text().splitlines()]
    assert [message["method"] for message in messages] == [
        "initialize",
        "initialized",
        "thread/start",
        "thread/name/set",
        "turn/start",
    ]
    initialize = messages[0]["params"]
    assert initialize["capabilities"] == {"experimentalApi": False}
    thread_start = messages[2]["params"]
    assert thread_start["cwd"] == str(worktree)
    assert thread_start["sandbox"] == "read-only"
    assert thread_start["approvalPolicy"] == "never"
    assert thread_start["ephemeral"] is False
    assert thread_start["threadSource"] == "appServer"
    title = messages[3]["params"]["name"]
    assert title == "INTERVENTION • daniel/probare-crm#41 • implementation • run-001"
    turn = messages[4]["params"]
    assert turn["sandboxPolicy"] == {"type": "readOnly", "networkAccess": False}
    assert turn["approvalPolicy"] == "never"
    prompt = turn["input"][0]["text"]
    for expected in (
        "Immediate deletion contradicts thirty-day retention.",
        "Choose the authoritative retention behavior.",
        "Records remain recoverable.",
        "It matches the audit requirement.",
        "Retention requirements conflict.",
    ):
        assert expected in prompt
    serialized = json.dumps(messages)
    assert "exec-server" not in serialized
    assert "experimentalApi\": true" not in serialized
    assert "ws://" not in serialized


def test_missing_stable_app_server_surface_fails_closed(tmp_path) -> None:
    executable, _, _ = _fake_server(tmp_path, fail_initialize=True)
    worktree = tmp_path / "worktree"
    worktree.mkdir()

    with pytest.raises(InterventionSessionError, match="stable_surface_unavailable"):
        CodexAppServerInterventionSessions(
            executable=str(executable),
            timeout_seconds=5,
        ).deliver(_request(worktree), worktree=worktree)


def test_first_later_user_turn_is_read_and_answered_history_is_archived(tmp_path) -> None:
    executable, messages_path = _fake_answer_server(tmp_path)
    adapter = CodexAppServerInterventionSessions(
        executable=str(executable),
        timeout_seconds=5,
    )
    session = InterventionSession(thread_id="thread-001", delivery_turn_id="turn-001")

    answer = adapter.read_answer(session)
    adapter.archive(session)

    assert answer == InterventionAnswer(
        turn_id="turn-002",
        text="Retain records for thirty days.",
    )
    messages = [json.loads(line) for line in messages_path.read_text().splitlines()]
    assert [message["method"] for message in messages] == [
        "initialize",
        "initialized",
        "thread/read",
        "initialize",
        "initialized",
        "thread/archive",
    ]
    assert messages[2]["params"] == {"threadId": "thread-001", "includeTurns": True}
    assert messages[5]["params"] == {"threadId": "thread-001"}
    serialized = json.dumps(messages)
    assert "thread/turns/list" not in serialized
    assert "thread/items/list" not in serialized
    assert "experimentalApi\": true" not in serialized
