import json
import os
from pathlib import Path
import subprocess
import unittest
from tests.test_submission_execution import SubmissionExecutionHarness
from tests.test_control_plane_black_box import PILOT_ROOT


def browser(payload):
    result = subprocess.run(['node', str(PILOT_ROOT / 'tests/submission_execution_browser.cjs')],
        input=json.dumps(payload), text=True, capture_output=True, timeout=210)
    if result.returncode: raise AssertionError('Browser proof failed: ' + result.stderr)
    return json.loads(result.stdout)


class SubmissionExecutionBrowserTests(SubmissionExecutionHarness, unittest.TestCase):
    def test_start_close_browser_and_reopen_real_persisted_result_view(self):
        self.analysis.release.clear()
        self.addCleanup(self.analysis.release.set)
        worker = self.worker()
        payload = {'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'sourceUrl': self.issue(601)}
        first = browser({**payload, 'mode': 'start'})
        self.analysis.release.set()
        self.await_state(first['submissionId'], 'completed')
        self.stop_process(worker)
        self.stop_process(self.api)
        self.start_api()
        evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
        evidence.mkdir(parents=True, exist_ok=True)
        second = browser({**payload, **first, 'baseUrl': self.base_url, 'mode': 'read',
            'expectedState': 'Analyse abgeschlossen', 'summary': 'Requirements analysis complete.',
            'screenshot': str(evidence / 'execution-completed-desktop.png'),
            'mobileScreenshot': str(evidence / 'execution-completed-mobile.png')})
        self.assertEqual(first['runId'], second['runId'])

    def test_saved_issue_start_reads_large_result_through_the_artifact_boundary(self):
        self.analysis.result_padding = 1200
        self.addCleanup(setattr, self.analysis, 'result_padding', 0)
        self.worker()
        _, submission, _ = self.post('', {'sourceUrl': self.issue(602)})
        result = browser({'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'submissionId': submission['submissionId'], 'mode': 'start-saved',
            'expectedState': 'Analyse abgeschlossen', 'summary': 'End of analysis.'})
        self.assertIn('End of analysis.', result['result'])
