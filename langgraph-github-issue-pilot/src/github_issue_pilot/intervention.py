from __future__ import annotations

import json
import queue
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TextIO

from jsonschema import ValidationError
from jsonschema.validators import Draft202012Validator

from github_issue_pilot.contracts import load_contract


class InvalidInterventionContract(ValueError):
    pass


class InterventionSessionError(RuntimeError):
    pass


class InterventionContinuationError(RuntimeError):
    pass


@dataclass(frozen=True)
class InterventionSession:
    thread_id: str
    delivery_turn_id: str


@dataclass(frozen=True)
class InterventionAnswer:
    turn_id: str
    text: str


class InterventionSessionPort(Protocol):
    def deliver(
        self,
        request: dict[str, object],
        *,
        worktree: Path,
    ) -> InterventionSession: ...

    def read_answer(self, session: InterventionSession) -> InterventionAnswer | None: ...

    def archive(self, session: InterventionSession) -> None: ...


def bounded_intervention_answer(
    application: dict[str, object],
    resumed: object,
    *,
    phase: str,
) -> dict[str, str]:
    if not isinstance(resumed, dict):
        raise InterventionContinuationError(f"{phase} intervention resume is malformed")
    actual = (
        resumed.get("intervention_id"),
        resumed.get("answer_turn_id"),
        resumed.get("answer_text"),
    )
    expected = (
        application["id"],
        application["answer_turn_id"],
        application["answer_text"],
    )
    if actual != expected or not all(isinstance(value, str) and value for value in actual):
        raise InterventionContinuationError(
            f"{phase} intervention resume does not match its persisted answer"
        )
    return {
        "intervention_id": str(actual[0]),
        "answer_turn_id": str(actual[1]),
        "answer_text": str(actual[2]),
    }


