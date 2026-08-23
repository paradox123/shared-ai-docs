from __future__ import annotations

import hashlib
import hmac
import json
import os
import plistlib
import stat
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import pytest

PILOTCTL = Path(__file__).parents[1] / "ops" / "macos" / "pilotctl"
SUPERVISOR = Path(__file__).parents[1] / "ops" / "macos" / "pilot-supervisor"
SECRET = "never-print-this-pilot-secret"


def write_executable(path: Path, body: str = "#!/bin/sh\nexit 0\n") -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def valid_environment(tmp_path: Path, **overrides: str | None) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    pilot = write_executable(tmp_path / "github-issue-pilot")
    cloudflared = write_executable(tmp_path / "cloudflared")
    tunnel_config = tmp_path / "tunnel.yml"
    tunnel_config.write_text("ingress: []\n", encoding="utf-8")
    repository = tmp_path / "repository"
    worktrees = tmp_path / "worktrees"
    skill_root = tmp_path / "skills"
    repository.mkdir()
    worktrees.mkdir()
    skill_root.mkdir()
    context = tmp_path / "CONTEXT.md"
    context.write_text("Controlled repository context\n", encoding="utf-8")

    values: dict[str, str | None] = {
        "PILOT_EXECUTABLE": str(pilot),
        "CLOUDFLARED_EXECUTABLE": str(cloudflared),
        "CLOUDFLARED_CONFIG": str(tunnel_config),
        "CLOUDFLARED_TUNNEL_NAME": "danielsvault-github-pilot",
        "PILOT_PUBLIC_RECEIVER_URL": "https://pilot.example.test/webhooks/github",
        "PILOT_HOST": "127.0.0.1",
        "PILOT_PORT": "18788",
        "PILOT_ALLOWED_REPOSITORIES": "daniel/probare-crm",
        "GITHUB_TOKEN": SECRET,
        "DANIEL_GITHUB_LOGIN": "daniel",
        "PILOT_REPOSITORY_ROOT": str(repository),
        "PILOT_WORKTREE_ROOT": str(worktrees),
        "PILOT_REPOSITORY_CONTEXT_PATH": str(context),
        "PILOT_PUBLIC_OBSERVATION_SURFACE": "http://127.0.0.1:18788",
        "PILOT_VERIFICATION_COMMAND": "pytest -q",
        "PILOT_SKILL_ROOT": str(skill_root),
        "PILOT_DATABASE_PATH": str(tmp_path / "pilot.db"),
        "PILOT_INTERNAL_WEBHOOK_SECRET": SECRET,
        "GITHUB_WEBHOOK_SECRET": "",
    }
    values.update(overrides)
    environment = tmp_path / "pilot.env"
    environment.write_text(
        "".join(
            f"{name}={value!r}\n"
            for name, value in values.items()
            if value is not None
        ),
        encoding="utf-8",
    )
    environment.chmod(0o600)
    return environment


def verify(environment: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PILOTCTL), "verify-config", str(environment)],
        check=False,
        capture_output=True,
        text=True,
    )


