#!/usr/bin/env python3
"""Serialize explicit wiki contexts and the existing QMD index maintenance.

stdout: artifact-directory event, then one final JSON report. Full command output
stays in the new artifact directory; a failed step stops the sequence.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import re
from pathlib import Path
import subprocess
import sys


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', action='append', required=True)
    parser.add_argument('--artifacts', required=True, help='New directory; never reuse a previous run')
    parser.add_argument('--wiki', default=str(Path(__file__).resolve().parents[1] / 'wiki'))
    parser.add_argument('--qmd', required=True, help='Resolved QMD executable')
    parser.add_argument('--reconcile', required=True, help='Existing sync-qmd-collections.py')
    parser.add_argument('--lock-file', help='Shared by all scheduled/manual runs; defaults beside artifacts')
    args = parser.parse_args()
    artifacts = Path(args.artifacts).resolve()
    report = {'ok': False, 'startedAt': stamp(), 'artifacts': str(artifacts), 'steps': [], 'contexts': []}
    try:
        artifacts.mkdir(parents=True, exist_ok=False, mode=0o700)
    except OSError as error:
        print(json.dumps({**report, 'error': str(error)}))
        return 1
    print(json.dumps({'event': 'artifacts', 'path': str(artifacts)}), flush=True)

    def run(name, command, structured=False):
        stem = artifacts / ('%02d-%s' % (len(report['steps']) + 1, name))
        step = {'name': name, 'command': command, 'startedAt': stamp()}
        report['steps'].append(step)
        with Path(str(stem) + '.stdout').open('w') as out, Path(str(stem) + '.stderr').open('w') as err:
            try:
                result = subprocess.run(command, cwd='/', stdout=out, stderr=err)
                code = result.returncode
            except OSError as error:
                err.write(str(error))
                code = 127
        Path(str(stem) + '.exitcode').write_text(str(code) + '\n')
        step.update(exitCode=code, completedAt=stamp(), output=str(stem) + '.stdout')
        if code:
            raise RuntimeError('%s exited %s; see %s.stderr' % (name, code, stem))
        if not structured:
            return None
        value = json.loads(Path(str(stem) + '.stdout').read_text())
        if not isinstance(value, dict):
            raise RuntimeError(name + ': expected JSON object')
        if name == 'reconcile':
            if value.get('status') != 'ok':
                raise RuntimeError(name + ': reconciliation not successful')
        elif value.get('ok') is not True:
            raise RuntimeError(name + ': missing successful result')
        if name.startswith('maintain-'):
            if not isinstance(value.get('pages'), list):
                raise RuntimeError(name + ': missing page result')
            if value.get('noop') is not True and not isinstance(value.get('changes'), dict):
                raise RuntimeError(name + ': missing change result')
        if name.startswith(('status-', 'lint-')):
            fields = ['pending', 'review']
            if name.startswith('lint-'):
                fields += ['activeIssues', 'unresolvedCompilerErrors', 'forbiddenStores']
            if any(value.get(field) != [] for field in fields):
                raise RuntimeError(name + ': pending work or incomplete audit')
        if name.startswith('status-'):
            changes = value.get('changes')
            if not isinstance(changes, dict) or any(changes.get(k) != [] for k in ['added', 'changed', 'removed']):
                raise RuntimeError(name + ': sources changed or missing source audit')
            if not isinstance(value.get('pages'), list) or type(value.get('sourceCount')) is not int or not value.get('lastCompleted'):
                raise RuntimeError(name + ': missing completed context status')
        return value

    lock = None
    try:
        lock_path = Path(args.lock_file).resolve() if args.lock_file else artifacts.parent / 'maintenance.lock'
        lock = lock_path.open('a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        configs = [(str(Path(p).resolve()), json.loads(Path(p).read_text())) for p in args.config]
        names = [c.get('context') for _, c in configs]
        if any(not isinstance(n, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', n) for n in names) or len(set(names)) != len(names):
            raise ValueError('Context names must be valid and unique')
        run('reconcile', [sys.executable, str(Path(args.reconcile).absolute()), '--apply'], True)
        run('preflight', [args.wiki, 'preflight'], True)
        for file, config in configs:
            context = config['context']
            maintained = run('maintain-' + context, [args.wiki, 'maintain', '--config', file], True)
            checked = run('status-' + context, [args.wiki, 'status', '--config', file], True)
            run('lint-' + context, [args.wiki, 'lint', '--config', file], True)
            report['contexts'].append({'context': context, 'config': file,
                                       'scope': config.get('scope', 'general'),
                                       'noop': maintained.get('noop', False),
                                       'pages': len(checked['pages']),
                                       'sources': checked['sourceCount'],
                                       'lastCompleted': checked['lastCompleted']})
        for action in ['update', 'embed', 'status']:
            run('qmd-' + action, [args.qmd, action])
        report['ok'] = True
    except Exception as error:
        report['error'] = str(error)
        report['failedStep'] = report['steps'][-1]['name'] if report['steps'] else 'preflight-or-lock'
    finally:
        if lock:
            lock.close()
    report['completedAt'] = stamp()
    (artifacts / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
