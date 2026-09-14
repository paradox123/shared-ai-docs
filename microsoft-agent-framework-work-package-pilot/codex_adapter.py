"""Run-scoped real Codex adapter. HTTP adapter contract plus native TUI gateway."""
import argparse
import asyncio
import fcntl
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import signal
import shlex
import importlib.metadata
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

from codex_connection import Connection
from codex_contract import CANONICAL_PATH, endpoint_schema, validate_result
from codex_runtime_gate import persist, probe_tools


def http_json(url, method='GET', body=None, headers=None):
    request = urllib.request.Request(url, None if body is None else json.dumps(body).encode(),
        {'Content-Type': 'application/json', **(headers or {})}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


class Adapter:
    def __init__(self, config, root, api, port, native_port):
        self.config, self.root, self.api = config, Path(root).resolve(), api.rstrip('/')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        self.owner = (self.root / 'adapter.lock').open('a')
        fcntl.flock(self.owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.repository, self.home = self.root / 'repository', self.root / 'codex-home'
        self.port, self.native_port = port, native_port
        self.runtime = None
        self.ready = False
        self.lock = threading.RLock()
        self.contexts = {}
        self.clients = set()
        self.execution_token = secrets.token_urlsafe(32)
        self.service_token = os.environ['WPCP_REAL_ADAPTER_TOKEN']
        self.terminal_events = threading.Condition()
        self.hook_configuration = {}
        self.active_turn = None
        self.qualification_operation = None
        self.analysis_operation = None
        self.analysis_mode = False
        self.turn_started_at = None
        self.outbox = self.root / 'observations'
        self.outbox.mkdir(exist_ok=True, mode=0o700)
        self.retry_observations = set(self.outbox.glob('*.json'))
        self.stopping = threading.Event()
        threading.Thread(target=self.recover_observations, daemon=True).start()

    def observation(self, context, event):
        identity = str(uuid.uuid5(uuid.NAMESPACE_URL, context.session + json.dumps(event, sort_keys=True)))
        path = self.outbox / (identity + '.json')
        persist(path, {'runId': context.run_id, 'attemptId': context.attempt['attemptId'],
            'sessionId': context.session, 'observationId': identity, 'event': event})
        return path

    def quarantine_observation(self, path):
        record = json.loads(path.read_text())
        status, _ = http_json(f'{self.api}/api/v1/runs/{record["runId"]}/native-quarantine/{record["attemptId"]}',
            'POST', {key: record[key] for key in ('sessionId', 'observationId', 'event')},
            {'X-Wpcp-Adapter-Token': self.service_token})
        if status != 200: raise PermissionError('quarantine-unavailable')
        path.unlink(missing_ok=True)

    def recover_observations(self):
        while not self.stopping.wait(1):
            for path in list(self.retry_observations):
                try:
                    self.quarantine_observation(path)
                    self.retry_observations.discard(path)
                except (OSError, ValueError):
                    pass  # Private durable outbox survives process/API replacement.

    def receipt_path(self, operation):
        uuid.UUID(operation)
        return self.root / (operation + '.json')

    def verify_pin(self):
        config = self.config
        if hashlib.sha256(Path(config['executable']).read_bytes()).hexdigest() != config['sha256']:
            raise ValueError('runtime-drift')
        version = subprocess.run([config['executable'], '--version'], capture_output=True,
                                 text=True, check=True, timeout=5).stdout.strip()
        if version != config['version']:
            raise ValueError('runtime-version-mismatch')
        if hashlib.sha256(CANONICAL_PATH.read_bytes()).hexdigest() != config['canonicalSchemaSha256']:
            raise ValueError('contract-drift')
        if importlib.metadata.version('jsonschema') != config['jsonschemaVersion'] or importlib.metadata.version('websockets') != '15.0.1':
            raise ValueError('dependency-drift')

    def start_runtime(self):
        if self.runtime:
            if not self.ready: raise ValueError('preflight-incomplete')
            return
        self.verify_pin()
        self.repository.mkdir(exist_ok=True)
        self.home.mkdir(exist_ok=True, mode=0o700)
        source = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'auth.json'
        shutil.copyfile(source, self.home / 'auth.json')
        os.chmod(self.home / 'auth.json', 0o600)
        tool = Path(__file__).with_name('codex_execution_tool.py')
        # No user configuration, plugins, external MCPs or native write tools.
        configuration = '''web_search = "disabled"
[features]
shell_tool = false
code_mode = false
code_mode_host = true
multi_agent = false
apps = false
plugins = false
browser_use = false
computer_use = false
image_generation = false
[mcp_servers.wpcp]
command = %s
args = [%s]
default_tools_approval_mode = "approve"
[mcp_servers.wpcp.env]
WPCP_EXECUTION_URL = %s
WPCP_EXECUTION_TOKEN = %s
''' % tuple(json.dumps(value) for value in (sys.executable, str(tool),
            f'http://127.0.0.1:{self.port}/execute', self.execution_token))
        (self.home / 'config.toml').write_text(configuration)
        os.chmod(self.home / 'config.toml', 0o600)
        env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR', 'LANG') if k in os.environ}
        env.update(CODEX_HOME=str(self.home), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        protocol = self.root / 'protocol'
        subprocess.run([self.config['executable'], 'app-server', 'generate-json-schema', '--out', str(protocol)],
                       env=env, capture_output=True, check=True, timeout=15)
        if hashlib.sha256((protocol / 'ClientRequest.json').read_bytes()).hexdigest() != self.config['protocolSha256']:
            raise ValueError('protocol-drift')
        hook_config = self.home / 'hook-endpoint.json'
        persist(hook_config, {'url': f'http://127.0.0.1:{self.port}/authorize-tool', 'token': self.execution_token})
        command = shlex.join([sys.executable, str(Path(__file__).with_name('codex_tool_hook.py')), str(hook_config)])
        (self.home / 'hooks.json').write_text(json.dumps({'hooks': {'PreToolUse': [
            {'hooks': [{'type': 'command', 'command': command, 'timeout': 12}]}]}}))
        if not (self.repository / '.git').exists():
            subprocess.run(['git', 'init', '-q', '--initial-branch=codex/disposable-issue', '--template=', str(self.repository)],
                           env=env, check=True, capture_output=True, timeout=5)
            if self.analysis_mode:
                (self.repository / 'README.md').write_text('Service-owned read-only requirements analysis workspace. No implementation checkout.\n')
                subprocess.run(['git', '-C', str(self.repository), 'add', 'README.md'], env=env, check=True, capture_output=True, timeout=5)
                subprocess.run(['git', '-C', str(self.repository), '-c', 'user.name=Codex Pilot',
                    '-c', 'user.email=pilot@localhost', '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Analysis workspace'],
                    env=env, check=True, capture_output=True, timeout=5)
            else:
                self.prepare_disposable_issue(env)
        self.runtime = Connection(self.config['executable'], str(self.repository), env, self.observe)
        hooks = self.runtime.request('hooks/list', {'cwds': [str(self.repository)]})['data'][0]['hooks']
        if len(hooks) != 1 or hooks[0]['command'] != command:
            raise ValueError('hook-configuration-mismatch')
        hook = hooks[0]
        self.hook_configuration = {'hooks.state': {hook['key']: {'trusted_hash': hook['currentHash']}}}
        with (self.home / 'config.toml').open('a') as output:
            output.write('\n[hooks.state.' + json.dumps(hook['key']) + ']\ntrusted_hash = ' + json.dumps(hook['currentHash']) + '\n')
        capabilities = {}
        # Capability probes must leave a supplied checkout unchanged.
        probe_file = self.repository / 'probe.txt'
        previous_probe = probe_file.read_bytes() if probe_file.exists() else None
        try:
            probe_tools(self.runtime, self.repository, self.root, capabilities)
        finally:
            if previous_probe is None: probe_file.unlink(missing_ok=True)
            else: probe_file.write_bytes(previous_probe)
        if any(value['status'] != 'passed' for value in capabilities.values()):
            raise ValueError('runtime-tools-or-sandbox-failed')
        persist(self.root / 'preflight.json', {'runtimeVersion': self.config['version'],
            'runtimeSha256': self.config['sha256'], 'protocolSha256': self.config['protocolSha256'],
            'canonicalSchemaSha256': self.config['canonicalSchemaSha256'],
            'dependencies': {'jsonschema': importlib.metadata.version('jsonschema'), 'websockets': importlib.metadata.version('websockets')},
            'repositoryBaseSha': subprocess.check_output(['git', '-C', str(self.repository), 'rev-parse', 'HEAD'], env=env, text=True).strip(),
            'remoteCount': len(subprocess.check_output(['git', '-C', str(self.repository), 'remote'], env=env, text=True).splitlines()),
            'capabilities': capabilities, 'process': self.runtime.owned.ownership})
        self.ready = True
        threading.Thread(target=self.watchdog, daemon=True).start()

    def prepare_disposable_issue(self, env):
        (self.repository / 'greeting.py').write_text('def greet(name):\n    return "Hello," + name\n')
        (self.repository / 'test_greeting.py').write_text('''import unittest
from greeting import greet
class GreetingTests(unittest.TestCase):
    def test_named_greeting(self): self.assertEqual('Hello, Ada!', greet(' Ada '))
    def test_empty_name(self):
        with self.assertRaises(ValueError): greet('   ')
if __name__ == '__main__': unittest.main()
''')
        (self.repository / 'ISSUE.md').write_text('Fix greet: trim the name, return Hello, NAME!; reject blank names with ValueError.\nRun the supplied unittest before and after the change. Do not change tests.\n')
        subprocess.run(['git', '-C', str(self.repository), 'add', 'ISSUE.md', 'greeting.py', 'test_greeting.py'],
                       env=env, check=True, capture_output=True, timeout=5)
        subprocess.run(['git', '-C', str(self.repository), '-c', 'user.name=Codex Pilot',
            '-c', 'user.email=pilot@localhost', '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Disposable issue fixture'],
            env=env, check=True, capture_output=True, timeout=5)

    def watchdog(self):
        while self.runtime is not None and self.runtime.owned.process.poll() is None:
            operation = self.qualification_operation
            if operation is not None:
                try: os.kill(operation['workerPid'], 0)
                except ProcessLookupError:
                    self.runtime.close()
                    return
            target = self.active_turn
            if target and self.turn_started_at and time.monotonic() - self.turn_started_at > 120:
                try:
                    self.runtime.request('turn/interrupt', {'threadId': target[0], 'turnId': target[1]}, timeout=3)
                    time.sleep(3)
                    if self.active_turn == target: raise TimeoutError('interrupt-did-not-stop-turn')
                except Exception:
                    stopped = self.runtime.close()
                    self.observe({'method': 'wpcp/processStopped', 'params': {
                        'threadId': target[0], 'turnId': target[1], 'process': stopped, 'reason': 'turn-timeout'}})
                    return
            time.sleep(.2)

    def observe(self, event):
        if self.analysis_operation is not None:
            self.analysis_operation.observe(event)
        params = event.get('params', {})
        if event.get('method') == 'wpcp/runtimeExited' and self.active_turn:
            params.update(threadId=self.active_turn[0], turnId=self.active_turn[1])
            self.active_turn = None
            self.turn_started_at = None
        if event.get('method') == 'turn/started':
            self.active_turn = (params['threadId'], params['turn']['id'])
            self.turn_started_at = time.monotonic()
        elif event.get('method') == 'turn/completed' and self.active_turn == (params['threadId'], params['turn']['id']):
            self.active_turn = None
            self.turn_started_at = None
        with self.terminal_events:
            self.terminal_events.notify_all()
        for client in list(self.clients):
            client.publish(event)

    def wait_turn(self, session, turn, timeout=60):
        deadline = time.monotonic() + timeout
        with self.terminal_events:
            while time.monotonic() < deadline:
                for event in self.runtime.events:
                    params = event.get('params', {})
                    if event.get('method') == 'turn/completed' and params.get('threadId') == session and params['turn']['id'] == turn:
                        return params['turn']
                self.terminal_events.wait(timeout=max(0, deadline - time.monotonic()))
        raise TimeoutError('turn-timeout')

    def capability(self, session):
        return {'mode': 'same-session', 'sameSession': True, 'appTaskVisible': False,
            'reason': 'native-codex-tui-via-fenced-gateway; desktop-sidebar-not-used',
            'url': f'ws://127.0.0.1:{self.native_port}/sessions/{session}'}

    def start(self, operation, request):
        with self.lock:
            path = self.receipt_path(operation)
            if path.exists():
                receipt = json.loads(path.read_text())
                if receipt.get('state') != 'complete':
                    raise ValueError('session-start-uncertain')
                if receipt['runId'] != request['runId']:
                    raise ValueError('assignment-conflict')
                return receipt['body']
            uuid.UUID(request['runId'])
            binding = self.root / 'binding.json'
            if binding.exists() and json.loads(binding.read_text())['runId'] != request['runId']:
                raise ValueError('adapter-is-bound-to-another-run')
            persist(binding, {'runId': request['runId']})
            self.start_runtime()
            persist(path, {'state': 'dispatching', 'runId': request['runId']})
            response = self.runtime.request('thread/start', {'cwd': str(self.repository),
                'sandbox': 'read-only', 'approvalPolicy': 'never',
                'config': self.hook_configuration,
                'baseInstructions': 'You implement only ISSUE.md in the disposable repository. Use only mcp__wpcp__execute for commands and file changes. Never access external repositories. Follow the user phase instructions.'})
            session = response['thread']['id']
            persist(path, {'state': 'mapped', 'runId': request['runId'], 'sessionId': session})
            turn, result = self.materialize(session, request.get('note'))
            background = [{'sequence': index + 2, 'type': 'message', 'data': {'runtimeEvent': event}}
                for index, event in enumerate(e for e in self.runtime.events
                    if e.get('params', {}).get('threadId') == session and
                    e.get('method') in ('turn/started', 'item/started', 'item/completed', 'turn/completed'))]
            body = {'contractVersion': 'AgentSessionAdapter/v1', 'operationKey': operation,
                'sessionId': session, 'openInCodex': self.capability(session), 'events': [
                    {'sequence': 1, 'type': 'message', 'data': {'threadId': session, 'turnId': turn,
                        'runtimeVersion': self.config['version'], 'runtimeSha256': self.config['sha256'],
                        'process': self.runtime.owned.ownership, 'preflight': json.loads((self.root / 'preflight.json').read_text()),
                        'canonicalValidationPassed': True}}, *background,
                    {'sequence': len(background) + 2, 'type': 'result', 'data': result}]}
            persist(path, {'state': 'complete', 'runId': request['runId'], 'body': body})
            return body

    def materialize(self, session, assignment=None):
        expected = {'schema_version': '3', 'outcome': 'blocked',
            'summary': 'Disposable greeting issue is ready for the human continuation.',
            'red_green_slices': [], 'changed_files': [], 'verification': [], 'evidence': [],
            'findings': [], 'intervention': None}
        turn = self.runtime.request('turn/start', {'threadId': session, 'outputSchema': endpoint_schema(),
            'input': [{'type': 'text', 'text': 'Preflight phase. Retain this assignment for the later authorized continuation: ' + (assignment or 'ISSUE.md') + '. Do not use tools or start implementation. Return exactly: ' + json.dumps(expected)}]})['turn']['id']
        completed = self.wait_turn(session, turn)
        messages = [e['params']['item']['text'] for e in self.runtime.events
            if e.get('method') == 'item/completed' and e['params'].get('threadId') == session
            and e['params']['item'].get('type') == 'agentMessage']
        result = json.loads(messages[-1]) if messages else None
        if completed['status'] != 'completed' or result != expected or validate_result(result):
            raise ValueError('canonical-result-invalid')
        return turn, result

    def continue_session(self, operation, request):
        with self.lock:
            source, action = request['sourceSessionId'], request['action']
            if action not in ('resume', 'fork', 'handoff', 'fresh-retry'):
                raise ValueError('unsupported-continuation')
            record = self.find(source)
            path = self.receipt_path(operation)
            if path.exists():
                saved = json.loads(path.read_text())
                if saved.get('intent') != request or saved.get('state') != 'complete':
                    raise ValueError('continuation-conflict-or-uncertain')
                return saved['body']
            self.start_runtime()
            persist(path, {'state': 'dispatching', 'runId': record['runId'], 'intent': request})
            if action == 'fresh-retry':
                response = self.runtime.request('thread/start', {'cwd': str(self.repository),
                    'sandbox': 'read-only', 'approvalPolicy': 'never', 'config': self.hook_configuration})
            else:
                response = self.runtime.request('thread/resume' if action == 'resume' else 'thread/fork',
                    {'threadId': source, 'sandbox': 'read-only', 'approvalPolicy': 'never'})
            session = response['thread']['id']
            if action == 'fresh-retry': self.materialize(session)
            parent = source if action in ('fork', 'handoff') else None
            if (action == 'resume') != (session == source): raise ValueError('incorrect-session-identity')
            if parent and response['thread'].get('forkedFromId') != source: raise ValueError('incorrect-session-lineage')
            body = {'contractVersion': 'AgentSessionAdapter/v1', 'operationKey': operation,
                'sourceSessionId': source, 'sessionId': session, 'parentSessionId': parent,
                'action': action, 'openInCodex': self.capability(session)}
            persist(path, {'state': 'complete', 'runId': record['runId'], 'intent': request, 'body': body})
            return body

    def fence(self, operation, request):
        with self.lock:
            path = self.receipt_path(operation)
            record = json.loads(path.read_text()) if path.exists() else None
            if record is None:
                persist(path, {'state': 'fenced', 'intent': request})
            applied = record and record.get('state') == 'complete'
            return {**request, 'contractVersion': 'AgentSessionAdapter/v1', 'operationKey': operation,
                'state': 'applied' if applied else 'fenced' if record is None or record.get('state') == 'fenced' else 'unsafe',
                'receipt': record['body'] if applied else None}

    def find(self, session):
        for path in self.root.glob('*.json'):
            receipt = json.loads(path.read_text())
            if 'runId' in receipt and receipt.get('body', {}).get('sessionId') == session:
                return receipt
        raise ValueError('unknown-session')

    def open(self, session, operation):
        with self.lock:
            self.find(session)
            self.start_runtime()
            read = self.runtime.request('thread/resume', {'threadId': session,
                'sandbox': 'read-only', 'approvalPolicy': 'never'})
            if read['thread']['id'] != session:
                raise ValueError('session-mismatch')
            return {'contractVersion': 'AgentSessionAdapter/v1', 'operationKey': operation,
                'sessionId': session, 'opened': True, 'openInCodex': self.capability(session)}

    def interaction(self, session, operation, message):
        with self.lock:
            path = self.receipt_path(operation)
            if path.exists():
                receipt = json.loads(path.read_text())
                if receipt.get('message') != message or receipt.get('sessionId') != session:
                    raise ValueError('interaction-conflict')
                if receipt.get('state') != 'complete': raise ValueError('interaction-uncertain')
                return receipt['body']
            self.find(session)
            payload = json.loads(message)
            persist(path, {'state': 'dispatching', 'sessionId': session, 'message': message})
            kind = payload['kind']
            if kind == 'prompt':
                if self.active_turn is not None: raise ValueError('turn-already-active')
                response = self.runtime.request('turn/start', {'threadId': session,
                    'input': [{'type': 'text', 'text': payload['text']}], 'outputSchema': endpoint_schema()})
                self.active_turn = (session, response['turn']['id'])
            elif kind == 'execute':
                command = payload['command']
                if not isinstance(command, list) or not command or not all(isinstance(s, str) for s in command):
                    raise ValueError('invalid-command')
                response = self.runtime.request('command/exec', {'command': command, 'cwd': str(self.repository),
                    'timeoutMs': 5000, 'sandboxPolicy': {'type': 'workspaceWrite', 'networkAccess': False,
                        'writableRoots': [str(self.repository)], 'excludeSlashTmp': True, 'excludeTmpdirEnvVar': True}})
            elif kind in ('observation', 'tool-check'):
                response = {'recorded': True}
            elif kind == 'interrupt':
                response = self.runtime.request('turn/interrupt', {'threadId': session, 'turnId': payload['turnId']})
            else:
                raise ValueError('unsupported-interaction')
            events = [{'type': kind, 'data': payload}, {'type': kind + '-result', 'data': response}]
            body = {'contractVersion': 'AgentSessionAdapter/v1', 'operationKey': operation,
                'sessionId': session, 'message': message, 'events': events, 'response': response}
            persist(path, {'state': 'complete', 'sessionId': session, 'message': message, 'body': body})
            return body

    def execute(self, command):
        if self.analysis_operation is not None:
            return self.analysis_operation.execute(command)
        if self.qualification_operation is not None:
            self.authorize_qualification_tool(self.qualification_operation['sessionId'])
            return self.runtime.request('command/exec', {'command': command, 'cwd': str(self.repository),
                'timeoutMs': 10000, 'sandboxPolicy': {'type': 'workspaceWrite', 'networkAccess': False,
                    'writableRoots': [str(self.repository)], 'excludeSlashTmp': True, 'excludeTmpdirEnvVar': True}})
        contexts = [context for context in self.contexts.values() if context.active and
                    self.active_turn is not None and context.session == self.active_turn[0]]
        if len(contexts) != 1:
            raise ValueError('no-exclusive-native-turn')
        return contexts[0].write({'kind': 'execute', 'command': command})

    def authorize_tool(self, tool):
        if self.analysis_operation is not None:
            self.analysis_operation.authorize(tool.get('session_id'))
            if tool.get('tool_name') != 'mcp__wpcp__execute': raise ValueError('analysis-tool-denied')
            return {'allowed': True}
        if self.qualification_operation is not None:
            self.authorize_qualification_tool(tool.get('session_id'))
            if tool.get('tool_name') != 'mcp__wpcp__execute': raise ValueError('qualification-tool-denied')
            return {'allowed': True}
        contexts = [context for context in self.contexts.values() if context.active and context.session == tool.get('session_id')]
        if len(contexts) != 1: raise ValueError('no-authorized-native-turn')
        contexts[0].write({'kind': 'tool-check', 'tool': tool})
        return {'allowed': True}

    def authorize_qualification_tool(self, session):
        operation = self.qualification_operation
        if (operation is None or operation['kind'] != 'repair' or operation['sessionId'] != session or
                self.active_turn is None or self.active_turn[0] != session):
            raise ValueError('qualification-tool-denied')
        os.kill(operation['workerPid'], 0)
        from publication_adapter import git
        if git({'localPath': str(self.repository)}, 'branch', '--show-current') != operation['branch']:
            raise ValueError('qualification-branch-drift')

    def close(self):
        self.stopping.set()
        if self.runtime: self.runtime.close()
        self.owner.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True); parser.add_argument('--state-root', required=True)
    parser.add_argument('--api-url', required=True); parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--native-port', type=int, required=True)
    args = parser.parse_args()
    adapter = Adapter(json.loads(Path(args.config).read_text()), args.state_root, args.api_url, args.port, args.native_port)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def reply(self, status, value):
            data = json.dumps(value).encode(); self.send_response(status)
            self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(data)))
            self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            if self.path == '/health': return self.reply(200, {'status': 'ready'})
            if self.path == '/submission-readiness':
                if not secrets.compare_digest(self.headers.get('X-Wpcp-Adapter-Token', ''), adapter.service_token):
                    return self.reply(403, {'code': 'adapter-access-denied'})
                try:
                    from submission_analysis import readiness
                    return self.reply(200, readiness(adapter))
                except Exception:
                    return self.reply(503, {'code': 'agent-readiness-unavailable'})
            if self.path == '/publication-readiness':
                if not secrets.compare_digest(self.headers.get('X-Wpcp-Adapter-Token', ''), adapter.service_token):
                    return self.reply(403, {'code': 'adapter-access-denied'})
                try:
                    with adapter.lock: adapter.start_runtime()
                    return self.reply(200, {'contractVersion': 'AgentSessionAdapter/v1',
                        'localPath': str(adapter.repository), 'runtimeReady': adapter.ready,
                        'sandboxReady': adapter.ready, 'activeTurn': adapter.active_turn is not None})
                except Exception:
                    return self.reply(503, {'code': 'agent-readiness-unavailable'})
            return self.reply(404, {'code': 'not-found'})
        def mutate(self):
            try:
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 1_000_000: raise ValueError('invalid-body-size')
                body = json.loads(self.rfile.read(size))
                parts = self.path.strip('/').split('/')
                if self.path not in ('/execute', '/authorize-tool') and not secrets.compare_digest(
                        self.headers.get('X-Wpcp-Adapter-Token', ''), adapter.service_token):
                    return self.reply(403, {'code': 'adapter-access-denied'})
                if self.command == 'PUT' and len(parts) == 2 and parts[0] == 'submission-analyses':
                    from submission_analysis import analyze
                    return self.reply(200, analyze(adapter, parts[1], body))
                if self.command == 'PUT' and len(parts) == 2 and parts[0] == 'sessions':
                    return self.reply(200, adapter.start(parts[1], body))
                if self.command == 'PUT' and len(parts) == 2 and parts[0] in ('qualification-reviews', 'qualification-repairs'):
                    from codex_qualification import execute
                    return self.reply(200, execute(adapter, 'review' if parts[0] == 'qualification-reviews' else 'repair',
                        parts[1], body, int(self.headers['X-Wpcp-Worker-Pid'])))
                if self.path in ('/execute', '/authorize-tool'):
                    if self.headers.get('Authorization') != 'Bearer ' + adapter.execution_token:
                        return self.reply(403, {'code': 'execution-denied'})
                    return self.reply(200, adapter.execute(body['command']) if self.path == '/execute' else adapter.authorize_tool(body))
                if len(parts) == 3 and parts[0] == 'sessions' and parts[2] == 'open':
                    return self.reply(200, adapter.open(parts[1], body['operationKey']))
                if len(parts) == 4 and parts[0] == 'sessions' and parts[2] == 'interactions':
                    return self.reply(200, adapter.interaction(parts[1], parts[3], body['message']))
                if len(parts) == 2 and parts[0] == 'continuations':
                    return self.reply(200, adapter.continue_session(parts[1], body))
                if len(parts) == 3 and parts[0] == 'control-operations' and parts[2] == 'fence':
                    return self.reply(200, adapter.fence(parts[1], body))
                return self.reply(404, {'code': 'not-found'})
            except Exception as error:
                # No upstream error text or credentials are returned.
                safe = {'session-start-uncertain', 'continuation-conflict-or-uncertain', 'interaction-uncertain',
                        'qualification-policy-rejected', 'qualification-worktree-mismatch', 'qualification-run-mismatch',
                        'qualification-operation-conflict', 'qualification-operation-uncertain', 'qualification-head-drift',
                        'qualification-branch-drift', 'qualification-result-unavailable', 'repair-writer-mismatch',
                        'runtime-drift', 'contract-drift', 'dependency-drift', 'protocol-drift', 'preflight-incomplete'}
                code = str(error) if isinstance(error, ValueError) and str(error) in safe else 'real-adapter-unavailable'
                return self.reply(503, {'code': code, 'category': type(error).__name__})
        do_POST = mutate
        do_PUT = mutate

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    from codex_native_gateway import run_gateway
    native = threading.Thread(target=lambda: asyncio.run(run_gateway(adapter)), daemon=True)
    native.start()
    def stop(*_): raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, stop)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        adapter.close(); server.server_close()


if __name__ == '__main__':
    main()
