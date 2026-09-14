"""Observe a GUI-started run through the public browser/history seam."""
import json
import subprocess
import os
import select
import time
import unittest
from pathlib import Path
from tests.test_submission_execution import SubmissionExecutionHarness
from tests.test_control_plane_black_box import PILOT_ROOT


def workflow_browser(payload):
    result = subprocess.run(['node', str(PILOT_ROOT / 'tests/workflow_browser.cjs')],
        input=json.dumps(payload), text=True, capture_output=True, timeout=240 if payload.get('live') else 90)
    if result.returncode:
        raise AssertionError('Workflow browser proof failed: ' + result.stderr)
    return json.loads(result.stdout)


class WorkflowBrowserTests(SubmissionExecutionHarness, unittest.TestCase):
    def test_live_history_reconnects_after_api_restart_and_clears_after_revocation(self):
        self.analysis.release.clear()
        self.addCleanup(self.analysis.release.set)
        process = subprocess.Popen(['node', str(PILOT_ROOT / 'tests/workflow_reconnect_browser.cjs')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        self.addCleanup(self.stop_process, process)
        for pipe in (process.stdin, process.stdout, process.stderr): self.addCleanup(pipe.close)
        def send(payload):
            process.stdin.write(json.dumps(payload) + '\n'); process.stdin.flush()
        def receive():
            ready, _, _ = select.select([process.stdout], [], [], 40)
            self.assertTrue(ready, 'Browser did not reach the next stage')
            line = process.stdout.readline()
            if not line: self.fail(process.stderr.read())
            return json.loads(line)
        self.worker()
        send({'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'sourceUrl': self.issue(703)})
        first = receive()
        self.assertEqual('watching', first['stage'])
        cls = type(self)
        self.stop_process(cls.api)
        self.analysis.release.set()
        # Replace the API process at the same public address while Chrome stays open.
        environment = {**os.environ, **self.service_environment, 'WPCP_CONNECTION_STRING': self.connection_string,
            'WPCP_GITHUB_TEST_ORIGIN': self.provider.origin}
        environment.pop('WPCP_FIXTURE_ACCESS_TOKEN', None)
        cls.api = subprocess.Popen(cls.api.args, cwd=PILOT_ROOT, env=environment,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        for _ in range(100):
            if self.request('GET', '/healthz')[0] == 200: break
            time.sleep(.1)
        self.await_state(first['submissionId'], 'completed')
        send({'continue': True})
        resumed = receive()
        self.assertEqual('reconnected', resumed['stage'])
        self.provider.identities['actor-authorized']['read'] = False
        self.provider.identities['actor-authorized']['push'] = False
        self.addCleanup(self.provider.identities['actor-authorized'].__setitem__, 'read', True)
        self.addCleanup(self.provider.identities['actor-authorized'].__setitem__, 'push', True)
        send({'continue': True})
        self.assertEqual({'stage': 'revoked', 'cleared': True}, receive())
        self.assertEqual(0, process.wait(timeout=10), process.stderr.read())

    def test_paged_history_and_artifact_bytes_are_complete_in_both_clients(self):
        self.analysis.result_padding = 1200
        self.analysis.extra_events = [{'type': 'message', 'data': {'role': 'assistant',
            'text': f'Observed finding {index:03d}'}} for index in range(205)]
        self.addCleanup(setattr, self.analysis, 'result_padding', 0)
        self.addCleanup(setattr, self.analysis, 'extra_events', [])
        self.worker()
        result = workflow_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'],
            'observer': self.provider.tokens['actor-observer'], 'sourceUrl': self.issue(702), 'artifacts': True, 'paged': True})
        self.assertEqual(result['first'], result['second'])
        self.assertGreater(result['first']['events'], 205)

    def test_missing_artifact_remains_explicit_without_source_link_fallback(self):
        self.analysis.result_padding = 1200
        self.addCleanup(setattr, self.analysis, 'result_padding', 0)
        self.worker()
        payload = {'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'observer': self.provider.tokens['actor-observer'], 'sourceUrl': self.issue(704), 'artifacts': True}
        result = workflow_browser(payload)
        run_id = result['first']['runId']
        _, manifest, _ = self.request('GET', f'/api/v1/runs/{run_id}/artifacts', include_fixture_access=False)
        # Fault injection only: normal creation and every verification use public surfaces.
        for artifact in manifest['artifacts']:
            (Path(self.service_environment['WPCP_ARTIFACT_ROOT']) / artifact['sha256']).unlink(missing_ok=True)
        _, records, _ = self.request('GET', '/api/v1/submissions', include_fixture_access=False)
        record = next(s for s in records['submissions'] if s['runId'] == run_id)
        reopened = workflow_browser({**payload, 'submissionId': record['submissionId']})
        self.assertEqual(result, reopened)

    def test_gui_started_run_exposes_correlated_session_history_to_second_client(self):
        self.worker()
        result = workflow_browser({'baseUrl': self.base_url,
            'credential': self.provider.tokens['actor-authorized'],
            'observer': self.provider.tokens['actor-observer'], 'sourceUrl': self.issue(701)})
        self.assertEqual(result['first'], result['second'])
        self.assertGreater(result['first']['events'], 3)
