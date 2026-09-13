#!/usr/bin/env python3
"""Real Mac activation, no-op and failed retrieval probe through the public wiki.

Uses the supplied fully qualified candidate and an isolated installation entry.
No production configuration or scheduler is passed to the update operation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from release_support import wrapper_input, retrieval_failure_path

BASE = Path(__file__).resolve().parents[1]


def files_digest(root):
    result = {}
    if root.is_file():
        result[root.name] = hashlib.sha256(root.read_bytes()).hexdigest()
    elif root.exists():
        for file in sorted(root.rglob('*')):
            if file.is_file():
                result[str(file.relative_to(root))] = hashlib.sha256(file.read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--protected-config', type=Path)
    parser.add_argument('--scheduler', type=Path)
    options = parser.parse_args()
    candidate = options.candidate.resolve()
    root = Path(tempfile.mkdtemp(prefix='activation-acceptance-', dir=BASE / '.runtime')).resolve()
    base = wrapper_input(root / 'installation')
    protected = []
    if options.protected_config:
        config = options.protected_config.resolve()
        protected += [config, (config.parent / json.loads(config.read_text())['output']).resolve()]
    if options.scheduler:
        protected.append(options.scheduler.resolve())
    before = {str(p): files_digest(p) for p in protected}

    def wiki(*args, env=None):
        result = subprocess.run([str(base / 'wiki'), *args], text=True, capture_output=True,
                                env={**os.environ, **(env or {})}, timeout=300)
        return result.returncode, json.loads(result.stdout)

    fault_bin = retrieval_failure_path(root)
    _, original = wiki('release-status')
    code, failed = wiki('update', '--candidate', str(candidate), env={
        'WIKI_QMD_PATH': str(fault_bin) + os.pathsep + os.environ['PATH']})
    assert code == 1 and failed['active'] == original, failed
    assert 'Activation probe failed: verify' in failed['error'], failed
    print('Failed functional probe restored previous runtime', flush=True)
    code, activated = wiki('update', '--candidate', str(candidate))
    assert code == 0 and activated['outcome'] == 'activated', activated
    assert activated['probe']['savedKnowledgePreserved'] is True, activated
    code, active = wiki('release-status')
    assert code == 0 and active == activated['active'], active
    selection = (base / '.runtime/selection.json').read_bytes()
    code, noop = wiki('update', '--candidate', str(candidate))
    assert code == 0 and noop['outcome'] == 'noop', noop
    assert (base / '.runtime/selection.json').read_bytes() == selection
    after = {str(p): files_digest(p) for p in protected}
    assert before == after, 'Protected production files changed during acceptance'
    report = dict(ok=True, installation=str(base), candidate=str(candidate), before=original,
                  failure=failed, activation=activated, active=active, noop=noop,
                  protectedBefore=before, protectedAfter=after, protectedUnchanged=before == after)
    (root / 'acceptance.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Activation, saved knowledge and no-op verified: ' + str(root / 'acceptance.json'))


if __name__ == '__main__':
    main()
