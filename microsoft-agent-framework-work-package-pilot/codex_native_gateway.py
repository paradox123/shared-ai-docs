"""Native Codex TUI access through the existing Operator authorization boundary."""
import asyncio
import base64
import json
import os
import queue
import threading
import sys
import uuid
from websockets.asyncio.server import serve
from codex_adapter import http_json


class NativeContext:
    def __init__(self, adapter, session, credential, publish):
        self.adapter, self.session = adapter, session
        self.run_id = adapter.find(session)['runId']
        self.headers = {'Authorization': credential}
        if token := os.environ.get('WPCP_FIXTURE_ACCESS_TOKEN'):
            self.headers['X-Wpcp-Fixture-Access'] = token
        status, run = self.call('GET', '')
        if status != 200: raise PermissionError('repository-access-denied')
        attempts = [a for a in run['attempts'] if a.get('session', {}) and a['session']['sessionId'] == session]
        if len(attempts) != 1 or not attempts[0]['session']['openedInCodex']:
            raise PermissionError('selected-session-not-opened')
        self.attempt = attempts[0]
        self.request_id = self.attempt['session']['humanRequest']['requestId']
        self.fence = run['control']
        self.publish_to_client = publish
        self.lock = threading.RLock()
        self.active = False
        self.events = queue.Queue(maxsize=4096)
        self.closed = False
        self.revoked = False
        self.disconnected = False
        self.pump = threading.Thread(target=self.forward_events, daemon=True)
        self.pump.start()

    def call(self, method, path, body=None):
        return http_json(f'{self.adapter.api}/api/v1/runs/{self.run_id}' + path,
                         method, body, self.headers)

    def write(self, payload):
        with self.lock:
            command = str(uuid.uuid4())
            status, decision = self.call('POST', '/control/write', {
                'targetAttemptId': self.attempt['attemptId'], 'requestId': self.request_id,
                'expectedRunVersion': self.fence['runVersion'], 'expectedHeadSha': self.fence['headSha'],
                'leaseEpoch': self.fence['leaseEpoch'], 'commandId': command,
                'message': json.dumps(payload, sort_keys=True)})
            if status != 200 or not decision.get('accepted'):
                raise PermissionError(decision.get('code', 'control-denied'))
            self.fence = decision['current']
            status, receipt = self.call('GET', '/continuations/' + command)
            if status != 200 or receipt.get('adapterReceipt') is None:
                raise PermissionError('receipt-unavailable')
            return receipt['adapterReceipt']['response']

    def publish(self, event):
        if event.get('params', {}).get('threadId') != self.session: return
        # Token deltas are superseded by complete items; they aren't accepted
        # business effects. Full message/tool/result records go through redaction.
        if event.get('method', '').endswith('/delta'): return
        path = self.adapter.observation(self, event) if self.active or self.revoked else None
        try: self.events.put_nowait((event, path))
        except queue.Full:
            self.active = False
            self.revoked = True
            if path is not None: self.adapter.retry_observations.add(path)

    def forward_events(self):
        while not self.closed:
            try: event, path = self.events.get(timeout=.5)
            except queue.Empty: continue
            try:
                if path is None:
                    pass  # Read-only viewers do not create another history branch.
                elif self.active and not self.revoked:
                    self.write({'kind': 'observation', 'event': event})
                    path.unlink(missing_ok=True)
                else:
                    self.adapter.quarantine_observation(path)
            except Exception:
                self.active = False
                self.revoked = True
                if path is not None: self.adapter.retry_observations.add(path)
            if not self.disconnected:
                try:
                    status, _ = self.call('GET', '')
                    if status == 200: self.publish_to_client(event)
                except Exception:
                    self.disconnected = True
            if event.get('method') == 'turn/completed':
                self.active = False
                if self.disconnected:
                    self.closed = True
                    self.adapter.clients.discard(self)
                    self.adapter.contexts.pop(id(self), None)

    def request(self, method, params):
        # No client can change the backend's sandbox, execute commands directly,
        # create an uncorrelated session, or install tools/configuration.
        status, _ = self.call('GET', '')
        if status != 200: raise PermissionError('repository-access-denied')
        if method == 'initialize': return self.adapter.runtime.initialized
        if method == 'account/read':
            result = self.adapter.runtime.request(method, {'refreshToken': False})
            if isinstance(result.get('account'), dict) and 'email' in result['account']:
                result['account']['email'] = '[managed runtime]'
            return result
        if method == 'thread/list':
            thread = self.adapter.runtime.request('thread/read', {'threadId': self.session})['thread']
            return {'data': [thread], 'nextCursor': None}
        if method in ('thread/read', 'thread/resume', 'thread/turns/list', 'thread/items/list'):
            if params.get('threadId') != self.session: raise PermissionError('wrong-session')
            safe = {key: value for key, value in params.items() if key in (
                'threadId', 'cursor', 'limit', 'sortDirection', 'includeTurns', 'turnId')}
            if method == 'thread/resume': safe.update(sandbox='read-only', approvalPolicy='never')
            return self.adapter.runtime.request(method, safe)
        if method == 'turn/start':
            if params.get('threadId') != self.session: raise PermissionError('wrong-session')
            if any(key not in ('threadId', 'input') for key in params):
                # UI supplies its defaults; explicit changes never reach Codex.
                allowed = {'threadId', 'input', 'cwd', 'approvalPolicy', 'sandboxPolicy', 'model',
                           'effort', 'summary', 'collaborationMode', 'personality', 'serviceTier',
                           'additionalContext', 'approvalsReviewer', 'clientUserMessageId', 'cyberAccessProgram',
                           'environments', 'multiAgentMode', 'outputSchema', 'permissions',
                           'responsesapiClientMetadata', 'runtimeWorkspaceRoots', 'serviceTierForTurn',
                           'toolOutput', 'turnTrigger'}
                if set(params) - allowed: raise PermissionError('unsupported-turn-override:' + ','.join(sorted(set(params) - allowed)))
            text = '\n'.join(item['text'] for item in params['input'] if item.get('type') == 'text')
            if not text or any(item.get('type') != 'text' for item in params['input']):
                raise PermissionError('only-text-input-supported')
            with self.lock:
                if any(c.active for c in self.adapter.contexts.values()): raise PermissionError('turn-already-active')
                self.active = True
                try: return self.write({'kind': 'prompt', 'text': text})
                except Exception:
                    self.active = False
                    raise
        if method == 'turn/interrupt':
            if params.get('threadId') != self.session: raise PermissionError('wrong-session')
            return self.write({'kind': 'interrupt', 'turnId': params['turnId']})
        reads = {'config/read', 'configRequirements/read', 'model/list', 'collaborationMode/list',
                 'experimentalFeature/list', 'mcpServerStatus/list', 'skills/list', 'hooks/list',
                 'plugin/list', 'account/rateLimits/read', 'thread/loaded/list'}
        if method not in reads: raise PermissionError('unsupported-native-method:' + method)
        if method in ('skills/list', 'hooks/list'):
            params = {'cwds': [str(self.adapter.repository)]}
        result = self.adapter.runtime.request(method, params)
        if method == 'config/read':
            result['config'].pop('mcp_servers', None)
            result['config'].pop('hooks', None)
            result['layers'] = None
        if method == 'thread/loaded/list': result['data'] = [self.session]
        return result


