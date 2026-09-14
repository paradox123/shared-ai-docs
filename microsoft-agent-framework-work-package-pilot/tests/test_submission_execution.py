"""Durable GUI start through HTTP, independent workers and central history."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import os
import subprocess
import threading
import time
import unittest
import uuid
from tests.test_submissions import SubmissionProcessHarness
from tests.test_control_plane_black_box import WORKER_DLL, PILOT_ROOT


class AnalysisProvider:
    """Controlled external agent boundary; never substitutes for the live proof."""
    def __init__(self):
        owner = self
        self.requests = {}
        self.started = threading.Event()
        self.ready = True
        self.failure = None
        self.result_padding = 0
        self.release = threading.Event()
        self.release.set()

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def do_GET(self):
                data = json.dumps({'contractVersion': 'AgentSessionAdapter/v1',
                    'step': 'submission-analysis/v1', 'runtimeReady': owner.ready,
                    'sandboxReady': owner.ready}).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                try: self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError): pass

            def do_PUT(self):
                request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                operation = self.path.rsplit('/', 1)[-1]
                owner.started.set()
                owner.release.wait(20)
                if operation not in owner.requests:
                    assignment = json.loads(request['note'])
                    owner.requests[operation] = {'contractVersion': 'AgentSessionAdapter/v1',
                        'operationKey': operation, 'sessionId': str(uuid.uuid4()), 'events': [
                            {'sequence': 1, 'type': 'message', 'data': {'assignment': assignment}},
                            {'sequence': 2, 'type': 'tool-call', 'data': {'tool': 'read-admitted-issue'}},
                            {'sequence': 3, 'type': 'tool-result', 'data': {'body': assignment['body']}},
                            {'sequence': 4, 'type': 'result', 'data': {
                                'schemaVersion': 'submission-analysis/v1', 'outcome': 'completed',
                                'summary': 'Requirements analysis complete.' + (' Detailed criterion.' * owner.result_padding + ' End of analysis.' if owner.result_padding else ''), 'findings': ['Preserve the approved requirements.']}}]}
                response = owner.requests[operation]
                if owner.failure:
                    response = {**response, 'events': response['events'][:3] + [
                        {'sequence': 4, 'type': 'process-exit', 'data': {'exitCode': 17}}]}
                data = json.dumps(response).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                try: self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError): pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.origin = f'http://127.0.0.1:{self.server.server_port}/'

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()


class SubmissionExecutionHarness(SubmissionProcessHarness):
    @classmethod
    def setUpClass(cls):
        cls.analysis = AnalysisProvider()
        cls.service_environment = {'WPCP_REAL_ADAPTER_TOKEN': 'controlled-analysis-service-token'}
        cls.addClassCleanup(cls.analysis.close)
        super().setUpClass()

    @classmethod
    def start_api(cls, **kwargs):
        if not hasattr(cls, 'fixture_path'):
            return super().start_api(**kwargs)
        cls.deployment_configuration = json.loads(cls.fixture_path.read_text())
        cls.deployment_configuration['backgroundExecution'] = {
            'adapterOrigin': cls.analysis.origin, 'timeoutSeconds': 180}
        cls.service_environment.setdefault('WPCP_ARTIFACT_ROOT', str(Path(cls.scratch.name) / 'artifacts'))
        super().start_api(**kwargs)

    def issue(self, number):
        self.provider.issues[str(number)] = {
            'id': 8000 + number, 'number': number, 'title': f'Analyze issue {number}',
            'body': 'Preserve the approved requirements. wpcp-controlled-secret-canary-v1',
            'html_url': f'https://github.com/pilot/fixture/issues/{number}',
            'updated_at': '2026-09-14T08:00:00Z', 'state': 'open',
            'labels': [{'name': 'ready-for-agent'}]}
        return self.provider.issues[str(number)]['html_url']

    def post(self, path, body=None, actor='actor-authorized'):
        return self.request('POST', '/api/v1/submissions' + path, body or {},
            actor_id=actor, include_fixture_access=False)

    def worker(self):
        process = subprocess.Popen(['dotnet', str(WORKER_DLL), '--submission-config',
            str(self.scratch.name + '/submission-config.json'), '--dispatch-submissions', 'true'],
            cwd=PILOT_ROOT, env={**os.environ, **self.service_environment,
                'WPCP_CONNECTION_STRING': self.connection_string}, start_new_session=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(self.stop_process, process)
        return process

    def execution(self, submission_id):
        status, body, raw = self.request('GET', f'/api/v1/submissions/{submission_id}/execution',
            include_fixture_access=False)
        self.assertEqual(200, status, raw)
        return body

    def await_state(self, submission_id, expected):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            state = self.execution(submission_id)
            if state['state'] == expected: return state
            time.sleep(.1)
        self.fail(f'Expected {expected}; retained state: {state}')


class SubmissionExecutionTests(SubmissionExecutionHarness, unittest.TestCase):
    def test_new_issue_executes_with_clients_closed_and_keeps_session_history(self):
        self.analysis.release.clear()
        self.addCleanup(self.analysis.release.set)
        status, submission, raw = self.post('', {'sourceUrl': self.issue(502), 'start': True})
        self.assertEqual(202, status, raw)
        worker = self.worker()
        self.await_state(submission['submissionId'], 'running')
        self.stop_process(self.api)
        self.analysis.release.set()
        time.sleep(.5)
        self.start_api()
        state = self.await_state(submission['submissionId'], 'completed')
        status, run, raw = self.request('GET', '/api/v1/runs/' + state['runId'], include_fixture_access=False)
        self.assertEqual(200, status, raw)
        sessions = [a['session'] for a in run['attempts'] if a.get('session')]
        self.assertEqual(1, len(sessions))
        self.assertEqual('Requirements analysis complete.', sessions[0]['originalResult']['summary'])
        session_id = sessions[0]['sessionId']
        status, history, raw = self.request('GET', '/api/v1/runs/' + state['runId'] + '/events', include_fixture_access=False)
        self.assertEqual(200, status, raw)
        observations = [e for e in history['events'] if e['eventType'] == 'AgentObservationReceived']
        self.assertEqual({'message', 'tool-call', 'tool-result'}, {e['payload']['type'] for e in observations})
        self.assertTrue(all(e['payload']['sessionId'] == session_id for e in observations))
        self.assertNotIn('wpcp-controlled-secret-canary-v1', raw)
        self.stop_process(worker)
        replacement = self.worker()
        self.assertEqual(200, self.post('/' + submission['submissionId'] + '/start')[0])
        self.assertEqual(state['runId'], self.execution(submission['submissionId'])['runId'])
        self.stop_process(replacement)

    def test_saved_issue_starts_once_and_retains_durable_run_after_restart(self):
        status, admitted, raw = self.post('', {'sourceUrl': self.issue(501)})
        self.assertEqual(201, status, raw)
        path = '/' + admitted['submissionId']
        with ThreadPoolExecutor(max_workers=6) as clients:
            results = list(clients.map(lambda _: self.post(path + '/start'), range(8)))
        self.assertEqual({200, 202}, {status for status, _, _ in results}, results)
        self.assertEqual(1, sum(status == 202 for status, _, _ in results))
        run_ids = {body['runId'] for _, body, _ in results}
        self.assertEqual(1, len(run_ids))
        self.assertNotIn(None, run_ids)
        self.stop_process(self.api)
        self.start_api()
        status, read, raw = self.request('GET', '/api/v1/submissions' + path,
            include_fixture_access=False)
        self.assertEqual(200, status, raw)
        self.assertEqual(run_ids, {read['runId']})
        self.assertEqual(admitted['body'], read['body'])
        self.assertEqual(admitted['contentSha256'], read['contentSha256'])
        status, execution, raw = self.request('GET', '/api/v1/submissions' + path + '/execution',
            include_fixture_access=False)
        self.assertEqual(200, status, raw)
        self.assertEqual('queued', execution['state'])
        self.assertEqual(run_ids, {execution['runId']})
        self.assertEqual(admitted['submissionId'], execution['submissionId'])

    def test_start_revalidates_authorization_mandate_identity_and_runtime(self):
        url = self.issue(503)
        _, admitted, _ = self.post('', {'sourceUrl': url})
        path = '/' + admitted['submissionId']
        for actor, code in [('actor-observer', 'repository-contribution-required'),
                            ('actor-unauthorized', 'repository-access-denied'),
                            ('worker-bot', 'human-identity-required')]:
            status, failure, raw = self.post(path + '/start', actor=actor)
            self.assertEqual(403, status, raw)
            self.assertEqual(code, failure['code'])
        issue = self.provider.issues['503']
        issue['labels'] = []
        self.assertEqual('implementation-authorization-required', self.post(path + '/start')[1]['code'])
        issue['labels'] = [{'name': 'ready-for-agent'}]
        issue['id'] = 999999
        self.assertEqual('github-source-identity-mismatch', self.post(path + '/start')[1]['code'])
        issue['id'] = 8503
        self.analysis.ready = False
        try:
            self.assertEqual('agent-readiness-unavailable', self.post(path + '/start')[1]['code'])
        finally: self.analysis.ready = True
        _, unchanged, _ = self.request('GET', '/api/v1/submissions' + path, include_fixture_access=False)
        self.assertIsNone(unchanged['runId'])
        issue['body'] = 'A later source edit is not the admitted mandate.'
        status, started, raw = self.post(path + '/start')
        self.assertEqual(202, status, raw)
        self.assertEqual(admitted['body'], started['body'])
        self.assertEqual(admitted['contentSha256'], started['contentSha256'])

    def test_controlled_process_failure_retains_session_and_observed_tools(self):
        self.analysis.failure = 'process-failure'
        self.addCleanup(setattr, self.analysis, 'failure', None)
        status, submission, raw = self.post('', {'sourceUrl': self.issue(504), 'start': True})
        self.assertEqual(202, status, raw)
        worker = self.worker()
        state = self.await_state(submission['submissionId'], 'failed')
        self.assertEqual('process-failure', state['code'])
        status, run, raw = self.request('GET', '/api/v1/runs/' + state['runId'], include_fixture_access=False)
        self.assertEqual(200, status, raw)
        attempt = next(a for a in run['attempts'] if a.get('session'))
        self.assertIsNotNone(attempt['session']['sessionId'])
        self.assertEqual('process-failure', attempt['session']['failureCategory'])
        self.assertIsNone(attempt['session']['originalResult'])
        self.stop_process(worker)
        self.assertEqual(state, self.execution(submission['submissionId']))

    def test_url_redelivery_returns_original_run_when_runtime_is_unavailable(self):
        url = self.issue(505)
        status, submission, raw = self.post('', {'sourceUrl': url, 'start': True})
        self.assertEqual(202, status, raw)
        self.analysis.ready = False
        try:
            status, repeated, raw = self.post('', {'sourceUrl': url, 'start': True})
            self.assertEqual(200, status, raw)
            self.assertEqual(submission['runId'], repeated['runId'])
        finally: self.analysis.ready = True

    def test_replacement_worker_reconciles_external_session_after_worker_crash(self):
        self.analysis.started.clear()
        self.analysis.release.clear()
        self.addCleanup(self.analysis.release.set)
        status, submission, raw = self.post('', {'sourceUrl': self.issue(506), 'start': True})
        self.assertEqual(202, status, raw)
        first = self.worker()
        self.assertTrue(self.analysis.started.wait(10), 'Worker did not dispatch to the external adapter')
        self.stop_process(first)
        self.analysis.release.set()
        replacement = self.worker()
        state = self.await_state(submission['submissionId'], 'completed')
        status, run, raw = self.request('GET', '/api/v1/runs/' + state['runId'], include_fixture_access=False)
        self.assertEqual(200, status, raw)
        attempts = [a for a in run['attempts'] if a.get('session')]
        self.assertEqual(1, len(attempts), run)
        self.assertEqual('completed', attempts[0]['state'])
        _, events, _ = self.request('GET', '/api/v1/runs/' + state['runId'] + '/events', include_fixture_access=False)
        self.assertEqual(1, sum(e['eventType'] == 'AgentSessionStarted' for e in events['events']))
        self.assertEqual(1, sum(e['eventType'] == 'AgentResultObserved' for e in events['events']))
        self.stop_process(replacement)

    def test_unavailable_artifact_storage_rejects_start_before_creating_a_run(self):
        path = Path(self.scratch.name) / 'not-an-artifact-directory'
        path.write_text('This is a file')
        original = self.service_environment['WPCP_ARTIFACT_ROOT']
        self.service_environment['WPCP_ARTIFACT_ROOT'] = str(path)
        self.stop_process(self.api)
        self.start_api()
        try:
            status, error, raw = self.post('', {'sourceUrl': self.issue(507), 'start': True})
            self.assertEqual(503, status, raw)
            self.assertEqual('artifact-storage-unavailable', error['code'])
        finally:
            self.service_environment['WPCP_ARTIFACT_ROOT'] = original
            self.stop_process(self.api)
            self.start_api()
