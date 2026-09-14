"""Real GitHub GUI start and real Codex processing, with no GitHub writes."""
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import time
import unittest
from tests.test_submissions import SubmissionProcessHarness
from tests.test_submission_execution import SubmissionExecutionHarness
from tests.test_submission_execution_browser import browser
from tests.test_submission_live_github import live_configuration
from tests.test_control_plane_black_box import PILOT_ROOT, WORKER_DLL, free_port


@unittest.skipUnless(os.environ.get('WPCP_CODEX_ENDPOINT_PROBE') == '1' and os.environ.get('WPCP_LIVE_GITHUB_SUBMISSION_URL'),
                     'explicit real GitHub issue and Codex endpoint')
class LiveSubmissionExecutionHarness(SubmissionProcessHarness):
    live_github = True
    worker = SubmissionExecutionHarness.worker

    @classmethod
    def setUpClass(cls):
        # Reuse the intake proof's live binding and source discovery, not its test cases.
        cls.live_issue, cls.deployment_configuration = live_configuration(os.environ['WPCP_LIVE_GITHUB_SUBMISSION_URL'])
        super().setUpClass()
        cls.provider.tokens['live-human'] = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()

    @classmethod
    def start_api(cls, **kwargs):
        if not hasattr(cls, 'adapter_port'):
            cls.adapter_port = free_port()
            cls.service_environment = {'WPCP_REAL_ADAPTER_TOKEN': secrets.token_urlsafe(32)}
        cls.deployment_configuration['backgroundExecution'] = {
            'adapterOrigin': f'http://127.0.0.1:{cls.adapter_port}/', 'timeoutSeconds': 180}
        cls.service_environment.setdefault('WPCP_ARTIFACT_ROOT', str(Path(cls.scratch.name) / 'artifacts'))
        super().start_api(**kwargs)

    def start_adapter(self):
        log = (Path(self.scratch.name) / 'analysis-adapter.log').open('w+')
        self.addCleanup(log.close)
        process = subprocess.Popen([sys.executable, str(PILOT_ROOT / 'codex_adapter.py'),
            '--config', str(PILOT_ROOT / 'codex-runtime-pin.json'),
            '--state-root', str(Path(self.scratch.name) / 'analysis-state'), '--api-url', self.base_url,
            '--port', str(self.adapter_port), '--native-port', str(free_port())],
            env={**os.environ, **self.service_environment}, start_new_session=True, stdout=log, stderr=log)
        self.addCleanup(self.stop_process, process)
        for _ in range(100):
            if self.request('GET', '/health', port=self.adapter_port)[0] == 200: return process
            time.sleep(.05)
        self.fail('Real adapter unavailable')

    def detached_worker(self):
        command = ['dotnet', str(WORKER_DLL), '--submission-config',
            str(Path(self.scratch.name) / 'submission-config.json'), '--dispatch-submissions', 'true']
        launcher = subprocess.run([sys.executable, '-c',
            'import json,subprocess,sys; p=subprocess.Popen(json.load(sys.stdin), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True); print(p.pid)'],
            input=json.dumps(command), text=True, capture_output=True, check=True, cwd=PILOT_ROOT,
            env={**os.environ, **self.service_environment, 'WPCP_CONNECTION_STRING': self.connection_string})
        pid = int(launcher.stdout)
        self.addCleanup(self.stop_detached_worker, pid)
        self.assertEqual('1', subprocess.check_output(['ps', '-o', 'ppid=', '-p', str(pid)], text=True).strip())
        return pid

    @staticmethod
    def stop_detached_worker(pid):
        observed = subprocess.run(['ps', '-o', 'command=', '-p', str(pid)], capture_output=True, text=True).stdout
        if 'Wpcp.Worker.dll' in observed:
            try: os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError: pass