async def run_gateway(adapter):
    async def handler(socket):
        context = None
        try:
            credential = socket.request.headers.get('Authorization', '')
            if socket.request.path == '/' and credential.startswith('Bearer wpcp1.'):
                binding = json.loads(base64.urlsafe_b64decode(credential.removeprefix('Bearer wpcp1.')))
                session, credential = binding['sessionId'], binding['credential']
            else:
                session = socket.request.path.removeprefix('/sessions/')
            uuid.UUID(session)
            loop = asyncio.get_running_loop()
            def publish(event):
                asyncio.run_coroutine_threadsafe(socket.send(json.dumps(event)), loop).result(timeout=10)
            context = await asyncio.to_thread(NativeContext, adapter, session, credential, publish)
            adapter.clients.add(context); adapter.contexts[id(context)] = context
            async for raw in socket:
                message = json.loads(raw)
                if os.environ.get('WPCP_NATIVE_TRACE') == '1':
                    print('native method', message.get('method'), flush=True, file=sys.stderr)
                if 'id' not in message: continue
                try:
                    result = await asyncio.to_thread(context.request, message['method'], message.get('params') or {})
                    response = {'id': message['id'], 'result': result}
                except Exception as error:
                    if os.environ.get('WPCP_NATIVE_TRACE') == '1':
                        print('native error', type(error).__name__, str(error) if isinstance(error, PermissionError) else getattr(error, 'code', None), flush=True, file=sys.stderr)
                    reason = str(error) if isinstance(error, PermissionError) else 'native-request-unavailable'
                    response = {'id': message['id'], 'error': {'code': -32001, 'message': reason}}
                await socket.send(json.dumps(response))
        except Exception:
            await socket.close(code=1008, reason='Native session unavailable or unauthorized')
        finally:
            if context:
                context.disconnected = True
                if not context.active and adapter.active_turn is None:
                    adapter.clients.discard(context)
                    context.closed = True; adapter.contexts.pop(id(context), None)

    async with serve(handler, '127.0.0.1', adapter.native_port, max_size=1_000_000):
        await asyncio.Future()
