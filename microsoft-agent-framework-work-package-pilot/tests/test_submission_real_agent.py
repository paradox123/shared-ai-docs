"""Opt-in public HTTP test of the pinned real Codex analysis adapter."""
import http.client
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from tests.test_control_plane_black_box import PILOT_ROOT, free_port, ControlPlaneProcessHarness


@unittest.skipUnless(os.environ.get('WPCP_CODEX_ENDPOINT_PROBE') == '1', 'explicit real Codex endpoint')
class SubmissionRealAgentTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory(prefix='wpcp-real-analysis-')
        self.addCleanup(self.root.cleanup)
        self.port = free_port()
        self.token = secrets.token_urlsafe(32)
        self.log = (Path(self.root.name) / 'adapter.log').open('w+')
        self.addCleanup(self.log.close)
        self.process = subprocess.Popen([sys.executable, str(PILOT_ROOT / 'codex_adapter.py'),
            '--config', str(PILOT_ROOT / 'codex-runtime-pin.json'), '--state-root', self.root.name,
            '--api-url', 'http://127.0.0.1:1', '--port', str(self.port), '--native-port', str(free_port())],
            env={**os.environ, 'WPCP_REAL_ADAPTER_TOKEN': self.token}, start_new_session=True,
            stdout=self.log, stderr=self.log)
        self.addCleanup(ControlPlaneProcessHarness.stop_process, self.process)
        for _ in range(100):
            try:
                if self.request('GET', '/health')[0] == 200: break
            except OSError: pass
            time.sleep(.05)
        else: self.fail('Adapter did not become available')

    def request(self, method, path, payload=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=180)
        try:
            connection.request(method, path, json.dumps(payload) if payload is not None else None,
                {'Content-Type': 'application/json', 'X-Wpcp-Adapter-Token': self.token})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally: connection.close()

    def test_real_analysis_reads_actual_assignment_and_replays_same_session(self):
        status, readiness = self.request('GET', '/submission-readiness')
        self.assertEqual(200, status, readiness)
        self.assertTrue(readiness['runtimeReady'])
        submission_id, run_id, operation = (str(uuid.uuid4()) for _ in range(3))
        submission = {'submissionId': submission_id, 'title': 'Export only selected contacts',
            'body': 'The contact CSV export must include only rows selected by the human. Preserve selection across pagination. Empty selection must show a message without exporting.',
            'repository': {'repositoryId': 'repo-proof', 'fullName': 'pilot/analysis', 'providerRepositoryId': 42},
            'source': {'provider': 'github', 'providerIssueId': 55, 'issueNumber': 7, 'url': 'https://github.com/pilot/analysis/issues/7'},
            'contentSha256': 'controlled-snapshot-digest'}
        request = {'runId': run_id, 'note': json.dumps(submission)}
        status, first = self.request('PUT', '/submission-analyses/' + operation, request)
        self.assertEqual(200, status, first)
        events = first['events']
        self.assertEqual('completed', events[-1]['data']['outcome'], events[-1])
        text = json.dumps(events[-1]['data']).lower()
        self.assertIn('csv', text)
        self.assertTrue({'message', 'tool-call', 'tool-result', 'artifact', 'result'} <= {e['type'] for e in events})
        self.assertNotIn('greeting', text)
        self.assertEqual(first, self.request('PUT', '/submission-analyses/' + operation, request)[1])
        if destination := os.environ.get('WPCP_SUBMISSION_PROOF_DIR'):
            Path(destination).mkdir(parents=True, exist_ok=True)
            (Path(destination) / 'real-analysis-adapter.json').write_text(json.dumps(first, indent=2))
