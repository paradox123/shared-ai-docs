"""Independent HTTP provider with real bare Git ref read-back for publication tests."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading
import uuid
import struct
import zlib


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True,
                                   stderr=subprocess.PIPE).strip()


def probe(output='surface available'):
    return {'argv': [sys.executable, '-c', 'print(' + repr(output) + ')'], 'expected': output}


class PublicationFixture:
    def __init__(self, root, issue):
        self.root = Path(root)
        self.repo, self.remote = self.root / 'checkout', self.root / 'remote.git'
        self.repo.mkdir(parents=True)
        git(self.repo, 'init', '-q', '-b', 'main')
        git(self.repo, 'config', 'user.name', 'Pilot')
        git(self.repo, 'config', 'user.email', 'pilot@localhost')
        (self.repo / 'greeting.py').write_text('def greet(): return "Hello, Ada!"\n')
        git(self.repo, 'add', '.')
        git(self.repo, 'commit', '-qm', 'Base')
        self.base = git(self.repo, 'rev-parse', 'HEAD')
        subprocess.run(['git', 'init', '--bare', '-q', str(self.remote)], check=True)
        git(self.repo, 'remote', 'add', 'origin', str(self.remote))
        git(self.repo, 'push', '-q', 'origin', 'main')
        self.branch = 'codex/issue-' + str(issue)
        git(self.repo, 'switch', '-qc', self.branch)
        def chunk(kind, data): return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
        self.probe_image = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) +
                            chunk(b'IDAT', zlib.compress(b'\x00\xff\xff\xff')) + chunk(b'IEND', b''))
        self.records = set()
        self.pulls = []
        self.creates = 0
        self.allowed = True
        self.lose_reply = False
        self.agent_content = 'def greet(): return "Hello, Ada!"  # implemented\n'
        self.agent_starts = 0
        self.result_summary = 'Greeting implemented'
        self.adapter_path = str(self.repo)
        self.session = str(uuid.uuid4())
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_): pass
            def send(self, value, status=200):
                body = json.dumps(value).encode()
                self.send_response(status)
                self.send_header('Content-Length', str(len(body)))
                self.end_headers(); self.wfile.write(body)
            def do_GET(self):
                path = self.path.split('?')[0]
                if path == '/image-ready':
                    body = fixture.probe_image; self.send_response(200)
                    self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
                if path == '/business': return self.send({'count': len(fixture.records)})
                if path in ('/image', '/document'):
                    file = fixture.root / ('evidence.png' if path == '/image' else 'document.html')
                    if not file.exists(): return self.send({}, 404)
                    body = file.read_bytes(); self.send_response(200)
                    self.send_header('Content-Type', 'image/png' if path == '/image' else 'text/html')
                    self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
                if path == '/app':
                    body = b'''<!doctype html><title>Publication evidence</title><h1>Records: 0</h1>
<button onclick="fetch('/business',{method:'POST',body:JSON.stringify({id:'one'})}).then(r=>r.json()).then(r=>document.querySelector('h1').textContent='Records: '+r.count)">Create record</button>'''
                    self.send_response(200); self.send_header('Content-Type', 'text/html')
                    self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
                if path == '/publication-readiness':
                    return self.send({'contractVersion': 'AgentSessionAdapter/v1', 'localPath': fixture.adapter_path,
                        'runtimeReady': True, 'sandboxReady': True})
                if path == '/repos/pilot/fixture':
                    return self.send({'id': 9001, 'full_name': 'pilot/fixture', 'clone_url': str(fixture.remote),
                        'permissions': {'push': fixture.allowed}})
                if path.startswith('/repos/pilot/fixture/commits/'):
                    branch = path.removeprefix('/repos/pilot/fixture/commits/')
                    from urllib.parse import unquote
                    try: sha = git(fixture.remote, 'rev-parse', 'refs/heads/' + unquote(branch))
                    except subprocess.CalledProcessError: return self.send({}, 404)
                    return self.send({'sha': sha})
                if path == '/repos/pilot/fixture/pulls': return self.send(fixture.pulls)
                if path.startswith('/repos/pilot/fixture/pulls/'):
                    return self.send(fixture.pulls[int(path.rsplit('/', 1)[1]) - 1])
                return self.send({}, 404)
            def do_PUT(self):
                request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                fixture.agent_starts += 1
                (fixture.repo / 'greeting.py').write_text(fixture.agent_content)
                observation = {'command': 'python greeting.py', 'observed': 'Hello, Ada!'}
                result = {'schema_version': '3', 'outcome': 'completed', 'summary': fixture.result_summary,
                    'red_green_slices': [{'requirement': 'AC1', 'red': {**observation, 'observed': 'Wrong greeting'}, 'green': observation}],
                    'changed_files': ['greeting.py'], 'verification': [observation], 'findings': [], 'intervention': None,
                    'evidence': [{'criterion': 'AC1', 'verdict': 'pass', 'kind': 'background',
                        'observed_interface': 'greet', 'expected_result': 'Hello, Ada!',
                        'observations': [{'phase': 'read_back', 'description': 'Greeting returned',
                            'artifact': 'Hello, Ada!', 'correlation_id': None}]}]}
                return self.send({'contractVersion': 'AgentSessionAdapter/v1',
                    'operationKey': self.path.split('/')[-1], 'sessionId': fixture.session,
                    'events': [{'sequence': 1, 'type': 'result', 'data': result}]})
            def do_POST(self):
                if self.path == '/business':
                    request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                    fixture.records.add(request['id'])
                    return self.send({'count': len(fixture.records)})
                if self.path != '/repos/pilot/fixture/pulls': return self.send({}, 404)
                request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                fixture.creates += 1
                pull = {'number': fixture.creates, 'state': 'open', 'draft': request['draft'],
                    'body': request['body'], 'title': request['title'],
                    'html_url': fixture.origin + '/pull/' + str(fixture.creates),
                    'head': {'ref': request['head'], 'sha': git(fixture.remote, 'rev-parse', 'refs/heads/' + request['head']),
                             'repo': {'id': 9001}},
                    'base': {'ref': request['base'], 'repo': {'id': 9001}}}
                fixture.pulls.append(pull)
                if fixture.lose_reply:
                    self.close_connection = True
                    return
                self.send(pull, 201)

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.origin = f'http://127.0.0.1:{self.server.server_port}'
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.plan = {'schemaVersion': 'wpcp-publication-plan/v1',
            'repository': {'repositoryId': 'repo-1', 'fullName': 'pilot/fixture', 'providerRepositoryId': 9001},
            'issueNumber': issue, 'localPath': str(self.repo), 'remoteName': 'origin',
            'baseBranch': 'main', 'branch': self.branch, 'expectedBaseSha': self.base,
            'providerOrigin': self.origin, 'title': 'Implement greeting',
            'agentOrigin': self.origin,
            'prerequisites': {name: probe() for name in ('contract', 'tools', 'dependencies', 'access', 'sandbox')},
            'criteria': [{'id': 'AC1', 'description': 'Greeting is readable', 'kind': 'command',
                'surface': 'python greeting public function', 'expectedReadBack': 'Hello, Ada!',
                'phases': [{'name': 'read-back', 'probe': probe(),
                    'execute': {'argv': [sys.executable, '-c', 'from greeting import greet; print(greet())'],
                                'expected': 'Hello, Ada!'}}]}]}
        self.path = self.root / 'plan.json'
        self.save()

    def save(self): self.path.write_text(json.dumps(self.plan))
    def close(self): self.server.shutdown(); self.server.server_close()
