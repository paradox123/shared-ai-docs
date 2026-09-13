#!/usr/bin/env python3
"""Exercise the public installer against a real release and a missing required test.

Run manually: python3 test/accept-release.py --release v1.3.0
Uses real GitHub/Git/npm/compiler/QMD; model responses use bounded test fixtures.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parents[1]


def active_identity():
    compiler = BASE / '.runtime/compiler'
    files = ('compiler-release.json', 'src/runtime.ts', 'wiki', 'wiki-node',
             '.runtime/compiler/package.json', '.runtime/compiler/package-lock.json',
             '.runtime/compiler/dist/index.js')
    return dict(files={name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in files},
                commit=subprocess.check_output(['git', '-C', str(compiler), 'rev-parse', 'HEAD'], text=True).strip(),
                patch=hashlib.sha256(subprocess.check_output(['git', '-C', str(compiler), 'diff', 'HEAD'])).hexdigest())


def invoke(source, release, destination):
    result = subprocess.run([sys.executable, str(source / 'scripts/install-release.py'),
                             '--release', release, '--destination', str(destination),
                             '--node', str(BASE / '.runtime/node/node_modules/node/bin/node')],
                            capture_output=True, text=True, timeout=1200)
    report = json.loads(result.stdout)
    assert report == json.loads((destination / 'report.json').read_text())
    return result.returncode, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', default='v1.3.0')
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix='release-acceptance-', dir=BASE / '.runtime')).resolve()
    before = active_identity()
    code, passed = invoke(BASE, args.release, root / 'success')
    assert code == 0 and passed['eligible'] is True, passed
    assert passed['checks']['upstream-tests']['testsPassed'] > 0
    assert passed['checks']['integration-tests']['testsPassed'] > 0
    print('Real release passed: ' + str(root / 'success/report.json'), flush=True)
    fault = root / 'missing-test-input'
    fault.mkdir()
    for name in ('src', 'test', 'scripts', 'patches'):
        shutil.copytree(BASE / name, fault / name, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('compiler-release.json', 'package.json', 'package-lock.json', 'tsconfig.json', 'wiki', 'wiki-node'):
        shutil.copy2(BASE / name, fault / name)
    (fault / 'test/release-compatibility.test.ts').unlink()
    code, failed = invoke(fault, args.release, root / 'failure')
    assert code == 1 and failed['eligible'] is False, failed
    assert failed['checks']['dependencies']['status'] == 'passed', failed
    assert failed['checks']['build']['status'] == 'passed', failed
    assert failed['checks']['integration-tests']['status'] == 'failed', failed
    assert 'test files missing' in failed['error'], failed
    after = active_identity()
    assert before == after, 'Active installation changed'
    summary = dict(release=args.release, commit=passed['commit'], success=passed, failure=failed,
                   activeInstallationUnchanged=True, activeBefore=before, activeAfter=after)
    (root / 'acceptance.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('Required test absent blocks eligibility; active installation unchanged: ' + str(root / 'acceptance.json'))


if __name__ == '__main__':
    main()
