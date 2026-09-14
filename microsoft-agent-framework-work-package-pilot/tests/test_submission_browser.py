"""Rendered GUI, API restart and second browser session against the central store."""
import json
import os
import subprocess
import unittest
from pathlib import Path
from tests.test_submissions import SubmissionProcessHarness
from tests.test_control_plane_black_box import PILOT_ROOT


class SubmissionBrowserTests(SubmissionProcessHarness, unittest.TestCase):
    def test_browser_intake_and_reconnect_show_the_persisted_provider_content(self):
        self.provider.issues['401'] = {
            'id': 7401, 'number': 401, 'title': 'Retain the provider issue',
            'body': 'Provider content <script>alert(1)</script>\nToken: wpcp-controlled-token-canary-v1',
            'html_url': 'https://github.com/pilot/fixture/issues/401',
            'updated_at': '2026-09-14T08:00:00Z', 'state': 'open',
            'labels': [{'name': 'ready-for-agent'}],
        }
        evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
        evidence.mkdir(parents=True, exist_ok=True)
        browser_input = {'credential': self.provider.tokens['actor-authorized'],
            'sourceUrl': 'https://github.com/pilot/fixture/issues/401', 'repository': 'pilot/fixture',
            'title': 'Retain the provider issue',
            'body': 'Provider content <script>alert(1)</script>\nToken: [REDACTED:CONTROLLED-CANARY]'}
        first = self.browser({**browser_input, 'baseUrl': self.base_url, 'admit': True,
            'screenshot': str(evidence / 'controlled-desktop.png'),
            'mobileScreenshot': str(evidence / 'controlled-mobile.png')})
        self.provider.issues['401']['body'] = 'Edited after admission'
        self.stop_process(self.api)
        self.start_api()
        second = self.browser({**browser_input, 'baseUrl': self.base_url, 'admit': False,
            'expectedSnapshot': first['snapshot']})
        self.assertEqual(first, second)
        # Persistence hygiene is supplementary to the public behavior assertions above.
        dump = subprocess.run(['docker', 'exec', self.postgres_name, 'pg_dump', '-U', 'wpcp_test', 'wpcp_test'],
            text=True, capture_output=True, check=True).stdout
        self.assertNotIn('wpcp-controlled-token-canary-v1', dump)
        self.assertNotIn(self.provider.tokens['actor-authorized'], dump)
        if os.environ.get('WPCP_SUBMISSION_PROOF_DIR'):
            (evidence / 'controlled-browser.json').write_text(json.dumps(first, indent=2))

    @staticmethod
    def browser(payload):
        result = subprocess.run(['node', str(PILOT_ROOT / 'tests/submission_browser.cjs')],
            input=json.dumps(payload), text=True, capture_output=True, timeout=90)
        if result.returncode:
            raise AssertionError('Browser proof failed: ' + result.stderr)
        return json.loads(result.stdout)
