"""Finite custody of a helper-owned command and registered detached provider groups."""
import json
import os
from pathlib import Path
import signal
import select
import sys
import subprocess
import time


def snapshot(file):
    try:
        return json.loads(Path(file).read_text())
    except (OSError, ValueError):
        return {}


def persist(file, value):
    file = Path(file)
    temporary = file.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(file)


def signal_group(pgid, started, sig, retry=True):
    # macOS can return EPERM for an already dead group containing only zombies.
    # Inspect identity and live membership together; never signal reused leaders.
    rows = subprocess.run(['/bin/ps', '-axo', 'pid=,pgid=,stat=,lstart='],
                          capture_output=True, text=True, timeout=0.5, check=True).stdout.splitlines()
    members = [row.split(None, 3) for row in rows if len(row.split(None, 3)) == 4]
    leader = next((row for row in members if int(row[0]) == pgid), None)
    if leader and leader[3].strip() != started:
        return
    if not any(int(row[1]) == pgid and not row[2].startswith('Z') for row in members):
        return
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        pass
    except PermissionError:
        if not retry:
            raise
        signal_group(pgid, started, sig, False)


def block_custody(registry, unresolved):
    value = {'reason': 'Process identity or termination could not be verified',
             'registry': str(registry), 'unresolved': unresolved}
    persist(str(registry) + '.unresolved', value)
    lock_file = os.environ.get('WIKI_MAINTENANCE_LOCK_FILE')
    if lock_file:
        persist(lock_file + '.blocked.json', value)


def execute(command, out, err, deadline, grace, progress, registry, env):
    owner_file = str(registry) + '.owner'
    custody_output = os.dup(sys.stdout.fileno())
    try:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--guard', str(registry), owner_file, *command],
                             cwd='/', stdin=subprocess.PIPE, stdout=out, stderr=err,
                             start_new_session=True, env=env, pass_fds=(custody_output, int(env["WIKI_MAINTENANCE_LOCK_FD"])))
    finally:
        os.close(custody_output)
    def identity(pid):
        return subprocess.run(["/bin/ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True, timeout=0.5).stdout.strip()

    groups = {}
    stopped = None
    forced = False

    def refresh():
        try:
            for line in Path(registry).read_text().splitlines():
                item = json.loads(line)
                pid = item["pid"]
                if item.get("released"):
                    groups.pop(pid, None)
                elif isinstance(pid, int) and pid > 1 and item.get("started"):
                    groups[pid] = item["started"]
        except (OSError, ValueError):
            pass

    def send(sig):
        refresh()
        unresolved = []
        for pgid, started in groups.items():
            try:
                signal_group(pgid, started, sig)
            except (OSError, subprocess.SubprocessError):
                unresolved.append({'pid': pgid, 'started': started})
        if unresolved:
            block_custody(registry, unresolved)
            if env.get('WIKI_MAINTENANCE_LOCK_FILE'):
                persist(env['WIKI_MAINTENANCE_LOCK_FILE'] + '.blocked.json', {'registry': str(registry), 'unresolved': unresolved})
            raise RuntimeError('Process custody unresolved; inspect ' + str(registry) + '.unresolved')

    try:
        groups[child.pid] = identity(child.pid)
        while child.poll() is None:
            refresh()
            state = snapshot(progress)
            reason = state.get('stopReason')
            if stopped is None and (time.monotonic() >= deadline or reason):
                stopped = (reason or 'budget-exhausted', time.monotonic())
                send(signal.SIGTERM)
            if stopped and time.monotonic() >= stopped[1] + grace:
                forced = True
                send(signal.SIGKILL)
                break
            time.sleep(0.025)
        code = child.wait(timeout=1)
        reason = snapshot(progress).get('stopReason')
        if stopped is None and reason:
            stopped = (reason, time.monotonic())
    finally:
        # The just-spawned command is owned even if the initial identity probe failed.
        if child.poll() is None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait(timeout=1)
        # Also reclaim registered detached groups when their owner exits early.
        send(signal.SIGKILL)
    child.stdin.close()
    return code, stopped[0] if stopped else None, forced, snapshot(owner_file).get('pid')


def guard(registry, owner_file, command):
    """Own the command even if the outer helper is killed without signal handling."""
    signal.signal(signal.SIGTERM, lambda *_: None)
    child = subprocess.Popen(command, stdin=subprocess.DEVNULL)
    try:
        persist(owner_file, {'pid': child.pid})
        while child.poll() is None:
            if select.select([sys.stdin], [], [], 0.025)[0] and not os.read(0, 1):
                break  # Parent died/closed its custody pipe.
        else:
            return child.returncode
    finally:
        if child.poll() is None:
            # Detached provider groups are registered by the compiler before work.
            registrations = {}
            try:
                for line in Path(registry).read_text().splitlines():
                    item = json.loads(line)
                    if item.get('released'):
                        registrations.pop(item['pid'], None)
                    else:
                        registrations[item['pid']] = item['started']
            except (OSError, ValueError, KeyError):
                pass
            unresolved = []
            for pid, started in registrations.items():
                try:
                    signal_group(pid, started, signal.SIGKILL)
                except (OSError, subprocess.SubprocessError):
                    unresolved.append({"pid": pid, "started": started})
            if unresolved:
                block_custody(registry, unresolved)
            os.killpg(os.getpgrp(), signal.SIGKILL)


if __name__ == '__main__' and sys.argv[1] == '--guard':
    raise SystemExit(guard(sys.argv[2], sys.argv[3], sys.argv[4:]))
