"""Public black-box contract for the first observable WPCP run slice.

The test intentionally uses only the HTTP API and separate process clients.  It
does not inspect PostgreSQL tables, Agent Framework state, or Durable Task
history; those implementation details must not become the product seam.
"""

from __future__ import annotations

import http.client
from tests.github_provider_fixture import GitHubProviderFixture
import json
import os
import signal
import socket
import subprocess
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor
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
        cls.scratch = tempfile.TemporaryDirectory(prefix="wpcp-control-")
        cls.addClassCleanup(cls.scratch.cleanup)
        provider_input = json.loads(FIXTURE.read_text())
        provider_input["provider"]["repositories"][0]["issues"] += [
            {"issueId": f"issue-{n}", "issueNumber": n, "title": f"Control issue {n}"}
            for n in range(43, 100)]
        cls.fixture_path = Path(cls.scratch.name) / "fixture.json"
        cls.fixture_path.write_text(json.dumps(provider_input))
        cls.next_issue = 43
        cls.provider = GitHubProviderFixture()
        cls.addClassCleanup(cls.provider.close)
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
        environment["WPCP_GITHUB_TEST_ORIGIN"] = cls.provider.origin
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
                    str(cls.fixture_path),
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
        identity = actor_id or (payload or {}).get("actorId", "actor-authorized")
        token = cls.provider.tokens.get(identity, "invalid-token")
        headers["Authorization"] = f"Bearer {token}"
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
            env={**os.environ, "WPCP_FIXTURE_ACCESS_TOKEN": cls.fixture_access_token,
                 "WPCP_PROVIDER_TOKEN": cls.provider.tokens[
                     arguments[arguments.index("--actor-id") + 1] if "--actor-id" in arguments
                     else "actor-authorized"]},
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
        self.assertEqual("repository-access-denied", denied["code"])

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

    def new_run(self):
        number = type(self).next_issue
        type(self).next_issue += 1
        status, result, _ = self.request("POST", f"/api/v1/issues/repo-1/{number}/runs", {
            "commandId": str(uuid.uuid4()), "actorId": "actor-authorized", "note": "control proof",
            "provenance": {"sourceRevision": "r1", "packageRevision": "r1",
                           "configurationRevision": "r1", "contractRevision": "r1"},
        })
        self.assertEqual(201, status, result)
        return result["runId"]

    def read_run(self, run_id, actor="actor-authorized"):
        status, result, _ = self.request("GET", f"/api/v1/runs/{run_id}", actor_id=actor)
        self.assertEqual(200, status, result)
        return result

    def test_concurrent_claim_is_exclusive_and_release_requires_holder(self):
        run_id = self.new_run()
        projection = self.read_run(run_id, "actor-observer")
        fence = {"targetAttemptId": projection["attempts"][0]["attemptId"],
                 "expectedRunVersion": 1, "expectedHeadSha": None, "leaseEpoch": 0}
        path = f"/api/v1/runs/{run_id}/control/claim"
        # Two separate API processes share PostgreSQL; no in-process lock can satisfy this.
        cls = type(self)
        first_api, first_port = cls.api, cls.api_port
        cls.start_api(excluded_ports={first_port})
        self.addCleanup(cls.stop_process, first_api)
        with ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(self.request, "POST", path, fence, actor,
                                port=port) for actor, port in [
                                    ("actor-authorized", first_port),
                                    ("actor-contributor", cls.api_port)]]
            outcomes = [job.result() for job in jobs]
        self.assertEqual([200, 409], sorted(result[0] for result in outcomes), outcomes)
        winner = "actor-authorized" if outcomes[0][0] == 200 else "actor-contributor"
        loser = "actor-contributor" if winner == "actor-authorized" else "actor-authorized"
        current = self.read_run(run_id)["control"]
        self.assertEqual(1, current["leaseEpoch"])
        self.assertEqual("human", current["holder"]["kind"])
        fence.update(expectedRunVersion=current["runVersion"], leaseEpoch=current["leaseEpoch"])
        rejected, decision, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/release", fence, loser)
        self.assertEqual(409, rejected, decision)
        self.assertEqual("control-lease-required", decision["code"])
        status, _, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/release", fence, winner)
        self.assertEqual(200, status)
        status, events, _ = self.request("GET", f"/api/v1/runs/{run_id}/events", actor_id="actor-observer")
        self.assertEqual(200, status)
        self.assertEqual(["ImplementationRunStarted", "ControlLeaseClaimed", "ControlLeaseReleased"],
                         [e["eventType"] for e in events["events"]])

    @staticmethod
    def fence(control):
        return {"targetAttemptId": control["targetAttemptId"],
                "expectedRunVersion": control["runVersion"],
                "expectedHeadSha": control["headSha"], "leaseEpoch": control["leaseEpoch"]}

    def test_each_stale_or_missing_fence_rejects_without_mutation(self):
        run_id = self.new_run()
        current = self.read_run(run_id)["control"]
        path = f"/api/v1/runs/{run_id}/control/claim"
        status, result, _ = self.request("POST", path, self.fence(current))
        self.assertEqual(200, status, result)
        current = result["current"]
        valid = self.fence(current)
        for field, value, code in [
            ("targetAttemptId", str(uuid.uuid4()), "stale-target-attempt"),
            ("expectedRunVersion", 1, "stale-run-version"),
            ("expectedHeadSha", "a" * 40, "stale-head-sha"),
            ("leaseEpoch", 0, "stale-lease-epoch"),
        ]:
            for missing in (False, True):
                with self.subTest(field=field, missing=missing):
                    request = dict(valid)
                    if missing:
                        request.pop(field)
                    else:
                        request[field] = value
                    status, decision, _ = self.request(
                        "POST", f"/api/v1/runs/{run_id}/control/release", request)
                    self.assertEqual(400 if missing else 409, status, decision)
                    self.assertEqual("invalid-control-mutation" if missing else code, decision["code"])
                    self.assertEqual(current, decision["current"])
                    self.assertEqual(current, self.read_run(run_id)["control"])
        status, events, _ = self.request("GET", f"/api/v1/runs/{run_id}/events")
        self.assertEqual(200, status)
        self.assertEqual([1, 2], [event["position"] for event in events["events"]])

    def test_revoked_permission_invalidates_lease_and_regrant_requires_new_claim(self):
        for trigger, retain_read in [("read", True), ("mutation", True), ("read", False)]:
            with self.subTest(trigger=trigger, retain_read=retain_read):
                run_id = self.new_run()
                status, claimed, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/claim",
                    self.fence(self.read_run(run_id)["control"]))
                self.assertEqual(200, status)
                old = claimed["current"]
                identity = self.provider.identities["actor-authorized"]
                identity.update(read=retain_read, push=False)
                try:
                    if trigger == "read":
                        status, result, _ = self.request("GET", f"/api/v1/runs/{run_id}")
                        self.assertEqual(200 if retain_read else 403, status, result)
                    else:
                        status, result, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/release",
                                                       self.fence(old))
                        self.assertEqual(403, status, result)
                    observed = self.read_run(run_id, "actor-observer")["control"]
                    self.assertIsNone(observed["holder"])
                    self.assertGreater(observed["leaseEpoch"], old["leaseEpoch"])
                    self.assertEqual(old["runVersion"] + 1, observed["runVersion"])
                finally:
                    identity.update(read=True, push=True)
                status, rejected, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/claim", self.fence(old))
                self.assertEqual(409, status, rejected)
                status, events, _ = self.request("GET", f"/api/v1/runs/{run_id}/events")
                self.assertEqual(["ImplementationRunStarted", "ControlLeaseClaimed", "ControlLeaseRevoked"],
                                 [event["eventType"] for event in events["events"]])
                status, reclaimed, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/claim",
                    self.fence(self.read_run(run_id)["control"]))
                self.assertEqual(200, status, reclaimed)
                self.assertGreater(reclaimed["current"]["leaseEpoch"], old["leaseEpoch"])

    def control_cli(self, action, run_id, current, actor="actor-authorized"):
        return self.operator_cli(action, "--run-id", run_id,
            "--target-attempt-id", current["targetAttemptId"],
            "--expected-run-version", str(current["runVersion"]),
            "--expected-head-sha", current["headSha"] or "null",
            "--lease-epoch", str(current["leaseEpoch"]), "--actor-id", actor)

    def test_lease_survives_all_clients_and_api_restart_with_same_human_new_token(self):
        run_id = self.new_run()
        exit_code, claimed, _ = self.control_cli("claim", run_id, self.read_run(run_id)["control"])
        self.assertEqual(0, exit_code, claimed)
        current = claimed["current"]
        # The CLI that claimed has already exited. Stop and replace the API, too.
        cls = type(self)
        cls.stop_process(cls.api)
        cls.start_api(excluded_ports={cls.api_port})
        exit_code, observed, _ = self.operator_cli("run", "--run-id", run_id,
            "--actor-id", "same-human-other-client")
        self.assertEqual(0, exit_code, observed)
        self.assertEqual(current, observed["control"])
        self.assertTrue(observed["authorization"]["canRelease"])
        exit_code, rejected, _ = self.control_cli("claim", run_id, current, "actor-contributor")
        self.assertEqual(1, exit_code, rejected)
        self.assertEqual("control-lease-held", rejected["code"])
        exit_code, released, _ = self.control_cli("release", run_id, current, "same-human-other-client")
        self.assertEqual(0, exit_code, released)
        self.assertIsNone(released["current"]["holder"])

    def test_human_history_and_security_audit_are_distinct_from_worker_evidence(self):
        run_id = self.new_run()
        status, accepted, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/claim",
            self.fence(self.read_run(run_id)["control"]))
        self.assertEqual(200, status)
        status, denied, denied_raw = self.request("POST", f"/api/v1/runs/{run_id}/control/release",
            self.fence(accepted["current"]), "worker-bot")
        self.assertEqual(403, status)
        self.assertIsNone(denied["current"])
        exit_code, output = self.worker("--run-id", run_id, "--worker-id", "technical-worker",
                                       "--evidence-note", "controlled service evidence")
        self.assertEqual(0, exit_code, output)
        _, events, events_raw = self.request("GET", f"/api/v1/runs/{run_id}/events")
        self.assertEqual({"kind": "human", "provider": "github", "subjectId": "101"},
                         events["events"][0]["payload"]["actor"])
        self.assertEqual(events["events"][0]["payload"]["actor"],
                         events["events"][1]["payload"]["actor"])
        projection = self.read_run(run_id, "actor-observer")
        worker = next(p for p in projection["processes"] if p["processKind"] == "worker")
        self.assertEqual("service", worker["actor"]["kind"])
        self.assertEqual("service", projection["executionEvidence"][0]["actor"]["kind"])
        exit_code, audit, audit_raw = self.operator_cli("audit", "--run-id", run_id,
                                                     "--actor-id", "actor-observer")
        self.assertEqual(0, exit_code, audit)
        self.assertEqual(["implementation-run-started", "control-lease-claimed", "human-identity-required"],
                         [entry["code"] for entry in audit["entries"]])
        self.assertEqual(["human", "human", "service"],
                         [entry["actor"]["kind"] for entry in audit["entries"]])
        for raw in (denied_raw, events_raw, audit_raw, json.dumps(projection), output):
            for token in self.provider.tokens.values():
                self.assertNotIn(token, raw)
            self.assertNotIn(self.fixture_access_token, raw)

    def test_read_and_control_permissions_fail_closed_at_each_provider_boundary(self):
        run_id = self.new_run()
        current = self.read_run(run_id)["control"]
        for actor in ("actor-observer", "actor-unauthorized", "worker-bot", "unknown"):
            with self.subTest(actor=actor):
                for action in ("claim", "release"):
                    status, decision, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/{action}",
                        self.fence(current), actor)
                    self.assertEqual(401 if actor == "unknown" else 403, status, decision)
                    self.assertFalse(decision["canClaim"])
                    self.assertFalse(decision["canRelease"])
                    self.assertEqual(current if actor == "actor-observer" else None, decision["current"])
                for suffix in ("", "/events", "/audit"):
                    status, result, _ = self.request("GET", f"/api/v1/runs/{run_id}{suffix}", actor_id=actor)
                    self.assertEqual(200 if actor == "actor-observer" else 401 if actor == "unknown" else 403,
                                     status, result)
        self.assertEqual(current, self.read_run(run_id)["control"])
        status, claimed, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/claim", self.fence(current))
        self.assertEqual(200, status)
        current = claimed["current"]
        for failure in (401, 403, 429, 500):
            self.provider.failure = failure
            try:
                status, rejected, raw = self.request("POST", f"/api/v1/runs/{run_id}/control/release",
                    self.fence(current))
                self.assertEqual(401 if failure == 401 else 503, status, rejected)
                self.assertIsNone(rejected["current"])
                self.assertNotIn("controlled upstream failure", raw)
            finally:
                self.provider.failure = None
            self.assertEqual(current, self.read_run(run_id)["control"])
        self.provider.repository_id = 9999
        try:
            status, rejected, _ = self.request("POST", f"/api/v1/runs/{run_id}/control/release", self.fence(current))
            self.assertEqual(403, status)
            self.assertEqual("repository-identity-mismatch", rejected["code"])
            self.assertIsNone(rejected["current"])
        finally:
            self.provider.repository_id = 9001
        self.assertEqual(current, self.read_run(run_id)["control"])

    def test_existing_run_cannot_follow_a_changed_repository_binding(self):
        run_id = self.new_run()
        issue_number = self.read_run(run_id)["correlation"]["issueNumber"]
        original = self.fixture_path.read_text()
        changed = json.loads(original)
        changed["provider"]["repositories"][0]["providerRepositoryId"] = 9999
        cls = type(self)
        cls.stop_process(cls.api)
        self.fixture_path.write_text(json.dumps(changed))
        self.provider.repository_id = 9999
        try:
            cls.start_api(excluded_ports={cls.api_port})
            status, result, _ = self.request("GET", f"/api/v1/runs/{run_id}")
            self.assertEqual(403, status, result)
            self.assertEqual("repository-identity-mismatch", result["code"])
            self.assertIsNone(result["current"])
            status, result, raw = self.request("POST", f"/api/v1/issues/repo-1/{issue_number}/runs", {
                "commandId": str(uuid.uuid4()), "note": "rebound admission",
                "provenance": {"sourceRevision": "r1", "packageRevision": "r1",
                    "configurationRevision": "r1", "contractRevision": "r1"}})
            self.assertEqual(403, status, result)
            self.assertNotIn(run_id, raw)
        finally:
            cls.stop_process(cls.api)
            self.fixture_path.write_text(original)
            self.provider.repository_id = 9001
            cls.start_api(excluded_ports={cls.api_port})
        self.assertEqual(run_id, self.read_run(run_id)["runId"])

    def test_reader_cannot_impersonate_contributor_in_start_payload(self):
        status, result, _ = self.request("POST", "/api/v1/issues/repo-1/41/runs", {
            "commandId": str(uuid.uuid4()), "actorId": "actor-authorized", "note": "spoof",
            "provenance": {"sourceRevision": "r1", "packageRevision": "r1",
                           "configurationRevision": "r1", "contractRevision": "r1"},
        }, actor_id="actor-observer")
        self.assertEqual(403, status, result)
        self.assertEqual("repository-contribution-required", result["code"])

    @staticmethod
    def instant(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


if __name__ == "__main__":
    unittest.main()
