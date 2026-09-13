"""Deterministic trusted-plan runner. PostgreSQL worker owns dispatch/recovery state."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import selectors
import time
import shutil
import struct
import zlib
import subprocess
import sys
import urllib.request
import urllib.parse

PHASES = {'command': ['read-back'], 'rest': ['request', 'response', 'read-back'],
          'ui': ['interaction', 'screenshot', 'read-back'],
          'idempotency': ['request', 'response', 'repeat', 'read-back'],
          'document': ['generate', 'render', 'inspect', 'read-back'],
          'negative-gate': ['rejection', 'read-back'], 'recovery': ['restart', 'read-back'],
          'background': ['request', 'read-back']}
PREREQUISITES = {'contract', 'tools', 'dependencies', 'access', 'sandbox'}


class Blocked(Exception):
    def __init__(self, message, **details):
        super().__init__(message)
        self.details = details


def run_command(argv, cwd, env=None, timeout=30, strip_output=True):
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
        raise Blocked('invalid-command')
    environment = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR', 'LANG') if k in os.environ}
    environment.update(PYTHONDONTWRITEBYTECODE='1', GIT_TERMINAL_PROMPT='0', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
    environment.update(env or {})
    supervised = [sys.executable, str(Path(__file__).resolve()), '--supervise-command',
                  str(os.getpid()), os.environ.get('WPCP_PUBLICATION_OWNER_PID', str(os.getpid())),
                  str(timeout), *argv]
    process = subprocess.Popen(supervised, cwd=cwd, env=environment, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    output = bytearray()
    total = 0
    deadline = time.monotonic() + timeout
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ, True)
            selector.register(process.stderr, selectors.EVENT_READ, False)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0: raise Blocked('command-timeout')
                for key, _ in selector.select(remaining):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    total += len(chunk)
                    if total > 1024 * 1024: raise Blocked('command-output-limit')
                    if key.data: output.extend(chunk)
        process.wait(timeout=max(.01, deadline - time.monotonic()))
        if process.returncode != 0: raise Blocked('command-failed')
        decoded = output.decode('utf-8')
        return decoded.strip() if strip_output else decoded
    finally:
        try: os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        process.wait()
        process.stdout.close()
        process.stderr.close()



def git(plan, *args, raw=False):
    return run_command(['git', '-c', 'core.hooksPath=/dev/null', '-C', plan['localPath'], *args],
                       plan['localPath'], strip_output=not raw)


def checked(command, plan, head=None):
    output = run_command(command['argv'], plan['localPath'], {'WPCP_EVIDENCE_HEAD': head or ''})
    if output != command['expected']:
        raise Blocked('business-assertion-failed')
    return {'argv': command['argv'], 'expected': command['expected'], 'observed': output}


def validate(plan, correlation):
    def require(condition):
        if not condition: raise Blocked('invalid-evidence-plan')
    try:
        require(plan['schemaVersion'] == 'wpcp-publication-plan/v1')
        require(plan['repository'] == correlation['repository'])
        require(plan['issueNumber'] == correlation['issueNumber'])
        require(Path(plan['localPath']).is_absolute() and Path(plan['localPath']).is_dir())
        require(re.fullmatch(r'[0-9a-f]{40}', plan['expectedBaseSha']))
        require(re.fullmatch(r'[A-Za-z0-9_-]+', plan['remoteName']))
        require(plan['branch'] != plan['baseBranch'])
        for name in ('branch', 'baseBranch'):
            git(plan, 'check-ref-format', 'refs/heads/' + plan[name])
        origin = urllib.parse.urlsplit(plan['providerOrigin'])
        require(origin.scheme == 'https' or (origin.scheme == 'http' and origin.hostname in ('127.0.0.1', 'localhost')))
        require(not origin.username and not origin.password and origin.path in ('', '/') and not origin.query and not origin.fragment)
        require(PREREQUISITES <= set(plan['prerequisites']))
        require(isinstance(plan['title'], str) and plan['title'].strip())
        require(plan['criteria'] and len({c['id'] for c in plan['criteria']}) == len(plan['criteria']))
        commands = list(plan['prerequisites'].values())
        for criterion in plan['criteria']:
            require(all(isinstance(criterion[k], str) and criterion[k].strip() for k in ('id', 'description', 'surface', 'expectedReadBack')))
            require([p['name'] for p in criterion['phases']] == PHASES[criterion['kind']])
            require(criterion['phases'][-1]['execute']['expected'] == criterion['expectedReadBack'])
            for phase in criterion['phases']:
                if phase['name'] == 'screenshot':
                    require(Path(phase['imagePath']).is_absolute())
                    target = urllib.parse.urlsplit(phase['imageUrl'])
                    probe_url = urllib.parse.urlsplit(phase['probeImageUrl'])
                    require(target.scheme in ('http', 'https') and target.hostname)
                    require(not target.username and not target.password and not target.fragment)
                    require((target.scheme, target.netloc) == (probe_url.scheme, probe_url.netloc))
                    require(not probe_url.fragment)
                    require(re.fullmatch(r'[0-9a-f]{64}', phase['probeImageSha256']))
                commands.extend([phase['probe'], phase['execute']])
        for command in commands:
            require(isinstance(command['argv'], list) and command['argv'] and all(isinstance(a, str) and a for a in command['argv']))
            require(isinstance(command['expected'], str) and command['expected'].strip())
        if 'headQualification' in plan:
            from head_qualification import validate_config
            validate_config(plan['headQualification'])
    except (KeyError, TypeError, ValueError, Blocked):
        raise Blocked('invalid-evidence-plan') from None


class Provider:
    def __init__(self, plan):
        self.plan = plan
        self.origin = plan['providerOrigin'].rstrip('/')
        self.prefix = '/repos/' + plan['repository']['fullName']

    def request(self, path, body=None, method=None):
        headers = {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'}
        if self.origin == 'https://api.github.com' and os.environ.get('WPCP_PUBLICATION_TOKEN'):
            headers['Authorization'] = 'Bearer ' + os.environ['WPCP_PUBLICATION_TOKEN']
        request = urllib.request.Request(self.origin + self.prefix + path,
            None if body is None else json.dumps(body).encode(), headers,
            method=method or ('GET' if body is None else 'POST'))
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)

    def check_repository(self):
        repo = self.request('')
        if repo.get('id') != self.plan['repository']['providerRepositoryId'] or repo.get('full_name') != self.plan['repository']['fullName']:
            raise Blocked('provider-repository-mismatch')
        if repo.get('permissions', {}).get('push') is not True:
            raise Blocked('provider-write-access-unavailable')
        permitted = {url for name in ('clone_url', 'ssh_url') if isinstance(url := repo.get(name), str) and url}
        fetch = git(self.plan, 'remote', 'get-url', '--all', self.plan['remoteName']).splitlines()
        push = git(self.plan, 'remote', 'get-url', '--push', '--all', self.plan['remoteName']).splitlines()
        if len(fetch) != 1 or len(push) != 1 or fetch[0] not in permitted or push[0] not in permitted:
            raise Blocked('git-remote-repository-mismatch')

    def head(self, branch):
        return self.request('/commits/' + urllib.parse.quote(branch, safe=''))['sha']


def base_check(plan, provider):
    provider.check_repository()
    expected = plan['expectedBaseSha']
    local = git(plan, 'rev-parse', '--verify', 'refs/heads/' + plan['baseBranch'])
    remote = git(plan, 'ls-remote', '--exit-code', plan['remoteName'], 'refs/heads/' + plan['baseBranch']).split()[0]
    actual = provider.head(plan['baseBranch'])
    if not expected == local == remote == actual:
        raise Blocked('repository-base-mismatch')
    if git(plan, 'branch', '--show-current') != plan['branch']:
        raise Blocked('repository-branch-mismatch')
    git(plan, 'merge-base', '--is-ancestor', expected, 'HEAD')
    return {'expected': expected, 'local': local, 'remote': remote, 'provider': actual}


def agent_readiness(plan):
    origin = plan['agentOrigin'].rstrip('/')
    parsed = urllib.parse.urlsplit(origin)
    if parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1') or parsed.username or parsed.password:
        raise Blocked('agent-origin-invalid')
    headers = {}
    if origin == os.environ.get('WPCP_REAL_ADAPTER_ORIGIN', '').rstrip('/'):
        headers['X-Wpcp-Adapter-Token'] = os.environ.get('WPCP_REAL_ADAPTER_TOKEN', '')
    request = urllib.request.Request(origin + '/publication-readiness', headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        readiness = json.load(response)
    if (readiness.get('contractVersion') != 'AgentSessionAdapter/v1' or
        Path(readiness.get('localPath', '')).resolve() != Path(plan['localPath']).resolve() or readiness.get('runtimeReady') is not True or
        readiness.get('sandboxReady') is not True):
        raise Blocked('agent-readiness-mismatch')
    if readiness.get('activeTurn'): raise Blocked('agent-turn-active')
    return readiness


def preflight(plan, correlation):
    validate(plan, correlation)
    from codex_contract import canonical_schema
    from jsonschema import Draft202012Validator
    Draft202012Validator.check_schema(canonical_schema())
    observations = []
    base = base_check(plan, Provider(plan))
    if git(plan, 'status', '--porcelain'):
        raise Blocked('initial-worktree-dirty')
    for name, command in plan['prerequisites'].items():
        try: observation = checked(command, plan)
        except Exception: raise Blocked('prerequisite-failed:' + name) from None
        observations.append({'prerequisite': name, **observation})
    for criterion in plan['criteria']:
        for phase in criterion['phases']:
            try:
                if not shutil.which(phase['execute']['argv'][0]): raise Blocked('tool-unavailable')
                observation = checked(phase['probe'], plan)
                if phase['name'] == 'screenshot':
                    image = read_png(phase['probeImageUrl'])
                    if hashlib.sha256(image).hexdigest() != phase['probeImageSha256']:
                        raise Blocked('image-surface-mismatch')
            except Exception: raise Blocked('surface-unavailable:' + criterion['id'] + ':' + phase['name']) from None
            observations.append({'criterion': criterion['id'], 'phase': phase['name'], **observation})
    adapter = agent_readiness(plan)
    if git(plan, 'status', '--porcelain'): raise Blocked('readiness-mutated-worktree')
    return {'state': 'ready', 'base': base, 'plan': plan['criteria'], 'probes': observations, 'adapter': adapter}


def verify_png(image):
    if not image.startswith(b'\x89PNG\r\n\x1a\n') or len(image) > 4 * 1024 * 1024:
        raise Blocked('invalid-screenshot')
    offset, compressed, dimensions = 8, bytearray(), None
    ended, data_ended = False, False
    channels = 0
    while offset + 12 <= len(image):
        length, = struct.unpack('>I', image[offset:offset + 4])
        kind = image[offset + 4:offset + 8]
        data = image[offset + 8:offset + 8 + length]
        end = offset + length + 12
        if end > len(image) or zlib.crc32(kind + data) != struct.unpack('>I', image[end - 4:end])[0]:
            raise Blocked('invalid-screenshot')
        if kind == b'IHDR':
            if length != 13 or offset != 8: raise Blocked('invalid-screenshot')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data)
            # Browser screenshots use non-interlaced eight-bit pixels. Reject other
            # encodings rather than pretending to decode formats we cannot inspect.
            channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color, 0)
            if depth != 8 or not channels or compression or filtering or interlace:
                raise Blocked('invalid-screenshot')
            dimensions = (width, height)
        elif not dimensions:
            raise Blocked('invalid-screenshot')
        elif kind == b'IDAT':
            if data_ended: raise Blocked('invalid-screenshot')
            compressed.extend(data)
        elif kind == b'IEND':
            ended = length == 0 and end == len(image)
            break
        else:
            if compressed: data_ended = True
            # PLTE is optional for truecolor; no other unknown critical chunks.
            if kind == b'PLTE':
                if compressed or color in (0, 4) or not 0 < length <= 768 or length % 3:
                    raise Blocked('invalid-screenshot')
            elif not kind[0] & 32:
                raise Blocked('invalid-screenshot')
        offset = end
    if not ended or not dimensions or not all(0 < n <= 10000 for n in dimensions) or not compressed:
        raise Blocked('invalid-screenshot')
    stride = 1 + width * channels
    expected = stride * height
    if expected > 32 * 1024 * 1024: raise Blocked('invalid-screenshot')
    decoder = zlib.decompressobj()
    pixels = decoder.decompress(compressed, expected + 1)
    if (len(pixels) != expected or not decoder.eof or decoder.unused_data or
        any(pixels[row] > 4 for row in range(0, expected, stride))):
        raise Blocked('invalid-screenshot')


def read_png(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        image = response.read(4 * 1024 * 1024 + 1)
    verify_png(image)
    return image


def inspect_outgoing_history(plan, fixture):
    objects = git(plan, 'rev-list', '--objects', '--no-object-names', plan['expectedBaseSha'] + '..HEAD').splitlines()
    for identity in objects:
        kind = git(plan, 'cat-file', '-t', identity)
        if kind not in ('blob', 'commit'): continue
        try: content = git(plan, 'cat-file', '-p', identity)
        except (UnicodeError, Blocked): raise Blocked('uninspectable-outgoing-source') from None
        if kind == 'commit': content = content.partition('\n\n')[2]
        if redact(content, fixture) != content: raise Blocked('sensitive-outgoing-source')
        if '\x00' in content: raise Blocked('uninspectable-outgoing-source')


def qualify(plan, correlation, result, source):
    validate(plan, correlation)
    from codex_contract import validate_result
    schema_valid = not validate_result(result)
    missing = []
    for criterion in plan['criteria']:
        observed = set()
        if schema_valid:
            for entry in result['evidence']:
                kind = entry['kind'].replace('_', '-')
                expected_kind = 'background' if criterion['kind'] == 'command' else criterion['kind']
                if entry['criterion'] == criterion['id'] and entry['verdict'] == 'pass' and kind == expected_kind:
                    observed.update(o['phase'].replace('_', '-') for o in entry['observations'])
        missing.extend({'criterion': criterion['id'], 'phase': phase['name']}
                       for phase in criterion['phases'] if phase['name'] not in observed)
    return {'schemaValid': schema_valid, 'complete': schema_valid and not missing,
            'missingPhases': missing, 'source': source}


def prepare(plan, correlation, fixture):
    validate(plan, correlation)
    base_check(plan, Provider(plan))
    agent_readiness(plan)
    inspect_outgoing_history(plan, fixture)
    # Inspect current source as well as every outgoing historical blob/message.
    diff = git(plan, 'diff', '--binary', plan['expectedBaseSha'])
    if 'GIT binary patch' in diff: raise Blocked('uninspectable-outgoing-source')
    if redact(diff, fixture) != diff:
        raise Blocked('sensitive-outgoing-source')
    untracked = git(plan, 'ls-files', '--others', '--exclude-standard').splitlines()
    for relative in untracked:
        try: content = (Path(plan['localPath']) / relative).read_text()
        except (UnicodeError, OSError): raise Blocked('uninspectable-outgoing-source') from None
        if redact(content, fixture) != content:
            raise Blocked('sensitive-outgoing-source')
    if git(plan, 'status', '--porcelain'):
        git(plan, 'add', '--all')
        git(plan, '-c', 'user.name=WPCP Publication', '-c', 'user.email=wpcp@localhost',
            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Implement issue #' + str(plan['issueNumber']))
    inspect_outgoing_history(plan, fixture)
    head = git(plan, 'rev-parse', 'HEAD')
    if head == plan['expectedBaseSha']:
        raise Blocked('branch-not-ahead')
    return {'state': 'evidence-prepared', 'headSha': head}


def check_capture_head(plan, head):
    if (git(plan, 'rev-parse', 'HEAD') != head or git(plan, 'status', '--porcelain') or
        git(plan, 'branch', '--show-current') != plan['branch']):
        raise Blocked('evidence-head-drift')


def evidence(plan, correlation, fixture, run_id, head=None):
    if head is None:
        head = prepare(plan, correlation, fixture)['headSha']
    validate(plan, correlation)
    check_capture_head(plan, head)
    agent_readiness(plan)
    entries = []
    for criterion in plan['criteria']:
        phases = []
        for phase in criterion['phases']:
            try:
                observation = checked(phase['execute'], plan, head)
                if phase['name'] == 'screenshot':
                    image = Path(phase['imagePath']).read_bytes()
                    verify_png(image)
                    for canary in fixture['redactionPolicy']['controlledCanaries']:
                        if any(canary['value'].encode(encoding) in image for encoding in ('utf-8', 'utf-16-le', 'utf-16-be')):
                            raise Blocked('sensitive-screenshot')
                    public = read_png(phase['imageUrl'])
                    if image != public: raise Blocked('screenshot-readback-mismatch')
                    observation.update(imageUrl=phase['imageUrl'], imageSha256=hashlib.sha256(image).hexdigest())
            except Exception:
                raise Blocked('evidence-failed:' + criterion['id'] + ':' + phase['name'],
                    failedPhases=[{'criterion': criterion['id'], 'phase': phase['name']}]) from None
            finally:
                check_capture_head(plan, head)
            phases.append({'name': phase['name'], 'headSha': head, **observation})
        entries.append({k: criterion[k] for k in ('id', 'description', 'kind', 'surface', 'expectedReadBack')} | {'phases': phases})
    check_capture_head(plan, head)
    safe = redact(entries, fixture)
    body = ['<!-- wpcp-run:' + run_id + ' -->', 'Closes #' + str(plan['issueNumber']),
            'Evidence for commit/head `' + head + '`.',
            'Review qualification is a separate gate.']
    for entry in safe:
        body += ['### ' + entry['id'] + ': ' + entry['description'],
                 'Kind: ' + entry['kind'] + '; surface: ' + entry['surface'],
                 'Expected read-back: ' + entry['expectedReadBack']]
        for phase in entry['phases']:
            body += ['**' + phase['name'] + '**', '<pre>' + __import__('html').escape(json.dumps(phase, ensure_ascii=False, indent=2)) + '</pre>']
            if 'imageUrl' in phase: body.append('![Decisive screenshot](' + phase['imageUrl'] + ')')
    intent = {'headSha': head, 'branch': plan['branch'], 'baseBranch': plan['baseBranch'],
              'body': '\n\n'.join(body), 'title': redact(plan['title'], fixture), 'entries': safe}
    if len(intent['body']) > 60000: raise Blocked('evidence-body-too-large')
    return {'state': 'evidence-ready', 'intent': intent}


def publish(plan, correlation, intent, allow_create):
    validate(plan, correlation)
    provider = Provider(plan)
    provider.check_repository()
    head = intent['headSha']
    if git(plan, 'rev-parse', 'HEAD') != head or git(plan, 'status', '--porcelain'):
        raise Blocked('publication-head-drift')
    if intent['branch'] != plan['branch'] or intent['baseBranch'] != plan['baseBranch']:
        raise Blocked('publication-intent-conflict')
    # All states, including closed/merged PRs, prevent a duplicate creation.
    pulls = []
    for page in range(1, 101):
        found = provider.request('/pulls?state=all&head=' + urllib.parse.quote(plan['repository']['fullName'].split('/')[0] + ':' + plan['branch']) + '&per_page=100&page=' + str(page))
        if not isinstance(found, list): raise Blocked('provider-receipt-invalid')
        pulls.extend(p for p in found if p['head']['ref'] == plan['branch'] and p['head']['repo']['id'] == plan['repository']['providerRepositoryId'])
        if len(found) < 100: break
    else: raise Blocked('provider-receipt-unbounded')
    if len(pulls) > 1: raise Blocked('provider-receipt-ambiguous')
    if not pulls:
        if not allow_create: raise Blocked('publication-create-uncertain')
        base_check(plan, provider)
        remote_ref = git(plan, 'ls-remote', plan['remoteName'], 'refs/heads/' + plan['branch'])
        if remote_ref and remote_ref.split()[0] != head:
            raise Blocked('remote-branch-conflict')
        git(plan, 'push', '--porcelain', '--force-with-lease=refs/heads/' + plan['branch'] + ':' + (head if remote_ref else ''),
            plan['remoteName'], head + ':refs/heads/' + plan['branch'])
        if provider.head(plan['branch']) != head: raise Blocked('provider-head-mismatch')
        created = provider.request('/pulls', {'title': intent['title'], 'body': intent['body'],
            'head': plan['branch'], 'base': plan['baseBranch'], 'draft': True})
        pulls = [created]
    pull = provider.request('/pulls/' + str(pulls[0]['number']))
    if (pull['draft'] is not True or pull['state'] != 'open' or pull['head']['sha'] != head or
        pull['head']['ref'] != plan['branch'] or pull['head']['repo']['id'] != plan['repository']['providerRepositoryId'] or
        pull['base']['ref'] != plan['baseBranch'] or pull['base']['repo']['id'] != plan['repository']['providerRepositoryId'] or
        pull['body'] != intent['body'] or provider.head(plan['branch']) != head):
        raise Blocked('provider-receipt-conflict')
    return {'state': 'draft-published', 'pullRequest': pull, 'adopted': not allow_create}


def redact(value, fixture):
    policy = fixture['redactionPolicy']
    marker = policy['marker']
    def text(value):
        for canary in sorted((c['value'] for c in policy['controlledCanaries']), key=len, reverse=True):
            value = value.replace(canary, marker)
        value = re.sub(r'(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+', r'\1' + marker, value)
        value = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{12,})\b', marker, value)
        value = re.sub(r'(?i)((?:password|token|secret|authorization)\s*[:=]\s*)[^\s,;]+', r'\1' + marker, value)
        value = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', marker, value)
        return value
    if isinstance(value, str): return text(value)
    if isinstance(value, list): return [redact(v, fixture) for v in value]
    if isinstance(value, dict):
        return {text(k): marker if k.lower() in ('password', 'token', 'secret', 'authorization') else redact(v, fixture) for k, v in value.items()}
    return value


def main():
    request = json.load(sys.stdin)
    fixture = json.loads(Path(request['fixture']).read_text())
    try:
        stage = request['stage']
        if stage == 'verify-head':
            from head_qualification import verify
            result = verify(request['plan'], request['headSha'], request['pullNumber'])
        elif stage == 'current-head':
            from head_qualification import current_head
            result = current_head(request['plan'], request['headSha'], request['pullNumber'])
        elif stage == 'review-head':
            from head_qualification import review
            result = review(request, fixture)
        elif stage in ('repair-assignment', 'repair-head', 'prepare-repair', 'publish-repair'):
            from head_qualification import repair_stage
            result = repair_stage(request, fixture)
        elif stage == 'preflight': result = preflight(request['plan'], request['correlation'])
        elif stage == 'qualify': result = qualify(request['plan'], request['correlation'], request['result'], request['source'])
        elif stage == 'prepare': result = prepare(request['plan'], request['correlation'], fixture)
        elif stage == 'capture': result = evidence(request['plan'], request['correlation'], fixture, request['runId'], request['headSha'])
        elif stage == 'evidence': result = evidence(request['plan'], request['correlation'], fixture, request['runId'])
        elif stage == 'publish': result = publish(request['plan'], request['correlation'], request['intent'], request['allowCreate'])
        else: raise Blocked('unknown-publication-stage')
    except Blocked as error:
        result = {'state': 'preflight-blocked' if request['stage'] == 'preflight' else 'publication-blocked', 'blocker': str(error), **error.details}
    except Exception:
        result = {'state': 'preflight-blocked' if request['stage'] == 'preflight' else 'publication-blocked', 'blocker': 'publication-evidence-unavailable'}
    print(json.dumps(redact(result, fixture)))


def supervise_command():
    # This process owns the command group independently of the adapter. A killed
    # adapter/worker cannot leave a capture tool running until a later retry.
    parent, owner = int(sys.argv[2]), int(sys.argv[3])
    deadline = time.monotonic() + float(sys.argv[4])
    command = subprocess.Popen(sys.argv[5:])
    try:
        while command.poll() is None:
            try:
                os.kill(owner, 0)
                alive = os.getppid() == parent
            except ProcessLookupError:
                alive = False
            if not alive or time.monotonic() >= deadline:
                os.killpg(os.getpgrp(), signal.SIGKILL)
            time.sleep(.05)
        return command.returncode
    finally:
        if command.poll() is None: command.kill()
        command.wait()


if __name__ == '__main__':
    sys.modules['publication_adapter'] = sys.modules[__name__]
    if len(sys.argv) > 1 and sys.argv[1] == '--supervise-command':
        raise SystemExit(supervise_command())
    main()
