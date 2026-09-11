"""External deterministic fake with independent durable session receipts."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
import uuid
import time
import subprocess


def serve(port, database, scenario):
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE IF NOT EXISTS sessions (operation TEXT PRIMARY KEY, body TEXT NOT NULL)')

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

        def do_GET(self):
            with sqlite3.connect(database) as db:
                if self.path.startswith('/sessions/'):
                    row = db.execute('SELECT body FROM sessions WHERE operation=?', (self.path.split('/')[-1],)).fetchone()
                    return self.reply(200, json.loads(row[0])) if row else self.reply(404, {'code': 'session-not-found'})
                rows = db.execute('SELECT body FROM sessions').fetchall()
            self.reply(200, {'sessionCount': len(rows), 'sessions': [json.loads(r[0]) for r in rows]})

        def do_PUT(self):
            request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            operation = self.path.removeprefix('/sessions/')
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

    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--scenario', default='blocked')
    args = parser.parse_args()
    serve(args.port, args.database, args.scenario)
