"""OS-controlled two-worker replacement probe and ledger verification."""

from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from pathlib import Path


def _events(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    events: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def _worker_command(
    command: list[str],
    name: str,
    phase: str,
    port: int,
    orchestration_id: str,
    ledger: Path,
) -> list[str]:
    return command + [
        "--gate-worker-name",
        name,
        "--gate-phase",
        phase,
        "--gate-port",
        str(port),
        "--gate-orchestration-id",
        orchestration_id,
        "--gate-ledger",
        str(ledger),
    ]


def run_probe(
    manifest: dict[str, object], gate_root: Path
) -> tuple[dict[str, object], list[str]]:
    probe = manifest.get("probe")
    probe = probe if isinstance(probe, dict) else {}
    command = probe.get("command")
    names = probe.get("workerProcessNames")
    state_paths = probe.get("statePaths")
    expected_effects = probe.get("expectedEffects")
    ports = probe.get("ports")
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(value, str) for value in command)
    ):
        return {"started": False}, ["probe.command-invalid"]
    if (
        not isinstance(names, list)
        or len(names) != 2
        or not all(isinstance(value, str) for value in names)
    ):
        return {"started": False}, ["probe.worker-names-invalid"]
    if (
        not isinstance(state_paths, list)
        or not state_paths
        or not isinstance(state_paths[0], str)
    ):
        return {"started": False}, ["probe.state-path-invalid"]
    if (
        not isinstance(expected_effects, list)
        or not expected_effects
        or not all(isinstance(value, str) for value in expected_effects)
    ):
        return {"started": False}, ["probe.expected-effects-invalid"]
    if (
        not isinstance(ports, list)
        or len(ports) < 2
        or not all(isinstance(value, int) for value in ports[:2])
    ):
        return {"started": False}, ["probe.ports-invalid"]
    state_root = Path(state_paths[0])
    state_root = gate_root / state_root if not state_root.is_absolute() else state_root
    orchestration_id = f"gate-{uuid.uuid4()}"
    run_root = state_root / orchestration_id
    run_root.mkdir(parents=True, exist_ok=False)
    ledger = run_root / "effect-ledger.jsonl"
    failures: list[str] = []
    environment = os.environ.copy()
    try:
        first = subprocess.Popen(
            _worker_command(
                command,
                names[0],
                "before-termination",
                ports[0],
                orchestration_id,
                ledger,
            ),
            cwd=gate_root,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        return {
            "started": True,
            "orchestrationId": orchestration_id,
            "errorType": type(exc).__name__,
        }, ["probe.worker-one-execution-failed"]
    deadline = time.monotonic() + 10
    checkpoint_seen = False
    while time.monotonic() < deadline:
        checkpoint_seen = any(
            event.get("type") == "checkpoint"
            and event.get("checkpoint") == "before-worker-termination"
            and event.get("pid") == first.pid
            for event in _events(ledger)
        )
        if checkpoint_seen or first.poll() is not None:
            break
        time.sleep(0.05)
    if not checkpoint_seen:
        failures.append("probe.worker-one-checkpoint-missing")
    if first.poll() is None:
        first.terminate()
    try:
        first.wait(timeout=5)
    except subprocess.TimeoutExpired:
        first.kill()
        first.wait(timeout=5)
        failures.append("probe.worker-one-termination-timeout")
    if checkpoint_seen and first.returncode == 0:
        failures.append("probe.worker-one-not-terminated")
    second_exit: int | None = None
    second_pid: int | None = None
    if checkpoint_seen:
        try:
            second = subprocess.Popen(
                _worker_command(
                    command,
                    names[1],
                    "after-termination",
                    ports[1],
                    orchestration_id,
                    ledger,
                ),
                cwd=gate_root,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            second_pid = second.pid
            second.communicate(timeout=30)
            second_exit = second.returncode
        except (OSError, subprocess.TimeoutExpired):
            if "second" in locals() and second.poll() is None:
                second.kill()
                second.wait(timeout=5)
            failures.append("probe.worker-two-execution-failed")
    events = _events(ledger)
    starts = [event for event in events if event.get("type") == "worker-start"]
    observed_workers = {event.get("worker"): event.get("pid") for event in starts}
    if (
        len(starts) != 2
        or set(observed_workers) != set(names)
        or len(set(observed_workers.values())) != 2
    ):
        failures.append("probe.two-distinct-workers-not-proved")
    if observed_workers.get(names[0]) != first.pid:
        failures.append("probe.worker-one-pid-mismatch")
    observed_second_pid = observed_workers.get(names[1])
    if (
        not isinstance(observed_second_pid, int)
        or observed_second_pid != second_pid
        or observed_second_pid == first.pid
    ):
        failures.append("probe.worker-two-pid-mismatch")
    observed_ports = {event.get("worker"): event.get("port") for event in starts}
    if observed_ports != {names[0]: ports[0], names[1]: ports[1]}:
        failures.append("probe.worker-port-mismatch")
    ids = {event.get("orchestrationId") for event in events}
    if ids != {orchestration_id}:
        failures.append("probe.orchestration-identity-mismatch")
    checkpoints = [
        event.get("checkpoint") for event in events if event.get("type") == "checkpoint"
    ]
    if "continued-after-worker-termination" not in checkpoints:
        failures.append("probe.worker-two-continuation-missing")
    continuation = [
        event
        for event in events
        if event.get("type") == "checkpoint"
        and event.get("checkpoint") == "continued-after-worker-termination"
    ]
    if len(continuation) != 1 or continuation[0].get("pid") != observed_second_pid:
        failures.append("probe.worker-two-continuation-pid-mismatch")
    effects: dict[str, int] = {}
    for event in events:
        if event.get("type") == "effect" and isinstance(event.get("effect"), str):
            effect = event["effect"]
            effects[effect] = effects.get(effect, 0) + 1
    if effects != {name: 1 for name in expected_effects}:
        failures.append("probe.effects-not-exactly-once")
    effect_events = {
        event.get("effect"): event.get("pid")
        for event in events
        if event.get("type") == "effect"
    }
    if effect_events.get(expected_effects[0]) != first.pid:
        failures.append("probe.worker-one-effect-pid-mismatch")
    if (
        len(expected_effects) > 1
        and effect_events.get(expected_effects[1]) != observed_second_pid
    ):
        failures.append("probe.worker-two-effect-pid-mismatch")
    if not any(
        event.get("type") == "complete" and event.get("pid") == observed_second_pid
        for event in events
    ):
        failures.append("probe.completion-not-proved")
    if checkpoint_seen and second_exit != 0:
        failures.append("probe.worker-two-nonzero-exit")
    result: dict[str, object] = {
        "started": True,
        "orchestrationId": orchestration_id,
        "workers": names,
        "workerPids": observed_workers,
        "workerOneExitCode": first.returncode,
        "workerTwoExitCode": second_exit,
        "checkpoints": checkpoints,
        "effects": effects,
        "ledger": events,
    }
    return result, failures
