#!/usr/bin/env python3
"""Stable public wiki entry point and local release activation."""
import argparse
import fcntl
import signal
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from release_integrity import qualified_report, runtime_digest

BASE = Path(__file__).resolve().parents[1]
SELECTION = BASE / '.runtime/selection.json'
LOCK_FD = None


def execute(command, *, capture_output=False, text=True, timeout=None, env=None):
    # Children retain the lock if their supervisor dies. Bound probes kill the
    # whole process group on timeout, including model and retrieval children.
    with subprocess.Popen(command, env=env, text=text, start_new_session=True,
                          pass_fds=(() if LOCK_FD is None else (LOCK_FD,)),
                          stdout=subprocess.PIPE if capture_output else None,
                          stderr=subprocess.PIPE if capture_output else None) as child:
        try:
            out, err = child.communicate(timeout=timeout)
        except BaseException:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            raise
        return subprocess.CompletedProcess(command, child.returncode, out, err)


def run_runtime(wrapper, args, **kwargs):
    return execute([str(wrapper / 'wiki-node'), str(wrapper / 'src/cli.ts'), *args], **kwargs)


def identity(wrapper):
    result = run_runtime(wrapper, ['release-status'], capture_output=True, text=True, timeout=30)
    report = json.loads(result.stdout)
    if result.returncode or report.get('ok') is not True:
        raise RuntimeError('Active runtime identity failed: ' + str(report))
    return report


def selection():
    return json.loads(SELECTION.read_text()) if SELECTION.exists() else None


def selected(state):
    return Path(state['wrapper']) if state else BASE


def save_selection(state):
    temporary = SELECTION.with_suffix('.tmp')
    with temporary.open('w') as stream:
        stream.write(json.dumps(state) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(SELECTION)


def probe(wrapper, phase, artifacts, fixture=None):
    env = {key: value for key, value in os.environ.items() if key != 'NODE_OPTIONS'}
    env['WIKI_TEST_ROOT'] = str(artifacts)
    result = execute([str(wrapper / 'wiki-node'), str(BASE / 'scripts/activation-probe.ts'),
                             str(wrapper), phase, str(fixture or '')],
                            env=env, capture_output=True, text=True, timeout=120)
    (artifacts / (phase + '.stdout')).write_text(result.stdout)
    (artifacts / (phase + '.stderr')).write_text(result.stderr)
    if result.returncode:
        raise RuntimeError('Activation probe failed: ' + phase + '; see ' + str(artifacts))
    report = json.loads(result.stdout)
    if report.get('ok') is not True:
        raise RuntimeError('Activation probe did not confirm success')
    return report


def activate(candidate, report, previous, artifacts):
    snapshot = BASE / '.runtime/releases' / uuid.uuid4().hex / 'wrapper'
    snapshot.parent.mkdir(parents=True)
    shutil.copytree(candidate / 'wrapper', snapshot, symlinks=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
    if runtime_digest(snapshot) != report['runtimeTreeSha256']:
        raise RuntimeError('Candidate changed while copying; renewed qualification required')
    prepared = probe(selected(previous), 'prepare', artifacts)
    current = dict(wrapper=str(snapshot), runtimeTreeSha256=report['runtimeTreeSha256'])
    save_selection({**current, 'pending': True, 'previous': previous})
    active = identity(selected(selection()))
    if (active['commit'] != report['commit'] or active['release'] != report['release']['tag_name']
            or Path(active['wrapper']) != snapshot):
        raise RuntimeError('Selected runtime does not match qualified candidate')
    checked = probe(selected(selection()), 'verify', artifacts, prepared['fixture'])
    if runtime_digest(snapshot) != report['runtimeTreeSha256']:
        raise RuntimeError('Runtime snapshot changed during activation verification')
    save_selection(current)
    return dict(ok=True, outcome='activated', active=active, probe=checked)


def update(args):
    parser = argparse.ArgumentParser(description='Activate a qualified local release candidate')
    parser.add_argument('--candidate', required=True, type=Path)
    options = parser.parse_args(args)
    previous = selection()
    artifacts = BASE / '.runtime/activation-runs' / uuid.uuid4().hex
    artifacts.mkdir(parents=True)
    result = dict(ok=False, outcome='failed', artifacts=str(artifacts))
    try:
        candidate = options.candidate.resolve()
        report = qualified_report(candidate)
        repository = json.loads((BASE / 'compiler-release.json').read_text())['repository']
        if report['repository'] != repository:
            raise RuntimeError('Candidate is from a different upstream repository')
        if previous and previous.get('runtimeTreeSha256') == report['runtimeTreeSha256']:
            if runtime_digest(selected(previous)) != report['runtimeTreeSha256']:
                raise RuntimeError('Active snapshot changed; cannot report an unchanged release')
            result.update(ok=True, outcome='noop', active=identity(selected(previous)))
        else:
            result.update(activate(candidate, report, previous, artifacts))
    except (Exception, KeyboardInterrupt) as error:
        if selection() != previous:
            save_selection(previous)
        result.update(error=str(error) or type(error).__name__)
        try:
            result['active'] = identity(selected(previous))
        except Exception as retained_error:
            result['activeError'] = str(retained_error)
    (artifacts / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['ok'] else 1


def main():
    global LOCK_FD
    args = sys.argv[1:]
    (BASE / '.runtime').mkdir(exist_ok=True)
    with (BASE / '.runtime/operation.lock').open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps(dict(ok=False, error='Wiki runtime busy; retry after the active operation')))
            return 1
        LOCK_FD = lock.fileno()
        state = selection()
        if state and state.get('pending'):
            save_selection(state['previous'])
            print(json.dumps(dict(ok=False, recovered=True,
                                  error='Interrupted activation recovered; previous runtime restored')), file=sys.stderr)
        if args and args[0] == 'update':
            return update(args[1:])
        return run_runtime(selected(selection()), args).returncode


if __name__ == '__main__':
    raise SystemExit(main())