class LiveSubmissionExecutionTests(LiveSubmissionExecutionHarness, unittest.TestCase):
    def test_gui_background_analysis_and_artifact_survive_closed_browser_and_api(self):
        self.start_adapter()
        payload = {'baseUrl': self.base_url, 'credential': subprocess.check_output(['gh', 'auth', 'token'], text=True).strip(),
            'sourceUrl': self.live_issue['html_url']}
        first = browser({**payload, 'mode': 'start'})
        # The real GUI process has exited. Stop the API before dispatching the worker.
        self.stop_process(self.api)
        worker = self.detached_worker()
        time.sleep(2)
        self.start_api()
        # Real model latency is bounded by the worker, independent of the browser.
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            status, state, raw = self.request('GET', f'/api/v1/submissions/{first["submissionId"]}/execution',
                actor_id='live-human', include_fixture_access=False)
            self.assertEqual(200, status, raw)
            if state['state'] in ('completed', 'failed'): break
            time.sleep(.5)
        run_path = '/api/v1/runs/' + first['runId']
        _, run, _ = self.request('GET', run_path, actor_id='live-human', include_fixture_access=False)
        _, events, _ = self.request('GET', run_path + '/events', actor_id='live-human', include_fixture_access=False)
        _, artifacts, _ = self.request('GET', run_path + '/artifacts', actor_id='live-human', include_fixture_access=False)
        if state['state'] != 'completed':
            evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
            evidence.mkdir(parents=True, exist_ok=True)
            (evidence / 'live-execution-failure-debug.json').write_text(json.dumps({'state': state, 'run': run, 'events': events, 'artifacts': artifacts}, indent=2))
        self.assertEqual('completed', state['state'], state)
        self.assertTrue(artifacts['artifacts'], artifacts)
        self.assertTrue(all(a['availability'] == 'available' for a in artifacts['artifacts']), artifacts)
        session = next(a['session'] for a in run['attempts'] if a.get('session'))
        self.assertEqual('completed', session['originalResult']['outcome'])
        self.assertTrue(session['sessionId'])
        types = {e['payload'].get('type') for e in events['events']}
        self.assertTrue({'message', 'tool-call', 'tool-result', 'artifact'} <= types, types)
        evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
        evidence.mkdir(parents=True, exist_ok=True)
        second = browser({**payload, **first, 'baseUrl': self.base_url, 'mode': 'read',
            'expectedState': 'Analyse abgeschlossen', 'screenshot': str(evidence / 'live-execution-desktop.png'),
            'mobileScreenshot': str(evidence / 'live-execution-mobile.png')})
        self.assertEqual(first['runId'], second['runId'])
        self.stop_detached_worker(worker)
        (evidence / 'live-execution.json').write_text(json.dumps({
            'guiStart': first, 'guiReadback': second, 'run': run, 'events': events, 'artifacts': artifacts,
            'browserClosedBeforeExecution': True, 'apiStoppedBeforeWorkerStarted': True, 'workerLauncherExited': True, 'workerParentPid': 1,
            'providerWrites': False, 'topology': 'Independent local processes; distributed acceptance remains Ticket 16'}, indent=2))


class LiveSubmissionFailureTests(LiveSubmissionExecutionHarness, unittest.TestCase):
    def test_gui_recovers_controlled_adapter_failure_after_browser_is_closed(self):
        adapter = self.start_adapter()
        payload = {'baseUrl': self.base_url, 'credential': self.provider.tokens['live-human'],
            'sourceUrl': self.live_issue['html_url']}
        first = browser({**payload, 'mode': 'start'})
        # Readiness passed at admission. Simulate the service disappearing before delivery.
        self.stop_process(adapter)
        worker = self.detached_worker()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            status, state, raw = self.request('GET', '/api/v1/submissions/' + first['submissionId'] + '/execution',
                actor_id='live-human', include_fixture_access=False)
            self.assertEqual(200, status, raw)
            if state['state'] == 'failed': break
            time.sleep(.2)
        self.assertEqual('failed', state['state'], state)
        self.assertEqual('transport-failure', state['code'])
        self.stop_detached_worker(worker)
        self.stop_process(self.api)
        self.start_api()
        evidence = Path(os.environ.get('WPCP_SUBMISSION_PROOF_DIR', self.scratch.name))
        evidence.mkdir(parents=True, exist_ok=True)
        second = browser({**payload, **first, 'baseUrl': self.base_url, 'mode': 'read',
            'expectedState': 'Fehlgeschlagen', 'summary': 'transport-failure',
            'screenshot': str(evidence / 'live-execution-failed.png')})
        self.assertEqual(first['runId'], second['runId'])
        (evidence / 'live-execution-failed.json').write_text(json.dumps({
            'start': first, 'readback': second, 'state': state,
            'fault': 'Stopped the real adapter after successful preflight, before worker delivery',
            'browserClosed': True, 'apiRestarted': True, 'workerLauncherExited': True}, indent=2))
