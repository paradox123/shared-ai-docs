"""Run the controlled two-process worker replacement probe."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import time
import uuid
from collections.abc import Callable
from pathlib import Path


def _events(ledger: Path) -> list[dict[str, object]]:
    if not ledger.exists():
        return []
    result: list[dict[str, object]] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            result.append(value)
    return result


def _wait_for_event(
    ledger: Path,
    predicate: Callable[[dict[str, object]], bool],
    process: subprocess.Popen[bytes],
    timeout_seconds: int,
) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if any(predicate(event) for event in _events(ledger)):
            return True
        if process.poll() is not None:
            return False
        time.sleep(0.1)
    return False


def _worker_command(
    base: list[str], worker_name: str, run_id: str, ledger: Path, start_run: bool
) -> list[str]:
    command = base + [
        "--worker-name",
        worker_name,
        "--run-id",
        run_id,
        "--ledger",
        str(ledger),
    ]
    if start_run:
        command.append("--start-run")
    return command


def _stop_process_group(process: subprocess.Popen[bytes]) -> None:
    """Abruptly stop a launcher and all descendants to simulate worker loss."""
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGKILL)
    process.wait(timeout=10)


def _prepare_probe(
    command: list[str], pilot_root: Path
) -> tuple[dict[str, object], list[str]]:
    if command[:2] != ["dotnet", "run"]:
        return {"mode": "test-fixture", "commands": []}, []
    project = pilot_root / "ManagedDurabilityProbe" / "ManagedDurabilityProbe.csproj"
    commands = [
        ["dotnet", "restore", "--locked-mode", str(project)],
        ["dotnet", "build", "--no-restore", str(project)],
    ]
    for build_command in commands:
        completed = subprocess.run(
            build_command,
            cwd=pilot_root,
            check=False,
            capture_output=True,
            timeout=120,
        )
        if completed.returncode != 0:
            return {
                "mode": "locked-dotnet-build",
                "commands": commands,
                "failedCommand": build_command,
                "exitCode": completed.returncode,
            }, ["probe.locked-build-failed"]
    assembly = (
        pilot_root
        / "ManagedDurabilityProbe"
        / "bin"
        / "Debug"
        / "net10.0"
        / "ManagedDurabilityProbe.dll"
    )
    return {
        "mode": "locked-dotnet-build",
        "commands": commands,
        "workerAssembly": str(assembly),
        "workerAssemblySha256": hashlib.sha256(assembly.read_bytes()).hexdigest(),
    }, []


def run_probe(
    config: dict[str, object],
    pilot_root: Path,
    state_root: Path,
    environment: dict[str, str] | None = None,
) -> tuple[dict[str, object], list[str]]:
    probe_value = config.get("probe")
    probe = probe_value if isinstance(probe_value, dict) else {}
    command = probe.get("command")
    names = probe.get("workerNames")
    expected_effects = probe.get("expectedEffects")
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(value, str) for value in command)
        or not isinstance(names, list)
        or len(names) != 2
        or not all(isinstance(value, str) for value in names)
        or not isinstance(expected_effects, list)
        or len(expected_effects) != 2
        or not all(isinstance(value, str) for value in expected_effects)
    ):
        return {"started": False}, ["probe.configuration-invalid"]

    run_id = f"managed-gate-{uuid.uuid4()}"
    build, build_failures = _prepare_probe(command, pilot_root)
    if build_failures:
        return {"started": False, "build": build}, build_failures
    run_root = state_root / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    ledger = run_root / "effect-ledger.jsonl"
    ledger.touch()
    first_stdout = run_root / "worker-1.stdout.log"
    first_stderr = run_root / "worker-1.stderr.log"
    second_stdout = run_root / "worker-2.stdout.log"
    second_stderr = run_root / "worker-2.stderr.log"
    failures: list[str] = []
    env = os.environ.copy()
    for name in list(env):
        if (name.startswith("AZURE_") and name != "AZURE_CONFIG_DIR") or name.startswith(
            ("MSI_", "IDENTITY_", "IMDS_")
        ):
            env.pop(name)
    if environment:
        env.update(environment)

    first: subprocess.Popen[bytes] | None = None
    second: subprocess.Popen[bytes] | None = None
    entered = False
    try:
        with first_stdout.open("wb") as stdout, first_stderr.open("wb") as stderr:
            first = subprocess.Popen(
                _worker_command(command, names[0], run_id, ledger, True),
                cwd=pilot_root,
                env=env,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            entered = _wait_for_event(
                ledger,
                lambda event: event.get("type") == "activity-enter"
                and event.get("activity") == expected_effects[1]
                and event.get("worker") == names[0],
                first,
                int(probe.get("entryTimeoutSeconds", 30)),
            )
            if not entered:
                failures.append("probe.worker-one-incomplete-activity-not-observed")
            _stop_process_group(first)
        if entered and first.returncode == 0:
            failures.append("probe.worker-one-not-terminated")

        if entered:
            with second_stdout.open("wb") as stdout, second_stderr.open("wb") as stderr:
                second = subprocess.Popen(
                    _worker_command(command, names[1], run_id, ledger, False),
                    cwd=pilot_root,
                    env=env,
                    stdout=stdout,
                    stderr=stderr,
                    start_new_session=True,
                )
                try:
                    second.wait(timeout=int(probe.get("completionTimeoutSeconds", 120)))
                except subprocess.TimeoutExpired:
                    _stop_process_group(second)
                    failures.append("probe.worker-two-completion-timeout")
    finally:
        for process in (first, second):
            if process is not None and process.poll() is None:
                _stop_process_group(process)

    events = _events(ledger)
    starts = [event for event in events if event.get("type") == "worker-start"]
    worker_pids = {
        str(event.get("worker")): event.get("pid")
        for event in starts
        if isinstance(event.get("worker"), str)
    }
    if set(worker_pids) != set(names) or len(set(worker_pids.values())) != 2:
        failures.append("probe.two-distinct-workers-not-proved")
    run_ids = {event.get("runId") for event in events}
    if run_ids != {run_id}:
        failures.append("probe.run-identity-mismatch")
    run_start_count = sum(event.get("type") == "run-start" for event in events)
    if run_start_count != 1:
        failures.append("probe.run-start-count-not-one")
    effects: dict[str, int] = {}
    activity_workers: dict[str, list[str]] = {}
    for event in events:
        if event.get("type") == "effect" and isinstance(event.get("effect"), str):
            effect = str(event["effect"])
            effects[effect] = effects.get(effect, 0) + 1
        if (
            event.get("type") == "activity-enter"
            and isinstance(event.get("activity"), str)
            and isinstance(event.get("worker"), str)
        ):
            activity_workers.setdefault(str(event["activity"]), []).append(
                str(event["worker"])
            )
    expected_counts = {str(effect): 1 for effect in expected_effects}
    if effects != expected_counts:
        failures.append("probe.effects-not-exactly-once")
    if any(event.get("type") == "duplicate-effect-suppressed" for event in events):
        failures.append("probe.duplicate-effect-attempted")
    if activity_workers.get(str(expected_effects[0])) != [names[0]]:
        failures.append("probe.completed-activity-reexecuted")
    if activity_workers.get(str(expected_effects[1])) != names:
        failures.append("probe.incomplete-activity-not-resumed")
    completions = [event for event in events if event.get("type") == "run-complete"]
    if len(completions) != 1 or completions[0].get("worker") != names[1]:
        failures.append("probe.worker-two-completion-not-proved")
    if second is None or second.returncode != 0:
        failures.append("probe.worker-two-nonzero-exit")

    result: dict[str, object] = {
        "started": True,
        "build": build,
        "runId": run_id,
        "runStartCount": run_start_count,
        "workerPids": worker_pids,
        "workerOneExitCode": first.returncode if first else None,
        "workerTwoExitCode": second.returncode if second else None,
        "activityWorkers": activity_workers,
        "effects": effects,
        "ledger": events,
        "stateDirectory": str(run_root),
        "logs": {
            "workerOneStdout": str(first_stdout),
            "workerOneStderr": str(first_stderr),
            "workerTwoStdout": str(second_stdout),
            "workerTwoStderr": str(second_stderr),
        },
    }
    return result, list(dict.fromkeys(failures))
