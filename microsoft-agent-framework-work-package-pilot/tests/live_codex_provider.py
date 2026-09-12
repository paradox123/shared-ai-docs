"""External active-operation fixture: durable receipts and real child processes.

Only loopback tests use this provider. It has no repository write capability.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
import subprocess
import sys
import threading


def serve(port, database, scenario):
    lock = threading.RLock()
    children = {}
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE IF NOT EXISTS operations (key TEXT PRIMARY KEY, intent TEXT NOT NULL, receipt TEXT NOT NULL)')

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

        def body(self):
            return json.loads(self.rfile.read(int(self.headers['Content-Length'])))

        def do_GET(self):
            with lock, sqlite3.connect(database) as db:
                records = [json.loads(row[0]) for row in db.execute('SELECT receipt FROM operations ORDER BY rowid')]
                if self.path == '/diagnostics':
                    return self.reply(200, {'operations': records, 'operationCount': len(records),
                        'alive': [key for key, child in children.items() if child.poll() is None]})
                key = self.path.removeprefix('/operations/')
                record = next((r for r in records if r['operationKey'] == key), None)
                self.reply(200, record) if record else self.reply(404, {'code': 'operation-not-found'})

        def stop_child(self, key):
            child = children.get(key)
            if child is not None and child.poll() is None:
                child.terminate()
                child.wait(timeout=5)

        def do_PUT(self):
            intent = self.body()
            key = self.path.removeprefix('/operations/')
            with lock, sqlite3.connect(database) as db:
                row = db.execute('SELECT intent, receipt FROM operations WHERE key=?', (key,)).fetchone()
                if row:
                    if json.loads(row[0]) != intent:
                        return self.reply(409, {'code': 'intent-conflict'})
                    return self.reply(200, json.loads(row[1]))
                child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(3600)'],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                children[key] = child
                receipt = dict(intent, contractVersion='AgentSessionAdapter/v1', operationKey=key,
                    processStatus='running', processId=str(child.pid), response=None)
                db.execute('INSERT INTO operations VALUES (?, ?, ?)', (key, json.dumps(intent), json.dumps(receipt)))
                self.reply(200, receipt)

        def do_POST(self):
            body = self.body()
            parts = self.path.strip('/').split('/')
            if len(parts) != 3 or parts[0] != 'operations' or parts[2] not in ('stop', 'complete'):
                return self.reply(404, {'code': 'route-not-found'})
            _, key, action = parts
            with lock, sqlite3.connect(database) as db:
                row = db.execute('SELECT intent, receipt FROM operations WHERE key=?', (key,)).fetchone()
                if row:
                    intent, receipt = map(json.loads, row)
                    if action == 'stop' and intent != body:
                        return self.reply(409, {'code': 'intent-conflict'})
                elif action == 'stop':
                    intent = body
                    receipt = dict(intent, contractVersion='AgentSessionAdapter/v1', operationKey=key,
                        processStatus='start-pending', processId=None, response=None)
                else:
                    return self.reply(404, {'code': 'operation-not-found'})
                self.stop_child(key)
                if action == 'stop':
                    receipt.update(processStatus='stopped', reconciliation='reconciled', effects=[])
                    if scenario == 'wrong-process':
                        receipt['processId'] = 'unrelated-process'
                    if scenario == 'conflicting-effects':
                        receipt['effects'] = [{'status': 'conflict'}]
                elif receipt['processStatus'] != 'stopped':
                    receipt.update(processStatus='completed', response={'text': 'answer: ' + intent['message']},
                        reconciliation='reconciled', effects=[])
                db.execute('INSERT INTO operations VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET receipt=excluded.receipt',
                    (key, json.dumps(intent), json.dumps(receipt)))
                self.reply(200, receipt)

    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--scenario', default='normal')
    args = parser.parse_args()
    serve(args.port, args.database, args.scenario)
