"""Public black-box contract for the first observable WPCP run slice.

The test intentionally uses only the HTTP API and separate process clients.  It
does not inspect PostgreSQL tables, Agent Framework state, or Durable Task
history; those implementation details must not become the product seam.
"""

from __future__ import annotations

import http.client
import json
import os
import signal
import socket
import subprocess
import time
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


PILOT_ROOT = Path(__file__).resolve().parents[1]
SOLUTION = PILOT_ROOT / "Wpcp.WorkPackageControlPlane.sln"
API_PROJECT = PILOT_ROOT / "src" / "Wpcp.Api" / "Wpcp.Api.csproj"
WORKER_PROJECT = PILOT_ROOT / "src" / "Wpcp.Worker" / "Wpcp.Worker.csproj"
CLI_PROJECT = PILOT_ROOT / "src" / "Wpcp.OperatorCli" / "Wpcp.OperatorCli.csproj"
API_DLL = API_PROJECT.parent / "bin" / "Debug" / "net10.0" / "Wpcp.Api.dll"
WORKER_DLL = WORKER_PROJECT.parent / "bin" / "Debug" / "net10.0" / "Wpcp.Worker.dll"
CLI_DLL = CLI_PROJECT.parent / "bin" / "Debug" / "net10.0" / "Wpcp.OperatorCli.dll"
FIXTURE = (
    PILOT_ROOT
    / "tests"
    / "Wpcp.BlackBox.Tests"
    / "fixtures"
    / "synthetic-provider-redaction-fixture.json"
)
POSTGRES_FIXTURE = (
    PILOT_ROOT
    / "tests"
    / "Wpcp.BlackBox.Tests"
    / "fixtures"
    / "postgres-test-fixture.json"
)


def free_port(*, excluded: set[int] | None = None) -> int:
    while True:
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = int(listener.getsockname()[1])
        if port not in (excluded or set()):
            return port


def command_output(
    command: list[str], *, timeout: int = 120, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PILOT_ROOT,
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
    )


