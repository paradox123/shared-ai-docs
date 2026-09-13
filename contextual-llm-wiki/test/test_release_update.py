"""Activation contract through the installed wiki entry point on bounded fixtures."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import time
import signal

from release_support import BASE, wrapper_input, retrieval_failure_path




class ReleaseUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='wiki-update-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.base = wrapper_input(self.root / 'installation')
        self.candidate = self.root / 'candidate'
        self.candidate.mkdir()
        (self.candidate / 'report.json').write_text(json.dumps(dict(ok=False, eligible=False)))

    def wiki(self, *args, env=None):
        result = subprocess.run([str(self.base / 'wiki'), *args], text=True,
                                capture_output=True, timeout=180, env={**os.environ, **(env or {})})
        return result.returncode, json.loads(result.stdout)

    @classmethod
    def qualified_candidate(cls):
        if os.environ.get('WIKI_UPDATE_TEST_CANDIDATE'):
            return Path(os.environ['WIKI_UPDATE_TEST_CANDIDATE']).resolve()
        if not hasattr(cls, 'qualified'):
            cls.qualified_temp = tempfile.TemporaryDirectory(prefix='wiki-qualified-test-')
            cls.addClassCleanup(cls.qualified_temp.cleanup)
            root = Path(cls.qualified_temp.name).resolve()
            cls.qualified = root / 'candidate'
            # GitHub metadata is replaced at its transport boundary; Git/npm/tests are real.
            bin_dir = root / 'bin'
            bin_dir.mkdir()
            release = dict(id=123, tag_name='v1.3.0', draft=False, prerelease=False,
                           published_at='2026-09-11T08:16:39Z',
                           html_url='https://github.com/atomicstrata/llm-wiki-compiler/releases/tag/v1.3.0')
            gh = bin_dir / 'gh'
            gh.write_text('#!' + sys.executable + '\nprint(' + repr(json.dumps(release)) + ')\n')
            gh.chmod(0o755)
            env = {**os.environ, 'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'],
                   'GIT_CONFIG_COUNT': '1',
                   'GIT_CONFIG_KEY_0': f'url.{(BASE / ".runtime/compiler").resolve().as_uri()}.insteadOf',
                   'GIT_CONFIG_VALUE_0': 'https://github.com/atomicstrata/llm-wiki-compiler.git'}
            command = [sys.executable, str(BASE / 'scripts/install-release.py'),
                       '--release', 'v1.3.0', '--destination', str(cls.qualified)]
            with subprocess.Popen(command, env=env, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, start_new_session=True) as child:
                try:
                    out, err = child.communicate(timeout=900)
                except BaseException:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
                    raise
                result = subprocess.CompletedProcess(command, child.returncode, out, err)
            if result.returncode:
                raise AssertionError(result.stdout + result.stderr)
        return cls.qualified

    def test_qualified_candidate_becomes_the_actual_runtime_and_preserves_saved_knowledge(self):
        code, result = self.wiki('update', '--candidate', str(self.qualified_candidate()))
        self.assertEqual(code, 0, result)
        self.assertEqual(result['outcome'], 'activated')
        self.assertTrue(result['probe']['savedKnowledgePreserved'])
        self.assertTrue(result['probe']['noop'])
        self.assertTrue(result['probe'].get('updatedKnowledgeVerified'), result['probe'])
        self.assertEqual(result['active']['release'], 'v1.3.0')
        self.assertNotEqual(Path(result['active']['wrapper']), self.base)
        code, active = self.wiki('release-status')
        self.assertEqual(code, 0, active)
        self.assertEqual(active['wrapper'], result['active']['wrapper'])
        self.assertEqual(active['commit'], result['active']['commit'])

    def test_repeating_unchanged_candidate_is_a_noop(self):
        candidate = self.qualified_candidate()
        code, first = self.wiki('update', '--candidate', str(candidate))
        self.assertEqual(code, 0, first)
        selection = (self.base / '.runtime/selection.json').read_bytes()
        code, repeated = self.wiki('update', '--candidate', str(candidate))
        self.assertEqual(code, 0, repeated)
        self.assertEqual(repeated['outcome'], 'noop')
        self.assertEqual(repeated['active'], first['active'])
        self.assertEqual((self.base / '.runtime/selection.json').read_bytes(), selection)

    def test_postqualification_changes_to_code_build_dependencies_and_node_are_rejected(self):
        shutil.rmtree(self.candidate)
        self.candidate.mkdir()
        qualified = self.qualified_candidate()
        shutil.copy2(qualified / 'report.json', self.candidate / 'report.json')
        wrapper = self.candidate / 'wrapper'
        shutil.copytree(qualified / 'wrapper', wrapper, symlinks=True,
                        ignore=shutil.ignore_patterns('__pycache__'))
        code, activated = self.wiki('update', '--candidate', str(self.candidate))
        self.assertEqual(code, 0, activated)
        for relative in ('src/runtime.ts', '.runtime/compiler/dist/index.js',
                         'node_modules/minimatch/package.json',
                         '.runtime/compiler/node_modules/vitest/package.json',
                         '.runtime/node/node_modules/node/bin/node'):
            with self.subTest(artifact=relative):
                file = wrapper / relative
                original = file.read_bytes()
                try:
                    file.write_bytes(original + b'\nchanged after tests\n')
                    code, result = self.wiki('update', '--candidate', str(self.candidate))
                    self.assertEqual(code, 1, result)
                    self.assertIn('changed since qualification', result['error'])
                    self.assertEqual(result['active'], activated['active'])
                finally:
                    file.write_bytes(original)

    def test_failed_public_function_probe_restores_previous_runtime(self):
        bin_dir = retrieval_failure_path(self.root)
        code, result = self.wiki('update', '--candidate', str(self.qualified_candidate()),
                                 env={'WIKI_QMD_PATH': str(bin_dir) + os.pathsep + os.environ['PATH']})
        self.assertEqual(code, 1, result)
        self.assertIn('Activation probe failed: verify', result['error'])
        self.assertEqual(Path(result['active']['wrapper']), self.base)
        self.assertIn('deliberate activation retrieval failure',
                      (Path(result['artifacts']) / 'verify.stderr').read_text())
        code, active = self.wiki('release-status')
        self.assertEqual(code, 0, active)
        self.assertEqual(Path(active['wrapper']), self.base)

    def test_eligibility_flag_cannot_replace_missing_or_pending_required_checks(self):
        for checks in ({}, {'build': {'status': 'passed'}, 'integration-tests': {'status': 'pending'}}):
            (self.candidate / 'report.json').write_text(json.dumps(dict(ok=True, eligible=True, checks=checks)))
            code, result = self.wiki('update', '--candidate', str(self.candidate))
            self.assertEqual(code, 1, result)
            self.assertIn('not qualified', result['error'])
            self.assertEqual(Path(result['active']['wrapper']), self.base)

    def test_interrupted_provisional_selection_is_recovered_before_public_use(self):
        state = self.base / '.runtime/selection.json'
        state.write_text(json.dumps(dict(wrapper=str(self.root / 'incomplete-snapshot'),
                                        pending=True, previous=None)))
        result = subprocess.run([str(self.base / 'wiki'), 'release-status'],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        active = json.loads(result.stdout)
        self.assertEqual(Path(active['wrapper']), self.base)
        self.assertIsNone(json.loads(state.read_text()))
        recovery = json.loads(result.stderr)
        self.assertTrue(recovery['recovered'])
        self.assertEqual(recovery.get('active'), active)
        self.assertEqual(json.loads((Path(recovery['artifacts']) / 'report.json').read_text()), recovery)

    def test_running_public_wiki_rejects_update_as_busy(self):
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        marker = self.root / 'entered'
        resume = self.root / 'resume'
        git = bin_dir / 'git'
        git.write_text('#!' + sys.executable + '\nimport os,time\nfrom pathlib import Path\n'
                       + 'Path(' + repr(str(marker)) + ').touch()\n'
                       + 'while not Path(' + repr(str(resume)) + ').exists(): time.sleep(0.02)\n'
                       + 'os.execv(' + repr(shutil.which('git')) + ', ["git", *os.sys.argv[1:]])\n')
        git.chmod(0o755)
        child = subprocess.Popen([str(self.base / 'wiki'), 'release-status'],
                                 env={**os.environ, 'PATH': str(bin_dir) + os.pathsep + os.environ['PATH']},
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 30
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(marker.exists(), 'Wiki did not reach its runtime identity check')
            code, result = self.wiki('update', '--candidate', str(self.candidate))
            self.assertEqual(code, 1)
            self.assertIn('busy', result['error'].lower())
        finally:
            resume.touch()
            child.communicate(timeout=30)

    def test_unqualified_candidate_is_rejected_and_previous_identity_is_reported(self):
        code, result = self.wiki('update', '--candidate', str(self.candidate))
        self.assertEqual(code, 1)
        self.assertIn('not qualified', result['error'])
        self.assertEqual(result['active']['commit'], json.loads((BASE / 'compiler-release.json').read_text())['commit'])
        self.assertFalse((self.base / '.runtime/selection.json').exists())


if __name__ == '__main__':
    unittest.main()