class CodexAppServerInterventionSessions:
    def __init__(
        self,
        *,
        executable: str = "codex",
        timeout_seconds: float = 3600,
    ) -> None:
        self._executable = executable
        self._timeout_seconds = timeout_seconds

    def deliver(
        self,
        request: dict[str, object],
        *,
        worktree: Path,
    ) -> InterventionSession:
        validate_intervention_request(request)
        context = request["context"]
        if not isinstance(context, dict) or Path(str(context["worktree_path"])).resolve() != (
            worktree.resolve()
        ):
            raise InterventionSessionError("intervention worktree does not match its request")
        if not worktree.is_dir():
            raise InterventionSessionError("intervention worktree is unavailable")

        command = [self._executable, "app-server", "--listen", "stdio://"]
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise InterventionSessionError("stable_surface_unavailable") from exc
        if process.stdin is None or process.stdout is None:
            process.terminate()
            raise InterventionSessionError("stable_surface_unavailable")

        pending_notifications: list[dict[str, object]] = []
        deadline = time.monotonic() + self._timeout_seconds
        try:
            self._call(
                process.stdin,
                process.stdout,
                request_id=1,
                method="initialize",
                params={
                    "clientInfo": {
                        "name": "github-issue-pilot",
                        "title": "GitHub Issue Pilot Interventions",
                        "version": "1",
                    },
                    "capabilities": {"experimentalApi": False},
                },
                deadline=deadline,
                pending_notifications=pending_notifications,
            )
            self._send(process.stdin, {"method": "initialized", "params": {}})
            thread_result = self._call(
                process.stdin,
                process.stdout,
                request_id=2,
                method="thread/start",
                params={
                    "cwd": str(worktree.resolve()),
                    "model": "gpt-5.6-luna",
                    "approvalPolicy": "never",
                    "sandbox": "read-only",
                    "ephemeral": False,
                    "serviceName": "github-issue-pilot",
                    "threadSource": "appServer",
                    "developerInstructions": (
                        "This read-only task presents one durable intervention request. "
                        "Do not inspect or modify files, call tools, broaden the request, or "
                        "decide for Daniel. Briefly acknowledge the request and wait for his answer."
                    ),
                },
                deadline=deadline,
                pending_notifications=pending_notifications,
            )
            thread = thread_result.get("thread")
            if not isinstance(thread, dict) or not isinstance(thread.get("id"), str):
                raise InterventionSessionError("stable_surface_invalid_response")
            thread_id = str(thread["id"])
            self._call(
                process.stdin,
                process.stdout,
                request_id=3,
                method="thread/name/set",
                params={"threadId": thread_id, "name": self._title(request)},
                deadline=deadline,
                pending_notifications=pending_notifications,
            )
            turn_result = self._call(
                process.stdin,
                process.stdout,
                request_id=4,
                method="turn/start",
                params={
                    "threadId": thread_id,
                    "input": [{"type": "text", "text": self._prompt(request)}],
                    "cwd": str(worktree.resolve()),
                    "model": "gpt-5.6-luna",
                    "effort": "medium",
                    "approvalPolicy": "never",
                    "sandboxPolicy": {"type": "readOnly", "networkAccess": False},
                    "clientUserMessageId": str(request["run"]["operation_key"]),
                },
                deadline=deadline,
                pending_notifications=pending_notifications,
            )
            turn = turn_result.get("turn")
            if not isinstance(turn, dict) or not isinstance(turn.get("id"), str):
                raise InterventionSessionError("stable_surface_invalid_response")
            turn_id = str(turn["id"])
            self._wait_for_turn(
                process.stdout,
                turn_id=turn_id,
                deadline=deadline,
                pending_notifications=pending_notifications,
            )
            return InterventionSession(thread_id=thread_id, delivery_turn_id=turn_id)
        except (BrokenPipeError, json.JSONDecodeError, OSError, TimeoutError) as exc:
            raise InterventionSessionError("stable_surface_unavailable") from exc
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=max(0.1, min(2.0, self._timeout_seconds)))
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=1)

    def read_answer(self, session: InterventionSession) -> InterventionAnswer | None:
        result = self._single_method(
            "thread/read",
            {"threadId": session.thread_id, "includeTurns": True},
        )
        thread = result.get("thread")
        turns = thread.get("turns") if isinstance(thread, dict) else None
        if not isinstance(turns, list):
            raise InterventionSessionError("stable_surface_invalid_response")
        delivery_seen = False
        for turn in turns:
            if not isinstance(turn, dict) or not isinstance(turn.get("id"), str):
                raise InterventionSessionError("stable_surface_invalid_response")
            turn_id = str(turn["id"])
            if not delivery_seen:
                delivery_seen = turn_id == session.delivery_turn_id
                continue
            items = turn.get("items")
            if not isinstance(items, list):
                raise InterventionSessionError("stable_surface_invalid_response")
            for item in items:
                if not isinstance(item, dict) or item.get("type") != "userMessage":
                    continue
                content = item.get("content")
                if not isinstance(content, list):
                    raise InterventionSessionError("stable_surface_invalid_response")
                text = "\n".join(
                    str(part["text"])
                    for part in content
                    if isinstance(part, dict)
                    and part.get("type") == "text"
                    and str(part.get("text", "")).strip()
                ).strip()
                if text:
                    return InterventionAnswer(turn_id=turn_id, text=text)
        if not delivery_seen:
            raise InterventionSessionError("stable_surface_invalid_response")
        return None

    def archive(self, session: InterventionSession) -> None:
        self._single_method("thread/archive", {"threadId": session.thread_id})

    def _single_method(
        self,
        method: str,
        params: dict[str, object],
    ) -> dict[str, object]:
        try:
            process = subprocess.Popen(
                [self._executable, "app-server", "--listen", "stdio://"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise InterventionSessionError("stable_surface_unavailable") from exc
        if process.stdin is None or process.stdout is None:
            process.terminate()
            raise InterventionSessionError("stable_surface_unavailable")
        deadline = time.monotonic() + self._timeout_seconds
        pending_notifications: list[dict[str, object]] = []
        try:
            self._call(
                process.stdin,
                process.stdout,
                request_id=1,
                method="initialize",
                params={
                    "clientInfo": {
                        "name": "github-issue-pilot",
                        "title": "GitHub Issue Pilot Interventions",
                        "version": "1",
                    },
                    "capabilities": {"experimentalApi": False},
                },
                deadline=deadline,
                pending_notifications=pending_notifications,
            )
            self._send(process.stdin, {"method": "initialized", "params": {}})
            return self._call(
                process.stdin,
                process.stdout,
                request_id=2,
                method=method,
                params=params,
                deadline=deadline,
                pending_notifications=pending_notifications,
            )
        except (BrokenPipeError, json.JSONDecodeError, OSError, TimeoutError) as exc:
            raise InterventionSessionError("stable_surface_unavailable") from exc
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=max(0.1, min(2.0, self._timeout_seconds)))
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=1)

    @staticmethod
    def _send(stream: TextIO, message: dict[str, object]) -> None:
        stream.write(json.dumps(message, separators=(",", ":"), sort_keys=True) + "\n")
        stream.flush()

    def _call(
        self,
        stdin: TextIO,
        stdout: TextIO,
        *,
        request_id: int,
        method: str,
        params: dict[str, object],
        deadline: float,
        pending_notifications: list[dict[str, object]],
    ) -> dict[str, object]:
        self._send(stdin, {"method": method, "id": request_id, "params": params})
        while True:
            message = self._read(stdout, deadline)
            if message.get("id") == request_id:
                if "error" in message:
                    raise InterventionSessionError("stable_surface_unavailable")
                result = message.get("result")
                if not isinstance(result, dict):
                    raise InterventionSessionError("stable_surface_invalid_response")
                return result
            if isinstance(message.get("method"), str):
                pending_notifications.append(message)

    def _wait_for_turn(
        self,
        stdout: TextIO,
        *,
        turn_id: str,
        deadline: float,
        pending_notifications: list[dict[str, object]],
    ) -> None:
        while True:
            message = (
                pending_notifications.pop(0)
                if pending_notifications
                else self._read(stdout, deadline)
            )
            if message.get("method") != "turn/completed":
                continue
            params = message.get("params")
            turn = params.get("turn") if isinstance(params, dict) else None
            if not isinstance(turn, dict) or turn.get("id") != turn_id:
                continue
            if turn.get("status") != "completed":
                raise InterventionSessionError("stable_surface_turn_failed")
            return

    @staticmethod
    def _read(stream: TextIO, deadline: float) -> dict[str, object]:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Codex app-server response timed out")
        lines: queue.Queue[str] = queue.Queue(maxsize=1)
        reader = threading.Thread(target=lambda: lines.put(stream.readline()), daemon=True)
        reader.start()
        try:
            line = lines.get(timeout=remaining)
        except queue.Empty as exc:
            raise TimeoutError("Codex app-server response timed out") from exc
        if not line:
            raise OSError("Codex app-server closed its response stream")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise json.JSONDecodeError("JSON-RPC message must be an object", line, 0)
        return value

    @staticmethod
    def _title(request: dict[str, object]) -> str:
        repository = request["repository"]
        run = request["run"]
        if not isinstance(repository, dict) or not isinstance(run, dict):
            raise InvalidInterventionContract("intervention identity is malformed")
        return (
            f"INTERVENTION • {repository['full_name']}#{repository['issue_number']} • "
            f"{run['phase']} • {run['id']}"
        )

    @staticmethod
    def _prompt(request: dict[str, object]) -> str:
        return (
            "# Interventionsanfrage\n\n"
            "Diese Anfrage gehoert zu einem dauerhaften Pilot-Lauf. Antworte mit der benoetigten "
            "Entscheidung oder Handlung; die Antwort erweitert das bestehende Arbeitsmandat nicht.\n\n"
            "```json\n"
            f"{json.dumps(request, ensure_ascii=False, indent=2, sort_keys=True)}\n"
            "```"
        )


def validate_intervention_request(request: dict[str, object]) -> None:
    try:
        Draft202012Validator(load_contract("intervention-request-v1.json")).validate(request)
    except ValidationError as exc:
        raise InvalidInterventionContract(
            f"intervention request does not match schema: {exc.message}"
        ) from exc