class ObservableRunBlackBoxTests(unittest.TestCase):
    api: subprocess.Popen[str] | None
    postgres_name: str
    postgres_port: int
    api_port: int
    connection_string: str
    base_url: str
    fixture_access_token: str

    @classmethod
    def setUpClass(cls) -> None:
        fixture = json.loads(POSTGRES_FIXTURE.read_text(encoding="utf-8"))
        database = fixture["database"]
        cls.postgres_name = f"wpcp-blackbox-{uuid.uuid4().hex[:12]}"
        cls.fixture_access_token = uuid.uuid4().hex + uuid.uuid4().hex
        cls.api = None
        cls.addClassCleanup(cls.cleanup_resources)

        build = command_output(
            ["dotnet", "build", str(SOLUTION), "--no-restore"], timeout=180
        )
        if build.returncode:
            raise RuntimeError(f"control-plane build failed:\n{build.stdout}\n{build.stderr}")

        start_database = command_output(
            [
                "docker",
                "run",
                "--detach",
                "--rm",
                "--name",
                cls.postgres_name,
                "--publish",
                "127.0.0.1::5432",
                "--env",
                f"POSTGRES_DB={database['name']}",
                "--env",
                f"POSTGRES_USER={database['username']}",
                "--env",
                f"POSTGRES_PASSWORD={database['password']}",
                fixture["docker"]["image"],
            ],
            timeout=60,
        )
        if start_database.returncode:
            raise RuntimeError(
                f"could not start disposable PostgreSQL:\n{start_database.stdout}\n"
                f"{start_database.stderr}"
            )
        cls.postgres_port = cls.published_postgres_port()
        cls.connection_string = (
            f"Host={database['host']};Port={cls.postgres_port};"
            f"Database={database['name']};Username={database['username']};"
            f"Password={database['password']};Pooling=false"
        )
        cls.wait_for_database(int(fixture["docker"]["readiness"]["timeoutSeconds"]))
        cls.start_api()

    @classmethod
    def cleanup_resources(cls) -> None:
        api = getattr(cls, "api", None)
        if api is not None:
            cls.stop_process(api)
            cls.api = None
        if getattr(cls, "postgres_name", None):
            command_output(["docker", "rm", "--force", cls.postgres_name], timeout=30)

    @classmethod
    def wait_for_database(cls, timeout_seconds: int) -> None:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            ready = command_output(
                [
                    "docker",
                    "exec",
                    cls.postgres_name,
                    "pg_isready",
                    "-U",
                    "wpcp_test",
                    "-d",
                    "wpcp_test",
                ],
                timeout=15,
            )
            if ready.returncode == 0:
                return
            time.sleep(0.2)
        raise TimeoutError("disposable PostgreSQL did not become ready")

    @classmethod
    def published_postgres_port(cls) -> int:
        published = command_output(
            ["docker", "port", cls.postgres_name, "5432/tcp"], timeout=30
        )
        if published.returncode:
            raise RuntimeError(f"could not resolve PostgreSQL port: {published.stderr}")
        try:
            return int(published.stdout.strip().rsplit(":", 1)[1])
        except (IndexError, ValueError) as error:
            raise RuntimeError(f"unexpected Docker port output: {published.stdout!r}") from error

    @classmethod
    def start_api(cls, *, excluded_ports: set[int] | None = None) -> None:
        environment = dict(os.environ)
        environment["WPCP_FIXTURE_ACCESS_TOKEN"] = cls.fixture_access_token
        for _ in range(5):
            api_port = free_port(excluded=excluded_ports)
            base_url = f"http://127.0.0.1:{api_port}"
            process = subprocess.Popen(
                [
                    "dotnet",
                    str(API_DLL),
                    "--connection-string",
                    cls.connection_string,
                    "--fixture",
                    str(FIXTURE),
                    "--urls",
                    base_url,
                ],
                cwd=PILOT_ROOT,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=environment,
                start_new_session=True,
            )
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                status, _payload, _raw = cls.request("GET", "/healthz", port=api_port)
                if status == 200:
                    cls.api = process
                    cls.api_port = api_port
                    cls.base_url = base_url
                    return
                time.sleep(0.1)
            cls.stop_process(process)
        raise RuntimeError("API process exited before its health endpoint was ready")

    @staticmethod
    def stop_process(process: subprocess.Popen[str]) -> None:
        if process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=15)

    @classmethod
    def request(
        cls,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        actor_id: str | None = None,
        *,
        include_fixture_access: bool = True,
        port: int | None = None,
    ) -> tuple[int, dict[str, Any], str]:
        body = None if payload is None else json.dumps(payload)
        headers: dict[str, str] = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if actor_id is not None:
            headers["X-Wpcp-Actor-Id"] = actor_id
        if include_fixture_access:
            headers["X-Wpcp-Fixture-Access"] = cls.fixture_access_token
        connection = http.client.HTTPConnection("127.0.0.1", port or cls.api_port, timeout=15)
        try:
            try:
                connection.request(method, path, body=body, headers=headers)
                response = connection.getresponse()
                raw = response.read().decode("utf-8")
                content_type = response.getheader("Content-Type") or ""
                decoded = json.loads(raw) if raw and "json" in content_type else {}
                return response.status, decoded, raw
            except OSError:
                # Startup probes race Kestrel's socket bind.  The caller retries
                # health checks; substantive test calls happen only after ready.
                return 0, {}, ""
        finally:
            connection.close()

    @classmethod
    def operator_cli(cls, *arguments: str) -> tuple[int, dict[str, Any], str]:
        completed = command_output(
            [
                "dotnet",
                str(CLI_DLL),
                "--base-url",
                cls.base_url,
                *arguments,
            ],
            timeout=60,
            env={**os.environ, "WPCP_FIXTURE_ACCESS_TOKEN": cls.fixture_access_token},
        )
        output = completed.stdout.strip()
        try:
            payload = json.loads(output) if output else {}
        except json.JSONDecodeError as error:
            raise AssertionError(
                f"operator CLI did not emit one JSON document:\nstdout={output}\nstderr={completed.stderr}"
            ) from error
        return completed.returncode, payload, output

    @classmethod
    def worker(cls, *arguments: str) -> tuple[int, str]:
        completed = command_output(
            [
                "dotnet",
                str(WORKER_DLL),
                "--connection-string",
                cls.connection_string,
                "--fixture",
                str(FIXTURE),
                *arguments,
            ],
            timeout=60,
        )
        return completed.returncode, completed.stdout + completed.stderr

    def test_authorized_issue_is_one_redacted_observable_run_across_restarts(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        secret = fixture["redactionPolicy"]["controlledCanaries"][0]["value"]
        worker_only_secret = fixture["redactionPolicy"]["controlledCanaries"][1]["value"]
        command_id = str(uuid.uuid4())
        start_payload = {
            "commandId": command_id,
            "actorId": "actor-authorized",
            "note": f"start synthetic issue with {secret}",
            "provenance": {
                "sourceRevision": "source-r1",
                "packageRevision": "package-r1",
                "configurationRevision": "config-r1",
                "contractRevision": "contract-r1",
            },
        }

        no_access_status, no_access, no_access_raw = self.request(
            "POST",
            "/api/v1/issues/repo-1/41/runs",
            start_payload,
            include_fixture_access=False,
        )
        self.assertEqual(403, no_access_status)
        self.assertEqual("synthetic-access-denied", no_access["code"])

        unauthorized_payload = dict(start_payload)
        unauthorized_payload["commandId"] = str(uuid.uuid4())
        unauthorized_payload["actorId"] = "actor-unauthorized"
        denied_status, denied, denied_raw = self.request(
            "POST", "/api/v1/issues/repo-1/41/runs", unauthorized_payload
        )
        self.assertEqual(403, denied_status)
        self.assertEqual("synthetic-authorization-denied", denied["code"])

        canary_correlation_payload = dict(start_payload)
        canary_correlation_payload["commandId"] = f"command-{secret}"
        canary_correlation_payload["note"] = "controlled correlation field"
        canary_status, canary_rejection, canary_raw = self.request(
            "POST", "/api/v1/issues/repo-1/41/runs", canary_correlation_payload
        )
        self.assertEqual(400, canary_status)
        self.assertEqual("invalid-start-command", canary_rejection["code"])
        self.assertNotIn(secret, canary_raw)

        accepted_exit, accepted, accepted_raw = self.operator_cli(
            "start",
            "--repository-id",
            "repo-1",
            "--issue-number",
            "41",
            "--actor-id",
            "actor-authorized",
            "--command-id",
            command_id,
            "--note",
            start_payload["note"],
            "--source-revision",
            "source-r1",
            "--package-revision",
            "package-r1",
            "--configuration-revision",
            "config-r1",
            "--contract-revision",
            "contract-r1",
        )
        self.assertEqual(0, accepted_exit)
        self.assertEqual("accepted", accepted["outcome"])
        self.assertFalse(accepted["idempotent"])
        self.assertEqual(command_id, accepted["commandId"])
        run_id = accepted["runId"]

        duplicate_exit, duplicate, duplicate_raw = self.operator_cli(
            "start",
            "--repository-id",
            "repo-1",
            "--issue-number",
            "41",
            "--actor-id",
            "actor-authorized",
            "--command-id",
            command_id,
            "--note",
            start_payload["note"],
            "--source-revision",
            "source-r1",
            "--package-revision",
            "package-r1",
            "--configuration-revision",
            "config-r1",
            "--contract-revision",
            "contract-r1",
        )
        self.assertEqual(0, duplicate_exit)
        self.assertEqual("idempotent", duplicate["outcome"])
        self.assertTrue(duplicate["idempotent"])
        self.assertEqual(run_id, duplicate["runId"])

        conflict_payload = dict(start_payload)
        conflict_payload["note"] = "same command identity, different canonical payload"
        conflict_status, conflict, conflict_raw = self.request(
            "POST", "/api/v1/issues/repo-1/41/runs", conflict_payload
        )
        self.assertEqual(409, conflict_status)
        self.assertEqual("command-id-conflict", conflict["code"])
        self.assertEqual(run_id, conflict["runId"])

        worker_one_exit, worker_one_output = self.worker(
            "--run-id",
            run_id,
            "--worker-id",
            "worker-one",
            "--agent-framework-workflow-id",
            "framework-workflow-1",
            "--durable-task-orchestration-id",
            "durability-orchestration-1",
            "--evidence-note",
            f"worker evidence also contains {secret}",
        )
        self.assertEqual(0, worker_one_exit, worker_one_output)

        observer_exit, projection, projection_raw = self.operator_cli(
            "run", "--run-id", run_id, "--actor-id", "actor-observer"
        )
        self.assertEqual(0, observer_exit)
        self.assertEqual(run_id, projection["runId"])
        self.assertEqual("admitted", projection["state"])
        self.assertEqual("repo-1", projection["correlation"]["repositoryId"])
        self.assertEqual(41, projection["correlation"]["issueNumber"])
        self.assertEqual(command_id, projection["correlation"]["commandId"])
        self.assertTrue(projection["activities"])
        self.assertTrue(projection["attempts"])
        self.assertIn("runStartedAt", projection)
        self.assertTrue(projection["processes"])
        self.assertTrue(projection["heartbeats"])
        self.assertTrue(all(attempt["startedAt"] for attempt in projection["attempts"]))
        self.assertTrue(all(attempt["completedAt"] for attempt in projection["attempts"]))
        self.assertTrue(all(process["processStartedAt"] for process in projection["processes"]))
        self.assertTrue(any(process["processStoppedAt"] for process in projection["processes"]))
        self.assertTrue(all(heartbeat["heartbeatAt"] for heartbeat in projection["heartbeats"]))
        worker_processes = [
            process for process in projection["processes"] if process["processKind"] == "worker"
        ]
        self.assertEqual(1, len(worker_processes))
        first_worker = worker_processes[0]
        self.assertIsNotNone(first_worker["processStoppedAt"])
        worker_started_at = self.instant(first_worker["processStartedAt"])
        worker_stopped_at = self.instant(first_worker["processStoppedAt"])
        self.assertLess(worker_started_at, worker_stopped_at)
        first_worker_heartbeats = [
            heartbeat
            for heartbeat in projection["heartbeats"]
            if heartbeat["processId"] == first_worker["processId"]
        ]
        self.assertGreaterEqual(len(first_worker_heartbeats), 2)
        for heartbeat in first_worker_heartbeats:
            heartbeat_at = self.instant(heartbeat["heartbeatAt"])
            self.assertGreaterEqual(heartbeat_at, worker_started_at)
            self.assertLessEqual(heartbeat_at, worker_stopped_at)
        self.assertEqual(
            start_payload["provenance"],
            projection["provenance"],
        )
        self.assertTrue(projection["redaction"]["occurred"])
        self.assertEqual("controlled-canary-v1", projection["redaction"]["policyVersion"])
        self.assertEqual(
            "[REDACTED:CONTROLLED-CANARY]", projection["redaction"]["marker"]
        )
        self.assertTrue(projection["executionEvidence"])
        evidence = projection["executionEvidence"][0]
        self.assertEqual("framework-workflow-1", evidence["agentFrameworkWorkflowId"])
        self.assertEqual(
            "durability-orchestration-1", evidence["durableTaskOrchestrationId"]
        )

        events_exit, events, events_raw = self.operator_cli(
            "events", "--run-id", run_id, "--after", "0", "--actor-id", "actor-observer"
        )
        self.assertEqual(0, events_exit)
        positions = [event["position"] for event in events["events"]]
        self.assertEqual(sorted(set(positions)), positions)
        self.assertTrue(positions)
        self.assertEqual(positions[-1], events["lastPosition"])
        self.assertTrue(all(event["position"] > 0 for event in events["events"]))

        after_exit, after_events, after_raw = self.operator_cli(
            "events",
            "--run-id",
            run_id,
            "--after",
            str(positions[-1]),
            "--actor-id",
            "actor-observer",
        )
        self.assertEqual(0, after_exit)
        self.assertEqual([], after_events["events"])

        original_positions = positions[:]
        assert self.api is not None
        old_api = self.api
        old_api_port = self.api_port
        self.stop_process(old_api)
        self.assertIsNotNone(old_api.poll())
        stopped_status, _stopped, _stopped_raw = self.request(
            "GET", "/healthz", include_fixture_access=False, port=old_api_port
        )
        self.assertEqual(0, stopped_status)
        self.api = None
        self.start_api(excluded_ports={old_api_port})
        self.assertNotEqual(old_api_port, self.api_port)
        worker_two_exit, worker_two_output = self.worker(
            "--run-id",
            run_id,
            "--worker-id",
            "worker-two",
            "--agent-framework-workflow-id",
            "framework-workflow-2",
            "--durable-task-orchestration-id",
            "durability-orchestration-2",
            "--evidence-note",
            "replacement worker evidence",
        )
        self.assertEqual(0, worker_two_exit, worker_two_output)
        restarted_exit, restarted, restarted_raw = self.operator_cli(
            "run", "--run-id", run_id, "--actor-id", "actor-observer"
        )
        self.assertEqual(0, restarted_exit)
        self.assertEqual(run_id, restarted["runId"])
        self.assertEqual(command_id, restarted["correlation"]["commandId"])
        self.assertGreaterEqual(len(restarted["processes"]), 2)
        self.assertGreaterEqual(len(restarted["heartbeats"]), 2)
        self.assertGreaterEqual(len(restarted["executionEvidence"]), 2)
        restarted_workers = [
            process for process in restarted["processes"] if process["processKind"] == "worker"
        ]
        self.assertEqual(2, len(restarted_workers))
        self.assertEqual(2, len({process["processId"] for process in restarted_workers}))
        for worker in restarted_workers:
            self.assertIsNotNone(worker["processStoppedAt"])
            self.assertLess(
                self.instant(worker["processStartedAt"]),
                self.instant(worker["processStoppedAt"]),
            )
        restarted_api_processes = [
            process for process in restarted["processes"] if process["processKind"] == "api"
        ]
        self.assertGreaterEqual(len(restarted_api_processes), 2)
        self.assertTrue(any(process["processStoppedAt"] for process in restarted_api_processes))

        restarted_events_exit, restarted_events, restarted_events_raw = self.operator_cli(
            "events", "--run-id", run_id, "--after", "0", "--actor-id", "actor-observer"
        )
        self.assertEqual(0, restarted_events_exit)
        self.assertEqual(
            original_positions,
            [event["position"] for event in restarted_events["events"]],
        )

        clean_command_id = str(uuid.uuid4())
        clean_start_exit, clean_start, clean_start_raw = self.operator_cli(
            "start",
            "--repository-id",
            "repo-1",
            "--issue-number",
            "42",
            "--actor-id",
            "actor-authorized",
            "--command-id",
            clean_command_id,
            "--note",
            "clean admission without a controlled canary",
            "--source-revision",
            "source-r2",
            "--package-revision",
            "package-r2",
            "--configuration-revision",
            "config-r2",
            "--contract-revision",
            "contract-r2",
        )
        self.assertEqual(0, clean_start_exit)
        clean_run_id = clean_start["runId"]
        clean_worker_exit, clean_worker_output = self.worker(
            "--run-id",
            clean_run_id,
            "--worker-id",
            "worker-redaction-only",
            "--evidence-note",
            f"only worker evidence contains {worker_only_secret}",
        )
        self.assertEqual(0, clean_worker_exit, clean_worker_output)
        clean_observer_exit, clean_projection, clean_projection_raw = self.operator_cli(
            "run", "--run-id", clean_run_id, "--actor-id", "actor-observer"
        )
        self.assertEqual(0, clean_observer_exit)
        self.assertTrue(clean_projection["redaction"]["occurred"])
        self.assertTrue(clean_projection["executionEvidence"])
        clean_evidence = clean_projection["executionEvidence"][0]
        self.assertTrue(clean_evidence["redaction"]["occurred"])
        self.assertEqual(
            "[REDACTED:CONTROLLED-CANARY]",
            clean_evidence["redaction"]["marker"],
        )

        public_surfaces = [
            accepted_raw,
            duplicate_raw,
            conflict_raw,
            denied_raw,
            no_access_raw,
            canary_raw,
            projection_raw,
            events_raw,
            after_raw,
            restarted_raw,
            restarted_events_raw,
            clean_start_raw,
            clean_projection_raw,
            worker_one_output,
            worker_two_output,
            clean_worker_output,
        ]
        for surface in public_surfaces:
            self.assertNotIn(secret, surface)
            self.assertNotIn(worker_only_secret, surface)

    @staticmethod
    def instant(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


if __name__ == "__main__":
    unittest.main()
