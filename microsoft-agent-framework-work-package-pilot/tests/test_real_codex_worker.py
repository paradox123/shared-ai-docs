"""Worker's real-adapter contract through public HTTP and Operator read-back."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import sys
import unittest
import uuid
from tests import test_control_plane_black_box as harness


class RealCodexWorkerTests(harness.ControlPlaneProcessHarness, unittest.TestCase):
    def test_real_worker_retains_canonical_result_and_creates_targeted_human_request(self):
        session_id = str(uuid.uuid4())
        result = {'schema_version': '3', 'outcome': 'blocked', 'summary': 'Choose the greeting format.',
                  'red_green_slices': [], 'changed_files': [], 'verification': [],
                  'evidence': [], 'findings': [], 'intervention': None}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def do_PUT(self):
                self.rfile.read(int(self.headers['Content-Length']))
                body = json.dumps({'contractVersion': 'AgentSessionAdapter/v1',
                    'operationKey': self.path.split('/')[-1], 'sessionId': session_id,
                    'openInCodex': {'mode': 'same-session', 'sameSession': True,
                        'appTaskVisible': False, 'reason': 'contract-fixture'},
                    'events': [{'sequence': 1, 'type': 'result', 'data': result}]}).encode()
                self.send_response(200); self.send_header('Content-Length', str(len(body)))
                self.end_headers(); self.wfile.write(body)

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        run_id = self.new_run()
        worker = harness.command_output(['dotnet', str(harness.WORKER_DLL),
            '--connection-string', self.connection_string, '--fixture', str(self.fixture_path),
            '--run-id', run_id, '--worker-id', 'real-codex',
            '--codex-python', sys.executable,
            '--real-agent-origin', f'http://127.0.0.1:{server.server_port}/'])
        self.assertEqual(0, worker.returncode, worker.stdout + worker.stderr)
        run = self.read_run(run_id)
        attempts = [a for a in run['attempts'] if a.get('session')]
        self.assertEqual(1, len(attempts), run)
        self.assertEqual('blocked', run['state'])
        self.assertEqual(result, attempts[0]['session']['originalResult'])
        self.assertEqual(session_id, attempts[0]['session']['humanRequest']['sessionId'])
        self.assertEqual('Choose the greeting format.', attempts[0]['session']['humanRequest']['problem'])
        self.assertTrue(any(a['activityType'] == 'real-codex' for a in run['activities']))
