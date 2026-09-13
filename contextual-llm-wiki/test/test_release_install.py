"""Public installer contract, with GitHub transport replaced at the process boundary."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]


class ReleaseInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='wiki-release-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        gh = self.bin / 'gh'
        gh.write_text('#!' + sys.executable + '\nimport os\nprint(os.environ["RELEASE_RESPONSE"])\n')
        gh.chmod(0o755)
        self.release = dict(id=123, tag_name='v1.3.0', draft=False, prerelease=False,
                            published_at='2026-09-11T08:16:39Z',
                            html_url='https://github.com/atomicstrata/llm-wiki-compiler/releases/tag/v1.3.0')
        self.destination = self.root / 'candidate'
        self.env = {}

    def install(self, *args):
        result = subprocess.run(
            [sys.executable, str(BASE / 'scripts/install-release.py'), '--release', 'v1.3.0',
             '--destination', str(self.destination), *args],
            env={**os.environ, 'PATH': str(self.bin) + os.pathsep + os.environ['PATH'],
                 'RELEASE_RESPONSE': json.dumps(self.release), **self.env},
            capture_output=True, text=True, timeout=60)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        report = json.loads(result.stdout)
        self.assertFalse(report['eligible'])
        self.assertFalse(report['ok'])
        return report

    def test_prerelease_is_not_a_regular_published_candidate(self):
        self.release['prerelease'] = True
        result = self.install()
        self.assertIn('regular published release', result['error'])
        self.assertEqual(result['checks']['release']['status'], 'failed')
        self.assertEqual(json.loads((self.destination / 'report.json').read_text()), result)

    def test_missing_runtime_keeps_candidate_ineligible_with_pending_build(self):
        result = self.install('--node', str(self.root / 'missing-node'))
        self.assertIn('Runtime unavailable', result['error'])
        self.assertEqual(result['checks']['runtime']['status'], 'failed')
        self.assertEqual(result['checks']['build']['status'], 'pending')
        self.assertEqual(result['release']['id'], 123)

    def test_drafts_unpublished_and_incomplete_release_metadata_are_rejected(self):
        for key, value in [('draft', True), ('published_at', None), ('id', None),
                           ('tag_name', 'main'), ('prerelease', None),
                           ('html_url', 'https://github.com/other/wiki/releases/tag/v1.3.0')]:
            with self.subTest(key=key):
                original = self.release[key]
                self.release[key] = value
                self.destination = self.root / key
                self.assertIn('regular published release', self.install()['error'])
                self.release[key] = original

    def test_existing_destination_is_never_overwritten(self):
        self.destination.mkdir()
        sentinel = self.destination / 'report.json'
        sentinel.write_text('existing active installation')
        self.install()
        self.assertEqual(sentinel.read_text(), 'existing active installation')

    def upstream(self):
        repo = self.root / 'upstream'
        repo.mkdir()
        subprocess.run(['git', 'init', '-q', str(repo)], check=True)
        (repo / 'package.json').write_text('{"name":"fixture","version":"1.3.0"}')
        (repo / 'package-lock.json').write_text('{"lockfileVersion":3}')
        subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null',
                        '-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'release fixture'], check=True)
        subprocess.run(['git', '-C', str(repo), 'tag', '-a', 'v1.3.0', '-m', 'release'],
                       check=True)
        self.env.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0=f'url.{repo.as_uri()}.insteadOf',
                        GIT_CONFIG_VALUE_0='https://github.com/atomicstrata/llm-wiki-compiler.git')
        return subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()

    def test_patch_conflict_records_exact_release_commit_and_stops_before_install(self):
        commit = self.upstream()
        result = self.install()
        self.assertEqual(result.get('commit'), commit)
        self.assertEqual(result['checks']['patches']['status'], 'failed')
        self.assertEqual(result['checks']['dependencies']['status'], 'pending')
        self.assertIn('patch', result['error'])
        self.assertEqual(len(result['patches']), 2)
        self.assertEqual(len(result['patches'][0]['sha256']), 64)

    def test_bare_tag_without_github_release_is_rejected_before_checkout(self):
        self.upstream()
        (self.bin / 'gh').write_text('#!/bin/sh\necho "HTTP 404: Not Found" >&2\nexit 1\n')
        result = self.install()
        self.assertEqual(result['checks']['release']['status'], 'failed')
        self.assertEqual(result['checks']['checkout']['status'], 'pending')
        self.assertNotIn('commit', result)

    def test_incompatible_runtime_is_reported_before_checkout(self):
        node = self.bin / 'old-node'
        node.write_text('#!/bin/sh\necho "20.0.0"\n')
        node.chmod(0o755)
        result = self.install('--node', str(node))
        self.assertIn('Runtime incompatible', result['error'])
        self.assertEqual(result['checks']['checkout']['status'], 'pending')

    def test_invalid_release_lockfile_stops_installation_without_repairing_it(self):
        repo = self.root / 'upstream'
        subprocess.run(['git', 'clone', '-q', '--shared', str(BASE / '.runtime/compiler'), str(repo)],
                       check=True, capture_output=True)
        lock = repo / 'package-lock.json'
        lock.write_text('invalid release lockfile\n')
        subprocess.run(['git', '-C', str(repo), 'add', 'package-lock.json'], check=True)
        subprocess.run(['git', '-C', str(repo), '-c', 'core.hooksPath=/dev/null',
                        '-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'broken upstream lockfile'], check=True)
        subprocess.run(['git', '-C', str(repo), 'tag', '-f', 'v1.3.0'], check=True, capture_output=True)
        self.env.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0=f'url.{repo.as_uri()}.insteadOf',
                        GIT_CONFIG_VALUE_0='https://github.com/atomicstrata/llm-wiki-compiler.git')
        result = self.install()
        self.assertEqual(result['checks']['dependencies']['status'], 'failed')
        self.assertEqual(result['checks']['build']['status'], 'pending')
        self.assertEqual((self.destination / 'wrapper/.runtime/compiler/package-lock.json').read_text(),
                         'invalid release lockfile\n')

    def test_destination_inside_active_compiler_is_rejected_without_writing(self):
        self.destination = BASE / '.runtime/compiler/forbidden-candidate-test'
        result = self.install('--node', str(self.root / 'missing-node'))
        self.assertIn('active installation', result['error'])
        self.assertFalse(self.destination.exists())


if __name__ == '__main__':
    unittest.main()