def run_pilotctl(
    arguments: list[str],
    *,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    process_environment = os.environ.copy()
    if environment:
        process_environment.update(environment)
    return subprocess.run(
        [str(PILOTCTL), *arguments],
        check=False,
        capture_output=True,
        text=True,
        env=process_environment,
    )


def read_state(path: Path) -> dict[str, str]:
    return dict(
        line.split("=", maxsplit=1)
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def wait_until(predicate, *, timeout: float = 8.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise AssertionError("condition did not become true before timeout")


def test_private_loopback_named_tunnel_configuration_is_accepted(tmp_path: Path) -> None:
    environment = valid_environment(tmp_path)

    result = verify(environment)

    assert result.returncode == 0
    assert result.stdout == "configuration_status=valid\n"
    assert result.stderr == ""
    assert SECRET not in result.stdout + result.stderr


@pytest.mark.parametrize(
    ("overrides", "expected_category"),
    [
        ({"PILOT_INTERNAL_WEBHOOK_SECRET": None}, "missing_variable"),
        ({"PILOT_HOST": "0.0.0.0"}, "unsafe_receiver_host"),
        (
            {"PILOT_PUBLIC_RECEIVER_URL": "http://pilot.example.test/webhooks/github"},
            "unsafe_receiver_url",
        ),
        (
            {"PILOT_PUBLIC_RECEIVER_URL": "https://pilot.example.test/other"},
            "unsafe_receiver_url",
        ),
        ({"PILOT_PORT": "65536"}, "invalid_receiver_port"),
        ({"PILOT_EXECUTABLE": "github-issue-pilot"}, "invalid_absolute_path"),
    ],
)
def test_configuration_errors_are_bounded_and_never_echo_values(
    tmp_path: Path,
    overrides: dict[str, str | None],
    expected_category: str,
) -> None:
    environment = valid_environment(tmp_path, **overrides)

    result = verify(environment)

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == f"configuration_status=invalid category={expected_category}\n"
    assert SECRET not in result.stdout + result.stderr


def test_group_or_other_access_to_environment_is_rejected(tmp_path: Path) -> None:
    environment = valid_environment(tmp_path)
    environment.chmod(0o640)

    result = verify(environment)

    assert result.returncode != 0
    assert result.stderr == "configuration_status=invalid category=unsafe_permissions\n"
    assert SECRET not in result.stdout + result.stderr


def test_failed_tunnel_validation_is_reported_without_child_output(tmp_path: Path) -> None:
    environment = valid_environment(tmp_path)
    write_executable(
        tmp_path / "cloudflared",
        f"#!/bin/sh\necho {SECRET!r} >&2\nexit 19\n",
    )

    result = verify(environment)

    assert result.returncode != 0
    assert result.stderr == "configuration_status=invalid category=tunnel_validation_failed\n"
    assert SECRET not in result.stdout + result.stderr


def test_environment_must_be_a_user_owned_regular_file(tmp_path: Path) -> None:
    environment = tmp_path / "pilot.env"
    environment.mkdir()

    result = verify(environment)

    assert result.returncode != 0
    assert result.stderr == "configuration_status=invalid category=unsafe_environment_file\n"
    assert SECRET not in result.stdout + result.stderr


def test_environment_is_parsed_as_data_and_never_executed(tmp_path: Path) -> None:
    environment = valid_environment(tmp_path)
    with environment.open("a", encoding="utf-8") as stream:
        stream.write(f"printf '%s\\n' {SECRET!r} >&2\n")

    result = verify(environment)

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == "configuration_status=invalid category=invalid_syntax\n"
    assert SECRET not in result.stdout + result.stderr


def test_supervisor_static_configuration_failure_exits_cleanly_for_launchd(
    tmp_path: Path,
) -> None:
    environment = valid_environment(tmp_path)
    environment.chmod(0o640)
    state_path = tmp_path / "runtime" / "stack.state"

    result = subprocess.run(
        [str(SUPERVISOR), "run", str(environment), str(state_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == "configuration_status=invalid category=unsafe_permissions\n"
    assert not state_path.exists()


@pytest.mark.skipif(os.uname().sysname != "Darwin", reason="macOS operations contract")
def test_configuration_contract_runs_on_macos(tmp_path: Path) -> None:
    assert verify(valid_environment(tmp_path)).returncode == 0


def test_rendered_launch_agent_is_login_scoped_restartable_and_secret_free(
    tmp_path: Path,
) -> None:
    environment = valid_environment(tmp_path)
    output = tmp_path / "com.danielsvault.github-issue-pilot.plist"

    result = subprocess.run(
        [str(PILOTCTL), "render-plist", str(environment), str(output)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout == f"plist_status=valid output={output}\n"
    assert result.stderr == ""
    configuration = plistlib.loads(output.read_bytes())
    support = (
        Path.home()
        / "Library"
        / "Application Support"
        / "DanielsVault GitHub Issue Pilot"
    )
    lifecycle_log = (
        Path.home()
        / "Library"
        / "Logs"
        / "DanielsVault GitHub Issue Pilot"
        / "lifecycle.log"
    )
    assert configuration == {
        "KeepAlive": {"SuccessfulExit": False},
        "Label": "com.danielsvault.github-issue-pilot",
        "LimitLoadToSessionType": "Aqua",
        "ProcessType": "Background",
        "ProgramArguments": [
            str(support / "bin" / "pilot-supervisor"),
            "run",
            str(environment),
            str(support / "run" / "stack.state"),
        ],
        "RunAtLoad": True,
        "StandardErrorPath": str(lifecycle_log),
        "StandardOutPath": str(lifecycle_log),
        "ThrottleInterval": 10,
    }
    serialized = output.read_text(encoding="utf-8")
    assert SECRET not in serialized
    assert "EnvironmentVariables" not in serialized
    assert subprocess.run(
        ["/usr/bin/plutil", "-lint", str(output)],
        check=False,
        capture_output=True,
        text=True,
    ).returncode == 0


def test_lifecycle_commands_converge_on_one_gui_user_job(tmp_path: Path) -> None:
    label = "com.danielsvault.github-issue-pilot.test"
    environment_file = valid_environment(
        tmp_path / "configuration",
        PILOT_LAUNCH_AGENT_LABEL=label,
    )
    user_root = tmp_path / "user"
    launchctl_state = tmp_path / "launchctl.state"
    launchctl_calls = tmp_path / "launchctl.calls"
    launchctl = write_executable(
        tmp_path / "launchctl",
        """#!/bin/bash
set -u
printf '%s\\n' "$*" >> "$FAKE_LAUNCHCTL_CALLS"
case "$1" in
    bootstrap)
        [[ ! -e "$FAKE_LAUNCHCTL_STATE" ]] || exit 37
        printf '%s\\n' "$3" > "$FAKE_LAUNCHCTL_STATE"
        ;;
    bootout)
        [[ -e "$FAKE_LAUNCHCTL_STATE" ]] || exit 3
        rm "$FAKE_LAUNCHCTL_STATE"
        ;;
    print)
        [[ -e "$FAKE_LAUNCHCTL_STATE" ]] || exit 3
        printf 'state = running\\n'
        ;;
    kickstart)
        [[ -e "$FAKE_LAUNCHCTL_STATE" ]] || exit 3
        ;;
    *) exit 64 ;;
esac
""",
    )
    command_environment = {
        "PILOTCTL_LAUNCHCTL": str(launchctl),
        "PILOTCTL_USER_ROOT": str(user_root),
        "FAKE_LAUNCHCTL_STATE": str(launchctl_state),
        "FAKE_LAUNCHCTL_CALLS": str(launchctl_calls),
    }

    first = run_pilotctl(
        ["install", str(environment_file)], environment=command_environment
    )
    second = run_pilotctl(
        ["install", str(environment_file)], environment=command_environment
    )
    loaded = run_pilotctl(
        ["status", str(environment_file)], environment=command_environment
    )
    restarted = run_pilotctl(
        ["restart", str(environment_file)], environment=command_environment
    )
    stopped = run_pilotctl(
        ["stop", str(environment_file)], environment=command_environment
    )
    not_loaded = run_pilotctl(
        ["status", str(environment_file)], environment=command_environment
    )
    started = run_pilotctl(
        ["start", str(environment_file)], environment=command_environment
    )
    uninstalled = run_pilotctl(
        ["uninstall", str(environment_file)], environment=command_environment
    )

    assert first.stdout == f"launch_agent_status=installed label={label}\n"
    assert second.stdout == f"launch_agent_status=installed label={label}\n"
    assert loaded.stdout == (
        f"launch_agent_status=loaded label={label} state=stale "
        "generation=unavailable supervisor_pid=unavailable pilot_pid=unavailable "
        "tunnel_pid=unavailable receiver=unready\n"
    )
    assert restarted.stdout == f"launch_agent_status=restarted label={label}\n"
    assert stopped.stdout == f"launch_agent_status=stopped label={label}\n"
    assert not_loaded.stdout == f"launch_agent_status=not_loaded label={label}\n"
    assert started.stdout == f"launch_agent_status=started label={label}\n"
    assert uninstalled.stdout == f"launch_agent_status=uninstalled label={label}\n"
    assert all(
        result.returncode == 0
        for result in (
            first,
            second,
            loaded,
            restarted,
            stopped,
            not_loaded,
            started,
            uninstalled,
        )
    )
    assert not launchctl_state.exists()
    launch_agents = user_root / "Library" / "LaunchAgents"
    assert not (launch_agents / f"{label}.plist").exists()
    installed_supervisor = (
        user_root
        / "Library"
        / "Application Support"
        / "DanielsVault GitHub Issue Pilot"
        / "bin"
        / "pilot-supervisor"
    )
    lifecycle_log = (
        user_root
        / "Library"
        / "Logs"
        / "DanielsVault GitHub Issue Pilot"
        / "lifecycle.log"
    )
    assert stat.S_IMODE(lifecycle_log.stat().st_mode) == 0o600
    assert not installed_supervisor.exists()
    calls = launchctl_calls.read_text(encoding="utf-8")
    assert calls.count("bootstrap gui/") == 3
    assert SECRET not in calls + first.stdout + first.stderr + second.stdout + second.stderr


def test_supervisor_starts_one_pair_and_converts_child_crash_to_bounded_failure(
    tmp_path: Path,
) -> None:
    events = tmp_path / "child-events"
    pilot = write_executable(
        tmp_path / "github-issue-pilot",
        f"""#!/bin/bash
printf 'pilot_started=%s\\n' "$$" >> {str(events)!r}
printf '%s\\n' {SECRET!r}
printf '%s\\n' {SECRET!r} >&2
trap 'printf "pilot_stopped=%s\\n" "$$" >> {str(events)!r}; exit 0' TERM INT
while true; do sleep 0.1; done
""",
    )
    cloudflared = write_executable(
        tmp_path / "cloudflared",
        f"""#!/bin/bash
if [[ "$*" == *" ingress "* ]]; then exit 0; fi
printf 'tunnel_started=%s\\n' "$$" >> {str(events)!r}
printf '%s\\n' {SECRET!r}
printf '%s\\n' {SECRET!r} >&2
trap 'printf "tunnel_stopped=%s\\n" "$$" >> {str(events)!r}; exit 0' TERM INT
while true; do sleep 0.1; done
""",
    )
    environment_file = valid_environment(
        tmp_path / "configuration",
        PILOT_EXECUTABLE=str(pilot),
        CLOUDFLARED_EXECUTABLE=str(cloudflared),
    )
    state_path = tmp_path / "runtime" / "stack.state"

    process = subprocess.Popen(
        [str(SUPERVISOR), "run", str(environment_file), str(state_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_until(lambda: state_path.exists())
        running = read_state(state_path)
        wait_until(
            lambda: events.exists()
            and "pilot_started=" in events.read_text()
            and "tunnel_started=" in events.read_text()
        )
        assert running["status"] == "running"
        assert int(running["supervisor_pid"]) == process.pid
        assert os.kill(int(running["pilot_pid"]), 0) is None
        assert os.kill(int(running["tunnel_pid"]), 0) is None

        os.kill(int(running["pilot_pid"]), 9)
        stdout, stderr = process.communicate(timeout=8)
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

    assert process.returncode == 70
    stopped = read_state(state_path)
    assert stopped["status"] == "restart_required"
    assert stopped["generation"] == running["generation"]
    assert stopped["failed_service"] == "pilot"
    assert stopped["exit_code"] == "137"
    assert stat.S_IMODE(state_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(state_path.parent.stat().st_mode) == 0o700
    child_events = events.read_text(encoding="utf-8")
    assert child_events.count("pilot_started=") == 1
    assert child_events.count("tunnel_started=") == 1
    assert child_events.count("tunnel_stopped=") == 1
    assert SECRET not in stdout + stderr + state_path.read_text() + child_events
    assert "event=stack_start" in stdout
    assert "event=child_exit" in stdout
    assert "service=pilot" in stdout
    assert stderr == ""


def test_supervisor_signal_stops_both_children_without_requesting_restart(
    tmp_path: Path,
) -> None:
    events = tmp_path / "child-events"
    child_body = f"""#!/bin/bash
if [[ "$*" == *" ingress "* ]]; then exit 0; fi
printf 'started=%s\\n' "$$" >> {str(events)!r}
trap 'printf "stopped=%s\\n" "$$" >> {str(events)!r}; exit 0' TERM INT
while true; do sleep 0.1; done
"""
    pilot = write_executable(tmp_path / "github-issue-pilot", child_body)
    cloudflared = write_executable(tmp_path / "cloudflared", child_body)
    environment_file = valid_environment(
        tmp_path / "configuration",
        PILOT_EXECUTABLE=str(pilot),
        CLOUDFLARED_EXECUTABLE=str(cloudflared),
    )
    state_path = tmp_path / "runtime" / "stack.state"

    process = subprocess.Popen(
        [str(SUPERVISOR), "run", str(environment_file), str(state_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_until(lambda: state_path.exists())
        wait_until(
            lambda: events.exists()
            and events.read_text(encoding="utf-8").count("started=") == 2
        )
        process.terminate()
        stdout, stderr = process.communicate(timeout=8)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)

    assert process.returncode == 0
    stopped = read_state(state_path)
    assert stopped["status"] == "stopped"
    assert events.read_text(encoding="utf-8").count("stopped=") == 2
    assert "event=stack_stop outcome=operator_signal" in stdout
    assert stderr == ""


class ReadyHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(204)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def test_status_and_logs_report_only_live_bounded_supervisor_observations(
    tmp_path: Path,
) -> None:
    label = "com.danielsvault.github-issue-pilot.status-test"
    user_root = tmp_path / "user"
    launchctl = write_executable(tmp_path / "launchctl", "#!/bin/sh\nexit 0\n")
    server = ThreadingHTTPServer(("127.0.0.1", 0), ReadyHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    port = server.server_address[1]
    environment_file = valid_environment(
        tmp_path / "configuration",
        PILOT_LAUNCH_AGENT_LABEL=label,
        PILOT_PORT=str(port),
    )
    sleepers = [subprocess.Popen(["/bin/sleep", "30"]) for _ in range(3)]
    support = (
        user_root
        / "Library"
        / "Application Support"
        / "DanielsVault GitHub Issue Pilot"
    )
    state_path = support / "run" / "stack.state"
    state_path.parent.mkdir(parents=True)
    state_path.write_text(
        "".join(
            (
                "status=running\n",
                "generation=20260823T120000Z-321\n",
                f"supervisor_pid={sleepers[0].pid}\n",
                f"pilot_pid={sleepers[1].pid}\n",
                f"tunnel_pid={sleepers[2].pid}\n",
                "started_at=2026-08-23T12:00:00Z\n",
                "updated_at=2026-08-23T12:00:01Z\n",
                "failed_service=none\n",
                "exit_code=0\n",
            )
        ),
        encoding="utf-8",
    )
    state_path.chmod(0o600)
    log_path = (
        user_root
        / "Library"
        / "Logs"
        / "DanielsVault GitHub Issue Pilot"
        / "lifecycle.log"
    )
    log_path.parent.mkdir(parents=True)
    valid_log = (
        "timestamp=2026-08-23T12:00:00Z generation=20260823T120000Z-321 "
        f"event=stack_start pilot_pid={sleepers[1].pid} "
        f"tunnel_pid={sleepers[2].pid} outcome=running"
    )
    log_path.write_text(
        f"{valid_log}\n{valid_log} extra={SECRET}\nraw={SECRET}\n",
        encoding="utf-8",
    )
    log_path.chmod(0o600)
    command_environment = {
        "PILOTCTL_LAUNCHCTL": str(launchctl),
        "PILOTCTL_USER_ROOT": str(user_root),
    }

    try:
        current = run_pilotctl(
            ["status", str(environment_file)], environment=command_environment
        )
        logs = run_pilotctl(
            ["logs", str(environment_file)], environment=command_environment
        )
        sleepers[1].terminate()
        sleepers[1].wait(timeout=5)
        stale = run_pilotctl(
            ["status", str(environment_file)], environment=command_environment
        )
    finally:
        for sleeper in sleepers:
            if sleeper.poll() is None:
                sleeper.terminate()
                sleeper.wait(timeout=5)
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)

    assert current.returncode == 0
    assert current.stdout == (
        f"launch_agent_status=loaded label={label} state=current "
        f"generation=20260823T120000Z-321 supervisor_pid={sleepers[0].pid} "
        f"pilot_pid={sleepers[1].pid} tunnel_pid={sleepers[2].pid} receiver=ready\n"
    )
    assert logs.returncode == 0
    assert logs.stdout == f"{valid_log}\n"
    assert SECRET not in logs.stdout + logs.stderr
    assert stale.returncode == 0
    assert stale.stdout == (
        f"launch_agent_status=loaded label={label} state=stale "
        "generation=unavailable supervisor_pid=unavailable pilot_pid=unavailable "
        "tunnel_pid=unavailable receiver=ready\n"
    )


def write_productive_pilot_fixture(path: Path) -> Path:
    path.write_text(
        """from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import uvicorn

from github_issue_pilot.app import create_app
from github_issue_pilot.github import BacklogIssue, IssueState

REPOSITORY = "daniel/probare-crm"


class ControlledGitHub:
    contract_version = "1"
    repository = REPOSITORY
    ready_label = "ready-for-agent"
    running_label = "agent-running"
    allowed_event_actions = frozenset({("issues", "labeled")})

    def __init__(self) -> None:
        self.labels = {"ready-for-agent"}

    def issue_state(self, repository: str, issue_number: int) -> IssueState:
        return IssueState(open=True, labels=frozenset(self.labels))

    def backlog(self, trigger_issue_number: int) -> tuple[BacklogIssue, ...]:
        return (BacklogIssue(trigger_issue_number, self.issue_state(REPOSITORY, trigger_issue_number)),)

    def ensure_label(self, repository: str, issue_number: int, label: str) -> None:
        if label not in self.labels:
            self.labels.add(label)
            with Path(os.environ["PILOT_TEST_EFFECT_LOG"]).open("a", encoding="utf-8") as stream:
                stream.write(f"label={label} issue={issue_number}\\n")


github = ControlledGitHub()
app = create_app(
    database_path=Path(os.environ["PILOT_DATABASE_PATH"]),
    webhook_secret=None,
    internal_webhook_secret=os.environ["PILOT_INTERNAL_WEBHOOK_SECRET"].encode(),
    repository_adapters={REPOSITORY: github},
    clock=lambda: datetime.now(UTC),
    boot_session_id=lambda: "controlled-macos-boot",
    heartbeat_interval_seconds=0.1,
)
uvicorn.run(app, host=os.environ["PILOT_HOST"], port=int(os.environ["PILOT_PORT"]), log_level="critical")
""",
        encoding="utf-8",
    )
    return path


def signed_delivery(port: int) -> tuple[bytes, dict[str, str], str]:
    delivery_id = "launchd-delivery-001"
    event = "issues"
    body = json.dumps(
        {
            "action": "labeled",
            "repository": {"full_name": "daniel/probare-crm"},
            "issue": {"number": 41},
            "label": {"name": "ready-for-agent"},
        },
        separators=(",", ":"),
    ).encode()
    canonical = b"\n".join((delivery_id.encode(), event.encode(), body))
    signature = hmac.new(SECRET.encode(), canonical, hashlib.sha256).hexdigest()
    return body, {
        "content-type": "application/json",
        "x-github-delivery": delivery_id,
        "x-github-event": event,
        "x-pilot-signature-256": f"sha256={signature}",
    }, f"http://127.0.0.1:{port}"


def parsed_status(result: subprocess.CompletedProcess[str]) -> dict[str, str]:
    assert result.returncode == 0, result.stderr
    return dict(field.split("=", maxsplit=1) for field in result.stdout.strip().split())


@dataclass(frozen=True)
class ProductiveLaunchdFixture:
    label: str
    user_root: Path
    effect_log: Path
    environment_file: Path
    command_environment: dict[str, str]
    body: bytes
    headers: dict[str, str]
    base_url: str


def productive_launchd_fixture(
    tmp_path: Path,
    *,
    label_suffix: str,
) -> ProductiveLaunchdFixture:
    label = f"com.danielsvault.github-issue-pilot.{label_suffix}-{os.getpid()}"
    user_root = tmp_path / "user"
    effect_log = tmp_path / "workflow-effects.log"
    fixture_app = write_productive_pilot_fixture(tmp_path / "productive_pilot.py")
    pilot = write_executable(
        tmp_path / "github-issue-pilot",
        f"#!/bin/bash\nexec {sys.executable!r} {str(fixture_app)!r}\n",
    )
    cloudflared = write_executable(
        tmp_path / "cloudflared",
        """#!/bin/bash
if [[ "$*" == *" ingress "* ]]; then exit 0; fi
trap 'exit 0' TERM INT
while true; do sleep 0.1; done
""",
    )
    probe = ThreadingHTTPServer(("127.0.0.1", 0), ReadyHandler)
    port = probe.server_address[1]
    probe.server_close()
    environment_file = valid_environment(
        tmp_path / "configuration",
        PILOT_LAUNCH_AGENT_LABEL=label,
        PILOT_EXECUTABLE=str(pilot),
        CLOUDFLARED_EXECUTABLE=str(cloudflared),
        PILOT_PORT=str(port),
        PILOT_TEST_EFFECT_LOG=str(effect_log),
    )
    body, headers, base_url = signed_delivery(port)
    return ProductiveLaunchdFixture(
        label=label,
        user_root=user_root,
        effect_log=effect_log,
        environment_file=environment_file,
        command_environment={"PILOTCTL_USER_ROOT": str(user_root)},
        body=body,
        headers=headers,
        base_url=base_url,
    )


def wait_for_productive_stack(
    fixture: ProductiveLaunchdFixture,
    *,
    previous_generation: str | None = None,
    timeout: float = 15,
) -> dict[str, str]:
    latest_status: dict[str, str] = {}

    def stack_is_ready() -> bool:
        nonlocal latest_status
        latest_status = parsed_status(
            run_pilotctl(
                ["status", str(fixture.environment_file)],
                environment=fixture.command_environment,
            )
        )
        return (
            latest_status.get("launch_agent_status") == "loaded"
            and latest_status.get("state") == "current"
            and latest_status.get("receiver") == "ready"
            and (
                previous_generation is None
                or latest_status.get("generation") != previous_generation
            )
        )

    try:
        wait_until(stack_is_ready, timeout=timeout)
    except AssertionError as exc:
        bounded_logs = run_pilotctl(
            ["logs", str(fixture.environment_file)],
            environment=fixture.command_environment,
        ).stdout
        raise AssertionError(
            f"launch agent did not become ready: status={latest_status!r} "
            f"bounded_logs={bounded_logs!r}"
        ) from exc
    return latest_status


@pytest.mark.skipif(os.uname().sysname != "Darwin", reason="requires macOS launchd")
def test_real_user_launch_agent_starts_and_processes_one_signed_delivery(
    tmp_path: Path,
) -> None:
    fixture = productive_launchd_fixture(tmp_path, label_suffix="acceptance")

    try:
        installed = run_pilotctl(
            ["install", str(fixture.environment_file)],
            environment=fixture.command_environment,
        )
        assert installed.returncode == 0, installed.stderr
        wait_for_productive_stack(fixture)
        accepted = httpx.post(
            f"{fixture.base_url}/webhooks/github",
            content=fixture.body,
            headers=fixture.headers,
            timeout=5,
        )
        observed = httpx.get(
            f"{fixture.base_url}/workflows/daniel/probare-crm/issues/41",
            timeout=5,
        )
    finally:
        run_pilotctl(
            ["uninstall", str(fixture.environment_file)],
            environment=fixture.command_environment,
        )

    assert accepted.status_code == 202
    assert accepted.json() == {
        "delivery_id": "launchd-delivery-001",
        "status": "accepted",
    }
    assert observed.status_code == 200
    workflow = observed.json()
    assert workflow["delivery"]["id"] == "launchd-delivery-001"
    assert workflow["run"]["issue_number"] == 41
    assert workflow["reconciliation"]["boot_id"] == "controlled-macos-boot"
    assert workflow["reconciliation"]["outcome"] == "first_start"
    assert fixture.effect_log.read_text(encoding="utf-8") == "label=agent-running issue=41\n"
    plist = (
        fixture.user_root / "Library" / "LaunchAgents" / f"{fixture.label}.plist"
    )
    assert not plist.exists()


@pytest.mark.skipif(os.uname().sysname != "Darwin", reason="requires macOS launchd")
def test_real_user_launch_agent_recovers_a_killed_pilot_exactly_once(
    tmp_path: Path,
) -> None:
    fixture = productive_launchd_fixture(tmp_path, label_suffix="recovery")

    try:
        installed = run_pilotctl(
            ["install", str(fixture.environment_file)],
            environment=fixture.command_environment,
        )
        assert installed.returncode == 0, installed.stderr
        initial_status = wait_for_productive_stack(fixture)
        accepted = httpx.post(
            f"{fixture.base_url}/webhooks/github",
            content=fixture.body,
            headers=fixture.headers,
            timeout=5,
        )
        wait_until(
            lambda: fixture.effect_log.exists()
            and fixture.effect_log.read_text(encoding="utf-8")
            == "label=agent-running issue=41\n"
        )
        before = httpx.get(
            f"{fixture.base_url}/workflows/daniel/probare-crm/issues/41",
            timeout=5,
        ).json()

        os.kill(int(initial_status["pilot_pid"]), 9)
        recovered_status = wait_for_productive_stack(
            fixture,
            previous_generation=initial_status["generation"],
            timeout=25,
        )
        duplicate = httpx.post(
            f"{fixture.base_url}/webhooks/github",
            content=fixture.body,
            headers=fixture.headers,
            timeout=5,
        )
        after = httpx.get(
            f"{fixture.base_url}/workflows/daniel/probare-crm/issues/41",
            timeout=5,
        ).json()
        lifecycle = run_pilotctl(
            ["logs", str(fixture.environment_file)],
            environment=fixture.command_environment,
        ).stdout
    finally:
        run_pilotctl(
            ["uninstall", str(fixture.environment_file)],
            environment=fixture.command_environment,
        )

    assert accepted.status_code == 202
    assert duplicate.status_code == 200
    assert duplicate.json() == {
        "delivery_id": "launchd-delivery-001",
        "status": "already_accepted",
    }
    assert recovered_status["pilot_pid"] != initial_status["pilot_pid"]
    assert recovered_status["tunnel_pid"] != initial_status["tunnel_pid"]
    assert after["delivery"] == before["delivery"]
    assert after["run"]["id"] == before["run"]["id"]
    assert after["claim"] == before["claim"]
    assert after["checkpoint"]["thread_id"] == after["run"]["id"]
    assert after["reconciliation"]["boot_id"] == before["reconciliation"]["boot_id"]
    assert after["reconciliation"]["started_at"] == before["reconciliation"]["started_at"]
    assert after["reconciliation"]["outcome"] == "first_start"
    assert fixture.effect_log.read_text(encoding="utf-8") == "label=agent-running issue=41\n"
    assert lifecycle.count("event=stack_start") == 2
    assert "event=child_exit service=pilot exit_code=137 outcome=restart_required" in lifecycle
    assert SECRET not in lifecycle
