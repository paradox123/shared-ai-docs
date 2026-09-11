"""Controlled external GitHub HTTP boundary; never an application membership list."""
import json
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class GitHubProviderFixture:
    def __init__(self):
        self.identities = {
            'actor-authorized': {'id': 101, 'type': 'User', 'read': True, 'push': True},
            'actor-observer': {'id': 102, 'type': 'User', 'read': True, 'push': False},
            'actor-contributor': {'id': 103, 'type': 'User', 'read': True, 'push': True},
            'actor-unauthorized': {'id': 104, 'type': 'User', 'read': False, 'push': False},
            'worker-bot': {'id': 105, 'type': 'Bot', 'read': True, 'push': True},
        }
        self.tokens = {actor: uuid.uuid4().hex for actor in self.identities}
        self.tokens['same-human-other-client'] = uuid.uuid4().hex
        self.identities['same-human-other-client'] = self.identities['actor-authorized']
        self.failure = None
        self.repository_id = 9001
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                actor = next((a for a, t in fixture.tokens.items()
                              if self.headers.get('Authorization') == f'Bearer {t}'), None)
                identity = fixture.identities.get(actor)
                status, payload = 404, {}
                if fixture.failure:
                    status, payload = fixture.failure, {'message': 'controlled upstream failure'}
                elif identity is None:
                    status = 401
                elif self.path == '/user':
                    status, payload = 200, {'id': identity['id'], 'type': identity['type'], 'login': actor}
                elif self.path == '/repos/pilot/fixture' and identity['read']:
                    status, payload = 200, {'id': fixture.repository_id, 'permissions': {
                        'pull': identity['read'], 'push': identity['push']}}
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode())

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.origin = f'http://127.0.0.1:{self.server.server_port}/'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
