"""Opt-in real pinned Codex qualification against a controlled GitHub provider."""
import hashlib
import os
from pathlib import Path
import unittest
import sys
from tests import test_control_plane_black_box as harness
from tests import test_publication_native as native
from tests.qualification_proof import record


@unittest.skipUnless(os.environ.get('WPCP_CODEX_ENDPOINT_PROBE') == '1', 'explicit real Codex endpoint')
class NativeHeadQualificationTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    start_real = native.NativePublicationTests.start_real
    open_and_claim = native.NativePublicationTests.open_and_claim
    run_native_ui = native.NativePublicationTests.run_native_ui
    run_native_publication = native.NativePublicationTests.run_native_publication

    def publish(self, run_id, path):
        return harness.command_output(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'native-qualification', '--codex-python', sys.executable,
            '--publication-plan', str(path)], timeout=600)

    def configuration(self):
        skills = {}
        for name in ('code-review', 'codebase-design', 'domain-modeling'):
            path = harness.PILOT_ROOT.parent / 'skills-repo' / 'skills' / name / 'SKILL.md'
            skills[name] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        return {'skills': skills, 'guidance': ['ISSUE.md'],
            'requirements': 'Fix greet() to return exactly Hello, Ada! Change greeting.py only.',
            'verification': {'argv': [sys.executable, '-B', '-c',
                'from greeting import greet; assert greet() == "Hello, Ada!"; print("checks passed")'],
                'expected': 'checks passed'}}

    def test_real_three_session_review_qualifies_the_evidence_head(self):
        run, fixture = self.run_native_publication(self.configuration())
        record(self._testMethodName, run, fixture, 'real pinned Codex and native writer session')
        q = run['publication']['headQualification']
        reviews = q['rounds'][-1]['reviews']
        self.assertEqual(3, len({r['report']['sessionId'] for r in reviews}))
        self.assertEqual(fixture.pulls[0]['head']['sha'], q['qualifiedHeadSha'])
        self.assertTrue(fixture.pulls[0]['draft'])

    def test_real_writer_repairs_review_findings_in_original_session(self):
        configuration = self.configuration()
        configuration['requirements'] += ' Additionally greeting.py must start with the module docstring "Canonical greeting.".'
        run, fixture = self.run_native_publication(configuration,
            'Controlled incomplete first pass: omit the requested module docstring for now; '
            'the subsequent qualification review must detect it and the repair phase will add it.')
        record(self._testMethodName, run, fixture, 'real pinned Codex and same-session writer repair')
        q = run['publication']['headQualification']
        self.assertGreaterEqual(len(q['repairs']), 1)
        self.assertLessEqual(len(q['repairs']), 3)
        writer = run['publication']['qualification']['source']['sessionId']
        self.assertTrue(all(r['report']['sessionId'] == writer for r in q['repairs']))
        self.assertNotEqual(q['rounds'][0]['headSha'], q['qualifiedHeadSha'])
        self.assertEqual(1, fixture.creates)
