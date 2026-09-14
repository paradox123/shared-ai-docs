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
    def test_recorded_runtime_failure_and_terminal_output_are_visible(self):
        self.analysis.extra_events = [
            {'type': 'message', 'data': {'runtimeEvent': {'method': 'error',
                'params': {'error': {'message': 'Upstream model quota exhausted'}}}}},
            {'type': 'tool-result', 'data': {'runtimeEvent': {'method': 'item/completed', 'params': {'item': {
                'id': 'command-1', 'type': 'commandExecution', 'command': 'git status --short',
                'aggregatedOutput': 'fatal: cannot open repository', 'exitCode': 128, 'durationMs': 42, 'status': 'completed'}}}}},
        ]
        self.addCleanup(setattr, self.analysis, 'extra_events', [])
        self.worker()
        workflow_browser({'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'observer': self.provider.tokens['actor-observer'], 'sourceUrl': self.issue(709), 'runtimeFailure': True})

    def test_unrecognized_json_messages_do_not_break_readable_history(self):
        self.analysis.extra_events = [{'type': 'message', 'data': {'role': 'assistant', 'text': text}} for text in (
            '{"content":[null]}', '{"contractVersion":"example/v1","events":[null]}',
            'Der Verlauf bleibt lesbar.')]
        self.addCleanup(setattr, self.analysis, 'extra_events', [])
        self.worker()
        workflow_browser({'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'observer': self.provider.tokens['actor-observer'], 'sourceUrl': self.issue(708), 'unknownShapes': True})

    def test_native_tool_failure_is_readable_and_protocol_duplicates_stay_in_full_history(self):
        item = {'id': 'recorded-tool-1', 'type': 'mcpToolCall', 'tool': 'execute',
            'arguments': {'command': ['git', 'status', '--short']}, 'status': 'failed',
            'error': {'message': 'Berechtigung fehlt'}, 'durationMs': 42,
            'result': {'content': [{'type': 'text', 'text': '<img src=x onerror="window.untrustedRan=true">'}]}}
        self.analysis.extra_events = [
            {'type': 'message', 'data': {'role': 'user', 'text': 'Prüfe den Arbeitsstand.'}},
            {'type': 'message', 'data': {'runtimeEvent': {'method': 'item/completed', 'params': {
                'item': {'id': 'user-1', 'type': 'userMessage', 'content': [{'type': 'text', 'text': 'Prüfe den Arbeitsstand.'}]}}}}},
            {'type': 'message', 'data': {'runtimeEvent': {'method': 'turn/started', 'params': {}}}},
            {'type': 'tool-result', 'data': {'runtimeEvent': {'method': 'item/completed', 'params': {'item': item}}}},
        ]
        self.addCleanup(setattr, self.analysis, 'extra_events', [])
        self.worker()
        workflow_browser({'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'observer': self.provider.tokens['actor-observer'], 'sourceUrl': self.issue(707), 'nativeTools': True})

    def test_session_presents_messages_and_findings_without_raw_envelopes(self):
        self.analysis.extra_events = [{'type': 'message', 'data': {'role': 'assistant',
            'text': 'Ich prüfe die freigegebenen Anforderungen.'}}]
        self.addCleanup(setattr, self.analysis, 'extra_events', [])
        self.worker()
        workflow_browser({'baseUrl': self.base_url, 'credential': self.provider.tokens['actor-authorized'],
            'observer': self.provider.tokens['actor-observer'], 'sourceUrl': self.issue(706), 'readable': True})

    def test_live_history_reconnects_after_api_restart_and_clears_after_revocation(self):
        self.check_recovery()

    def test_page_catchup_retries_failed_projection_even_without_later_events(self):
        self.check_recovery(catchup=True)

    def check_recovery(self, catchup=False):
        self.analysis.release.clear()
        self.analysis.extra_events = [{'type': 'message', 'data': {'role': 'assistant',
            'text': 'Document the literal event: access-revoked without changing access.'}}]
        self.addCleanup(setattr, self.analysis, 'extra_events', [])
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
            'sourceUrl': self.issue(705 if catchup else 703), 'catchup': catchup})
        first = receive()
        self.assertEqual('projection-held' if catchup else 'watching', first['stage'])
        cls = type(self)
        if catchup:
            self.analysis.release.set()
        else:
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
