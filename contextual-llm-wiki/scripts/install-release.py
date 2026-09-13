#!/usr/bin/env python3
"""Prepare and qualify a separate upstream release candidate; never activate it."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
from urllib.parse import quote
import uuid

BASE = Path(__file__).resolve().parents[1]
REQUIRED = ('release', 'runtime', 'checkout', 'patches', 'dependencies', 'build',
            'typecheck', 'upstream-tests', 'integration-tests', 'integrity')


class Candidate:
    def __init__(self, destination, tag):
        self.root = destination.resolve()
        protected = [BASE / name for name in (
            '.runtime/compiler', '.runtime/node', '.local', 'src', 'test',
            'scripts', 'patches', 'node_modules')]
        if any(self.root.is_relative_to(path.resolve()) for path in protected):
            raise RuntimeError('Candidate destination overlaps the active installation')
        self.root.mkdir()  # Exclusive creation: never overwrite an existing installation/report.
        (self.root / 'logs').mkdir()
        self.report = dict(schemaVersion=1, candidate=str(self.root), requestedRelease=tag,
                           createdAt=datetime.now(timezone.utc).isoformat(), ok=False,
                           eligible=False, checks={name: {'status': 'pending'} for name in REQUIRED})
        self.save()

    def save(self):
        temporary = self.root / 'report.json.tmp'
        temporary.write_text(json.dumps(self.report, indent=2) + '\n')
        temporary.replace(self.root / 'report.json')

    @contextmanager
    def check(self, name):
        self.report['checks'][name] = {'status': 'running'}
        self.save()
        try:
            yield
        except BaseException:
            self.report['checks'][name]['status'] = 'failed'
            self.save()
            raise
        self.report['checks'][name]['status'] = 'passed'
        self.save()

    def command(self, name, args, cwd=None, env=None, timeout=900):
        with (self.root / 'logs' / (name + '.log')).open('w') as log:
            result = subprocess.run(args, cwd=cwd, env=env, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=timeout, text=True)
        if result.returncode:
            raise RuntimeError(f'{name} failed (exit {result.returncode}); see logs/{name}.log')
        return (self.root / 'logs' / (name + '.log')).read_text()


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def dependency_inputs(compiler):
    return {name: digest(compiler / name) for name in ('package.json', 'package-lock.json')}


def tree_digest(root, exclude=frozenset()):
    files = {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob('*'))
             if p.is_file() and not set(p.relative_to(root).parts).intersection(exclude | {'__pycache__'})}
    if not files:
        raise RuntimeError(f'No artifacts found: {root}')
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def required_tests(wrapper, target, kind):
    tests = (wrapper / f'scripts/{kind}-tests.txt').read_text().splitlines()
    if not tests or any(not test or not (target / test).is_file() for test in tests):
        raise RuntimeError(f'Required {kind} test files missing')
    return tests


def install(candidate, args):
    definition = json.loads((BASE / 'compiler-release.json').read_text())
    repository = definition['repository']
    candidate.report['repository'] = repository
    with candidate.check('release'):
        release = json.loads(candidate.command('release', [
            'gh', 'api', '--hostname', 'github.com',
            f'repos/{repository}/releases/tags/{quote(args.release, safe="")}',
        ], timeout=60))
        if (release.get('tag_name') != args.release or release.get('draft') is not False
                or release.get('prerelease') is not False or not release.get('published_at')
                or not isinstance(release.get('id'), int)
                or release.get('html_url') != f'https://github.com/{repository}/releases/tag/{quote(args.release, safe="/")}'):
            raise RuntimeError('Not a regular published release of the configured upstream repository')
        candidate.report['release'] = {key: release[key] for key in (
            'id', 'tag_name', 'draft', 'prerelease', 'published_at', 'html_url')}
    with candidate.check('runtime'):
        node = args.node.resolve()
        if not node.is_file() or not os.access(node, os.X_OK):
            raise RuntimeError(f'Runtime unavailable: {node}')
        version = candidate.command('runtime', [str(node), '-p', 'process.versions.node']).strip()
        required = json.loads((BASE / 'package.json').read_text())['engines']['node']
        if version != required:
            raise RuntimeError(f'Runtime incompatible with wrapper: need {required}, got {version}')
        candidate.report['runtime'] = dict(node=str(node), version=version)
    wrapper = candidate.root / 'wrapper'
    wrapper.mkdir()
    for name in ('src', 'scripts', 'test', 'patches'):
        shutil.copytree(BASE / name, wrapper / name, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('package.json', 'package-lock.json', 'tsconfig.json', 'wiki', 'wiki-node'):
        shutil.copy2(BASE / name, wrapper / name)
    node_link = wrapper / '.runtime/node/node_modules/node/bin/node'
    node_link.parent.mkdir(parents=True)
    node_link.symlink_to(node)
    compiler = wrapper / '.runtime/compiler'
    with candidate.check('checkout'):
        candidate.command('git-init', ['git', 'init', '-q', str(compiler)])
        candidate.command('git-fetch', ['git', '-C', str(compiler), 'fetch', '--depth=1',
                                      f'https://github.com/{repository}.git', f'refs/tags/{args.release}'])
        commit = candidate.command('git-commit', ['git', '-C', str(compiler),
                                                'rev-parse', 'FETCH_HEAD^{commit}']).strip()
        candidate.report['commit'] = commit
        candidate.command('git-checkout', ['git', '-C', str(compiler), '-c', 'core.hooksPath=/dev/null',
                                         'checkout', '--detach', commit])
        (wrapper / 'compiler-release.json').write_text(json.dumps(dict(
            repository=repository, release=args.release, commit=commit), indent=2) + '\n')
        candidate.report['dependencyInputs'] = dependency_inputs(compiler)
    with candidate.check('patches'):
        patches = sorted((wrapper / 'patches').glob('*.patch'))
        if not patches:
            raise RuntimeError('Required integration patches missing')
        candidate.report['patches'] = [dict(name=p.name, sha256=digest(p)) for p in patches]
        candidate.save()
        for patch in patches:
            candidate.command('patch-' + patch.stem, ['git', '-C', str(compiler), 'apply', str(patch)])
        if dependency_inputs(compiler) != candidate.report['dependencyInputs']:
            raise RuntimeError('Integration patches changed upstream manifest or lockfile')
    env = {**os.environ, 'PATH': str(node.parent) + os.pathsep + os.environ['PATH'],
           'WIKI_QMD_PATH': os.environ.get('WIKI_QMD_PATH', os.environ['PATH']), 'HUSKY': '0'}
    # Never run npm install/update: each package keeps its own upstream lockfile.
    with candidate.check('dependencies'):
        for name, directory in [('compiler', compiler), ('wrapper', wrapper)]:
            candidate.command(name + '-ci', ['npm', 'ci', '--ignore-scripts', '--include=dev',
                                            '--engine-strict', '--no-audit', '--no-fund'],
                              cwd=directory, env=env)
        if dependency_inputs(compiler) != candidate.report['dependencyInputs']:
            raise RuntimeError('Installation changed upstream manifest or lockfile')
    with candidate.check('build'):
        candidate.command('build', ['npm', 'run', 'build'], cwd=compiler, env=env)
        if not (compiler / 'dist/index.js').is_file():
            raise RuntimeError('Compiler build entrypoint missing')
    with candidate.check('typecheck'):
        candidate.command('typecheck', ['npm', 'run', 'typecheck'], cwd=wrapper, env=env)
    with candidate.check('upstream-tests'):
        tests = required_tests(wrapper, compiler, 'upstream')
        result_path = candidate.root / 'logs/upstream-results.json'
        candidate.command('upstream-tests', [str(wrapper / 'scripts/verify-upstream.sh'),
                                            '--reporter=json', '--outputFile=' + str(result_path)],
                          cwd=wrapper, env=env)
        results = json.loads(result_path.read_text())
        count = results.get('numTotalTests', 0)
        if (results.get('success') is not True or count <= 0
                or results.get('numPassedTests') != count
                or results.get('numPendingTests') != 0 or results.get('numTodoTests') != 0):
            raise RuntimeError('Required upstream tests missing, pending or failed')
        executed = {Path(result['name']).resolve(): result for result in results.get('testResults', [])}
        for test in tests:
            result = executed.get((compiler / test).resolve(), {})
            assertions = result.get('assertionResults', [])
            if (result.get('status') != 'passed' or not assertions
                    or any(assertion.get('status') != 'passed' for assertion in assertions)):
                raise RuntimeError(f'Required upstream test not fully executed: {test}')
        candidate.report['checks']['upstream-tests']['testsPassed'] = count
    with candidate.check('integration-tests'):
        tests = required_tests(wrapper, wrapper, 'integration')
        fixtures = candidate.root / 'fixtures'
        fixtures.mkdir()
        # Inherited Node test filters can silently remove scenarios within a file.
        test_env = {key: value for key, value in env.items() if key != 'NODE_OPTIONS'}
        events_path = candidate.root / 'logs/integration-events.jsonl'
        result = candidate.command('integration-tests', [str(wrapper / 'wiki-node'), '--test',
                                   '--test-reporter=tap', '--test-reporter-destination=stdout',
                                   '--test-reporter=' + str(wrapper / 'scripts/report-tests.mjs'),
                                   '--test-reporter-destination=' + str(events_path), *tests], cwd=wrapper,
                                   env={**test_env, 'WIKI_TEST_ROOT': str(fixtures)})
        summary = {name: int(value) for name, value in re.findall(
            r'^# (tests|pass|fail|cancelled|skipped|todo) (\d+)$', result, re.MULTILINE)}
        if (summary.get('tests', 0) <= 0 or summary.get('pass') != summary.get('tests')
                or any(summary.get(name) != 0 for name in ('fail', 'cancelled', 'skipped', 'todo'))):
            raise RuntimeError('Required integration tests missing, pending or failed')
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        executed = {Path(event['file']).resolve() for event in events
                    if event.get('file') and event.get('event') == 'test:pass'
                    and event.get('type') == 'test' and not event.get('skip') and not event.get('todo')
                    and (wrapper / event['name']).resolve() != Path(event['file']).resolve()}
        for test in tests:
            if (wrapper / test).resolve() not in executed:
                raise RuntimeError(f'Required integration test not executed: {test}')
        candidate.report['checks']['integration-tests']['testsPassed'] = summary['pass']
    with candidate.check('integrity'):
        if dependency_inputs(compiler) != candidate.report['dependencyInputs']:
            raise RuntimeError('Build or checks changed upstream manifest or lockfile')
        candidate.report['compilerBuildSha256'] = tree_digest(compiler / 'dist')
        candidate.report['wrapperSha256'] = tree_digest(wrapper, exclude={'.runtime', 'node_modules'})
        candidate.report['runtime']['sha256'] = digest(node)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', required=True, help='Published regular upstream release tag')
    parser.add_argument('--destination', type=Path, help='New, non-existing candidate directory')
    parser.add_argument('--node', type=Path, default=BASE / '.runtime/node/node_modules/node/bin/node')
    args = parser.parse_args()
    candidate = None
    try:
        if args.destination is None:
            parent = BASE / '.runtime/candidates'
            parent.mkdir(parents=True, exist_ok=True)
            args.destination = parent / uuid.uuid4().hex
        candidate = Candidate(args.destination, args.release)
        install(candidate, args)
        candidate.report['eligible'] = all(
            candidate.report['checks'][name]['status'] == 'passed' for name in REQUIRED)
        candidate.report['ok'] = candidate.report['eligible']
        candidate.save()
    except (Exception, KeyboardInterrupt) as error:
        report = candidate.report if candidate else dict(ok=False, eligible=False)
        report.update(ok=False, eligible=False, error=str(error) or type(error).__name__)
        if candidate:
            try:
                candidate.save()
            except OSError as persistence_error:
                report['reportPersistenceError'] = str(persistence_error)
        print(json.dumps(report))
        return 1
    print(json.dumps(candidate.report))
    return 0 if candidate.report['eligible'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
