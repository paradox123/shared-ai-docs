#!/usr/bin/env python3
"""Serialize explicit wiki contexts and the existing QMD index maintenance.

stdout: artifact-directory event, then one final JSON report. Full command output
stays in the new artifact directory. Verified bounded failures permit safe QMD work.
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


def validate_maintenance(value):
    if not isinstance(value.get('pages'), list):
        raise RuntimeError('missing page result')
    if value.get('noop') is not True and not isinstance(value.get('changes'), dict):
        raise RuntimeError('missing change result')
    evidence = value.get('report')
    if not isinstance(evidence, str) or not Path(evidence).is_absolute():
        raise RuntimeError('missing local run report')
    if json.loads(Path(evidence).read_text()) != value:
        raise RuntimeError('local run report does not match command result')
    if value.get('qmdSafe') is not True:
        raise RuntimeError('shared failure or missing eligibility blocks QMD maintenance')
    for field in ['failures', 'pending', 'completed', 'unchanged']:
        if not isinstance(value.get(field), list):
            raise RuntimeError('incomplete maintenance result: ' + field)
    if value.get('ok') is False:
        if not value['failures'] or not value['pending']:
            raise RuntimeError('partial result without failed or pending work')
    elif value.get('ok') is not True:
        raise RuntimeError('missing successful result')
    elif value['pending'] or value['failures']:
        raise RuntimeError('successful result still contains failed or pending work')


def validate_audit(name, value, partial):
    expected_pending = partial['pending'] if partial else []
    if value.get('pending') != expected_pending or not isinstance(value.get('review'), list):
        raise RuntimeError(name + ': pending work or incomplete audit')
    affected_pages = {page for item in expected_pending for page in item.get('pages', [])}
    affected_sources = {source for item in expected_pending for source in item.get('sources', [])}
    if any(item.get('id') not in affected_pages for item in value['review']):
        raise RuntimeError(name + ': unaccounted page review')
    if name.startswith('lint-'):
        if any(value.get(field) != [] for field in ['activeIssues', 'unresolvedCompilerErrors', 'forbiddenStores']):
            raise RuntimeError(name + ': unsafe active wiki output')
    if name.startswith('status-'):
        changes = value.get('changes')
        if not isinstance(changes, dict) or any(not isinstance(changes.get(k), list) for k in ['added', 'changed', 'removed']):
            raise RuntimeError(name + ': missing source audit')
        if any(source not in affected_sources for ids in changes.values() for source in ids):
            raise RuntimeError(name + ': sources changed outside bounded failure')
        if not isinstance(value.get('pages'), list) or type(value.get('sourceCount')) is not int:
            raise RuntimeError(name + ': missing context status')
        if not partial and not value.get('lastCompleted'):
            raise RuntimeError(name + ': missing completed context status')
        if any(page.get('id') in affected_pages and page.get('withdrawn') is not True for page in value['pages']):
            raise RuntimeError(name + ': affected page is still active')


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

    def run(name, command, structured=False, partial=None):
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
        step['outcome'] = 'failed' if code else 'completed'
        allowed_failure = structured and code == 1 and (name.startswith('maintain-') or partial)
        if code and not allowed_failure:
            raise RuntimeError('%s exited %s; see %s.stderr' % (name, code, stem))
        if not structured:
            return None
        value = json.loads(Path(str(stem) + '.stdout').read_text())
        if not isinstance(value, dict):
            raise RuntimeError(name + ': expected JSON object')
        if name == 'reconcile':
            if value.get('status') != 'ok':
                raise RuntimeError(name + ': reconciliation not successful')
        elif name.startswith('maintain-'):
            # Retain independently completed source work even when wiki safety validation blocks later steps.
            if (isinstance(value.get('sourceIndex'), dict) and value.get('report')
                    and json.loads(Path(value['report']).read_text()) == value):
                report['contexts'].append({
                    'context': name.removeprefix('maintain-'),
                    'sourceIndex': value['sourceIndex'], 'wiki': value.get('wiki'),
                    'ok': value.get('ok'), 'report': value['report'],
                    'pending': value.get('pending', [])})
            validate_maintenance(value)
            if (value['ok'] is True) != (code == 0):
                raise RuntimeError(name + ': exit status contradicts result')
            step['outcome'] = 'partial' if not value['ok'] else ('noop' if value.get('noop') else 'completed')
        elif partial and name.startswith(('status-', 'lint-')):
            if type(value.get('ok')) is not bool:
                raise RuntimeError(name + ': missing audit result')
        elif value.get('ok') is not True:
            raise RuntimeError(name + ': missing successful result')
        if name.startswith(('status-', 'lint-')):
            validate_audit(name, value, partial)
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
        for file, config in configs:
            context = config['context']
            maintained = run('maintain-' + context, [args.wiki, 'maintain', '--config', file], True)
            partial = maintained if maintained.get('ok') is False else None
            checked = run('status-' + context, [args.wiki, 'status', '--config', file], True, partial)
            run('lint-' + context, [args.wiki, 'lint', '--config', file], True, partial)
            report['contexts'] = [item for item in report['contexts'] if item['context'] != context]
            report['contexts'].append({'context': context, 'config': file,
                                       'scope': config.get('scope', 'general'),
                                       'noop': maintained.get('noop', False),
                                       'pages': len(checked['pages']),
                                       'sources': checked['sourceCount'],
                                       'lastCompleted': checked['lastCompleted'],
                                       'ok': maintained['ok'],
                                       'sourceIndex': maintained.get('sourceIndex'),
                                       'wiki': maintained.get('wiki'),
                                       'completed': maintained.get('completed', []),
                                       'unchanged': maintained.get('unchanged', []),
                                       'failures': maintained.get('failures', []),
                                       'pending': maintained.get('pending', []),
                                       'report': maintained['report']})
        for action in ['update', 'embed', 'status']:
            run('qmd-' + action, [args.qmd, action])
        report['ok'] = all(context['ok'] for context in report['contexts'])
        if not report['ok']:
            report['error'] = 'Wiki maintenance partially failed; independent work and safe QMD maintenance completed'
            report['remaining'] = [item for context in report['contexts'] for item in context['pending']]
    except Exception as error:
        report['error'] = str(error)
        if report['steps']:
            report['steps'][-1]['outcome'] = 'failed'
        report['remaining'] = ['Resolve failed prerequisite and repeat maintenance; dependent steps were not completed']
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
