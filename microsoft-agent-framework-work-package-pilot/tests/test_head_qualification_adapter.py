"""Public JSON adapter contract, including policy/result rejection under Python -O."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid
from tests.publication_fixture import PublicationFixture, probe
from tests import test_control_plane_black_box as harness


class HeadQualificationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = PublicationFixture(self.temp.name, 43)
        self.addCleanup(self.fixture.close)
        self.correlation = {'repository': self.fixture.plan['repository'], 'issueNumber': 43}
        skills = {}
        for name in ('code-review', 'codebase-design', 'domain-modeling'):
            path = Path(self.temp.name) / (name + '.md')
            path.write_text('Review the assigned axis only.')
            skills[name] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        self.fixture.plan['headQualification'] = {'verification': probe('passed'),
            'requirements': 'Greeting is Hello, Ada!', 'guidance': [], 'skills': skills}
        (self.fixture.repo / 'greeting.py').write_text(self.fixture.agent_content)
        self.intent = self.call('evidence')['intent']
        self.call('publish', intent=self.intent, allowCreate=True)

    def call(self, stage, **fields):
        request = {'stage': stage, 'plan': self.fixture.plan, 'correlation': self.correlation,
            'fixture': str(harness.FIXTURE), 'runId': str(uuid.uuid4()), **fields}
        process = subprocess.run([sys.executable, '-O', str(harness.PILOT_ROOT / 'publication_adapter.py')],
            input=json.dumps(request), text=True, capture_output=True, timeout=30)
        self.assertEqual(0, process.returncode, process.stderr)
        return json.loads(process.stdout)

    def review(self):
        return self.call('review-head', headSha=self.intent['headSha'], pullNumber=1,
            axis='requirements', operationKey=str(uuid.uuid4()), intent=self.intent)

    def test_optimized_python_still_rejects_forbidden_requirements_not_applicable(self):
        self.fixture.review_override = lambda request, result: result.update(verdict='not_applicable')
        self.assertEqual('review-invalid', self.review()['state'])

    def test_malformed_verdicts_keep_diagnostics_without_becoming_actionable(self):
        for update in ({'axis': 'architecture'}, {'headSha': 'f' * 40}, {'rationale': ''},
                       {'verdict': 'fail', 'findings': []}, {'unexpected': 'field'}):
            with self.subTest(update=update):
                self.fixture.review_override = lambda request, result: result.update(update)
                report = self.review()
                self.assertEqual('review-invalid', report['state'])
                self.assertIn('receipt', report)

    def test_changed_skill_bytes_block_before_reviewer_start(self):
        Path(self.fixture.plan['headQualification']['skills']['code-review']['path']).write_text('Changed skill')
        self.assertEqual('invalid-head-qualification-plan', self.review()['blocker'])
        self.assertEqual([], self.fixture.review_requests)
