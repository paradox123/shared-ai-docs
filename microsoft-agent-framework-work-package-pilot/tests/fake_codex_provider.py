"""External deterministic fake with independent durable session receipts."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
import uuid
import time
import subprocess


OPEN_MODES = ('same-session', 'handoff-confirmation-required', 'unsupported')
CONTINUATION_ACTIONS = ('resume', 'fork', 'fresh-retry', 'handoff')


def open_in_codex_capability(open_mode):
    if open_mode == 'same-session':
        return {
            'mode': open_mode,
            'sameSession': True,
            'appTaskVisible': False,
            'reason': 'controlled-fake-same-session-receipt-only',
            'url': None,
        }
    if open_mode == 'handoff-confirmation-required':
        return {
            'mode': open_mode,
            'sameSession': False,
            'appTaskVisible': False,
            'reason': 'controlled-fake-requires-explicit-handoff',
            'url': None,
        }
    return {
        'mode': 'unsupported',
        'sameSession': False,
        'appTaskVisible': False,
        'reason': 'fake-adapter-has-no-codex-app-session',
        'url': None,
    }


def serve(port, database, scenario, open_mode='unsupported', capability_reason=None):
    if open_mode not in OPEN_MODES:
        raise ValueError('Unsupported open mode: ' + open_mode)
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE IF NOT EXISTS sessions (operation TEXT PRIMARY KEY, body TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS continuations (operation TEXT PRIMARY KEY, body TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS continuation_faults (operation TEXT PRIMARY KEY)')
        db.execute('CREATE TABLE IF NOT EXISTS interaction_faults (operation TEXT PRIMARY KEY)')
        db.execute('CREATE TABLE IF NOT EXISTS opens (operation TEXT PRIMARY KEY, session_id TEXT NOT NULL, body TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS interactions (operation TEXT PRIMARY KEY, body TEXT NOT NULL)')

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def read_request(self):
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size <= 0:
                    raise ValueError()
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError()
                return body
            except (TypeError, ValueError, json.JSONDecodeError):
                self.reply(400, {'code': 'invalid-request'})
                return None

        @staticmethod
        def record_for_session_id(db, session_id):
            for table in ('sessions', 'continuations'):
                for (body,) in db.execute(f'SELECT body FROM {table}'):
                    record = json.loads(body)
                    if record.get('sessionId') == session_id:
                        return record
            return None

        @staticmethod
        def resource_path(path, prefix):
            if not path.startswith(prefix):
                return None
            resource = path.removeprefix(prefix)
            return resource if resource and '/' not in resource else None

        def diagnostics(self):
            with sqlite3.connect(database) as db:
                sessions = [json.loads(row[0]) for row in db.execute('SELECT body FROM sessions')]
                continuations = [json.loads(row[0]) for row in db.execute('SELECT body FROM continuations')]
                opens = [json.loads(row[0]) for row in db.execute('SELECT body FROM opens')]
                interactions = [json.loads(row[0]) for row in db.execute('SELECT body FROM interactions')]
            self.reply(200, {
                'openMode': open_mode,
                'sessionCount': len(sessions),
                'sessions': sessions,
                'continuationCount': len(continuations),
                'continuations': continuations,
                'openCount': len(opens),
                'opens': opens,
                'interactionCount': len(interactions),
                'interactions': interactions,
            })

        def do_GET(self):
            with sqlite3.connect(database) as db:
                if self.path.startswith('/sessions/'):
                    row = db.execute('SELECT body FROM sessions WHERE operation=?', (self.path.split('/')[-1],)).fetchone()
                    return self.reply(200, json.loads(row[0])) if row else self.reply(404, {'code': 'session-not-found'})
            self.diagnostics()

        def do_PUT(self):
            request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            operation = self.path.removeprefix('/sessions/')
            capability = open_in_codex_capability(open_mode)
            if capability_reason is not None:
                capability['reason'] = capability_reason
            session = {
                'contractVersion': 'AgentSessionAdapter/v1',
                'operationKey': operation, 'sessionId': str(uuid.uuid4()),
                'events': [
                    {'sequence': 1, 'type': 'message', 'data': {'text': '1: inspect ' + request['note']}},
                    {'sequence': 2, 'type': 'tool-call', 'data': {'callId': 'tool-1', 'name': 'inspect', 'argument': request['note']}},
                    {'sequence': 3, 'type': 'tool-result', 'data': {'callId': 'tool-1', 'output': request['note']}},
                    {'sequence': 4, 'type': 'artifact', 'data': {'uri': 'fake://report', 'description': request['note']}},
                    {'sequence': 5, 'type': 'result', 'data': {'schemaVersion': 'fake-worker-result/v1', 'status': 'blocked', 'reason': 'Controlled blocker ' + request['note']}},
                ],
                'openInCodex': capability,
            }
            with sqlite3.connect(database) as db:
                db.execute('INSERT OR IGNORE INTO sessions VALUES (?, ?)', (operation, json.dumps(session)))
                stored = json.loads(db.execute('SELECT body FROM sessions WHERE operation = ?', (operation,)).fetchone()[0])
            if scenario == 'timeout':
                time.sleep(2)
            if scenario == 'transport-failure':
                self.connection.close()
                return
            if scenario == 'infrastructure-failure':
                self.reply(503, {'error': request['note']})
                return
            if scenario == 'contract-incompatible':
                stored['contractVersion'] = 'AgentSessionAdapter/v99'
            if scenario == 'schema-failure':
                stored['events'][-1]['data'] = {'status': 'blocked', 'reason': request['note']}
            if scenario == 'wrong-operation':
                stored['operationKey'] = str(uuid.uuid4())
            if scenario == 'sequence-gap':
                stored['events'][1]['sequence'] = 3
            if scenario == 'conflicting-replay':
                stored['events'][1]['sequence'] = 1
            if scenario == 'null-event':
                stored['events'][1] = None
            if scenario == 'malformed-json':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{invalid')
                return
            if scenario == 'process-failure':
                child = subprocess.run(['python3', '-c', 'raise SystemExit(17)'], capture_output=True)
                stored['events'][-1] = {'sequence': 5, 'type': 'process-exit',
                    'data': {'exitCode': child.returncode, 'stderr': request['note']}}
            self.reply(200, stored)

        def do_POST(self):
            continuation_operation = self.resource_path(self.path, '/continuations/')
            if continuation_operation is not None:
                request = self.read_request()
                if request is not None:
                    self.continue_session(continuation_operation, request)
                return

            interaction_prefix = '/sessions/'
            if self.path.startswith(interaction_prefix) and '/interactions/' in self.path:
                session_id, operation = self.path.removeprefix(interaction_prefix).split('/interactions/', 1)
                if session_id and operation and '/' not in session_id and '/' not in operation:
                    request = self.read_request()
                    if request is not None:
                        self.interact(session_id, operation, request)
                    return

            if self.path.startswith('/sessions/') and self.path.endswith('/open'):
                session_id = self.path.removeprefix('/sessions/').removesuffix('/open')
                if session_id and '/' not in session_id:
                    request = self.read_request()
                    if request is not None:
                        self.open_session(session_id, request)
                    return
            self.reply(404, {'code': 'route-not-found'})

        def continue_session(self, operation, request):
            source_session_id = request.get('sourceSessionId')
            action = request.get('action')
            if not isinstance(source_session_id, str) or not source_session_id or action not in CONTINUATION_ACTIONS:
                self.reply(400, {'code': 'invalid-continuation-request'})
                return

            parent_session_id = source_session_id if action in ('fork', 'handoff') else None
            with sqlite3.connect(database) as db:
                stored = db.execute('SELECT body FROM continuations WHERE operation=?', (operation,)).fetchone()
                if stored:
                    continuation = json.loads(stored[0])
                    if continuation['sourceSessionId'] != source_session_id or continuation['action'] != action:
                        self.reply(409, {'code': 'continuation-intent-conflict'})
                        return
                    self.reply(200, continuation)
                    return
                if self.record_for_session_id(db, source_session_id) is None:
                    self.reply(404, {'code': 'session-not-found'})
                    return
                session_id = source_session_id if action == 'resume' else str(uuid.uuid4())
                capability = open_in_codex_capability('same-session' if action == 'handoff' else open_mode)
                if action == 'handoff':
                    capability['reason'] = 'controlled-fake-handoff-session-receipt-only'
                continuation = {
                    'contractVersion': 'AgentSessionAdapter/v1',
                    'operationKey': operation,
                    'sessionId': session_id,
                    'sourceSessionId': source_session_id,
                    'parentSessionId': parent_session_id,
                    'action': action,
                    'events': [{
                        'sequence': 1,
                        'type': 'continuation',
                        'data': {
                            'sourceSessionId': source_session_id,
                            'parentSessionId': parent_session_id,
                            'action': action,
                        },
                    }],
                    'openInCodex': capability,
                }
                db.execute('INSERT OR IGNORE INTO continuations VALUES (?, ?)', (operation, json.dumps(continuation)))
                continuation = json.loads(
                    db.execute('SELECT body FROM continuations WHERE operation=?', (operation,)).fetchone()[0])
            if continuation['sourceSessionId'] != source_session_id or continuation['action'] != action:
                self.reply(409, {'code': 'continuation-intent-conflict'})
                return
            if scenario == 'continuation-success-gap':
                with sqlite3.connect(database) as db:
                    first_delivery = db.execute(
                        'INSERT OR IGNORE INTO continuation_faults VALUES (?)', (operation,)).rowcount == 1
                if first_delivery:
                    # The controlled fault is deliberately after durable adapter
                    # success and before any HTTP receipt reaches the API.
                    self.connection.close()
                    return
            if scenario == 'continuation-wrong-operation':
                response = dict(continuation)
                response['operationKey'] = str(uuid.uuid4())
                self.reply(200, response)
                return
            if scenario == 'continuation-reuses-source-session' and action != 'resume':
                response = dict(continuation)
                response['sessionId'] = source_session_id
                self.reply(200, response)
                return
            if scenario == 'continuation-contract-incompatible':
                response = dict(continuation)
                response['contractVersion'] = 'AgentSessionAdapter/v99'
                self.reply(200, response)
                return
            self.reply(200, continuation)

        def open_session(self, session_id, request):
            operation = request.get('operationKey')
            if not isinstance(operation, str):
                self.reply(400, {'code': 'invalid-open-request'})
                return
            try:
                uuid.UUID(operation)
            except ValueError:
                self.reply(400, {'code': 'invalid-open-request'})
                return
            with sqlite3.connect(database) as db:
                stored = db.execute('SELECT session_id, body FROM opens WHERE operation=?', (operation,)).fetchone()
                if stored:
                    if stored[0] != session_id:
                        self.reply(409, {'code': 'open-intent-conflict'})
                        return
                    self.reply(200, json.loads(stored[1]))
                    return
                session = self.record_for_session_id(db, session_id)
                if session is None:
                    self.reply(404, {'code': 'session-not-found'})
                    return
                capability = session.get('openInCodex', open_in_codex_capability(open_mode))
                receipt = {
                    'contractVersion': 'AgentSessionAdapter/v1',
                    'operationKey': operation,
                    'sessionId': session_id,
                    'opened': capability['mode'] == 'same-session',
                    'openInCodex': capability,
                }
                db.execute('INSERT OR IGNORE INTO opens VALUES (?, ?, ?)', (operation, session_id, json.dumps(receipt)))
                receipt = json.loads(db.execute('SELECT body FROM opens WHERE operation=?', (operation,)).fetchone()[0])
            if scenario == 'open-wrong-operation':
                response = dict(receipt)
                response['operationKey'] = str(uuid.uuid4())
                self.reply(200, response)
                return
            if scenario == 'open-contract-incompatible':
                response = dict(receipt)
                response['contractVersion'] = 'AgentSessionAdapter/v99'
                self.reply(200, response)
                return
            self.reply(200, receipt)

        def interact(self, session_id, operation, request):
            message = request.get('message', request.get('text'))
            if not isinstance(message, str) or not message:
                self.reply(400, {'code': 'invalid-interaction-request'})
                return
            with sqlite3.connect(database) as db:
                stored = db.execute('SELECT body FROM interactions WHERE operation=?', (operation,)).fetchone()
                if stored:
                    interaction = json.loads(stored[0])
                    if interaction['sessionId'] != session_id or interaction['message'] != message:
                        self.reply(409, {'code': 'interaction-intent-conflict'})
                        return
                    self.reply(200, interaction)
                    return
                if self.record_for_session_id(db, session_id) is None:
                    self.reply(404, {'code': 'session-not-found'})
                    return
                opened = db.execute('SELECT body FROM opens WHERE session_id=?', (session_id,)).fetchone()
                if opened is None or not json.loads(opened[0]).get('opened'):
                    self.reply(409, {'code': 'session-not-open'})
                    return
                interaction = {
                    'contractVersion': 'AgentSessionAdapter/v1',
                    'operationKey': operation,
                    'sessionId': session_id,
                    'message': message,
                    'events': [
                        {'sequence': 1, 'type': 'message', 'data': {'text': message}},
                        {'sequence': 2, 'type': 'tool-call', 'data': {
                            'callId': 'interaction-' + operation,
                            'name': 'continue-session',
                            'argument': message,
                        }},
                        {'sequence': 3, 'type': 'tool-result', 'data': {
                            'callId': 'interaction-' + operation,
                            'output': 'accepted',
                        }},
                    ],
                }
                db.execute('INSERT OR IGNORE INTO interactions VALUES (?, ?)', (operation, json.dumps(interaction)))
                interaction = json.loads(
                    db.execute('SELECT body FROM interactions WHERE operation=?', (operation,)).fetchone()[0])
            if interaction['sessionId'] != session_id or interaction['message'] != message:
                self.reply(409, {'code': 'interaction-intent-conflict'})
                return
            if scenario == 'interaction-success-gap':
                with sqlite3.connect(database) as db:
                    first_delivery = db.execute(
                        'INSERT OR IGNORE INTO interaction_faults VALUES (?)', (operation,)).rowcount == 1
                if first_delivery:
                    self.connection.close()
                    return
            if scenario == 'interaction-wrong-operation':
                response = dict(interaction)
                response['operationKey'] = str(uuid.uuid4())
                self.reply(200, response)
                return
            if scenario == 'interaction-wrong-message':
                response = dict(interaction)
                response['message'] = 'adapter-substituted-message'
                self.reply(200, response)
                return
            if scenario == 'interaction-contract-incompatible':
                response = dict(interaction)
                response['contractVersion'] = 'AgentSessionAdapter/v99'
                self.reply(200, response)
                return
            self.reply(200, interaction)

    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--scenario', default='blocked')
    parser.add_argument('--open-mode', choices=OPEN_MODES, default='unsupported')
    parser.add_argument('--capability-reason')
    args = parser.parse_args()
    serve(args.port, args.database, args.scenario, args.open_mode, args.capability_reason)
