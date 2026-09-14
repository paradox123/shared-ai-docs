"""Opt-in real issue → real analysis → two authenticated production browsers."""
import json
import hashlib
import urllib.request
import os
from pathlib import Path
import unittest
from tests.test_submission_execution_live import LiveSubmissionExecutionHarness
from tests.test_workflow_browser import workflow_browser


class LiveWorkflowTests(LiveSubmissionExecutionHarness, unittest.TestCase):
    def test_real_issue_workflow_matches_public_history_and_artifacts_after_restart(self):
        self.start_adapter()
        worker = self.detached_worker()
        evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
        evidence.mkdir(parents=True, exist_ok=True)
        payload = {'baseUrl': self.base_url, 'credential': self.provider.tokens['live-human'],
            'observer': self.provider.tokens['live-human'], 'sourceUrl': self.live_issue['html_url'],
            'live': True, 'artifacts': True,
            'screenshot': str(evidence / 'live-workflow-desktop.png'),
            'mobileScreenshot': str(evidence / 'live-workflow-mobile.png')}
        observed = workflow_browser(payload)
        self.assertEqual(observed['first'], observed['second'])
        run_id = observed['first']['runId']
        public = {}
        for name, path in [('run', ''), ('history', '/events?limit=1000'), ('artifacts', '/artifacts')]:
            status, body, _ = self.request('GET', '/api/v1/runs/' + run_id + path,
                actor_id='live-human', include_fixture_access=False)
            self.assertEqual(200, status)
            public[name] = body
        for artifact in public['artifacts']['artifacts']:
            self.assertEqual('available', artifact['availability'])
            request = urllib.request.Request(self.base_url + '/api/v1/runs/' + run_id + '/artifacts/' + artifact['artifactId'],
                headers={'Authorization': 'Bearer ' + self.provider.tokens['live-human']})
            with urllib.request.urlopen(request, timeout=15) as response:
                content = response.read()
            self.assertEqual(artifact['sha256'], hashlib.sha256(content).hexdigest())
            (evidence / ('live-artifact-' + artifact['artifactId'] + '.json')).write_bytes(content)
        self.stop_detached_worker(worker)
        self.stop_process(self.api)
        self.start_api()
        _, records, _ = self.request('GET', '/api/v1/submissions', actor_id='live-human', include_fixture_access=False)
        record = next(s for s in records['submissions'] if s['runId'] == run_id)
        reopened = workflow_browser({**payload, 'baseUrl': self.base_url, 'submissionId': record['submissionId']})
        self.assertEqual(observed, reopened)
        (evidence / 'live-workflow.json').write_text(json.dumps({
            'sourceUrl': self.live_issue['html_url'], 'browsers': observed, 'afterApiRestart': reopened,
            **public, 'providerWrites': False,
            'topology': 'Independent browser contexts/API/worker processes on one Mac; no original-client files or database access from browsers.'}, indent=2) + '\n')
