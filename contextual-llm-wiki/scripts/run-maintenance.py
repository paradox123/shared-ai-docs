#!/usr/bin/env python3
"""Start maintenance once, retain its artifacts and bound observation independently."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from bounded_process import persist, snapshot


def seconds(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('must be finite and positive')
    return number


def tail(file):
    with Path(file).open('rb') as stream:
        stream.seek(0, 2)
        stream.seek(max(0, stream.tell() - 4000))
        return stream.read(4000).decode(errors='replace')


def terminate_owned(child, grace):
    if child.poll() is not None:
        return
    child.terminate()
    try:
        child.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait(timeout=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--helper', default=str(Path(__file__).with_name('maintain-index.py')))
    parser.add_argument('--artifacts', required=True, help='New task-owned directory')
    parser.add_argument('--budget-seconds', type=seconds, default=1200)
    parser.add_argument('--termination-grace-seconds', type=seconds, default=10)
    parser.add_argument('--observation-margin-seconds', type=seconds, default=30)
    parser.add_argument('--stall-seconds', type=seconds, default=180)
    args, helper_args = parser.parse_known_args()
    artifacts = Path(args.artifacts).resolve()
    try:
        artifacts.mkdir(parents=True, exist_ok=False, mode=0o700)
    except OSError as error:
        print(json.dumps({'ok': False, 'outcome': 'artifact-directory-unavailable',
                          'artifacts': str(artifacts), 'helper': {'starts': 0, 'running': False},
                          'error': str(error)}), flush=True)
        return 1
    helper_artifacts = artifacts / 'maintenance'
    print(json.dumps({'event': 'artifacts', 'path': str(artifacts)}), flush=True)
    started = time.monotonic()
    limit = args.budget_seconds + args.termination_grace_seconds + args.observation_margin_seconds
    result = {'ok': False, 'artifacts': str(artifacts), 'helperArtifacts': str(helper_artifacts),
              'limits': {'budgetSeconds': args.budget_seconds, 'terminationGraceSeconds': args.termination_grace_seconds,
                         'observationSeconds': limit, 'stallSeconds': args.stall_seconds}, 'helper': {'starts': 0}}
    if not any(value == '--lock-file' or value.startswith('--lock-file=') for value in helper_args):
        helper_args += ['--lock-file', str(artifacts.parent / 'maintenance.lock')]
    child = None
    try:
        with (artifacts / 'helper.stdout').open('w') as out, (artifacts / 'helper.stderr').open('w') as err:
            child = subprocess.Popen([sys.executable, args.helper, '--artifacts', str(helper_artifacts),
                '--budget-seconds', str(args.budget_seconds), '--termination-grace-seconds', str(args.termination_grace_seconds),
                *helper_args], stdout=out, stderr=err, stdin=subprocess.DEVNULL)
            result['helper'] = {'starts': 1, 'pid': child.pid, 'running': True}
            persist(artifacts / 'process.json', result['helper'])
            previous = None
            last_change = started
            diagnosed = False
            while child.poll() is None and time.monotonic() - started < limit:
                progress = snapshot(helper_artifacts / 'progress.json')
                detail = snapshot(progress['detail']) if progress.get('detail') else {}
                current = [progress, detail]
                if current != previous:
                    previous, last_change = current, time.monotonic()
                if not diagnosed and time.monotonic() - last_change >= args.stall_seconds:
                    persist(artifacts / 'diagnosis.json', {'reason': 'no-durable-progress', 'helperPid': child.pid,
                            'progress': progress, 'detail': detail, 'elapsedSeconds': time.monotonic() - started})
                    diagnosed = True
                time.sleep(min(0.2, max(0, limit - (time.monotonic() - started))))
            if child.poll() is None:
                result['outcome'] = 'observation-expired'
                # Only our unreaped direct child. Its existing guardian retains cleanup custody.
                terminate_owned(child, args.termination_grace_seconds)
            result['helper'].update(running=child.poll() is None, exitCode=child.returncode)
            (artifacts / 'helper.exitcode').write_text(str(child.returncode) + '\n')
        report = snapshot(helper_artifacts / 'report.json')
        result['progress'] = snapshot(helper_artifacts / 'progress.json')
        if result['progress'].get('detail'):
            result['detail'] = snapshot(result['progress']['detail'])
        if type(report.get('ok')) is not bool or not isinstance(report.get('contexts'), list):
            result.setdefault('outcome', 'missing-or-invalid-report')
        else:
            result['report'] = report
            result['ok'] = (child.returncode == 0 and report['ok'] is True and not report.get('remaining')
                            and bool(report['contexts']) and all(c.get('ok') is True and not c.get('pending') for c in report['contexts'])
                            and 'outcome' not in result)
            result.setdefault('outcome', 'completed' if result['ok'] else 'incomplete-or-failed')
        if not result['ok']:
            persist(artifacts / 'diagnosis.json', {'reason': result['outcome'], 'helper': result['helper'],
                    'progress': result.get('progress'), 'detail': result.get('detail'),
                    'remaining': report.get('remaining', [{'phase': 'unknown-without-final-report'}]),
                    'stderrTail': tail(artifacts / 'helper.stderr')})
    except Exception as error:
        result.update(ok=False, outcome='observer-failed', error=str(error))
        if child:
            try:
                terminate_owned(child, args.termination_grace_seconds)
            except (OSError, subprocess.TimeoutExpired) as cleanup_error:
                result['cleanupError'] = str(cleanup_error)
            result['helper'].update(running=child.poll() is None, exitCode=child.returncode)
        result['progress'] = snapshot(helper_artifacts / 'progress.json')
        result['remaining'] = [{'phase': 'unknown-after-observer-failure'}]
    result['elapsedSeconds'] = time.monotonic() - started
    for name, value in [('process.json', result['helper']), ('observation.json', result)]:
        try:
            persist(artifacts / name, value)
        except OSError:
            result.update(ok=False, outcome='observer-storage-failure')
            result.setdefault('artifactErrors', []).append({'artifact': name, 'code': 'persist-failed'})
    print(json.dumps(result), flush=True)
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
