import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import secrets
import uuid
from tests import test_control_plane_black_box as harness


@unittest.skipUnless(os.environ.get('WPCP_CODEX_ENDPOINT_PROBE') == '1', 'explicit real Codex endpoint')
class RealCodexAdapterTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def start_real(self):
        port, native_port = harness.free_port(), harness.free_port()
        for name, value in {'WPCP_REAL_ADAPTER_ORIGIN': f'http://127.0.0.1:{port}/',
                            'WPCP_REAL_ADAPTER_TOKEN': secrets.token_urlsafe(32)}.items():
            previous = os.environ.get(name)
            self.addCleanup(lambda n=name, old=previous: os.environ.pop(n, None) if old is None else os.environ.__setitem__(n, old))
            os.environ[name] = value
        type(self).stop_process(type(self).api)
        type(self).start_api()
        root = Path(self.scratch.name) / ('adapter-' + str(port))
        self.adapter_log = (Path(self.scratch.name) / ('adapter-' + str(port) + '.log')).open('w+')
        self.addCleanup(self.adapter_log.close)
        process = subprocess.Popen([sys.executable, str(harness.PILOT_ROOT / 'codex_adapter.py'),
            '--config', str(harness.PILOT_ROOT / 'codex-runtime-pin.json'), '--state-root', str(root),
            '--api-url', self.base_url, '--port', str(port), '--native-port', str(native_port)],
            stdout=self.adapter_log, stderr=self.adapter_log, start_new_session=True,
            env={**os.environ, 'WPCP_FIXTURE_ACCESS_TOKEN': self.fixture_access_token, 'WPCP_NATIVE_TRACE': '1'})
        self.adapter_process = process
        self.adapter_port = port
        self.addCleanup(harness.ControlPlaneProcessHarness.stop_process, process)
        for _ in range(100):
            status, _, _ = self.request('GET', '/health', port=port)
            if status == 200: break
            if process.poll() is not None: self.fail('adapter exited')
            time.sleep(.05)
        else: self.fail('adapter did not start')
        self.adapter_root, self.native_port = root, native_port
        return port

    def prepare_real(self):
        port, run_id = self.start_real(), self.new_run()
        worker = harness.command_output(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'real-codex', '--codex-python', sys.executable,
            '--agent-timeout-ms', '90000', '--real-agent-origin', f'http://127.0.0.1:{port}/'], timeout=100)
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        return run_id, self.read_run(run_id)

    def test_real_background_session_has_complete_result_and_native_open_descriptor(self):
        run_id, run = self.prepare_real()
        self.assertEqual('blocked', run['state'], run)
        attempt = next(a for a in run['attempts'] if a.get('session'))
        self.assertEqual('3', attempt['session']['originalResult']['schema_version'])
        self.assertEqual('same-session', attempt['session']['openInCodex']['mode'])
        self.assertIn(attempt['session']['sessionId'], attempt['session']['openInCodex']['url'])
        self.assertFalse(attempt['session']['openInCodex']['appTaskVisible'])

    def open_and_claim(self, run_id, run):
        attempt = next(a for a in run['attempts'] if a.get('session'))
        code, opened, raw = self.operator_cli('open', '--run-id', run_id,
            '--attempt-id', attempt['attemptId'], '--request-id', attempt['session']['humanRequest']['requestId'],
            '--command-id', str(uuid.uuid4()))
        self.assertEqual(0, code, raw)
        current = self.read_run(run_id)['control']
        status, claimed, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/claim', {
            'targetAttemptId': current['targetAttemptId'], 'expectedRunVersion': current['runVersion'],
            'expectedHeadSha': current['headSha'], 'leaseEpoch': current['leaseEpoch']})
        self.assertEqual(200, status, claimed)
        return attempt

    def test_native_non_holder_cannot_write_or_change_backend_configuration(self):
        from websockets.sync.client import connect
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        session = attempt['session']['sessionId']
        with connect(attempt['session']['openInCodex']['url'], additional_headers={
                'Authorization': 'Bearer ' + self.provider.tokens['actor-observer']}) as socket:
            socket.send(json.dumps({'id': 1, 'method': 'turn/start', 'params': {
                'threadId': session, 'input': [{'type': 'text', 'text': 'Change greeting.py now'}]}}))
            response = json.loads(socket.recv(timeout=15))
            self.assertIn('error', response)
            socket.send(json.dumps({'id': 2, 'method': 'command/exec', 'params': {
                'command': ['touch', 'unauthorized'], 'cwd': str(self.adapter_root / 'repository')}}))
            response = json.loads(socket.recv(timeout=15))
            self.assertIn('error', response)
            socket.send(json.dumps({'id': 3, 'method': 'config/value/write', 'params': {
                'keyPath': 'sandbox_mode', 'value': 'danger-full-access', 'mergeStrategy': 'replace'}}))
            self.assertIn('error', json.loads(socket.recv(timeout=15)))
        status, denied, _ = self.request('POST', f'/sessions/{session}/interactions/{uuid.uuid4()}',
            {'message': json.dumps({'kind': 'execute', 'command': ['touch', 'unauthorized']})}, port=self.adapter_port)
        self.assertEqual(403, status, denied)
        self.assertFalse((self.adapter_root / 'repository' / 'unauthorized').exists())
        self.assertEqual('def greet(name):\n    return "Hello," + name\n',
                         (self.adapter_root / 'repository' / 'greeting.py').read_text())

    def test_holder_completes_disposable_issue_through_native_protocol_and_history(self):
        from codex_contract import validate_result
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        session = attempt['session']['sessionId']
        prompt = ('Implement ISSUE.md now. Use mcp__wpcp__execute for all commands. '
                  'First read ISSUE.md, greeting.py and test_greeting.py and run the existing unittest to observe red. '
                  'Fix greeting.py only. Run unittest again to observe green. '
                  'Return completed output with the actual red/green observations and evidence. '
                  'Use this Python interpreter for commands: ' + sys.executable)
        original_tests = (self.adapter_root / 'repository' / 'test_greeting.py').read_bytes()
        native_output, history = self.run_native_ui(run_id, attempt, prompt)
        events = [e['payload']['data']['event'] for e in history['events']
            if e['eventType'] == 'AgentInteractiveObservation' and e['payload']['type'] == 'observation']
        messages = [e['params']['item']['text'] for e in events if e.get('method') == 'item/completed'
                    and e['params']['item'].get('type') == 'agentMessage']
        self.assertTrue(messages, events)
        result = json.loads(messages[-1])
        self.assertEqual([], validate_result(result), result)
        self.assertEqual('completed', result['outcome'], result)
        self.assertEqual(original_tests, (self.adapter_root / 'repository' / 'test_greeting.py').read_bytes())
        self.assertEqual('', subprocess.check_output(['git', 'remote'], cwd=self.adapter_root / 'repository', text=True))
        test = subprocess.run([sys.executable, '-m', 'unittest', '-v'],
            cwd=self.adapter_root / 'repository', capture_output=True, text=True, timeout=10)
        self.assertEqual(0, test.returncode, test.stdout + test.stderr)
        _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
        observations = [e for e in history['events'] if e['eventType'] == 'AgentInteractiveObservation']
        self.assertTrue(observations, history)
        raw = json.dumps(observations)
        self.assertIn('execute-result', raw)
        self.assertIn('turn/completed', raw)
        self.assertIn(session, raw)
        if destination := os.environ.get('WPCP_CODEX_EVIDENCE_DIR'):
            root = Path(destination); root.mkdir(parents=True, exist_ok=True)
            (root / 'real-issue.json').write_text(json.dumps({'runId': run_id, 'sessionId': session,
                'result': result, 'history': history, 'testOutput': test.stderr,
                'diff': subprocess.check_output(['git', 'diff'], cwd=self.adapter_root / 'repository', text=True),
                'remoteCount': 0, 'suppliedTestsUnchanged': True,
                'greeting': (self.adapter_root / 'repository' / 'greeting.py').read_text()}, indent=2))
            (root / 'native-issue-tui.txt').write_text(native_output)

    def test_open_launcher_displays_the_background_session_in_native_codex_tui(self):
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        output, _ = self.run_native_ui(run_id, attempt)
        self.assertTrue('Disposable greeting issue' in output, output[:2500])

    def test_native_observation_outbox_survives_api_and_adapter_crash(self):
        import signal
        from websockets.sync.client import connect
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        session = attempt['session']['sessionId']
        cls = type(self)
        api_args = cls.api.args
        with connect(attempt['session']['openInCodex']['url'], additional_headers={
                'Authorization': 'Bearer ' + self.provider.tokens['actor-authorized']}) as socket:
            socket.send(json.dumps({'id': 1, 'method': 'turn/start', 'params': {'threadId': session,
                'input': [{'type': 'text', 'text': 'Do not use tools. Return blocked with summary "Outage recovery observation".'}]}}))
            while True:
                response = json.loads(socket.recv(timeout=20))
                if response.get('id') == 1: break
            self.assertIn('result', response, response)
            os.kill(cls.api.pid, signal.SIGKILL); cls.api.wait(timeout=10)
            deadline = time.monotonic() + 70
            while time.monotonic() < deadline:
                records = [json.loads(p.read_text()) for p in (self.adapter_root / 'observations').glob('*.json')]
                if any(r['event'].get('method') == 'turn/completed' for r in records): break
                time.sleep(.1)
            else: self.fail('No durable terminal observation during API outage')
            os.kill(self.adapter_process.pid, signal.SIGKILL); self.adapter_process.wait(timeout=10)
        cls.api = subprocess.Popen(api_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True, env={**os.environ, 'WPCP_FIXTURE_ACCESS_TOKEN': self.fixture_access_token,
                                       'WPCP_GITHUB_TEST_ORIGIN': self.provider.origin})
        for _ in range(100):
            if self.request('GET', '/healthz')[0] == 200: break
            time.sleep(.05)
        replacement = subprocess.Popen(self.adapter_process.args, stdout=self.adapter_log, stderr=self.adapter_log,
            start_new_session=True, env={**os.environ, 'WPCP_FIXTURE_ACCESS_TOKEN': self.fixture_access_token})
        self.addCleanup(self.stop_process, replacement)
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
            late = [e for e in history['events'] if e['eventType'] == 'NativeObservationQuarantined']
            if any(e['payload']['data'].get('method') == 'turn/completed' for e in late): break
            time.sleep(.2)
        else: self.fail('Durable outbox did not recover through public history')
        self.assertTrue(all(e['payload']['qualifiesResult'] is False for e in late))
        self.assertEqual(session, next(a for a in self.read_run(run_id)['attempts'] if a.get('session'))['session']['sessionId'])
        self.export_proof('native-outbox-recovery', run_id, sessionId=session, recoveredEvents=len(late))

    def test_real_adapter_replacement_reopens_exact_session(self):
        import signal
        from websockets.sync.client import connect
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        original = attempt['session']['sessionId']
        ownership = json.loads((self.adapter_root / 'preflight.json').read_text())['process']
        os.kill(self.adapter_process.pid, signal.SIGKILL)
        self.adapter_process.wait(timeout=10)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try: os.kill(ownership['processId'], 0)
            except ProcessLookupError: break
            time.sleep(.1)
        else: self.fail('Owned Codex process survived adapter loss')
        replacement = subprocess.Popen(self.adapter_process.args, stdout=self.adapter_log, stderr=self.adapter_log,
            start_new_session=True, env={**os.environ, 'WPCP_FIXTURE_ACCESS_TOKEN': self.fixture_access_token})
        self.addCleanup(self.stop_process, replacement)
        for _ in range(100):
            if self.request('GET', '/health', port=self.adapter_port)[0] == 200: break
            time.sleep(.05)
        code, opened, raw = self.operator_cli('open', '--run-id', run_id,
            '--attempt-id', attempt['attemptId'], '--request-id', attempt['session']['humanRequest']['requestId'],
            '--command-id', str(uuid.uuid4()))
        self.assertEqual(0, code, raw)
        with connect(attempt['session']['openInCodex']['url'], additional_headers={
                'Authorization': 'Bearer ' + self.provider.tokens['actor-authorized']}) as socket:
            socket.send(json.dumps({'id': 1, 'method': 'thread/read', 'params': {'threadId': original}}))
            reply = json.loads(socket.recv(timeout=15))
            self.assertEqual(original, reply['result']['thread']['id'])
        self.export_proof('native-replacement', run_id, sessionId=original, stoppedProcess=ownership)

    def test_native_interrupt_returns_correlated_terminal_event(self):
        from websockets.sync.client import connect
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        session = attempt['session']['sessionId']
        with connect(attempt['session']['openInCodex']['url'], additional_headers={
                'Authorization': 'Bearer ' + self.provider.tokens['actor-authorized']}) as socket:
            socket.send(json.dumps({'id': 1, 'method': 'turn/start', 'params': {'threadId': session,
                'input': [{'type': 'text', 'text': 'Explain how to fix the issue in detail, without tools.'}]}}))
            while True:
                reply = json.loads(socket.recv(timeout=15))
                if reply.get('id') == 1: break
            turn = reply['result']['turn']['id']
            socket.send(json.dumps({'id': 2, 'method': 'turn/interrupt', 'params': {'threadId': session, 'turnId': turn}}))
            completed = None
            while True:
                reply = json.loads(socket.recv(timeout=20))
                if reply.get('id') == 2: self.assertIn('result', reply, reply)
                if reply.get('method') == 'turn/completed':
                    completed = reply['params']['turn']; break
            self.assertEqual(turn, completed['id'])
            self.assertEqual('interrupted', completed['status'])
            self.export_proof('native-interrupt', run_id, turn=completed)

    @staticmethod
    def fences(control):
        return dict(targetAttemptId=control['targetAttemptId'], expectedRunVersion=control['runVersion'],
                    expectedHeadSha=control['headSha'], leaseEpoch=control['leaseEpoch'])

    def export_proof(self, name, run_id, **facts):
        if destination := os.environ.get('WPCP_CODEX_EVIDENCE_DIR'):
            _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-observer')
            value = json.dumps(dict(run=self.read_run(run_id, 'actor-observer'), history=history, facts=facts), indent=2)
            for secret in self.provider.tokens.values(): self.assertNotIn(secret, value)
            root = Path(destination); root.mkdir(parents=True, exist_ok=True)
            (root / (name + '.json')).write_text(value)

    def test_native_live_revocation_blocks_tools_and_quarantines_late_result(self):
        from websockets.sync.client import connect
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        identity = self.provider.identities['actor-authorized']
        with connect(attempt['session']['openInCodex']['url'], additional_headers={
                'Authorization': 'Bearer ' + self.provider.tokens['actor-authorized']}) as socket:
            socket.send(json.dumps({'id': 1, 'method': 'turn/start', 'params': {
                'threadId': attempt['session']['sessionId'], 'input': [{'type': 'text',
                'text': 'Use mcp__wpcp__execute to create revoked-write.txt now. Return the tool result.'}]}}))
            while True:
                reply = json.loads(socket.recv(timeout=20))
                if reply.get('id') == 1: break
            self.assertIn('result', reply, reply)
            identity.update(push=False)
            try:
                deadline = time.monotonic() + 70
                while time.monotonic() < deadline:
                    _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events', actor_id='actor-observer')
                    late = [e for e in history['events'] if e['eventType'] == 'NativeObservationQuarantined']
                    if any(e['payload']['data'].get('method') == 'turn/completed' for e in late): break
                    time.sleep(.2)
                else: self.fail('No correlated late terminal observation')
                self.assertFalse((self.adapter_root / 'repository' / 'revoked-write.txt').exists())
                self.assertTrue(all(e['payload']['qualifiesResult'] is False for e in late))
                self.assertTrue(any(e['payload']['data'].get('method') == 'hook/completed' and
                    e['payload']['data']['params']['run']['status'] == 'blocked' for e in late), late)
                self.export_proof('native-revocation', run_id, preventedFile='revoked-write.txt')
            finally:
                identity.update(push=True)

    def test_native_old_window_is_fenced_after_forced_takeover(self):
        from websockets.sync.client import connect
        run_id, run = self.prepare_real()
        attempt = self.open_and_claim(run_id, run)
        with connect(attempt['session']['openInCodex']['url'], additional_headers={
                'Authorization': 'Bearer ' + self.provider.tokens['actor-authorized']}) as socket:
            socket.send(json.dumps({'id': 1, 'method': 'thread/read', 'params': {'threadId': attempt['session']['sessionId']}}))
            self.assertIn('result', json.loads(socket.recv(timeout=15)))
            current = self.read_run(run_id)['control']
            status, changed, _ = self.request('POST', f'/api/v1/runs/{run_id}/control/force-takeover',
                dict(self.fences(current), reason='Native session takeover verification'), actor_id='actor-contributor')
            self.assertEqual(200, status, changed)
            socket.send(json.dumps({'id': 2, 'method': 'turn/start', 'params': {
                'threadId': attempt['session']['sessionId'], 'input': [{'type': 'text', 'text': 'Write stale.txt'}]}}))
            response = json.loads(socket.recv(timeout=15))
            self.assertIn('error', response, response)
            self.assertFalse((self.adapter_root / 'repository' / 'stale.txt').exists())
            self.export_proof('native-takeover', run_id, denied=response)

    def test_real_resume_and_fork_are_exactly_once_through_operator(self):
        from tests.test_fake_codex_attempt import FakeCodexTests
        for action in ('resume', 'fork'):
            with self.subTest(action=action):
                run_id, run = self.prepare_real()
                attempt = self.open_and_claim(run_id, run)
                current = self.read_run(run_id)['control']
                command = str(uuid.uuid4())
                arguments = (action, '--run-id', run_id, *FakeCodexTests.fence(self, {'control': current}),
                    '--request-id', attempt['session']['humanRequest']['requestId'], '--command-id', command)
                code, decision, raw = self.operator_cli(*arguments)
                self.assertEqual(0, code, raw)
                operation = decision['continuation']
                result = operation['resultSessionId']
                self.assertEqual(action == 'resume', result == attempt['session']['sessionId'])
                code, replay, raw = self.operator_cli(*arguments)
                self.assertEqual(0, code, raw)
                self.assertEqual(operation, replay['continuation'])
                self.export_proof('native-' + action, run_id, operation=operation)

    def run_native_ui(self, run_id, attempt, prompt=None):
        import fcntl
        import pty
        import select
        import struct
        import termios
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack('HHHH', 40, 120, 0, 0))
        command = [sys.executable, str(harness.PILOT_ROOT / 'codex_open.py'),
            '--api-url', self.base_url, '--run-id', run_id, '--attempt-id', attempt['attemptId']]
        if prompt: command += ['--prompt', prompt]
        process = subprocess.Popen(command,
            stdin=slave, stdout=slave, stderr=slave, start_new_session=True,
            env={**os.environ, 'TERM': 'xterm-256color', 'WPCP_FIXTURE_ACCESS_TOKEN': self.fixture_access_token,
                 'WPCP_PROVIDER_TOKEN': self.provider.tokens['actor-authorized']})
        os.close(slave)
        captured = b''
        history = {'events': []}
        try:
            deadline = time.monotonic() + (120 if prompt else 20)
            last_poll = 0
            while time.monotonic() < deadline and process.poll() is None:
                if select.select([master], [], [], .1)[0]:
                    data = os.read(master, 65536); captured += data
                    if b'\x1b[6n' in data: os.write(master, b'\x1b[1;1R')
                    if not prompt and b'Disposable greeting issue' in captured: break
                    if b'Failed to start turn:' in captured: break
                if prompt and time.monotonic() - last_poll > .5:
                    _, history, _ = self.request('GET', f'/api/v1/runs/{run_id}/events')
                    if any(e['eventType'] == 'AgentInteractiveObservation' and
                           e['payload']['type'] == 'observation' and
                           e['payload']['data']['event'].get('method') == 'turn/completed'
                           for e in history['events']): break
                    last_poll = time.monotonic()
        finally:
            self.stop_process(process); os.close(master)
        output = captured.decode('utf-8', errors='replace')
        self.adapter_log.flush(); self.adapter_log.seek(0)
        trace = self.adapter_log.read()
        if destination := os.environ.get('WPCP_CODEX_EVIDENCE_DIR'):
            root = Path(destination); root.mkdir(parents=True, exist_ok=True)
            (root / 'native-tui.txt').write_text(output)
            (root / 'native-trace.txt').write_text(trace)
        self.assertTrue('Disposable greeting issue' in output, trace + '\n' + output[:2500])
        return output, history
