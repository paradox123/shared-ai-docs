"""Opt-in real GitHub GUI intake; reads an existing issue without provider writes."""
import json
import os
import re
import subprocess
import unittest
from pathlib import Path
from tests.test_submissions import SubmissionProcessHarness
from tests import test_submission_browser as browser_proof



def live_configuration(url):
    match = re.fullmatch(r'https://github.com/([\w.-]+/[\w.-]+)/issues/(\d+)', url)
    if not match:
        raise ValueError('The live proof requires a GitHub issue URL')
    name, number = match.groups()
    issue = json.loads(subprocess.check_output(['gh', 'api', f'repos/{name}/issues/{number}'], text=True))
    repository = json.loads(subprocess.check_output(['gh', 'api', f'repos/{name}'], text=True))
    configuration = {
        'provider': {'repositories': [{'repositoryId': f'github-{repository["id"]}',
            'fullName': repository['full_name'], 'providerRepositoryId': repository['id']}]},
        'redactionPolicy': {'version': 'controlled-canary-v1', 'marker': '[REDACTED:CONTROLLED-CANARY]',
            'controlledCanaries': [{'value': 'wpcp-controlled-secret-canary-v1'},
                {'value': 'wpcp-controlled-token-canary-v1'}]},
    }
    return issue, configuration

@unittest.skipUnless(os.environ.get('WPCP_LIVE_GITHUB_SUBMISSION_URL'), 'Set an eligible GitHub issue URL for live intake')
class LiveGitHubSubmissionTests(SubmissionProcessHarness, unittest.TestCase):
    live_github = True

    @classmethod
    def setUpClass(cls):
        cls.live_issue, cls.deployment_configuration = live_configuration(os.environ['WPCP_LIVE_GITHUB_SUBMISSION_URL'])
        super().setUpClass()

    def test_real_issue_admitted_in_browser_and_read_after_service_restart(self):
        credential = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
        evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
        evidence.mkdir(parents=True, exist_ok=True)
        payload = {'credential': credential, 'sourceUrl': self.live_issue['html_url'],
            'title': self.live_issue['title'], 'body': self.live_issue['body'] or '',
            'repository': self.deployment_configuration['provider']['repositories'][0]['fullName']}
        first = browser_proof.SubmissionBrowserTests.browser({**payload, 'baseUrl': self.base_url, 'admit': True,
            'screenshot': str(evidence / 'live-github-desktop.png'),
            'mobileScreenshot': str(evidence / 'live-github-mobile.png')})
        self.assertEqual(self.live_issue['id'], first['snapshot']['source']['providerIssueId'])
        self.stop_process(self.api)
        self.start_api()
        second = browser_proof.SubmissionBrowserTests.browser({**payload, 'baseUrl': self.base_url, 'admit': False,
            'expectedSnapshot': first['snapshot']})
        self.assertEqual(first, second)
        if os.environ.get('WPCP_SUBMISSION_PROOF_DIR'):
            (evidence / 'live-github-browser.json').write_text(json.dumps({
                **first, 'newBrowserAndRestartReadbackIdentical': True,
                'topology': 'Separate processes on one macOS host; not a separate-machine acceptance proof',
                'sourceProvider': 'https://api.github.com', 'providerWrites': False,
            }, indent=2))
