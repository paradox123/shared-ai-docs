"""Independent controlled provider: real bare Git head and durable effect receipts."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
import subprocess
import uuid


def serve(port, database, repository):
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE IF NOT EXISTS effects (operation TEXT PRIMARY KEY, receipt TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS completed (issue INTEGER PRIMARY KEY)')
        db.execute('CREATE TABLE IF NOT EXISTS faults (operation TEXT PRIMARY KEY, mode TEXT NOT NULL)')

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, status, value):
            data = json.dumps(value).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            with sqlite3.connect(database) as db:
                if self.path == '/base':
                    head = subprocess.check_output(['git', '--git-dir', repository, 'rev-parse', 'refs/heads/main'], text=True).strip()
                    return self.reply(200, {'contractVersion': 'RepositoryEffects/v1',
                        'repository': {'repositoryId': 'repo-1', 'fullName': 'pilot/fixture', 'providerRepositoryId': 9001},
                        'headSha': head, 'completedIssues': [row[0] for row in db.execute('SELECT issue FROM completed')]})
                if self.path.startswith('/effects/'):
                    row = db.execute('SELECT receipt FROM effects WHERE operation=?', (self.path.split('/')[-1],)).fetchone()
                    operation = self.path.split('/')[-1]
                    fault = db.execute('SELECT mode FROM faults WHERE operation=?', (operation,)).fetchone()
                    mode = fault[0] if fault else 'none'
                    if mode == 'unavailable':
                        return self.reply(503, {'code': 'controlled-outage'})
                    receipts = [json.loads(row[0])] if row else []
                    if receipts and mode == 'ambiguous':
                        receipts.append(dict(receipts[0], receiptId=str(uuid.uuid5(uuid.NAMESPACE_URL, operation)),
                            target='wpcp-controlled-secret-canary-v1'))
                    if receipts and mode == 'conflict':
                        receipts[0]['headSha'] = 'f' * 40
                    return self.reply(200, {'receipts': receipts})
                rows = [json.loads(row[0]) for row in db.execute('SELECT receipt FROM effects')]
                return self.reply(200, {'effectCount': len(rows), 'effects': rows})

        def do_PUT(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            with sqlite3.connect(database) as db:
                if self.path.startswith('/faults/'):
                    db.execute('INSERT OR REPLACE INTO faults VALUES (?,?)', (self.path.split('/')[-1], body['mode']))
                    return self.reply(200, {'configured': body['mode']})
                if self.path.startswith('/completed/'):
                    db.execute('INSERT OR IGNORE INTO completed VALUES (?)', (int(self.path.split('/')[-1]),))
                    return self.reply(200, {'completed': True})
                operation = self.path.split('/')[-1]
                receipt = dict(body, receiptId=str(uuid.uuid4()), contractVersion='RepositoryEffects/v1')
                db.execute('INSERT OR IGNORE INTO effects VALUES (?,?)', (operation, json.dumps(receipt)))
                stored = json.loads(db.execute('SELECT receipt FROM effects WHERE operation=?', (operation,)).fetchone()[0])
                if any(stored.get(k) != body.get(k) for k in body):
                    return self.reply(409, {'code': 'effect-intent-conflict'})
            return self.reply(200, {'receipts': [stored]})

    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--database', required=True)
    parser.add_argument('--repository', required=True)
    options = parser.parse_args()
    serve(options.port, options.database, options.repository)
